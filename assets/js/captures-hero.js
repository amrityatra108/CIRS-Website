/* CIRS Captures — "Through our eyes".

   The field of photographs between the featured compositions and the
   journal (tools/pages/captures.html; the cards are HERO in
   tools/captures.py, laid out by assets/css/captures-hero.css).

   Everything that moves here is drawn by one function on the shared GSAP
   ticker, which is also what drives Lenis and ScrollTrigger, so the field,
   the smooth scroll and the scroll positions are always read on the same
   frame. The function runs only while the section is on screen. GSAP
   tweens here move numbers, never the cards themselves; each frame the
   function puts together what the entrance, the idle breathing, the
   pointer, a drag, a hover, an opened photograph and the exit each ask of
   every card, and writes one transform for it. That is what lets the
   entrance hand over to the idle scene without a seam: the entrance's
   easing is still arriving when the breathing and the pointer begin, each
   faded in from nothing.

   The entrance, once the section is reached and its photographs and title
   face are ready (times in seconds; a phone runs them at 0.85):

     0.00  the dark ground and its grain, which are already there
     0.15  the camera starts forward from further back and a little low
     0.25  back photographs start to materialise, then the middle (0.40)
           and the front (0.55), each out of its own depth
     0.70  "Through" rises through its mask, "our eyes." from 0.85
     1.25  the gold rule draws in
     1.45  the place and the ways on
     1.90  the scene begins to breathe; the pointer takes hold by 2.65

   The site's header is the shared one (assets/js/cirs.js) and is left
   alone. With reduced motion there is no camera, no depth movement and no
   drag: the photographs are simply faded up, already in place. */
(function () {
  "use strict";

  var section = document.querySelector("[data-toe]");
  if (!section) return;
  window.__toeBooted = true;

  var root = document.documentElement;
  var stage = section.querySelector("[data-toe-stage]");
  var worlds = Array.prototype.slice.call(section.querySelectorAll("[data-toe-world]"));
  var head = section.querySelector(".toe__head");
  var lines = Array.prototype.slice.call(section.querySelectorAll("[data-toe-line]"));
  var accent = section.querySelector("[data-toe-accent]");
  var footBox = section.querySelector(".toe__foot");
  var foot = Array.prototype.slice.call(section.querySelectorAll("[data-toe-foot]"));
  var shade = section.querySelector("[data-toe-shade]");
  var viewer = document.querySelector("[data-cv]");

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var narrowQuery = window.matchMedia("(max-width: 720px)");
  var hasGsap = typeof window.gsap !== "undefined" && typeof window.ScrollTrigger !== "undefined";
  var motion = hasGsap && !reduced.matches && root.classList.contains("toe-motion") &&
               !!(window.CSS && CSS.supports && CSS.supports("transform-style", "preserve-3d"));

  var cards = Array.prototype.slice.call(section.querySelectorAll("[data-toe-card]")).map(function (el, i) {
    return {
      el: el,
      i: i,
      img: el.querySelector("img"),
      fogEl: el.querySelector(".toe__fog"),
      meta: el.querySelector(".toe__meta"),
      metaIn: el.querySelector(".toe__meta-in"),
      layer: el.getAttribute("data-toe-layer"),
      index: +el.getAttribute("data-toe-index")
    };
  });

  // A card opens the viewer on its photograph, flying out of the field when
  // there is motion. A click with a modifier is left alone, so the
  // photograph can still be opened in a tab of its own; without the viewer
  // the link simply goes to the full-size image.
  function canView(e) {
    return viewer && typeof viewer.showModal === "function" &&
           e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey;
  }
  function view(card, from) {
    document.dispatchEvent(new CustomEvent("captures:view", { detail: {
      index: card.index,
      opener: card.el,
      from: from || null,
      src: card.img.currentSrc || card.img.src
    } }));
  }

  // Load the field's photographs once the section is anywhere near, and
  // decode them, so that none arrives after its card has started to appear.
  var decoded = null;
  function prefetch() {
    if (decoded) return decoded;
    decoded = Promise.all(cards.map(function (c) {
      c.img.loading = "eager";
      if (!c.img.decode) return Promise.resolve();
      return c.img.decode().catch(function () {});
    }));
    return decoded;
  }
  if ("IntersectionObserver" in window) {
    var near = new IntersectionObserver(function (entries) {
      if (entries.some(function (e) { return e.isIntersecting; })) { prefetch(); near.disconnect(); }
    }, { rootMargin: "300% 0px" });
    near.observe(section);
  } else {
    prefetch();
  }

  if (!motion) {
    still();
    return;
  }


  /* ------------------------------------------------------------------
     Without motion: the written composition, faded up once
     ------------------------------------------------------------------ */
  function still() {
    root.classList.remove("toe-motion");
    cards.forEach(function (c) {
      c.el.addEventListener("click", function (e) {
        if (!canView(e)) return;
        e.preventDefault();
        view(c, null);
      });
    });
    // The page's floating buttons keep off the foot while the field fills
    // the window, as they do while it is held with motion.
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        document.body.classList.toggle("toe-on", entries[0].intersectionRatio > .75);
      }, { threshold: [0, .75, 1] }).observe(section);
    }
    if (!hasGsap) return;
    // Gentle opacity only, photographs already in place.
    gsap.set(cards.map(function (c) { return c.el; }), { opacity: 0 });
    gsap.set(head, { opacity: 0 });
    ScrollTrigger.create({
      trigger: section,
      start: "top 70%",
      once: true,
      onEnter: function () {
        gsap.to(head, { opacity: 1, duration: .9, ease: "power1.out" });
        gsap.to(cards.map(function (c) { return c.el; }),
                { opacity: 1, duration: .8, ease: "power1.out", stagger: .04, clearProps: "opacity" });
      }
    });
  }


  /* ------------------------------------------------------------------
     With motion
     ------------------------------------------------------------------ */

  var W = 0, H = 0, P = 0, narrow = false;
  var visible = [];

  function num(style, name) { return parseFloat(style.getPropertyValue(name)) || 0; }

  // The layout in use for each card, read back from the sheet so the two
  // can never disagree; and the stage's size. Once, and on resize.
  function measure() {
    W = stage.clientWidth;
    H = stage.clientHeight;
    P = parseFloat(getComputedStyle(stage).perspective) || Math.max(W, H) * .95;
    narrow = narrowQuery.matches;
    visible = [];
    cards.forEach(function (c) {
      var s = getComputedStyle(c.el);
      c.shown = s.display !== "none";
      if (!c.shown) return;
      c.sx = num(s, "--x");
      c.sy = num(s, "--y");
      c.z = num(s, "--cz");
      c.rx = num(s, "--crx");
      c.ry = num(s, "--cry");
      c.rz = num(s, "--crz");
      c.last = null;
      visible.push(c);
    });
  }

  // What each card starts from and how it breathes. The two front cards
  // nearest the title's outer edges rise further, so they pass the title as
  // it is revealed.
  var LAYERS = {
    back:  { fog: .5,  s0: .8,  dz: .16, dy: 34, amp: 1.6, start: .25 },
    mid:   { fog: .26, s0: .85, dz: .13, dy: 40, amp: 2.6, start: .40 },
    front: { fog: .08, s0: .9,  dz: .11, dy: 46, amp: 3.8, start: .55 }
  };
  cards.forEach(function (c, i) {
    var L = LAYERS[c.layer] || LAYERS.mid;
    c.L = L;
    c.p = 0;            // how far the entrance has brought it, eased
    c.o = 0;            // its opacity in the entrance
    c.h = 0;            // hover, 0..1
    c.fog = L.fog;
    // Breathing: an irregular pair of slow cycles, 8 to 14 seconds.
    var seed = Math.sin((i + 1) * 12.9898) * 43758.5453;
    seed -= Math.floor(seed);
    c.w1 = 2 * Math.PI / (8 + 6 * seed);
    c.w2 = 2 * Math.PI / (9.5 + 4.5 * ((seed * 7.31) % 1));
    c.ph1 = seed * 6.283;
    c.ph2 = seed * 3.7;
  });

  var cam = { z: -.36, y: .045 };        // the entrance's camera offset, in P and H
  var idle = { v: 0 }, lean = { v: 0 };  // breathing and pointer, faded in
  var pointer = { tx: 0, ty: 0, x: 0, y: 0 };
  var drag = { down: null, on: false, tY: 0, tX: 0, rY: 0, rX: 0, vY: 0, vX: 0, released: -1 };
  var focus = { v: 0, card: null };
  var hovered = null;
  var exit = 0;
  var entered = false, running = false, active = false;
  var lastT = 0;

  var fixed = function (v) { return Math.round(v * 100) / 100; };
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function ease(dt, tau) { return 1 - Math.exp(-dt / tau); }

  function frame(time) {
    var dt = lastT ? Math.min(time - lastT, .05) : 1 / 60;
    lastT = time;
    var step60 = dt * 60;

    // The pointer, heavily smoothed: 4% of the way each frame at 60fps.
    var a = 1 - Math.pow(.96, step60);
    pointer.x += (pointer.tx - pointer.x) * a;
    pointer.y += (pointer.ty - pointer.y) * a;

    // The drag: after release a little of its speed is kept and decays;
    // after a pause the field drifts back to where it was written.
    var maxY = narrow ? 9 : 14, maxX = narrow ? 0 : 6;
    if (!drag.on) {
      if (Math.abs(drag.vY) > .002 || Math.abs(drag.vX) > .002) {
        drag.tY = clamp(drag.tY + drag.vY * step60, -maxY, maxY);
        drag.tX = clamp(drag.tX + drag.vX * step60, -maxX, maxX);
        var decay = Math.pow(.935, step60);
        drag.vY *= decay;
        drag.vX *= decay;
      } else {
        drag.vY = drag.vX = 0;
      }
      if (drag.released >= 0 && time - drag.released > 2.5) {
        var home = ease(dt, 2.4);
        drag.tY -= drag.tY * home;
        drag.tX -= drag.tX * home;
      }
    }
    var follow = ease(dt, .22);
    drag.rY += (drag.tY - drag.rY) * follow;
    drag.rX += (drag.tX - drag.rX) * follow;

    // The camera.
    var lw = lean.v * (1 - focus.v), iw = idle.v;
    // Go into the field first; release it to the journal only afterwards.
    // Both phases follow the scroll, so reversing retraces the same camera.
    var inward = clamp(exit / .75, 0, 1);
    var e = inward * inward * (3 - 2 * inward);
    var leave = clamp((exit - .75) / .25, 0, 1);
    leave = leave * leave * (3 - 2 * leave);
    var camX = pointer.x * .026 * W * lw;
    var camY = pointer.y * .018 * H * lw + cam.y * H + iw * .0035 * H * Math.sin(time * .57);
    var camZ = cam.z * P + e * (narrow ? .38 : .52) * P;
    var turnY = drag.rY + pointer.x * 2.2 * lw;
    var turnX = drag.rX - pointer.y * 1.3 * lw;
    var world = "translate3d(" + fixed(-camX) + "px," + fixed(-camY) + "px," + fixed(camZ) + "px) rotateX(" +
                fixed(turnX) + "deg) rotateY(" + fixed(turnY) + "deg)";
    for (var w = 0; w < worlds.length; w++) {
      if (worlds[w].__t !== world) { worlds[w].style.transform = world; worlds[w].__t = world; }
    }

    // Each card.
    var spread = 1;
    var any = hovered && !drag.on && !focus.card;
    for (var i = 0; i < visible.length; i++) {
      var c = visible[i], L = c.L;
      var k = 1 - c.z, q = 1 - c.p;
      var isFocus = focus.card === c;
      var ff = isFocus ? focus.v : 0;

      var hTarget = (any && hovered === c) || isFocus ? 1 : 0;
      c.h += (hTarget - c.h) * ease(dt, .15);

      var fogTarget = focus.card ? (isFocus ? 0 : Math.max(L.fog, .5 + .28 * focus.v))
                    : any ? (hovered === c ? 0 : Math.max(L.fog, .55))
                    : L.fog;
      c.fog += (fogTarget - c.fog) * ease(dt, .16);

      var bY = iw * L.amp * Math.sin(time * c.w1 + c.ph1);
      var bX = iw * L.amp * .5 * Math.sin(time * c.w2 + c.ph2);
      var rise = (c.passer ? 2.1 : 1) * L.dy;
      var X = c.sx * W * k * spread + bX * k;
      var Y = c.sy * H * k * spread + (bY + q * rise) * k;
      var Z = c.z * P - q * L.dz * P + c.h * .05 * P + ff * .1 * P;
      var side = c.sx < 0 ? -1 : 1;
      var rx = c.rx * (1 - ff) + q * 4;
      var ry = c.ry * (1 - ff) - q * 6 * side;
      var rz = c.rz * (1 - ff);
      var s = (L.s0 + (1 - L.s0) * c.p) * (1 + .05 * c.h);

      var t = "translate3d(" + fixed(X) + "px," + fixed(Y) + "px," + fixed(Z) + "px) rotateX(" + fixed(rx) +
              "deg) rotateY(" + fixed(ry) + "deg) rotateZ(" + fixed(rz) + "deg) scale(" + s.toFixed(4) + ")";
      if (t !== c.last) { c.el.style.transform = t; c.last = t; }
      var o = (c.o * (1 - leave * .25)).toFixed(3);
      if (o !== c.lastO) { c.el.style.opacity = o; c.lastO = o; }
      var f = (c.fog * (1 - e * .85)).toFixed(3);
      if (f !== c.lastF) { c.fogEl.style.opacity = f; c.lastF = f; }
      var m = (isFocus ? 0 : c.h).toFixed(3);
      if (m !== c.lastM) {
        c.meta.style.opacity = m;
        c.metaIn.style.transform = "translate3d(0," + ((1 - m) * 105).toFixed(1) + "%,0)";
        c.lastM = m;
      }
    }

    // The title quietens while a photograph is open, and fades on the way out.
    var ho = ((1 - .45 * focus.v) * (1 - leave)).toFixed(3);
    if (ho !== head.__o) {
      head.style.opacity = ho;
      head.__o = ho;
    }
    var ht = e ? "scale(" + (1 + e * .35).toFixed(3) + ")" : "";
    if (ht !== head.__t) { head.style.transform = ht; head.__t = ht; }
    var fo = ((1 - .7 * focus.v) * (1 - Math.min(1, e * 2.2))).toFixed(3);
    if (fo !== footBox.__o) { footBox.style.opacity = fo; footBox.__o = fo; }
    var so = (leave * .12).toFixed(3);
    if (so !== shade.__o) { shade.style.opacity = so; shade.__o = so; }
  }

  function setActive(on) {
    if (on === active) return;
    active = on;
    if (on) { lastT = 0; gsap.ticker.add(frame); }
    else gsap.ticker.remove(frame);
  }

  function holdOn(on) { document.body.classList.toggle("toe-on", on); }


  /* ---- The entrance ---------------------------------------------------- */

  function ready() {
    var fonts = document.fonts && document.fonts.load
      ? document.fonts.load('400 1em "Bodoni Moda"').catch(function () {})
      : Promise.resolve();
    // A slow photograph is not waited for long: after four seconds the
    // field goes with what it has.
    return Promise.race([
      Promise.all([prefetch(), fonts]),
      new Promise(function (r) { window.setTimeout(r, 4000); })
    ]);
  }

  // The camera's ease: a long deceleration like expo.out's, but leaving rest
  // at no speed at all. expo.out starts at seven times its average speed,
  // which was a visible lurch in the first frame of the camera's travel.
  // This one starts from nothing, is at its fastest a quarter of the way in,
  // and is still settling by a pixel or two when the breathing takes over.
  function glide(t) { var u = 1 - t, u2 = u * u; return 1 - u2 * u2 * (1 + 4 * t); }

  var timeline = null;
  function build() {
    var D = narrow ? .85 : 1;
    var tl = gsap.timeline({ paused: true, onComplete: settled });
    tl.to(cam, { z: 0, y: 0, duration: 2.3 * D, ease: glide }, .15 * D);

    ["back", "mid", "front"].forEach(function (layer) {
      var set = visible.filter(function (c) { return c.layer === layer; });
      set.forEach(function (c, n) {
        var at = (c.L.start + n * .085) * D;
        var dur = (c.passer ? 1.75 : 1.55) * D;
        tl.to(c, { p: 1, duration: dur, ease: "power3.out" }, at);
        tl.to(c, { o: 1, duration: 1.1 * D, ease: "power2.out" }, at);
      });
    });

    lines.forEach(function (line, n) {
      tl.to(line, { y: 0, clipPath: "inset(-12% -8% -30% -8%)", duration: 1.15 * D, ease: "power4.out" },
            (.70 + n * .15) * D);
    });
    tl.to(accent, { scaleX: 1, duration: .7 * D, ease: "power3.inOut" }, 1.25 * D);
    tl.to(foot, { opacity: 1, y: 0, duration: .8 * D, ease: "power3.out", stagger: .1 }, 1.45 * D);
    tl.to(idle, { v: 1, duration: 1.6, ease: "sine.inOut" }, 1.9 * D);
    tl.to(lean, { v: 1, duration: .65, ease: "power1.inOut" }, 2.0 * D);
    return tl;
  }

  // The masks come off once the lettering is whole, so nothing is left
  // clipping it.
  function settled() {
    lines.forEach(function (line) { line.style.clipPath = "none"; });
  }

  function arm(immediate) {
    if (entered) return;
    entered = true;
    ready().then(function () {
      if (!timeline) timeline = build();
      if (immediate) { timeline.progress(1); settled(); }
      else timeline.play();
    });
  }


  /* ---- Pointer, drag, hover -------------------------------------------- */

  var suppressClick = false;

  stage.addEventListener("pointermove", function (e) {
    if (e.pointerType === "mouse" && !drag.on) {
      pointer.tx = clamp((e.clientX / W) * 2 - 1, -1, 1);
      pointer.ty = clamp((e.clientY / H) * 2 - 1, -1, 1);
    }
    var d = drag.down;
    if (!d || d.id !== e.pointerId) return;
    var dx = e.clientX - d.lx, dy = e.clientY - d.ly;
    if (!drag.on) {
      var ox = e.clientX - d.x, oy = e.clientY - d.y;
      if (ox * ox + oy * oy < 36) return;
      // A touch that is mostly vertical is the page being scrolled.
      if (e.pointerType !== "mouse" && Math.abs(oy) > Math.abs(ox)) { drag.down = null; return; }
      drag.on = true;
      hovered = null;
      section.classList.add("is-dragging");
      try { stage.setPointerCapture(e.pointerId); } catch (err) {}
    }
    // Heavy: the drag moves a target, and the field follows it.
    var kY = .15, kX = e.pointerType === "mouse" ? .08 : 0;
    var maxY = narrow ? 9 : 14, maxX = narrow ? 0 : 6;
    drag.tY = clamp(drag.tY + dx * kY, -maxY, maxY);
    drag.tX = clamp(drag.tX - dy * kX, -maxX, maxX);
    drag.vY = drag.vY * .5 + dx * kY * .5;
    drag.vX = drag.vX * .5 - dy * kX * .5;
    d.lx = e.clientX;
    d.ly = e.clientY;
  });

  stage.addEventListener("pointerdown", function (e) {
    if (e.button !== 0 || !e.isPrimary || focus.card) return;
    drag.down = { id: e.pointerId, x: e.clientX, y: e.clientY, lx: e.clientX, ly: e.clientY };
    drag.vY = drag.vX = 0;
  });

  function release(e) {
    if (!drag.down || drag.down.id !== e.pointerId) return;
    drag.down = null;
    if (!drag.on) return;
    drag.on = false;
    drag.released = lastT;
    // Only a little of the throw is kept.
    drag.vY *= .35;
    drag.vX *= .35;
    section.classList.remove("is-dragging");
    suppressClick = true;
    window.setTimeout(function () { suppressClick = false; }, 0);
  }
  stage.addEventListener("pointerup", release);
  stage.addEventListener("pointercancel", release);
  stage.addEventListener("click", function (e) {
    if (suppressClick) { e.preventDefault(); e.stopPropagation(); suppressClick = false; }
  }, true);

  stage.addEventListener("pointerleave", function (e) {
    if (e.pointerType !== "mouse") return;
    pointer.tx = pointer.ty = 0;
    hovered = null;
  });

  cards.forEach(function (c) {
    c.el.addEventListener("pointerenter", function (e) {
      if (e.pointerType === "mouse") hovered = c;
    });
    c.el.addEventListener("pointerleave", function () {
      if (hovered === c) hovered = null;
    });
    c.el.addEventListener("focus", function () {
      if (c.el.matches(":focus-visible")) hovered = c;
    });
    c.el.addEventListener("blur", function () {
      if (hovered === c) hovered = null;
    });
    c.el.addEventListener("click", function (e) {
      if (!canView(e)) return;
      e.preventDefault();
      if (focus.card) return;
      open(c);
    });
  });


  /* ---- A photograph out of the field ------------------------------------
     The card comes forward and turns square to the reader while the rest of
     the field dims and the title quietens; then the viewer takes the
     photograph from exactly where the card is and carries it to its frame
     (the flight itself is in assets/js/captures-gallery.js). */

  function open(c) {
    focus.card = c;
    hovered = null;
    gsap.to(focus, {
      v: 1, duration: .42, ease: "power2.inOut", overwrite: true,
      onComplete: function () {
        var r = c.img.getBoundingClientRect();
        view(c, { left: r.left, top: r.top, width: r.width, height: r.height });
        // The photograph is now the viewer's.
        c.el.style.visibility = "hidden";
      }
    });
  }

  if (viewer) {
    viewer.addEventListener("close", function () {
      var c = focus.card;
      if (!c) return;
      c.el.style.visibility = "";
      c.o = 0;
      c.lastO = null;
      gsap.to(c, { o: 1, duration: .6, ease: "power2.out" });
      gsap.to(focus, { v: 0, duration: .8, ease: "power2.out", overwrite: true,
                       onComplete: function () { focus.card = null; } });
    });
  }


  /* ---- Setting up --------------------------------------------------------- */

  section.classList.add("is-live");
  measure();
  // The fronts nearest the title's outer edges are the two that pass it.
  var fronts = visible.filter(function (c) { return c.layer === "front"; })
    .sort(function (a, b) { return Math.abs(a.sy) - Math.abs(b.sy); });
  fronts.slice(0, 2).forEach(function (c) { c.passer = true; });

  // The entrance's first frame, written by the script before anything can
  // be seen; the sheet has already hidden the same things.
  gsap.set(lines, { y: 50, clipPath: "inset(125% -8% -30% -8%)" });
  gsap.set(accent, { scaleX: 0, transformOrigin: "left center" });
  gsap.set(foot, { opacity: 0, y: 10 });
  frame(0);

  /* Where the reader is, read from the section itself on every scroll
     update rather than from a ScrollTrigger's cached start and end: this
     site's html has scroll-behavior:smooth, which ScrollTrigger's refresh
     does not survive (see where() in assets/js/filmintro.js), and here it
     measured this section as starting at the top of the page. The trigger,
     with no element, is only the signal that the page has moved; it is fed
     by Lenis on the same ticker frame, before the field is drawn, so the
     rectangle is read before anything is written. */
  var held = null;
  function sense() {
    var box = section.getBoundingClientRect();
    var vh = window.innerHeight;
    var stageH = stage.offsetHeight || vh;
    var travel = box.height - stageH;
    // On screen at all: the field is drawn.
    setActive(box.top < vh && box.bottom > 0);
    // Held: the exit follows the scroll.
    exit = travel > 0 ? clamp(-box.top / travel, 0, 1) : 0;
    var on = box.top <= .5 && box.bottom > 0;
    if (on !== held) { held = on; holdOn(on); }
    // Reached: the entrance.
    if (!entered && box.top < vh * .45 && box.bottom > 0) arm(false);
  }

  // A page that opens already past the field (a reload further down, a
  // link to the journal) finds it finished.
  if (section.getBoundingClientRect().bottom < 0) arm(true);
  ScrollTrigger.create({ onUpdate: sense, onRefresh: sense });
  window.addEventListener("scroll", sense, { passive: true });
  sense();

  var resizeTimer = 0;
  window.addEventListener("resize", function () {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(function () {
      var wasNarrow = narrow;
      measure();
      if (narrow !== wasNarrow && timeline && timeline.progress() < 1) timeline.progress(1);
      if (narrow !== wasNarrow && entered) visible.forEach(function (c) { c.p = 1; c.o = 1; });
    }, 120);
  });
})();
