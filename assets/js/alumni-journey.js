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
     The galaxy
     ----------------------------------------------------------
     A spiral seen at an angle, with CIRS at the core and the
     nineteen destinations out along its two arms.

     The arms here are the SAME arms the destinations sit on:
     tools/alumni.py writes the spiral's numbers onto the field
     as data-spiral and this reads them back, so the scattered
     stars and the named ones cannot drift apart. The spiral is
     written down once, in Python.

     Fixed seed, so it is the same galaxy on every reload — one
     that reshuffles itself is a screensaver, not a place. None
     of what is drawn here carries information: the nineteen
     destinations are separate, larger, labelled and focusable.
     ========================================================== */
  function buildSky() {
    var field = $("[data-constellation-field]");
    if (!field) return null;
    var NS = "http://www.w3.org/2000/svg";

    var sp = (field.getAttribute("data-spiral") || "").split(",").map(Number);
    if (sp.length < 8 || sp.some(isNaN)) return null;
    var CX = sp[0], CY = sp[1], R0 = sp[2], B = sp[3], ROT = sp[4],
        YK = sp[5], TMIN = sp[6], TMAX = sp[7];
    // The stars run a little further in and out than the named ones do, so
    // the arms do not simply stop where the first and last destination sits.
    var SMIN = Math.max(0.9, TMIN - 1.5), SMAX = TMAX + 0.55;

    // mulberry32: small, fast, deterministic from one integer.
    var seed = 0x1996;   // the year the school opened on this campus
    function rnd() {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }
    function gauss() { return (rnd() + rnd() + rnd() + rnd() - 2) * 0.7; }
    function el(name, attrs) {
      var n = document.createElementNS(NS, name);
      for (var k in attrs) n.setAttribute(k, attrs[k]);
      return n;
    }
    // A point on an arm, in the SVG's own units. The field is 3:2 and the
    // viewBox is 150x100, so the scale is uniform and a circle stays round.
    function arm(a, theta, rScale) {
      var r = R0 * Math.exp(B * theta) * (rScale === undefined ? 1 : rScale);
      var ang = theta + a * Math.PI + ROT;
      return [(CX + r * Math.cos(ang)) * 1.5, CY + r * Math.sin(ang) * YK];
    }

    var svg = el("svg", {
      "class": "ajc__stars", viewBox: "0 0 150 100",
      preserveAspectRatio: "none", "aria-hidden": "true", focusable: "false"
    });

    var defs = el("defs", {});
    var grad = el("radialGradient", { id: "ajCoreGlow" });
    [["0%", "#FFFDF4", ".92"], ["20%", "#FFF0D2", ".42"],
     ["52%", "#D9BC92", ".11"], ["100%", "#7A6448", "0"]].forEach(function (st) {
      grad.appendChild(el("stop", {
        offset: st[0], "stop-color": st[1], "stop-opacity": st[2] }));
    });
    defs.appendChild(grad);

    var halo = el("radialGradient", { id: "ajDiscGlow" });
    [["0%", "#8DA6DC", ".10"], ["44%", "#3E4C7C", ".035"], ["100%", "#181C33", "0"]]
      .forEach(function (st) {
        halo.appendChild(el("stop", {
          offset: st[0], "stop-color": st[1], "stop-opacity": st[2] }));
      });
    defs.appendChild(halo);

    [["ajArmBlur", 2.6], ["ajBloom", 0.55]].forEach(function (f) {
      var filter = el("filter", {
        id: f[0], x: "-70%", y: "-70%", width: "240%", height: "240%",
        "color-interpolation-filters": "sRGB"
      });
      filter.appendChild(el("feGaussianBlur", { stdDeviation: f[1] }));
      defs.appendChild(filter);
    });
    svg.appendChild(defs);

    var RMAX = R0 * Math.exp(B * SMAX);

    // ---- the disc it all sits in ----
    svg.appendChild(el("ellipse", {
      cx: CX * 1.5, cy: CY,
      rx: (RMAX * 1.5 * 1.12).toFixed(2), ry: (RMAX * YK * 1.12).toFixed(2),
      fill: "url(#ajDiscGlow)"
    }));

    // ---- the arms, as light before they are stars ----
    var gArms = el("g", { filter: "url(#ajArmBlur)" });
    [0, 1].forEach(function (a) {
      var d = "", n = 90;
      for (var i = 0; i <= n; i++) {
        var th = SMIN + (SMAX - SMIN) * i / n;
        var pt = arm(a, th);
        d += (i ? " L" : "M") + pt[0].toFixed(2) + " " + pt[1].toFixed(2);
      }
      gArms.appendChild(el("path", {
        d: d, fill: "none", stroke: a ? "#8FA8DC" : "#A8B8E0",
        "stroke-width": "2.6", "stroke-linecap": "round", opacity: "0.17"
      }));
    });
    svg.appendChild(gArms);

    // ---- the stars ----
    var hues = ["#CFE2FF", "#DCE9FF", "#FFFFFF", "#FFFFFF", "#FFF4E2",
                "#FFE0B0", "#FFC98E", "#FFB577"];
    var gBloom = el("g", { filter: "url(#ajBloom)" });
    var gCore = el("g", {});
    var bright = [];

    function star(x, y, m) {
      var hue = hues[Math.floor(rnd() * hues.length)];
      var r = 0.10 + m * m * 0.58;
      var o = 0.20 + m * 0.78;
      gCore.appendChild(el("circle", {
        "class": "ajc__star", cx: x.toFixed(2), cy: y.toFixed(2),
        r: r.toFixed(3), fill: hue, opacity: o.toFixed(2)
      }));
      if (m > 0.32) {
        gBloom.appendChild(el("circle", {
          cx: x.toFixed(2), cy: y.toFixed(2), r: (r * 2.9).toFixed(3),
          fill: hue, opacity: (o * 0.38).toFixed(2)
        }));
      }
      if (m > 0.80) bright.push({ x: x, y: y, m: m, hue: hue });
    }

    // Along the arms. The jitter is in theta and in radius, so the scatter
    // follows the curve rather than sitting in a straight cloud beside it.
    [0, 1].forEach(function (a) {
      for (var i = 0; i < 300; i++) {
        var f = Math.pow(rnd(), 0.62);                 // crowd the inside
        var th = SMIN + (SMAX - SMIN) * f;
        var p = arm(a, th + gauss() * 0.13, 1 + gauss() * 0.085);
        if (p[0] < -4 || p[0] > 154 || p[1] < -4 || p[1] > 104) continue;
        star(p[0], p[1], Math.pow(rnd(), 1.5) * (0.55 + 0.45 * (1 - f)));
      }
    });

    // The core: a dense, mostly warm knot.
    for (var c = 0; c < 190; c++) {
      var rr = Math.abs(gauss()) * 2.4;
      var aa = rnd() * Math.PI * 2;
      star((CX + Math.cos(aa) * rr) * 1.5, CY + Math.sin(aa) * rr * YK,
           Math.pow(rnd(), 1.7) * 0.72);
    }

    // And the sky behind all of it.
    for (var d2 = 0; d2 < 150; d2++) {
      star(rnd() * 150, rnd() * 100, Math.pow(rnd(), 3.2) * 0.6);
    }

    svg.appendChild(gBloom);
    svg.appendChild(gCore);

    // the core's own light, over its stars
    svg.appendChild(el("ellipse", {
      cx: CX * 1.5, cy: CY, rx: "8.2", ry: (8.2 * YK).toFixed(2),
      fill: "url(#ajCoreGlow)"
    }));

    // ---- diffraction spikes on the brightest few ----
    bright.sort(function (x, y) { return y.m - x.m; });
    var gSpike = el("g", {});
    var twinklers = [];
    bright.slice(0, 7).forEach(function (st) {
      var len = 0.9 + st.m * 1.7;
      [[len, 0.045], [0.045, len]].forEach(function (dd) {
        gSpike.appendChild(el("rect", {
          x: (st.x - dd[0]).toFixed(2), y: (st.y - dd[1]).toFixed(2),
          width: (dd[0] * 2).toFixed(2), height: (dd[1] * 2).toFixed(2),
          fill: st.hue, opacity: "0.30"
        }));
      });
      var core = el("circle", {
        "class": "ajc__star", cx: st.x.toFixed(2), cy: st.y.toFixed(2),
        r: "0.42", fill: "#FFFFFF", opacity: "0.96"
      });
      gSpike.appendChild(core);
      twinklers.push(core);
    });
    svg.appendChild(gSpike);

    field.insertBefore(svg, field.firstChild);
    return { svg: svg, twinklers: twinklers };
  }

  /* ==========================================================
     Motion
     ========================================================== */
  function motion(parts, sky) {
    /* ---- chapter 1: the opening --------------------------- */
    /* The site opens every page behind a full-screen curtain that cirs.js
       holds for up to 4.2 seconds, with the scroll locked under it. An
       entrance that starts on DOMContentLoaded therefore plays out
       entirely underneath it and is over before the curtain lifts — which
       is why this one appeared not to run at all. So the timeline is built
       paused and released when the curtain is actually gone. */
    function whenCurtainGone(play) {
      var curtain = document.getElementById("curtain");
      if (!curtain) { play(); return; }
      var fired = false, obs;
      function go() {
        if (fired) return;
        fired = true;
        if (obs) obs.disconnect();
        play();
      }
      obs = new MutationObserver(function () {
        if (!document.getElementById("curtain")) go();
      });
      obs.observe(document.body, { childList: true });
      // Past cirs.js's own 4200ms ceiling, so this can never be the thing
      // that strands the page on a still hero.
      window.setTimeout(go, 4600);
    }

    var open = $("[data-open]");
    if (open) {
      var lines = $$(".aj-open__line > span", open);
      var media = $("[data-open-media] img", open);
      var eyebrow = $("[data-open-eyebrow]", open);
      var sub = $("[data-open-sub]", open);
      var cue = $("[data-open-cue]", open);

      // The sheet parks the two rows off opposite edges with translateX in
      // vw, so there is no flash before this file runs. GSAP reads that
      // computed transform as a PIXEL x — so the starting point is set here
      // explicitly, in pixels, rather than tweening a percentage GSAP never
      // saw. Same lesson as the vertical version this replaced.
      var offL = function () { return -(window.innerWidth + lines[0].offsetWidth); };
      var offR = function () { return  (window.innerWidth + lines[1].offsetWidth); };
      if (lines[0]) gsap.set(lines[0], { x: offL(), y: 0 });
      if (lines[1]) gsap.set(lines[1], { x: offR(), y: 0 });
      gsap.set(eyebrow, { opacity: 0, y: 14 });
      if (media) gsap.set(media, { scale: 1.14 });

      var intro = gsap.timeline({ paused: true });
      // The campus settles first and keeps settling under everything else —
      // the frame is already moving when the lettering arrives, which is
      // what makes the arrival feel like a camera rather than a slide.
      if (media) intro.to(media, { scale: 1.04, duration: 2.6, ease: "power2.out" }, 0);
      // The two rows come in from opposite sides and meet.
      intro.to(eyebrow, { opacity: 1, y: 0, duration: .8, ease: "power2.out" }, .15)
           .to(lines, { x: 0, duration: 1.5, ease: "expo.out", stagger: .14 }, .28)
           .to(sub, { opacity: 1, duration: .9, ease: "power2.out" }, 1.25)
           .to(cue, { opacity: 1, duration: .7, ease: "power2.out" }, 1.5);

      whenCurtainGone(function () { intro.play(); });

      // The header goes quiet while the opening holds the screen.
      ScrollTrigger.create({
        trigger: open, start: "top top", end: "bottom 45%",
        onToggle: function (self) { root.classList.toggle("aj-quiet", self.isActive); }
      });

      /* Leaving, the two rows go back out the way they came in — each to
         its own side — while the campus pushes past the frame. The move is
         spent over the first 72% of the hero, so the screen is clear well
         before the next chapter pins.

         EVERY TWEEN HERE IS A fromTo, AND THAT IS THE WHOLE POINT. A plain
         .to() records its start value the first time it renders, and this
         timeline is built while the entrance is still parked off-screen
         waiting for the curtain. It recorded THAT as home — so scrolling
         back up to the top restored the parked state instead of the hero:
         no headline, no eyebrow, no line underneath, and the campus left
         sitting up off its own frame with black below it.

         Writing both ends out means the top of the page is a fixed state
         rather than whatever happened to be on screen when GSAP first
         looked. immediateRender:false keeps these from being stamped on at
         build time, which would undo the entrance before it plays. */
      var leave = gsap.timeline({
        scrollTrigger: {
          trigger: open, start: "top top", end: "bottom 28%",
          scrub: .55, invalidateOnRefresh: true
        }
      });
      var IR = { immediateRender: false };
      function part(el, to, at) {
        if (!el) return;
        var from = { opacity: 1, x: 0, xPercent: 0, y: 0 };
        leave.fromTo(el, from, Object.assign({ ease: "none" }, to, IR), at);
      }
      part(cue,     { opacity: 0, duration: .12 }, 0);
      part(eyebrow, { opacity: 0, y: -22, duration: .5 }, 0);
      part(sub,     { opacity: 0, y: -22, duration: .5 }, .1);
      part(lines[0], { xPercent: -60, opacity: 0, duration: .8, ease: "power1.in" }, .06);
      part(lines[1], { xPercent:  60, opacity: 0, duration: .8, ease: "power1.in" }, .06);
      if (media) {
        leave.fromTo(media,
          { scale: 1.04, yPercent: 0 },
          { scale: 1.3, yPercent: -7, ease: "none", duration: 1,
            immediateRender: false }, 0);
      }
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
      // How far the rail actually has to travel sideways.
      var distance = function () {
        return Math.max(0, rail.scrollWidth - window.innerWidth + 32);
      };
      /* And how much scrolling that travel is spread over. At 1 the rail
         moves a pixel sideways for every pixel scrolled, which runs the
         five scenes past far too briskly to read any of them. At 2.2 each
         scene holds the screen for better than twice as long without the
         rail moving any further than it did. This is the pacing dial for
         the chapter; nothing else needs to change with it. */
      var PACE = 2.2;
      var travel = function () {
        return Math.round(distance() * PACE + window.innerHeight * .5);
      };

      var railTween = gsap.to(rail, {
        x: function () { return -distance(); },
        ease: "none",
        scrollTrigger: {
          trigger: track, start: "top top",
          end: function () { return "+=" + travel(); },
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
    }

    /* ---- put every other trigger on the page right -------- */
    /* This page pins two chapters, and a pin inserts a spacer — about
       3,200px of it. cirs.js has already measured its own reveals by then,
       so every .rv below the pins is holding a trigger position that is now
       thousands of pixels off, never fires, and leaves the heading it was
       meant to reveal sitting at opacity 0. Ten of the eleven on this page
       did exactly that.

       One refresh once the pins exist re-measures all of them, cirs.js's
       included. It has to happen after gsap.matchMedia() has run its
       callback, hence the frame. */
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { ScrollTrigger.refresh(); });
    });
    // Images and fonts land late and move everything below them again.
    window.addEventListener("load", function () { ScrollTrigger.refresh(); });

    /* And a net under that, because a reader can be scrolling before load.
       Anything still invisible once it is inside the viewport is shown. */
    var net = gsap.utils.toArray(".rv, .ajp, .ajv");
    function sweep() {
      for (var i = net.length - 1; i >= 0; i--) {
        var e = net[i];
        var r = e.getBoundingClientRect();
        if (r.top > window.innerHeight * 0.95) continue;
        if (parseFloat(getComputedStyle(e).opacity) < 0.1) {
          gsap.set(e, { opacity: 1, y: 0, clearProps: "transform" });
        }
        net.splice(i, 1);
      }
      if (!net.length) window.removeEventListener("scroll", queue);
    }
    var queued = false;
    function queue() {
      if (queued) return;
      queued = true;
      window.setTimeout(function () { queued = false; sweep(); }, 350);
    }
    window.addEventListener("scroll", queue, { passive: true });
    window.setTimeout(sweep, 2000);
  }

  /* ==========================================================
     Fail-open
     Nothing on this page may stay invisible because a timeline
     did not run. Anything still at zero opacity a moment after
     load is simply shown.
     ========================================================== */
  /* It may only restore OPACITY. An earlier version also wrote
     transform:none, which is a different thing entirely on this page:
     the scroll cue is centred with translateX(-50%) and every one of the
     nineteen destinations is placed with translate(-50%,-50%), so
     clearing their transforms threw the cue half its own width to the
     right and would have unpinned every star from its arm. The one
     element whose transform genuinely has to be undone is a masked
     headline line, and that is done by name, through GSAP, which knows
     what it set. */
  function failOpen() {
    $$(".aj-open__line > span").forEach(function (el) {
      var parked = Math.abs(gsap.getProperty(el, "x")) > 40 ||
                   Math.abs(gsap.getProperty(el, "xPercent")) > 20 ||
                   Math.abs(gsap.getProperty(el, "y")) > 12;
      if (parked) gsap.set(el, { x: 0, xPercent: 0, y: 0, opacity: 1 });
    });
    $$("[data-open-sub], [data-open-cue], [data-open-eyebrow], .ajc__pt, " +
       "[data-portal-plate], [data-portal-copy], [data-portal-depth]").forEach(function (el) {
      if (parseFloat(getComputedStyle(el).opacity) < .05) el.style.opacity = "1";
    });
    $$(".ajc__line").forEach(function (el) {
      if (parseFloat(getComputedStyle(el).opacity) < .05) el.style.opacity = "1";
      if (el.style.strokeDashoffset) el.style.strokeDashoffset = "0";
    });
  }

  /* Did motion() actually build this page's chapters? That is the only
     question worth asking before sweeping, and it is answerable: every
     chapter registers a ScrollTrigger against its own section. */
  function motionBuilt() {
    if (!window.ScrollTrigger) return false;
    return ScrollTrigger.getAll().some(function (t) {
      var el = t.trigger;
      return el && el.closest &&
             el.closest(".aj-open, .ajc__field, .ajw-track, .aj-portal, .aj-return");
    });
  }

  function start() {
    var parts = interactions();
    var sky = buildSky();
    if (canMove) {
      try { motion(parts, sky); }
      catch (err) { failOpen(); }
      /* The sweep fires ONLY if nothing got built. It used to fire on a
         plain timer, and that made it a saboteur rather than a safety
         net: by the time it ran the reader could already have scrolled,
         and it would then shove the scroll cue, the eyebrow and the
         departure chapter's copy back to full opacity — over the top of
         the scroll-driven timelines that had quite deliberately just
         taken them down. The scroll cue stayed on screen the whole way
         through the hero because of it. */
      window.setTimeout(function () {
        if (!motionBuilt()) failOpen();
      }, 3200);
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
