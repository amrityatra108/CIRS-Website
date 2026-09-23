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

   CIRS Captures goes one step further. Once its line has been read, a
   photograph from the school appears inside the camera's lens and opens out
   of it to fill the window; the page declares that with data-film-lens and
   a [data-film-shot], and without them none of it runs. Every part of it is
   a function of the scroll position too — nothing here is a tween with a
   duration of its own — so any scroll position, reached slowly or in one
   jump, backwards or forwards, has exactly one picture, and a reload or a
   resize halfway through lands on it.

   The section's travel is divided by data-film-phases in the markup:

       [0, FILM_END]            the film, under the scroll
       [FILM_END, HOLD_END]     the last frame, held
       [HOLD_END, TITLE_END]    the line arrives
       [TITLE_END, READ_END]    the line is read        } CIRS Captures only;
       [READ_END, LENS_END]     the photograph, in lens } without a lens these
       [LENS_END, OPEN_END]     it opens to the window  } are all at 1, and the
       [OPEN_END, 1]            the photograph is held  } composition is held

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
  if (!stage || !film || !title) return;

  function numbers(name) {
    return (section.getAttribute(name) || "").trim().split(/\s+/).map(Number);
  }
  var ph = numbers("data-film-phases");
  var FILM_END = ph[0] || 0.70;
  var HOLD_END = ph[1] || 0.77;
  var TITLE_END = ph[2] || 0.90;
  var READ_END = ph[3] || 1;
  var LENS_END = ph[4] || 1;
  var OPEN_END = ph[5] || 1;
  // No lens in the markup, or no photograph: the opening is the film and the
  // line, exactly as it was before the photograph was added.
  var LENS = numbers("data-film-lens");
  var payoff = !!(photo && LENS.length === 5 && READ_END < 1);

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
  var progress = 0;    // the last position painted, for repainting on resize
  var written = {};    // the last value of every style this file writes

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function span(p, a, b) { return b > a ? clamp((p - a) / (b - a)) : (p >= b ? 1 : 0); }
  // Slow in and slow out. The line should be noticed; its arrival should not.
  function smooth(t) { return t * t * (3 - 2 * t); }
  function lerp(a, b, t) { return a + (b - a) * t; }

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

  /* ---- The lens ---------------------------------------------------------

     The lens's front rim is an ellipse in the film's own pixels. On screen it
     is wherever object-fit:cover puts it, which depends on the shape of the
     window and on the film's object-position — so both are read from the
     page rather than assumed, and the geometry is worked out again whenever
     the window changes size.

     The photograph fills the stage the same way, and its object-position is
     the point in it that the opening treats as its subject: with cover, the
     point at x%/y% of the picture always lands at x%/y% of the window, so
     that point on screen is known without knowing how large the file is.

     While the photograph is small, it is drawn scaled down about that point
     and moved so the point sits on the lens, and clipped to the lens's own
     ellipse. The clip is in the photograph's own coordinates, so it is
     always inside the picture's edges; what grows first is the picture, and
     the opening in it only grows past the picture's edges once the picture
     itself is the size of the window, when those edges are the window's. */
  var geo = null;

  function percentages(value) {
    var parts = String(value).split(/\s+/);
    var x = parseFloat(parts[0]), y = parseFloat(parts[1]);
    return [isNaN(x) ? 0.5 : x / 100, isNaN(y) ? 0.5 : y / 100];
  }

  function halfBox(a, b, t) {
    var c = Math.cos(t), s = Math.sin(t);
    return [Math.sqrt(a * a * c * c + b * b * s * s),
            Math.sqrt(a * a * s * s + b * b * c * c)];
  }

  function measure() {
    var box = stage.getBoundingClientRect();
    var W = box.width, H = box.height;
    if (!W || !H) return null;
    var fw = Number(film.getAttribute("width")) || 1280;
    var fh = Number(film.getAttribute("height")) || 720;
    var crop = percentages(getComputedStyle(film).objectPosition);
    var focus = percentages(getComputedStyle(photo).objectPosition);
    var s = Math.max(W / fw, H / fh);
    var g = {
      W: W, H: H,
      lx: (W - fw * s) * crop[0] + LENS[0] * s,
      ly: (H - fh * s) * crop[1] + LENS[1] * s,
      a0: LENS[2] * s, b0: LENS[3] * s, t0: LENS[4] * Math.PI / 180,
      fx: focus[0] * W, fy: focus[1] * H
    };
    // How far the subject is from the nearest edge of the picture, each way.
    var dx = Math.min(g.fx, W - g.fx), dy = Math.min(g.fy, H - g.fy);
    var half = halfBox(g.a0, g.b0, g.t0);
    /* k0 is how small the photograph is while it sits in the lens: small
       enough that the lens shows most of the picture around its subject, and
       no smaller than keeps a margin of the picture outside the lens on every
       side (MARGIN), so the rim never shows the picture's own edge. */
    var MARGIN = 1.12;
    g.k0 = Math.min(0.95, MARGIN * Math.max(half[0] / dx, half[1] / dy));
    // The circle, centred on the subject, that covers every corner.
    g.cover = 1.02 * Math.sqrt(Math.pow(Math.max(g.fx, W - g.fx), 2) +
                               Math.pow(Math.max(g.fy, H - g.fy), 2));
    g.grow = g.cover / Math.min(g.a0, g.b0);
    /* The picture grows first and the opening in it follows; handing the
       growth from one to the other is eased over a short span (soft) so the
       picture settles at full size rather than stopping dead. The span is as
       long as it can be while the opening stays inside the picture's edges. */
    var room = Math.log(0.99 * MARGIN);
    g.soft = Math.max(0.02, Math.min(0.25, 0.9 * room / -Math.log(g.k0)));
    g.key = W + "x" + H;
    return g;
  }

  function ellipsePath(cx, cy, a, b, t) {
    var c = Math.cos(t), s = Math.sin(t), d = (t * 180 / Math.PI).toFixed(3);
    var x1 = (cx + a * c).toFixed(2), y1 = (cy + a * s).toFixed(2);
    var x2 = (cx - a * c).toFixed(2), y2 = (cy - a * s).toFixed(2);
    var r = a.toFixed(2) + " " + b.toFixed(2) + " " + d;
    return 'path("M ' + x1 + " " + y1 + " A " + r + " 1 0 " + x2 + " " + y2 +
           " A " + r + " 1 0 " + x1 + " " + y1 + ' Z")';
  }

  /* e is how far the photograph has opened, 0 in the lens to 1 at the whole
     window. The opening's size on screen is one smooth curve over all of it;
     how that growth is divided between the picture and the opening in it is
     what keeps the picture's edges out of sight. */
  function openTo(g, e) {
    var ease = e * e * e * (e * (e * 6 - 15) + 10);        // smootherstep
    var lnG = Math.log(g.grow) * ease;                       // screen growth
    var x = lnG / -Math.log(g.k0);                           // 1 = picture full size
    var d = g.soft, kp;
    if (x <= 1 - d) kp = x;
    else if (x >= 1 + d) kp = 1;
    else kp = x - (x - (1 - d)) * (x - (1 - d)) / (4 * d);
    var k = Math.pow(g.k0, 1 - kp);
    var px = lerp(g.lx, g.fx, kp), py = lerp(g.ly, g.fy, kp);
    /* The opening on screen. Once the picture is full size it rounds out and
       straightens as it grows, so what finally covers the window is a
       circle; before that it keeps the lens's own shape and tilt. */
    // Measured from the moment the picture reached full size, so the shape
    // starts changing from exactly the lens's shape rather than jumping.
    var lnFull = (1 + d) * -Math.log(g.k0);
    var round = kp >= 1 ? clamp((lnG - lnFull) / (Math.log(g.grow) - lnFull)) : 0;
    var aspect = Math.pow(g.a0 / g.b0, round);
    var growth = Math.exp(lnG);
    var sa = g.a0 * growth, sb = g.b0 * growth;
    if (g.a0 < g.b0) sb *= aspect; else sa /= aspect;
    var tilt = g.t0 * (1 - round);
    return { k: k, x: px - k * g.fx, y: py - k * g.fy,
             a: sa / k, b: sb / k, t: tilt, full: e >= 1 };
  }

  function paintShot(p) {
    if (!payoff) return;
    if (!geo) geo = measure();
    var g = geo;
    if (!g) return;
    var inLens = span(p, READ_END, LENS_END);
    var e = span(p, LENS_END, OPEN_END);
    var o = openTo(g, e);
    put(shot, "shot-o", "opacity", smooth(inLens).toFixed(3));
    if (o.full) {
      put(shot, "shot-t", "transform", "none");
      put(shot, "shot-c", "clip-path", "none");
    } else {
      put(shot, "shot-t", "transform", "translate(" + o.x.toFixed(2) + "px, " +
          o.y.toFixed(2) + "px) scale(" + o.k.toFixed(5) + ")");
      put(shot, "shot-c", "clip-path", ellipsePath(g.fx, g.fy, o.a, o.b, o.t));
    }
    // The glass: darker at the rim inside the lens, gone by halfway out.
    var glass = 1 - smooth(clamp(e / 0.45));
    put(shot, "glass", "--film-glass", (0.85 * glass).toFixed(3));
    put(shot, "glass-x", "--film-glass-x", (o.a * 1.05).toFixed(1) + "px");
    put(shot, "glass-y", "--film-glass-y", (o.b * 1.05).toFixed(1) + "px");
    put(shot, "glass-cx", "--film-glass-cx", g.fx.toFixed(1) + "px");
    put(shot, "glass-cy", "--film-glass-cy", g.fy.toFixed(1) + "px");
    // The camera and the line leave inside the same movement: the line fades
    // before the opening can reach it, and the camera leans toward the lens.
    put(title, "exit", "--film-exit", smooth(clamp(e / 0.3)).toFixed(3));
    put(film, "lens-x", "--film-lens-x", g.lx.toFixed(1) + "px");
    put(film, "lens-y", "--film-lens-y", g.ly.toFixed(1) + "px");
    put(film, "push", "--film-push", (1 + 0.06 * smooth(e)).toFixed(4));
  }

  // Our Sports carries one discreet cue over its first frames; it goes as
  // soon as the reader has started.
  function setScrollCue(p) {
    if (!scrollCue) return;
    put(scrollCue, "cue", "--film-scroll-cue-opacity", (1 - smooth(clamp(p / 0.08))).toFixed(3));
  }

  function paint(value) {
    var p = clamp(value);
    progress = p;
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
    section.setAttribute("data-film-still", "");
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
      onRefresh: function () { geo = null; update(); }
    });
    update();
  }

  /* The opening starts at once. It does not wait for the film: the line and
     the photograph are drawn from the scroll position alone, and the film
     joins in when its metadata arrives. */
  function start() {
    if (reduced.matches || !hasST || film.error) { still(); return; }
    /* The film begins loading while the page is still being parsed, before
       this deferred script runs, so if every source has already failed, the
       errors fired with nobody listening. networkState then reads
       NETWORK_NO_SOURCE — but it also reads that for a moment at the start of
       an ordinary load, so it cannot be taken as failure on its own. Loading
       again settles it: a film that really is missing fails again, now with
       the listener above attached; one that was merely starting just starts. */
    if (film.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) film.load();
    scrub();
  }

  film.addEventListener("loadedmetadata", function () {
    if (!frames()) return;
    asked = -1;
    if (trigger) paint(progress);
    else if (section.hasAttribute("data-film-still")) seek(last);
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
  film.addEventListener("error", function () {
    setTimeout(function () {
      if (failed()) { teardown(); still(); }
    }, 0);
  }, true);


  /* A change of window shape can move the lens (the film's crop changes at
     6:5) and swap the photograph's cut, so the geometry is taken again and
     the current position repainted straight away, rather than waiting for
     ScrollTrigger's own refresh a moment later. */
  window.addEventListener("resize", function () {
    geo = null;
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
        if (trigger) paint(progress);
      }).catch(function () { /* No decoder; the poster is the fallback. */ });
    }
  }
  window.addEventListener("touchstart", unlock, { passive: true, once: true });

  reduced.addEventListener("change", function () {
    if (reduced.matches) { teardown(); still(); }
    else { section.removeAttribute("data-film-still"); written = {}; scrub(); }
  });

  // A trigger left registered across a back-forward-cache restore is one
  // measuring a page that has since moved, so it goes on the way out and is
  // built again on the way back in.
  window.addEventListener("pagehide", teardown);
  window.addEventListener("pageshow", function (event) {
    if (!event.persisted) return;
    asked = -1;
    geo = null;
    start();
  });

  start();
}());
