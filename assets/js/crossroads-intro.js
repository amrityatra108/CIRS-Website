(function () {
  "use strict";
  var intro = document.querySelector("[data-crossroads-intro]");
  if (!intro) return;
  var enter = intro.querySelector("[data-crossroads-intro-enter]");
  var target = document.getElementById("crossroads-main");
  var reveal = intro.querySelector(".crossroads-intro__reveal");
  var ring = document.getElementById("ring");
  var header = document.getElementById("header");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)");
  var active = false, frame = null, x = 0, y = 0;
  var transitionFrame = null;
  var exitItems = [".crossroads-intro__mark", ".crossroads-intro__motto", ".crossroads-intro__cta"].map(function (selector) { return intro.querySelector(selector); }).filter(Boolean);
  var hint = intro.querySelector(".crossroads-intro__hint");
  var video = intro.querySelector("[data-crossroads-intro-video]");
  var opening = intro.querySelector("[data-crossroads-intro-opening]");
  var openingStarted = false, openingDone = false, openingTimer = null;
  var content = intro.querySelector(".crossroads-intro__content");
  var scrollLocked = false;
  function lockScroll(locked) {
    scrollLocked = locked;
    document.documentElement.classList.toggle("crossroads-intro-scroll-locked", locked);
    if (content) content.inert = locked;
  }
  function blockOpeningScroll(event) {
    releaseRestoredScroll();
    if (!scrollLocked) return;
    if (event.type === "keydown" && !["ArrowDown", "ArrowUp", "PageDown", "PageUp", "Home", "End", " "].includes(event.key)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
  }
  window.addEventListener("wheel", blockOpeningScroll, { passive:false, capture:true });
  window.addEventListener("touchmove", blockOpeningScroll, { passive:false, capture:true });
  window.addEventListener("keydown", blockOpeningScroll, { capture:true });
  if (!reduced.matches && (!location.hash || location.hash === "#crossroads-intro")) {
    lockScroll(true);
    openingTimer = setTimeout(finishOpening, 20000);
  } else {
    intro.removeAttribute("data-crossroads-intro-pending");
    intro.setAttribute("data-crossroads-intro-settled", "");
    if (!reduced.matches) openingDone = true;
  }
  function finishOpening() {
    if (openingDone) return;
    openingDone = true;
    clearTimeout(openingTimer);
    if (opening) opening.pause();
    intro.removeAttribute("data-crossroads-intro-opening-playing");
    intro.removeAttribute("data-crossroads-intro-pending");
    intro.removeAttribute("data-crossroads-intro-film");
    intro.setAttribute("data-crossroads-intro-settled", "");
    if (!reduced.matches && intro.getBoundingClientRect().bottom > 88) {
      intro.setAttribute("data-crossroads-intro-arriving", "");
      setTimeout(function () { intro.removeAttribute("data-crossroads-intro-arriving"); }, 1200);
    }
    lockScroll(false);
    stop();
    requestAnimationFrame(syncVideo);
  }
  function releaseRestoredScroll() {
    // Live reload / history restoration may place the reader below the movie.
    // Never retain an opening-only lock when that opening is offscreen.
    if (scrollLocked && intro.getBoundingClientRect().bottom <= 88) {
      finishOpening();
      lockScroll(false);
    }
  }
  window.addEventListener("scroll", releaseRestoredScroll, {passive:true});
  window.addEventListener("pageshow", releaseRestoredScroll);
  function syncOpening() {
    if (!opening || openingDone) return;
    if (reduced.matches) { intro.setAttribute("data-crossroads-intro-film", ""); finishOpening(); return; }
    if (!active || document.hidden) { opening.pause(); return; }
    if (document.getElementById("curtain")) return;
    if (!openingStarted) {
      openingStarted = true;
      if (!opening.getAttribute("src")) {
        opening.src = opening.getAttribute("data-src");
        opening.load();
      }
    }
    opening.muted = true;
    opening.play().catch(finishOpening);
  }
  if (opening) {
    opening.addEventListener("playing", function () {
      if (openingDone) return;
      intro.setAttribute("data-crossroads-intro-opening-playing", "");
      intro.setAttribute("data-crossroads-intro-film", "");
      if (video) video.pause();
      primeAmbientVideo(false);
      clearTimeout(openingTimer);
      openingTimer = setTimeout(finishOpening, 12000);
    });
    opening.addEventListener("ended", finishOpening);
    opening.addEventListener("error", finishOpening);
    var openingObserver = new MutationObserver(function () {
      if (!document.getElementById("curtain")) { openingObserver.disconnect(); syncOpening(); }
    });
    openingObserver.observe(document.body, { childList:true, subtree:true });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !openingDone) finishOpening();
    });
  }
  intro.addEventListener("click", function () {
    if (!openingDone && intro.hasAttribute("data-crossroads-intro-pending")) finishOpening();
  });
  function primeAmbientVideo(playNow) {
    if (!video || reduced.matches || getComputedStyle(reveal).display === "none") return;
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
    if (!active || document.hidden || reduced.matches || getComputedStyle(reveal).display === "none" || (opening && !openingDone) || intro.hasAttribute("data-crossroads-intro-film")) { video.pause(); return; }
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
    // Leave a visible central window into the film when the pointer is absent.
    reveal.style.removeProperty("--crossroads-intro-x");
    reveal.style.removeProperty("--crossroads-intro-y");
    intro.toggleAttribute("data-crossroads-intro-lit", active && !reduced.matches && !document.hidden);
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
      if (header) header.classList.toggle("crossroads-intro-header", active);
      if (ring) ring.classList.toggle("crossroads-intro-cursor-muted", active);
      intro.toggleAttribute("data-crossroads-intro-active", active && !document.hidden);
      if (!active) { stop(); stopTransition(); paintTransition(); }
      else { stop(); queueTransition(); }
    }).observe(intro);
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
