/* Creative Writing — the hero's dust, and the pointer parallax.

   No dependency and no framework. Everything this file adds is decoration on
   top of a hero that is already complete without it: the page renders, reads
   and links correctly with JavaScript off, and this only lifts the dust and
   lets the desk lean towards the pointer.

   It does nothing at all under prefers-reduced-motion, and nothing on a
   touch screen, where there is no pointer to lean towards and the listeners
   would only cost battery. Both are watched rather than read once, so a
   person who turns reduced motion on gets a still page without reloading. */
(function () {
  "use strict";

  var hero = document.querySelector(".cw-hero");
  if (!hero) return;                        // not this page

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var coarse = window.matchMedia("(hover: none), (pointer: coarse)");

  /* ---------- the drifting dust ---------- */
  var host = document.getElementById("cwParticles");

  function buildParticles() {
    if (!host) return;
    host.innerHTML = "";
    if (reduce.matches) return;
    var count = window.innerWidth < 760 ? 14 : 30;
    var frag = document.createDocumentFragment();
    for (var i = 0; i < count; i++) {
      var p = document.createElement("span");
      var size = 1.5 + Math.random() * 3.5;
      p.className = "cw-particle";
      p.style.width = size + "px";
      p.style.height = size + "px";
      p.style.left = (Math.random() * 100).toFixed(2) + "%";
      p.style.top = (12 + Math.random() * 84).toFixed(2) + "%";
      p.style.setProperty("--cw-dx", (Math.random() * 40 - 20).toFixed(1) + "px");
      p.style.setProperty("--cw-o", (0.18 + Math.random() * 0.42).toFixed(2));
      p.style.animationDuration = (10 + Math.random() * 12).toFixed(1) + "s";
      p.style.animationDelay = (-Math.random() * 20).toFixed(1) + "s";
      // A few of them are paper-white rather than gold, so the field is dust
      // and not a string of identical lights.
      if (Math.random() > 0.72) {
        p.style.background =
          "radial-gradient(circle, #FBF5EB 0%, rgba(251,245,235,0) 70%)";
      }
      frag.appendChild(p);
    }
    host.appendChild(frag);
  }
  buildParticles();

  /* ---------- the pointer parallax ----------
     Two custom properties on the hero, which the planes read; the easing is
     done here rather than in a transition so that a fast pointer does not
     drag the whole stack across the hero. */
  var tx = 0, ty = 0, cx = 0, cy = 0, raf = null, active = false;

  function tick() {
    cx += (tx - cx) * 0.07;
    cy += (ty - cy) * 0.07;
    hero.style.setProperty("--cw-px", cx.toFixed(4));
    hero.style.setProperty("--cw-py", cy.toFixed(4));
    if (Math.abs(tx - cx) > 0.001 || Math.abs(ty - cy) > 0.001) {
      raf = window.requestAnimationFrame(tick);
    } else {
      raf = null;
    }
  }

  function onMove(e) {
    var r = hero.getBoundingClientRect();
    tx = ((e.clientX - r.left) / r.width - 0.5) * 2;
    ty = ((e.clientY - r.top) / r.height - 0.5) * 2;
    if (!raf) raf = window.requestAnimationFrame(tick);
  }

  function onLeave() {
    tx = 0;
    ty = 0;
    if (!raf) raf = window.requestAnimationFrame(tick);
  }

  function setParallax(on) {
    if (on === active) return;
    active = on;
    if (on) {
      hero.addEventListener("pointermove", onMove, { passive: true });
      hero.addEventListener("pointerleave", onLeave, { passive: true });
    } else {
      hero.removeEventListener("pointermove", onMove);
      hero.removeEventListener("pointerleave", onLeave);
      onLeave();
    }
  }

  function sync() { setParallax(!reduce.matches && !coarse.matches); }
  sync();

  if (reduce.addEventListener) {
    reduce.addEventListener("change", function () { sync(); buildParticles(); });
  }
  if (coarse.addEventListener) {
    coarse.addEventListener("change", sync);
  }

  var rz;
  window.addEventListener("resize", function () {
    window.clearTimeout(rz);
    rz = window.setTimeout(buildParticles, 260);
  }, { passive: true });
})();
