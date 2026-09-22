/* The cinematic opening two pages share — CIRS Captures and Our Sports.

   Both open the same way, because they are the same page furniture with a
   different film in it: the reader scrubs a short piece of footage with the
   scroll, it ends, it is held, and one thin widely-tracked line arrives over
   the frame it ended on. What differs between them is the file, the words,
   and where the line sits — all of which come from the markup that
   build-site.py generates, not from here.

   The film does not play. The scroll position chooses the frame:

       video.currentTime = progress * video.duration

   and nothing else advances it, so scrolling back runs the camera backwards
   and stopping leaves it on the frame it was on. The section's travel is
   divided into four phases, the last three of which the film has no part in:
   it ends at 0.70, is held frozen to 0.77, the line arrives by 0.90, and the
   finished composition is held to the end.

   Two things make the scrubbing smooth, and neither is in this file.
   Each film is encoded with every frame a keyframe,
   so a seek never has to decode forward from a distant one; and the moov
   atom is at the front, so the browser knows the duration and can seek
   before the whole file has arrived. Re-encoding it any other way is what
   would make this stutter. The stage is held by CSS position:sticky rather
   than by a GSAP pin, which is why a resize or a reload halfway down the
   page needs nothing from this script. */
(function () {
  "use strict";

  var section = document.querySelector("[data-film]");
  if (!section) return;
  var film = section.querySelector("[data-film-video]");
  var title = section.querySelector("[data-film-title]");
  if (!film || !title) return;

  /* The phase boundaries, as fractions of the section's travel, and the
     length of one frame of the file. Both are stated in the markup so a page
     can keep its own timing, and both fall back to what CIRS Captures
     established: the film to 0.70, held to 0.77, the line out by 0.90. */
  var phases = (section.getAttribute("data-film-phases") || "").split(/\s+/).map(Number);
  var FILM_END = phases[0] > 0 ? phases[0] : 0.70;
  var HOLD_END = phases[1] > 0 ? phases[1] : 0.77;
  var TITLE_END = phases[2] > 0 ? phases[2] : 0.90;

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var hasST = typeof window.gsap !== "undefined" &&
              typeof window.ScrollTrigger !== "undefined";

  var duration = 0;
  var last = 0;        // the timestamp that lands on the final frame
  // One frame of the film. The files are ours and are encoded at 24fps, and
  // HTMLVideoElement will not report a frame rate, so it is stated in the
  // markup rather than guessed at from playback.
  var step = 1 / (Number(section.getAttribute("data-film-fps")) || 24);
  var asked = -1;      // the last time the decoder was sent to
  var reveal = -1;     // the last value written to the stylesheet
  var trigger = null;
  var furniture = null;

  /* Seeking to exactly duration is the one value that is not a frame: some
     browsers treat it as the end and hand back the first frame, or fire
     "ended". Stop a fraction short and the last frame is what stays up. */
  function frames() {
    duration = film.duration;
    if (!duration || !isFinite(duration)) return false;
    last = Math.max(0, duration - Math.min(0.03, duration / 2));
    return true;
  }

  function seek(time) {
    if (!duration) return;
    var t = time < 0 ? 0 : time > last ? last : time;
    // Anything finer than half a frame cannot be seen, and asking for it
    // only queues work the decoder will throw away.
    if (asked >= 0 && Math.abs(t - asked) < step * 0.5) return;
    asked = t;
    try { film.currentTime = t; } catch (error) { asked = -1; }
  }

  function setReveal(value) {
    if (Math.abs(value - reveal) < 0.001) return;
    reveal = value;
    title.style.setProperty("--film-reveal", value.toFixed(4));
  }

  // Slow in and slow out. The line should be noticed; its arrival should not.
  function smooth(t) { return t * t * (3 - 2 * t); }

  function paint(progress) {
    var p = progress < 0 ? 0 : progress > 1 ? 1 : progress;
    seek(p >= FILM_END ? last : (p / FILM_END) * duration);
    var r = (p - HOLD_END) / (TITLE_END - HOLD_END);
    setReveal(r <= 0 ? 0 : r >= 1 ? 1 : smooth(r));
  }

  /* The composition, without the scrubbing: the camera as the film leaves
     it and the line already up. assets/css/captures.css takes the section
     back to one screen when this is set, so nobody is asked to scroll four
     screens through something that is no longer moving. */
  function still() {
    section.setAttribute("data-film-still", "");
    setReveal(1);
    asked = -1;
    seek(last);
  }

  function teardown() {
    if (trigger) { trigger.kill(); trigger = null; }
    if (furniture) { furniture.kill(); furniture = null; }
    document.body.classList.remove("film-on");
  }

  function scrub() {
    if (trigger || !hasST || reduced.matches) return;
    section.removeAttribute("data-film-still");
    trigger = ScrollTrigger.create({
      trigger: section,
      start: "top top",
      end: "bottom bottom",
      onUpdate: function (self) { paint(self.progress); },
      onRefresh: function (self) { paint(self.progress); },
    });
    /* A second trigger, only to say whether the opening is on screen, because
       it ends later than the first one does: the stage is still stuck to the
       window through the final hold and for a screen after it, and the
       reading rule and the back-to-top button cannot come back over the
       finished composition. */
    furniture = ScrollTrigger.create({
      trigger: section,
      start: "top top",
      end: "bottom top",
      onToggle: function (self) {
        document.body.classList.toggle("film-on", self.isActive);
      },
      onRefresh: function (self) {
        document.body.classList.toggle("film-on", self.isActive);
      }
    });
    paint(trigger.progress);
  }

  function start() {
    if (!frames()) return;
    if (reduced.matches || !hasST) { still(); return; }
    if (trigger) paint(trigger.progress);
    else scrub();
  }

  if (film.readyState >= 1) start();
  film.addEventListener("loadedmetadata", start);
  // Without the file there is no opening to scrub. Leave the section at one
  // screen with the line up, rather than four screens of nothing.
  film.addEventListener("error", function () {
    teardown();
    section.setAttribute("data-film-still", "");
    setReveal(1);
  });

  /* iOS will not paint a frame of a video that has never been told to play,
     so a seek alone leaves the poster up. One muted play, stopped as soon as
     it has started, is enough to get a decoder. It is not the film playing:
     the next paint puts it straight back on the frame the scroll chose, and
     this only ever happens under the reader's own finger. */
  var unlocked = false;
  function unlock() {
    if (unlocked || reduced.matches) return;
    unlocked = true;
    var playing = film.play();
    if (playing && playing.then) {
      playing.then(function () {
        film.pause();
        asked = -1;
        if (trigger) paint(trigger.progress);
      }).catch(function () { /* No decoder; the poster is the fallback. */ });
    }
  }
  window.addEventListener("touchstart", unlock, { passive: true, once: true });

  reduced.addEventListener("change", function () {
    if (reduced.matches) { teardown(); start(); }
    else { section.removeAttribute("data-film-still"); scrub(); start(); }
  });

  // A trigger left registered across a back-forward-cache restore is one
  // measuring a page that has since moved, so it goes on the way out and is
  // built again on the way back in.
  window.addEventListener("pagehide", teardown);
  window.addEventListener("pageshow", function (event) {
    if (!event.persisted) return;
    asked = -1;
    start();
  });
}());
