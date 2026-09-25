/* CIRS Captures — the featured photographs.

   The opening ends with a photograph filling the window. This section is
   laid over the opening's last screen and stays invisible until its own
   held stage reaches the top of the window — the scroll position at which
   the opening's stage would begin to leave — and there it shows the same
   photograph at the same crop. So the photograph stays, and the page goes
   on from it:

       rest     the photograph, full-screen, with its caption
       move     it settles into a tall panel; the next photograph arrives
       hold     the pair
       change   the pair gives way to the portrait
       hold     the portrait
        change   the portrait gives way to a bird amid pink blossoms
       hold     and the stage is let go, into the gallery

   The lengths are in the markup (data-cf-phases, in vh of scroll) and in
   assets/css/captures-featured.css (--cf-travel, their sum). Everything is
   drawn from the scroll position, as the opening is, so it runs backwards
   exactly as it runs forwards and a fast scroll lands on the right frame.

   The move is the one change of size, and it happens once. The changes
   after it are the same each time: the frame going is carried up out of
   the stage as the next is carried up into it, on one eased movement.

   None of this runs where the opening itself is a still — reduced motion,
   a film that has failed, no ScrollTrigger — because there is then no
   photograph on screen to take over from. The frames are then three still
   screens, which is how they are written. */
(function () {
  "use strict";

  var section = document.querySelector("[data-cf]");
  var cap = document.querySelector("[data-film]");
  if (!section || !cap) return;

  var stage = section.querySelector("[data-cf-stage]");
  var lead = section.querySelector("[data-cf-lead]");
  var restcap = section.querySelector("[data-cf-restcap]");
  var slot = section.querySelector("[data-cf-slot]");
  var frames = section.querySelectorAll("[data-cf-frame]");
  var pair = frames[0], portrait = frames[1], band = frames[2];
  var enter = pair.querySelector("[data-cf-enter]");
  var pairCaps = pair.querySelectorAll("figcaption");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  // Phase boundaries as fractions of the travel.
  var lengths = section.getAttribute("data-cf-phases").split(/\s+/).map(Number);
  var sum = lengths.reduce(function (a, b) { return a + b; }, 0);
  var at = [0];
  lengths.forEach(function (l, i) { at.push(at[i] + l / sum); });

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function span(p, a, b) { return clamp((p - a) / (b - a)); }
  function smooth(t) { return t * t * (3 - 2 * t); }
  function smoother(t) { return t * t * t * (t * (t * 6 - 15) + 10); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  // Only what has changed is written.
  var written = {};
  function put(el, key, prop, value) {
    if (written[key] === value) return;
    written[key] = value;
    el.style.setProperty(prop, value);
  }

  // Where the lead photo's panel is in the stage. Offsets rather than
  // rectangles, so that the frame's own drift never moves the target.
  var geo = null;
  function measure() {
    var x = 0, y = 0, el = slot;
    while (el && el !== stage) { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; }
    return { w: stage.clientWidth, h: stage.clientHeight,
             slot: { x: x, y: y, w: slot.offsetWidth, h: slot.offsetHeight } };
  }

  function layer(el, key, opacity, shift) {
    put(el, key + "o", "opacity", opacity.toFixed(3));
    put(el, key + "t", "transform", shift ? "translate3d(0," + shift.toFixed(1) + "px,0)" : "none");
  }

  function paint(p) {
    if (!geo) geo = measure();
    var H = geo.h, rise = 0.03 * H;

    var rest = span(p, at[0], at[1]);
    var move = span(p, at[1], at[2]);
    var toPortrait = span(p, at[3], at[4]);
    var toBand = span(p, at[5], at[6]);

    // Rest: the caption comes up once the photograph has settled.
    put(restcap, "rc", "opacity",
        (smooth(clamp(rest / 0.4)) * (1 - smooth(clamp(move / 0.25)))).toFixed(3));

    // Move: the photograph's box goes from the whole stage to its panel.
    var u = smoother(move), s = geo.slot;
    put(lead, "ll", "left", lerp(0, s.x, u).toFixed(2) + "px");
    put(lead, "lt", "top", lerp(0, s.y, u).toFixed(2) + "px");
    put(lead, "lw", "width", lerp(geo.w, s.w, u).toFixed(2) + "px");
    put(lead, "lh", "height", lerp(H, s.h, u).toFixed(2) + "px");
    put(lead, "lf", "--cf-foot", (1 - smooth(clamp(move / 0.5))).toFixed(3));
    var companion = smooth(span(move, 0.35, 1));
    layer(enter, "k", companion, (1 - companion) * rise);
    var caps = smooth(span(move, 0.7, 1)).toFixed(3);
    for (var i = 0; i < pairCaps.length; i++) put(pairCaps[i], "pc" + i, "opacity", caps);

    // The pair gives way to the portrait, and the portrait to the wide photo:
    // the frame going is carried up and out of the stage as the next is
    // carried up into it, both whole, on one eased movement. Wherever the
    // reader stops there are photographs on the stage — never an empty
    // frame, and never two laid over each other.
    var u2 = smoother(toPortrait), u3 = smoother(toBand);
    layer(pair, "f1", 1, -H * u2);
    layer(lead, "lx", 1, -H * u2);
    layer(portrait, "f2", 1, H * (1 - u2) - H * u3);
    layer(band, "f3", 1, H * (1 - u3));
  }

  var pinned = false, live = null, trigger = null;

  function update() {
    if (!pinned) return;
    var box = section.getBoundingClientRect();
    var held = stage.offsetHeight || window.innerHeight;
    var travel = box.height - held;
    paint(travel > 0 ? clamp(-box.top / travel) : 0);
    var on = box.top <= 0.5 && box.bottom > 0;
    if (on !== live) {
      live = on;
      section.classList.toggle("is-live", on);
      document.body.classList.toggle("cf-on", on);
    }
  }

  function clear() {
    written = {};
    [lead, restcap, pair, portrait, band, enter].concat(Array.prototype.slice.call(pairCaps))
      .forEach(function (el) { el.removeAttribute("style"); });
  }

  // Fetch every picture here as soon as the section is anywhere near, so
  // that nothing is still arriving when its frame comes up; and decode the
  // lead photograph ahead of time, because it must already be there on the
  // first frame, exactly as the opening leaves it.
  function prefetch() {
    Array.prototype.forEach.call(section.querySelectorAll("img"), function (img) {
      img.loading = "eager";
    });
    var first = lead.querySelector("img");
    if (first && first.decode) first.decode().catch(function () {});
  }
  if ("IntersectionObserver" in window) {
    var near = new IntersectionObserver(function (entries) {
      if (entries.some(function (e) { return e.isIntersecting; })) { prefetch(); near.disconnect(); }
    }, { rootMargin: "300% 0px" });
    near.observe(section);
  } else {
    prefetch();
  }

  function mode() {
    var want = !reduced.matches && !cap.hasAttribute("data-film-still") &&
               typeof window.ScrollTrigger !== "undefined" &&
               !!(window.CSS && CSS.supports && CSS.supports("container-type", "size"));
    if (want === pinned) return;
    pinned = want;
    section.classList.toggle("cf--pinned", want);
    clear();
    geo = null;
    live = null;
    if (want) {
      if (!trigger) trigger = ScrollTrigger.create({ onUpdate: update, onRefresh: function () { geo = null; update(); } });
      update();
    } else {
      section.classList.remove("is-live");
      document.body.classList.remove("cf-on");
    }
  }

  // The opening decides, as it goes, whether it is a still; follow it.
  new MutationObserver(mode).observe(cap, { attributes: true, attributeFilter: ["data-film-still"] });
  reduced.addEventListener("change", mode);
  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", function () { geo = null; update(); });
  mode();
})();
