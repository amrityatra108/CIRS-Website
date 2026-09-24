/* Alumni destination search. All records remain visible when JavaScript is unavailable. */
(function () {
  "use strict";

  var input = document.getElementById("ajd-q");
  if (!input) return;
  input.closest(".ajd__search").hidden = false;

  var rows = Array.prototype.slice.call(document.querySelectorAll(".ajd__row"));
  var groups = Array.prototype.slice.call(document.querySelectorAll(".ajd__group"));
  var count = document.querySelector("[data-destinations-count]");
  var empty = document.querySelector("[data-destinations-empty]");
  var total = rows.length;
  var countryNodes = document.querySelectorAll(".ajd__country");
  var countries = Object.create(null);
  Array.prototype.forEach.call(countryNodes, function (node) {
    countries[node.textContent.trim()] = true;
  });
  var countryCount = Object.keys(countries).length;

  function update() {
    var query = input.value.trim().toLocaleLowerCase();
    var visible = 0;

    rows.forEach(function (row) {
      var text = (row.dataset.search || row.textContent).toLocaleLowerCase();
      var match = !query || text.indexOf(query) !== -1;
      row.hidden = !match;
      if (match) visible += 1;
    });

    groups.forEach(function (group) {
      var matches = group.querySelectorAll(".ajd__row:not([hidden])").length;
      group.hidden = matches === 0;
      var number = group.querySelector(".ajd__n");
      if (number && number.firstChild) number.firstChild.nodeValue = String(matches);
    });

    if (empty) empty.hidden = visible !== 0;
    if (count) {
      count.textContent = query
        ? visible + " of " + total + " institutions match “" + input.value.trim() + "”."
        : total + " institutions across " + countryCount + " locations.";
    }
  }

  input.addEventListener("input", update);
  update();
}());
