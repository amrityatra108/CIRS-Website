/* The CIRS experience — one school day, both schools at once.

   The page is complete without this file: the day is written as twelve
   events, in order, each with the Junior and Senior timings it covers
   (tools/experience.py). On a window wide and tall enough for it, this turns
   the same markup into a pinned stage: the event in the middle, each school's
   own times beside it, and the whole day as two thin lanes underneath with
   the current event lit in both. Scrolling moves from one event to the next;
   the photograph changes with the event.

   It owns no smooth scrolling of its own. The position comes from
   ScrollTrigger's lifecycle when the site's GSAP is loaded (Lenis feeds it),
   otherwise from a single rAF-throttled scroll listener. Moves requested by
   the buttons go through the shared "cirs-section-scroll" event, so Lenis
   lands them when it is running. */
(function () {
  "use strict";

  var root = document.querySelector(".xd");
  if (!root) return;
  var run = root.querySelector("[data-xd-run]");
  var live = root.querySelector("[data-xd-live]");
  var nav = root.querySelector("[data-xd-nav]");
  var status = document.querySelector("[data-xd-status]");
  if (!run || !live || !nav) return;

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var wide = window.matchMedia("(min-width: 900px) and (min-height: 600px)");
  var hasST = typeof window.gsap !== "undefined" && typeof window.ScrollTrigger !== "undefined";

  var $ = function (sel, ctx) { return (ctx || root).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || root).querySelectorAll(sel)); };

  var FIRST = Number(run.dataset.first), LAST = Number(run.dataset.last);

  /* ---------- The day, read back from the page ---------- */
  var events = $$(".xp").map(function (li) {
    var track = function (side) { return $('[data-track="' + side + '"]', li); };
    var slots = function (side) {
      return $$("li[data-start]", track(side)).map(function (s) {
        return { start: Number(s.dataset.start), end: Number(s.dataset.end), kind: s.dataset.kind,
                 what: $(".xp__what", s).textContent };
      });
    };
    return {
      el: li,
      scene: li.dataset.scene || "",
      same: li.hasAttribute("data-same"),
      title: $(".xp__title", li).textContent,
      gap: $(".xp__gap", li).textContent,
      line: $(".xp__line", li).textContent,
      body: { junior: $("[data-body]", track("junior")), senior: $("[data-body]", track("senior")) },
      slots: { junior: slots("junior"), senior: slots("senior") }
    };
  });
  var N = events.length;

  var figures = {};
  $$(".xp__photo").forEach(function (fig) { figures[fig.dataset.scene] = fig; });

  function hm(t) {
    var h = Math.floor(t / 60), m = t - h * 60;
    return { c: ((h + 11) % 12 + 1) + ":" + (m < 10 ? "0" : "") + m, p: h < 12 ? "am" : "pm" };
  }
  function range(a, b) {
    var x = hm(a), y = hm(b);
    return x.p === y.p ? x.c + "–" + y.c + " " + y.p : x.c + " " + x.p + " – " + y.c + " " + y.p;
  }

  /* ---------- The stage ---------- */
  var cards = { junior: $('[data-card="junior"] [data-body]', live), senior: $('[data-card="senior"] [data-body]', live) };
  var countEl = $("[data-count]", live), titleEl = $("[data-title]", live);
  var gapEl = $("[data-gap]", live), lineEl = $("[data-line]", live), captionEl = $("[data-caption]", live);
  var ribbons = $("[data-ribbons]", live);
  var jumps = $$("[data-go]", nav), stepBtns = $$("[data-step]", nav);
  var stage = $("[data-xd-stage]");

  // The tint over the photographs follows the hour the Junior event starts:
  // before light, day, the warmer end of the afternoon, dusk and night. One
  // purple family throughout, lightest by day; the photographs carry the colour.
  var SKY = [
    [290, [22, 16, 30], .9], [350, [30, 22, 38], .78], [440, [36, 27, 46], .6],
    [560, [40, 31, 50], .46], [900, [40, 31, 50], .46], [1040, [52, 34, 50], .52],
    [1110, [44, 28, 48], .64], [1200, [30, 22, 38], .76], [1290, [22, 16, 30], .86],
    [1350, [16, 11, 22], .93]
  ];
  function sky(t) {
    var k = 0;
    while (k < SKY.length - 2 && t > SKY[k + 1][0]) k++;
    var a = SKY[k], b = SKY[k + 1];
    var f = Math.max(0, Math.min(1, (t - a[0]) / (b[0] - a[0])));
    var rgb = a[1].map(function (c, n) { return Math.round(c + (b[1][n] - c) * f); });
    return { rgb: rgb.join(" "), a: (a[2] + (b[2] - a[2]) * f).toFixed(3) };
  }

  var segs = [];
  function buildRibbons() {
    if (ribbons.dataset.built) return;
    ribbons.dataset.built = "1";
    events.forEach(function (ev, k) {
      ["junior", "senior"].forEach(function (side) {
        ev.slots[side].forEach(function (s) {
          var seg = document.createElement("span");
          seg.className = "xd__seg";
          seg.dataset.lane = side;
          seg.dataset.kind = s.kind;
          seg.dataset.event = String(k);
          seg.style.left = ((s.start - FIRST) / (LAST - FIRST) * 100) + "%";
          seg.style.width = ((s.end - s.start) / (LAST - FIRST) * 100) + "%";
          ribbons.appendChild(seg);
          segs.push(seg);
        });
      });
    });
  }

  var current = -1;

  function show(k) {
    if (k === current) return;
    current = k;
    var ev = events[k];
    countEl.textContent = (k + 1 < 10 ? "0" : "") + (k + 1);
    titleEl.textContent = ev.title;
    gapEl.textContent = ev.gap;
    lineEl.textContent = ev.line;
    ["junior", "senior"].forEach(function (side) {
      cards[side].innerHTML = ev.body[side].innerHTML;
    });
    live.classList.toggle("is-aligned", ev.same);
    var fig = ev.scene ? figures[ev.scene] : null;
    var cap = fig ? fig.querySelector("figcaption") : null;
    captionEl.textContent = cap ? "Photograph: " + cap.textContent : "";
    // This event's photograph, and its neighbours' so they are loaded before
    // they are needed. Nothing further away is drawn.
    var near = [k - 1, k, k + 1].map(function (n) { return events[n] && events[n].scene; });
    Object.keys(figures).forEach(function (key) {
      figures[key].classList.toggle("is-shown", !!fig && key === ev.scene);
      figures[key].classList.toggle("is-near", near.indexOf(key) !== -1);
    });
    segs.forEach(function (seg) { seg.classList.toggle("is-on", Number(seg.dataset.event) === k); });
    jumps.forEach(function (b, n) {
      if (n === k) { b.setAttribute("aria-current", "step"); b.tabIndex = 0; }
      else { b.removeAttribute("aria-current"); b.tabIndex = -1; }
    });
    stepBtns[0].disabled = k === 0;
    stepBtns[1].disabled = k === N - 1;
    var tone = sky(ev.slots.junior[0].start);
    stage.style.setProperty("--xd-rgb", tone.rgb);
    stage.style.setProperty("--xd-a", tone.a);
  }

  function render(p) {
    show(Math.max(0, Math.min(N - 1, Math.floor(Math.max(0, p) * N))));
  }

  /* ---------- Moving through the day ---------- */
  function runBox() {
    var box = run.getBoundingClientRect();
    var y = window.scrollY || window.pageYOffset || 0;
    return { top: box.top + y, length: Math.max(1, run.offsetHeight - window.innerHeight) };
  }
  function progressNow() {
    var b = runBox();
    return ((window.scrollY || window.pageYOffset || 0) - b.top) / b.length;
  }
  function topFor(k) {
    var b = runBox();
    return Math.round(b.top + (k + 0.5) / N * b.length);
  }

  function goTo(k, focusButton) {
    k = Math.max(0, Math.min(N - 1, k));
    var top = topFor(k);
    var event = new CustomEvent("cirs-section-scroll", { cancelable: true, detail: { top: top, duration: reduced ? 0.01 : 0.9 } });
    window.dispatchEvent(event);
    if (!event.defaultPrevented) window.scrollTo({ top: top, behavior: reduced ? "instant" : "smooth" });
    show(k);
    announce(k);
    if (focusButton) jumps[k].focus({ preventScroll: true });
  }

  function announce(k) {
    if (!status) return;
    var ev = events[k], j = ev.slots.junior, s = ev.slots.senior;
    status.textContent = (k + 1) + " of " + N + ". " + ev.title + ". Junior School: " +
      range(j[0].start, j[j.length - 1].end) + ". Senior School: " +
      range(s[0].start, s[s.length - 1].end) + ". " + ev.gap + ".";
  }

  nav.addEventListener("click", function (event) {
    var button = event.target.closest("button");
    if (!button || !nav.contains(button)) return;
    if (button.hasAttribute("data-step")) goTo(current + Number(button.dataset.step), false);
    else if (button.hasAttribute("data-go")) goTo(Number(button.dataset.go), false);
  });
  // One tab stop for the twelve steps; the arrow keys move along them.
  nav.addEventListener("keydown", function (event) {
    if (!event.target.hasAttribute("data-go")) return;
    var k = Number(event.target.dataset.go), to = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") to = k + 1;
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") to = k - 1;
    else if (event.key === "Home") to = 0;
    else if (event.key === "End") to = N - 1;
    if (to === null) return;
    event.preventDefault();
    goTo(to, true);
  });

  /* ---------- Switching the stage on and off ---------- */
  var trigger = null, listening = false, queued = false;

  function onScroll() {
    if (queued) return;
    queued = true;
    requestAnimationFrame(function () { queued = false; render(progressNow()); });
  }

  function enable() {
    root.classList.add("is-stage");
    nav.hidden = false;
    buildRibbons();
    current = -1;
    if (hasST) {
      window.gsap.registerPlugin(window.ScrollTrigger);
      // ScrollTrigger is the tick, not the ruler: while it refreshes after a
      // resize its own progress can be stale, so the page is measured.
      trigger = window.ScrollTrigger.create({
        trigger: run, start: "top top", end: "bottom bottom",
        onUpdate: function () { render(progressNow()); },
        onRefresh: function () { render(progressNow()); }
      });
      window.ScrollTrigger.refresh();
    } else if (!listening) {
      listening = true;
      window.addEventListener("scroll", onScroll, { passive: true });
    }
    render(progressNow());
  }

  function disable() {
    root.classList.remove("is-stage");
    nav.hidden = true;
    if (trigger) { trigger.kill(); trigger = null; }
    if (listening) { window.removeEventListener("scroll", onScroll); listening = false; }
    Object.keys(figures).forEach(function (key) { figures[key].classList.remove("is-shown", "is-near"); });
    if (hasST) window.ScrollTrigger.refresh();
  }

  var on = false;
  function apply() {
    if (wide.matches === on) return;
    // Keep the reader on the same event across the switch.
    var keep = on ? current : null;
    var inside = keep !== null && keep >= 0 && progressNow() >= 0 && progressNow() <= 1;
    on = wide.matches;
    if (on) enable(); else disable();
    if (!on && inside) events[keep].el.scrollIntoView({ block: "start", behavior: "instant" });
  }

  // A resize inside the stage changes its length, so the same scroll offset
  // is a different event. Hold the event the reader was on before the first
  // resize of a burst, and put them back on it once the window settles.
  var resizeTimer, hold = null;
  window.addEventListener("resize", function () {
    if (!on) return;
    if (hold === null) { var p = progressNow(); hold = { k: current, inside: p > 0 && p < 1 }; }
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(function () {
      var h = hold;
      hold = null;
      if (!on || !h || !h.inside || h.k < 0) return;
      var top = topFor(h.k);
      var event = new CustomEvent("cirs-section-scroll", { cancelable: true, detail: { top: top, duration: 0.01 } });
      window.dispatchEvent(event);
      if (!event.defaultPrevented) window.scrollTo({ top: top, behavior: "instant" });
      show(h.k);
    }, 320);
  }, { passive: true });

  if (wide.addEventListener) wide.addEventListener("change", apply);
  else if (wide.addListener) wide.addListener(apply);
  apply();
}());
