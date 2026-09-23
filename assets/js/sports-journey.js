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
