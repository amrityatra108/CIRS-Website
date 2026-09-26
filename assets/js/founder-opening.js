/* Founder opening: the four-second intro film, then the portrait.
   Adapted from the designer's Gurudev handoff (src/experience.js).

   Every fresh load and reload begins at the intro; nothing saved can skip
   it. Reduced motion goes straight to the portrait, a blocked autoplay
   offers Play, and Skip is always there. The vector GURUDEV fades in at
   3.78–3.88s on the film's own clock, so Pause and Replay keep it in step.

   What differs from the handoff: its life story was a widget with its own
   controls, which this script used to gate. Here the story is the page's
   own section below (#life, founder-gurudev-journey.js), reached by native
   scroll or by "Begin the journey", an ordinary link that cirs.js scrolls.
   So there is no story phase, and nothing is saved between visits. A visit
   that arrives at an anchor further down, or scrolls the film away, finishes
   the intro at once, so the portrait is waiting when the reader comes back. */
(() => {
  'use strict';
  const root = document.querySelector('[data-gurudev-opening]');
  const portrait = root?.__gurudevPortrait;
  if (!root || !portrait) return;

  const hero = root.querySelector('.gp-hero');
  const intro = root.querySelector('.gc-intro');
  const video = root.querySelector('.gc-intro-video');
  const skip = root.querySelector('.gc-intro-skip');
  const play = root.querySelector('.gc-intro-play');
  const pause = root.querySelector('.gc-intro-pause');
  const fallback = root.querySelector('.gc-intro-fallback');
  const status = root.querySelector('.gc-intro-status');
  const progress = root.querySelector('.gc-intro-progress span');
  const sharpTitle = root.querySelector('.gc-title-sharp');
  const begin = hero.querySelector('.gp-begin');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const skipLabel = skip.innerHTML;
  let phase = 'intro', started = false, epoch = 0, finishTimer = 0, playWatchdog = 0, videoFrame = 0;

  function setPhase(value) { phase = value; root.dataset.phase = value; }

  function updateProgress() {
    if (phase !== 'intro') return;
    const p = Number.isFinite(video.duration) && video.duration > 0
      ? Math.max(0, Math.min(1, video.currentTime / video.duration)) : 0;
    progress.style.transform = `scaleX(${p})`;
    sharpTitle.style.opacity = String(Math.max(0, Math.min(1, (video.currentTime - 3.78) / 0.10)));
    if (!video.paused) videoFrame = requestAnimationFrame(updateProgress);
  }
  function stopProgress() { cancelAnimationFrame(videoFrame); videoFrame = 0; }

  function showFallback(message, error = false) {
    if (phase !== 'intro') return;
    fallback.hidden = false; status.textContent = message; play.hidden = error; pause.hidden = true;
    skip.innerHTML = error ? 'Continue <span aria-hidden="true">&rarr;</span>' : skipLabel;
  }

  function showPortrait({ focus = false } = {}) {
    clearTimeout(finishTimer);
    portrait.activate(false); portrait.reset();
    intro.hidden = true; intro.inert = true; hero.hidden = false; hero.inert = false;
    setPhase('portrait'); portrait.activate(true);
    if (focus) begin.focus({ preventScroll: true });
  }

  function finishIntro({ instant = false } = {}) {
    if (phase !== 'intro') return;
    epoch++; clearTimeout(playWatchdog); video.pause(); stopProgress();
    const focus = intro.contains(document.activeElement);
    setPhase('leaving'); intro.inert = true; hero.hidden = false; hero.inert = true;
    portrait.activate(true);
    finishTimer = setTimeout(() => showPortrait({ focus }), instant || reduced.matches ? 0 : 550);
  }

  function attemptPlay() {
    if (phase !== 'intro') return;
    const token = ++epoch;
    started = true; fallback.hidden = true; pause.hidden = false; pause.textContent = 'Pause intro'; skip.innerHTML = skipLabel;
    video.muted = true;
    clearTimeout(playWatchdog);
    playWatchdog = setTimeout(() => {
      if (phase === 'intro' && token === epoch && video.paused) showFallback('Play the opening, or skip to the portrait.');
    }, 4500);
    try {
      const p = video.play();
      if (p?.catch) p.catch(() => { if (phase === 'intro' && token === epoch) showFallback('Play the opening, or skip to the portrait.'); });
    } catch { showFallback('Play the opening, or skip to the portrait.'); }
  }

  function beginIntro(userInitiated = false) {
    clearTimeout(finishTimer); clearTimeout(playWatchdog); stopProgress(); epoch++;
    setPhase('intro'); started = false;
    portrait.activate(false); hero.hidden = true; hero.inert = true; intro.hidden = false; intro.inert = false;
    fallback.hidden = true; play.hidden = false; pause.hidden = true;
    progress.style.transform = 'scaleX(0)'; sharpTitle.style.opacity = '0'; skip.innerHTML = skipLabel;
    if (video.readyState > 0) video.currentTime = 0;
    if (userInitiated) { attemptPlay(); skip.focus({ preventScroll: true }); return; }
    if (reduced.matches) { finishIntro({ instant: true }); return; }
    if (!('IntersectionObserver' in window)) attemptPlay();
  }

  video.addEventListener('playing', () => {
    if (phase !== 'intro') { video.pause(); return; }
    clearTimeout(playWatchdog); fallback.hidden = true; pause.hidden = false; pause.textContent = 'Pause intro';
    stopProgress(); updateProgress();
  });
  video.addEventListener('pause', () => { stopProgress(); if (phase === 'intro' && !video.ended) pause.textContent = 'Resume intro'; });
  video.addEventListener('ended', () => finishIntro());
  // A failing <source> reports on itself, not on the video, and the browser
  // then tries the next one; only the last one failing means no film.
  const lastSource = video.querySelector('source:last-of-type');
  video.addEventListener('error', event => {
    if (event.target === video || event.target === lastSource)
      showFallback('The opening is unavailable. Continue to the portrait and life story.', true);
  }, true);
  play.addEventListener('click', attemptPlay);
  pause.addEventListener('click', () => {
    if (video.paused) attemptPlay();
    else { epoch++; clearTimeout(playWatchdog); video.pause(); }
  });
  skip.addEventListener('click', () => finishIntro());
  hero.querySelector('.gp-watch').addEventListener('click', () => {
    root.scrollIntoView({ block: 'start', behavior: 'instant' });
    beginIntro(true);
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden && phase === 'intro' && !video.paused) video.pause(); });

  // The film starts once a fifth of it is on screen. Scrolled wholly away
  // before or while it plays, it finishes at once instead of playing unseen.
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      const entry = entries[entries.length - 1];
      if (phase !== 'intro' || !entry) return;
      if (!entry.isIntersecting) finishIntro({ instant: true });
      else if (entry.intersectionRatio >= 0.2 && !started && !reduced.matches) attemptPlay();
    }, { threshold: [0, 0.2] }).observe(intro);
  }

  // A reload starts at the top, at the intro — unless the address names a
  // place further down, like founder.html#life from School History.
  const deepLink = location.hash.length > 1 && location.hash !== '#top';
  if (!deepLink && 'scrollRestoration' in history) history.scrollRestoration = 'manual';
  beginIntro();
  if (deepLink) finishIntro({ instant: true });
})();
