"""Build the shared product store from campaign records. No AI calls."""
import html
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent


def category_label(product):
    category = str(product.get('category') or 'other').strip().lower()
    labels = {'sunglasses': 'Lunettes de soleil', 'audio': 'Audio', 'kitchen': 'Cuisine',
              'home': 'Maison', 'electronics': 'Électronique', 'beauty': 'Beauté',
              'sport': 'Sport', 'fashion': 'Mode', 'accessories': 'Accessoires',
              'other': 'Non classé'}
    return category, labels.get(category, category.replace('_', ' ').replace('-', ' ').capitalize())


def build(root=ROOT):
    root = Path(root)
    records = json.loads((root / 'data/products.json').read_text(encoding='utf-8-sig'))
    keys = set()
    for record in records:
        p = record['product']
        slug = record['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in keys:
            raise ValueError('Invalid or duplicate product slug')
        keys.add(slug)
        if float(p['price']) < 0 or not re.fullmatch(r'[A-Z]{3}', p['currency']):
            raise ValueError('Invalid price or currency')
    target = root / 'dist'
    target.mkdir(exist_ok=True)
    for filename in ('style.css', 'cart.js', 'catalog.js'):
        shutil.copyfile(root / filename, target / filename)
    template = (root / 'template.html').read_text(encoding='utf-8')
    cards = []
    esc = lambda x: html.escape(str(x), quote=True)
    catalog = []
    categories = {}
    featured = ''
    for record in records:
        p, c, slug = record['product'], record['campaign'], record['slug']
        folder = target / 'products' / slug
        folder.mkdir(parents=True, exist_ok=True)
        image = '../../' + record['image_file']
        price = f"{float(p['price']):.3f} {p['currency']}"
        category, label = category_label(p)
        categories[category] = label
        supplier_url = p.get('supplier_url', '')
        parsed_supplier = urlparse(supplier_url)
        if parsed_supplier.scheme != 'https' or not parsed_supplier.netloc:
            raise ValueError('Invalid supplier URL')
        # Ads remain standalone; the product page has no video dependency.
        values = {'NAME': esc(p['name']), 'HEADLINE': esc(c['headline']), 'DESCRIPTION': esc(p['description']), 'SUBHEAD': esc(c['subheadline']), 'PRICE': esc(price), 'SLUG': esc(slug), 'IMAGE': esc(image), 'VIDEO': '', 'CATEGORY': esc(label), 'SUPPLIER_URL': esc(supplier_url), 'BENEFITS': ''.join('<li>' + esc(b) + '</li>' for b in c['benefits'])}
        page = template
        for name, value in values.items():
            page = page.replace('__' + name + '__', value)
        page = page.replace('</head>', '<meta name="campaign-revision" content="' + esc(record.get('page_revision', 'legacy')) + '"></head>')
        (folder / 'index.html').write_text(page, encoding='utf-8')
        cards.append('<a class="product-card" href="products/' + slug + '/" data-product-category="' + esc(category) + '" data-search="' + esc(p['name'] + ' ' + label + ' ' + p['description']) + '"><div class="card-image"><span class="card-category">' + esc(label) + '</span><img loading="lazy" src="' + esc(record['image_file']) + '" alt="' + esc(p['name']) + '"></div><div class="card-body"><h3>' + esc(p['name']) + '</h3><p class="card-description">' + esc(p['description']) + '</p><div class="card-bottom"><span>' + esc(price) + '</span><span class="card-arrow" aria-hidden="true">↗</span></div></div></a>')
        catalog.append({'slug': slug, 'name': p['name'], 'price': float(p['price']), 'currency': p['currency'], 'category': category})
        if not featured:
            featured = '<a class="featured-product" href="products/' + slug + '/"><img src="' + esc(record['image_file']) + '" alt="' + esc(p['name']) + '"><span>' + esc(p['name']) + '</span></a>'
    assets = root / 'assets'
    if assets.exists():
        shutil.copytree(assets, target / 'assets', dirs_exist_ok=True)
    (target / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False), encoding='utf-8')
    homepage = (root / 'home.html').read_text(encoding='utf-8')
    filters = ''.join('<button class="filter-chip" type="button" data-category="' + esc(key) + '" aria-pressed="false">' + esc(label) + '</button>' for key, label in sorted(categories.items(), key=lambda kv: kv[1]))
    values = {'COUNT': str(len(records)), 'CARDS': ''.join(cards), 'FEATURED': featured or '<div class="featured-product"><span>La sélection arrive bientôt.</span></div>', 'FILTERS': filters}
    for name, value in values.items():
        homepage = homepage.replace('__' + name + '__', value)
    (target / 'index.html').write_text(homepage, encoding='utf-8')
    for record in records:
        for field in ('image_file', 'video_file'):
            if record.get(field) and not (target / record[field]).is_file():
                raise ValueError('Missing asset: ' + record[field])
    return {'product_count': len(records), 'build_directory': str(target), 'deployment_status': 'not_configured'}


def cart_markup():
    return '<dialog id="cart"><h2>Votre sélection</h2><div id="cart-lines"></div><p id="cart-total"></p><p>Les commandes ne sont pas encore activées.</p><button data-cart-close>Fermer</button></dialog>'


if __name__ == '__main__':
    print(json.dumps(build()))
