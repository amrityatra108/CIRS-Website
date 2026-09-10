/* ============================================================
   Page-level behaviour
   ------------------------------------------------------------
   assets/js/cirs.js is the design system's interaction layer and
   comes out of the Claude artifact — a single-page design. This
   file is the repository's own, for behaviour only a multi-page
   site needs. Keep it small, and keep it working without GSAP or
   Lenis, which are loaded from a CDN and may not arrive.
   ============================================================ */
(function () {
  "use strict";

  /* ----------------------------------------------------------
     "On this page" — the index that opens from the right edge.
     Progressive enhancement: the markup is a button and a list,
     so with this file blocked the links are still reachable, and
     the panel is simply always closed.
     ---------------------------------------------------------- */
  var jump = document.querySelector(".jump");
  if (!jump) return;

  var toggle = jump.querySelector(".jump__toggle");
  var panel = jump.querySelector(".jump__panel");
  if (!toggle || !panel) return;

  // Hover opens it; a click pins it open so it survives the pointer
  // leaving. Without the pin, hovering opened the panel and the click
  // that followed immediately toggled it shut again.
  var pinned = false;

  function open() {
    jump.classList.add("is-open");
    toggle.setAttribute("aria-expanded", "true");
  }
  function close() {
    pinned = false;
    jump.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
  }
  function isOpen() {
    return jump.classList.contains("is-open");
  }

  toggle.addEventListener("click", function () {
    if (pinned) { close(); return; }
    pinned = true;
    open();
  });

  // Pointer users get it on hover. Ignored where hover is emulated, so a
  // first tap on a touchscreen does not open and close in one gesture.
  if (window.matchMedia && window.matchMedia("(hover:hover)").matches) {
    jump.addEventListener("mouseenter", open);
    jump.addEventListener("mouseleave", function () { if (!pinned) close(); });
  }

  // Keyboard: reaching the toggle by tab should show what it controls.
  toggle.addEventListener("focus", open);
  jump.addEventListener("focusout", function (e) {
    if (!pinned && !jump.contains(e.relatedTarget)) close();
  });

  panel.addEventListener("click", function (e) {
    if (e.target.closest("a")) close();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && isOpen()) {
      close();
      toggle.focus();
    }
  });

  document.addEventListener("click", function (e) {
    if (isOpen() && !jump.contains(e.target)) close();
  });

  /* Mark the section currently on screen. Uses IntersectionObserver
     where it exists and does nothing where it does not, rather than
     falling back to a scroll handler nobody needs. */
  if (!("IntersectionObserver" in window)) return;

  var links = Array.prototype.slice.call(panel.querySelectorAll('a[href^="#"]'));
  var byId = {};
  var targets = [];
  links.forEach(function (a) {
    var el = document.getElementById(a.getAttribute("href").slice(1));
    if (el) { byId[el.id] = a; targets.push(el); }
  });
  if (!targets.length) return;

  var seen = {};
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) { seen[entry.target.id] = entry.isIntersecting; });
    var current = null;
    targets.forEach(function (el) { if (seen[el.id] && !current) current = el.id; });
    links.forEach(function (a) { a.removeAttribute("aria-current"); });
    if (current && byId[current]) byId[current].setAttribute("aria-current", "true");
  }, { rootMargin: "-45% 0px -45% 0px" });

  targets.forEach(function (el) { io.observe(el); });
})();
