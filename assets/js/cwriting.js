/* Creative Writing: a student literary journal.
   The page is complete without this file: every edition, poem, link and
   download is in the HTML. This adds, in order of the page:
     "Another line": a second student's line in the hero, swapped in place
     the hero's two words parting on the first scroll (wide, tall windows)
     the editions as two opposing waves around a sticky preview (the same)
     opening an edition: the chosen title carries over to its page
     one sliced word, once
     on an edition, a small "which poem" mark and focus that follows a link
   The shared script (cirs.js) owns GSAP's registration and Lenis; nothing
   here creates a second scroll engine, pins for more than a short hold, or
   listens to the wheel. Reading, on an edition page, has no motion at all.
   The two media queries are the ones head_html() in creativewriting.py
   marks <html> with before first paint; keep them in step. */
(function () {
  "use strict";

  var body = document.body;
  if (!body || !body.classList.contains("cwriting")) return;
  window.__cwBooted = true;

  var root = document.documentElement;
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var SPLIT = "(min-width:900px) and (min-height:620px) and (prefers-reduced-motion:no-preference)";
  // A wave of faded titles is not for a reader who asked for more contrast.
  var WAVE = "(min-width:1100px) and (min-height:620px) and (prefers-reduced-motion:no-preference)" +
             " and (prefers-contrast:no-preference) and (forced-colors:none)";

  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function make(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }

  /* ---------------------------------------------------------- old addresses */
  /* The anthology's #poem-… and #chapter-… addresses, sent to where they went. */
  function legacy() {
    var h = window.location.hash.slice(1);
    if (!/^(poem|chapter)-[a-z0-9-]+$/.test(h)) return;
    var t = $("template[data-cw-legacies]");
    if (!t) return;
    var a = t.content.querySelector('[data-cw-legacy="' + h + '"]');
    if (a) window.location.replace(new URL(a.getAttribute("href"), window.location.href).href);
  }

  /* ---------------------------------------------------------- another line */
  /* One more of the students' lines, from the same stored excerpts the
     collection is built on. Author, edition and poem link come with it in
     one piece; nothing is autoplayed, timed or scrambled, and focus stays
     on the button. Without this the first line stays where it is. */
  function anotherLine() {
    var button = $("[data-cw-another]");
    var stage = $("[data-cw-stage]");
    if (!button || !stage) return;
    var pool = $$("template[data-cw-line]").map(function (t) { return t.content.firstElementChild; });
    if (pool.length < 2) return;
    var announce = $("[data-cw-announce]");
    var first = $(".cw-quote", stage);
    var current = first ? first.getAttribute("data-cw-key") : "";
    var runs = [];
    var busy = false;
    button.hidden = false;

    /* Keep the stage as tall as the tallest line so nothing below it moves. */
    function reserve() {
      var ghost = stage.cloneNode(false);
      ghost.removeAttribute("data-cw-stage");
      ghost.setAttribute("aria-hidden", "true");
      ghost.style.cssText = "position:absolute;visibility:hidden;pointer-events:none;min-height:0;width:" + stage.clientWidth + "px";
      stage.parentNode.insertBefore(ghost, stage);
      var tallest = 0;
      pool.forEach(function (q) {
        ghost.innerHTML = "";
        ghost.appendChild(q.cloneNode(true));
        tallest = Math.max(tallest, ghost.offsetHeight);
      });
      ghost.remove();
      stage.style.minHeight = Math.ceil(tallest) + "px";
    }
    reserve();
    var timer = 0;
    window.addEventListener("resize", function () {
      window.clearTimeout(timer);
      timer = window.setTimeout(reserve, 200);
    }, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(reserve);

    function pick() {
      var n = 0, q;
      do { q = pool[Math.floor(Math.random() * pool.length)]; } while (q.getAttribute("data-cw-key") === current && n++ < 30);
      return q.cloneNode(true);
    }
    function put(node) {
      stage.innerHTML = "";
      stage.appendChild(node);
      current = node.getAttribute("data-cw-key");
      var read = $("[data-cw-read]");
      if (read) read.setAttribute("href", node.getAttribute("data-cw-href"));
      if (announce) {
        var text = $$(".cw-quote__text .cw-l", node).map(function (l) { return l.textContent; }).join(" ");
        announce.textContent = "Another line: " + text + ", " +
          $(".cw-quote__author", node).textContent + ", " + $(".cw-quote__edition", node).textContent + ".";
      }
    }
    function stop() { runs.forEach(function (a) { a.cancel(); }); runs = []; }

    button.addEventListener("click", function () {
      var next = pick();
      var old = $(".cw-quote", stage);
      var wasBusy = busy;
      stop();
      if (still || !old || !old.animate) { put(next); busy = false; return; }
      function enter() {
        put(next);
        var a = next.animate([{ opacity: 0, transform: "translateY(12px)" }, { opacity: 1, transform: "none" }],
                             { duration: 380, easing: "cubic-bezier(.16,1,.3,1)" });
        a.onfinish = function () { busy = false; };
        runs.push(a);
      }
      // Clicked mid-swap: no queue, straight to the newest line.
      if (wasBusy) { enter(); return; }
      busy = true;
      var out = old.animate([{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateY(-10px)" }],
                            { duration: 260, easing: "ease-in", fill: "forwards" });
      out.onfinish = enter;
      runs.push(out);
    });
  }

  /* ---------------------------------------------------------- opening an edition */
  /* A title is a real link and one click opens it. Where the browser can
     carry an element from one page to the next (cross-document view
     transitions), the chosen title is named and becomes the edition's own
     heading. Elsewhere, on the wave, the title swells, the rest let go, and
     the page follows about half a second later. Lists and phones just
     navigate. */
  function openings() {
    var carries = "onpagereveal" in window;
    function names() { $$("[data-cw-title]").forEach(function (t) { t.style.viewTransitionName = ""; }); }
    function reset() {
      names();
      $$(".cw-wave.is-leaving").forEach(function (w) { w.classList.remove("is-leaving"); });
      $$(".cw-wave__item.is-chosen").forEach(function (i) { i.classList.remove("is-chosen"); });
    }
    document.addEventListener("click", function (e) {
      if (e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var a = e.target.closest && e.target.closest("a[data-cw-open]");
      if (!a) return;
      var title = a.hasAttribute("data-cw-title") ? a : (a.querySelector("[data-cw-title]") || a.closest("[data-cw-title]"));
      if (!title) return;
      reset();
      var wave = a.closest(".cw-wave");
      var item = a.closest("[data-cw-item]");
      var waving = wave && item && root.classList.contains("cw-wave-on");
      if (carries && !still) {
        title.style.viewTransitionName = "cw-title";
        if (waving) { wave.classList.add("is-leaving"); item.classList.add("is-chosen"); }
        return;
      }
      if (still || !waving) return;
      e.preventDefault();
      wave.classList.add("is-leaving");
      item.classList.add("is-chosen");
      window.setTimeout(function () { window.location.href = a.href; }, 460);
    });
    window.addEventListener("pageshow", reset);
  }

  /* ---------------------------------------------------------- the reading */
  /* No motion. A small mark of which poem is in view, and focus that
     follows an in-page link to its heading. Back and Forward are the
     browser's own. */
  function reading() {
    var poems = $$("[data-cw-poem]");
    if (poems.length) {
      var now = $("[data-cw-now]");
      var who = $(".cw-rail__who");
      if (now && who && "IntersectionObserver" in window) {
        var seen = {};
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) { seen[en.target.id] = en.isIntersecting; });
          var here = poems.filter(function (p) { return seen[p.id]; })[0];
          if (here) {
            now.textContent = here.getAttribute("data-cw-n");
            who.textContent = here.getAttribute("data-cw-who");
          }
        }, { rootMargin: "-40% 0px -50% 0px" });
        poems.forEach(function (p) { io.observe(p); });
      }
    }
    if (!$(".cw-edition")) return;
    // The links between poems are the browser's own fragment navigation (each
    // carries the page's address, see edition_html), so the address changes
    // and Back and Forward walk the poems. All that is added is where focus goes.
    window.addEventListener("hashchange", function () {
      var id = "";
      try { id = decodeURIComponent(window.location.hash.slice(1)); } catch (err) { return; }
      var t = id && document.getElementById(id);
      var h = t && $("h2", t);
      if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
    });
  }

  /* ---------------------------------------------------------- one sliced word */
  /* "Voices" resolves once, its upper and lower halves drawn together. The
     real word stays in the heading for readers; the halves are for the eye. */
  function slice() {
    if (still || !("IntersectionObserver" in window) || !Element.prototype.animate) return;
    $$("[data-cw-slice]").forEach(function (h) {
      var text = h.textContent;
      var wrap = make("span", "cw-slice");
      wrap.setAttribute("aria-hidden", "true");
      var a = make("span", "cw-slice__a", text);
      var b = make("span", "cw-slice__b", text);
      wrap.appendChild(a); wrap.appendChild(b);
      h.textContent = "";
      h.appendChild(make("span", "sr-only", text));
      h.appendChild(wrap);
      a.style.opacity = b.style.opacity = "0";
      new IntersectionObserver(function (entries, io) {
        if (!entries[0].isIntersecting) return;
        io.disconnect();
        a.style.opacity = b.style.opacity = "";
        var opts = { duration: 800, easing: "cubic-bezier(.16,1,.3,1)", fill: "backwards" };
        a.animate([{ opacity: 0, transform: "translateX(-12%)" }, { opacity: 1, transform: "none" }], opts);
        var last = b.animate([{ opacity: 0, transform: "translateX(12%)" }, { opacity: 1, transform: "none" }], opts);
        // Resolved: the heading is simply its word again.
        last.onfinish = function () { h.textContent = text; };
      }, { threshold: 0.6 }).observe(h);
    });
  }

  /* ---------------------------------------------------------- the hero opens apart */
  /* Held for a short run (CSS sticky, so the page still scrolls
     normally): CREATIVE eases left and up, WRITING right and down, and
     "Two schools. Many voices." comes up between them. The line and the
     poem fade first. */
  function heroSplit(mm) {
    mm.add(SPLIT, function () {
      var zone = $("[data-cw-zone]");
      var hero = $("[data-cw-hero]");
      var a = $("[data-cw-a]");
      var b = $("[data-cw-b]");
      var between = $("[data-cw-between]");
      if (!zone || !hero || !a || !b || !between) return;
      root.classList.add("cw-split-on");
      var fades = $$("[data-cw-fade]", hero);
      var em = function () { return parseFloat(window.getComputedStyle(a).fontSize) || 100; };
      // How far CREATIVE may go left without touching the edge of the window.
      var room = function () {
        return Math.max(0, a.getBoundingClientRect().left - window.gsap.getProperty(a, "x") - 14);
      };
      var tl = window.gsap.timeline({
        defaults: { ease: "none" },
        scrollTrigger: {
          trigger: zone, start: "top top", end: "bottom bottom", scrub: true,
          invalidateOnRefresh: true,
          onUpdate: function (self) { hero.classList.toggle("is-past", self.progress > 0.55); }
        }
      });
      tl.to(a, {
        x: function () { return -Math.min(window.innerWidth * 0.08, room()); },
        y: function () { return -em() * 0.34; }, duration: 1
      }, 0);
      tl.to(b, {
        x: function () { return window.innerWidth * 0.08; },
        y: function () { return em() * 0.34; }, duration: 1
      }, 0);
      tl.fromTo(between, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.4 }, 0.3);
      tl.to(fades, { opacity: 0, y: -18, duration: 0.34 }, 0);
      return function () {
        hero.classList.remove("is-past");
        root.classList.remove("cw-split-on");
      };
    });
  }

  /* ---------------------------------------------------------- the wave */
  /* One finite list of real links, no clones. Each title is placed by its
     distance from the reading line (the middle of the window): the nearer,
     the fuller, larger and straighter; the farther, the fainter and the more
     it leans, the left and right columns leaning in mirror image, and the
     two columns drifting very slightly against each other. The preview in
     the middle is the active title's own text. Which title is active:
     keyboard focus, else a pointer that has rested on one, else the one on
     the reading line. */
  function wave(mm) {
    mm.add(WAVE, function () {
      var box = $("[data-cw-wave]");
      var list = box && $(".cw-wave__list", box);
      var items = list ? $$("[data-cw-item]", list) : [];
      var preview = box && $("[data-cw-preview-body]", box);
      if (!items.length || !preview) return;
      root.classList.add("cw-wave-on");

      var n = items.length;
      var left = items.map(function (it) { return it.getAttribute("data-side") === "left"; });
      var K = 0.06;                   // how far the columns drift against each other
      var cy = [], listTop = 0, unit = 100, mid = 0, vh = 0, amp = 20, centre = 0;
      var st = [];                    // per title: x, y, scale, opacity as last computed
      var scrollIdx = 0, hover = null, focus = null, active = -1;
      var intent = 0, letgo = 0;

      function measure() {
        var lr = list.getBoundingClientRect();
        listTop = lr.top + window.scrollY;
        cy = items.map(function (it) { return it.offsetTop + it.offsetHeight / 2; });
        var span = Math.max.apply(null, cy) - Math.min.apply(null, cy);
        unit = n > 1 ? Math.max(60, span / (n - 1)) : 120;
        var wr = box.getBoundingClientRect();
        centre = wr.top + window.scrollY + wr.height / 2;
        vh = window.innerHeight;
        amp = clamp(window.innerWidth * 0.017, 14, 26);
      }

      function compute() {
        mid = window.scrollY + vh / 2;
        var drift = K * (mid - centre);
        var best = -1, bestD = Infinity, cur = Infinity;
        items.forEach(function (it, i) {
          var dy = left[i] ? -drift : drift;
          var d = (listTop + cy[i] + dy - mid) / unit;
          var ad = Math.abs(d);
          var w = Math.exp(-Math.pow(ad, 1.5) / 0.9);
          var lean = Math.sin(clamp(d, -1.75, 1.75) * 0.9);
          st[i] = { x: (left[i] ? 1 : -1) * amp * lean, y: dy, s: 0.94 + 0.06 * w, o: 0.26 + 0.74 * w, d: ad };
          if (ad < bestD) { bestD = ad; best = i; }
          if (i === scrollIdx) cur = ad;
        });
        // A little hysteresis, so two titles level with the line do not trade places.
        if (best !== scrollIdx && bestD < cur - 0.12) scrollIdx = best;
      }

      function paint() {
        items.forEach(function (it, i) {
          var s = st[i];
          if (!s) return;
          it.style.transform = "translate3d(" + s.x.toFixed(1) + "px," + s.y.toFixed(1) + "px,0) scale(" + s.s.toFixed(3) + ")";
          it.style.opacity = (i === active ? 1 : Math.min(s.o, 0.55)).toFixed(2);
        });
      }

      /* -- the preview: a copy of the active title's own words */
      var shown = -1, token = 0, busy = false, runs = [];
      function fill(i) {
        var it = items[i];
        var when = $(".cw-wave__when", it);
        var frag = document.createDocumentFragment();
        var bar = make("span", "cw-preview__bar");
        bar.setAttribute("aria-hidden", "true");
        frag.appendChild(bar);
        if (when) frag.appendChild(make("p", "cw-preview__when", when.textContent));
        frag.appendChild(make("p", "cw-preview__title", $(".cw-wave__title", it).textContent));
        var detail = $("[data-cw-detail]", it).cloneNode(true);
        detail.removeAttribute("data-cw-detail");
        frag.appendChild(detail);
        preview.textContent = "";
        preview.appendChild(frag);
        preview.style.setProperty("--ed-mark", it.style.getPropertyValue("--ed-mark"));
      }
      function stop() { runs.forEach(function (a) { a.cancel(); }); runs = []; }
      function swap(i) {
        var wasBusy = busy;
        stop();
        var mine = ++token;
        if (shown < 0 || !preview.animate) { fill(i); shown = i; busy = false; return; }
        shown = i;
        function enter() {
          stop();               // a finished "out" still holds its last frame
          fill(i);
          busy = true;
          var a = preview.animate([{ opacity: 0, transform: "translateY(12px)" }, { opacity: 1, transform: "none" }],
                                  { duration: 320, easing: "cubic-bezier(.16,1,.3,1)" });
          a.onfinish = function () { if (mine === token) busy = false; };
          runs.push(a);
        }
        // Scrolling fast: nothing queues. A change mid-swap goes straight in.
        if (wasBusy) { enter(); return; }
        busy = true;
        var out = preview.animate([{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateY(-12px)" }],
                                  { duration: 140, easing: "ease-in", fill: "forwards" });
        out.onfinish = function () { if (mine === token) enter(); };
        runs.push(out);
      }

      function resolve() {
        var next = focus !== null ? focus : hover !== null ? hover : scrollIdx;
        if (next === active) return false;
        active = next;
        items.forEach(function (it, i) { it.classList.toggle("is-active", i === active); });
        swap(active);
        return true;
      }
      function frame() { compute(); resolve(); paint(); }

      /* -- pointer and keyboard */
      var offs = [];
      function on(target, type, fn, opts) {
        target.addEventListener(type, fn, opts);
        offs.push(function () { target.removeEventListener(type, fn, opts); });
      }
      items.forEach(function (it, i) {
        on(it, "pointerenter", function (e) {
          if (e.pointerType !== "mouse") return;
          window.clearTimeout(letgo);
          window.clearTimeout(intent);
          // Only a pointer that rests on a title changes the preview.
          intent = window.setTimeout(function () { hover = i; resolve(); paint(); }, 110);
        });
        on(it, "pointerleave", function (e) {
          if (e.pointerType !== "mouse") return;
          window.clearTimeout(intent);
          window.clearTimeout(letgo);
          letgo = window.setTimeout(function () { if (hover === i) { hover = null; resolve(); paint(); } }, 140);
        });
        on(it, "focusin", function () { focus = i; resolve(); paint(); });
        on(it, "focusout", function (e) {
          if (it.contains(e.relatedTarget)) return;
          if (focus === i) { focus = null; resolve(); paint(); }
        });
      });

      measure();
      frame();
      var trigger = window.ScrollTrigger.create({
        trigger: box, start: "top bottom", end: "bottom top",
        onUpdate: frame,
        onRefresh: function () { measure(); frame(); }
      });
      var ro = null;
      if ("ResizeObserver" in window) {
        ro = new ResizeObserver(function () { measure(); frame(); });
        ro.observe(list);
      }

      return function () {
        window.clearTimeout(intent);
        window.clearTimeout(letgo);
        stop();
        offs.forEach(function (off) { off(); });
        if (ro) ro.disconnect();
        trigger.kill();
        items.forEach(function (it) {
          it.style.transform = ""; it.style.opacity = ""; it.classList.remove("is-active");
        });
        preview.textContent = "";
        root.classList.remove("cw-wave-on");
      };
    });
  }

  /* ---------------------------------------------------------- boot */
  legacy();
  anotherLine();
  reading();
  openings();
  slice();

  function late() {
    var g = window.gsap, ST = window.ScrollTrigger;
    if (!g || !ST || typeof g.matchMedia !== "function") {
      // No GSAP: the page stays the plain list it was written as.
      root.classList.remove("cw-split-on", "cw-wave-on");
      return;
    }
    g.registerPlugin(ST);
    var mm = g.matchMedia();
    heroSplit(mm);
    wave(mm);
    var refresh = function () { ST.refresh(); };
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(refresh);
    window.addEventListener("load", refresh);
  }
  // cirs.js sets GSAP up on DOMContentLoaded; this runs just after it.
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", late);
  else late();
})();
