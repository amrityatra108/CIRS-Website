import * as THREE from '../vendor/three.module.js';
import { createMarbleSanctuary } from './marble-sanctuary.js';
import { createSolidLogo } from './solid-logo.js?v=polished-gallium-2';
import { createLogoAudio } from './logo-audio.js?v=polished-gallium-2';
import { INTRO, logoVertexShader, logoFragmentShader } from './intro-particles.js?v=liquid-chrome-5';
import { createCirsSequence } from './cirs-sequence.js';
import { installSanctuaryReview } from './sanctuary-review.js';

// Tuning is intentionally kept here for the developer handoff.
export const SETTINGS = Object.freeze({
  entranceSeconds: INTRO.complete, desktopParticles: 90000, mobileParticles: 36000,
  pointerRadius: 0.23, force: 44, spring: 52, drag: 17,
  maxDisplacement: 0.58, maxDpr: 1.5, cameraParallax: 0,
  ivory: '#F6F0E2', sand: '#E9DFCD', ink: '#342F27', muted: '#756A5B', copper: '#A66A3F'
});

const root = document.querySelector('#spiritual');
const hero = document.querySelector('#cirs-hero');
const canvas = document.querySelector('#scene');
const replay = document.querySelector('#replay');
const experience = document.querySelector('#experience');
const announce = document.querySelector('#announcement');
const footerControls = document.querySelector('.footer-row');
footerControls.inert=true;
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const coarse = matchMedia('(pointer: coarse)');
const logoAudio=createLogoAudio({button:document.querySelector('#sound'),url:new URL('../assets/logo-gallium-hum.mp3',import.meta.url)});
const params = new URLSearchParams(location.search);
let reduced = motion.matches || params.has('reduced');
let bootStage='starting';
function setBootStage(stage){bootStage=stage;root.dataset.bootStage=stage;}
let renderer, scene, camera, sculpture, particles, material, geometry, sanctuary, orb, solidLogo, floorInvocation, sequence;
let sequencePreparation=null;
const bootAbort=new AbortController();
let rest, positions, velocities, heat, seeds, total = 0;
let width = 1, height = 1, bounds, aspect = 1, finalDistance = 8.2;
let elapsed = 0, entranceStart = 0, lastStamp = 0, raf = 0, loaded = false;
let active = !document.hidden, demoStart = -99, disposed = false;
let inView = false, failed = false;
let interactionUntil = -99, pointerValid = false, priorValid = false;
let introRuns = 0, maximumDisplacement = 0, affected = 0, rendererError = null;
let lastEvent = 0, pointerSpeed = 0, pointerTravel = 0;
const pointer = new THREE.Vector2(), smoothed = new THREE.Vector2();
const raycaster = new THREE.Raycaster();
const localPoint = new THREE.Vector3(), previousPoint = new THREE.Vector3();
const worldPoint = new THREE.Vector3(), plane = new THREE.Plane();
const normal = new THREE.Vector3(), origin = new THREE.Vector3();
const inverse = new THREE.Matrix4();
const logoCells = new Map();
let hoveringLogo=false, logoTouchedThisFrame=false, hitPriorValid=false;
let hitPrevious=new THREE.Vector3(), contactIndex=0, introCompleteAt=null;
let lastForceAt=-99;
let finalLogoCommitted=false;
const HIT_CELL=.07;
let observer, intersection, bootIntersection;
let bootRequested=false, nearView=false, heroNear=false, sanctuaryNear=false;
let resumeSequenceOnVisible=false;
let heroHandoff=null;
const cleanup=[];
function listen(target,type,handler,options){target.addEventListener(type,handler,options);cleanup.push(()=>target.removeEventListener(type,handler,options));}

function assembleModel(data) {
  const source=new Float32Array(data);
  total=Math.min(source.length/6,coarse.matches||width<650?SETTINGS.mobileParticles:SETTINGS.desktopParticles);
  rest=new Float32Array(total*3);positions=new Float32Array(total*3);velocities=new Float32Array(total*3);
  const normals=new Float32Array(total*3);heat=new Float32Array(total);seeds=new Float32Array(total);
  // Preserve the exact calligraphic orientation authored in the supplied model.
  const rotation=new THREE.Matrix4();
  const v=new THREE.Vector3(), n=new THREE.Vector3();
  for(let i=0;i<total;i++){
    const j=i*6,k=i*3;
    v.set(source[j],source[j+1],source[j+2]).applyMatrix4(rotation);
    n.set(source[j+3],source[j+4],source[j+5]).transformDirection(rotation);
    rest.set([v.x,v.y,v.z],k);normals.set([n.x,n.y,n.z],k);
    seeds[i]=((i*16807)%2147483647)/2147483647;
    seeds[i]=Math.abs(Math.sin(i*78.233+4.21)*43758.5453)%1;
  }
  positions.set(rest);
  geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));
  geometry.setAttribute('aRest',new THREE.BufferAttribute(rest,3));
  geometry.setAttribute('aNormal',new THREE.BufferAttribute(normals,3));
  geometry.setAttribute('aHeat',new THREE.BufferAttribute(heat,1).setUsage(THREE.DynamicDrawUsage));
  geometry.setAttribute('aSeed',new THREE.BufferAttribute(seeds,1));
  material=new THREE.ShaderMaterial({vertexShader:logoVertexShader,fragmentShader:logoFragmentShader,transparent:true,depthWrite:false,uniforms:{uEdge:{value:new THREE.Vector2(6,4)},uTime:{value:0},uIntro:{value:0},uDpr:{value:renderer.getPixelRatio()},uPointScale:{value:width<650?1.2:1}}});
  particles=new THREE.Points(geometry,material);particles.frustumCulled=false;particles.renderOrder=4;
  sculpture=new THREE.Group();sculpture.add(particles);scene.add(sculpture);
  let best=Infinity;
  for(let i=0;i<total;i++){
    const j=i*3,cx=Math.floor(rest[j]/HIT_CELL),cy=Math.floor(rest[j+1]/HIT_CELL),key=cx+','+cy;
    if(!logoCells.has(key))logoCells.set(key,[]);
    logoCells.get(key).push(j);
    const score=(rest[j]+.4)**2+(rest[j+1]-.55)**2;
    if(score<best){best=score;contactIndex=j;}
  }
}

function resize() {
  bounds=canvas.getBoundingClientRect();const sectionBounds=root.getBoundingClientRect();width=Math.max(1,sectionBounds.width);height=Math.max(1,sectionBounds.height);aspect=width/height;
  camera.aspect=aspect;camera.updateProjectionMatrix();
  finalDistance=9.6;
  camera.position.set(0,0,finalDistance);camera.lookAt(0,0,0);
  sanctuary?.layout(width,height,camera,sculpture);
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,SETTINGS.maxDpr));
  if(sequence?.ownsCanvas){
    const heroBounds=hero.getBoundingClientRect();
    sequence.resize(Math.max(1,heroBounds.width),Math.max(1,heroBounds.height));
  }else renderer.setSize(width,height,false);
  if(material){material.uniforms.uDpr.value=renderer.getPixelRatio();material.uniforms.uPointScale.value=aspect<.85?1.15:1;}
  priorValid=false;
  if(reduced&&loaded&&inView&&!sequence?.ownsCanvas)drawStill();
}

function replayIntro(){
  if(!loaded||failed||disposed||!sequence)return;
  cancelHeroHandoff();
  logoAudio.silence();
  hero.scrollIntoView({behavior:'instant',block:'start'});
  footerControls.inert=true;
  sequence.play();introRuns++;
  lastStamp=performance.now();
  schedule();
}

function onPointer(event){
  if(event.pointerType==='touch')return; // Leave normal page gestures available.
  if(!loaded||reduced||failed||disposed||sequence?.ownsCanvas)return;
  bounds=canvas.getBoundingClientRect();
  const now=performance.now();
  const x=(event.clientX-bounds.left)/width*2-1,y=1-(event.clientY-bounds.top)/height*2;
  const distance=pointerValid?Math.hypot(x-pointer.x,y-pointer.y):0;
  pointerSpeed=Math.min(3,distance/Math.max(.008,(now-lastEvent)/1000));
  pointerTravel+=distance;lastEvent=now;
  pointer.set(x,y);pointerValid=true;
  if(distance>.00015){interactionUntil=elapsed+.075;demoStart=-99;}
  if(root.dataset.entrance==='complete'&&projectPointer()){
    if(touchesLogo(localPoint.x,localPoint.y))logoTouchedThisFrame=true;
    if(hitPriorValid){
      const steps=Math.min(100,Math.ceil(hitPrevious.distanceTo(localPoint)/.055));
      for(let i=1;i<steps&&!logoTouchedThisFrame;i++){
        const t=i/steps;if(touchesLogo(THREE.MathUtils.lerp(hitPrevious.x,localPoint.x,t),THREE.MathUtils.lerp(hitPrevious.y,localPoint.y,t)))logoTouchedThisFrame=true;
      }
    }
    if(distance>.00015&&(logoTouchedThisFrame||touchesLogo(localPoint.x,localPoint.y)))logoAudio.movement(pointerSpeed);
    else if(!touchesLogo(localPoint.x,localPoint.y))logoAudio.silence();
    hitPrevious.copy(localPoint);hitPriorValid=true;
  }
  schedule();
}
function clearPointer(){logoAudio.silence();hoveringLogo=false;hitPriorValid=false;pointerValid=false;priorValid=false;interactionUntil=-99;pointer.set(0,0);pointerSpeed=0;schedule();}

function projectPointer(){
  sculpture.updateMatrixWorld(true);
  normal.set(0,0,1).transformDirection(sculpture.matrixWorld);
  origin.set(0,0,0).applyMatrix4(sculpture.matrixWorld);plane.setFromNormalAndCoplanarPoint(normal,origin);
  raycaster.setFromCamera(pointer,camera);
  if(!raycaster.ray.intersectPlane(plane,worldPoint))return false;
  inverse.copy(sculpture.matrixWorld).invert();localPoint.copy(worldPoint).applyMatrix4(inverse);
  return Number.isFinite(localPoint.x)&&Number.isFinite(localPoint.y);
}

function touchesLogo(x,y){
  const cx=Math.floor(x/HIT_CELL),cy=Math.floor(y/HIT_CELL);
  for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++){
    const indices=logoCells.get((cx+a)+','+(cy+b));if(!indices)continue;
    for(const j of indices){const dx=rest[j]-x,dy=rest[j+1]-y;if(dx*dx+dy*dy<.0050)return true;}
  }
  return false;
}

function updateParticles(dt,forceActive){
  const friction=Math.exp(-SETTINGS.drag*dt),cool=Math.exp(-2.2*dt);
  const sx=priorValid?previousPoint.x:localPoint.x,sy=priorValid?previousPoint.y:localPoint.y;
  const dx=localPoint.x-sx,dy=localPoint.y-sy,len2=dx*dx+dy*dy;
  const distance=Math.sqrt(len2),tx=distance>.001?dx/distance:1,ty=distance>.001?dy/distance:0;
  const radius=SETTINGS.pointerRadius+Math.min(pointerSpeed,.9)*.09,r2=radius*radius;
  const force=SETTINGS.force*(.35+Math.min(pointerSpeed,1.8)*.5);
  maximumDisplacement=0;affected=0;
  for(let i=0;i<total;i++){
    const j=i*3;let ox=positions[j]-rest[j],oy=positions[j+1]-rest[j+1],oz=positions[j+2]-rest[j+2];
    let vx=velocities[j],vy=velocities[j+1],vz=velocities[j+2];
    if(forceActive){
      const t=len2>.000001?Math.max(0,Math.min(1,((rest[j]-sx)*dx+(rest[j+1]-sy)*dy)/len2)):0;
      const rx=rest[j]-sx-dx*t,ry=rest[j+1]-sy-dy*t,d2=rx*rx+ry*ry;
      if(d2<r2){
        const w=Math.pow(1-d2/r2,2),s=seeds[i],angle=s*6.283+elapsed*2.2;
        // A short, local shear suggests softened metal rather than a burst of dust.
        vx+=(tx*.38-ry*1.55+Math.cos(angle)*.20)*force*w*dt;
        vy+=(ty*.38+rx*1.55+Math.sin(angle)*.20+.11)*force*w*dt;
        vz+=(.22+Math.sin(angle*1.7)*.42)*force*w*dt;
        heat[i]=Math.min(1,heat[i]+w*.55);affected++;
      }
    }
    vx=(vx-ox*SETTINGS.spring*dt)*friction;vy=(vy-oy*SETTINGS.spring*dt)*friction;vz=(vz-oz*SETTINGS.spring*dt)*friction;
    ox+=vx*dt;oy+=vy*dt;oz+=vz*dt;
    const length=Math.sqrt(ox*ox+oy*oy+oz*oz);
    if(length>SETTINGS.maxDisplacement){const scale=SETTINGS.maxDisplacement/length;ox*=scale;oy*=scale;oz*=scale;vx*=.6;vy*=.6;vz*=.6;}
    maximumDisplacement=Math.max(maximumDisplacement,Math.min(length,SETTINGS.maxDisplacement));
    positions[j]=rest[j]+ox;positions[j+1]=rest[j+1]+oy;positions[j+2]=rest[j+2]+oz;
    velocities[j]=vx;velocities[j+1]=vy;velocities[j+2]=vz;heat[i]*=cool;
  }
  geometry.attributes.position.needsUpdate=true;geometry.attributes.aHeat.needsUpdate=true;
  previousPoint.copy(localPoint);priorValid=forceActive;
}

function compose(intro){
  const introSeconds=reduced?INTRO.complete:(elapsed-entranceStart);
  const completed=introSeconds>=INTRO.complete;
  const settle=THREE.MathUtils.smootherstep(introSeconds,INTRO.formationStart,INTRO.complete);
  // A locked camera is essential: the room plate, plaque and emblem must agree.
  camera.position.set(0,0,finalDistance);camera.lookAt(0,0,0);
  camera.updateMatrixWorld();
  sculpture.rotation.set(0,.045,0);
  sanctuary.layout(width,height,camera,sculpture);
  sculpture.updateMatrixWorld(true);
  const viewHalfHeight=Math.tan(THREE.MathUtils.degToRad(camera.fov)*.5)*finalDistance;
  material.uniforms.uEdge.value.set(viewHalfHeight*aspect*1.05,viewHalfHeight*1.10);
  material.uniforms.uIntro.value=introSeconds;
  material.uniforms.uTime.value=elapsed;
  orb?.update({time:elapsed,introSeconds,reduced});
  floorInvocation?.update(introSeconds,aspect);
  if(completed&&root.dataset.entrance!=='complete'){
    introCompleteAt=elapsed;
    announce.textContent='Spiritual is ready. Move through the logo, or choose Experience the light.';
  }
  root.dataset.entrance=completed?'complete':'playing';
  footerControls.inert=!completed;
  root.dataset.chapter=completed?'logo':introSeconds<INTRO.orbStart?'convergence':introSeconds<INTRO.formationStart?'orb':'formation';
  sanctuary.update({time:elapsed,parallaxX:smoothed.x,parallaxY:smoothed.y,interaction:maximumDisplacement,entrance:intro});
}

function settleSanctuary(){
  if(!loaded||failed||disposed||sequence?.ownsCanvas)return;
  entranceStart=elapsed-INTRO.complete;
  positions.set(rest);velocities.fill(0);heat.fill(0);
  geometry.attributes.position.needsUpdate=true;geometry.attributes.aHeat.needsUpdate=true;
  maximumDisplacement=0;affected=0;lastForceAt=-99;
  particles.visible=false;
  pointerValid=false;priorValid=false;hitPriorValid=false;hoveringLogo=false;
  smoothed.set(0,0);pointer.set(0,0);
  compose(1);
  solidLogo?.update({introSeconds:INTRO.complete,positions,rest,total,reduced});
  finalLogoCommitted=true;
  footerControls.inert=false;
  renderer.render(scene,camera);
}

function cancelHeroHandoff(){
  if(!heroHandoff)return;
  const handoff=heroHandoff;heroHandoff=null;
  hero.classList.remove('is-auto-dissolving');hero.style.removeProperty('opacity');
  delete hero.dataset.handoff;handoff.placeholder?.remove();
  document.documentElement.style.overflow=handoff.overflow;
  document.documentElement.style.overscrollBehavior=handoff.overscroll;
}

function advanceHeroHandoff(dt){
  const handoff=heroHandoff;if(!handoff)return;
  handoff.time+=dt;
  if(handoff.time<.8){schedule();return;}
  if(!handoff.placeholder){
    hero.dataset.holdSeconds=handoff.time.toFixed(3);
    const placeholder=document.createElement('div');
    placeholder.className='cirs-handoff-placeholder';placeholder.setAttribute('aria-hidden','true');
    hero.before(placeholder);handoff.placeholder=placeholder;
    hero.classList.add('is-auto-dissolving');hero.dataset.handoff='dissolving';
    root.scrollIntoView({behavior:'instant',block:'start'});
    resize();settleSanctuary();
  }
  const p=Math.min(1,(handoff.time-.8)/1.1);
  const eased=p*p*p*(p*(p*6-15)+10);
  hero.style.opacity=String(1-eased);
  if(p<1){schedule();return;}
  hero.dataset.dissolveSeconds=(handoff.time-.8).toFixed(3);
  cancelHeroHandoff();
  root.setAttribute('tabindex','-1');root.focus({preventScroll:true});
  announce.textContent='Spiritual is ready. Move gently through the Chinmaya logo.';
  if(inView&&!reduced)schedule();
}

function onSequenceComplete(reason){
  if(disposed)return;
  if(!failed&&loaded){
    renderer.setClearColor(0xf6f0e2,0);
    resize();settleSanctuary();if(inView&&!reduced)schedule();
  }
  else footerControls.inert=false;
  announce.textContent='Spiritual is ready. Continue to the Chinmaya logo or explore the practices.';
  cancelHeroHandoff();
  if(reason==='complete'&&!reduced&&!failed){
    heroHandoff={time:0,placeholder:null,overflow:document.documentElement.style.overflow,overscroll:document.documentElement.style.overscrollBehavior};
    hero.dataset.handoff='holding';
    document.documentElement.style.overflow='hidden';document.documentElement.style.overscrollBehavior='none';
    schedule();
  }
}

function drawStill(){
  if(!loaded||!inView||failed||disposed||sequence?.ownsCanvas)return;
  settleSanctuary();
}

function frame(stamp){
  raf=0;if(!active||failed||disposed||!loaded)return;
  const realDelta=Math.max(0,(stamp-lastStamp)/1000||1/60);
  const dt=Math.min(realDelta,1/30);lastStamp=stamp;elapsed+=realDelta;
  if(heroHandoff){advanceHeroHandoff(realDelta);return;}
  if(sequence?.ownsCanvas){
    sequence.advance(realDelta);
    if(sequence.playing)schedule();
    return;
  }
  if(!inView||reduced)return;
  if(stamp-lastEvent>120)pointerSpeed=0;
  const intro=Math.min(1,(elapsed-entranceStart)/SETTINGS.entranceSeconds);
  const alpha=1-Math.exp(-4*dt);smoothed.lerp(pointer,alpha);
  compose(intro);
  let forceActive=false;
  hoveringLogo=false;
  if(intro>=1){
    if(pointerValid&&projectPointer())hoveringLogo=touchesLogo(localPoint.x,localPoint.y);
    const demoTime=elapsed-demoStart;
    if(demoTime>=0&&demoTime<2.4){
      localPoint.set(-2.0+4.0*demoTime/2.4,Math.sin(demoTime*2.8)*.62,0);pointerSpeed=1.3;forceActive=true;
    }else if(pointerValid&&elapsed<interactionUntil&&(hoveringLogo||logoTouchedThisFrame)){
      forceActive=projectPointer();
    }
    if(forceActive)lastForceAt=elapsed;
    if(forceActive||elapsed-lastForceAt<.9||maximumDisplacement>.002)
      updateParticles(dt,forceActive);
    if(forceActive&&affected>0){root.classList.add('explored');if(demoTime>=0&&demoTime<2.4)logoAudio.movement(pointerSpeed);}
  }
  const settling=intro>=1&&(elapsed-lastForceAt<.9||maximumDisplacement>.002||
    (solidLogo?.maxMask??0)>.002||(solidLogo?.liquidEnergy??0)>.002);
  if(intro<1||!finalLogoCommitted||forceActive||settling||hoveringLogo){
    solidLogo?.update({introSeconds:elapsed-entranceStart,positions,rest,total,reduced,
      cursor:forceActive?localPoint:null,
      impulse:forceActive?Math.min(.94,.60+Math.min(pointerSpeed,2)*.17):0,
      updateMask:forceActive||maximumDisplacement>.002||elapsed-lastForceAt<.3});
    if(intro>=1)finalLogoCommitted=true;
  }
  particles.visible=forceActive||maximumDisplacement>.002;
  logoTouchedThisFrame=false;
  renderer.render(scene,camera);
  const recentPointer=pointerValid&&stamp-lastEvent<240;
  const restoring=!forceActive&&(solidLogo?.liquidEnergy??0)>.002;
  if(intro<1||forceActive||elapsed-lastForceAt<.9||maximumDisplacement>.002||
    (solidLogo?.maxMask??0)>.002||restoring||recentPointer||
    smoothed.distanceToSquared(pointer)>.00001)schedule();
}
function schedule(){
  if(!raf&&active&&!failed&&loaded&&!disposed&&
      (heroHandoff||sequence?.ownsCanvas||(inView&&!reduced))){
    const now=performance.now();
    // A sleeping scene must resume on the next frame, not jump its interaction
    // clock by all the seconds it spent idle.
    if(!lastStamp||now-lastStamp>100)lastStamp=now;
    raf=requestAnimationFrame(frame);
  }
}

function playSweep(){
  if(!loaded)return;
  if(reduced){announce.textContent='The Chinmaya logo is shown in stillness because reduced motion is enabled.';return;}
  demoStart=elapsed;priorValid=false;announce.textContent='A gentle sweep of light passes through the logo and returns to stillness.';schedule();
}

function fallback(message){
  cancelHeroHandoff();
  failed=true;cancelAnimationFrame(raf);raf=0;
  try{sequence?.skip();}catch{}
  hero.classList.add('is-fallback');hero.dataset.introState='complete';
  hero.querySelector('#cirs-status').textContent='The opening is available as a still image.';
  hero.querySelector('#cirs-skip').hidden=true;
  logoAudio.silence();
  rendererError=message;document.querySelector('#fallback').hidden=false;canvas.hidden=true;
  document.querySelector('#loading').hidden=true;root.classList.add('ready','is-fallback');
  document.querySelector('#hint').textContent='A moment of stillness';
  footerControls.inert=false;root.dataset.entrance='complete';document.querySelector('#sound').disabled=true;
  replay.disabled=true;experience.disabled=true;
  announce.textContent='Spiritual. The Chinmaya logo is displayed as a still image.';
}

async function init(){
  try{
    if(params.has('introDebug')&&params.get('introFail')==='webgl')throw new Error('Deliberate renderer-unavailable recovery test');
    renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'});
    renderer.debug.onShaderError=(gl,program,vertex,fragment)=>{rendererError=[gl.getProgramInfoLog(program),gl.getShaderInfoLog(vertex),gl.getShaderInfoLog(fragment)].filter(Boolean).join(' | ');console.error(rendererError);};
    renderer.setClearColor(0xf6f0e2,0);renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
    scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(39,1,.006,70);
    resize();sanctuary=createMarbleSanctuary({THREE,scene,root});setBootStage('logo-particles');
    const response=await fetch(new URL('../assets/logo-particles.bin',import.meta.url),{signal:bootAbort.signal});
    if(!response.ok)throw new Error('A scene asset could not load.');
    const modelData=await response.arrayBuffer();
    if(disposed)return;
    assembleModel(modelData);
    setBootStage('orb-and-solid-assets');
    const results=await Promise.allSettled([createSolidLogo({THREE,parent:sculpture}),sanctuary.ready]);
    if(results.some(result=>result.status==='rejected')){
      if(results[0].status==='fulfilled')results[0].value.dispose();
      throw results.find(result=>result.status==='rejected').reason;
    }
    solidLogo=results[0].value;
    if(disposed){solidLogo.dispose();return;}
    setBootStage('compile');
    // Compile both final and intro materials before starting the real-time clock.
    solidLogo.update({introSeconds:INTRO.complete,positions,rest,total,reduced:false});
    renderer.compile(scene,camera);
    if(disposed)return;
    setBootStage('settled-sanctuary');
    entranceStart=elapsed-INTRO.complete;
    compose(1);solidLogo.update({introSeconds:INTRO.complete,positions,rest,total,reduced});
    renderer.compile(scene,camera);
    if(disposed)return;
    setBootStage('first-render');
    renderer.render(scene,camera);
    finalLogoCommitted=true;
    setBootStage('cirs-assets');
    try{
      const preparing=createCirsSequence({THREE,renderer,canvas,hero,signal:bootAbort.signal,onComplete:onSequenceComplete,requestFrame:schedule});
      sequencePreparation=preparing;
      try{sequence=await preparing;}
      finally{if(sequencePreparation===preparing)sequencePreparation=null;}
      if(disposed){sequence.destroy();return;}
      hero.dataset.introReady='true';
    }catch(error){
      if(disposed)return;
      console.warn('CIRS opening unavailable:',error);
      hero.classList.add('is-fallback');hero.dataset.introState='complete';
      hero.querySelector('#cirs-status').textContent='The opening is available as a still image.';
      hero.querySelector('#cirs-skip').hidden=true;
    }
    setBootStage('ready');
    cleanup.push(installSanctuaryReview({root,renderer,scene,camera,inspect:()=>window.__spiritual.inspect(),refresh:()=>compose(1)}));
    loaded=true;root.classList.add('ready');
    observer=new ResizeObserver(resize);observer.observe(root);observer.observe(hero);
    intersection=new IntersectionObserver(entries=>{
      inView=entries[0].isIntersecting;lastStamp=performance.now();
      if(!inView){
        if(!sequence?.ownsCanvas){cancelAnimationFrame(raf);raf=0;}
        clearPointer();
      }else if(sequence?.ownsCanvas)schedule();
      else if(reduced)drawStill();else schedule();
    });intersection.observe(root);
    const heroRect=hero.getBoundingClientRect();
    const heroVisible=heroRect.bottom>0&&heroRect.top<innerHeight;
    const directToHero=!location.hash||location.hash==='#cirs-hero';
    if(sequence&&!reduced&&!hero.dataset.introBypassed&&
       (params.has('introDebug')||(heroVisible&&directToHero))){
      replayIntro();
    }else if(sequence){
      sequence.skip();
    }else{
      resize();settleSanctuary();
    }
  }catch(error){if(disposed)return;console.error('Spiritual scene:',error);fallback(error.message);}
}

function requestBoot(){
  if(bootRequested||disposed||!active||!nearView)return;
  bootRequested=true;
  bootIntersection?.disconnect();
  init();
}

listen(root,'pointermove',onPointer,{passive:true});listen(root,'pointerleave',clearPointer);listen(root,'pointercancel',clearPointer);
listen(window,'scroll',()=>{bounds=canvas.getBoundingClientRect();clearPointer();},{passive:true});
listen(replay,'click',replayIntro);listen(experience,'click',playSweep);
listen(hero,'click',event=>{
  if(event.target.closest('a,#cirs-replay,#cirs-skip'))cancelHeroHandoff();
},true);
listen(document,'visibilitychange',()=>{
  active=!document.hidden;clearPointer();lastStamp=performance.now();
  if(!active){
    resumeSequenceOnVisible=Boolean(sequence?.playing);
    sequence?.pause();cancelAnimationFrame(raf);raf=0;
  }else if(!bootRequested)requestBoot();
  else if(sequence?.ownsCanvas){
    if(resumeSequenceOnVisible)sequence.resume();
    resumeSequenceOnVisible=false;schedule();
  }else if(heroHandoff)schedule();
  else if(inView){reduced?drawStill():schedule();}
});
listen(window,'blur',clearPointer);
listen(window,'pageshow',event=>{
  if(!event.persisted)return;
  active=!document.hidden;lastStamp=performance.now();
  if(!bootRequested)requestBoot();
  else if(sequence?.ownsCanvas){if(resumeSequenceOnVisible)sequence.resume();resumeSequenceOnVisible=false;schedule();}
  else if(heroHandoff)schedule();
  else if(loaded&&inView){reduced?drawStill():schedule();}
});
listen(window,'pagehide',()=>{
  resumeSequenceOnVisible=Boolean(sequence?.playing);
  sequence?.pause();active=false;cancelAnimationFrame(raf);raf=0;clearPointer();
});
listen(motion,'change',event=>{
  reduced=event.matches||params.has('reduced');cancelAnimationFrame(raf);raf=0;
  clearPointer();lastStamp=performance.now();if(!loaded)return;
  if(reduced){cancelHeroHandoff();if(sequence?.ownsCanvas)sequence.skip();if(inView)drawStill();}
  else if(sequence?.ownsCanvas)schedule();
  else if(inView)schedule();
});
listen(canvas,'webglcontextlost',event=>{event.preventDefault();fallback('WebGL context lost');});

function contactScreen(){
  if(!sculpture||!rest)return null;
  const p=new THREE.Vector3(rest[contactIndex],rest[contactIndex+1],0);
  sculpture.updateMatrixWorld(true);p.applyMatrix4(sculpture.matrixWorld).project(camera);
  return {x:(p.x+1)*width*.5+(bounds?.left||0),y:(1-p.y)*height*.5+(bounds?.top||0)};
}

// Read-only diagnostics make the custom interaction verifiable without adding UI.
window.__spiritual={
  inspect:()=>({bootStage,particleIntro:material?.uniforms.uIntro.value,renderedPoints:renderer?.info.render.points,loaded,reduced,active,inView,failed,introRuns,entrance:root.dataset.entrance,chapter:root.dataset.chapter,introSeconds:elapsed-entranceStart,sequence:sequence?.inspect(),hoveringLogo,arrowsRemoved:true,contactScreen:contactScreen(),resources:renderer?{...renderer.info.memory,programs:renderer.info.programs.length}:null,particleCount:total,maximumDisplacement,affected,pointerTravel,pointerSpeed,elapsed,rendererError,width,height,settings:SETTINGS,chamber:sanctuary?.inspect(),orb:orb?.inspect(),solidLogo:solidLogo?.inspect(),audio:logoAudio.inspect(),camera:camera?.position.toArray(),modelRotation:sculpture?[sculpture.rotation.x,sculpture.rotation.y]:null}),
  replay:replayIntro,
  skipIntro:()=>sequence?.skip(),
  renderIntroAt:time=>sequence?.renderAt(time),
  destroy:()=>{
    if(disposed)return;
    cancelHeroHandoff();disposed=true;bootAbort.abort();cancelAnimationFrame(raf);
    bootIntersection?.disconnect();observer?.disconnect();intersection?.disconnect();
    for(const fn of cleanup)fn();
    sequence?.destroy();logoAudio.dispose();orb?.dispose();solidLogo?.dispose();floorInvocation?.dispose();sanctuary?.dispose();
    scene?.traverse(object=>{object.geometry?.dispose();if(object.material){for(const m of Array.isArray(object.material)?object.material:[object.material])m.dispose();}});
    const sharedRenderer=renderer;
    if(sequencePreparation){
      // compileAsync may still be using the renderer; release it only after
      // the cancelled sequence has drained and disposed its own resources.
      sequencePreparation.then(pending=>{pending?.destroy();sharedRenderer?.dispose();},()=>sharedRenderer?.dispose());
    }else sharedRenderer?.dispose();
  }
};
setBootStage('waiting-for-view');
if('IntersectionObserver' in window){
  // A restored/deep-linked spiral should not initialize and compile the
  // landing WebGL scene while both the hero and sanctuary are offscreen.
  bootIntersection=new IntersectionObserver(entries=>{
    for(const entry of entries){
      if(entry.target===hero)heroNear=entry.isIntersecting;
      else if(entry.target===root)sanctuaryNear=entry.isIntersecting;
    }
    nearView=heroNear||sanctuaryNear;
    requestBoot();
  },{rootMargin:`${Math.round(window.innerHeight*.5)}px 0px`});
  bootIntersection.observe(hero);bootIntersection.observe(root);
}else{
  nearView=true;
  requestBoot();
}
