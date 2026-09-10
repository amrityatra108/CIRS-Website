/* ============================================================
   CIRS Content Editor
   Turns every meaningful piece of copy into an editable field and
   every photo (plus the hero video) into a click-to-replace target,
   then exports a new, complete, self-contained HTML file with the
   changes baked in. No server, no build step — open it, edit it,
   download it.
   ============================================================ */
(function () {
  "use strict";

  document.documentElement.classList.add("cirs-editor-active");

  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  var TEXT_SELECTORS = [
    ".hero .marker .sc", ".hero h1",
    ".quote__text", ".quote__attr",
    ".sec-head .marker .sc", ".sec-head .feature__tag", ".sec-head h2", ".sec-head p.lead",
    ".about .pull", ".about p.copy",
    ".factrail dd",
    ".feature__text .marker .sc", ".feature__text .feature__tag", ".feature__text h2",
    ".feature__text p.copy", ".feature__cta a",
    ".prog__card h3", ".prog__card p.copy", ".prog__meta b",
    ".motto__deva", ".motto__iast", ".motto__en",
    ".dmoment h3", ".dmoment > p:not(.dmoment__i)", ".dmoment__i",
    ".facilities h3", ".facilities p", ".band .btn",
    ".record p", ".record__fig",
    ".peopletile h3", ".peopletile__role", ".peopletile__bio", ".teamphoto figcaption",
    ".steps .step h3", ".steps .step p", ".step__aside",
    ".adm-cta a", ".adm-cta__contact",
    ".finalcta h2", ".finalcta p.lead", ".finalcta__cta a",
    ".footer__brand span", ".footer address", ".footer h4", ".footer li a", ".footer__bar span"
  ].join(",");

  // The curtain removes itself on load when GSAP isn't present (see cirs.js
  // failOpen()), which this editor build deliberately omits, so it is never
  // a live edit target here.
  var IMAGE_SELECTOR = ".feature__media img, .prog__card img, .band__media img, " +
                        ".finalcta__media img, .quote__photo img, .teamphoto img, " +
                        ".brand img, .footer__brand img";

  var dirty = false, dirtyDot, bar;

  function markDirty() {
    if (dirty) return;
    dirty = true;
    if (dirtyDot) dirtyDot.classList.remove("is-clean");
  }

  function forcePlainPaste(el) {
    el.addEventListener("paste", function (e) {
      e.preventDefault();
      var text = (e.clipboardData || window.clipboardData).getData("text/plain");
      document.execCommand("insertText", false, text);
    });
  }

  $$(TEXT_SELECTORS).forEach(function (el) {
    if (el.closest("#cirsEditorBar")) return;
    el.setAttribute("contenteditable", "true");
    el.setAttribute("data-editable", "text");
    forcePlainPaste(el);
    el.addEventListener("input", markDirty);
  });

  /* ----------------------------------------------------------
     Images — a shared hidden file input, and a helper that keeps
     every occurrence of the same photo (e.g. the emblem in the
     header and footer) in sync when one instance is replaced.
     ---------------------------------------------------------- */
  var fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.style.display = "none";
  document.body.appendChild(fileInput);

  var pendingTarget = null;

  function warnIfLarge(file) {
    if (file.size <= 4 * 1024 * 1024) return true;
    var mb = (file.size / 1024 / 1024).toFixed(1);
    return window.confirm(
      "This file is " + mb + " MB. Large photos and video make the exported " +
      "page big and slow to load — consider compressing it first. Use it anyway?"
    );
  }

  function swapAllMatching(oldSrc, newSrc) {
    $$("img").forEach(function (im) { if (im.src === oldSrc) im.src = newSrc; });
  }

  $$(IMAGE_SELECTOR).forEach(function (img) {
    img.setAttribute("data-editable", "image");
    img.addEventListener("click", function (e) {
      e.preventDefault();
      pendingTarget = img;
      fileInput.accept = "image/*";
      fileInput.dataset.mode = "image";
      fileInput.click();
    });
  });

  var heroVideo = document.querySelector(".hero__video");
  if (heroVideo) {
    heroVideo.setAttribute("data-editable", "image");
    heroVideo.addEventListener("click", function () {
      pendingTarget = heroVideo;
      fileInput.accept = "image/*,video/*";
      fileInput.dataset.mode = "hero";
      fileInput.click();
    });
  }

  fileInput.addEventListener("change", function () {
    var file = fileInput.files && fileInput.files[0];
    if (!file || !pendingTarget) return;
    if (!warnIfLarge(file)) { fileInput.value = ""; return; }

    var reader = new FileReader();
    reader.onload = function () {
      var dataUrl = reader.result;
      if (fileInput.dataset.mode === "hero" && file.type.indexOf("video/") === 0) {
        $$("source", heroVideo).forEach(function (s) { s.remove(); });
        heroVideo.src = dataUrl;
        heroVideo.load();
        if (heroVideo.play) heroVideo.play().catch(function () {});
      } else if (fileInput.dataset.mode === "hero") {
        heroVideo.setAttribute("poster", dataUrl);
      } else {
        swapAllMatching(pendingTarget.src, dataUrl);
      }
      markDirty();
      fileInput.value = "";
      pendingTarget = null;
    };
    reader.readAsDataURL(file);
  });

  /* ----------------------------------------------------------
     Toolbar
     ---------------------------------------------------------- */
  bar = document.createElement("div");
  bar.id = "cirsEditorBar";
  bar.innerHTML =
    '<span class="cirs-dirty is-clean" title="Unsaved changes"></span>' +
    "<strong>CIRS Content Editor</strong>" +
    '<span class="cirs-hint">Click any highlighted text to edit it. Click any photo, or the hero video, to replace it.</span>' +
    '<button type="button" class="cirs-reset">Reload (discard changes)</button>' +
    '<button type="button" class="cirs-save">Download Updated Site</button>';
  document.body.appendChild(bar);
  dirtyDot = bar.querySelector(".cirs-dirty");

  bar.querySelector(".cirs-reset").addEventListener("click", function () {
    if (!dirty || window.confirm("Discard all changes and reload the original page?")) location.reload();
  });

  var REAL_TITLE = "Chinmaya International Residential School — Siruvani, Coimbatore";

  bar.querySelector(".cirs-save").addEventListener("click", function () {
    var clone = document.documentElement.cloneNode(true);
    clone.classList.remove("cirs-editor-active");
    var titleEl = clone.querySelector("title");
    if (titleEl) titleEl.textContent = REAL_TITLE;
    $$("[data-editable]", clone).forEach(function (el) {
      el.removeAttribute("data-editable");
      el.removeAttribute("contenteditable");
    });
    ["cirsEditorBar", "cirsEditorStyle", "cirsEditorScript"].forEach(function (id) {
      var el = clone.querySelector("#" + id);
      if (el) el.remove();
    });
    $$("input[type=file]", clone).forEach(function (el) { el.remove(); });

    // This editor build deliberately runs without GSAP/Lenis so the page
    // stays plain and easy to click into. Re-add them on export so the
    // downloaded file regains the real site's scroll animation.
    var mainScript = clone.querySelector("#cirsMainScript");
    if (mainScript) {
      [
        "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js",
        "https://cdn.jsdelivr.net/npm/lenis@1.1.20/dist/lenis.min.js"
      ].forEach(function (src) {
        var s = document.createElement("script");
        s.src = src;
        s.defer = true;
        mainScript.parentNode.insertBefore(s, mainScript);
      });
    }

    var html = "<!doctype html>\n" + clone.outerHTML;
    var blob = new Blob([html], { type: "text/html" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "cirs-website-updated.html";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);

    dirty = false;
    dirtyDot.classList.add("is-clean");
  });

  window.addEventListener("beforeunload", function (e) {
    if (!dirty) return;
    e.preventDefault();
    e.returnValue = "";
  });
})();
