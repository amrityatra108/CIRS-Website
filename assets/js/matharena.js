/* The Math Challenge archive: grade filters and search.

   No dependency and no framework — the page holds the cards, this only
   decides which of them are shown. It exits immediately when there is no
   archive on the page, which is the case until the mathematics department
   supplies the problem papers, so the file costs an empty page nothing.

   Filtering hides with the hidden attribute rather than display:none, so a
   hidden card leaves the tab order and the accessibility tree rather than
   staying in it invisibly. The filter buttons carry aria-pressed, so which
   zone is showing is announced and not only coloured.

   The attribute still does that work; it just no longer does it on the same
   frame as the decision. A card fades out first and takes the attribute at
   the end of the fade, and gets the attribute removed before it fades back
   in. The card's own opacity transition is in the stylesheet -- nothing here
   animates anything, it only sequences the attribute against a transition
   that already exists, which is why this file still has no dependency. */
(function () {
  "use strict";

  var grid = document.getElementById("maGrid");
  if (!grid) return;                       // nothing published yet

  var cards = Array.prototype.slice.call(grid.querySelectorAll(".ma-card"));
  var months = Array.prototype.slice.call(grid.querySelectorAll(".ma-month"));
  var buttons = Array.prototype.slice.call(document.querySelectorAll(".ma-filter"));
  var search = document.getElementById("maSearch");
  var none = document.getElementById("maNone");
  var grade = "all";
  var term = "";

  // Matches the opacity transition on .ma-card in matharena.css: no shorter,
  // or a card would take the hidden attribute while still visible and vanish
  // mid-fade. Zero under reduced motion, where the stylesheet turns the
  // transition off -- waiting out a fade that is not running would leave the
  // card sitting there at full opacity for a fifth of a second and then pop,
  // which is worse than the instant switch reduced motion asked for.
  var FADE = window.matchMedia
    && window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 200;

  function reveal(card) {
    if (card.tOut) { clearTimeout(card.tOut); card.tOut = 0; }
    if (!card.hidden && !card.classList.contains("is-out")) return;
    card.hidden = false;
    // The attribute and the class cannot come off in the same frame: the
    // card would be laid out already at full opacity and there would be
    // nothing to transition from.
    requestAnimationFrame(function () { card.classList.remove("is-out"); });
  }

  function conceal(card) {
    if (card.hidden) return;
    if (card.classList.contains("is-out")) return;   // already on its way out
    card.classList.add("is-out");
    card.tOut = setTimeout(function () {
      card.hidden = true;
      card.tOut = 0;
      settle();
    }, FADE);
  }

  // A month with nothing left showing goes too, heading and all — a bare
  // month name over an empty space reads as a month with no winners. This
  // runs after the fades rather than with them, or the month would take its
  // cards out from under them while they were still fading.
  function settle() {
    months.forEach(function (m) {
      m.hidden = !m.querySelector(".ma-card:not([hidden])");
    });
    if (none) none.hidden = !!grid.querySelector(".ma-card:not([hidden])");
  }

  function apply() {
    cards.forEach(function (card) {
      var byGrade = grade === "all" || card.dataset.grade === grade;
      var byTerm = !term || (card.dataset.find || "").indexOf(term) !== -1;
      if (byGrade && byTerm) reveal(card); else conceal(card);
    });
    // Anything coming back needs its month back now, not in a fifth of a
    // second; anything leaving is settled by its own timer.
    settle();
  }

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      grade = btn.dataset.grade;
      buttons.forEach(function (b) {
        var on = b === btn;
        b.classList.toggle("is-on", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      apply();
    });
  });

  if (search) {
    search.addEventListener("input", function () {
      term = search.value.trim().toLowerCase();
      apply();
    });
  }
})();
