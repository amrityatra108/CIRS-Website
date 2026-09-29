/* Houses: progressive enhancement, native scrolling, reversible local motion. */
(function () {
  'use strict';
  if (!document.body.classList.contains('houses')) return;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var gs = window.gsap, ST = window.ScrollTrigger;
  var tablist = document.querySelector('[data-stage-tabs]');
  var tabs = Array.from(document.querySelectorAll('[data-stage-tab]'));
  var panels = Array.from(document.querySelectorAll('[data-stage-panel]'));
  var stack = document.querySelector('.house-stage-stack');
  var active = null, stageTween = null, runner = null, runnerTween = null;
  var refreshFrame = 0;
  function refresh() {
    if (!ST || refreshFrame) return;
    refreshFrame = requestAnimationFrame(function () { refreshFrame = 0; ST.refresh(); });
  }
  function cleanStage() {
    if (stageTween) stageTween.kill();
    if (runnerTween) runnerTween.kill();
    if (stack) stack.querySelectorAll('.house-stage-echo').forEach(function (el) { el.remove(); });
    if (gs) panels.forEach(function (panel) {
      gs.set(panel.querySelectorAll(':scope>.house-stage__media,:scope>.house-stage__copy,.house-stage__media img,.house-stage__media figcaption,.house-culture-grid figure'), {clearProps:'transform,opacity,--sport-line'});
    });
  }
  function moveRunner(animate) {
    if (!runner || !active) return;
    var tab = tabs.find(function (el) { return el.dataset.stageTab === active; });
    var vars = {x:tab.offsetLeft,y:tab.offsetTop,scaleX:tab.offsetWidth,duration:animate ? .5 : 0,ease:'power3.out'};
    if (runnerTween) runnerTween.kill();
    runnerTween = gs.to(runner, vars);
  }
  function activate(id, focus) {
    if (!panels.some(function (panel) { return panel.id === id; })) return;
    var previous = document.getElementById(active), incoming = document.getElementById(id);
    var animate = gs && !reduced.matches && active && active !== id;
    var direction = tabs.findIndex(function (t) { return t.dataset.stageTab === id; }) > tabs.findIndex(function (t) { return t.dataset.stageTab === active; }) ? 1 : -1;
    cleanStage();
    var echo;
    if (animate && previous) {
      // Decorative old photograph only; never duplicate IDs, controls or accessible content.
      echo = document.createElement('div'); echo.className = 'house-stage-echo';
      echo.setAttribute('aria-hidden','true'); echo.inert = true;
      echo.style.width = previous.querySelector('.house-stage__media').offsetWidth + 'px';
      echo.appendChild(previous.querySelector('.house-stage__media').cloneNode(true));
      echo.querySelectorAll('[id]').forEach(function (el) { el.removeAttribute('id'); });
      stack.appendChild(echo);
    }
    active = id;
    tabs.forEach(function (tab) {
      var selected = tab.dataset.stageTab === id;
      tab.setAttribute('aria-selected',String(selected)); tab.tabIndex = selected ? 0 : -1;
      if (selected && focus) tab.focus();
    });
    panels.forEach(function (panel) { panel.hidden = panel.id !== id; });
    moveRunner(animate);
    if (animate) {
      stageTween = gs.timeline({defaults:{ease:'power3.out'},onComplete:function () { if (echo) echo.remove(); }});
      stageTween.to(echo,{x:-direction*22,opacity:0,duration:.25},0)
        .fromTo(incoming.querySelector('.house-stage__media'),{x:direction*24,opacity:0},{x:0,opacity:1,duration:.5},.08)
        .fromTo(incoming.querySelector('.house-stage__copy'),{y:12},{y:0,duration:.4},.14);
      if (id === 'culture') {
        stageTween.fromTo(incoming.querySelectorAll('.house-culture-grid figure'),{y:12,opacity:.35},{y:0,opacity:1,duration:.35,stagger:.055},.08);
      }
      if (id === 'sport') {
        stageTween.fromTo(incoming.querySelector('figure img'),{scale:1.03},{scale:1,duration:.55},0)
          .fromTo(incoming.querySelector('figure'),{'--sport-line':0},{'--sport-line':1,duration:.5},.08)
          .fromTo(incoming.querySelector('figcaption'),{opacity:0,y:5},{opacity:1,y:0,duration:.3},.22);
      }
    }
    refresh();
  }
  if (tablist && tabs.length) {
    tablist.hidden = false; tablist.setAttribute('role','tablist');
    if (gs) { runner=document.createElement('span'); runner.className='house-tab-runner'; runner.setAttribute('aria-hidden','true');tablist.appendChild(runner); }
    tabs.forEach(function (tab,index) {
      tab.setAttribute('role','tab');
      tab.addEventListener('click',function () { activate(tab.dataset.stageTab,false); });
      tab.addEventListener('keydown',function (event) {
        var next;
        if (event.key==='ArrowRight'||event.key==='ArrowDown') next=(index+1)%tabs.length;
        if (event.key==='ArrowLeft'||event.key==='ArrowUp') next=(index+tabs.length-1)%tabs.length;
        if (event.key==='Home') next=0;
        if (event.key==='End') next=tabs.length-1;
        if (next===undefined) return;
        event.preventDefault();activate(tabs[next].dataset.stageTab,true);
      });
    });
    panels.forEach(function (panel) { panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby','tab-'+panel.id);panel.tabIndex=0; });
    activate('march',false);
  }
  var filters=Array.from(document.querySelectorAll('[data-house-filter]'));
  var frames=Array.from(document.querySelectorAll('[data-gallery-house]'));
  var strip=document.querySelector('.house-gallery__strip');
  var status=document.querySelector('.house-gallery__status');
  var selectedFrame=null;
  frames.forEach(function (frame,index) {
    var img=frame.querySelector('img'),button=document.createElement('button');
    button.type='button';button.className='house-gallery__select';button.setAttribute('aria-pressed','false');
    button.setAttribute('aria-label','Expand photograph '+(index+1)+': '+img.alt);
    img.parentNode.insertBefore(button,img);button.appendChild(img);
    button.addEventListener('click',function () { selectFrame(selectedFrame===frame?null:frame,false); });
  });
  function selectFrame(frame,focus) {
    selectedFrame=frame;
    frames.forEach(function (item) {var yes=item===frame;item.classList.toggle('is-selected',yes);item.querySelector('button').setAttribute('aria-pressed',String(yes));});
    if (frame) {
      if (focus) frame.querySelector('button').focus({preventScroll:true});
      strip.scrollTo({left:frame.offsetLeft-strip.offsetLeft-(strip.clientWidth-frame.offsetWidth)/2,behavior:reduced.matches?'instant':'smooth'});
    }
  }
  if (strip) strip.addEventListener('keydown',function (event) {
    if (event.altKey||event.ctrlKey||event.metaKey) return;
    if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
    event.preventDefault();
    var visible=frames.filter(function (frame) {return !frame.hidden;});
    var current=event.target.closest('[data-gallery-house]')||selectedFrame;
    var index=visible.indexOf(current);
    var next=event.key==='Home'?0:event.key==='End'?visible.length-1:Math.max(0,Math.min(visible.length-1,index+(event.key==='ArrowRight'?1:-1)));
    selectFrame(visible[next],true);
  });
  function filterHouse(house) {
    selectFrame(null,false);
    filters.forEach(function (button) {button.setAttribute('aria-pressed',String(button.dataset.houseFilter===house));});
    frames.forEach(function (frame) {frame.hidden=house!=='all'&&frame.dataset.galleryHouse!==house;});
    strip.scrollLeft=0;
    status.innerHTML=frames.filter(function (frame) {return !frame.hidden;}).length+' photographs<span class="house-gallery__hint"> · Scroll or swipe to explore</span>';
    refresh();
  }
  if (filters.length) {
    document.querySelector('.house-gallery__filters').hidden=false;
    filters.forEach(function (button) {button.addEventListener('click',function () {filterHouse(button.dataset.houseFilter);});});
  }
  function followHash() {
    var id=location.hash.slice(1);
    if (panels.some(function (panel) {return panel.id===id;})) activate(id,false);
    if (id.indexOf('gallery-')===0 && filters.some(function (button) {return button.dataset.houseFilter===id.slice(8);})) filterHouse(id.slice(8));
    var target=document.getElementById(id);
    if (target&&target.tagName==='DETAILS') target.open=true;
    if (target && (id.indexOf('gallery-')===0||id.indexOf('event-')===0||panels.includes(target))) {
      requestAnimationFrame(function () {refresh();target.scrollIntoView({block:'start',behavior:'instant'});});
    }
  }
  document.addEventListener('click',function (event) {
    var link=event.target.closest('a[href^="#"]');if(!link)return;
    var id=link.getAttribute('href').slice(1),target=document.getElementById(id);
    if (id.indexOf('gallery-')===0) filterHouse(id.slice(8));
    if(target&&target.tagName==='DETAILS')target.open=true;
    if(location.hash==='#'+id)followHash();
  });
  document.querySelectorAll('.house-archive details').forEach(function (el) {el.addEventListener('toggle',refresh);});
  window.addEventListener('hashchange',followHash);
  window.addEventListener('resize',function () {moveRunner(false);});
  reduced.addEventListener('change',function () {cleanStage();moveRunner(false);});
  followHash();

  if (!gs || !ST) return; // All interactions above work without the animation libraries.
  gs.registerPlugin(ST);
  var media=gs.matchMedia();
  media.add({motion:'(prefers-reduced-motion: no-preference)',desktop:'(min-width:901px)'},function (context) {
    if (!context.conditions.motion) return;
    document.body.classList.add('houses-motion');
    var desktop=context.conditions.desktop;
    var chapters=Array.from(document.querySelectorAll('.house-spread'));
    var titleLayers=[];
    chapters.forEach(function (chapter,index) {
      var figure=chapter.querySelector('figure');
      var mask=chapter.querySelector('.house-photo-mask');
      var picture=mask.querySelector('img');
      var heading=chapter.querySelector('h2');
      var word=heading.querySelector('span');
      var number=chapter.querySelector('.house-spread__index');
      var colour=chapter.querySelector('.house-spread__colour');
      var line=chapter.querySelector('.house-signature-line');
      var blocks=chapter.querySelectorAll('.house-copy-block');
      var link=chapter.querySelector('.house-spread__copy a');
      var ghost=chapter.querySelector('.house-spread__ghost');
      var tracking=getComputedStyle(word).letterSpacing;
      var ghostOpacity=+getComputedStyle(ghost).opacity;
      var slices=[];
      if(desktop) {
        var layer=document.createElement('div');layer.className='house-title-slices';
        layer.setAttribute('aria-hidden','true');layer.inert=true;
        for(var i=0;i<3;i++) {
          var slice=document.createElement('span');slice.textContent=word.textContent;
          slice.style.clipPath='inset('+(i*100/3)+'% 0 '+((2-i)*100/3)+'% 0)';
          layer.appendChild(slice);slices.push(slice);
        }
        heading.appendChild(layer);titleLayers.push(layer);
      }
      // Synchronous sets run only after GSAP and ScrollTrigger are available.
      // Base HTML/CSS is readable; matchMedia reverts every set on teardown.
      gs.set([figure,heading,number,colour,ghost],{opacity:0});
      gs.set(number,{y:10});gs.set(colour,{x:10,'--marker-scale':0});
      gs.set(line,{scaleX:0,opacity:0});
      gs.set(mask,{clipPath:desktop?'inset(0% 0% 100% 0%)':'inset(0% 0% 12% 0%)'});
      gs.set(picture,{scale:desktop?1.035:1.015});
      gs.set(word,{yPercent:115,skewY:desktop?6:0,letterSpacing:'.012em',opacity:0});
      gs.set(blocks,{opacity:0,y:28});gs.set(link,{autoAlpha:0,y:8});
      if(desktop) gs.set(slices,{yPercent:115,skewY:6,opacity:0,letterSpacing:'.012em',x:function(i){return [-18,22,-12][i];}});
      var enter=gs.timeline({paused:true,defaults:{ease:'power3.out'}});
      enter.fromTo(number,{opacity:0,y:10},{opacity:1,y:0,duration:.14,immediateRender:false},0)
        .fromTo(colour,{opacity:0,x:10,'--marker-scale':0},{opacity:1,x:0,'--marker-scale':1,duration:.14,immediateRender:false},.02)
        .fromTo(line,{opacity:0,scaleX:0},{opacity:1,scaleX:1,duration:.18,immediateRender:false},.04)
        .fromTo(figure,{opacity:0},{opacity:1,duration:.14,immediateRender:false},.12)
        .fromTo(mask,{clipPath:desktop?'inset(0% 0% 100% 0%)':'inset(0% 0% 12% 0%)'},{clipPath:'inset(0% 0% 0% 0%)',duration:.36,ease:'power2.inOut',immediateRender:false},.12)
        .fromTo(picture,{scale:desktop?1.035:1.015},{scale:1,duration:.36,immediateRender:false},.12)
        .fromTo(heading,{opacity:0},{opacity:1,duration:.01,immediateRender:false},.22)
        .fromTo(word,{yPercent:115,skewY:desktop?6:0,letterSpacing:'.012em',opacity:0},{yPercent:0,skewY:0,letterSpacing:tracking,opacity:desktop?0:1,duration:.48,immediateRender:false},.22)
        .fromTo(ghost,{opacity:0},{opacity:ghostOpacity,duration:.2,immediateRender:false},.28)
        .fromTo(blocks,{opacity:0,y:28},{opacity:1,y:0,duration:.26,stagger:.07,immediateRender:false},.53)
        .fromTo(link,{autoAlpha:0,y:8},{autoAlpha:1,y:0,duration:.14,immediateRender:false},.72);
      if(desktop) {
        enter.fromTo(slices,{yPercent:115,skewY:6,opacity:0,letterSpacing:'.012em'},{yPercent:0,skewY:0,opacity:1,letterSpacing:tracking,duration:.48,immediateRender:false},.22)
          .fromTo(slices,{x:function(i){return [-18,22,-12][i];}},{x:0,duration:.35,ease:'power3.out',immediateRender:false},.30)
          .fromTo(slices,{opacity:1},{opacity:0,duration:.001,immediateRender:false},.70)
          .fromTo(word,{opacity:0},{opacity:1,duration:.001,immediateRender:false},.70);
      }
      if(index>0) {
        var previous=chapters[index-1];
        enter.fromTo(previous.querySelector('figure'),{yPercent:0},{yPercent:-2,duration:.4,immediateRender:false},0)
          .fromTo(previous.querySelector('.house-spread__copy'),{y:0},{y:-12,duration:.4,immediateRender:false},0)
          .fromTo(previous.querySelector('h2>span'),{y:0},{y:-30,duration:.4,immediateRender:false},0);
      }
      // One entry trigger coordinates the complete chapter. A short triggered
      // sequence finishes even when the visitor stops at the threshold.
      ST.create({id:'houses-handoff-'+index,trigger:chapter,animation:enter,
        start:'top 78%',end:'top 40%',invalidateOnRefresh:true,
        toggleActions:'play complete none reset',
        onUpdate:function(self){
          if(self.progress>0 && self.progress<.25) {
            if(self.direction<0) enter.reverse(); else enter.play();
          }
        },
        onLeaveBack:function(){enter.pause(0);},
        onRefresh:function(self){
          if(self.scroll()<self.start) enter.pause(0);
          else if(!enter.isActive()) enter.progress(1).pause();
        }
      });
    });
    [['competition','.house-convergence','houses-converge'],['together','.house-closing__bars','houses-closing']].forEach(function(item){
      var section=document.getElementById(item[0]),lines=section.querySelector(item[1]);
      gs.timeline({scrollTrigger:{id:item[2],trigger:lines,start:'top 94%',end:'top 65%',scrub:true}})
        .fromTo(lines.querySelectorAll('span'),{scaleX:.3,x:function(i){return i%2?14:-14;}},{scaleX:1,x:0,duration:.4,stagger:.025,ease:'power2.out'},0)
        .from(section.querySelector('h2'),{y:16,duration:.3},.08);
    });
    refresh();
    return function () {
      titleLayers.forEach(function(el){el.remove();});
      document.body.classList.remove('houses-motion');
    };
  });
  if(document.fonts)document.fonts.ready.then(refresh);
  window.addEventListener('load',refresh,{once:true});
  window.addEventListener('pageshow',refresh);
})();
