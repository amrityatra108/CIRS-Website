import {DURATION,evaluateSequence,coverCrop} from './cirs/sequence-state.js';
import {fullscreenVertex,photoVertex,photoFragment,compositeFragment} from './cirs/shaders.js';

// The landing scene owns the renderer and RAF. This module owns only its
// temporary scenes/target and an elapsed-time evaluator, never another RAF.
export async function createCirsSequence({THREE,renderer,canvas,hero,signal,onComplete=()=>{},requestFrame=()=>{}}){
 const preparationStarted=performance.now();let preparationMs=0;
 const asset=new URL('../assets/cirs-sequence/',import.meta.url);
 const query=new URLSearchParams(location.search),debug=query.has('introDebug');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const originalParent=canvas.parentElement,originalNext=canvas.nextSibling;
 const slot=hero.querySelector('.cirs-canvas-slot');
 const photoFrame=hero.querySelector('.cirs-hero-photo-frame');
 const img=hero.querySelector('.cirs-hero-photo');
 const headings=hero.querySelector('.cirs-headings');
 const lines=[...hero.querySelectorAll('.cirs-line > span')];
 const status=hero.querySelector('#cirs-status');
 let time=0,owned=false,playing=false,disposed=false,finished=false,ready=false,failed=false;
 let width=1,height=1,oldOverflow=null,oldOverscroll=null,lastFocus=null,maskView=false,calibration=false;
 let target,photoTexture,wordTexture,revealTexture,exitTexture,photoScene,photoCamera,sheet,composite,quad,quadMaterial,photoMaterial;
 let toolbar,readout,slider,reportNode;
 const cleanup=[],resources=[];
 let compiling=false,pendingDisposal=false;
 const disposeResources=()=>{
  if(compiling){pendingDisposal=true;return;}
  resources.forEach(r=>r.dispose?.());resources.length=0;pendingDisposal=false;
 };
 let abortListener;
 const aborted=()=>disposed||Boolean(signal?.aborted);
 const abortPromise=signal?new Promise((_,reject)=>{
  abortListener=()=>reject(new DOMException('Sequence preparation cancelled','AbortError'));
  if(signal.aborted)abortListener();
  else signal.addEventListener('abort',abortListener,{once:true});
 }):null;
 // A signal may already be aborted before the first await attaches the race.
 abortPromise?.catch(()=>{});
 const awaitPreparation=promise=>abortPromise?Promise.race([promise,abortPromise]):promise;
 const timings=[],drawTimes=[],longTasks=[],runs=[],gpuTimes=[],gpuPending=[];
 const gl=renderer.getContext(),gpuTimer=debug?renderer.extensions.get('EXT_disjoint_timer_query_webgl2'):null;
 function drainGpuQueries(){
  if(!gpuTimer)return;
  while(gpuPending.length&&gl.getQueryParameter(gpuPending[0],gl.QUERY_RESULT_AVAILABLE)){
   const q=gpuPending.shift();
   if(!gl.getParameter(gpuTimer.GPU_DISJOINT_EXT)&&gpuTimes.length<1500)
    gpuTimes.push(gl.getQueryParameter(q,gl.QUERY_RESULT)/1e6);
   gl.deleteQuery(q);
  }
 }
 function discardGpuQueries(){gpuPending.forEach(q=>gl.deleteQuery(q));gpuPending.length=0;}
 let observer, recorder=null, captureCanvas=null, captureContext=null, titleSprites=[], captureStream=null;
 try{observer=new PerformanceObserver(list=>{for(const e of list.getEntries())if(owned&&longTasks.length<120)longTasks.push({start:e.startTime,duration:e.duration});});observer.observe({type:'longtask',buffered:false});}catch{}
 const listen=(el,event,fn)=>{el?.addEventListener(event,fn);cleanup.push(()=>el?.removeEventListener(event,fn));};
 const own=r=>(resources.push(r),r);
 function lock(){if(oldOverflow===null){oldOverflow=document.documentElement.style.overflow;oldOverscroll=document.documentElement.style.overscrollBehavior;document.documentElement.style.overflow='hidden';document.documentElement.style.overscrollBehavior='none';}}
 function unlock(){if(oldOverflow!==null){document.documentElement.style.overflow=oldOverflow;document.documentElement.style.overscrollBehavior=oldOverscroll;oldOverflow=null;}}
 function mount(){if(disposed)return;owned=true;finished=false;hero.dataset.introState='playing';photoFrame.style.opacity='0';headings.style.opacity='1';slot.append(canvas);canvas.setAttribute('aria-hidden','true');lock();resize(hero.clientWidth,hero.clientHeight);}
 function restoreCanvas(){if(canvas.parentElement===slot){if(originalNext?.parentElement===originalParent)originalParent.insertBefore(canvas,originalNext);else originalParent.append(canvas);}canvas.removeAttribute('aria-hidden');}
 function complete(reason='complete'){
  if(disposed||finished)return;time=DURATION;playing=false;finished=true;owned=false;
  hero.dataset.introState='complete';hero.classList.toggle('is-fallback',failed);
  photoFrame.style.opacity='1';headings.style.opacity='1';hero.querySelector('.cirs-hero-header').style.opacity='1';
  lines.forEach(l=>{l.style.transform='none';l.style.willChange='auto';});
  status.textContent=failed?'The still image is ready. Continue below.':'';
  restoreCanvas();unlock();
  // Release the full-screen temporary photo buffer. Immutable masks, photo
  // and shader programs stay cached for the explicit Replay control.
  target?.dispose();
  if(document.activeElement===hero.querySelector('#cirs-skip'))hero.querySelector('#cirs-enter')?.focus({preventScroll:true});
  if(recorder?.state==='recording')recorder.stop();
  drainGpuQueries();
  // The remaining GPU queries cannot be waited on without another frame.
  // Record their count, then retire them so replay starts with a clean run.
  runs.push({reason,...metrics()});discardGpuQueries();updateReport();onComplete(reason);
 }
 function metrics(){
  const stats=a=>{const s=a.slice().sort((x,y)=>x-y);return {count:s.length,median:s[Math.floor(s.length*.5)]||0,p95:s[Math.floor(s.length*.95)]||0,p99:s[Math.floor(s.length*.99)]||0,max:s.at(-1)||0};};
  return {time,phase:evaluateSequence(time).phase,playing,ownsCanvas:owned,ready,failed,
   preparationMs,viewport:[width,height],devicePixelRatio:devicePixelRatio,renderDPR:renderer.getPixelRatio(),browser:navigator.userAgent,
   frameIntervalsMs:stats(timings),cpuSubmissionMs:stats(drawTimes),gpuDrawMs:gpuTimer?stats(gpuTimes):null,gpuPendingQueries:gpuPending.length,longTasks:longTasks.slice(),
   renderer:{textures:renderer.info.memory.textures,geometries:renderer.info.memory.geometries,programs:renderer.info.programs?.length,drawCalls:renderer.info.render.calls},
   crop:coverCrop(width,height),maskView,calibration};
 }
 function updateReport(){if(reportNode)reportNode.textContent=JSON.stringify({current:metrics(),runs},null,2);}
 function resize(w,h){
  width=Math.max(1,w);height=Math.max(1,h);
  const crop=coverCrop(width,height);
  img.style.objectPosition=hero.classList.contains('cirs-missing-photo')?'50% 50%':crop.objectPosition;
  if(!ready)return;
  const dpr=Math.min(devicePixelRatio||1,1.5);renderer.setPixelRatio(dpr);renderer.setSize(width,height,false);
  const rw=Math.round(width*dpr),rh=Math.round(height*dpr);
  if(target.width!==rw||target.height!==rh)target.setSize(rw,rh);
  photoCamera.aspect=width/height;photoCamera.updateProjectionMatrix();
  photoMaterial.uniforms.uCropScale.value.set(...crop.scale);photoMaterial.uniforms.uCropOffset.value.set(...crop.offset);
  quadMaterial.uniforms.uViewport.value.set(width,height);
  // Keep the approved composition at desktop; only uniform scaling on phones.
  quadMaterial.uniforms.uLogoScale.value=width/height<1?1.36:1;
  if(owned){draw(time);updateReport();}
 }
 function draw(t){
  if(!ready||disposed||failed)return;
  const begin=performance.now(),state=evaluateSequence(t);
  let gpuQuery=null;
  if(gpuTimer&&playing){
   drainGpuQueries();
   if(gpuPending.length<12){gpuQuery=gl.createQuery();gl.beginQuery(gpuTimer.TIME_ELAPSED_EXT,gpuQuery);}
  }
  const heightAtZ=2*3*Math.tan(15*Math.PI/180),widthAtZ=heightAtZ*width/height;
  sheet.rotation.y=state.angle;
  sheet.scale.set(widthAtZ*state.expansion,heightAtZ*state.expansion,Math.min(widthAtZ,heightAtZ));
  sheet.position.set(.015*(1-state.opening)*widthAtZ,0,0);
  photoMaterial.uniforms.uBend.value=state.bend;
  photoMaterial.uniforms.uOpening.value=state.opening;
  photoMaterial.uniforms.uCalibration.value=calibration?1:0;
  quadMaterial.uniforms.uTime.value=t;
  quadMaterial.uniforms.uDeparture.value=state.departure;
  quadMaterial.uniforms.uMaskView.value=maskView?1:0;
  renderer.setRenderTarget(target);renderer.setClearColor(0x000000,0);renderer.clear();
  if(t>2.65)renderer.render(photoScene,photoCamera);
  renderer.setRenderTarget(null);renderer.setClearColor(0x000000,1);renderer.render(composite,newCamera);
  if(gpuQuery){gl.endQuery(gpuTimer.TIME_ELAPSED_EXT);gpuPending.push(gpuQuery);}
  state.headings.forEach((p,i)=>{lines[i].style.transform=`translate3d(${(-112*(1-p)).toFixed(5)}%,${(38*(1-p)).toFixed(5)}%,0)`;});
  headings.style.opacity=maskView?'0':'1';
  hero.querySelector('.cirs-hero-header').style.opacity=String(Math.max(0,Math.min(1,(t-5.2)/.8)));
  if(readout)readout.textContent=`${t.toFixed(3)} s · ${state.phase}`;
  if(slider)slider.value=t;
  hero.dataset.sequenceTime=t.toFixed(5);hero.dataset.sequencePhase=state.phase;
  if(recorder?.state==='recording')captureFrame(state);
  if(playing&&drawTimes.length<1500)drawTimes.push(performance.now()-begin);
 }
 let newCamera;
 function renderAt(seconds){if(disposed)return;pause();if(!owned)mount();time=Math.min(DURATION,Math.max(0,Number(seconds)||0));draw(time);updateReport();}
 function advance(dt){if(!owned||disposed)return;if(playing){const delta=Math.max(0,Number(dt)||0);time=Math.min(DURATION,time+delta);if(timings.length<1500&&delta>0)timings.push(delta*1000);}draw(time);if(playing&&time>=DURATION)complete();}
 function play(){if(disposed)return;if(failed||reduced.matches){complete('static');return;}lastFocus=document.activeElement;const keyboardReplay=lastFocus?.matches('#replay,#cirs-replay');discardGpuQueries();timings.length=0;drawTimes.length=0;longTasks.length=0;gpuTimes.length=0;time=0;playing=true;hero.scrollIntoView({behavior:'instant',block:'start'});mount();if(keyboardReplay)hero.querySelector('#cirs-skip')?.focus({preventScroll:true});draw(0);requestFrame();}
 function pause(){playing=false;updateReport();}
 function resume(){if(disposed||failed||!owned||time>=DURATION)return;playing=true;requestFrame();}
 function skip(){complete('skip');}
 listen(hero.querySelector('#cirs-skip'),'click',skip);
 listen(hero.querySelector('#cirs-replay'),'click',play);
 listen(reduced,'change',()=>{if(reduced.matches)complete('reduced-motion');});
 listen(canvas,'webglcontextlost',()=>{failed=true;complete('context-lost');});
 const api={get ownsCanvas(){return owned;},get playing(){return playing;},renderAt,seek:renderAt,advance,play,pause,resume,skip,resize,inspect:()=>({current:metrics(),runs}),destroy(){if(disposed)return;playing=false;owned=false;disposed=true;unlock();restoreCanvas();cleanup.forEach(f=>f());observer?.disconnect();if(recorder?.state==='recording')recorder.stop();captureStream?.getTracks().forEach(t=>t.stop());discardGpuQueries();disposeResources();toolbar?.remove();if(window.__cirsSequence===api)delete window.__cirsSequence;}};
 window.__cirsSequence=api;
 async function texture(name,data=true){if(debug&&query.get('introFail')==='photo'&&name==='gurudev-seated-original.png'){img.removeAttribute('src');throw new Error('Deliberate missing-photo test');}const image=new Image();image.src=new URL(name,asset);await image.decode();if(aborted()||failed)throw new Error('Sequence preparation cancelled');const tex=own(new THREE.Texture(image));tex.colorSpace=data?THREE.NoColorSpace:THREE.SRGBColorSpace;tex.minFilter=tex.magFilter=THREE.LinearFilter;tex.generateMipmaps=false;tex.needsUpdate=true;return tex;}
 try{
  if(debug&&query.has('introDelay'))await awaitPreparation(new Promise(r=>setTimeout(r,Math.min(5000,Number(query.get('introDelay'))||2000))));
  if(aborted()){api.destroy();return api;}
  [photoTexture,wordTexture,revealTexture,exitTexture]=await awaitPreparation(Promise.all([
   texture('gurudev-seated-original.png',false),texture('wordmark-data.png'),texture('reveal-order.png'),texture('exit-map.png'),document.fonts.load('900 48px "Arial Black"'),img.decode()
  ]));
  if(aborted()){api.destroy();return api;}
  target=own(new THREE.WebGLRenderTarget(1,1,{type:renderer.extensions.has('EXT_color_buffer_float')?THREE.HalfFloatType:THREE.UnsignedByteType,format:THREE.RGBAFormat,depthBuffer:false,stencilBuffer:false,minFilter:THREE.LinearFilter,magFilter:THREE.LinearFilter}));
  target.texture.colorSpace=THREE.NoColorSpace;
  photoScene=new THREE.Scene();photoCamera=new THREE.PerspectiveCamera(30,1,.1,20);photoCamera.position.z=3;
  photoMaterial=own(new THREE.ShaderMaterial({vertexShader:photoVertex,fragmentShader:photoFragment,uniforms:{uPhoto:{value:photoTexture},uBend:{value:0},uOpening:{value:0},uCropScale:{value:new THREE.Vector2(1,1)},uCropOffset:{value:new THREE.Vector2()},uCalibration:{value:0}},side:THREE.DoubleSide,depthTest:false,depthWrite:false,toneMapped:false,blending:THREE.NoBlending}));
  sheet=new THREE.Mesh(own(new THREE.PlaneGeometry(1,1,40,20)),photoMaterial);photoScene.add(sheet);
  composite=new THREE.Scene();newCamera=new THREE.Camera();
  quadMaterial=own(new THREE.ShaderMaterial({vertexShader:fullscreenVertex,fragmentShader:compositeFragment,depthTest:false,depthWrite:false,toneMapped:false,uniforms:{uPhotoSurface:{value:target.texture},uWordmark:{value:wordTexture},uReveal:{value:revealTexture},uExit:{value:exitTexture},uTime:{value:0},uLogoScale:{value:1},uDeparture:{value:0},uMaskView:{value:0},uViewport:{value:new THREE.Vector2()},uCream:{value:new THREE.Color('#f2e6d2')}}}));
  quad=new THREE.Mesh(own(new THREE.PlaneGeometry(2,2)),quadMaterial);composite.add(quad);
  // Upload and compile outside the elapsed sequence clock. Warm both passes.
  for(const tex of [photoTexture,wordTexture,revealTexture,exitTexture])renderer.initTexture(tex);
  if(aborted()){api.destroy();return api;}
  // An in-flight compile cannot be aborted safely. The parent keeps the
  // shared renderer alive until this promise settles, then disposes it.
  compiling=true;
  try{
   const compiled=await Promise.allSettled([
    Promise.resolve().then(()=>renderer.compileAsync(photoScene,photoCamera)),
    Promise.resolve().then(()=>renderer.compileAsync(composite,newCamera))
   ]);
   const error=compiled.find(result=>result.status==='rejected');
   if(error)throw error.reason;
  }
  finally{compiling=false;if(pendingDisposal)disposeResources();}
  if(aborted()){api.destroy();return api;}
  ready=true;preparationMs=performance.now()-preparationStarted;resize(hero.clientWidth,hero.clientHeight);
  const previousTarget=renderer.getRenderTarget();renderer.setRenderTarget(target);renderer.clear();renderer.render(photoScene,photoCamera);renderer.setRenderTarget(previousTarget);
  status.textContent='';hero.querySelector('.cirs-hero-header').style.opacity='0';
  if(debug)makeDebug();
 }catch(error){
  if(aborted()){api.destroy();return api;}
  console.error('CIRS preparation failed:',error);failed=true;preparationMs=performance.now()-preparationStarted;
  if(!img.complete||!img.naturalWidth){img.src=new URL('static-fallback.svg',asset);img.style.objectFit='contain';img.style.objectPosition='50% 50%';hero.classList.add('cirs-missing-photo');img.alt='CIRS';}
  status.textContent='The opening is available as a still image.';complete('asset-error');disposeResources();
 }finally{if(signal&&abortListener)signal.removeEventListener('abort',abortListener);}
 return api;
 function makeDebug(){
  toolbar=document.createElement('aside');toolbar.id='cirs-debug';toolbar.setAttribute('aria-label','Intro development controls');
  Object.assign(toolbar.style,{position:'fixed',zIndex:9999,bottom:'8px',left:'8px',right:'8px',padding:'10px',background:'#141414ed',color:'#fff',font:'12px Arial',display:'flex',gap:'8px',flexWrap:'wrap',alignItems:'center'});
  const button=(label,fn)=>{const b=document.createElement('button');b.type='button';b.textContent=label;b.style.cssText='color:#fff;background:#333;border:1px solid #777;padding:5px;cursor:pointer';b.addEventListener('click',fn);toolbar.append(b);return b;};
  button('Replay',play);button('Pause',pause);button('Resume',resume);button('Skip',skip);
  slider=document.createElement('input');slider.type='range';slider.min=0;slider.max=DURATION;slider.step=.001;slider.setAttribute('aria-label','Sequence time');slider.style.width='210px';slider.addEventListener('input',()=>renderAt(slider.value));toolbar.append(slider);
  const seek=document.createElement('input');seek.type='number';seek.min=0;seek.max=DURATION;seek.step=.01;seek.value=3.25;seek.setAttribute('aria-label','Exact seconds');seek.style.width='70px';toolbar.append(seek);button('Seek',()=>renderAt(seek.value));
  button('Coverage mask',()=>{maskView=!maskView;renderAt(time);});button('Colour test',()=>{calibration=!calibration;renderAt(time);});
  readout=document.createElement('output');toolbar.append(readout);
  button('Record sequence',recordSequence);
  button('Save frame',()=>{if(recorder?.state==='recording')return;draw(time);download(canvas.toDataURL('image/png'),`CIRS-${width}x${height}-${time.toFixed(3)}.png`);});
  button('Save hero preview',()=>{if(recorder?.state==='recording')return;prepareCapture();draw(time);captureFrame(evaluateSequence(time));download(captureCanvas.toDataURL('image/png'),`CIRS-hero-${width}x${height}.png`);captureCanvas=null;captureContext=null;titleSprites=[];});
  button('Check lifecycle',checkLifecycle);
  button('Save report',()=>download(URL.createObjectURL(new Blob([JSON.stringify(api.inspect(),null,2)],{type:'application/json'})),'cirs-runtime-report.json'));
  reportNode=document.createElement('pre');reportNode.id='cirs-runtime-report';reportNode.style.cssText='display:none';toolbar.append(reportNode);
  document.body.append(toolbar);updateReport();
  if(query.has('seek'))setTimeout(()=>renderAt(query.get('seek')),0);
 }
 function checkLifecycle(){
  const checks=[];
  for(const t of [.70,1.40,2.35,2.65,3.25,3.85,4.25,4.85,5.35,6.25]){
   renderAt(t);const stateA=JSON.stringify(evaluateSequence(time));renderAt(.15);renderAt(t);
   checks.push({test:'seek',time:t,pass:stateA===JSON.stringify(evaluateSequence(time))&&hero.dataset.sequenceTime===t.toFixed(5)});
   skip();checks.push({test:'skip',time:t,pass:!owned&&!playing&&document.documentElement.style.overflow!=='hidden'&&canvas.parentElement===originalParent});
  }
  for(let i=0;i<3;i++){play();pause();renderAt(3.25);skip();checks.push({test:'resource-cycle',cycle:i,...metrics().renderer});}
  const out={checks,viewport:[width,height],label:'Development lifecycle assertions executed against the integrated controller'};
  download(URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{type:'application/json'})),'cirs-lifecycle-checks.json');updateReport();
 }
 async function recordSequence(){
  if(recorder||!ready||!canvas.captureStream||!window.MediaRecorder)return;
  // Development export only: same rendered GPU frame plus pre-rasterised
  // DOM title masks. Nothing is rasterised/read back in the production loop.
  prepareCapture();
  captureStream=captureCanvas.captureStream(60);const chunks=[];
  const mime=['video/webm;codecs=vp9','video/webm;codecs=vp8','video/webm'].find(t=>MediaRecorder.isTypeSupported(t));
  recorder=new MediaRecorder(captureStream,{mimeType:mime,videoBitsPerSecond:10000000});
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
  recorder.onstop=()=>{download(URL.createObjectURL(new Blob(chunks,{type:'video/webm'})),`CIRS-complete-${width}x${height}.webm`);captureStream.getTracks().forEach(t=>t.stop());recorder=null;captureCanvas=null;captureContext=null;titleSprites=[];};
  recorder.start();play();
 }
 function prepareCapture(){
  titleSprites=[];
  for(const line of lines){
   const prior=line.style.transform;line.style.transform='none';
   const bounds=line.getBoundingClientRect(),clip=line.parentElement.getBoundingClientRect(),base=hero.getBoundingClientRect(),style=getComputedStyle(line);
   const sprite=document.createElement('canvas');sprite.width=Math.ceil(bounds.width*2+48);sprite.height=Math.ceil(bounds.height*2+48);
   const ctx=sprite.getContext('2d');ctx.scale(2,2);ctx.font=style.font;ctx.letterSpacing=style.letterSpacing;ctx.textBaseline='top';ctx.fillStyle='#fff';ctx.shadowColor='#0009';ctx.shadowBlur=12;ctx.shadowOffsetY=2;
   ctx.fillText(line.textContent,12,12+parseFloat(style.fontSize)*.08);line.style.transform=prior;
   titleSprites.push({sprite,x:bounds.left-base.left-12,y:bounds.top-base.top-12,w:bounds.width,h:bounds.height,clip:{x:clip.left-base.left,y:clip.top-base.top,w:clip.width,h:clip.height}});
  }
  captureCanvas=document.createElement('canvas');captureCanvas.width=Math.round(width);captureCanvas.height=Math.round(height);captureContext=captureCanvas.getContext('2d');
 }
 function captureFrame(state){
  captureContext.drawImage(canvas,0,0,width,height);
  titleSprites.forEach((s,i)=>{const p=state.headings[i];if(p<=0)return;
   captureContext.save();captureContext.beginPath();captureContext.rect(s.clip.x,s.clip.y,s.clip.w,s.clip.h);captureContext.clip();
   captureContext.drawImage(s.sprite,s.x-1.12*(1-p)*s.w,s.y+.38*(1-p)*s.h,s.sprite.width/2,s.sprite.height/2);captureContext.restore();
  });
 }
 function download(url,name){const a=document.createElement('a');a.href=url;a.download=name;a.click();if(url.startsWith('blob:'))setTimeout(()=>URL.revokeObjectURL(url),1000);}
}
