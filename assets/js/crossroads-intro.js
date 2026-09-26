(function () {
  "use strict";
  var intro = document.querySelector("[data-crossroads-intro]");
  if (!intro) return;
  if (intro._crossroadsIntroInitialized) return;
  intro._crossroadsIntroInitialized = true;
  var enter = intro.querySelector("[data-crossroads-intro-enter]");
  var target = document.getElementById("crossroads-main");
  var reveal = intro.querySelector(".crossroads-intro__reveal");
  var ring = document.getElementById("ring");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)");
  var active = false, frame = null, x = 0, y = 0;
  var transitionFrame = null;
  var exitItems = [".crossroads-intro__mark", ".crossroads-intro__motto", ".crossroads-intro__cta"].map(function (selector) { return intro.querySelector(selector); }).filter(Boolean);
  var hint = intro.querySelector(".crossroads-intro__hint");
  var video = intro.querySelector("[data-crossroads-intro-video]");
  var opening = intro.querySelector("[data-crossroads-intro-opening]");
  var skip = intro.querySelector("[data-crossroads-intro-skip]");
  var connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  var navigationEntry = performance.getEntriesByType && performance.getEntriesByType("navigation")[0];
  var historyReturn = navigationEntry && navigationEntry.type === "back_forward";
  var openingStarted = false, openingDone = false, openingTimer = null, finishTimer = null;
  var openingState = "pending";
  // performance.now() is relative to navigation. A late deferred script must
  // never begin a fresh lock after the visitor has already waited six seconds.
  var intentReadyAt = 2000;
  var lockDeadlineAt = 6000;
  var content = intro.querySelector(".crossroads-intro__content");
  var scrollLocked = false;
  var focusAfterSkip = false;
  var touchOpeningX = 0, touchOpeningY = 0;
  function slowConnection() {
    return !!(connection && (connection.saveData || ["slow-2g", "2g", "3g"].includes(connection.effectiveType)));
  }
  function lockScroll(locked) {
    scrollLocked = locked;
    document.documentElement.classList.toggle("crossroads-intro-scroll-locked", locked);
    intro.toggleAttribute("data-crossroads-intro-locked", locked);
    if (content) content.inert = locked;
  }
  function removeLockListeners() {
    window.removeEventListener("wheel", onOpeningWheel, true);
    window.removeEventListener("touchstart", onOpeningTouchStart, true);
    window.removeEventListener("touchmove", onOpeningTouchMove, true);
    window.removeEventListener("keydown", onOpeningScrollKey, true);
  }
  function onOpeningWheel(event) {
    if (!scrollLocked || event.ctrlKey || Math.abs(event.deltaY) < 4 || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
    if (performance.now() >= intentReadyAt) { finishOpening(false, true); return; }
    event.preventDefault();
    event.stopImmediatePropagation();
  }
  function onOpeningTouchStart(event) {
    if (event.touches.length !== 1) return;
    touchOpeningX = event.touches[0].clientX;
    touchOpeningY = event.touches[0].clientY;
  }
  function onOpeningTouchMove(event) {
    if (!scrollLocked || event.touches.length !== 1) return;
    var dx = touchOpeningX - event.touches[0].clientX;
    var dy = touchOpeningY - event.touches[0].clientY;
    if (performance.now() >= intentReadyAt && Math.abs(dy) >= 30 && Math.abs(dy) > Math.abs(dx)) {
      finishOpening(false, true);
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
  }
  function onOpeningScrollKey(event) {
    if (!scrollLocked || !["ArrowDown", "ArrowUp", "PageDown", "PageUp", "Home", "End", " "].includes(event.key)) return;
    if (event.key === " " && event.target.closest("a, button, input, textarea, select, [contenteditable=true]")) return;
    if (event.target.closest("input, textarea, select, [contenteditable=true]")) return;
    if (performance.now() >= intentReadyAt) { finishOpening(false, true); return; }
    event.preventDefault();
    event.stopImmediatePropagation();
  }
  function removeOpeningListeners() {
    removeLockListeners();
    document.removeEventListener("keydown", onOpeningEscape, true);
    intro.removeEventListener("click", onIntroClick);
    if (skip) skip.removeEventListener("click", onSkipClick);
    if (opening) {
      opening.removeEventListener("playing", onOpeningPlaying);
      opening.removeEventListener("ended", finishOpening);
      opening.removeEventListener("error", onOpeningError);
    }
    if (connection && connection.removeEventListener) connection.removeEventListener("change", onConnectionChange);
    reduced.removeEventListener("change", onMotionChange);
    document.removeEventListener("visibilitychange", onOpeningVisibility);
    window.removeEventListener("pagehide", onOpeningPageHide);
  }
  function settleOpeningVisual() {
    clearTimeout(finishTimer);
    finishTimer = null;
    intro.removeAttribute("data-crossroads-intro-film");
    intro.removeAttribute("data-crossroads-intro-finishing");
    if (focusAfterSkip && enter) {
      focusAfterSkip = false;
      enter.focus({preventScroll:true});
    }
    requestAnimationFrame(syncVideo);
  }
  function finishOpening(immediate, quick) {
    if (openingState === "complete") {
      if (immediate === true) settleOpeningVisual();
      return;
    }
    var hadFilm = intro.hasAttribute("data-crossroads-intro-pending") || intro.hasAttribute("data-crossroads-intro-film");
    openingState = "complete";
    openingDone = true;
    clearTimeout(openingTimer);
    openingTimer = null;
    lockScroll(false);
    removeOpeningListeners();
    if (opening) opening.pause();
    intro.removeAttribute("data-crossroads-intro-opening-playing");
    intro.removeAttribute("data-crossroads-intro-pending");
    intro.setAttribute("data-crossroads-intro-settled", "");
    if (immediate === true || reduced.matches || !hadFilm) settleOpeningVisual();
    else {
      intro.setAttribute("data-crossroads-intro-finishing", "");
      finishTimer = setTimeout(settleOpeningVisual, 240);
    }
    if (immediate !== true && !quick && !reduced.matches && hadFilm && intro.getBoundingClientRect().bottom > 88) {
      intro.setAttribute("data-crossroads-intro-arriving", "");
      setTimeout(function () { intro.removeAttribute("data-crossroads-intro-arriving"); }, 1200);
    }
    stop();
  }
  function releaseOpening() {
    if (openingState === "released" || openingState === "complete") return;
    if (openingState !== "active" || document.hidden) { finishOpening(false, true); return; }
    clearTimeout(openingTimer);
    openingTimer = null;
    lockScroll(false);
    removeLockListeners();
    intro.removeAttribute("data-crossroads-intro-pending");
    openingState = "released";
  }
  function onOpeningEscape(event) {
    if (event.key !== "Escape" || openingState === "complete") return;
    event.preventDefault();
    if (document.activeElement === skip) focusAfterSkip = true;
    finishOpening(false, true);
  }
  function onSkipClick(event) {
    if (event.detail === 0 && document.activeElement === skip) focusAfterSkip = true;
    finishOpening(false, true);
  }
  function onIntroClick(event) {
    if (openingState !== "complete" && !event.target.closest("[data-crossroads-intro-enter]")) finishOpening(false, true);
  }
  function onOpeningPlaying() {
    if (openingState === "complete") return;
    if (openingState === "pending") openingState = "active";
    intro.setAttribute("data-crossroads-intro-opening-playing", "");
    intro.setAttribute("data-crossroads-intro-film", "");
    if (video) video.pause();
  }
  function onOpeningError() { finishOpening(false, true); }
  function onConnectionChange() { if (slowConnection()) finishOpening(true); }
  function onMotionChange() { if (reduced.matches) finishOpening(true); }
  function onOpeningVisibility() { if (document.hidden) finishOpening(true); }
  function onOpeningPageHide() { finishOpening(true); }
  if (!document.hidden && !historyReturn && performance.now() < lockDeadlineAt && !reduced.matches && !slowConnection() && (!location.hash || location.hash === "#crossroads-intro")) {
    lockScroll(true);
    window.addEventListener("wheel", onOpeningWheel, {passive:false, capture:true});
    window.addEventListener("touchstart", onOpeningTouchStart, {passive:true, capture:true});
    window.addEventListener("touchmove", onOpeningTouchMove, {passive:false, capture:true});
    window.addEventListener("keydown", onOpeningScrollKey, {capture:true});
    document.addEventListener("keydown", onOpeningEscape, {capture:true});
    intro.addEventListener("click", onIntroClick);
    if (skip) skip.addEventListener("click", onSkipClick);
    if (opening) {
      opening.addEventListener("playing", onOpeningPlaying);
      opening.addEventListener("ended", finishOpening);
      opening.addEventListener("error", onOpeningError);
    }
    if (connection && connection.addEventListener) connection.addEventListener("change", onConnectionChange);
    reduced.addEventListener("change", onMotionChange);
    document.addEventListener("visibilitychange", onOpeningVisibility);
    window.addEventListener("pagehide", onOpeningPageHide);
    openingTimer = setTimeout(releaseOpening, Math.max(0, lockDeadlineAt - performance.now()));
  } else finishOpening(true);
  function releaseRestoredScroll() {
    // Live reload / history restoration may place the reader below the movie.
    // Never retain an opening-only lock when that opening is offscreen.
    if (scrollLocked && intro.getBoundingClientRect().bottom <= 88) {
      finishOpening(true);
    }
  }
  window.addEventListener("scroll", releaseRestoredScroll, {passive:true});
  window.addEventListener("pageshow", function (event) {
    if (event.persisted) finishOpening(true);
    else releaseRestoredScroll();
  });
  function syncOpening() {
    if (!opening || openingDone) return;
    if (reduced.matches || slowConnection()) { finishOpening(true); return; }
    if (!active || document.hidden) { opening.pause(); return; }
    if (!openingStarted) {
      openingStarted = true;
      // Match the same desktop threshold as the site's other optimized films.
      // Select only after the intro qualifies, so reduced motion and Save-Data
      // do not trigger a film request while the page is parsed.
      opening.src = window.matchMedia("(min-width: 768px) and (min-height: 501px)").matches ?
        opening.getAttribute("data-src") : opening.getAttribute("data-mobile-src");
      opening.load();
    }
    opening.muted = true;
    var playback = opening.play();
    if (playback) playback.catch(function () { finishOpening(false, true); });
  }
  function primeAmbientVideo(playNow) {
    if (!video || reduced.matches || slowConnection() || getComputedStyle(reveal).display === "none") return;
    if (!video.getAttribute("src")) {
      video.src = video.getAttribute("data-src");
      video.load();
    }
    video.muted = true;
    if (playNow && active && !document.hidden) {
      var promise = video.play();
      if (promise) promise.catch(function () { /* The still remains a complete fallback. */ });
    }
  }
  function syncVideo() {
    syncOpening();
    if (!video) return;
    if (!active || document.hidden || reduced.matches || slowConnection() || getComputedStyle(reveal).display === "none" || (opening && !openingDone) || intro.hasAttribute("data-crossroads-intro-film")) { video.pause(); return; }
    primeAmbientVideo(false);
    var playing = video.play();
    if (playing) playing.catch(function () { /* Keep the still visible when autoplay is unavailable. */ });
  }
  if (video) {
    video.addEventListener("playing", function () {
      intro.setAttribute("data-crossroads-intro-video-ready", "");
    });
    video.addEventListener("error", function () { intro.removeAttribute("data-crossroads-intro-video-ready"); });
  }
  function resetExit() {
    intro.style.removeProperty("--crossroads-intro-exit");
    exitItems.forEach(function (item) { item.style.removeProperty("opacity"); });
    if (hint) hint.style.removeProperty("opacity");
  }

  function paintTransition() {
    transitionFrame = null;
    if (reduced.matches) {
      resetExit();
      return;
    }
    var rect = intro.getBoundingClientRect();
    var nextText = target && target.parentElement.querySelector(".crhero__inner");
    var available = nextText ? nextText.getBoundingClientRect().top - rect.top - window.innerHeight - 48 : rect.height * 0.4;
    var distance = Math.max(1, Math.min(rect.height * 0.48, Math.max(rect.height * 0.12, available)));
    var progress = Math.max(0, Math.min(1, -rect.top / distance));
    var eased = progress * progress * (3 - 2 * progress);
    intro.style.setProperty("--crossroads-intro-exit", eased.toFixed(4));
    exitItems.forEach(function (item, index) {
      var step = Math.max(0, Math.min(1, progress * exitItems.length - index));
      item.style.opacity = (1 - step * step * (3 - 2 * step)).toFixed(4);
    });
    if (hint) hint.style.opacity = exitItems[exitItems.length - 1].style.opacity;
  }
  function queueTransition() {
    if (!active || document.hidden || reduced.matches || transitionFrame !== null) return;
    transitionFrame = window.requestAnimationFrame(paintTransition);
  }
  function stopTransition() {
    if (transitionFrame !== null) window.cancelAnimationFrame(transitionFrame);
    transitionFrame = null;
  }
  window.addEventListener("scroll", queueTransition, { passive:true });
  window.addEventListener("resize", queueTransition, { passive:true });
  reduced.addEventListener("change", function () {
    syncVideo();
    stopTransition();
    if (reduced.matches) resetExit();
    else queueTransition();
  });
  document.addEventListener("visibilitychange", function () {
    syncVideo();
    intro.toggleAttribute("data-crossroads-intro-active", active && !document.hidden);
    if (document.hidden) stopTransition();
    else queueTransition();
  });

  function stop() {
    if (frame !== null) window.cancelAnimationFrame(frame);
    frame = null;
    // Keep the finished title card still until the pointer reveals the film.
    reveal.style.removeProperty("--crossroads-intro-x");
    reveal.style.removeProperty("--crossroads-intro-y");
    intro.removeAttribute("data-crossroads-intro-lit");
    if (ring) ring.classList.toggle("crossroads-intro-cursor-muted", active);
  }
  function paint() {
    frame = null;
    if (!active || reduced.matches || document.hidden) return;
    var rect = intro.getBoundingClientRect();
    // Keep pointer updates on the image, outside the title/text subtree.
    reveal.style.setProperty("--crossroads-intro-x", (x - rect.left) + "px");
    reveal.style.setProperty("--crossroads-intro-y", (y - rect.top) + "px");
    if (!intro.hasAttribute("data-crossroads-intro-lit")) intro.setAttribute("data-crossroads-intro-lit", "");
    if (ring && fine.matches) ring.classList.add("crossroads-intro-cursor-muted");
  }
  intro.addEventListener("pointermove", function (event) {
    if (!active || reduced.matches) return;
    x = event.clientX;
    y = event.clientY;
    if (frame === null) frame = window.requestAnimationFrame(paint);
  }, { passive:true });
  intro.addEventListener("pointerdown", function (event) {
    if (!active || reduced.matches || event.pointerType !== "touch") return;
    x = event.clientX; y = event.clientY;
    if (frame === null) frame = window.requestAnimationFrame(paint);
  }, { passive:true });
  intro.addEventListener("pointercancel", stop);
  intro.addEventListener("pointerleave", stop);
  document.addEventListener("visibilitychange", stop);
  reduced.addEventListener("change", stop);
  fine.addEventListener("change", stop);
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      active = entries[0].isIntersecting;
      syncVideo();
      if (ring) ring.classList.toggle("crossroads-intro-cursor-muted", active);
      intro.toggleAttribute("data-crossroads-intro-active", active && !document.hidden);
      if (!active) {
        if (openingState === "released") finishOpening(true);
        stop(); stopTransition(); paintTransition();
      }
      else { stop(); queueTransition(); }
    }).observe(intro);
  } else {
    active = true;
    syncVideo();
  }

  // Step through the first three sections; leave the remaining page scrolling normally.
  var sectionMoving = false, nativeSectionScroll = false, sectionTimer = null, wheelIntent = 0, wheelTime = 0;
  var touchStartX = 0, touchStartY = 0;
  function sectionDestination(direction) {
    if (scrollLocked || !target) return null;
    var sections = [intro, target, document.getElementById("statement")].filter(Boolean);
    var positions = sections.map(function (section) {
      var margin = parseFloat(getComputedStyle(section).scrollMarginTop) || 0;
      return Math.max(0, section.getBoundingClientRect().top + window.scrollY - margin);
    });
    var y = window.scrollY;
    if (y > positions[positions.length - 1] + 4) return null;
    // Tall mobile sections must remain fully readable before advancing.
    var current = 0;
    for (var k = 0; k < positions.length; k++) if (positions[k] <= y + 4) current = k;
    var currentSection = sections[current] === target ? target.parentElement : sections[current];
    var readableEnd = currentSection.getBoundingClientRect().bottom + y - window.innerHeight;
    if (direction > 0 && readableEnd > y + 4) return null;
    if (direction < 0 && readableEnd > positions[current] + 4 && y > positions[current] + 4) return null;
    if (direction > 0) {
      for (var i = 0; i < sections.length; i++) if (positions[i] > y + 4) return sections[i];
    } else if (direction < 0) {
      for (var j = sections.length - 1; j >= 0; j--) if (positions[j] < y - 4) return sections[j];
    }
    return null;
  }
  function settleSection() {
    sectionMoving = false;
    wheelIntent = 0;
    clearTimeout(sectionTimer);
  }
  function moveSection(destination) {
    sectionMoving = true;
    wheelIntent = 0;
    clearTimeout(sectionTimer);
    var margin = parseFloat(getComputedStyle(destination).scrollMarginTop) || 0;
    var top = Math.max(0, destination.getBoundingClientRect().top + window.scrollY - margin);
    var request = new CustomEvent("crossroads-intro-scroll", {
      cancelable:true,
      detail:{top:top, immediate:reduced.matches, onComplete:settleSection}
    });
    nativeSectionScroll = window.dispatchEvent(request);
    if (nativeSectionScroll) {
      window.scrollTo({top:top, behavior:reduced.matches ? "instant" : "smooth"});
    }
    // Completion normally unlocks immediately; this only covers interrupted motion.
    sectionTimer = setTimeout(settleSection, reduced.matches ? 100 : 1100);
  }
  window.addEventListener("wheel", function (event) {
    if (event.ctrlKey || Math.abs(event.deltaX) > Math.abs(event.deltaY) ||
        event.target.closest("dialog, .drawer, input, textarea, select, [contenteditable=true]")) return;
    if (sectionMoving) { event.preventDefault(); event.stopImmediatePropagation(); return; }
    var destination = sectionDestination(event.deltaY);
    if (!sectionMoving && !destination) return;
    event.preventDefault(); event.stopImmediatePropagation();
    if (sectionMoving) return;
    if (event.deltaY !== 0) moveSection(destination);
  }, {passive:false, capture:true});
  window.addEventListener("touchstart", function (event) {
    if (event.touches.length !== 1) return;
    touchStartX = event.touches[0].clientX;
    touchStartY = event.touches[0].clientY;
  }, {passive:true});
  window.addEventListener("touchmove", function (event) {
    if (scrollLocked || event.touches.length !== 1 || event.target.closest("dialog, .drawer")) return;
    var dx = touchStartX - event.touches[0].clientX;
    var dy = touchStartY - event.touches[0].clientY;
    if (Math.abs(dx) > Math.abs(dy)) return;
    var destination = sectionDestination(dy);
    if (!sectionMoving && !destination) return;
    event.preventDefault(); event.stopImmediatePropagation();
    if (!sectionMoving && Math.abs(dy) >= 40) moveSection(destination);
  }, {passive:false, capture:true});
  window.addEventListener("keydown", function (event) {
    if (event.target.closest("a, button, input, textarea, select, [contenteditable=true], dialog, .drawer")) return;
    var direction = event.key === "PageDown" || (event.key === " " && !event.shiftKey) ? 1 :
      event.key === "PageUp" || (event.key === " " && event.shiftKey) ? -1 : 0;
    if (!direction) return;
    var destination = sectionDestination(direction);
    if (destination) { event.preventDefault(); event.stopImmediatePropagation(); moveSection(destination); }
  }, {capture:true});
  window.addEventListener("pageshow", settleSection);
  window.addEventListener("scrollend", function () { if (sectionMoving && nativeSectionScroll) settleSection(); });

  // Capture only this CTA, ahead of the shared site's anchor listener.
  // Preserve native hash/history semantics and move keyboard focus with it.
  intro.addEventListener("click", function (event) {
    if (!event.target.closest("[data-crossroads-intro-enter]") || !target ||
        event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    event.stopPropagation();
    if (opening && !openingDone) finishOpening();
    if (window.location.hash !== enter.hash) window.history.pushState(null, "", enter.hash);
    target.focus({ preventScroll:true });
    moveSection(target);
  }, true);
}());
