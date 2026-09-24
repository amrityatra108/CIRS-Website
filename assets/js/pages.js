/* ============================================================
   Page-level behaviour
   ------------------------------------------------------------
   assets/js/cirs.js is the design system's interaction layer and
   comes out of the Claude artifact — a single-page design. This
   file is the repository's own, for behaviour only a multi-page
   site needs. Keep it small, and keep it working without GSAP or
   Lenis, which are loaded from a CDN and may not arrive.
   ============================================================ */
(function () {
  "use strict";

  /* ----------------------------------------------------------
     "On this page" — the index above the back-to-top button.
     It is a native <details>, so it opens, closes and takes the
     keyboard with this file blocked. What this adds is the rest:
     Escape and a click elsewhere close it, choosing a link closes
     it, and the section on screen is marked in the list.
     ---------------------------------------------------------- */
  var jump = document.querySelector(".jump");
  if (!jump) return;

  var details = jump.querySelector(".jump__details");
  var toggle = jump.querySelector(".jump__toggle");
  var panel = jump.querySelector(".jump__panel");
  if (!details || !toggle || !panel) return;

  panel.addEventListener("click", function (e) {
    if (e.target.closest("a")) details.open = false;
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && details.open) {
      details.open = false;
      toggle.focus();
    }
  });

  document.addEventListener("click", function (e) {
    if (details.open && !jump.contains(e.target)) details.open = false;
  });

  /* Mark the section currently on screen. Uses IntersectionObserver
     where it exists and does nothing where it does not, rather than
     falling back to a scroll handler nobody needs. */
  if (!("IntersectionObserver" in window)) return;

  var links = Array.prototype.slice.call(panel.querySelectorAll('a[href^="#"]'));
  var byId = {};
  var targets = [];
  links.forEach(function (a) {
    var el = document.getElementById(a.getAttribute("href").slice(1));
    if (el) { byId[el.id] = a; targets.push(el); }
  });
  if (!targets.length) return;

  var seen = {};
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) { seen[entry.target.id] = entry.isIntersecting; });
    var current = null;
    targets.forEach(function (el) { if (seen[el.id] && !current) current = el.id; });
    links.forEach(function (a) { a.removeAttribute("aria-current"); });
    if (current && byId[current]) byId[current].setAttribute("aria-current", "true");
  }, { rootMargin: "-45% 0px -45% 0px" });

  targets.forEach(function (el) { io.observe(el); });
})();

/* ============================================================
   Admissions contact panel
   ------------------------------------------------------------
   Shown as the page opens, because the one thing a family most
   often wants from an admissions page is a person to ask. Closed
   once, it stays closed for the rest of the browsing session:
   arriving is a good moment to offer it, returning from another
   page is not.
   ============================================================ */
(function () {
  "use strict";

  var pop = document.getElementById("admissionsPop");
  if (!pop) return;

  var closeBtn = document.getElementById("popClose");
  var KEY = "cirs.admissionsPop.dismissed";
  var lastFocus = null;

  function dismissed() {
    try { return sessionStorage.getItem(KEY) === "1"; } catch (e) { return false; }
  }
  function remember() {
    try { sessionStorage.setItem(KEY, "1"); } catch (e) { /* private mode: just don't remember */ }
  }

  function close() {
    pop.classList.remove("is-open");
    document.body.classList.remove("is-locked");
    remember();
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function open() {
    lastFocus = document.activeElement;
    pop.classList.add("is-open");
    document.body.classList.add("is-locked");
    if (closeBtn) closeBtn.focus();
  }

  if (closeBtn) closeBtn.addEventListener("click", close);

  // Clicking the darkened area outside the card closes it too.
  pop.addEventListener("click", function (e) {
    if (e.target === pop) close();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && pop.classList.contains("is-open")) close();
  });

  // Keep the tab ring inside the card while it is open.
  pop.addEventListener("keydown", function (e) {
    if (e.key !== "Tab" || !pop.classList.contains("is-open")) return;
    var focusable = pop.querySelectorAll("button, a[href]");
    if (!focusable.length) return;
    var first = focusable[0], last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  if (!dismissed()) {
    // A beat after the page settles, so it reads as an offer rather than
    // an interruption of something still loading.
    setTimeout(open, 900);
  }
})();

/* ============================================================
   Detail panels — About CIRS
   ------------------------------------------------------------
   Every "Know more" on the About page opens one of these. The
   page itself carries a photograph and a line; the prose that
   used to sit under it lives in the panel.

   Same manners as the admissions popup below: Escape closes,
   clicking the darkened area closes, the tab ring stays inside
   while it is open, and focus returns to the button that opened
   it. The panels are hidden until a pointer or key asks for one,
   so a reader who never opens one is never told about them.
   ============================================================ */
(function () {
  "use strict";

  var openers = document.querySelectorAll("[data-panel]");
  if (!openers.length) return;

  var current = null, lastFocus = null;

  function close() {
    if (!current) return;
    current.classList.remove("is-open");
    var closing = current;
    current = null;
    document.body.classList.remove("is-locked");
    // hidden only after the fade, or it vanishes rather than closes
    setTimeout(function () {
      if (!closing.classList.contains("is-open")) closing.hidden = true;
    }, 360);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function open(panel, opener) {
    if (current) close();
    lastFocus = opener;
    panel.hidden = false;
    current = panel;
    document.body.classList.add("is-locked");
    // Two frames: one with the element laid out so the transition has somewhere
    // to run from, then focus — and only after .is-open, because until then the
    // panel is visibility:hidden and nothing inside it can take focus. Focusing
    // too early leaves the ring on the button outside, and Tab walks the page
    // behind the panel instead of its contents.
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        panel.classList.add("is-open");
        // Reading a layout property flushes the style change. Without it the
        // element's used visibility is still hidden in this task and focus()
        // is silently refused, leaving the ring on the button outside.
        void panel.offsetHeight;
        var first = panel.querySelector("[data-panel-close]");
        if (first) first.focus();
      });
    });
  }

  Array.prototype.forEach.call(openers, function (btn) {
    var panel = document.getElementById(btn.getAttribute("data-panel"));
    if (!panel) return;
    btn.addEventListener("click", function () { open(panel, btn); });
  });

  document.addEventListener("click", function (e) {
    if (e.target.closest && e.target.closest("[data-panel-close]")) { close(); return; }
    if (current && e.target === current) close();          // the darkened area
  });

  document.addEventListener("keydown", function (e) {
    if (!current) return;
    if (e.key === "Escape") { e.preventDefault(); close(); return; }
    if (e.key !== "Tab") return;
    var focusable = current.querySelectorAll("button, a[href]");
    if (!focusable.length) return;
    var first = focusable[0], last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });
})();

/* ------------------------------------------------------------
   Leadership — the messages reader
   ------------------------------------------------------------
   The markup is every message in order, with the tab list hidden,
   so with this file blocked every message is still read. Here it
   becomes a tab list and one message at a time: a column of names
   from 900px, a strip of names that scrolls sideways below it.
   Arrow keys, Home and End move between tabs, as the ARIA tabs
   pattern expects.
   ------------------------------------------------------------ */
(function () {
  "use strict";
  var reader = document.querySelector("[data-msgs]");
  if (!reader) return;
  var list = reader.querySelector('[role="tablist"]');
  var tabs = Array.prototype.slice.call(reader.querySelectorAll('[role="tab"]'));
  var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute("aria-controls")); });
  if (!list || !tabs.length) return;

  function select(i, focus) {
    tabs.forEach(function (t, j) {
      var on = j === i;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      if (panels[j]) panels[j].hidden = !on;
    });
    if (focus) tabs[i].focus();
    // On the narrow strip, keep the chosen name in view.
    if (list.scrollWidth > list.clientWidth) {
      list.scrollTo({ left: tabs[i].offsetLeft - 20, behavior: "smooth" });
    }
  }

  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { select(i, false); });
    t.addEventListener("keydown", function (e) {
      var n = tabs.length, to = null;
      if (e.key === "ArrowDown" || e.key === "ArrowRight") to = (i + 1) % n;
      else if (e.key === "ArrowUp" || e.key === "ArrowLeft") to = (i - 1 + n) % n;
      else if (e.key === "Home") to = 0;
      else if (e.key === "End") to = n - 1;
      if (to === null) return;
      e.preventDefault();
      select(to, true);
    });
  });

  reader.classList.add("is-tabbed");
  list.hidden = false;
  select(0, false);

  // "Read the message from …" in a person's introduction panel. The panel
  // closes itself (the link carries data-panel-close); once it has, the
  // matching tab is chosen and the page travels to the messages — through
  // the shared smooth scroll when it is running, natively when it is not.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-msg-link]");
    if (!a) return;
    var i = -1;
    tabs.forEach(function (t, j) { if (t.id === "msg-tab-" + a.getAttribute("data-msg-link")) i = j; });
    if (i < 0) return;
    e.preventDefault();
    setTimeout(function () {
      select(i, false);
      var top = reader.getBoundingClientRect().top + window.pageYOffset - 120;
      var ev = new CustomEvent("cirs-section-scroll", { cancelable: true, detail: { top: top, duration: 1.1 } });
      if (window.dispatchEvent(ev)) window.scrollTo({ top: top, behavior: "smooth" });
      tabs[i].focus({ preventScroll: true });
    }, 380);
  });
})();

/* ------------------------------------------------------------
   Leadership — the people cards lean towards the pointer
   ------------------------------------------------------------
   Only with a fine pointer that can hover and with motion welcome;
   on touch the card simply lifts (pages.css). The lean is capped at
   six degrees, eased by the card's own transition as the pointer
   leaves, and written once per frame.
   ------------------------------------------------------------ */
(function () {
  "use strict";
  var cards = document.querySelectorAll("[data-tilt]");
  if (!cards.length) return;

  // The name's button stretches over the card, but the photograph and the
  // words sit forward of the card in 3D, and depth, not z-index, decides
  // what a click lands on there. So a click anywhere on the card is the
  // button's click.
  Array.prototype.forEach.call(cards, function (card) {
    var btn = card.querySelector("button");
    if (!btn) return;
    card.addEventListener("click", function (e) {
      if (e.target !== btn && !btn.contains(e.target)) btn.click();
    });
  });

  if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var MAX = 6;

  Array.prototype.forEach.call(cards, function (card) {
    var raf = 0, px = 0, py = 0;
    function paint() {
      raf = 0;
      var r = card.getBoundingClientRect();
      var x = (px - r.left) / r.width, y = (py - r.top) / r.height;
      card.style.setProperty("--ry", ((x - 0.5) * 2 * MAX).toFixed(2) + "deg");
      card.style.setProperty("--rx", ((0.5 - y) * 2 * MAX).toFixed(2) + "deg");
      card.style.setProperty("--gx", (x * 100).toFixed(1) + "%");
      card.style.setProperty("--gy", (y * 100).toFixed(1) + "%");
    }
    card.addEventListener("pointerenter", function () {
      card.classList.add("is-tilting");
      card.style.setProperty("--glare", "1");
    });
    card.addEventListener("pointermove", function (e) {
      px = e.clientX; py = e.clientY;
      if (!raf) raf = requestAnimationFrame(paint);
    });
    card.addEventListener("pointerleave", function () {
      if (raf) { cancelAnimationFrame(raf); raf = 0; }
      card.classList.remove("is-tilting");
      card.style.setProperty("--rx", "0deg");
      card.style.setProperty("--ry", "0deg");
      card.style.setProperty("--glare", "0");
    });
  });
})();
