/* Creative Writing — "The Living Manuscript".
   The page is complete without this file: every edition, poem, link and
   download is in the HTML. This adds, in order of the page:
     the hero's words, which lean towards a pointer and gather into the title
     the collection switch (All / Junior / Senior) as tabs
     entrances as each section is reached (never before)
     the cover-to-edition transition
     "Give me a line"
     the afterword's typing
     the edition reader: one poem at a time, index, progress, drawer
   html.cw-js was set in the head so nothing is drawn and then hidden;
   html.cw-still (reduced motion) leaves every piece at rest. */
(function () {
  "use strict";

  var body = document.body;
  if (!body || !body.classList.contains("cwriting")) return;
  window.__cwBooted = true;

  var root = document.documentElement;
  var reduceQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (reduceQuery.matches) root.classList.add("cw-still");
  var still = root.classList.contains("cw-still");
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

  /* Scroll through the site's own engine (Lenis) when it is running. */
  function scrollToY(y, duration) {
    var handled = !window.dispatchEvent(new CustomEvent("cirs-section-scroll", {
      cancelable: true, detail: { top: y, duration: duration || 0.9 }
    }));
    if (!handled) window.scrollTo({ top: y, behavior: still ? "auto" : "smooth" });
  }
  function refreshTriggers() {
    if (window.ScrollTrigger) window.ScrollTrigger.refresh();
  }

  /* ---------------------------------------------------------- entrances */
  var observer = null;
  function reveal(el) { el.classList.add("is-in"); }
  function watch(els) {
    if (still || !("IntersectionObserver" in window)) { els.forEach(reveal); return; }
    if (!observer) {
      observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          reveal(entry.target);
          observer.unobserve(entry.target);
        });
      }, { rootMargin: "0px 0px -12% 0px", threshold: 0.01 });
    }
    els.forEach(function (el) { if (!el.classList.contains("is-in")) observer.observe(el); });
  }
  function staggerWall(scope) {
    $$(".cw-wall", scope).forEach(function (wall) {
      $$(".cw-wall__item", wall).forEach(function (item, i) {
        item.style.setProperty("--d", (i % 2) * 0.14 + "s");
      });
    });
  }

  /* ---------------------------------------------------------- hero */
  function hero() {
    var el = $("[data-cw-hero]");
    if (!el) return;
    var words = $$(".cw-word", el);
    var title = $("[data-cw-title]", el);
    var caret = $("[data-cw-caret]", el);
    var afters = $$("[data-cw-after]", el);
    afters.forEach(function (a, i) { a.style.setProperty("--d", (0.1 + i * 0.22) + "s"); });

    if (still || !title || !caret || !words.length) {
      el.classList.add("is-ready");
      if (!still) el.classList.add("is-assembled");
      return;
    }
    // Arriving part-way down the page (a restored scroll, a link to a
    // section): the title is simply there.
    if (window.scrollY > el.offsetHeight * 0.4) {
      el.classList.add("is-ready", "is-assembled");
      scrollOut();
      return;
    }
    el.classList.add("is-blank", "is-ready");

    /* Words lean towards a nearby pointer, and drift a little on touch. */
    var states = words.map(function (w) { return { el: w, x: 0, y: 0, tx: 0, ty: 0, hx: 0, hy: 0 }; });
    var pointer = { x: -1e5, y: -1e5 };
    var running = false, assembled = false, visible = true, frame = 0;
    function measure() {
      states.forEach(function (s) {
        var r = s.el.getBoundingClientRect();
        s.hx = r.left + r.width / 2 - s.x;
        s.hy = r.top + r.height / 2 - s.y + window.scrollY;
      });
    }
    function tick() {
      frame = 0;
      var moving = false, scroll = window.scrollY, R = Math.max(180, Math.min(window.innerWidth, 1400) * 0.2);
      states.forEach(function (s) {
        var dx = pointer.x - s.hx, dy = pointer.y - (s.hy - scroll);
        var d = Math.sqrt(dx * dx + dy * dy);
        if (d < R && d > 0) {
          var f = Math.pow(1 - d / R, 2), pull = Math.min(26, d * 0.22);
          s.tx = dx / d * pull * f * 1.6; s.ty = dy / d * pull * f * 1.6;
        } else { s.tx = 0; s.ty = 0; }
        s.x += (s.tx - s.x) * 0.12; s.y += (s.ty - s.y) * 0.12;
        if (Math.abs(s.tx - s.x) > 0.1 || Math.abs(s.ty - s.y) > 0.1) moving = true;
        s.el.style.setProperty("--mx", s.x.toFixed(2) + "px");
        s.el.style.setProperty("--my", s.y.toFixed(2) + "px");
      });
      if (moving && !assembled && visible) frame = requestAnimationFrame(tick);
      else running = false;
    }
    function kick() { if (!running && !assembled && visible) { running = true; frame = requestAnimationFrame(tick); } }
    function onPointer(e) {
      if (e.pointerType === "touch" && e.type === "pointermove" && !e.isPrimary) return;
      pointer.x = e.clientX; pointer.y = e.clientY; kick();
    }
    function onLeave() { pointer.x = -1e5; pointer.y = -1e5; kick(); }
    measure();
    window.addEventListener("resize", measure, { passive: true });
    el.addEventListener("pointermove", onPointer, { passive: true });
    el.addEventListener("pointerdown", onPointer, { passive: true });
    el.addEventListener("pointerleave", onLeave, { passive: true });
    if (!finePointer) el.classList.add("is-drifting");
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting; }).observe(el);
    }

    /* The gathering: each letter of the title is taken from the nearest
       scattered word that holds it, and flies to its place. */
    function assemble() {
      if (assembled) return;
      assembled = true;
      cancelAnimationFrame(frame);
      window.clearTimeout(timer);
      ["wheel", "touchmove", "keydown", "scroll"].forEach(function (t) { window.removeEventListener(t, early); });

      var box = el.getBoundingClientRect();
      var c0 = caret.getBoundingClientRect();
      el.classList.remove("is-blank", "is-drifting");
      var c1 = caret.getBoundingClientRect();

      var layer = document.createElement("div");
      layer.className = "cw-hero__fly";
      layer.setAttribute("aria-hidden", "true");
      el.appendChild(layer);

      var sources = [];
      words.forEach(function (w) {
        var rot = parseFloat(getComputedStyle(w).getPropertyValue("--r")) || 0;
        var size = parseFloat(getComputedStyle(w).fontSize) || 20;
        $$(".cw-l", w).forEach(function (l) {
          var r = l.getBoundingClientRect();
          sources.push({ el: l, ch: l.textContent.toLowerCase(), r: r, rot: rot, size: size, used: false });
        });
      });
      var targets = $$(".cw-ch", title);
      var last = 0;
      var tone = getComputedStyle(root);
      var mute = tone.getPropertyValue("--ink-mute").trim() || "#5F5E58";
      var ink = tone.getPropertyValue("--ink").trim() || "#1F1F1B";
      targets.forEach(function (t, i) {
        var tr = t.getBoundingClientRect();
        var ch = t.textContent.toLowerCase();
        var best = null, bestD = Infinity;
        sources.forEach(function (s) {
          if (s.used || s.ch !== ch) return;
          var dx = s.r.left - tr.left, dy = s.r.top - tr.top, d = dx * dx + dy * dy;
          if (d < bestD) { bestD = d; best = s; }
        });
        var delay = 120 + i * 42 + Math.random() * 90;
        var dur = 1150;
        if (!best) {
          window.setTimeout(function () { t.classList.add("is-lit"); }, delay + dur * 0.8);
          return;
        }
        best.used = true;
        // Set at the title's size and scaled down to the word's, so the
        // letter is drawn sharp when it arrives rather than enlarged.
        var tSize = parseFloat(getComputedStyle(t).fontSize) || 100;
        var k = tSize / best.size;
        var fly = document.createElement("span");
        fly.className = "cw-fly";
        fly.textContent = best.el.textContent;
        fly.style.fontSize = tSize + "px";
        layer.appendChild(fly);
        var fw = fly.offsetWidth, fh = fly.offsetHeight;
        var sx = best.r.left + best.r.width / 2 - box.left, sy = best.r.top + best.r.height / 2 - box.top;
        fly.style.left = (sx - fw / 2) + "px";
        fly.style.top = (sy - fh / 2) + "px";
        best.el.style.opacity = "0";
        var dx = tr.left + tr.width / 2 - box.left - sx, dy = tr.top + tr.height / 2 - box.top - sy;
        var anim = fly.animate([
          { transform: "translate(0,0) rotate(" + best.rot + "deg) scale(" + (1 / k) + ")", opacity: 1, color: mute },
          { transform: "translate(" + dx + "px," + dy + "px) rotate(0deg) scale(1)", opacity: 1, color: ink, offset: 0.86 },
          { transform: "translate(" + dx + "px," + dy + "px) rotate(0deg) scale(1)", opacity: 0, color: ink }
        ], { duration: dur, delay: delay, easing: "cubic-bezier(.7,0,.2,1)", fill: "both" });
        window.setTimeout(function () { t.classList.add("is-lit"); }, delay + dur * 0.78);
        last = Math.max(last, delay + dur);
        void anim;
      });
      // Every letter no word gave away fades where it stood.
      sources.forEach(function (s) {
        if (s.used) return;
        s.el.animate([{ opacity: 1, transform: "none", filter: "blur(0)" },
                      { opacity: 0, transform: "translateY(-10px)", filter: "blur(3px)" }],
                     { duration: 700, delay: Math.random() * 380, easing: "ease-out", fill: "forwards" });
      });
      // The cursor moves from the middle of the page to the end of the title.
      caret.animate([
        { transform: "translate(" + (c0.left - c1.left) + "px," + (c0.top - c1.top) + "px) scaleY(" + (c0.height / Math.max(c1.height, 1)) + ")" },
        { transform: "none" }
      ], { duration: 1300, delay: 200, easing: "cubic-bezier(.7,0,.2,1)", fill: "backwards" });

      window.setTimeout(function () {
        el.classList.add("is-assembled");
        layer.remove();
        // After the subtitle has finished arriving, so the scrubbed exit
        // starts from what is on screen.
        window.setTimeout(scrollOut, 1900);
      }, Math.max(last, 1500) + 60);
    }
    function early(e) {
      if (e.type === "keydown" && !/^(ArrowDown|PageDown|Space| |End)$/.test(e.key)) return;
      assemble();
    }
    ["wheel", "touchmove", "keydown", "scroll"].forEach(function (t) {
      window.addEventListener(t, early, { passive: true });
    });
    var timer = window.setTimeout(assemble, 1500);

    /* As the hero leaves, CREATIVE and WRITING part to either side: the
       page opens into its two collections. */
    function scrollOut() {
      if (still || !window.gsap || !window.ScrollTrigger) return;
      var lines = $$(".cw-hero__line", el);
      var trigger = { trigger: el, start: "top top", end: "bottom top", scrub: 0.6 };
      if (lines[0]) gsap.to(lines[0], { xPercent: -16, ease: "none", scrollTrigger: trigger });
      if (lines[1]) gsap.to(lines[1], { xPercent: 16, ease: "none", scrollTrigger: trigger });
      var fade = { trigger: el, start: "top top", end: "45% top", scrub: 0.4 };
      gsap.fromTo($$(".cw-hero__sub, .cw-hero__meta", el), { opacity: 1, y: 0 },
        { opacity: 0, y: -20, ease: "none", immediateRender: false, scrollTrigger: fade });
      gsap.fromTo($$(".cw-hero__cue", el), { opacity: 1 },
        { opacity: 0, ease: "none", immediateRender: false, scrollTrigger: fade });
    }
  }

  function splitRule() {
    var split = $("[data-cw-split]");
    if (!split) return;
    watch($$(".cw-split__half", split));
    var rule = $("[data-cw-rule]", split);
    if (!rule || still || !window.gsap || !window.ScrollTrigger) return;
    gsap.fromTo(rule, { "--rule": 0 }, {
      "--rule": 1, ease: "none",
      scrollTrigger: { trigger: split, start: "top 85%", end: "top 15%", scrub: 0.5 }
    });
  }

  /* ---------------------------------------------------------- collections */
  function collections() {
    var page = $("[data-cw-page]");
    var sw = $("[data-cw-switch]");
    if (!page || !sw) return;
    var tabs = $$("[data-cw-pick]", sw);
    var panels = $$("[data-cw-panel]");
    var thumb = $(".cw-switch__thumb", sw);
    var active = page.getAttribute("data-cw-active") || "all";
    var busy = false;

    sw.setAttribute("role", "tablist");
    sw.removeAttribute("aria-label");
    sw.setAttribute("aria-label", "Collections");
    tabs.forEach(function (t) {
      var key = t.getAttribute("data-cw-pick");
      t.id = "cw-tab-" + key;
      t.setAttribute("role", "tab");
      t.removeAttribute("aria-current");
      t.setAttribute("aria-selected", String(key === active));
      t.tabIndex = key === active ? 0 : -1;
    });
    panels.forEach(function (p) {
      p.setAttribute("role", "tabpanel");
      p.setAttribute("aria-labelledby", "cw-tab-" + p.getAttribute("data-cw-panel"));
    });

    function place() {
      var t = tabs.filter(function (x) { return x.getAttribute("data-cw-pick") === active; })[0];
      if (!t || !thumb) return;
      sw.style.setProperty("--thumb-x", t.offsetLeft + "px");
      sw.style.setProperty("--thumb-w", t.offsetWidth + "px");
      sw.classList.add("is-live");
    }
    place();
    window.addEventListener("resize", place, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(place);

    function panelFor(key) { return panels.filter(function (p) { return p.getAttribute("data-cw-panel") === key; })[0]; }
    function wire(panel) {
      staggerWall(panel);
      watch($$("[data-cw-reveal], .cw-wall__item, .cw-featured", panel));
    }
    panels.forEach(function (p) { if (!p.hidden) wire(p); });

    function select(key, opts) {
      opts = opts || {};
      if (key === active || busy) { if (opts.scroll) toEditions(); return; }
      var from = panelFor(active), to = panelFor(key);
      if (!to) return;
      active = key;
      page.setAttribute("data-cw-active", key);
      tabs.forEach(function (t) {
        var on = t.getAttribute("data-cw-pick") === key;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
      });
      place();
      updateUrl(key);
      function swap() {
        if (from) { from.hidden = true; from.classList.remove("is-leaving"); }
        to.hidden = false;
        if (!still) {
          to.classList.add("is-entering");
          window.setTimeout(function () { to.classList.remove("is-entering"); }, 750);
        }
        wire(to);
        busy = false;
        refreshTriggers();
        if (opts.scroll) toEditions();
      }
      if (still || !from) { swap(); return; }
      busy = true;
      from.classList.add("is-leaving");
      window.setTimeout(swap, 220);
    }
    function toEditions() {
      var target = $("#editions");
      if (target) scrollToY(target.getBoundingClientRect().top + window.scrollY - 20, 1.1);
    }
    // /creative-writing/junior and /senior are siblings: the address can
    // follow the switch between them without moving the page's base. On the
    // root page it stays, since every relative link is written from there.
    function updateUrl(key) {
      if (key === "all" || !window.history.replaceState) return;
      var m = window.location.pathname.match(/\/creative-writing\/(junior|senior)(\.html)?$/);
      if (!m) return;
      window.history.replaceState(null, "", key + (m[2] || "") + window.location.search + "#editions");
    }

    sw.addEventListener("click", function (e) {
      var t = e.target.closest("[data-cw-pick]");
      if (!t) return;
      e.preventDefault();
      select(t.getAttribute("data-cw-pick"));
    });
    sw.addEventListener("keydown", function (e) {
      var i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      var next = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (next === undefined) return;
      e.preventDefault();
      next = (next + tabs.length) % tabs.length;
      tabs[next].focus();
      select(tabs[next].getAttribute("data-cw-pick"));
    });
    // The two halves of the split open their collection here.
    $$(".cw-split [data-cw-pick]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
        e.preventDefault();
        e.stopPropagation();
        select(a.getAttribute("data-cw-pick"), { scroll: true });
      }, true);
    });
  }

  /* ---------------------------------------------------------- cover → edition */
  function coverTransitions() {
    if (still) return;
    var crossDocument = "onpagereveal" in window;
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("[data-cw-cover], [data-cw-cover-link]");
      if (!a || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var cover = a.hasAttribute("data-cw-cover-link")
        ? $(".cw-featured__cover", a.closest(".cw-featured")) : a;
      if (!cover) return;
      $$("[data-cw-cover]").forEach(function (c) { c.style.viewTransitionName = ""; });
      if (crossDocument) { cover.style.viewTransitionName = "cw-cover"; return; }
      // Without cross-document transitions, the cover opens to fill the
      // window in its own colour, and the edition opens on that colour.
      e.preventDefault();
      var r = cover.getBoundingClientRect();
      var veil = document.createElement("div");
      veil.className = "cw-veil";
      veil.style.background = getComputedStyle(cover).backgroundColor;
      body.appendChild(veil);
      var W = window.innerWidth, H = window.innerHeight;
      var from = "inset(" + r.top + "px " + (W - r.right) + "px " + (H - r.bottom) + "px " + r.left + "px)";
      var go = function () { window.location.href = a.href; };
      var anim = veil.animate([{ clipPath: from }, { clipPath: "inset(0px 0px 0px 0px)" }],
                              { duration: 520, easing: "cubic-bezier(.7,0,.2,1)", fill: "forwards" });
      anim.onfinish = go;
      window.setTimeout(go, 800);
    });
    window.addEventListener("pageshow", function () {
      $$(".cw-veil").forEach(function (v) { v.remove(); });
      $$("[data-cw-cover]").forEach(function (c) { c.style.viewTransitionName = ""; });
    });
  }

  /* ---------------------------------------------------------- give me a line */
  function lines() {
    var section = $("[data-cw-lines]");
    if (!section) return;
    var templates = $$("template[data-cw-line]", section);
    var stage = $("[data-cw-line-stage]", section);
    var button = $("[data-cw-line-button]", section);
    if (!templates.length || !stage || !button) return;
    var last = -1;
    stage.innerHTML = '<p class="cw-line__empty">A line is waiting.</p>';
    button.hidden = false;
    function show() {
      var i;
      do { i = Math.floor(Math.random() * templates.length); } while (templates.length > 1 && i === last);
      last = i;
      var figure = templates[i].content.firstElementChild.cloneNode(true);
      if (!still) {
        var p = $("blockquote p", figure);
        var n = 0;
        $$("br", p).forEach(function (br) { br.setAttribute("data-br", ""); });
        Array.prototype.slice.call(p.childNodes).forEach(function (node) {
          if (node.nodeType !== 3) return;
          var frag = document.createDocumentFragment();
          node.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var w = document.createElement("span");
            w.className = "w"; w.textContent = part; w.style.setProperty("--i", n++);
            frag.appendChild(w);
          });
          p.replaceChild(frag, node);
        });
        var cap = $("figcaption", figure);
        cap.classList.add("is-late");
        cap.style.setProperty("--late", (0.25 + n * 0.045) + "s");
      }
      stage.innerHTML = "";
      stage.appendChild(figure);
      stage.classList.remove("is-out");
      button.firstChild.nodeValue = "Another line ";
    }
    button.addEventListener("click", function () {
      if (still || !$(".cw-line__quote", stage)) { show(); return; }
      stage.classList.add("is-out");
      window.setTimeout(show, 230);
    });
  }

  /* ---------------------------------------------------------- afterword */
  function typing() {
    $$("[data-cw-type]").forEach(function (el) {
      if (still) { el.classList.add("is-split", "is-in"); return; }
      var caret = $(".cw-caret", el);
      var text = el.textContent;
      var sr = document.createElement("span");
      sr.className = "sr-only"; sr.textContent = text;
      var shown = document.createElement("span");
      shown.setAttribute("aria-hidden", "true");
      text.split("").forEach(function (ch, i) {
        var c = document.createElement("span");
        c.className = "c"; c.textContent = ch; c.style.setProperty("--i", i);
        shown.appendChild(c);
      });
      el.textContent = "";
      el.appendChild(sr); el.appendChild(shown);
      if (caret) shown.appendChild(caret);
      el.classList.add("is-split");
      watch([el]);
    });
  }

  /* ---------------------------------------------------------- old addresses */
  function legacy() {
    var h = window.location.hash.slice(1);
    if (!/^(poem|chapter)-[a-z0-9-]+$/.test(h)) return;
    var t = $("template[data-cw-legacies]");
    if (!t) return;
    var a = t.content.querySelector('[data-cw-legacy="' + h + '"]');
    if (a) window.location.replace(new URL(a.getAttribute("href"), window.location.href).href);
  }

  /* ---------------------------------------------------------- the reader */
  function reader() {
    var section = $("[data-cw-reader]");
    if (!section) return;
    var poems = $$("[data-cw-poem]", section);
    if (!poems.length) return;
    var rail = $("[data-cw-rail]", section);
    var indexLinks = $$(".cw-index [data-cw-goto]", section);
    var nows = $$("[data-cw-now]", section);
    var fills = $$(".cw-progress__fill", section);
    var bar = $("[data-cw-drawer-open]", section);
    var closeBtn = $("[data-cw-drawer-close]", section);
    var current = -1;
    var n = poems.length;

    section.classList.add("is-paged");

    function fromHash() {
      var h = window.location.hash.slice(1);
      for (var i = 0; i < n; i++) if (poems[i].id === h) return i;
      return -1;
    }
    function show(i, entering) {
      poems.forEach(function (p, k) { p.classList.toggle("is-current", k === i); });
      var p = poems[i];
      if (entering && !still) {
        $$(".cw-verse__stanza", p).forEach(function (s, k) { s.style.setProperty("--s", Math.min(k, 8)); });
        p.classList.remove("is-entering");
        void p.offsetWidth;
        p.classList.add("is-entering");
      }
      indexLinks.forEach(function (a, k) {
        if (k === i) a.setAttribute("aria-current", "true");
        else a.removeAttribute("aria-current");
      });
      var label = (i + 1 < 10 ? "0" : "") + (i + 1);
      nows.forEach(function (el) { el.textContent = label; });
      current = i;
      progress();
    }
    function progress() {
      var p = poems[current];
      if (!p) return;
      var r = p.getBoundingClientRect();
      var within = clamp((window.innerHeight - r.top) / Math.max(r.height + window.innerHeight * 0.2, 1), 0, 1);
      var value = (current + within) / n;
      fills.forEach(function (f) { f.style.setProperty("--p", value.toFixed(4)); });
    }
    function go(i, focus) {
      if (i < 0 || i >= n || i === current) return;
      show(i, true);
      if (window.history.replaceState) window.history.replaceState(null, "", "#" + poems[i].id);
      var top = section.getBoundingClientRect().top + window.scrollY;
      var poemTop = poems[i].getBoundingClientRect().top + window.scrollY - 110;
      if (window.scrollY > poemTop + 4 || window.scrollY < top - window.innerHeight * 0.5) scrollToY(Math.max(poemTop, 0), 0.8);
      if (focus) {
        var h = $("h2", poems[i]);
        if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
      }
    }

    var start = fromHash();
    show(start < 0 ? 0 : start, false);

    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("[data-cw-goto]");
      if (!a || !section.contains(a) || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
      e.preventDefault();
      e.stopPropagation();
      closeDrawer(false);
      go(parseInt(a.getAttribute("data-cw-goto"), 10), e.detail === 0);
    }, true);
    window.addEventListener("hashchange", function () {
      var i = fromHash();
      if (i >= 0) go(i, false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      var t = e.target;
      if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.closest("[role=tablist]"))) return;
      if (body.classList.contains("menu-open")) return;
      var r = section.getBoundingClientRect();
      if (r.bottom < 80 || r.top > window.innerHeight * 0.6) return;
      e.preventDefault();
      go(current + (e.key === "ArrowRight" ? 1 : -1), true);
    });
    var queued = false;
    window.addEventListener("scroll", function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () { queued = false; progress(); });
    }, { passive: true });

    /* Phones and tablets: the index is a sheet drawn up from the bar. */
    if (!bar || !rail) return;
    bar.hidden = false;
    var back = null, lastFocus = null;
    var narrow = window.matchMedia("(max-width: 1023px)");
    function isOpen() { return rail.classList.contains("is-open"); }
    function openDrawer() {
      if (!narrow.matches) return;
      lastFocus = document.activeElement;
      back = document.createElement("div");
      back.className = "cw-drawer-back";
      back.addEventListener("click", function () { closeDrawer(true); });
      // Inside the reader, so it sits under the sheet; the body class lifts
      // the page above the site's fixed controls while the sheet is open.
      section.insertBefore(back, section.firstChild);
      body.classList.add("cw-drawer-open");
      requestAnimationFrame(function () { back.classList.add("is-on"); });
      rail.classList.add("is-open");
      rail.setAttribute("role", "dialog");
      rail.setAttribute("aria-modal", "true");
      bar.setAttribute("aria-expanded", "true");
      window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: true } }));
      var target = $('[aria-current="true"]', rail) || closeBtn;
      window.setTimeout(function () { if (target) target.focus({ preventScroll: true }); }, 60);
    }
    function closeDrawer(restore) {
      if (!isOpen()) return;
      rail.classList.remove("is-open");
      body.classList.remove("cw-drawer-open");
      rail.removeAttribute("role");
      rail.removeAttribute("aria-modal");
      bar.setAttribute("aria-expanded", "false");
      if (back) {
        var b = back; back = null;
        b.classList.remove("is-on");
        window.setTimeout(function () { b.remove(); }, 400);
      }
      window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: false } }));
      if (restore && lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    }
    bar.addEventListener("click", function () { if (isOpen()) closeDrawer(true); else openDrawer(); });
    if (closeBtn) closeBtn.addEventListener("click", function () { closeDrawer(true); });
    document.addEventListener("keydown", function (e) {
      if (!isOpen()) return;
      if (e.key === "Escape") { e.preventDefault(); closeDrawer(true); return; }
      if (e.key !== "Tab") return;
      var f = $$("a[href], button:not([hidden])", rail).filter(function (x) { return x.offsetParent !== null; });
      if (!f.length) return;
      if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
    });
    $$('a[href="#presentation"]', rail).forEach(function (a) {
      a.addEventListener("click", function () { closeDrawer(false); }, true);
    });
    if (narrow.addEventListener) narrow.addEventListener("change", function () { if (!narrow.matches) closeDrawer(false); });
    // The bar shows while the poems are on screen, and steps aside after.
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        bar.classList.toggle("is-on", entries[0].isIntersecting);
      }, { rootMargin: "-30% 0px -20% 0px" }).observe($(".cw-poems", section));
    } else bar.classList.add("is-on");
  }

  /* ---------------------------------------------------------- boot */
  legacy();
  reader();
  collections();
  typing();
  lines();
  coverTransitions();
  watch($$("[data-cw-reveal]").filter(function (el) { return !el.closest("[data-cw-panel]"); }));
  // The shared script owns GSAP's registration and Lenis; the hero, the
  // split's rule and anything scrubbed wait for it and for the faces.
  function late() {
    if (window.gsap && window.ScrollTrigger) window.gsap.registerPlugin(window.ScrollTrigger);
    hero();
    splitRule();
  }
  var fonts = document.fonts && document.fonts.ready;
  var started = false;
  function once() { if (!started) { started = true; late(); } }
  if (fonts) fonts.then(once);
  window.setTimeout(once, 1200);
})();
