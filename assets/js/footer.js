(function () {
  "use strict";

  var scene = document.querySelector("[data-closing-scene]");
  var root = document.documentElement;
  var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (scene && !reducedMotion && "IntersectionObserver" in window) {
    root.classList.add("has-footer-scene-motion");
    var reveal = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          scene.classList.add("is-visible");
          reveal.unobserve(scene);
        }
      });
    }, { threshold: 0.18, rootMargin: "0px 0px -6% 0px" });
    reveal.observe(scene);
  }
  if (scene) {
    scene.addEventListener("focusin", function () {
      scene.classList.add("is-visible");
    });
  }

  /* The header, the page index and back-to-top give way to the closing
     scene — but only once it is the thing on screen. They used to go the
     moment the scene's first pixel came up at the foot of the window, which
     on a short page or an article is while the reader is still several
     paragraphs from the end, with nothing left to navigate by.

     So they now go when the scene fills three quarters of the window: its
     top edge has risen to the upper quarter, or to the bottom of the bar if
     that is lower down. By then what is left of the page is a line or two
     under the header, and the scene is plainly what is being looked at. It
     is a quarter rather than the bar itself because on many pages the
     scene never reaches the bar — the footer below it is shorter than the
     window, so the page stops scrolling first — and the chrome would stay
     over the scene to the very end. On a page without a scene (Captures,
     Leadership) the page's end is <main>'s lower edge, over the footer, and
     the same line applies. So does a scene a page has put away: News keeps
     the shared scene in its markup at no height at all, and that is not a
     scene to give way to.

     Some pages stop scrolling before their edge reaches that line at all:
     where the footer under the edge is shorter than three quarters of the
     window (News, Captures and Leadership on a desktop, whose 430px footer
     leaves the edge at 470px in a 900px window), the edge's highest point
     is short of the upper quarter. There the chrome goes as the page
     arrives at its end, which is the most of the footer the reader will
     ever see. The line is whichever of the two comes first.

     It is read from the geometry, once a frame and only while that edge is
     on screen, with a band so the chrome does not flicker for a scroll that
     comes to rest on the line. */
  var main = document.querySelector("main");
  var sceneEdge = !!(scene && scene.offsetHeight);
  var edgeEl = sceneEdge ? scene : main;
  if (edgeEl && "IntersectionObserver" in window) {
    var BAND = 24;
    var header = document.querySelector("#header");
    var bar = (header && header.querySelector(".wrap")) || header;
    var line = 0, near = false, active = null, queued = false;
    var measure = function () {
      // Offsets rather than the bar's box: a header collapsed past the
      // opening has slid up out of the window, and its box with it.
      var barBottom = bar ? header.offsetTop + (bar === header ? 0 : bar.offsetTop) + bar.offsetHeight : 0;
      line = Math.max(barBottom, window.innerHeight * .25);
    };
    var update = function () {
      queued = false;
      var r = edgeEl.getBoundingClientRect();
      var top = sceneEdge ? r.top : r.bottom;
      // Where the edge will stand once the page can scroll no further.
      var rest = document.documentElement.scrollHeight - window.innerHeight -
        (window.scrollY || window.pageYOffset || 0);
      var target = Math.max(line, top - Math.max(rest, 0) + 2);
      var next = active ? top <= target + BAND : top <= target;
      if (next === active) return;
      active = next;
      root.classList.toggle("footer-zone-active", next);
    };
    var queue = function () {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(update);
    };
    // The edge on screen, or anywhere above it, is when the geometry is worth
    // reading; below the window the answer is simply "not yet".
    new IntersectionObserver(function (entries) {
      near = entries[entries.length - 1].isIntersecting;
      queue();
    }).observe(edgeEl);
    window.addEventListener("scroll", function () { if (near) queue(); }, { passive: true });
    window.addEventListener("resize", function () { measure(); queue(); }, { passive: true });
    measure();
    update();
  }

  if (!scene || reducedMotion || !window.matchMedia ||
      !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

  var frame = 0;
  var shiftX = 0;
  var shiftY = 0;

  scene.addEventListener("pointermove", function (event) {
    if (event.pointerType === "touch") return;
    var bounds = scene.getBoundingClientRect();
    shiftX = ((event.clientX - bounds.left) / bounds.width - 0.5) * -14;
    shiftY = ((event.clientY - bounds.top) / bounds.height - 0.5) * -8;
    if (frame) return;
    frame = window.requestAnimationFrame(function () {
      scene.style.setProperty("--scene-shift-x", shiftX.toFixed(1) + "px");
      scene.style.setProperty("--scene-shift-y", shiftY.toFixed(1) + "px");
      frame = 0;
    });
  }, { passive: true });

  scene.addEventListener("pointerleave", function () {
    scene.style.setProperty("--scene-shift-x", "0px");
    scene.style.setProperty("--scene-shift-y", "0px");
  }, { passive: true });
})();
