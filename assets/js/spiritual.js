/* Page-scoped motion. The shared CIRS controller remains the only Lenis.
   The document is a complete, ordered reading experience without this file. */
(function () {
  'use strict';
  const root = document.documentElement;
  const main = document.querySelector('body.spiritual main');
  if (!main) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const desktop = matchMedia('(min-width: 900px) and (min-height: 700px)');
  const nav = main.querySelector('.sl-chapters');
  const links = nav ? [...nav.querySelectorAll('a')] : [];
  const chapters = links.map(a => a.hash ? document.getElementById(a.hash.slice(1)) : null);
  const line = main.querySelector('.sl-rhythm__line');
  const practices = [...main.querySelectorAll('.sl-practice')];
  const memory = main.querySelector('.sl-memory-run');
  const track = main.querySelector('.sl-memory-track');
  const values = main.querySelector('.sl-values');
  const valuePanels = [...main.querySelectorAll('.sl-value')];
  let triggers = [], valueTrigger = null, frame = 0, timer = 0;
  const clamp = v => Math.min(1, Math.max(0, v));
  const animated = () => !reduced.matches && !!window.ScrollTrigger;
  function create(options) { const t = ScrollTrigger.create(options); triggers.push(t); return t; }
  function reset() {
    triggers.forEach(t => t.kill()); triggers = []; valueTrigger = null;
    [memory, track, ...valuePanels, ...main.querySelectorAll('.sl-spatial,.sl-reflection__image,.sl-return__rings')].forEach(el => el?.removeAttribute('style'));
    valuePanels.forEach(el => { el.inert = false; });
  }
  function measure() {
    frame = 0;
    const mark = innerHeight * .58;
    if (line) {
      const box = line.getBoundingClientRect();
      const p = reduced.matches ? 1 : clamp((mark - box.top) / Math.max(1, box.height));
      line.style.setProperty('--sl-progress', p.toFixed(4));
      practices.forEach(el => el.classList.toggle('is-lit', reduced.matches || el.getBoundingClientRect().top + 55 < mark));
    }
    let active = 0;
    chapters.forEach((el, i) => { if (el && el.getBoundingClientRect().top < mark) active = i; });
    links.forEach((link, i) => { if (i === active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current'); });
    if (nav) nav.classList.toggle('is-ended', (chapters.at(-1)?.getBoundingClientRect().bottom || 0) < 0);
  }
  function queue() { if (!frame) frame = requestAnimationFrame(measure); }
  function configure() {
    reset();
    root.classList.toggle('sl-body-motion', animated());
    if (animated()) {
      if (desktop.matches) {
        main.querySelectorAll('.sl-spatial').forEach(el => {
          const depth = Number(el.dataset.depth) || 0;
          create({trigger:el, start:'top bottom', end:'bottom top', onUpdate:self => {
            el.style.transform = `translate3d(0,${(self.progress - .5) * depth * 600}px,${self.progress * depth * 150}px)`;
          }});
        });
        if (memory && track) {
          const distance = () => Math.max(0, track.scrollWidth - innerWidth);
          const setHeight = () => { memory.style.height = `${innerHeight + distance()}px`; };
          setHeight();
          create({id:'spiritual-memories', trigger:memory, start:'top top', end:'bottom bottom',
            onRefreshInit:setHeight, onUpdate:self => { track.style.transform = `translate3d(${-distance() * self.progress}px,0,0)`; },
            onRefresh:self => { track.style.transform = `translate3d(${-distance() * self.progress}px,0,0)`; }
          });
        }
        if (values && valuePanels.length) {
          const update = self => {
            const position = self.progress * valuePanels.length;
            const active = Math.min(valuePanels.length - 1, Math.floor(position));
            main.querySelectorAll('.sl-value-nav a').forEach((a, i) => {
              if (i === active) a.setAttribute('aria-current', 'step');
              else a.removeAttribute('aria-current');
            });
            valuePanels.forEach((el, i) => {
              const local = position - i;
              const current = active === i;
              el.style.visibility = current ? 'visible' : 'hidden';
              el.style.opacity = current ? String(i === valuePanels.length - 1 ? 1 : 1 - clamp((local - .86) / .14)) : '0';
              el.style.transform = current ? `translate3d(0,0,${-50 + clamp(local) * 100}px)` : 'translate3d(0,0,-100px)';
              el.inert = !current;
            });
          };
          valueTrigger = create({id:'spiritual-values', trigger:values,start:'top top',end:'bottom bottom',onUpdate:update,onRefresh:update});
          update(valueTrigger);
        }
      }
      const reflection = main.querySelector('.sl-reflection');
      const image = main.querySelector('.sl-reflection__image');
      if (reflection && image) create({trigger:reflection, start:'top bottom',end:'top 15%',onUpdate:self => {
        image.style.transform = `scale(${.86 + self.progress * .14})`;
      }});
      const finale = main.querySelector('.sl-return');
      const rings = main.querySelector('.sl-return__rings');
      if (finale && rings) create({trigger:finale,start:'top bottom',end:'center center',onUpdate:self => {
        rings.style.opacity = String(.05 + self.progress * .12);
        rings.style.transform = `translateY(-50%) rotate(${(1-self.progress)*-12}deg) scale(${.83+self.progress*.17})`;
      }});
    }
    window.__spiritualBodyReady = true;
    document.body.dataset.spiritualBody = animated() ? 'ready' : 'static';
    window.ScrollTrigger?.refresh();
    queue();
  }
  function resolve(hash) {
    try { return document.getElementById(decodeURIComponent(hash.replace(/^#/,''))); } catch { return null; }
  }
  function openParents(target) {
    let item = target;
    while (item && item !== main) { if (item.tagName === 'DETAILS') item.open = true; item = item.parentElement; }
  }
  function go(hash, push = false, focus = false) {
    const target = resolve(hash);
    if (!target) return;
    openParents(target);
    window.ScrollTrigger?.refresh();
    const valueIndex = valuePanels.findIndex(el => el === target || el.contains(target));
    let top = target.getBoundingClientRect().top + scrollY - 95;
    if (valueIndex >= 0 && valueTrigger) top = valueTrigger.start + (valueTrigger.end-valueTrigger.start) * (valueIndex+.24)/valuePanels.length;
    if (target.id === 'top') top = 0;
    if (push && location.hash !== hash) history.pushState(null, '', hash);
    const done = () => {
      if (!focus) return;
      const existed = target.hasAttribute('tabindex');
      if (!existed) target.tabIndex = -1;
      target.focus({preventScroll:true});
      if (!existed) target.addEventListener('blur', () => target.removeAttribute('tabindex'), {once:true});
    };
    const event = new CustomEvent('cirs-section-scroll', {cancelable:true,detail:{top:Math.max(0,top),duration:reduced.matches?0:.75,onComplete:done}});
    if (window.dispatchEvent(event)) { window.scrollTo({top:Math.max(0,top),behavior:'instant'}); done(); }
  }
  function click(event) {
    const link = event.target.closest('a[href^="#"]');
    if (!link || !main.contains(link) || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    if (!resolve(link.hash)) return;
    event.preventDefault(); event.stopImmediatePropagation(); go(link.hash, true, true);
  }
  function hashChange() { if (location.hash) go(location.hash); }
  function sharedHash(event) {
    const target = event.detail?.target;
    if (!target || !main.contains(target)) return;
    // Sticky chapters need their timeline position, not their current box.
    event.preventDefault();
    go('#' + target.id);
  }
  function toggle(event) {
    if (event.target.tagName !== 'DETAILS') return;
    clearTimeout(timer); timer = setTimeout(() => { window.ScrollTrigger?.refresh(); queue(); }, 80);
  }
  function resize() {
    clearTimeout(timer); timer = setTimeout(() => { window.ScrollTrigger?.refresh(); queue(); }, 150);
  }
  function focusIn(event) {
    const panel = event.target.closest('.sl-memory');
    const trigger = window.ScrollTrigger?.getById('spiritual-memories');
    if (!panel || !trigger) return;
    const rect = event.target.getBoundingClientRect();
    if (rect.left >= 0 && rect.right <= innerWidth) return;
    const distance = Math.max(1, track.scrollWidth - innerWidth);
    const top = trigger.start + (trigger.end-trigger.start) * clamp(panel.offsetLeft/distance);
    const request = new CustomEvent('cirs-section-scroll', {cancelable:true,detail:{top,duration:.5}});
    if (window.dispatchEvent(request)) window.scrollTo({top,behavior:'instant'});
  }
  function show(event) { if (event.persisted) { window.ScrollTrigger?.refresh(); queue(); } }
  try { configure(); } catch {
    reset(); root.classList.remove('sl-body-motion'); document.body.dataset.spiritualBody = 'static';
  }
  window.addEventListener('scroll', queue, {passive:true});
  window.addEventListener('resize', resize);
  window.addEventListener('hashchange', hashChange);
  window.addEventListener('cirs-hash-open', sharedHash);
  window.addEventListener('popstate', hashChange);
  window.addEventListener('pageshow', show);
  document.addEventListener('click', click, true);
  main.addEventListener('toggle', toggle, true);
  main.addEventListener('focusin', focusIn);
  reduced.addEventListener('change', configure);
  desktop.addEventListener('change', configure);
  document.fonts?.ready.then(() => { window.ScrollTrigger?.refresh(); if (location.hash) go(location.hash); });
  window.addEventListener('pagehide', event => {
    cancelAnimationFrame(frame); frame = 0;
    if (event.persisted) return;
    reset(); clearTimeout(timer);
    window.removeEventListener('scroll', queue); window.removeEventListener('resize', resize);
    window.removeEventListener('hashchange', hashChange); window.removeEventListener('popstate', hashChange); window.removeEventListener('pageshow', show);
    window.removeEventListener('cirs-hash-open', sharedHash);
    document.removeEventListener('click', click, true); main.removeEventListener('toggle', toggle, true);
    main.removeEventListener('focusin', focusIn);
    reduced.removeEventListener('change', configure); desktop.removeEventListener('change', configure);
  });
})();
