/* ============================================================
   School History — the journey
   ------------------------------------------------------------
   Progressive enhancement over the markup tools/history.py writes:
   an intro, one <section data-hj-scene> per moment, and the close.
   Every word is already in the page; this file only decides how it
   is arranged and what moves.

   FLOW  A phone, a short window, reduced motion, or a window where
         WebGL will not start: the moments stay an editorial column.
         With motion allowed, each settles as it comes into view.
   LIVE  A wide, tall window with motion allowed. history-world.js
         (Three.js, imported only here, so a phone never fetches it)
         draws the camera path behind the page, and this file drives
         it from the page's own scroll position — the one Lenis
         already smooths; nothing here intercepts the wheel or the
         touch. Each moment's text holds in its column while the
         camera moves, and each photograph's caption is placed beside
         its plate every frame.

   Scroll becomes progress P: P = k exactly when moment k's text is
   held at the middle of its stretch (k = 0 is the top of the page),
   and it runs linearly between those points. The world turns P into
   a camera pose, with its own pauses; see history-world.js.
   ============================================================ */

const root = document.documentElement;
const journey = document.querySelector(".hj");
const reduced = matchMedia("(prefers-reduced-motion: reduce)");
const wide = matchMedia("(min-width: 1000px) and (min-height: 620px)");
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const ease = (t) => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

if (journey) init();

function init() {
  const canvas = journey.querySelector(".hj-canvas");
  const scenes = [...journey.querySelectorAll("[data-hj-scene]")];
  const texts = scenes.map((s) => s.querySelector(".hj-text"));
  const endStage = journey.querySelector(".hj-end__stage");
  const endFrame = journey.querySelector(".hj-end__frame");
  const endFig = endFrame && endFrame.querySelector(".hj-fig");
  const endImg = endFig && endFig.querySelector("img");
  const indexLinks = [...journey.querySelectorAll("[data-hj-go]")];
  const figs = [...journey.querySelectorAll(".hj-plates .hj-fig")];

  let mode = "";            // "flow" | "live"
  let world = null, worldLoading = null;
  let anchors = [], vh = innerHeight;
  let pTarget = 0, pNow = 0, vel = 0, lastT = 0, raf = 0, running = false;
  let inView = true;

  /* ---- the small things every mode shares -------------------------- */
  const onScrollFlag = () => root.classList.toggle("hj-scrolled", scrollY > 40);
  addEventListener("scroll", onScrollFlag, { passive: true });
  onScrollFlag();

  // The index follows the moment being read, and appears only while the
  // journey is on screen.
  let current = -1;
  function markIndex(k) {
    if (k === current) return;
    current = k;
    // A moment without an index entry of its own (June 1996) keeps the
    // entry before it lit.
    let lit = null;
    for (const a of indexLinks) {
      const target = document.getElementById(a.dataset.hjGo);
      if (target && scenes.indexOf(target) <= k) lit = a;
    }
    indexLinks.forEach((a) => (a === lit ? a.setAttribute("aria-current", "step") : a.removeAttribute("aria-current")));
    showReading(k, indexLinks.indexOf(lit));
  }

  // The column arrangement (a phone, a narrow window, reduced motion) has
  // no index beside it, so a small line under the header names the moment
  // being read: "3 of 8 · 3 August 1993 · Gurudev attains Mahasamadhi",
  // numbered as the index of moments is.
  // It repeats what is on the page and is hidden from assistive technology.
  const reading = document.createElement("p");
  reading.className = "hj-reading";
  reading.setAttribute("aria-hidden", "true");
  journey.appendChild(reading);
  function showReading(k, n) {
    const s = scenes[k];
    if (!s || n < 0) return;
    const year = s.querySelector(".hj-year"), head = s.querySelector(".hj-head");
    reading.innerHTML = `<b>${n + 1} of ${indexLinks.length}</b><span>${year ? year.textContent.trim() : ""}</span>` +
      `<span>${head ? head.textContent.trim() : ""}</span>`;
  }
  const seen = new IntersectionObserver((entries) => {
    inView = entries[0].isIntersecting;
    root.classList.toggle("hj-inview", inView && scrollY > vh * .5);
    if (inView) kick();
  }, { rootMargin: "0px 0px -40% 0px" });
  seen.observe(journey);
  addEventListener("scroll", () => root.classList.toggle("hj-inview", inView && scrollY > vh * .5), { passive: true });

  indexLinks.forEach((a) => a.addEventListener("click", (e) => {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const k = scenes.indexOf(document.getElementById(a.dataset.hjGo));
    if (k < 0 || mode !== "live") return;       // flow: an ordinary anchor
    e.preventDefault(); e.stopPropagation();
    // No address is written: returning to a #chapter address by Back would
    // make the browser drop focus, which a record's dialog must restore.
    goTo(anchors[k + 1]);
    focusLater(texts[k]);
  }, true));

  function goTo(top, instant) {
    const ev = new CustomEvent("cirs-section-scroll", { cancelable: true,
      detail: { top: Math.round(top), duration: instant ? .01 : 1.6 } });
    if (dispatchEvent(ev)) scrollTo({ top: Math.round(top), behavior: instant ? "auto" : "smooth" });
  }
  function focusLater(el) {
    if (!el) return;
    if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
    setTimeout(() => el.focus({ preventScroll: true }), 1650);
  }

  // Keyboard: focus landing in a moment that is not the one on screen
  // brings the page to it, so nothing focusable is ever read unseen.
  journey.addEventListener("focusin", (e) => {
    if (mode !== "live") return;
    const s = e.target.closest && e.target.closest("[data-hj-scene]");
    const k = scenes.indexOf(s);
    if (k >= 0 && Math.abs(pNow - (k + 1)) > .35) goTo(anchors[k + 1], true);
  });

  /* ---- FLOW ---------------------------------------------------------- */
  let flowIO = null;
  function enterFlow() {
    mode = "flow";
    root.classList.remove("hj-live");
    root.classList.add("hj-flow");
    clearLive();
    if (!reduced.matches && "IntersectionObserver" in window) {
      flowIO = new IntersectionObserver((entries) => {
        entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("is-in"); flowIO.unobserve(en.target); } });
      }, { rootMargin: "0px 0px -18% 0px" });
      scenes.forEach((s) => flowIO.observe(s));
    } else scenes.forEach((s) => s.classList.add("is-in"));
    const idx = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) markIndex(scenes.indexOf(en.target)); });
    }, { rootMargin: "-45% 0px -45% 0px" });
    scenes.forEach((s) => idx.observe(s));
    flowIndexIO = idx;
  }
  let flowIndexIO = null;
  function leaveFlow() {
    if (flowIO) { flowIO.disconnect(); flowIO = null; }
    if (flowIndexIO) { flowIndexIO.disconnect(); flowIndexIO = null; }
    scenes.forEach((s) => s.classList.add("is-in"));
    root.classList.remove("hj-flow");
  }

  /* ---- LIVE ---------------------------------------------------------- */
  function clearLive() {
    texts.forEach((t) => { t.style.cssText = ""; t.removeAttribute("data-hidden"); });
    figs.forEach((f) => f.style.cssText = "");
    if (endFrame) endFrame.style.cssText = "";
    if (canvas) canvas.classList.remove("is-off");
  }

  async function enterLive() {
    if (!worldLoading) {
      worldLoading = import("./history-world.js")
        .then((m) => m.createWorld(canvas, plateSources(), { onDirty: () => kick(), onLost: () => enterFlow() }))
        .catch(() => null);
    }
    world = await worldLoading;
    if (!world || !wantLive()) { if (!world) enterFlow(); return; }
    leaveFlow();
    mode = "live";
    root.classList.add("hj-live");
    measure();
    landPending();
    pNow = pTarget = progress();
    frame(performance.now());
  }

  function plateSources() {
    const out = {};
    journey.querySelectorAll("[data-hj-plate]").forEach((f) => {
      const img = f.querySelector("img");
      if (!img) return;
      const set = img.getAttribute("srcset");
      // The large cut where there is one: plates are read close up.
      const lg = set && (set.split(",").map((x) => x.trim().split(" ")[0]).pop());
      out[f.dataset.hjPlate] = { url: lg || img.getAttribute("src"), ratio: img.width / img.height };
    });
    return out;
  }

  // Where each moment's text is held mid-stretch, in page scroll.
  function measure() {
    vh = innerHeight;
    anchors = [0];
    texts.forEach((t, k) => {
      const s = scenes[k];
      const h = t.offsetHeight;
      const top = clamp((vh - h) / 2, 84, vh * .3);
      t.style.setProperty("--top", top + "px");
      const sTop = s.getBoundingClientRect().top + scrollY;
      // Held from (sTop - top) until the text's foot meets the scene's.
      const start = sTop - top, end = sTop + s.offsetHeight - h - top;
      anchors.push((start + end) / 2);
    });
    if (endStage) {
      const eTop = endStage.getBoundingClientRect().top + scrollY;
      anchors.push(eTop);           // the camera arrives at the last plate
      endStage._top = eTop;
      endStage._h = endStage.offsetHeight;
    }
  }

  function progress() {
    const y = scrollY;
    const n = anchors.length;
    if (y <= anchors[0]) return 0;
    for (let k = 0; k < n - 1; k++) {
      if (y < anchors[k + 1]) return k + (y - anchors[k]) / Math.max(1, anchors[k + 1] - anchors[k]);
    }
    return n - 1;
  }

  function kick() {
    if (mode !== "live" || running) return;
    running = true;
    lastT = performance.now();
    raf = requestAnimationFrame(frame);
  }
  addEventListener("scroll", () => { if (mode === "live") { pTarget = progress(); kick(); } }, { passive: true });

  function frame(t) {
    raf = 0;
    const dt = Math.min(.05, Math.max(.001, (t - lastT) / 1000));
    lastT = t;
    pTarget = progress();
    // A little weight on top of the page's own scroll smoothing: the
    // camera follows closely and comes to rest exactly where the page is.
    const d = pTarget - pNow;
    pNow = Math.abs(d) < 1e-4 ? pTarget : pNow + d * (1 - Math.exp(-dt * 9));
    // Velocity in moments per second, smoothed; it only ever nudges.
    vel += ((d * 9) - vel) * (1 - Math.exp(-dt * 5));
    if (Math.abs(vel) < 1e-3 && d === 0) vel = 0;

    const endT = endProgress();
    const visible = inView || endT < 1.2;
    if (canvas) canvas.classList.toggle("is-off", !visible || endT >= .999);
    let busy = false;
    if (visible && endT < .999) busy = world.render(pNow, clamp(vel, -3, 3));
    const rects = world.plateRects();
    paintTexts();
    paintCaptions(rects);
    paintEnd(endT, rects);
    markIndex(Math.max(0, Math.min(scenes.length - 1, Math.round(pNow) - 1)));

    const settled = pNow === pTarget && Math.abs(vel) < 2e-3 && !busy;
    if (!settled && mode === "live") { raf = requestAnimationFrame(frame); running = true; }
    else running = false;
  }

  // Each moment's text: uncovered from the top as its stretch begins,
  // held, then let go as the camera leaves. A short dark pause between.
  function paintTexts() {
    texts.forEach((el, k) => {
      const f = pNow - (k + 1);                     // 0 = held mid-stretch
      // One moment's text at a time: the last has gone (f = .38) before
      // the next begins (f = -.42), so there is always a dark pause.
      const inn = clamp((f + .42) / .22);           // arrives -.42 .. -.20
      const out = clamp((f - .18) / .2);            // leaves   .18 ..  .38
      const o = inn * (1 - out);
      if (o <= .002) {
        if (!el.hasAttribute("data-hidden")) el.setAttribute("data-hidden", "");
        return;
      }
      el.removeAttribute("data-hidden");
      el.style.setProperty("--o", o.toFixed(3));
      el.style.setProperty("--m", (1 - ease(inn)).toFixed(3));
      el.style.setProperty("--y", (out * -14 + (1 - inn) * 10).toFixed(1));
    });
  }

  // Captions sit under their plates, at the plate's own width, and are
  // shown only while the camera is reading that moment — one at a time,
  // for the plate nearest the camera, so captions never stack.
  function paintCaptions(rects) {
    const lead = new Map();
    figs.forEach((fig) => {
      const r = rects[fig.dataset.hjPlate], s = fig.closest("[data-hj-scene]");
      if (r && r.facing && (!lead.has(s) || r.area > rects[lead.get(s).dataset.hjPlate].area)) lead.set(s, fig);
    });
    figs.forEach((fig) => {
      const r = rects[fig.dataset.hjPlate];
      const s = fig.closest("[data-hj-scene]");
      const k = scenes.indexOf(s);
      const f = pNow - (k + 1);
      const o = r && lead.get(s) === fig ? clamp((f + .36) / .2) * (1 - clamp((f - .18) / .18)) : 0;
      if (o <= .002 || !r) { fig.style.setProperty("--co", "0"); return; }
      const w = Math.max(200, Math.min(360, r.w));
      const x = Math.min(innerWidth - w - 24, r.x);
      const y = Math.min(innerHeight - 64, r.y + r.h + 14);
      fig.style.setProperty("--co", o.toFixed(3));
      fig.style.setProperty("--w", w.toFixed(0) + "px");
      fig.style.setProperty("--x", x.toFixed(1) + "px");
      fig.style.setProperty("--yy", y.toFixed(1) + "px");
    });
  }

  /* The close. When the camera reaches the last plate it stops facing it
     squarely; the page's own copy of the photograph is laid exactly over
     the plate, the plate goes, and the photograph opens out to fill the
     window. From then on it is simply the page's image. */
  function endProgress() {
    if (!endStage || endStage._top == null) return 0;
    return clamp((scrollY - endStage._top) / (vh * .75));
  }
  function paintEnd(t, rects) {
    if (!endImg) return;
    const handed = pNow >= anchors.length - 1.004;
    if (!handed) {
      endFrame.style.setProperty("--fo", "0");
      endFrame.style.setProperty("--fc", "0");
      world.showLast(true);
      return;
    }
    const r = rects["campus-band"];
    const W = innerWidth, H = innerHeight, ar = endImg.width / endImg.height;
    const cover = W / H > ar ? { w: W, h: W / ar } : { w: H * ar, h: H };
    cover.x = (W - cover.w) / 2; cover.y = (H - cover.h) / 2;
    const from = r || cover;
    const e = ease(t);
    const lerp = (a, b) => a + (b - a) * e;
    endFrame.style.setProperty("--fx", lerp(from.x, cover.x).toFixed(1) + "px");
    endFrame.style.setProperty("--fy", lerp(from.y, cover.y).toFixed(1) + "px");
    endFrame.style.setProperty("--fw", lerp(from.w, cover.w).toFixed(1) + "px");
    endFrame.style.setProperty("--fh", lerp(from.h, cover.h).toFixed(1) + "px");
    endFrame.style.setProperty("--fo", "1");
    endFrame.style.setProperty("--fc", clamp((t - .75) / .25).toFixed(3));
    world.showLast(false);
  }

  /* ---- choosing, and changing, the arrangement ----------------------- */
  function wantLive() { return !reduced.matches && wide.matches && !!canvas; }
  function evaluate() {
    if (wantLive()) { if (mode !== "live") enterLive(); else { measure(); world.resize(); kick(); } }
    else if (mode !== "flow") {
      if (raf) cancelAnimationFrame(raf);
      running = false;
      enterFlow();
    }
  }
  let rt = 0;
  addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(evaluate, 140); });
  wide.addEventListener && wide.addEventListener("change", evaluate);
  reduced.addEventListener && reduced.addEventListener("change", evaluate);
  addEventListener("load", () => {
    if (mode !== "live") return;
    measure();
    // cirs.js settles a linked address again on load; hold the moment.
    if (hashScene >= 0 && !landed) { landed = true; setTimeout(() => goTo(anchors[hashScene + 1], true), 60); }
    kick();
  });
  let landed = false;
  document.fonts && document.fonts.ready.then(() => { if (mode === "live") { measure(); kick(); } });
  addEventListener("pagehide", (e) => { if (!e.persisted && world) { world.destroy(); world = null; mode = ""; } });

  if (wantLive()) enterFlowQuietly(), enterLive();
  else enterFlow();

  // While the world loads, the column is what shows — without its
  // settle-in hiding, so nothing flashes if the switch comes quickly.
  function enterFlowQuietly() { root.classList.add("hj-flow"); scenes.forEach((s) => s.classList.add("is-in")); }

  // A link to a moment, in the live arrangement: land on its held point
  // rather than the top of its stretch. cirs.js offers every address to
  // the page before it scrolls; this claims the moments.
  let pending = -1;
  addEventListener("cirs-hash-open", (e) => {
    const k = scenes.indexOf(e.detail && e.detail.target);
    if (k < 0 || !wantLive()) return;
    e.preventDefault();
    pending = k;
    if (mode === "live") landPending();
  });
  // The address may already have been handled, in the column's layout,
  // before this module ran; the live layout moves every moment, so claim
  // it again once that layout exists.
  const hashScene = /^#chapter-[a-z]+$/.test(location.hash) ? scenes.findIndex((s) => "#" + s.id === location.hash) : -1;
  if (hashScene >= 0 && wantLive()) pending = hashScene;
  function landPending() {
    if (pending < 0) return;
    measure();
    goTo(anchors[pending + 1], true);
    pending = -1;
    // Arriving far down the page: the world starts where the page is.
    pNow = pTarget = progress();
  }

  // Development only: jump to a point of the path for screenshots.
  if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
    window.__hjGo = (p) => {
      const n = anchors.length - 1, P = clamp(p, 0, n);
      const k = Math.floor(P), f = P - k;
      goTo(k >= n ? anchors[n] : anchors[k] + (anchors[k + 1] - anchors[k]) * f, true);
    };
    window.__hjState = () => ({ mode, p: pNow, anchors: anchors.length, world: world && world.info() });
  }
}
