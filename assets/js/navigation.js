/*
 * Shared CIRS menu and Enquire controller.
 * Kept independent of the animation and smooth-scroll bundles so the site
 * navigation can work while those optional resources are still loading.
 */
(function () {
  "use strict";
  if (window.CIRSNavigation) return;

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var drawer = $("#drawer"), burger = $("#burger"), header = $("#header");
  var drawerCloseTimer = null, drawerInerted = [], isolationObserver = null, lockBeforeMenu = false;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var setEnquire = function () {};
  var enquireOpen = function () { return false; };

  function scrollLock(locked) {
    window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: locked } }));
  }

  function isolateDrawer(open) {
    if (open) {
      function isolate(el) {
        if (!el || el.nodeType !== 1 || el === drawer || el === header || el.inert || el.tagName === "SCRIPT") return;
        el.inert = true;
        drawerInerted.push(el);
      }
      drawerInerted = [];
      Array.prototype.forEach.call(document.body.children, isolate);
      // When navigation starts before a long page has finished parsing, the
      // footer and deferred script tags can still be appended to <body> while
      // the drawer is open. Keep those later siblings behind the same inert
      // boundary; the observer exists only for the lifetime of this opening.
      isolationObserver = new MutationObserver(function (records) {
        records.forEach(function (record) {
          Array.prototype.forEach.call(record.addedNodes, isolate);
        });
      });
      isolationObserver.observe(document.body, { childList: true });
    } else {
      if (isolationObserver) { isolationObserver.disconnect(); isolationObserver = null; }
      drawerInerted.forEach(function (el) { el.inert = false; });
      drawerInerted = [];
    }
  }

  function closeDrawer() {
    if (!drawer || !drawer.classList.contains("is-open")) return;
    drawer.classList.remove("is-open");
    document.body.classList.add("menu-closing");
    document.body.classList.remove("menu-open");
    // Preserve a page intro's lock that existed before the menu was opened.
    if (!lockBeforeMenu) document.body.classList.remove("is-locked");
    lockBeforeMenu = false;
    scrollLock(false);
    isolateDrawer(false);
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-label", "Open menu");
    burger.focus({ preventScroll: true });
    window.clearTimeout(drawerCloseTimer);
    drawerCloseTimer = window.setTimeout(function () {
      if (!drawer.classList.contains("is-open")) drawer.hidden = true;
      document.body.classList.remove("menu-closing");
    }, reduced ? 0 : 280);
  }

  function initEnquire() {
    var wrap = $("#enq"), btn = $("#enqBtn"), panel = $("#enqPanel"), close = $("#enqClose");
    if (!wrap || !btn || !panel) return;

    var open = false, timer = null, returning = false;
    var fine = window.matchMedia("(hover:hover) and (pointer:fine)");
    var menuOpen = function () { return drawer && drawer.classList.contains("is-open"); };
    panel.hidden = false;

    function set(next, returnFocus) {
      if (next === open) return;
      open = next;
      wrap.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      if (!open && returnFocus) { returning = true; btn.focus(); returning = false; }
    }
    setEnquire = set;
    enquireOpen = function () { return open; };

    wrap.addEventListener("mouseenter", function () {
      if (!fine.matches || menuOpen()) return;
      window.clearTimeout(timer);
      timer = window.setTimeout(function () { set(true); }, 70);
    });
    wrap.addEventListener("mouseleave", function () {
      if (!fine.matches) return;
      window.clearTimeout(timer);
      timer = window.setTimeout(function () { set(false); }, 220);
    });
    btn.addEventListener("click", function (event) {
      event.preventDefault();
      window.clearTimeout(timer);
      if (menuOpen()) closeDrawer();
      set(fine.matches ? true : !open);
    });
    if (close) close.addEventListener("click", function () {
      window.clearTimeout(timer);
      set(false, true);
    });
    wrap.addEventListener("focusin", function (event) {
      if (returning || menuOpen()) return;
      try { if (event.target && event.target.matches(":focus-visible")) set(true); }
      catch (err) { /* Older browser without :focus-visible selector support. */ }
    });
    wrap.addEventListener("focusout", function (event) {
      if (!wrap.contains(event.relatedTarget)) set(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && open) {
        event.preventDefault();
        event.stopImmediatePropagation();
        set(false, true);
      }
    });
    document.addEventListener("click", function (event) {
      if (open && !wrap.contains(event.target)) set(false);
    });
  }

  function initDrawer() {
    if (!drawer || !burger || !header) return;
    var nav = $(".nv-menu__nav", drawer), marker = $(".nv-marker", drawer);
    var cats = $$(".nv-cat", drawer), dests = $$(".nv-dest", drawer);
    if (!cats.length || cats.length !== dests.length) return;
    var initial = Math.max(0, Math.min(cats.length - 1, Number(drawer.dataset.initialGroup) || 0));
    var active = -1, hoverTimer = null;
    var narrow = window.matchMedia("(max-width:900px)");
    var fine = window.matchMedia("(hover:hover) and (pointer:fine)");

    function placeMarker(instant) {
      if (!marker) return;
      if (narrow.matches || active < 0) { marker.classList.remove("is-set"); return; }
      var word = $(".nv-cat__word", cats[active]);
      var cs = getComputedStyle(word), size = parseFloat(cs.fontSize);
      var lead = (parseFloat(cs.lineHeight) - size) / 2;
      var y = word.getBoundingClientRect().top - nav.getBoundingClientRect().top + lead + size * .16;
      if (instant) marker.style.transition = "none";
      marker.style.transform = "translateY(" + y.toFixed(1) + "px)";
      marker.classList.add("is-set");
      if (instant) { void marker.offsetWidth; marker.style.transition = ""; }
    }

    function select(index, options) {
      options = options || {};
      if (index === active && !options.force) return;
      active = index;
      cats.forEach(function (cat, i) {
        var on = i === index;
        cat.setAttribute("aria-expanded", String(on));
        dests[i].hidden = !on;
        dests[i].classList.remove("is-entering");
        if (on && !options.quiet && !reduced) { void dests[i].offsetWidth; dests[i].classList.add("is-entering"); }
      });
      placeMarker(options.instant);
    }
    select(initial, { quiet: true, instant: true });

    cats.forEach(function (cat, i) {
      var wasOpen = false;
      cat.addEventListener("pointerdown", function () { wasOpen = i === active; });
      cat.addEventListener("click", function (event) {
        var collapse = narrow.matches && (event.detail === 0 ? i === active : wasOpen);
        select(collapse ? -1 : i);
        wasOpen = false;
      });
      cat.addEventListener("focus", function () { if (!narrow.matches) select(i); });
      cat.addEventListener("mouseenter", function () {
        if (narrow.matches || !fine.matches) return;
        if (dests[active] && dests[active].contains(document.activeElement)) return;
        window.clearTimeout(hoverTimer);
        hoverTimer = window.setTimeout(function () {
          if (drawer.classList.contains("is-open") && cat.matches(":hover")) select(i);
        }, 90);
      });
      cat.addEventListener("mouseleave", function () { window.clearTimeout(hoverTimer); });
      cat.addEventListener("keydown", function (event) {
        var next;
        if (event.key === "ArrowDown") next = (i + 1) % cats.length;
        else if (event.key === "ArrowUp") next = (i + cats.length - 1) % cats.length;
        else if (event.key === "Home") next = 0;
        else if (event.key === "End") next = cats.length - 1;
        else if (event.key === "ArrowRight" && !narrow.matches) {
          var first = $("a", dests[active]);
          if (first) { event.preventDefault(); first.focus(); }
          return;
        } else return;
        event.preventDefault();
        cats[next].focus();
      });
    });
    dests.forEach(function (dest, i) {
      dest.addEventListener("keydown", function (event) {
        if (event.key === "ArrowLeft" && !narrow.matches) { event.preventDefault(); cats[i].focus(); return; }
        var links = $$("a", dest), k = links.indexOf(document.activeElement);
        if (k === -1) return;
        if (event.key === "ArrowDown") { event.preventDefault(); links[(k + 1) % links.length].focus(); }
        if (event.key === "ArrowUp") { event.preventDefault(); links[(k + links.length - 1) % links.length].focus(); }
      });
    });

    function openDrawer() {
      setEnquire(false);
      window.clearTimeout(drawerCloseTimer);
      document.body.classList.remove("menu-closing");
      lockBeforeMenu = document.body.classList.contains("is-locked");
      drawer.hidden = false;
      drawer.scrollTop = 0;
      active = -1;
      select(initial, { quiet: true, instant: true });
      void drawer.offsetWidth;
      drawer.classList.add("is-open");
      burger.setAttribute("aria-expanded", "true");
      burger.setAttribute("aria-label", "Close menu");
      document.body.classList.add("is-locked", "menu-open");
      scrollLock(true);
      isolateDrawer(true);
      cats[initial].focus({ preventScroll: true });
    }
    burger.addEventListener("click", function () {
      if (drawer.classList.contains("is-open")) closeDrawer(); else openDrawer();
    });
    $$("a", drawer).forEach(function (link) { link.addEventListener("click", closeDrawer); });
    window.addEventListener("resize", function () {
      if (!drawer.classList.contains("is-open")) return;
      if (!narrow.matches && active === -1) select(initial, { quiet: true });
      placeMarker(true);
    }, { passive: true });
    document.addEventListener("keydown", function (event) {
      if (!drawer.classList.contains("is-open")) return;
      if (event.key === "Escape") {
        if (enquireOpen()) return;
        event.preventDefault(); closeDrawer(); return;
      }
      if (event.key !== "Tab") return;
      var panel = $("#enqPanel");
      var items = $$("a[href], button", header).concat($$("a[href], button", drawer)).filter(function (el) {
        return !el.disabled && el.tabIndex >= 0 && el.getClientRects().length && !el.closest("[hidden]") &&
          !(panel && panel.contains(el) && !enquireOpen());
      });
      if (!items.length) return;
      var k = items.indexOf(document.activeElement);
      if (k === -1 || (event.shiftKey && k === 0) || (!event.shiftKey && k === items.length - 1)) {
        event.preventDefault();
        items[event.shiftKey ? items.length - 1 : 0].focus();
      }
    });
    return { open: openDrawer, close: closeDrawer };
  }


  // The established header and footer fit logic is shared with standalone pages.
  // Optional page animation code attaches its refresh sentinel to this owner.
  var headerController = null, headerRefreshTrigger = null, footerFitted = false;
  function headerState() {
    var header = $("#header");
    if (!header) return;
    // Over a full-screen opening the controls sit clear on the picture; the
    // first real scroll gathers them into the floating pill, and they come
    // back out only near the very top. Two thresholds, so a reader resting
    // on the boundary does not make the header flicker between the two.
    var PILL_IN = 56, PILL_OUT = 16;

    var main = header.dataset.headerMain ? $(header.dataset.headerMain) : $("#main");
    var barBottom = 0, zones = [], scrolled = null, queued = false;
    // Read live: a page can open a view with no full-screen picture above an
    // opening that has one (the Creative Writing reader), and ask for the pill.
    function contentFirst() { return header.dataset.headerStart === "content"; }
    var heroBoundary = header.dataset.headerHero ? $(header.dataset.headerHero) : null;
    var heroEnd = null;

    function darkGround(node) {
      var declared = node.getAttribute("data-header-theme");
      if (declared) return declared === "dark";
      var raw = node.getAttribute("data-ground") || getComputedStyle(node).backgroundColor;
      var hex = raw.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
      var rgb = raw.match(/^rgba?\(([^)]+)\)/i);
      var channels;
      if (hex) {
        var value = hex[1].length === 3 ? hex[1].split("").map(function (c) { return c + c; }).join("") : hex[1];
        channels = [0, 2, 4].map(function (i) { return parseInt(value.slice(i, i + 2), 16); });
      } else if (rgb) {
        channels = rgb[1].split(",").map(Number);
        if (channels.length > 3 && channels[3] === 0) return null;
      } else return null;
      return channels[0] * .2126 + channels[1] * .7152 + channels[2] * .0722 < 145;
    }

    // Measured, not read every frame: it moves only when the layout does.
    function measure() {
      var bar = header.querySelector(".nv-header__bar") || header;
      barBottom = bar.getBoundingClientRect().bottom;
      if (heroBoundary) {
        var heroBox = heroBoundary.getBoundingClientRect();
        heroEnd = heroBox.bottom + (window.scrollY || window.pageYOffset || 0);
      }
      var nodes = main ? Array.prototype.slice.call(main.querySelectorAll(":scope > section, :scope > article, :scope > header, [data-ground], [data-header-theme]")) : [];
      var footer = header.dataset.headerFooter ? $(header.dataset.headerFooter) : $(".footer");
      if (footer) nodes.push(footer);
      zones = nodes.map(function (node) {
        var dark = darkGround(node);
        if (dark === null) return null;
        var box = node.parentElement && node.parentElement.classList.contains("pin-spacer") ? node.parentElement : node;
        var rect = box.getBoundingClientRect();
        var y = window.scrollY || window.pageYOffset || 0;
        // The sticky footer sits behind the main page while scrolling. Its
        // viewport rect is not where the footer enters the document flow.
        // Measure it after the preceding content so it cannot tint the bar
        // over a light section several screens earlier.
        if (node === footer && footer.parentElement &&
            getComputedStyle(footer.parentElement).position === "sticky" &&
            footer.parentElement.previousElementSibling) {
          var before = footer.parentElement.previousElementSibling;
          var top = before.getBoundingClientRect().bottom + y;
          return { top: top, bottom: top + footer.parentElement.offsetHeight, dark: dark };
        }
        return { top: rect.top + y, bottom: rect.bottom + y, dark: dark };
      }).filter(Boolean);
    }

    function apply() {
      queued = false;
      var y = window.scrollY || window.pageYOffset || 0;
      var pillIn = heroEnd === null ? PILL_IN : Math.max(PILL_IN, heroEnd - barBottom);
      var pillOut = heroEnd === null ? PILL_OUT : Math.max(PILL_OUT, pillIn - 24);
      var next = contentFirst() || (scrolled ? y > pillOut : y > pillIn);
      var at = y + barBottom;
      var dark = false;
      zones.forEach(function (zone) { if (at >= zone.top && at < zone.bottom) dark = zone.dark; });
      header.dataset.headerSurface = dark ? "dark" : "light";
      if (next === scrolled) return;
      scrolled = next;
      header.classList.toggle("is-scrolled", next);
      header.dataset.headerMode = next ? "content" : "hero";
    }
    function queue() {
      if (queued) return;
      queued = true;
      requestAnimationFrame(apply);
    }
    function remeasure() { measure(); queue(); }

    // The state the page opens in is set without a transition, so a page
    // refreshed halfway down (or restored there by the browser) shows the
    // structured header at once rather than watching the clear one become it.
    // is-settling holds until the load event has let the browser restore
    // the scroll position, then two frames more so the settled state has
    // painted before transitions come back.
    header.classList.add("is-settling");
    measure();
    apply();
    function settle() {
      remeasure();
      requestAnimationFrame(function () {
        apply();
        requestAnimationFrame(function () { header.classList.remove("is-settling"); });
      });
    }
    if (document.readyState === "complete") settle();
    else window.addEventListener("load", settle, { once: true });

    // One reader of the scroll position. Lenis moves the window itself, so
    // the native event fires whether or not smooth scrolling is on.
    window.addEventListener("scroll", queue, { passive: true });
    window.addEventListener("resize", remeasure, { passive: true });
    window.addEventListener("pageshow", remeasure);
    // A page that changes its view in place (the Creative Writing reader)
    // asks for a fresh reading here. A synthetic resize would do it too, but
    // would also make ScrollTrigger refresh and put back a stale position.
    window.addEventListener("cirs-header-refresh", remeasure);
    // A trigger rather than ScrollTrigger.addEventListener("refresh"). With
    // only the listener, a page reloaded halfway down came back near the top:
    // on pages that create no trigger of their own at boot, the browser's
    // scroll restoration does not survive ScrollTrigger's first refresh. The
    // header's old sentinels created one by accident; this does it on purpose.

    if ("ResizeObserver" in window) new ResizeObserver(remeasure).observe(document.body);
    return { refresh: remeasure };
  }

  function initHeaderState(scrollTrigger) {
    if (!headerController) headerController = headerState();
    if (headerController && scrollTrigger && !headerRefreshTrigger) {
      headerRefreshTrigger = scrollTrigger.create({ onRefresh: headerController.refresh });
    }
    return headerController;
  }
  function fitFooter() {
    if (footerFitted) return;
    var wrap = $(".footer-wrap");
    if (!wrap) return;
    footerFitted = true;
    function fit() { wrap.classList.toggle("is-tall", wrap.offsetHeight > window.innerHeight); }
    fit();
    window.addEventListener("resize", fit, { passive: true });
    if ("ResizeObserver" in window) new ResizeObserver(fit).observe(wrap);
  }

  var drawerController = initDrawer();
  initEnquire();
  window.CIRSNavigation = {
    closeDrawer: closeDrawer,
    openDrawer: drawerController && drawerController.open,
    isOpen: function () { return !!(drawer && drawer.classList.contains("is-open")); },
    isEnquireOpen: enquireOpen,
    initHeaderState: initHeaderState,
    fitFooter: fitFooter
  };
  function initChrome() { initHeaderState(); fitFooter(); }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initChrome, { once: true });
  } else initChrome();
}());
