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
  var exitItems = [".crossroads-intro__eyebrow", ".crossroads-intro__pen", ".crossroads-intro-title-art", ".crossroads-intro__sanskrit", ".crossroads-intro__tagline", ".crossroads-intro__cta"].map(function (selector) { return intro.querySelector(selector); }).filter(Boolean);
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
    if (!reduced.matches) openingDone = true;
  }
  function finishOpening() {
    if (openingDone) return;
    openingDone = true;
    clearTimeout(openingTimer);
    if (opening) opening.pause();
    intro.removeAttribute("data-crossroads-intro-opening-playing");
    intro.removeAttribute("data-crossroads-intro-pending");
    setTimeout(function () { lockScroll(false); }, reduced.matches ? 0 : 1500);
    syncVideo();
  }
  function syncOpening() {
    if (!opening || openingDone) return;
    if (reduced.matches) { intro.setAttribute("data-crossroads-intro-film", ""); finishOpening(); return; }
    if (!active || document.hidden) { opening.pause(); return; }
    if (document.getElementById("curtain")) return;
    if (!openingStarted) {
      openingStarted = true;
      opening.src = opening.getAttribute("data-src");
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
      if (event.key === "Escape" && intro.hasAttribute("data-crossroads-intro-opening-playing")) finishOpening();
    });
  }
  function syncVideo() {
    syncOpening();
    if (!video) return;
    if (!active || document.hidden || reduced.matches || (opening && !openingDone) || intro.hasAttribute("data-crossroads-intro-film")) { video.pause(); return; }
    if (!video.getAttribute("src")) video.src = video.getAttribute("data-src");
    video.muted = true;
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
    if (ring) ring.classList.remove("crossroads-intro-cursor-muted");
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
      intro.toggleAttribute("data-crossroads-intro-active", active && !document.hidden);
      if (!active) { stop(); stopTransition(); paintTransition(); }
      else { stop(); queueTransition(); }
    }).observe(intro);
  }

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
    target.scrollIntoView({ behavior:reduced.matches ? "instant" : "smooth", block:"start" });
  }, true);
}());
