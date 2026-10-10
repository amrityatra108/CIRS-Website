/* All stories: one sideways shelf of even cards, with search, topics and sort.
   Without this script the shelf still scrolls sideways on its own scrollbar;
   with it, the scrollbar gives way to buttons, a drag and a thin track. */
(() => {
  const journal = document.querySelector('[data-journal]');
  if (!journal) return;
  const shelf = journal.querySelector('[data-story-list]');
  const cards = Array.from(shelf.querySelectorAll('[data-story]'));
  const controls = journal.querySelector('[data-discovery]');
  const topicControls = journal.querySelector('[data-topic-controls]');
  const topics = Array.from(topicControls.querySelectorAll('[data-topic]'));
  const search = journal.querySelector('[data-search-input]');
  const sort = journal.querySelector('[data-sort]');
  const result = journal.querySelector('[data-results]');
  const empty = journal.querySelector('[data-empty]');
  const reset = journal.querySelector('[data-reset]');
  const nav = journal.querySelector('[data-shelf-nav]');
  const steps = Array.from(journal.querySelectorAll('[data-shelf-step]'));
  const track = journal.querySelector('[data-shelf-track]');
  const thumb = journal.querySelector('[data-shelf-thumb]');
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  const text = value => String(value || '').normalize('NFKD').toLocaleLowerCase().trim();
  let selectedTopic = 'all';
  let visible = cards;

  function readState() {
    const params = new URL(location.href).searchParams;
    search.value = params.get('q') || '';
    sort.value = ['newest','oldest','title'].includes(params.get('sort')) ? params.get('sort') : 'newest';
    selectedTopic = topics.some(button => button.dataset.topic === params.get('topic')) ? params.get('topic') : 'all';
  }

  // Where the shelf is: the buttons stop at its ends, the track shows how much
  // of it is in view and where, and the edges fade only where more lies beyond.
  let framed = 0;
  function edges() {
    framed = 0;
    const max = shelf.scrollWidth - shelf.clientWidth;
    const x = Math.round(shelf.scrollLeft);
    const start = x <= 2, end = x >= max - 2;
    shelf.dataset.start = String(start); shelf.dataset.end = String(end);
    steps[0].disabled = start; steps[1].disabled = end;
    const shown = shelf.scrollWidth ? shelf.clientWidth / shelf.scrollWidth : 1;
    thumb.style.width = (shown * 100) + '%';
    thumb.style.transform = 'translateX(' + (max > 0 ? (x / max) * (1 / shown - 1) * 100 : 0) + '%)';
    track.style.visibility = max > 2 ? '' : 'hidden';
  }
  function frame() { if (!framed) framed = requestAnimationFrame(edges); }

  // A step moves on by as many whole cards as are in view, from the first
  // card the shelf now starts at, so a card is never left cut in half.
  function starts() {
    const origin = visible[0].offsetLeft;
    return visible.map(card => card.offsetLeft - origin);
  }
  function go(left) { shelf.scrollTo({left, behavior: still.matches ? 'auto' : 'smooth'}); }
  function step(direction) {
    if (!visible.length) return;
    const lefts = starts();
    const width = visible[0].getBoundingClientRect().width;
    const gap = visible.length > 1 ? lefts[1] - width : 0;
    const perView = Math.max(1, Math.floor((shelf.clientWidth + gap) / (width + gap)));
    let at = lefts.findIndex(left => left >= shelf.scrollLeft - 2);
    if (at < 0) at = lefts.length - 1;
    go(lefts[Math.min(lefts.length - 1, Math.max(0, at + direction * perView))]);
  }
  // After a drag, come to rest on the nearest card's edge.
  function settle() {
    if (!visible.length) return;
    const lefts = starts();
    go(lefts.reduce((best, left) => Math.abs(left - shelf.scrollLeft) < Math.abs(best - shelf.scrollLeft) ? left : best, lefts[0]));
  }
  steps.forEach(button => button.addEventListener('click', () => step(Number(button.dataset.shelfStep))));

  // A sideways swipe on a trackpad scrolls the shelf itself: the page's smooth
  // scroll would otherwise take it for an upward or downward one.
  shelf.addEventListener('wheel', event => {
    if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) event.lenisStopPropagation = true;
  }, {passive:true});

  // With a mouse the shelf can be dragged. A drag that moved is not a click,
  // so letting go over a card does not open it.
  let drag = null, dragged = false;
  shelf.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'mouse' || event.button !== 0) return;
    drag = {x:event.clientX, left:shelf.scrollLeft}; dragged = false;
  });
  addEventListener('pointermove', event => {
    if (!drag) return;
    const dx = event.clientX - drag.x;
    if (!dragged && Math.abs(dx) > 6) { dragged = true; shelf.classList.add('is-dragging'); }
    if (dragged) shelf.scrollLeft = drag.left - dx;
  });
  addEventListener('pointerup', () => {
    if (!drag) return;
    drag = null;
    if (dragged) { shelf.classList.remove('is-dragging'); settle(); }
  });
  shelf.addEventListener('click', event => {
    if (dragged) { event.preventDefault(); event.stopPropagation(); dragged = false; }
  }, true);
  shelf.addEventListener('dragstart', event => event.preventDefault());
  shelf.addEventListener('scroll', frame, {passive:true});
  new ResizeObserver(frame).observe(shelf);

  function update(save = true) {
    const query = text(search.value);
    const searchMatches = cards.filter(card => text(card.dataset.search).includes(query));
    const sorted = [...cards].sort((a,b) => {
      const difference = sort.value === 'title' ? a.dataset.title.localeCompare(b.dataset.title)
        : (Number(a.dataset.issue)-Number(b.dataset.issue)) * (sort.value === 'oldest' ? 1 : -1);
      return difference || Number(a.dataset.order)-Number(b.dataset.order);
    });
    visible = sorted.filter(card => searchMatches.includes(card) && (selectedTopic === 'all' || card.dataset.category === selectedTopic));
    const fragment = document.createDocumentFragment();
    visible.forEach(card => { card.hidden = false; fragment.append(card); });
    sorted.filter(card => !visible.includes(card)).forEach(card => { card.hidden = true; fragment.append(card); });
    shelf.append(fragment);
    shelf.hidden = visible.length === 0;
    shelf.scrollLeft = 0;
    topics.forEach(button => {
      button.querySelector('[data-topic-count]').textContent = button.dataset.topic === 'all' ? searchMatches.length : searchMatches.filter(card => card.dataset.category === button.dataset.topic).length;
      button.setAttribute('aria-pressed',String(button.dataset.topic === selectedTopic));
    });
    result.textContent = visible.length === cards.length ? cards.length + ' stories' : visible.length + ' of ' + cards.length + ' stories';
    empty.hidden = visible.length !== 0;
    edges();
    if (save) {
      const url = new URL(location.href);
      for (const [key,value,defaultValue] of [['q',search.value,''],['topic',selectedTopic,'all'],['sort',sort.value,'newest']]) {
        if (value === defaultValue) url.searchParams.delete(key); else url.searchParams.set(key,value);
      }
      history.replaceState(null,'',url);
    }
  }
  topics.forEach(button => button.addEventListener('click',() => {selectedTopic = button.dataset.topic; update();}));
  search.addEventListener('input',() => update());
  sort.addEventListener('change',() => update());
  reset.addEventListener('click',() => {selectedTopic='all'; search.value=''; sort.value='newest'; update(); search.focus();});
  addEventListener('popstate',() => {readState(); update(false);});
  addEventListener('pageshow',() => {readState(); update(false);});
  controls.hidden = false; topicControls.hidden = false; nav.hidden = false; track.hidden = false;
  journal.classList.add('is-enhanced');
  readState(); update(false);
})();
