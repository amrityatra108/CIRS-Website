/* A continuous measured route; both programmes keep their original reading order. */
(function () {
  'use strict';
  var main = document.querySelector('.curriculum #main');
  if (!main) return;
  var svg = main.querySelector('.curriculum-route');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)');
  var choices = Array.from(main.querySelectorAll('[data-route-choice]'));
  var controls = main.querySelector('.journey-controls');
  var fork = main.querySelector('.atl-div__node');
  var active = '', routes = {}, nodes = [], frame = 0, layoutFrame = 0;
  var forkThreshold=Infinity;
  var tween = null, switching = false, state = { cbse:0, ib:0 };
  function box(el) {
    var r = el.getBoundingClientRect(), m = main.getBoundingClientRect();
    return { x:r.left-m.left, y:r.top-m.top, w:r.width, h:r.height };
  }
  function makeRoute(group, d) {
    group.querySelectorAll('path').forEach(function (p) { p.setAttribute('d', d); });
    var p = group.querySelector('.route-progress'), length = p.getTotalLength();
    p.style.strokeDasharray = length + ' ' + length;
    var hover = group.querySelector('.route-hover');
    if (hover) { hover.style.strokeDasharray = length + ' ' + length; hover.style.strokeDashoffset = length * .84; }
    // Match arc length to vertical document position, including the curves.
    var samples = [];
    for (var i=0; i<=500; i++) { var at=length*i/500; samples.push({ y:p.getPointAtLength(at).y, length:at }); }
    return { path:p, length:length, samples:samples };
  }
  function progress(route, y) {
    var a=route.samples;
    if (y<=a[0].y) return 0;
    if (y>=a[a.length-1].y) return 1;
    var lo=0, hi=a.length-1;
    while (hi-lo>1) { var mid=(lo+hi)>>1; if (a[mid].y<=y) lo=mid; else hi=mid; }
    var t=(y-a[lo].y)/Math.max(.001,a[hi].y-a[lo].y);
    return (a[lo].length+(a[hi].length-a[lo].length)*t)/route.length;
  }
  function illuminate(route,p) {
    var value=(route.length*(1-p)).toFixed(3);
    if (route.lastOffset!==value) { route.path.style.strokeDashoffset=value; route.lastOffset=value; }
  }
  function readingY() { return -main.getBoundingClientRect().top + innerHeight*.72; }
  function draw() {
    frame=0;
    if (!routes.trunk) return;
    var y=readingY(), end=scrollY+innerHeight>=document.documentElement.scrollHeight-4;
    illuminate(routes.trunk, reduce.matches||end ? 1 : progress(routes.trunk,y));
    ['cbse','ib'].forEach(function (key) {
      if (!switching) state[key]=reduce.matches ? 1 : (key===active ? progress(routes[key],y) : 0);
      illuminate(routes[key],state[key]);
    });
    nodes.forEach(function (n) {
      var reached=reduce.matches||y>=n.y;
      n.circle.classList.toggle('is-reached',reached&&(!n.route||!active||n.route===active));
      if (n.element) n.element.classList.toggle('is-reached',reached);
    });
    controls.classList.toggle('is-visible',y>forkThreshold&&!end);
  }
  function schedule() { if (!frame) frame=requestAnimationFrame(draw); }
  function fit() {
    layoutFrame=0;
    var w=main.clientWidth, h=main.scrollHeight;
    var forkBox=box(main.querySelector('#journey-division'));
    forkThreshold=forkBox.y+forkBox.h+innerHeight*.37;
    svg.setAttribute('viewBox','0 0 '+w+' '+h);
    var hero=box(main.querySelector('.atl-open')), wrap=box(main.querySelector('.atl-journey > .wrap'));
    var j=box(fork), cx=j.x+j.w/2, jy=j.y+j.h/2;
    var mobile=w<=680, tablet=w<=1023;
    var left=mobile ? 20 : tablet ? 26 : Math.max(24,wrap.x-30), right=w-left;
    var bottom=box(main.querySelector('.journey-end span')), ey=bottom.y+bottom.h/2;
    // Breakpoint-specific turns; the mobile path stays in vertical gutters.
    var sx=w*(mobile ? .06 : .60), sy=hero.y+hero.h;
    var seniorRail=mobile ? left : right;
    var junior=box(main.querySelector('#journey-foundation'));
    var juniorPhoto=box(main.querySelector('.atl-shot[data-step="0"]'));
    var senior=box(main.querySelector('#journey-board'));
    var seniorPhoto=box(main.querySelector('.atl-shot[data-step="1"]'));
    var bendStart=Math.max(junior.y+junior.h,juniorPhoto.y+juniorPhoto.h)+16;
    var bendEnd=Math.min(senior.y,seniorPhoto.y)-16;
    var bendMid=(bendStart+bendEnd)/2;
    var trunk='M'+sx+' '+sy+' C'+sx+' '+(sy+70)+' '+left+' '+(sy+50)+' '+left+' '+(sy+130);
    if (!mobile) trunk+=' L'+left+' '+bendStart+' C'+left+' '+bendMid+' '+seniorRail+' '+bendMid+' '+seniorRail+' '+bendEnd;
    trunk+=' L'+seniorRail+' '+(jy-90)+' C'+seniorRail+' '+(jy-24)+' '+cx+' '+(jy-65)+' '+cx+' '+(jy-j.h/2);
    routes.trunk=makeRoute(svg.querySelector('.journey-trunk'),trunk);
    ['cbse','ib'].forEach(function (key) {
      var icon=box(main.querySelector('.atl-div__end--'+key+' .journey-icon'));
      var ix=icon.x+icon.w/2, iy=icon.y+icon.h/2, rail=key==='cbse' ? left : right, turn=mobile ? 30 : 55;
      routes[key]=makeRoute(svg.querySelector('[data-route="'+key+'"]'),
        'M'+cx+' '+(jy+j.h/2)+' C'+cx+' '+(jy+turn)+' '+rail+' '+(jy+j.h/2)+' '+rail+' '+(jy+turn*2)+
        ' L'+rail+' '+(iy-icon.h/2-50)+' Q'+rail+' '+(iy-icon.h/2)+' '+ix+' '+(iy-icon.h/2)+
        ' M'+ix+' '+(iy+icon.h/2)+' C'+ix+' '+(iy+icon.h/2+50)+' '+rail+' '+(iy+icon.h/2+25)+' '+rail+' '+(iy+icon.h/2+85)+
        ' L'+rail+' '+(ey-85)+' Q'+rail+' '+ey+' '+(w/2)+' '+ey);
    });
    var layer=svg.querySelector('.journey-nodes'); layer.replaceChildren(); nodes=[];
    function node(el,x,key,waypoint) {
      var b=box(el), y=b.y+Math.min(26,b.h/2), circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
      circle.setAttribute('cx',x); circle.setAttribute('cy',y); circle.setAttribute('r',mobile ? 4 : 5);
      layer.appendChild(circle); nodes.push({ circle:circle,y:y,route:key,element:waypoint });
    }
    main.querySelectorAll('.journey-waypoint').forEach(function (el) { node(el,el.closest('#journey-board') ? seniorRail : left,'',el); });
    node(main.querySelector('#cbse .atl-prog-head'),left,'cbse');
    node(main.querySelector('#ib .atl-prog-head'),right,'ib');
    main.querySelectorAll('.atl-group,.atl-core__title').forEach(function (el) { node(el,right,'ib'); });
    main.querySelectorAll('.atl-stream').forEach(function (el) { node(el,left,'cbse'); });
    main.classList.add('journey-ready'); draw();
  }
  function scheduleFit() { if (!layoutFrame) layoutFrame=requestAnimationFrame(fit); }
  function select(key,animate) {
    if (key!=='cbse'&&key!=='ib') return;
    var old=active; active=key; main.dataset.activeRoute=key;
    choices.forEach(function (a) { if (a.dataset.routeChoice===key) a.setAttribute('aria-current','true'); else a.removeAttribute('aria-current'); });
    ['cbse','ib'].forEach(function (k) { var el=main.querySelector('#'+k); if (k===key) el.setAttribute('data-active-route',''); else el.removeAttribute('data-active-route'); });
    if (tween) { tween.kill(); tween=null; } switching=false;
    if (animate&&!reduce.matches&&window.gsap&&routes[key]) {
      switching=true;
      tween=gsap.timeline({ onUpdate:schedule,onComplete:function () { switching=false; schedule(); } });
      if (old&&old!==key) tween.to(state,{ [old]:0,duration:.25,ease:'power1.inOut' });
      tween.to(state,{ [key]:progress(routes[key],readingY()),duration:.45,ease:'power1.inOut' });
    }
    schedule();
  }
  function fromHash() {
    var hash=location.hash;
    if (hash==='#cbse'||hash.indexOf('#stream-')===0) select('cbse',false);
    else if (hash==='#ib'||hash.indexOf('#ib-g')===0||hash==='#core') select('ib',false);
    else if (!hash||['#top','#journey-division','#journey','#journey-foundation','#journey-board','#pathways','#subjects'].includes(hash)) {
      active=''; delete main.dataset.activeRoute;
      choices.forEach(function (a) { a.removeAttribute('aria-current'); });
      main.querySelectorAll('[data-active-route]').forEach(function (el) { el.removeAttribute('data-active-route'); });
      if (tween) tween.kill(); switching=false; schedule();
    }
  }
  // Capture chooses the route before cirs.js scrolls its existing anchor.
  main.addEventListener('click',function (e) {
    var a=e.target.closest('a[href^="#"]');
    if (!a||e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey) return;
    if (a.dataset.routeChoice) select(a.dataset.routeChoice,true);
    var hash=a.getAttribute('href');
    if (location.hash!==hash) history.pushState(null,'',hash);
    if (!a.dataset.routeChoice) fromHash();
    if (a.dataset.routeChoice||hash==='#journey-division') { var t=document.getElementById(hash.slice(1)); t.setAttribute('tabindex','-1'); t.focus({ preventScroll:true }); }
  },true);
  choices.forEach(function (a) {
    var group=svg.querySelector('[data-route="'+a.dataset.routeChoice+'"]');
    ['pointerenter','focus'].forEach(function (event) { a.addEventListener(event,function () { group.classList.add('is-hovered'); }); });
    ['pointerleave','blur'].forEach(function (event) { a.addEventListener(event,function () { group.classList.remove('is-hovered'); }); });
  });
  window.addEventListener('popstate',function () {
    fromHash(); var t=document.getElementById(location.hash.slice(1)||'top');
    if (t) {
      var top=t.getBoundingClientRect().top+scrollY-96;
      var event=new CustomEvent('cirs-section-scroll',{ cancelable:true,detail:{ top:top,duration:reduce.matches ? 0 : .6 } });
      if (window.dispatchEvent(event)) scrollTo({ top:top,behavior:reduce.matches ? 'instant' : 'smooth' });
    }
  });
  window.addEventListener('hashchange',fromHash);
  window.addEventListener('scroll',schedule,{ passive:true });
  window.addEventListener('resize',scheduleFit,{ passive:true });
  window.addEventListener('load',scheduleFit);
  new ResizeObserver(scheduleFit).observe(main);
  if (document.fonts) document.fonts.ready.then(scheduleFit);
  reduce.addEventListener('change',function () { if (tween) tween.kill(); switching=false; schedule(); });
  // Reveal the two school photographs once. A preference change restores the
  // still composition immediately; the reading column never waits for motion.
  var photoObserver=new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in-view');
        photoObserver.unobserve(entry.target);
      }
    });
  },{ threshold:.12 });
  main.querySelectorAll('.atl-shot').forEach(function (el) {
    el.classList.add('journey-photo-ready'); photoObserver.observe(el);
  });
  // Preserve the existing hero curves, fitting strokes to real pixels.
  function fitHero() {
    main.querySelectorAll('svg[data-fit]').forEach(function (el) {
      var w=el.clientWidth,h=el.clientHeight; if (!w||!h) return;
      el.setAttribute('viewBox','0 0 '+w+' '+h);
      el.querySelectorAll('path').forEach(function (p) {
        var d=p.dataset.original||p.getAttribute('d'); p.dataset.original=d; var i=0;
        p.setAttribute('d',d.replace(/[A-Za-z]|-?\d*\.?\d+/g,function (t) { if (/[A-Za-z]/.test(t)) { i=0; return t; } return String(Number(t)*(i++%2 ? h : w)/100); }));
      }); el.classList.add('is-fit');
    });
  }
  new ResizeObserver(fitHero).observe(main.querySelector('.atl-open')); fitHero();
  fromHash(); fit();
  var links=Array.from(main.querySelectorAll('.atl-ib__rail a'));
  var index=new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) { if (!entry.isIntersecting) return; links.forEach(function (a) { if (a.hash==='#'+entry.target.id) a.setAttribute('aria-current','true'); else a.removeAttribute('aria-current'); }); });
  },{ rootMargin:'-30% 0px -55% 0px' });
  main.querySelectorAll('.atl-group').forEach(function (g) { index.observe(g); });
})();
