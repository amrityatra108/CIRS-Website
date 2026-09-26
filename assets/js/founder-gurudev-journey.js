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
  const last = scenes.length - 1;
  let width = 0, height = 0, roadY = 0, total = 0, points = [], anchors = [];
  let current = 0, target = 0, active = -1, frame = 0, lastTime = 0;

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
    const travelling=clamp((within-.3)/.5,0,1);
    const eased=travelling*travelling*(3-2*travelling);
    return anchors[index]+eased*(anchors[index+1]-anchors[index]);
  }

  function layout() {
    if (!motion.matches) {
      if (frame) cancelAnimationFrame(frame);
      frame=0;lastTime=0;active=-1;anchors=[];
      root.classList.remove('is-enhanced');
      world.removeAttribute('style');
      svg.removeAttribute('width');
      svg.removeAttribute('height');
      svg.removeAttribute('viewBox');
      scenes.forEach(scene => {
        scene.classList.remove('is-active');
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
    const samples=Array.from({length:4801},(_,i)=>{
      const length=total*i/4800,p=path.getPointAtLength(length);
      return {length,x:p.x,y:p.y};
    });
    anchors=points.map(point=>{
      let best=samples[0],distance=Infinity;
      for (const sample of samples) {
        const candidate=(sample.x-point.x)**2+(sample.y-point.y)**2;
        if (candidate<distance) {distance=candidate;best=sample;}
      }
      return best.length/total;
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
    const cardTop=118;
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

  function render() {
    if (!root.classList.contains('is-enhanced') || !anchors.length) return;
    current=clamp(current,anchors[0],anchors[last]);
    const distance=current*total,p=path.getPointAtLength(distance),part=segment(current);
    const framing=Math.sin(part.f*Math.PI)**2;
    const lead=framing*Math.min(80,width*.14);
    const camera=path.getPointAtLength(clamp(distance+lead,0,total));
    const cameraY=roadY-framing*190;
    world.style.transform=`translate3d(${width/2-camera.x}px,${cameraY-camera.y}px,0)`;

    let closest=0,best=Infinity;
    anchors.forEach((anchor,i)=>{
      const gap=Math.abs(anchor-current);
      if (gap<best) {best=gap;closest=i;}
    });
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
    const sceneOpacity=active===part.i
      ?1-clamp((part.f-.12)/.18,0,1)
      :clamp((part.f-.7)/.18,0,1);
    scenes[active].style.opacity=String(sceneOpacity);

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
    current+= (target-current)*(1-Math.exp(-dt/145));
    if (Math.abs(target-current)<.000005) current=target;
    render();
    if (current!==target) frame=requestAnimationFrame(animate);
    else {frame=0;lastTime=0;}
  }

  function readScroll() {
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
  addEventListener('resize',layout,{passive:true});
  motion.addEventListener('change',layout);
  if (document.fonts) document.fonts.ready.then(layout);
  layout();
})();
