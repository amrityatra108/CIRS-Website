/* Creative Writing: the anthology's shelves and chapters, and a focused
   reader that shows one poem at a time.
   All poetry and navigation are present in the HTML before this file runs;
   without it the page is the whole anthology, chapter after chapter. */
(function () {
  "use strict";

  var page = document.body;
  if (!page.classList.contains("cwriting")) return;
  var root = document.documentElement;
  root.classList.add("cw-js");

  var main = document.getElementById("main");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* ==========================================================
     The reader
     One poem at a time. The chapter sections keep every article; the reader
     borrows the one being read and gives it back when the reader moves on,
     so a poem is never copied and never two are on screen.
     ========================================================== */
  var reader = document.querySelector("[data-cw-reader]");
  var stage = reader && reader.querySelector("[data-cw-reader-stage]");
  var chapters = [];
  var byPoem = {};

  if (reader && stage) {
    Array.prototype.forEach.call(document.querySelectorAll("[data-cw-chapter]"), function (section) {
      var shelf = section.querySelector(".cw-chapter__poems");
      if (!shelf) return;
      var chapter = {
        id: section.id,
        number: section.getAttribute("data-cw-chapter-number") || "",
        design: section.getAttribute("data-cw-design") || "",
        title: (section.querySelector(".cw-chapter__title") || {}).textContent || "",
        section: section,
        shelf: shelf,
        poems: Array.prototype.slice.call(shelf.querySelectorAll("[data-cw-poem]"))
      };
      chapters.push(chapter);
      chapter.poems.forEach(function (poem, index) {
        byPoem[poem.id] = { chapter: chapter, index: index };
      });
    });
  }

  var hasReader = chapters.length > 0;

  /* The state the reader keeps. Everything visible is drawn from it. */
  var state = {
    currentChapter: null,
    currentPoemIndex: -1,
    currentPoem: null,
    previousPoem: null,
    nextPoem: null,
    showChapterDesign: false,
    quietReading: false
  };

  var baseTitle = document.title;
  var switching = null;

  function poemTitle(poem) {
    var heading = poem && poem.querySelector(".cw-poem__title");
    return heading ? heading.textContent.trim() : "";
  }
  function poemAuthor(poem) {
    var name = poem && poem.querySelector(".cw-poem__byline span");
    return name ? name.textContent.trim() : "";
  }

  /* Reading modes are a per-reader convenience, remembered between visits
     where the browser allows it and never required for the page to work. */
  var MODE_KEYS = { design: "cirs-cw-chapter-design", quiet: "cirs-cw-quiet-reading" };
  function remembered(key) {
    try { return window.localStorage.getItem(MODE_KEYS[key]) === "on"; }
    catch (error) { return false; }
  }
  function remember(key, on) {
    try { window.localStorage.setItem(MODE_KEYS[key], on ? "on" : "off"); }
    catch (error) { /* Private windows may refuse storage; the mode still applies. */ }
  }

  /* The reader has no full-screen picture at its head, so the shared header
     sits on its pill there, told whether the ground beneath it is dark. */
  var header = document.getElementById("header");
  var headerStart = header ? header.getAttribute("data-header-start") : null;
  function syncHeader() {
    if (!reader) return;
    var reading = root.classList.contains("cw-reading");
    var dark = state.quietReading || (state.showChapterDesign &&
      !!state.currentChapter && state.currentChapter.design === "night");
    reader.setAttribute("data-header-theme", dark ? "dark" : "light");
    if (header && headerStart) header.setAttribute("data-header-start", reading ? "content" : headerStart);
    window.dispatchEvent(new CustomEvent("cirs-header-refresh"));
  }

  function applyModes() {
    if (!reader) return;
    reader.classList.toggle("cw-reader--design", state.showChapterDesign);
    reader.classList.toggle("cw-reader--quiet", state.quietReading);
    root.classList.toggle("cw-reading-quiet", state.quietReading && root.classList.contains("cw-reading"));
    Array.prototype.forEach.call(reader.querySelectorAll("[data-cw-mode]"), function (button) {
      var on = button.getAttribute("data-cw-mode") === "design" ? state.showChapterDesign : state.quietReading;
      button.setAttribute("aria-pressed", String(on));
    });
    syncHeader();
  }

  function returnPoem(poem) {
    var home = poem && byPoem[poem.id];
    if (!home || !stage.contains(poem)) return;
    var after = home.chapter.poems.slice(home.index + 1).filter(function (p) {
      return p.parentNode === home.chapter.shelf;
    })[0];
    home.chapter.shelf.insertBefore(poem, after || null);
  }

  function setStep(button, target, direction) {
    var label = direction < 0 ? "Previous poem" : "Next poem";
    var title = button.querySelector("[data-cw-step-title]");
    if (target) {
      button.removeAttribute("aria-disabled");
      button.setAttribute("aria-label", label + ": " + poemTitle(target) + ", by " + poemAuthor(target));
      if (title) title.textContent = poemTitle(target);
    } else {
      button.setAttribute("aria-disabled", "true");
      button.setAttribute("aria-label", label + ": " + (direction < 0 ?
        "this is the first poem in the chapter" : "this is the last poem in the chapter"));
      if (title) title.textContent = direction < 0 ? "First poem of the chapter" : "Last poem of the chapter";
    }
  }

  function drawChrome() {
    var chapter = state.currentChapter;
    var count = chapter.poems.length;
    reader.setAttribute("data-cw-design", chapter.design);
    reader.querySelector("[data-cw-reader-eyebrow]").textContent = "Chapter " + chapter.number;
    reader.querySelector("[data-cw-reader-chapter]").textContent = chapter.title;
    reader.querySelector("[data-cw-back]").setAttribute("href", "#" + chapter.id);
    reader.querySelector("[data-cw-position]").textContent =
      "Poem " + (state.currentPoemIndex + 1) + " of " + count;
    setStep(reader.querySelector('[data-cw-step="-1"]'), state.previousPoem, -1);
    setStep(reader.querySelector('[data-cw-step="1"]'), state.nextPoem, 1);
    document.title = poemTitle(state.currentPoem) + " — " + chapter.title + " | " + baseTitle;
  }

  function scrollToReader() {
    var top = reader.getBoundingClientRect().top + window.scrollY;
    window.scrollTo({ top: Math.max(0, top), behavior: "instant" });
  }

  function place(found) {
    var previous = state.currentPoem;
    var chapter = found.chapter;
    var poem = chapter.poems[found.index];
    if (previous && previous !== poem) returnPoem(previous);
    state.currentChapter = chapter;
    state.currentPoemIndex = found.index;
    state.currentPoem = poem;
    state.previousPoem = chapter.poems[found.index - 1] || null;
    state.nextPoem = chapter.poems[found.index + 1] || null;
    if (poem.parentNode !== stage) stage.appendChild(poem);
    var heading = poem.querySelector(".cw-poem__title");
    if (heading) heading.setAttribute("tabindex", "-1");
    drawChrome();
  }

  function announce() {
    var status = reader.querySelector("[data-cw-reader-status]");
    if (!status) return;
    status.textContent = "";
    window.setTimeout(function () {
      status.textContent = "Poem " + (state.currentPoemIndex + 1) + " of " +
        state.currentChapter.poems.length + ": " + poemTitle(state.currentPoem) +
        ", by " + poemAuthor(state.currentPoem) + ".";
    }, 60);
  }

  function focusTitle() {
    var heading = state.currentPoem && state.currentPoem.querySelector(".cw-poem__title");
    if (heading) heading.focus({ preventScroll: true });
  }

  /* Open a poem. `focus` is "title" when the reader should move there,
     "keep" when focus should stay on the control just used. */
  function openPoem(found, options) {
    options = options || {};
    var wasOpen = root.classList.contains("cw-reading");
    var sameChapter = wasOpen && state.currentChapter === found.chapter;

    function show() {
      place(found);
      if (!wasOpen) {
        reader.hidden = false;
        root.classList.add("cw-reading");
      }
      // Also on a change of chapter: the night design darkens the ground.
      applyModes();
      root.classList.remove("cw-boot-reader");
      scrollToReader();
      // A step keeps focus while it can be used again; at either end of the
      // chapter, focus moves to the poem rather than rest on a spent control.
      var active = document.activeElement;
      var spent = active && active.getAttribute && active.getAttribute("aria-disabled") === "true" &&
        reader.contains(active);
      if (options.focus === "title" || (options.focus === "keep" && spent)) focusTitle();
      if (wasOpen) announce();
    }

    stopSwitch();
    // Between poems of one chapter, a short fade: the page settles on the
    // new poem rather than cutting to it. Anything else changes at once.
    // A timer, not an animation's finish event, makes the swap, so a tab
    // that is not painting still changes poem.
    if (sameChapter && !reduce.matches) {
      stage.classList.add("is-leaving");
      switching = window.setTimeout(function () {
        switching = null;
        show();
        stage.classList.remove("is-leaving");
        stage.classList.add("is-arriving");
        void stage.offsetWidth;
        stage.classList.remove("is-arriving");
      }, 150);
      return;
    }
    show();
  }

  function stopSwitch() {
    if (switching) window.clearTimeout(switching);
    switching = null;
    stage.classList.remove("is-leaving", "is-arriving");
  }

  function closeReader() {
    stopSwitch();
    if (state.currentPoem) returnPoem(state.currentPoem);
    reader.hidden = true;
    root.classList.remove("cw-reading", "cw-reading-quiet", "cw-boot-reader");
    document.title = baseTitle;
    syncHeader();
  }

  /* Mark the poem last read in its chapter's list, so a reader returning to
     the chapter sees where they were. */
  function markLastRead(chapter, poem) {
    Array.prototype.forEach.call(chapter.section.querySelectorAll(".cw-contents__link"), function (link) {
      var last = poem && link.getAttribute("href") === "#" + poem.id;
      link.classList.toggle("is-last-read", !!last);
      if (last) link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
    });
  }

  /* Every in-page address goes through here: typed, followed or walked with
     Back and Forward. */
  function route(hash, options) {
    options = options || {};
    var id = hash && hash.length > 1 ? decodeURIComponent(hash.slice(1)) : "";
    var found = hasReader ? byPoem[id] : null;
    if (found) {
      openPoem(found, options);
      return true;
    }
    var from = state.currentChapter, last = state.currentPoem;
    if (hasReader && root.classList.contains("cw-reading")) closeReader();
    var target = id ? document.getElementById(id) : null;
    if (from && last) markLastRead(from, last);
    if (target) {
      target.scrollIntoView({ block: "start", behavior: "instant" });
      // The anthology has just been drawn again and may still settle (type,
      // the shelves), moving the chapter. Look once more, unless the reader
      // has taken the scroll back in the meantime.
      var moved = false;
      var mine = function () { moved = true; };
      // Listen from the next tick, so the key that closed the reader
      // (Escape) is not taken for the reader scrolling.
      window.setTimeout(function () {
        ["wheel", "touchstart", "keydown"].forEach(function (type) {
          window.addEventListener(type, mine, { once: true, passive: true });
        });
      }, 0);
      window.setTimeout(function () {
        ["wheel", "touchstart", "keydown"].forEach(function (type) { window.removeEventListener(type, mine); });
        if (!moved && !root.classList.contains("cw-reading") && window.location.hash === "#" + id &&
            Math.abs(target.getBoundingClientRect().top - (parseFloat(getComputedStyle(target).scrollMarginTop) || 0)) > 2) {
          target.scrollIntoView({ block: "start", behavior: "instant" });
        }
      }, 350);
      if (options.focus) {
        // Coming back to a chapter lands on the poem just read, so the next
        // Tab or Enter continues from there.
        var link = target.querySelector(".cw-contents__link.is-last-read");
        var heading = target.querySelector("h1, h2, h3");
        var focusable = options.focus === "last" && link ? link : heading;
        if (focusable) {
          if (focusable === heading) heading.setAttribute("tabindex", "-1");
          focusable.focus({ preventScroll: true });
        }
      }
    }
    return false;
  }

  function go(hash, options) {
    if (window.location.hash !== hash) window.history.pushState(null, "", hash);
    route(hash, options);
  }

  if (hasReader) {
    state.showChapterDesign = remembered("design");
    state.quietReading = remembered("quiet");

    /* Links to a poem or a chapter are routed here, ahead of the shared
       handlers, so each is a real history entry and a real address. */
    window.addEventListener("click", function (event) {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey ||
          event.shiftKey || event.altKey || !(event.target instanceof Element)) return;
      var link = event.target.closest('a[href^="#"]');
      if (!link || !main || !main.contains(link)) return;
      var hash = link.getAttribute("href");
      var id = hash.slice(1);
      if (!id || !document.getElementById(id)) return;
      event.preventDefault();
      var keyboard = event.detail === 0;
      if (link.hasAttribute("data-cw-back")) {
        go(hash, { focus: "last" });
      } else if (byPoem[id]) {
        go(hash, { focus: "title" });
      } else {
        go(hash, { focus: keyboard ? "heading" : null });
      }
    }, true);

    window.addEventListener("popstate", function () {
      route(window.location.hash, {});
    });

    reader.addEventListener("click", function (event) {
      if (!(event.target instanceof Element)) return;
      var step = event.target.closest("[data-cw-step]");
      if (step) {
        if (step.getAttribute("aria-disabled") === "true") return;
        var target = Number(step.getAttribute("data-cw-step")) < 0 ? state.previousPoem : state.nextPoem;
        if (target) go("#" + target.id, { focus: "keep" });
        return;
      }
      var mode = event.target.closest("[data-cw-mode]");
      if (mode) {
        var key = mode.getAttribute("data-cw-mode");
        if (key === "design") state.showChapterDesign = !state.showChapterDesign;
        else state.quietReading = !state.quietReading;
        remember(key, key === "design" ? state.showChapterDesign : state.quietReading);
        applyModes();
      }
    });

    /* The arrow keys turn the page and Escape closes the book, whenever
       focus is not in something that uses those keys itself. */
    document.addEventListener("keydown", function (event) {
      if (!root.classList.contains("cw-reading") || event.defaultPrevented ||
          event.metaKey || event.ctrlKey || event.altKey) return;
      if (event.target instanceof Element &&
          event.target.closest("input, textarea, select, [contenteditable], dialog, #drawer")) return;
      if (document.body.classList.contains("menu-open")) return;
      if (event.key === "Escape") {
        event.preventDefault();
        go("#" + state.currentChapter.id, { focus: "last" });
      } else if (event.key === "ArrowLeft" && state.previousPoem) {
        event.preventDefault();
        go("#" + state.previousPoem.id, { focus: "keep" });
      } else if (event.key === "ArrowRight" && state.nextPoem) {
        event.preventDefault();
        go("#" + state.nextPoem.id, { focus: "keep" });
      }
    });

    reader.setAttribute("aria-keyshortcuts", "ArrowLeft ArrowRight Escape");
    applyModes();
    // A shared poem address opens the reader directly.
    if (route(window.location.hash, { focus: null })) {
      // The browser makes its own jump to the fragment as the page finishes
      // loading, which would land on the poem's first line and leave the
      // way back and the settings above the fold. Aim at the reader again,
      // unless the reader has already begun to scroll.
      var touched = false;
      var claim = function () { touched = true; };
      ["wheel", "touchstart", "keydown", "pointerdown"].forEach(function (type) {
        window.addEventListener(type, claim, { once: true, passive: true });
      });
      var reaim = function () {
        if (!touched && root.classList.contains("cw-reading")) scrollToReader();
      };
      if (document.readyState === "complete") window.requestAnimationFrame(reaim);
      else window.addEventListener("load", function () { window.requestAnimationFrame(reaim); }, { once: true });
    } else {
      root.classList.remove("cw-boot-reader");
    }
  }

  /* ==========================================================
     The shelves
     ========================================================== */
  if (main) {
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
      if (original) original.click();
    });
  }

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
    pauseButton.hidden = false;
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

  if (reduce.addEventListener) {
    reduce.addEventListener("change", function () {
      if (reduce.matches) {
        running.forEach(function (animation) { animation.cancel(); });
        running.length = 0;
      }
      syncPauseButton();
    });
  }
})();
