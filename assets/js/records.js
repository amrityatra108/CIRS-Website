/* ============================================================
   THE CIRS RECORD — School Information
   ------------------------------------------------------------
   Four jobs, none of which the page needs in order to be read:
   without this file the sheets lie still, the index is a list
   of links and the register is the complete list.

     1. depth    the first screen of scroll moves the sheets
                 apart: one toward the reader, three away. It
                 writes one number, --p, and CSS does the rest.
                 Off below 700px and under reduced motion.
     2. index    marks the section on screen, and keeps it in
                 view in the strip the index becomes on a phone.
     3. jumps    every #link on the page lands its target clear
                 of the header and that strip, then moves focus
                 to it. cirs.js aims for 88px from the top, which
                 is under the strip below 1200px.
     4. register search by title, one category at a time, a
                 count, and a way back from an empty result.
   ============================================================ */
(function () {
  "use strict";

  var body = document.body;
  if (!body || !body.classList.contains("records")) return;

  var root = document.documentElement;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var wideStage = window.matchMedia("(min-width: 700px)");
  var railed = window.matchMedia("(min-width: 1200px)");

  function onChange(mq, fn) {
    if (mq.addEventListener) mq.addEventListener("change", fn);
    else if (mq.addListener) mq.addListener(fn);
  }
  function scrollTop() { return window.scrollY || window.pageYOffset || 0; }

  /* The header takes its glass as soon as the page moves: the sheets rise
     under it. See the note on rec-moved in records.css. */
  var moved = null;
  function markMoved() {
    var now = scrollTop() > 24;
    if (now === moved) return;
    moved = now;
    body.classList.toggle("rec-moved", now);
  }
  window.addEventListener("scroll", markMoved, { passive: true });
  markMoved();

  /* ----------------------------------------------------------
     1. Depth
     ---------------------------------------------------------- */
  var open = document.querySelector(".rec-open");
  var depthOn = false, ticking = false, last = -1, span = 1;

  function measureDepth() { span = Math.max(1, open.offsetHeight * 0.9); }
  function paintDepth() {
    ticking = false;
    var p = Math.min(1, Math.max(0, scrollTop() / span));
    p = Math.round(p * 1000) / 1000;
    if (p === last) return;
    last = p;
    open.style.setProperty("--p", String(p));
  }
  function onDepthScroll() {
    if (!ticking) { ticking = true; window.requestAnimationFrame(paintDepth); }
  }
  function setDepth() {
    var want = !!open && wideStage.matches && !reduced.matches;
    if (want === depthOn) { if (want) { measureDepth(); paintDepth(); } return; }
    depthOn = want;
    root.classList.toggle("rec-depth", want);
    if (want) {
      measureDepth();
      window.addEventListener("scroll", onDepthScroll, { passive: true });
      paintDepth();
    } else {
      window.removeEventListener("scroll", onDepthScroll);
      if (open) open.style.removeProperty("--p");
      last = -1;
    }
  }
  if (open) {
    setDepth();
    onChange(reduced, setDepth);
    onChange(wideStage, setDepth);
    window.addEventListener("resize", function () { if (depthOn) { measureDepth(); paintDepth(); } }, { passive: true });
  }

  /* ----------------------------------------------------------
     2. The index
     ---------------------------------------------------------- */
  var index = document.querySelector(".rec-index");
  var indexList = index && index.querySelector(".rec-index__list");
  var indexLinks = index ? Array.prototype.slice.call(index.querySelectorAll('a[href^="#"]')) : [];
  var sections = indexLinks.map(function (a) {
    return document.getElementById(a.getAttribute("href").slice(1));
  });
  var current = null, indexTicking = false;

  function barBottom() {
    // The strip's foot below 1200px; the header's above it.
    if (!railed.matches && index) return index.getBoundingClientRect().bottom;
    return 96;
  }

  function markIndex() {
    indexTicking = false;
    var line = Math.max(barBottom() + 40, window.innerHeight * 0.34);
    var found = null;
    for (var i = 0; i < sections.length; i++) {
      var s = sections[i];
      if (!s) continue;
      var r = s.getBoundingClientRect();
      if (r.top <= line && r.bottom > line) { found = i; break; }
    }
    if (found === current) return;
    current = found;
    indexLinks.forEach(function (a, i) {
      if (i === found) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
    // In the strip, keep the current section's tab in view.
    if (found !== null && indexList && !railed.matches) {
      var a = indexLinks[found];
      var left = a.offsetLeft - (indexList.clientWidth - a.offsetWidth) / 2;
      try {
        indexList.scrollTo({ left: Math.max(0, left), behavior: reduced.matches ? "auto" : "smooth" });
      } catch (err) {
        indexList.scrollLeft = Math.max(0, left);
      }
    }
  }
  function onIndexScroll() {
    if (!indexTicking) { indexTicking = true; window.requestAnimationFrame(markIndex); }
  }
  if (indexLinks.length) {
    window.addEventListener("scroll", onIndexScroll, { passive: true });
    window.addEventListener("resize", onIndexScroll, { passive: true });
    markIndex();
  }

  /* ----------------------------------------------------------
     4. The register (before 3: a jump may need to clear it)
     ---------------------------------------------------------- */
  var register = (function () {
    var reg = document.querySelector("[data-reg]");
    if (!reg) return null;

    var tools = reg.querySelector("[data-reg-tools]");
    var input = reg.querySelector("#regSearch");
    var count = reg.querySelector("[data-reg-count]");
    var empty = reg.querySelector("[data-reg-empty]");
    var reset = reg.querySelector("[data-reg-reset]");
    var filters = Array.prototype.slice.call(reg.querySelectorAll("[data-reg-filter]"));
    var groups = Array.prototype.slice.call(reg.querySelectorAll("[data-reg-group]"));
    if (!tools || !input || !count) return null;

    function words(text) {
      text = (text || "").toLowerCase();
      if (text.normalize) text = text.normalize("NFKD").replace(/[\u0300-\u036f]/g, "");
      return text.split(/[^a-z0-9]+/).filter(Boolean);
    }

    var entries = Array.prototype.slice.call(reg.querySelectorAll(".reg__row")).map(function (row) {
      var group = row.closest("[data-reg-group]");
      return {
        row: row,
        words: words(row.getAttribute("data-reg-text")),
        group: group ? group.getAttribute("data-reg-group") : ""
      };
    });
    var total = entries.length;
    var labels = {};
    filters.forEach(function (b) {
      var clone = b.cloneNode(true);
      var n = clone.querySelector(".reg__n");
      if (n) n.remove();
      labels[b.getAttribute("data-reg-filter")] = clone.textContent.trim();
    });
    groups.forEach(function (g) {
      var n = g.querySelector(".reg__cat .reg__n");
      g._label = n;
      g._text = n ? n.textContent : "";
      g._total = g.querySelectorAll(".reg__row").length;
    });

    var category = "all";

    // A word of the query matches a word of the record that begins with it —
    // "fire" finds "Fire Safety" — or one it begins with, a letter or two
    // shorter, so "fees" still finds "Fee Structure".
    function hit(entry, query) {
      return query.every(function (q) {
        return entry.words.some(function (w) {
          return w.indexOf(q) === 0 || (w.length >= 3 && w.length >= q.length - 2 && q.indexOf(w) === 0);
        });
      });
    }

    function esc(s) {
      return s.replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    }

    function apply() {
      var raw = input.value.trim();
      var query = words(raw);
      var shown = 0;
      entries.forEach(function (e) {
        var ok = (category === "all" || e.group === category) && (!query.length || hit(e, query));
        e.row.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach(function (g) {
        var visible = g.querySelectorAll(".reg__row:not([hidden])").length;
        g.hidden = visible === 0;
        if (g._label) {
          g._label.textContent = (visible === g._total) ? g._text : visible + " of " + g._text;
        }
      });
      if (empty) empty.hidden = shown !== 0;

      var text;
      if (!query.length && category === "all") {
        text = "Showing all <b>" + total + "</b> records";
      } else {
        text = "Showing <b>" + shown + "</b> of " + total + " records";
        if (category !== "all") text += " in " + esc(labels[category] || "");
        if (query.length) text += " matching &ldquo;" + esc(raw) + "&rdquo;";
      }
      count.innerHTML = text;
    }

    var timer;
    input.addEventListener("input", function () {
      window.clearTimeout(timer);
      timer = window.setTimeout(apply, 160);
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && input.value) { e.preventDefault(); input.value = ""; apply(); }
    });
    // The form-less input still submits nothing; Enter just settles the search.
    input.addEventListener("search", apply);

    function choose(value) {
      category = value;
      filters.forEach(function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-reg-filter") === value));
      });
      apply();
    }
    filters.forEach(function (b) {
      b.addEventListener("click", function () { choose(b.getAttribute("data-reg-filter")); });
    });

    function clear() {
      window.clearTimeout(timer);
      input.value = "";
      choose("all");
    }
    if (reset) reset.addEventListener("click", function () { clear(); input.focus(); });

    tools.hidden = false;
    apply();
    return { clear: clear };
  })();

  /* ----------------------------------------------------------
     3. Jumps
     ---------------------------------------------------------- */
  function offsetFor(target) {
    var clear = railed.matches ? 100 : barBottom() + 14;
    if (target.classList.contains("reg__row")) clear += 6;
    return clear;
  }

  function flag(row) {
    row.classList.add("is-flagged");
    window.setTimeout(function () { row.classList.remove("is-flagged"); }, 2400);
  }

  function arrive(target) {
    var focusable = target.matches(".rec-sec")
      ? target.querySelector(".rec-h2") || target
      : target;
    if (!focusable.hasAttribute("tabindex")) focusable.setAttribute("tabindex", "-1");
    try { focusable.focus({ preventScroll: true }); } catch (err) { focusable.focus(); }
    if (target.classList.contains("reg__row")) flag(target);
  }

  function jump(target, id) {
    if (target.hidden || (target.closest && target.closest("[hidden]"))) {
      if (register) register.clear();
    }
    var top = Math.max(0, target.getBoundingClientRect().top + scrollTop() - offsetFor(target));
    var done = false;
    function finish() { if (done) return; done = true; arrive(target); }

    // Hand the move to the site's smooth scroll when it is running; cirs.js
    // cancels this event when it has taken it.
    var ev;
    try {
      ev = new CustomEvent("cirs-section-scroll", {
        cancelable: true,
        detail: { top: top, duration: 1.05, onComplete: finish }
      });
    } catch (err) { ev = null; }
    var handled = ev && !window.dispatchEvent(ev);
    if (!handled) {
      window.scrollTo({ top: top, behavior: reduced.matches ? "auto" : "smooth" });
    }
    // A fallback for a scroll that ends without saying so.
    window.setTimeout(finish, handled ? 1400 : (reduced.matches ? 60 : 900));

    if (history.replaceState) {
      try { history.replaceState(null, "", "#" + id); } catch (err) { /* file:// */ }
    }
  }

  // Capture, so this runs before cirs.js's own handler on each link and can
  // take the in-page ones from it. Only links inside <main>: the skip link and
  // the drawer keep their own behaviour.
  document.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a || !a.closest("main")) return;
    var id = a.getAttribute("href").slice(1);
    if (!id) return;
    var target = document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    e.stopPropagation();
    jump(target, id);
  }, true);

  // Arriving with a record in the address: make sure it is showing, and mark it.
  if (/^#doc-/.test(window.location.hash)) {
    var row = document.getElementById(window.location.hash.slice(1));
    if (row) {
      window.addEventListener("load", function () {
        window.setTimeout(function () { flag(row); }, 600);
      });
    }
  }
})();
