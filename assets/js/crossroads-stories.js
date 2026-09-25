(function () {
  "use strict";
  var section = document.querySelector("[data-crossroads-stories]");
  if (!section) return;
  var stack = section.querySelector(".crossroads-stories__stack");
  var covers = stack ? Array.from(stack.querySelectorAll("a")) : [];
  var selected = stack && stack.querySelector(".crossroads-stories__front");
  var pointerDownCover = null;
  var hoveredCover = null;
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  var rearSlot = {1:2,2:4,3:6,4:5,5:3,6:1};
  function clearHover() {
    hoveredCover = null;
    stack.removeAttribute("data-crossroads-stories-hovering");
    covers.forEach(function (item) { item.style.removeProperty("--crossroads-stories-hover-shift"); });
  }
  function showHover(cover) {
    if (!finePointer.matches || hoveredCover === cover) return;
    clearHover();
    hoveredCover = cover;
    var rect = cover.getBoundingClientRect();
    var center = rect.left + rect.width / 2;
    var width = cover.offsetWidth;
    var distanceLimit = width * 3.2;
    var maxShift = Math.min(44, width * .18);
    covers.forEach(function (item) {
      if (item === cover || item === selected) return;
      var itemRect = item.getBoundingClientRect();
      var offset = itemRect.left + itemRect.width / 2 - center;
      var amount = Math.round(maxShift * Math.max(0, 1 - Math.abs(offset) / distanceLimit));
      if (amount > 1) item.style.setProperty("--crossroads-stories-hover-shift", (offset < 0 ? -amount : amount) + "px");
    });
    stack.setAttribute("data-crossroads-stories-hovering", "");
  }
  function selectCover(cover) {
    if (!cover || cover === selected || !covers.includes(cover)) return;
    clearHover();
    selected = cover;
    var selectedIndex = covers.indexOf(selected);
    covers.forEach(function (item,index) {
      Array.from(item.classList).forEach(function (name) { if (name === "crossroads-stories__front" || name === "crossroads-stories__rear" || name.indexOf("crossroads-stories__rear--") === 0) item.classList.remove(name); });
      if (item === selected) item.classList.add("crossroads-stories__front");
      else {
        var delta = (index-selectedIndex+covers.length)%covers.length;
        item.classList.add("crossroads-stories__rear", "crossroads-stories__rear--" + rearSlot[delta]);
      }
    });
  }
  if (stack) {
    covers.forEach(function (cover) {
      cover.addEventListener("pointerenter", function (event) { if (event.pointerType !== "touch") showHover(cover); });
      cover.addEventListener("pointerleave", function () { if (hoveredCover === cover) clearHover(); });
    });
    stack.addEventListener("pointerleave", clearHover);
    finePointer.addEventListener("change", function () { if (!finePointer.matches) clearHover(); });
    stack.addEventListener("pointerdown",function(event){pointerDownCover=event.target.closest("a");},{passive:true});
    stack.addEventListener("focusin", function (event) {
      var cover=event.target.closest("a");
      if (cover !== pointerDownCover) selectCover(cover);
    });
    stack.addEventListener("click", function (event) {
      var cover=event.target.closest("a");
      if (cover && cover !== selected) {
        event.preventDefault();
        selectCover(cover);
        cover.focus({preventScroll:true});
      }
      pointerDownCover=null;
    });
    stack.addEventListener("pointercancel",function(){pointerDownCover=null;});
  }
  if (!window.gsap || !("IntersectionObserver" in window)) return;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (reduced.matches) return;
  var media = section.querySelector(".crossroads-stories__media");
  var left = section.querySelector(".crossroads-stories__left");
  var right = section.querySelector(".crossroads-stories__right");
  var rears = section.querySelectorAll(".crossroads-stories__rear");
  var number = section.querySelector("[data-crossroads-stories-number]");
  var total = Number(number.textContent), played = false, timeline = null;
  if (!media) return;
  function initial() {
    var desktop = matchMedia("(min-width:768px)").matches;
    var distance = desktop ? 24 : 0;
    gsap.set(left, {x:distance}); gsap.set(right, {x:-distance});
    gsap.set(media, {clipPath:"inset(0 50% 0 50%)"});
    gsap.set(rears, {opacity:0});
  }
  function finalState() {
    if (timeline) { timeline.eventCallback("onComplete", null); timeline.progress(1).kill(); timeline = null; }
    played = true; observer.disconnect();
    gsap.set([left,right,media], {clearProps:"transform,clipPath"});
    gsap.set(rears, {clearProps:"opacity"});
    number.textContent = String(total);
  }
  function play() {
    if (played) return;
    played = true; observer.disconnect();
    var count = {value:1}; number.textContent = "01";
    timeline = gsap.timeline({onComplete:finalState});
    timeline.to(count, {value:total,duration:.8,ease:"power2.out",onUpdate:function () {number.textContent=String(Math.round(count.value)).padStart(2,"0");}},0);
    timeline.to([left,right], {x:0,duration:1.1,ease:"expo.out"},0);
    timeline.to(media, {clipPath:"inset(0 47% 0 47%)",duration:.15},0);
    timeline.to(media, {clipPath:"inset(0 0% 0 0%)",duration:1.05,ease:"expo.out"},.15);
    timeline.to(rears, {opacity:1,duration:.45,stagger:.1,ease:"power2.out"},.65);
  }
  var observer = new IntersectionObserver(function (entries) { if (entries[0].intersectionRatio >= .4) play(); }, {threshold:.4});
  initial(); observer.observe(section);
  section.addEventListener("focusin",finalState);
  reduced.addEventListener("change",function () {if (reduced.matches) finalState();});
  window.addEventListener("resize",function () {if (!played) initial();});
  window.addEventListener("pageshow",function (event) {if (event.persisted) finalState();});
}());
