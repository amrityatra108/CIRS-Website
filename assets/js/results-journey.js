/* Our Results — the results book.
   ------------------------------------------------------------------
   The pages in tools/pages/our-results.html are the page's content. When
   there is room and motion (see bookPossible), this lays them out as an
   open book, pins the stage and turns the leaves on scroll; otherwise, or
   when "Plain results" is pressed, it leaves them as a document.

   One state model: the scroll position. The chapter links, previous and
   next, the arrow keys, focus arriving in a page and an inbound #hash all
   become a scroll target, and the scrubbed timeline follows it. Nothing
   captures the wheel.
   ------------------------------------------------------------------ */
(function () {
  "use strict";

  var body = document.body;
  if (!body.classList.contains("results")) return;
  var root = document.querySelector("[data-results-book]");
  if (!root) return;

  var gsap = window.gsap;
  var ST = window.ScrollTrigger;
  var stage = root.querySelector(".rb-stage");
  var intro = root.querySelector(".rb-intro");
  var nav = root.querySelector(".rb-chapters");
  var book = root.querySelector("[data-book]");
  var leaves = Array.prototype.slice.call(root.querySelectorAll("[data-leaf]"));
  var endPage = root.querySelector(".rb-page--end");
  var shadeL = root.querySelector(".rb-shade--l");
  var shadeR = root.querySelector(".rb-shade--r");
  var next = root.querySelector(".rb-next");
  var nextInner = root.querySelector(".rb-next__inner");
  var plainToggle = root.querySelector("[data-plain-toggle]");
  var chapterLinks = Array.prototype.slice.call(root.querySelectorAll("[data-chapter-link]"));

  var roomQuery = window.matchMedia("(min-width: 960px) and (min-height: 640px)");
  var motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

  // chapter -> the element (and #hash) that stands for it
  var ANCHORS = { opening: "top", cbse: "cbse-results", ib: "ib-results", next: "destinations" };
  var ORDER = ["opening", "cbse", "ib", "next"];

  var PLAIN_KEY = "cirs-results-plain";
  var plain = false;
  try { plain = window.sessionStorage.getItem(PLAIN_KEY) === "1"; } catch (e) {}

  var scene = null;
  var directory = initDirectory();

  function bookPossible() {
    return !!(gsap && ST) && roomQuery.matches && !motionQuery.matches;
  }

  function chapterForHash(hash) {
    var id = (hash || "").replace(/^#/, "");
    for (var key in ANCHORS) if (ANCHORS[key] === id) return key;
    return null;
  }

  /* ---------------------------------------------------------------
     The book
     --------------------------------------------------------------- */
  function build() {
    gsap.registerPlugin(ST);
    body.classList.add("rb-on");

    var s = { labels: null, tl: null, st: null };
    s.ctx = gsap.context(function () {
      var wrap = book.parentNode;

      // Where the book sits before it settles: tilted, a little smaller,
      // just under the headline. Measured from layout (offset*), which
      // transforms do not disturb, so it can be re-read on every refresh.
      function introFit() {
        var gap = 16;
        var headBottom = intro.offsetTop + intro.offsetHeight + gap;
        var areaBottom = wrap.offsetTop + wrap.offsetHeight;
        var bh = book.offsetHeight;
        var bw = book.offsetWidth;
        var scale = Math.min(0.88, (areaBottom - headBottom) / bh, (stage.clientWidth * 0.84) / bw);
        scale = Math.max(0.5, scale);
        var settledTop = wrap.offsetTop + (wrap.offsetHeight - bh) / 2;
        // transform-origin is 50% 60%, so a scaled book's top moves down by
        // 60% of what it loses in height.
        var scaledTop = settledTop + bh * (1 - scale) * 0.6;
        var room = areaBottom - headBottom - bh * scale;
        return { scale: scale, y: headBottom - scaledTop + Math.max(0, room / 2) };
      }

      // The settled right-hand page, as a clip-path inset of the stage: the
      // shape the destinations panel grows out of.
      function pageInset() {
        var x = wrap.offsetLeft + book.offsetLeft + endPage.offsetLeft;
        var y = wrap.offsetTop + book.offsetTop + endPage.offsetTop;
        var r = stage.clientWidth - x - endPage.offsetWidth;
        var b = stage.clientHeight - y - endPage.offsetHeight;
        return "inset(" + y + "px " + r + "px " + b + "px " + x + "px round 2px)";
      }

      var fit = null;
      function getFit() { return fit || (fit = introFit()); }

      var tl = gsap.timeline({ defaults: { ease: "none" }, paused: true, onUpdate: paint });

      // Time is measured in window heights of scroll.
      tl.addLabel("opening", 0)
        .fromTo(intro, { opacity: 1, y: 0 }, { opacity: 0, y: -28, duration: 0.34, ease: "power1.in" }, 0)
        .fromTo(book,
          { rotationX: 8, rotationY: -4, scale: function () { return getFit().scale; }, y: function () { return getFit().y; } },
          { rotationX: 0, rotationY: 0, scale: 1, y: 0, duration: 0.6, ease: "power2.inOut" }, 0)
        .to(leaves[0], { rotationY: -180, duration: 0.5, ease: "power1.inOut" }, 0.6)
        .addLabel("cbse", 1.1)
        .to(leaves[1], { rotationY: -180, duration: 0.5, ease: "power1.inOut" }, 1.75)
        .addLabel("ib", 2.25)
        .to(leaves[2], { rotationY: -180, duration: 0.38, ease: "power1.inOut" }, 2.9)
        .addLabel("expand", 3.5)
        .set(next, { opacity: 1 }, "expand")
        .fromTo(next, { clipPath: pageInset }, { clipPath: "inset(0px 0px 0px 0px round 0px)", duration: 0.4, ease: "power2.inOut" }, "expand")
        .fromTo(nextInner, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.2, ease: "power1.out" }, "expand+=0.18")
        .to(book, { opacity: 0, scale: 0.97, duration: 0.3, ease: "power1.in" }, "expand+=0.06")
        .to(nav, { autoAlpha: 0, duration: 0.16 }, "expand+=0.08")
        .addLabel("next", 3.9);

      s.tl = tl;
      s.labels = tl.labels;
      s.st = ST.create({
        id: "results-book",
        trigger: root,
        start: "top top",
        end: function () { return "+=" + Math.round(tl.duration() * window.innerHeight); },
        pin: stage,
        anticipatePin: 1,
        scrub: 0.3,
        animation: tl,
        invalidateOnRefresh: true,
        onRefreshInit: function () { fit = null; },
        onRefresh: paint
      });
    });

    // Shading, stacking and the active chapter all follow from where the
    // timeline is, so scrubbing backwards undoes them exactly.
    function paint() {
      var turning = -1;
      var p = 0;
      leaves.forEach(function (leaf, i) {
        var q = Math.min(1, Math.max(0, -gsap.getProperty(leaf, "rotationY") / 180));
        var z = q <= 0.001 ? 10 + (leaves.length - i) : (q >= 0.999 ? 20 + i : 40);
        leaf.style.zIndex = z;
        leaf.children[0].style.setProperty("--shade", (Math.min(1, q * 2) * 0.34).toFixed(3));
        leaf.children[1].style.setProperty("--shade", (Math.min(1, (1 - q) * 2) * 0.34).toFixed(3));
        if (z === 40) { turning = i; p = q; }
      });
      var lift = turning < 0 ? 0 : Math.sin(p * Math.PI);
      shadeR.style.opacity = turning < 0 ? 0 : (p <= 0.5 ? lift : Math.max(0, 1 - (p - 0.5) * 6)).toFixed(3);
      shadeL.style.opacity = turning < 0 ? 0 : (p >= 0.5 ? lift : Math.max(0, 1 - (0.5 - p) * 6)).toFixed(3);
      if (s.tl) {
        var open = s.tl.time() >= s.labels.expand + 0.25;
        next.classList.toggle("is-open", open);
        // Once the paper panel is under the header, its lettering has to be
        // dark: the site's own switch for a page that opens on paper.
        body.classList.toggle("litehead", open);
        body.classList.toggle("rb-paper", open);
        markChapter(chapterAtTime(s.tl.time(), s.labels));
      }
    }

    s.paint = paint;
    scene = s;
    paint();
    return s;
  }

  function teardown() {
    if (!scene) return;
    scene.ctx.revert();
    // revert() puts back the values it first read, and for a .set() or a
    // from-state those were the book's own computed ones (the panel's
    // opacity: 0, for one), which the plain layout must not inherit.
    gsap.set([intro, nav, book, next, nextInner, shadeL, shadeR].concat(leaves), { clearProps: "all" });
    leaves.forEach(function (leaf) {
      leaf.children[0].style.removeProperty("--shade");
      leaf.children[1].style.removeProperty("--shade");
    });
    next.classList.remove("is-open");
    body.classList.remove("rb-on", "litehead", "rb-paper");
    markChapter(null);
    scene = null;
    ST.refresh();
  }

  function chapterAtTime(t, labels) {
    var L = labels || scene.labels;
    if (t >= L.expand + 0.2) return "next";
    if (t >= 2.0) return "ib";
    if (t >= 0.85) return "cbse";
    return "opening";
  }

  // Where the scroll is, in timeline time: ahead of the scrubbed animation,
  // which trails it slightly, so steps are taken from where the reader is going.
  function scrollTime() {
    var st = scene.st;
    var span = st.end - st.start;
    var p = span > 0 ? (window.scrollY - st.start) / span : 0;
    return Math.min(1, Math.max(0, p)) * scene.tl.duration();
  }

  function scrollFor(chapter) {
    var st = scene.st;
    var t = scene.labels[chapter] || 0;
    return Math.round(st.start + (t / scene.tl.duration()) * (st.end - st.start));
  }

  function scrollTo(top, instant) {
    if (instant) {
      window.scrollTo(0, top);
      ST.update();
      var scrub = scene && scene.st.getTween && scene.st.getTween();
      if (scrub) scrub.progress(1);
      return;
    }
    var move = new CustomEvent("cirs-section-scroll", { cancelable: true, detail: { top: top, duration: 0.65 } });
    if (window.dispatchEvent(move)) window.scrollTo({ top: top, behavior: "smooth" });
  }

  function go(chapter, instant) {
    if (!scene || !chapter) return;
    scrollTo(scrollFor(chapter), instant);
  }

  function step(dir) {
    if (!scene) return;
    var t = scrollTime();
    var stops = ORDER.map(function (key) { return { key: key, t: scene.labels[key] }; });
    var target = null;
    if (dir > 0) {
      for (var i = 0; i < stops.length; i++) if (stops[i].t > t + 0.05) { target = stops[i].key; break; }
    } else {
      for (var j = stops.length - 1; j >= 0; j--) if (stops[j].t < t - 0.05) { target = stops[j].key; break; }
    }
    if (target) go(target);
  }

  function markChapter(chapter) {
    chapterLinks.forEach(function (link) {
      if (!link.closest(".rb-chapters")) return;
      if (link.getAttribute("data-chapter-link") === chapter) link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
    });
  }

  // In the plain layout, the chapter whose heading was last passed.
  function plainChapter() {
    var found = "opening";
    ORDER.forEach(function (key) {
      var el = document.getElementById(ANCHORS[key]);
      if (el && key !== "opening" && el.getBoundingClientRect().top < window.innerHeight * 0.4) found = key;
    });
    return found;
  }

  function sync(keepChapter) {
    var possible = bookPossible();
    if (plainToggle) {
      plainToggle.hidden = !possible;
      plainToggle.setAttribute("aria-pressed", String(plain));
    }
    var want = possible && !plain;
    if (want && !scene) {
      build();
      if (keepChapter) {
        ST.refresh();
        go(keepChapter, true);
      }
    } else if (!want && scene) {
      teardown();
      plainHeader();
      if (keepChapter) {
        var el = document.getElementById(ANCHORS[keepChapter]);
        if (el) window.scrollTo(0, keepChapter === "opening" ? 0 : el.getBoundingClientRect().top + window.scrollY - 96);
      }
    }
  }

  /* ---------------------------------------------------------------
     Controls
     --------------------------------------------------------------- */
  // Capture, so this runs before the site-wide anchor handler, which would
  // otherwise scroll to where a page sits in the layout rather than to the
  // point in the scene where it lies open.
  root.addEventListener("click", function (event) {
    var region = event.target.closest("[data-region-link]");
    if (region && directory) directory.setRegion(region.getAttribute("data-region-link"));

    var link = event.target.closest("a[href^='#']");
    if (!link || !scene) return;
    var chapter = chapterForHash(link.getAttribute("href"));
    if (!chapter) return;
    event.preventDefault();
    event.stopPropagation();
    go(chapter);
    try { window.history.replaceState(null, "", link.getAttribute("href")); } catch (e) {}
  }, true);

  root.querySelectorAll("[data-chapter-step]").forEach(function (button) {
    button.addEventListener("click", function () { step(Number(button.getAttribute("data-chapter-step"))); });
  });

  if (plainToggle) {
    plainToggle.addEventListener("click", function () {
      var chapter = scene ? chapterAtTime(scrollTime()) : plainChapter();
      plain = !plain;
      try { window.sessionStorage.setItem(PLAIN_KEY, plain ? "1" : "0"); } catch (e) {}
      sync(chapter);
      plainToggle.focus({ preventScroll: true });
    });
  }

  // The arrow keys turn the page while the book is on screen.
  document.addEventListener("keydown", function (event) {
    if (!scene || event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    var el = event.target;
    if (el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName))) return;
    var y = window.scrollY;
    if (y < scene.st.start - 4 || y > scene.st.end + 4) return;
    event.preventDefault();
    step(event.key === "ArrowRight" ? 1 : -1);
  });

  // Tabbing into a page that is not lying open opens the book at it.
  root.addEventListener("focusin", function (event) {
    if (!scene) return;
    var holder = event.target.closest("[data-chapter]");
    var chapter = holder ? holder.getAttribute("data-chapter") : (next.contains(event.target) ? "next" : null);
    if (!chapter || chapter === "opening") return;
    if (chapterAtTime(scrollTime()) !== chapter) go(chapter);
  });

  // An inbound #cbse-results, #ib-results or #destinations: cirs.js would
  // jump to the page's box; open the book at it instead.
  window.addEventListener("cirs-hash-open", function (event) {
    if (!scene) return;
    var chapter = chapterForHash(window.location.hash);
    if (!chapter) return;
    event.preventDefault();
    go(chapter, true);
  });
  window.addEventListener("hashchange", function () {
    if (scene) go(chapterForHash(window.location.hash));
  });

  // In the plain layout the first section runs on to the directory, so the
  // site header would stay clear over every page. Glass once the headline
  // has gone up under it; the book sets the same classes from paint().
  var headerQueued = false;
  function plainHeader() {
    headerQueued = false;
    if (scene) return;
    var under = intro.getBoundingClientRect().bottom < 90;
    body.classList.toggle("litehead", under);
    body.classList.toggle("rb-paper", under);
  }
  window.addEventListener("scroll", function () {
    if (scene || headerQueued) return;
    headerQueued = true;
    window.requestAnimationFrame(plainHeader);
  }, { passive: true });

  function onQueryChange() { sync(scene ? chapterAtTime(scrollTime()) : null); }
  [roomQuery, motionQuery].forEach(function (query) {
    if (query.addEventListener) query.addEventListener("change", onQueryChange);
    else if (query.addListener) query.addListener(onQueryChange);
  });

  window.addEventListener("pageshow", function (event) {
    if (event.persisted && scene) ST.refresh();
  });
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function () { if (scene) ST.refresh(); });
  }

  sync(null);
  plainHeader();

  /* ---------------------------------------------------------------
     The directory: search and region filters. Updates are immediate —
     no row waits on a scroll reveal, so a match is always visible.
     --------------------------------------------------------------- */
  function initDirectory() {
    var form = document.querySelector(".rb-filters");
    var input = document.getElementById("destinationSearch");
    var list = document.getElementById("destinationList");
    var count = document.getElementById("destinationCount");
    var empty = document.getElementById("destinationEmpty");
    if (!form || !input || !list || !count || !empty) return null;

    var items = Array.prototype.slice.call(list.querySelectorAll("li"));
    var buttons = Array.prototype.slice.call(form.querySelectorAll("[data-filter]"));
    var clear = empty.querySelector("[data-directory-clear]");
    var total = items.length;
    var region = "all";

    function update() {
      var words = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      var visible = 0;
      items.forEach(function (item) {
        var text = item.getAttribute("data-search") || item.textContent.toLocaleLowerCase();
        var show = (region === "all" || item.getAttribute("data-region") === region) &&
          words.every(function (word) { return text.indexOf(word) !== -1; });
        item.hidden = !show;
        if (show) visible += 1;
      });
      count.textContent = visible === total
        ? total + " institutions"
        : visible + " of " + total + (total === 1 ? " institution" : " institutions");
      /* The count is the live region, so it is what a screen reader hears
         when the list empties: the message itself, not just a zero. */
      if (visible === 0) {
        var said = document.createElement("span");
        said.className = "sr-only";
        said.textContent = ". No institutions match your search.";
        count.appendChild(said);
      }
      empty.hidden = visible !== 0;
    }

    function setRegion(key) {
      region = key || "all";
      buttons.forEach(function (button) {
        var active = button.getAttribute("data-filter") === region;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", String(active));
      });
      update();
    }

    buttons.forEach(function (button) {
      button.addEventListener("click", function () { setRegion(button.getAttribute("data-filter")); });
    });
    input.addEventListener("input", update);
    form.addEventListener("submit", function (event) { event.preventDefault(); update(); });
    form.addEventListener("reset", function () {
      window.setTimeout(function () { setRegion("all"); }, 0);
    });
    if (clear) {
      clear.addEventListener("click", function () {
        form.reset();
        input.focus();
      });
    }
    return { setRegion: setRegion };
  }
}());
