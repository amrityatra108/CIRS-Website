/* The cinematic opening two pages share — CIRS Captures and Our Sports.

   Both open the same way, because they are the same page furniture with a
   different film in it: the reader scrubs a short piece of footage with the
   scroll, it ends, it is held, and one thin widely-tracked line arrives over
   the frame it ended on. What differs between them is the file, the words,
   where the line sits and the timing — all of which come from the markup
   that build-site.py generates, not from here.

   The film does not play. The scroll position chooses the frame:

       video.currentTime = progress * video.duration

   and nothing else advances it, so scrolling back runs the camera backwards
   and stopping leaves it on the frame it was on.

   CIRS Captures goes one step further. Once its line has been read, its
   photograph dissolves across the whole frame over the camera's final image.
   The page declares that with data-film-photo and a [data-film-shot]. The
   dissolve follows the scroll position too, so it reverses cleanly and a
   reload halfway through lands on the same composition.

   The section's travel is divided by data-film-phases in the markup:

       [0, FILM_END]            the film, under the scroll
       [FILM_END, HOLD_END]     the last frame, held
       [HOLD_END, TITLE_END]    the line arrives
       [TITLE_END, READ_END]    the line is read
       [READ_END, PHOTO_END]    the photograph dissolves
       [PHOTO_END, 1]          the photograph is held

   For openings without a photograph, READ_END and PHOTO_END are both 1.

   Without phases in the markup, the timing CIRS Captures first established:
   the film to 0.70, held to 0.77, the line in by 0.90.

   Two things make the scrubbing smooth, and neither is in this file.
   Each film is encoded with every frame a keyframe, so a seek never has to
   decode forward from a distant one; and the moov atom is at the front, so
   the browser knows the duration and can seek before the whole file has
   arrived. Re-encoding one any other way is what would make it stutter. The
   stage is held by CSS position:sticky rather than by a GSAP pin, which is
   why a resize or a reload halfway down the page needs nothing from this
   script. */
(function () {
  "use strict";

  var section = document.querySelector("[data-film]");
  if (!section) return;
  var stage = section.querySelector(".film__stage");
  var film = section.querySelector("[data-film-video]");
  var title = section.querySelector("[data-film-title]");
  var shot = section.querySelector("[data-film-shot]");
  var scrollCue = section.querySelector("[data-film-scroll-cue]");
  var photo = shot && shot.querySelector("img");
  var hasStill = section.hasAttribute("data-film-pending");
  var sources = film ? film.querySelectorAll("source") : [];
  var failedSources = 0;
  var fallbackTimer = null;
  var unavailable = false;
  if (!stage || !film || !title) return;

  function numbers(name) {
    return (section.getAttribute(name) || "").trim().split(/\s+/).map(Number);
  }
  var ph = numbers("data-film-phases");
  var FILM_END = ph[0] || 0.70;
  var HOLD_END = ph[1] || 0.77;
  var TITLE_END = ph[2] || 0.90;
  var READ_END = ph[3] || 1;
  var PHOTO_END = ph[4] || 1;
  // The other film openings keep only their video and title.
  var payoff = !!(photo && section.hasAttribute("data-film-photo") && READ_END < PHOTO_END);

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
  var trigger = null;
  var furnished = null; // whether the site's furniture is currently put away
  var written = {};    // the last value of every style this file writes

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function span(p, a, b) { return b > a ? clamp((p - a) / (b - a)) : (p >= b ? 1 : 0); }
  // Slow in and slow out. The line should be noticed; its arrival should not.
  function smooth(t) { return t * t * (3 - 2 * t); }

  // Every style goes through here, so a frame that changes nothing writes
  // nothing, and the photograph's layer is not repainted for no reason.
  function put(el, key, prop, value) {
    if (written[key] === value) return;
    written[key] = value;
    el.style.setProperty(prop, value);
  }

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

  /* The photograph is already the size and crop of the following section.
     A full-frame dissolve leaves the camera's actual final frame visible
     underneath until the photo has completely replaced it. */
  function paintShot(p) {
    if (!payoff) return;
    var dissolve = smooth(span(p, READ_END, PHOTO_END));
    var titleEnd = READ_END + (PHOTO_END - READ_END) * 0.38;
    put(title, "exit", "--film-exit", smooth(span(p, READ_END, titleEnd)).toFixed(3));
    put(shot, "shot-o", "opacity", dissolve.toFixed(3));
  }

  // Our Sports carries one discreet cue over its first frames; it goes as
  // soon as the reader has started.
  function setScrollCue(p) {
    if (!scrollCue) return;
    put(scrollCue, "cue", "--film-scroll-cue-opacity", (1 - smooth(clamp(p / 0.08))).toFixed(3));
  }

  function paint(value) {
    var p = clamp(value);
    seek(p >= FILM_END ? last : (p / FILM_END) * duration);
    var r = span(p, HOLD_END, TITLE_END);
    put(title, "reveal", "--film-reveal", smooth(r).toFixed(4));
    setScrollCue(p);
    paintShot(p);
  }

  /* The composition, without the scrubbing: the film's last frame and the
     line up. assets/css/filmintro.css takes the section back to one screen
     when this is set and leaves any photograph out. A page with a still of
     its last frame (--film-still-image) shows that in place of the film, so
     it needs nothing from the video at all; one without has the film sent to
     its last frame, as soon as the film can be sent anywhere. */
  function still() {
    if (fallbackTimer) { window.clearTimeout(fallbackTimer); fallbackTimer = null; }
    section.setAttribute("data-film-still", "");
    section.removeAttribute("data-film-pending");
    put(title, "reveal", "--film-reveal", "1");
    put(title, "exit", "--film-exit", "0");
    // The page still goes on below the one screen, so a cue stays up.
    setScrollCue(0);
    asked = -1;
    seek(last);
  }

  function teardown() {
    if (trigger) { trigger.kill(); trigger = null; }
    furnished = null;
    document.body.classList.remove("film-on");
  }

  /* Where the reader is, read from the section itself every time rather
     than from ScrollTrigger's own start and end. Those are measured once and
     cached until a refresh, and this site's html carries scroll-behavior:
     smooth, which ScrollTrigger's refresh is documented not to survive: after
     a resize it can measure the section as starting a whole scroll-position
     above where it is, and every frame after that is drawn for the wrong
     place. The live rectangle cannot be stale. The travel is the section's
     height less the stage's, because that is how far the stage is actually
     held — the stage is 100svh, which on a phone is not the window's height
     while the address bar is away. */
  function where() {
    var box = section.getBoundingClientRect();
    var held = stage.offsetHeight || window.innerHeight;
    var travel = box.height - held;
    return {
      p: travel > 0 ? clamp(-box.top / travel) : 0,
      // The reading rule and the back-to-top button stay away while any of
      // the opening is on screen: through the final hold, and for the screen
      // after it as the stage scrolls off.
      on: box.top < 0 && box.bottom > 0
    };
  }

  function update() {
    var w = where();
    paint(w.p);
    if (w.on !== furnished) {
      furnished = w.on;
      document.body.classList.toggle("film-on", w.on);
    }
  }

  function scrub() {
    if (trigger || !hasST || reduced.matches) return;
    section.removeAttribute("data-film-still");
    /* ScrollTrigger is kept only as the signal that the page has moved: it is
       what Lenis, the site's smooth scrolling, reports to. With no trigger
       element it spans the whole page, so it has no measured range to go
       stale. */
    trigger = ScrollTrigger.create({
      onUpdate: update,
      onRefresh: update
    });
    update();
  }

  /* The opening starts at once. It does not wait for the film: the line and
     the photograph are drawn from the scroll position alone, and the film
     joins in when its metadata arrives. */
  function start() {
    if (unavailable) return;
    if (reduced.matches || !hasST) { still(); return; }
    if (film.error) { fallback(); return; }
    /* The film begins loading while the page is still being parsed, before
       this deferred script runs, so if every source has already failed, the
       errors fired with nobody listening. networkState then reads
       NETWORK_NO_SOURCE — but it also reads that for a moment at the start of
       an ordinary load, so it cannot be taken as failure on its own. Loading
       again settles it: a film that really is missing fails again, now with
       the listener above attached; one that was merely starting just starts. */
    if (film.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) film.load();
    scrub();
    if (!frames()) {
      if (hasStill && !fallbackTimer) {
        fallbackTimer = window.setTimeout(fallback, 5000);
      }
      return;
    }
    if (fallbackTimer) { window.clearTimeout(fallbackTimer); fallbackTimer = null; }
    section.removeAttribute("data-film-pending");
    update();
  }

  film.addEventListener("loadedmetadata", function () {
    asked = -1;
    start();
  });
  if (film.readyState >= 1) frames();

  /* Without the film there is no opening to scrub, so the still takes its
     place. A <video> with <source> children reports a failed file on the
     <source>, and that error does not bubble — which is why this listens in
     the capture phase — and a failure on one source is only a failure of the
     video once the last one has failed too, which networkState then says. */
  function failed() {
    return !!film.error || film.networkState === HTMLMediaElement.NETWORK_NO_SOURCE;
  }
  function fallback() {
    if (unavailable) return;
    unavailable = true;
    teardown();
    section.setAttribute("data-film-still", "");
    section.removeAttribute("data-film-pending");
    put(title, "reveal", "--film-reveal", "1");
    put(title, "exit", "--film-exit", "0");
    if (scrollCue) put(scrollCue, "cue", "--film-scroll-cue-opacity", "0");
    asked = -1;
    seek(last);
    if (fallbackTimer) { window.clearTimeout(fallbackTimer); fallbackTimer = null; }
  }

  sources.forEach(function (source) {
    source.addEventListener("error", function () {
      failedSources += 1;
      if (hasStill && failedSources === sources.length) fallback();
    });
  });
  film.addEventListener("error", function () {
    setTimeout(function () {
      if (failed()) fallback();
    }, 0);
  }, true);

  /* A resize can change the scroll position and swap the photograph's cut,
     so repaint straight away rather than waiting for ScrollTrigger. */
  window.addEventListener("resize", function () {
    if (trigger) update();
  }, { passive: true });

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
        if (trigger) update();
      }).catch(function () { /* No decoder; the poster is the fallback. */ });
    }
  }
  window.addEventListener("touchstart", unlock, { passive: true, once: true });

  reduced.addEventListener("change", function () {
    if (unavailable) return;
    if (reduced.matches) { teardown(); still(); }
    else { section.removeAttribute("data-film-still"); written = {}; start(); }
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

  start();
}());
