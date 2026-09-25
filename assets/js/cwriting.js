<<<<<<< HEAD
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
=======
/* Creative Writing: a quiet chapter entrance and an optional reading mode.
   All poetry and navigation are present in the HTML before this file runs. */
(function () {
  "use strict";

  var page = document.body;
  if (!page.classList.contains("cwriting")) return;

  /* The shared smooth-scroll handler prevents native fragment navigation.
     Keep chapter and poem URLs shareable when a reader follows an in-page link. */
  var main = document.getElementById("main");
  var activatingClone = false;
  if (main) {
    document.addEventListener("click", function (event) {
      if (!(event.target instanceof Element)) return;
      var link = event.target.closest('a[href^="#"]');
      if (!link) return;
      var hash = link.getAttribute("href");
      if (!main.contains(link) && !(hash === "#main" && link.classList.contains("skip-link"))) return;
      var target = hash && hash.length > 1 ? document.getElementById(hash.slice(1)) : null;
      if (!target) return;
      if (window.location.hash !== hash) window.history.pushState(null, "", hash);
      if (event.detail === 0 && !activatingClone) {
        var heading = target.querySelector("h1, h2, h3");
        if (heading) {
          heading.setAttribute("tabindex", "-1");
          window.setTimeout(function () { heading.focus({ preventScroll: true }); }, 0);
        }
      }
    }, true);

    /* Repeated cards keep the loop seamless. Their original preview link is
       the sole accessible link, while a pointer can open any visible repeat. */
    main.addEventListener("click", function (event) {
      if (!(event.target instanceof Element)) return;
      var clone = event.target.closest(".cw-row__card[data-cw-target]");
      if (!clone || !main.contains(clone)) return;
      var hash = clone.getAttribute("data-cw-target");
      var original = Array.prototype.find.call(
        main.querySelectorAll("a.cw-row__card[href]"),
        function (link) { return link.getAttribute("href") === hash; }
      );
      if (!original) return;
      activatingClone = true;
      try { original.click(); }
      finally { activatingClone = false; }
    });
  }

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var running = [];
  var pauseButton = document.querySelector(".cw-rows__pause");

  function syncPauseButton() {
    if (!pauseButton) return;
    if (reduce.matches) {
      pauseButton.disabled = true;
      pauseButton.setAttribute("aria-pressed", "true");
      pauseButton.textContent = "Motion off";
      return;
    }
    var paused = page.classList.contains("cw-motion-paused");
    pauseButton.disabled = false;
    pauseButton.setAttribute("aria-pressed", String(paused));
    pauseButton.textContent = paused ? "Resume motion" : "Pause motion";
  }

  if (pauseButton) {
    pauseButton.addEventListener("click", function () {
      page.classList.toggle("cw-motion-paused");
      syncPauseButton();
    });
    syncPauseButton();
  }

  if (main) {
    main.addEventListener("focusin", function (event) {
      if (!(event.target instanceof Element)) return;
      var card = event.target.closest(".cw-row__card[href]");
      if (!card) return;
      var row = card.closest(".cw-row");
      var scroller = row && row.querySelector(".cw-row__window");
      if (!scroller) return;
      window.requestAnimationFrame(function () {
        var frame = scroller.getBoundingClientRect();
        var bounds = card.getBoundingClientRect();
        if (bounds.left < frame.left + 20) scroller.scrollLeft += bounds.left - frame.left - 20;
        else if (bounds.right > frame.right - 20) scroller.scrollLeft += bounds.right - frame.right + 20;
      });
    });
    main.addEventListener("focusout", function (event) {
      if (!(event.target instanceof Element)) return;
      var row = event.target.closest(".cw-row");
      if (!row) return;
      window.setTimeout(function () {
        if (!row.contains(document.activeElement)) {
          var scroller = row.querySelector(".cw-row__window");
          if (scroller && !reduce.matches && !page.classList.contains("cw-motion-paused")) {
            scroller.scrollLeft = 0;
          }
        }
      }, 0);
    });
  }

  if ("IntersectionObserver" in window && !reduce.matches) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        if (reduce.matches || !entry.target.animate) return;
        var animation = entry.target.animate(
          [
            { opacity: 0.7, transform: "translateY(16px)" },
            { opacity: 1, transform: "translateY(0)" }
          ],
          {
            duration: entry.target.classList.contains("cw-interlude") ? 800 : 620,
            easing: "cubic-bezier(.2,.75,.3,1)"
          }
        );
        running.push(animation);
        animation.addEventListener("finish", function () {
          var index = running.indexOf(animation);
          if (index !== -1) running.splice(index, 1);
        }, { once: true });
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.04 });

    document.querySelectorAll(".cw-chapter__head, .cw-interlude").forEach(function (element) {
      observer.observe(element);
    });
  }

  function cancelMotion() {
    if (!reduce.matches) return;
    running.forEach(function (animation) { animation.cancel(); });
    running.length = 0;
  }
  if (reduce.addEventListener) {
    reduce.addEventListener("change", function () {
      cancelMotion();
      syncPauseButton();
    });
  }

  var controls = [];
  function setQuietReading(quiet) {
    page.classList.toggle("cw-quiet", quiet);
    controls.forEach(function (button) {
      button.setAttribute("aria-pressed", String(quiet));
      button.textContent = quiet ? "Show chapter design" : "Quiet reading";
    });
  }

  document.querySelectorAll(".cw-chapter__head").forEach(function (header) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "cw-reader-toggle";
    button.setAttribute("aria-pressed", "false");
    button.textContent = "Quiet reading";
    button.addEventListener("click", function () {
      setQuietReading(!page.classList.contains("cw-quiet"));
    });
    header.appendChild(button);
    controls.push(button);
  });
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
})();
