/* The Math Challenge archive: grade filters and search.

   No dependency and no framework — the page holds the cards, this only
   decides which of them are shown. It exits immediately when there is no
   archive on the page, which is the case until the mathematics department
   supplies the problem papers, so the file costs an empty page nothing.

   Filtering hides with the hidden attribute rather than display:none, so a
   hidden card leaves the tab order and the accessibility tree rather than
   staying in it invisibly. The filter buttons carry aria-pressed, so which
   zone is showing is announced and not only coloured. */
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

  function apply() {
    var shown = 0;
    cards.forEach(function (card) {
      var byGrade = grade === "all" || card.dataset.grade === grade;
      var byTerm = !term || (card.dataset.find || "").indexOf(term) !== -1;
      var show = byGrade && byTerm;
      card.hidden = !show;
      if (show) shown++;
    });
    // A month with nothing left showing goes too, heading and all — a bare
    // month name over an empty space reads as a month with no winners.
    months.forEach(function (m) {
      m.hidden = !m.querySelector(".ma-card:not([hidden])");
    });
    if (none) none.hidden = shown !== 0;
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
