(function () {
  "use strict";

  var intro = document.getElementById("portal-intro");
  var image = document.getElementById("portalIntroImage");
  var entry = document.getElementById("portalIntroEntry");
  var target = document.getElementById("top");
  if (!intro || !image || !entry || !target) return;

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var originalRestoration = window.__portalOriginalRestoration || history.scrollRestoration;
  var originalScrollBehavior = document.documentElement.style.scrollBehavior;
  var revealed = false;
  var entered = false;
  var revealTimer;

  function scrollLock(locked) {
    document.body.classList.toggle("portal-intro-active", locked);
    document.documentElement.style.scrollBehavior = locked ? "auto" : originalScrollBehavior;
    history.scrollRestoration = locked ? "manual" : originalRestoration;
    window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: locked } }));
  }

  // Scroll restoration can run after load/pageshow. Keep the opening at the
  // viewport top until the visitor explicitly uses the entry control.
  function keepIntroAtTop() {
    if (!entered && document.body.classList.contains("portal-intro-active") && window.scrollY !== 0) {
      window.scrollTo(0, 0);
    }
  }

  function reveal() {
    if (revealed || entered) return;
    revealed = true;
    intro.classList.add("is-revealed");
  }

  // The title rises once the photograph is ready behind it — or at once if
  // it fails, since the text does not depend on it.
  function imageReady() {
    if (revealed || entered || revealTimer) return;
    revealTimer = setTimeout(reveal, reduced ? 0 : 220);
  }

  function enter(event) {
    if (!revealed || entered) return;
    entered = true;
    scrollLock(false);
    if (event.detail === 0) {
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
    }
    requestAnimationFrame(function () {
      var move = new CustomEvent("cirs-section-scroll", {
        cancelable: true,
        detail: { top: target, duration: 0.9 }
      });
      window.dispatchEvent(move);
      if (!move.defaultPrevented) {
        target.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
      }
    });
  }

  entry.addEventListener("click", enter);
  if (image.complete) imageReady();
  else {
    image.addEventListener("load", imageReady);
    image.addEventListener("error", imageReady);
  }

  scrollLock(true);
  window.scrollTo(0, 0);
  window.addEventListener("scroll", keepIntroAtTop, { passive: true });
  window.addEventListener("load", function () {
    keepIntroAtTop();
    setTimeout(keepIntroAtTop, 250);
  });

  if (reduced) reveal();

  window.addEventListener("pagehide", function () {
    scrollLock(false);
    if (!entered) window.scrollTo(0, 0);
  });
  window.addEventListener("pageshow", function (event) {
    if (!event.persisted || entered) return;
    scrollLock(true);
    keepIntroAtTop();
    requestAnimationFrame(keepIntroAtTop);
    setTimeout(keepIntroAtTop, 150);
  });
})();
