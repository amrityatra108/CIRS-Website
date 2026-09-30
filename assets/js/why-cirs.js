/* Why CIRS: one deliberate desktop gesture per chapter. The document remains
   normally scrollable on touch, with reduced motion, and outside the sequence. */
(function () {
  "use strict";
  var enabled = matchMedia("(min-width: 900px) and (min-height: 600px) and (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)");
  var sections = Array.from(document.querySelectorAll("body.why-cirs .saga, body.why-cirs #facts"));
  var busyUntil = 0, lastWheel = 0, sum = 0, direction = 0;

  function available(event) {
    return enabled.matches && !event.defaultPrevented &&
      !document.body.matches(".is-locked, .menu-open, .has-lightbox") &&
      !document.querySelector('dialog[open], .panel.is-open') &&
      !event.target.closest('input, textarea, select, button, a, summary, [contenteditable], [role="dialog"], [data-lenis-prevent], .jump');
  }

  function destination(dir) {
    var y = window.scrollY;
    var tops = sections.map(function (section) { return section.getBoundingClientRect().top + y; });
    // Once past the last chapter, leave the facts, closing and footer native.
    if (y > tops[tops.length - 1] + 8) return null;
    var current = 0;
    tops.forEach(function (top, i) { if (top <= y + 8) current = i; });
    // A tall chapter must be readable before advancing; reverse scroll likewise.
    if (dir > 0 && sections[current].getBoundingClientRect().bottom > innerHeight + 12) return null;
    if (dir < 0 && y > tops[current] + 12) return null;
    var next = current + dir;
    return next >= 0 && next < tops.length ? tops[next] : null;
  }

  function move(top) {
    busyUntil = performance.now() + 900;
    var request = new CustomEvent("cirs-section-scroll", {
      cancelable: true,
      detail: { top: top, duration: 0.75 }
    });
    if (window.dispatchEvent(request)) window.scrollTo({ top: top, behavior: "smooth" });
  }

  window.addEventListener("wheel", function (event) {
    if (!available(event) || event.ctrlKey || event.metaKey || event.shiftKey ||
        Math.abs(event.deltaX) > Math.abs(event.deltaY) || !event.deltaY) return;
    var now = performance.now(), gap = now - lastWheel;
    lastWheel = now;
    var dir = Math.sign(event.deltaY);
    if (now < busyUntil || (gap < 180 && direction === dir && sum === Infinity)) {
      event.preventDefault();
      return;
    }
    if (gap >= 180 || direction !== dir) sum = 0;
    direction = dir;
    var top = destination(dir);
    if (top === null) { sum = 0; return; }
    event.preventDefault();
    sum += Math.abs(event.deltaY) * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? innerHeight : 1);
    if (sum >= 24) { sum = Infinity; move(top); }
  }, { passive: false, capture: true });

  window.addEventListener("keydown", function (event) {
    if (!available(event) || event.altKey || event.ctrlKey || event.metaKey) return;
    var dir = ({ ArrowDown: 1, PageDown: 1, ArrowUp: -1, PageUp: -1 })[event.key];
    if (event.key === " ") dir = event.shiftKey ? -1 : 1;
    if (!dir) return;
    var top = destination(dir);
    if (top === null) return;
    event.preventDefault();
    if (!event.repeat && performance.now() >= busyUntil) move(top);
  }, true);
})();
