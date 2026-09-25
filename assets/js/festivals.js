/* CIRS Festivals — the page's own behaviour.

   Everything on the page works without this file: the strip and the
   index are links, the night is a sequence of captioned photographs,
   and every archive tile opens its photograph. What it adds:

   - the opening's light-up, festival by festival, once the curtain has
     gone, and the dawn that rises behind the strip as the reader scrolls;
   - the year index: which chapter is being read, and how far through;
   - the night's clock, which keeps the time of the photograph in view;
   - the archive's filters, and a viewer with keyboard and swipe.

   Motion stops at the reader's request: under prefers-reduced-motion
   the light is simply on and nothing follows the scroll. */
(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;
  var body = doc.body;
  if (!body.classList.contains("festivals")) return;

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };

  /* ----------------------------------------------------------
     Where the floating header ends, so the index sits under it.
     ---------------------------------------------------------- */
  function measureHeader() {
    var bar = $(".header .wrap") || $(".header");
    if (!bar) return;
    var bottom = bar.getBoundingClientRect().bottom;
    if (bottom > 0 && bottom < 200) {
      body.style.setProperty("--fx-top", Math.round(bottom + 8) + "px");
    }
  }

  /* ----------------------------------------------------------
     The opening: the festivals light one after another.
     The shared curtain covers the page on a first visit; the light-up
     waits for it to go, or plays at once when there is none.
     ---------------------------------------------------------- */
  var open = $("[data-fx-open]");

  function lightUp() {
    if (!open || open.classList.contains("is-lit")) return;
    // Two frames, so the dark state is painted before the transition runs.
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () { open.classList.add("is-lit"); });
    });
  }

  function whenCurtainGone(fn) {
    var waited = 0;
    (function check() {
      var c = doc.getElementById("curtain");
      var locked = body.classList.contains("is-locked");
      if ((!c && !locked) || waited > 6000) { fn(); return; }
      waited += 120;
      window.setTimeout(check, 120);
    })();
  }

  if (open && !reduced) {
    open.classList.add("is-dark");
    whenCurtainGone(lightUp);
  }

  /* ----------------------------------------------------------
     Scroll: the dawn behind the strip, and the index's fill.
     One passive listener, one frame of work at most per frame.
     ---------------------------------------------------------- */
  var year = $("#year");
  var chapters = $$("[data-fx-chapter]");
  var fill = $(".fx-index");
  var ticking = false;

  function onScroll() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () {
      ticking = false;
      var vh = window.innerHeight;
      if (open && !reduced) {
        var r = open.getBoundingClientRect();
        var p = Math.min(1, Math.max(0, -r.top / Math.max(1, r.height * .6)));
        open.style.setProperty("--fx-dawn", p.toFixed(3));
      }
      if (year && fill && chapters.length) {
        var first = chapters[0].getBoundingClientRect();
        var last = chapters[chapters.length - 1].getBoundingClientRect();
        var span = last.bottom - first.top - vh * .5;
        var done = Math.min(1, Math.max(0, (vh * .5 - first.top) / Math.max(1, span)));
        fill.style.setProperty("--fx-progress", done.toFixed(4));
        // The index takes no room of its own, so it would ride on past the
        // last chapter into the next section; it bows out once Holi has gone.
        var top = parseFloat(getComputedStyle(body).getPropertyValue("--fx-top")) || 84;
        fill.classList.toggle("is-past", last.bottom < top + 72);
      }
    });
  }

  /* ----------------------------------------------------------
     The year index: the chapter crossing the middle of the window
     is the one being read.
     ---------------------------------------------------------- */
  var links = $$("[data-fx-index]");
  var list = $(".fx-index__list");
  var current = null;

  function setCurrent(id) {
    if (id === current) return;
    current = id;
    links.forEach(function (a) {
      if (a.getAttribute("data-fx-index") === id) {
        a.setAttribute("aria-current", "location");
        // Keep it in view on a narrow index without moving the page.
        if (list && list.scrollWidth > list.clientWidth) {
          var left = a.offsetLeft - (list.clientWidth - a.offsetWidth) / 2;
          try { list.scrollTo({ left: left, behavior: reduced ? "auto" : "smooth" }); }
          catch (e) { list.scrollLeft = left; }
        }
      } else {
        a.removeAttribute("aria-current");
      }
    });
  }

  if ("IntersectionObserver" in window && chapters.length) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) setCurrent(e.target.id); });
    }, { rootMargin: "-48% 0px -48% 0px" });
    chapters.forEach(function (c) { seen.observe(c); });
  }

  /* ----------------------------------------------------------
     The night: the clock keeps the time of the photograph that is
     crossing the middle of the window, and the ground deepens into
     the small hours. Each photograph also settles from a little
     smaller as it arrives, more for the frame the night builds to.
     ---------------------------------------------------------- */
  var night = $("[data-fx-night]");
  if (night && "IntersectionObserver" in window) {
    var clock = $("[data-fx-clock]", night);
    var date = $("[data-fx-date]", night);
    var face = clock && clock.parentNode;
    var shown = clock ? clock.textContent : "";
    var tickTimer;

    var watch = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var f = e.target;
        night.setAttribute("data-phase", f.getAttribute("data-phase") || "night");
        var t = f.getAttribute("data-time");
        if (clock && t && t !== shown) {
          shown = t;
          if (reduced || !face) {
            clock.textContent = t;
            if (date) date.textContent = f.getAttribute("data-date");
          } else {
            face.classList.add("is-ticking");
            window.clearTimeout(tickTimer);
            tickTimer = window.setTimeout(function () {
              clock.textContent = t;
              if (date) date.textContent = f.getAttribute("data-date");
              face.classList.remove("is-ticking");
            }, 180);
          }
        }
      });
    }, { rootMargin: "-45% 0px -45% 0px" });
    $$("[data-fx-frame]", night).forEach(function (f) { watch.observe(f); });

    // Leaving the night upwards returns it to the morning.
    var edge = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting && e.boundingClientRect.top > 0) night.removeAttribute("data-phase");
      });
    });
    edge.observe(night);
  }

  function nightScale() {
    if (reduced || !night || typeof window.gsap === "undefined" ||
        typeof window.ScrollTrigger === "undefined") return;
    $$(".fx-frame", night).forEach(function (f) {
      var img = $(".fx-frame__img", f);
      if (!img) return;
      var big = f.classList.contains("fx-frame--7");
      window.gsap.fromTo(img, { scale: big ? .84 : .94, opacity: big ? .55 : .8 }, {
        scale: 1, opacity: 1, ease: "none",
        scrollTrigger: { trigger: f, start: "top 96%", end: big ? "top 18%" : "top 50%", scrub: .6 }
      });
    });
  }

  /* ----------------------------------------------------------
     The archive: filters by festival and by year.
     ---------------------------------------------------------- */
  var grid = $("[data-fx-grid]");
  var tiles = grid ? $$(".fx-tile", grid) : [];
  var count = $("[data-fx-count]");
  var empty = $("[data-fx-empty]");
  var chips = $$("[data-fx-filter]");
  var state = { festival: "all", year: "all" };

  function matches(t, s) {
    return (s.festival === "all" || t.getAttribute("data-festival") === s.festival) &&
           (s.year === "all" || t.getAttribute("data-year") === s.year);
  }

  function applyFilters() {
    var n = 0;
    tiles.forEach(function (t) {
      var on = matches(t, state);
      t.hidden = !on;
      if (on) n++;
    });
    // A year with nothing for the chosen festival, or a festival with
    // nothing in the chosen year, cannot be picked into an empty grid.
    chips.forEach(function (c) {
      var kind = c.getAttribute("data-fx-filter");
      var value = c.getAttribute("data-value");
      c.setAttribute("aria-pressed", String(state[kind] === value));
      if (value === "all") { c.disabled = false; return; }
      var probe = { festival: state.festival, year: state.year };
      probe[kind] = value;
      c.disabled = !tiles.some(function (t) { return matches(t, probe); });
    });
    if (count) count.textContent = n + (n === 1 ? " photograph" : " photographs");
    if (empty) empty.hidden = n > 0;
    if (typeof window.ScrollTrigger !== "undefined") window.ScrollTrigger.refresh();
  }

  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      if (c.disabled) return;
      state[c.getAttribute("data-fx-filter")] = c.getAttribute("data-value");
      applyFilters();
    });
  });

  /* ----------------------------------------------------------
     The viewer. A native dialog keeps focus inside and closes on
     Escape; the arrows move through the photographs the filters
     are showing, and focus goes back to the tile that opened it.
     ---------------------------------------------------------- */
  var viewer = $("[data-fx-viewer]");
  if (viewer && typeof viewer.showModal === "function" && grid) {
    var vImg = $("[data-fx-viewer-img]", viewer);
    var vCap = $("[data-fx-viewer-cap]", viewer);
    var vWhen = $("[data-fx-viewer-when]", viewer);
    var vPos = $("[data-fx-viewer-pos]", viewer);
    var opener = null;
    var at = 0;

    function visible() {
      return tiles.filter(function (t) { return !t.hidden; })
                  .map(function (t) { return $(".fx-tile__link", t); });
    }

    function show(i) {
      var set = visible();
      if (!set.length) return;
      at = (i + set.length) % set.length;
      var a = set[at];
      var thumb = $("img", a);
      vImg.src = a.getAttribute("href");
      vImg.alt = thumb ? thumb.alt : "";
      vCap.textContent = a.getAttribute("data-caption") || "";
      vWhen.textContent = a.getAttribute("data-when") || "";
      vPos.textContent = (at + 1) + " / " + set.length;
      // Fetch the neighbours now, so the next press is immediate.
      [at + 1, at - 1].forEach(function (k) {
        var n = set[(k + set.length) % set.length];
        if (n) { var pre = new Image(); pre.src = n.getAttribute("href"); }
      });
    }

    function openAt(link) {
      opener = link;
      show(visible().indexOf(link));
      root.classList.add("fx-viewing");
      viewer.showModal();
      var close = $("[data-fx-close]", viewer);
      if (close) close.focus();
    }

    grid.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest(".fx-tile__link");
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button > 0) return;
      e.preventDefault();
      openAt(a);
    });

    $("[data-fx-prev]", viewer).addEventListener("click", function () { show(at - 1); });
    $("[data-fx-next]", viewer).addEventListener("click", function () { show(at + 1); });
    $("[data-fx-close]", viewer).addEventListener("click", function () { viewer.close(); });

    viewer.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); show(at - 1); }
      else if (e.key === "ArrowRight") { e.preventDefault(); show(at + 1); }
    });
    // A click on the dark ground around the photograph closes it.
    viewer.addEventListener("click", function (e) {
      if (e.target === viewer || e.target.classList.contains("fx-viewer__inner")) viewer.close();
    });
    viewer.addEventListener("close", function () {
      root.classList.remove("fx-viewing");
      vImg.src = "data:,";
      if (opener) opener.focus({ preventScroll: true });
    });

    var x0 = null;
    viewer.addEventListener("touchstart", function (e) {
      x0 = e.touches.length === 1 ? e.touches[0].clientX : null;
    }, { passive: true });
    viewer.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      x0 = null;
      if (Math.abs(dx) > 48) show(dx < 0 ? at + 1 : at - 1);
    }, { passive: true });
  }

  /* ---------------------------------------------------------- */
  measureHeader();
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", function () { measureHeader(); onScroll(); }, { passive: true });
  if (chips.length) applyFilters();
  // The shared script builds its ScrollTriggers once the fonts are in;
  // these join them then, so their positions are measured with the rest.
  if (doc.fonts && doc.fonts.ready) {
    doc.fonts.ready.then(function () { window.setTimeout(nightScale, 0); });
  } else {
    window.addEventListener("load", nightScale);
  }
})();
