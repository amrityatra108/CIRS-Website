/* ============================================================
   Leadership — "In their own words"
   ------------------------------------------------------------
   The markup holds all five messages in full, one after another,
   so with no scripting every message is read and every #msg-…
   link lands. A small script in <head> (tools/leadership.py)
   marks <html> with the message the URL names before first
   paint, and CSS shows only that one; this file wires up the
   index that chooses between them.

   One state, three controls that show it:
     html[data-ld-msg]      which message is shown
     the tab list           from 900px: a vertical index
     the select             below 900px: a labelled picker
   The URL follows too: a choice made in the index replaces the
   history entry (#msg-…), so the address can be shared without
   filling Back with every name clicked; a "Read message" link is
   an ordinary fragment link and so makes its own entry, which
   Back and Forward walk. Nothing changes the message except the
   reader: there is no timer and no rotation.

   The page keeps the browser's own scroll (cirs.js leaves
   Lenis off here), so fragment links, scroll-margin and history
   restoration are all native.
   ============================================================ */
(function () {
  "use strict";
  var root = document.documentElement;
  var reader = document.querySelector("[data-ld-reader]");
  window.__ldBooted = true;
  if (!reader) return;

  var tabs = Array.prototype.slice.call(reader.querySelectorAll('[role="tab"]'));
  var select = reader.querySelector(".ld-idx__select");
  var now = reader.querySelector(".ld-idx__now");
  var sheet = reader.querySelector(".ld-sheet");
  var ids = tabs.map(function (t) { return t.id.replace("msg-tab-", ""); });
  if (!ids.length) return;

  var still = window.matchMedia("(prefers-reduced-motion: reduce)");

  function panel(id) { return document.getElementById("msg-" + id); }
  function current() {
    var id = root.getAttribute("data-ld-msg");
    return ids.indexOf(id) > -1 ? id : ids[0];
  }
  function fromHash() {
    var id = window.location.hash.replace(/^#msg-/, "");
    return ids.indexOf(id) > -1 ? id : null;
  }

  function show(id, animate) {
    var was = current();
    root.setAttribute("data-ld-msg", id);
    tabs.forEach(function (t, i) {
      var on = ids[i] === id;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
    });
    if (select) {
      select.value = id;
      var opt = select.options[select.selectedIndex];
      if (now && opt) now.textContent = opt.getAttribute("data-role");
    }
    // A short fade on the new message — its portrait, name, role and text
    // arrive together, as one change. Never on the first paint, never under
    // reduced motion, never when nothing changed.
    var p = panel(id);
    if (p && animate && was !== id && !still.matches) {
      p.classList.remove("is-entering");
      void p.offsetWidth;
      p.classList.add("is-entering");
    }
  }

  // Deep in a long letter, a new choice would otherwise leave the reader
  // looking at the middle, or the end, of a different message. Bring the new
  // one's opening into view — only then; a short page is left where it is.
  function keepStartInView(id) {
    var p = panel(id);
    if (!p) return;
    var margin = parseFloat(getComputedStyle(p).scrollMarginTop) || 0;
    if (sheet.getBoundingClientRect().top < margin - 1) {
      p.scrollIntoView({ block: "start", behavior: still.matches ? "auto" : "smooth" });
    }
  }

  function choose(id, focusTab) {
    show(id, true);
    if (window.history && history.replaceState) {
      history.replaceState(history.state, "", "#msg-" + id);
    }
    keepStartInView(id);
    if (focusTab) tabs[ids.indexOf(id)].focus();
  }

  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { choose(ids[i], false); });
    t.addEventListener("keydown", function (e) {
      var n = tabs.length, to = null;
      if (e.key === "ArrowDown" || e.key === "ArrowRight") to = (i + 1) % n;
      else if (e.key === "ArrowUp" || e.key === "ArrowLeft") to = (i - 1 + n) % n;
      else if (e.key === "Home") to = 0;
      else if (e.key === "End") to = n - 1;
      if (to === null) return;
      e.preventDefault();
      choose(ids[to], true);
    });
  });

  if (select) {
    select.addEventListener("change", function () {
      if (ids.indexOf(select.value) > -1) choose(select.value, false);
    });
  }

  // "Read message" beside a portrait. It stays a plain #msg-… link: this only
  // shows the right message a moment before the browser follows it, so the
  // browser scrolls to a panel that is there to be scrolled to, records the
  // step in history, and leaves the message's heading clear of the fixed
  // header by the panel's scroll-margin. Focus then moves to the message, so
  // a keyboard reader continues from where they were sent.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[data-ld-msg]");
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var id = a.getAttribute("data-ld-msg");
    if (ids.indexOf(id) < 0) return;
    show(id, false);
    window.setTimeout(function () {
      var p = panel(id);
      if (p) p.focus({ preventScroll: true });
    }, 0);
  }, true);

  // Back and Forward between #msg-… entries. The browser restores the scroll
  // position itself; this only puts the matching message back. An entry that
  // names no message leaves the current one alone.
  function sync() {
    var id = fromHash();
    if (id && id !== current()) show(id, false);
  }
  window.addEventListener("popstate", sync);
  window.addEventListener("hashchange", sync);

  show(fromHash() || current(), false);
})();
