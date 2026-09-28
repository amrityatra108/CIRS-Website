/* The supplied Gurudev route, adapted to native page scrolling. All scenes
   remain ordinary reading content on small screens and with reduced motion. */
(() => {
  'use strict';
  const root = document.querySelector('[data-gurudev-journey]');
  if (!root) return;

  const motion = matchMedia('(min-width: 900px) and (prefers-reduced-motion: no-preference)');
  const viewport = root.querySelector('[data-story-viewport]');
  const world = root.querySelector('[data-story-world]');
  const svg = root.querySelector('[data-story-route]');
  const path = root.querySelector('[data-route-path]');
  const paths = svg.querySelectorAll('path');
  const scenes = [...root.querySelectorAll('[data-story-scene]')];
  const vehicle = root.querySelector('[data-story-vehicle]');
  const vehicleArt = root.querySelector('[data-vehicle-art]');
  const rearWheel = root.querySelector('[data-wheel="rear"]');
  const frontWheel = root.querySelector('[data-wheel="front"]');
  const count = root.querySelector('[data-story-count]');
  const levels = [1,2.2,2.2,2.2,3.6,4.75,5.75,6.75,7.75,9.15,9.15,9.9,9.15];
  const clamp = (n,a,b) => Math.max(a,Math.min(b,n));
  const smooth = n => { const t=clamp(n,0,1); return t*t*(3-2*t); };
  const last = scenes.length - 1;
  let width = 0, height = 0, roadY = 0, total = 0, points = [], anchors = [];
  let cardH = 0, cardTop = 118;
  let current = 0, target = 0, active = -1, visiblePair = -1, frame = 0, lastTime = 0;
  let heading = 1, lastY = 0, restTimer = 0, held = false;

  function rounded(ps,r) {
    let d = `M ${ps[0].x} ${ps[0].y}`;
    for (let i=1;i<ps.length-1;i++) {
      const a=ps[i-1],b=ps[i],c=ps[i+1];
      const ab=Math.hypot(b.x-a.x,b.y-a.y),bc=Math.hypot(c.x-b.x,c.y-b.y);
      if (ab<.01 || bc<.01) continue;
      const cut=Math.min(r,ab*.42,bc*.42);
      d+=` L ${b.x+(a.x-b.x)*cut/ab} ${b.y+(a.y-b.y)*cut/ab}`;
      d+=` Q ${b.x} ${b.y} ${b.x+(c.x-b.x)*cut/bc} ${b.y+(c.y-b.y)*cut/bc}`;
    }
    const end=ps[ps.length-1];
    return `${d} L ${end.x} ${end.y}`;
  }

  function segment(value) {
    if (anchors.length<2) return {i:0,f:0};
    const at=clamp(value,anchors[0],anchors[last]);
    let i=0;
    while (i<last-1 && anchors[i+1]<at) i++;
    const span=anchors[i+1]-anchors[i];
    return {i,f:span>0?clamp((at-anchors[i])/span,0,1):0};
  }

  function distanceForScroll(progress) {
    const leg=clamp(progress,0,1)*last;
    const index=Math.min(last-1,Math.floor(leg));
    const within=leg-index;
    const travelling=clamp((within-.2)/.6,0,1);
    const eased=smooth(travelling);
    return anchors[index]+eased*(anchors[index+1]-anchors[index]);
  }

  function layout() {
    if (!motion.matches) {
      if (frame) cancelAnimationFrame(frame);
      frame=0;lastTime=0;active=-1;visiblePair=-1;anchors=[];
      root.classList.remove('is-enhanced');
      world.removeAttribute('style');
      svg.removeAttribute('width');
      svg.removeAttribute('height');
      svg.removeAttribute('viewBox');
      scenes.forEach(scene => {
        scene.classList.remove('is-active');
        scene.classList.remove('is-visible');
        scene.removeAttribute('style');
        scene.removeAttribute('inert');
        scene.setAttribute('aria-hidden','false');
      });
      return;
    }
    root.classList.add('is-enhanced');
    const w=viewport.clientWidth,h=viewport.clientHeight;
    if (!w || !h) return;
    const previousPosition=anchors.length>1
      ?clamp((target-anchors[0])/(anchors[last]-anchors[0]),0,1)
      :0;
    width=w;height=h;
    points=levels.map((level,i)=>({x:(1+i*1.7)*w,y:h+(level-1)*w*.6}));
    const routePoints=[];
    points.forEach((p,i)=>{
      routePoints.push({x:p.x-w*.6,y:p.y},p,{x:p.x+w*.6,y:p.y});
      if ([0,3,8].includes(i) && i<last) {
        const nextPoint=points[i+1],cornerX=(p.x+nextPoint.x)/2;
        routePoints.push({x:cornerX,y:p.y},{x:cornerX,y:nextPoint.y});
      }
    });
    const d=rounded(routePoints,w*.3);
    paths.forEach(item=>item.setAttribute('d',d));
    total=path.getTotalLength();
    if (!Number.isFinite(total) || total<=0) return;
    // The route is constructed with monotonically increasing x coordinates.
    // Find each scene's exact point on that route with a bounded search instead
    // of scanning thousands of samples on every initial layout and resize.
    anchors=points.map(point=>{
      let low=0,high=total;
      for (let i=0;i<20;i++) {
        const length=(low+high)/2;
        if (path.getPointAtLength(length).x<point.x) low=length;
        else high=length;
      }
      return (low+high)/(2*total);
    });
    if (!anchors.every((anchor,i)=>Number.isFinite(anchor) && (i===0 || anchor>anchors[i-1]))) {
      root.classList.remove('is-enhanced');
      return;
    }
    const worldWidth=w*23,worldHeight=h+w*7;
    world.style.width=`${worldWidth}px`;
    world.style.height=`${worldHeight}px`;
    svg.setAttribute('width',worldWidth);
    svg.setAttribute('height',worldHeight);
    svg.setAttribute('viewBox',`0 0 ${worldWidth} ${worldHeight}`);
    const cardHeight=Math.min(472,Math.max(290,h-275));
    roadY=h-18;
    cardH=cardHeight;cardTop=118;
    scenes.forEach((scene,i)=>{
      scene.style.width=`${w*.94}px`;
      scene.style.height=`${cardHeight}px`;
      scene.style.left=`${points[i].x-w*.47}px`;
      scene.style.top=`${points[i].y-roadY+cardTop}px`;
    });
    current=target=anchors[0]+previousPosition*(anchors[last]-anchors[0]);
    render();
    readScroll();
  }

  // Where the camera stands, and how the two neighbouring scenes are mixed,
  // for a position on the route. render() draws from it; presence() and
  // restOn() ask it about positions the page is not at.
  function view(value) {
    const distance=value*total,part=segment(value);
    const framing=Math.sin(part.f*Math.PI)**2;
    const lead=framing*Math.min(80,width*.14);
    const camera=path.getPointAtLength(clamp(distance+lead,0,total));
    const cameraY=roadY-framing*190;
    return {distance,part,camera,cameraY,x:width/2-camera.x,y:cameraY-camera.y,fade:smooth((part.f-.15)/.7)};
  }

  function render() {
    if (!root.classList.contains('is-enhanced') || !anchors.length) return;
    current=clamp(current,anchors[0],anchors[last]);
    const v=view(current),distance=v.distance,p=path.getPointAtLength(distance),part=v.part,cameraY=v.cameraY;
    world.style.transform=`translate3d(${v.x}px,${v.y}px,0)`;

    let closest=0,best=Infinity;
    anchors.forEach((anchor,i)=>{
      const gap=Math.abs(anchor-current);
      if (gap<best) {best=gap;closest=i;}
    });
    if (part.i!==visiblePair) {
      visiblePair=part.i;
      scenes.forEach((scene,i)=>{
        const visible=i===part.i || i===part.i+1;
        scene.classList.toggle('is-visible',visible);
        if (!visible) scene.style.removeProperty('opacity');
      });
    }
    if (closest!==active) {
      active=closest;
      scenes.forEach((scene,i)=>{
        const shown=i===active;
        scene.classList.toggle('is-active',shown);
        scene.setAttribute('aria-hidden',String(!shown));
        scene.toggleAttribute('inert',!shown);
      });
      count.textContent=active===last?'THE END':`${String(active+1).padStart(2,'0')} / ${String(last).padStart(2,'0')}`;
    }
    scenes[part.i].style.opacity=String(1-v.fade);
    scenes[part.i+1].style.opacity=String(v.fade);

    const carWidth=clamp(width*.3,134,220),scale=carWidth/916;
    const probe=Math.max(3,539*scale*.24);
    const before=path.getPointAtLength(Math.max(0,distance-probe));
    const after=path.getPointAtLength(Math.min(total,distance+probe));
    const heading=Math.atan2(after.y-before.y,after.x-before.x)*180/Math.PI;
    const travel=(current-anchors[0])*total;
    vehicle.style.transform=`translate3d(${p.x}px,${p.y}px,0) rotate(${heading}deg)`;
    vehicleArt.style.transform=`scale(${scale}) translate(-483.5px,-426px)`;
    rearWheel.style.transform=`rotate(${travel/(52*scale)*180/Math.PI}deg)`;
    frontWheel.style.transform=`rotate(${travel/(50*scale)*180/Math.PI}deg)`;
  }

  function animate(now) {
    const dt=Math.min(50,lastTime?now-lastTime:16);lastTime=now;
    current+= (target-current)*(1-Math.exp(-dt/120));
    if (Math.abs(target-current)<.000005) current=target;
    render();
    if (current!==target) frame=requestAnimationFrame(animate);
    else {frame=0;lastTime=0;}
  }

  /* How much of a scene a reader could take in at a position on the route: the
     larger of the two neighbouring cards' share on screen, weighted by how
     far each has faded in. The camera stands still for the first and last
     fifth of every leg, so the road between two scenes is mostly a drive: the
     van, the route and the counter, with the next card still arriving. That
     is the design, and it is good to pass through. */
  function presence(value) {
    const v=view(value),w=width*.94;
    let best=0;
    [[v.part.i,1-v.fade],[v.part.i+1,v.fade]].forEach(([k,opacity]) => {
      const left=points[k].x-width*.47+v.x,top=points[k].y-roadY+cardTop+v.y;
      const across=Math.max(0,Math.min(width,left+w)-Math.max(0,left));
      const down=Math.max(0,Math.min(height,top+cardH)-Math.max(0,top));
      best=Math.max(best,opacity*across*down/(w*cardH));
    });
    return best;
  }

  /* But it is wrong to stop in. A reader who let go of the wheel on the road
     was left with a van on a corner and no words, as still as any scene. So a
     scroll that comes to rest with no scene readable carries on, the way it
     was going, to the first position where the next one is fully up, through
     the same event the site's other pages use to ask Lenis for a move. A rest
     anywhere a scene can be read is left exactly where it is. */
  function restOn() {
    restTimer=0;
    if (held || document.hidden || !root.classList.contains('is-enhanced') || !anchors.length) return;
    const rect=root.getBoundingClientRect(),travel=root.offsetHeight-innerHeight;
    if (travel<=0 || rect.top>0 || rect.bottom<innerHeight) return;
    const from=clamp(-rect.top/travel,0,1);
    if (presence(distanceForScroll(from))>=.6) return;
    const step=heading*.0008;
    for (let progress=from;progress>=0 && progress<=1;progress+=step) {
      if (presence(distanceForScroll(progress))<.98) continue;
      const top=Math.round(rect.top+scrollY+progress*travel);
      const move=new CustomEvent('cirs-section-scroll',{cancelable:true,detail:{top,duration:.7,easing:t=>1-Math.pow(1-t,3)}});
      if (window.dispatchEvent(move)) window.scrollTo({top,behavior:'smooth'});
      return;
    }
  }
  function armRest() {
    clearTimeout(restTimer);
    restTimer=setTimeout(restOn,200);
  }

  function readScroll() {
    // Which way the reader is going, from the window and only past a few
    // pixels: Lenis lands every glide with a sub-pixel step the other way,
    // which is not the reader turning round.
    if (Math.abs(scrollY-lastY)>=4) {heading=scrollY>lastY?1:-1;lastY=scrollY;}
    armRest();
    const rect=root.getBoundingClientRect();
    document.body.classList.toggle('founder-story-visible',rect.top<innerHeight && rect.bottom>0);
    if (!root.classList.contains('is-enhanced') || !anchors.length) return;
    const travel=root.offsetHeight-window.innerHeight;
    if (travel<=0) return;
    const progress=clamp(-rect.top/travel,0,1);
    target=distanceForScroll(progress);
    if (!frame) frame=requestAnimationFrame(animate);
  }

  addEventListener('scroll',readScroll,{passive:true});
  // Not while a finger or a mouse button is down: a rest is a let-go.
  const grab = () => {held=true;};
  const release = () => {held=false;armRest();};
  addEventListener('pointerdown',grab,{passive:true});
  addEventListener('pointerup',release,{passive:true});
  addEventListener('pointercancel',release,{passive:true});
  addEventListener('resize',layout,{passive:true});
  motion.addEventListener('change',layout);
  layout();
})();
