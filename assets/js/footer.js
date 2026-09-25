(function () {
  "use strict";

  var scene = document.querySelector("[data-closing-scene]");
  var footerWrap = document.querySelector(".footer-wrap");
  var root = document.documentElement;
  var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (scene && !reducedMotion && "IntersectionObserver" in window) {
    root.classList.add("has-footer-scene-motion");
    var reveal = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          scene.classList.add("is-visible");
          reveal.unobserve(scene);
        }
      });
    }, { threshold: 0.18, rootMargin: "0px 0px -6% 0px" });
    reveal.observe(scene);
  }
  if (scene) {
    scene.addEventListener("focusin", function () {
      scene.classList.add("is-visible");
    });
  }

  if ("IntersectionObserver" in window) {
    var zoneState = { scene: false, footer: false };
    var zone = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        zoneState[entry.target === scene ? "scene" : "footer"] = entry.isIntersecting;
      });
      // The sticky footer sits behind the page even at scroll position zero.
      // Its intersection alone does not mean the visitor has reached it.
      var footerReached = zoneState.footer &&
        (!scene || scene.getBoundingClientRect().bottom <= window.innerHeight);
      root.classList.toggle("footer-zone-active", zoneState.scene || footerReached);
    }, { threshold: 0.01 });
    if (scene) zone.observe(scene);
    if (footerWrap) zone.observe(footerWrap);
  }

  if (!scene || reducedMotion || !window.matchMedia ||
      !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

  var frame = 0;
  var shiftX = 0;
  var shiftY = 0;

  scene.addEventListener("pointermove", function (event) {
    if (event.pointerType === "touch") return;
    var bounds = scene.getBoundingClientRect();
    shiftX = ((event.clientX - bounds.left) / bounds.width - 0.5) * -14;
    shiftY = ((event.clientY - bounds.top) / bounds.height - 0.5) * -8;
    if (frame) return;
    frame = window.requestAnimationFrame(function () {
      scene.style.setProperty("--scene-shift-x", shiftX.toFixed(1) + "px");
      scene.style.setProperty("--scene-shift-y", shiftY.toFixed(1) + "px");
      frame = 0;
    });
  }, { passive: true });

  scene.addEventListener("pointerleave", function () {
    scene.style.setProperty("--scene-shift-x", "0px");
    scene.style.setProperty("--scene-shift-y", "0px");
  }, { passive: true });
})();
