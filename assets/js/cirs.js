/* ============================================================
   CIRS — interaction layer
   GSAP + ScrollTrigger for scroll choreography, Lenis for the
   scroll itself. Everything is progressive enhancement: if the
   libraries are blocked, or motion is reduced, the page is
   complete and nothing stays hidden.
   ============================================================ */
(function () {
  "use strict";

  // Inline scripts ignore `defer`, so when this file is inlined (the dist and
  // editor single-file builds) it can run before the deferred GSAP/Lenis
  // <script> tags that precede it in the document have executed — making
  // hasGSAP false below even though the libraries are on their way in. Every
  // deferred script is guaranteed to finish before DOMContentLoaded, so
  // gating the whole module on that event fixes both cases. For the real,
  // externally-loaded cirs.js (also deferred) this is a no-op: readyState is
  // already past "loading" by the time an external deferred script runs.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  function boot() {

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasGSAP = typeof window.gsap !== "undefined";
  var hasST = hasGSAP && typeof window.ScrollTrigger !== "undefined";
  var animate = hasGSAP && !reduced;

  if (hasST) gsap.registerPlugin(ScrollTrigger);

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ==========================================================
     Smooth scroll
     ========================================================== */
  var lenis = null;
  if (typeof window.Lenis !== "undefined" && !reduced) {
    lenis = new Lenis({ duration: 1.05, smoothWheel: true, touchMultiplier: 1.5 });
    if (hasGSAP) {
      lenis.on("scroll", function () { if (hasST) ScrollTrigger.update(); });
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    } else {
      (function raf(t) { lenis.raf(t); requestAnimationFrame(raf); })(0);
    }
  }

  /* ----------------------------------------------------------
     Scroll subscription
     Lenis suppresses the native scroll event, so anything that
     reacts to scrolling must subscribe through Lenis when it is
     running. Subscribing to window.scroll directly would simply
     never fire.
     ---------------------------------------------------------- */
  /* A sentinel is a zero-height marker placed at a scroll depth. Watching it
     with IntersectionObserver reports crossing that depth without depending on
     scroll events, Lenis, GSAP or requestAnimationFrame. */
  function sentinel(px, onCross) {
    var state = null;
    function report(past) {
      if (past === state) return;
      state = past;
      onCross(past);
    }
    function depth() { return typeof px === "function" ? px() : px; }
    function check() { report((window.scrollY || window.pageYOffset || 0) > depth()); }

    // Three independent signals, because each can be unavailable: ScrollTrigger
    // (fed by Lenis), IntersectionObserver on a marker, and the native event.
    if (hasST) ScrollTrigger.create({ onUpdate: check, onRefresh: check });
    if ("IntersectionObserver" in window) {
      var el = document.createElement("div");
      el.setAttribute("aria-hidden", "true");
      el.style.cssText = "position:absolute;left:0;width:1px;height:1px;pointer-events:none;top:" + depth() + "px";
      document.body.appendChild(el);
      new IntersectionObserver(function (entries) {
        report(entries[0].boundingClientRect.top < 0);
      }, { threshold: 0 }).observe(el);
    }
    window.addEventListener("scroll", check, { passive: true });
    if (lenis) lenis.on("scroll", check);
    check();
  }

  function onScroll(fn) {
    // ScrollTrigger is the most reliable source: it is fed by Lenis when Lenis
    // is running and falls back to the native event when it is not.
    if (hasST) {
      var st = ScrollTrigger.create({ onUpdate: fn, onRefresh: fn });
      return function () { st.kill(); };
    }
    if (lenis) { lenis.on("scroll", fn); return function () { lenis.off("scroll", fn); }; }
    window.addEventListener("scroll", fn, { passive: true });
    return function () { window.removeEventListener("scroll", fn); };
  }

  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      var id = a.getAttribute("href");
      // Links to pages that do not exist in this prototype. Swallow the click
      // rather than letting the browser jump to the top of the page.
      if (id === "#") { e.preventDefault(); return; }
      if (id.length < 2) return;
      var t = document.querySelector(id);
      if (!t) return;
      e.preventDefault();
      closeDrawer();
      if (lenis) lenis.scrollTo(t, { offset: -88 });
      else t.scrollIntoView({ behavior: reduced ? "auto" : "smooth" });
    });
  });

  /* ==========================================================
     Line splitter
     Wraps each rendered line of a heading in its own mask, so
     lines can ride up independently. Re-runs on resize because
     the line breaks move.
     ========================================================== */
  function splitLines(el) {
    if (el.dataset.splitDone === "1") return null;
    var original = el.innerHTML;
    el.dataset.splitOriginal = original;

    // Wrap every word so we can measure where the lines break.
    var html = original.replace(/(<[^>]+>)|([^\s<]+)/g, function (m, tag, word) {
      return tag ? tag : '<span class="w">' + word + "</span>";
    });
    el.innerHTML = html;

    var words = $$("span.w", el);
    if (!words.length) { el.innerHTML = original; return null; }

    var lines = [], current = null, lastTop = null;
    words.forEach(function (w) {
      var top = Math.round(w.offsetTop);
      if (lastTop === null || Math.abs(top - lastTop) > 3) {
        current = [];
        lines.push(current);
        lastTop = top;
      }
      current.push(w);
    });

    // Rebuild as one mask per line, preserving inline markup within the line.
    var frag = document.createDocumentFragment();
    lines.forEach(function (lineWords) {
      var mask = document.createElement("span");
      mask.className = "line-mask";
      var inner = document.createElement("span");
      lineWords.forEach(function (w, i) {
        // A word inside inline formatting (<em>, <b>, ...) keeps that
        // formatting — otherwise splitting a line would silently drop it.
        var parent = w.parentNode;
        var wrap = parent && parent.tagName && /^(EM|B|STRONG|I)$/.test(parent.tagName)
          ? document.createElement(parent.tagName.toLowerCase()) : null;
        var target = wrap || inner;
        while (w.firstChild) target.appendChild(w.firstChild);
        if (wrap) inner.appendChild(wrap);
        if (i < lineWords.length - 1) inner.appendChild(document.createTextNode(" "));
      });
      mask.appendChild(inner);
      frag.appendChild(mask);
    });
    el.innerHTML = "";
    el.appendChild(frag);
    el.dataset.splitDone = "1";
    return $$(".line-mask > span", el);
  }

  function unsplit(el) {
    if (el.dataset.splitDone !== "1") return;
    el.innerHTML = el.dataset.splitOriginal;
    el.dataset.splitDone = "0";
  }

  /* ==========================================================
     Opening sequence
     ========================================================== */
  function playIntro(done) {
    var curtain = $("#curtain");
    if (!curtain) { done(); return; }

    var finished = false;
    function finish() {
      if (finished) return;
      finished = true;
      if (curtain.parentNode) curtain.remove();
      document.body.classList.remove("is-locked");
      if (lenis) lenis.start();
      if (hasST) ScrollTrigger.refresh();
      done();
    }

    // A hidden tab suspends requestAnimationFrame, so GSAP never ticks and an
    // onComplete would never fire. Nobody is watching an intro they cannot see,
    // so skip straight to the page.
    if (!animate || document.visibilityState === "hidden") { finish(); return; }

    if (lenis) lenis.stop();
    document.body.classList.add("is-locked");

    // Hard ceiling. setTimeout still fires in a background tab, so the curtain
    // can never strand a visitor behind a full-screen panel with scroll locked.
    window.setTimeout(finish, 4200);

    var tl = gsap.timeline({ onComplete: finish });

    tl.from(curtain.querySelectorAll("img, .curtain__deva, .curtain__en"), {
        opacity: 0, y: 16, duration: .7, ease: "power2.out", stagger: .12
      })
      .to(curtain.querySelector(".curtain__bar i"), { width: "100%", duration: .9, ease: "power1.inOut" }, "-=.25")
      .to(curtain.querySelectorAll("img, .curtain__deva, .curtain__en, .curtain__bar"), {
        opacity: 0, y: -12, duration: .45, ease: "power2.in", stagger: .05
      })
      .to(curtain, { yPercent: -100, duration: .95, ease: "expo.inOut" }, "-=.1");
  }

  /* ==========================================================
     Hero
     ========================================================== */
  function heroIn() {
    var hero = $(".hero");
    if (!hero || !animate) return;
    // Loaded out of sight: show the hero as-is rather than hiding it behind an
    // entrance that cannot run.
    if (document.visibilityState === "hidden") { heroParallax(); return; }

    var h1 = $(".hero h1");
    var lines = h1 ? splitLines(h1) : null;
    var rest = [$(".hero .marker"), $(".hero__scroll")].filter(Boolean);

    var tl = gsap.timeline();
    if (lines) {
      gsap.set(lines, { yPercent: 112 });
      tl.to(lines, { yPercent: 0, duration: 1.15, ease: "expo.out", stagger: .09 });
    }
    tl.from(rest, { opacity: 0, y: 22, duration: .9, ease: "power3.out", stagger: .1 }, lines ? "-=.75" : 0);

    heroParallax();
  }

  function heroParallax() {
    var hero = $(".hero"), img = $(".hero__media img, .hero__media video");
    if (!hero || !img || !hasST || !animate) return;

    // The media is sized exactly to the hero, so scaling from the centre is
    // the only thing that covers the drift: it gains (scale-1)/2 of its
    // height as overhang on each edge, and the drift may not exceed that.
    // This ended at scale 1 while still pushed 6% down, which left 6% of the
    // hero's own ground showing above the video as a black band on the way
    // back up. Both ends now keep more overhang than the drift spends.
    gsap.fromTo(img, { scale: 1.20, yPercent: -4 }, {
      scale: 1.12, yPercent: 4, ease: "none",
      scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: .6 }
    });
  }

  /* ==========================================================
     Generic scroll choreography
     ========================================================== */
  function choreograph() {
    if (!hasST || !animate) return;

    // Headings rise line by line. The hero headline is excluded — it belongs to
    // the opening timeline, not to a scroll trigger.
    $$("[data-split]").filter(function (el) { return !el.closest(".hero"); }).forEach(function (el) {
      var lines = splitLines(el);
      if (!lines) return;
      gsap.set(lines, { yPercent: 110 });
      gsap.to(lines, {
        yPercent: 0, duration: 1.05, ease: "expo.out", stagger: .08,
        scrollTrigger: { trigger: el, start: "top 88%", once: true }
      });
    });

    // Photographs open from a clip and settle from a slow push-in.
    $$(".img-reveal").forEach(function (frame) {
      var img = $("img", frame);
      var tl = gsap.timeline({ scrollTrigger: { trigger: frame, start: "top 86%", once: true } });
      tl.fromTo(frame, { clipPath: "inset(0% 0% 100% 0%)" },
                       { clipPath: "inset(0% 0% 0% 0%)", duration: 1.1, ease: "expo.out" });
      // Settles to 1.12, not 1: the drift below spends 4% and needs the
      // overhang to cover it, exactly as the hero does.
      if (img) tl.fromTo(img, { scale: 1.18 }, { scale: 1.12, duration: 1.4, ease: "expo.out" }, 0);

      // and keep drifting gently while they are on screen
      if (img) {
        gsap.fromTo(img, { yPercent: -4 }, {
          yPercent: 4, ease: "none",
          scrollTrigger: { trigger: frame, start: "top bottom", end: "bottom top", scrub: .8 }
        });
      }
    });

    // Everything else fades up.
    $$(".rv").forEach(function (el) {
      gsap.from(el, {
        opacity: 0, y: 24, duration: .95, ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 90%", once: true }
      });
    });

    // Record figures ride out of their masks.
    $$(".fig-mask > span").forEach(function (fig) {
      gsap.from(fig, {
        yPercent: 105, duration: 1.05, ease: "expo.out",
        scrollTrigger: { trigger: fig.parentNode, start: "top 88%", once: true }
      });
    });

    // Facilities rules draw themselves.
    $$(".facilities > div").forEach(function (d, i) {
      gsap.from(d, {
        opacity: 0, y: 18, duration: .8, ease: "power3.out", delay: (i % 3) * .08,
        scrollTrigger: { trigger: d, start: "top 92%", once: true }
      });
    });

    // Parallax on the campus band photograph.
    var band = $(".band__media img");
    if (band) {
      gsap.fromTo(band, { yPercent: -8, scale: 1.12 }, {
        yPercent: 8, ease: "none",
        scrollTrigger: { trigger: ".band", start: "top bottom", end: "bottom top", scrub: .7 }
      });
    }
  }

  /* ==========================================================
     Day — pinned horizontal timetable
     ========================================================== */
  function dayTrack() {
    var sec = $("#day"), pin = $(".dayh__pin"), track = $(".dayh__track");
    var fill = $(".dayh__fill"), tick = $("#dayTick");
    if (!sec || !track) return;

    function staticMode() { sec.classList.add("is-static"); }

    if (!hasST || !animate || typeof gsap.matchMedia !== "function") { staticMode(); return; }

    var mm = gsap.matchMedia();

    mm.add("(min-width: 900px)", function () {
      sec.classList.remove("is-static");
      var moments = $$(".dmoment", track);

      var st = ScrollTrigger.create({
        trigger: sec,
        start: "top top",
        end: function () { return "+=" + Math.max(track.scrollWidth - window.innerWidth + 320, 600); },
        pin: pin,
        scrub: .8,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onUpdate: function (self) {
          var dist = Math.max(track.scrollWidth - window.innerWidth + 120, 0);
          gsap.set(track, { x: -dist * self.progress });
          if (fill) fill.style.width = (self.progress * 100).toFixed(2) + "%";
          if (tick) {
            var i = Math.min(moments.length - 1, Math.round(self.progress * (moments.length - 1)));
            var t = moments[i] && moments[i].getAttribute("data-time");
            if (t && tick.textContent !== t) tick.textContent = t;
          }
        }
      });
      return function () { st.kill(true); gsap.set(track, { clearProps: "x" }); staticMode(); };
    });

    mm.add("(max-width: 899px)", function () {
      staticMode();
      return function () {};
    });
  }

  /* ==========================================================
     Page ground shifts between paper and purple
     ========================================================== */
  function groundShift() {
    if (!hasST || !animate) return;
    $$("[data-ground]").forEach(function (sec) {
      var colour = sec.getAttribute("data-ground");
      ScrollTrigger.create({
        trigger: sec,
        start: "top 55%",
        end: "bottom 45%",
        onToggle: function (self) {
          if (self.isActive) gsap.to(document.body, { backgroundColor: colour, duration: .6, ease: "power2.out" });
          else gsap.to(document.body, { backgroundColor: "#FAF7F8", duration: .6, ease: "power2.out" });
        }
      });
    });
  }

  /* ==========================================================
     Scroll progress
     ========================================================== */
  function progressBar() {
    var bar = $("#progress");
    if (!bar) return;
    if (hasST && animate) {
      gsap.to(bar, {
        scaleX: 1, ease: "none",
        scrollTrigger: { start: 0, end: "max", scrub: .3 }
      });
    } else {
      onScroll(function () {
        var max = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.transform = "scaleX(" + ((window.scrollY || 0) / Math.max(max, 1)) + ")";
      });
    }
  }

  /* ==========================================================
     Magnetic call to action
     ========================================================== */
  function magnets() {
    if (!animate || !window.matchMedia("(hover: hover)").matches) return;
    $$("[data-magnetic]").forEach(function (el) {
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect();
        gsap.to(el, {
          x: (e.clientX - (r.left + r.width / 2)) * .25,
          y: (e.clientY - (r.top + r.height / 2)) * .35,
          duration: .5, ease: "power3.out"
        });
      });
      el.addEventListener("pointerleave", function () {
        gsap.to(el, { x: 0, y: 0, duration: .7, ease: "elastic.out(1,.5)" });
      });
    });
  }

  /* ==========================================================
     Trailing cursor ring
     The native cursor is kept — this rides behind it and swells
     over anything interactive.
     ========================================================== */
  function cursorRing() {
    var ring = $("#ring");
    if (!ring || !animate) return;
    if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) { ring.remove(); return; }

    var x = gsap.quickTo(ring, "x", { duration: .45, ease: "power3" });
    var y = gsap.quickTo(ring, "y", { duration: .45, ease: "power3" });

    window.addEventListener("pointermove", function (e) {
      x(e.clientX); y(e.clientY);
      if (ring.style.opacity !== "1") gsap.to(ring, { opacity: 1, duration: .3 });
    }, { passive: true });
    document.addEventListener("pointerleave", function () { gsap.to(ring, { opacity: 0, duration: .3 }); });

    var hot = "a, button, .dmoment, .facilities > div, .node, input, [data-magnetic]";
    document.addEventListener("pointerover", function (e) {
      if (e.target.closest && e.target.closest(hot)) ring.classList.add("is-big");
    });
    document.addEventListener("pointerout", function (e) {
      if (e.target.closest && e.target.closest(hot)) ring.classList.remove("is-big");
    });
  }

  /* ==========================================================
     Credentials ticker
     Two identical sets; the track loops by exactly one set width,
     and scroll direction flips the travel direction.
     ========================================================== */
  function ticker() {
    var track = $("#tickerTrack");
    if (!track || !animate) return;
    var set = track.firstElementChild;
    if (!set) return;

    var half = set.getBoundingClientRect().width;
    var tl = gsap.to(track, {
      x: -half, duration: half / 100, ease: "none", repeat: -1,
      modifiers: { x: function (v) { return (parseFloat(v) % half) + "px"; } }
    });

    if (hasST) {
      ScrollTrigger.create({
        onUpdate: function (self) { tl.timeScale(self.direction === -1 ? -1 : 1); }
      });
    }
    window.addEventListener("resize", function () {
      half = set.getBoundingClientRect().width;
    }, { passive: true });
  }

  /* ==========================================================
     Back to top
     ========================================================== */
  function backToTop() {
    var btn = $("#totop");
    if (!btn) return;
    btn.addEventListener("click", function () {
      if (lenis) lenis.scrollTo(0);
      else window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" });
    });
    sentinel(function () { return window.innerHeight * 1.2; },
             function (past) { btn.classList.toggle("is-on", past); });
  }

  /* ==========================================================
     Motto band drift
     ========================================================== */
  function mottoDrift() {
    if (!hasST || !animate) return;
    var band = $(".motto");
    if (!band) return;
    gsap.fromTo(band.querySelectorAll(".motto__deva, .motto__iast, .motto__en"),
      { yPercent: 26 },
      { yPercent: -20, ease: "none", stagger: .04,
        scrollTrigger: { trigger: band, start: "top bottom", end: "bottom top", scrub: .8 } });
  }

  /* ==========================================================
     Header and drawer
     ========================================================== */
  var drawer = $("#drawer"), burger = $("#burger");

  function closeDrawer() {
    if (!drawer || !drawer.classList.contains("is-open")) return;
    drawer.classList.remove("is-open");
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-label", "Open menu");
    document.body.classList.remove("is-locked");
    if (lenis) lenis.start();
    window.setTimeout(function () {
      if (!drawer.classList.contains("is-open")) drawer.hidden = true;
    }, 320);
  }

  (function chrome() {
    var header = $("#header");
    if (header) {
      // The header rides transparent over the hero and only turns solid once
      // the hero itself has scrolled mostly out of view.
      sentinel(function () {
        var hero = $(".hero");
        return hero ? Math.max(hero.getBoundingClientRect().height - 140, 80) : 80;
      }, function (past) { header.classList.toggle("is-stuck", past); });
    }
    if (!burger || !drawer) return;
    burger.addEventListener("click", function () {
      if (drawer.classList.contains("is-open")) { closeDrawer(); return; }
      drawer.hidden = false;
      requestAnimationFrame(function () { drawer.classList.add("is-open"); });
      burger.setAttribute("aria-expanded", "true");
      burger.setAttribute("aria-label", "Close menu");
      document.body.classList.add("is-locked");
      if (lenis) lenis.stop();
      if (animate) {
        gsap.from(drawer.querySelectorAll(".drawer__grid > div, .drawer__cta"), {
          opacity: 0, y: 18, duration: .6, ease: "power3.out", stagger: .06, delay: .1
        });
      }
    });
    $$("a", drawer).forEach(function (a) { a.addEventListener("click", closeDrawer); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });
    window.addEventListener("resize", function () { if (window.innerWidth > 1040) closeDrawer(); }, { passive: true });
  })();

  /* ==========================================================
     University pathways chart
     ========================================================== */
  function chart() {
    var svg = $("#worldChart");
    if (!svg) return;
    var NS = "http://www.w3.org/2000/svg";
    var W = 1000, H = 460;
    var grat = $("#grat", svg), arcs = $("#arcs", svg), nodes = $("#nodes", svg);
    function proj(lat, lon) { return [((lon + 180) / 360) * W, ((78 - lat) / 156) * H]; }

    var i, el;
    for (i = -180; i <= 180; i += 30) {
      el = document.createElementNS(NS, "line"); el.setAttribute("class", "grat");
      el.setAttribute("x1", proj(0, i)[0]); el.setAttribute("y1", 0);
      el.setAttribute("x2", proj(0, i)[0]); el.setAttribute("y2", H); grat.appendChild(el);
    }
    for (i = -60; i <= 60; i += 20) {
      el = document.createElementNS(NS, "line"); el.setAttribute("class", "grat");
      el.setAttribute("x1", 0); el.setAttribute("y1", proj(i, 0)[1]);
      el.setAttribute("x2", W); el.setAttribute("y2", proj(i, 0)[1]); grat.appendChild(el);
    }

    var ORIGIN = [10.9307, 76.7401];
    var DEST = [
      ["Boston", 42.36, -71.06], ["Berkeley", 37.87, -122.27], ["Toronto", 43.65, -79.38],
      ["London", 51.51, -0.13], ["Edinburgh", 55.95, -3.19], ["Delft", 52.01, 4.36],
      ["Dubai", 25.20, 55.27], ["New Delhi", 28.61, 77.21], ["Bengaluru", 12.97, 77.59],
      ["Singapore", 1.35, 103.82], ["Hong Kong", 22.32, 114.17], ["Tokyo", 35.68, 139.69],
      ["Melbourne", -37.81, 144.96]
    ];
    var o = proj(ORIGIN[0], ORIGIN[1]), paths = [], dots = [];

    DEST.forEach(function (d) {
      var p = proj(d[1], d[2]);
      var cx = (o[0] + p[0]) / 2;
      var cy = (o[1] + p[1]) / 2 - Math.abs(p[0] - o[0]) * .20 - 20;
      var path = document.createElementNS(NS, "path");
      path.setAttribute("class", "arc");
      path.setAttribute("d", "M" + o[0].toFixed(1) + " " + o[1].toFixed(1) +
                             " Q" + cx.toFixed(1) + " " + cy.toFixed(1) +
                             " " + p[0].toFixed(1) + " " + p[1].toFixed(1));
      arcs.appendChild(path); paths.push(path);

      var g = document.createElementNS(NS, "g");
      g.setAttribute("class", "node"); g.setAttribute("tabindex", "0");
      g.setAttribute("role", "img"); g.setAttribute("aria-label", d[0]);
      var c = document.createElementNS(NS, "circle");
      c.setAttribute("cx", p[0]); c.setAttribute("cy", p[1]); c.setAttribute("r", 2.8);
      g.appendChild(c);
      var t = document.createElementNS(NS, "text");
      var flip = p[0] > W - 110;
      t.setAttribute("x", flip ? p[0] - 7 : p[0] + 7);
      t.setAttribute("y", p[1] - 5);
      if (flip) t.setAttribute("text-anchor", "end");
      t.textContent = d[0]; g.appendChild(t);
      nodes.appendChild(g); dots.push(g);
    });

    var og = document.createElementNS(NS, "g");
    og.setAttribute("class", "node origin");
    var oc = document.createElementNS(NS, "circle");
    oc.setAttribute("cx", o[0]); oc.setAttribute("cy", o[1]); oc.setAttribute("r", 5);
    og.appendChild(oc);
    var ot = document.createElementNS(NS, "text");
    ot.setAttribute("x", o[0] - 8); ot.setAttribute("y", o[1] + 14);
    ot.setAttribute("text-anchor", "end"); ot.textContent = "Siruvani";
    og.appendChild(ot); nodes.appendChild(og);

    if (!animate) return;

    paths.forEach(function (p) {
      var len = p.getTotalLength();
      p.style.strokeDasharray = len;
      p.style.strokeDashoffset = len;
    });
    gsap.set(dots, { opacity: 0 });

    var drawn = false;
    function draw() {
      if (drawn) return;
      drawn = true;
      paths.forEach(function (p, i) {
        gsap.to(p, { strokeDashoffset: 0, duration: 1.2, ease: "power2.inOut", delay: i * .075 });
      });
      gsap.to(dots, { opacity: 1, duration: .5, stagger: .075, delay: .55 });
    }
    if (hasST) ScrollTrigger.create({ trigger: svg, start: "top 78%", once: true, onEnter: draw });
    window.setTimeout(draw, 5000);
  }

  /* ==========================================================
     Safety sweep
     GSAP's from() hides an element until its trigger fires. If a
     trigger's measured position goes stale — a late font, a late
     image, a pin that changed the page height — an element can be
     scrolled past while still invisible. This sweep catches that:
     anything inside the viewport that is still hidden is shown.
     ========================================================== */
  function startSweep() {
    var targets = $$(".rv, .img-reveal, .facilities > div, .line-mask > span, .fig-mask > span");
    if (!targets.length) return;
    var queued = false, unsub = null;

    function hidden(el) {
      if (parseFloat(getComputedStyle(el).opacity) < 0.05) return true;
      // Masked lines and figures are hidden by transform, not opacity.
      var y = gsap.getProperty(el, "yPercent");
      return Math.abs(y) > 40;
    }

    // gsap.set() applies synchronously. gsap.to() would not: the case this
    // guards against is precisely the one where the ticker is not running.
    function show(el) {
      gsap.set(el, { opacity: 1, y: 0, yPercent: 0, clearProps: "clipPath" });
    }

    function sweep() {
      queued = false;
      var h = window.innerHeight;
      for (var i = targets.length - 1; i >= 0; i--) {
        var el = targets[i];
        var r = el.getBoundingClientRect();
        if (r.top > h * 0.95) continue;   // not reached yet
        if (hidden(el)) show(el);
        targets.splice(i, 1);
      }
      if (!targets.length && unsub) unsub();
    }
    function request() {
      if (queued) return;
      queued = true;
      window.setTimeout(sweep, 400);
    }
    unsub = onScroll(request);
    window.setTimeout(sweep, 1500);
  }

  /* ==========================================================
     Fail-safe
     Nothing may stay invisible because an animation did not run.
     ========================================================== */
  function failOpen() {
    document.documentElement.classList.remove("js-motion");
    $$(".line-mask > span, .fig-mask > span").forEach(function (el) {
      if (hasGSAP) gsap.set(el, { yPercent: 0, y: 0 });
      else el.style.transform = "none";
    });
    $$(".rv, .img-reveal, .facilities > div").forEach(function (e) {
      e.style.opacity = "1"; e.style.transform = "none"; e.style.clipPath = "none";
    });
    var c = $("#curtain");
    if (c) c.remove();
  }


  /* ==========================================================
     Enquire panel
     Hover for a mouse, click for a touch screen, focus for a
     keyboard — all three drive the same open state.
     ========================================================== */
  function enquirePanel() {
    var wrap = $("#enq"), btn = $("#enqBtn");
    if (!wrap || !btn) return;

    var open = false, hoverTimer;
    var fine = window.matchMedia("(hover:hover) and (pointer:fine)").matches;

    function set(next) {
      if (next === open) return;
      open = next;
      wrap.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }

    if (fine) {
      wrap.addEventListener("mouseenter", function () {
        window.clearTimeout(hoverTimer);
        set(true);
      });
      // A short grace period: the pointer may clip a corner on its way in.
      wrap.addEventListener("mouseleave", function () {
        hoverTimer = window.setTimeout(function () { set(false); }, 180);
      });
    }

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      // With a mouse, moving onto the tab has already opened the panel, so a
      // plain toggle here would shut it the instant it was clicked. A mouse
      // click therefore only ever opens; hovering away is what closes it.
      // Touch has no hover, so there the click is the toggle.
      set(fine ? true : !open);
    });

    // Only a *keyboard* focus opens it. Reacting to every focusin meant a
    // mouse click opened the panel on focus and then the click handler below
    // toggled it straight shut again, so it never appeared.
    wrap.addEventListener("focusin", function (e) {
      var t = e.target;
      if (!t || !t.matches) return;
      try { if (t.matches(":focus-visible")) set(true); } catch (err) { /* older browser */ }
    });
    wrap.addEventListener("focusout", function (e) {
      if (!wrap.contains(e.relatedTarget)) set(false);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && open) { set(false); btn.focus(); }
    });
    document.addEventListener("click", function (e) {
      if (open && !wrap.contains(e.target)) set(false);
    });
  }

  /* ==========================================================
     Film lightbox
     The iframe is built on open and removed on close: YouTube is
     not contacted until someone asks for the film, and removing
     the element is the only thing that reliably stops the audio.
     ========================================================== */
  function filmLightbox() {
    var box = $("#lightbox"), frame = $("#lightboxFrame");
    var triggers = $$("[data-video]");
    if (!box || !frame || !triggers.length) return;

    var opener = null;

    function open(id, from) {
      opener = from || null;
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) +
              "?autoplay=1&rel=0&modestbranding=1&playsinline=1";
      f.title = "The official CIRS film";
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; " +
                "gyroscope; picture-in-picture; web-share";
      f.setAttribute("allowfullscreen", "");
      f.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
      frame.appendChild(f);

      box.hidden = false;
      document.body.classList.add("has-lightbox");
      if (lenis) lenis.stop();
      var close = $(".lightbox__close", box);
      if (close) close.focus();
    }

    function close() {
      if (box.hidden) return;
      box.hidden = true;
      frame.innerHTML = "";
      document.body.classList.remove("has-lightbox");
      if (lenis) lenis.start();
      if (opener) { opener.focus(); opener = null; }
    }

    triggers.forEach(function (t) {
      t.addEventListener("click", function (e) {
        var id = t.getAttribute("data-video");
        if (!id) return;              // no id: leave the href alone
        e.preventDefault();
        open(id, t);
      });
    });

    box.addEventListener("click", function (e) {
      if (e.target.closest("[data-close]")) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !box.hidden) close();
      // Nothing behind the dialog should be reachable while it is open.
      if (e.key === "Tab" && !box.hidden) {
        var c = $(".lightbox__close", box);
        if (c) { e.preventDefault(); c.focus(); }
      }
    });
  }


  /* ==========================================================
     Glimpses collage
     The drift is CSS. This is only the cross-fade: every so
     often one tile dissolves into another photograph from the
     same pool, so the wall is never twice the same.
     ========================================================== */
  function glimpses() {
    var sec = $("#glimpses");
    if (!sec || reduced) return;
    var tiles = $$(".gt", sec);
    if (tiles.length < 2) return;

    // The pool is whatever the markup already references, so it cannot
    // drift out of step with what is actually on disk.
    var pool = [];
    tiles.forEach(function (t) {
      var im = $("img", t);
      if (im && pool.indexOf(im.getAttribute("src")) === -1) pool.push(im.getAttribute("src"));
    });
    if (pool.length < 2) return;

    var timer = null;

    function swap() {
      var t = tiles[(Math.random() * tiles.length) | 0];
      if (!t || t.getAttribute("data-busy")) return;
      var cur = $("img", t);
      if (!cur) return;
      var next = pool[(Math.random() * pool.length) | 0];
      if (next === cur.getAttribute("src")) return;

      t.setAttribute("data-busy", "1");
      var img = document.createElement("img");
      img.className = "gt__in";
      img.alt = "";
      img.width = 440; img.height = 440;
      img.decoding = "async";
      img.src = next;

      function reveal() {
        t.appendChild(img);
        // One frame with opacity 0 in the DOM, or the transition never runs.
        requestAnimationFrame(function () { img.classList.add("is-on"); });
        window.setTimeout(function () {
          if (cur.parentNode === t) t.removeChild(cur);
          img.classList.remove("gt__in");
          img.classList.remove("is-on");
          t.removeAttribute("data-busy");
        }, 1250);
      }

      // Never fade in a blank: wait for the bytes, and give up if they
      // never come rather than leaving the tile stuck as busy.
      if (img.complete) reveal();
      else {
        img.onload = reveal;
        img.onerror = function () { t.removeAttribute("data-busy"); };
      }
    }

    function run(on) {
      if (on && !timer) timer = window.setInterval(swap, 850);
      if (!on && timer) { window.clearInterval(timer); timer = null; }
    }

    // Only while it is on screen — off screen it is invisible work, and a
    // background tab would still be fetching photographs.
    if (typeof window.IntersectionObserver !== "undefined") {
      new IntersectionObserver(function (entries) {
        run(entries[0].isIntersecting && document.visibilityState !== "hidden");
      }, { rootMargin: "200px" }).observe(sec);
      document.addEventListener("visibilitychange", function () {
        if (document.visibilityState === "hidden") run(false);
      });
    } else {
      run(true);
    }
  }

  /* ==========================================================
     Boot
     ========================================================== */
  function start() {
    backToTop();
    enquirePanel();
    filmLightbox();
    glimpses();
    if (!animate) { failOpen(); dayTrack(); chart(); progressBar(); return; }

    document.documentElement.classList.add("js-motion");
    choreograph();
    dayTrack();
    groundShift();
    progressBar();
    magnets();
    chart();
    cursorRing();
    ticker();
    mottoDrift();

    playIntro(heroIn);
    startSweep();

    // Late-loading images change every trigger position below them.
    window.addEventListener("load", function () {
      if (hasST) ScrollTrigger.refresh();
    });

    // Returning to a backgrounded tab: positions may be stale after the catch-up.
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible" && hasST) ScrollTrigger.refresh();
    });

    // If anything above threw, or ScrollTrigger never reported, show everything.
    window.setTimeout(function () {
      if (hasST && ScrollTrigger.getAll().length === 0) failOpen();
    }, 4000);

    var resizeTimer;
    window.addEventListener("resize", function () {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(function () {
        $$("[data-split]").forEach(unsplit);
        if (hasST) ScrollTrigger.refresh();
      }, 250);
    }, { passive: true });
  }

  try {
    if (document.fonts && document.fonts.ready) {
      var settled = false;
      document.fonts.ready.then(function () { if (!settled) { settled = true; start(); } });
      window.setTimeout(function () { if (!settled) { settled = true; start(); } }, 2500);
    } else {
      start();
    }
  } catch (err) {
    failOpen();
  }

  } // end boot()
})();
