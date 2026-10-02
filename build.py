"""Build the shared sunglasses store from campaign records. No AI calls."""
import html
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent


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
    for filename in ('style.css', 'cart.js'):
        shutil.copyfile(root / filename, target / filename)
    template = (root / 'template.html').read_text(encoding='utf-8')
    cards = []
    esc = lambda x: html.escape(str(x), quote=True)
    catalog = []
    for record in records:
        p, c, slug = record['product'], record['campaign'], record['slug']
        folder = target / 'products' / slug
        folder.mkdir(parents=True, exist_ok=True)
        image = '../../' + record['image_file']
        price = f"{float(p['price']):.3f} {p['currency']}"
        video = '<video controls playsinline preload="metadata" src="../../' + esc(record['video_file']) + '"></video>' if record.get('video_file') else ''
        values = {'NAME': esc(p['name']), 'HEADLINE': esc(c['headline']), 'DESCRIPTION': esc(p['description']), 'SUBHEAD': esc(c['subheadline']), 'PRICE': esc(price), 'SLUG': esc(slug), 'IMAGE': esc(image), 'VIDEO': video, 'BENEFITS': ''.join('<li>' + esc(b) + '</li>' for b in c['benefits'])}
        page = template
        for name, value in values.items():
            page = page.replace('__' + name + '__', value)
        page = page.replace('</head>', '<meta name="campaign-revision" content="' + esc(record.get('page_revision', 'legacy')) + '"></head>')
        (folder / 'index.html').write_text(page, encoding='utf-8')
        cards.append('<a class="product-card" href="products/' + slug + '/"><img src="' + esc(record['image_file']) + '" alt="' + esc(p['name']) + '"><h2>' + esc(p['name']) + '</h2><p>' + esc(price) + '</p></a>')
        catalog.append({'slug': slug, 'name': p['name'], 'price': float(p['price']), 'currency': p['currency']})
    assets = root / 'assets'
    if assets.exists():
        shutil.copytree(assets, target / 'assets', dirs_exist_ok=True)
    (target / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False), encoding='utf-8')
    homepage = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Collection Soleil</title><link rel="stylesheet" href="style.css"><script src="cart.js" defer></script></head><body data-base="./"><header><a href="./">COLLECTION SOLEIL</a><button data-cart-open>Panier <span data-cart-count>0</span></button></header><main><p class="eyebrow">La collection</p><h1>Un regard sur le soleil.</h1><p>Découvrez notre sélection de lunettes de soleil.</p><section class="catalog">' + ''.join(cards) + '</section></main>' + cart_markup() + '<footer>Catalogue de démonstration · Commandes et paiement à configurer.</footer></body></html>'
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
