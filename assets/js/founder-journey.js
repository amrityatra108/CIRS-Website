(function(){
  "use strict";

  const root=document.querySelector("[data-founder-journey]");
  if(!root||root.dataset.founderInitialized==="true") return;
  root.dataset.founderInitialized="true";

  const reduced=matchMedia("(prefers-reduced-motion: reduce)");
  const desktop=matchMedia("(min-width: 900px)");
  if(reduced.matches||!desktop.matches||!window.gsap||!window.ScrollTrigger){
    root.classList.add("is-static");
    return;
  }

  const gsap=window.gsap;
  const ScrollTrigger=window.ScrollTrigger;
  gsap.registerPlugin(ScrollTrigger);

  const world=root.querySelector("[data-founder-world]");
  const route=root.querySelector("[data-founder-route]");
  const routeBase=root.querySelector("[data-founder-route-base]");
  const routeProgress=root.querySelector("[data-founder-route-progress]");
  const routePoints=root.querySelector("[data-founder-route-points]");
  const opening=root.querySelector("[data-founder-opening]");
  const vehicle=root.querySelector("[data-founder-vehicle]");
  const wheels=gsap.utils.toArray("[data-vehicle-wheel]",root);
  const stops=gsap.utils.toArray("[data-route-stop]",root);
  const backgrounds={
    ivory:root.querySelector('[data-founder-background="ivory"]'),
    charcoal:root.querySelector('[data-founder-background="charcoal"]'),
    sage:root.querySelector('[data-founder-background="sage"]')
  };
  const period=root.querySelector("[data-founder-period]");
  const title=root.querySelector("[data-founder-title]");
  const count=root.querySelector("[data-founder-count]");
  const total=root.querySelector("[data-founder-total]");
  const meter=root.querySelector("[data-founder-meter]");
  if(!world||!route||!routeBase||!routeProgress||!routePoints||!opening||!vehicle||stops.length<2) return;

  /* One continuous journey: horizontal, down, right, one diagonal, vertical. */
  const points=[
    [1110,1100],[1800,1100],[2500,1100],[3200,1100],[3900,1100],
    [4300,1600],[4300,2300],[4300,3000],
    [5100,3300],[5900,3300],[6700,3300],[7500,3300],[8300,3300],
    [9000,3900],[9700,4500],[10400,5000],
    [10400,5800],[10400,6500]
  ].slice(0,stops.length).map(([x,y])=>({x,y}));
  const openingPoint={x:180,y:1100};
  const clamp01=gsap.utils.clamp(0,1);
  const INTRO_END=.13;
  const MAIN_START=.145;
  const MAIN_END=.97;
  const milestonePresentation={
    "life-intro":{align:"center",viewportY:.40,maxWidth:760,offsetX:-70,offsetY:-315},
    "ernakulam-1916":{align:"center",viewportY:.44,maxWidth:840,offsetX:90,offsetY:-315},
    "freedom-movement":{align:"left",viewportY:.44,maxWidth:780,offsetX:-70,offsetY:-315},
    "rishikesh-1947":{align:"right",viewportY:.44,maxWidth:780,offsetX:90,offsetY:-315},
    "sannyasa-1949":{align:"left",viewportY:.44,maxWidth:780,offsetX:-70,offsetY:-315},
    "uttarkashi-1949":{align:"center",viewportY:.46,maxWidth:840,offsetX:420,offsetY:-315},
    "first-yajna-1951":{align:"right",viewportY:.44,maxWidth:840,offsetX:520,offsetY:-40},
    "chinmaya-mission-1953":{align:"right",viewportY:.44,maxWidth:780,offsetX:620,offsetY:-40},
    "forty-years":{align:"left",viewportY:.44,maxWidth:800,offsetX:500,offsetY:-315},
    "mahasamadhi-1993":{align:"right",viewportY:.44,maxWidth:820,offsetX:90,offsetY:-315},
    "education-transformation":{align:"center",viewportY:.50,maxWidth:960,offsetX:90,offsetY:-315}
  };
  const state={active:-1,lastProgress:0,routeLength:0,stopLengths:[],frames:[],wheelRadius:1,safeTop:96,trigger:null};

  function labelFor(stop,index){
    const heading=stop.querySelector("h2,h3");
    return stop.dataset.routeTitle||(heading?heading.textContent.replace(/\s+/g," ").trim():"Chapter "+(index+1));
  }
  function periodFor(stop){
    const year=stop.querySelector(".flife__yr");
    return stop.dataset.routePeriod||(year?year.textContent.trim():"The journey");
  }
  function unit(a,b){
    const length=Math.hypot(b.x-a.x,b.y-a.y)||1;
    return {x:(b.x-a.x)/length,y:(b.y-a.y)/length};
  }
  function roundedPath(pathPoints,radius){
    let d=`M ${pathPoints[0].x} ${pathPoints[0].y}`;
    for(let i=1;i<pathPoints.length-1;i++){
      const previous=pathPoints[i-1],point=pathPoints[i],next=pathPoints[i+1];
      const incoming=unit(previous,point),outgoing=unit(point,next);
      const r=Math.min(radius,Math.hypot(point.x-previous.x,point.y-previous.y)/3,Math.hypot(next.x-point.x,next.y-point.y)/3);
      const before={x:point.x-incoming.x*r,y:point.y-incoming.y*r};
      const after={x:point.x+outgoing.x*r,y:point.y+outgoing.y*r};
      d+=` L ${before.x.toFixed(1)} ${before.y.toFixed(1)} Q ${point.x} ${point.y} ${after.x.toFixed(1)} ${after.y.toFixed(1)}`;
    }
    const last=pathPoints[pathPoints.length-1];
    return d+` L ${last.x} ${last.y}`;
  }
  function nearestLength(target){
    const samples=900;
    let bestLength=0,bestDistance=Infinity;
    for(let i=0;i<=samples;i++){
      const length=state.routeLength*i/samples;
      const point=routeProgress.getPointAtLength(length);
      const distance=Math.hypot(point.x-target.x,point.y-target.y);
      if(distance<bestDistance){bestDistance=distance;bestLength=length;}
    }
    return bestLength;
  }
  function buildRoute(){
    const pathPoints=[openingPoint,...points];
    const d=roundedPath(pathPoints,180);
    route.setAttribute("viewBox","0 0 12200 6900");
    routeBase.setAttribute("d",d);
    routeProgress.setAttribute("d",d);
    state.routeLength=routeProgress.getTotalLength();
    routeProgress.style.strokeDasharray=String(state.routeLength);
    routeProgress.style.strokeDashoffset=String(state.routeLength);
    state.stopLengths=points.map(nearestLength);
    routePoints.replaceChildren();
    const ns="http://www.w3.org/2000/svg";
    points.forEach((point,index)=>{
      const dot=document.createElementNS(ns,"circle");
      dot.setAttribute("cx",point.x);dot.setAttribute("cy",point.y);dot.setAttribute("r","8");
      dot.setAttribute("class","route-point");dot.dataset.routePoint=String(index);
      routePoints.appendChild(dot);
    });
    state.dots=gsap.utils.toArray("[data-route-point]",routePoints);
  }
  function configFor(stop,index){
    return milestonePresentation[stop.dataset.routeId]||{
      align:index%2===0?"left":"right",viewportY:.45,maxWidth:820,
      offsetX:index%2===0?-70:90,offsetY:-315
    };
  }
  function placeStops(){
    stops.forEach((stop,index)=>{
      const point=points[index];
      const config=configFor(stop,index);
      stop.style.left=(point.x+config.offsetX)+"px";
      stop.style.top=(point.y+config.offsetY)+"px";
      stop.style.setProperty("--stop-width",config.maxWidth+"px");
      stop.dataset.founderIndex=String(index);
    });
  }
  function measureCompositions(){
    const header=document.querySelector(".header");
    const hud=root.querySelector(".founders-journey__hud");
    const side=Math.max(24,Math.min(72,innerWidth*.04));
    const safe={
      left:side,right:side,
      top:Math.max(72,(header?header.offsetHeight:56)+28),
      bottom:Math.max(48,(hud?hud.offsetHeight:34)+30)
    };
    state.safeTop=safe.top;
    root.style.setProperty("--journey-safe-block",(safe.top+safe.bottom)+"px");
    const vehicleTop=Math.min(
      innerHeight-safe.bottom-vehicle.offsetHeight-16,
      safe.top+16+opening.offsetHeight+28
    );
    root.style.setProperty("--founder-vehicle-top",Math.max(safe.top+16,vehicleTop)+"px");
    state.frames=stops.map((stop,index)=>{
      const config=configFor(stop,index);
      const width=stop.offsetWidth;
      const height=stop.offsetHeight;
      const compositionPad=16;
      const minX=safe.left+compositionPad+width/2;
      const maxX=innerWidth-safe.right-compositionPad-width/2;
      let desiredX=innerWidth/2;
      if(config.align==="left") desiredX=minX;
      if(config.align==="right") desiredX=maxX;
      desiredX=Math.max(minX,Math.min(maxX,desiredX));
      const minY=safe.top+compositionPad+height/2;
      const maxY=innerHeight-safe.bottom-compositionPad-height/2;
      const desiredY=minY>maxY?(safe.top+innerHeight-safe.bottom)/2:
        Math.max(minY,Math.min(maxY,innerHeight*config.viewportY));
      const worldX=points[index].x+config.offsetX;
      const worldY=points[index].y+config.offsetY;
      return {id:stop.dataset.routeId,x:desiredX-worldX,y:desiredY-worldY,width,height,desiredX,desiredY};
    });
  }
  function setActive(index){
    index=Math.max(0,Math.min(stops.length-1,index));
    if(index===state.active) return;
    state.active=index;
    stops.forEach((stop,i)=>{
      stop.classList.toggle("is-active",i===index);
      if(i===index) stop.classList.add("is-seen");
    });
    period.textContent=periodFor(stops[index]);
    title.textContent=labelFor(stops[index],index);
    count.textContent=String(index+1).padStart(2,"0");
  }
  function activeForPosition(position,direction){
    if(state.active<0) return 0;
    const tolerance=.035;
    let index=state.active;
    while(index<stops.length-1){
      const boundary=index+.5;
      if(position<=boundary+(direction>0?tolerance:-tolerance)) break;
      index++;
    }
    while(index>0){
      const boundary=index-.5;
      if(position>=boundary+(direction<0?-tolerance:tolerance)) break;
      index--;
    }
    return index;
  }
  function smoothstep(edge0,edge1,value){
    const x=clamp01((value-edge0)/(edge1-edge0));
    return x*x*(3-2*x);
  }
  function timelinePosition(progress){
    return clamp01((progress-MAIN_START)/(MAIN_END-MAIN_START))*(stops.length-1);
  }
  function travelProgress(fraction){
    return smoothstep(.34,.66,fraction);
  }
  function routeDistanceFor(position){
    const index=Math.min(stops.length-2,Math.floor(position));
    const fraction=index===stops.length-1?0:position-index;
    return gsap.utils.interpolate(state.stopLengths[index],state.stopLengths[index+1],travelProgress(fraction));
  }
  function cameraFor(position){
    const index=Math.min(stops.length-2,Math.floor(position));
    const fraction=index===stops.length-1?0:position-index;
    const next=Math.min(stops.length-1,index+1);
    const travel=travelProgress(fraction);
    return {
      x:gsap.utils.interpolate(state.frames[index].x,state.frames[next].x,travel),
      y:gsap.utils.interpolate(state.frames[index].y,state.frames[next].y,travel)
    };
  }
  function setStopOpacities(position,progress){
    stops.forEach((stop,index)=>{
      const distance=Math.abs(position-index);
      let opacity=distance<=.22?1:distance>=.34?0:1-smoothstep(.22,.34,distance);
      if(progress<MAIN_START) opacity=0;
      stop.style.setProperty("--stop-opacity",opacity.toFixed(3));
    });
  }
  function setBackground(mainProgress){
    const charcoal=smoothstep(.34,.39,mainProgress)*(1-smoothstep(.58,.64,mainProgress));
    const sage=smoothstep(.76,.81,mainProgress)*(1-smoothstep(.89,.94,mainProgress));
    gsap.set(backgrounds.charcoal,{opacity:charcoal});
    gsap.set(backgrounds.sage,{opacity:sage});
    gsap.set(backgrounds.ivory,{opacity:1-Math.max(charcoal,sage)});
    root.classList.toggle("tone-charcoal",charcoal>.55);
  }
  function render(progress){
    progress=clamp01(progress);
    const direction=progress>=state.lastProgress?1:-1;
    state.lastProgress=progress;
    const firstStopLength=state.stopLengths[0];
    const mainProgress=clamp01((progress-MAIN_START)/(MAIN_END-MAIN_START));
    const position=timelinePosition(progress);
    const routeDistance=progress<MAIN_START?firstStopLength:routeDistanceFor(position);
    const milestoneCamera=cameraFor(position);
    const openingCamera={x:innerWidth/2-1110,y:state.safeTop+16-555};
    const openingHandoff=smoothstep(.12,MAIN_START,progress);
    const camera={
      x:gsap.utils.interpolate(openingCamera.x,milestoneCamera.x,openingHandoff),
      y:gsap.utils.interpolate(openingCamera.y,milestoneCamera.y,openingHandoff)
    };
    gsap.set(world,{x:camera.x,y:camera.y,force3D:true});

    const introProgress=clamp01(progress/INTRO_END);
    const eased=1-Math.pow(1-introProgress,3);
    const vehicleStart=-innerWidth*.28;
    const vehicleEnd=innerWidth*1.08;
    const vehicleX=gsap.utils.interpolate(vehicleStart,vehicleEnd,eased);
    const travelled=Math.max(0,vehicleX-vehicleStart);
    const rotation=travelled/(2*Math.PI*state.wheelRadius)*360;
    if(progress<INTRO_END){
      vehicle.classList.remove("is-gone");
      gsap.set(vehicle,{x:vehicleX,y:0,opacity:1-smoothstep(.105,.13,progress),force3D:true});
      gsap.set(wheels,{rotation});
    }else{
      vehicle.classList.add("is-gone");
    }
    gsap.set(opening,{opacity:1-smoothstep(.075,.12,progress)});
    root.classList.toggle("is-opening",progress<MAIN_START);

    const drawn=progress<MAIN_START?firstStopLength*clamp01(progress/.11):routeDistance;
    routeProgress.style.strokeDashoffset=String(state.routeLength-drawn);
    const active=activeForPosition(position,direction);
    setActive(active);
    setStopOpacities(position,progress);
    if(progress<MAIN_START){period.textContent="1996";title.textContent="CIRS begins";count.textContent="00";}
    state.dots.forEach((dot,index)=>dot.classList.toggle("is-passed",state.stopLengths[index]<=drawn));
    meter.style.transform="scaleX("+mainProgress+")";
    setBackground(mainProgress);
  }
  function mount(){
    root.style.setProperty("--founder-journey-height",innerWidth<1100?"12600px":"13800px");
    root.classList.add("is-enhanced","is-camera-moving");
    total.textContent=String(stops.length).padStart(2,"0");
    buildRoute();
    placeStops();
    measureCompositions();
    state.wheelRadius=Math.max(1,wheels[0].getBoundingClientRect().width/2);
    stops.forEach((stop,index)=>{
      stop.classList.toggle("is-near",index===1);
      if(index===0) stop.classList.add("is-seen");
    });
    setActive(0);
    render(0);
    state.trigger=ScrollTrigger.create({
      id:"founder-world",trigger:root,start:"top top",end:"bottom bottom",scrub:true,
      invalidateOnRefresh:true,
      onEnter:()=>document.body.classList.add("founder-journey-active"),
      onEnterBack:()=>document.body.classList.add("founder-journey-active"),
      onLeave:()=>{document.body.classList.remove("founder-journey-active");root.classList.remove("is-camera-moving");},
      onLeaveBack:()=>{document.body.classList.remove("founder-journey-active");root.classList.remove("is-camera-moving");},
      onUpdate:self=>{root.classList.add("is-camera-moving");render(self.progress);},
      onRefresh:()=>{
        state.wheelRadius=Math.max(1,wheels[0].getBoundingClientRect().width/2);
        measureCompositions();
      }
    });
  }

  mount();
  let resizeTimer;
  const onResize=()=>{
    clearTimeout(resizeTimer);
    resizeTimer=setTimeout(()=>{
      if(!desktop.matches||reduced.matches){location.reload();return;}
      state.wheelRadius=Math.max(1,wheels[0].getBoundingClientRect().width/2);
      measureCompositions();
      ScrollTrigger.refresh();
    },180);
  };
  addEventListener("resize",onResize,{passive:true});
  addEventListener("load",()=>ScrollTrigger.refresh(),{once:true});
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(()=>ScrollTrigger.refresh());
  addEventListener("pagehide",()=>{
    clearTimeout(resizeTimer);
    removeEventListener("resize",onResize);
    if(state.trigger) state.trigger.kill();
  },{once:true});
})();
