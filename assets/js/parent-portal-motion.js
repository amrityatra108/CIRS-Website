/* Parent Portal: a one-time photographic entrance and light, unpinned parallax. */
(function () {
  "use strict";

  function boot() {
    window.__cirsPortalMotionBooted = true;
    window.clearTimeout(window.__cirsPortalMotionFallback);

    var root = document.documentElement;
    var intro = document.querySelector(".portal-intro");
    var gsap = window.gsap;
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (!intro || !gsap || reduce.matches) {
      root.classList.remove("portal-motion-pending");
      return;
    }

    var photo = intro.querySelector(".portal-intro__photo");
    var picture = intro.querySelector(".portal-intro__picture");
    var image = intro.querySelector(".portal-intro__image");
    var line = intro.querySelector(".portal-intro__line");
    var words = intro.querySelectorAll(".portal-intro__title-word > span");
    var note = intro.querySelector(".portal-intro__note");
    var entry = intro.querySelector(".portal-intro__entry");
    var border = intro.querySelector(".portal-intro__entry-border rect");
    var arrow = intro.querySelector(".portal-intro__entry-arrow");
    var scrollTween = null;

    // The wrapper has 24px of overscan on each edge. Moving it down makes the
    // photograph travel upward a little more slowly than the page on scroll.
    if (window.ScrollTrigger) {
      gsap.registerPlugin(window.ScrollTrigger);
      scrollTween = gsap.to(picture, {
        y: function () { return window.innerWidth <= 700 ? 12 : 20; },
        ease: "none",
        scrollTrigger: {
          trigger: intro,
          start: "top top",
          end: "bottom top",
          scrub: true,
          invalidateOnRefresh: true
        }
      });
    }

    var pending = root.classList.contains("portal-motion-pending");
    if (!pending || window.scrollY > 8) {
      root.classList.remove("portal-motion-pending");
      return;
    }

    var mobile = window.matchMedia("(max-width: 700px)").matches;
    var settled = false;
    var lineDone = false;
    var photoReady = image.complete && image.naturalWidth > 0;
    var lineTween = null;
    var timeline = null;
    var waitTimeout = window.setTimeout(skip, 6500);

    function removeSkipListeners() {
      window.removeEventListener("scroll", skipOnScroll);
      window.removeEventListener("keydown", skipOnKey);
      window.removeEventListener("wheel", skip);
      window.removeEventListener("touchmove", skip);
      entry.removeEventListener("pointerdown", skip);
      entry.removeEventListener("focus", skip);
    }

    function settle() {
      if (settled) return;
      settled = true;
      window.clearTimeout(waitTimeout);
      removeSkipListeners();
      root.classList.remove("portal-motion-pending");
      gsap.set(photo, { clearProps: "clipPath" });
      gsap.set(image, { clearProps: "transform" });
      gsap.set(words, { clearProps: "transform" });
      gsap.set([note, entry], { clearProps: "transform,opacity,visibility" });
      gsap.set(border, { clearProps: "strokeDashoffset" });
      gsap.set(line, { clearProps: "transform,opacity" });
      gsap.set(arrow, { clearProps: "transform" });
    }

    function skip() {
      if (settled) return;
      if (lineTween) lineTween.kill();
      if (timeline) timeline.kill();
      settle();
    }

    function skipOnScroll() {
      if (window.scrollY > 8) skip();
    }

    function skipOnKey(event) {
      if (["Tab", "ArrowDown", "ArrowUp", "PageDown", "PageUp", "Home", "End", " "].indexOf(event.key) !== -1) skip();
    }

    function startPhotograph() {
      if (!lineDone || !photoReady || settled || timeline) return;
      if (window.scrollY > 8) { skip(); return; }

      // Desktop: 0.7s line + 4.8s sequence = 5.5s. Mobile: about 2.1s.
      timeline = gsap.timeline({ onComplete: settle });
      timeline.fromTo(photo,
        { clipPath: "inset(50% 0% 50% 0%)" },
        { clipPath: "inset(0% 0% 0% 0%)", duration: mobile ? 0.68 : 1.75, ease: "power3.inOut" }, 0);
      timeline.fromTo(image,
        { scale: mobile ? 1.04 : 1.08, y: mobile ? 5 : 10 },
        { scale: 1, y: 0, duration: mobile ? 0.92 : 2.25, ease: "power2.out" }, 0);
      timeline.to(line, { opacity: 0, duration: mobile ? 0.2 : 0.42, ease: "power1.out" }, mobile ? 0.08 : 0.18);
      timeline.to(words[0],
        { y: 0, duration: mobile ? 0.42 : 0.85, ease: "power3.out" }, mobile ? 0.60 : 1.90);
      timeline.to(words[1],
        { y: 0, duration: mobile ? 0.42 : 0.85, ease: "power3.out" }, mobile ? 0.72 : 2.05);
      timeline.fromTo([note, entry], { y: 16, autoAlpha: 0 },
        { y: 0, autoAlpha: 1, duration: mobile ? 0.38 : 0.70, ease: "power2.out" }, mobile ? 1.08 : 2.95);
      timeline.fromTo(border, { strokeDashoffset: 1 },
        { strokeDashoffset: 0, duration: mobile ? 0.42 : 1.15, ease: "power1.inOut" }, mobile ? 1.22 : 3.33);
      timeline.fromTo(arrow, { x: -5 },
        { x: 0, duration: mobile ? 0.15 : 0.28, ease: "power2.out" }, mobile ? 1.67 : 4.52);
    }

    window.addEventListener("scroll", skipOnScroll, { passive: true });
    window.addEventListener("keydown", skipOnKey);
    window.addEventListener("wheel", skip, { passive: true });
    window.addEventListener("touchmove", skip, { passive: true });
    entry.addEventListener("pointerdown", skip);
    entry.addEventListener("focus", skip);

    if (!photoReady) {
      image.addEventListener("load", function () { photoReady = true; startPhotograph(); }, { once: true });
      image.addEventListener("error", skip, { once: true });
    }

    lineTween = gsap.fromTo(line, { scaleX: 0, opacity: 1 }, {
      scaleX: 1,
      duration: mobile ? 0.25 : 0.70,
      ease: "power2.out",
      onComplete: function () { lineDone = true; startPhotograph(); }
    });

    function motionPreferenceChanged() {
      if (!reduce.matches) return;
      skip();
      if (scrollTween) {
        scrollTween.kill();
        gsap.set(picture, { clearProps: "transform" });
      }
    }
    if (reduce.addEventListener) reduce.addEventListener("change", motionPreferenceChanged);
    else reduce.addListener(motionPreferenceChanged);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
})();
