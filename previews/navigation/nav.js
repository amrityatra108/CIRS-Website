/* Navigation prototype — header, full-screen menu, Enquire.
   Carries over what production's cirs.js already does for each control
   (hover intent, keyboard focus opening Enquire, Escape, the Tab loop,
   the header sliding away past the opening) and adds the menu's
   choreography. Self-contained: no GSAP, no Lenis. */
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var body = document.body;
  var header = $("#nvHeader");
  var menu = $("#nvMenu"), menuBtn = $("#nvMenuBtn");
  var enq = $("#nvEnq"), enqBtn = $("#nvEnqBtn"), enqPanel = $("#nvEnqPanel");
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
     Header: holds, and the slide away past the opening.
     ---------------------------------------------------------- */
  var holds = { menu: false, enquire: false, focus: false, pointer: false };
  var lastY = window.scrollY, away = false;

  function held() { return holds.menu || holds.enquire || holds.focus || holds.pointer; }
  function setAway(next) {
    if (next && held()) next = false;
    if (next === away) return;
    away = next;
    header.classList.toggle("is-away", away);
  }
  function hold(name, on) { holds[name] = on; if (on) setAway(false); }

  window.addEventListener("scroll", function () {
    var y = window.scrollY, dy = y - lastY;
    if (y < 160) setAway(false);
    else if (dy > 6) setAway(true);
    else if (dy < -6) setAway(false);
    if (Math.abs(dy) > 6 || y < 160) lastY = y;
  }, { passive: true });
  document.addEventListener("pointermove", function (e) {
    if (e.pointerType !== "mouse") return;
    var near = e.clientY < 28;
    if (near !== holds.pointer) hold("pointer", near);
  }, { passive: true });
  // Only keyboard focus holds the bar: a mouse click leaves focus on the
  // control it pressed, and that alone should not pin the header.
  header.addEventListener("focusin", function (e) {
    try { if (e.target.matches(":focus-visible")) hold("focus", true); } catch (err) { /* older browser */ }
  });
  header.addEventListener("focusout", function (e) {
    if (!header.contains(e.relatedTarget)) hold("focus", false);
  });

  /* ----------------------------------------------------------
     Menu: categories and their destinations.
     ---------------------------------------------------------- */
  var active = -1, hoverTimer = null, closeTimer = null, inerted = [];

  function reveal(panel, delay) {
    if (still.matches) return;
    panel.classList.remove("is-entering");
    panel.style.setProperty("--d0", (delay || 0) + "ms");
    void panel.offsetWidth;          // restart the animation on this panel
    panel.classList.add("is-entering");
  }

  function select(index, delay) {
    if (index === active) return;
    active = index;
    cats.forEach(function (cat, i) {
      var on = i === index;
      cat.setAttribute("aria-expanded", String(on));
      dests[i].hidden = !on;
      if (on) reveal(dests[i], delay);
    });
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
      if (e.key === "ArrowLeft" && !narrow.matches) { e.preventDefault(); cats[i].focus(); }
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
    active = -1;
    menu.hidden = false;
    select(initial, 300);
    void menu.offsetWidth;
    menu.classList.add("is-open");
    menuBtn.setAttribute("aria-expanded", "true");
    menuBtn.setAttribute("aria-label", "Close menu");
    body.classList.add("nv-menu-open");
    hold("menu", true);
    isolate(true);
    window.setTimeout(function () {
      if (menu.classList.contains("is-open")) cats[initial].focus({ preventScroll: true });
    }, still.matches ? 0 : 160);
  }
  function closeMenu(returnFocus) {
    if (!menu.classList.contains("is-open")) return;
    menu.classList.remove("is-open");
    menuBtn.setAttribute("aria-expanded", "false");
    menuBtn.setAttribute("aria-label", "Open menu");
    body.classList.remove("nv-menu-open");
    hold("menu", false);
    isolate(false);
    if (returnFocus) menuBtn.focus({ preventScroll: true });
    closeTimer = window.setTimeout(function () {
      if (!menu.classList.contains("is-open")) menu.hidden = true;
    }, still.matches ? 160 : 360);
  }
  menuBtn.setAttribute("aria-label", "Open menu");
  menuBtn.addEventListener("click", function () {
    if (menu.classList.contains("is-open")) closeMenu(false); else openMenu();
  });
  $$("a", menu).forEach(function (a) { a.addEventListener("click", function () { closeMenu(false); }); });

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
             !(enqPanel.contains(el) && !enqOpen);
    });
    var k = items.indexOf(document.activeElement);
    if (k === -1 || (e.shiftKey && k === 0) || (!e.shiftKey && k === items.length - 1)) {
      e.preventDefault();
      items[e.shiftKey ? items.length - 1 : 0].focus();
    }
  });

  // Switching between one column and two while the menu is open: one
  // column may have left every category closed; two always shows one.
  narrow.addEventListener("change", function () {
    if (!narrow.matches && active === -1) select(initial);
  });

  /* ----------------------------------------------------------
     Enquire: hover, click, keyboard focus, Escape.
     ---------------------------------------------------------- */
  var enqOpen = false, enqTimer = null;
  enqPanel.hidden = false;           // the sheet is clipped shut, not removed

  function setEnquire(next) {
    if (next === enqOpen) return;
    enqOpen = next;
    enq.classList.toggle("is-open", enqOpen);
    enqBtn.setAttribute("aria-expanded", String(enqOpen));
    hold("enquire", enqOpen);
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
    // click only ever opens; leaving is what closes it. Touch toggles.
    setEnquire(hover.matches ? true : !enqOpen);
  });
  enq.addEventListener("focusin", function (e) {
    try { if (e.target.matches(":focus-visible") && !menu.classList.contains("is-open")) setEnquire(true); }
    catch (err) { /* older browser */ }
  });
  enq.addEventListener("focusout", function (e) {
    if (!enq.contains(e.relatedTarget)) setEnquire(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && enqOpen) { e.preventDefault(); setEnquire(false); enqBtn.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (enqOpen && !enq.contains(e.target)) setEnquire(false);
  });
})();
