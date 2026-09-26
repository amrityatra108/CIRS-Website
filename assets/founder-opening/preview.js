import * as THREE from "./vendor/three.module.min.js";

// Same 2048-pixel portrait, with a lossless alpha channel and compressed colour.
const PORTRAIT="assets/swami-chinmayananda-registered.webp";
const mount=document.querySelector("#founder-root");
if(new URLSearchParams(location.search).has("embed")) document.documentElement.classList.add("is-embedded");

mount.innerHTML=`
  <main class="prototype" aria-label="Interactive founder portrait">
    <div class="ambient" aria-hidden="true">
      <div class="ambient-layer ambient-layer--far" data-parallax="far">
        <div class="ambient-drift ambient-drift--far">
          <svg viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice">
            <path class="ambient-form" d="M-120 730C72 468 229 255 520 151c221-79 457-70 640 74 175 137 213 367 413 496 112 72 232 86 360 52v323H-120Z"/>
            <path class="ambient-form ambient-form--left" d="M-170 42c201-63 383-22 455 112 54 101 5 193-94 250-115 66-160 154-116 277 34 96-3 198-142 284l-103 31Z"/>
            <path class="ambient-form ambient-form--right" d="M1354-111c157 103 222 228 174 362-39 108-148 141-214 239-68 101-38 209 94 322 83 71 120 166 94 285h254V-111Z"/>
            <circle class="ambient-orbit" cx="1160" cy="260" r="225"/>
            <circle class="ambient-orbit ambient-orbit--inner" cx="1160" cy="260" r="156"/>
          </svg>
        </div>
      </div>
      <div class="ambient-layer ambient-layer--middle" data-parallax="middle">
        <div class="ambient-drift ambient-drift--middle">
          <svg viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice">
            <g class="ambient-symbol">
              <circle cx="800" cy="500" r="350"/>
              <circle cx="800" cy="500" r="218"/>
              <path d="M800 99 1148 700H452Z"/>
              <path d="m800 901-348-601h696Z"/>
            </g>
          </svg>
        </div>
      </div>
      <div class="ambient-layer ambient-layer--front" data-parallax="front">
        <div class="ambient-drift ambient-drift--front">
          <svg viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice">
            <g class="ambient-contours">
              <path d="M-70 177c229-159 399-137 575 7 148 122 259 105 406-26 169-150 386-180 710-14"/>
              <path d="M-90 249c230-155 406-135 582 9 151 123 264 109 414-23 172-151 393-177 731-10"/>
              <path d="M-106 326c236-157 418-140 596 5 154 126 269 114 422-20 178-154 404-176 747 2"/>
              <path d="M-85 718c187-118 350-99 500 24 174 143 314 159 493 28 203-149 421-144 733 30"/>
              <path d="M-111 792c201-126 368-104 520 21 177 146 321 165 503 32 208-152 433-142 755 44"/>
              <path d="M181 458c80-98 190-123 281-56 78 57 99 167 36 248-67 87-184 110-272 48-82-58-105-160-45-240Z"/>
              <path d="M1246 445c68-84 164-100 242-43 71 52 88 145 34 218-58 78-158 99-236 45-75-51-94-144-40-220Z"/>
            </g>
          </svg>
        </div>
      </div>
      <div class="ambient-grain"></div>
    </div>
    <div class="portrait-stage" data-portrait>
      <div class="portrait-composition" data-composition>
        <img class="portrait-fallback" src="${PORTRAIT}" crossorigin="anonymous" alt="Swami Chinmayananda">
        <canvas class="portrait-canvas" data-canvas aria-label="Move over Swami Chinmayananda to reveal colour"></canvas>
      </div>
      <p class="status" aria-live="polite" data-status>Loading interactive portrait</p>
    </div>
    <div class="founder-cursor" data-cursor aria-hidden="true">
      <span class="founder-cursor__ring" data-cursor-ring></span>
      <span class="founder-cursor__dot" data-cursor-dot></span>
    </div>
  </main>`;

const prototype=mount.querySelector(".prototype");
const portrait=mount.querySelector("[data-portrait]");
const composition=mount.querySelector("[data-composition]");
const canvas=mount.querySelector("[data-canvas]");
const status=mount.querySelector("[data-status]");
const cursor=mount.querySelector("[data-cursor]");
const cursorRing=mount.querySelector("[data-cursor-ring]");
const cursorDot=mount.querySelector("[data-cursor-dot]");
const parallaxLayers={
  far:mount.querySelector('[data-parallax="far"]'),
  middle:mount.querySelector('[data-parallax="middle"]'),
  front:mount.querySelector('[data-parallax="front"]')
};

function startAmbientDrift(){
  if(!window.gsap)return;
  const settings=[
    [".ambient-drift--far",22,28,12,.22],
    [".ambient-drift--middle",18,-19,15,-.28],
    [".ambient-drift--front",15,23,-9,.18]
  ];
  settings.forEach(([selector,duration,x,y,rotation],index)=>{
    window.gsap.to(selector,{x,y,rotation,duration,ease:"sine.inOut",repeat:-1,yoyo:true,delay:index*-3.7,force3D:true});
  });
  window.gsap.to(".ambient-form:not(.ambient-form--left):not(.ambient-form--right)",{scaleX:1.1,scaleY:.92,x:32,y:-14,rotation:.32,transformOrigin:"50% 50%",duration:9.5,ease:"sine.inOut",repeat:-1,yoyo:true});
  window.gsap.to(".ambient-form--left",{scaleX:.9,scaleY:1.12,x:34,y:19,rotation:-.34,transformOrigin:"30% 45%",duration:8.2,ease:"sine.inOut",repeat:-1,yoyo:true});
  window.gsap.to(".ambient-form--right",{scaleX:1.12,scaleY:.91,x:-28,y:-13,rotation:.28,transformOrigin:"75% 40%",duration:10.8,ease:"sine.inOut",repeat:-1,yoyo:true});
  window.gsap.to(".ambient-symbol",{scaleX:.94,scaleY:1.06,rotation:-.24,transformOrigin:"50% 50%",duration:12.5,ease:"sine.inOut",repeat:-1,yoyo:true});
}

if(matchMedia("(prefers-reduced-motion: reduce)").matches){
  status.textContent="Static Swami Chinmayananda portrait shown because reduced motion is enabled";
}else{
  startAmbientDrift();
  initialise();
}

async function initialise(){
  let renderer;
  try{
    renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:"high-performance"});
  }catch{
    status.textContent="Static Swami Chinmayananda portrait shown because WebGL is unavailable";
    return;
  }

  renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));
  renderer.setClearColor(0x000000,0);
  renderer.outputColorSpace=THREE.SRGBColorSpace;

  const loader=new THREE.TextureLoader();
  let portraitTexture;
  try{
    portraitTexture=await loader.loadAsync(PORTRAIT);
  }catch{
    renderer.dispose();
    status.textContent="Static Swami Chinmayananda portrait shown because an image could not be loaded";
    return;
  }

  portraitTexture.colorSpace=THREE.SRGBColorSpace;
  portraitTexture.minFilter=THREE.LinearFilter;
  portraitTexture.magFilter=THREE.LinearFilter;
  portraitTexture.generateMipmaps=false;

  // Use the supplied cutout's alpha so empty parts of the square stage do
  // not trigger the colour brush.
  let subjectAlpha;
  try{
    const hitCanvas=document.createElement("canvas");
    hitCanvas.width=hitCanvas.height=256;
    const hitContext=hitCanvas.getContext("2d",{willReadFrequently:true});
    hitContext.drawImage(portraitTexture.image,0,0,256,256);
    subjectAlpha=hitContext.getImageData(0,0,256,256).data;
  }catch{}

  // The reveal brush is parked below the portrait until the pointer enters.
  const PARK=new THREE.Vector2(.5,-.75);

  const uniforms={
    uPortrait:{value:portraitTexture},
    uPointer:{value:PARK.clone()},
    uPrevious:{value:PARK.clone()},
    uResolution:{value:new THREE.Vector2(1,1)},
    uActive:{value:0},
    uBrushOpacity:{value:0},
    uTime:{value:0},
    uVelocity:{value:0}
  };
  uniforms.uTrail={value:Array.from({length:7},()=>PARK.clone())};

  const material=new THREE.ShaderMaterial({
    transparent:true,
    depthTest:false,
    depthWrite:false,
    uniforms,
    vertexShader:`
      varying vec2 vUv;
      void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}
    `,
    fragmentShader:`
      precision highp float;
      varying vec2 vUv;
      uniform sampler2D uPortrait;
      uniform vec2 uPointer;
      uniform vec2 uPrevious;
      uniform vec2 uResolution;
      uniform float uActive;
      uniform float uBrushOpacity;
      uniform float uTime;
      uniform float uVelocity;
      uniform vec2 uTrail[7];

      float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float noise(vec2 p){
        vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.0-2.0*f);
        return mix(mix(hash(i),hash(i+vec2(1.0,0.0)),f.x),mix(hash(i+vec2(0.0,1.0)),hash(i+vec2(1.0)),f.x),f.y);
      }
      void main(){
        vec4 portrait=texture2D(uPortrait,vUv);
        float gray=dot(portrait.rgb,vec3(.2126,.7152,.0722));

        // The soft brush reveals colour on the same photograph.
        float radius=clamp(uResolution.x*.18,72.0,135.0);
        float edgeNoise=((noise(vUv*vec2(19.0,23.0))-.5)*.28
                        +(noise(vUv*vec2(43.0,37.0))-.5)*.10)*radius;
        float cursorDistance=length((vUv-uPointer)*uResolution)+edgeNoise;
        float colourBrush=1.0-smoothstep(radius*.68,radius*1.08,cursorDistance);
        vec3 portraitColor=mix(vec3(gray),portrait.rgb,colourBrush*.68*uBrushOpacity);

        // Keep the cursor-steered fluid light moving across the portrait
        // as the colour brush appears and disappears.
        float t=uTime*.34;
        vec2 drift=(uTrail[1]-vec2(.5))*.62+(uTrail[0]-uTrail[1])*1.35;
        vec2 q=vUv*vec2(4.1,3.3)-drift+vec2(t*.38,-t*.27);
        vec2 warp=vec2(noise(q+vec2(t,-t*.55)),noise(q+vec2(6.1-t*.61,2.7+t*.44)));
        float field=noise(q+warp*1.55+vec2(t*.18,-t*.13));
        float detail=noise(q*2.35-warp*.52+vec2(-t*.14,t*.19));
        float fluid=smoothstep(.28,.74,field*.78+detail*.22);
        float silhouette=smoothstep(.018,.22,portrait.a);
        float transfer=sin(clamp(uActive,0.0,1.0)*3.14159265);
        float veil=(.28+fluid*.72)*transfer*silhouette;
        float luminance=dot(portraitColor,vec3(.2126,.7152,.0722));
        vec3 neutral=vec3(luminance*1.035+.018);
        portraitColor=mix(portraitColor,neutral,veil*.62);
        portraitColor+=vec3(.028)*veil;
        gl_FragColor=vec4(portraitColor,portrait.a);
        #include <colorspace_fragment>
      }
    `
  });

  const scene=new THREE.Scene();
  const camera=new THREE.OrthographicCamera(-1,1,1,-1,0,2);
  camera.position.z=1;
  const plane=new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);
  scene.add(plane);

  const state={
    frame:0,lastFrame:0,elapsed:0,inView:true,inside:false,inHero:false,touch:false,lastEvent:0,lastHeroEvent:0,lastMove:performance.now(),active:0,targetActive:0,brush:0,targetBrush:0,velocity:0,targetVelocity:0,
    rx:0,ry:0,tx:0,ty:0,scale:1,targetRx:0,targetRy:0,targetTx:0,targetTy:0,targetScale:1,
    bgX:0,bgY:0,targetBgX:0,targetBgY:0,
    ringX:innerWidth*.5,ringY:innerHeight*.5,targetCursorX:innerWidth*.5,targetCursorY:innerHeight*.5
  };
  const coarsePointer=matchMedia("(pointer:coarse)").matches;
  let touchPinned=false;

  function resize(){
    const rect=portrait.getBoundingClientRect();
    renderer.setSize(Math.max(1,Math.round(rect.width)),Math.max(1,Math.round(rect.height)),false);
    uniforms.uResolution.value.set(rect.width,rect.height);
  }

  function point(event){
    const rect=portrait.getBoundingClientRect();
    return new THREE.Vector2(
      THREE.MathUtils.clamp((event.clientX-rect.left)/rect.width,0,1),
      THREE.MathUtils.clamp(1-(event.clientY-rect.top)/rect.height,0,1)
    );
  }

  function overSubject(position){
    if(!subjectAlpha)return true;
    const x=Math.min(255,Math.floor(position.x*256));
    const y=Math.min(255,Math.floor((1-position.y)*256));
    return subjectAlpha[(y*256+x)*4+3]>24;
  }

  function move(event){
    if(event.pointerType==="touch"&&!state.touch)return;
    const now=performance.now();
    const next=point(event);
    if(!overSubject(next)){
      if(state.inside)leave();
      return;
    }
    const distance=next.distanceTo(uniforms.uPointer.value);
    uniforms.uPointer.value.copy(next);
    state.targetVelocity=Math.min(distance/Math.max(now-state.lastMove,12)*34,1);
    state.lastMove=now;
    state.lastEvent=now;
    state.inside=true;
    state.targetActive=1;
    state.targetBrush=1;
    state.targetTx=0;state.targetTy=0;state.targetRy=0;state.targetRx=0;state.targetScale=1;
    cursor.classList.add("is-over-portrait");
    requestRender();
  }

  function enter(event){if(event.pointerType!=="touch")move(event);}
  function mouseMove(event){if(!coarsePointer&&performance.now()-state.lastEvent>24)move(event);}
  function down(event){
    if(event.pointerType==="mouse")return;
    if(touchPinned){leave();return;}
    if(!overSubject(point(event)))return;
    touchPinned=true;
    state.touch=true;portrait.setPointerCapture?.(event.pointerId);move(event);
  }
  function up(event){
    if(event.pointerType!=="touch"){leave();return;}
    state.touch=false;
    state.inside=false;
    requestRender();
  }
  function leave(){
    touchPinned=false;
    state.inside=false;state.touch=false;state.targetActive=0;state.targetBrush=0;state.targetVelocity=0;state.targetRx=0;state.targetRy=0;state.targetTx=0;state.targetTy=0;state.targetScale=1;
    cursor.classList.remove("is-over-portrait");requestRender();
  }
  function bounds(event){
    if(!state.inside||event.pointerType==="touch")return;
    const rect=portrait.getBoundingClientRect();
    if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)leave();
  }

  function requestRender(){if(!state.frame&&state.inView&&!document.hidden)state.frame=requestAnimationFrame(render);}
  function sceneMove(event){
    const now=performance.now();
    state.lastHeroEvent=now;
    state.inHero=true;
    state.targetCursorX=event.clientX;state.targetCursorY=event.clientY;
    cursorDot.style.transform=`translate3d(${event.clientX}px,${event.clientY}px,0)`;
    cursor.classList.add("is-visible");
    state.targetBgX=THREE.MathUtils.clamp((event.clientX/Math.max(innerWidth,1)-.5)*2,-1,1);
    state.targetBgY=THREE.MathUtils.clamp((event.clientY/Math.max(innerHeight,1)-.5)*2,-1,1);
    requestRender();
  }
  function sceneMouseMove(event){if(!coarsePointer&&performance.now()-state.lastHeroEvent>24)sceneMove(event);}
  function sceneLeave(){
    if(touchPinned)return;
    state.inHero=false;state.targetBgX=0;state.targetBgY=0;cursor.classList.remove("is-visible","is-over-portrait");leave();requestRender();
  }
  function portraitLeave(event){if(event.pointerType==="touch"&&touchPinned)return;if(!touchPinned)leave();}
  function render(time){
    state.frame=0;if(!state.inView||document.hidden)return;
    const dt=state.lastFrame?Math.min((time-state.lastFrame)/16.667,3):1;
    state.lastFrame=time;
    state.elapsed+=dt/60;
    // Let the fluid field and colour brush ease with the cursor.
    state.active+=(state.targetActive-state.active)*(state.targetActive>.5 ? .055 : .05);
    state.brush+=(state.targetBrush-state.brush)*.14;
    state.velocity+=(state.targetVelocity-state.velocity)*.18;
    state.targetVelocity*=.78;
    state.rx+=(state.targetRx-state.rx)*.09;state.ry+=(state.targetRy-state.ry)*.09;
    state.tx+=(state.targetTx-state.tx)*.09;state.ty+=(state.targetTy-state.ty)*.09;state.scale+=(state.targetScale-state.scale)*.09;
    state.bgX+=(state.targetBgX-state.bgX)*.035;state.bgY+=(state.targetBgY-state.bgY)*.035;
    const ringEase=1-Math.pow(.80,dt);
    state.ringX+=(state.targetCursorX-state.ringX)*ringEase;state.ringY+=(state.targetCursorY-state.ringY)*ringEase;
    const trail=uniforms.uTrail.value;
    // Keep the existing cursor easing and ambient movement; the brush itself
    // reads the exact pointer position so it cannot drift away from the hand.
    uniforms.uPrevious.value.lerp(uniforms.uPointer.value,1-Math.pow(.90,dt));
    trail[0].lerp(uniforms.uPointer.value,1-Math.pow(.86,dt));
    trail[1].lerp(trail[0],1-Math.pow(.965,dt));
    uniforms.uActive.value=state.active;
    uniforms.uBrushOpacity.value=state.brush;
    uniforms.uVelocity.value=state.velocity;
    uniforms.uTime.value=state.elapsed;
    composition.style.transform=`translate3d(${state.tx}px,${state.ty}px,0) rotateX(${state.rx}deg) rotateY(${state.ry}deg) scale(${state.scale})`;
    parallaxLayers.far.style.transform=`translate3d(${-state.bgX*4}px,${-state.bgY*3}px,0)`;
    parallaxLayers.middle.style.transform=`translate3d(${-state.bgX*8}px,${-state.bgY*5}px,0)`;
    parallaxLayers.front.style.transform=`translate3d(${-state.bgX*12}px,${-state.bgY*7}px,0)`;
    cursorRing.style.transform=`translate3d(${state.ringX}px,${state.ringY}px,0)`;
    renderer.render(scene,camera);
    // Keep the field alive while the pointer is over the portrait and while
    // its in/out transition settles; otherwise leave the GPU idle.
    if(state.inside||uniforms.uPrevious.value.distanceTo(uniforms.uPointer.value)>.0015||Math.abs(state.active-state.targetActive)>.002||Math.abs(state.brush-state.targetBrush)>.002||state.velocity>.003||Math.abs(state.bgX-state.targetBgX)>.002||Math.abs(state.bgY-state.targetBgY)>.002||Math.abs(state.ringX-state.targetCursorX)>.08||Math.abs(state.ringY-state.targetCursorY)>.08)requestRender();
  }

  prototype.addEventListener("pointermove",sceneMove,{passive:true});
  prototype.addEventListener("mousemove",sceneMouseMove,{passive:true});
  prototype.addEventListener("pointerleave",sceneLeave,{passive:true});
  prototype.addEventListener("mouseleave",sceneLeave,{passive:true});

  portrait.addEventListener("pointermove",move,{passive:true});
  portrait.addEventListener("pointerenter",enter,{passive:true});
  portrait.addEventListener("pointerdown",down,{passive:true});
  portrait.addEventListener("pointerup",up,{passive:true});
  portrait.addEventListener("pointercancel",leave,{passive:true});
  portrait.addEventListener("pointerleave",portraitLeave,{passive:true});
  portrait.addEventListener("mousemove",mouseMove,{passive:true});
  portrait.addEventListener("mouseenter",mouseMove,{passive:true});
  portrait.addEventListener("mouseleave",portraitLeave,{passive:true});
  prototype.addEventListener("pointerdown",event=>{
    if(touchPinned&&event.pointerType==="touch"&&!portrait.contains(event.target))leave();
  },{passive:true});
  window.addEventListener("pointermove",bounds,{passive:true});

  const resizeObserver=new ResizeObserver(()=>{resize();requestRender();});
  resizeObserver.observe(portrait);
  const intersectionObserver=new IntersectionObserver(([entry])=>{state.inView=entry.isIntersecting;if(state.inView)requestRender();else leave();},{threshold:.01});
  intersectionObserver.observe(portrait);
  document.addEventListener("visibilitychange",requestRender);

  resize();portrait.classList.add("is-ready");status.textContent="Interactive portrait ready";requestRender();

  addEventListener("pagehide",()=>{
    cancelAnimationFrame(state.frame);resizeObserver.disconnect();intersectionObserver.disconnect();window.removeEventListener("pointermove",bounds);
    window.gsap?.killTweensOf?.(".ambient-drift");
    portraitTexture.dispose();plane.geometry.dispose();material.dispose();renderer.dispose();
  },{once:true});
}
