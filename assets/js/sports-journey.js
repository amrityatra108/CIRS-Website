/**
 * CIRS SPORTS & LAURELS — BUILT IN THE ARENA
 * assets/js/sports-journey.js
 * Interactive cursor, photographic reveal mask, scroll transitions,
 * and house band choreography.
 */

(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);

  /* ------------------------------------------------------------
     1. HERO CURSOR & PHOTOGRAPHIC REVEAL (DESKTOP)
     ------------------------------------------------------------ */
  const hero = document.querySelector('.arena-hero');
  const heroReveal = document.getElementById('heroRevealLayer');
  const cursor = document.getElementById('sportsCursor');
  const heroImgs = document.querySelectorAll('.arena-hero__img');

  if (hero && !isTouch && !prefersReducedMotion) {
    let heroRect = hero.getBoundingClientRect();
    let mouseX = heroRect.width / 2;
    let mouseY = heroRect.height / 2;
    let targetX = mouseX;
    let targetY = mouseY;
    let isHovering = false;

    window.addEventListener('resize', () => {
      heroRect = hero.getBoundingClientRect();
    });

    hero.addEventListener('mouseenter', () => {
      isHovering = true;
      if (cursor) cursor.classList.add('is-active');
      if (heroReveal) heroReveal.style.opacity = '1';
    });

    hero.addEventListener('mouseleave', () => {
      isHovering = false;
      if (cursor) cursor.classList.remove('is-active');
      if (heroReveal) {
        heroReveal.style.opacity = '0';
        heroReveal.style.clipPath = 'circle(0px at 50% 50%)';
      }
      heroImgs.forEach(img => {
        img.style.transform = 'scale(1.04) translate(0px, 0px)';
      });
    });

    hero.addEventListener('mousemove', (e) => {
      heroRect = hero.getBoundingClientRect();
      targetX = e.clientX - heroRect.left;
      targetY = e.clientY - heroRect.top;

      if (cursor) {
        cursor.style.transform = `translate3d(${e.clientX}px, ${e.clientY}px, 0)`;
      }
    });

    // Smooth animation loop for reveal circle and subtle parallax
    function renderHero() {
      if (isHovering) {
        mouseX += (targetX - mouseX) * 0.18;
        mouseY += (targetY - mouseY) * 0.18;

        if (heroReveal) {
          heroReveal.style.clipPath = `circle(140px at ${Math.round(mouseX)}px ${Math.round(mouseY)}px)`;
        }

        // Very light parallax on base image (understated, max 10px)
        const relX = (mouseX / heroRect.width - 0.5) * -16;
        const relY = (mouseY / heroRect.height - 0.5) * -16;
        heroImgs.forEach(img => {
          img.style.transform = `scale(1.05) translate3d(${relX.toFixed(1)}px, ${relY.toFixed(1)}px, 0)`;
        });
      }
      requestAnimationFrame(renderHero);
    }
    requestAnimationFrame(renderHero);
  }

  /* ------------------------------------------------------------
     2. THE FIVE O’CLOCK SHIFT (SCROLL-DRIVEN TRANSITION)
     ------------------------------------------------------------ */
  const shiftSec = document.getElementById('shift');
  const shiftAcademic = document.getElementById('shiftMediaAcademic');
  const shiftSports = document.getElementById('shiftMediaSports');
  const shiftProgress = document.getElementById('shiftTimelineProgress');
  const shiftSteps = document.querySelectorAll('.shift-step');

  if (shiftSec) {
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined' && !prefersReducedMotion) {
      gsap.registerPlugin(ScrollTrigger);

      ScrollTrigger.create({
        trigger: shiftSec,
        start: 'top 70%',
        end: 'bottom 30%',
        scrub: true,
        onUpdate: (self) => {
          const p = self.progress;

          // Cross-fade academic into sports
          if (shiftAcademic) shiftAcademic.style.opacity = Math.max(0, 1 - p * 1.2).toFixed(2);
          if (shiftSports) shiftSports.style.opacity = Math.min(1, 0.15 + p * 0.85).toFixed(2);

          // Update progress bar
          if (shiftProgress) shiftProgress.style.width = `${Math.max(20, p * 100)}%`;

          // Activate step indicators
          shiftSteps.forEach((step, idx) => {
            const threshold = idx / (shiftSteps.length - 1);
            if (p >= threshold - 0.15) {
              step.classList.add('is-active');
            } else if (idx > 0) {
              step.classList.remove('is-active');
            }
          });
        }
      });
    } else {
      // Fallback intersection observer
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            if (shiftSports) shiftSports.style.opacity = '0.7';
            if (shiftProgress) shiftProgress.style.width = '100%';
            shiftSteps.forEach(s => s.classList.add('is-active'));
          }
        });
      }, { threshold: 0.3 });
      observer.observe(shiftSec);
    }
  }

  /* ------------------------------------------------------------
     3. HOUSE COMPETITION BANDS INTERACTION
     ------------------------------------------------------------ */
  const houseBands = document.querySelectorAll('.house-band');

  if (houseBands.length) {
    function activateHouse(band) {
      houseBands.forEach(b => {
        const isActive = (b === band);
        b.classList.toggle('is-active', isActive);
        b.setAttribute('aria-expanded', isActive ? 'true' : 'false');
        const btn = b.querySelector('.house-band__trigger');
        if (btn) btn.setAttribute('aria-expanded', isActive ? 'true' : 'false');
      });
    }

    houseBands.forEach(band => {
      const trigger = band.querySelector('.house-band__trigger');

      band.addEventListener('mouseenter', () => {
        if (!isTouch && window.innerWidth > 900) {
          activateHouse(band);
        }
      });

      band.addEventListener('focusin', () => {
        activateHouse(band);
      });

      if (trigger) {
        trigger.addEventListener('click', (e) => {
          e.preventDefault();
          activateHouse(band);
        });
      }
    });
  }

  /* ------------------------------------------------------------
     4. HERO SMOOTH SCROLL ANCHOR NAVIGATION
     ------------------------------------------------------------ */
  const enterBtn = document.getElementById('enterArenaBtn');
  if (enterBtn) {
    enterBtn.addEventListener('click', (e) => {
      const target = document.querySelector(enterBtn.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth' });
      }
    });
  }

})();

(function () {
  "use strict";

  var root = document.documentElement;
  var move = document.querySelector("[data-sports-move]");
  var chapters = document.querySelector("[data-sports-chapters]");
  if (!move || !chapters) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var gsap = window.gsap;
  var ScrollTrigger = window.ScrollTrigger;
  if (!gsap || !ScrollTrigger) return;

  var moveTrigger = null;
  var moveVisualTrigger = null;
  var chapterTrigger = null;
  var wave = move.querySelector("[data-move-wave]");
  var scenes = Array.prototype.slice.call(chapters.querySelectorAll(".sports-chapter"));
  var markers = Array.prototype.slice.call(chapters.querySelectorAll("[data-chapter-point]"));
  var links = Array.prototype.slice.call(chapters.querySelectorAll("[data-chapter-link]"));
  var chapterNav = chapters.querySelector(".sports-chapters__nav");
  var currentLink = null;

  function clamp(value) {
    return Math.max(0, Math.min(1, value));
  }

  function smooth(value) {
    var t = clamp(value);
    return t * t * (3 - 2 * t);
  }

  function setMove(progress) {
    var p = clamp(progress);
    var reveal = smooth((p - 0.012) / 0.31);
    var edge = 1 - reveal;
    var amplitude = (window.innerWidth <= 720 ? 0.055 : 0.04) * Math.sin(Math.PI * reveal);

    if (wave) {
      wave.setAttribute(
        "d",
        "M " + edge.toFixed(4) + " 0 C " +
          (edge + amplitude).toFixed(4) + " .26 " +
          (edge - amplitude).toFixed(4) + " .74 " +
          edge.toFixed(4) + " 1 L 1 1 L 1 0 Z"
      );
    }

    var enter = smooth((p - 0.30) / 0.13);
    var resolve = smooth((p - 0.71) / 0.20);
    var mobile = window.innerWidth <= 720;
    var scale = (0.66 + 0.34 * enter) * (1 - resolve) + (mobile ? 0.16 : 0.14) * resolve;
    var x = -window.innerWidth * (mobile ? 0.30 : 0.34) * resolve;
    var y = -window.innerHeight * 0.35 * resolve;
    var actionX = -window.innerWidth * (mobile ? 0.018 : 0.025) * reveal;
    var actionScale = 1.035 - 0.035 * reveal;
    var finish = smooth((p - 0.61) / 0.20);

    move.style.setProperty("--move-scale", scale.toFixed(4));
    move.style.setProperty("--move-x", x.toFixed(1) + "px");
    move.style.setProperty("--move-y", y.toFixed(1) + "px");
    move.style.setProperty("--action-x", actionX.toFixed(1) + "px");
    move.style.setProperty("--action-scale", actionScale.toFixed(4));
    move.style.setProperty("--move-opacity", enter.toFixed(4));
    move.style.setProperty("--finish-opacity", finish.toFixed(4));
    move.style.setProperty("--move-resolution", smooth((p - 0.79) / 0.14).toFixed(4));
  }

  function chapterCenter(index) {
    var last = scenes.length - 1;
    if (index <= 0 || last <= 1) return 0.04;
    return 0.14 + ((index - 1) / (last - 1)) * 0.72;
  }

  function setChapterProgress(progress) {
    var p = clamp(progress);
    var revealWidth = window.innerWidth <= 720 ? 0.14 : 0.12;
    var reveals = scenes.map(function (_scene, index) {
      if (index === 0) return 1;
      var center = chapterCenter(index);
      return smooth((p - (center - revealWidth / 2)) / revealWidth);
    });

    scenes.forEach(function (scene, index) {
      var reveal = reveals[index];
      scene.style.setProperty("--chapter-reveal", reveal.toFixed(4));
      scene.style.setProperty("--chapter-right", ((1 - reveal) * 100).toFixed(2) + "%");
      scene.style.setProperty("--chapter-left", ((1 - reveal) * 100).toFixed(2) + "%");
      scene.style.setProperty("--chapter-top", ((1 - reveal) * 100).toFixed(2) + "%");

      var next = reveals[index + 1] || 0;
      var caption = scene.querySelector(".sports-chapter__caption");
      if (caption) caption.style.setProperty("--chapter-caption", (reveal * (1 - next)).toFixed(3));
    });

    var current = 0;
    for (var i = 1; i < reveals.length; i += 1) {
      if (reveals[i] >= 0.5) current = i;
    }
    var activeName = scenes[current].getAttribute("data-chapter");
    var activeLink = null;
    links.forEach(function (link) {
      if (link.getAttribute("data-chapter-link") === activeName) {
        link.setAttribute("aria-current", "step");
        activeLink = link;
      } else {
        link.removeAttribute("aria-current");
      }
    });
    if (activeLink && activeLink !== currentLink && chapterNav && chapterNav.scrollWidth > chapterNav.clientWidth + 1) {
      /* Keep the chapter control in its sticky viewport. scrollIntoView can
         pull the page all the way to the nav when the first scene activates
         on a narrow screen; adjust only the nav's horizontal scroll instead. */
      var centered = activeLink.offsetLeft - (chapterNav.clientWidth - activeLink.offsetWidth) / 2;
      chapterNav.scrollLeft = Math.max(0, Math.min(chapterNav.scrollWidth - chapterNav.clientWidth, centered));
    }
    currentLink = activeLink;
  }

  function placeMarkers() {
    if (!root.classList.contains("sports-journey-ready")) return;
    var travel = Math.max(0, chapters.offsetHeight - window.innerHeight);
    var anchorOffset = 88;
    markers.forEach(function (marker, index) {
      var progress = index === 0 ? 0.04 : chapterCenter(index);
      marker.style.top = Math.round(travel * progress + anchorOffset) + "px";
    });
  }

  function setMoveVisibility(active) {
    if (active) move.setAttribute("data-move-active", "");
    else move.removeAttribute("data-move-active");
  }

  function clearStyles() {
    ["--move-scale", "--move-x", "--move-y", "--action-x", "--action-scale", "--move-opacity",
      "--finish-opacity", "--move-resolution"].forEach(function (name) {
      move.style.removeProperty(name);
    });
    scenes.forEach(function (scene) {
      ["--chapter-reveal", "--chapter-right", "--chapter-left", "--chapter-top"].forEach(function (name) {
        scene.style.removeProperty(name);
      });
      var caption = scene.querySelector(".sports-chapter__caption");
      if (caption) caption.style.removeProperty("--chapter-caption");
    });
    markers.forEach(function (marker) { marker.style.removeProperty("top"); });
    links.forEach(function (link) { link.removeAttribute("aria-current"); });
    currentLink = null;
  }

  function teardown() {
    if (moveTrigger) { moveTrigger.kill(); moveTrigger = null; }
    if (moveVisualTrigger) { moveVisualTrigger.kill(); moveVisualTrigger = null; }
    if (chapterTrigger) { chapterTrigger.kill(); chapterTrigger = null; }
    root.classList.remove("sports-journey-ready");
    setMoveVisibility(false);
    clearStyles();
  }

  function setup() {
    if (reduce.matches || moveTrigger || !window.gsap || !window.ScrollTrigger) return;
    root.classList.add("sports-journey-ready");
    placeMarkers();

    moveVisualTrigger = ScrollTrigger.create({
      trigger: move,
      start: "top top",
      end: "bottom top",
      onToggle: function (self) { setMoveVisibility(self.isActive); },
      onRefresh: function (self) { setMoveVisibility(self.isActive); }
    });

    moveTrigger = ScrollTrigger.create({
      trigger: move,
      start: "top top",
      end: "bottom bottom",
      onUpdate: function (self) { setMove(self.progress); },
      onRefresh: function (self) { setMove(self.progress); }
    });

    chapterTrigger = ScrollTrigger.create({
      trigger: chapters,
      start: "top top",
      end: "bottom bottom",
      onUpdate: function (self) { setChapterProgress(self.progress); },
      onRefresh: function (self) {
        placeMarkers();
        setChapterProgress(self.progress);
      }
    });
    ScrollTrigger.refresh();
  }

  setup();

  reduce.addEventListener("change", function () {
    if (reduce.matches) teardown();
    else setup();
  });
  window.addEventListener("resize", function () {
    placeMarkers();
    if (ScrollTrigger) ScrollTrigger.refresh();
  }, { passive: true });
  window.addEventListener("pagehide", teardown);
  window.addEventListener("pageshow", function (event) {
    if (event.persisted) setup();
  });
}());