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
  // The photograph wall has its own infinite drag/scroll surface and must not
  // compete with document-level smooth scrolling.
  if (typeof window.Lenis !== "undefined" && !reduced && !document.body.classList.contains("wall")) {
    lenis = new Lenis({ duration: 1.05, smoothWheel: true, touchMultiplier: 1.5 });
    if (hasGSAP) {
      lenis.on("scroll", function () { if (hasST) ScrollTrigger.update(); });
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    } else {
      (function raf(t) { lenis.raf(t); requestAnimationFrame(raf); })(0);
    }
  }

  // Route Crossroads section steps through the existing scroll controller.
  if (document.querySelector("[data-crossroads-intro]")) {
    window.addEventListener("crossroads-intro-scroll", function (event) {
      if (!lenis || !event.detail || event.detail.immediate) return;
      event.preventDefault();
      lenis.scrollTo(event.detail.top, {
        duration:0.8, force:true, lock:true,
        onComplete:event.detail.onComplete
      });
    });
  }

  // Page-specific section navigation can ask the shared smooth-scroll engine
  // to land precisely without coupling the page script to Lenis.
  window.addEventListener("cirs-section-scroll", function (event) {
    if (!lenis || !event.detail) return;
    event.preventDefault();
    lenis.scrollTo(event.detail.top, {
      duration:event.detail.duration,
      force:true,
      lock:true,
      onComplete:event.detail.onComplete
    });
  });

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

  /* ----------------------------------------------------------
     An anchor arrived at from another page
     The browser jumps to it while the page is still short: the
     pinned sections have not taken their spacers yet and the
     photographs below have not loaded, so the place it lands is
     not where the section finally sits. ScrollTrigger.refresh()
     on load settles the real layout; this puts the page back on
     the anchor once it has, at the same offset a click uses.

     Without it a cross-page anchor lands wherever the unfinished
     layout happened to put it — which is why the Enquire menu's
     Student Login, at the foot of a page with a pinned hero,
     arrived at the top of it instead.
     ---------------------------------------------------------- */
  var hashArmed = false;

  function openHash() {
    var id = window.location.hash;
    if (!id || id.length < 2) return;
    // The opening curtain holds the page at the top with the scroll locked,
    // so moving now would only be undone when it lifts. finish() calls this
    // again on the way out, which is where the move actually happens.
    if (document.body.classList.contains("is-locked")) return;
    if (hashArmed) return;
    var t;
    // A hash is not necessarily a valid selector — #2026 is legal in a URL.
    try { t = document.querySelector(id); } catch (err) { return; }
    if (!t) return;
    hashArmed = true;

    var timer;

    function align() {
      if (lenis) {
        // Lenis clamps to the page height it measured last. On a page whose
        // photographs have not all arrived that height is still the short
        // one, and an anchor near the foot is silently cut back to it — the
        // symptom being a jump that stops halfway down and stays there.
        lenis.resize();
        lenis.scrollTo(t, { offset: -88, immediate: true });
      } else {
        t.scrollIntoView();
      }
    }
    // One jump is not enough: the page goes on moving underneath the anchor as
    // photographs arrive and the pinned sections claim their spacers. But
    // aligning *during* a refresh fights ScrollTrigger, which restores the
    // scroll position itself as part of one — that overshoots. So wait for the
    // refreshes to stop coming, and only then move, once.
    function schedule() {
      window.clearTimeout(timer);
      timer = window.setTimeout(align, 160);
    }
    // Chasing an anchor the visitor has already scrolled away from is worse
    // than never having jumped at all.
    function stop() {
      window.clearTimeout(timer);
      if (hasST) ScrollTrigger.removeEventListener("refresh", schedule);
      window.removeEventListener("wheel", stop);
      window.removeEventListener("touchstart", stop);
      window.removeEventListener("keydown", stop);
    }

    schedule();
    if (hasST) ScrollTrigger.addEventListener("refresh", schedule);
    window.addEventListener("wheel", stop, { passive: true });
    window.addEventListener("touchstart", stop, { passive: true });
    window.addEventListener("keydown", stop);
    window.setTimeout(stop, 6000);
  }

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

    var lines = [], current = null, lineBand = null;
    words.forEach(function (w) {
      // Different font ascenders can give words on one baseline different tops.
      // Use their shared vertical band, not a fixed offsetTop tolerance.
      var rect = w.getBoundingClientRect();
      var overlap = lineBand ? Math.min(lineBand.bottom, rect.bottom) - Math.max(lineBand.top, rect.top) : 0;
      if (!lineBand || overlap < Math.min(lineBand.bottom - lineBand.top, rect.height) * .5) {
        current = [];
        lines.push(current);
        lineBand = { top: rect.top, bottom: rect.bottom };
      } else {
        lineBand.top = Math.max(lineBand.top, rect.top);
        lineBand.bottom = Math.min(lineBand.bottom, rect.bottom);
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
      // The scroll is free and the layout is settled: if this page was opened
      // at an anchor, this is the first moment it can honour it.
      openHash();
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

  function claimIntroVisit() {
    var key = "cirs-intro-complete";
    try {
      if (window.sessionStorage.getItem(key) === "1") return false;
      window.sessionStorage.setItem(key, "1");
    } catch (err) {
      // Storage can be unavailable in hardened/private contexts. In that case
      // retain the existing one-visit behaviour rather than blocking startup.
    }
    return true;
  }

  /* ==========================================================
     Hero
     ========================================================== */
  function heroIn() {
    // Either opening: the video panel other pages still use, or the
    // home sequence, whose stage plays the same part.
    var hero = $(".hero") || $(".hseq__stage");
    if (!hero || !animate) return;
    // Loaded out of sight: show the hero as-is rather than hiding it behind an
    // entrance that cannot run.
    if (document.visibilityState === "hidden") { heroParallax(); return; }

    // Prepare the entrance only while the opening curtain covers the hero.
    // Without a curtain the content is already visible and must stay visible.
    if (!$("#curtain")) { heroParallax(); return; }

    var h1 = $("h1", hero);
    var lines = h1 ? splitLines(h1) : null;
    var rest = [$(".marker", hero), $(".hero__scroll", hero)].filter(Boolean);

    var tl = gsap.timeline({ paused: true });
    if (lines) {
      gsap.set(lines, { yPercent: 112 });
      tl.to(lines, { yPercent: 0, duration: 1.15, ease: "expo.out", stagger: .09 });
    }
    gsap.set(rest, { opacity: 0, y: 22 });
    tl.to(rest, { opacity: 1, y: 0, duration: .9, ease: "power3.out", stagger: .1 }, lines ? "-=.75" : 0);

    heroParallax();
    return tl;
  }

  function heroParallax() {
    var hero = $(".hero"), media = $(".hero__media");
    if (!hero || !media || !hasST || !animate) return;

    // Transform the media wrapper rather than the actively decoding video.
    // This keeps the same crop and movement without rebuilding the video's
    // composited layer on each scroll update.
    //
    // The wrapper is sized exactly to the hero, so scaling from the centre is
    // what covers the drift: it gains (scale-1)/2 of its height as overhang,
    // and the drift may not exceed that.
    // This ended at scale 1 while still pushed 6% down, which left 6% of the
    // hero's own ground showing above the video as a black band on the way
    // back up. Both ends now keep more overhang than the drift spends.
    gsap.fromTo(media, { scale: 1.20, yPercent: -4 }, {
      scale: 1.12, yPercent: 4, ease: "none",
      // Lenis already smooths the document scroll. A timed scrub here made the
      // full-screen media continue catching up after input, including after
      // the hero left the viewport. Direct scrubbing stops that offscreen work
      // and follows the restored scroll position immediately on Back.
      scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true }
    });
  }

  /* ==========================================================
     The opening sequence
     ==========================================================
     The stage is pinned by CSS sticky, so this function never pins
     anything and never touches the document's height. All it does is
     read where the three .hseq__mark boxes are and scrub the plate's
     own box between them as the track passes.

     The marks are the contract with the stylesheet. Nothing here knows
     what P2 looks like; it knows only that some element in the sheet
     says so, which is what keeps the breakpoints in the one file that
     already holds every other breakpoint on the page.
     ========================================================== */
  function heroSeq() {
    var seq = $(".hseq");
    if (!seq) return;

    var stage = $(".hseq__stage", seq),
        plate = $(".hseq__plate", seq),
        type  = $(".hseq__type", seq),
        scrim = $(".hseq__scrim", seq),
        marks = $$(".hseq__mark", seq);

    if (!stage || !plate || marks.length < 3) return;

    // No ScrollTrigger, or motion off: the sheet already lays the
    // sequence out as one still panel. Leave it alone.
    if (!hasST || !animate) { seq.classList.add("is-static"); return; }

    // Measured on refresh, never cached across one. A mark's box is
    // read relative to the stage, which is the plate's containing
    // block, so these are exactly the values the plate's inset takes.
    var P = [];
    function measure() {
      var base = stage.getBoundingClientRect();
      P = marks.map(function (m) {
        var r = m.getBoundingClientRect();
        return {
          top:    r.top - base.top,
          right:  base.right - r.right,
          bottom: base.bottom - r.bottom,
          left:   r.left - base.left,
          w:      r.width
        };
      });
    }
    measure();

    // Interpolate between two measured boxes. Keeping this in pixels
    // rather than percentages means the plate lands on the mark's box
    // exactly, whatever units the sheet used to describe it.
    function at(a, b, t) {
      return {
        top:    a.top    + (b.top    - a.top)    * t,
        right:  a.right  + (b.right  - a.right)  * t,
        bottom: a.bottom + (b.bottom - a.bottom) * t,
        left:   a.left   + (b.left   - a.left)   * t
      };
    }

    function paint(p) {
      plate.style.top    = p.top    + "px";
      plate.style.right  = p.right  + "px";
      plate.style.bottom = p.bottom + "px";
      plate.style.left   = p.left   + "px";
    }

    // The two halves of the travel: P0 to P1 over the first, P1 to P2
    // over the second. A single eased run from P0 to P2 passes through
    // a different middle and loses the first inset entirely.
    // The plate arrives at P2 at seven tenths of the travel and holds
    // there for the rest of it, still stuck. Without the hold the frame
    // lands on the same pixel the stage begins to leave on.
    var ARRIVE = .70, BEND = .45;

    function frame(t) {
      var u = Math.min(t / ARRIVE, 1);
      var box = u < BEND ? at(P[0], P[1], u / BEND)
                         : at(P[1], P[2], (u - BEND) / (1 - BEND));
      paint(box);
      // The corner arrives with the frame rather than being on from the
      // start, so the full-bleed opening has no rounded edge against
      // the window.
      plate.style.borderRadius = (u * 14) + "px";
      // The scrim exists so the headline can be read over the photograph.
      // Once the plate has drawn in, the headline is beside it rather than
      // on it and the wash has nothing left to do but crush the picture,
      // so it lifts as the plate insets. It does not go entirely: the last
      // of it keeps the foot of the frame from glaring against the ground.
      if (scrim) scrim.style.opacity = String(1 - u * .78);
      if (type) {
        // The type clears the way as the plate closes in on its column,
        // then settles. It does not fade out — the headline is the
        // page's first sentence and stays readable through the whole
        // sequence.
        type.style.opacity = String(1 - Math.min(u, .55) * .28);
      }
    }

    ScrollTrigger.create({
      trigger: seq,
      start: "top top",
      end: "bottom bottom",
      scrub: true,
      // Direct scrub, not timed. Lenis already smooths the document
      // scroll; a timed scrub here leaves the full-screen plate still
      // catching up after the sequence has left the window, which is
      // the same offscreen work heroParallax was changed to stop.
      onRefresh: function (self) { measure(); frame(self.progress || 0); },
      onUpdate:  function (self) { frame(self.progress); }
    });
  }

  /* ==========================================================
     Generic scroll choreography
     ========================================================== */
  function choreograph() {
    if (!hasST || !animate) return;

    // Headings rise line by line. The hero headline is excluded — it belongs to
    // the opening timeline, not to a scroll trigger.
    $$("[data-split]").filter(function (el) { return !el.closest(".hero, .hseq"); }).forEach(function (el) {
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

    // Everything else fades up. Crossroads covers are held back from this
    // pass: they get the same reveal with a per-column delay below, and two
    // tweens on one element's opacity is a fight nobody wins.
    $$(".rv").filter(function (el) { return !el.classList.contains("crcard"); })
      .forEach(function (el) {
        gsap.from(el, {
          opacity: 0, y: 24, duration: .95, ease: "power3.out",
          scrollTrigger: { trigger: el, start: "top 90%", once: true }
        });
      });

    // The archive wall comes in a column at a time, so a row of covers
    // arrives as a wave rather than a slab.
    $$(".crcard").forEach(function (card, i) {
      gsap.from(card, {
        opacity: 0, y: 26, duration: .85, ease: "power3.out", delay: (i % 3) * .09,
        scrollTrigger: { trigger: card, start: "top 92%", once: true }
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
     Student Life — the hero deck
     A line of oversized lettering drifting across the screen, and
     ten photographs dealt up through it. Card 0 is already down
     when the page opens; the rest rise from below at a tilt as the
     section is scrolled, each landing square on top of the last.

     The lettering has two layers on purpose: .slhero__run carries
     the CSS keyframe, which runs whether or not this file does, and
     .slhero__push carries the scroll offset set here. One element
     cannot hold both — the transform this sets would cancel the
     keyframe's.

     No pin under 700px. A pinned scrub on a phone is a scroll that
     fights the thumb, so there the deck is a swipe track and the
     lettering simply drifts.
     ========================================================== */
  function slHero() {
    var sec = $(".slhero");
    if (!sec) return;
    var pin = $(".slhero__pin", sec), push = $(".slhero__push", sec);
    var deck = $(".slhero__deck", sec);
    var cards = $$(".slcard", sec);
    if (!cards.length) return;

    // A new order on every load. Ten photographs dealt in the same sequence
    // every time is a slideshow; dealt in a different one each visit, the
    // hero is the school rather than a fixed advertisement for ten moments
    // of it. Fisher-Yates over the elements themselves, so the swipe track
    // the phone falls back to is shuffled too, and so every later lookup —
    // z-order, the deal, the clean-up — simply follows the DOM.
    if (deck) {
      for (var k = cards.length - 1; k > 0; k--) {
        var j = Math.floor(Math.random() * (k + 1));
        var tmp = cards[k]; cards[k] = cards[j]; cards[j] = tmp;
      }
      cards.forEach(function (c) { deck.appendChild(c); });
    }

    function staticMode() { sec.classList.add("is-static"); }

    if (!hasST || !animate || typeof gsap.matchMedia !== "function") { staticMode(); return; }

    var mm = gsap.matchMedia();

    mm.add("(min-width: 700px)", function () {
      sec.classList.remove("is-static");
      var n = cards.length;

      function deal(p) {
        // The highest card that has started to rise: the top of the deck.
        var top = Math.min(Math.max(Math.ceil(p * n), 0), n - 1);
        for (var i = 0; i < n; i++) {
          // Card i rises through the slot that ends at i/n, so card 0 is
          // already down at the top of the page and the last lands with a
          // beat of scroll to spare.
          var t = Math.min(Math.max((p - (i - 1) / n) * n, 0), 1);
          var e = t * t * (3 - 2 * t);                  // smoothstep
          // Only the card on top and the one rising behind it are ever
          // seen. Leaving the settled ones underneath visible stacks ten
          // identical drop shadows into a halo around the whole deck.
          var show = t > 0 && i >= top - 1;
          gsap.set(cards[i], {
            yPercent: (1 - e) * 88,
            rotation: (1 - e) * (i % 2 ? 6 : -6),
            scale: 0.93 + e * 0.07,
            zIndex: i + 1,
            opacity: show ? 1 : 0
          });
        }
      }

      deal(0);

      var st = ScrollTrigger.create({
        trigger: sec,
        start: "top top",
        end: function () { return "+=" + Math.round(window.innerHeight * 1.9); },
        pin: pin,
        scrub: 0.7,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onUpdate: function (self) {
          deal(self.progress);
          // The lettering is pushed along by the scroll on top of its own
          // drift, so the two read as one movement rather than a loop with
          // something sliding over it.
          if (push) gsap.set(push, { xPercent: -14 * self.progress });
        }
      });

      return function () {
        st.kill(true);
        cards.forEach(function (c) { gsap.set(c, { clearProps: "all" }); });
        if (push) gsap.set(push, { clearProps: "all" });
        staticMode();
      };
    });

    mm.add("(max-width: 699px)", function () {
      staticMode();
      return function () {};
    });
  }

  /* ==========================================================
     Day — pinned horizontal timetables
     There are two of these on Student Life now, one per school,
     where there used to be one standing for the whole campus. So
     everything below is scoped to its own section rather than
     looked up on the document: two tracks sharing a selector would
     have left the second one unscrubbed and the first one scrubbed
     twice. Each section gets its own ScrollTrigger; they pin in
     sequence because each is pinned to its own trigger.
     ========================================================== */
  function dayTrack() {
    $$(".dayh").forEach(function (sec) { oneDayTrack(sec); });
  }

  function oneDayTrack(sec) {
    var pin = $(".dayh__pin", sec), track = $(".dayh__track", sec);
    var fill = $(".dayh__fill", sec), tick = $(".dayh__tick", sec);
    if (!track) return;

    function staticMode() { sec.classList.add("is-static"); }

    if (!hasST || !animate || typeof gsap.matchMedia !== "function") { staticMode(); return; }

    // Two pins in a row is twice the scroll to sit through, so a pair of
    // tracks is scrubbed at a shorter distance than the single one was:
    // the whole track still passes, in about two thirds of the scrolling.
    var pace = sec.classList.contains("dayh--duo") ? .6 : 1;

    var mm = gsap.matchMedia();

    mm.add("(min-width: 900px)", function () {
      sec.classList.remove("is-static");
      var moments = $$(".dmoment", track);

      var st = ScrollTrigger.create({
        trigger: sec,
        start: "top top",
        end: function () {
          return "+=" + Math.max((track.scrollWidth - window.innerWidth + 320) * pace, 600);
        },
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
     News flash — the hero's cycling headline reel
     Plain class toggling against CSS transitions, with no GSAP in it:
     the reel is the News page's opening statement, and it should still
     turn on a connection that never reaches the animation CDN. The
     first item is already marked in the markup, so doing nothing here
     leaves one headline standing rather than an empty strip — which is
     exactly what reduced motion, and a single item, both want.
     ========================================================== */
  function newsFlash() {
    var strip = $("#newsFlash");
    if (!strip) return;
    var items = $$(".newsflash__item", strip);
    if (items.length < 2 || reduced) return;

    var i = 0, paused = false;

    function show(n) {
      items[i].classList.remove("is-on");
      i = n;
      items[i].classList.add("is-on");
    }

    window.setInterval(function () {
      // A hidden tab still fires setInterval; cycling through it would land
      // the reader mid-reel on return for no benefit.
      if (paused || document.visibilityState !== "visible") return;
      show((i + 1) % items.length);
    }, 4200);

    // Hold on hover and while a headline has focus, so the link someone is
    // reaching for does not change under the cursor.
    ["mouseenter", "focusin"].forEach(function (e) {
      strip.addEventListener(e, function () { paused = true; });
    });
    ["mouseleave", "focusout"].forEach(function (e) {
      strip.addEventListener(e, function () { paused = false; });
    });
  }

  /* ==========================================================
     Crossroads — where you are in the run
     Thirty-two covers is a long scroll, so the archive keeps a
     count of how far through it you are. It is a readout, not an
     animation: no GSAP, and it stays on under reduced motion,
     because knowing you are at 18 of 32 is information. The panel
     is aria-hidden — every number it shows is already on the card
     beside it — so a screen reader meets the issues, not a ticker.
     ========================================================== */
  function crossroadsProgress() {
    var out = $("#crProgN");
    var cards = $$(".crcard");
    if (!out || !cards.length || typeof window.IntersectionObserver === "undefined") return;

    function updatePosition() {
      var current = 1, line = window.innerHeight * 0.5;
      // Follow the current reading position in both scroll directions rather
      // than retaining only the furthest card the reader has encountered.
      cards.forEach(function (card, index) {
        if (card.getBoundingClientRect().top <= line) current = index + 1;
      });
      out.textContent = current < 10 ? "0" + current : String(current);
    }
    var io = new IntersectionObserver(updatePosition, { rootMargin: "-50% 0px -49% 0px" });

    cards.forEach(function (c) { io.observe(c); });
    window.addEventListener("pageshow", updatePosition);
    window.addEventListener("resize", updatePosition);
  }

  /* ==========================================================
     News track — pinned horizontal reel of highlighted stories
     Same trick as dayTrack() above: pin the section, scrub an inner
     flex row by scroll progress, and fall back to a native swipe track
     under 900px or when motion is off. Kept separate rather than made
     generic because dayTrack's time-of-day fill and tick readout do not
     mean anything for a set of stories — this one drives a plain
     progress rail and a "n of m" count instead.
     ========================================================== */
  function newsTrack() {
    var sec = $("#highlights"), pin = $(".newstrack__pin"), track = $(".newstrack__track");
    var fill = $(".newstrack__fill"), count = $("#newsTrackCount");
    if (!sec || !track) return;

    function staticMode() { sec.classList.add("is-static"); }

    if (!hasST || !animate || typeof gsap.matchMedia !== "function") { staticMode(); return; }

    var mm = gsap.matchMedia();

    mm.add("(min-width: 900px)", function () {
      sec.classList.remove("is-static");
      var cards = $$(".newsitem", track);

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
          if (count) {
            var i = Math.min(cards.length - 1, Math.round(self.progress * (cards.length - 1)));
            var label = (i + 1) + " of " + cards.length;
            if (count.textContent !== label) count.textContent = label;
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
     The run — the home page's horizontal passage
     The section pins at the full height of the window and a
     measured gallery stage is scrubbed across it. Every image and
     text panel owns a separate cell; 3D depth never changes layout
     or allows neighbouring content to collide.

     Parallax is measured against the middle of the window, not
     against how far the stage has travelled. Multiplying the
     whole distance by a depth difference is the obvious way to
     do it and it is wrong: the offsets grow without limit, and
     by the middle of the run the frames had drifted hundreds of
     pixels into each other. Offsetting by how far an item is
     from the centre of the screen keeps every offset inside one
     screen width.
     ========================================================== */
  function homeRun() {
    var sec = $("#run");
    if (!sec) return;
    var pin = $(".hrun__pin", sec), viewport = $(".hrun__viewport", sec), stage = $(".hrun__stage", sec);
    if (!stage) return;

    function clamp01(n) { return n < 0 ? 0 : n > 1 ? 1 : n; }
    function mix(a, b, t) { return Math.round(a + (b - a) * t); }
    function rgb(a, b, t) {
      return "rgb(" + mix(a[0], b[0], t) + "," + mix(a[1], b[1], t) + "," + mix(a[2], b[2], t) + ")";
    }
    function paintTheme(progress) {
      // Hold the gold opening, then make the ivory/gold inversion around the
      // centre of the run. Smoothstep keeps the hand-driven change calm.
      var t = clamp01((progress - .42) / .08);
      t = t * t * (3 - 2 * t);
      pin.style.setProperty("--run-ivory", t.toFixed(3));
      pin.style.setProperty("--run-ink", rgb([28,23,10], [126,88,0], t));
      pin.style.setProperty("--run-soft", rgb([68,55,17], [102,75,8], t));
      pin.style.setProperty("--run-accent", rgb([74,53,0], [152,104,0], t));
      pin.style.setProperty("--run-ghost", rgb([28,23,10], [190,142,18], t));
    }
    function syncStaticTheme() {
      var max = Math.max(viewport.scrollWidth - viewport.clientWidth, 0);
      paintTheme(max ? viewport.scrollLeft / max : 0);
    }
    function staticMode() {
      sec.classList.add("is-static");
      window.requestAnimationFrame(syncStaticTheme);
    }

    // The reduced-motion and phone layouts are native horizontal scrollers;
    // they receive the same colour story from their real swipe position.
    viewport.addEventListener("scroll", syncStaticTheme, { passive:true });
    paintTheme(0);

    if (!hasST || !animate || typeof gsap.matchMedia !== "function") { staticMode(); return; }

    var HOLD = 0.10;
    // Move the measured gallery at half pace so the photographs have
    // enough time to turn through the cylindrical field.
    var PACE = 0.5;
    var PARALLAX = 0.30;

    var mm = gsap.matchMedia();

    mm.add("(min-width: 900px)", function () {
      sec.classList.remove("is-static");

      var layers = $$("[data-depth]", stage).map(function (el) {
        var d = parseFloat(el.getAttribute("data-depth")) || 1;
        var ghost = el.classList.contains("hghost");
        var frame = el.classList.contains("hframe");
        return {
          el: el,
          d: d,
          ghost: ghost,
          frame: frame,
          // An item asking for the middle band is placed at top:50% and
          // has to come back up by half its own height. That cannot live
          // in the stylesheet: the parallax rewrites the whole transform
          // every frame and would drop it.
          mid: getComputedStyle(el).getPropertyValue("--mid").trim() === "1",
          scale: ghost ? 1 : Math.min(Math.max(1 + (d - 1) * 0.5, 0.96), 1.04),
          base: el.offsetLeft + el.offsetWidth / 2
        };
      });

      // How far the stage has to travel: its own width less one screen,
      // taken from layout so no transform can feed back into it.
      // How far the stage must travel: the right edge of the LAST item, not
      // the width of the canvas. The stage is 780vw but the content ends at
      // about 746vw, and measuring the canvas spent that surplus as scroll
      // after the tenth photograph had passed — the frame slid on across an
      // empty gold field and then reappeared parked at the left, which reads
      // as the tenth picture arriving twice before the film section.
      //
      // Ghosts are excluded deliberately: they are decoration, they lag far
      // behind their own depth, and counting them would put the surplus back
      // and then some.
      //
      // offsetLeft and offsetWidth are layout values, so no transform this
      // function's own result drives can feed back into it.
      function reach() {
        var kids = stage.children, far = 0;
        for (var i = 0; i < kids.length; i++) {
          var k = kids[i];
          if (k.classList.contains("hghost")) continue;
          far = Math.max(far, k.offsetLeft + k.offsetWidth);
        }
        return far;
      }

      function place(q, dist) {
        var mid = window.innerWidth / 2;
        var stageX = -dist * q;
        for (var i = 0; i < layers.length; i++) {
          var L = layers[i];
          var from = L.base + stageX - mid;
          var statement = !L.frame && !L.ghost;
          // Bend photographs around a shallow horizontal cylinder. The card
          // nearest the lens faces forward; cards towards either edge turn
          // inward, recede and follow a small vertical arc. Text and ghost
          // layers retain the calmer parallax treatment.
          var arc = Math.min(Math.abs(from) / mid, 1.2);
          var turn = L.frame ? Math.max(-30, Math.min(30, from / mid * -24)) :
            (statement ? Math.max(-18, Math.min(18, from / mid * -15)) : 0);
          var textFocus = statement ? 1 - Math.min(arc, 1) : 0;
          var depth = L.frame ? -Math.pow(arc, 1.35) * 180 : textFocus * 245;
          var curveY = L.frame ? Math.pow(arc, 1.7) * 22 :
            (statement ? textFocus * -24 : 0);
          var arcScale = L.frame ? 1 - Math.min(arc, 1) * .06 :
            (statement ? .91 + textFocus * .19 : 1);
          gsap.set(L.el, {
            x: L.frame ? from * (L.d - 1) * PARALLAX : 0,
            y: curveY,
            yPercent: 0,
            z: depth,
            scale: L.scale * arcScale,
            rotationX: statement ? (1 - textFocus) * 5 : 0,
            rotationY: turn,
            opacity: statement ? .62 + textFocus * .38 : 1,
            force3D: true
          });
        }
      }

      var st = ScrollTrigger.create({
        trigger: sec,
        start: "top top",
        end: function () {
          var run = Math.max((reach() - window.innerWidth + 120) * PACE, 600);
          return "+=" + Math.round(run / (1 - HOLD));
        },
        // Pin the same section that defines the trigger boundary. Pinning the
        // child panel let their cached positions diverge briefly during a
        // refresh or a fast end-of-run handoff, exposing the page ground above
        // the gallery. The inner stage remains the only animated surface.
        pin: sec,
        scrub: .8,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onUpdate: function (self) {
          // The first tenth holds the stage still, so the opening statement
          // gets a screen of its own before anything moves.
          var q = self.progress <= HOLD ? 0 : (self.progress - HOLD) / (1 - HOLD);
          var dist = Math.max(reach() - window.innerWidth + 120, 0);
          gsap.set(stage, { x: -dist * q, force3D: true });
          place(q, dist);
          paintTheme(self.progress);
        }
      });

      place(0, 0);

      return function () {
        st.kill(true);
        gsap.set(stage, { clearProps: "transform" });
        layers.forEach(function (L) { gsap.set(L.el, { clearProps: "transform" }); });
        paintTheme(0);
        staticMode();
      };
    });

    mm.add("(max-width: 899px)", function () {
      staticMode();
      return function () {};
    });
  }

  /* ==========================================================
     Founder — the five words take their highlight in turn
     Knowledge, Character, Culture, Service, Responsibility, set
     large and stacked. A dark plate opens across each one in turn
     as the list is scrolled, and the lettering reverses out of it.

     The slices overlap by half, which is what keeps it continuous:
     a word begins to fill while the one above it is still filling,
     so the sweep never sits still between two words. Scrubbing back
     up empties them again in the same order.
     ========================================================== */
  function founderWords() {
    var list = $(".fwords");
    if (!list || !hasST || !animate) return;
    $$("li", list).forEach(function (row) {
      var wrapper = $(".fwords__w", row);
      if (!wrapper) return;
      gsap.fromTo(wrapper, { "--lit": 0 }, {
        "--lit": 1, ease: "none",
        scrollTrigger: {
          trigger: row, start: "top 65%", end: "top 10%",
          scrub: true, invalidateOnRefresh: true
        }
      });
    });
  }

  /* ==========================================================
     Founder — one restrained, section-local motto entrance.
     The two editorial columns enter once in reading order; there
     is no scrub or decorative motion, and reduced motion remains
     at the fully visible CSS state.
     ========================================================== */
  function founderMottoReveal() {
    var section = $(".fmotto");
    if (!section || !hasST || !animate) return;
    var left = $(".fmotto__left", section);
    var right = $(".fmotto__right", section);
    if (!left || !right) return;
    var tl = gsap.timeline({
      scrollTrigger: { trigger: section, start: "top 78%", once: true }
    });
    tl.from(left, { opacity: 0, y: 22, duration: .82, ease: "power3.out" })
      .from(right, { opacity: 0, y: 18, duration: .78, ease: "power3.out" }, "-=.56");
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
      var homeHeader = document.body.classList.contains("home") && el.closest(".header");
      function magneticIsOn() {
        return !homeHeader || homeHeader.classList.contains("is-stuck");
      }
      var bounds = null;
      var xTo = gsap.quickTo(el, "x", { duration: .34, ease: "power3.out" });
      var yTo = gsap.quickTo(el, "y", { duration: .34, ease: "power3.out" });
      el.addEventListener("pointerenter", function () {
        if (!magneticIsOn()) return;
        bounds = el.getBoundingClientRect();
      });
      el.addEventListener("pointermove", function (e) {
        if (!magneticIsOn()) { xTo(0); yTo(0); return; }
        if (!bounds) bounds = el.getBoundingClientRect();
        xTo((e.clientX - (bounds.left + bounds.width / 2)) * .18);
        yTo((e.clientY - (bounds.top + bounds.height / 2)) * .18);
      });
      el.addEventListener("pointerleave", function () {
        bounds = null;
        gsap.to(el, { x: 0, y: 0, duration: .5, ease: "power3.out", overwrite: "auto" });
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
    var muted = false;

    window.addEventListener("pointermove", function (e) {
      x(e.clientX); y(e.clientY);
      var overHeader = !!(e.target.closest && e.target.closest(".header"));
      if (overHeader !== muted) {
        muted = overHeader;
        if (muted) ring.classList.remove("is-big");
        gsap.to(ring, { opacity: muted ? 0 : 1, duration: .2 });
      } else if (!muted && ring.style.opacity !== "1") {
        gsap.to(ring, { opacity: 1, duration: .3 });
      }
    }, { passive: true });
    document.addEventListener("pointerleave", function () { gsap.to(ring, { opacity: 0, duration: .3 }); });

    var hot = "a, button, .dmoment, .facilities > div, .node, input, [data-magnetic]";
    document.addEventListener("pointerover", function (e) {
      if (e.target.closest && e.target.closest(".header")) return;
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
  var drawer = $("#drawer"), burger = $("#burger"), drawerMotion = null;

  function finishDrawerClose() {
    if (!drawer || drawer.classList.contains("is-open")) return;
    drawer.hidden = true;
    if (animate) {
      gsap.set([drawer].concat($$(".drawer__grid > div, .drawer__utility, .drawer__cta", drawer)), {
        clearProps: "opacity,visibility,transform"
      });
    }
  }

  function closeDrawer() {
    if (!drawer || !drawer.classList.contains("is-open")) return;
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-label", "Open menu");
    burger.focus({ preventScroll: true });
    if (animate && drawerMotion) {
      drawerMotion.eventCallback("onReverseComplete", function () {
        drawer.classList.remove("is-open");
        document.body.classList.remove("is-locked", "menu-open");
        if (lenis) lenis.start();
        finishDrawerClose();
      });
      drawerMotion.reverse();
      return;
    }
    drawer.classList.remove("is-open");
    document.body.classList.remove("is-locked", "menu-open");
    if (lenis) lenis.start();
    window.setTimeout(finishDrawerClose, 420);
  }

  (function chrome() {
    var header = $("#header");
    if (header) {
      var main = $("#main");
      // Ignore non-visual utility nodes (the gallery's canvas controls, for
      // example) and use the first actual section on every page. Blog entries
      // wrap the full story in one article, so their opening ends with the
      // lead image rather than at the end of the story.
      var opening = main && main.querySelector(":scope > section, :scope > article");
      if (!opening && main) opening = main.firstElementChild;
      var openingBoundary = opening;
      if (opening && opening.matches("article.art")) {
        openingBoundary = $(".art__hero", opening) || $(".art__head", opening) || opening;
      }
      sentinel(function () {
        if (!openingBoundary) return 80;
        var box = openingBoundary.getBoundingClientRect();
        return Math.max(box.top + window.pageYOffset + box.height - 1, 80);
      }, function (past) {
        header.classList.toggle("is-first-section", !past);
        // Pale opening sections retain their existing dark lettering while
        // the container itself stays transparent.
        if (!document.body.classList.contains("litehead")) {
          header.classList.toggle("is-stuck", past);
        }
      });
    }

    // The bare header — no glass bar around the controls — belongs to the
    // opening composition and nothing else. Taking the bar off for good
    // looked right on the hero and was wrong two screens down: on Admissions
    // the page's own text scrolled straight through the News pill, and on
    // Why CIRS the wordmark ended up dark purple over an aerial photograph.
    // The bar is what gives it a ground once content passes under it.
    //
    // This runs on bare pages whether or not they are litehead, so a page
    // that opens pale loses the bar over its own opening too, which is the
    // point of the flag.
    if (header && header.classList.contains("is-bare")) {
      header.classList.add("is-atop");
      sentinel(function () {
        var first = $("main > *");
        if (!first) return 80;
        return Math.max(first.offsetTop + first.offsetHeight - 120, 80);
      }, function (past) { header.classList.toggle("is-atop", !past); });
    }
    if (!burger || !drawer) return;
    burger.addEventListener("click", function () {
      if (drawer.classList.contains("is-open")) { closeDrawer(); return; }
      drawer.hidden = false;
      requestAnimationFrame(function () { drawer.classList.add("is-open"); });
      burger.setAttribute("aria-expanded", "true");
      burger.setAttribute("aria-label", "Close menu");
      // is-locked is the scroll lock and nothing more — the intro curtain uses
      // it too. menu-open is what turns the header solid, and only the drawer
      // sets it. See the note on body.menu-open .header in pages.css.
      document.body.classList.add("is-locked", "menu-open");
      if (lenis) lenis.stop();
      if (animate) {
        var pieces = $$(".drawer__grid > div, .drawer__utility, .drawer__cta", drawer);
        if (drawerMotion) drawerMotion.kill();
        drawerMotion = gsap.timeline({ paused:true, defaults:{ ease:"power3.out" } });
        drawerMotion
          .fromTo(drawer,
            { autoAlpha:0, y:-10 },
            { autoAlpha:1, y:0, duration:.42, overwrite:"auto" }, 0)
          .fromTo(pieces,
            { autoAlpha:0, y:16 },
            { autoAlpha:1, y:0, duration:.5, stagger:.045, overwrite:"auto" }, .08)
          .play(0);
      }
    });
    $$("a", drawer).forEach(function (a) { a.addEventListener("click", closeDrawer); });
    document.addEventListener("keydown", function (e) {
      if (!drawer.classList.contains("is-open")) return;
      if (e.key === "Escape") { e.preventDefault(); closeDrawer(); return; }
      if (e.key !== "Tab") return;
      var items = [burger].concat($$("a[href], button", drawer).filter(function (el) {
        return !el.disabled && el.getClientRects().length;
      }));
      var i = items.indexOf(document.activeElement);
      e.preventDefault();
      items[(i + (e.shiftKey ? items.length - 1 : 1)) % items.length].focus();
    });
    document.addEventListener("focusin", function (e) {
      if (drawer.classList.contains("is-open") && e.target !== burger && !drawer.contains(e.target)) {
        burger.focus({ preventScroll: true });
      }
    });
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
    // The hero belongs to the opening timeline, not a scroll reveal. Its
    // prepared lines must remain hidden until that timeline plays.
    var targets = $$(".rv, .img-reveal, .facilities > div, .line-mask > span, .fig-mask > span")
      .filter(function (el) { return !el.closest(".hero, .hseq"); });
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
    var panel = $(".lightbox__panel", box);
    // Focus guards also catch Tab leaving the cross-origin player's document.
    var before = document.createElement("span"), after = document.createElement("span");
    [before, after].forEach(function (guard) { guard.tabIndex = 0; guard.className = "sr-only"; });
    panel.prepend(before); panel.append(after);
    before.addEventListener("focus", function () { $(".lightbox__close", box).focus(); });
    after.addEventListener("focus", function () { var player = $("iframe", frame); if (player) player.focus(); });

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
      box.showModal();
      document.body.classList.add("has-lightbox");
      if (lenis) lenis.stop();
      var close = $(".lightbox__close", box);
      if (close) close.focus();
    }

    function close() {
      if (box.hidden) return;
      box.close();
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

    // Use native modal cancellation for browser close requests.
    box.addEventListener("cancel", function (e) { e.preventDefault(); close(); });
    box.addEventListener("click", function (e) {
      if (e.target.closest("[data-close]")) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !box.hidden) close();
      // Native Tab enters the iframe; the guards wrap at either boundary.
      // The native modal keeps background content inert until it closes.
    });
  }


  /* ==========================================================
     Glimpses collage
     The cross-fade itself is CSS: every tile holds two frames
     and swings between them for ever. This only changes what
     the frames ARE — and only ever the layer that is currently
     invisible, so a photograph is never seen to be replaced.
     ========================================================== */
  function glimpses() {
    var sec = $("#glimpses");
    if (!sec || reduced) return;
    var tiles = $$(".gt", sec);
    if (tiles.length < 2) return;

    // The pool is whatever the markup already references, so it cannot drift
    // out of step with what is on disk.
    var pool = [];
    $$("img", sec).forEach(function (im) {
      var src = im.getAttribute("src");
      if (src && pool.indexOf(src) === -1) pool.push(src);
    });
    if (pool.length < 3) return;

    var timer = null;
    var toneTimer = null;
    var inView = false;

    function retire() {
      var t = tiles[(Math.random() * tiles.length) | 0];
      if (!t) return;
      var a = $(".gt__a", t), b = $(".gt__b", t);
      if (!a || !b) return;

      // Whichever layer is fully out of sight can be changed for nothing.
      var o = parseFloat(window.getComputedStyle(b).opacity);
      var target = o < 0.04 ? b : (o > 0.96 ? a : null);
      if (!target) return;

      var other = target === b ? a : b;
      var next = pool[(Math.random() * pool.length) | 0];
      if (next === target.getAttribute("src") || next === other.getAttribute("src")) return;
      target.setAttribute("src", next);
    }

    function run(on) {
      if (on && !timer) timer = window.setInterval(retire, 1200);
      if (on && !toneTimer) {
        toneTimer = window.setInterval(function () {
          sec.classList.toggle("is-tone-flipped");
        }, 4000);
      }
      if (!on && timer) { window.clearInterval(timer); timer = null; }
      if (!on && toneTimer) { window.clearInterval(toneTimer); toneTimer = null; }
    }

    // Off screen it is invisible work, and a hidden tab would still be
    // fetching photographs.
    if (typeof window.IntersectionObserver !== "undefined") {
      new IntersectionObserver(function (entries) {
        inView = entries[0].isIntersecting;
        run(inView && document.visibilityState !== "hidden");
      }, { rootMargin: "200px" }).observe(sec);
      document.addEventListener("visibilitychange", function () {
        run(inView && document.visibilityState !== "hidden");
      });
    } else {
      run(true);
    }
  }


  /* ==========================================================
     Crossroads hero: the wall of covers behind the masthead
     ========================================================== */
  function crossroadsWall() {
    var wall = $(".crwall");
    if (!wall || reduced) return;
    var runs = $$(".crwall__run", wall);
    if (!runs.length) return;

    // The CSS keyframe is what has been running until now. Taking the
    // transform over by hand is what buys the turn: animation-direction
    // flips to the mirror of the current position, which is a jump, and
    // a jump is the one thing a drift cannot do.
    var cols = runs.map(function (run, i) {
      run.style.animation = "none";
      return { el: run, sign: +(run.getAttribute("data-dir") || 1), pos: 0, span: 0, seed: (i * 0.37) % 1 };
    });

    function measure() {
      cols.forEach(function (c) {
        // Half the run, because the run is written out twice: travel that
        // far and the second copy is exactly where the first began.
        var span = c.el.scrollHeight / 2;
        if (span > 0 && span !== c.span) {
          c.pos = c.span ? c.pos * (span / c.span) : span * c.seed;
          c.span = span;
        }
      });
    }
    measure();

    var SPEED = 15;          // px per second: a drift, not a carousel
    var dir = 1, want = 1;   // where the scroll last went, and where we are
    var lastY = window.scrollY || 0;
    var raf = null, last = 0;

    onScroll(function () {
      var y = window.scrollY || 0;
      var d = y - lastY;
      if (Math.abs(d) > 0.5) want = d > 0 ? 1 : -1;
      lastY = y;
    });

    function frame(now) {
      var dt = last ? Math.min((now - last) / 1000, 0.05) : 0.016;
      last = now;

      // Eased rather than switched: the columns slow, stop and come back
      // the other way, which is the turn the reader actually sees.
      dir += (want - dir) * Math.min(dt * 1.7, 1);

      cols.forEach(function (c) {
        if (!c.span) return;
        c.pos += SPEED * c.sign * dir * dt;
        c.pos = ((c.pos % c.span) + c.span) % c.span;
        c.el.style.transform = "translate3d(0," + (-c.pos).toFixed(2) + "px,0)";
      });
      raf = window.requestAnimationFrame(frame);
    }

    function run(on) {
      if (on && raf === null) { last = 0; raf = window.requestAnimationFrame(frame); }
      if (!on && raf !== null) { window.cancelAnimationFrame(raf); raf = null; }
    }

    // Scrolled past, or in a hidden tab, it is work nobody can see.
    if (typeof window.IntersectionObserver !== "undefined") {
      new IntersectionObserver(function (entries) {
        run(entries[0].isIntersecting && document.visibilityState !== "hidden");
      }, { rootMargin: "100px" }).observe(wall);
      document.addEventListener("visibilitychange", function () {
        run(document.visibilityState !== "hidden" &&
            wall.getBoundingClientRect().bottom > 0);
      });
    } else {
      run(true);
    }

    // The covers arrive after first paint, so the run keeps growing.
    window.addEventListener("resize", measure);
    $$("img", wall).forEach(function (im) {
      if (!im.complete) im.addEventListener("load", measure, { once: true });
    });
  }


  /* ==========================================================
     School History timeline
     Activation is an IntersectionObserver, not a ScrollTrigger,
     so the milestones light up even when GSAP never arrives from
     its CDN. The spine's fill rides the site's own onScroll
     helper, which uses ScrollTrigger when it is there and the
     native event when it is not.
     ========================================================== */
  function historyTimeline() {
    var sec = $("#timeline");
    if (!sec) return;
    var items = $$(".tl__item", sec), fill = $("#tlFill");

    // No script, reduced motion, or nothing to observe: show it all at once.
    if (!items.length || reduced || typeof window.IntersectionObserver === "undefined") {
      sec.classList.add("is-static");
      if (fill) fill.style.height = "100%";
      return;
    }

    // A milestone activates once it is properly on screen and stays active —
    // a history that un-tells itself as you scroll back would be worse than
    // one that does not animate at all.
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-on"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -18% 0px", threshold: 0.28 });
    items.forEach(function (el) { io.observe(el); });

    if (!fill) return;

    // The line fills from where the first milestone sits to where the last one
    // does, so it is full exactly as the last year is reached rather than when
    // the section's padding ends.
    function draw() {
      var first = items[0].getBoundingClientRect();
      var last = items[items.length - 1].getBoundingClientRect();
      var mid = window.innerHeight * 0.62;
      var span = (last.top + last.height / 2) - (first.top + first.height / 2);
      if (span <= 0) { fill.style.height = "100%"; return; }
      var p = (mid - (first.top + first.height / 2)) / span;
      p = p < 0 ? 0 : (p > 1 ? 1 : p);
      fill.style.height = (p * 100).toFixed(2) + "%";
    }
    draw();
    onScroll(draw);
    window.addEventListener("resize", draw, { passive: true });
  }

  /* ==========================================================
     Boot
     ========================================================== */
  function start() {
    backToTop();
    enquirePanel();
    filmLightbox();
    glimpses();
    historyTimeline();
    newsFlash();
    crossroadsProgress();
    crossroadsWall();
    if (!animate) {
      // heroSeq belongs here too. Under reduced motion the stylesheet's own
      // media query has already flattened the sequence, but when GSAP simply
      // fails to load that query does not fire, and the sheet would otherwise
      // leave a full-bleed plate stuck for 160vh with nothing scrubbing it.
      // Called here, it puts is-static on and the opening is one still panel.
      failOpen(); slHero(); homeRun(); dayTrack(); newsTrack(); chart(); progressBar();
      heroSeq();
      // No curtain and no pinning here, but the photographs still arrive late
      // and move everything below them, so an inbound anchor still needs
      // putting right once they have.
      window.addEventListener("load", openHash);
      return;
    }

    document.documentElement.classList.add("js-motion");
    choreograph();
    slHero();
    homeRun();
    founderWords();
    founderMottoReveal();
    dayTrack();
    newsTrack();
    heroSeq();
    groundShift();
    progressBar();
    magnets();
    chart();
    cursorRing();
    ticker();
    mottoDrift();

    // A completed intro belongs to the tab, not to one document instance.
    // Remove a freshly parsed curtain before heroIn() can prepare hidden lines,
    // so refresh and non-bfcached Back navigation cannot flash and replay it.
    if (!claimIntroVisit()) {
      var repeatedCurtain = $("#curtain");
      if (repeatedCurtain) repeatedCurtain.remove();
      document.body.classList.remove("is-locked");
    }

    // Set the hero's initial state before the curtain starts uncovering it,
    // then play the prepared timeline without hiding visible content again.
    var heroEntrance = heroIn();
    playIntro(function () { if (heroEntrance) heroEntrance.play(); });
    startSweep();

    // Late-loading images change every trigger position below them.
    window.addEventListener("load", function () {
      if (hasST) ScrollTrigger.refresh();
      // Covers the pages that have no curtain to lift, and the case where the
      // photographs land after it already has.
      openHash();
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
