'use strict';
(async()=>{
  const base=document.body.dataset.base;
  const response=await fetch(base+'catalog.json');
  if(!response.ok) throw new Error('Catalogue unavailable');
  const products=await response.json();
  const lookup=new Map(products.map(p=>[p.slug,p]));
  let cart={};
  try { const saved=JSON.parse(localStorage.getItem('soleil-cart')||'{}'); for(const [slug,quantity] of Object.entries(saved)) if(lookup.has(slug)&&Number.isInteger(quantity)&&quantity>0&&quantity<=99) cart[slug]=quantity; } catch {}
  const dialog=document.querySelector('#cart');
  function render(){
    const lines=document.querySelector('#cart-lines'); lines.replaceChildren();
    const totals=new Map(); let count=0;
    for(const [slug,quantity] of Object.entries(cart)){
      const product=lookup.get(slug); if(!product) continue;
      const line=document.createElement('div'); line.className='cart-line';
      const label=document.createElement('span'); label.textContent=product.name+' × '+quantity;
      const remove=document.createElement('button'); remove.textContent='Retirer'; remove.addEventListener('click',()=>{delete cart[slug];render();});
      line.append(label,remove);lines.append(line);count+=quantity;
      totals.set(product.currency,(totals.get(product.currency)||0)+product.price*quantity);
    }
    document.querySelector('#cart-total').textContent=Array.from(totals,([currency,value])=>value.toFixed(3)+' '+currency).join(' · ')||'Votre panier est vide.';
    document.querySelectorAll('[data-cart-count]').forEach(el=>el.textContent=count);
    try {localStorage.setItem('soleil-cart',JSON.stringify(cart));} catch {}
  }
  document.querySelectorAll('[data-cart-open]').forEach(el=>el.addEventListener('click',()=>dialog.showModal()));
  document.querySelector('[data-cart-close]').addEventListener('click',()=>dialog.close());
  document.querySelectorAll('[data-add]').forEach(el=>el.addEventListener('click',()=>{const slug=el.dataset.add;if(lookup.has(slug)){cart[slug]=Math.min(99,(cart[slug]||0)+1);render();dialog.showModal();}}));
  render();
})().catch(()=>{document.querySelectorAll('[data-add],[data-cart-open]').forEach(el=>el.disabled=true);});
