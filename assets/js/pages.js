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

