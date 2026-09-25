/* CIRS Theatre — the three acts after the opening.

   Four small things, each of which the page does without:

   1. Anand Utsav's stage. With motion allowed, the stage holds while the
      scroll runs it: a darkened frame, then the whole stage opening out of
      a slit of light and coming up to full colour. The script only turns the
      scroll into four numbers; assets/css/theatre.css draws with them.
      Without it the stage is simply the finished photograph.
   2. The houses. Choosing a house from the programme moves to its gallery,
      as the link always would, and also writes the house into the address
      so the place can be shared, preloads the house's first photograph,
      plays a one-second blackout on arrival and moves focus to its heading.
   3. The rail. Marks the house being read.
   4. The viewer. Every photograph is a link to its largest file; a plain
      click opens it in a native modal dialog instead, with the house, the
      count and the caption, arrows and swipes to step, and Escape to close.
      "View all" steps through every house in programme order.

   Nothing here holds the scroll or makes anyone wait for an animation. */
(function () {
  "use strict";

  // Read before boot runs: a deferred script finds the document already
  // parsed and boots at once, below.
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();

  function boot() {
    if (!document.body.classList.contains("theatre")) return;
    if (!reduced) document.body.classList.add("th-motion");
    stage();
    houses();
    viewer();
  }

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function span(p, a, b) { return clamp((p - a) / (b - a)); }
  function ease(t) { return t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

  /* 1. ------------------------------------------------------------ stage */
  function stage() {
    var act = document.querySelector(".th-au");
    if (!act || reduced) return;
    var track = act.querySelector("[data-au-track]");
    var box = act.querySelector(".th-au__stage");
    if (!track || !box) return;
    act.classList.add("is-live");

    var queued = false, last = -1;
    function draw() {
      queued = false;
      var r = track.getBoundingClientRect();
      var run = r.height - window.innerHeight;
      var p = run > 0 ? clamp(-r.top / run) : 1;
      if (Math.abs(p - last) < 0.0005) return;
      last = p;
      // Title first, in the dark; then the slit opens and the light rises;
      // the darkened frame is gone by the time the stage is fully open.
      box.style.setProperty("--type", ease(span(p, .02, .2)).toFixed(4));
      box.style.setProperty("--open", ease(span(p, .18, .66)).toFixed(4));
      box.style.setProperty("--lit", ease(span(p, .28, .8)).toFixed(4));
      box.style.setProperty("--dark", (1 - ease(span(p, .3, .6))).toFixed(4));
      box.style.setProperty("--credit", span(p, .78, .92).toFixed(4));
    }
    function queue() { if (!queued) { queued = true; requestAnimationFrame(draw); } }
    window.addEventListener("scroll", queue, { passive: true });
    window.addEventListener("resize", function () { last = -1; queue(); });
    draw();
  }

  /* 2 and 3. ------------------------------------------------------ houses */
  function houses() {
    var articles = Array.prototype.slice.call(document.querySelectorAll(".th-house"));
    if (!articles.length) return;

    function lead(article) { return article.querySelector(".th-house__leadimg"); }
    // Asking for the first photograph before the scroll gets there is what
    // makes the arrival land on a picture rather than on a grey box.
    function preload(article) { var img = lead(article); if (img) img.loading = "eager"; }

    function arrive(article, focus) {
      preload(article);
      if (!reduced) {
        article.classList.remove("is-arriving");
        void article.offsetWidth;
        article.classList.add("is-arriving");
        window.setTimeout(function () { article.classList.remove("is-arriving"); }, 1500);
      }
      if (focus) {
        var heading = article.querySelector(".th-house__play");
        // The shared scroll carries the page there; focus follows without a
        // second jump, so a keyboard continues from the house it chose.
        if (heading) window.setTimeout(function () { heading.focus({ preventScroll: true }); }, reduced ? 0 : 700);
      }
    }

    document.querySelectorAll("[data-house-link]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        if (e.button > 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        var article = document.getElementById(a.getAttribute("data-house-link"));
        if (!article) return;
        // assets/js/cirs.js scrolls to the anchor and cancels the browser's
        // own jump, which would have written the hash. Write it here.
        if (location.hash !== "#" + article.id) history.pushState(null, "", "#" + article.id);
        arrive(article, true);
      });
    });

    // Arriving with a house already in the address: fetch its photograph now.
    var start = location.hash && document.getElementById(location.hash.slice(1));
    if (start && start.classList.contains("th-house")) preload(start);

    // The rail marks the house under the middle of the window, and a house
    // coming within a screen of view has its first photograph asked for.
    var rail = {};
    document.querySelectorAll(".th-rail a").forEach(function (a) { rail[a.getAttribute("data-house-link")] = a; });
    if (!("IntersectionObserver" in window)) return;
    var current = null;
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var id = e.target.id;
        if (current === id) return;
        if (current && rail[current]) rail[current].removeAttribute("aria-current");
        current = id;
        if (rail[id]) rail[id].setAttribute("aria-current", "true");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    var near = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { preload(e.target); near.unobserve(e.target); }
      });
    }, { rootMargin: "100% 0px 100% 0px" });
    articles.forEach(function (a) { spy.observe(a); near.observe(a); });
  }

  /* 4. ------------------------------------------------------------ viewer */
  function viewer() {
    var box = document.getElementById("thViewer");
    var source = document.getElementById("th-viewer-data");
    if (!box || !source || typeof box.showModal !== "function") return;
    var data;
    try { data = JSON.parse(source.textContent); } catch (err) { return; }

    var stageEl = box.querySelector("[data-th-stage]");
    var titleEl = box.querySelector(".th-viewer__title");
    var subEl = box.querySelector(".th-viewer__sub");
    var countEl = box.querySelector(".th-viewer__count");
    var captionEl = box.querySelector(".th-viewer__caption");
    var list = [], pos = 0, all = false, opener = null, fetched = {};

    function sequence(key) {
      var keys = key === "all" ? data.all : [key];
      var out = [];
      keys.forEach(function (g) {
        (data.groups[g] ? data.groups[g].items : []).forEach(function (_, i) { out.push({ g: g, i: i }); });
      });
      return out;
    }

    function full(item) {
      if (!fetched[item.src]) {
        var im = new Image();
        im.decoding = "async";
        im.src = item.src;
        fetched[item.src] = im;
      }
      return fetched[item.src];
    }

    function show(k) {
      var n = list.length;
      pos = ((k % n) + n) % n;
      var ref = list[pos], group = data.groups[ref.g], item = group.items[ref.i];
      var img = document.createElement("img");
      img.alt = item.alt;
      img.width = item.w;
      img.height = item.h;
      // The large file if it is already here, otherwise the page's own copy
      // at once, swapped for the large one when it has decoded.
      var big = full(item);
      if (big.complete && big.naturalWidth) {
        img.src = item.src;
      } else {
        img.src = item.tile;
        var swap = function () { if (list[pos] === ref) img.src = item.src; };
        if (big.decode) big.decode().then(swap, function () {});
        else big.addEventListener("load", swap);
      }
      stageEl.replaceChildren(img);
      titleEl.textContent = group.label;
      subEl.textContent = group.sub;
      countEl.textContent = (ref.i + 1) + " / " + group.items.length +
        (all ? "  ·  " + (pos + 1) + " of " + n + " in all" : "");
      captionEl.textContent = item.caption;
      [1, -1].forEach(function (d) {
        var r = list[(pos + d + n) % n];
        full(data.groups[r.g].items[r.i]);
      });
    }

    function lock(on) {
      document.documentElement.classList.toggle("th-locked", on);
      // Pauses the site's smooth scroll behind the dialog (cirs.js).
      window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: on } }));
    }

    function open(key, index, from) {
      if (!data.groups[key] && key !== "all") return;
      all = key === "all";
      list = sequence(key);
      if (!list.length) return;
      opener = from || null;
      show(index || 0);
      box.showModal();
      lock(true);
    }

    box.addEventListener("close", function () {
      lock(false);
      stageEl.replaceChildren();
      if (opener) opener.focus({ preventScroll: true });
      opener = null;
    });

    document.querySelectorAll("[data-th-open]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        if (e.button > 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        var parts = a.getAttribute("data-th-open").split(":");
        if (!data.groups[parts[0]]) return;
        e.preventDefault();
        open(parts[0], parseInt(parts[1], 10) || 0, a);
      });
    });

    document.querySelectorAll("[data-th-view]").forEach(function (b) {
      b.hidden = false;
      b.addEventListener("click", function () { open(b.getAttribute("data-th-view"), 0, b); });
    });

    box.querySelectorAll("[data-th-step]").forEach(function (b) {
      b.addEventListener("click", function () { show(pos + parseInt(b.getAttribute("data-th-step"), 10)); });
    });
    box.querySelector("[data-th-close]").addEventListener("click", function () { box.close(); });

    box.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); show(pos + 1); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); show(pos - 1); }
    });

    // A click on the dark around the photograph closes, as it does in most
    // viewers; a click on the photograph itself does nothing.
    stageEl.addEventListener("click", function (e) {
      if (e.target === stageEl && e.timeStamp - swipedAt > 500) box.close();
    });

    // A swipe sideways steps. Vertical movement and pinching stay the
    // browser's (touch-action on the stage).
    var start = null, swipedAt = -1;
    stageEl.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse") return;
      start = { x: e.clientX, y: e.clientY };
    });
    stageEl.addEventListener("pointerup", function (e) {
      if (!start) return;
      var dx = e.clientX - start.x, dy = e.clientY - start.y;
      start = null;
      if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy) * 1.4 && (!window.visualViewport || window.visualViewport.scale <= 1.01)) {
        swipedAt = e.timeStamp;
        show(pos + (dx < 0 ? 1 : -1));
      }
    });
    stageEl.addEventListener("pointercancel", function () { start = null; });
  }
})();
