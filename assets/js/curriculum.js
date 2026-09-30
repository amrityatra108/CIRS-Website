/* Curriculum: the Curriculum Atlas.

   The page is complete without this file: every section is ordinary
   reading order in the markup, and the stylesheet lays it out. This adds:

   - the grade journey's sticky frame (html.cur-stage), on windows at least
     1024 x 680 with motion. The stylesheet stacks the photographs in one
     sticky grid area; this decides which stage is being read, from the
     text nearest the reading line, and uncovers that stage's photograph.
     The page's own scroll does everything else; nothing is pinned here.
   - once-only entrances (html.cur-motion) for the Grade X division, the
     Diploma core's line and the school-life photographs, with motion.
   - the IB index's current group, always: it is navigation state.
   - refitting the stretched drawings to their pixels, so their strokes
     can be drawn by dash.

   Every mode is built when its media query starts to hold and taken down
   completely when it stops, so a resize across the line, or reduced motion
   switched on mid-visit, leaves the page exactly as the stylesheet draws
   it. Links use the site's own anchor handling in assets/js/cirs.js. */
(function () {
  "use strict";

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  // After the helpers above: a deferred script can run while the document
  // is still "interactive", so boot may be called at once.
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();

  /* Drawings stretched across a box of any shape (preserveAspectRatio
     none) are written in a 0-100 square. A dash measured along such a path
     is distorted by the stretch, so each is refitted to its own pixels:
     the viewBox becomes the box, and the path's points are scaled into it.
     The unscaled path is kept, so a resize refits from it. */
  function scalePath(d, sx, sy) {
    var i = 0;
    return d.replace(/[A-Za-z]|-?\d*\.?\d+/g, function (t) {
      if (/[A-Za-z]/.test(t)) { i = 0; return t; }
      return String(Math.round(parseFloat(t) * (i++ % 2 ? sy : sx) * 100) / 100);
    });
  }
  function fitStretched(svg) {
    var w = svg.clientWidth, h = svg.clientHeight;
    if (!w || !h) return;
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    $$("path", svg).forEach(function (p) {
      if (!p.getAttribute("data-d")) p.setAttribute("data-d", p.getAttribute("d"));
      p.setAttribute("d", scalePath(p.getAttribute("data-d"), w / 100, h / 100));
    });
    svg.classList.add("is-fit");
  }

  /* The Grade X division is drawn from where things actually are: the
     stem down to the node, and a branch from the node to each column line
     of the comparison, which the two destinations stand on. */
  function fitDivision(div) {
    var svg = $(".atl-div__fork", div), node = $(".atl-div__node", div);
    var ends = $$(".atl-div__end a", div);
    if (!svg || !node || ends.length < 2) return;
    var box = svg.getBoundingClientRect();
    if (!box.width || !box.height || getComputedStyle(svg).display === "none") return;
    var n = node.getBoundingClientRect();
    var nx = n.left + n.width / 2 - box.left, ny = n.top + n.height / 2 - box.top;
    var h = box.height, w = box.width;
    function branch(a, bend) {
      var x = a.getBoundingClientRect().left - box.left;
      return "M" + r(nx) + " " + r(ny) + "C" + r(nx) + " " + r(ny + (h - ny) * bend) + " " +
        r(x) + " " + r(ny + (h - ny) * (1 - bend) * .6) + " " + r(x) + " " + r(h);
    }
    function r(v) { return Math.round(v * 10) / 10; }
    svg.setAttribute("viewBox", "0 0 " + r(w) + " " + r(h));
    $(".atl-div__stem", svg).setAttribute("d", "M" + r(nx) + " 0V" + r(ny));
    $(".atl-div__b1", svg).setAttribute("d", branch(ends[0], .72));
    $(".atl-div__b2", svg).setAttribute("d", branch(ends[1], .86));
    svg.classList.add("is-fit");
  }

  function boot() {
    if (!document.body.classList.contains("curriculum")) return;
    var root = document.documentElement;
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
    var wide = window.matchMedia("(min-width: 1024px) and (min-height: 680px)");

    /* Drawings: fitted now and whenever their boxes change. */
    var stretched = $$("svg[data-fit]");
    var div = $(".atl-div");
    function fitDrawings() {
      stretched.forEach(fitStretched);
      if (div) fitDivision(div);
    }
    fitDrawings();
    if ("ResizeObserver" in window) {
      var ro = new ResizeObserver(function () { fitDrawings(); });
      stretched.forEach(function (s) { ro.observe(s); });
      if (div) ro.observe(div);
    }
    // Fonts change the width of the division's labels' column only
    // indirectly, but they move the node's heading; refit once they land.
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitDrawings);

    ibIndex();

    var undoStage = null, undoMotion = null;
    function apply() {
      var motion = !reduce.matches;
      var stage = false; // The numbered academic split owns the feature sequence.
      if (stage && !undoStage) undoStage = journeyStage();
      else if (!stage && undoStage) { undoStage(); undoStage = null; }
      if (motion && !undoMotion) undoMotion = entrances();
      else if (!motion && undoMotion) { undoMotion(); undoMotion = null; }
      // The layout under the shared header's and footer's triggers changed.
      requestAnimationFrame(function () {
        fitDrawings();
        if (window.ScrollTrigger) window.ScrollTrigger.refresh();
      });
    }
    listen(reduce, apply);
    listen(wide, apply);
    apply();

    function listen(mq, fn) {
      if (mq.addEventListener) mq.addEventListener("change", fn);
      else if (mq.addListener) mq.addListener(fn);
    }

    /* ---------------------------------------------------------------
       The grade journey: one sticky frame, the stage being read shown.
       --------------------------------------------------------------- */
    function journeyStage() {
      var grid = $(".atl-jr");
      if (!grid || !("IntersectionObserver" in window)) return null;
      var steps = $$(".atl-step", grid);
      var shots = $$(".atl-shot", grid);
      var links = $$(".atl-jr__route a", grid);
      var division = $("#journey-division");
      if (steps.length < 2 || shots.length !== steps.length) return null;

      root.classList.add("cur-stage");
      // Both photographs sit in the one frame now, the second under the
      // first; fetch it with the first so it is ready when it is wanted.
      shots.forEach(function (s) { var img = $("img", s); if (img) img.loading = "eager"; });

      var current = -1, shown = -1, z = 1, running = [], wanted = 0, alive = true;
      var DUR = 600, EASE = "cubic-bezier(.65,0,.35,1)";

      function stop() {
        running.forEach(function (a) { a.cancel(); });
        running = [];
      }
      // The photograph is uncovered only once it can be drawn, so the one
      // on screen stays until the next is ready. A later change wins.
      function ready(img) {
        if (!img || (img.complete && img.naturalWidth)) return Promise.resolve();
        return (img.decode ? img.decode() : Promise.reject()).catch(function () {
          return new Promise(function (res) {
            img.addEventListener("load", res, { once: true });
            img.addEventListener("error", res, { once: true });
          });
        });
      }
      function show(k, animate) {
        wanted = k;
        var shot = shots[k], img = $("img", shot);
        ready(img).then(function () {
          if (!alive || wanted !== k || shown === k) return;
          var forward = k > shown;
          stop();
          z += 1;
          shot.style.zIndex = String(z);
          shown = k;
          if (!animate || !shot.animate) return;
          var from = forward ? "inset(100% 0% 0% 0%)" : "inset(0% 0% 100% 0%)";
          running.push(shot.animate(
            [{ clipPath: from }, { clipPath: "inset(0% 0% 0% 0%)" }],
            { duration: DUR, easing: EASE }));
          if (img) running.push(img.animate(
            [{ transform: "scale(1.035)" }, { transform: "none" }],
            { duration: DUR + 250, easing: "cubic-bezier(.16,1,.3,1)" }));
          var edge = $(".atl-shot__edge", shot);
          if (edge) running.push(edge.animate(
            forward
              ? [{ top: "100%", opacity: 1 }, { top: "0%", opacity: 1, offset: .92 }, { top: "0%", opacity: 0 }]
              : [{ top: "0%", opacity: 1 }, { top: "calc(100% - 2px)", opacity: 1, offset: .92 }, { top: "calc(100% - 2px)", opacity: 0 }],
            { duration: DUR, easing: EASE }));
        });
      }
      function setActive(k) {
        if (k === current) return;
        current = k;
        steps.forEach(function (s, i) { s.classList.toggle("is-active", i === k); });
        links.forEach(function (a, i) {
          if (i === k) a.setAttribute("aria-current", "step");
          else a.removeAttribute("aria-current");
        });
        grid.style.setProperty("--atl-progress", String(Math.min(k, links.length - 1) / (links.length - 1)));
        show(Math.min(k, shots.length - 1), true);
      }

      // The reading line: a band at 45% of the window. Whichever stage's
      // text crosses it is the stage being read; above the journey the
      // first stays, past it the last.
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var i = e.target === division ? steps.length : steps.indexOf(e.target);
          if (i >= 0) setActive(i);
        });
      }, { rootMargin: "-45% 0px -55% 0px" });
      steps.forEach(function (s) { io.observe(s); });
      if (division) io.observe(division);

      // The first stage is on top from the start, without a transition.
      current = 0;
      steps[0].classList.add("is-active");
      if (links[0]) links[0].setAttribute("aria-current", "step");
      grid.style.setProperty("--atl-progress", "0");
      shots[0].style.zIndex = String(++z);
      shown = 0;

      return function () {
        alive = false;
        io.disconnect();
        stop();
        root.classList.remove("cur-stage");
        steps.forEach(function (s) { s.classList.remove("is-active"); });
        links.forEach(function (a) { a.removeAttribute("aria-current"); });
        shots.forEach(function (s) { s.style.zIndex = ""; });
        grid.style.removeProperty("--atl-progress");
      };
    }

    /* ---------------------------------------------------------------
       Once-only entrances. Each element is marked .is-in the first time
       it comes into view and is then left alone, so scrolling back does
       not replay it. Anything already on screen is marked at once.
       --------------------------------------------------------------- */
    function entrances() {
      if (!("IntersectionObserver" in window)) return null;
      var items = $$(".atl-div, .atl-core, .atl-life");
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add("is-in");
          io.unobserve(e.target);
        });
      }, { rootMargin: "0px 0px -18% 0px", threshold: 0.12 });
      var vh = window.innerHeight;
      items.forEach(function (el) {
        var r = el.getBoundingClientRect();
        // Above the window (a reload part-way down) or already in it:
        // shown, not staged.
        if (r.top < vh * 0.82) el.classList.add("is-in");
        else io.observe(el);
      });
      root.classList.add("cur-motion");
      return function () {
        io.disconnect();
        root.classList.remove("cur-motion");
        items.forEach(function (el) { el.classList.add("is-in"); });
      };
    }

    /* ---------------------------------------------------------------
       The IB index: the group being read is marked. The links themselves
       are plain anchors, handled by the site's own scroll.
       --------------------------------------------------------------- */
    function ibIndex() {
      var links = $$(".atl-ib__rail a");
      var groups = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
      if (!links.length || groups.indexOf(null) >= 0 || !("IntersectionObserver" in window)) return;
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var k = groups.indexOf(e.target);
          links.forEach(function (a, i) {
            if (i === k) a.setAttribute("aria-current", "true");
            else a.removeAttribute("aria-current");
          });
        });
      }, { rootMargin: "-35% 0px -60% 0px" });
      groups.forEach(function (g) { io.observe(g); });
    }
  }
})();
