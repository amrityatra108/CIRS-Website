(function () {
  "use strict";

  var body = document.body;
  if (!body.classList.contains("admissions")) return;

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  body.classList.add("ad-enhanced");

  var hero = document.querySelector(".pagehero");
  if (hero && !reduced) {
    body.classList.add("ad-hero-pending");
    var revealHero = function () {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () { body.classList.add("ad-hero-visible"); });
      });
    };
    var curtain = document.getElementById("curtain");
    if (!curtain && !body.classList.contains("is-locked")) {
      revealHero();
    } else {
      var heroObserver = new MutationObserver(function () {
        if (!body.classList.contains("is-locked") && !document.getElementById("curtain")) {
          heroObserver.disconnect();
          revealHero();
        }
      });
      heroObserver.observe(body, { attributes:true, childList:true });
      window.setTimeout(function () {
        if (!body.classList.contains("ad-hero-visible")) {
          heroObserver.disconnect();
          revealHero();
        }
      }, 4400);
    }
  }

  if (!("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(document.querySelectorAll(".ad-section,.ad-campus__media,.ad-campus__content"), function (el) {
      el.classList.add(el.classList.contains("ad-section") ? "is-seen" : "is-revealed");
    });
    return;
  }

  var sectionObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-seen");
        sectionObserver.unobserve(entry.target);
      }
    });
  }, { rootMargin: "0px 0px -18% 0px", threshold: 0.08 });
  Array.prototype.forEach.call(document.querySelectorAll(".ad-section"), function (section) {
    sectionObserver.observe(section);
  });

  var process = document.querySelector(".ad-process");
  if (process) {
    var steps = Array.prototype.slice.call(process.querySelectorAll(".ad-process__item"));
    var processFrame = 0;
    var processCompleted = false;
    var updateProcess = function () {
      processFrame = 0;
      var circles = steps.map(function (step) { return step.querySelector(".ad-process__number"); });
      var first = circles[0].getBoundingClientRect();
      var last = circles[circles.length - 1].getBoundingClientRect();
      var firstY = first.top + first.height / 2;
      var lastY = last.top + last.height / 2;
      var readingLine = window.innerHeight * .44;
      var progress = Math.max(0, Math.min(1, (readingLine - firstY) / Math.max(1, lastY - firstY)));
      process.style.setProperty("--process-progress", progress.toFixed(4));
      if (!processCompleted && progress >= .985) {
        processCompleted = true;
        process.classList.add("is-complete");
      }

      var nearest = 0;
      var distance = Infinity;
      circles.forEach(function (circle, index) {
        var box = circle.getBoundingClientRect();
        var nextDistance = Math.abs(box.top + box.height / 2 - readingLine);
        if (nextDistance < distance) { distance = nextDistance; nearest = index; }
      });
      steps.forEach(function (step, index) { step.classList.toggle("is-current", index === nearest); });
    };
    var requestProcessUpdate = function () {
      if (!processFrame) processFrame = window.requestAnimationFrame(updateProcess);
    };
    window.addEventListener("scroll", requestProcessUpdate, { passive:true });
    window.addEventListener("resize", requestProcessUpdate);
    updateProcess();
  }

  var dates = Array.prototype.slice.call(document.querySelectorAll(".ad-timeline li"));
  if (dates.length) {
    if (window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
      dates.forEach(function (date) {
        date.addEventListener("pointerenter", function () {
          dates.forEach(function (item) { item.classList.remove("is-pointer"); });
          date.classList.add("is-pointer");
        });
        date.addEventListener("pointermove", function (event) {
          var box = date.getBoundingClientRect();
          date.style.setProperty("--pointer-x", (event.clientX - box.left) + "px");
          date.style.setProperty("--pointer-y", (event.clientY - box.top) + "px");
        });
        date.addEventListener("pointerleave", function () {
          date.classList.remove("is-pointer");
        });
      });
    }
  }

  var revealTargets = document.querySelectorAll(".ad-campus__media,.ad-campus__content");
  if (reduced) {
    Array.prototype.forEach.call(revealTargets, function (el) { el.classList.add("is-revealed"); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -16% 0px", threshold: 0.16 });
    Array.prototype.forEach.call(revealTargets, function (el) { revealObserver.observe(el); });
  }
})();
