/* ============================================================
   School History — the archive and its records
   ------------------------------------------------------------
   Progressive enhancement over tools/pages/school-history.html.
   Without this file every record's full text sits under its card.
   The journey at the top of the page is history-journey.js; this
   file only opens records, from its links or from the archive.

   RECORD Every archive card, and every "Read the record" link in
          the journey, opens its record in a dialog. The URL names
          it (#record-<id>), Back closes it, Escape closes it, and
          focus returns to where it was opened from.
   ============================================================ */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("hx-js");

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var vh = window.innerHeight;
  window.addEventListener("resize", function () { vh = window.innerHeight; });

  /* ==========================================================
     The archive: filters
     ========================================================== */
  var grid = $("#hx-grid");
  var items = grid ? $$(".hx-item", grid) : [];
  var filters = $$("[data-hx-filter]");
  var status = $("#hx-archive-status");
  var search = $("#hx-search"), decade = $("#hx-decade"), period = "all";
  var searchable = items.map(function (it) { return it.textContent.toLocaleLowerCase(); });
  var searchControls = $(".hx-search"), filterControls = $(".hx-filters");
  if (searchControls) searchControls.hidden = false;
  if (filterControls) filterControls.hidden = false;
  function filterRecords() {
    var query = search ? search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean) : [];
    var selected = decade ? decade.value : "all", shown = 0;
    items.forEach(function (it, i) {
      var on = (period === "all" || it.getAttribute("data-hx-period") === period) &&
        (selected === "all" || it.getAttribute("data-hx-decade") === selected) &&
        query.every(function (word) { return searchable[i].includes(word); });
      it.hidden = !on;
      if (on) shown++;
    });
    if (status) status.textContent = shown + " of " + items.length + " records";
    var empty = $(".hx-empty"); if (empty) empty.hidden = shown !== 0;
  }
  if (search) search.addEventListener("input", filterRecords);
  if (decade) decade.addEventListener("change", filterRecords);
  var reset = $("#hx-reset");
  if (reset) reset.addEventListener("click", function () {
    search.value = ""; decade.value = "all"; period = "all";
    filters.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-hx-filter") === "all")); });
    filterRecords(); search.focus();
  });
  filters.forEach(function (b) {
    b.addEventListener("click", function () {
      period = b.getAttribute("data-hx-filter");
      filters.forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
      filterRecords();
    });
  });
  filterRecords();

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
     Links to a record
     Caught before cirs.js's own anchor handler, which would scroll to
     the card: a record is read in the dialog, where it is.
     ========================================================== */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-hx-record]");
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault(); e.stopPropagation();
    openRecord(a.getAttribute("data-hx-record"), a, true);
  }, true);

  /* An address that names a record. cirs.js offers the jump to the page
     first; this claims it, and opens the record over its card. */
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
    return false;
  }
  window.addEventListener("cirs-hash-open", function (e) {
    var t = e.detail && e.detail.target;
    if (t && t.classList.contains("hx-rec")) {
      e.preventDefault();
      claim(t);
    }
  });

  window.addEventListener("load", function () {
    if (!hashDone && location.hash.length > 1) {
      var t = null;
      try { t = document.querySelector(location.hash); } catch (err) { t = null; }
      claim(t);
    }
  });
})();
