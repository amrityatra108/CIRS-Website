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
<<<<<<< HEAD
=======
  var gestureHeld = false;
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
  var leaving = null;
  var arriving = null;
  var settleTimer = 0;

  function topOf(el) {
    return Math.max(0, el.getBoundingClientRect().top + window.scrollY);
  }

  function nearestIndex() {
    // Compare section starts with the viewport start. The opening frame is
    // intentionally shorter on phones, where using a point near the middle
    // of the viewport made the first wheel gesture mistake chapter two for
    // the current chapter and skip directly to chapter three.
    var y = window.scrollY;
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
    window.clearTimeout(settleTimer);
    document.body.classList.remove("is-section-moving");
    [leaving, arriving].forEach(function (target) {
      if (!target) return;
      target.classList.remove("is-section-leaving", "is-section-entering");
      target.style.removeProperty("--section-shift");
    });
    leaving = null;
    arriving = null;
    moving = false;
  }

  function prepareTransition(from, to, direction) {
<<<<<<< HEAD
    if (reduced.matches) return;
=======
    if (reduced.matches || from === to) return;
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
    leaving = targets[from];
    arriving = targets[to];
    document.body.classList.add("is-section-moving");
    leaving.classList.add("is-section-leaving");
    arriving.classList.add("is-section-entering");
    leaving.style.setProperty("--section-shift", direction > 0 ? "-8px" : "8px");
    arriving.style.setProperty("--section-shift", direction > 0 ? "8px" : "-8px");
  }

<<<<<<< HEAD
  function move(direction) {
    if (moving || !inPhotoSequence()) return false;
    var from = nearestIndex();
    var to = Math.max(0, Math.min(targets.length - 1, from + direction));
    if (to === from) return false;

    moving = true;
    prepareTransition(from, to, direction);
    var top = topOf(targets[to]);
    var duration = reduced.matches ? 0 : 0.72;
    var request = new CustomEvent("cirs-section-scroll", {
      cancelable:true,
      detail:{ top:top, duration:duration, onComplete:settle }
=======
  // Ease in and out so a chapter change gathers speed and then settles,
  // rather than leaping off at full speed the moment the wheel turns.
  function easeInOut(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  function move(direction) {
    if (moving || !(inPhotoSequence() || (direction < 0 && atFactsTop()))) return false;
    var from = nearestIndex();
    var to = Math.max(0, Math.min(targets.length - 1, from + direction));
    if (to === from) return false;
    return moveBetween(from, to, direction);
  }

  function moveBetween(from, to, direction) {
    moving = true;
    prepareTransition(from, to, direction);
    var top = topOf(targets[to]);
    var duration = reduced.matches ? 0 : 1.1;
    var request = new CustomEvent("cirs-section-scroll", {
      cancelable:true,
      detail:{ top:top, duration:duration, easing:easeInOut, onComplete:settle }
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
    });
    window.dispatchEvent(request);

    if (!request.defaultPrevented) {
      window.scrollTo({ top:top, behavior:reduced.matches ? "auto" : "smooth" });
<<<<<<< HEAD
      settleTimer = window.setTimeout(settle, reduced.matches ? 80 : 900);
    } else {
      // A hard ceiling keeps the interaction usable if a smooth-scroll
      // controller is interrupted before it reports completion.
      settleTimer = window.setTimeout(settle, reduced.matches ? 80 : 1100);
=======
      settleTimer = window.setTimeout(settle, reduced.matches ? 80 : 1200);
    } else {
      // A hard ceiling keeps the interaction usable if a smooth-scroll
      // controller is interrupted before it reports completion.
      settleTimer = window.setTimeout(settle, reduced.matches ? 80 : 1500);
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
    }
    return true;
  }

<<<<<<< HEAD
  window.addEventListener("wheel", function (event) {
    if (blocked(event.target) || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
    if (!inPhotoSequence()) { wheelTotal = 0; return; }
=======
  // The figures panel is the last stop. Standing at its top, the wheel
  // still steps back up into the photographs, but a downward turn is the
  // reader leaving the sequence, so it goes to ordinary scrolling.
  function atFactsTop() {
    return !!facts && Math.abs(window.scrollY - topOf(facts)) < 4;
  }

  function armGestureTimer() {
    window.clearTimeout(wheelTimer);
    wheelTimer = window.setTimeout(function () {
      wheelTotal = 0;
      gestureHeld = false;
    }, 180);
  }

  window.addEventListener("wheel", function (event) {
    if (blocked(event.target) || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
    var held = moving || gestureHeld;
    if (!held && atFactsTop() && event.deltaY > 0) { wheelTotal = 0; return; }
    if (!held && !inPhotoSequence() && !atFactsTop()) {
      wheelTotal = 0;
      // Scrolling back up from below with the figures panel still on
      // screen: settle on its top first, so the return into the
      // photographs starts from a chapter rather than halfway through one.
      if (event.deltaY < 0 && facts && window.scrollY > topOf(facts) &&
          window.scrollY < topOf(facts) + window.innerHeight * 0.6) {
        event.preventDefault();
        event.lenisStopPropagation = true;
        if (moveBetween(targets.length - 1, targets.length - 1, -1)) gestureHeld = true;
        armGestureTimer();
      }
      return;
    }
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

    // Own the complete wheel gesture while the photo sequence is active.
    // Otherwise the follow-up events emitted by a trackpad or wheel leak into
    // Lenis during the transition and can carry the page across many panels.
<<<<<<< HEAD
    event.preventDefault();
    if (moving) return;

    wheelTotal += event.deltaY;
    window.clearTimeout(wheelTimer);
    wheelTimer = window.setTimeout(function () { wheelTotal = 0; }, 140);
=======
    // Lenis does not look at defaultPrevented; this is the flag it honours.
    event.preventDefault();
    event.lenisStopPropagation = true;

    // A trackpad keeps sending momentum for a moment after the finger lifts.
    // Hold every gesture that started a move until the wheel has been quiet,
    // so that tail cannot carry the page on into a second chapter.
    armGestureTimer();
    if (moving || gestureHeld) return;

    wheelTotal += event.deltaY;
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
    if (Math.abs(wheelTotal) < 24) return;

    var direction = wheelTotal > 0 ? 1 : -1;
    wheelTotal = 0;
<<<<<<< HEAD
    move(direction);
  }, { passive:false });
=======
    if (move(direction)) gestureHeld = true;
  // Capture, so this runs before Lenis's own listener, which cirs.js
  // registers first; otherwise the flag above arrives too late to matter.
  }, { passive:false, capture:true });
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

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
<<<<<<< HEAD
    if (touchY !== null && !blocked(event.target) && inPhotoSequence()) event.preventDefault();
  }, { passive:false });

  document.addEventListener("keydown", function (event) {
    if (event.defaultPrevented || blocked(event.target) || !inPhotoSequence()) return;
    var direction = 0;
    if (event.key === "PageDown" || event.key === "ArrowDown" || (event.key === " " && !event.shiftKey)) direction = 1;
    if (event.key === "PageUp" || event.key === "ArrowUp" || (event.key === " " && event.shiftKey)) direction = -1;
=======
    if (touchY !== null && !blocked(event.target) && inPhotoSequence()) {
      event.preventDefault();
      event.lenisStopPropagation = true;
    }
  }, { passive:false, capture:true });

  document.addEventListener("keydown", function (event) {
    if (event.defaultPrevented || blocked(event.target)) return;
    var direction = 0;
    if (event.key === "PageDown" || event.key === "ArrowDown" || (event.key === " " && !event.shiftKey)) direction = 1;
    if (event.key === "PageUp" || event.key === "ArrowUp" || (event.key === " " && event.shiftKey)) direction = -1;
    if (!(inPhotoSequence() || (direction < 0 && atFactsTop()))) return;
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
    if (direction) {
      event.preventDefault();
      if (!moving) move(direction);
    }
  });
})();
