/* CIRS Art Attack — the opening, the wall's filters, and the viewer.

   The opening. The page's own inline script marks the section .is-live
   before first paint (unless the reader prefers reduced motion). Here the
   section's scroll progress is written to --p, 0 to 1, and the stylesheet
   does the rest: the photograph slides aside, the work comes forward. Only
   a custom property changes, once per frame at most, and only while the
   section is on screen.

   The wall. Every work is a link to its full-size image, which is what a
   click does without this script. The filters and the issue select hide
   and show figures; "Show more" reveals the next thirty of whatever is
   selected. Hidden images are lazy and so are never fetched.

   The viewer. A native modal <dialog>: the page behind is inert, and
   Escape closes it. Arrow keys and the buttons step through the works
   currently selected on the wall (the opening's, the hang's and the
   ribbons' works lead), swipes do the same on touch, and closing returns
   focus to the link that opened it. The full-size image replaces the thumbnail once decoded, and
   the neighbours are fetched next so that stepping is immediate. */
(function () {
  "use strict";

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Direct native playback: keep the visitor's pause choice and the supplied poster. */
  var videoHero = document.querySelector("[data-aa-video-hero]");
  var openingVideo = videoHero && videoHero.querySelector("[data-aa-opening-video]");
  if (openingVideo) {
    openingVideo.addEventListener("error", function () {
      var fallback = openingVideo.dataset.errorPoster;
      if (!fallback) return;
      openingVideo.poster = fallback;
      videoHero.querySelector(".aa-video-hero__poster").src = fallback;
    });
    if (window.CIRSMedia) window.CIRSMedia.manage(openingVideo);
  }

  /* ---------------- Opening ---------------- */
  var open = document.querySelector("[data-aa-open]");
  if (open) {
    window.aaOpenReady = true;
    if (reduced) open.classList.remove("is-live");
    if (open.classList.contains("is-live")) {
      var ticking = false, lastP = -1;
      var measure = function () {
        ticking = false;
        var r = open.getBoundingClientRect();
        var run = r.height - window.innerHeight;
        var p = run > 0 ? Math.min(1, Math.max(0, -r.top / (run * 0.82))) : 1;
        // A gentle ease: the photograph starts moving at once, and settles.
        p = 1 - Math.pow(1 - p, 2);
        if (Math.abs(p - lastP) > 0.001) {
          open.style.setProperty("--p", p.toFixed(4));
          lastP = p;
        }
      };
      var onScroll = function () {
        if (!ticking) { ticking = true; window.requestAnimationFrame(measure); }
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      window.addEventListener("resize", onScroll);
      measure();
    }
  }

  /* ---------------- Ribbons ----------------
     Each band of works drifts sideways, by exactly the part of it that
     does not fit the window, while the band crosses the screen: the warm
     one leftward, the cool one rightward. Without this, or with reduced
     motion, the band scrolls sideways by hand. A keyboard reader tabbing
     into a band stops its drift, so the browser can scroll to the link. */
  var ribbons = reduced ? [] : Array.prototype.slice.call(document.querySelectorAll("[data-aa-ribbon]"));
  ribbons.forEach(function (band) {
    var track = band.querySelector("[data-aa-track]");
    var dir = +band.getAttribute("data-dir") || -1;
    var ticking = false, on = true;
    band.classList.add("is-drifting");
    function place() {
      ticking = false;
      if (!on) return;
      var r = band.getBoundingClientRect();
      var vh = window.innerHeight;
      if (r.bottom < -50 || r.top > vh + 50) return;
      var p = Math.min(1, Math.max(0, (vh - r.top) / (vh + r.height)));
      var room = Math.max(0, track.scrollWidth - band.clientWidth);
      var x = -room * (dir < 0 ? p : 1 - p);
      track.style.setProperty("--x", x.toFixed(1) + "px");
    }
    function onScroll() {
      if (!ticking) { ticking = true; window.requestAnimationFrame(place); }
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    band.addEventListener("focusin", function () {
      if (!on) return;
      on = false;
      band.classList.remove("is-drifting");
      track.style.removeProperty("--x");
    });
    place();
  });

  /* ---------------- Wall ---------------- */
  var grid = document.querySelector("[data-aa-grid]");
  var figures = grid ? Array.prototype.slice.call(grid.querySelectorAll(".aa-work")) : [];
  var moreBtn = document.querySelector("[data-aa-more]");
  var status = document.querySelector("[data-aa-status]");
  var select = document.querySelector("[data-aa-issue]");
  var filterBtns = Array.prototype.slice.call(document.querySelectorAll(".aa-filter"));
  var STEP = 30;
  var state = { cat: "all", issue: "", shown: STEP };

  function matches(fig) {
    var a = fig.querySelector("a");
    var cats = (a.getAttribute("data-cat") || "").split(" ");
    if (state.cat !== "all" && cats.indexOf(state.cat) < 0) return false;
    if (state.issue && a.getAttribute("data-issue") !== state.issue) return false;
    return true;
  }

  function selected() { return figures.filter(matches); }

  function render(announce) {
    var list = selected();
    figures.forEach(function (f) { f.hidden = true; });
    list.forEach(function (f, i) { f.hidden = i >= state.shown; });
    var left = Math.max(0, list.length - state.shown);
    if (moreBtn) {
      moreBtn.hidden = left === 0;
      moreBtn.textContent = "Show more works (" + left + " more)";
    }
    if (status) {
      var shown = Math.min(state.shown, list.length);
      var text = list.length === 0 ? "No works match." :
        (shown < list.length ? "Showing " + shown + " of " + list.length + " works." :
                               "Showing all " + list.length + " works.");
      if (announce || status.textContent) status.textContent = text;
    }
  }

  if (grid) {
    filterBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        state.cat = b.getAttribute("data-filter");
        state.shown = STEP;
        filterBtns.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
        render(true);
      });
    });
    if (select) {
      select.addEventListener("change", function () {
        state.issue = select.value;
        state.shown = STEP;
        render(true);
      });
    }
    if (moreBtn) {
      moreBtn.addEventListener("click", function () {
        var list = selected();
        var firstNew = list[state.shown];
        state.shown += STEP;
        render(true);
        // Carry focus to the first newly shown work, so a keyboard reader
        // continues where the wall grew rather than at the button.
        if (firstNew) firstNew.querySelector("a").focus({ preventScroll: true });
      });
    }
    render(false);
  }

  /* ---------------- Viewer ---------------- */
  var box = document.querySelector("[data-aa-viewer]");
  if (!box || typeof box.showModal !== "function") return;

  var frame = box.querySelector("[data-aa-frame]");
  var stage = box.querySelector("[data-aa-stage]");
  var el = {
    count: box.querySelector("[data-aa-count]"),
    title: box.querySelector("[data-aa-title]"),
    grade: box.querySelector("[data-aa-grade]"),
    kind: box.querySelector("[data-aa-kind]"),
    source: box.querySelector("[data-aa-source]"),
    note: box.querySelector("[data-aa-note]")
  };
  var fixed = Array.prototype.slice.call(document.querySelectorAll(".aa-open__work, .aa-hang__work a, .aa-ribbon__work a"));
  var list = [], current = -1, opener = null, fetched = {};

  function sequence() {
    // The opening's work, the hang and the ribbons first, then whatever the wall has selected.
    var wall = grid ? selected().map(function (f) { return f.querySelector("a"); }) : [];
    return fixed.concat(wall);
  }

  function fetchFull(a) {
    var url = a.getAttribute("href");
    if (!fetched[url]) {
      var img = new Image();
      img.decoding = "async";
      img.src = url;
      fetched[url] = img;
    }
    return fetched[url];
  }

  function wrap(i) { var n = list.length; return (i % n + n) % n; }

  function describe(a) {
    var title = a.getAttribute("data-title");
    var name = a.getAttribute("data-name");
    // A title if the work has one (only the archive's do), otherwise the
    // credit; with neither, the kind of work. Never "Unknown artist".
    el.title.textContent = title || name || a.getAttribute("data-kind") || "Student work";
    var grade = a.getAttribute("data-grade") || "";
    el.grade.textContent = (title && name ? name + (grade ? " · " : "") : "") + grade;
    el.grade.hidden = !el.grade.textContent;
    el.kind.textContent = a.getAttribute("data-kind") || "";
    el.source.textContent = a.getAttribute("data-source") || "";
    var note = a.getAttribute("data-note");
    el.note.textContent = note || "";
    el.note.hidden = !note;
  }

  function show(i, animate) {
    i = wrap(i);
    current = i;
    var a = list[i];
    var thumb = a.querySelector("img");
    var img = document.createElement("img");
    img.alt = thumb.alt;
    img.width = +a.getAttribute("data-w");
    img.height = +a.getAttribute("data-h");
    var full = fetchFull(a);
    img.src = full.complete && full.naturalWidth ? full.src : (thumb.currentSrc || thumb.src);
    if (animate && !reduced) img.className = "is-entering";

    var placed = false;
    function place() {
      if (placed || current !== i) return;
      placed = true;
      var old = Array.prototype.slice.call(frame.children);
      frame.appendChild(img);
      old.forEach(function (o) { o.remove(); });
      describe(a);
      el.count.textContent = (i + 1) + " / " + list.length;
    }
    if (img.decode) img.decode().then(place, place);
    window.setTimeout(place, 220);
    if (!frame.firstChild) place();

    function swap() {
      if (current !== i) return;
      if (img.src !== full.src) img.src = full.src;
      fetchFull(list[wrap(i + 1)]);
      fetchFull(list[wrap(i - 1)]);
    }
    if (full.complete && full.naturalWidth) swap();
    else full.addEventListener("load", swap, { once: true });
  }

  function lock(on) {
    document.body.classList.toggle("has-lightbox", on);
    window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: on } }));
  }

  function openAt(a) {
    list = sequence();
    var i = list.indexOf(a);
    if (i < 0) { list.unshift(a); i = 0; }
    opener = a;
    frame.replaceChildren();
    show(i, false);
    box.showModal();
    lock(true);
    box.querySelector("[data-aa-close]").focus({ preventScroll: true });
  }

  function step(d) { if (box.open && list.length > 1) show(current + d, true); }

  box.addEventListener("close", function () {
    lock(false);
    frame.replaceChildren();
    current = -1;
    if (opener) { opener.focus({ preventScroll: true }); opener = null; }
  });

  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[data-aa-work]");
    if (!a || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    openAt(a);
  });
  Array.prototype.forEach.call(document.querySelectorAll("a[data-aa-work]"), function (a) {
    a.setAttribute("aria-haspopup", "dialog");
  });

  box.querySelector("[data-aa-close]").addEventListener("click", function () { box.close(); });
  box.querySelector("[data-aa-prev]").addEventListener("click", function () { step(-1); });
  box.querySelector("[data-aa-next]").addEventListener("click", function () { step(1); });
  box.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
  });

  // Swipe sideways to step; vertical movement and pinching stay the browser's.
  var start = null, swipedAt = -1;
  stage.addEventListener("pointerdown", function (e) {
    if (e.pointerType === "mouse" || !e.isPrimary) return;
    start = { x: e.clientX, y: e.clientY };
  });
  stage.addEventListener("pointercancel", function () { start = null; });
  stage.addEventListener("pointerup", function (e) {
    if (!start) return;
    var dx = e.clientX - start.x, dy = e.clientY - start.y;
    var zoomed = window.visualViewport && window.visualViewport.scale > 1.01;
    start = null;
    if (zoomed || Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy) * 1.2) return;
    swipedAt = e.timeStamp;
    step(dx < 0 ? 1 : -1);
  });
  // A click on the empty room around the work closes the viewer.
  stage.addEventListener("click", function (e) {
    if (e.timeStamp - swipedAt < 500) return;
    if (e.target === stage || e.target === frame) box.close();
  });
})();

/* Background marks share the existing GSAP/ScrollTrigger clock. Static by default. */
(function () {
  "use strict";
  if (!document.body.classList.contains("artattack") || !window.gsap || !window.ScrollTrigger) return;
  var media = gsap.matchMedia();
  media.add("(prefers-reduced-motion: no-preference)", function () {
    document.querySelectorAll(".aa-sec > .aa-decor--brush").forEach(function (mark) {
      gsap.fromTo(mark, { clipPath:"inset(0 100% 0 0)" }, {
        clipPath:"inset(0 0% 0 0)", duration:0.65, ease:"power2.out",
        scrollTrigger:{ trigger:mark.parentNode, start:"top 85%", once:true }
      });
    });
    document.querySelectorAll(".aa-sketch-stroke").forEach(function (stroke) {
      gsap.fromTo(stroke, { strokeDasharray:1, strokeDashoffset:1 }, {
        strokeDashoffset:0, duration:0.85, ease:"power1.inOut",
        scrollTrigger:{ trigger:stroke.closest("section"), start:"top 80%", once:true }
      });
    });
    var film = document.querySelector("#art-attack-opening[data-film]");
    if (!film) return;
    var phases = (film.getAttribute("data-film-phases") || "").trim().split(/\s+/).map(Number);
    var hold = phases[1] || 0.77, settled = phases[2] || 0.90;
    // Clear the decorative ground while the existing film is being scrubbed.
    gsap.timeline({ scrollTrigger:{ trigger:film, start:"top top", end:"bottom bottom", scrub:0.15 } })
      .to(".aa-decor--hero", { opacity:0, duration:0.025, ease:"none" })
      .to(".aa-decor--hero", { opacity:0, duration:hold - 0.025, ease:"none" })
      .to(".aa-decor--hero", { opacity:1, duration:settled - hold, ease:"power1.inOut" })
      .to(".aa-decor--hero", { opacity:1, duration:1 - settled, ease:"none" });
    gsap.to(".aa-decor-drift", { y:6, x:4, ease:"none",
      scrollTrigger:{ trigger:"#art-attack-opening", start:"top top", end:"bottom bottom", scrub:0.6 }
    });
  });
})();
