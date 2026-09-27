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
      gs.set(panel.querySelectorAll(':scope>.house-stage__media,:scope>.house-stage__copy,.house-stage__media img,.house-stage__media figcaption'), {clearProps:'transform,opacity,--sport-line'});
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
      echo.style.width = previous.querySelector('figure').offsetWidth + 'px';
      echo.appendChild(previous.querySelector('figure').cloneNode(true)); stack.appendChild(echo);
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
    status.textContent=frames.filter(function (frame) {return !frame.hidden;}).length+' photographs · Scroll or swipe to explore';
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
  media.add('(prefers-reduced-motion: no-preference)',function () {
    document.body.classList.add('houses-motion');
    var chapters=Array.from(document.querySelectorAll('.house-spread'));
    chapters.forEach(function (chapter,index) {
      var outgoing=chapter.querySelector('.house-wipe__out'),incoming=chapter.querySelector('.house-wipe__in');
      var wipe=gs.timeline({scrollTrigger:{id:'houses-wipe-'+index,trigger:chapter,start:'top bottom',end:'top 42%',scrub:true},defaults:{ease:'power2.inOut'}});
      // Switch at the same 1.2%-wide stripe: never interpolate house colours.
      wipe.fromTo(outgoing,{scaleX:.012,scaleY:1},{scaleX:1,duration:.18},0)
        .to(outgoing,{scaleX:.012,duration:.18},.18);
      var turn=.36;
      wipe.set(outgoing,{opacity:0},turn).set(incoming,{scaleX:.012,scaleY:1,opacity:1},turn)
        .to(incoming,{scaleX:1,duration:.18},turn)
        .to(incoming,{scaleY:.004,opacity:0,duration:.26},turn+.18);
      // A bounded entrance: content is settled while the chapter is still entering.
      var enter=gs.timeline({scrollTrigger:{id:'houses-enter-'+index,trigger:chapter,start:'top 94%',end:'top 38%',scrub:true},defaults:{ease:'power2.out'}});
      enter.from(chapter.querySelector('.house-spread__index'),{y:12,duration:.2},0)
        .from(chapter.querySelector('.house-spread__colour'),{y:10,duration:.2},.03)
        .from(chapter.querySelector('h2>span'),{yPercent:105,duration:.35},.06)
        .from(chapter.querySelector('figure'),{y:18,scale:.985,opacity:.5,duration:.32},.14)
        .from(chapter.querySelectorAll('.house-copy-block'),{y:14,stagger:.05,duration:.3},.2)
        .from(chapter.querySelector('.house-signature-line'),{scaleX:0,duration:.4},.04);
      gs.fromTo(chapter.querySelector('.house-spread__ghost'),{xPercent:-3},{xPercent:3,ease:'none',scrollTrigger:{id:'houses-ghost-'+index,trigger:chapter,start:'top bottom',end:'bottom top',scrub:true}});
    });
    // The first handoff always belongs to Vasishta, regardless of hero exploration.
    gs.to(document.querySelector('.house-opening__panels'),{scale:.975,transformOrigin:'50% 100%',ease:'none',scrollTrigger:{id:'houses-hero-recede',trigger:chapters[0],start:'top bottom',end:'top 45%',scrub:true}});
    var meet=document.querySelector('#competition');
    gs.timeline({scrollTrigger:{id:'houses-converge',trigger:meet,start:'top bottom',end:'top 42%',scrub:true}})
      .fromTo(meet.querySelectorAll('.house-convergence span'),{xPercent:function(i){return (i-1.5)*110;},y:function(i){return i%2?60:-60;},scaleY:9},{xPercent:0,y:0,scaleY:1,duration:.6,ease:'power2.inOut',stagger:.035},0)
      .from(meet.querySelector('.house-section-heading'),{y:24,duration:.35},.25);
    var archive=document.querySelector('#record');
    gs.fromTo(archive.querySelector('.house-archive-wash'),{opacity:.18},{opacity:0,ease:'none',scrollTrigger:{id:'houses-archive-drain',trigger:archive,start:'top bottom',end:'top 55%',scrub:true}});
    gs.from(archive.querySelector('.house-archive-line'),{scaleX:0,ease:'none',scrollTrigger:{id:'houses-archive',trigger:archive,start:'top 95%',end:'top 48%',scrub:true}});
    var closing=document.querySelector('#together');
    gs.timeline({scrollTrigger:{id:'houses-closing',trigger:closing,start:'top bottom',end:'top 18%',scrub:true},defaults:{ease:'power2.inOut'}})
      .fromTo(closing.querySelectorAll('.house-closing-reveal span'),{scaleX:.012,scaleY:0},{scaleX:.012,scaleY:1,duration:.26,stagger:.025},0)
      .to(closing.querySelectorAll('.house-closing-reveal span'),{scaleX:1,duration:.25},.32)
      .to(closing.querySelectorAll('.house-closing-reveal span'),{xPercent:function(i){return (1.5-i)*100;},scaleX:.008,duration:.28},.59)
      .to(closing.querySelectorAll('.house-closing-reveal span'),{opacity:0,duration:.12},.85)
      .from(closing.querySelector('h2'),{y:28,duration:.3},.69);
    refresh();
    return function () {
      document.body.classList.remove('houses-motion');

    };
  });
  if(document.fonts)document.fonts.ready.then(refresh);
  window.addEventListener('load',refresh,{once:true});
})();
