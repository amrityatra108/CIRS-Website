import {getJourneyLayout,measureJourneyLayout,evaluateJourneyBridge,evaluateLivePortal,clamp01,smooth} from './journey-layout.js';
// Parent owns scroll and chapter progress. The child only sends navigation intent.
const host=document.querySelector('#crossroads-helix');
const frame=host.querySelector('iframe');
const reviewParams=new URLSearchParams(location.search),childURL=new URL(frame.src);
if(reviewParams.has('journeyFail'))childURL.searchParams.set('journeyFail','1');
if(/^(localhost|127\.0\.0\.1)$/.test(location.hostname)&&(reviewParams.has('journeyDebug')||reviewParams.has('vineDebug')))childURL.searchParams.set('vineDebug','1');
if(childURL.href!==frame.src)frame.src=childURL.href;
const tapovan=document.querySelector('#tapovan-journey');
const mountainStage=tapovan.querySelector('.tapovan-sticky');
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
const destination=document.createElement('div');destination.className='journey-destination';
host.append(destination);destination.append(frame);
const fallback=document.createElement('div');fallback.className='journey-fallback';fallback.innerHTML='<p hidden>The painted garden is ready. <a href="crossroads-ivory-helix-v2.html#chapters">Explore the seventeen practices</a></p>';destination.prepend(fallback);
fallback.querySelector('a').href=new URL('#chapters',childURL).href;
const mistViewport=document.createElement('div');mistViewport.className='journey-mist-viewport';mistViewport.setAttribute('aria-hidden','true');mistViewport.innerHTML='<div class="journey-mist"></div>';document.body.append(mistViewport);
let child=null,childDocument=null,resizeObserver=null,nativeChildScrollTo=null;
let navigationTarget=null,navigationResetTimer=0,childMax=0,childJourneySpan=1,hostHeight=0,disposed=false,pageVisible=false;
let portalLocked=false,lockedParentY=0,portalDriverRaf=0,handoff=0,sceneReady=false,prepareStarted=false;
let scheduled=0,lastActive=null,lastPreparedProgress=null,connectionDocument=null,connectionGeneration=0;
let measuredWindowWidth=innerWidth,measuredWindowHeight=innerHeight,lastStableScrollY=scrollY;
let entryHandoff=0;
let portalViewport={width:innerWidth,height:innerHeight},portalPose=null,lastPreviewVisible=null,lastPreviewUI=null;
const introHero=document.querySelector('#cirs-hero');
const introObserver=new MutationObserver(()=>scheduleSync());
if(introHero)introObserver.observe(introHero,{attributes:true,attributeFilter:['data-intro-state']});
const clamp=(value,low,high)=>Math.max(low,Math.min(high,value));
const sectionTop=()=>getJourneyLayout().helixStart;
function measureSectionBoundary(){measureJourneyLayout();}
function updateHandoff(){
 // Browser scroll positions are rounded to device pixels, while measured
 // boundaries may be fractional. Treat the nearest reachable pixel as the
 // endpoint so a completed reveal does not leave chapter controls disabled.
 const l=getJourneyLayout(),p=l.isStatic||scrollY>=Math.round(l.bridgeEnd)?1:clamp01((scrollY-l.bridgeStart)/(l.bridgeEnd-l.bridgeStart));
 const state=evaluateLivePortal(p,portalViewport.width,portalViewport.height);portalPose=state;handoff=p;
 mountainStage.style.setProperty('--tapovan-ui-opacity',String(l.isStatic?1:1-smooth((p-.10)/.35)));
 const entry=l.isStatic?1:clamp01((scrollY-l.entryStart)/(l.entryEnd-l.entryStart));
 const entryState=evaluateJourneyBridge(entry);entryHandoff=entry;
 const entering=!l.isStatic&&scrollY>=l.entryStart&&scrollY<l.entryEnd;
 mountainStage.style.setProperty('--mountain-reveal',`${entryState.reveal*100}%`);
 mountainStage.classList.toggle('is-entry-reveal',entering);
 mountainStage.classList.toggle('is-entry-complete',entryState.finished||l.isStatic);
 document.documentElement.dataset.sanctuaryBridge=entering?'active':entry===1?'complete':'before';
 destination.style.setProperty('--portal-clip',state.clipPath);
 destination.classList.toggle('is-complete',state.finished||l.isStatic);
 destination.style.pointerEvents=(state.finished||l.isStatic)?'':'none';
 // The veil belongs only to sanctuary arrival. The exit is an unobscured,
 // geometric window into the actual stationary child scene.
 mistViewport.classList.toggle('is-visible',!l.isStatic&&entering);
 mistViewport.style.setProperty('--veil-opacity',String(entryState.veil*.48));
 mistViewport.style.setProperty('--veil-lift',`${entryState.lift}%`);
 mistViewport.style.setProperty('--veil-drift',`${entryState.drift}%`);
 frame.style.visibility=sceneReady?'visible':'hidden';
 const introDone=document.querySelector('#cirs-hero')?.dataset.introState==='complete';
 const near=introDone||scrollY+innerHeight>=l.tapovanStart;
 if(near&&!prepareStarted){frame.loading='eager';prepareScene();}
 pageVisible=!document.hidden&&scrollY+innerHeight>l.hostTop&&scrollY<l.hostTop+hostHeight;
 const active=pageVisible&&(state.finished||l.isStatic)&&!portalLocked&&sceneReady;
 if(active!==lastActive){child?.CrossroadsHelix?.setPageVisible(active);lastActive=active;}
 const preview=pageVisible&&!state.finished&&!l.isStatic&&p>0&&!portalLocked&&sceneReady;
 if(preview!==lastPreviewVisible){child?.CrossroadsHelix?.setTransitionPreview(preview);lastPreviewVisible=preview;}
 const uiOpacity=l.isStatic?1:state.uiOpacity;
 if(uiOpacity!==lastPreviewUI){child?.CrossroadsHelix?.setPreviewUI(uiOpacity);lastPreviewUI=uiOpacity;}
 if(sceneReady&&!state.finished&&!l.isStatic&&lastPreparedProgress!==0){child?.CrossroadsHelix?.holdInitial();lastPreparedProgress=0;}
 updateDebug();
}
async function prepareScene(){
 if(prepareStarted||!child?.CrossroadsHelix)return;
 prepareStarted=true;
 const preparingChild=child.CrossroadsHelix,preparingDocument=childDocument,generation=connectionGeneration;
 const isCurrent=()=>!disposed&&generation===connectionGeneration&&preparingDocument===childDocument&&frame.contentDocument===preparingDocument;
 try{
   const result=await preparingChild.prepare();
   if(!isCurrent())return;
   sceneReady=Boolean(result?.ready);fallback.hidden=sceneReady;
   if(!sceneReady)fallback.querySelector('p').hidden=false;
   lastActive=null;lastPreparedProgress=null;lastPreviewVisible=null;lastPreviewUI=null;measure();
 }catch(error){if(!isCurrent())return;console.warn('Spiral preparation failed:',error);fallback.querySelector('p').hidden=false;}
}
function measure(){
 if(disposed)return;
 const previous=getJourneyLayout(),previousMax=childMax;
 const windowChanged=innerWidth!==measuredWindowWidth||innerHeight!==measuredWindowHeight;
 // Scroll anchoring can move scrollY before the resize event/observer arrives.
 // Preserve the last position recorded in the old measured viewport instead.
 const previousY=windowChanged?lastStableScrollY:scrollY;
 measureSectionBoundary();
 const nextLayout=getJourneyLayout();
 portalViewport={width:destination.clientWidth||innerWidth,height:destination.clientHeight||nextLayout.viewportHeight};
 if(childDocument){
   const height=Math.max(childDocument.documentElement.scrollHeight,childDocument.body.scrollHeight,child.innerHeight);
   childMax=Math.max(0,height-child.innerHeight);
   const journey=childDocument.querySelector('#journey'),stage=childDocument.querySelector('.stage');
   childJourneySpan=Math.max(1,(journey?.offsetHeight||1)-(stage?.offsetHeight||0));
   host.style.height=`${height+Math.max(0,sectionTop()-getJourneyLayout().hostTop)}px`;
 }
 hostHeight=host.offsetHeight;
 if(previous&&(windowChanged||previous.viewportHeight!==nextLayout.viewportHeight)&&!previous.isStatic&&!nextLayout.isStatic&&previousY>=previous.entryStart){
   const remapped=previousY<=previous.entryEnd?nextLayout.entryStart+(previousY-previous.entryStart)/Math.max(1,previous.entryEnd-previous.entryStart)*(nextLayout.entryEnd-nextLayout.entryStart):previousY<=previous.helixStart?nextLayout.tapovanStart+(previousY-previous.tapovanStart)/previous.viewportHeight*nextLayout.viewportHeight:nextLayout.helixStart+(previousY-previous.helixStart)/Math.max(1,previousMax)*childMax;
   if(portalLocked)lockedParentY=remapped;
   window.scrollTo({top:remapped,behavior:'instant'});
 }
 measuredWindowWidth=innerWidth;measuredWindowHeight=innerHeight;
 lastStableScrollY=scrollY;
 syncChildFromParent();
}
function rememberStableScroll(){
 if(innerWidth===measuredWindowWidth&&innerHeight===measuredWindowHeight)lastStableScrollY=scrollY;
}
function syncChildFromParent(){
 rememberStableScroll();
 updateHandoff();if(!child||disposed)return;
 if(portalLocked){if(Math.abs(scrollY-lockedParentY)>1)window.scrollTo({top:lockedParentY,behavior:'instant'});return;}
 if(navigationTarget!==null&&Math.abs(scrollY-navigationTarget)<=1)releaseNavigation();
 const next=clamp(scrollY-sectionTop(),0,childMax);
 if(Math.abs(child.scrollY-next)>.25)nativeChildScrollTo(0,next);
 const progress=clamp01(next/childJourneySpan);
 child.CrossroadsHelix?.setExternalProgress(handoff<1?0:progress);
 lastPreparedProgress=handoff<1?0:progress;
}
function scheduleSync(){rememberStableScroll();if(!scheduled&&!disposed)scheduled=requestAnimationFrame(()=>{scheduled=0;syncChildFromParent();});}
function navigateToOffset(offset,behavior='smooth'){
 navigationTarget=sectionTop()+clamp(offset,0,childMax);
 clearTimeout(navigationResetTimer);navigationResetTimer=setTimeout(releaseNavigation,2500);
 window.scrollTo({top:navigationTarget,behavior:reducedMotion.matches?'instant':behavior});
}
function handleChildAnchor(event){
 const anchor=event.target.closest?.('a[href^="#"]');
 if(!anchor||event.defaultPrevented||portalLocked)return;
 const target=childDocument.querySelector(anchor.getAttribute('href'));
 if(!target)return;
 event.preventDefault();navigateToOffset(target.getBoundingClientRect().top+child.scrollY);
}
function navigateToProgress(progress){
 navigationTarget=sectionTop()+clamp01(progress)*childJourneySpan;
 clearTimeout(navigationResetTimer);navigationResetTimer=setTimeout(releaseNavigation,2500);
 window.scrollTo({top:navigationTarget,behavior:reducedMotion.matches?'instant':'smooth'});
}
let debugOutput=null,debugRange=null,entryRange=null;
function updateDebug(){
 if(!debugOutput)return;
 const data={...getJourneyLayout(),parentY:scrollY,childY:child?.scrollY??null,childMax,sceneReady,preparing:prepareStarted&&!sceneReady,entryHandoff,handoff,aperture:portalPose,preview:lastPreviewVisible,active:lastActive,portalLocked,resources:child?.CrossroadsHelix?.resourceCounts?.()||null};
 if(debugOutput){debugOutput.value=`Entry ${entryHandoff.toFixed(3)} · Exit ${handoff.toFixed(3)} · ${sceneReady?'ready':'preparing'}`;debugRange.value=String(handoff);entryRange.value=String(entryHandoff);document.querySelector('#journey-runtime-report').textContent=JSON.stringify(data,null,2);}
}
if(new URLSearchParams(location.search).has('journeyDebug')){
 const ui=document.createElement('div');ui.className='journey-debug';ui.innerHTML='<label>Entry <input aria-label="Sanctuary bridge progress" type="range" min="0" max="1" step=".01" value="0"></label><label>Exit <input aria-label="Bridge progress" type="range" min="0" max="1" step=".01" value="0"></label><output></output><button type="button" data-entry-cross="20">20 entry crossings</button><button type="button" data-cross="20">20 crossings</button><button type="button" data-portals>Check 17 chapter returns</button><button type="button" data-save>Save journey report</button><pre id="journey-runtime-report" hidden></pre>';
 document.body.append(ui);debugOutput=ui.querySelector('output');debugRange=ui.querySelector('[aria-label="Bridge progress"]');entryRange=ui.querySelector('[aria-label="Sanctuary bridge progress"]');
 entryRange.addEventListener('input',()=>{const l=getJourneyLayout();window.scrollTo({top:l.entryStart+Number(entryRange.value)*(l.entryEnd-l.entryStart),behavior:'instant'});syncChildFromParent();});
 ui.querySelector('[data-entry-cross]').addEventListener('click',async event=>{const button=event.currentTarget;button.disabled=true;const samples=[];for(let i=0;i<40&&!disposed;i++){const l=getJourneyLayout();window.scrollTo({top:i%2?l.entryStart:l.entryEnd,behavior:'instant'});syncChildFromParent();await new Promise(resolve=>setTimeout(resolve,80));samples.push({entry:entryHandoff,videoTime:tapovan.querySelector('video').currentTime,presentedTime:Number(tapovan.dataset.presentedTime||0),presentationSource:tapovan.dataset.frameSource||'poster',resources:child?.CrossroadsHelix?.inspect().resources||null});}ui.dataset.entryCrossingReport=JSON.stringify({crossings:20,samples});button.disabled=false;});
 debugRange.addEventListener('input',()=>{const l=getJourneyLayout();window.scrollTo({top:l.bridgeStart+Number(debugRange.value)*(l.bridgeEnd-l.bridgeStart),behavior:'instant'});syncChildFromParent();});
 ui.querySelector('[data-cross]').addEventListener('click',async event=>{const button=event.currentTarget;button.disabled=true;const samples=[],phases=[0,.15,.3,.5,.7,.85,1];for(let i=0;i<20&&!disposed;i++){for(const p of [...phases,...phases.slice(0,-1).reverse()]){const l=getJourneyLayout();window.scrollTo({top:l.bridgeStart+p*(l.bridgeEnd-l.bridgeStart),behavior:'instant'});syncChildFromParent();await new Promise(resolve=>setTimeout(resolve,20));const state=child?.CrossroadsHelix?.inspect();samples.push({cycle:i+1,aperture:portalPose,progress:state?.progress??null,preview:lastPreviewVisible,resources:state?.resources||null});}}ui.dataset.crossingReport=JSON.stringify({crossings:20,phases,samples});button.disabled=false;});
 ui.querySelector('[data-portals]').addEventListener('click',async event=>{
   const button=event.currentTarget;button.disabled=true;const results=[];
   const until=async test=>{const start=performance.now();while(!test()&&performance.now()-start<6000)await new Promise(resolve=>setTimeout(resolve,40));return test();};
   for(let i=0;i<17&&!disposed;i++){
     navigateToProgress(i/16);const reached=await until(()=>Math.abs((child?.CrossroadsHelix?.inspect().progress??-1)-i/16)<.0003);
     if(!reached){results.push({chapter:i+1,reached:false});break;}
     const before=scrollY;childDocument.querySelector('.active-chapter')?.click();
     const opened=await until(()=>childDocument.querySelector('#chapter-dialog')?.classList.contains('is-open'));
     const title=childDocument.querySelector('#chapter-dialog h2')?.textContent;
     childDocument.querySelector('#chapter-dialog .dialog-close')?.click();
     const closed=await until(()=>!childDocument.querySelector('#chapter-dialog')?.open);
     results.push({chapter:i+1,reached,title,opened,closed,restored:Math.abs(scrollY-before)<1,resources:child?.CrossroadsHelix?.inspect().resources||null});
   }
   ui.dataset.portalReport=JSON.stringify(results);button.disabled=false;
 });
 ui.querySelector('[data-save]').addEventListener('click',()=>{updateDebug();const blob=new Blob([JSON.stringify({journey:JSON.parse(document.querySelector('#journey-runtime-report').textContent),entryCrossings:JSON.parse(ui.dataset.entryCrossingReport||'null'),crossings:JSON.parse(ui.dataset.crossingReport||'null'),portals:JSON.parse(ui.dataset.portalReport||'null'),helix:child?.CrossroadsHelix?.inspect()},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='journey-runtime-report.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
}
function releaseNavigation() {
  navigationTarget = null;
  clearTimeout(navigationResetTimer);
}

// The existing portal flight deliberately uses this one parent driver while
// background chapter motion is locked; the child does not schedule a duplicate.
function stopPortalDriver() {
  if (portalDriverRaf) cancelAnimationFrame(portalDriverRaf);
  portalDriverRaf = 0;
}
function startPortalDriver() {
  if (disposed || !child?.CrossroadsHelix?.advancePortal) return false;
  if (portalDriverRaf) return true;
  const tick = () => {
    portalDriverRaf = 0;
    if (!portalLocked || disposed) return;
    try {
      if (child?.CrossroadsHelix?.advancePortal())
        portalDriverRaf = requestAnimationFrame(tick);
    } catch (error) {
      console.error('Crossroads portal driver:', error);
    }
  };
  portalDriverRaf = requestAnimationFrame(tick);
  return true;
}

let touchY=null,touchLastAt=0,touchVelocity=0,touchMomentumRaf=0;
function stopTouchMomentum(){if(touchMomentumRaf)cancelAnimationFrame(touchMomentumRaf);touchMomentumRaf=0;touchVelocity=0;}
function startTouchMomentum(){
 if(reducedMotion.matches||Math.abs(touchVelocity)<.10||portalLocked||document.hidden)return;
 let last=performance.now();
 const tick=now=>{
  touchMomentumRaf=0;if(disposed||portalLocked||document.hidden)return;
  const dt=Math.min(32,now-last);last=now;
  const before=scrollY;window.scrollBy({top:touchVelocity*dt,behavior:'instant'});
  touchVelocity*=Math.exp(-dt/230);
  if(Math.abs(touchVelocity)>.012&&Math.abs(scrollY-before)>.1)touchMomentumRaf=requestAnimationFrame(tick);
 };
 touchMomentumRaf=requestAnimationFrame(tick);
}
const controlTarget=target=>target.closest?.('input,textarea,select,[contenteditable="true"]');
function handleWheel(event) {
  stopTouchMomentum();
  if(controlTarget(event.target))return;
  if (portalLocked) {
    const chapter = childDocument.querySelector('#chapter-dialog[open]');
    if (chapter?.classList.contains('is-open') && chapter.contains(event.target)) return;
    event.preventDefault();
    return;
  }
  if (event.ctrlKey || childDocument.querySelector('dialog[open]')) return;
  event.preventDefault();
  releaseNavigation();
  const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? window.innerHeight : 1;
  window.scrollBy({ top: event.deltaY * unit, left: event.deltaX * unit, behavior: 'instant' });
}

function handleTouchStart(event) {
  stopTouchMomentum();touchLastAt=event.timeStamp;
  if(controlTarget(event.target)){touchY=null;return;}
  if (portalLocked) { touchY = null; return; }
  releaseNavigation();
  touchY = event.touches.length === 1 ? event.touches[0].clientY : null;
}
function handleTouchMove(event) {
  if (portalLocked) {
    const chapter = childDocument.querySelector('#chapter-dialog[open]');
    if (chapter?.classList.contains('is-open') && chapter.contains(event.target)) return;
    event.preventDefault();
    return;
  }
  if (touchY === null || event.touches.length !== 1 || childDocument.querySelector('dialog[open]')) return;
  const next = event.touches[0].clientY;
  const delta = touchY - next;
  touchY = next;
  const elapsed=Math.max(8,event.timeStamp-touchLastAt);touchLastAt=event.timeStamp;
  touchVelocity=touchVelocity*.35+clamp(delta/elapsed,-2.4,2.4)*.65;
  if (Math.abs(delta) < 1) return;
  event.preventDefault();
  window.scrollBy({ top: delta, behavior: 'instant' });
}
function handleTouchEnd(event) { touchY=null;if(event?.type==='touchcancel')stopTouchMomentum();else startTouchMomentum(); }
function handleKeyboard(event) {
  stopTouchMomentum();
  if (portalLocked) {
    const chapter = childDocument.querySelector('#chapter-dialog[open]');
    if (chapter?.classList.contains('is-open') && chapter.contains(event.target)) return;
    if (['ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(event.key))
      event.preventDefault();
    return;
  }
  releaseNavigation();
  if (childDocument.querySelector('dialog[open]') ||
      /^(INPUT|TEXTAREA|SELECT|BUTTON)$/.test(event.target.tagName) ||
      event.altKey || event.ctrlKey || event.metaKey) return;
  const amount = event.key === 'ArrowDown' ? 56 :
    event.key === 'ArrowUp' ? -56 :
    event.key === 'PageDown' ? window.innerHeight * .85 :
    event.key === ' ' ? window.innerHeight * (event.shiftKey ? -.85 : .85) :
    event.key === 'PageUp' ? -window.innerHeight * .85 : null;
  if (amount !== null) {
    event.preventDefault();
    window.scrollBy({ top: amount, behavior: 'instant' });
  } else if (event.key === 'Home' || event.key === 'End') {
    event.preventDefault();
    window.scrollTo({ top: sectionTop() + (event.key === 'End' ? childMax : 0), behavior: 'instant' });
  }
}

function disconnectChildEvents(){
  resizeObserver?.disconnect();resizeObserver=null;
  child?.removeEventListener('resize',measure);
  connectionDocument?.removeEventListener('wheel',handleWheel);
  connectionDocument?.removeEventListener('touchstart',handleTouchStart);
  connectionDocument?.removeEventListener('touchmove',handleTouchMove);
  connectionDocument?.removeEventListener('touchend',handleTouchEnd);
  connectionDocument?.removeEventListener('touchcancel',handleTouchEnd);
  connectionDocument?.removeEventListener('keydown',handleKeyboard);
  connectionDocument?.removeEventListener('click',handleChildAnchor);
}

function connect() {
  if (disposed) return;
  try {
    const nextChild=frame.contentWindow,nextDocument=frame.contentDocument;
    if(!nextChild?.CrossroadsHelix||!nextDocument?.body)return;
    if(connectionDocument===nextDocument)return;
    disconnectChildEvents();
    // A new iframe document owns fresh resources. Old preparation results and
    // visibility decisions cannot be applied to its replacement scene.
    connectionGeneration++;
    sceneReady=false;prepareStarted=false;
    lastActive=lastPreparedProgress=lastPreviewVisible=lastPreviewUI=null;
    fallback.hidden=false;fallback.querySelector('p').hidden=true;
    frame.style.visibility='hidden';
    if(portalLocked){portalLocked=false;stopPortalDriver();releaseNavigation();stopTouchMomentum();touchY=null;}
    child=nextChild;childDocument=nextDocument;
    connectionDocument=childDocument;
    nativeChildScrollTo = child.scrollTo.bind(child);
    child.CrossroadsHelix?.setExternalProgress(0);
    child.CrossroadsHelix?.setPageVisible(false);
    child.addEventListener('resize', measure, { passive: true });
    childDocument.addEventListener('wheel', handleWheel, { passive: false });
    childDocument.addEventListener('touchstart', handleTouchStart, { passive: true });
    childDocument.addEventListener('touchmove', handleTouchMove, { passive: false });
    childDocument.addEventListener('touchend', handleTouchEnd, { passive: true });
    childDocument.addEventListener('touchcancel', handleTouchEnd, { passive: true });
    childDocument.addEventListener('keydown', handleKeyboard);
    childDocument.addEventListener('click',handleChildAnchor);
    resizeObserver = new ResizeObserver(measure);
    resizeObserver.observe(childDocument.documentElement);
    resizeObserver.observe(childDocument.body);
    resizeObserver.observe(tapovan);
    measure();
  } catch (error) {
    console.error('Crossroads scroll connection:', error);
  }
}

frame.addEventListener('load', connect);
window.addEventListener('scroll', scheduleSync, { passive: true });
document.addEventListener('visibilitychange',scheduleSync);
window.addEventListener('pageshow',measure);
window.addEventListener('cirs:tapovan-mode',measure);
window.addEventListener('resize', measure, { passive: true });
function blockParentWheel(event) { if (portalLocked) event.preventDefault(); }
function blockParentTouch(event) { if (portalLocked) event.preventDefault(); }
function blockParentKey(event) {
  if (portalLocked && ['ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(event.key))
    event.preventDefault();
}
window.addEventListener('wheel', blockParentWheel, { passive: false, capture: true });
window.addEventListener('touchmove', blockParentTouch, { passive: false, capture: true });
window.addEventListener('keydown', blockParentKey, true);
window.__crossroadsEmbed = {
  startPortalDriver,
  navigateToProgress,
  navigateToOffset,
  stopPortalDriver,
  setPortalLock(locked) {
    if (portalLocked === Boolean(locked)) return;
    portalLocked = Boolean(locked);
    if (portalLocked) {
      stopTouchMomentum();
      lockedParentY = window.scrollY;
      releaseNavigation();
      touchY = null;
    } else {
      stopPortalDriver();
      window.scrollTo({ top: lockedParentY, behavior: 'instant' });
      syncChildFromParent();
    }
  },
  inspect: () => ({ready:sceneReady,parentY:scrollY,childY:child?.scrollY??null,childMax,sectionTop:sectionTop(),height:host.offsetHeight,entryHandoff,handoff,aperture:portalPose,preview:lastPreviewVisible,...getJourneyLayout()}),
  destroy: () => {
    if (disposed) return;
    disposed = true;
    frame.removeEventListener('load', connect);
    window.removeEventListener('scroll', scheduleSync);
    document.removeEventListener('visibilitychange',scheduleSync);
    window.removeEventListener('pageshow',measure);
    window.removeEventListener('cirs:tapovan-mode',measure);
    cancelAnimationFrame(scheduled);
    mistViewport.remove();
    child?.CrossroadsHelix?.setTransitionPreview(false);
    child?.CrossroadsHelix?.setPageVisible(false);
    child?.CrossroadsHelix?.setPreviewUI(1);
    mountainStage.classList.remove('is-entry-reveal','is-entry-complete');
    mountainStage.style.removeProperty('--mountain-reveal');
    mountainStage.style.removeProperty('--tapovan-ui-opacity');
    delete document.documentElement.dataset.sanctuaryBridge;
    introObserver.disconnect();
    window.removeEventListener('resize', measure);
    window.removeEventListener('wheel', blockParentWheel, true);
    window.removeEventListener('touchmove', blockParentTouch, true);
    window.removeEventListener('keydown', blockParentKey, true);
    disconnectChildEvents();
    clearTimeout(navigationResetTimer);
    stopPortalDriver();
    stopTouchMomentum();
    touchY = null;
  }
};
measureSectionBoundary();

if(frame.contentDocument?.readyState==='complete')connect();
