/* Creative Writing: a quiet chapter entrance and an optional reading mode.
   All poetry and navigation are present in the HTML before this file runs. */
(function () {
  "use strict";

  var page = document.body;
  if (!page.classList.contains("cwriting")) return;

  /* The shared smooth-scroll handler prevents native fragment navigation.
     Keep chapter and poem URLs shareable when a reader follows an in-page link. */
  var main = document.getElementById("main");
  var activatingClone = false;
  if (main) {
    document.addEventListener("click", function (event) {
      if (!(event.target instanceof Element)) return;
      var link = event.target.closest('a[href^="#"]');
      if (!link) return;
      var hash = link.getAttribute("href");
      if (!main.contains(link) && !(hash === "#main" && link.classList.contains("skip-link"))) return;
      var target = hash && hash.length > 1 ? document.getElementById(hash.slice(1)) : null;
      if (!target) return;
      if (window.location.hash !== hash) window.history.pushState(null, "", hash);
      if (event.detail === 0 && !activatingClone) {
        var heading = target.querySelector("h1, h2, h3");
        if (heading) {
          heading.setAttribute("tabindex", "-1");
          window.setTimeout(function () { heading.focus({ preventScroll: true }); }, 0);
        }
      }
    }, true);

    /* Repeated cards keep the loop seamless. Their original preview link is
       the sole accessible link, while a pointer can open any visible repeat. */
    main.addEventListener("click", function (event) {
      if (!(event.target instanceof Element)) return;
      var clone = event.target.closest(".cw-row__card[data-cw-target]");
      if (!clone || !main.contains(clone)) return;
      var hash = clone.getAttribute("data-cw-target");
      var original = Array.prototype.find.call(
        main.querySelectorAll("a.cw-row__card[href]"),
        function (link) { return link.getAttribute("href") === hash; }
      );
      if (!original) return;
      activatingClone = true;
      try { original.click(); }
      finally { activatingClone = false; }
    });
  }

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var running = [];
  var pauseButton = document.querySelector(".cw-rows__pause");

  function syncPauseButton() {
    if (!pauseButton) return;
    if (reduce.matches) {
      pauseButton.disabled = true;
      pauseButton.setAttribute("aria-pressed", "true");
      pauseButton.textContent = "Motion off";
      return;
    }
    var paused = page.classList.contains("cw-motion-paused");
    pauseButton.disabled = false;
    pauseButton.setAttribute("aria-pressed", String(paused));
    pauseButton.textContent = paused ? "Resume motion" : "Pause motion";
  }

  if (pauseButton) {
    pauseButton.addEventListener("click", function () {
      page.classList.toggle("cw-motion-paused");
      syncPauseButton();
    });
    syncPauseButton();
  }

  if (main) {
    main.addEventListener("focusin", function (event) {
      if (!(event.target instanceof Element)) return;
      var card = event.target.closest(".cw-row__card[href]");
      if (!card) return;
      var row = card.closest(".cw-row");
      var scroller = row && row.querySelector(".cw-row__window");
      if (!scroller) return;
      window.requestAnimationFrame(function () {
        var frame = scroller.getBoundingClientRect();
        var bounds = card.getBoundingClientRect();
        if (bounds.left < frame.left + 20) scroller.scrollLeft += bounds.left - frame.left - 20;
        else if (bounds.right > frame.right - 20) scroller.scrollLeft += bounds.right - frame.right + 20;
      });
    });
    main.addEventListener("focusout", function (event) {
      if (!(event.target instanceof Element)) return;
      var row = event.target.closest(".cw-row");
      if (!row) return;
      window.setTimeout(function () {
        if (!row.contains(document.activeElement)) {
          var scroller = row.querySelector(".cw-row__window");
          if (scroller && !reduce.matches && !page.classList.contains("cw-motion-paused")) {
            scroller.scrollLeft = 0;
          }
        }
      }, 0);
    });
  }

  if ("IntersectionObserver" in window && !reduce.matches) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        if (reduce.matches || !entry.target.animate) return;
        var animation = entry.target.animate(
          [
            { opacity: 0.7, transform: "translateY(16px)" },
            { opacity: 1, transform: "translateY(0)" }
          ],
          {
            duration: entry.target.classList.contains("cw-interlude") ? 800 : 620,
            easing: "cubic-bezier(.2,.75,.3,1)"
          }
        );
        running.push(animation);
        animation.addEventListener("finish", function () {
          var index = running.indexOf(animation);
          if (index !== -1) running.splice(index, 1);
        }, { once: true });
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.04 });

    document.querySelectorAll(".cw-chapter__head, .cw-interlude").forEach(function (element) {
      observer.observe(element);
    });
  }

  function cancelMotion() {
    if (!reduce.matches) return;
    running.forEach(function (animation) { animation.cancel(); });
    running.length = 0;
  }
  if (reduce.addEventListener) {
    reduce.addEventListener("change", function () {
      cancelMotion();
      syncPauseButton();
    });
  }

  var controls = [];
  function setQuietReading(quiet) {
    page.classList.toggle("cw-quiet", quiet);
    controls.forEach(function (button) {
      button.setAttribute("aria-pressed", String(quiet));
      button.textContent = quiet ? "Show chapter design" : "Quiet reading";
    });
  }

  document.querySelectorAll(".cw-chapter__head").forEach(function (header) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "cw-reader-toggle";
    button.setAttribute("aria-pressed", "false");
    button.textContent = "Quiet reading";
    button.addEventListener("click", function () {
      setQuietReading(!page.classList.contains("cw-quiet"));
    });
    header.appendChild(button);
    controls.push(button);
  });
})();
