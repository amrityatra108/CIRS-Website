/* Creative Writing owns excerpts and reading aids; cirs.js owns the header,
   GSAP registration and the single Lenis instance. All text exists without JS. */
(function () {
  "use strict";
  function boot() {
    var body = document.body;
    if (!body.classList.contains("cwriting") || body.dataset.cwBooted) return;
    body.dataset.cwBooted = "true";
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    var running = [];
    function animate(el, frames, timing) {
      if (reduced.matches || !el || typeof el.animate !== "function") return null;
      var animation = el.animate(frames, timing);
      running.push(animation);
      animation.finished.catch(function () {}).finally(function () {
        running = running.filter(function (a) { return a !== animation; });
      });
      return animation;
    }
    function revealLines() {
      document.querySelectorAll(".cw-excerpt-line").forEach(function (line, i) {
        animate(line, [{ opacity: 0, transform: "translateY(7px)" }, { opacity: 1, transform: "none" }],
          { duration: 360, delay: i * 65, easing: "ease-out" });
      });
    }
    reduced.addEventListener("change", function () {
      if (reduced.matches) running.slice().forEach(function (a) { a.cancel(); });
    });

    var payload = document.getElementById("cw-excerpts");
    var feature = document.querySelector("[data-cw-feature]");
    var another = document.querySelector("[data-cw-another]");
    if (payload && feature && another) {
      var pool;
      try { pool = JSON.parse(payload.textContent); } catch (e) { pool = []; }
      if (pool.length > 1) {
        var index = 0, changing = false;
        another.hidden = false;
        revealLines();
        function replace() {
          index = (index + 1) % pool.length;
          var excerpt = pool[index];
          var text = document.querySelector("[data-cw-excerpt]");
          var fragment = document.createDocumentFragment();
          excerpt.lines.forEach(function (line) {
            var span = document.createElement("span");
            span.className = "cw-excerpt-line";
            span.textContent = line;
            fragment.appendChild(span);
          });
          // One synchronous update: visual text, attribution and destination
          // always describe the same poem, including during the entrance.
          text.replaceChildren(fragment);
          document.querySelector("[data-cw-author]").textContent = excerpt.author;
          document.querySelector("[data-cw-grade]").textContent = excerpt.grade || "";
          document.querySelector("[data-cw-edition]").textContent = excerpt.edition;
          document.querySelector("[data-cw-date]").textContent = excerpt.date;
          document.querySelector("[data-cw-read]").setAttribute("href", excerpt.href);
          document.querySelector("[data-cw-announcement]").textContent = "Now showing " + excerpt.author + ", " + excerpt.edition + ".";
          animate(feature, [{ opacity: .2 }, { opacity: 1 }], { duration: 230, easing: "ease-out" });
          revealLines();
          changing = false;
        }
        another.addEventListener("click", function () {
          if (changing) return;
          changing = true;
          var exit = animate(feature, [{ opacity: 1 }, { opacity: .2 }], { duration: 120 });
          if (exit) exit.finished.then(replace, replace);
          else replace();
        });
      }
    }

    // Animate only arriving archive rows. CSS never hides content, and no
    // enhancement is necessary to reach an edition or read any stanza.
    if ("IntersectionObserver" in window) {
      var entrance = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          animate(entry.target, [{ opacity: .6, transform: "translateY(8px)" }, { opacity: 1, transform: "none" }],
            { duration: 350, easing: "ease-out" });
          entrance.unobserve(entry.target);
        });
      }, { threshold: .05 });
      document.querySelectorAll(".cw-archive-row").forEach(function (row) { entrance.observe(row); });
    }

    var disclosure = document.querySelector("[data-cw-contents]");
    var mobile = window.matchMedia("(max-width: 850px)");
    function sizeContents() {
      if (disclosure) disclosure.open = !mobile.matches || location.hash === "#contents";
    }
    sizeContents();
    mobile.addEventListener("change", sizeContents);
    var userMoved = false;
    ["wheel", "touchstart", "pointerdown", "keydown"].forEach(function (type) {
      window.addEventListener(type, function () { userMoved = true; }, { passive: true });
    });
    function targetFromHash() {
      try { return document.getElementById(decodeURIComponent(location.hash.slice(1))); }
      catch (e) { return null; }
    }
    function alignHash(force, focus) {
      if (!location.hash || (userMoved && !force)) return;
      var target = targetFromHash();
      if (!target || !target.closest(".cw-page,.cw-edition")) return;
      if (disclosure && location.hash === "#contents") disclosure.open = true;
      requestAnimationFrame(function () {
        var header = document.querySelector("#header .nv-header__bar");
        var offset = Math.max(112, header ? header.getBoundingClientRect().bottom + 24 : 112);
        var top = Math.max(0, target.getBoundingClientRect().top + window.scrollY - offset);
        var event = new CustomEvent("cirs-section-scroll", { cancelable: true, detail: { top: top, duration: 0 } });
        // Reuse the shared scroll engine if present; otherwise the browser
        // supplies identical fragment behavior. Do not create a new engine.
        if (window.dispatchEvent(event)) window.scrollTo({ top: top, behavior: "instant" });
        if (focus && target.matches("[data-cw-poem]")) target.focus({ preventScroll: true });
      });
    }
    window.addEventListener("hashchange", function () { alignHash(true, true); });
    window.addEventListener("pageshow", function (event) { if (!event.persisted) alignHash(false, false); });
    window.addEventListener("load", function () { alignHash(false, false); }, { once: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { alignHash(false, false); });
    alignHash(false, false);

    var rail = document.querySelector(".cw-rail");
    if (rail && "IntersectionObserver" in window) {
      var active = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          rail.querySelectorAll("a[aria-current]").forEach(function (a) { a.removeAttribute("aria-current"); });
          var link = Array.from(rail.querySelectorAll("a")).find(function (a) { return a.hash === "#" + entry.target.id; });
          if (link) link.setAttribute("aria-current", "location");
        });
      }, { rootMargin: "-15% 0px -65% 0px", threshold: 0 });
      document.querySelectorAll("[data-cw-poem]").forEach(function (poem) { active.observe(poem); });
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
})();
