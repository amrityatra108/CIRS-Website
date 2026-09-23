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
  var chapterTrigger = null;
  var wave = move.querySelector("[data-move-wave]");
  var markers = {
    court: document.getElementById("sports-court-point"),
    water: document.getElementById("sports-water-point")
  };
  var links = Array.prototype.slice.call(
    chapters.querySelectorAll("[data-chapter-link]")
  );
  var captions = {
    court: chapters.querySelector('[data-chapter="court"] .sports-chapter__caption'),
    water: chapters.querySelector('[data-chapter="water"] .sports-chapter__caption')
  };

  function clamp(value) {
    return Math.max(0, Math.min(1, value));
  }

  function smooth(value) {
    var t = clamp(value);
    return t * t * (3 - 2 * t);
  }

  function setMove(progress) {
    var p = clamp(progress);
    var reveal = smooth((p - 0.015) / 0.54);
    var edge = 1 - reveal;
    var amplitude = (window.innerWidth <= 720 ? 0.065 : 0.045) * Math.sin(Math.PI * reveal);

    if (wave) {
      wave.setAttribute(
        "d",
        "M " + edge.toFixed(4) + " 0 C " +
          (edge + amplitude).toFixed(4) + " .26 " +
          (edge - amplitude).toFixed(4) + " .74 " +
          edge.toFixed(4) + " 1 L 1 1 L 1 0 Z"
      );
    }

    var enter = smooth((p - 0.055) / 0.18);
    var resolve = smooth((p - 0.58) / 0.34);
    var finishReveal = smooth((p - 0.58) / 0.32);
    var finalScale = window.innerWidth <= 720 ? 0.20 : 0.14;
    var scale = (0.54 + enter * 0.46) * (1 - resolve) + finalScale * resolve;
    var x = -window.innerWidth * (window.innerWidth <= 720 ? 0.31 : 0.35) * resolve;
    var y = -window.innerHeight * 0.36 * resolve;
    var actionX = -window.innerWidth * (window.innerWidth <= 720 ? 0.025 : 0.035) * reveal * (1 - resolve);
    var actionScale = 1.05 - 0.05 * reveal;

    move.style.setProperty("--move-scale", scale.toFixed(4));
    move.style.setProperty("--move-x", x.toFixed(1) + "px");
    move.style.setProperty("--move-y", y.toFixed(1) + "px");
    move.style.setProperty("--action-x", actionX.toFixed(1) + "px");
    move.style.setProperty("--action-scale", actionScale.toFixed(4));
    move.style.setProperty("--move-opacity", smooth((p - 0.055) / 0.12).toFixed(4));
    move.style.setProperty("--finish-bottom", ((1 - finishReveal) * 100).toFixed(2) + "%");
    move.style.setProperty("--move-resolution", smooth((p - 0.78) / 0.15).toFixed(4));
  }

  function setCaptionProgress(progress) {
    var p = clamp(progress);
    var waterIn = smooth((p - 0.48) / 0.20);
    var courtOut = smooth((p - 0.49) / 0.17);

    chapters.style.setProperty("--water-right", ((1 - waterIn) * 100).toFixed(2) + "%");
    if (captions.court) captions.court.style.setProperty("--chapter-caption", (1 - courtOut).toFixed(3));
    if (captions.water) captions.water.style.setProperty("--chapter-caption", waterIn.toFixed(3));

    var current = p < 0.64 ? "court" : "water";
    links.forEach(function (link) {
      if (link.getAttribute("data-chapter-link") === current) {
        link.setAttribute("aria-current", "step");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }

  function placeMarkers() {
    if (!root.classList.contains("sports-journey-ready")) return;
    var travel = Math.max(0, chapters.offsetHeight - window.innerHeight);
    var anchorOffset = 88;
    if (markers.court) markers.court.style.top = anchorOffset + "px";
    if (markers.water) {
      var waterOffset = window.innerWidth <= 720 ? window.innerHeight : travel * 0.56;
      markers.water.style.top = Math.round(waterOffset + anchorOffset) + "px";
    }
  }

  function clearStyles() {
    ["--move-scale", "--move-x", "--move-y", "--action-x", "--action-scale", "--move-opacity",
      "--finish-bottom", "--move-resolution"].forEach(function (name) {
      move.style.removeProperty(name);
    });
    ["--water-right"].forEach(function (name) {
      chapters.style.removeProperty(name);
    });
    Object.keys(captions).forEach(function (key) {
      if (captions[key]) captions[key].style.removeProperty("--chapter-caption");
    });
    links.forEach(function (link) { link.removeAttribute("aria-current"); });
  }

  function teardown() {
    if (moveTrigger) { moveTrigger.kill(); moveTrigger = null; }
    if (chapterTrigger) { chapterTrigger.kill(); chapterTrigger = null; }
    root.classList.remove("sports-journey-ready");
    clearStyles();
  }

  function setup() {
    if (reduce.matches || moveTrigger || !window.gsap || !window.ScrollTrigger) return;
    root.classList.add("sports-journey-ready");
    placeMarkers();

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
      onUpdate: function (self) { setCaptionProgress(self.progress); },
      onRefresh: function (self) {
        placeMarkers();
        setCaptionProgress(self.progress);
      }
    });
    ScrollTrigger.refresh();
  }

  setup();

  reduce.addEventListener("change", function () {
    if (reduce.matches) teardown();
    else setup();
  });
  window.addEventListener("resize", placeMarkers, { passive: true });
  window.addEventListener("pagehide", teardown);
  window.addEventListener("pageshow", function (event) {
    if (event.persisted) setup();
  });
}());
