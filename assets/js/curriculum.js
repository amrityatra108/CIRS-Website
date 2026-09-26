/* Curriculum: the grade route's one-time draw.

   The route is drawn by the stylesheet on load, which is right when it is
   already on screen and harmless when there is no script at all. When the
   page opens with the route below the fold, that draw would play unseen, so
   hold the route undrawn (it is off screen, so nothing visibly changes) and
   let it draw when it arrives. Reduced motion: the stylesheet draws nothing,
   and this does nothing. */
(function () {
  "use strict";
  var route = document.querySelector(".cur-route");
  if (!route || !("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (route.getBoundingClientRect().top < window.innerHeight) return;

  route.classList.add("is-waiting");
  var io = new IntersectionObserver(function (entries) {
    if (!entries[0].isIntersecting) return;
    route.classList.remove("is-waiting");
    io.disconnect();
  }, { rootMargin: "0px 0px -15% 0px" });
  io.observe(route);
})();
