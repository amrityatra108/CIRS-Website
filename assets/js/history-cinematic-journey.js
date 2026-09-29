/* One normal document scroll owner (cirs.js / Lenis), one finite Three.js
   scene, HTML chapter text, reversible SVG mask and typographic expansion.
   Reference techniques are independently authored; see docs. */
const root=document.documentElement,journey=document.querySelector('.hj');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const wide=matchMedia('(min-width:1000px) and (min-height:680px)');
const clamp=(n,a=0,b=1)=>Math.min(b,Math.max(a,n));
const smooth=n=>{n=clamp(n);return n*n*(3-2*n);};
if(journey)boot();
function boot(){
 const scenes=[...journey.querySelectorAll('[data-hj-scene]')];
 const stage=journey.querySelector('.hj-stage'),canvas=stage.querySelector('canvas');
 const expansion=document.querySelector('.hj-expansion');
 const left=expansion.querySelector('.hj-expansion__left'),right=expansion.querySelector('.hj-expansion__right'),expImage=expansion.querySelector('.hj-expansion__image');
 const nav=[...document.querySelectorAll('[data-hj-go]')];
 const svg=journey.querySelector('.hj-blinds'),strips=svg.querySelector('g'),svgImage=svg.querySelector('image'),caption=stage.querySelector('.hj-stage__caption');
 const opening=scenes.findIndex(s=>s.id==='chapter-opening');
 const controller=new AbortController(),signal=controller.signal;
 let world=null,loading=false,epoch=0,frame=0,visible=true,anchors=[],active=-1;
 let expStart=0,expRange=1,progress=0,lastTime=0,settled=true,expTravel=innerWidth*.6,blindPairs=[],gsapContext=null,disposed=false;
 const portrait=scenes[0].querySelector('.hj-fig');
 const stations=scenes.map(s=>{
  const figures=[...s.querySelectorAll('.hj-fig')],selected=figures.length?figures:[portrait];
  return {id:s.id,images:selected.map(fig=>{const img=fig.querySelector('img');return {src:img.src.replace('-sm.jpg','-lg.jpg'),ratio:+img.getAttribute('width')/+img.getAttribute('height')};}),caption:figures.length?figures[0].querySelector('figcaption').textContent:'Pujya Gurudev Swami Chinmayananda. Archival portrait; photograph date unrecorded.'};
 });
 stations.at(-1).images=[{src:'assets/img/campus-band.jpg',ratio:16/9}];
 stations.at(-1).caption='The campus today. Recent records come from the dated Annual Report and results briefs.';
 function measure(){
  if(disposed)return;
  expStart=expansion.getBoundingClientRect().top+scrollY;expRange=Math.max(1,expansion.offsetHeight-innerHeight);
  anchors=scenes.map(s=>s.getBoundingClientRect().top+scrollY+innerHeight*.55);
  expTravel=Math.max(innerWidth*.55,left.getBoundingClientRect().width+innerWidth*.15,right.getBoundingClientRect().width+innerWidth*.15);
  world?.resize();layoutMask();kick();
 }
 function layoutMask(){
  const w=innerWidth,h=innerHeight;svg.setAttribute('viewBox',`0 0 ${w} ${h}`);
  for(const node of [svg.querySelector('.hj-mask-base'),svgImage]){node.setAttribute('width',w);node.setAttribute('height',h);}
  strips.replaceChildren();blindPairs=[];
  const rows=10,band=h/rows;
  for(let i=0;i<rows;i++){
   const center=(i+.5)*band,pair=[0,1].map(()=>{const r=document.createElementNS('http://www.w3.org/2000/svg','rect');r.setAttribute('fill','white');r.setAttribute('x','0');r.setAttribute('width',w);strips.append(r);return r;});
   blindPairs.push({pair,center,half:band/2});
  }
 }
 function drawMask(k){
  const phase=clamp((k-(opening-.48))/.34),exit=1-smooth((k-opening-.15)/.32);
  svg.style.opacity=String(exit);
  canvas.style.opacity=String(1-smooth((phase-.4)/.4)*exit);
  blindPairs.forEach(({pair,center,half},i)=>{
   const t=smooth((phase-i*.024)/.78),size=(half+1)*t;
   pair[0].setAttribute('y',center-size);pair[1].setAttribute('y',center);pair.forEach(r=>r.setAttribute('height',size));
  });
 }
 function cameraProgress(y){
  if(y<=anchors[0])return 0;
  for(let i=0;i<anchors.length-1;i++)if(y<=anchors[i+1]){
   const t=(y-anchors[i])/(anchors[i+1]-anchors[i]);
   // Half the interval is a still reading pose; all movement is finite.
   return i+smooth((t-.26)/.48);
  }
  return anchors.length-1;
 }
 function markActive(index){
  if(index===active)return;active=index;
  nav.forEach(a=>{a.dataset.hjGo===scenes[index]?.id?a.setAttribute('aria-current','step'):a.removeAttribute('aria-current');});
  caption.textContent=stations[index]?.caption||'';journey.dataset.activeChapter=scenes[index]?.id||'';
 }
 function update(time){
  frame=0;if(disposed||document.hidden)return;
  const y=scrollY,dt=Math.min(.05,(time-lastTime)/1000||.016);lastTime=time;
  const target=cameraProgress(y);progress+=(target-progress)*(1-Math.exp(-dt*12));
  if(Math.abs(target-progress)<.0005)progress=target;settled=progress===target;
  if(root.classList.contains('hj-motion')){
   const p=smooth((y-expStart)/expRange),mobile=innerWidth<768;
   expImage.style.clipPath=`inset(0 ${(mobile?20:45)*(1-p)}%)`;
   left.style.transform=mobile?'':`translate3d(${-p*expTravel}px,${-p*innerHeight*.12}px,0)`;
   right.style.transform=mobile?'':`translate3d(${p*expTravel}px,${p*innerHeight*.12}px,0)`;
   expansion.style.setProperty('--expand-caption',String(smooth((p-.24)/.15)));
  }
  const enhanced=root.classList.contains('hj-enhanced');
  const index=enhanced?Math.round(progress):Math.max(0,scenes.findLastIndex(s=>s.getBoundingClientRect().top<=innerHeight*.45));
  markActive(index);
  if(world&&visible){
   if(world.photoFailed(index)){fallback();return;}
   world.render(progress);drawMask(progress);
   scenes.forEach((s,i)=>{
    let opacity=1-smooth((Math.abs(progress-i)-.27)/.3);
    if(i===opening)opacity*=smooth((progress-opening+.12)/.12);
    s.style.setProperty('--text-opacity',opacity);s.style.setProperty('--text-shift',`${(i-progress)*18}px`);
    s.style.setProperty('--coin-turn',`${18+Math.sin(progress*2)*13}deg`);
    s.querySelector('.hj-text').inert=opacity<.25;
   });
  }
  if(!settled&&visible)kick();
 }
 function kick(){if(!frame&&!document.hidden&&!disposed)frame=requestAnimationFrame(update);}
 async function setup(){
  const token=++epoch,motion=!reduced.matches;root.classList.toggle('hj-motion',motion);
  if(!motion||!wide.matches){fallback();if(!motion){left.style.transform='';right.style.transform='';expImage.style.clipPath='';gsapContext?.revert();gsapContext=null;}measure();return;}
  if(world||loading){measure();return;}
  loading=true;
  try{
   const {createWorld}=await import('./history-cinematic-world.js');
   if(token!==epoch||disposed)return;
   stage.style.display='block';stage.style.height='100svh';stage.style.width='100%';stage.style.position='absolute';stage.style.opacity='0';canvas.style.display='block';canvas.style.width='100%';canvas.style.height='100%';
   world=createWorld(canvas,stations,kick);if(!world)throw Error('WebGL unavailable');
   world.render(0);measure();
   let attempts=0;
   const wait=()=>{
    if(token!==epoch||!world||disposed)return;
    const index=Math.max(0,scenes.findLastIndex(s=>s.getBoundingClientRect().top<=innerHeight*.45));
    world.render(index);
    if(world.photoReady(index)){
     stage.style.removeProperty('position');stage.style.removeProperty('opacity');
     root.classList.add('hj-enhanced');journey.classList.add('hj-ready');measure();
     resolveChapterHash();progress=cameraProgress(scrollY);kick();
    }
    else if(++attempts>80||world.photoFailed(index)){fallback();measure();}else setTimeout(wait,100);
   };wait();
  }catch{fallback();}finally{loading=false;if(token!==epoch&&!disposed)setup();}
  measure();resolveChapterHash();
 }
 function fallback(){
  const retain=root.classList.contains('hj-enhanced')&&journey.getBoundingClientRect().top<0&&journey.getBoundingClientRect().bottom>0;
  root.classList.remove('hj-enhanced');journey.classList.remove('hj-ready');
  const old=world;world=null;old?.dispose();stage.style.removeProperty('display');stage.style.removeProperty('height');stage.style.removeProperty('position');stage.style.removeProperty('opacity');
  scenes.forEach(s=>{s.style.removeProperty('--text-opacity');s.style.removeProperty('--text-shift');s.querySelector('.hj-text').inert=false;});
  if(retain&&!disposed&&scenes[active]){measure();go(scenes[active].id,false,true);}
 }
 function go(id,push=true,instant=false){
  const index=scenes.findIndex(s=>s.id===id),element=document.getElementById(id);if(!element)return;
  const y=root.classList.contains('hj-enhanced')&&index>=0?anchors[index]:element.getBoundingClientRect().top+scrollY-90;
  if(push)history.pushState(null,'',`#${id}`);
  const text=element.querySelector('.hj-text,.hj-present__text')||element;
  const done=()=>{text.inert=false;if(!text.hasAttribute('tabindex'))text.setAttribute('tabindex','-1');text.focus({preventScroll:true});kick();};
  const event=new CustomEvent('cirs-section-scroll',{cancelable:true,detail:{top:Math.max(0,y),duration:instant||reduced.matches?0:1.05,lock:false,onComplete:done}});
  if(dispatchEvent(event)){scrollTo({top:Math.max(0,y),behavior:instant||reduced.matches?'instant':'smooth'});setTimeout(done,instant?0:1100);}
 }
 function resolveChapterHash(){const id=location.hash.slice(1);if(scenes.some(s=>s.id===id)||id==='chapter-now')go(id,false,true);}
 document.addEventListener('click',event=>{
  const link=event.target.closest('[data-hj-go],a[href="#chapter-now"]');if(!link||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
  event.preventDefault();event.stopPropagation();go(link.dataset.hjGo||'chapter-now');
 },{capture:true,signal});
 addEventListener('cirs-hash-open',event=>{const id=event.detail?.target?.id;if(scenes.some(s=>s.id===id)||id==='chapter-now'){event.preventDefault();go(id,false,true);}},{signal});
 addEventListener('popstate',resolveChapterHash,{signal});addEventListener('hashchange',resolveChapterHash,{signal});
 addEventListener('scroll',kick,{passive:true,signal});addEventListener('resize',measure,{signal});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(frame);frame=0;}else{lastTime=performance.now();kick();}},{signal});
 canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();fallback();measure();},{signal});
 const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)kick();},{rootMargin:'100px'});observer.observe(journey);
 reduced.addEventListener('change',setup,{signal});wide.addEventListener('change',setup,{signal});
 document.fonts.ready.then(()=>{measure();window.ScrollTrigger?.refresh();resolveChapterHash();});
 addEventListener('load',()=>{measure();resolveChapterHash();},{once:true,signal});
 if(!reduced.matches&&window.gsap){gsapContext=gsap.context(()=>{
  gsap.fromTo('.hj-hero__image',{scale:1.045},{scale:1,duration:1.4,ease:'power2.out'});
  gsap.fromTo('.hj-line>span',{yPercent:108},{yPercent:0,duration:.8,stagger:.09,ease:'power3.out'});
  gsap.fromTo('.hj-hero__intro,.hj-hero__links',{opacity:0,y:12},{opacity:1,y:0,duration:.7,delay:.3});
 },document.querySelector('.hj-hero'));}
 function cleanup(){disposed=true;epoch++;controller.abort();observer.disconnect();cancelAnimationFrame(frame);gsapContext?.revert();fallback();root.classList.remove('hj-motion');}
 addEventListener('pagehide',event=>{if(!event.persisted)cleanup();else{cancelAnimationFrame(frame);frame=0;}},{signal});
 addEventListener('pageshow',event=>{if(event.persisted){measure();kick();}},{signal});setup();measure();
}
