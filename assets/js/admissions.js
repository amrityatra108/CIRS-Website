(function () {
  "use strict";

  var body = document.body;
  if (!body.classList.contains("admissions")) return;

  var sections = Array.prototype.slice.call(document.querySelectorAll(".cirs-entry-section"));
  var canObserve = typeof window.IntersectionObserver === "function";
  body.classList.add("ad-enhanced");

  // Section rules are decorative. Keep the page readable if observation fails.
  function showSectionRules() {
    sections.forEach(function (section) { section.classList.add("is-seen"); });
  }

  function initSectionRules() {
    if (!canObserve) { showSectionRules(); return; }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-seen");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -18% 0px", threshold: 0.08 });
    sections.forEach(function (section) { observer.observe(section); });
  }

  function initProcess() {
    var process = document.querySelector(".ad-process");
    if (!process) return;
    var steps = Array.prototype.slice.call(process.querySelectorAll(".ad-process__item"));
    var circles = steps.map(function (step) { return step.querySelector(".ad-process__number"); });
    if (!steps.length || circles.some(function (circle) { return !circle; })) return;

    var processFrame = 0;
    var processCompleted = false;
    function updateProcess() {
      processFrame = 0;
      if (!circles.every(function (circle) { return circle.isConnected; })) return;
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
    }

    function requestProcessUpdate() {
      if (!processFrame) processFrame = window.requestAnimationFrame(updateProcess);
    }
    // Lenis can suppress native scroll events; ScrollTrigger receives its ticks.
    if (typeof window.ScrollTrigger !== "undefined") {
      try {
        window.ScrollTrigger.create({
          trigger: process,
          start: "top bottom",
          end: "bottom top",
          onUpdate: requestProcessUpdate,
          onRefresh: requestProcessUpdate
        });
      } catch (error) { /* Native scrolling still updates the decoration. */ }
    }
    window.addEventListener("scroll", requestProcessUpdate, { passive: true });
    window.addEventListener("resize", requestProcessUpdate);
    updateProcess();
  }

  // An error in one enhancement must not prevent the others from starting.
  try { initSectionRules(); } catch (error) { showSectionRules(); }
  try { initProcess(); } catch (error) { /* The numbered list stays fully visible. */ }
})();
