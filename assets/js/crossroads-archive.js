(function () {
  "use strict";
  var hero = document.querySelector(".crossroads-archive-hero");
  if (!hero) return;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var played = false, animations = [];
  var selectors = [".crwall", ".crossroads-archive-hero__eyebrow", ".crossroads-archive-hero__title", ".crossroads-archive-hero__statement", ".crossroads-archive-hero__description", ".crossroads-archive-hero__footer", ".crossroads-archive-hero__feature"];
  function reveal() {
    if (played) return;
    played = true;
    if (reduced.matches || !hero.animate) return;
    selectors.forEach(function (selector, index) {
      var el = hero.querySelector(selector);
      if (!el) return;
      var restingTransform = getComputedStyle(el).transform;
      var entranceTransform = index ? "translateY(24px) " + (restingTransform === "none" ? "" : restingTransform) : restingTransform;
      animations.push(el.animate([{opacity:0, transform:entranceTransform}, {opacity:1, transform:restingTransform}], {duration:650, delay:index * 85, easing:"cubic-bezier(.2,.65,.3,1)", fill:"backwards"}));
    });
  }
  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { reveal(); observer.disconnect(); }
    }, {threshold:0.15});
    observer.observe(hero);
  }
  function finish() { played = true; animations.forEach(function (animation) { animation.finish(); }); }
  reduced.addEventListener("change", function () { if (reduced.matches) finish(); });
  window.addEventListener("pageshow", function (event) { if (event.persisted) finish(); });
  hero.addEventListener("focusin", finish);
  hero.addEventListener("click", function (event) {
    var link = event.target.closest(".crossroads-archive-hero__primary");
    if (!link || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var archive = document.getElementById("archive");
    if (!archive) return;
    event.preventDefault(); event.stopPropagation();
    if (location.hash !== "#archive") history.pushState(null, "", "#archive");
    archive.setAttribute("tabindex", "-1");
    archive.focus({preventScroll:true});
    archive.scrollIntoView({behavior:reduced.matches ? "instant" : "smooth", block:"start"});
  }, true);
}());
