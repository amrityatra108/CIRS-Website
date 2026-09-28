/* Content-aware composition. Keep compose in sync with tools/bloglayout.py. */
const CirsBlogLayout = (() => {
  const spans = {feature:7, essay:5, text:4, brief:3, micro:2, portrait:4, strip:9, visual:6, wide:8};
  function compose(items) {
    let previous = '';
    const result = items.map((item, i) => {
      const long = item.title_length > 55;
      let role = !i ? 'feature' : item.image
        ? (item.ratio < .85 ? 'portrait' : item.ratio > 2.3 ? (previous !== 'strip' ? 'strip' : 'wide') : long ? 'wide' : 'visual')
        : (long || item.minutes >= 5 ? 'essay' : item.excerpt_length < 80 ? 'micro' : ['feature','essay','wide'].includes(previous) ? 'brief' : 'text');
      const override = item.override;
      if (i && Object.hasOwn(spans, override) && (!['portrait','strip','visual','wide'].includes(override) || item.image) && (!long || spans[override] >= 5)) role = override;
      previous = role;
      return {role, span:spans[role]};
    });
    const split = items.length >= 6 ? Math.round(items.length * .45) : 0;
    let start = 0;
    while (start < result.length) {
      let end = start, used = 0;
      while (end < result.length && (end === start || end !== split)) {
        const span = result[end].span;
        if (used + span > 12 || end - start === 3) break;
        used += span; end++;
      }
      const band = result.slice(start,end);
      const largest = band.reduce((a,b) => a.span >= b.span ? a : b);
      largest.span += Math.max(0,12-used-(used < 7 ? 2 : 0));
      band.forEach((entry,i) => {entry.start = i === 0;});
      start = end;
    }
    return {result,split};
  }
  return {compose};
})();
if (typeof module !== 'undefined') module.exports = CirsBlogLayout;
if (typeof document !== 'undefined') (() => {
  const journal = document.querySelector('[data-journal]');
  if (!journal) return;
  const list = journal.querySelector('[data-story-list]');
  const rows = Array.from(list.querySelectorAll('[data-story]'));
  const controls = journal.querySelector('[data-discovery]');
  const topicControls = journal.querySelector('[data-topic-controls]');
  const topics = Array.from(topicControls.querySelectorAll('[data-topic]'));
  const search = journal.querySelector('[data-search-input]');
  const sort = journal.querySelector('[data-sort]');
  const result = journal.querySelector('[data-results]');
  const empty = journal.querySelector('[data-empty]');
  const reset = journal.querySelector('[data-reset]');
  const quote = journal.querySelector('[data-interruption]');
  const text = value => String(value || '').normalize('NFKD').toLocaleLowerCase().trim();
  let selectedTopic = 'all';
  function readState() {
    const params = new URL(location.href).searchParams;
    search.value = params.get('q') || '';
    sort.value = ['newest','oldest','title'].includes(params.get('sort')) ? params.get('sort') : 'newest';
    selectedTopic = topics.some(button => button.dataset.topic === params.get('topic')) ? params.get('topic') : 'all';
  }
  function syncImageSizes() {
    // Measure the actual slot, including native-resolution and editorial caps.
    // Browser density selection still uses the existing responsive srcset.
    list.querySelectorAll('[data-story]:not([hidden]) img').forEach(img => {
      img.sizes = Math.ceil(img.getBoundingClientRect().width) + 'px';
    });
  }
  const imageSlots = new ResizeObserver(syncImageSizes);
  imageSlots.observe(list);
  function update(save = true) {
    const query = text(search.value);
    const searchMatches = rows.filter(row => text(row.dataset.search).includes(query));
    const sorted = [...rows].sort((a,b) => {
      const difference = sort.value === 'title' ? a.dataset.title.localeCompare(b.dataset.title)
        : (Number(a.dataset.issue)-Number(b.dataset.issue)) * (sort.value === 'oldest' ? 1 : -1);
      return difference || Number(a.dataset.order)-Number(b.dataset.order);
    });
    const visible = sorted.filter(row => searchMatches.includes(row) && (selectedTopic === 'all' || row.dataset.category === selectedTopic));
    const {result:layout,split} = CirsBlogLayout.compose(visible.map(row => ({
      image:row.dataset.image === 'true', ratio:Number(row.dataset.ratio), title_length:row.dataset.title.length,
      excerpt_length:Number(row.dataset.excerptLength), minutes:Number(row.dataset.minutes), override:row.dataset.override
    })));
    const fragment = document.createDocumentFragment();
    visible.forEach((row,i) => {
      const {role,span,start} = layout[i];
      row.dataset.role = role; row.dataset.bandStart = String(start);
      row.style.setProperty('--span',span);
      row.hidden = false;
      fragment.append(row);
      if (i+1 === split) fragment.append(quote);
    });
    sorted.filter(row => !visible.includes(row)).forEach(row => {row.hidden = true; fragment.append(row);});
    quote.hidden = !split;
    if (!split) fragment.append(quote);
    if (visible.length) {
      const lead = visible[0], link = lead.querySelector('h3 a');
      quote.querySelector('[data-quote-text]').textContent = '“' + lead.dataset.quote + '”';
      const source = quote.querySelector('[data-quote-link]');
      source.textContent = lead.dataset.title; source.href = link.getAttribute('href');
      quote.querySelector('[data-quote-issue]').textContent = 'Issue ' + lead.dataset.issue;
    }
    list.append(fragment);
    syncImageSizes();
    topics.forEach(button => {
      button.querySelector('[data-topic-count]').textContent = button.dataset.topic === 'all' ? searchMatches.length : searchMatches.filter(row => row.dataset.category === button.dataset.topic).length;
      button.setAttribute('aria-pressed',String(button.dataset.topic === selectedTopic));
    });
    result.textContent = visible.length === rows.length ? rows.length + ' stories' : visible.length + ' of ' + rows.length + ' stories';
    empty.hidden = visible.length !== 0;
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
  controls.hidden = false; topicControls.hidden = false;
  readState(); update(false);
})();
