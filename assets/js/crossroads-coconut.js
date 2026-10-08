(function () {
  "use strict";
  var patch = document.querySelector("[data-crossroads-coconut]");
  if (!patch) return;
  var button = patch.querySelector("button");
  var seed = patch.querySelector(".cr-coconut__seed");
  var rain = patch.querySelector(".cr-coconut__rain");
  var status = patch.querySelector("[role=status]");
  var motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var clicks = 0, timers = new Set(), tapAnimation = null;
  function later(callback, delay) {
    var id = window.setTimeout(function () { timers.delete(id); callback(); }, delay);
    timers.add(id);
  }
  function reset(announce) {
    timers.forEach(window.clearTimeout); timers.clear();
    if (tapAnimation) { tapAnimation.cancel(); tapAnimation = null; }
    rain.replaceChildren(); clicks = 0;
    patch.dataset.state = "idle"; patch.dataset.clicks = "0";
    button.setAttribute("aria-disabled", "false");
    button.setAttribute("aria-label", "A little coconut. Tap to investigate.");
    status.textContent = announce ? "The little coconut is back. You can grow it again." : "";
  }
  function shower() {
    patch.dataset.state = "raining";
    // A finite shower, inside the margin: no page-wide overlay or animation loop.
    var count = motion.matches ? 6 : 24;
    var fragment = document.createDocumentFragment();
    for (var i = 0; i < count; i++) {
      var drop = document.createElement("span");
      drop.className = "cr-coconut__drop";
      drop.style.left = (30 + (i * 37 % 132)) + "px";
      drop.style.setProperty("--delay", (i * 95) + "ms");
      drop.style.setProperty("--drift", ((i % 5 - 2) * 10) + "px");
      drop.style.setProperty("--turn", (i % 2 ? 160 : -140) + "deg");
      var fruit = seed.cloneNode(true); fruit.removeAttribute("class");
      drop.appendChild(fruit); fragment.appendChild(drop);
    }
    rain.appendChild(fragment);
    status.textContent = motion.matches ? "A pixel coconut palm! Coconuts have gathered underneath." : "A pixel coconut palm! It's raining coconuts.";
    later(function () { reset(true); }, motion.matches ? 4000 : 4500);
  }
  button.addEventListener("click", function () {
    if (patch.dataset.state !== "idle") return;
    clicks++; patch.dataset.clicks = String(clicks);
    if (tapAnimation) tapAnimation.cancel();
    if (clicks < 10) {
      button.setAttribute("aria-label", "A little coconut. " + clicks + " of 10 taps.");
      if (!motion.matches && seed.animate) {
        tapAnimation = seed.animate([
          {transform:"translateY(0) rotate(0deg)"},
          {transform:"translateY(-7px) rotate(" + (clicks % 2 ? 12 : -12) + "deg)"},
          {transform:"translateY(0) rotate(0deg)"}
        ], {duration:180, easing:"steps(4, end)"});
      }
      return;
    }
    if (tapAnimation) { tapAnimation.cancel(); tapAnimation = null; }
    patch.dataset.state = "growing";
    button.setAttribute("aria-disabled", "true");
    button.setAttribute("aria-label", "Coconut palm growing. The coconut will return shortly.");
    status.textContent = "Ten taps! Your coconut is growing into a pixel palm.";
    if (motion.matches) shower(); else later(shower, 1200);
  });
  function preferences() {
    patch.toggleAttribute("data-reduced", motion.matches);
    if (patch.dataset.state !== "idle") reset(false);
  }
  motion.addEventListener("change", preferences);
  document.addEventListener("visibilitychange", function () { if (document.hidden) reset(false); });
  window.addEventListener("pagehide", function () { reset(false); });
  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting && patch.dataset.state !== "idle") reset(false);
    });
    observer.observe(patch);
  }
  preferences(); reset(false);
}());
