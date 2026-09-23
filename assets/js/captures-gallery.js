/* CIRS Captures — the photograph viewer.

   Every tile in the gallery is a link to its full-size image, which is what
   happens without this script. With it, a plain click opens the viewer
   instead: a native modal dialog, so the page behind is inert and Escape
   closes it without any help from here. A click with a modifier key is
   left alone, so a photograph can still be opened in a tab of its own.

   Nothing full-size is fetched until a photograph is opened. The viewer
   shows the tile at once, which the page has usually loaded already, and
   swaps in the full-size image when it has decoded; then it fetches the
   next and the previous, so that stepping through is immediate. Closing
   returns focus to the tile that opened it. */
(function () {
  "use strict";

  var box = document.querySelector("[data-cv]");
  var items = Array.prototype.slice.call(document.querySelectorAll("[data-cg-item]"));
  if (!box || !items.length || typeof box.showModal !== "function") return;

  var frame = box.querySelector("[data-cv-frame]");
  var stage = box.querySelector("[data-cv-stage]");
  var caption = box.querySelector("[data-cv-caption]");
  var credit = box.querySelector("[data-cv-credit]");
  var count = box.querySelector("[data-cv-count]");
  var total = items.length;
  var current = -1, opener = null;
  var fetched = {};          // full-size images already asked for, by URL

  function wrap(i) { return (i % total + total) % total; }

  function tileImage(i) { return items[i].querySelector("img"); }

  // Ask for a full-size image once, and remember that it was asked for.
  function fetchFull(i) {
    var url = items[i].getAttribute("href");
    if (!fetched[url]) {
      var img = new Image();
      img.decoding = "async";
      img.src = url;
      fetched[url] = img;
    }
    return fetched[url];
  }

  function show(i, animate) {
    i = wrap(i);
    current = i;
    var item = items[i], tile = tileImage(i);
    var w = +item.getAttribute("data-cg-w"), h = +item.getAttribute("data-cg-h");

    var img = document.createElement("img");
    img.alt = tile.alt;
    img.width = w;
    img.height = h;
    // The full-size image if it is already here (a neighbour fetched in
    // advance); otherwise the tile, which is small, and which the page has
    // usually loaded already.
    var full = fetchFull(i);
    img.src = full.complete && full.naturalWidth ? full.src : (tile.currentSrc || tile.src);
    if (animate) img.className = "is-entering";

    // The photograph on screen stays until the next one has decoded, so that
    // stepping through never flashes an empty frame; the caption and the
    // count change with it. A decode that is slow is not waited for long.
    var placed = false;
    function place() {
      if (placed || current !== i) return;
      placed = true;
      box.style.setProperty("--cv-ar", (w / h).toFixed(4));
      // Laid over the photograph it replaces, which goes once it is covered.
      var old = Array.prototype.slice.call(frame.children);
      frame.appendChild(img);
      function clear() { old.forEach(function (o) { o.remove(); }); }
      if (animate && old.length) {
        img.addEventListener("animationend", clear, { once: true });
        window.setTimeout(clear, 600);
      } else clear();
      caption.textContent = tile.alt;
      var who = item.getAttribute("data-cg-credit");
      credit.textContent = who ? "Photograph: " + who : "";
      credit.hidden = !who;
      count.textContent = (i + 1) + " / " + total;
    }
    if (img.decode) img.decode().then(place, place);
    window.setTimeout(place, 250);
    if (!frame.firstChild) place();

    function swap() {
      // Only if the reader is still on this photograph.
      if (current !== i) return;
      if (img.src !== full.src) img.src = full.src;
      fetchFull(wrap(i + 1));
      fetchFull(wrap(i - 1));
    }
    if (full.complete && full.naturalWidth) swap();
    else if (full.decode) full.decode().then(swap, function () {});
    else full.addEventListener("load", swap);
  }

  function open(i, from) {
    opener = from;
    show(i, false);
    box.showModal();
    document.body.classList.add("has-lightbox");
  }

  function step(d) { if (box.open) show(current + d, true); }

  box.addEventListener("close", function () {
    document.body.classList.remove("has-lightbox");
    frame.replaceChildren();
    current = -1;
    if (opener) { opener.focus({ preventScroll: true }); opener = null; }
  });

  items.forEach(function (item, i) {
    item.setAttribute("aria-haspopup", "dialog");
    item.addEventListener("click", function (e) {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      open(i, item);
    });
  });

  box.querySelector("[data-cv-close]").addEventListener("click", function () { box.close(); });
  box.querySelector("[data-cv-prev]").addEventListener("click", function () { step(-1); });
  box.querySelector("[data-cv-next]").addEventListener("click", function () { step(1); });

  box.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
  });

  // A swipe sideways steps through. Vertical movement and pinching are the
  // browser's (touch-action on the stage), and a zoomed-in page is being
  // panned, not swiped, so it is left alone.
  var start = null, swipedAt = -1;
  stage.addEventListener("pointerdown", function (e) {
    if (e.pointerType === "mouse" || !e.isPrimary) return;
    start = { x: e.clientX, y: e.clientY, t: e.timeStamp };
  });
  stage.addEventListener("pointercancel", function () { start = null; });
  stage.addEventListener("pointerup", function (e) {
    if (!start) return;
    var dx = e.clientX - start.x, dy = e.clientY - start.y;
    var zoomed = window.visualViewport && window.visualViewport.scale > 1.01;
    start = null;
    if (zoomed || Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy) * 1.2) return;
    swipedAt = e.timeStamp;
    step(dx < 0 ? 1 : -1);
  });

  // A click on the dark around the photograph closes, as it does in most
  // viewers; a click on the photograph, its caption or a control does not,
  // and nor does the click some browsers send at the end of a swipe.
  box.addEventListener("click", function (e) {
    if (e.timeStamp - swipedAt < 500) return;
    if (!e.target.closest("img, .cv__caption, .cv__count, button")) box.close();
  });
})();
