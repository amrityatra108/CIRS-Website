/* Curriculum: the Curriculum Atlas.

   The page is complete without this file: every scene is ordinary reading
   order in the markup, and the stylesheet lays it out. This adds motion,
   and only where it says something about the curriculum's shape.

   Large windows with motion (html.cur-live): the journey, the comparison,
   the IB groups, the Diploma core and the close each hold on a sticky stage
   while the page's own scroll walks them. Nothing is pinned by script and
   nothing is added to the document; the stylesheet makes the tracks tall.
   Smaller windows with motion (html.cur-lite): the same reading order, with
   the lines drawn and the photographs uncovered as they arrive.
   Reduced motion, or no GSAP: nothing here runs.

   gsap.matchMedia builds each mode and reverts it completely when the
   window leaves it, so a resize across the line, or reduced motion switched
   on mid-visit, leaves the page exactly as the stylesheet draws it. */
(function () {
  "use strict";

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();

  /* Drawings stretched across a box of any shape (preserveAspectRatio
     none) are written in a 0-100 square. A dash measured along such a path
     is distorted by the stretch, so each is refitted to its own pixels:
     the viewBox becomes the box, and the path's points are scaled into it.
     The unscaled path is kept, so a resize refits from it. */
  function fitAll() {
    var svgs = Array.prototype.slice.call(document.querySelectorAll("svg[data-fit]"));
    function scale(d, sx, sy) {
      var i = 0;
      return d.replace(/[A-Za-z]|-?\d*\.?\d+/g, function (t) {
        if (/[A-Za-z]/.test(t)) { i = 0; return t; }
        return String(Math.round(parseFloat(t) * (i++ % 2 ? sy : sx) * 100) / 100);
      });
    }
    function fit(svg) {
      var w = svg.clientWidth, h = svg.clientHeight;
      if (!w || !h) return;
      svg.setAttribute("viewBox", "0 0 " + w + " " + h);
      Array.prototype.forEach.call(svg.querySelectorAll("path"), function (p) {
        if (!p.getAttribute("data-d")) p.setAttribute("data-d", p.getAttribute("d"));
        p.setAttribute("d", scale(p.getAttribute("data-d"), w / 100, h / 100));
      });
      svg.classList.add("is-fit");
    }
    svgs.forEach(fit);
    if ("ResizeObserver" in window) {
      var ro = new ResizeObserver(function (entries) { entries.forEach(function (e) { fit(e.target); }); });
      svgs.forEach(function (s) { ro.observe(s); });
    }
  }

  function boot() {
    var body = document.body;
    if (!body.classList.contains("curriculum")) return;
    fitAll();
    var gs = window.gsap, ST = window.ScrollTrigger;
    if (!gs || !ST) return;
    gs.registerPlugin(ST);

    var root = document.documentElement;
    var $ = function (s, c) { return (c || document).querySelector(s); };
    var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
    var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

    var LIVE = "(min-width: 1024px) and (min-height: 680px)";
    var MOTION = "(prefers-reduced-motion: no-preference)";

    var mm = gs.matchMedia();

    mm.add({ live: LIVE, motion: MOTION }, function (ctx) {
      if (!ctx.conditions.motion) return;
      var undo = ctx.conditions.live ? live() : lite();
      var frame = requestAnimationFrame(function () { ST.refresh(); });
      return function () {
        cancelAnimationFrame(frame);
        if (undo) undo();
      };
    });

    mm.add(MOTION + " and (pointer: fine)", openingDepth);
    mm.add(MOTION, openingDrift);

    /* ---------------------------------------------------------------
       Shared: a scene's scroll position for a point in its progress, and
       a way to go there that uses the site's smooth scroll when it runs.
       --------------------------------------------------------------- */
    function scrollFor(track, p) {
      var top = track.getBoundingClientRect().top + window.scrollY;
      return top + clamp(p, 0, 1) * Math.max(0, track.offsetHeight - window.innerHeight);
    }
    function goTo(y, instant) {
      var ev = new CustomEvent("cirs-section-scroll", {
        cancelable: true,
        detail: { top: y, duration: instant ? 0.01 : 1.1 }
      });
      if (window.dispatchEvent(ev)) window.scrollTo({ top: y, behavior: "instant" });
    }
    // A link inside a stage can be reached by Tab while its scene shows
    // something else. Bring its moment on screen rather than leave focus on
    // a link nobody can see.
    function focusBrings(el, track, p) {
      function on() {
        var y = scrollFor(track, typeof p === "function" ? p() : p);
        if (Math.abs(y - window.scrollY) > 4) goTo(y, true);
      }
      el.addEventListener("focusin", on);
      return function () { el.removeEventListener("focusin", on); };
    }

    /* ---------------------------------------------------------------
       The opening: the linework and the grades at their own depths.
       --------------------------------------------------------------- */
    function openingDepth() {
      var open = $(".atl-open");
      if (!open) return;
      var layers = $$("[data-depth]", open).map(function (el) {
        var d = parseFloat(el.getAttribute("data-depth")) || 0;
        return {
          d: d,
          x: gs.quickTo(el, "x", { duration: 1.4, ease: "power3.out" }),
          y: gs.quickTo(el, "y", { duration: 1.4, ease: "power3.out" })
        };
      });
      function move(e) {
        var nx = e.clientX / window.innerWidth - 0.5;
        var ny = e.clientY / window.innerHeight - 0.5;
        layers.forEach(function (l) { l.x(-nx * 22 * l.d); l.y(-ny * 14 * l.d); });
      }
      function rest() { layers.forEach(function (l) { l.x(0); l.y(0); }); }
      open.addEventListener("pointermove", move);
      open.addEventListener("pointerleave", rest);
      return function () {
        open.removeEventListener("pointermove", move);
        open.removeEventListener("pointerleave", rest);
      };
    }

    // As the opening leaves, its planes part: the linework lags furthest,
    // the path a little less, the heading goes with the page.
    function openingDrift() {
      var open = $(".atl-open");
      if (!open) return;
      var st = { trigger: open, start: "top top", end: "bottom top", scrub: true };
      gs.to($(".atl-open__field", open), { y: 140, ease: "none", scrollTrigger: st });
      gs.to($(".atl-open__grades", open), { y: 70, ease: "none", scrollTrigger: st });
    }

    /* ===============================================================
       html.cur-live
       =============================================================== */
    function live() {
      root.classList.add("cur-live");
      var undos = [journey(), comparison(), streams(), groups(), core(), beyond()].filter(Boolean);
      return function () {
        undos.forEach(function (u) { u(); });
        root.classList.remove("cur-live");
      };
    }

    /* The grade journey. One timeline, 100 units long, scrubbed by the
       track: the foundation (0-26), the turn to the Board years (26-36),
       the rest of the route to Grade X (36-52), the arrival (52-62), a
       hold, the node's activation (68-76), the division (74-90), a hold. */
    function journey() {
      var track = $(".atl-journey__track");
      if (!track) return;
      var route = $(".atl-route", track);
      var rail = $(".atl-route__rail i", track);
      var marks = $$(".atl-route__marks li", track);
      var found = $(".atl-phase--found", track);
      var board = $(".atl-phase--board", track);
      var fork = $(".atl-phase--fork", track);
      var fText = $(".atl-phase__text", found), fPlate = $(".atl-phase__plate", found);
      var bText = $(".atl-phase__text", board), bPlate = $(".atl-phase__plate", board);
      var bFig = $(".atl-phase__figure", board);
      var ruled = $$(".atl-ruled i", board);
      var breadth = $$(".atl-breadth li", found);
      var junction = $(".atl-junction", fork);
      var node = $(".atl-node", fork);
      var ring = $(".atl-node__ring", node), pulse = $(".atl-node__pulse", node), numeral = $(".atl-node__x", node);
      var paths = $$(".atl-fork .is-wide", fork);
      var kText = $(".atl-phase__text", fork);
      var branches = $$(".atl-branch", fork);
      var NODE = 74; // vh: where Grade X waits, as --node-y in the sheet

      function markRoute() {
        var reached = gs.getProperty(rail, "scaleY") * NODE;
        marks.forEach(function (m) {
          m.classList.toggle("is-past", reached >= parseFloat(m.style.getPropertyValue("--at")) - 0.5);
        });
      }

      gs.set(rail, { scaleY: 0 });
      gs.set(bText, { opacity: 0, y: 36 });
      gs.set(bFig, { clipPath: "inset(100% 0% 0% 0%)" });
      gs.set(ruled, { scaleX: 0 });
      gs.set(node, { scale: 0.16 });
      gs.set(ring, { backgroundColor: "#F4F0E6" });
      gs.set(numeral, { opacity: 0, color: "#1E1626" });
      gs.set(pulse, { opacity: 0, scale: 1 });
      gs.set(paths, { strokeDashoffset: 1 });
      gs.set(kText, { opacity: 0, y: 24 });
      gs.set(branches, { opacity: 0, y: 18 });

      var tl = gs.timeline({
        defaults: { ease: "none" },
        scrollTrigger: {
          trigger: track, start: "top top", end: "bottom bottom", scrub: true,
          onUpdate: markRoute, onRefresh: markRoute
        }
      });
      tl.to(rail, { scaleY: 37 / NODE, duration: 26 }, 0)
        // The same broad course, set in order: the five subjects of the
        // foundation come to rest on ruled lines, and the Board years'
        // photograph is uncovered over the foundation's.
        .to(fText, { opacity: 0, y: -36, duration: 7, ease: "power2.in" }, 26)
        .to(bText, { opacity: 1, y: 0, duration: 8, ease: "power2.out" }, 29)
        .to(ruled, { scaleX: 1, duration: 6, stagger: 0.5, ease: "power2.out" }, 27)
        .to(bFig, { clipPath: "inset(0% 0% 0% 0%)", duration: 9, ease: "power2.inOut" }, 27);
      breadth.forEach(function (li, i) {
        // On the line, not through it: the label sits above its rule.
        tl.to(li, { left: "0%", top: (12 + 11 * i) + "%", yPercent: -52, duration: 8, ease: "power3.inOut" }, 27 + i * 0.4);
      });
      tl.to(rail, { scaleY: 54 / NODE, duration: 8 }, 36)
        .to(rail, { scaleY: 1, duration: 8 }, 44)
        // Arrival: the phases give the stage to the node, which comes up
        // the window and opens to its full size.
        .to([bText, bPlate, fPlate], { opacity: 0, y: -40, duration: 5, ease: "power2.in" }, 52)
        .to([route, junction], { y: function () { return -window.innerHeight * 0.38; }, duration: 8, ease: "power2.inOut" }, 54)
        .to(node, { scale: 1, duration: 7, ease: "power2.out" }, 55)
        .to(numeral, { opacity: 1, duration: 3 }, 59)
        .to({}, { duration: 6 }, 62)
        // Activation, once.
        .to(ring, { backgroundColor: "#392A48", duration: 4, ease: "power2.out" }, 68)
        .to(numeral, { color: "#FAF9F3", duration: 4, ease: "power2.out" }, 68)
        .fromTo(pulse, { opacity: 0.9, scale: 1 }, { opacity: 0, scale: 2.4, duration: 8, ease: "power2.out", immediateRender: false }, 68)
        // The division.
        .to(paths, { strokeDashoffset: 0, duration: 14, ease: "power1.inOut" }, 74)
        .to(kText, { opacity: 1, y: 0, duration: 6, ease: "power2.out" }, 76)
        .to(branches, { opacity: 1, y: 0, duration: 6, stagger: 1.5, ease: "power2.out" }, 82)
        .to({}, { duration: 10 }, 90);

      var unfocus = branches.map(function (b) { return focusBrings(b, track, 0.95); });
      return function () {
        unfocus.forEach(function (u) { u(); });
        marks.forEach(function (m) { m.classList.remove("is-past"); });
        gs.set([rail, bText, bFig, ruled, node, ring, numeral, pulse, paths, kText, branches,
                fText, fPlate, bPlate, route, junction].concat(breadth), { clearProps: "all" });
      };
    }

    /* The comparison: four themes, one at a time, each held for most of
       its quarter of the track and handed on in the rest. */
    function comparison() {
      var track = $(".atl-paths__track");
      if (!track) return;
      var themes = $$(".atl-theme", track);
      var dial = $$(".atl-cmp__dial i", track);
      var photos = $$(".atl-cmp__photo", track);
      var parts = themes.map(function (t) {
        return {
          name: $(".atl-theme__name", t),
          sides: $$(".atl-theme__side", t),
          stats: $$(".atl-theme__stat b", t),
          texts: $$(".atl-theme__text, .atl-theme__prog", t)
        };
      });
      var crops = ["inset(0% 0% 0% 0%)", "inset(14% 0% 0% 0%)", "inset(0% 0% 18% 0%)", "inset(7% 0% 7% 0%)"];

      parts.forEach(function (p, i) {
        if (i === 0) return;
        gs.set([p.name].concat(p.sides), { opacity: 0 });
      });

      var tl = gs.timeline({
        defaults: { ease: "none" },
        scrollTrigger: {
          trigger: track, start: "top top", end: "bottom bottom", scrub: true,
          onUpdate: function (self) { setDial(self.progress); },
          onRefresh: function (self) { setDial(self.progress); }
        }
      });
      tl.fromTo(photos, { "--pan": "30%" }, { "--pan": "70%", duration: 100 }, 0);
      for (var k = 1; k < parts.length; k++) {
        var at = 25 * k - 3, prev = parts[k - 1], next = parts[k];
        tl.to([prev.name].concat(prev.sides), { opacity: 0, y: -28, duration: 4, ease: "power2.in" }, at)
          .fromTo(next.name, { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: 5, ease: "power2.out" }, at + 3)
          .fromTo(next.sides, { opacity: 0 }, { opacity: 1, duration: 3 }, at + 3)
          .fromTo(next.stats, { yPercent: 105 }, { yPercent: 0, duration: 5, ease: "power3.out" }, at + 3)
          .fromTo(next.texts, { y: 18 }, { y: 0, duration: 5, ease: "power2.out" }, at + 4)
          .to(photos, { clipPath: crops[k], duration: 6, ease: "power2.inOut" }, at);
      }
      tl.to({}, { duration: 1 }, 99);

      function setDial(p) {
        var on = clamp(Math.floor((p * 100 + 3) / 25), 0, dial.length - 1);
        dial.forEach(function (d, i) { d.classList.toggle("is-on", i === on); });
      }

      return function () {
        dial.forEach(function (d) { d.classList.remove("is-on"); });
        var all = photos.slice();
        parts.forEach(function (p) { all = all.concat([p.name], p.sides, p.stats, p.texts); });
        gs.set(all, { clearProps: "all" });
      };
    }

    /* The CBSE streams. Each word becomes the control for its subjects:
       hover, focus or a tap opens it, and one is always open. */
    function streams() {
      var items = $$(".atl-stream");
      if (!items.length) return;
      var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
      var controls = items.map(function (li, i) {
        var h = $(".atl-stream__name", li);
        var panel = $(".atl-stream__subjects", li);
        var label = h.textContent;
        var b = document.createElement("button");
        b.type = "button";
        b.textContent = label;
        b.setAttribute("aria-controls", panel.id);
        h.textContent = "";
        h.appendChild(b);
        function open() { show(i); }
        b.addEventListener("click", open);
        b.addEventListener("focus", open);
        if (fine) li.addEventListener("pointerenter", open);
        return {
          li: li, b: b,
          undo: function () {
            b.removeEventListener("click", open);
            b.removeEventListener("focus", open);
            li.removeEventListener("pointerenter", open);
            h.textContent = label;
          }
        };
      });
      function show(n) {
        controls.forEach(function (c, i) {
          c.li.classList.toggle("is-open", i === n);
          c.b.setAttribute("aria-expanded", String(i === n));
        });
      }
      show(0);
      return function () {
        controls.forEach(function (c) { c.li.classList.remove("is-open"); c.undo(); });
      };
    }

    /* The IB groups. The track's progress is a position along the six
       groups, held on each and moved between them; each group is placed by
       its distance from that position. */
    function groups() {
      var track = $(".atl-ib__track");
      if (!track) return;
      var items = $$(".atl-group", track);
      var links = $$(".atl-ib__rail a", track);
      var nav = $(".atl-ib__rail", track);
      var n = items.length, HOLD = 0.42, LEAD = 0.05;
      var spacing = 0, current = -1;

      function measure() {
        var w = items[0].offsetWidth;
        spacing = w + window.innerWidth * 0.06;
      }
      function position(p) {
        var t = clamp((p - LEAD) / (1 - 2 * LEAD), 0, 1) * (n - 1);
        var i = Math.min(Math.floor(t), n - 2), f = t - i;
        var u = clamp((f - HOLD / 2) / (1 - HOLD), 0, 1);
        return i + u * u * (3 - 2 * u);
      }
      function progressOf(k) { return LEAD + (1 - 2 * LEAD) * (k / (n - 1)); }
      function render(p) {
        var f = position(p);
        items.forEach(function (el, i) {
          var d = i - f, a = Math.abs(d);
          gs.set(el, {
            x: d * spacing,
            scale: 1 - Math.min(a, 1.6) * 0.14,
            opacity: 1 - Math.min(a, 1) * 0.72,
            zIndex: 10 - Math.round(a)
          });
        });
        var on = Math.round(f);
        if (on !== current) {
          current = on;
          links.forEach(function (l, i) {
            if (i === on) l.setAttribute("aria-current", "true");
            else l.removeAttribute("aria-current");
          });
        }
      }
      measure();
      var st = ST.create({
        trigger: track, start: "top top", end: "bottom bottom",
        onUpdate: function (self) { render(self.progress); },
        onRefresh: function (self) { measure(); render(self.progress); }
      });
      render(st.progress || 0);

      // The rail's links go to their group's moment rather than to an
      // anchor inside a stage that does not move.
      function jump(e) {
        var a = e.target.closest && e.target.closest("a");
        if (!a) return;
        var k = links.indexOf(a);
        if (k < 0) return;
        e.preventDefault();
        e.stopPropagation();
        goTo(scrollFor(track, progressOf(k)));
      }
      nav.addEventListener("click", jump, true);
      var unfocus = items.map(function (el, k) { return focusBrings(el, track, progressOf(k)); });

      return function () {
        st.kill();
        nav.removeEventListener("click", jump, true);
        unfocus.forEach(function (u) { u(); });
        links.forEach(function (l) { l.removeAttribute("aria-current"); });
        gs.set(items, { clearProps: "all" });
      };
    }

    /* The Diploma core. The rings turn a few degrees across the scene, no
       more, and each part of the core comes forward in turn. */
    function core() {
      var track = $(".atl-core__track");
      if (!track) return;
      var orbits = $$(".atl-orbit", track);
      var items = $$(".atl-core__list li", track);
      var all = $(".atl-orbits", track);
      var current = -1;
      function setActive(p) {
        var on = p < 0.36 ? 0 : p < 0.68 ? 1 : 2;
        if (on === current) return;
        current = on;
        orbits.forEach(function (o, i) { o.classList.toggle("is-on", i === on); });
        items.forEach(function (li, i) { li.classList.toggle("is-on", i === on); });
      }
      var tl = gs.timeline({
        defaults: { ease: "none" },
        scrollTrigger: {
          trigger: track, start: "top top", end: "bottom bottom", scrub: true,
          onUpdate: function (self) { setActive(self.progress); },
          onRefresh: function (self) { setActive(self.progress); }
        }
      });
      tl.fromTo(all, { rotation: -9 }, { rotation: 12, svgOrigin: "300 300", duration: 1 }, 0)
        .fromTo(orbits[0], { rotation: 0 }, { rotation: 16, svgOrigin: "300 300", duration: 1 }, 0)
        .fromTo(orbits[1], { rotation: 0 }, { rotation: -12, svgOrigin: "300 300", duration: 1 }, 0)
        .fromTo(orbits[2], { rotation: 0 }, { rotation: 7, svgOrigin: "300 300", duration: 1 }, 0);
      return function () {
        orbits.forEach(function (o) { o.classList.remove("is-on"); });
        items.forEach(function (li) { li.classList.remove("is-on"); });
        gs.set([all].concat(orbits), { clearProps: "all" });
      };
    }

    /* School life: the drawing's marks give way to photographs. */
    function beyond() {
      var track = $(".atl-beyond__track");
      if (!track) return;
      var tl = gs.timeline({
        defaults: { ease: "none" },
        scrollTrigger: { trigger: track, start: "top top", end: "bottom bottom", scrub: true }
      });
      lifeReveal(tl, $$(".atl-life", track), false);
      tl.to({}, { duration: 12 }, 88);
      return function () { lifeClear(track); };
    }

    // One sequence for both modes. In the live stage the three figures
    // follow one another on the scene's timeline (the figure's own start is
    // its place in the sequence); in the lite layout each figure has a
    // timeline of its own and starts at once.
    function lifeReveal(tl, figs, alone) {
      figs.forEach(function (fig) {
        var img = $(".atl-life__img", fig), cap = $("figcaption", fig);
        if (fig.classList.contains("atl-life--line")) {
          tl.fromTo($(".atl-life__rule", fig), { scaleX: 0 }, { scaleX: 1, duration: 12, ease: "power2.inOut" }, 0)
            .fromTo(img, { clipPath: "inset(0% 0% 100% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 20, ease: "power2.inOut" }, 8)
            .fromTo(cap, { opacity: 0 }, { opacity: 1, duration: 6 }, 24);
        } else if (fig.classList.contains("atl-life--circle")) {
          var o = alone ? 0 : 22, comp = $(".atl-life__compass", fig);
          tl.fromTo(comp, { opacity: 0, rotation: -120, transformOrigin: "50% 50%" }, { opacity: 1, rotation: 0, duration: 14, ease: "power2.out" }, o)
            .fromTo(img, { clipPath: "circle(0% at 50% 50%)" }, { clipPath: "circle(50% at 50% 50%)", duration: 18, ease: "power2.inOut" }, o + 10)
            .to(comp, { opacity: 0.35, duration: 8 }, o + 24)
            .fromTo(cap, { opacity: 0 }, { opacity: 1, duration: 6 }, o + 24);
        } else {
          var f = alone ? 0 : 44, dims = $$(".atl-life__dims i", fig);
          tl.fromTo(dims[0], { scaleX: 0 }, { scaleX: 1, duration: 10, ease: "power2.out" }, f)
            .fromTo(dims[1], { scaleY: 0 }, { scaleY: 1, duration: 10, ease: "power2.out" }, f + 4)
            .fromTo(img, { clipPath: "inset(50% 50% 50% 50%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 20, ease: "power2.inOut" }, f + 10)
            .to(dims, { opacity: 0.4, duration: 8 }, f + 28)
            .fromTo(cap, { opacity: 0 }, { opacity: 1, duration: 6 }, f + 28);
        }
      });
    }
    function lifeClear(scope) {
      gs.set($$(".atl-life__rule, .atl-life__img, .atl-life figcaption, .atl-life__compass, .atl-life__dims i", scope),
             { clearProps: "all" });
    }

    /* ===============================================================
       html.cur-lite
       =============================================================== */
    function lite() {
      root.classList.add("cur-lite");
      var made = [];
      function scrub(targets, from, to, trigger, start, end) {
        made.push(gs.fromTo(targets, from, Object.assign({ ease: "none", scrollTrigger: {
          trigger: trigger, start: start || "top 85%", end: end || "bottom 60%", scrub: true
        } }, to)));
      }

      // The spine draws as the approach passes, and on into the journey.
      $$(".atl-approach .atl-spine i, .atl-journey__intro .atl-spine i").forEach(function (i) {
        scrub(i, { scaleY: 0 }, { scaleY: 1 }, i.parentNode.parentNode, "top 80%", "bottom 55%");
      });

      // Grade X, then the division, drawn through the junction.
      var junction = $(".atl-junction");
      if (junction) {
        var paths = $$(".atl-fork path", junction);
        var tl = gs.timeline({ scrollTrigger: { trigger: junction, start: "top 88%", end: "bottom 62%", scrub: true } });
        tl.fromTo(paths.filter(function (p) { return p.classList.contains("atl-fork__join"); }), { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 3, ease: "none" }, 0)
          .fromTo($(".atl-node", junction), { scale: 0.35 }, { scale: 1, duration: 3, ease: "power2.out" }, 2)
          .fromTo($(".atl-node__ring", junction), { backgroundColor: "#F4F0E6" }, { backgroundColor: "#392A48", duration: 2 }, 4)
          .fromTo($(".atl-node__x", junction), { color: "#1E1626" }, { color: "#FAF9F3", duration: 2 }, 4)
          .fromTo(paths.filter(function (p) { return !p.classList.contains("atl-fork__join"); }), { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 5, ease: "power1.inOut" }, 5);
        made.push(tl);
      }

      // The stream in the middle of the window is the one lit.
      var toggles = $$(".atl-stream").map(function (li) {
        return ST.create({ trigger: li, start: "top 62%", end: "bottom 38%", toggleClass: "is-open" });
      });

      // The core: the part in the middle of the window comes forward.
      var orbits = $$(".atl-orbit");
      var coreToggles = $$(".atl-core__list li").map(function (li, i) {
        return ST.create({
          trigger: li, start: "top 66%", end: "bottom 34%",
          onToggle: function (self) {
            li.classList.toggle("is-on", self.isActive);
            if (orbits[i]) orbits[i].classList.toggle("is-on", self.isActive);
          }
        });
      });

      // School life: each photograph is uncovered as it arrives.
      $$(".atl-life").forEach(function (fig) {
        var tl = gs.timeline({ defaults: { ease: "none" }, scrollTrigger: { trigger: fig, start: "top 92%", end: "top 38%", scrub: true } });
        lifeReveal(tl, [fig], true);
        made.push(tl);
      });

      return function () {
        made.forEach(function (t) { if (t.scrollTrigger) t.scrollTrigger.kill(); t.kill(); });
        toggles.concat(coreToggles).forEach(function (t) { t.kill(); });
        $$(".atl-stream, .atl-core__list li, .atl-orbit").forEach(function (el) { el.classList.remove("is-open", "is-on"); });
        gs.set($$(".atl-spine i, .atl-fork path, .atl-node, .atl-node__ring, .atl-node__x"), { clearProps: "all" });
        lifeClear(document);
        root.classList.remove("cur-lite");
      };
    }
  }
})();
