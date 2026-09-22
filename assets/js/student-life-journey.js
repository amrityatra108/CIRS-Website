(function () {
  "use strict";

  var root = document.querySelector(".sj-day");
  if (!root) return;

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasGSAP = typeof window.gsap !== "undefined";
  var hasScrollTrigger = hasGSAP && typeof window.ScrollTrigger !== "undefined";
  var journey = root.querySelector(".sj-journey");
  var sticky = root.querySelector(".sj-journey__sticky");
  var scenes = Array.prototype.slice.call(root.querySelectorAll(".sj-scenes img"));
  var stars = root.querySelector(".sj-stars");
  var clock = root.querySelector(".sj-clock span");
  var period = root.querySelector(".sj-clock small");
  var range = root.querySelector(".sj-chapter small");
  var title = root.querySelector(".sj-chapter h3");
  var copy = root.querySelector(".sj-chapter p");
  var school = root.querySelector(".sj-school");
  var current = root.querySelector(".sj-controls b");
  var total = root.querySelector(".sj-controls i");
  var index = root.querySelector(".sj-index");
  var status = root.querySelector("[data-day-status]");
  var trackFill = root.querySelector(".sj-track span");
  var trackSun = root.querySelector(".sj-track i");
  var timeline = null;
  var mode = "senior";
  var active = -1;

  function scheduleArticles(name) {
    return Array.prototype.slice.call(root.querySelectorAll('[data-schedule-panel="' + name + '"] article'));
  }

  function scheduleData(name) {
    return scheduleArticles(name).map(function (article) {
      return {
        time: article.dataset.time,
        period: article.dataset.period,
        range: article.dataset.range,
        photo: Number(article.dataset.photo),
        color: article.dataset.color,
        title: article.querySelector("h4").textContent,
        copy: article.querySelector("p").textContent
      };
    });
  }

  function updateSchedulePanels() {
    root.querySelectorAll("[data-schedule-panel]").forEach(function (panel) {
      var selected = panel.dataset.schedulePanel === mode;
      panel.classList.toggle("is-active", selected);
      panel.toggleAttribute("hidden", !selected && document.documentElement.classList.contains("sj-enhanced"));
    });
  }

  function renderIndex() {
    var data = scheduleData(mode);
    index.innerHTML = data.map(function (chapter, chapterIndex) {
      return '<li><button type="button" data-jump="' + chapterIndex + '" aria-label="Go to ' + chapter.time + ' ' + chapter.period + '">' + chapter.time + "</button></li>";
    }).join("");
    total.textContent = String(data.length);
  }

  function showChapter(next, announce) {
    var data = scheduleData(mode);
    var nextIndex = Math.max(0, Math.min(data.length - 1, next));
    if (nextIndex === active) return;
    active = nextIndex;
    var chapter = data[active];
    clock.textContent = chapter.time;
    period.textContent = chapter.period;
    range.textContent = chapter.range;
    title.textContent = chapter.title;
    copy.textContent = chapter.copy;
    current.textContent = String(active + 1);
    index.querySelectorAll("button").forEach(function (button, buttonIndex) {
      if (buttonIndex === active) button.setAttribute("aria-current", "true");
      else button.removeAttribute("aria-current");
    });
    if (announce) status.textContent = chapter.time + " " + chapter.period + ", " + chapter.title + ". " + chapter.copy;
  }

  function destroyTimeline() {
    if (!timeline) return;
    if (timeline.scrollTrigger) timeline.scrollTrigger.kill();
    timeline.kill();
    timeline = null;
  }

  function buildTimeline() {
    destroyTimeline();
    document.documentElement.classList.remove("sj-motion");
    if (!hasScrollTrigger || reduced || window.innerWidth <= 800) return;
    document.documentElement.classList.add("sj-motion");

    gsap.registerPlugin(ScrollTrigger);
    var data = scheduleData(mode);
    active = -1;
    gsap.set(scenes, { autoAlpha:0, xPercent:100 });
    gsap.set(scenes[0], { autoAlpha:.68, xPercent:0 });
    gsap.set(trackFill, { scaleX:0 });
    gsap.set(trackSun, { x:0, scale:.82, backgroundColor:"#d5a84b", boxShadow:"0 0 8px rgba(213,168,75,.4)", "--moon-cover":0 });
    gsap.set(stars, { autoAlpha:0 });

    timeline = gsap.timeline({
      defaults:{ ease:"none" },
      scrollTrigger:{
        trigger:journey,
        start:"top top",
        end:"bottom bottom",
        scrub:.55,
        invalidateOnRefresh:true,
        onUpdate:function (self) {
          showChapter(Math.round(self.progress * (data.length - 1)), false);
        }
      }
    });

    data.forEach(function (chapter, chapterIndex) {
      var position = chapterIndex;
      timeline.addLabel("chapter-" + chapterIndex, position);
      timeline.to(sticky, { backgroundColor:chapter.color, duration:1 }, position);
      if (chapterIndex > 0) {
        timeline.to(scenes[chapterIndex - 1], { xPercent:-100, autoAlpha:.28, duration:.9 }, position - .35);
        timeline.to(scenes[chapter.photo], { xPercent:0, autoAlpha:.68, duration:.9 }, position - .35);
      }
    });
    timeline.to(trackFill, { scaleX:1, duration:data.length - 1 }, 0);
    timeline.to(trackSun, { x:function () { return root.querySelector(".sj-track").clientWidth; }, duration:data.length - 1 }, 0);
    timeline.to(trackSun, { scale:1.24, backgroundColor:"#ffe7a0", boxShadow:"0 0 10px 3px rgba(255,214,104,.78)", duration:(data.length - 1) * .42 }, 0);
    timeline.to(trackSun, { scale:1, backgroundColor:"#e99a52", boxShadow:"0 0 8px 2px rgba(225,111,52,.55)", duration:(data.length - 1) * .3 }, (data.length - 1) * .42);
    timeline.to(trackSun, { scale:1.08, backgroundColor:"#f1eee1", boxShadow:"0 0 8px 2px rgba(211,224,255,.45)", "--moon-cover":1, duration:(data.length - 1) * .18 }, (data.length - 1) * .78);
    timeline.to(stars, { autoAlpha:1, duration:(data.length - 1) * .18 }, (data.length - 1) * .78);
    timeline.duration(data.length - 1);
    showChapter(0, false);
    requestAnimationFrame(function () { ScrollTrigger.refresh(); });
  }

  function seekChapter(chapterIndex, announce) {
    var data = scheduleData(mode);
    var targetIndex = Math.max(0, Math.min(data.length - 1, chapterIndex));
    if (!timeline || !timeline.scrollTrigger) {
      showChapter(targetIndex, announce);
      return;
    }
    var trigger = timeline.scrollTrigger;
    var destination = trigger.start + (trigger.end - trigger.start) * (targetIndex / (data.length - 1));
    var event = new CustomEvent("cirs-section-scroll", { cancelable:true, detail:{ top:destination, duration:.65 } });
    window.dispatchEvent(event);
    if (!event.defaultPrevented) window.scrollTo({ top:destination, behavior:reduced ? "auto" : "smooth" });
    showChapter(targetIndex, announce);
  }

  function selectSchedule(nextMode, announce) {
    mode = nextMode;
    root.querySelectorAll("[data-schedule]").forEach(function (button) {
      var selected = button.dataset.schedule === mode;
      button.classList.toggle("is-active", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
    school.textContent = mode === "senior" ? "Senior School · Grades IX–XII" : "Junior School · Grades V–VIII";
    updateSchedulePanels();
    renderIndex();
    buildTimeline();
    showChapter(0, announce);
  }

  function setupRailControls() {
    document.querySelectorAll("[data-rail-controls]").forEach(function (controls) {
      var rail = document.getElementById(controls.dataset.railControls);
      var count = controls.querySelector("p span");
      if (!rail) return;
      function items() { return Array.prototype.slice.call(rail.querySelectorAll("figure")); }
      function nearestIndex() {
        var railLeft = rail.getBoundingClientRect().left;
        var distances = items().map(function (item) { return Math.abs(item.getBoundingClientRect().left - railLeft); });
        return distances.indexOf(Math.min.apply(Math, distances));
      }
      function updateCount() { count.textContent = String(nearestIndex() + 1); }
      function move(direction) {
        var list = items();
        var nextIndex = Math.max(0, Math.min(list.length - 1, nearestIndex() + direction));
        list[nextIndex].scrollIntoView({ behavior:reduced ? "auto" : "smooth", block:"nearest", inline:"center" });
        count.textContent = String(nextIndex + 1);
      }
      controls.querySelector("[data-rail-prev]").addEventListener("click", function () { move(-1); });
      controls.querySelector("[data-rail-next]").addEventListener("click", function () { move(1); });
      rail.addEventListener("scroll", updateCount, { passive:true });
      rail.addEventListener("keydown", function (event) {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        move(event.key === "ArrowRight" ? 1 : -1);
      });
    });
  }

  document.documentElement.classList.add("sj-enhanced");
  root.addEventListener("click", function (event) {
    var button = event.target.closest("button");
    if (!button) return;
    if (button.dataset.schedule) selectSchedule(button.dataset.schedule, true);
    else if (button.hasAttribute("data-prev")) seekChapter(active - 1, true);
    else if (button.hasAttribute("data-next")) seekChapter(active + 1, true);
    else if (button.dataset.jump !== undefined) seekChapter(Number(button.dataset.jump), true);
  });
  index.addEventListener("keydown", function (event) {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight" && event.key !== "Home" && event.key !== "End") return;
    event.preventDefault();
    var length = scheduleData(mode).length;
    var next = event.key === "Home" ? 0 : event.key === "End" ? length - 1 : active + (event.key === "ArrowRight" ? 1 : -1);
    seekChapter(next, true);
    var target = index.querySelectorAll("button")[Math.max(0, Math.min(length - 1, next))];
    if (target) target.focus({ preventScroll:true });
  });
  setupRailControls();
  selectSchedule("senior", false);
  window.addEventListener("resize", function () {
    window.clearTimeout(window.__sjResizeTimer);
    window.__sjResizeTimer = window.setTimeout(buildTimeline, 220);
  });
}());
