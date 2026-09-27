/* Home's approved campus film owns entry. The static poster is its first frame. */
(function () {
  "use strict";
  var intro = document.getElementById("homeIntro");
  var film = document.getElementById("homeIntroVideo");
  if (!intro || !film) return;
  var playButton = intro.querySelector("[data-home-play]");
  var skipButton = intro.querySelector("[data-home-skip]");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var state = "boot";
  var startupTimer, stallTimer, exitTimer;
  function underlay() {
    return [document.querySelector(".header"), document.querySelector(".drawer"),
      document.querySelector("main"), document.querySelector(".footer-wrap")].filter(Boolean);
  }
  var nav = performance.getEntriesByType && performance.getEntriesByType("navigation")[0];

  function lock(locked) {
    underlay().forEach(function (node) { node.inert = locked; });
    window.dispatchEvent(new CustomEvent("cirs-intro-scroll-lock", {detail:{locked:locked}}));
  }
  function cleanup() {
    clearTimeout(startupTimer);
    clearTimeout(stallTimer);
    clearTimeout(exitTimer);
  }
  function finishIntro(reason, immediate) {
    if (state === "exiting" || state === "entered") return;
    state = "exiting";
    cleanup();
    film.pause(); // Keep the currently displayed frame through the crossfade.
    document.body.classList.remove("home-intro-pending");
    document.body.classList.add("home-intro-exiting");
    var duration = immediate ? 0 : reduced.matches ? 80 : reason === "skip" ? 500 : 750;
    intro.style.transitionDuration = duration + "ms";
    function entered() {
      if (state !== "exiting") return;
      state = "entered";
      var focusFromIntro = intro.contains(document.activeElement);
      intro.remove();
      document.body.classList.remove("home-intro-exiting");
      lock(false);
      window.dispatchEvent(new Event("cirs-home-intro-entered"));
      if (focusFromIntro) {
        var focusHero = function () {
          var heading = document.querySelector(".hseq__type h1");
          if (heading) { heading.tabIndex = -1; heading.focus({preventScroll:true}); }
        };
        if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", focusHero, {once:true});
        else focusHero();
      }
      if (window.ScrollTrigger) requestAnimationFrame(function () { ScrollTrigger.refresh(); });
    }
    exitTimer = setTimeout(entered, duration + 40);
  }
  function showPlay() {
    if (state === "exiting" || state === "entered") return;
    state = "awaiting-play";
    playButton.hidden = false;
    skipButton.textContent = "Continue to website";
  }
  function start() {
    if (state === "exiting" || state === "entered") return;
    clearTimeout(startupTimer);
    state = "awaiting-play";
    film.muted = true;
    var request;
    try { request = film.play(); } catch (error) { showPlay(); return; }
    if (request && request.catch) request.catch(showPlay);
    startupTimer = setTimeout(showPlay, 8000);
  }
  lock(true);
  document.addEventListener("DOMContentLoaded", function () {
    if (state !== "entered") lock(true);
  }, {once:true});
  skipButton.addEventListener("click", function () { finishIntro("skip"); });
  playButton.addEventListener("click", start);
  film.addEventListener("playing", function () {
    if (state === "exiting" || state === "entered") return;
    state = "playing";
    clearTimeout(startupTimer);
    clearTimeout(stallTimer);
    playButton.hidden = true;
    skipButton.textContent = "Skip intro";
    stallTimer = setTimeout(function () { finishIntro("timeout"); }, Math.max(30000, (film.duration || 20) * 1000 + 10000));
  });
  film.addEventListener("ended", function () { finishIntro("ended"); });
  film.addEventListener("error", function () { finishIntro("error"); });
  film.addEventListener("stalled", function () {
    if (state === "playing") { clearTimeout(stallTimer); stallTimer = setTimeout(function () { finishIntro("stalled"); }, 10000); }
  });
  window.addEventListener("pageshow", function (event) { if (event.persisted) finishIntro("restored", true); });
  if ((nav && nav.type === "back_forward") || location.hash) finishIntro("deep-link", true);
  else if (reduced.matches) showPlay();
  else start();
  window.__homeIntroReady = true;
}());
