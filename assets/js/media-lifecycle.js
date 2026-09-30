/* Shared, opt-in media ownership. Scripted openings keep their own controllers. */
(function () {
  "use strict";
  function createSeeker(video) {
    var wanted = null, enabled = true;
    function flush() {
      if (!enabled || document.hidden || wanted === null || video.seeking || video.readyState < 1 || !isFinite(video.duration)) return;
      var target = Math.max(0, Math.min(wanted, Math.max(0, video.duration - 0.03)));
      if (Math.abs(video.currentTime - target) < 1 / 48) return;
      try { video.currentTime = target; } catch (error) { /* Keep the latest target for loadeddata/progress. */ }
    }
    ["seeked", "loadedmetadata", "loadeddata", "canplay", "progress"].forEach(function (name) { video.addEventListener(name, flush); });
    document.addEventListener("visibilitychange", flush);
    return {
      seek: function (time) { if (isFinite(time)) wanted = time; flush(); },
      enable: function (value) { enabled = value; if (!value) wanted = null; else flush(); },
      destroy: function () {
        ["seeked", "loadedmetadata", "loadeddata", "canplay", "progress"].forEach(function (name) { video.removeEventListener(name, flush); });
        document.removeEventListener("visibilitychange", flush);
      }
    };
  }
  function manage(video) {
    if (video._cirsMedia) return video._cirsMedia;
    var motion = matchMedia("(prefers-reduced-motion: reduce)");
    var visible = true, resume = false, suspended = false, ownPause = false;
    function blocked() { return !visible || document.hidden || suspended; }
    function pause() {
      if (video.paused) return;
      ownPause = true;
      video.pause();
    }
    function sync() {
      if (blocked()) {
        if (!video.paused) { resume = true; pause(); }
      } else if (resume && !motion.matches && !video.ended) {
        resume = false;
        var promise = video.play();
        if (promise) promise.catch(function () {});
      }
    }
    video.addEventListener("pause", function () {
      if (ownPause) ownPause = false;
      else resume = false; // A visitor's pause must never become an autoplay request.
    });
    video.addEventListener("play", function () { if (blocked()) { resume = true; pause(); } });
    document.addEventListener("visibilitychange", sync);
    window.addEventListener("pagehide", function () { suspended = true; sync(); });
    window.addEventListener("pageshow", function () { suspended = false; sync(); });
    if (typeof IntersectionObserver !== "undefined") {
      new IntersectionObserver(function (entries) { visible = entries[entries.length - 1].isIntersecting; sync(); }).observe(video);
    }
    function quiet() {
      if (motion.matches) { resume = false; video.removeAttribute("autoplay"); pause(); }
    }
    motion.addEventListener("change", quiet);
    quiet(); sync();
    video._cirsMedia = { forget: function () { resume = false; } };
    return video._cirsMedia;
  }
  window.CIRSMedia = { createSeeker: createSeeker, manage: manage };
  // No native controls here: these are decorative background loops. The Art
  // player registers explicitly so its mode switch can clear pending resume.
  document.querySelectorAll(".pagehero__video, .hseq__video, video[autoplay][aria-hidden='true']").forEach(manage);
}());
