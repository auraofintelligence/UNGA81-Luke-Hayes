const $ = s => document.querySelector(s);
const words = {
  joyful: ['Did life become more worth living?', 'Relationships, curiosity, belonging, creativity, music, travel, laughter, rest and time to enjoy them.'],
  responsible: ['Did we take responsibility for the consequences?', 'Who pays, who benefits, what is hidden, what happens to other people and species, and what is passed to future generations.'],
  abundance: ['Did useful capability become more abundant and more widely shared?', 'Food, energy, housing, knowledge, care, opportunity and productive capacity, with more freedom from avoidable shortage.']
};
document.querySelectorAll('[data-word]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-word]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  $('#compass-question').textContent = words[button.dataset.word][0];
  $('#compass-detail').textContent = words[button.dataset.word][1];
  $('.compass-answer').dataset.active = button.dataset.word;
}));
const menu = $('.site-menu');
document.addEventListener('click', e => { if (menu && !menu.contains(e.target)) menu.open = false; });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && menu?.open) { menu.open = false; menu.querySelector('summary').focus(); } });
let scheduled = false;
const progress = () => {
  const range = document.documentElement.scrollHeight - innerHeight;
  $('.reading-progress').style.transform = `scaleX(${range > 0 ? Math.min(1, scrollY / range) : 0})`;
  $('.back-top').classList.toggle('visible', scrollY > 400);
  scheduled = false;
};
addEventListener('scroll', () => { if (!scheduled) { scheduled = true; requestAnimationFrame(progress); } }, {passive:true});
addEventListener('resize', progress); progress();
if ($('#reference-search')) {
  const cards = [...document.querySelectorAll('.reference-card')];
  const search = $('#reference-search'), category = $('#reference-category'), status = $('#reference-status');
  function filter() {
    const terms = search.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const card of cards) {
      const match = terms.every(t => card.textContent.toLocaleLowerCase().includes(t)) && (category.value === 'all' || card.dataset.category === category.value) && (status.value === 'all' || (status.value === 'pending' ? card.dataset.status.startsWith('Awaiting') : !!card.querySelector('.source-links a')));
      card.hidden = !match;
      if (match) count++;
    }
    $('#result-count').textContent = `${count} of ${cards.length} references`;
    $('#empty-results').hidden = count !== 0;
  }
  const reset = () => { search.value = ''; category.value = status.value = 'all'; filter(); };
  search.addEventListener('input', filter); category.addEventListener('change', filter); status.addEventListener('change', filter);
  $('#clear-filters').addEventListener('click', () => { reset(); search.focus(); });
  function revealHash() { if (/^#ref-\d+$/.test(location.hash)) { reset(); document.getElementById(location.hash.slice(1))?.scrollIntoView(); } }
  addEventListener('hashchange', revealHash); revealHash();
}
if ('IntersectionObserver' in window) {
  const links = [...document.querySelectorAll('.contents nav a')];
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) links.forEach(a => { if (a.hash === '#' + entry.target.id) a.setAttribute('aria-current','location'); else a.removeAttribute('aria-current'); });
  }), {rootMargin:'-15% 0px -65% 0px'});
  document.querySelectorAll('.reading-section').forEach(s => observer.observe(s));
}
