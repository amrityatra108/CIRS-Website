import * as THREE from "./vendor/three.module.min.js";

const MENON="assets/menon-state-2048.png";
const GURUDEV="assets/gurudev-state-2048.png";
const mount=document.querySelector("#founder-root");
if(new URLSearchParams(location.search).has("embed")) document.documentElement.classList.add("is-embedded");

mount.innerHTML=`
  <main class="prototype" aria-label="Interactive founder portrait prototype">
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
        <img class="portrait-fallback" src="${MENON}" alt="Balakrishna Menon">
        <canvas class="portrait-canvas" data-canvas aria-label="Continuously flowing portrait transition between Balakrishna Menon and Gurudev Swami Chinmayananda"></canvas>
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
  status.textContent="Static Balakrishna Menon portrait shown because reduced motion is enabled";
}else{
  startAmbientDrift();
  initialise();
}

async function initialise(){
  let renderer;
  try{
    renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:"high-performance"});
  }catch{
    status.textContent="Static Balakrishna Menon portrait shown because WebGL is unavailable";
    return;
  }

  renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));
  renderer.setClearColor(0x000000,0);
  renderer.outputColorSpace=THREE.SRGBColorSpace;

  const loader=new THREE.TextureLoader();
  let menon;
  let gurudev;
  try{
    [menon,gurudev]=await Promise.all([loader.loadAsync(MENON),loader.loadAsync(GURUDEV)]);
  }catch{
    renderer.dispose();
    status.textContent="Static Balakrishna Menon portrait shown because an image could not be loaded";
    return;
  }

  for(const texture of [menon,gurudev]){
    texture.colorSpace=THREE.SRGBColorSpace;
    texture.minFilter=THREE.LinearFilter;
    texture.magFilter=THREE.LinearFilter;
    texture.generateMipmaps=false;
  }

<<<<<<< HEAD
  // Where the pointer rests when there is no pointer. Every tear is scaled
  // by proximity() to this, so a value on the face means every tear is wide
  // open before the cursor has arrived and again the moment it leaves --
  // which is exactly what (.5,.5) was doing. Below the frame, everything is
  // shut.
=======
  // The cursor is parked below the composition until it enters. Its trail
  // steers the neutral fluid field, but never cuts a hole through either
  // face.
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
  const PARK=new THREE.Vector2(.5,-.75);

  const uniforms={
    uMenon:{value:menon},
    uGurudev:{value:gurudev},
    uPointer:{value:PARK.clone()},
    uPrevious:{value:PARK.clone()},
    uResolution:{value:new THREE.Vector2(1,1)},
    uActive:{value:0},
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
      uniform sampler2D uMenon;
      uniform sampler2D uGurudev;
      uniform vec2 uPointer;
      uniform vec2 uPrevious;
      uniform vec2 uResolution;
      uniform float uActive;
      uniform float uTime;
      uniform float uVelocity;
      uniform vec2 uTrail[7];

      float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float noise(vec2 p){
        vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.0-2.0*f);
        return mix(mix(hash(i),hash(i+vec2(1.0,0.0)),f.x),mix(hash(i+vec2(0.0,1.0)),hash(i+vec2(1.0)),f.x),f.y);
      }
<<<<<<< HEAD
      // The tears. These were written to be driven by the cursor -- every
      // one of them is multiplied by proximity() to the pointer -- and then
      // never called: main() took its reveal from the flow field instead,
      // and the torn edges the shapes describe only ever appeared as the
      // field's own hard smoothstep cutting across the face. They are wired
      // up now, and every edge here is wider than it was, so a tear opens
      // and closes under the cursor instead of snapping.
      float zone(vec2 centre,vec2 size,float seed,float phase){
        vec2 p=(vUv-centre)/size;
        float distortion=(noise(vUv*vec2(13.0,9.0)+vec2(seed,phase*.12))-.5)*.31;
        distortion+=sin(p.x*5.0+phase+seed)*.075;
        // was smoothstep(.88,1.045) -- a sixth of the width of this one.
        return 1.0-smoothstep(.58,1.16,length(p)+distortion);
      }
      float proximity(vec2 pointer,vec2 centre,vec2 reach){
        return 1.0-smoothstep(.34,1.12,length((pointer-centre)/reach));
      }
      float tornSlice(float y,float halfHeight,float left,float right,float seed,float phase){
        float warpedY=y+sin(vUv.x*23.0+phase+seed)*.008+(noise(vec2(vUv.x*19.0+seed,phase*.11))-.5)*.018;
        // The feather on a slice was .009 against a half-height of about .01,
        // which is a torn strip with a razor edge. It is now several times
        // the strip's own height, so the strip reads as a soft opening.
        float vertical=1.0-smoothstep(halfHeight*.35,halfHeight+.055,abs(vUv.y-warpedY));
        float horizontal=smoothstep(left-.09,left+.05,vUv.x)*(1.0-smoothstep(right-.05,right+.09,vUv.x));
        return vertical*horizontal;
      }
      float fragmentedReveal(vec2 pointer,float phase){
        float crown=zone(vec2(.5,.82),vec2(.235,.05),1.1,phase)*proximity(pointer,vec2(.5,.80),vec2(.30,.095));
        float visor=zone(vec2(.5,.708),vec2(.225,.035),2.3,phase)*proximity(pointer,vec2(.5,.70),vec2(.30,.09));
        float leftCheek=zone(vec2(.405,.625),vec2(.075,.072),3.7,phase)*proximity(pointer,vec2(.39,.62),vec2(.17,.085));
        float rightCheek=zone(vec2(.595,.625),vec2(.075,.072),4.9,phase)*proximity(pointer,vec2(.61,.62),vec2(.17,.085));
        float chin=zone(vec2(.5,.515),vec2(.205,.067),6.2,phase)*proximity(pointer,vec2(.5,.51),vec2(.27,.09));
        float jaw=zone(vec2(.5,.425),vec2(.18,.038),7.4,phase)*proximity(pointer,vec2(.5,.43),vec2(.25,.07));
        float sliceA=tornSlice(.765,.012,.31,.72,8.2,phase)*proximity(pointer,vec2(.5,.75),vec2(.33,.105));
        float sliceB=tornSlice(.655,.008,.36,.67,9.6,phase)*proximity(pointer,vec2(.5,.64),vec2(.29,.10));
        float sliceC=tornSlice(.565,.01,.29,.75,10.8,phase)*proximity(pointer,vec2(.5,.55),vec2(.32,.105));
        // max() stacks these into one another with a visible ridge wherever
        // two overlap. Adding and rolling off keeps the overlaps smooth.
        float sum=crown+visor+leftCheek+rightCheek+chin+jaw+sliceA+sliceB+sliceC;
        float r=clamp(1.0-exp(-sum*1.35),0.0,1.0);
        // The roll-off is what keeps overlapping tears from ridging against
        // each other, but it also lifts a nearly-zero sum well off zero, and
        // the elder beard stayed on the young man with the cursor right out
        // of the frame. The gate puts the floor back without returning the
        // ridges: below a twentieth nothing opens at all, and the climb out
        // of it is still a smoothstep.
        return r*smoothstep(.05,.26,r);
      }

=======
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
      void main(){
        vec4 base=texture2D(uMenon,vUv);
        vec4 transformed=texture2D(uGurudev,vUv);

<<<<<<< HEAD
        // A continuous domain-warped field spans the whole registered image.
        // Autonomous flow changes visibility while photographs stay registered.
        vec2 p=vUv;
        float t=uTime*.24;
        vec2 flow=vec2(sin(t*.43),cos(t*.37))*.28;
        vec2 lag=vec2(sin(t*.31-1.1),cos(t*.29+.8))*.19;
        vec2 q=p*vec2(3.2,3.8)-flow*1.3-lag*.8;
        // Gently steer the full fluid field; never distort either photograph.
        vec2 cursorDrift=(uTrail[1]-vec2(.5))*.32;
        vec2 cursorWake=(uTrail[0]-uTrail[1])*.75;
        q-=cursorDrift+cursorWake;
        vec2 warp=vec2(noise(q+vec2(t,-t*.6)),noise(q+vec2(5.7-t*.7,2.4+t*.5)));
        float field=noise(q+warp*1.85+vec2(t*.3,-t*.22));
        float detail=noise(q*2.1-warp*.65+vec2(-t*.18,t*.25));
        float contour=field*.8+detail*.2;
        // The edge of the reveal is a long gradient, not a cut. It was
        // smoothstep(.505,.525) -- a band two hundredths wide on a warped
        // noise field, which is a hard organic edge in everything but name,
        // and it is what sliced the forehead in half. The two photographs
        // are different crops of different decades and will never register
        // perfectly; a dissolve this soft carries the difference as a man
        // ageing instead of as a tear.
        //
        // The cursor opens the tears; the flow field only breathes under
        // them. uPrevious is the smoothed pointer the move handler already
        // maintains, so the shapes follow the hand with a little lag rather
        // than snapping to the raw position, and the field's own edge is
        // wide enough now that it can no longer cut anything by itself.
        float torn=fragmentedReveal(uPrevious,uTime*.6);
        float breath=smoothstep(.40,.62,contour)*.18;
        float reveal=clamp((torn+breath*torn*2.0)*uActive,0.0,1.0);

        // The smudge. The elder texture's alpha sampled out in four
        // directions, and warm brown laid wherever the neighbourhood is
        // opaque but the pixel is not -- around the dark jacket that falls
        // on the body, which is where it shows. It is scaled by the tear
        // now, so it belongs to whatever the cursor has opened instead of
        // sitting on the picture whether or not anything is happening.
        float nearbyAlpha=0.0;
        vec2 px=1.0/uResolution;
        nearbyAlpha=max(nearbyAlpha,texture2D(uGurudev,vUv+vec2(px.x*15.0,0.0)).a);
        nearbyAlpha=max(nearbyAlpha,texture2D(uGurudev,vUv-vec2(px.x*15.0,0.0)).a);
        nearbyAlpha=max(nearbyAlpha,texture2D(uGurudev,vUv+vec2(0.0,px.y*15.0)).a);
        nearbyAlpha=max(nearbyAlpha,texture2D(uGurudev,vUv-vec2(0.0,px.y*15.0)).a);
        float aura=max(nearbyAlpha-transformed.a,0.0)*.13*reveal;
        vec4 guruState=transformed;
        guruState.rgb=mix(vec3(.68,.45,.19),guruState.rgb,transformed.a);
        guruState.a=max(transformed.a,aura);

        vec4 composed=mix(base,guruState,reveal);
        // The same warm tint along the outer skirt of the flow field, kept
        // faint and kept inside the tear.
        float localWarmth=smoothstep(.49,.51,contour)*(1.0-smoothstep(.505,.525,contour))*reveal*.035;
        composed.rgb=mix(composed.rgb,vec3(.68,.45,.19),localWarmth);
=======
        // Hover controls the state: Menon while the pointer is away, Gurudev
        // while it is over the portrait. The state changes as one complete
        // registered portrait, never as a face/body blend.
        float reveal=step(.5,uActive);
        vec4 composed=mix(base,transformed,reveal);

        // A soft monochrome field ripples through the entire silhouette while
        // the state changes. It follows the cursor with a delayed wake, but
        // does not mask, distort, or recolour the historical photographs.
        float t=uTime*.34;
        vec2 drift=(uTrail[1]-vec2(.5))*.62+(uTrail[0]-uTrail[1])*1.35;
        vec2 q=vUv*vec2(4.1,3.3)-drift+vec2(t*.38,-t*.27);
        vec2 warp=vec2(noise(q+vec2(t,-t*.55)),noise(q+vec2(6.1-t*.61,2.7+t*.44)));
        float field=noise(q+warp*1.55+vec2(t*.18,-t*.13));
        float detail=noise(q*2.35-warp*.52+vec2(-t*.14,t*.19));
        float fluid=smoothstep(.28,.74,field*.78+detail*.22);
        float silhouette=smoothstep(.018,.22,max(base.a,transformed.a));
        float transfer=sin(clamp(uActive,0.0,1.0)*3.14159265);
        float veil=(.28+fluid*.72)*transfer*silhouette;
        float luminance=dot(composed.rgb,vec3(.2126,.7152,.0722));
        vec3 neutral=vec3(luminance*1.035+.018);
        composed.rgb=mix(composed.rgb,neutral,veil*.62);
        composed.rgb+=vec3(.028)*veil;
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
        gl_FragColor=composed;
      }
    `
  });

  const scene=new THREE.Scene();
  const camera=new THREE.OrthographicCamera(-1,1,1,-1,0,2);
  camera.position.z=1;
  const plane=new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);
  scene.add(plane);

  const state={
<<<<<<< HEAD
    frame:0,lastFrame:0,elapsed:0,inView:true,inside:false,inHero:false,touch:false,lastEvent:0,lastHeroEvent:0,lastMove:performance.now(),active:1,targetActive:1,velocity:0,targetVelocity:0,
=======
    frame:0,lastFrame:0,elapsed:0,inView:true,inside:false,inHero:false,touch:false,lastEvent:0,lastHeroEvent:0,lastMove:performance.now(),active:0,targetActive:0,velocity:0,targetVelocity:0,
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
    rx:0,ry:0,tx:0,ty:0,scale:1,targetRx:0,targetRy:0,targetTx:0,targetTy:0,targetScale:1,
    bgX:0,bgY:0,targetBgX:0,targetBgY:0,
    ringX:innerWidth*.5,ringY:innerHeight*.5,targetCursorX:innerWidth*.5,targetCursorY:innerHeight*.5
  };

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

  function move(event){
    if(event.pointerType==="touch"&&!state.touch)return;
    const now=performance.now();
    const next=point(event);
    const distance=next.distanceTo(uniforms.uPointer.value);
    uniforms.uPointer.value.copy(next);
    state.targetVelocity=Math.min(distance/Math.max(now-state.lastMove,12)*34,1);
    state.lastMove=now;
    state.lastEvent=now;
    state.inside=true;
    state.targetActive=1;
    state.targetTx=0;state.targetTy=0;state.targetRy=0;state.targetRx=0;state.targetScale=1;
    cursor.classList.add("is-over-portrait");
    requestRender();
  }

  function enter(event){if(event.pointerType!=="touch")move(event);}
  function mouseMove(event){if(performance.now()-state.lastEvent>24)move(event);}
  function down(event){
    if(event.pointerType==="mouse")return;
    state.touch=true;portrait.setPointerCapture?.(event.pointerId);move(event);
  }
  function leave(){
    uniforms.uPointer.value.copy(PARK);
<<<<<<< HEAD
    state.inside=false;state.touch=false;state.targetVelocity=0;state.targetRx=0;state.targetRy=0;state.targetTx=0;state.targetTy=0;state.targetScale=1;
=======
    state.inside=false;state.touch=false;state.targetActive=0;state.targetVelocity=0;state.targetRx=0;state.targetRy=0;state.targetTx=0;state.targetTy=0;state.targetScale=1;
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
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
  function sceneMouseMove(event){if(performance.now()-state.lastHeroEvent>24)sceneMove(event);}
  function sceneLeave(){
    state.inHero=false;state.targetBgX=0;state.targetBgY=0;cursor.classList.remove("is-visible","is-over-portrait");leave();requestRender();
  }
  function render(time){
    state.frame=0;if(!state.inView||document.hidden)return;
    const dt=state.lastFrame?Math.min((time-state.lastFrame)/16.667,3):1;
    state.lastFrame=time;
    state.elapsed+=dt/60;
<<<<<<< HEAD
    state.active+=(state.targetActive-state.active)*(state.targetActive>.5 ? 0.34 : 0.2);
=======
    // A deliberate, short handoff lets the neutral field travel across the
    // full body before and after the complete portrait state changes.
    state.active+=(state.targetActive-state.active)*(state.targetActive>.5 ? .055 : .05);
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
    state.velocity+=(state.targetVelocity-state.velocity)*.18;
    state.targetVelocity*=.78;
    state.rx+=(state.targetRx-state.rx)*.09;state.ry+=(state.targetRy-state.ry)*.09;
    state.tx+=(state.targetTx-state.tx)*.09;state.ty+=(state.targetTy-state.ty)*.09;state.scale+=(state.targetScale-state.scale)*.09;
    state.bgX+=(state.targetBgX-state.bgX)*.035;state.bgY+=(state.targetBgY-state.bgY)*.035;
<<<<<<< HEAD
    state.ringX+=(state.targetCursorX-state.ringX)*.22;state.ringY+=(state.targetCursorY-state.ringY)*.22;
    const trail=uniforms.uTrail.value;
    // uPrevious is what the tears follow. It used to be stepped 72% of the
    // way once per pointer event, which makes the shapes jump with the event
    // rate and leaves them wherever the last event put them. Easing it here
    // instead, per frame and frame-rate corrected, is what makes a tear open
    // and close smoothly under the hand -- and it is what lets the pointer
    // ease back to PARK when the cursor leaves instead of snapping shut.
=======
    const ringEase=1-Math.pow(.80,dt);
    state.ringX+=(state.targetCursorX-state.ringX)*ringEase;state.ringY+=(state.targetCursorY-state.ringY)*ringEase;
    const trail=uniforms.uTrail.value;
    // The ink sweep reads this slow pointer trail as a very slight global
    // bend. Easing it per frame prevents mouse-event-rate jumps while the
    // portraits themselves remain perfectly fixed.
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
    uniforms.uPrevious.value.lerp(uniforms.uPointer.value,1-Math.pow(.90,dt));
    trail[0].lerp(uniforms.uPointer.value,1-Math.pow(.86,dt));
    trail[1].lerp(trail[0],1-Math.pow(.965,dt));
    uniforms.uActive.value=state.active;
    uniforms.uVelocity.value=state.velocity;
    uniforms.uTime.value=state.elapsed;
    composition.style.transform=`translate3d(${state.tx}px,${state.ty}px,0) rotateX(${state.rx}deg) rotateY(${state.ry}deg) scale(${state.scale})`;
    parallaxLayers.far.style.transform=`translate3d(${-state.bgX*4}px,${-state.bgY*3}px,0)`;
    parallaxLayers.middle.style.transform=`translate3d(${-state.bgX*8}px,${-state.bgY*5}px,0)`;
    parallaxLayers.front.style.transform=`translate3d(${-state.bgX*12}px,${-state.bgY*7}px,0)`;
    cursorRing.style.transform=`translate3d(${state.ringX}px,${state.ringY}px,0)`;
    renderer.render(scene,camera);
<<<<<<< HEAD
    if(uniforms.uPrevious.value.distanceTo(uniforms.uPointer.value)>.0015||Math.abs(state.active-state.targetActive)>.002||state.active>.002||state.velocity>.003||Math.abs(state.rx-state.targetRx)>.002||Math.abs(state.ry-state.targetRy)>.002||Math.abs(state.tx-state.targetTx)>.02||Math.abs(state.ty-state.targetTy)>.02||Math.abs(state.scale-state.targetScale)>.0001||Math.abs(state.bgX-state.targetBgX)>.002||Math.abs(state.bgY-state.targetBgY)>.002||Math.abs(state.ringX-state.targetCursorX)>.08||Math.abs(state.ringY-state.targetCursorY)>.08)requestRender();
=======
    // Keep the field alive while the pointer is over the portrait and while
    // its in/out transition settles; otherwise leave the GPU idle.
    if(state.inside||uniforms.uPrevious.value.distanceTo(uniforms.uPointer.value)>.0015||Math.abs(state.active-state.targetActive)>.002||state.velocity>.003||Math.abs(state.bgX-state.targetBgX)>.002||Math.abs(state.bgY-state.targetBgY)>.002||Math.abs(state.ringX-state.targetCursorX)>.08||Math.abs(state.ringY-state.targetCursorY)>.08)requestRender();
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
  }

  prototype.addEventListener("pointermove",sceneMove,{passive:true});
  prototype.addEventListener("mousemove",sceneMouseMove,{passive:true});
  prototype.addEventListener("pointerleave",sceneLeave,{passive:true});
  prototype.addEventListener("mouseleave",sceneLeave,{passive:true});

  portrait.addEventListener("pointermove",move,{passive:true});
  portrait.addEventListener("pointerenter",enter,{passive:true});
  portrait.addEventListener("pointerdown",down,{passive:true});
  portrait.addEventListener("pointerup",leave,{passive:true});
  portrait.addEventListener("pointercancel",leave,{passive:true});
  portrait.addEventListener("pointerleave",leave,{passive:true});
  portrait.addEventListener("mousemove",mouseMove,{passive:true});
  portrait.addEventListener("mouseenter",mouseMove,{passive:true});
  portrait.addEventListener("mouseleave",leave,{passive:true});
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
    menon.dispose();gurudev.dispose();plane.geometry.dispose();material.dispose();renderer.dispose();
  },{once:true});
}
