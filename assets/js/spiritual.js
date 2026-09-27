/* Spiritual Life — two small pieces of motion, both optional.

   1. The opening photograph settles and its lines rise once the shared
      curtain has lifted (cirs.js removes #curtain when it is done), so the
      entrance is not spent behind it.
   2. The day's timeline: a gold thread runs down the hairline as the reader
      does, and each practice's mark lights as the thread reaches it.

   The fade-up of every .rv element is the shared one in cirs.js. With
   reduced motion, or no scripting, the hero is simply there and the thread is
   drawn in full (see spiritual.css). */
(function () {
  "use strict";
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) return;

  // 1. The opening.
  var hero = document.querySelector(".sp-hero");
  if (hero && document.visibilityState !== "hidden" && window.scrollY < 40) {
    hero.classList.add("sp-hero--armed");
    var started = Date.now();
    (function wait() {
      // A hard ceiling, so a curtain that never leaves cannot hide the title.
      if (!document.getElementById("curtain") || Date.now() - started > 5000) {
        requestAnimationFrame(function () {
          requestAnimationFrame(function () { hero.classList.add("is-in"); });
        });
        return;
      }
      window.setTimeout(wait, 80);
    })();
  }

  // 2. The thread of the day.
  var line = document.querySelector("[data-sp-line]");
  if (!line) return;
  var steps = Array.prototype.slice.call(line.querySelectorAll(".sp-step"));
  line.setAttribute("data-sp-live", "");
  var queued = false;
  function update() {
    queued = false;
    var box = line.getBoundingClientRect();
    var mark = window.innerHeight * 0.62;
    var p = Math.min(1, Math.max(0, (mark - box.top) / Math.max(1, box.height)));
    line.style.setProperty("--sp-progress", p.toFixed(4));
    steps.forEach(function (step) {
      step.classList.toggle("is-lit", step.getBoundingClientRect().top + 8 < mark);
    });
  }
  function queue() {
    if (queued) return;
    queued = true;
    requestAnimationFrame(update);
  }
  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", queue);
  update();
})();
