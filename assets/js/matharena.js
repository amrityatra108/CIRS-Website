/* ============================================================
   Math Challenge — page controller
   1. The results archive: month search, division filter, count,
      empty state and Reset. The records are in the HTML; this only
      hides and shows them.
   2. The four divisions: each row is a real link to #archive; on the
      way it selects that division in the filter and says so.
   3. The stage: one progress value for the scrolled installation,
      the lettering it moves, and the optional sculpture it loads
      (math-sculpture.js). A failed sculpture leaves the plain
      opening; nothing else here depends on it.
   The shared Lenis instance in cirs.js is the only scroll engine;
   this file only reads the scroll and asks cirs.js to move it.
   ============================================================ */
(function () {
  "use strict";

  var doc = document, root = doc.documentElement;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var reducedQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var thisScript = doc.currentScript;

  window.__mcBooted = true;

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function range(p, a, b) { return clamp((p - a) / (b - a)); }
  function smooth(t) { return t * t * t * (t * (t * 6 - 15) + 10); }

  /* ==========================================================
     1. The archive
     ========================================================== */
  function initArchive() {
    var list = $("#mcMonths");
    if (!list) return null;
    var months = $$(".mc-month", list);
    var buttons = $$(".mc-filter");
    var search = $("#mcSearch");
    var count = $("#mcCount");
    var reset = $("#mcReset");
    var none = $("#mcNone");
    var noneText = $("#mcNoneText");
    var totals = months.map(function (m) { return $$(".mc-doc", m).length; });
    var state = { grade: "all", term: "" };
    var announceTimer = 0;

    function gradeName(key) {
      var b = buttons.filter(function (x) { return x.dataset.grade === key; })[0];
      return b ? b.textContent.trim() : "";
    }
    function norm(text) {
      return String(text || "").toLowerCase().replace(/[–—]/g, "-").replace(/\s+/g, " ").trim();
    }
    function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }

    function apply(opts) {
      opts = opts || {};
      var terms = state.term ? state.term.split(" ") : [];
      var shown = 0, monthsShown = 0;
      months.forEach(function (m, i) {
        var find = m.dataset.find || "";
        var termOk = terms.every(function (t) { return find.indexOf(t) !== -1; });
        var n = 0;
        $$(".mc-doc", m).forEach(function (d) {
          var ok = termOk && (state.grade === "all" || d.dataset.grade === state.grade);
          d.hidden = !ok;
          if (ok) n++;
        });
        m.hidden = n === 0;
        var meta = $(".mc-month__meta", m);
        if (meta) {
          meta.innerHTML = '<span class="mc-month__n">' + n + "</span> " +
            (n === totals[i] ? (n === 1 ? "bulletin" : "bulletins") : "of " + totals[i] + " bulletins");
        }
        if (n) { shown += n; monthsShown++; }
      });

      var filtered = state.grade !== "all" || !!state.term;
      var text;
      if (shown) {
        text = plural(shown, "bulletin", "bulletins") + " " +
          (monthsShown === 1 ? "in 1 month" : "across " + monthsShown + " months");
        if (state.grade !== "all") text += " · " + gradeName(state.grade);
        if (state.term) text += " · “" + search.value.trim() + "”";
      } else {
        text = "No published bulletins match";
      }
      none.hidden = shown !== 0;
      if (!shown && noneText) {
        var what = [];
        if (state.term) what.push("“" + search.value.trim() + "”");
        if (state.grade !== "all") what.push(gradeName(state.grade));
        noneText.textContent = "Nothing in the archive matches " + what.join(" in ") +
          ". Months and divisions appear here only when a bulletin was published.";
      }
      reset.hidden = !filtered;

      // The count is the live region. Typing would announce every
      // keystroke, so a search waits until the reader pauses.
      window.clearTimeout(announceTimer);
      if (opts.quiet) announceTimer = window.setTimeout(function () { count.textContent = text; }, 450);
      else count.textContent = text;
    }

    function setGrade(key, opts) {
      if (!buttons.some(function (b) { return b.dataset.grade === key; })) key = "all";
      state.grade = key;
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.grade === key)); });
      apply(opts);
    }
    function clear(focusTarget) {
      state.term = "";
      search.value = "";
      setGrade("all");
      if (focusTarget) focusTarget.focus();
    }

    buttons.forEach(function (b) {
      b.addEventListener("click", function () { setGrade(b.dataset.grade); });
    });
    search.addEventListener("input", function () {
      state.term = norm(search.value);
      apply({ quiet: true });
    });
    search.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && search.value) { e.preventDefault(); clear(); search.focus(); }
    });
    // Reset from the tally hides itself; the reader lands on "All divisions".
    reset.addEventListener("click", function () { clear(buttons[0]); });
    $$("[data-reset]").forEach(function (b) {
      b.addEventListener("click", function () { clear(search); });
    });

    // ?grade=9-10 opens the archive on a division; the browser may also
    // have restored a search from history.
    var params = new URLSearchParams(window.location.search);
    var asked = params.get("grade");
    if (search.value) state.term = norm(search.value);
    if (asked || state.term) setGrade(asked || "all", { quiet: true });

    return { setGrade: setGrade, buttons: buttons };
  }

  /* ==========================================================
     2. The divisions
     ========================================================== */
  function initZones(archive) {
    if (!archive) return;
    $$(".mc-zone__link").forEach(function (link) {
      // cirs.js already takes every #hash link to its section through the
      // shared scroll. This only selects the division on the way and puts
      // the keyboard on the filter it chose, without moving the page itself.
      link.addEventListener("click", function () {
        var key = link.dataset.grade;
        archive.setGrade(key);
        var pressed = archive.buttons.filter(function (b) { return b.dataset.grade === key; })[0];
        if (pressed) {
          try { pressed.focus({ preventScroll: true }); } catch (err) { pressed.focus(); }
        }
      });
    });
  }

  // Native scroll controls a decorative stack; grade links and papers never hide.
  function initGradeStack() {
    var panels = $$(".mc-grade"), blocks = $$(".mc-stack__block");
    var mode = window.matchMedia("(min-width:1000px) and (min-height:680px) and (prefers-reduced-motion:no-preference)");
    var queued = false;
    // Preserve native fragment history for these grade links. The shared site's
    // older hash-link handler otherwise scrolls without updating the URL.
    $$(".mc-grade-nav a").forEach(function (link) {
      link.addEventListener("click", function (event) {
        event.stopImmediatePropagation();
      }, true);
    });
    function paint() {
      queued = false;
      panels.forEach(function (panel, i) {
        var p = mode.matches ? clamp((window.innerHeight * .8 - panel.getBoundingClientRect().top) / (window.innerHeight * .4)) : 1;
        blocks[i].style.opacity = p.toFixed(3);
        blocks[i].style.transform = mode.matches ? "translateY(" + ((1-p)*-64).toFixed(2) + "px) rotateY(-9deg) scale(" + (.96+.04*p).toFixed(3) + ")" : "none";
      });
    }
    function queue() { if (!queued) { queued = true; requestAnimationFrame(paint); } }
    window.addEventListener("scroll", queue, {passive:true});
    window.addEventListener("resize", queue, {passive:true});
    window.addEventListener("pageshow", queue);
    mode.addEventListener("change", queue);
    paint();
  }

  /* ==========================================================
     3. Headings that ride out of their masks, once
     ========================================================== */
  function initReveals() {
    var heads = $$(".mc-h2");
    if (!root.classList.contains("mc-motion") || !heads.length) return;
    if (!("IntersectionObserver" in window)) {
      heads.forEach(function (h) { h.classList.add("is-in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-in");
        io.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    heads.forEach(function (h) { io.observe(h); });
  }

  /* ==========================================================
     4. The stage
     ========================================================== */
  function initStage() {
    var stage = $(".mc-stage");
    if (!stage) return;
    var view = $(".mc-stage__view", stage);
    var art = $("#mcArt");
    var canvas = $(".mc-art__canvas", art);
    var fallback = $(".mc-art__fallback", art);
    var pulse = $("#mcPulse");
    var open = $(".mc-open", stage);
    var progress = 0, queued = false, failed = false, sculpture = null;
    var selectedProgress = null, lastScrollProgress = 0;
    var shapes = $$("[data-mc-shape]", stage), states = $(".mc-states", stage);
    var listeners = [];
    var lastState = -1, lastDark = null, lastPast = null;

    // Kinetic only where motion is allowed, WebGL exists and the window is
    // tall enough to compose the pinned stage in. The head script made the
    // same decision before first paint; this keeps it as the window changes.
    function wantKinetic() {
      return !failed && !reducedQuery.matches && "WebGLRenderingContext" in window && window.innerHeight >= 500 && window.innerWidth > 760 && !window.matchMedia("(max-aspect-ratio:4/5)").matches;
    }
    function kinetic() { return root.classList.contains("mc-kinetic"); }

    function read() {
      if (!kinetic()) return 0;
      var r = stage.getBoundingClientRect();
      var length = r.height - view.offsetHeight;
      return length > 0 ? clamp(-r.top / length) : 0;
    }

    function paint() {
      queued = false;
      var p = read();
      if (Math.abs(p - lastScrollProgress) > .005) selectedProgress = null;
      lastScrollProgress = p;
      progress = selectedProgress === null ? p : selectedProgress;
      // The wide field has its own clear stage. Cube and torus retain the opening.
      view.classList.toggle("is-field", progress >= .18 && progress < .62);
      open.inert = progress >= .18 && progress < .62;
      shapes.forEach(function (b, i) { b.setAttribute("aria-pressed", String(i === (progress < .33 ? 0 : progress < .62 ? 1 : 2))); });
      var s = view.style;
      if (kinetic()) {
        // The same windows the sculpture uses (math-sculpture.js): the cube
        // is held, opens into the field (.18-.48), curls into the torus
        // (.48-.76) and settles. The lettering is staged around them so no
        // line ever sits across the edge of the purple.
        var exit = smooth(range(p, 0.15, 0.33));
        var wipe = smooth(range(p, 0.46, 0.6));
        var lead = smooth(range(p, 0.58, 0.66));
        var leadOut = smooth(range(p, 0.73, 0.79));
        var end = smooth(range(p, 0.8, 0.9));
        s.setProperty("--exit", exit.toFixed(4));
        s.setProperty("--wipe", wipe.toFixed(4));
        s.setProperty("--lead", lead.toFixed(4));
        s.setProperty("--lead-out", leadOut.toFixed(4));
        s.setProperty("--end", end.toFixed(4));
        var st = p < 0.33 ? 0 : p < 0.62 ? 1 : 2;
        if (st !== lastState) { view.dataset.state = st; lastState = st; }
        var dark = wipe > 0.5;
        if (dark !== lastDark) { view.classList.toggle("is-dark", dark); lastDark = dark; }
        var past = p > 0.3;
        if (past !== lastPast) { view.classList.toggle("is-past-open", past); lastPast = past; }
      } else if (lastState !== -1) {
        ["--exit", "--wipe", "--lead", "--lead-out", "--end"].forEach(function (k) { s.removeProperty(k); });
        view.classList.remove("is-dark", "is-past-open");
        delete view.dataset.state;
        lastState = -1; lastDark = null; lastPast = null;
      }
      stage.classList.toggle("is-kinetic", kinetic());
      for (var i = 0; i < listeners.length; i++) listeners[i](progress);
    }
    function queue() {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(paint);
    }
    shapes.forEach(function (button, index) {
      button.addEventListener("click", function () {
        selectedProgress = [0, .48, .76][index];
        queue();
      });
    });

    // On a portrait screen the sculpture takes the space the lettering
    // leaves between the title and the line below it, however the title
    // wraps. Offsets, not boxes: they ignore the exit transforms.
    var portraitQuery = window.matchMedia("(max-width: 760px), (max-aspect-ratio: 4/5)");
    var title = $(".mc-title", stage), copy = $(".mc-open__copy", stage);
    function fitArt() {
      if (!kinetic() || !portraitQuery.matches) {
        view.style.removeProperty("--art-y");
        view.style.removeProperty("--art-size");
        return;
      }
      var top = open.offsetTop + title.offsetTop + title.offsetHeight;
      var bottom = open.offsetTop + copy.offsetTop;
      var gap = bottom - top;
      var size = Math.max(140, Math.min(view.offsetWidth * 0.86, gap - 12));
      view.style.setProperty("--art-y", Math.round(top + gap / 2) + "px");
      view.style.setProperty("--art-size", Math.round(size) + "px");
    }

    function setMode() {
      var want = wantKinetic();
      if (want !== kinetic()) {
        root.classList.toggle("mc-kinetic", want);
        if (window.ScrollTrigger) window.ScrollTrigger.refresh();
      }
      fitArt();
      queue();
      modeListeners.forEach(function (fn) { fn(); });
    }
    var modeListeners = [];
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(setMode);

    window.addEventListener("scroll", queue, { passive: true });
    window.addEventListener("resize", setMode, { passive: true });
    window.addEventListener("pageshow", setMode);
    if (reducedQuery.addEventListener) reducedQuery.addEventListener("change", setMode);
    setMode();

    // A link in the opening, reached by Tab after the lettering has left,
    // brings the opening back rather than focusing something unseen. The
    // return is all but immediate: the shared scroll holds a lock while it
    // moves, and an Enter pressed during a longer glide would be lost.
    open.addEventListener("focusin", function () {
      if (!kinetic() || progress < 0.08) return;
      var top = stage.getBoundingClientRect().top + window.scrollY;
      var handled = !window.dispatchEvent(new CustomEvent("cirs-section-scroll", {
        cancelable: true, detail: { top: top, duration: 0.05 }
      }));
      if (!handled) window.scrollTo(0, top);
    });

    // The sculpture is optional. Import it only where it can be drawn.
    function fail() {
      failed = true;
      art.classList.remove("is-live");
      if (pulse) pulse.hidden = true;
      if (states) states.hidden = true;
      setMode();
    }
    var api = {
      stage: stage, view: view, art: art, canvas: canvas, fallback: fallback, pulse: pulse,
      progress: function () { return progress; },
      kinetic: kinetic,
      reduced: function () { return reducedQuery.matches; },
      onProgress: function (fn) { listeners.push(fn); },
      onMode: function (fn) { modeListeners.push(fn); },
      fail: fail
    };
    if (!("WebGLRenderingContext" in window) || !canvas) { fail(); return; }
    var src = thisScript && thisScript.src ? thisScript.src : "assets/js/matharena.js";
    var url = new URL("math-sculpture.js" + (src.indexOf("?") > -1 ? src.slice(src.indexOf("?")) : ""), src).href;
    import(url).then(function (mod) {
      sculpture = mod.mount(api);
      if (!sculpture) fail();
      else if (states) states.hidden = false;
    }).catch(function (err) {
      if (window.console) console.warn("Math Challenge: the sculpture could not start.", err);
      fail();
    });
  }

  function boot() {
    initZones(initArchive());
    initGradeStack();
    initReveals();
    initStage();
  }
  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
})();
