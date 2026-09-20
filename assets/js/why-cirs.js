/* Why CIRS — measured, section-by-section navigation for the photo sequence. */
(function () {
  "use strict";

  var sections = Array.prototype.slice.call(document.querySelectorAll("main > .saga"));
  var facts = document.getElementById("facts");
  if (sections.length < 2) return;

  var targets = facts ? sections.concat(facts) : sections;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var moving = false;
  var wheelTotal = 0;
  var wheelTimer = 0;
  var touchY = null;

  function topOf(el) {
    return Math.max(0, el.getBoundingClientRect().top + window.scrollY);
  }

  function nearestIndex() {
    var y = window.scrollY + window.innerHeight * 0.42;
    var best = 0;
    var distance = Infinity;
    targets.forEach(function (target, index) {
      var nextDistance = Math.abs(topOf(target) - y);
      if (nextDistance < distance) {
        distance = nextDistance;
        best = index;
      }
    });
    return best;
  }

  function inPhotoSequence() {
    var first = topOf(sections[0]);
    var last = topOf(sections[sections.length - 1]) + sections[sections.length - 1].offsetHeight;
    var middle = window.scrollY + window.innerHeight * 0.5;
    return middle >= first && middle <= last;
  }

  function blocked(target) {
    return document.body.classList.contains("is-locked") ||
      (target && target.closest && target.closest("input, textarea, select, [contenteditable], .panel"));
  }

  function settle() {
    moving = false;
  }

  function move(direction) {
    if (moving || !inPhotoSequence()) return false;
    var from = nearestIndex();
    var to = Math.max(0, Math.min(targets.length - 1, from + direction));
    if (to === from) return false;

    moving = true;
    var top = topOf(targets[to]);
    var duration = reduced.matches ? 0 : 0.82;
    var request = new CustomEvent("cirs-section-scroll", {
      cancelable:true,
      detail:{ top:top, duration:duration, onComplete:settle }
    });
    window.dispatchEvent(request);

    if (!request.defaultPrevented) {
      window.scrollTo({ top:top, behavior:reduced.matches ? "auto" : "smooth" });
      window.setTimeout(settle, reduced.matches ? 80 : 900);
    }
    return true;
  }

  window.addEventListener("wheel", function (event) {
    if (blocked(event.target) || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
    if (!inPhotoSequence()) { wheelTotal = 0; return; }

    // Own the complete wheel gesture while the photo sequence is active.
    // Otherwise the follow-up events emitted by a trackpad or wheel leak into
    // Lenis during the transition and can carry the page across many panels.
    event.preventDefault();
    if (moving) return;

    wheelTotal += event.deltaY;
    window.clearTimeout(wheelTimer);
    wheelTimer = window.setTimeout(function () { wheelTotal = 0; }, 140);
    if (Math.abs(wheelTotal) < 24) return;

    var direction = wheelTotal > 0 ? 1 : -1;
    wheelTotal = 0;
    move(direction);
  }, { passive:false });

  window.addEventListener("touchstart", function (event) {
    if (blocked(event.target) || event.touches.length !== 1) return;
    touchY = event.touches[0].clientY;
  }, { passive:true });

  window.addEventListener("touchend", function (event) {
    if (touchY === null || blocked(event.target) || !event.changedTouches.length) return;
    var distance = touchY - event.changedTouches[0].clientY;
    touchY = null;
    if (Math.abs(distance) >= 48) move(distance > 0 ? 1 : -1);
  }, { passive:true });

  window.addEventListener("touchmove", function (event) {
    if (touchY !== null && !blocked(event.target) && inPhotoSequence()) event.preventDefault();
  }, { passive:false });

  document.addEventListener("keydown", function (event) {
    if (event.defaultPrevented || blocked(event.target) || !inPhotoSequence()) return;
    var direction = 0;
    if (event.key === "PageDown" || event.key === "ArrowDown" || (event.key === " " && !event.shiftKey)) direction = 1;
    if (event.key === "PageUp" || event.key === "ArrowUp" || (event.key === " " && event.shiftKey)) direction = -1;
    if (direction) {
      event.preventDefault();
      if (!moving) move(direction);
    }
  });
})();
