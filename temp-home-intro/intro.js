(function () {
  'use strict';
  const root = document.documentElement;
  const cover = document.querySelector('[data-home-intro]');
  const video = cover.querySelector('video');
  const hero = document.querySelector('.hero__still');
  const skip = cover.querySelector('button');
  const controller = new AbortController();
  const timers = [];
  const handoffTime = 5.70;
  let finished = false, started = false, entrance = function () {}, lenis;
  const delay = (fn, ms) => timers.push(setTimeout(fn, ms));
  const listen = (target, event, fn) => target.addEventListener(event, fn, {signal: controller.signal});
  const ready = hero.decode ? hero.decode().catch(function () {}) : Promise.resolve();
  async function finish(reason) {
    if (finished) return;
    finished = true;
    timers.forEach(clearTimeout);
    controller.abort();
    video.pause();
    await Promise.race([ready, new Promise(resolve => setTimeout(resolve, 700))]);
    const focusInCover = cover.contains(document.activeElement);
    entrance();
    cover.classList.add('is-leaving');
    try { sessionStorage.setItem('cirsHomeIntroSeen', '1'); } catch (_) {}
    setTimeout(function () {
      root.classList.remove('intro-active');
      document.body.classList.remove('is-locked');
      if (lenis) lenis.start();
      cover.remove();
      video.removeAttribute('src');
      video.replaceChildren();
      video.load();
      root.dataset.introResult = reason;
      if (focusInCover) {
        const heading = document.querySelector('h1');
        heading.setAttribute('tabindex', '-1');
        heading.focus({preventScroll: true});
      }
      if (window.ScrollTrigger) ScrollTrigger.refresh();
    }, matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 350);
  }
  window.cirsTempFinish = finish;
  window.cirsTempIntro = function (done, scroll) {
    if (started) return;
    started = true; entrance = done; lenis = scroll;
    if (finished) { done(); return; }
    if (!root.classList.contains('intro-active')) { cover.remove(); done(); return; }
    document.body.classList.add('is-locked');
    if (lenis) lenis.stop();
    listen(skip, 'click', () => finish('skip'));
    listen(document, 'keydown', e => { if (e.key === 'Escape') finish('escape'); });
    listen(document, 'visibilitychange', () => { if (document.hidden) finish('hidden'); });
    listen(window, 'pagehide', () => finish('pagehide'));
    listen(window, 'resize', () => finish('resize'));
    listen(matchMedia('(prefers-reduced-motion: reduce)'), 'change', e => { if (e.matches) finish('reduced-motion'); });
    const mobile = matchMedia('(max-width: 767px)').matches;
    const sources = mobile ? [cover.dataset.mobileWebm, cover.dataset.mobileMp4] : [cover.dataset.webm, cover.dataset.mp4];
    sources.forEach((src, i) => {
      if (!src) return;
      const source = document.createElement('source');
      source.src = src; source.type = i === 0 ? 'video/webm' : 'video/mp4';
      video.appendChild(source);
    });
    if (!sources.some(Boolean)) {
      // Explicit still placeholder; no imitation of missing construction footage.
      delay(() => finish('placeholder'), 1200);
      return;
    }
    video.hidden = false;
    video.poster = cover.querySelector('.home-intro__poster').src;
    let playbackStarted = false;
    let stallTimer = 0;
    const clearStall = () => { clearTimeout(stallTimer); stallTimer = 0; };
    const startPlayback = () => {
      if (playbackStarted || finished) return;
      playbackStarted = true;
      cover.classList.add('is-ready');
      video.play().catch(() => finish('play-rejected'));
    };
    listen(video, 'canplay', startPlayback);
    listen(video, 'playing', clearStall);
    listen(video, 'waiting', () => {
      clearStall();
      stallTimer = setTimeout(() => finish('stalled'), 1200);
    });
    listen(video, 'ended', () => finish('ended'));
    listen(video, 'error', () => finish('error'));
    listen(video, 'timeupdate', () => { if (video.currentTime >= handoffTime) finish('handoff'); });
    delay(() => { if (!playbackStarted) finish('startup-timeout'); }, 2500);
    video.load();
    if (video.readyState >= 3) startPlayback();
  };
  // Shared boot intentionally bypasses its animated branch for reduced motion.
  if (!root.classList.contains('intro-active')) cover.remove();
})();
