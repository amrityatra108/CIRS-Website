/* ============================================================
   Our Laurels — motion and interaction.
   The page is complete without this file (see laurels.css): every
   record, figure and source in reading order. This adds, in order:

     the entrance        one timeline, then the pointer eases in
     the world           the count becomes the running head; the
                         fields arrive out of depth, one by one
     counted             one figure to a screen
     the reel            the years travel toward the reader; the last
                         milestone opens into the first featured story
     the featured        five compositions, restrained parallax
     the archive         quiet: filters, search, rows, a preview
     looking closely     a document comes forward, the page dims

   GSAP and ScrollTrigger run on the Lenis that cirs.js already
   starts; nothing here starts a second smooth scroller or a second
   animation loop. gsap.matchMedia() chooses between three modes and
   reverts everything it made when the choice changes:
     cine    a wide window, motion allowed: the sequences are pinned
             and moved through depth (.lr-cine on <body>)
     lite    a phone, a narrow or short window: the document, with
             each part settling as it arrives, and the years holding
             their numerals while their records are read
     reduce  motion reduced: the document, nothing moves
   ============================================================ */
(function () {
  "use strict";

  var root = document.querySelector(".lr");
  if (!root) return;

  var html = document.documentElement, body = document.body;
  var hasGSAP = typeof window.gsap !== "undefined";
  var hasST = hasGSAP && typeof window.ScrollTrigger !== "undefined";
  if (hasST) gsap.registerPlugin(ScrollTrigger);
  var reducedMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var smooth = function (t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); };
  var easeOut = function (t) { t = clamp(t, 0, 1); return 1 - Math.pow(1 - t, 3); };

  body.classList.add("lr-live");
  var unpre = function () { html.classList.remove("lr-pre"); };

  // The scroll engine is cirs.js's; this asks it to land somewhere.
  function scrollToY(y, instant) {
    var ev = new CustomEvent("cirs-section-scroll", { cancelable: true, detail: { top: Math.round(y), duration: instant ? 0.01 : 1.4 } });
    if (window.dispatchEvent(ev)) window.scrollTo({ top: Math.round(y), behavior: instant || reducedMQ.matches ? "auto" : "smooth" });
  }
  function lockScroll(locked) {
    window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: locked } }));
  }

  /* Restore entrances when returning from above; keep completed content below. */
  var seenIO = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting || reducedMQ.matches) e.target.classList.add("is-seen");
      else if (e.boundingClientRect.top > 0) e.target.classList.remove("is-seen");
    });
  }, { threshold: 0.16, rootMargin: "0px 0px -6% 0px" }) : null;
  function onSeen(el) {
    if (seenIO && !reducedMQ.matches) seenIO.observe(el);
    else el.classList.add("is-seen");
  }

  /* ==========================================================
     The cursor: the site's own ring, given a word where there is one
     ========================================================== */
  (function cursor() {
    var ring = $("#ring");
    if (!ring || !fine) return;
    document.addEventListener("pointerover", function (e) {
      var t = e.target.closest && e.target.closest("[data-cursor]");
      if (!t) return;
      ring.setAttribute("data-label", t.getAttribute("data-cursor"));
      ring.classList.add("has-label");
    });
    document.addEventListener("pointerout", function (e) {
      var t = e.target.closest && e.target.closest("[data-cursor]");
      if (!t) return;
      var to = e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest("[data-cursor]");
      if (to) { ring.setAttribute("data-label", to.getAttribute("data-cursor")); return; }
      ring.classList.remove("has-label");
    });
  })();

  /* ==========================================================
     The entrance. One timeline; the start state is already in CSS
     (html.lr-pre), so nothing is seen before it begins.
     ========================================================== */
  var introDone = false;
  var pointerState = { w: 0 };            // how far the pointer is allowed to steer, 0..1

  function splitMask(el) {
    var text = el.textContent;
    el.textContent = "";
    el.setAttribute("aria-label", text);
    return text.split("").map(function (ch) {
      var m = document.createElement("span"), d = document.createElement("span");
      m.style.cssText = "display:inline-block;overflow:hidden;vertical-align:top;padding-block:.22em;margin-block:-.22em;";
      d.style.cssText = "display:inline-block;will-change:transform;";
      d.setAttribute("aria-hidden", "true"); m.setAttribute("aria-hidden", "true");
      d.textContent = ch; m.appendChild(d); el.appendChild(m);
      return d;
    });
  }

  function fontsReady() {
    var ready = document.fonts && document.fonts.load
      ? Promise.all([document.fonts.load('200 120px "Newsreader"'), document.fonts.load('500 14px "Mona Sans"')]).catch(function () {})
      : Promise.resolve();
    return Promise.race([ready, new Promise(function (r) { setTimeout(r, 1400); })]);
  }

  function entrance(withPointer) {
    var num = $("[data-lr-num]"), word = $("[data-lr-word]"), range = $("[data-lr-range]");
    var frags = $$(".lr-frag"), cue = $("[data-lr-cue]");
    if (!num) { unpre(); return; }
    // Reloaded part-way down, or motion reduced: no entrance, the page is simply there.
    if (window.scrollY > 40 || reducedMQ.matches) { unpre(); introDone = true; pointerState.w = withPointer ? 1 : 0; return; }
    fontsReady().then(function () {
      var digits = splitMask(num), letters = splitMask(word);
      gsap.set(digits, { yPercent: 150 });
      gsap.set(letters, { yPercent: 170 });
      gsap.set(range, { opacity: 0, y: 14 });
      gsap.set(frags, { "--io": 0, "--iz": "-1300px" });
      if (cue) gsap.set(cue, { opacity: 0 });
      unpre();                                   // the start state is now GSAP's, in the same frame
      var tl = gsap.timeline({ defaults: { ease: "power3.out" }, onComplete: function () { introDone = true; } });
      tl.to(digits, { yPercent: 0, duration: 1.15, ease: "power4.out", stagger: 0.09 }, 0.15)
        .to(frags, { "--io": 1, duration: 0.9, ease: "power1.out", stagger: { each: 0.05, from: "random" } }, 0.3)
        .to(letters, { yPercent: 0, duration: 0.95, ease: "power4.out", stagger: 0.045 }, 0.45)
        .to(frags, { "--iz": "0px", duration: 1.5, ease: "power3.out", stagger: { each: 0.04, from: "random" } }, 0.65)
        .to(range, { opacity: 1, y: 0, duration: 0.85 }, 0.85);
      if (cue) tl.to(cue, { opacity: 1, duration: 0.9 }, 1.35);
      if (withPointer) tl.to(pointerState, { w: 1, duration: 0.8, ease: "power2.inOut" }, 1.6);
    });
  }

  /* ==========================================================
     Common to every mode
     ========================================================== */

  /* ---- the archive -------------------------------------------------- */
  var archive = $("[data-lr-archive]");
  var rows = archive ? $$(".lr-row", archive) : [];
  var state = { cat: "all", level: "all", year: "all", q: "" };
  var status = archive ? $("[data-lr-status]", archive) : null;
  var emptyMsg = archive ? $("[data-lr-empty]", archive) : null;
  var filters = archive ? $("[data-lr-filters]", archive) : null;
  var searchBox = archive ? $("[data-lr-search]", archive) : null;
  var qInput = searchBox ? $("input", searchBox) : null;
  var catNames = {};
  var animateFilter = function () { return hasGSAP && !reducedMQ.matches; };

  function rowMatches(r, s) {
    if (s.cat !== "all" && (" " + r.getAttribute("data-cats") + " ").indexOf(" " + s.cat + " ") < 0) return false;
    if (s.level !== "all" && r.getAttribute("data-level") !== s.level) return false;
    if (s.year !== "all" && r.getAttribute("data-year") !== s.year) return false;
    if (s.q) {
      var hay = r.getAttribute("data-q");
      var words = s.q.toLowerCase().split(/\s+/).filter(Boolean);
      for (var i = 0; i < words.length; i++) if (hay.indexOf(words[i]) < 0) return false;
    }
    return true;
  }

  function closeRow(r, instant) {
    var b = $(".lr-row__btn", r), p = $(".lr-row__panel", r);
    if (!b || b.getAttribute("aria-expanded") !== "true") return;
    b.setAttribute("aria-expanded", "false");
    if (instant || !animateFilter()) { p.hidden = true; return; }
    gsap.to(p, { height: 0, opacity: 0, duration: 0.45, ease: "power3.inOut", onComplete: function () { p.hidden = true; gsap.set(p, { clearProps: "height,opacity" }); } });
  }
  function openRow(r, instant) {
    var b = $(".lr-row__btn", r), p = $(".lr-row__panel", r);
    if (!b || b.getAttribute("aria-expanded") === "true") return;
    rows.forEach(function (o) { if (o !== r) closeRow(o, instant); });
    b.setAttribute("aria-expanded", "true");
    p.hidden = false;
    if (instant || !animateFilter()) return;
    gsap.fromTo(p, { height: 0, opacity: 0 }, { height: "auto", opacity: 1, duration: 0.6, ease: "power3.out", clearProps: "height,opacity" });
  }

  function applyFilters(animate) {
    if (!archive) return;
    var first = null;
    if (animate && animateFilter()) {
      first = new Map();
      rows.forEach(function (r) { if (!r.hidden) first.set(r, r.getBoundingClientRect().top); });
    }
    var shown = 0, entering = [];
    rows.forEach(function (r) {
      var ok = rowMatches(r, state), was = !r.hidden;
      r.hidden = !ok;
      if (ok) { shown++; if (!was) entering.push(r); } else closeRow(r, true);
    });
    if (first) {
      rows.forEach(function (r) {
        if (r.hidden) return;
        if (first.has(r)) {
          var dy = first.get(r) - r.getBoundingClientRect().top;
          if (Math.abs(dy) > 1) gsap.fromTo(r, { y: dy }, { y: 0, duration: 0.6, ease: "power3.inOut", clearProps: "transform" });
        }
      });
      if (entering.length) gsap.fromTo(entering, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out", stagger: 0.02, delay: 0.12, clearProps: "opacity,transform" });
    }
    // Counts under the other choices; a field with none is set aside.
    if (filters) {
      $$(".lr-cat-btn", filters).forEach(function (b) {
        var cat = b.getAttribute("data-cat");
        var n = rows.filter(function (r) { return rowMatches(r, { cat: cat, level: state.level, year: state.year, q: state.q }); }).length;
        $(".lr-cat-btn__c", b).textContent = n;
        b.disabled = n === 0 && cat !== state.cat;
        b.setAttribute("aria-pressed", String(cat === state.cat));
      });
      $$(".lr-opt", filters).forEach(function (b) {
        var lv = b.getAttribute("data-level"), yr = b.getAttribute("data-year");
        b.setAttribute("aria-pressed", String(lv ? lv === state.level : yr === state.year));
      });
    }
    var bits = [];
    if (state.cat !== "all") bits.push(catNames[state.cat]);
    if (state.year !== "all") bits.push(state.year === "undated" ? "undated" : state.year);
    if (state.level !== "all") bits.push($('.lr-opt[data-level="' + state.level + '"]', filters).textContent);
    if (state.q) bits.push("“" + state.q + "”");
    if (status) status.textContent = "Showing " + shown + " of " + rows.length + " records" + (bits.length ? ": " + bits.join(" · ") : "") + ".";
    if (emptyMsg) emptyMsg.hidden = shown !== 0;
    if (hasST) ScrollTrigger.refresh();
  }
  function setFilter(next) {
    Object.keys(next).forEach(function (k) { state[k] = next[k]; });
    applyFilters(true);
  }

  if (archive && filters) {
    filters.hidden = false;
    if (searchBox) searchBox.hidden = false;
    $$(".lr-cat-btn", filters).forEach(function (b) { catNames[b.getAttribute("data-cat")] = $(".lr-cat-btn__name", b).textContent; });
    filters.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b || b.disabled) return;
      if (b.hasAttribute("data-cat")) setFilter({ cat: b.getAttribute("data-cat") });
      else if (b.hasAttribute("data-level")) setFilter({ level: b.getAttribute("data-level") });
      else if (b.hasAttribute("data-year")) setFilter({ year: b.getAttribute("data-year") });
    });
    var reset = $("[data-lr-reset]", archive);
    if (reset) reset.addEventListener("click", function () { if (qInput) qInput.value = ""; setFilter({ cat: "all", level: "all", year: "all", q: "" }); });
    if (qInput) {
      var qTimer = 0;
      qInput.addEventListener("input", function () {
        clearTimeout(qTimer);
        qTimer = setTimeout(function () { setFilter({ q: qInput.value.trim() }); }, 140);
      });
    }
    archive.addEventListener("click", function (e) {
      var b = e.target.closest(".lr-row__btn");
      if (!b) return;
      var r = b.closest(".lr-row");
      if (b.getAttribute("aria-expanded") === "true") closeRow(r); else openRow(r);
    });
    applyFilters(false);
  }
  // "All 19 in academics" in a field: filter the archive, then let the anchor land.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-lr-filter]");
    if (!a || !archive) return;
    setFilter({ cat: a.getAttribute("data-lr-filter"), level: "all", year: "all", q: "" });
    if (qInput) qInput.value = "";
  });
  // Numbered chapter links reveal their archive record before the shared scroll handler runs.
  var chapters = $(".rd-laurels");
  if (chapters) chapters.addEventListener("click", function (e) {
    var link = e.target.closest('a[href^="#laurel-"]');
    if (!link || !archive) return;
    var row = document.getElementById(link.getAttribute("href").slice(1));
    if (!row) return;
    if (row.hidden) { if (qInput) qInput.value = ""; setFilter({ cat: "all", level: "all", year: "all", q: "" }); }
    openRow(row, true);
  });
  // A link to one record opens it.
  function openFromHash() {
    var m = /^#laurel-(.+)$/.exec(location.hash);
    if (!m || !archive) return;
    var r = document.getElementById("laurel-" + m[1]);
    if (!r) return;
    if (r.hidden) { if (qInput) qInput.value = ""; setFilter({ cat: "all", level: "all", year: "all", q: "" }); }
    openRow(r, true);
  }
  window.addEventListener("hashchange", openFromHash);
  openFromHash();

  /* ---- the preview that follows the pointer over a record ----------- */
  (function peek() {
    var fig = $("[data-lr-peek]");
    if (!fig || !archive || !fine || !hasGSAP) return;
    var img = $("img", fig);
    var target = { x: 0, y: 0 }, cur = { x: 0, y: 0 }, shown = false, active = null;
    function tick() {
      cur.x += (target.x - cur.x) * 0.08;
      cur.y += (target.y - cur.y) * 0.08;
      var tilt = clamp((target.x - cur.x) * 0.045, -2.5, 2.5);
      fig.style.transform = "translate3d(" + (cur.x + 56).toFixed(1) + "px," + (cur.y - 46).toFixed(1) + "px,0) rotate(" + tilt.toFixed(2) + "deg)";
    }
    function show(row, x, y) {
      var src = row.getAttribute("data-peek");
      if (!src || reducedMQ.matches) return;
      if (!shown) { cur.x = x; cur.y = y; gsap.ticker.add(tick); shown = true; }
      target.x = x; target.y = y;
      if (img.getAttribute("src") !== src) img.setAttribute("src", src);
      active = row;
      gsap.to(fig, { opacity: 1, duration: 0.3, overwrite: "auto" });
    }
    function hide() {
      active = null;
      gsap.to(fig, { opacity: 0, duration: 0.25, overwrite: "auto", onComplete: function () { if (!active && shown) { gsap.ticker.remove(tick); shown = false; } } });
    }
    archive.addEventListener("pointermove", function (e) {
      var b = e.target.closest && e.target.closest(".lr-row__btn");
      var row = b && b.closest(".lr-row");
      if (row && row.hasAttribute("data-peek")) show(row, e.clientX, e.clientY);
      else if (active) hide();
    });
    archive.addEventListener("pointerleave", function () { if (active) hide(); });
  })();

  /* ---- the roll of names -------------------------------------------- */
  (function names() {
    var sec = $("[data-lr-names]");
    if (!sec) return;
    var field = $("[data-lr-namefield]", sec), reading = $("[data-lr-reading]", sec), pinned = null;
    function light(li) {
      $$(".lr-name.is-on", field).forEach(function (x) { if (x !== li) x.classList.remove("is-on"); });
      if (!li) { field.classList.remove("is-dim"); reading.classList.remove("is-on"); return; }
      li.classList.add("is-on"); field.classList.add("is-dim");
      reading.innerHTML = "<span><b></b></span>";
      $("b", reading).textContent = $(".lr-name__btn", li).textContent;
      $("span", reading).appendChild(document.createTextNode($(".lr-name__detail", li).textContent));
      reading.classList.add("is-on");
    }
    field.addEventListener("pointerover", function (e) { if (e.pointerType !== "mouse") return; var li = e.target.closest(".lr-name"); if (li && !pinned) light(li); });
    field.addEventListener("pointerleave", function () { if (!pinned) light(null); });
    field.addEventListener("focusin", function (e) { var li = e.target.closest(".lr-name"); if (li) light(li); });
    field.addEventListener("focusout", function (e) { if (!field.contains(e.relatedTarget)) { pinned = null; light(null); } });
    field.addEventListener("click", function (e) {
      var li = e.target.closest(".lr-name"); if (!li) return;
      if (pinned === li) { pinned = null; light(null); li.classList.remove("is-on"); } else { pinned = li; light(li); }
    });
    sec.addEventListener("keydown", function (e) { if (e.key === "Escape" && field.classList.contains("is-dim")) { pinned = null; light(null); } });
    if (hasST && !reducedMQ.matches) {
      ScrollTrigger.create({ trigger: sec, start: "top bottom", end: "bottom top", onUpdate: function (s) { sec.style.setProperty("--np", ((s.progress - 0.5) * 2).toFixed(3)); } });
    }
  })();

  $$(".lr-event").forEach(onSeen);

  /* ==========================================================
     Looking closely: a document comes forward and the page dims
     ========================================================== */
  var inspect = (function () {
    var dlg = $("#lr-inspect");
    var openers = $$(".lr-ms__open");
    if (!dlg || !openers.length || typeof dlg.showModal !== "function") return null;
    var stage = $("[data-lr-inspect-stage]", dlg), cap = $("[data-lr-inspect-cap]", dlg), links = $("[data-lr-inspect-links]", dlg);
    var count = $("[data-lr-inspect-count]", dlg), prev = $("[data-lr-inspect-prev]", dlg), next = $("[data-lr-inspect-next]", dlg);
    var closeBtn = $("[data-lr-inspect-close]", dlg);
    var cur = -1, opener = null, clone = null, busy = false;

    function fit(w, h) {
      var r = stage.getBoundingClientRect();
      var k = Math.min(r.width / w, r.height / h, 1.6);
      var W = w * k, H = h * k;
      return { x: r.left + (r.width - W) / 2, y: r.top + (r.height - H) / 2, w: W, h: H };
    }
    function fill(i) {
      var b = openers[i], li = b.closest(".lr-ms");
      cur = i;
      cap.textContent = $("figcaption", li).textContent + " — " + $(".lr-ms__title", li).textContent + ", " + li.getAttribute("data-year");
      links.innerHTML = "";
      var src = $(".lr-src", li);
      if (src) { var a = src.cloneNode(true); a.removeAttribute("data-cursor"); links.appendChild(a); }
      count.textContent = (i + 1) + " / " + openers.length;
      prev.disabled = i === 0; next.disabled = i === openers.length - 1;
    }
    function bigImage(i) {
      var b = openers[i], im = new Image();
      im.alt = $("img", b).getAttribute("alt");
      im.src = b.getAttribute("data-large");
      im.setAttribute("width", b.getAttribute("data-w")); im.setAttribute("height", b.getAttribute("data-h"));
      return im;
    }
    function open(i) {
      if (busy) return;
      opener = openers[i];
      fill(i);
      var small = $("img", opener), r0 = small.getBoundingClientRect();
      var w = +opener.getAttribute("data-w"), h = +opener.getAttribute("data-h");
      var r1;
      lockScroll(true);
      dlg.showModal();
      stage.innerHTML = "";
      var big = bigImage(i);
      big.style.opacity = "0";
      stage.appendChild(big);
      r1 = fit(w, h);
      if (!hasGSAP || reducedMQ.matches) { big.style.opacity = "1"; closeBtn.focus(); return; }
      busy = true;
      clone = document.createElement("img");
      clone.className = "lr-inspect__clone";
      clone.src = small.currentSrc || small.src; clone.alt = "";
      gsap.set(clone, { left: r0.left, top: r0.top, width: r0.width, height: r0.height, objectFit: "cover" });
      dlg.appendChild(clone);
      gsap.set(dlg, { backgroundColor: "rgba(14,11,18,0)" });
      gsap.set($(".lr-inspect__bar", dlg), { opacity: 0 });
      gsap.set($(".lr-inspect__foot", dlg), { opacity: 0 });
      var tl = gsap.timeline({ onComplete: function () {
        big.style.opacity = "1"; if (clone) { clone.remove(); clone = null; } busy = false;
      } });
      tl.to(dlg, { backgroundColor: "rgba(14,11,18,.94)", duration: 0.6, ease: "power2.out" }, 0)
        .to(clone, { left: r1.x, top: r1.y, width: r1.w, height: r1.h, duration: 0.8, ease: "power3.inOut" }, 0)
        .to([$(".lr-inspect__bar", dlg), $(".lr-inspect__foot", dlg)], { opacity: 1, duration: 0.5 }, 0.45);
      closeBtn.focus();
    }
    function swap(i) {
      if (busy || i < 0 || i >= openers.length) return;
      fill(i);
      var old = $("img", stage), big = bigImage(i);
      big.style.opacity = "0"; stage.appendChild(big);
      if (!hasGSAP || reducedMQ.matches) { if (old) old.remove(); big.style.opacity = "1"; return; }
      gsap.to(old, { opacity: 0, duration: 0.3, onComplete: function () { old.remove(); } });
      gsap.to(big, { opacity: 1, duration: 0.5, delay: 0.15 });
    }
    function close() {
      if (busy || !dlg.open) return;
      var big = $("img", stage), b = openers[cur];
      var done = function () {
        dlg.close(); lockScroll(false);
        hasGSAP && gsap.set([dlg, $(".lr-inspect__bar", dlg), $(".lr-inspect__foot", dlg)], { clearProps: "all" });
        if (clone) { clone.remove(); clone = null; }
        busy = false;
        if (b) b.focus({ preventScroll: true });
      };
      if (!hasGSAP || reducedMQ.matches) { done(); return; }
      // Back to the plane it came from, if that plane is still in view.
      var small = $("img", b), r0 = small.getBoundingClientRect(), li = b.closest(".lr-ms");
      var visible = r0.width > 4 && r0.bottom > 0 && r0.top < innerHeight && r0.right > 0 && r0.left < innerWidth && parseFloat(getComputedStyle(li).opacity) > 0.4;
      busy = true;
      var r1 = big.getBoundingClientRect();
      clone = document.createElement("img");
      clone.className = "lr-inspect__clone"; clone.src = big.currentSrc || big.src; clone.alt = "";
      gsap.set(clone, { left: r1.left, top: r1.top, width: r1.width, height: r1.height, objectFit: "contain" });
      dlg.appendChild(clone); big.style.opacity = "0";
      var tl = gsap.timeline({ onComplete: done });
      tl.to([$(".lr-inspect__bar", dlg), $(".lr-inspect__foot", dlg)], { opacity: 0, duration: 0.25 }, 0)
        .to(dlg, { backgroundColor: "rgba(14,11,18,0)", duration: 0.6, ease: "power2.inOut" }, 0.1);
      if (visible) tl.to(clone, { left: r0.left, top: r0.top, width: r0.width, height: r0.height, objectFit: "cover", duration: 0.7, ease: "power3.inOut" }, 0);
      else tl.to(clone, { opacity: 0, duration: 0.4 }, 0);
    }
    // Without script the opener is a plain link to the large image; with it, the image comes forward.
    openers.forEach(function (b, i) { b.addEventListener("click", function (e) { e.preventDefault(); open(i); }); });
    prev.addEventListener("click", function () { swap(cur - 1); });
    next.addEventListener("click", function () { swap(cur + 1); });
    closeBtn.addEventListener("click", close);
    dlg.addEventListener("cancel", function (e) { e.preventDefault(); close(); });      // Escape
    dlg.addEventListener("click", function (e) { if (e.target === dlg || e.target === stage) close(); });
    dlg.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") swap(cur + 1);
      else if (e.key === "ArrowLeft") swap(cur - 1);
    });
    return { open: open };
  })();

  /* ==========================================================
     The three modes
     ========================================================== */
  if (!hasGSAP || !hasST) {
    unpre();
    $$(".lr-feature, .lr-cat, .lr-stat, .lr-ms").forEach(function (e) { e.classList.add("is-seen"); });
    return;
  }

  // A local dissolve OUT: sample the preceding text once into a bounded
  // particle field. GSAP supplies the clock; there is no extra render loop.
  function ending(cleanups) {
    var sec = $('[data-lr-end]'), title = $('.lr-end__title', sec);
    if (!sec || !title || reducedMQ.matches || !window.IntersectionObserver) return;
    var previous = $('.lr-end__previous', title), words = $$('.lr-end__words > span', title);
    var canvas = document.createElement('canvas');
    canvas.className = 'lr-end__dust'; canvas.setAttribute('aria-hidden', 'true');
    title.appendChild(canvas); sec.classList.add('is-motion');
    var context = canvas.getContext('2d'), particles = [], phase = { value: 0 }, active = false, disposed = false;
    if (!context) { canvas.remove(); sec.classList.remove('is-motion'); return; }
    function sample() {
      var rect = title.getBoundingClientRect(), css = getComputedStyle(previous);
      var width = Math.ceil(rect.width), height = Math.ceil(rect.height);
      canvas.width = width; canvas.height = height;
      context.clearRect(0, 0, width, height);
      context.font = css.font; context.fillStyle = css.color; context.textBaseline = 'top';
      var lines = previous.innerHTML.split(/<br\s*\/?\s*>/i), lineHeight = parseFloat(css.lineHeight);
      lines.forEach(function (line, i) { context.fillText(line, 0, i * lineHeight); });
      var pixels = context.getImageData(0, 0, width, height).data;
      var step = Math.max(4, Math.ceil(Math.sqrt(width * height / 1400)));
      particles = [];
      for (var y = 0; y < height; y += step) for (var x = 0; x < width; x += step) {
        if (pixels[(y * width + x) * 4 + 3] > 60 && particles.length < 550) {
          var seed = ((x * 13 + y * 17) % 101) / 100;
          particles.push({ x: x, y: y, dx: (seed - .35) * 110, dy: -18 - seed * 80, size: 2 + seed * 2 });
        }
      }
      draw();
    }
    function draw() {
      var t = phase.value;
      context.clearRect(0, 0, canvas.width, canvas.height);
      if (t <= 0 || t >= 1) return;
      context.fillStyle = getComputedStyle(previous).color;
      context.globalAlpha = Math.min(t * 5, 1) * (1 - t);
      particles.forEach(function (p) { context.fillRect(p.x + p.dx * t, p.y + p.dy * t, p.size, p.size); });
      context.globalAlpha = 1;
    }
    gsap.set(words, { opacity: 0 });
    var tl = gsap.timeline({ paused: true, onUpdate: draw });
    tl.to(previous, { opacity: 0, duration: .55, ease: 'power2.out' }, 0)
      .to(phase, { value: 1, duration: .65, ease: 'none' }, 0);
    words.forEach(function (word, i) { tl.to(word, { opacity: 1, duration: .3, ease: 'power2.out' }, .7 + i * .55); });
    sample();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        active = entry.isIntersecting;
        bind(active);
        if (active) { if (!particles.length) sample(); tl.play(); }
        else {
          tl.pause(entry.boundingClientRect.top > 0 ? 0 : tl.duration());
          particles = []; canvas.width = canvas.height = 0;
        }
      });
    }, { threshold: 0, rootMargin: '-18% 0px -22% 0px' });
    io.observe(sec);
    var lastY = window.scrollY;
    function onScroll() {
      var delta = window.scrollY - lastY;
      if (Math.abs(delta) < 8) return;
      lastY = window.scrollY;
      if (active && !document.hidden) { if (delta < 0) tl.reverse(); else tl.play(); }
    }
    // Crossing the reveal boundary in reverse restores the earlier text;
    // re-entry always begins with that text before the words are revealed.
    var sizeTimer;
    function onResize() {
      clearTimeout(sizeTimer);
      sizeTimer = setTimeout(function () { if (!disposed && active) sample(); }, 100);
    }
    function onVisibility() {
      if (document.hidden) tl.pause(); else if (active) tl.play();
    }
    var bound = false;
    function bind(enabled) {
      if (bound === enabled) return;
      bound = enabled; lastY = window.scrollY;
      var method = enabled ? 'addEventListener' : 'removeEventListener';
      window[method]('scroll', onScroll, { passive: true });
      window[method]('resize', onResize, { passive: true });
      document[method]('visibilitychange', onVisibility);
      if (!enabled) clearTimeout(sizeTimer);
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (!disposed && active) sample(); });
    cleanups.push(function () {
      disposed = true; bind(false); clearTimeout(sizeTimer); io.disconnect(); tl.kill();
      particles = []; canvas.width = canvas.height = 0; canvas.remove(); sec.classList.remove('is-motion');
      gsap.set([previous].concat(words), { clearProps: 'opacity' });
    });
  }

  var mm = gsap.matchMedia();
  var features = $$(".lr-feature");
  var featuresSec = $(".lr-features");

  mm.add({
    cine: "(min-width: 900px) and (min-height: 560px) and (prefers-reduced-motion: no-preference)",
    lite: "(max-width: 899px), (max-height: 559px)",
    reduce: "(prefers-reduced-motion: reduce)"
  }, function (ctx) {
    var c = ctx.conditions;
    var cleanups = [];
    var listen = function (t, ev, fn, o) { t.addEventListener(ev, fn, o); cleanups.push(function () { t.removeEventListener(ev, fn, o); }); };

    features.forEach(onSeen);
    ending(cleanups);

    if (c.reduce) { unpre(); $$(".lr-cat, .lr-stat, .lr-ms").forEach(function (e) { e.classList.add("is-seen"); }); return; }

    /* ---------------- lite: the document, settling as it arrives ---------------- */
    if (!c.cine) {
      entrance(false);
      $$(".lr-cat, .lr-stat, .lr-ms, .lr-hero__range").forEach(onSeen);
      // Each year holds its numerals while its record is read (CSS sticky), and
      // arrives out of a little depth: scale, not travel.
      $$(".lr-ms__inner").forEach(function (inner) {
        gsap.fromTo(inner, { scale: 0.93, opacity: 0.35 }, {
          scale: 1, opacity: 1, ease: "none",
          scrollTrigger: { trigger: inner, start: "top 92%", end: "top 48%", scrub: true }
        });
      });
      return function () { cleanups.forEach(function (f) { f(); }); };
    }

    /* ---------------- cine ---------------- */
    body.classList.add("lr-cine");
    cleanups.push(function () { body.classList.remove("lr-cine"); });
    var vh = function () { return window.innerHeight; };
    var vw = function () { return window.innerWidth; };

    /* --- the world: the count, the fields ------------------------------------- */
    (function world() {
      var w = $("[data-lr-world]");
      if (!w) { unpre(); return; }
      var stage = $(".lr-world__stage", w), scene = $("[data-lr-scene]", w);
      var hero = $("[data-lr-hero]", w), num = $("[data-lr-num]", w), word = $("[data-lr-word]", w), range = $("[data-lr-range]", w);
      var frags = $$(".lr-frag", hero), mast = $("[data-lr-mast]", w), mastB = $("b", mast);
      var index = $("[data-lr-catindex]", w), cue = $("[data-lr-cue]", w);
      var title = $("[data-lr-forms-title]", w), cats = $$(".lr-cat", w);
      var links = $$("a", index);
      var STEP = 0.85, F0 = 2.32;
      var F = cats.map(function (_, i) { return F0 + STEP * i; });

      gsap.set(title, { "--z": "-2600px", "--o": 0 });
      cats.forEach(function (el) { gsap.set(el, { "--z": "-2400px", "--o": 0 }); });
      gsap.set(mastB, { autoAlpha: 0 });
      gsap.set(num, { transformOrigin: "0 0" });
      frags.forEach(function (f) { gsap.set(f, { "--sz": "0px", "--o": 1 }); });

      // Where the count comes to rest: on the running head, sized to it.
      function metrics() {
        var fs = parseFloat(getComputedStyle(num).fontSize), ms = parseFloat(getComputedStyle(mastB).fontSize);
        var tx = mast.offsetLeft + mastB.offsetLeft, ty = mast.offsetTop + mastB.offsetTop - ms * 0.04;
        return { x: tx - num.offsetLeft, y: ty - num.offsetTop, s: ms / fs };
      }
      var tl = gsap.timeline({ defaults: { ease: "none" } });
      tl.to(num, { x: function () { return metrics().x; }, y: function () { return metrics().y; }, scale: function () { return metrics().s; }, duration: 1.0, ease: "power2.inOut" }, 0)
        .to(word, { autoAlpha: 0, y: -26, duration: 0.34 }, 0)
        .to(range, { autoAlpha: 0, duration: 0.3 }, 0)
        .to(cue, { autoAlpha: 0, duration: 0.12 }, 0)
        .set(num, { autoAlpha: 0 }, 1.0)
        .set(mastB, { autoAlpha: 1 }, 1.0)
        .to(mast, { opacity: 1, duration: 0.3 }, 0.72);
      frags.forEach(function (f) {
        tl.to(f, { "--sz": "1900px", duration: 1.0, ease: "power2.in" }, 0)
          .to(f, { "--o": 0, duration: 0.5 }, 0.32);
      });
      // one title, then the fields: each arrives out of depth, is held, and passes
      tl.to(title, { "--z": "0px", duration: 0.7, ease: "power3.out" }, 0.55)
        .to(title, { "--o": 1, duration: 0.5 }, 0.6)
        .to(title, { "--z": "760px", duration: 0.55, ease: "power2.in" }, 1.42)
        .to(title, { "--o": 0, duration: 0.3 }, 1.42);
      cats.forEach(function (el, i) {
        var f = F[i];
        tl.to(el, { "--z": "0px", duration: 0.8, ease: "power3.out" }, f - 0.8)
          .to(el, { "--o": 1, duration: 0.4, ease: "power1.out" }, f - 0.42)
          .to(el, { "--z": "680px", duration: 0.5, ease: "power2.in" }, f + 0.22)
          .to(el, { "--o": 0, duration: 0.22, ease: "power1.in" }, f + 0.22);
      });
      tl.to(index, { opacity: 1, duration: 0.4 }, F[0] - 0.7)
        .to(index, { opacity: 0, duration: 0.4 }, F[F.length - 1] + 0.3)
        .to(mast, { opacity: 0, duration: 0.25 }, F[F.length - 1] + 0.5);
      var DUR = tl.duration();
      w.style.setProperty("--units", DUR.toFixed(3));

      // A little lean when the scroll is quick, gone as it slows.
      var skew = gsap.quickTo(scene, "skewY", { duration: 0.6, ease: "power3.out" });
      var active = -1;
      var st = ScrollTrigger.create({
        trigger: w, start: "top top", end: "bottom bottom", animation: tl, scrub: 0.5, invalidateOnRefresh: true,
        onUpdate: function (self) {
          var t = self.progress * DUR;
          for (var i = 0; i < cats.length; i++) cats[i].classList.toggle("is-near", t > F[i] - 0.95 && t < F[i] + 0.85);
          var a = -1, best = 9;
          for (var j = 0; j < cats.length; j++) { var d = Math.abs(t - F[j]); if (d < best) { best = d; a = j; } }
          if (t < F[0] - 0.55 || t > F[F.length - 1] + 0.5) a = -1;
          if (a !== active) {
            active = a;
            links.forEach(function (l, k) { if (k === a) l.setAttribute("aria-current", "true"); else l.removeAttribute("aria-current"); });
          }
          index.classList.toggle("is-on", a >= 0);
          skew(clamp(self.getVelocity() / -1600, -1.4, 1.4));
        }
      });
      var onEnd = function () { skew(0); };
      ScrollTrigger.addEventListener("scrollEnd", onEnd);
      cleanups.push(function () { ScrollTrigger.removeEventListener("scrollEnd", onEnd); });

      // The field index, and keyboard focus, travel by scroll position.
      function goToCat(i) { scrollToY(st.start + (F[i] / DUR) * (st.end - st.start)); }
      links.forEach(function (a, i) {
        listen(a, "click", function (e) { if (e.button !== 0 || e.metaKey || e.ctrlKey) return; e.preventDefault(); goToCat(i); });
      });
      cats.forEach(function (el, i) {
        listen(el, "focusin", function () {
          var t = st.progress * DUR;
          if (Math.abs(t - F[i]) > 0.35) scrollToY(st.start + (F[i] / DUR) * (st.end - st.start), true);
        });
      });

      // The pointer steers only once the entrance has settled, and eases in.
      var px = { x: 0, y: 0 }, tgt = { x: 0, y: 0 };
      var setPX = gsap.quickSetter(hero, "--px", "px"), setPY = gsap.quickSetter(hero, "--py", "px");
      var rotY = gsap.quickTo(scene, "rotationY", { duration: 1.1, ease: "power3.out" });
      var rotX = gsap.quickTo(scene, "rotationX", { duration: 1.1, ease: "power3.out" });
      listen(window, "pointermove", function (e) {
        tgt.x = (e.clientX / vw() - 0.5) * 2; tgt.y = (e.clientY / vh() - 0.5) * 2;
      }, { passive: true });
      var tick = function () {
        // Track from the first move; let it steer in as pointerState.w rises.
        px.x += (tgt.x - px.x) * 0.04; px.y += (tgt.y - px.y) * 0.04;
        var g = pointerState.w * (1 - smooth(st.progress * DUR / 0.9));
        setPX(px.x * 26 * g); setPY(px.y * 16 * g);
        rotY(px.x * 1.2 * g); rotX(-px.y * 0.8 * g);
      };
      gsap.ticker.add(tick);
      cleanups.push(function () { gsap.ticker.remove(tick); gsap.set([scene, hero], { clearProps: "transform,--px,--py" }); });

      entrance(true);
    })();

    /* --- counted, not claimed --------------------------------------------------- */
    (function counted() {
      var sec = $("[data-lr-count]"), stage = $(".lr-count__stage", sec);
      var title = $("[data-lr-count-title]", sec), stats = $$(".lr-stat", sec), ledger = $$("[data-lr-ledger] li", sec);
      var STEP = 0.95, F0 = 1.35;
      var F = stats.map(function (_, i) { return F0 + STEP * i; });
      gsap.set(ledger, { opacity: 0 });
      gsap.set(title, { "--z": "0px", "--o": 1 });
      stats.forEach(function (s) { gsap.set(s, { "--z": "-1800px", "--o": 0, "--fo": 0, "--fx": "0px", "--fy": "0px", "--fs": 1 }); });
      var tl = gsap.timeline({ defaults: { ease: "none" } });
      tl.to(title, { "--z": "900px", duration: 0.65, ease: "power2.in" }, 0.45)
        .to(title, { "--o": 0, duration: 0.35 }, 0.5);
      stats.forEach(function (s, i) {
        var f = F[i];
        tl.to(s, { "--z": "0px", duration: 0.75, ease: "power3.out" }, f - 0.8)
          .to(s, { "--fo": 1, duration: 0.5, ease: "power1.out" }, f - 0.78)
          .to(s, { "--o": 1, duration: 0.3 }, f - 0.22)
          .to(s, { "--o": 0, duration: 0.24 }, f + 0.3)
          .to(s, { "--fx": function () { return (-0.37 * vw()) + "px"; }, "--fy": function () { return (-0.31 * vh()) + "px"; }, "--fs": 0.2, duration: 0.7, ease: "power2.inOut" }, f + 0.3)
          .to(s, { "--fo": 0, duration: 0.3 }, f + 0.72);
        tl.to(ledger[i], { opacity: 1, duration: 0.3 }, f + 0.78);
      });
      var DUR = tl.duration() + 0.2;
      tl.to({}, { duration: 0.2 }, DUR - 0.2);
      sec.style.setProperty("--count-units", DUR.toFixed(3));
      ScrollTrigger.create({
        trigger: sec, start: "top top", end: "bottom bottom", animation: tl, scrub: 0.5, invalidateOnRefresh: true,
        onUpdate: function (self) {
          var t = self.progress * DUR;
          stats.forEach(function (s, i) { s.classList.toggle("is-near", t > F[i] - 1.0 && t < F[i] + 1.0); });
        }
      });
    })();

    /* --- the reel: the years come toward the reader ---------------------------- */
    (function reel() {
      var sec = $("[data-lr-reel]"), stage = $(".lr-reel__stage", sec), list = $("[data-lr-milestones]", sec);
      var planes = $$(".lr-ms", list), n = planes.length;
      var head = $("[data-lr-reel-head]", sec), rail = $("[data-lr-rail]", sec), railBtns = $$("button", rail);
      var final = $("[data-lr-final]", sec);
      var LEAD = 0.6, TAIL = 1.05, S = LEAD + (n - 1) + TAIL;
      var SP = 1050;                                   // px of depth between years
      sec.style.setProperty("--S", S.toFixed(3));

      // The last milestone opens into the first featured story: that story lives
      // inside the stage while the reel runs, and goes home when the mode changes.
      var first = features[0], home = first ? first.parentNode : null, homeNext = first ? first.nextSibling : null;
      var finalFrame = null, finalLines = null;
      if (first) {
        final.appendChild(first);
        first.classList.add("is-seen");
        finalFrame = $(".lr-feature__frame", first);
        cleanups.push(function () {
          if (home) home.insertBefore(first, homeNext);
          first.removeAttribute("style"); first.classList.remove("is-seen");
          final.removeAttribute("style");
        });
      }
      var pl = planes.map(function (p) {
        return { el: p, i: +p.getAttribute("data-i"), s: (+p.getAttribute("data-i")) % 2 ? 1 : -1, near: false, focus: false };
      });
      var rect = { x: 0, y: 0, w: 0, h: 0 };
      function measure() {
        var last = planes[n - 1], frame = $(".lr-ms__frame", last), inner = $(".lr-ms__inner", last);
        rect.x = last.offsetLeft + inner.offsetLeft + frame.offsetLeft;
        rect.y = last.offsetTop + inner.offsetTop + frame.offsetTop;
        rect.w = frame.offsetWidth; rect.h = frame.offsetHeight;
      }
      // dwell: each year is held at the focal point before the next comes on
      function camera(u) {
        if (u <= LEAD) return { P: -1.05 + 1.05 * smooth(u / LEAD), tail: 0 };
        var f = u - LEAD;
        if (f >= n - 1) return { P: n - 1, tail: clamp((f - (n - 1)) / TAIL, 0, 1) };
        var k = Math.floor(f), r = f - k;
        return { P: k + smooth((r - 0.2) / 0.6), tail: 0 };
      }
      var lastFocus = -1;
      function place(u) {
        var cam = camera(u), P = cam.P, tail = cam.tail, A = vw() * 0.15;
        var fade = 1 - smooth(tail / 0.42);                  // the planes give way to the opening story
        pl.forEach(function (q) {
          var d = q.i - P, ad = Math.abs(d), e = smooth(Math.min(ad, 1.25) / 1.25);
          var z = -d * SP, x = q.s * A * e * (d < 0 ? 1.6 : 1), y = (q.i % 3 - 1) * 14 * Math.min(ad, 1);
          var ry = -q.s * 9 * smooth(clamp(d, 0, 1.3) / 1.3);
          var o = d <= 0 ? clamp(1 + d / 0.34, 0, 1) : clamp(1 - d / 0.85, 0, 1);
          if (q.i === n - 1) o *= fade;
          var el = q.el, st = el.style;
          st.setProperty("--x", x.toFixed(1) + "px"); st.setProperty("--y", y.toFixed(1) + "px");
          st.setProperty("--z", z.toFixed(1) + "px"); st.setProperty("--ry", ry.toFixed(2) + "deg");
          st.setProperty("--o", o.toFixed(3));
          var near = d > -0.65 && d < 2.05;
          if (near !== q.near) { q.near = near; el.classList.toggle("is-near", near); }
          var foc = ad < 0.3 && o > 0.6;
          if (foc !== q.focus) { q.focus = foc; el.classList.toggle("is-focus", foc); }
        });
        // the years, and where we are among them
        var cur = clamp(Math.round(P), 0, n - 1);
        if (cur !== lastFocus) {
          lastFocus = cur;
          railBtns.forEach(function (b, k) { if (k === cur) b.setAttribute("aria-current", "true"); else b.removeAttribute("aria-current"); });
        }
        rail.style.setProperty("--p", clamp(P / (n - 1), 0, 1).toFixed(3));
        rail.style.opacity = String(clamp((u - 0.1) / 0.5, 0, 1) * (1 - smooth(tail / 0.25)));
        head.style.opacity = String(1 - smooth((P + 0.72) / 0.5));
        // the opening story: the milestone's picture grows into the window
        if (first) {
          var g = easeOut(clamp(tail / 0.6, 0, 1));
          final.style.visibility = tail > 0 ? "visible" : "hidden";
          final.style.opacity = tail > 0 ? "1" : "0";
          final.style.pointerEvents = tail > 0.7 ? "auto" : "none";
          finalFrame.style.left = lerp(rect.x, 0, g).toFixed(1) + "px";
          finalFrame.style.top = lerp(rect.y, 0, g).toFixed(1) + "px";
          finalFrame.style.width = lerp(rect.w, vw(), g).toFixed(1) + "px";
          finalFrame.style.height = lerp(rect.h, vh(), g).toFixed(1) + "px";
          finalFrame.style.setProperty("--sc", smooth((tail - 0.3) / 0.4).toFixed(3));
          first.style.setProperty("--lt", smooth((tail - 0.55) / 0.42).toFixed(3));
        }
      }
      var st = ScrollTrigger.create({
        trigger: sec, start: "top top", end: "bottom bottom", scrub: true, invalidateOnRefresh: true,
        onRefresh: function (self) { measure(); place(self.progress * S); },
        onUpdate: function (self) { place(self.progress * S); }
      });
      // Set the first frame before anything can be seen of it.
      measure(); place(st.progress * S);

      function goTo(i) { scrollToY(st.start + ((LEAD + i) / S) * (st.end - st.start)); }
      railBtns.forEach(function (b) { listen(b, "click", function () { goTo(+b.getAttribute("data-go")); }); });
      pl.forEach(function (q) {
        listen(q.el, "focusin", function () {
          if (!q.focus) scrollToY(st.start + ((LEAD + q.i) / S) * (st.end - st.start), true);
        });
      });
      // arrow keys move between years while the reel has focus
      listen(rail, "keydown", function (e) {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        var b = document.activeElement && document.activeElement.closest("button"); var k = railBtns.indexOf(b);
        if (k < 0) return;
        var nk = clamp(k + (e.key === "ArrowRight" ? 1 : -1), 0, n - 1);
        e.preventDefault(); railBtns[nk].focus(); goTo(nk);
      });
    })();

    /* --- the featured stories: a little depth, no more ------------------------- */
    features.slice(1).forEach(function (f) {
      gsap.fromTo(f, { "--py": -5 }, { "--py": 5, ease: "none", scrollTrigger: { trigger: f, start: "top bottom", end: "bottom top", scrub: true } });
    });

    return function () { cleanups.forEach(function (fn) { fn(); }); };
  });

  // Heights that depend on fonts and images are settled by now.
  window.addEventListener("load", function () { ScrollTrigger.refresh(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
})();
