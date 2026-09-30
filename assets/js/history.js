/* ============================================================
   School History — the depth sequence, the archive, the records
   ------------------------------------------------------------
   Progressive enhancement over tools/pages/school-history.html.
   Without this file the chapters are a column and every record's
   full text sits under its card.

   STAGE  On a wide, tall window with motion allowed, the chapters
          become one bounded sticky sequence (html.hx-staged). Each
          chapter holds still for most of its stretch of scroll, then
          hands over: the outgoing exhibit drifts left and recedes, the
          next comes forward and straightens, and the text changes in
          its own column without moving. After the sixth, the six
          exhibits pull back into a grid, and the archive follows.
          Only transform and opacity are written, and only while the
          sequence is on screen; exhibits far from the current one are
          hidden rather than animated.
   LIST   Everywhere else: ordinary scrolling, and the two designed
          compositions simply settle when they come into view.
   RECORD Every archive card opens its record in a dialog. The URL
          names it (#record-<id>), Back closes it, Escape closes it,
          and focus returns to the card.
   ============================================================ */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("hx-js");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var wide = window.matchMedia("(min-width: 1000px) and (min-height: 620px)");
  var motion = !reduced.matches;
  if (motion) root.classList.add("hx-motion");

  // Scroll lengths, in window heights. Six chapters of SEG each, the last
  // followed by OVER for the pull back into the grid: 6 x .62 + .6 = 4.3
  // heights of scroll, in a section 5.3 heights tall.
  var SEG = 0.62, OVER = 0.6;
  // The share of each chapter's stretch in which nothing moves.
  var HOLD = 0.58;

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.min(b === undefined ? 1 : b, Math.max(a || 0, v)); };
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var ease = function (t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };

  var seq = $("#chapters");
  var list = seq && $(".hx-chapters", seq);
  var chapters = seq ? $$(".hx-ch", seq) : [];
  var navLinks = seq ? $$("[data-hx-jump]", seq) : [];
  if (!seq || !chapters.length) return;
  var N = chapters.length;

  var parts = chapters.map(function (li, i) {
    return {
      li: li,
      text: $(".hx-ch__text", li),
      ex: $(".hx-ex", li),
      kind: $(".hx-ex", li).getAttribute("data-exhibit"),
      home: null
    };
  });

  /* The overview's captions: each exhibit's date and chapter, written
     under it once the arrangement has settled. Decorative — the same
     words are in the chapter text and the navigation. */
  parts.forEach(function (p, i) {
    var cap = document.createElement("span");
    cap.className = "hx-ex__cap";
    cap.setAttribute("aria-hidden", "true");
    var when = $(".hx-ch__when", p.li).lastChild.textContent.trim();
    var short = navLinks[i] ? $(".hx-nav__t", navLinks[i]).textContent : "";
    cap.innerHTML = "<b></b>";
    cap.firstChild.textContent = when;
    cap.appendChild(document.createTextNode(short));
    p.ex.appendChild(cap);
  });

  // The overview's one line, under the arrangement.
  var over = document.createElement("p");
  over.className = "hx-stage__over";
  over.setAttribute("aria-hidden", "true");
  over.textContent = "The complete archive follows";
  $(".hx-stage", seq).appendChild(over);

  /* ==========================================================
     Mode
     ========================================================== */
  var staged = false, vh = window.innerHeight, current = -1, rafId = 0;

  function setMode() {
    var want = motion && wide.matches;
    if (want === staged) { if (staged) layout(); return; }
    staged = want;
    root.classList.toggle("hx-staged", staged);
    if (!staged) {
      seq.style.removeProperty("--hx-seq-h");
      parts.forEach(function (p) {
        p.li.style.zIndex = ""; p.li.classList.remove("is-current");
        p.ex.style.transform = ""; p.ex.style.opacity = ""; p.ex.style.visibility = "";
        p.ex.style.removeProperty("--dim"); p.ex.style.removeProperty("--capo"); p.ex.style.removeProperty("--a");
        p.text.style.opacity = ""; p.text.removeAttribute("data-hidden");
      });
      current = -1;
      watchList();
    } else {
      unwatchList();
      layout();
    }
  }

  /* ==========================================================
     STAGE
     ========================================================== */
  function layout() {
    vh = window.innerHeight;
    seq.style.setProperty("--hx-seq-h", Math.round((N * SEG + OVER + 1) * vh) + "px");
    // Measure every exhibit where it sits untransformed, for the grid.
    parts.forEach(function (p) { p.ex.style.transform = "none"; });
    var box = list.getBoundingClientRect();
    parts.forEach(function (p) {
      var r = p.ex.getBoundingClientRect();
      p.home = { cx: r.left + r.width / 2 - box.left, cy: r.top + r.height / 2 - box.top, w: r.width, h: r.height };
    });
    var cols = 3, rows = Math.ceil(N / cols);
    var cw = box.width / cols, ch = (box.height - 64) / rows;
    parts.forEach(function (p, i) {
      var col = i % cols, row = Math.floor(i / cols);
      var tx = (col + .5) * cw, ty = row * ch + ch * .44;
      var s = Math.min(cw * .56 / p.home.w, ch * .64 / p.home.h);
      p.grid = { x: tx - p.home.cx, y: ty - p.home.cy, s: s };
      p.visW = p.ex.parentNode.getBoundingClientRect().width;
    });
    render();
  }

  // The stack: where an exhibit sits at a given distance from the front.
  // Positive distances wait behind, to the right; negative ones have left.
  function stack(d, visW) {
    if (d >= 0) {
      var k = Math.min(d, 2.4);
      return { x: k * .14 * visW, y: -k * .035 * vh, z: -k * 190,
               ry: -Math.min(d, 1.4) * 3.4, op: d <= 2 ? 1 : clamp(3 - d), dim: k * .2 };
    }
    var a = -d;
    return { x: -a * .62 * visW, y: 0, z: -a * 160, ry: Math.min(a, 1) * 4.5,
             op: clamp(1 - a * 1.4), dim: Math.min(a, 1) * .35 };
  }

  function render() {
    rafId = 0;
    if (!staged) return;
    var r = seq.getBoundingClientRect();
    // Nothing to draw while the sequence is off screen.
    if (r.bottom < -vh * .2 || r.top > vh * 1.2) return;
    var d = clamp(-r.top / vh, 0, N * SEG + OVER);
    // i is the chapter being read; g runs 0 to 1 through its hand-over.
    // The outgoing exhibit leaves early in g and the incoming one arrives
    // late, so the two are never both in the front at once.
    var p = d / SEG, i, g = 0, o = 0;
    if (p >= N) { i = N - 1; o = ease(clamp((d - N * SEG) / OVER)); }
    else {
      i = Math.floor(p);
      if (i < N - 1) g = clamp((p - i - HOLD) / (1 - HOLD));
    }
    var out = ease(clamp(g / .62)), inn = ease(clamp((g - .28) / .72));
    var v = i + (out + inn) / 2;

    parts.forEach(function (part, j) {
      var dist = j < i ? j - i - out : j === i ? -out : j - i - inn;
      var s = stack(dist, part.visW || 400);
      var x = s.x, y = s.y, z = s.z, ry = s.ry, op = s.op, dim = s.dim, sc = 1;
      if (o > 0 && part.grid) {
        x = lerp(x, part.grid.x, o); y = lerp(y, part.grid.y, o); z = lerp(z, 0, o);
        // Those coming back from the left stay unseen until the last
        // chapter's text has gone, so nothing ever crosses words being read.
        ry = lerp(ry, 0, o); dim = lerp(dim, 0, o); sc = lerp(1, part.grid.s, o);
        op = j === i ? 1 : lerp(op, 1, clamp((o - .4) / .4));
      }
      var ex = part.ex;
      if (op < .005) {
        if (ex.style.visibility !== "hidden") ex.style.visibility = "hidden";
      } else {
        if (ex.style.visibility) ex.style.visibility = "";
        ex.style.transform = "translate3d(" + x.toFixed(1) + "px," + y.toFixed(1) + "px," + z.toFixed(1) +
          "px) rotateY(" + ry.toFixed(2) + "deg) scale(" + sc.toFixed(4) + ")";
        ex.style.opacity = op.toFixed(3);
        ex.style.setProperty("--dim", dim.toFixed(3));
        ex.style.setProperty("--capo", clamp((o - .6) / .3).toFixed(3));
        ex.style.setProperty("--s", sc.toFixed(4));
      }
      // Front-most on top. What is leaving stays over what is arriving
      // until it has all but faded, then drops beneath it.
      var a = -dist;
      part.li.style.zIndex = String(Math.round(dist >= 0 ? 100 - dist * 10
                                                        : (a < .8 ? 101 - a * 10 : 80 - a * 10)));

      // The text never moves; it only fades, and only in the hand-over.
      // Its own column: the outgoing text is gone in the first two-fifths
      // of the hand-over, the incoming one in place by the last fifth.
      var t = j === i ? 1 - clamp(g / .4) : j === i + 1 ? clamp((g - .45) / .4) : 0;
      t *= 1 - clamp(o * 3.2);
      part.text.style.opacity = t.toFixed(3);
      if (t < .01) part.text.setAttribute("data-hidden", "");
      else part.text.removeAttribute("data-hidden");
    });

    // One rupee at a time: the marks gather as the chapter arrives.
    parts.forEach(function (part, j) {
      if (part.kind === "rupee") part.ex.style.setProperty("--a", clamp((p - j + .45) / .75).toFixed(3));
      if (part.kind === "opening") part.ex.classList.toggle("is-on", v > j - .4);
    });

    if (over) over.style.setProperty("--o", clamp((o - .65) / .3).toFixed(3));

    var now = o > .5 ? -1 : Math.round(v);
    if (now !== current) {
      current = now;
      parts.forEach(function (part, j) { part.li.classList.toggle("is-current", j === now); });
      markNav(now);
    }
  }

  function schedule() { if (!rafId) rafId = requestAnimationFrame(render); }
  window.addEventListener("scroll", schedule, { passive: true });

  var resizeTimer = 0;
  window.addEventListener("resize", function () {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(setMode, 120);
  });
  if (wide.addEventListener) wide.addEventListener("change", setMode);
  if (reduced.addEventListener) reduced.addEventListener("change", function () {
    motion = !reduced.matches;
    root.classList.toggle("hx-motion", motion);
    setMode();
  });

  function markNav(i) {
    navLinks.forEach(function (a, k) {
      if (k === i) a.setAttribute("aria-current", "step");
      else a.removeAttribute("aria-current");
    });
  }

  // Where chapter k's still interval begins.
  function chapterTop(k) {
    var top = seq.getBoundingClientRect().top + window.scrollY;
    return Math.round(top + (k * SEG + .03) * vh);
  }

  function goTo(top, instant) {
    var ev = new CustomEvent("cirs-section-scroll", { cancelable: true,
      detail: { top: top, duration: instant ? 0.01 : 1.1 } });
    // Lenis takes the request when it is running; otherwise, the window.
    if (window.dispatchEvent(ev)) window.scrollTo({ top: top, behavior: instant || !motion ? "auto" : "smooth" });
  }

  function jumpToChapter(k, instant) {
    var text = parts[k] && parts[k].text;
    if (!text) return;
    goTo(chapterTop(k), instant);
    if (!text.hasAttribute("tabindex")) text.setAttribute("tabindex", "-1");
    window.setTimeout(function () { text.focus({ preventScroll: true }); }, instant ? 0 : 1150);
  }

  /* ==========================================================
     LIST
     ========================================================== */
  var io = null;
  function watchList() {
    if (!("IntersectionObserver" in window) || io) return;
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var k = chapters.indexOf(e.target);
        if (e.isIntersecting) {
          var ex = parts[k].ex;
          if (parts[k].kind === "rupee" || parts[k].kind === "opening") ex.classList.add("is-on");
          markNav(k);
        }
      });
    }, { rootMargin: "-35% 0px -45% 0px" });
    chapters.forEach(function (li) { io.observe(li); });
  }
  function unwatchList() { if (io) { io.disconnect(); io = null; } }

  /* ==========================================================
     The archive: filters
     ========================================================== */
  var grid = $("#hx-grid");
  var items = grid ? $$(".hx-item", grid) : [];
  var filters = $$("[data-hx-filter]");
  var status = $("#hx-archive-status");
  filters.forEach(function (b) {
    b.addEventListener("click", function () {
      var key = b.getAttribute("data-hx-filter"), shown = 0;
      filters.forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
      items.forEach(function (it) {
        var on = key === "all" || it.getAttribute("data-hx-period") === key;
        it.hidden = !on;
        if (on) shown++;
      });
      if (status) status.textContent = shown + (shown === 1 ? " record" : " records") +
        (key === "all" ? "" : ": " + b.firstChild.textContent.trim());
    });
  });

  /* ==========================================================
     RECORD: one record in its own view
     ========================================================== */
  var dlg = $("#hx-dialog"), body = $("#hx-dialog-body");
  var openId = null, opener = null;

  function visibleIds() {
    return items.filter(function (it) { return !it.hidden; })
                .map(function (it) { return $(".hx-rec", it).id.slice(7); });
  }

  function fill(id) {
    var rec = document.getElementById("record-" + id);
    if (!rec || !body) return false;
    var detail = $(".hx-rec__detail", rec).cloneNode(true);
    var title = $(".hx-rec__title", detail);
    title.id = "hx-dialog-title";
    if ($(".hx-rec__figure", detail)) detail.classList.add("has-figure");
    var img = $("img", detail);
    if (img) { img.setAttribute("sizes", "(max-width: 760px) 92vw, 900px"); img.removeAttribute("loading"); }
    body.replaceChildren(detail);
    openId = id;
    var ids = visibleIds(), k = ids.indexOf(id);
    $("[data-hx-step='-1']", dlg).disabled = k <= 0;
    $("[data-hx-step='1']", dlg).disabled = k < 0 || k >= ids.length - 1;
    return true;
  }

  function lock(on) {
    window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: on } }));
  }

  function openRecord(id, from, push) {
    if (!dlg || !fill(id)) return;
    opener = from || $("[data-hx-open='" + id + "']");
    if (!dlg.open) { dlg.showModal(); lock(true); }
    if (push) history.pushState({ hxRecord: id }, "", "#record-" + id);
    $("[data-hx-close]", dlg).focus();
  }

  function closeRecord(fromHistory) {
    if (!dlg || !dlg.open) return;
    dlg.close();
    body.replaceChildren();
    lock(false);
    if (!fromHistory) {
      // A record this page opened is one step of history: go back past it.
      // One arrived at by link is the page's own address: drop the hash.
      if (history.state && history.state.hxRecord) history.back();
      else history.replaceState(null, "", location.pathname + location.search);
    }
    var back = opener && document.contains(opener) && opener.offsetParent ? opener : $("#hx-archive-title");
    if (back) {
      if (!back.hasAttribute("tabindex") && back.tagName === "H2") back.setAttribute("tabindex", "-1");
      back.focus({ preventScroll: false });
    }
    openId = null; opener = null;
  }

  if (dlg) {
    dlg.addEventListener("cancel", function (e) { e.preventDefault(); closeRecord(false); });
    dlg.addEventListener("click", function (e) {
      if (e.target === dlg || e.target.closest("[data-hx-close]")) closeRecord(false);
      var step = e.target.closest("[data-hx-step]");
      if (step && !step.disabled) {
        var ids = visibleIds(), k = ids.indexOf(openId) + Number(step.getAttribute("data-hx-step"));
        if (ids[k]) {
          fill(ids[k]);
          opener = $("[data-hx-open='" + ids[k] + "']");
          history.replaceState(history.state && history.state.hxRecord ? { hxRecord: ids[k] } : null,
                               "", "#record-" + ids[k]);
          step.disabled ? $("[data-hx-close]", dlg).focus() : step.focus();
        }
      }
    });
  }

  $$("[data-hx-open]").forEach(function (b) {
    b.addEventListener("click", function () { openRecord(b.getAttribute("data-hx-open"), b, true); });
  });

  window.addEventListener("popstate", function () {
    var m = /^#record-([a-z0-9-]+)$/.exec(location.hash);
    if (m && document.getElementById("record-" + m[1])) openRecord(m[1], null, false);
    else closeRecord(true);
  });

  /* ==========================================================
     Links into the sequence and the archive
     Caught before cirs.js's own anchor handler, which would scroll to
     the element: on the stage a chapter's element is not where its
     chapter is read, and a record is read in the dialog.
     ========================================================== */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-hx-jump], [data-hx-record]");
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (a.hasAttribute("data-hx-record")) {
      e.preventDefault(); e.stopPropagation();
      openRecord(a.getAttribute("data-hx-record"), a, true);
      return;
    }
    if (!staged) return;           // the list: an ordinary anchor
    e.preventDefault(); e.stopPropagation();
    jumpToChapter(Number(a.getAttribute("data-hx-jump")));
  }, true);

  /* An address that names a chapter or a record. cirs.js offers the jump
     to the page first; this claims the ones it would get wrong. */
  var hashDone = false;
  function claim(target) {
    if (!target || hashDone) return false;
    if (target.classList.contains("hx-rec")) {
      hashDone = true;
      var card = $(".hx-card", target);
      window.scrollTo(0, target.getBoundingClientRect().top + window.scrollY - vh * .3);
      openRecord(target.id.slice(7), card, false);
      return true;
    }
    if (target.classList.contains("hx-ch") && staged) {
      hashDone = true;
      jumpToChapter(chapters.indexOf(target), true);
      return true;
    }
    return false;
  }
  window.addEventListener("cirs-hash-open", function (e) {
    var t = e.detail && e.detail.target;
    if (t && (t.classList.contains("hx-rec") || (t.classList.contains("hx-ch") && staged))) {
      e.preventDefault();
      claim(t);
    }
  });

  setMode();
  if (!staged) watchList();
  window.addEventListener("load", function () {
    if (staged) layout();
    if (!hashDone && location.hash.length > 1) {
      var t = null;
      try { t = document.querySelector(location.hash); } catch (err) { t = null; }
      claim(t);
    }
  });
})();
