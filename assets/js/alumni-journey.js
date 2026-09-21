/* ============================================================
   WHERE CIRS TAKES YOU — the alumni journey
   ------------------------------------------------------------
   Two halves, deliberately kept apart:

     interactions()  the filters, the search, the destination panel,
                     the keyboard. These run whether or not there is
                     motion, whether or not GSAP loaded, and whether
                     or not the reader asked for reduced motion.
                     Nothing a reader needs is inside a timeline.

     motion()        the opening, the departure, the field coming up,
                     the pathway rail and the return. Runs only when
                     cirs.js has already decided to animate — the same
                     gate that adds html.js-motion, which is what every
                     "start hidden" rule in alumni.css hangs off.

   If the second half never runs, the first half still works and the
   page is simply a still one. That is the contract, and the sweep at
   the foot of this file enforces it.
   ============================================================ */
(function () {
  "use strict";

  var root = document.body;
  if (!root.classList.contains("alumni")) return;

  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) {
    return Array.prototype.slice.call((c || document).querySelectorAll(s));
  };

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine    = window.matchMedia("(hover: hover) and (pointer: fine)");

  var gsap = window.gsap;
  var ScrollTrigger = window.ScrollTrigger;
  var canMove = !!(gsap && ScrollTrigger && !reduced);
  if (canMove) gsap.registerPlugin(ScrollTrigger);

  /* ==========================================================
     The destination panel, the filters, the search
     ========================================================== */
  function interactions() {
    var field = $("[data-constellation]");
    var panel = $("#ajc-panel");
    var points = $$(".ajc__pt");
    var items = $$(".ajc__item");
    var lines = $$(".ajc__line");
    var status = $("[data-constellation-status]");
    var openPoint = null;

    /* ---- the panel ---------------------------------------- */
    function panelParts() {
      return {
        region:  $("[data-panel-region]", panel),
        name:    $("[data-panel-name]", panel),
        country: $("[data-panel-country]", panel),
        close:   $("[data-panel-close]", panel)
      };
    }

    function regionLabel(key) {
      var b = document.querySelector('.ajc__filter[data-filter="' + key + '"]');
      if (!b) return "";
      // The button carries its count in a child; the label is the rest.
      return b.textContent.replace(/\s*\d+\s*$/, "").trim();
    }

    function openPanel(btn) {
      if (!panel) return;
      var p = panelParts();
      var label = $(".ajc__label", btn);
      // The full institution name lives in the screen-reader line, which
      // reads "Destination n of m. <name>, <country>. Open details."
      var sr = $(".sr-only", btn);
      var name = "";
      if (sr) {
        var m = sr.textContent.match(/\.\s*(.+?),\s*([^,]+)\.\s*Open details\./);
        if (m) name = m[1];
      }
      if (!name && label) name = $(".ajc__name", label).textContent;

      p.name.textContent = name;
      p.country.textContent = $(".ajc__country", btn).textContent;
      p.region.textContent = regionLabel(btn.dataset.region);
      panel.hidden = false;

      points.forEach(function (o) {
        o.classList.toggle("is-active", o === btn);
        o.setAttribute("aria-expanded", o === btn ? "true" : "false");
      });
      lines.forEach(function (l) {
        l.classList.toggle("is-lit", l.dataset.line === btn.dataset.point);
        l.classList.toggle("is-dim", l.dataset.line !== btn.dataset.point);
      });

      openPoint = btn;
      p.close.focus();
    }

    function closePanel(restore) {
      if (!panel || panel.hidden) return;
      panel.hidden = true;
      points.forEach(function (o) {
        o.classList.remove("is-active");
        o.setAttribute("aria-expanded", "false");
      });
      lines.forEach(function (l) { l.classList.remove("is-lit", "is-dim"); });
      if (restore !== false && openPoint) openPoint.focus();
      openPoint = null;
    }

    if (panel) {
      points.forEach(function (btn) {
        btn.addEventListener("click", function () {
          if (openPoint === btn) { closePanel(); return; }
          openPanel(btn);
        });
        // Hovering and focusing light the route without opening anything.
        ["pointerenter", "focus"].forEach(function (type) {
          btn.addEventListener(type, function () {
            if (openPoint) return;
            lines.forEach(function (l) {
              l.classList.toggle("is-lit", l.dataset.line === btn.dataset.point);
            });
          });
        });
        ["pointerleave", "blur"].forEach(function (type) {
          btn.addEventListener(type, function () {
            if (openPoint) return;
            lines.forEach(function (l) { l.classList.remove("is-lit"); });
          });
        });
      });

      $("[data-panel-close]", panel).addEventListener("click", function () { closePanel(); });

      // Escape closes it, and Tab is held inside it while it is open —
      // there is one focusable thing in there, so the trap is a short loop.
      document.addEventListener("keydown", function (e) {
        if (panel.hidden) return;
        if (e.key === "Escape") { e.preventDefault(); closePanel(); return; }
        if (e.key !== "Tab") return;
        var focusable = $$("button, a[href], input, [tabindex]:not([tabindex='-1'])", panel)
          .filter(function (el) { return !el.disabled && el.offsetParent !== null; });
        if (!focusable.length) return;
        var first = focusable[0], last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      });

      // A click anywhere outside it closes it, without stealing focus back.
      document.addEventListener("pointerdown", function (e) {
        if (panel.hidden) return;
        if (panel.contains(e.target)) return;
        if (e.target.closest && e.target.closest(".ajc__pt")) return;
        closePanel(false);
      });
    }

    /* ---- the region filters ------------------------------- */
    var filters = $$(".ajc__filter");
    filters.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var want = btn.dataset.filter;
        filters.forEach(function (o) {
          var on = o === btn;
          o.classList.toggle("is-on", on);
          o.setAttribute("aria-pressed", on ? "true" : "false");
        });
        var shown = 0;
        items.forEach(function (li) {
          var out = want !== "all" && li.dataset.region !== want;
          li.classList.toggle("is-out", out);
          if (!out) shown++;
        });
        lines.forEach(function (l) {
          l.classList.toggle("is-dim", want !== "all" && l.dataset.region !== want);
        });
        closePanel(false);
        if (status) {
          status.textContent = want === "all"
            ? "Showing all " + shown + " destinations."
            : "Showing " + shown + " destination" + (shown === 1 ? "" : "s") +
              " — " + regionLabel(want) + ".";
        }
      });
    });

    /* ---- the index search --------------------------------- */
    var input = $("#ajd-q");
    if (input) {
      var rows = $$(".ajd__row");
      var groups = $$(".ajd__group");
      var count = $("[data-destinations-count]");
      var empty = $("[data-destinations-empty]");
      var total = rows.length;
      var countries = new Set(rows.map(function (r) {
        return r.querySelector(".ajd__country").textContent;
      })).size;

      input.addEventListener("input", function () {
        var q = input.value.trim().toLowerCase();
        var shown = 0;
        rows.forEach(function (row) {
          var hit = !q || row.dataset.search.indexOf(q) !== -1;
          row.hidden = !hit;
          if (hit) shown++;
        });
        groups.forEach(function (g) {
          g.hidden = !$$(".ajd__row:not([hidden])", g).length;
        });
        if (empty) empty.hidden = shown !== 0;
        if (count) {
          count.textContent = q
            ? shown + " of " + total + " institutions match “" + input.value.trim() + "”."
            : total + " institutions in " + countries + " countries.";
        }
      });
    }

    /* ---- the cursor label --------------------------------- */
    if (fine.matches && !reduced) cursorLabel();

    return { field: field, points: points, lines: lines };
  }

  /* ==========================================================
     The cursor label
     A word, inside the alumni interactions only. The site's own
     difference-blend ring keeps running underneath it.
     ========================================================== */
  function cursorLabel() {
    var tag = document.createElement("p");
    tag.className = "aj-cursor";
    tag.setAttribute("aria-hidden", "true");
    document.body.appendChild(tag);

    /* Only over things that actually do something. A label reading "Story"
       over a chapter that cannot be opened, or "Explore" over a list row
       that is not a link, promises an interaction the page does not have —
       which is worse than no label at all. */
    var zones = [
      [".ajc__pt", "Open"],
      [".ajc__panelClose", "Close"],
      [".ajw__evName[href]", "Read"],
      [".ajw-track.is-live", "Scroll"]
    ];

    var x = null, y = null;
    if (gsap) {
      x = gsap.quickTo(tag, "x", { duration: .3, ease: "power3" });
      y = gsap.quickTo(tag, "y", { duration: .3, ease: "power3" });
    }

    window.addEventListener("pointermove", function (e) {
      var word = null;
      for (var i = 0; i < zones.length; i++) {
        if (e.target.closest && e.target.closest(zones[i][0])) { word = zones[i][1]; break; }
      }
      if (word) {
        if (tag.textContent !== word) tag.textContent = word;
        tag.classList.add("is-on");
        if (x) { x(e.clientX + 26); y(e.clientY + 22); }
        else { tag.style.transform = "translate(" + (e.clientX + 26) + "px," + (e.clientY + 22) + "px)"; }
      } else {
        tag.classList.remove("is-on");
      }
    }, { passive: true });

    document.addEventListener("pointerleave", function () { tag.classList.remove("is-on"); });
  }

  /* ==========================================================
     The sky
     ----------------------------------------------------------
     A few hundred stars behind the eighteen destinations. Drawn
     rather than written into the markup: they carry no
     information, and three hundred inert <circle> elements in
     every generated page would be three hundred lines of noise
     in a file a person has to read.

     The seed is fixed, so it is the same sky on every reload —
     a constellation that reshuffles itself each time is a
     screensaver, not a place.
     ========================================================== */
  function buildStars() {
    var field = $("[data-constellation-field]");
    if (!field) return null;
    var NS = "http://www.w3.org/2000/svg";

    // mulberry32: small, fast, and deterministic from one integer.
    var seed = 0x1996;   // the year the school opened on this campus
    function rnd() {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }

    var svg = document.createElementNS(NS, "svg");
    svg.setAttribute("class", "ajc__stars");
    svg.setAttribute("viewBox", "0 0 160 90");
    svg.setAttribute("preserveAspectRatio", "none");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("focusable", "false");

    var twinklers = [];
    for (var i = 0; i < 320; i++) {
      var x = rnd() * 160, y = rnd() * 90;
      // Thicken the drift along the diagonal band the sheet paints, so the
      // stars and the cloud are the same cloud.
      var band = Math.abs((y / 90) - (0.22 + (x / 160) * 0.62));
      if (band > 0.30 && rnd() > 0.45) continue;

      var bright = rnd();
      var c = document.createElementNS(NS, "circle");
      c.setAttribute("class", "ajc__star");
      c.setAttribute("cx", x.toFixed(2));
      c.setAttribute("cy", y.toFixed(2));
      c.setAttribute("r", (0.07 + bright * bright * 0.24).toFixed(3));
      c.setAttribute("opacity", (0.16 + bright * 0.62).toFixed(2));
      svg.appendChild(c);
      if (bright > 0.86) twinklers.push(c);
    }
    field.insertBefore(svg, field.firstChild);
    return { svg: svg, twinklers: twinklers };
  }

  /* ==========================================================
     The return: eighteen marks coming home to one ring
     Built here rather than in the markup because it is decoration
     and carries no information the page does not already state.
     ========================================================== */
  function buildGather() {
    var svg = $("[data-return-gather]");
    if (!svg) return null;
    var NS = "http://www.w3.org/2000/svg";
    var total = $$(".ajc__pt").length || 18;

    var ring = document.createElementNS(NS, "circle");
    ring.setAttribute("class", "aj-return__gatherRing");
    ring.setAttribute("cx", "200"); ring.setAttribute("cy", "200");
    ring.setAttribute("r", "120");
    svg.appendChild(ring);

    var dots = [];
    for (var i = 0; i < total; i++) {
      var a = (i / total) * Math.PI * 2 - Math.PI / 2;
      var d = document.createElementNS(NS, "circle");
      d.setAttribute("class", "aj-return__gatherDot");
      d.setAttribute("cx", (200 + Math.cos(a) * 120).toFixed(2));
      d.setAttribute("cy", (200 + Math.sin(a) * 120).toFixed(2));
      d.setAttribute("r", "3.2");
      svg.appendChild(d);
      dots.push(d);
    }
    // The centre: one beginning.
    var hub = document.createElementNS(NS, "circle");
    hub.setAttribute("class", "aj-return__gatherDot");
    hub.setAttribute("cx", "200"); hub.setAttribute("cy", "200");
    hub.setAttribute("r", "5.5");
    svg.appendChild(hub);

    return { svg: svg, ring: ring, dots: dots, hub: hub };
  }

  /* ==========================================================
     Motion
     ========================================================== */
  function motion(parts, gather, sky) {
    /* ---- chapter 1: the opening --------------------------- */
    var open = $("[data-open]");
    if (open) {
      var lines = $$(".aj-open__line > span", open);
      var route = $("[data-open-route]", open);
      var seed = $(".aj-open__routeSeed", open);
      var media = $("[data-open-media] img", open);

      // The sheet hides these two lines with transform:translateY(105%) so
      // there is no flash before this file runs. GSAP reads that computed
      // transform as a PIXEL y, not as yPercent — so tweening yPercent to 0
      // moves nothing and the lettering stays parked off its own line box.
      // Handing the property to GSAP first is what makes the tween real.
      gsap.set(lines, { yPercent: 105, y: 0 });

      var len = route ? route.getTotalLength() : 0;
      if (route) gsap.set(route, { strokeDasharray: len, strokeDashoffset: len });

      var intro = gsap.timeline({ delay: .15 });
      intro.to(lines, { yPercent: 0, duration: 1.15, ease: "expo.out", stagger: .09 })
           .to("[data-open-sub]", { opacity: 1, duration: .9, ease: "power2.out" }, "-=.55")
           .to("[data-open-cue]", { opacity: 1, duration: .7, ease: "power2.out" }, "-=.5");
      if (seed) intro.to(seed, { opacity: 1, duration: .5 }, "-=.9");
      if (route) intro.to(route, { strokeDashoffset: len * .55, duration: 1.8, ease: "power2.inOut" }, "-=1.0");

      // The header goes quiet while the opening holds the screen.
      ScrollTrigger.create({
        trigger: open, start: "top top", end: "bottom 45%",
        onToggle: function (self) { root.classList.toggle("aj-quiet", self.isActive); }
      });

      // Leaving: the title parts, the campus pulls back, the route runs on.
      var leave = gsap.timeline({
        scrollTrigger: {
          trigger: open, start: "top top", end: "bottom top", scrub: .6
        }
      });
      leave.to(lines[0], { xPercent: -14, opacity: .1, ease: "none" }, 0)
           .to(lines[1], { xPercent: 14, opacity: .1, ease: "none" }, 0)
           .to("[data-open-sub]", { opacity: 0, y: -20, ease: "none" }, 0)
           .to("[data-open-eyebrow]", { opacity: 0, ease: "none" }, 0)
           .to("[data-open-cue]", { opacity: 0, ease: "none" }, 0);
      if (media) leave.to(media, { scale: 1.24, yPercent: -6, ease: "none" }, 0);
      if (route) leave.to(route, { strokeDashoffset: 0, ease: "none" }, 0);
    }

    /* ---- chapter 2 and chapter 5 ------------------------- */
    /* Both are desktop-only builds, and both have to be torn down again
       when the window crosses 900px — a pin left behind at phone width is
       a scroll trap. gsap.matchMedia() is what cirs.js uses for exactly
       this, and it reverts everything its callback set on the way out. */
    var mm = gsap.matchMedia();

    mm.add("(min-width: 900px)", function () {
      /* chapter 2: the campus recedes into one plate in a dark field */
      var portal = $("[data-portal]");
      if (portal) {
        var plate = $("[data-portal-plate]", portal);
        var depth = $("[data-portal-depth]", portal);
        var copy = $("[data-portal-copy]", portal);

        gsap.set(plate, { scale: 1.42, yPercent: 6 });
        gsap.set(copy, { opacity: 0, y: 40 });

        gsap.timeline({
          scrollTrigger: {
            trigger: portal, start: "top top", end: "+=110%",
            pin: $("[data-portal-stage]", portal), scrub: .7, anticipatePin: 1
          }
        })
          .to(plate, { scale: 1, yPercent: 0, ease: "power2.out", duration: 1 }, 0)
          .to(depth, { opacity: 1, ease: "none", duration: 1 }, 0)
          .to(copy, { opacity: 1, y: 0, ease: "power2.out", duration: .7 }, .45);
      }

      /* chapter 5: the pathway rail, pinned and dragged sideways */
      var track = $("[data-pathways]");
      var rail = $("[data-pathways-rail]");
      if (!track || !rail) return;

      var scenes = $$(".ajw", rail);
      var dots = $$(".ajw__dot");
      var section = $(".aj-paths");
      var current = -1;
      var distance = function () {
        return Math.max(0, rail.scrollWidth - window.innerWidth + 32);
      };

      var railTween = gsap.to(rail, {
        x: function () { return -distance(); },
        ease: "none",
        scrollTrigger: {
          trigger: track, start: "top top",
          end: function () { return "+=" + (distance() + window.innerHeight * .4); },
          pin: true, scrub: .6, invalidateOnRefresh: true, anticipatePin: 1,
          onUpdate: function (self) {
            var i = Math.round(self.progress * (scenes.length - 1));
            if (i === current) return;
            current = i;
            scenes.forEach(function (s, n) { s.classList.toggle("is-on", n === i); });
            dots.forEach(function (d, n) { d.classList.toggle("is-on", n === i); });
            // The ground belongs to the section, and the colour comes from
            // the scene's own --aj-scene, so alumni.css stays the one place
            // any of these five colours is written down.
            var ground = getComputedStyle(scenes[i]).getPropertyValue("--aj-scene").trim();
            if (ground) gsap.to(section, { backgroundColor: ground, duration: .9, ease: "power2.out" });
          }
        }
      });

      function goto(n) {
        var trig = railTween.scrollTrigger;
        if (!trig) return;
        var p = scenes.length > 1 ? n / (scenes.length - 1) : 0;
        window.scrollTo({ top: trig.start + (trig.end - trig.start) * p, behavior: "smooth" });
      }
      dots.forEach(function (d, n) { d.addEventListener("click", function () { goto(n); }); });

      track.classList.add("is-live");
      if (scenes[0]) scenes[0].classList.add("is-on");
      if (dots[0]) dots[0].classList.add("is-on");

      return function () {
        // Leaving the desktop query: hand the scenes back to the stack and
        // give the section its own ground again.
        track.classList.remove("is-live");
        scenes.forEach(function (s) { s.classList.add("is-on"); });
        dots.forEach(function (d) { d.classList.remove("is-on"); });
        if (section) gsap.set(section, { clearProps: "backgroundColor" });
        current = -1;
      };
    });

    mm.add("(max-width: 899px)", function () {
      /* Narrow: no pins anywhere. The plate and the copy still arrive, and
         every pathway scene is simply on. */
      var portal = $("[data-portal]");
      if (portal) {
        gsap.set($("[data-portal-depth]", portal), { opacity: 1 });
        gsap.set($("[data-portal-copy]", portal), { opacity: 1, y: 0 });
        gsap.from($("[data-portal-plate]", portal), {
          opacity: 0, y: 30, duration: 1, ease: "power3.out",
          scrollTrigger: { trigger: portal, start: "top 80%", once: true }
        });
      }
      $$(".ajw").forEach(function (s) { s.classList.add("is-on"); });
    });

    /* ---- chapter 3: the field comes up -------------------- */
    var cField = $("[data-constellation-field]");
    if (cField) {
      var cLines = $$(".ajc__line", cField);
      var cPoints = $$(".ajc__pt", cField);

      cLines.forEach(function (l) {
        var d = l.getTotalLength();
        gsap.set(l, { strokeDasharray: d, strokeDashoffset: d, opacity: 1 });
      });

      gsap.timeline({
        scrollTrigger: { trigger: cField, start: "top 78%", once: true }
      })
        .to(cLines, {
          strokeDashoffset: 0, duration: 1.5, ease: "power2.inOut", stagger: .045
        }, 0)
        .to(cPoints, {
          opacity: 1, duration: .5, ease: "power2.out", stagger: .04
        }, .35);
    }

    /* ---- the brightest stars breathe ---------------------- */
    if (sky && sky.twinklers.length) {
      sky.twinklers.forEach(function (star, i) {
        gsap.to(star, {
          opacity: 0.30, duration: 1.6 + (i % 7) * 0.42,
          repeat: -1, yoyo: true, ease: "sine.inOut", delay: (i % 11) * 0.31
        });
      });
      // Nothing off-screen should be animating.
      ScrollTrigger.create({
        trigger: "[data-constellation-field]",
        start: "top bottom", end: "bottom top",
        onToggle: function (self) {
          sky.twinklers.forEach(function (star) {
            var tws = gsap.getTweensOf(star);
            tws.forEach(function (t) { self.isActive ? t.play() : t.pause(); });
          });
        }
      });
    }

    /* ---- chapter 7: the return ---------------------------- */
    var ret = $("[data-return]");
    if (ret) {
      var rMedia = $("[data-return-media] img", ret);
      if (rMedia) {
        gsap.fromTo(rMedia, { scale: 1.16 }, {
          scale: 1.02, ease: "none",
          scrollTrigger: { trigger: ret, start: "top bottom", end: "bottom top", scrub: .8 }
        });
      }
      if (gather) {
        // The marks arrive from outside the frame and settle onto the ring:
        // the scattered come home, and the centre lights last.
        gsap.set(gather.ring, { opacity: 0 });
        gsap.set(gather.hub, { opacity: 0, scale: 0, transformOrigin: "200px 200px" });
        gather.dots.forEach(function (d, i) {
          var a = (i / gather.dots.length) * Math.PI * 2 - Math.PI / 2;
          gsap.set(d, {
            opacity: 0,
            x: Math.cos(a) * 240, y: Math.sin(a) * 240
          });
        });
        gsap.timeline({
          scrollTrigger: { trigger: ret, start: "top 62%", once: true }
        })
          .to(gather.dots, {
            opacity: 1, x: 0, y: 0, duration: 1.5, ease: "power3.out", stagger: .035
          }, 0)
          .to(gather.ring, { opacity: 1, duration: 1.2, ease: "power2.out" }, .5)
          .to(gather.hub, { opacity: 1, scale: 1, duration: .8, ease: "back.out(2)" }, 1.1);
      }
    }

    // Images and fonts land late and move everything below them.
    window.addEventListener("load", function () { ScrollTrigger.refresh(); });
  }

  /* ==========================================================
     Fail-open
     Nothing on this page may stay invisible because a timeline
     did not run. Anything still at zero opacity a moment after
     load is simply shown.
     ========================================================== */
  function failOpen() {
    $$(".aj-open__line > span, [data-open-sub], [data-open-cue], .ajc__pt, .ajc__line, " +
       "[data-portal-plate], [data-portal-copy], [data-portal-depth]").forEach(function (el) {
      var o = parseFloat(getComputedStyle(el).opacity);
      if (o < .05) {
        el.style.opacity = "1";
        el.style.transform = "none";
        el.style.strokeDashoffset = "0";
      }
    });
  }

  function start() {
    var parts = interactions();
    var sky = buildStars();
    var gather = buildGather();
    if (canMove) {
      try { motion(parts, gather, sky); }
      catch (err) { failOpen(); }
      window.setTimeout(failOpen, 2600);
    } else {
      // No motion at all: reveal everything the sheet held back. js-motion
      // is cirs.js's flag, not this file's, and is left alone — the other
      // components on the page read it too.
      failOpen();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
