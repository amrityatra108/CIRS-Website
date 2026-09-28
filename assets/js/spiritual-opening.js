/* One Three.js scene and one ScrollTrigger. The shared CIRS Lenis instance
   remains the sole smooth-scroll controller. Layout works without this file. */
import { createSpiritualScene } from './spiritual-light.js';

function initSpiritualOpening() {
  const hero = document.querySelector('.sl-entry');
  if (!hero || hero.dataset.initialized) return;
  hero.dataset.initialized = 'true';
  const root = document.documentElement;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const compact = matchMedia('(max-width: 767px), (pointer: coarse)');
  const canvas = hero.querySelector('canvas');
  const stage = hero.querySelector('.sl-entry__stage');
  const photo = hero.querySelector('.sl-entry__photo');
  const photoImage = photo.querySelector('img');
  const copy = hero.querySelector('.sl-entry__copy');
  const landing = hero.querySelector('.sl-entry__landing');
  const edge = hero.querySelector('.sl-entry__edge');
  let scene = null, trigger = null, raf = 0, visible = true, progress = 0;
  let pointerX = 0, pointerY = 0, lastFrame = 0, contextTimer = 0;
  const clamp = (n) => Math.max(0, Math.min(1, n));
  const range = (p, a, b) => clamp((p - a) / (b - a));
  function paint() {
    // Keep the aperture close to the projected inner ring as the camera enters.
    const reveal = range(progress, .23, .76);
    photo.style.opacity = String(range(progress, .22, .42));
    photo.style.clipPath = `circle(${reveal * 76}% at 50% 50%)`;
    photoImage.style.transform = `scale(${1.06 - reveal * .06})`;
    copy.style.opacity = String(1 - range(progress, .16, .34));
    copy.style.transform = `translateY(${-range(progress, .16, .4) * 30}px)`;
    copy.style.visibility = progress > .4 ? 'hidden' : 'visible';
    edge.style.opacity = String(1 - range(progress, .12, .25));
    const arrived = range(progress, .77, .94);
    landing.style.opacity = String(arrived);
    landing.style.visibility = arrived > 0 ? 'visible' : 'hidden';
    canvas.style.opacity = String(1 - range(progress, .83, .98));
    hero.style.setProperty('--sl-progress', progress.toFixed(4));
  }
  function frame(time) {
    raf = 0;
    if (!scene || !visible || document.hidden || canvas.dataset.webgl === 'lost') return;
    // Touch devices render at 30fps; their document scroll remains native.
    if (!compact.matches || time - lastFrame > 31) {
      scene.render(motion.matches ? 0 : progress, time * .001, pointerX, pointerY);
      lastFrame = time;
    }
    if (!motion.matches && progress < .98) raf = requestAnimationFrame(frame);
  }
  function wake() { if (!raf && visible && !document.hidden) raf = requestAnimationFrame(frame); }
  function pointer(event) {
    if (compact.matches || event.pointerType !== 'mouse') return;
    pointerX = event.clientX / innerWidth * 2 - 1;
    pointerY = event.clientY / innerHeight * 2 - 1;
  }
  function resetPointer() { pointerX = pointerY = 0; }
  function resize() { scene?.resize(); wake(); }
  function visibility() {
    if (document.hidden) { cancelAnimationFrame(raf); raf = 0; }
    else wake();
  }
  function motionChanged() {
    cancelAnimationFrame(raf); raf = 0;
    scene?.destroy();
    try { scene = createSpiritualScene(canvas, { compact: compact.matches, reducedMotion: motion.matches }); }
    catch { scene = null; }
    hero.classList.toggle('is-webgl', !!scene);
    hero.dataset.renderer = scene ? 'three' : 'fallback';
    configure();
    window.ScrollTrigger?.refresh();
  }
  function configure() {
    trigger?.kill(); trigger = null;
    if (!scene || canvas.dataset.webgl === 'lost' || motion.matches || !window.ScrollTrigger) {
      root.classList.remove('sp-boot');
      [photo, photoImage, copy, landing, edge, canvas].forEach(el => el.removeAttribute('style'));
    } else {
      root.classList.add('sp-boot');
      trigger = window.ScrollTrigger.create({
        id: 'spiritual-opening', trigger: hero, start: 'top top', end: 'bottom bottom',
        onUpdate(self) { progress = self.progress; paint(); wake(); },
        onRefresh(self) { progress = self.progress; paint(); }
      });
      progress = trigger.progress; paint();
    }
    resize();
  }
  try { scene = createSpiritualScene(canvas, { compact: compact.matches, reducedMotion: motion.matches }); }
  catch { scene = null; }
  if (!scene) {
    root.classList.remove('sp-boot');
    hero.dataset.renderer = 'fallback';
    return;
  }
  hero.classList.add('is-webgl');
  hero.dataset.renderer = 'three';
  window.__spiritualOpeningReady = true;
  configure();
  const observer = new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    if (!visible && raf) { cancelAnimationFrame(raf); raf = 0; }
    else wake();
  });
  observer.observe(stage);
  hero.addEventListener('pointermove', pointer, { passive: true });
  hero.addEventListener('pointerleave', resetPointer);
  window.addEventListener('resize', resize);
  document.addEventListener('visibilitychange', visibility);
  motion.addEventListener('change', motionChanged);
  compact.addEventListener('change', motionChanged);
  function contextChanged() {
    // Renderer listeners can be reattached after a motion preference change.
    // Read their state after every listener has processed the context event.
    clearTimeout(contextTimer);
    contextTimer = setTimeout(() => {
      const ready = !!scene && canvas.dataset.webgl !== 'lost';
      hero.classList.toggle('is-webgl', ready);
      hero.dataset.renderer = ready ? 'three' : 'fallback';
      configure();
      window.ScrollTrigger?.refresh();
    }, 0);
  }
  canvas.addEventListener('webglcontextlost', contextChanged);
  canvas.addEventListener('webglcontextrestored', contextChanged);
  function pageShow() { resize(); trigger?.refresh(); wake(); }
  window.addEventListener('pageshow', pageShow);
  window.addEventListener('pagehide', event => {
    cancelAnimationFrame(raf); raf = 0;
    clearTimeout(contextTimer);
    if (event.persisted) return;
    observer.disconnect(); trigger?.kill(); scene?.destroy();
    hero.removeEventListener('pointermove', pointer);
    hero.removeEventListener('pointerleave', resetPointer);
    window.removeEventListener('resize', resize);
    window.removeEventListener('pageshow', pageShow);
    document.removeEventListener('visibilitychange', visibility);
    motion.removeEventListener('change', motionChanged);
    compact.removeEventListener('change', motionChanged);
    canvas.removeEventListener('webglcontextlost', contextChanged);
    canvas.removeEventListener('webglcontextrestored', contextChanged);
  });
  document.fonts?.ready.then(() => trigger?.refresh());
  wake();
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initSpiritualOpening, { once:true });
else initSpiritualOpening();
