'use strict';
(() => {
  const search = document.querySelector('#product-search');
  if (!search) return;
  const cards = [...document.querySelectorAll('.product-card')];
  const buttons = [...document.querySelectorAll('[data-category]')];
  let category = 'all';
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('fr').trim();
  function filter() {
    const words = normalize(search.value).split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const matches = (category === 'all' || card.dataset.productCategory === category) && words.every(word => normalize(card.dataset.search).includes(word));
      card.hidden = !matches;
      if (matches) visible++;
    }
    document.querySelector('#result-count').textContent = `${visible} produit${visible === 1 ? '' : 's'} à découvrir`;
    document.querySelector('#empty-results').hidden = visible !== 0;
    buttons.forEach(button => {const active = button.dataset.category === category; button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active));});
  }
  search.addEventListener('input', filter);
  buttons.forEach(button => button.addEventListener('click', () => {category = button.dataset.category; filter();}));
  document.querySelector('#reset-filters').addEventListener('click', () => {category = 'all'; search.value = ''; filter(); search.focus();});
})();
