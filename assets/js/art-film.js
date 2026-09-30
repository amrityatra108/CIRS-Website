(function () {
  'use strict';
  var hero = document.querySelector('[data-aa-video-hero]');
  if (!hero || !window.CIRSMedia) return;
  var video = hero.querySelector('video'), toolbar = hero.querySelector('[data-art-controls]');
  if (!video || !toolbar) return;
  var button = toolbar.querySelector('[data-art-mode]'), rewind = toolbar.querySelector('[data-art-rewind]');
  var status = toolbar.querySelector('[data-art-status]');
  var motion = matchMedia('(prefers-reduced-motion: reduce)');
  var seeker = window.CIRSMedia.createSeeker(video), lifecycle = window.CIRSMedia.manage(video);
  var scrollMode = false, frame = 0;
  seeker.enable(false);
  toolbar.hidden = false;
  function update() {
    frame = 0;
    if (!scrollMode || document.hidden || !isFinite(video.duration)) return;
    var box = hero.getBoundingClientRect();
    var travel = hero.offsetHeight - hero.querySelector('.aa-video-hero__frame').offsetHeight;
    seeker.seek(Math.min(1, Math.max(0, -box.top / Math.max(1, travel))) * video.duration);
  }
  function queue() { if (scrollMode && !frame) frame = requestAnimationFrame(update); }
  function top() { hero.scrollIntoView({ behavior: 'instant', block: 'start' }); }
  function setMode(value) {
    video.removeEventListener('seeked', finishRewind);
    scrollMode = value && !motion.matches;
    video.pause(); lifecycle.forget();
    seeker.enable(scrollMode);
    hero.classList.toggle('is-scroll-film', scrollMode);
    video.controls = !scrollMode;
    button.setAttribute('aria-pressed', String(scrollMode));
    status.textContent = scrollMode ? 'Scroll down to advance; scroll up to rewind.' : 'Native controls: play, pause or seek at your own pace.';
    top();
    if (window.ScrollTrigger) window.ScrollTrigger.refresh();
    queue();
  }
  button.addEventListener('click', function () { setMode(!scrollMode); });
  function finishRewind() {
    if (!scrollMode && video.readyState >= 1 && !video.seeking && video.currentTime < 0.03) {
      seeker.enable(false);
      video.removeEventListener('seeked', finishRewind);
    }
  }
  video.addEventListener('loadedmetadata', finishRewind);
  rewind.addEventListener('click', function () {
    video.pause(); lifecycle.forget();
    if (scrollMode) { top(); seeker.seek(0); }
    else {
      seeker.enable(true); seeker.seek(0);
      if (!video.seeking && video.readyState >= 1 && video.currentTime < 0.03) finishRewind();
      else video.addEventListener('seeked', finishRewind);
    }
    status.textContent = 'Back at the beginning. ' + (scrollMode ? 'Scroll to explore again.' : 'Press Play when you are ready.');
  });
  function preference() {
    button.disabled = motion.matches;
    if (motion.matches && scrollMode) setMode(false);
    if (motion.matches) status.textContent = 'Reduced motion is on. Use the native controls to play or seek.';
    else if (!scrollMode) status.textContent = 'Native controls: play, pause or seek at your own pace.';
  }
  motion.addEventListener('change', preference);
  ['loadedmetadata', 'loadeddata'].forEach(function (name) { video.addEventListener(name, queue); });
  window.addEventListener('scroll', queue, { passive: true });
  window.addEventListener('resize', queue, { passive: true });
  document.addEventListener('visibilitychange', queue);
  preference();
}());
