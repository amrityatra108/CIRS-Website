/* Navigation prototype — header, full-screen menu, Enquire.
   Carries over what production's cirs.js already does for each control
   (hover intent, keyboard focus opening Enquire, Escape, the Tab loop)
   and adds the menu's travelling marker. The header does not hide on
   scroll. Self-contained: no GSAP, no Lenis. */
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var root = document.documentElement, body = document.body;
  var header = $("#nvHeader");
  var menu = $("#nvMenu"), menuBtn = $("#nvMenuBtn"), nav = $(".nv-menu__nav", menu), marker = $("#nvMarker");
  var enq = $("#nvEnq"), enqBtn = $("#nvEnqBtn"), enqPanel = $("#nvEnqPanel"), enqClose = $("#nvEnqClose");
  var cats = $$(".nv-cat", menu);
  var dests = $$(".nv-dest", menu);

  var narrow = window.matchMedia("(max-width:900px)");
  var hover = window.matchMedia("(hover:hover) and (pointer:fine)");
  var still = window.matchMedia("(prefers-reduced-motion:reduce)");

  /* ----------------------------------------------------------
     Which page the prototype is standing in for (?page=slug),
     so the "you are here" state and the menu's opening category
     can be judged. Production knows this at build time.
     ---------------------------------------------------------- */
  var slug = (new URLSearchParams(location.search).get("page") || "sports").replace(/[^a-z-]/g, "");
  var initial = 0;
  cats.forEach(function (cat, i) {
    var link = $('a[data-slug="' + slug + '"]', dests[i]);
    if (link) { link.setAttribute("aria-current", "page"); initial = i; }
  });
  if (slug === "index") $("#nvHome").hidden = true;
  if (slug === "news") $("#nvNews").setAttribute("aria-current", "page");
  $$(".nv-demo__viewing a").forEach(function (a) {
    if (a.search === "?page=" + slug) a.setAttribute("aria-current", "true");
  });

  /* ----------------------------------------------------------
     Menu: categories, destinations and the marker.
     ---------------------------------------------------------- */
  var active = -1, hoverTimer = null, closeTimer = null, inerted = [], savedY = 0;

  // The marker sits beside the first line of the open category's label.
  function placeMarker(instant) {
    if (!marker || narrow.matches || active < 0) { if (marker) marker.classList.remove("is-set"); return; }
    var word = $(".nv-cat__word", cats[active]);
    var navBox = nav.getBoundingClientRect(), wordBox = word.getBoundingClientRect();
    var size = parseFloat(getComputedStyle(word).fontSize);
    var lead = (parseFloat(getComputedStyle(word).lineHeight) - size) / 2;
    var y = wordBox.top - navBox.top + lead + size * 0.16;
    if (instant) marker.style.transition = "none";
    marker.style.transform = "translateY(" + y.toFixed(1) + "px)";
    marker.classList.add("is-set");
    if (instant) { void marker.offsetWidth; marker.style.transition = ""; }
  }

  function select(index, opts) {
    opts = opts || {};
    if (index === active && !opts.force) return;
    active = index;
    cats.forEach(function (cat, i) {
      var on = i === index;
      cat.setAttribute("aria-expanded", String(on));
      dests[i].hidden = !on;
      // Only the incoming list animates; the outgoing one is gone at once,
      // so a fast pass across the categories never leaves two lists up.
      dests[i].classList.remove("is-entering");
      if (on && !opts.quiet && !still.matches) { void dests[i].offsetWidth; dests[i].classList.add("is-entering"); }
    });
    placeMarker(opts.instant);
  }

  cats.forEach(function (cat, i) {
    var wasOpen = false;
    cat.addEventListener("pointerdown", function () { wasOpen = i === active; });
    cat.addEventListener("click", function (e) {
      // On one column a category is an accordion and a second press closes
      // it. Beside the destinations it only ever opens.
      var collapse = narrow.matches && (e.detail === 0 ? i === active : wasOpen);
      select(collapse ? -1 : i);
      wasOpen = false;
    });
    cat.addEventListener("focus", function () { if (!narrow.matches) select(i); });
    cat.addEventListener("mouseenter", function () {
      if (narrow.matches || !hover.matches) return;
      // A reader who has tabbed into a destination list is not dragged out
      // of it by a pointer passing over another category.
      if (dests[active] && dests[active].contains(document.activeElement)) return;
      window.clearTimeout(hoverTimer);
      hoverTimer = window.setTimeout(function () {
        if (menu.classList.contains("is-open") && cat.matches(":hover")) select(i);
      }, 90);
    });
    cat.addEventListener("mouseleave", function () { window.clearTimeout(hoverTimer); });
    cat.addEventListener("keydown", function (e) {
      var next;
      if (e.key === "ArrowDown") next = (i + 1) % cats.length;
      else if (e.key === "ArrowUp") next = (i + cats.length - 1) % cats.length;
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = cats.length - 1;
      else if (e.key === "ArrowRight" && !narrow.matches) {
        var first = $("a", dests[active]);
        if (first) { e.preventDefault(); first.focus(); }
        return;
      } else return;
      e.preventDefault();
      cats[next].focus();
    });
  });
  // From a destination, Left returns to its category.
  dests.forEach(function (panel, i) {
    panel.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft" && !narrow.matches) { e.preventDefault(); cats[i].focus(); return; }
      var links = $$("a", panel), k = links.indexOf(document.activeElement);
      if (k === -1) return;
      if (e.key === "ArrowDown") { e.preventDefault(); links[(k + 1) % links.length].focus(); }
      if (e.key === "ArrowUp") { e.preventDefault(); links[(k + links.length - 1) % links.length].focus(); }
    });
  });

  function isolate(on) {
    if (on) {
      inerted = Array.prototype.slice.call(body.children).filter(function (el) {
        return el !== header && el !== menu && !el.inert && el.tagName !== "SCRIPT";
      });
      inerted.forEach(function (el) { el.inert = true; });
    } else {
      inerted.forEach(function (el) { el.inert = false; });
      inerted = [];
    }
  }

  function openMenu() {
    setEnquire(false);
    window.clearTimeout(closeTimer);
    savedY = window.scrollY;
    menu.hidden = false;
    menu.scrollTop = 0;
    active = -1;
    select(initial, { quiet: true, instant: true });
    void menu.offsetWidth;
    menu.classList.add("is-open");
    menuBtn.setAttribute("aria-expanded", "true");
    menuBtn.setAttribute("aria-label", "Close menu");
    root.classList.add("nv-menu-open");
    isolate(true);
    cats[initial].focus({ preventScroll: true });
  }
  function closeMenu(returnFocus) {
    if (!menu.classList.contains("is-open")) return;
    menu.classList.remove("is-open");
    menuBtn.setAttribute("aria-expanded", "false");
    menuBtn.setAttribute("aria-label", "Open menu");
    root.classList.remove("nv-menu-open");
    isolate(false);
    // The page behind was never scrolled; this only guards against a
    // browser that resets it when overflow is restored.
    if (window.scrollY !== savedY) window.scrollTo({ top: savedY, behavior: "instant" });
    if (returnFocus) menuBtn.focus({ preventScroll: true });
    closeTimer = window.setTimeout(function () {
      if (!menu.classList.contains("is-open")) menu.hidden = true;
    }, still.matches ? 0 : 280);
  }
  menuBtn.setAttribute("aria-label", "Open menu");
  menuBtn.addEventListener("click", function () {
    if (menu.classList.contains("is-open")) closeMenu(false); else openMenu();
  });
  $$("a", menu).forEach(function (a) { a.addEventListener("click", function () { closeMenu(false); }); });

  // The marker follows its category when the window changes size.
  window.addEventListener("resize", function () {
    if (menu.classList.contains("is-open")) {
      if (!narrow.matches && active === -1) select(initial, { quiet: true });
      placeMarker(true);
    }
  });

  // Tab circles through the header and the menu while it is open.
  document.addEventListener("keydown", function (e) {
    if (!menu.classList.contains("is-open")) return;
    if (e.key === "Escape") {
      if (enqOpen) return;       // Escape closes the innermost thing first
      e.preventDefault(); closeMenu(true); return;
    }
    if (e.key !== "Tab") return;
    var items = $$("a[href], button", header).concat($$("a[href], button", menu)).filter(function (el) {
      return !el.disabled && !el.hidden && el.tabIndex >= 0 && el.getClientRects().length &&
             !el.closest("[hidden]") && !(enqPanel.contains(el) && !enqOpen);
    });
    var k = items.indexOf(document.activeElement);
    if (k === -1 || (e.shiftKey && k === 0) || (!e.shiftKey && k === items.length - 1)) {
      e.preventDefault();
      items[e.shiftKey ? items.length - 1 : 0].focus();
    }
  });

  /* ----------------------------------------------------------
     Enquire: hover, click, keyboard focus, its own Close, Escape.
     ---------------------------------------------------------- */
  var enqOpen = false, enqTimer = null, returning = false;
  enqPanel.hidden = false;           // the sheet is hidden by visibility, not removed

  function setEnquire(next, returnFocus) {
    if (next === enqOpen) return;
    enqOpen = next;
    enq.classList.toggle("is-open", enqOpen);
    enqBtn.setAttribute("aria-expanded", String(enqOpen));
    // Focus goes back to the tab without the tab's own keyboard-focus
    // rule reopening the sheet that was just closed.
    if (!enqOpen && returnFocus) { returning = true; enqBtn.focus(); returning = false; }
  }

  enq.addEventListener("mouseenter", function () {
    if (!hover.matches || menu.classList.contains("is-open")) return;
    window.clearTimeout(enqTimer);
    enqTimer = window.setTimeout(function () { setEnquire(true); }, 70);
  });
  enq.addEventListener("mouseleave", function () {
    if (!hover.matches) return;
    window.clearTimeout(enqTimer);
    // A grace period: the pointer may clip a corner on its way in.
    enqTimer = window.setTimeout(function () { setEnquire(false); }, 220);
  });
  enqBtn.addEventListener("click", function () {
    window.clearTimeout(enqTimer);
    if (menu.classList.contains("is-open")) closeMenu(false);
    // With a mouse, arriving on the tab has already opened the sheet, so a
    // click only ever opens; leaving or Close is what shuts it. Touch toggles.
    setEnquire(hover.matches ? true : !enqOpen);
  });
  enqClose.addEventListener("click", function () {
    window.clearTimeout(enqTimer);
    setEnquire(false, true);
  });
  enq.addEventListener("focusin", function (e) {
    if (returning) return;
    try { if (e.target.matches(":focus-visible") && !menu.classList.contains("is-open")) setEnquire(true); }
    catch (err) { /* older browser */ }
  });
  enq.addEventListener("focusout", function (e) {
    if (!enq.contains(e.relatedTarget)) setEnquire(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && enqOpen) { e.preventDefault(); setEnquire(false, true); }
  });
  document.addEventListener("click", function (e) {
    if (enqOpen && !enq.contains(e.target)) setEnquire(false);
  });
})();
