(function () {
  "use strict";

  var intro = document.getElementById("portal-intro");
  var video = document.getElementById("portalIntroVideo");
  var entry = document.getElementById("portalIntroEntry");
  var target = document.getElementById("top");
  if (!intro || !video || !entry || !target) return;

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var originalRestoration = window.__portalOriginalRestoration || history.scrollRestoration;
  var originalScrollBehavior = document.documentElement.style.scrollBehavior;
  var revealed = false;
  var entered = false;
  var revealTimer;
  var failTimer;

  function scrollLock(locked) {
    document.body.classList.toggle("portal-intro-active", locked);
    document.documentElement.style.scrollBehavior = locked ? "auto" : originalScrollBehavior;
    history.scrollRestoration = locked ? "manual" : originalRestoration;
    window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: locked } }));
  }

  // Scroll restoration can run after load/pageshow. Keep the video at the
  // viewport top until the visitor explicitly uses the entry control.
  function keepIntroAtTop() {
    if (!entered && document.body.classList.contains("portal-intro-active") && window.scrollY !== 0) {
      window.scrollTo(0, 0);
    }
  }

  function reveal() {
    if (revealed || entered) return;
    revealed = true;
    clearTimeout(failTimer);
    intro.classList.add("is-revealed");
  }

  function finishVideo() {
    if (revealed || entered || revealTimer) return;
    clearTimeout(failTimer);
    revealTimer = setTimeout(reveal, reduced ? 0 : 220);
  }

  function fallback() {
    if (revealed || entered) return;
    intro.classList.add("is-fallback");
    video.pause();
    finishVideo();
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
  video.addEventListener("ended", finishVideo);
  video.addEventListener("error", fallback);
  var source = video.querySelector("source");
  if (source) source.addEventListener("error", fallback);

  scrollLock(true);
  window.scrollTo(0, 0);
  window.addEventListener("scroll", keepIntroAtTop, { passive: true });
  window.addEventListener("load", function () {
    keepIntroAtTop();
    setTimeout(keepIntroAtTop, 250);
  });

  if (reduced) {
    // Keep the moving vault out of view and make the entry available at once.
    video.pause();
    intro.classList.add("is-fallback");
    reveal();
  } else {
    failTimer = setTimeout(fallback, 15000);
    if (video.ended) finishVideo();
    else {
      var playback = video.play();
      if (playback && playback.catch) playback.catch(fallback);
    }
  }

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
    if (video.ended) finishVideo();
    else if (!reduced) {
      var playback = video.play();
      if (playback && playback.catch) playback.catch(fallback);
    }
  });
})();
