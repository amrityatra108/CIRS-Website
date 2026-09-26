/* Our Houses — the journey through the four identities.
 *
 * Six pieces, each of which stands down on its own if what it needs is not
 * there. Nothing here is required for the page to be readable, and that is
 * the design rather than a nicety:
 *
 *   1. the opening frame   which house is live, and the pointer depth
 *   2. the release         the live house's colour filling the window as
 *                          the hero is scrolled past
 *   3. the chapter wipes   the outgoing colour contracting to a stripe and
 *                          opening into the incoming one
 *   4. the march           the horizontal run, and the names behind it
 *   5. the competition     the season line, one event at a time
 *   6. the gallery         expand a frame, filter by house, arrow keys
 *
 * The opening interaction itself is CSS — :has() expands the hovered or
 * focused zone — so a visitor can use this page with the script blocked. What
 * 1 adds on top is the pointer depth and a live house that survives the mouse
 * leaving, which is what the release in 2 needs.
 *
 * Pinning is position:sticky in assets/css/houses.css and nothing else, for
 * the reason cirs.css records: ScrollTrigger's own pin rewrites the document
 * with a spacer, which on this site fights Lenis and moves the boundary the
 * header's probe watches. ScrollTrigger is used here only to read progress.
 *
 * EVERYTHING WIDTH-DEPENDENT GOES THROUGH gsap.matchMedia().
 * ----------------------------------------------------------------------
 * This was first written as `if (wide.matches) { ... }` around the setup, and
 * it was wrong in a way that only showed up under test: the query is read
 * once, when the script runs, so a window that is narrow at that moment and
 * wide a second later — a pane still laying out, a phone turned on its side,
 * anyone dragging a window edge — never gets the desktop behaviour, and a
 * window that goes the other way keeps a pinned hero at 480px. matchMedia
 * builds each context when it becomes true and REVERTS everything it set when
 * it stops being true, including the inline styles, so resizing across the
 * breakpoint lands in a clean state in both directions. It also makes the
 * reduced-motion branch a context rather than a load-time decision, so the
 * page follows the setting being changed.
 */
(function () {
  "use strict";

  var root = document.body;
  if (!root.classList.contains("houses")) return;

  var gsap = window.gsap;
  var ScrollTrigger = window.ScrollTrigger;
  if (gsap && ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

  var reduced = matchMedia("(prefers-reduced-motion: reduce)");

  function all(sel, from) {
    return Array.prototype.slice.call((from || document).querySelectorAll(sel));
  }
  function one(sel, from) { return (from || document).querySelector(sel); }

  var hero = one("[data-houses-hero]");
  var zones = all("[data-houses-zone]");
  var fill = one("[data-houses-fill]");
  var title = one("[data-houses-title]");

  /* The live house is what the release fills the window with. It starts as
     the first house, so a visitor who scrolls without touching anything still
     gets a deterministic order — Vasishtha, then the rest — rather than
     nothing at all. */
  var live = zones.length ? zones[0] : null;
  if (fill && live) fill.setAttribute("data-house", live.getAttribute("data-house"));

  function setLive(zone) {
    if (!zone) return;
    live = zone;
    zones.forEach(function (z) { z.classList.toggle("is-live", z === live); });
    if (fill) fill.setAttribute("data-house", live.getAttribute("data-house"));
  }

  /* A zone is a link to its chapter. Following it should leave that house
     live, so the chapter a reader lands in is the one the hero was showing.
     Outside every context: it is navigation, not motion. */
  zones.forEach(function (zone) {
    zone.addEventListener("click", function () { setLive(zone); });
  });

  /* ==========================================================
     5. Inter-house competition
     ----------------------------------------------------------
     Not in a context: this is behaviour, not motion, and it is
     wanted at every width and under reduced motion.

     The panels are all on the page and all open. This collapses
     them to one at a time and lights the matching stop, and it
     only does so after it has run: is-driven is added here, so
     the no-script page is the full archive rather than a single
     event with seven hidden behind a control that does nothing.
     ========================================================== */
  (function competition() {
    var track = one("[data-houses-track]");
    var panels = all("[data-houses-panel]");
    var stops = all("[data-houses-stop]");
    var lineFill = one("[data-houses-line]");
    var list = one("[data-houses-panels]");
    if (!track || !list || !panels.length || !stops.length) return;

    list.classList.add("is-driven");

    function show(index) {
      stops.forEach(function (stop, i) {
        var on = i === index;
        stop.classList.toggle("is-on", on);
        stop.setAttribute("aria-current", on ? "true" : "false");
      });
      panels.forEach(function (panel, i) {
        panel.classList.toggle("is-on", i === index);
      });
      if (!lineFill) return;
      var visible = stops.filter(function (s) { return !s.parentNode.hidden; });
      var at = visible.indexOf(stops[index]);
      var of = Math.max(1, visible.length - 1);
      lineFill.style.width = (at <= 0 ? 0 : (at / of) * 100) + "%";
      // The line takes the colour of the house that won the event it has
      // reached — and gives that colour up again when it reaches one that was
      // never placed. Two of these events have no published placings at all
      // (the house symposiums, and the 2025-2026 aquatic meet), and leaving
      // the previous winner's colour on the line through them showed a house
      // colour against a result this page is explicit about not having. The
      // line falls back to var(--dark) with no house attribute set.
      var first = one("[data-house]", panels[index]);
      if (first) lineFill.setAttribute("data-house", first.getAttribute("data-house"));
      else lineFill.removeAttribute("data-house");
    }

    stops.forEach(function (stop, i) {
      stop.addEventListener("click", function () { show(i); });
      // Left and right walk the season line, which is what a line of stops
      // invites and what a row of buttons does not give on its own.
      stop.addEventListener("keydown", function (event) {
        var step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
        if (!step) return;
        event.preventDefault();
        var open = stops.filter(function (s) { return !s.parentNode.hidden; });
        var at = open.indexOf(stop);
        var next = open[Math.min(open.length - 1, Math.max(0, at + step))];
        if (next) { next.focus(); show(stops.indexOf(next)); }
      });
    });

    all("[data-houses-filter]").forEach(function (button) {
      button.addEventListener("click", function () {
        var want = button.getAttribute("data-houses-filter");
        all("[data-houses-filter]").forEach(function (b) {
          var on = b === button;
          b.classList.toggle("is-on", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        var firstVisible = -1;
        stops.forEach(function (stop, i) {
          var keep = want === "All" || stop.getAttribute("data-cat") === want;
          stop.parentNode.hidden = !keep;
          panels[i].hidden = !keep;
          if (keep && firstVisible < 0) firstVisible = i;
        });
        if (firstVisible >= 0) show(firstVisible);
      });
    });

    show(0);
    // Until the event handlers exist, the full archive is readable below and
    // the controls stay out of both the visual and keyboard flow.
    track.hidden = false;
  })();

  /* ==========================================================
     6. The gallery
     ----------------------------------------------------------
     Also not in a context, and for the same reason. Each frame
     becomes a button so it can be opened from the keyboard as
     well as the pointer, and the buttons are built here rather
     than in the markup: a control that does nothing without a
     script should not be served to someone who has none. Left
     and right move along the strip; the adjacent frames stay
     visible, which is the point of a strip.
     ========================================================== */
  (function gallery() {
    var strip = one("[data-houses-strip]");
    if (!strip) return;
    var items = all("li", strip);

    items.forEach(function (item) {
      var figure = one("figure", item);
      if (!figure) return;
      var button = document.createElement("button");
      button.type = "button";
      button.setAttribute("aria-expanded", "false");
      figure.parentNode.insertBefore(button, figure);
      button.appendChild(figure);

      function open() {
        items.forEach(function (other) {
          var on = other === item;
          other.classList.toggle("is-open", on);
          var b = one("button", other);
          if (b) b.setAttribute("aria-expanded", on ? "true" : "false");
        });
        item.scrollIntoView({ block: "nearest", inline: "nearest",
                              behavior: reduced.matches ? "auto" : "smooth" });
      }

      button.addEventListener("click", open);
      button.addEventListener("focus", open);
      button.addEventListener("keydown", function (event) {
        var step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
        if (!step) return;
        event.preventDefault();
        var shown = items.filter(function (i) { return !i.hidden; });
        var at = shown.indexOf(item);
        var next = shown[Math.min(shown.length - 1, Math.max(0, at + step))];
        var b = next && one("button", next);
        if (b) b.focus();
      });
    });

    var tabs = all("[data-houses-house]");
    var tabGroup = one("[data-houses-tabs]");
    function filter(slug) {
      tabs.forEach(function (tab) {
        var on = tab.getAttribute("data-houses-house") === slug;
        tab.classList.toggle("is-on", on);
        tab.setAttribute("aria-pressed", on ? "true" : "false");
      });
      items.forEach(function (item) {
        var keep = slug === "all" || item.getAttribute("data-house") === slug;
        item.hidden = !keep;
        // A frame that is being filtered away gives up its expanded state with
        // it. Left alone, an open frame kept .is-open while hidden: returning
        // to "All" then showed one frame already expanded with nothing focused
        // on it, and aria-expanded="true" sat on a button no one could reach.
        if (!keep && item.classList.contains("is-open")) {
          item.classList.remove("is-open");
          var button = one("button", item);
          if (button) button.setAttribute("aria-expanded", "false");
        }
      });
    }
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        filter(tab.getAttribute("data-houses-house"));
      });
    });

    // A chapter links to the portrait itself so the destination also works
    // without script. With script, that link filters the strip to its house.
    function applyTab(id) {
      if (!id || id.indexOf("gallery-") !== 0) return;
      var slug = id.slice("gallery-".length);
      var tab = tabs.find(function (candidate) {
        return candidate.getAttribute("data-houses-house") === slug;
      });
      if (tab) filter(slug);
    }

    // Two ways in, and both are needed.
    //
    // hashchange covers a pasted URL, a bookmark and the back button. It does
    // NOT cover a reader clicking the link on the page: cirs.js intercepts
    // in-page anchors to hand them to Lenis for a smooth scroll, calls
    // preventDefault and never writes location.hash — so the chapter link
    // scrolled the gallery into view with all four houses still showing,
    // which is the one thing that link exists not to do. Listening for the
    // click as well is independent of who ends up handling the navigation.
    document.addEventListener("click", function (event) {
      var link = event.target.closest && event.target.closest('a[href^="#gallery-"]');
      if (link) applyTab(link.getAttribute("href").slice(1));
    });
    window.addEventListener("hashchange", function () {
      applyTab((location.hash || "").replace("#", ""));
    });
    applyTab((location.hash || "").replace("#", ""));
    if (tabGroup) tabGroup.hidden = false;
  })();

  /* Everything below this point is motion, and everything below this point
     is therefore inside a context that can be reverted. */
  if (!gsap || !ScrollTrigger || !gsap.matchMedia) return;

  var mm = gsap.matchMedia();

  /* ==========================================================
     Motion at every width
     ----------------------------------------------------------
     The chapter wipes, the depths, and the two entrances that
     are not width-dependent.
     ========================================================== */
  mm.add("(prefers-reduced-motion: no-preference)", function () {

    /* ---- 3. the chapter wipes ----
       One bar per chapter. Entering, it is a full-width band in the
       OUTGOING house's colour; it contracts to a narrow vertical stripe at
       the middle of the scrub, changes to the INCOMING colour there, and
       opens out again. So the colours never cross-fade into a muddle: one
       leaves, the other arrives, and for an instant there is only a stripe.

       The first chapter's outgoing colour is its own, which makes its wipe a
       plain opening rather than a change — correct, because the hero has just
       filled the window with it. */
    all("[data-houses-chapter]").forEach(function (chapter) {
      var wipe = one("[data-houses-wipe]", chapter);
      var ghost = one("[data-houses-ghost]", chapter);
      var frame = one(".hch__bleed img", chapter);
      var from = chapter.getAttribute("data-from");
      var to = chapter.getAttribute("data-house");

      if (wipe) {
        ScrollTrigger.create({
          trigger: chapter,
          start: "top bottom",
          end: "top 42%",
          onUpdate: function (self) {
            var p = self.progress;
            // 1 at the edges, 0.02 in the middle: a band, a stripe, a band.
            var w = Math.max(0.02, Math.abs(p - 0.5) * 2);
            wipe.style.transform = "scaleX(" + w.toFixed(3) + ") scaleY(" +
              (1 + (1 - w) * 22).toFixed(2) + ")";
            wipe.setAttribute("data-house", p < 0.5 ? from : to);
          }
        });
      }

      // The oversized name and the photograph move at different depths, so
      // the chapter has some thickness to it rather than sliding as a slab.
      if (ghost) {
        gsap.fromTo(ghost, { xPercent: -6 }, {
          xPercent: 6, ease: "none",
          scrollTrigger: { trigger: chapter, start: "top bottom", end: "bottom top", scrub: 0.6 }
        });
      }
      if (frame) {
        gsap.fromTo(frame, { yPercent: -4 }, {
          yPercent: 4, ease: "none",
          scrollTrigger: { trigger: chapter, start: "top bottom", end: "bottom top", scrub: 0.8 }
        });
      }
    });

    /* ---- the symposium flats, and the four bars of the ending ---- */
    var set = one("[data-houses-symposiums]");
    if (set) {
      gsap.from(all("li", set), {
        opacity: 0, yPercent: 12, duration: 0.85, ease: "power3.out", stagger: 0.09,
        scrollTrigger: { trigger: set, start: "top 86%", once: true }
      });
    }
    var bars = all(".hend__bars span");
    if (bars.length) {
      gsap.from(bars, {
        scaleX: 0, transformOrigin: "0% 50%", duration: 0.8, ease: "expo.out", stagger: 0.08,
        scrollTrigger: { trigger: ".hend__bars", start: "top 90%", once: true }
      });
    }
    if (title) {
      gsap.from(title, { yPercent: 16, opacity: 0, duration: 1.1, ease: "expo.out", delay: 0.95 });
    }
  });

  /* ==========================================================
     Motion above the breakpoint only
     ----------------------------------------------------------
     The release and the march. Both are pinned or scrubbed
     horizontal motion, which is exactly what the mobile layout
     in houses.css does not have — so they are built when the
     window is wide and reverted when it is not, rather than
     decided once at load.
     ========================================================== */
  mm.add("(min-width: 901px) and (prefers-reduced-motion: no-preference)", function () {

    /* ---- 1. the opening frame: which house is live, and the depth ----
       Inside the context because both only make sense where the zones
       expand; reverting drops the listeners with the context. */
    var offs = [];
    function on(el, type, fn) {
      el.addEventListener(type, fn);
      offs.push(function () { el.removeEventListener(type, fn); });
    }
    var fine = matchMedia("(hover: hover) and (pointer: fine)");
    zones.forEach(function (zone) {
      // The expansion itself stays in CSS, and .is-live deliberately carries
      // no width: the class outlives the pointer so the release knows whose
      // colour to use, and a class that outlives the pointer must not hold
      // the layout open.
      on(zone, "pointerenter", function () { setLive(zone); });
      on(zone, "focus", function () { setLive(zone); });
      if (!fine.matches) return;
      // Depth, on the photograph only, and small: about 10px at the edge of
      // the zone. A transform, so it costs no layout.
      on(zone, "pointermove", function (event) {
        var box = zone.getBoundingClientRect();
        var x = (event.clientX - box.left) / box.width - 0.5;
        var y = (event.clientY - box.top) / box.height - 0.5;
        zone.style.setProperty("--px", (-x * 20).toFixed(1) + "px");
        zone.style.setProperty("--py", (-y * 14).toFixed(1) + "px");
      });
      on(zone, "pointerleave", function () {
        zone.style.removeProperty("--px");
        zone.style.removeProperty("--py");
      });
    });

    /* ---- 2. the release ----
       The sticky stage stands still through the second 84vh of its track, and
       that travel is the scrub distance. Across it the title rises away, the
       three quiet zones fade back, and the live house's colour comes up over
       the whole window — which is the handover into its chapter.

       Opacity and transform only, and it reverses because it reads progress
       rather than running a sequence of toggles. */
    var track = hero && one(".hsx__track", hero);
    var say = hero && one(".hsx__say", hero);
    if (track && fill) {
      ScrollTrigger.create({
        trigger: track,
        start: "top top",
        end: "bottom bottom",
        onUpdate: function (self) {
          // Nothing happens through the first third: the opening frame is
          // meant to be looked at before it starts dissolving.
          var p = Math.max(0, (self.progress - 0.34) / 0.66);
          fill.style.opacity = (p * 0.96).toFixed(3);
          if (say) {
            say.style.transform = "translate3d(0," + (-p * 26).toFixed(1) + "vh,0)";
            say.style.opacity = (1 - Math.min(1, p * 1.5)).toFixed(3);
          }
          zones.forEach(function (z) {
            z.style.opacity = z === live ? "1" : (1 - p * 0.85).toFixed(3);
          });
        }
      });
    }

    /* ---- 4. the march ----
       The run is pushed sideways as the section passes, and the names behind
       it travel further, so the two read as separate distances. It is NOT
       pinned and it does not take the wheel: the page keeps scrolling
       normally throughout, which is what keeps this from becoming a section
       a reader can get stuck in. Below the breakpoint, and under reduced
       motion, the run keeps its own native horizontal scroll instead. */
    var march = one("[data-houses-march]");
    var run = march && one("[data-march-run]", march);
    var names = march && one("[data-march-names]", march);
    if (run) {
      run.classList.add("is-driven");
      // How far it has to travel to show its last frame, measured rather
      // than assumed, and re-measured when the window changes.
      gsap.to(run, {
        x: function () { return -Math.max(0, run.scrollWidth - run.clientWidth + 40); },
        ease: "none",
        scrollTrigger: {
          trigger: march, start: "top 82%", end: "bottom 18%",
          scrub: 0.7, invalidateOnRefresh: true
        }
      });
      if (names) {
        gsap.fromTo(names, { xPercent: 4 }, {
          xPercent: -26, ease: "none",
          scrollTrigger: { trigger: march, start: "top bottom", end: "bottom top", scrub: 0.9 }
        });
      }
    }

    // What matchMedia cannot revert on its own: the listeners above, the
    // class on the run, and the inline properties the two scrubs write
    // straight onto style rather than through gsap.set.
    return function () {
      offs.forEach(function (off) { off(); });
      if (run) run.classList.remove("is-driven");
      if (fill) fill.style.removeProperty("opacity");
      if (say) { say.style.removeProperty("transform"); say.style.removeProperty("opacity"); }
      zones.forEach(function (z) {
        z.style.removeProperty("opacity");
        z.style.removeProperty("--px");
        z.style.removeProperty("--py");
      });
    };
  });
})();
