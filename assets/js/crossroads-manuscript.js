(function () {
  "use strict";
  var section = document.querySelector("[data-crossroads-manuscript]");
  if (!section || !window.gsap || !("IntersectionObserver" in window)) return;
  var reduced = matchMedia("(prefers-reduced-motion: reduce)");
  if (reduced.matches) return;
  var words = section.querySelectorAll(".crossroads-manuscript__mask > span");
  var eyebrow = section.querySelector(".crossroads-manuscript__eyebrow");
  var body = section.querySelector(".crossroads-manuscript__body");
  var rule = section.querySelector(".crossroads-manuscript__margin-rule");
  var notes = section.querySelectorAll(".crossroads-manuscript__quote,.crossroads-manuscript__motto,.crossroads-manuscript__notes li");
  var cta = section.querySelector(".crossroads-manuscript__cta");
  var highlights = section.querySelectorAll(".crossroads-manuscript__highlight");
  var drawPaths = matchMedia("(max-width:699px)").matches ? [] : Array.from(section.querySelectorAll(".crossroads-manuscript__pattern-line--draw"));
  var played = false, timeline = null, highlightTweens = [];
  gsap.set(words,{yPercent:115});
  gsap.set([eyebrow,body],{opacity:0});
  gsap.set(body,{y:16});
  gsap.set(notes,{opacity:0,y:10});
  var ruleScale = matchMedia("(max-width:699px)").matches ? "scaleX" : "scaleY";
  gsap.set(rule,{[ruleScale]:0});
  gsap.set(highlights,{backgroundSize:"0% 100%"});
  gsap.set(cta,{"--crossroads-manuscript-underline":0});
  drawPaths.forEach(function(path){
    var length=path.getTotalLength();
    gsap.set(path,{strokeDasharray:length,strokeDashoffset:length});
  });
  function finish() {
    played=true; observer.disconnect(); highlightObserver.disconnect();
    if(timeline) {timeline.progress(1);timeline.kill();}
    highlightTweens.forEach(function(t){t.progress(1);t.kill();});
    gsap.set(words,{clearProps:"transform"});
    gsap.set([eyebrow,body,rule].concat(Array.from(notes)),{clearProps:"transform,opacity"});
    gsap.set(highlights,{backgroundSize:"100% 100%"});
    gsap.set(cta,{"--crossroads-manuscript-underline":1});
    gsap.set(drawPaths,{strokeDashoffset:0});
  }
  function reveal() {
    if(played) return;
    played=true;observer.disconnect();
    timeline=gsap.timeline();
    timeline.to(drawPaths,{strokeDashoffset:0,duration:1.65,stagger:.15,ease:"power4.out"},0)
      .to(eyebrow,{opacity:1,duration:.25},0)
      .to(words,{yPercent:0,duration:.85,stagger:.055,ease:"power3.out"},.1)
      .to(body,{opacity:1,y:0,duration:.45,ease:"power2.out"},.45)
      .to(rule,{[ruleScale]:1,duration:.45,ease:"power2.out"},.7)
      .to(notes,{opacity:1,y:0,duration:.4,stagger:.045,ease:"power2.out"},.85)
      .to(cta,{"--crossroads-manuscript-underline":1,duration:.3},1.25);
  }
  var observer=new IntersectionObserver(function(entries){if(entries[0].intersectionRatio>=.35)reveal();},{threshold:.35});
  var highlightObserver=new IntersectionObserver(function(entries){
    entries.forEach(function(entry){
      if(!entry.isIntersecting || entry.intersectionRatio < .5)return;
      highlightObserver.unobserve(entry.target);
      var index=Array.prototype.indexOf.call(highlights,entry.target);
      highlightTweens.push(gsap.to(entry.target,{backgroundSize:"100% 100%",duration:.7,delay:index*.12,ease:"power2.out"}));
    });
  },{threshold:.5});
  observer.observe(section);highlights.forEach(function(el){highlightObserver.observe(el);});
  section.addEventListener("focusin",finish);
  reduced.addEventListener("change",function(){if(reduced.matches)finish();});
  window.addEventListener("pageshow",function(event){if(event.persisted)finish();});
}());
