import { getJourneyLayout } from './journey-layout.js';
import { TIMES, clamp, timeForProgress, progressForTime, targetFrame, frameIndexForTime, captionPose, mobilePan } from './tapovan-timing.js';

// One native-scroll owner, one latest desired target, one in-flight media seek.
// Presentation is observed BEFORE currentTime changes. Confirmation never puts
// the next seek behind an arbitrary 32/75 ms timer.
const section = document.querySelector('#tapovan-journey');
const stage = section.querySelector('.tapovan-sticky');
const video = section.querySelector('.tapovan-video');
const beats = [...section.querySelectorAll('.tapovan-beat')];
const number = section.querySelector('#tapovan-number');
const counter = section.querySelector('.tapovan-progress');
const hint = section.querySelector('.tapovan-scroll-hint');
const reducedList = section.querySelector('.tapovan-reduced-list');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const mobile = matchMedia('(max-width: 700px)');
const diagnostics = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
const debugParams = new URLSearchParams(location.search);
const useVideoFrameCallback = Boolean(video.requestVideoFrameCallback) && !(diagnostics && debugParams.has('tapovanPaintFallback'));
const forceReduced = diagnostics && debugParams.has('tapovanReduced');
const abort = new AbortController(), listeners = [], samples = [];
let disposed = false, reduced = motion.matches || forceReduced, failed = false;
let nearby = false, active = false, preloaded = false, prewarmed = false;
let stream = null, timingData = null, desiredTime = TIMES[0], presentedTime = TIMES[0];
let desiredIndex = -1, requestedIndex = -1, presentedIndex = -1, activeBeat = 0;
let scrollRaf = 0, resizeRaf = 0, fallbackRaf = 0, frameCallback = 0, watchdog = 0;
let inFlight = null, seeking = false, lastPan = null, generation = 0;
let seekCount = 0, seekRecoveries = 0, longestSeekMs = 0, lastSeekMs = 0;
let lastPresentationMs = 0, presentationSource = 'poster', confirmedFrames = 0, fallbackFrames = 0;
let geometry = { tapovanStart: 0, phraseSpan: 1, bridgeEnd: 1, viewportHeight: innerHeight };
function listen(target, event, fn, options) { target.addEventListener(event, fn, options); listeners.push(() => target.removeEventListener(event, fn, options)); }
function record(type, data = {}) { if (diagnostics) { if (samples.length >= 512) samples.shift(); samples.push({ type, at: performance.now(), ...data }); } }
function canRequest() { return !disposed && !failed && !reduced && !document.hidden && (active || (nearby && !prewarmed)); }
function measure() {
  geometry = getJourneyLayout();
  requestScrollUpdate();
}
function updateMobilePan(time) {
  const pan = mobile.matches ? mobilePan(time) : .58;
  if (pan === lastPan) return;
  lastPan = pan;
  const position = `${(pan * 100).toFixed(3)}% 50%`;
  video.style.objectPosition = position;
  stage.style.backgroundPosition = position;
}
function renderPresented(time, source, metadata) {
  if (!canRequest() || !Number.isFinite(time)) return;
  presentedTime = time;
  presentedIndex = stream ? frameIndexForTime(time, stream.pts) : -1;
  presentationSource = source;
  if (source === 'video-frame') confirmedFrames++; else fallbackFrames++;
  let best = 0, bestOpacity = 0;
  for (let i = 0; i < beats.length; i++) {
    const pose = captionPose(time, i);
    beats[i].style.opacity = pose.opacity.toFixed(4);
    beats[i].style.transform = `translate3d(0,${pose.y.toFixed(3)}px,0)`;
    if (pose.opacity > bestOpacity) { best = i + 1; bestOpacity = pose.opacity; }
  }
  activeBeat = best;
  number.textContent = String(best).padStart(2, '0');
  counter.style.opacity = String(bestOpacity);
  hint.style.opacity = String((1 - Math.min(1, time / (TIMES[1] - .42))) * .65);
  section.dataset.phase = best ? 'descent' : 'arrival';
  section.dataset.step = String(best);
  updateMobilePan(time);
  if (inFlight) {
    lastPresentationMs = performance.now() - inFlight.started;
    if (presentedIndex === inFlight.index) inFlight.presented = true;
  }
  if (diagnostics) {
    section.dataset.frameSource = source;
    section.dataset.presentedTime = time.toFixed(6);
    section.dataset.presentationMs = lastPresentationMs.toFixed(2);
    record('presented', { time, index: presentedIndex, source, processingMs: metadata?.processingDuration * 1000, lag: desiredTime - time });
  }
}
function cancelFrameObservation() {
  generation++;
  if (frameCallback && video.cancelVideoFrameCallback) video.cancelVideoFrameCallback(frameCallback);
  frameCallback = 0;
  cancelAnimationFrame(fallbackRaf); fallbackRaf = 0;
}
function observeBeforeSeek() {
  if (!useVideoFrameCallback || frameCallback) return;
  const token = generation;
  frameCallback = video.requestVideoFrameCallback((_, metadata) => {
    if (token !== generation) return;
    frameCallback = 0;
    if (!canRequest()) return;
    renderPresented(metadata.mediaTime, 'video-frame', metadata);
    if (!seeking) {
      cancelAnimationFrame(fallbackRaf); fallbackRaf = 0;
      prewarmed = true;
      pumpSeek();
    } else observeBeforeSeek();
  });
}
function afterPaintFallback() {
  if (fallbackRaf) return;
  // One paint opportunity, not a fixed-rate timer. Some paused media engines
  // omit rVFC. Label this estimate honestly; it is not confirmed presentation.
  fallbackRaf = requestAnimationFrame(() => {
    fallbackRaf = 0;
    if (!canRequest() || video.seeking || video.readyState < 2) return;
    if (!inFlight?.presented) {
      const time = stream ? stream.pts[frameIndexForTime(video.currentTime, stream.pts)] : video.currentTime;
      renderPresented(time, 'paint-fallback');
    }
    prewarmed = true;
    pumpSeek();
  });
}
function clearSeek() { clearTimeout(watchdog); watchdog = 0; seeking = false; inFlight = null; }
function pumpSeek() {
  if (!canRequest() || !stream || video.readyState < 1 || seeking || video.seeking) return;
  const desired = active ? desiredTime : TIMES[0];
  const target = targetFrame(clamp(desired, 0, Math.max(0, video.duration || stream.duration)), stream);
  desiredIndex = target.index;
  if (requestedIndex === target.index) return;
  observeBeforeSeek();
  inFlight = { index: target.index, time: target.time, started: performance.now(), presented: false, recoveries: 0 };
  requestedIndex = target.index; seeking = true; seekCount++;
  try {
    video.currentTime = target.time;
    section.dataset.seekTarget = target.time.toFixed(6);
    record('request', { desiredTime, target: target.time, frame: target.index });
    clearTimeout(watchdog);
    const request = inFlight;
    const recover = () => {
      watchdog = 0;
      if (!canRequest() || inFlight !== request) return;
      seekRecoveries++; request.recoveries++;
      record('watchdog', { seeking: video.seeking, readyState: video.readyState });
      if (!video.seeking && video.readyState >= 2) { seeking = false; afterPaintFallback(); }
      else if (request.recoveries < 3) watchdog = setTimeout(recover, 1800);
      else fail('media-seek-timeout');
    };
    watchdog = setTimeout(recover, 1800);
  } catch (error) { record('error', { message: error.message }); fail('media-seek-error'); }
}
function updateFromScroll() {
  scrollRaf = 0;
  if (disposed || reduced || failed || document.hidden) return;
  desiredTime = timeForProgress((scrollY - geometry.filmStart) / geometry.phraseSpan);
  const nextActive = scrollY + geometry.viewportHeight > geometry.entryStart && scrollY < geometry.bridgeEnd;
  if (active && !nextActive) { cancelFrameObservation(); clearSeek(); }
  if (!active && nextActive) {
    // A seek may have completed while inactive. Re-synchronise once on entry.
    requestedIndex = -1;
  }
  active = nextActive;
  if (canRequest()) pumpSeek();
}
function requestScrollUpdate() { if (!scrollRaf && !disposed) scrollRaf = requestAnimationFrame(updateFromScroll); }
function scheduleMeasure() { if (!resizeRaf && !disposed) resizeRaf = requestAnimationFrame(() => { resizeRaf = 0; measure(); updateMobilePan(presentedTime); }); }
function showStaticAlternative() {
  stage.classList.add('is-reduced'); section.classList.add('is-static'); reducedList.hidden = false; video.style.opacity = '0';
  cancelFrameObservation(); clearSeek(); video.pause();
  window.dispatchEvent(new Event('cirs:tapovan-mode'));
}
function fail(reason) { if (disposed || failed) return; failed = true; section.dataset.mediaFailure = reason; showStaticAlternative(); }
function updateMotion() {
  reduced = motion.matches || forceReduced;
  if (reduced) return showStaticAlternative();
  if (!failed) {
    stage.classList.remove('is-reduced'); section.classList.remove('is-static'); reducedList.hidden = true; video.style.opacity = '';
    requestedIndex = -1; window.dispatchEvent(new Event('cirs:tapovan-mode')); measure();
  }
}
function selectStream() {
  if (!timingData || !video.currentSrc) return;
  const name = new URL(video.currentSrc).pathname.split('/').at(-1);
  stream = timingData.streams[name] || null;
  if (!stream) { fail('missing-frame-timestamps'); return; }
  section.dataset.mediaFrames = String(stream.frames);
  requestScrollUpdate();
}
const timingURL = diagnostics && debugParams.get('tapovanFail') === 'timing' ? '../assets/tapovan-missing-test.json' : '../assets/tapovan-timing.json';
fetch(new URL(timingURL, import.meta.url), { signal: abort.signal })
  .then(r => { if (!r.ok) throw Error('Timing metadata unavailable'); return r.json(); })
  .then(data => { if (!disposed) { timingData = data; selectStream(); } })
  .catch(error => { if (!disposed && error.name !== 'AbortError') fail('missing-frame-timestamps'); });
const observer = new IntersectionObserver(entries => {
  nearby = entries[0].isIntersecting;
  if (!nearby) { cancelFrameObservation(); clearSeek(); return; }
  if (!preloaded && !reduced && !failed) {
    preloaded = true; video.preload = 'auto';
    if (video.networkState === HTMLMediaElement.NETWORK_EMPTY) video.load();
  }
  requestScrollUpdate();
}, { rootMargin: `${Math.round(innerHeight * .6)}px 0px` });
observer.observe(section);
const resizeObserver = new ResizeObserver(scheduleMeasure); resizeObserver.observe(section); resizeObserver.observe(stage);
listen(window, 'scroll', requestScrollUpdate, { passive: true });
listen(window, 'resize', scheduleMeasure, { passive: true });
listen(window, 'orientationchange', scheduleMeasure, { passive: true });
listen(window, 'cirs:journey-layout', measure);
listen(video, 'loadedmetadata', () => { video.pause(); selectStream(); });
listen(video, 'loadeddata', () => { if (!reduced && !failed) video.style.opacity = ''; selectStream(); });
listen(video, 'seeked', () => {
  if (!seeking || !inFlight) return;
  clearTimeout(watchdog); watchdog = 0; seeking = false;
  lastSeekMs = performance.now() - inFlight.started; longestSeekMs = Math.max(longestSeekMs, lastSeekMs);
  record('seeked', { index: inFlight.index, ms: lastSeekMs, readyState: video.readyState });
  section.dataset.seekMs = lastSeekMs.toFixed(2); section.dataset.seekCount = String(seekCount);
  if (!canRequest()) return;
  if (inFlight.presented) {
    prewarmed = true;
    if (frameCallback && video.cancelVideoFrameCallback) video.cancelVideoFrameCallback(frameCallback);
    frameCallback = 0; pumpSeek();
  } else afterPaintFallback();
});
listen(video, 'canplay', requestScrollUpdate);
listen(video, 'error', () => fail('media-error'));
const eligibleSources = [...video.querySelectorAll('source')].filter(source => !source.media || matchMedia(source.media).matches);
const sourceErrors = new Set();
for (const source of eligibleSources) listen(source, 'error', () => {
  sourceErrors.add(source);
  if (!disposed && eligibleSources.every(item => sourceErrors.has(item))) fail('media-source-error');
});
listen(document, 'visibilitychange', () => {
  if (document.hidden) { cancelFrameObservation(); clearSeek(); }
  else { requestedIndex = -1; scheduleMeasure(); }
});
listen(window, 'pageshow', () => { requestedIndex = -1; scheduleMeasure(); });
listen(motion, 'change', updateMotion);
if (document.fonts?.ready) document.fonts.ready.then(() => { if (!disposed) scheduleMeasure(); });
measure(); updateMotion();
window.__tapovan = {
  inspect: () => ({ controllerVersion: 'pts-before-seek-v2', useVideoFrameCallback, step: activeBeat, phrase: beats[activeBeat - 1]?.textContent || 'Arrival', requestedTime: desiredTime, presentedTime,
    videoTime: video.currentTime, videoPlaying: !video.paused, desiredIndex, requestedIndex, presentedIndex, presentationSource, confirmedFrames, fallbackFrames,
    seeking, seekCount, longestSeekMs: Math.round(longestSeekMs), lastSeekMs, lastPresentationMs, seekRecoveries, reduced, failed, active, nearby,
    scrollHeight: section.offsetHeight, phraseSpan: geometry.phraseSpan, summitHold: geometry.bridgeStart - geometry.holdStart, pendingFrameObservers: Number(Boolean(frameCallback)), samples: samples.length }),
  trace: () => samples.slice(),
  goToStepForReview: step => scrollTo({ top: geometry.filmStart + geometry.phraseSpan * clamp(Math.round(step), 0, 6) / 6, behavior: 'instant' }),
  seekForReview: time => scrollTo({ top: geometry.filmStart + geometry.phraseSpan * progressForTime(clamp(time, TIMES[0], TIMES[6])), behavior: 'instant' }),
  destroy: () => {
    if (disposed) return; disposed = true; abort.abort(); observer.disconnect(); resizeObserver.disconnect(); listeners.forEach(off => off());
    cancelAnimationFrame(scrollRaf); cancelAnimationFrame(resizeRaf); cancelFrameObservation(); clearSeek(); video.pause(); samples.length = 0;
  }
};
