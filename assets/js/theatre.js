/* CIRS Theatre — the page as a performance.

   Everything here is an addition to a page that already reads in full
   without it. None of it holds the scroll, and nothing makes anyone wait:
   the longest thing that plays is about half a second, and it only ever
   follows a click.

   One owner for the scroll. Every scene that follows the scroll (the film's
   handoff, Act I's stage, the intermission's line, and each reel's edge
   fade) registers with the one listener below, so there is one scroll
   listener and one frame of work per scroll, however many scenes there are.

   1. handoff   Over the last 110vh of the film's run, the film's final frame
                darkens at the edges, one warm line is drawn, the picture goes
                to black, the page names itself and the line opens onto ivory.
                assets/js/filmintro.js still owns the film; this only adds
                a layer and moves the film's own title out (--film-exit).
   2. stage     Act I. The stage holds while the scroll runs it: seven numbers
                that assets/css/theatre.css draws with.
   3. rule      The intermission's line is drawn across the page as it arrives.
   4. programme Hover or focus on an act shows its picture, revealed from a
                clip, beside the list; a click on a mouse carries that picture
                up to fill the window and the page moves behind it.
   5. playbill  The same for the four houses; a click assembles the house's
                opening photograph from four strips before the page moves.
   6. houses    Choosing a house writes it into the address, asks for its
                photographs, and moves focus to its heading. The rail marks
                the house being read.
   7. reels     One finite row of photographs a house. Native horizontal
                scrolling with snap; this only adds the arrows, the arrow keys,
                the count, and the current photograph's scale and shift.
   8. classes   Hover or focus on a production shows the school's own still.
   9. viewer    Every photograph is a link to its largest file; a plain click
                opens it in a native modal dialog, carried there from where it
                was on the page, with the house, the count and the caption,
                arrows and swipes to step, and Escape to close (and carried
                back to where it was, if that is still on screen). "View all"
                steps through every house in programme order.

   No script here holds a list of photographs, titles or dates: it reads
   what tools/theatre.py wrote into the markup. */
(function () {
  "use strict";

  // Read before boot runs: a deferred script finds the document already
  // parsed and boots at once, below.
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var api = {};   // what one part offers another (houses -> playbill)

  function boot() {
    if (!document.body.classList.contains("theatre")) return;
    if (!reduced) document.body.classList.add("th-motion");
    handoff();
    stage();
    rule();
    programme();
    houses();
    playbill();
    reels();
    classes();
    recordings();
    viewer();
  }

  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }
  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function span(p, a, b) { return clamp((p - a) / (b - a)); }
  function ease(t) { return t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
  function smooth(t) { return t * t * (3 - 2 * t); }
  function plain(e) { return e.button === 0 && !(e.metaKey || e.ctrlKey || e.shiftKey || e.altKey); }
  function media(q) { return window.matchMedia(q); }
  function onChange(mq, fn) {
    if (mq.addEventListener) mq.addEventListener("change", fn); else mq.addListener(fn);
  }

  /* The one scroll listener. A scene registers a function that reads its
     own place and writes its own numbers; it is called once a frame, and
     only when the scroll or the window has moved. */
  var scenes = [], queued = false;
  function scene(fn) {
    scenes.push(fn);
    if (scenes.length === 1) {
      window.addEventListener("scroll", queue, { passive: true });
      window.addEventListener("resize", queue);
    }
    fn();
  }
  function queue() { if (!queued) { queued = true; requestAnimationFrame(tick); } }
  function tick() { queued = false; for (var i = 0; i < scenes.length; i++) scenes[i](); }

  /* A style written only when it changes: a frame that moves nothing costs
     nothing. */
  function writer(el) {
    var last = {};
    return function (name, value) {
      if (last[name] === value) return;
      last[name] = value;
      el.style.setProperty(name, value);
    };
  }
  function num(v) { return v.toFixed(4); }

  /* 1. ------------------------------------------------------------- handoff */
  function handoff() {
    var film = $("[data-film]");
    var hand = film && $("[data-th-hand]", film);
    if (!hand || reduced) return;
    var stageEl = $(".film__stage", film);
    var title = $("[data-film-title]", film);
    if (!stageEl || !title) return;

    var START = .72;            // of the film's travel: the last frame is held until here
    var live = false;
    var put = writer(hand), putTitle = writer(title);

    function enable(on) {
      if (on === live) return;
      live = on;
      film.classList.toggle("th-hand-live", on);
      if (!on) {
        ["--g-edge", "--g-trace", "--g-night", "--g-label", "--g-say", "--g-out", "--g-paper"].forEach(function (n) { hand.style.removeProperty(n); });
        title.style.removeProperty("--film-exit");
        put = writer(hand); putTitle = writer(title);
      }
    }

    function draw() {
      // filmintro.js falls back to the still (no film, no motion layer): the
      // composition is then one screen with nothing to hand over.
      if (film.hasAttribute("data-film-still")) { enable(false); return; }
      enable(true);
      var r = film.getBoundingClientRect();
      if (r.bottom < -40 || r.top > window.innerHeight + 40) return;
      var travel = r.height - (stageEl.offsetHeight || window.innerHeight);
      var p = travel > 0 ? clamp(-r.top / travel) : 0;
      var g = span(p, START, 1);
      putTitle("--film-exit", num(smooth(span(g, 0, .16))));
      put("--g-edge",  num(smooth(span(g, 0, .22))));
      put("--g-trace", num(smooth(span(g, .08, .32))));
      put("--g-night", num(smooth(span(g, .12, .44))));
      put("--g-label", num(smooth(span(g, .34, .48))));
      put("--g-say",   num(smooth(span(g, .40, .58))));
      put("--g-out",   num(smooth(span(g, .78, .87))));
      put("--g-paper", num(smooth(span(g, .76, 1))));
    }

    scene(draw);
    new MutationObserver(function () { queue(); }).observe(film, { attributes: true, attributeFilter: ["data-film-still"] });
  }

  /* 2. --------------------------------------------------------------- stage */
  function stage() {
    var act = $(".th-au");
    if (!act || reduced) return;
    var track = $("[data-au-track]", act);
    var box = $(".th-au__stage", act);
    if (!track || !box) return;
    act.classList.add("is-live");
    var put = writer(box);

    scene(function () {
      var r = track.getBoundingClientRect();
      if (r.bottom < -40 || r.top > window.innerHeight + 40) return;
      var run = r.height - (box.offsetHeight || window.innerHeight);
      var p = run > 0 ? clamp(-r.top / run) : 1;
      // One figure in his light first, then the act, then its name; windows
      // open in the dark and widen; the figure gives way and the stage comes
      // up to its own colour; the caption arrives last. Held a beat at the
      // end before the stage lets go.
      put("--pool",   num(ease(span(p, 0, .2))));
      put("--act",    num(ease(span(p, .1, .24))));
      put("--type",   num(ease(span(p, .18, .42))));
      put("--open",   num(ease(span(p, .36, .8))));
      put("--dark",   num(1 - ease(span(p, .46, .74))));
      put("--lit",    num(ease(span(p, .5, .9))));
      put("--credit", num(span(p, .86, .97)));
    });
  }

  /* 3. ---------------------------------------------------------------- rule */
  function rule() {
    var sec = $(".th-inter");
    if (!sec || reduced) return;
    var put = writer(sec);
    scene(function () {
      var r = sec.getBoundingClientRect();
      if (r.bottom < -40 || r.top > window.innerHeight + 40) return;
      var p = clamp((window.innerHeight - r.top) / (window.innerHeight * .95));
      put("--rule", num(ease(span(p, .3, .95))));
    });
  }

  /* A picture revealed from a clip, in the direction the list is read: the
     incoming one wipes over the one that was there. */
  var running = null;
  function reveal(items, from, to) {
    var a = items[from], b = items[to];
    if (!b || a === b) return;
    if (running) { running.finish(); running = null; }
    items.forEach(function (el) { if (el !== a && el !== b) el.classList.remove("is-on"); });
    b.classList.add("is-on");
    if (reduced || !b.animate) { a.classList.remove("is-on"); return; }
    a.style.zIndex = 1; b.style.zIndex = 2;
    var down = to > from;
    var anim = b.animate(
      [{ clipPath: down ? "inset(100% 0 0 0)" : "inset(0 0 100% 0)" }, { clipPath: "inset(0 0 0 0)" }],
      { duration: 340, easing: "cubic-bezier(.22,.61,.36,1)" });
    running = anim;
    var done = function () {
      a.classList.remove("is-on"); a.style.zIndex = ""; b.style.zIndex = "";
      if (running === anim) running = null;
    };
    anim.onfinish = done; anim.oncancel = done;
  }

  /* The picture the pointer was on grows to fill the window while the page
     is moved behind it; then it goes. A matched hand-over, not a route: the
     address changes by a hash and nothing is loaded. */
  var busy = false;
  function veil(build, land) {
    if (busy) return;
    busy = true;
    var v = document.createElement("div");
    v.className = "th-veil";
    document.body.appendChild(v);
    var cleaned = false;
    function clean() { if (cleaned) return; cleaned = true; v.remove(); busy = false; }
    var failsafe = window.setTimeout(clean, 2600);
    build(v, function () {
      // The window is full: move the page, then let the picture go.
      try { land(); } catch (err) { /* the veil must still go */ }
      var out = v.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 420, delay: 60, easing: "cubic-bezier(.4,0,.2,1)", fill: "forwards" });
      out.onfinish = function () { window.clearTimeout(failsafe); clean(); };
      out.oncancel = out.onfinish;
    }, clean);
  }

  function growFrom(sourceImg) {
    return function (v, done, fail) {
      var r = sourceImg.getBoundingClientRect();
      var box = document.createElement("div");
      box.className = "th-veil__box";
      var im = new Image();
      im.alt = "";
      im.src = sourceImg.currentSrc || sourceImg.src;
      im.style.setProperty("--fx", sourceImg.style.getPropertyValue("--fx") || "50%");
      im.style.setProperty("--fy", sourceImg.style.getPropertyValue("--fy") || "50%");
      box.appendChild(im);
      v.appendChild(box);
      var from = { left: r.left + "px", top: r.top + "px", width: r.width + "px", height: r.height + "px" };
      var to = { left: "0px", top: "0px", width: window.innerWidth + "px", height: window.innerHeight + "px" };
      Object.keys(from).forEach(function (k) { box.style[k] = from[k]; });
      var a = box.animate([from, to], { duration: 520, easing: "cubic-bezier(.65,0,.35,1)", fill: "forwards" });
      a.onfinish = done;
      a.oncancel = fail;
    };
  }

  function assembleFrom(src, fx, fy) {
    return function (v, done) {
      var W = window.innerWidth, H = window.innerHeight, n = 4, w = W / n;
      var lifts = [-.42, .34, -.26, .46];
      var anims = [];
      for (var i = 0; i < n; i++) {
        var f = document.createElement("div");
        f.className = "th-veil__frag";
        f.style.left = (i * w) + "px";
        f.style.width = (w + 1) + "px";
        var im = new Image();
        im.alt = ""; im.src = src;
        im.style.setProperty("--fx", fx); im.style.setProperty("--fy", fy);
        im.style.width = W + "px";
        im.style.left = (-i * w) + "px";
        f.appendChild(im);
        v.appendChild(f);
        anims.push(f.animate(
          [{ transform: "translateY(" + (lifts[i] * H) + "px)", opacity: 0 },
           { transform: "translateY(" + (lifts[i] * H * .35) + "px)", opacity: 1, offset: .35 },
           { transform: "translateY(0)", opacity: 1 }],
          { duration: 620, delay: i * 55, easing: "cubic-bezier(.22,.61,.36,1)", fill: "both" }));
      }
      anims[n - 1].onfinish = done;
    };
  }

  /* Moves the page to an act or a house and writes it into the address. */
  function land(target, hash) {
    var y = target.getBoundingClientRect().top + (window.scrollY || window.pageYOffset || 0);
    window.scrollTo({ top: y, behavior: "instant" });
    if (location.hash !== hash) history.pushState(null, "", hash);
  }

  /* 4. ------------------------------------------------------------ programme */
  function programme() {
    var body = $("[data-programme]");
    if (!body) return;
    var rows = $$(".th-prog__row", body);
    var slides = $$(".th-prog__slide", body);
    var fine = media("(min-width: 1024px) and (hover: hover) and (pointer: fine)");
    var current = 0;

    function show(i) {
      if (!fine.matches || i === current) return;
      reveal(slides, current, i);
      current = i;
    }
    var warmed = false;
    function warm() {
      if (warmed) return;
      warmed = true;
      $$("img", body).forEach(function (im) { im.loading = "eager"; });
    }
    rows.forEach(function (row, i) {
      row.addEventListener("pointerenter", function () { warm(); show(i); });
      row.addEventListener("focus", function () { warm(); show(i); });
    });

    // A click with a mouse: the still grows to fill the window, the page
    // moves, the still goes. Anything else (touch, keys, reduced motion, a
    // modified click) is the plain link, which assets/js/cirs.js scrolls.
    body.addEventListener("click", function (e) {
      var row = e.target.closest && e.target.closest(".th-prog__row");
      if (!row || !plain(e) || !fine.matches || reduced) return;
      var i = rows.indexOf(row);
      var img = $("img", slides[i]);
      var target = document.getElementById(row.getAttribute("href").slice(1));
      if (!img || !target || !img.complete || !img.naturalWidth) return;
      e.preventDefault();
      e.stopPropagation();
      var shown = slides[i];
      // The still must be the one on screen; if the pointer has not been
      // over this row, it is not, and the plain scroll is the honest answer.
      if (!shown.classList.contains("is-on")) { warm(); show(i); }
      veil(growFrom(img), function () {
        land(target, "#" + target.id);
        var heading = $("h2", target);
        if (heading) { heading.setAttribute("tabindex", "-1"); heading.focus({ preventScroll: true }); }
      });
    }, true);
  }

  /* 6. ---------------------------------------------------------------- houses */
  function houses() {
    var articles = $$(".th-house");
    if (!articles.length) return;

    function lead(article) { return $(".th-house__leadimg", article); }
    // Asking for the first photograph before the scroll gets there is what
    // makes the arrival land on a picture rather than on a grey box.
    function preload(article) { var im = lead(article); if (im) im.loading = "eager"; }

    function arrive(article, focus, quiet) {
      preload(article);
      if (!reduced) {
        article.classList.remove("is-arriving", "is-arriving-quiet");
        void article.offsetWidth;
        article.classList.add(quiet ? "is-arriving-quiet" : "is-arriving");
        window.setTimeout(function () { article.classList.remove("is-arriving", "is-arriving-quiet"); }, 1500);
      }
      if (focus) {
        var heading = $(".th-house__play", article);
        // The shared scroll carries the page there; focus follows without a
        // second jump, so a keyboard continues from the house it chose.
        if (heading) window.setTimeout(function () { heading.focus({ preventScroll: true }); }, reduced || quiet ? 0 : 700);
      }
    }
    api.arrive = arrive;
    api.preload = preload;
    api.lead = lead;

    $$("[data-house-link]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        if (!plain(e)) return;
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
    $$(".th-rail a").forEach(function (a) { rail[a.getAttribute("data-house-link")] = a; });
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

  /* 5. ---------------------------------------------------------------- playbill */
  function playbill() {
    var body = $("[data-playbill]");
    if (!body) return;
    var list = $(".th-bill__list", body);
    var rows = $$(".th-bill__row", body);
    var imgs = $$(".th-bill__img", body);
    var caps = $$(".th-bill__cap", body);
    var fine = media("(min-width: 900px) and (hover: hover) and (pointer: fine)");
    var current = 0;

    function paint(i) {
      rows.forEach(function (r, k) { r.classList.toggle("is-active", k === i); });
      caps.forEach(function (c, k) { c.classList.toggle("is-on", k === i); });
    }
    function activate(i) {
      if (!fine.matches) return;
      var article = document.getElementById(rows[i].getAttribute("data-house-link"));
      if (article && api.preload) api.preload(article);
      if (imgs[i]) imgs[i].loading = "eager";
      if (i === current) return;
      paint(i);
      reveal(imgs, current, i);
      current = i;
    }
    function set() {
      list.classList.toggle("is-live", fine.matches);
      if (fine.matches) paint(current);
      else rows.forEach(function (r) { r.classList.remove("is-active"); });
    }
    set();
    onChange(fine, set);

    rows.forEach(function (row, i) {
      row.addEventListener("pointerenter", function () { activate(i); });
      row.addEventListener("focus", function () { activate(i); });
    });

    // A click with a mouse: the house's opening photograph is put together
    // from four strips while the page moves behind it. The plain link,
    // and the shared handler that scrolls it, are everything else.
    list.addEventListener("click", function (e) {
      var row = e.target.closest && e.target.closest(".th-bill__row");
      if (!row || !plain(e) || !fine.matches || reduced) return;
      var article = document.getElementById(row.getAttribute("data-house-link"));
      var im = article && api.lead && api.lead(article);
      if (!article || !im) return;
      e.preventDefault();
      e.stopPropagation();
      api.preload(article);
      // The largest cut the page offers for a window this wide.
      var src = im.currentSrc || im.src;
      var cands = (im.getAttribute("srcset") || "").split(",").map(function (s) { return s.trim().split(/\s+/); });
      var want = window.innerWidth * (window.devicePixelRatio > 1 ? 1.3 : 1);
      var pick = cands.filter(function (c) { return parseInt(c[1], 10) >= want; })[0] || cands[cands.length - 1];
      if (pick && pick[0]) src = pick[0];
      var probe = new Image();
      probe.src = src;
      var go = function () {
        veil(assembleFrom(src, im.style.getPropertyValue("--fx") || "50%", im.style.getPropertyValue("--fy") || "50%"), function () {
          land(article, "#" + article.id);
          api.arrive(article, true, true);
        });
      };
      // Wait for the photograph, but not for long: a slow connection gets
      // the plain scroll rather than a wait.
      var settled = false;
      function once(fn) { if (settled) return; settled = true; fn(); }
      (probe.decode ? probe.decode() : Promise.resolve()).then(function () { once(go); }, function () { once(plainGo); });
      window.setTimeout(function () { once(plainGo); }, 900);
      function plainGo() {
        land(article, "#" + article.id);
        api.arrive(article, true);
      }
    }, true);
  }

  /* 7. ------------------------------------------------------------------ reels */
  function reels() {
    var all = $$("[data-reel]");
    if (!all.length) return;
    var wide = media("(min-width: 761px)");

    all.forEach(function (root) {
      var viewport = $("[data-reel-track]", root);
      var slides = $$(".th-reel__slide", root);
      var now = $("[data-reel-now]", root);
      var ctl = $("[data-reel-ctl]", root);
      var set = $(".th-reel__set", root);
      var prev = $("[data-reel-step='-1']", root), next = $("[data-reel-step='1']", root);
      if (!viewport || !slides.length) return;
      var pending = false, visible = false;

      function centre(s) { return s.offsetLeft + s.offsetWidth / 2; }
      function at() { return viewport.scrollLeft + viewport.clientWidth / 2; }
      function nearest() {
        var c = at(), best = 0, gap = Infinity;
        slides.forEach(function (s, i) { var d = Math.abs(centre(s) - c); if (d < gap) { gap = d; best = i; } });
        return best;
      }
      function pad(n) { return n < 10 ? "0" + n : String(n); }

      function update() {
        pending = false;
        if (!wide.matches) return;
        var c = at(), best = 0, gap = Infinity;
        slides.forEach(function (s, i) {
          var d = (centre(s) - c) / (s.offsetWidth * 1.05);
          var a = Math.abs(d);
          if (a < gap) { gap = a; best = i; }
          if (reduced) return;
          if (a > 2.2) { s.style.removeProperty("--near"); s.style.removeProperty("--dx"); return; }
          s.style.setProperty("--near", num(clamp(1 - a)));
          s.style.setProperty("--dx", num(Math.max(-1.2, Math.min(1.2, d))));
        });
        var link = $("a[data-th-open]", slides[best]);
        var index = link ? parseInt(link.getAttribute("data-th-open").split(":")[1], 10) : best + 1;
        if (now) now.textContent = pad(index + 1);
        if (prev) prev.disabled = best === 0;
        if (next) next.disabled = best === slides.length - 1;
      }
      function ask() { if (!pending) { pending = true; requestAnimationFrame(update); } }

      function go(i) {
        i = Math.max(0, Math.min(slides.length - 1, i));
        viewport.scrollTo({ left: centre(slides[i]) - viewport.clientWidth / 2, behavior: reduced ? "auto" : "smooth" });
      }
      function step(d) { go(nearest() + d); }

      viewport.addEventListener("scroll", ask, { passive: true });
      viewport.addEventListener("keydown", function (e) {
        if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
        else if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
      });
      $$("[data-reel-step]", root).forEach(function (b) {
        b.addEventListener("click", function () { step(parseInt(b.getAttribute("data-reel-step"), 10)); });
      });

      // Room either side of the first and last photograph, so each can sit
      // at the middle like the rest.
      function room() {
        var track = viewport.firstElementChild;
        if (!track || !wide.matches) return;
        var w = viewport.clientWidth;
        track.style.setProperty("--pad-s", Math.max(0, (w - slides[0].offsetWidth) / 2) + "px");
        track.style.setProperty("--pad-e", Math.max(0, (w - slides[slides.length - 1].offsetWidth) / 2) + "px");
      }
      function mode() {
        if (ctl) ctl.hidden = !wide.matches;
        // Wide: the reel is open and scrolls. Narrow: a column, folded away
        // until it is asked for.
        if (set) set.open = wide.matches;
        if (wide.matches) { room(); viewport.scrollLeft = 0; update(); }
        else slides.forEach(function (s) { s.style.removeProperty("--near"); s.style.removeProperty("--dx"); });
      }
      mode();
      onChange(wide, mode);
      window.addEventListener("resize", function () { room(); ask(); });
      // A reel nowhere near the window has nothing to keep up to date.
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) ask(); }, { rootMargin: "50% 0px" }).observe(root);
      }
    });
  }

  /* 8. ---------------------------------------------------------------- classes */
  function classes() {
    var body = $("[data-cp]");
    var pane = body && $("[data-cp-preview]", body);
    if (!pane) return;
    var img = $("img", pane), cap = $(".th-cp__still", pane);
    var rows = $$(".th-prod", body);
    var fine = media("(min-width: 1100px) and (hover: hover) and (pointer: fine)");
    var shown = null, token = 0;

    function show(row) {
      if (!fine.matches || !row || shown === row) return;
      shown = row;
      var mine = ++token;
      var still = $(".th-prod__still", row);
      var src = still && still.getAttribute("src");
      if (!src) return;
      cap.textContent = row.getAttribute("data-thumb-label") + " · " + row.getAttribute("data-len") + " · a still from the recording";
      if (img.getAttribute("src") === src) return;
      var probe = new Image();
      probe.onload = function () {
        if (mine !== token) return;
        img.src = src;
        if (!reduced && img.animate) img.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 260, easing: "ease-out" });
      };
      probe.src = src;
    }
    rows.forEach(function (row) {
      row.addEventListener("pointerenter", function () { show(row); });
      row.addEventListener("focus", function () { show(row); });
    });
    if (rows[0]) show(rows[0]);
    onChange(fine, function () { if (fine.matches && rows[0]) show(shown || rows[0]); });
  }

  /* 8b. ------------------------------------------------------- recordings
     The shared player (cirs.js) gives focus back to the link it was opened
     from, then steps back one history entry. When the address carries a
     house (#vasistha) that step is a move to a fragment, and the browser
     lets go of the focus it was handed. Hand it back once that has settled. */
  function recordings() {
    var box = $("#lightbox");
    if (!box) return;
    var from = null, timer = 0;
    document.addEventListener("click", function (e) {
      var t = e.target.closest && e.target.closest("[data-video]");
      if (t) from = t;
    }, true);
    box.addEventListener("close", function () {
      var el = from;
      window.clearTimeout(timer);
      timer = window.setTimeout(function () {
        if (el && el.isConnected && !box.open && (!document.activeElement || document.activeElement === document.body)) {
          el.focus({ preventScroll: true });
        }
      }, 320);
    });
  }

  /* 9. ------------------------------------------------------------------ viewer */
  function viewer() {
    var box = $("#thViewer");
    var source = $("#th-viewer-data");
    if (!box || !source || typeof box.showModal !== "function") return;
    var data;
    try { data = JSON.parse(source.textContent); } catch (err) { return; }

    var stageEl = $("[data-th-stage]", box);
    var titleEl = $(".th-viewer__title", box);
    var subEl = $(".th-viewer__sub", box);
    var countEl = $(".th-viewer__count", box);
    var captionEl = $(".th-viewer__caption", box);
    var list = [], pos = 0, all = false, opener = null, fetched = {}, openedAt = -1, closing = false;

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

    /* The photograph is carried between the page and the viewer, so the eye
       never loses it. The viewer shows the photograph whole; the page often
       shows a crop of it. The keyframes therefore scale the whole photograph
       until it covers the page's frame and clip it to that frame, then
       release both: what is seen at the start is exactly what was on the
       page. */
    function carry(frame, im, opening) {
      if (reduced || !im.animate || !frame) return null;
      var fr = frame.getBoundingClientRect();
      var to = im.getBoundingClientRect();
      var vw = window.innerWidth, vh = window.innerHeight;
      if (!to.width || !to.height || !fr.width || fr.bottom < 0 || fr.top > vh || fr.right < 0 || fr.left > vw) return null;
      var src = $("img", frame);
      var fx = src ? parseFloat(src.style.getPropertyValue("--fx")) / 100 : .5;
      var fy = src ? parseFloat(src.style.getPropertyValue("--fy")) / 100 : .5;
      if (isNaN(fx)) fx = .5;
      if (isNaN(fy)) fy = .5;
      var s = Math.max(fr.width / to.width, fr.height / to.height);
      var bw = fr.width / s, bh = fr.height / s;
      var cx = Math.max(0, (to.width - bw) * fx), cy = Math.max(0, (to.height - bh) * fy);
      var tx = fr.left - to.left - s * cx, ty = fr.top - to.top - s * cy;
      var away = {
        transformOrigin: "0 0",
        transform: "translate(" + tx + "px," + ty + "px) scale(" + s + ")",
        clipPath: "inset(" + cy + "px " + Math.max(0, to.width - cx - bw) + "px " + Math.max(0, to.height - cy - bh) + "px " + cx + "px)"
      };
      var here = { transformOrigin: "0 0", transform: "none", clipPath: "inset(0px 0px 0px 0px)" };
      return im.animate(opening ? [away, here] : [here, away],
        { duration: opening ? 520 : 400, easing: "cubic-bezier(.65,0,.35,1)", fill: opening ? "none" : "forwards" });
    }

    function open(key, index, from) {
      if (!data.groups[key] && key !== "all") return;
      all = key === "all";
      list = sequence(key);
      if (!list.length) return;
      opener = from || null;
      show(index || 0);
      openedAt = pos;
      box.showModal();
      lock(true);
      var im = $("img", stageEl);
      if (im && opener && opener.matches("a.th-photo")) carry(opener, im, true);
    }

    function finish() {
      closing = false;
      box.classList.remove("is-closing");
      box.close();
    }
    // Back to where the photograph was, if that is on screen; otherwise it
    // simply lets go.
    function dismiss() {
      if (closing) return;
      if (reduced) { box.close(); return; }
      closing = true;
      box.classList.add("is-closing");
      var im = $("img", stageEl);
      var link = opener;
      if (pos !== openedAt && list[pos]) {
        // The visitor has stepped on: go to the photograph now shown, if the
        // page has it in view.
        var ref = list[pos];
        link = $("a.th-photo[data-th-open='" + ref.g + ":" + ref.i + "']") || null;
      }
      var a = im && link && link.matches("a.th-photo") ? carry(link, im, false) : null;
      if (a) { a.onfinish = finish; a.oncancel = finish; }
      else window.setTimeout(finish, 320);
    }

    box.addEventListener("close", function () {
      lock(false);
      stageEl.replaceChildren();
      closing = false;
      box.classList.remove("is-closing");
      if (opener) opener.focus({ preventScroll: true });
      opener = null;
    });
    // Escape asks to close; let it take the same road out as the button.
    box.addEventListener("cancel", function (e) { e.preventDefault(); dismiss(); });

    $$("[data-th-open]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        if (!plain(e)) return;
        var parts = a.getAttribute("data-th-open").split(":");
        if (!data.groups[parts[0]]) return;
        e.preventDefault();
        open(parts[0], parseInt(parts[1], 10) || 0, a);
      });
    });

    $$("[data-th-view]").forEach(function (b) {
      b.hidden = false;
      b.addEventListener("click", function () { open(b.getAttribute("data-th-view"), 0, b); });
    });

    $$("[data-th-step]", box).forEach(function (b) {
      b.addEventListener("click", function () { show(pos + parseInt(b.getAttribute("data-th-step"), 10)); });
    });
    $("[data-th-close]", box).addEventListener("click", dismiss);

    box.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); show(pos + 1); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); show(pos - 1); }
    });

    // A click on the dark around the photograph closes, as it does in most
    // viewers; a click on the photograph itself does nothing.
    stageEl.addEventListener("click", function (e) {
      if (e.target === stageEl && e.timeStamp - swipedAt > 500) dismiss();
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

  // Last, so every var above has been given its value: a deferred script
  // finds the document already parsed and boots at once.
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
