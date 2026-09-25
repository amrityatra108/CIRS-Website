/* Search and category browsing for the published News archive. */
(function () {
  "use strict";

  var list = document.getElementById("journal-archive-list");
  var search = document.getElementById("journal-search");
  var status = document.getElementById("journal-status");
  var empty = document.getElementById("journal-empty");
  var reset = document.getElementById("journal-reset");
  var filters = Array.prototype.slice.call(document.querySelectorAll("[data-journal-filter]"));
  if (!list || !search || !status || !empty || !reset || !filters.length) return;

  var rows = Array.prototype.slice.call(list.querySelectorAll("[data-journal-category]"));
  var category = "all";
  document.body.classList.add("journal-js");

  function normalise(value) {
    return value.toLocaleLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").trim();
  }

  function update() {
    var query = normalise(search.value);
    var visible = 0;

    rows.forEach(function (row) {
      var topics = (row.dataset.journalTopics || "").split(/\s+/);
      var matchesCategory = category === "all" || row.dataset.journalCategory === category || topics.indexOf(category) !== -1;
      var haystack = normalise(row.textContent + " " + (row.dataset.journalSearch || ""));
      var matchesSearch = !query || haystack.indexOf(query) !== -1;
      row.hidden = !(matchesCategory && matchesSearch);
      if (!row.hidden) visible += 1;
    });

    status.textContent = visible + (visible === 1 ? " story" : " stories");
    empty.hidden = visible !== 0;
  }

  filters.forEach(function (button) {
    button.addEventListener("click", function () {
      category = button.dataset.journalFilter;
      filters.forEach(function (item) {
        item.setAttribute("aria-pressed", String(item === button));
      });
      update();
    });
  });

  search.addEventListener("input", update);
  var main = document.querySelector("main");
  main.addEventListener("click", function (event) {
    var link = event.target.closest('a[href^="#"]');
    if (!link || !main.contains(link)) return;
    var hash = link.getAttribute("href");
    if (!document.getElementById(hash.slice(1))) return;
    if (window.location.hash !== hash) window.history.pushState(null, "", hash);
  });
  reset.addEventListener("click", function () {
    category = "all";
    search.value = "";
    filters.forEach(function (item) {
      item.setAttribute("aria-pressed", String(item.dataset.journalFilter === "all"));
    });
    update();
    search.focus();
  });

  update();

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var hero = document.querySelector(".journal-hero");
  var slides = hero && Array.prototype.slice.call(hero.querySelectorAll("[data-journal-slide]"));
  if (hero && slides.length > 1) {
    var heroStage = document.getElementById("journal-hero-stage");
    var indicators = Array.prototype.slice.call(hero.querySelectorAll("[data-journal-slide-to]"));
    var heroCount = document.getElementById("journal-hero-count");
    var heroToggle = document.getElementById("journal-hero-toggle");
    var heroPrev = document.getElementById("journal-hero-prev");
    var heroNext = document.getElementById("journal-hero-next");
    var heroAnnouncement = document.getElementById("journal-hero-announcement");
    var hoverAvailable = window.matchMedia("(hover: hover)");
    var heroIndex = 0;
    var heroTimer = null;
    var heroFadeTimer = null;
    var heroPendingIndex = null;
    var heroPaused = false;
    var heroInterval = 9000;
    var heroFadeHalf = 210;

    function stopHeroTimer() {
      if (heroTimer) window.clearTimeout(heroTimer);
      heroTimer = null;
    }

    function canRotateHero() {
      return !heroPaused && !reducedMotion.matches && !document.hidden &&
        !(hoverAvailable.matches && hero.matches(":hover")) && !hero.querySelector(":focus-visible");
    }

    function scheduleHero() {
      stopHeroTimer();
      if (!canRotateHero()) return;
      heroTimer = window.setTimeout(function () {
        transitionHero(heroIndex + 1, false);
      }, heroInterval - heroFadeHalf);
    }

    function setHeroPaused(paused) {
      heroPaused = paused;
      heroToggle.setAttribute("aria-pressed", String(paused));
      heroToggle.setAttribute("aria-label", paused ? "Play story rotation" : "Pause story rotation");
      heroToggle.textContent = paused ? "Play" : "Pause";
      scheduleHero();
    }

    function showHero(next, announced) {
      heroIndex = (next + slides.length) % slides.length;
      slides.forEach(function (slide, index) {
        var active = index === heroIndex;
        slide.classList.toggle("is-active", active);
        slide.inert = !active;
        if (active) slide.removeAttribute("aria-hidden");
        else slide.setAttribute("aria-hidden", "true");
      });
      indicators.forEach(function (button, index) {
        button.setAttribute("aria-pressed", String(index === heroIndex));
      });
      heroCount.textContent = String(heroIndex + 1).padStart(2, "0") + " / " + String(slides.length).padStart(2, "0");
      if (announced) heroAnnouncement.textContent = "Featured story: " + slides[heroIndex].querySelector("h2").textContent.trim();
      scheduleHero();
    }

    function transitionHero(next, announced) {
      var target = (next + slides.length) % slides.length;
      stopHeroTimer();
      if (heroFadeTimer) window.clearTimeout(heroFadeTimer);
      if (reducedMotion.matches) {
        heroFadeTimer = null;
        heroPendingIndex = null;
        heroStage.classList.remove("is-fading");
        showHero(target, announced);
        return;
      }
      heroPendingIndex = target;
      heroStage.classList.add("is-fading");
      heroFadeTimer = window.setTimeout(function () {
        heroFadeTimer = null;
        var settled = heroPendingIndex;
        heroPendingIndex = null;
        showHero(settled, announced);
        heroStage.classList.remove("is-fading");
      }, heroFadeHalf);
    }

    function stepHero(direction) {
      transitionHero((heroPendingIndex === null ? heroIndex : heroPendingIndex) + direction, true);
    }

    indicators.forEach(function (button) {
      button.addEventListener("click", function () { transitionHero(Number(button.dataset.journalSlideTo), true); });
    });
    heroPrev.addEventListener("click", function () { stepHero(-1); });
    heroNext.addEventListener("click", function () { stepHero(1); });
    heroToggle.addEventListener("click", function () { setHeroPaused(!heroPaused); });
    hero.addEventListener("pointerdown", function (event) {
      if (event.pointerType !== "mouse" && event.target !== heroToggle) setHeroPaused(true);
    });
    hero.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      stepHero(event.key === "ArrowRight" ? 1 : -1);
    });
    hero.addEventListener("mouseenter", stopHeroTimer);
    hero.addEventListener("mouseleave", scheduleHero);
    hero.addEventListener("focusin", stopHeroTimer);
    hero.addEventListener("focusout", function () { window.setTimeout(scheduleHero, 0); });
    document.addEventListener("visibilitychange", scheduleHero);
    reducedMotion.addEventListener("change", function () {
      heroToggle.hidden = reducedMotion.matches;
      if (reducedMotion.matches && heroFadeTimer) {
        window.clearTimeout(heroFadeTimer);
        heroFadeTimer = null;
        var settled = heroPendingIndex;
        heroPendingIndex = null;
        heroStage.classList.remove("is-fading");
        showHero(settled, false);
      }
      scheduleHero();
    });
    heroToggle.hidden = reducedMotion.matches;
    showHero(0, false);
  }

  var highlightLinks = Array.prototype.slice.call(document.querySelectorAll('.journal-highlights-nav a[href^="#highlight-"]'));
  var highlightCount = document.getElementById("journal-highlight-count");
  var highlightProgress = document.getElementById("journal-highlight-progress");
  var highlightTargets = highlightLinks.map(function (link) { return document.querySelector(link.getAttribute("href")); });
  if (highlightLinks.length && highlightTargets.every(Boolean) && highlightCount && highlightProgress) {
    var highlightIndex = -1;
    var highlightScrollQueued = false;
    var highlightLockUntil = 0;

    function paintHighlight(next) {
      if (next === highlightIndex) return;
      highlightIndex = next;
      highlightCount.textContent = (next + 1) + " of " + highlightLinks.length;
      highlightProgress.style.width = ((next + 1) / highlightLinks.length * 100) + "%";
      highlightLinks.forEach(function (link, index) {
        if (index === next) link.setAttribute("aria-current", "true");
        else link.removeAttribute("aria-current");
      });
    }

    function trackHighlights() {
      if (Date.now() < highlightLockUntil) return;
      var next = 0;
      var bestTop = -Infinity;
      highlightTargets.forEach(function (target, index) {
        var top = target.getBoundingClientRect().top;
        if (top < window.innerHeight * 0.42 && (top > bestTop + 4 || (Math.abs(top - bestTop) <= 4 && index === highlightIndex))) {
          next = index;
          bestTop = top;
        }
      });
      paintHighlight(next);
    }

    highlightLinks.forEach(function (link, index) {
      link.addEventListener("click", function () {
        highlightLockUntil = Date.now() + (reducedMotion.matches ? 0 : 1600);
        paintHighlight(index);
        window.setTimeout(trackHighlights, reducedMotion.matches ? 0 : 1650);
      });
    });
    window.addEventListener("scroll", function () {
      if (highlightScrollQueued) return;
      highlightScrollQueued = true;
      window.requestAnimationFrame(function () { highlightScrollQueued = false; trackHighlights(); });
    }, { passive: true });
    window.addEventListener("resize", trackHighlights);
    trackHighlights();
  }
}());
