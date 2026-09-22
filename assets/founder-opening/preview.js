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
        <img class="portrait-fallback" data-fallback src="${MENON}" alt="Balakrishna Menon, the young journalist, arms folded in a Nehru-collar jacket">
        <canvas class="portrait-canvas" data-canvas aria-hidden="true"></canvas>
      </div>
      <p class="portrait-description" data-description>Balakrishna Menon, the young journalist, dissolving into Swami Chinmayananda, the teacher he became &mdash; the same folded arms, the ochre robe and rudraksha mala resolving over the dark jacket.</p>
      <p class="status" aria-live="polite" data-status>Loading the founder portrait</p>
    </div>
    <div class="founder-cursor" data-cursor aria-hidden="true">
      <span class="founder-cursor__ring" data-cursor-ring></span>
      <span class="founder-cursor__dot" data-cursor-dot></span>
    </div>
  </main>`;

const prototype=mount.querySelector(".prototype");
const portrait=mount.querySelector("[data-portrait]");
const canvas=mount.querySelector("[data-canvas]");
const fallback=mount.querySelector("[data-fallback]");
const status=mount.querySelector("[data-status]");
const cursor=mount.querySelector("[data-cursor]");
const cursorRing=mount.querySelector("[data-cursor-ring]");
const cursorDot=mount.querySelector("[data-cursor-dot]");
const parallaxLayers={
  far:mount.querySelector('[data-parallax="far"]'),
  middle:mount.querySelector('[data-parallax="middle"]'),
  front:mount.querySelector('[data-parallax="front"]')
};

const reducedMotion=matchMedia("(prefers-reduced-motion: reduce)").matches;

function startAmbientDrift(){
  if(!window.gsap)return;
  // 60-90s loops across three parallax depths, translating no more than 3%
  // of the viewport. This continues whether or not a pointer is present.
  const settings=[
    [".ambient-drift--far",74,22,10,.18],
    [".ambient-drift--middle",62,-17,13,-.22],
    [".ambient-drift--front",86,19,-8,.15]
  ];
  settings.forEach(([selector,duration,x,y,rotation],index)=>{
    window.gsap.to(selector,{x,y,rotation,duration,ease:"sine.inOut",repeat:-1,yoyo:true,delay:index*-11,force3D:true});
  });
  window.gsap.to(".ambient-form:not(.ambient-form--left):not(.ambient-form--right)",{scaleX:1.06,scaleY:.95,x:24,y:-11,transformOrigin:"50% 50%",duration:68,ease:"sine.inOut",repeat:-1,yoyo:true});
  window.gsap.to(".ambient-form--left",{scaleX:.94,scaleY:1.07,x:26,y:15,transformOrigin:"30% 45%",duration:79,ease:"sine.inOut",repeat:-1,yoyo:true});
  window.gsap.to(".ambient-form--right",{scaleX:1.07,scaleY:.94,x:-21,y:-10,transformOrigin:"75% 40%",duration:90,ease:"sine.inOut",repeat:-1,yoyo:true});
  window.gsap.to(".ambient-symbol",{scaleX:.96,scaleY:1.04,transformOrigin:"50% 50%",duration:84,ease:"sine.inOut",repeat:-1,yoyo:true});
}

initialise();

async function initialise(){
  let renderer;
  try{
    renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:"high-performance"});
  }catch{
    archivalFallback("WebGL is unavailable");
    return;
  }

  // Cap at 2 -- above that the two 2048 textures cost more than the extra
  // sharpness is worth, and the frame budget is what the dissolve lives on.
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));
  renderer.setClearColor(0x000000,0);
  // No colour conversion either way. This is 2D image compositing, not
  // lighting: the two photographs are blended in the space they are stored
  // in, which is what makes a twelve per cent floor read as twelve per cent
  // and keeps the canvas pixel-identical to the plain <img> of the same PNG
  // behind it. Decoding to linear instead lifts the black jacket to charcoal
  // at that same floor, which is not "faintly present".
  renderer.outputColorSpace=THREE.LinearSRGBColorSpace;

  const loader=new THREE.TextureLoader();
  let menon;
  let gurudev;
  try{
    [menon,gurudev]=await Promise.all([loader.loadAsync(MENON),loader.loadAsync(GURUDEV)]);
  }catch{
    renderer.dispose();
    archivalFallback("a portrait could not be loaded");
    return;
  }

  for(const texture of [menon,gurudev]){
    texture.colorSpace=THREE.NoColorSpace;
    // Mipmapped and linearly filtered: the beard and the rudraksha mala are
    // fine repeating detail at 2048, and they crawl without this the moment
    // the stage is drawn smaller than the texture.
    texture.minFilter=THREE.LinearMipmapLinearFilter;
    texture.magFilter=THREE.LinearFilter;
    texture.generateMipmaps=true;
    texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy?.()||1);
  }

  // Where the pointer rests when there is no pointer. Every zone is scaled
  // by proximity() to this, so a value on the face means every tear is wide
  // open before the cursor has arrived and again the moment it leaves.
  // Below the frame, everything is shut -- shut here meaning the resting
  // floor, not bare Menon.
  const PARK=new THREE.Vector2(.5,-.75);
  // The floor. The elder never leaves: at rest he is faintly present across
  // the whole figure, and the pointer opens him the rest of the way. This is
  // the single value that separates a transformation from a toy you can
  // strip back off.
  const RESTING=.12;

  const uniforms={
    uMenon:{value:menon},
    uGurudev:{value:gurudev},
    uPointer:{value:PARK.clone()},
    uPrevious:{value:PARK.clone()},
    uResolution:{value:new THREE.Vector2(1,1)},
    uActive:{value:0},
    uTime:{value:0},
    uVelocity:{value:0},
    uReach:{value:1},
    uRest:{value:RESTING},
    uStatic:{value:0}
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
      uniform float uReach;
      uniform float uRest;
      uniform float uStatic;
      uniform vec2 uTrail[7];

      const vec3 WARM=vec3(.678,.451,.188); // #AD7330, edge tint only

      float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float noise(vec2 p){
        vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.0-2.0*f);
        return mix(mix(hash(i),hash(i+vec2(1.0,0.0)),f.x),mix(hash(i+vec2(0.0,1.0)),hash(i+vec2(1.0)),f.x),f.y);
      }

      // A soft horizontal band across the figure at an anatomical height.
      // The bands are named for the man, not for the reference this was
      // ported from: robe, mala, beard, mouth, eyes, forehead.
      float band(float centre,float halfHeight){
        return 1.0-smoothstep(halfHeight*.45,halfHeight,abs(vUv.y-centre));
      }

      // How far the hand has opened one place on the figure: near it, or
      // already climbed past it. The lead is the bias -- above 1 the place
      // opens from further away and holds from lower down; below 1 the hand
      // has to be on it. The robe leads everything; the eyes trail everything.
      float drive(vec2 pointer,vec2 centre,vec2 reach,float lead){
        float near=1.0-smoothstep(.34*lead,1.12*lead,length((pointer-centre)/(reach*uReach)));
        float held=smoothstep(centre.y-.14*lead,centre.y+.16/lead,pointer.y);
        return clamp(max(near,held*.85),0.0,1.0);
      }

      float tornSlice(float y,float halfHeight,float left,float right,float seed,float phase){
        float warpedY=y+sin(vUv.x*23.0+phase+seed)*.008+(noise(vec2(vUv.x*19.0+seed,phase*.11))-.5)*.018;
        float vertical=1.0-smoothstep(halfHeight*.35,halfHeight+.055,abs(vUv.y-warpedY));
        float horizontal=smoothstep(left-.09,left+.05,vUv.x)*(1.0-smoothstep(right-.05,right+.09,vUv.x));
        return vertical*horizontal;
      }

      // The dissolve. One torn front that climbs the figure with the hand,
      // rather than a stack of separate blobs: a front is continuous by
      // construction, which is what keeps the mask one region across the
      // eyes, the nose and the mouth. A face broken into disconnected pieces
      // reads as damage, not as transformation.
      float climbingReveal(vec2 pointer,float phase,float breath){
        // The reveal order. Each band lifts the front by its own amount, so
        // the robe crosses well before the front arrives and the face only
        // when the front is on it. Every lift is positive: a band that pulled
        // the front down would open the forehead while the eyes were still
        // shut, which is exactly the broken face to avoid.
        float lift=band(.175,.215)*.075
                  +band(.320,.140)*.055
                  +band(.500,.175)*.030
                  +band(.648,.080)*.008
                  +band(.862,.080)*.012;

        // Across the face the tear calms right down. Over robe and chest it
        // is free to throw fragments; over the eyes it stays a single soft
        // boundary.
        float guard=1.0-smoothstep(.56,.72,vUv.y)*.62;

        // The torn edge: three octaves of domain-warped value noise, so the
        // boundary is organic and never a clean wipe, a circle or a cross-fade.
        float w=noise(vec2(vUv.x*3.1+phase*.06,vUv.y*2.4+1.7));
        float tear=noise(vec2(vUv.x*7.4+w*2.6+phase*.05,vUv.y*5.6-w*1.9+.4))*.66
                  +noise(vec2(vUv.x*17.0-w*1.3,vUv.y*12.5+w*.9-.9))*.26
                  +noise(vec2(vUv.x*31.0,vUv.y*24.0+2.2))*.08;

        // The hand. The front climbs with it, and opens a little higher
        // directly beneath it, so lateral movement reads as well as vertical.
        float bulge=(1.0-smoothstep(.0,.42*uReach,abs(vUv.x-pointer.x)))*.070;
        float crestRef=pointer.y+.125;
        // The ambient breath: the boundary itself breathes on the slow field,
        // which never touches what is already resolved.
        float crest=crestRef+lift+bulge+(tear-.5)*(.235+uVelocity*.06)*guard+(breath-.5)*.014;
        float edge=.052+.040*(1.0-guard);
        float front=1.0-smoothstep(crest-edge,crest+edge,vUv.y);

        // The eyes behind the glasses are the last thing to resolve, and the
        // point of the whole piece. That lag is a dimmer band inside the
        // front, never a gap in it -- floored at half, so the region stays
        // continuous however little the hand has climbed.
        float dEyes=drive(pointer,vec2(.489,.768),vec2(.24,.10),0.74);
        // Squared by hand: pow() is undefined for a negative base in GLSL,
        // and this one is negative below the eye line.
        float e=(vUv.y-.768)/.058;
        float eyeLag=exp(-e*e);
        front*=mix(1.0,min(.50+.50*dEyes,1.0),eyeLag);

        // Torn slices for the in-between states: they surface just ahead of
        // the front and are swallowed as it passes. Kept over cloth and
        // chest, well below the eye line, where an island reads as cloth.
        float aA=(.285-crestRef)/(.135*uReach);
        float aB=(.400-crestRef)/(.135*uReach);
        float aC=(.510-crestRef)/(.135*uReach);
        float sA=tornSlice(.285,.016,.16,.84, 8.2,phase)*exp(-aA*aA);
        float sB=tornSlice(.400,.013,.22,.78, 9.6,phase)*exp(-aB*aB);
        float sC=tornSlice(.510,.014,.28,.72,10.8,phase)*exp(-aC*aC);
        float islands=clamp(sA+sB+sC,0.0,1.0)*(1.0-front)*(1.0-smoothstep(.52,.60,vUv.y));

        float opened=clamp(front+islands*.80,0.0,1.0);

        // Reduced motion gets one still instead: essentially resolved, with
        // the torn boundary held open across the robe as a static edge, so
        // the idea survives with nothing moving at all.
        if(uStatic>.5){
          float held=opened*.90;
          opened=mix(held,held*.26,tornSlice(.300,.030,.14,.86,8.2,0.0));
        }
        return opened;
      }

      void main(){
        vec4 base=texture2D(uMenon,vUv);
        vec4 transformed=texture2D(uGurudev,vUv);

        // A slow domain-warped field: the ambient breath under the tear. It
        // moves the boundary a little and nothing else, so it can never cut
        // anything by itself and never disturbs what is already resolved.
        float t=uTime*.24;
        vec2 flow=vec2(sin(t*.43),cos(t*.37))*.28;
        vec2 lag=vec2(sin(t*.31-1.1),cos(t*.29+.8))*.19;
        vec2 q=vUv*vec2(3.2,3.8)-flow*1.3-lag*.8;
        q-=(uTrail[3]-vec2(.5))*.32+(uTrail[0]-uTrail[6])*.75;
        vec2 warp=vec2(noise(q+vec2(t,-t*.6)),noise(q+vec2(5.7-t*.7,2.4+t*.5)));
        float breath=noise(q+warp*1.85+vec2(t*.3,-t*.22))*.8+noise(q*2.1-warp*.65+vec2(-t*.18,t*.25))*.2;

        // The front is driven from the smoothed pointer, so the tear follows
        // the hand with lag rather than snapping to the raw position.
        float torn=climbingReveal(uPrevious,uTime*.6,breath);

        // The floor, and the single value that separates a transformation
        // from a toy: the dissolve never strips back to bare Menon. Even
        // untouched the elder is faintly there, a little stronger down the
        // robe than at the eyes, so that even at rest the figure reads as
        // resolving from the bottom up. Held inside the young man's own
        // silhouette, so the floor is the elder showing faintly through the
        // portrait rather than a second silhouette hanging off it: both
        // photographs stay hard-edged cut-outs on paper.
        float rest=uRest*(.80+.40*smoothstep(.12,.95,1.0-vUv.y))*base.a;
        float reveal=clamp(mix(rest,1.0,torn)*uActive,0.0,1.0);

        // The smudge: the elder texture's alpha sampled out in four
        // directions, and warm brown laid wherever the neighbourhood is
        // opaque but the pixel is not -- a thin aura around the robe where it
        // falls against the dark jacket beneath. Scaled by the reveal, so it
        // belongs to what the pointer has opened.
        float nearbyAlpha=0.0;
        vec2 px=1.0/uResolution;
        nearbyAlpha=max(nearbyAlpha,texture2D(uGurudev,vUv+vec2(px.x*15.0,0.0)).a);
        nearbyAlpha=max(nearbyAlpha,texture2D(uGurudev,vUv-vec2(px.x*15.0,0.0)).a);
        nearbyAlpha=max(nearbyAlpha,texture2D(uGurudev,vUv+vec2(0.0,px.y*15.0)).a);
        nearbyAlpha=max(nearbyAlpha,texture2D(uGurudev,vUv-vec2(0.0,px.y*15.0)).a);
        // Gated by the young man's own alpha: this is the robe falling
        // against the dark jacket beneath, so it belongs only where there is
        // still a jacket under it. Off the silhouette there is nothing for it
        // to fall against, and an unscaled aura there is just a halo on the
        // paper.
        float aura=max(nearbyAlpha-transformed.a,0.0)*.13*reveal*base.a;
        vec4 guruState=transformed;
        guruState.rgb=mix(WARM,guruState.rgb,transformed.a);
        guruState.a=max(transformed.a,aura);

        vec4 composed=mix(base,guruState,reveal);
        // Edge warmth, inside the tear only: the band where the front is
        // neither shut nor open is the torn boundary itself, and that is the
        // only place the ochre goes. Never a fill, never a wash.
        float rim=smoothstep(.10,.42,torn)*(1.0-smoothstep(.55,.95,torn));
        composed.rgb=mix(composed.rgb,WARM,rim*.038*uActive);
        gl_FragColor=composed;
      }
    `
  });

  const scene=new THREE.Scene();
  const camera=new THREE.OrthographicCamera(-1,1,1,-1,0,2);
  camera.position.z=1;
  const plane=new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);
  scene.add(plane);

  function resize(){
    const rect=portrait.getBoundingClientRect();
    renderer.setSize(Math.max(1,Math.round(rect.width)),Math.max(1,Math.round(rect.height)),false);
    uniforms.uResolution.value.set(rect.width,rect.height);
    // Tablet: the same composition, with the zones pulled in so the tears
    // stay readable at a smaller size.
    uniforms.uReach.value=innerWidth>=1280||innerWidth<768 ? 1 : .85;
  }

  // ---- Reduced motion: one static composite, no loop, no listeners -------
  // Gurudev essentially resolved, with the torn boundary still visible across
  // the robe as a static edge, so the idea survives without any movement.
  if(reducedMotion){
    uniforms.uPrevious.value.set(.489,.84);
    uniforms.uPointer.value.set(.489,.84);
    uniforms.uTrail.value.forEach(v=>v.set(.489,.84));
    uniforms.uStatic.value=1;
    uniforms.uActive.value=1;
    uniforms.uTime.value=0;
    resize();
    renderer.render(scene,camera);
    portrait.classList.add("is-ready");
    status.textContent="Static founder portrait shown because reduced motion is enabled";
    new ResizeObserver(()=>{resize();renderer.render(scene,camera);}).observe(portrait);
    return;
  }

  startAmbientDrift();

  // No pointer on a phone: the reveal runs itself, climbing the figure in the
  // same order over about eleven seconds and easing back down. Showing the
  // finished elder instead would throw away the content, which is the
  // transformation and not the portrait.
  const AUTOPLAY=matchMedia("(pointer: coarse)").matches||innerWidth<768;
  const LOOP=11;

  const state={
    frame:0,lastFrame:0,elapsed:0,inView:true,inside:false,touch:false,lastEvent:0,lastHeroEvent:0,lastMove:performance.now(),
    active:0,targetActive:1,velocity:0,targetVelocity:0,
    bgX:0,bgY:0,targetBgX:0,targetBgY:0,
    ringX:innerWidth*.5,ringY:innerHeight*.5,targetCursorX:innerWidth*.5,targetCursorY:innerHeight*.5,
    slow:0,degraded:0
  };

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
    // To resting, not to zero. The pointer parks below the frame and the
    // zones close behind it over about nine hundred milliseconds, down to the
    // floor and no further.
    uniforms.uPointer.value.copy(PARK);
    state.inside=false;state.touch=false;state.targetVelocity=0;
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
    state.targetCursorX=event.clientX;state.targetCursorY=event.clientY;
    cursorDot.style.transform=`translate3d(${event.clientX}px,${event.clientY}px,0)`;
    cursor.classList.add("is-visible");
    state.targetBgX=THREE.MathUtils.clamp((event.clientX/Math.max(innerWidth,1)-.5)*2,-1,1);
    state.targetBgY=THREE.MathUtils.clamp((event.clientY/Math.max(innerHeight,1)-.5)*2,-1,1);
    requestRender();
  }
  function sceneMouseMove(event){if(performance.now()-state.lastHeroEvent>24)sceneMove(event);}
  function sceneLeave(){
    state.targetBgX=0;state.targetBgY=0;cursor.classList.remove("is-visible","is-over-portrait");leave();requestRender();
  }

  function render(time){
    state.frame=0;if(!state.inView||document.hidden)return;
    const dt=state.lastFrame?Math.min((time-state.lastFrame)/16.667,3):1;
    state.lastFrame=time;
    state.elapsed+=dt/60;

    // Thirty consecutive frames over budget: drop the ambient parallax
    // layers first, then the pixel ratio. Never the dissolve.
    if(dt>1.35)state.slow++;else state.slow=Math.max(0,state.slow-1);
    if(state.slow>30&&state.degraded<2){
      state.slow=0;state.degraded++;
      if(state.degraded===1)prototype.classList.add("is-degraded");
      else renderer.setPixelRatio(1);
      resize();
    }

    if(AUTOPLAY&&!state.touch){
      const phase=(state.elapsed%LOOP)/LOOP;
      const climb=.5-.5*Math.cos(phase*Math.PI*2);
      uniforms.uPointer.value.set(.49+Math.sin(phase*Math.PI*2)*.035,.10+climb*.82);
    }

    state.active+=(state.targetActive-state.active)*(1-Math.pow(.90,dt));
    state.velocity+=(state.targetVelocity-state.velocity)*.18;
    state.targetVelocity*=.78;
    state.bgX+=(state.targetBgX-state.bgX)*.035;state.bgY+=(state.targetBgY-state.bgY)*.035;
    state.ringX+=(state.targetCursorX-state.ringX)*.22;state.ringY+=(state.targetCursorY-state.ringY)*.22;

    // The settle. Damped lerp toward the pointer, never keyframe easing, and
    // deliberately slower than the reference: .915 per frame at sixty is
    // about 430ms to ninety per cent and 560ms to ninety-five. Leaving is
    // slower again, .945, which is the ~900ms fall back to the floor. The
    // extra weight is most of what separates dignity from gimmick.
    const settle=state.inside||AUTOPLAY ? .915 : .945;
    uniforms.uPrevious.value.lerp(uniforms.uPointer.value,1-Math.pow(settle,dt));
    const trail=uniforms.uTrail.value;
    trail[0].lerp(uniforms.uPointer.value,1-Math.pow(.86,dt));
    for(let i=1;i<trail.length;i++)trail[i].lerp(trail[i-1],1-Math.pow(.90+i*.008,dt));

    uniforms.uActive.value=state.active;
    uniforms.uVelocity.value=state.velocity;
    uniforms.uTime.value=state.elapsed;

    parallaxLayers.far.style.transform=`translate3d(${-state.bgX*4}px,${-state.bgY*3}px,0)`;
    parallaxLayers.middle.style.transform=`translate3d(${-state.bgX*8}px,${-state.bgY*5}px,0)`;
    parallaxLayers.front.style.transform=`translate3d(${-state.bgX*12}px,${-state.bgY*7}px,0)`;
    cursorRing.style.transform=`translate3d(${state.ringX}px,${state.ringY}px,0)`;
    renderer.render(scene,camera);

    // The ambient breath and the autoplay loop never settle, so those keep
    // the loop alive on their own; everything else drops out when it stops.
    if(AUTOPLAY||uniforms.uPrevious.value.distanceTo(uniforms.uPointer.value)>.0015||Math.abs(state.active-state.targetActive)>.002||state.velocity>.003||Math.abs(state.bgX-state.targetBgX)>.002||Math.abs(state.bgY-state.targetBgY)>.002||Math.abs(state.ringX-state.targetCursorX)>.08||Math.abs(state.ringY-state.targetCursorY)>.08||state.elapsed<3)requestRender();
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
  const intersectionObserver=new IntersectionObserver(([entry])=>{state.inView=entry.isIntersecting;if(state.inView){state.lastFrame=0;requestRender();}else leave();},{threshold:.01});
  intersectionObserver.observe(portrait);
  document.addEventListener("visibilitychange",()=>{state.lastFrame=0;requestRender();});

  resize();portrait.classList.add("is-ready");status.textContent="Founder portrait ready";requestRender();

  addEventListener("pagehide",()=>{
    cancelAnimationFrame(state.frame);resizeObserver.disconnect();intersectionObserver.disconnect();window.removeEventListener("pointermove",bounds);
    window.gsap?.killTweensOf?.(".ambient-drift");
    menon.dispose();gurudev.dispose();plane.geometry.dispose();material.dispose();renderer.dispose();
  },{once:true});
}

// Nothing to dissolve with. Show the elder alone on the paper field, so that
// what is left reads as a deliberate archival portrait rather than as a
// feature that broke.
function archivalFallback(reason){
  fallback.src=GURUDEV;
  fallback.alt="Swami Chinmayananda, born Balakrishna Menon, in ochre robe with a rudraksha mala, arms folded";
  prototype.classList.add("is-archival");
  status.textContent=`Archival portrait of Swami Chinmayananda shown because ${reason}`;
}
