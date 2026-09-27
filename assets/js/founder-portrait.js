/* Founder portrait: the two GLB busts, the cursor reveal, the idle swirls.
   Ported from the designer's Gurudev handoff (src/portrait.js). The shader,
   reveal width, smoothing, 0.82s wake, idle-flow timing and turn limits are
   the designer's and are unchanged. What differs for this site:

   - the model payload (both busts at their original topology, packed by the
     designer) is fetched from the portrait's data-models, not inlined, so
     the page's HTML stays small;
   - "Begin the journey" is a link, so links count as controls like buttons;
   - the portrait's status line is its own element (the handoff wrote these
     messages into the sound status, which shares the class);
   - the in-browser tuning panel hook (Tweak) is left out.

   Portrait 2 (the young Balakrishna Menon) is shown first; Portrait 1 (the
   older Gurudev) shows through a trail that follows the pointer and recedes.
   After 2s without movement a pair of swirls enters from opposite edges
   through the same trail; they never sound, never move the busts, and stop
   the moment the pointer moves. See the handoff's planning notes, recorded
   in CLAUDE.md, before changing any of it. */
(()=>{
 'use strict';
 const root=document.querySelector('[data-gurudev-opening]'),hero=root?.querySelector('.gp-hero');if(!hero)return;
 const canvas=hero.querySelector('.gp-canvas'),initialPhoto=hero.querySelector('.gp-initial'),olderPhoto=hero.querySelector('.gp-revealed');
 const toggle=hero.querySelector('.gp-toggle'),hint=hero.querySelector('.gp-hint'),status=hero.querySelector('.gp-portrait-status');
 const reduced=matchMedia('(prefers-reduced-motion:reduce)'),coarse=matchMedia('(pointer:coarse)');
 const settings={yaw:2.8,pitch:1.8,radius:1,trail:.82};
 // Idle passes feed the existing trail/mask; they never move the real cursor or the models.
 const idleSettings={delayMs:2000,speedMultiplier:1.25,baseDurationMinMs:2100,baseDurationMaxMs:2650,gapMinMs:1100,gapMaxMs:3500};
 let idleTimer=0,idleFlow=null,idleDue=0,idlePasses=0,idleLastShape=null,idleFocused=true;
 const N=36,strokeData=new Float32Array(N*4);
 let packedStrokeIds=[];
 let width=1,height=1,dpr=1,active=false,visible=true,loaded=false,disposed=false,gl=null,meshProgram=null,postProgram=null,maskProgram=null,maskTarget=null,screenBuffer=null;
 let models=[],targets=[],resources=[],listeners=[],resizeObserver,intersectionObserver,removalObserver;
let raf=0,lastFrame=0,full=0,targetFull=0,yaw=0,pitch=0,targetYaw=0,targetPitch=0,initializeStarted=false;
 let inside=false,contextLost=false,pinned=false,tx=0,ty=0,px=0,py=0,lastSample=null,trail=[],stroke=0,speed=0,lastInput=null,lastMotion=0,meshDirty=true;
 let fallbackCanvas=null,fallbackContext=null,fallbackMask=null,fallbackMaskContext=null,fallbackLayer=null,fallbackLayerContext=null,fallbackReady=false;
 const deg=Math.PI/180,cameraDistance=2.8,eyeZ=.0935;
 const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
 const vertex=`attribute vec3 position;attribute vec3 normal;attribute vec2 texcoord;
 uniform vec3 pivot;uniform vec2 rotation;uniform float modelScale;uniform vec2 resolution;uniform float focal;uniform float eyeScreenY;uniform float distance;
 varying vec2 uv;varying vec3 nrm;
 vec3 rotate(vec3 v){float cy=cos(rotation.x),sy=sin(rotation.x),cx=cos(rotation.y),sx=sin(rotation.y);vec3 p=vec3(cy*v.x+sy*v.z,v.y,-sy*v.x+cy*v.z);return vec3(p.x,cx*p.y-sx*p.z,sx*p.y+cx*p.z);}
 void main(){vec3 p=rotate((position-pivot)*modelScale);p.y+=(1.0-eyeScreenY*2.0)*distance/focal;float z=distance-p.z;float near=.1,far=10.0;gl_Position=vec4(p.x*focal/(resolution.x/resolution.y),p.y*focal,((far+near)/(far-near))*z-2.0*far*near/(far-near),z);uv=texcoord;nrm=rotate(normal);}`;
 const material=`precision highp float;varying vec2 uv;varying vec3 nrm;uniform sampler2D photo;uniform sampler2D silhouette;uniform float older;
 void main(){vec4 col=texture2D(photo,uv);float coverage=texture2D(silhouette,uv).r;if(coverage<.015)discard;float l=dot(col.rgb,vec3(.2126,.7152,.0722));vec3 c=mix(vec3(l),col.rgb,mix(.97,.86,older));c=(c-.5)*.97+.51;c*=mix(vec3(1.0,.993,.976),vec3(1.0,.997,.986),older);float fill=.977+.028*max(0.0,dot(normalize(nrm),normalize(vec3(-.4,.7,2.0))));gl_FragColor=vec4(c*fill*coverage,coverage);}`;
 const screenVertex='attribute vec2 position;varying vec2 uv;void main(){uv=position*.5+.5;gl_Position=vec4(position,0.,1.);}';
 const maskFragment=`precision highp float;varying vec2 uv;uniform vec2 resolution;uniform vec4 strokes[36];uniform float clock;
 float smoothUnion(float a,float b,float k){float h=max(k-abs(a-b),0.0)/k;return min(a,b)-h*h*k*.25;}
 void main(){vec2 p=vec2(uv.x,1.0-uv.y)*resolution;
 // Warp only the mask. Portrait pixels and facial features remain undistorted.
 vec2 flow=vec2(sin(p.y*.022+sin(p.x*.009+clock*.4)*1.8),cos(p.x*.019+sin(p.y*.012-clock*.3)*1.6));
 p+=flow*min(13.0,resolution.y*.017);
 float field=10000.0;
 for(int i=0;i<36;i++){vec4 b=strokes[i];if(b.z>.1){float d=length(p-b.xy)-b.z;
 if(i>0&&b.w>.5){vec4 a=strokes[i-1];vec2 v=b.xy-a.xy;float t=clamp(dot(p-a.xy,v)/max(dot(v,v),.001),0.0,1.0);d=length(p-mix(a.xy,b.xy,t))-mix(a.z,b.z,t);}
 field=smoothUnion(field,d,11.0);}}
 float mask=1.0-smoothstep(-1.0,1.2,field);gl_FragColor=vec4(mask,mask,mask,1.0);}`;
 const composite=`precision highp float;varying vec2 uv;uniform sampler2D first;uniform sampler2D second;uniform sampler2D revealMask;uniform float allReveal;
 void main(){vec2 p=vec2(uv.x,1.0-uv.y);vec3 paper=vec3(.964706,.941176,.886275);
 float vignette=clamp(length((p-vec2(.5,.42))*vec2(.72,.5)),0.,1.);vec3 bg=paper-vec3(.015,.014,.012)*vignette;
 float mask=max(allReveal,texture2D(revealMask,uv).r);
 vec4 a=texture2D(first,uv),b=texture2D(second,uv);a.rgb/=max(a.a,.001);b.rgb/=max(b.a,.001);float bottom=1.0-smoothstep(.78,.97,p.y);a.a*=bottom;b.a*=bottom;
 vec3 sceneA=mix(bg,a.rgb,a.a),sceneB=mix(bg-vec3(.035,.032,.026)*(1.0-allReveal),b.rgb,b.a);
 gl_FragColor=vec4(mix(sceneA,sceneB,mask),1.0);}`;
 function on(target,event,fn,options){target.addEventListener(event,fn,options);listeners.push(()=>target.removeEventListener(event,fn,options))}
 function shader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));resources.push(['shader',s]);return s}
 function program(v,f,attributes,uniformNames){const p=gl.createProgram();gl.attachShader(p,shader(gl.VERTEX_SHADER,v));gl.attachShader(p,shader(gl.FRAGMENT_SHADER,f));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));resources.push(['program',p]);const a={},u={};attributes.forEach(n=>a[n]=gl.getAttribLocation(p,n));uniformNames.forEach(n=>u[n]=gl.getUniformLocation(p,n));return{p,a,u}}
 function buffer(array,type=gl.ARRAY_BUFFER){const b=gl.createBuffer();gl.bindBuffer(type,b);gl.bufferData(type,array,gl.STATIC_DRAW);resources.push(['buffer',b]);return b}
 function bindAttribute(p,name,b,size){const a=p.a[name];if(a<0)return;gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,size,gl.FLOAT,false,0,0)}
 function bytes(s){const b=atob(s),out=new Uint8Array(b.length);for(let i=0;i<b.length;i++)out[i]=b.charCodeAt(i);return out}
 async function unpack(model){const raw=bytes(model.geometry.data);const stream=new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'));const ab=await new Response(stream).arrayBuffer();const meta=model.geometry;const view=name=>{const b=meta.buffers[name];return new Uint16Array(ab,b.byteOffset,b.count)};
  const qp=view('positions'),quv=view('uv'),positions=new Float32Array(qp.length),uvs=new Float32Array(quv.length);for(let i=0;i<qp.length;i++)positions[i]=meta.positionMin[i%3]+qp[i]/65535*meta.positionRange[i%3];for(let i=0;i<quv.length;i++)uvs[i]=quv[i]/65535;
  const front=view('frontIndices'),reverse=view('reverseIndices'),normals=new Float32Array(positions.length);
  for(const indices of [front,reverse])for(let i=0;i<indices.length;i+=3){const a=indices[i]*3,b=indices[i+1]*3,c=indices[i+2]*3,ux=positions[b]-positions[a],uy=positions[b+1]-positions[a+1],uz=positions[b+2]-positions[a+2],vx=positions[c]-positions[a],vy=positions[c+1]-positions[a+1],vz=positions[c+2]-positions[a+2],nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;for(const k of [a,b,c]){normals[k]+=nx;normals[k+1]+=ny;normals[k+2]+=nz}}
  for(let i=0;i<normals.length;i+=3){const l=Math.hypot(normals[i],normals[i+1],normals[i+2])||1;normals[i]/=l;normals[i+1]/=l;normals[i+2]/=l}
  const images=await Promise.all([...model.textures,model.alpha].map(t=>{const im=new Image();im.src=t.data.startsWith('data:')?t.data:`data:${t.mimeType};base64,${t.data}`;return im.decode().then(()=>im)}));
  const textures=images.map(im=>{const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);resources.push(['texture',t]);return t});
  const older=String(model.id).includes('1')||model.role==='revealed'||model.role==='older';
  return{older,position:buffer(positions),normal:buffer(normals),uv:buffer(uvs),front:buffer(front,gl.ELEMENT_ARRAY_BUFFER),reverse:buffer(reverse,gl.ELEMENT_ARRAY_BUFFER),frontCount:front.length,reverseCount:reverse.length,textures,pivot:older?[-.02709,.72393,.0941]:[-.03177,.75756,.093],scale:older?1.032:1,vertexCount:positions.length/3};
 }
 function destroyTargets(){if(!gl)return;for(const t of [...targets,...(maskTarget?[maskTarget]:[])]){gl.deleteFramebuffer(t.fb);gl.deleteTexture(t.texture);gl.deleteRenderbuffer(t.depth)}targets=[];maskTarget=null}
 function makeTarget(w=canvas.width,h=canvas.height){const fb=gl.createFramebuffer(),texture=gl.createTexture(),depth=gl.createRenderbuffer();gl.bindTexture(gl.TEXTURE_2D,texture);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,w,h,0,gl.RGBA,gl.UNSIGNED_BYTE,null);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.bindRenderbuffer(gl.RENDERBUFFER,depth);gl.renderbufferStorage(gl.RENDERBUFFER,gl.DEPTH_COMPONENT16,w,h);gl.bindFramebuffer(gl.FRAMEBUFFER,fb);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,texture,0);gl.framebufferRenderbuffer(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.RENDERBUFFER,depth);if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE)throw Error('Portrait render target unavailable');return{fb,texture,depth,width:w,height:h}}
 function framing(){const mobile=width<651;const pxPerUnit=Math.min(height*(mobile?1.18:1.72),width*(mobile?2.10:2.0));return{focal:pxPerUnit*2*cameraDistance/height,eyeY:mobile?.35:.38,pxPerUnit}}
 function drawModel(model,target){const p=meshProgram,u=p.u,frame=framing();gl.bindFramebuffer(gl.FRAMEBUFFER,target.fb);gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.BLEND);gl.useProgram(p.p);bindAttribute(p,'position',model.position,3);bindAttribute(p,'normal',model.normal,3);bindAttribute(p,'texcoord',model.uv,2);
  gl.uniform3fv(u.pivot,model.pivot);gl.uniform2f(u.rotation,yaw,pitch);gl.uniform1f(u.modelScale,model.scale);gl.uniform2f(u.resolution,width,height);gl.uniform1f(u.focal,frame.focal);gl.uniform1f(u.eyeScreenY,frame.eyeY);gl.uniform1f(u.distance,cameraDistance);gl.uniform1f(u.older,model.older?1:0);gl.uniform1i(u.photo,0);gl.uniform1i(u.silhouette,2);gl.activeTexture(gl.TEXTURE2);gl.bindTexture(gl.TEXTURE_2D,model.textures[2]);
  for(let i=0;i<2;i++){gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,model.textures[i]);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,i?model.reverse:model.front);gl.drawElements(gl.TRIANGLES,i?model.reverseCount:model.frontCount,gl.UNSIGNED_SHORT,0)}
 }
 function drawMask(now){
  const p=maskProgram,u=p.u;gl.bindFramebuffer(gl.FRAMEBUFFER,maskTarget.fb);gl.viewport(0,0,maskTarget.width,maskTarget.height);gl.disable(gl.DEPTH_TEST);gl.useProgram(p.p);bindAttribute(p,'position',screenBuffer,2);gl.uniform2f(u.resolution,width,height);gl.uniform4fv(u['strokes[0]'],strokeData);gl.uniform1f(u.clock,now/1000);gl.drawArrays(gl.TRIANGLES,0,6);
 }
 function draw(now=performance.now()){
  if(disposed)return;
  if(!loaded||contextLost){drawFallback();return}
  const initial=models.find(m=>!m.older),older=models.find(m=>m.older);if(!initial||!older||!maskTarget)return;
  if(meshDirty){drawModel(initial,targets[0]);drawModel(older,targets[1]);meshDirty=false}
  drawMask(now);
  const p=postProgram,u=p.u;gl.bindFramebuffer(gl.FRAMEBUFFER,null);gl.viewport(0,0,canvas.width,canvas.height);gl.disable(gl.DEPTH_TEST);gl.useProgram(p.p);bindAttribute(p,'position',screenBuffer,2);
  targets.forEach((t,i)=>{gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,t.texture);gl.uniform1i(i?u.second:u.first,i)});
  gl.activeTexture(gl.TEXTURE2);gl.bindTexture(gl.TEXTURE_2D,maskTarget.texture);gl.uniform1i(u.revealMask,2);gl.uniform1f(u.allReveal,full);gl.drawArrays(gl.TRIANGLES,0,6);
 }
 function photoScene(ctx,im,older){
  const f=framing(),ph=f.pxPerUnit*1.047,pw=ph*1049/1500;
  ctx.fillStyle=older?'#EDE8DD':'#F6F0E2';ctx.fillRect(0,0,width,height);ctx.drawImage(im,width/2-pw*.456,height*f.eyeY-ph*.188,pw,ph);
  const g=ctx.createLinearGradient(0,height*.78,0,height*.97);g.addColorStop(0,'rgba(246,240,226,0)');g.addColorStop(1,'#F6F0E2');ctx.fillStyle=g;ctx.fillRect(0,height*.78,width,height*.22);
 }
 function drawFallback(){
  if(!fallbackReady||!fallbackContext){olderPhoto.style.opacity=String(full);initialPhoto.style.opacity=String(1-full);return}
  const c=fallbackContext,m=fallbackMaskContext,l=fallbackLayerContext;
  for(const ctx of [c,m,l]){ctx.setTransform(dpr,0,0,dpr,0,0);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.clearRect(0,0,width,height)}
  photoScene(c,initialPhoto,false);photoScene(l,olderPhoto,true);
  m.fillStyle='white';m.strokeStyle='white';m.lineCap='round';m.lineJoin='round';
  for(let i=0;i<N;i++){const k=i*4,x=strokeData[k],y=strokeData[k+1],r=strokeData[k+2];if(r<.1)continue;
   m.beginPath();m.arc(x,y,r,0,Math.PI*2);m.fill();if(i&&strokeData[k+3]>.5){const j=k-4;m.lineWidth=r+strokeData[j+2];m.beginPath();m.moveTo(strokeData[j],strokeData[j+1]);m.lineTo(x,y);m.stroke()}}
  if(full>0){m.globalAlpha=full;m.fillRect(0,0,width,height);m.globalAlpha=1}
  l.globalCompositeOperation='destination-in';l.drawImage(fallbackMask,0,0,width,height);l.globalCompositeOperation='source-over';c.drawImage(fallbackLayer,0,0,width,height);
 }
 async function initFallback(){
  if(fallbackCanvas)return;
  fallbackCanvas=document.createElement('canvas');fallbackCanvas.className='gp-canvas gp-flat-canvas';fallbackCanvas.setAttribute('aria-hidden','true');canvas.after(fallbackCanvas);fallbackContext=fallbackCanvas.getContext('2d');
  fallbackMask=document.createElement('canvas');fallbackMaskContext=fallbackMask.getContext('2d');fallbackLayer=document.createElement('canvas');fallbackLayerContext=fallbackLayer.getContext('2d');
  try{await Promise.all([initialPhoto.decode(),olderPhoto.decode()]);if(disposed)return;fallbackReady=Boolean(fallbackContext&&fallbackMaskContext&&fallbackLayerContext);hero.dataset.renderer=fallbackReady?'canvas-trail':'static-fallback';size();draw();request()}catch{hero.dataset.renderer='static-fallback'}
 }
 function size(){
  const r=hero.getBoundingClientRect();if(r.width<1||r.height<1)return;
  const changed=width!==r.width||height!==r.height;width=r.width;height=r.height;dpr=Math.min(devicePixelRatio||1,1.5);
  const cw=Math.max(1,Math.round(width*dpr)),ch=Math.max(1,Math.round(height*dpr));
  if(canvas.width!==cw||canvas.height!==ch){canvas.width=cw;canvas.height=ch;if(loaded)destroyTargets();meshDirty=true}
  if(loaded&&!targets.length){targets=[makeTarget(),makeTarget()];const ratio=Math.min(.65,640/width);maskTarget=makeTarget(Math.max(1,Math.round(width*ratio)),Math.max(1,Math.round(height*ratio)));meshDirty=true}
  if(fallbackCanvas)for(const c of [fallbackCanvas,fallbackMask,fallbackLayer]){if(c.width!==cw||c.height!==ch){c.width=cw;c.height=ch}}
  const f=framing(),ph=f.pxPerUnit*1.047,pw=ph*1049/1500;hero.style.setProperty('--gp-photo-width',pw+'px');hero.style.setProperty('--gp-photo-left',(width/2-pw*.456)+'px');hero.style.setProperty('--gp-photo-top',(height*f.eyeY-ph*.188)+'px');
  if(changed){interruptIdle();trail=[];lastSample=null;strokeData.fill(0);inside=false;lastInput=null}draw();
 }
 function request(){if(!raf&&active&&visible&&!document.hidden&&!disposed){lastFrame=performance.now();hero.dataset.idle='false';raf=requestAnimationFrame(tick)}}
 function baseRadius(){return Math.min(height*.145,width*.23,112)*settings.radius}
 function fillStroke(now){
  trail=trail.filter(p=>now-p.born<settings.trail*1000);
  if(trail.some(p=>p.automatic)){
   const groups=new Map();for(const p of trail){if(!groups.has(p.stroke))groups.set(p.stroke,[]);groups.get(p.stroke).push(p)}
   trail=Array.from(groups.values()).flatMap(group=>group.slice(-160));
  }else trail=trail.slice(-160);
  let points=trail.slice();
  if(inside&&!pinned&&!reduced.matches&&now-lastMotion<140&&lastSample){points.push({x:px,y:py,r:baseRadius()*(.67+Math.min(speed/1700,.4)),born:lastMotion,stroke})}
  // Opposing emitters arrive interleaved. Pack each ribbon contiguously so the
  // existing shader connects its own points, never bridges between the two swirls.
  if(points.some(p=>p.automatic)){
   const groups=new Map();for(const p of points){if(!groups.has(p.stroke))groups.set(p.stroke,[]);groups.get(p.stroke).push(p)}
   const ribbons=Array.from(groups.values());let remaining=N;
   points=ribbons.flatMap((group,index)=>{
    const budget=Math.min(group.length,Math.floor(remaining/(ribbons.length-index)));remaining-=budget;
    return Array.from({length:budget},(_,i)=>group[Math.round(i*(group.length-1)/Math.max(1,budget-1))]);
   });
  }
  strokeData.fill(0);packedStrokeIds=[];let previousStroke=-1;
  const count=Math.min(N,points.length);
  for(let i=0;i<count;i++){
   const p=points[Math.round(i*(points.length-1)/Math.max(1,count-1))];const age=clamp((now-p.born)/(settings.trail*1000),0,1),r=p.r*Math.pow(1-age,.72);
   const drift=Math.sin(p.x*.013+p.y*.008+age*3.0)*age*10;
   packedStrokeIds.push(p.stroke);strokeData[i*4]=p.x+drift;strokeData[i*4+1]=p.y+Math.cos(p.y*.016-p.x*.01+age*2)*age*8;
   strokeData[i*4+2]=r;strokeData[i*4+3]=p.stroke===previousStroke?1:0;previousStroke=p.stroke;
  }
 }
 function idleAllowed(){return active&&visible&&!document.hidden&&!disposed&&!pinned&&!reduced.matches&&idleFocused}
 function cancelIdle(){clearTimeout(idleTimer);idleTimer=0;idleDue=0;idleFlow=null;hero.dataset.idleFlow='resting'}
 function armIdle(delay=idleSettings.delayMs){
  clearTimeout(idleTimer);idleTimer=0;idleDue=0;
  if(!idleAllowed()||idleFlow)return;
  idleDue=performance.now()+delay;
  idleTimer=setTimeout(()=>{idleTimer=0;idleDue=0;if(idleAllowed())startIdleFlow()},delay);
 }
 function interruptIdle(restart=true){cancelIdle();if(restart)armIdle()}
 function makeIdlePath(random=Math.random,options={}){
  const range=(a,b)=>a+(b-a)*random(),margin=baseRadius()*1.8,frame=framing();
  let right=options.right??(random()>.5);
  // Vary continuously, while preventing long runs of the same entrance/height.
  if(options.right===undefined&&idleLastShape?.sideRun>=2)right=!idleLastShape.right;
  let cy=height*range(.34,.57);
  if(idleLastShape&&Math.abs(cy-idleLastShape.cy)<height*.07)cy=height*(cy/height>.455?range(.34,.405):range(.505,.57));
  const cx=width*(.5+(options.role?range(-.012,.012):range(-.026,.026)));
  const rx=Math.min(width*.23,frame.pxPerUnit*range(options.role?.090:.108,options.role?.119:.142));
  const ry=Math.min(height*.215,rx*range(.80,1.16)),tilt=range(-.26,.26),spin=options.spin??(random()>.5?1:-1);
  if(options.role){
   // The upper curl passes across the eyes; its partner opens the mouth/beard.
   // These complementary targets keep the pair informative as its shape varies.
   const focusY=height*(frame.eyeY+(options.role==='upper'?range(-.018,.012):range(.105,.155)));
   cy=focusY+(options.role==='upper'?1:-1)*ry*.9;
  }
  let angle0=(right?Math.PI:0)+spin*range(.25,.45);
  // Meet the curl while heading into it, including on narrow phone layouts.
  for(let i=0;i<8;i++){
   const dx=(-rx*Math.sin(angle0)*Math.cos(tilt)-ry*Math.cos(angle0)*Math.sin(tilt))*spin;
   const dy=(-rx*Math.sin(angle0)*Math.sin(tilt)+ry*Math.cos(angle0)*Math.cos(tilt))*spin;
   if((right?1:-1)*dx/Math.hypot(dx,dy)>.22)break;
   angle0+=spin*.06;
  }
  // Release while the tangent is still travelling toward the exit. Extending past
  // this point creates a hairpin at the orbit/exit join, even with matching tangents.
  let release=range(.35,.65),angle1=(right?(spin>0?Math.PI*2:0):(spin>0?Math.PI:-Math.PI))-spin*release;
  for(let i=0;i<8;i++){
   const dx=(-rx*Math.sin(angle1)*Math.cos(tilt)-ry*Math.cos(angle1)*Math.sin(tilt))*spin;
   const dy=(-rx*Math.sin(angle1)*Math.sin(tilt)+ry*Math.cos(angle1)*Math.cos(tilt))*spin;
   if((right?1:-1)*dx/Math.hypot(dx,dy)>.28)break;
   release+=.07;angle1-=spin*.07;
  }
  const sweep=angle1-angle0;
  const rotate=(x,y)=>({x:cx+x*Math.cos(tilt)-y*Math.sin(tilt),y:cy+x*Math.sin(tilt)+y*Math.cos(tilt)});
  const orbit=t=>{const angle=angle0+sweep*t;return rotate(rx*Math.cos(angle),ry*Math.sin(angle))};
  const tangent=t=>{const angle=angle0+sweep*t,x=-rx*Math.sin(angle)*sweep,y=ry*Math.cos(angle)*sweep;const dx=x*Math.cos(tilt)-y*Math.sin(tilt),dy=x*Math.sin(tilt)+y*Math.cos(tilt),length=Math.hypot(dx,dy);return{x:dx/length,y:dy/length}};
  const entry={x:right?-margin:width+margin,y:clamp(cy+height*range(-.18,.18),height*.14,height*.76)};
  const exit={x:right?width+margin:-margin,y:clamp(cy+height*range(-.20,.20),height*.14,height*.78)};
  const first=orbit(0),last=orbit(1),tin=tangent(0),tout=tangent(1),direction=right?1:-1,handle=rx*range(.48,.70);
  const points=[];
  function bezier(a,b,c,d,steps){for(let i=0;i<=steps;i++){const t=i/steps,v=1-t;points.push({x:v*v*v*a.x+3*v*v*t*b.x+3*v*t*t*c.x+t*t*t*d.x,y:v*v*v*a.y+3*v*v*t*b.y+3*v*t*t*c.y+t*t*t*d.y})}}
  bezier(entry,{x:entry.x+direction*Math.abs(first.x-entry.x)*.55,y:entry.y},{x:first.x-tin.x*handle,y:first.y-tin.y*handle},first,42);
  const orbitStart=points.length-1;
  for(let i=1;i<=88;i++)points.push(orbit(i/88));
  const orbitEnd=points.length-1;
  bezier(last,{x:last.x+tout.x*handle,y:last.y+tout.y*handle},{x:exit.x-direction*Math.abs(exit.x-last.x)*.48,y:exit.y},exit,42);
  const lengths=[0];for(let i=1;i<points.length;i++)lengths.push(lengths[i-1]+Math.hypot(points[i].x-points[i-1].x,points[i].y-points[i-1].y));
  const length=lengths[lengths.length-1],baseDuration=options.baseDuration??range(idleSettings.baseDurationMinMs,idleSettings.baseDurationMaxMs);
  const pixelsPerSecond=(width+2*margin)/(baseDuration/1000)*idleSettings.speedMultiplier;
  return{points,lengths,length,baseDuration,role:options.role||null,duration:length/pixelsPerSecond*1000,pixelsPerSecond,basePixelsPerSecond:pixelsPerSecond/idleSettings.speedMultiplier,right,cy,cx,rx,ry,spin,sweep,orbitStart:lengths[orbitStart]/length,orbitEnd:lengths[orbitEnd]/length,widthScale:range(.68,.82)};
 }
 function idlePoint(flow,u){
  // Arc-length lookup keeps the curl moving at a constant speed without corner stalls.
  const distance=clamp(u,0,1)*flow.length;let lo=0,hi=flow.lengths.length-1;
  while(lo+1<hi){const mid=(lo+hi)>>1;if(flow.lengths[mid]<distance)lo=mid;else hi=mid}
  const a=flow.points[lo],b=flow.points[hi],t=(distance-flow.lengths[lo])/Math.max(.0001,flow.lengths[hi]-flow.lengths[lo]);
  return{x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t};
 }
 function makeIdlePair(random=Math.random){
  const right=random()>.5,spin=random()>.5?1:-1;
  const role=right===(spin>0)?'upper':'lower';
  const first=makeIdlePath(random,{right,spin,role});
  const second=makeIdlePath(random,{right:!right,spin,role:role==='upper'?'lower':'upper',baseDuration:clamp(first.baseDuration*(.96+random()*.08),idleSettings.baseDurationMinMs,idleSettings.baseDurationMaxMs)});
  const middle=path=>(path.orbitStart+path.orbitEnd)*.5*path.duration;
  // Arrive near the face together, with a small playful offset rather than a mirror.
  const difference=middle(first)-middle(second)+(random()>.5?1:-1)*(90+random()*150);
  first.delay=Math.min(360,Math.max(0,-difference));second.delay=Math.min(360,Math.max(0,difference));
  return[first,second].sort((a,b)=>a.delay-b.delay);
 }
 function startIdleFlow(){
  const paths=makeIdlePair(),now=performance.now();
  idleFlow={members:paths.map((path,index)=>({...path,start:now+path.delay,stroke:-(idlePasses*2+index+1),last:null,finished:false}))};
  idlePasses++;hero.dataset.idleFlow='running';request();
 }
 function advanceIdle(now){
  const pair=idleFlow;if(!pair)return;
  if(!idleAllowed()){cancelIdle();return}
  for(const flow of pair.members){
   if(flow.finished||now<flow.start)continue;
   const u=clamp((now-flow.start)/flow.duration,0,1),point=idlePoint(flow,u);
   const radius=baseRadius()*flow.widthScale*(.67+Math.min(flow.pixelsPerSecond/1700,.4));
   const previous=flow.last||point,distance=Math.hypot(point.x-previous.x,point.y-previous.y);
   const count=Math.min(40,Math.max(1,Math.ceil(distance/Math.max(7,baseRadius()*.13))));
   for(let i=1;i<=count;i++){
    const t=i/count;trail.push({x:previous.x+(point.x-previous.x)*t,y:previous.y+(point.y-previous.y)*t,r:radius,born:now,stroke:flow.stroke,automatic:true});
   }
   flow.last=point;if(u>=1)flow.finished=true;
  }
  if(pair.members.every(flow=>flow.finished)){idleFlow=null;hero.dataset.idleFlow='resting';armIdle(idleSettings.gapMinMs+Math.random()*(idleSettings.gapMaxMs-idleSettings.gapMinMs))}
 }
 function inspectIdle(){
  const describe=flow=>({entrySide:flow.right?'left':'right',exitSide:flow.right?'right':'left',center:[flow.cx,flow.cy],radius:[flow.rx,flow.ry],spin:flow.spin,sweepRadians:flow.sweep,durationMs:flow.duration,pixelsPerSecond:flow.pixelsPerSecond,basePixelsPerSecond:flow.basePixelsPerSecond,orbitStart:flow.orbitStart,orbitEnd:flow.orbitEnd,role:flow.role,ribbonRadius:baseRadius()*flow.widthScale*(.67+Math.min(flow.pixelsPerSecond/1700,.4))});
  const members=idleFlow?.members||[],first=members[0];
  return{running:Boolean(idleFlow),dueInMs:idleDue?Math.max(0,idleDue-performance.now()):null,passes:idlePasses,delayMs:idleSettings.delayMs,point:first?.last||null,speedMultiplier:idleSettings.speedMultiplier,route:first?describe(first):null,members:members.map(flow=>({point:flow.last,finished:flow.finished,delayMs:flow.delay,stroke:flow.stroke,route:describe(flow)}))};
 }
 function tick(now){
  raf=0;if(!active||!visible||document.hidden||disposed)return;
  const dt=clamp((now-lastFrame)/1000,.001,.04);lastFrame=now;
  const ease=reduced.matches?1:1-Math.exp(-dt*9),oldYaw=yaw,oldPitch=pitch;
  yaw+=(targetYaw-yaw)*ease;pitch+=(targetPitch-pitch)*ease;full+=(targetFull-full)*(reduced.matches?1:1-Math.exp(-dt*12));if(Math.abs(targetFull-full)<.0005)full=targetFull;
  if(Math.abs(yaw-oldYaw)+Math.abs(pitch-oldPitch)>.000001)meshDirty=true;
  const dx=tx-px,dy=ty-py,follow=1-Math.exp(-dt*24);const oldX=px,oldY=py;px+=dx*follow;py+=dy*follow;
  speed+=(Math.hypot(px-oldX,py-oldY)/dt-speed)*(1-Math.exp(-dt*12));
  if(inside&&!pinned&&!reduced.matches&&now-lastMotion<180){
   if(!lastSample){lastSample={x:px,y:py};trail.push({x:px,y:py,r:baseRadius()*.7,born:now,stroke})}
   const vx=px-lastSample.x,vy=py-lastSample.y,distance=Math.hypot(vx,vy),step=Math.max(7,baseRadius()*.13),count=Math.min(40,Math.floor(distance/step));
   for(let i=1;i<=count;i++){const t=i*step/Math.max(distance,.001);trail.push({x:lastSample.x+vx*t,y:lastSample.y+vy*t,r:baseRadius()*(.67+Math.min(speed/1700,.4)),born:now-dt*1000*(1-t),stroke})}
   if(count){const t=count*step/Math.max(distance,.001);lastSample={x:lastSample.x+vx*t,y:lastSample.y+vy*t}}
  }
  advanceIdle(now);fillStroke(now);draw(now);
  const moving=Math.abs(targetYaw-yaw)>.00002||Math.abs(targetPitch-pitch)>.00002||Math.abs(targetFull-full)>.0005||trail.length>0||inside&&Math.hypot(dx,dy)>.15;
  if(moving||idleFlow)raf=requestAnimationFrame(tick);else hero.dataset.idle='true';
 }
 function move(event){
  if(!active)return;if(event.target.closest('a,button')){leave();return}if(event.pointerType==='touch'&&event.buttons===0)return;
  const b=hero.getBoundingClientRect(),x=event.clientX-b.left,y=event.clientY-b.top;if(!Number.isFinite(x+y))return;
  if(lastInput&&Math.hypot(x-lastInput.x,y-lastInput.y)<.4)return;lastInput={x,y};lastMotion=performance.now();interruptIdle();
  if(!inside){inside=true;px=tx=x;py=ty=y;lastSample=null;stroke++;speed=0}
  tx=x;ty=y;targetYaw=reduced.matches?0:clamp((x/width-.5)*2,-1,1)*settings.yaw*deg;targetPitch=reduced.matches?0:clamp((y/height-.5)*2,-1,1)*settings.pitch*deg;
  if(!pinned&&!reduced.matches)root.__gurudevLiquidSound?.motion(x,y,performance.now());else root.__gurudevLiquidSound?.silence('no-reveal');
  hero.dataset.explored='true';request();
 }
 function leave(){interruptIdle();root.__gurudevLiquidSound?.silence('pointer-exit');inside=false;lastSample=null;lastInput=null;targetYaw=targetPitch=0;request()}
 function reveal(value=true,persist=true){
  root.__gurudevLiquidSound?.silence('portrait-toggle');
  interruptIdle(false);pinned=Boolean(value);targetFull=pinned?1:0;trail=[];strokeData.fill(0);lastSample=null;inside=false;lastInput=null;
  toggle.textContent=pinned?'Return to first portrait':'Reveal portrait';toggle.setAttribute('aria-pressed',String(pinned));status.textContent=pinned?'The older portrait is visible.':'Move across the portrait to reveal the older Gurudev through a flowing trail.';
  armIdle();if(reduced.matches){full=targetFull;draw()}request();if(persist)root.dispatchEvent(new CustomEvent('gurudev:portrait-choice',{detail:{revealed:pinned}}));
 }
 function startInitialize(){if(initializeStarted||disposed)return;initializeStarted=true;initialize()}
 function activate(value){interruptIdle(false);active=Boolean(value);root.__gurudevLiquidSound?.setActive(active);if(active){startInitialize();size();request();armIdle()}else{cancelAnimationFrame(raf);raf=0;inside=false;trail=[];strokeData.fill(0);lastSample=null;lastInput=null;targetYaw=targetPitch=yaw=pitch=0;meshDirty=true}}
 async function initialize(){
  try{
   if(!('DecompressionStream' in window))throw Error('Geometry decoder unavailable');
   gl=canvas.getContext('webgl',{alpha:false,antialias:true,powerPreference:'low-power',premultipliedAlpha:false});if(!gl)throw Error('WebGL unavailable');
   meshProgram=program(vertex,material,['position','normal','texcoord'],['pivot','rotation','modelScale','resolution','focal','eyeScreenY','distance','older','photo','silhouette']);
   maskProgram=program(screenVertex,maskFragment,['position'],['resolution','strokes[0]','clock']);
   postProgram=program(screenVertex,composite,['position'],['first','second','revealMask','allReveal']);
   screenBuffer=buffer(new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]));
   const response=await fetch(hero.dataset.models,{credentials:'same-origin'});if(!response.ok)throw Error(`Portrait models unavailable (${response.status})`);const payload=await response.json();if(disposed)return;models=await Promise.all(payload.models.map(unpack));if(disposed)return;
   loaded=true;size();draw();hero.dataset.renderer='webgl-3d';hero.dataset.geometry='actual-glb-mesh';hero.dataset.reveal='cursor-fluid-trail';request();
  }catch(error){hero.dataset.rendererReason=error.message;loaded=false;initFallback()}
 }
 function cleanup(){if(disposed)return;disposed=true;cancelIdle();root.__gurudevLiquidSound?.dispose();cancelAnimationFrame(raf);resizeObserver?.disconnect();intersectionObserver?.disconnect();removalObserver?.disconnect();listeners.forEach(fn=>fn());destroyTargets();if(gl&&!contextLost)for(const [type,obj] of resources){const fn={texture:'deleteTexture',buffer:'deleteBuffer',shader:'deleteShader',program:'deleteProgram'}[type];gl[fn](obj)}resources=[];fallbackCanvas?.remove()}
 on(hero,'pointermove',move);on(hero,'pointerleave',leave);on(hero,'pointercancel',leave);on(window,'blur',()=>{idleFocused=false;leave()});on(window,'focus',()=>{idleFocused=true;armIdle()});on(toggle,'click',()=>reveal(!pinned));
 on(hero,'pointerover',e=>{if(e.target.closest('a,button'))leave()});
 on(hero,'pointerdown',e=>{if(e.pointerType==='touch')move(e)});on(hero,'pointerup',e=>{if(e.pointerType==='touch')leave()});
 on(document,'visibilitychange',()=>{interruptIdle(false);if(document.hidden){cancelAnimationFrame(raf);raf=0;inside=false;lastInput=null;trail=[];strokeData.fill(0);targetYaw=targetPitch=0}else{request();armIdle()}});
 on(window,'scroll',()=>{interruptIdle();if(inside)leave()},{passive:true});
 on(reduced,'change',()=>{interruptIdle(false);if(reduced.matches){targetYaw=targetPitch=yaw=pitch=0;full=targetFull;trail=[];strokeData.fill(0);meshDirty=true;draw()}request();armIdle()});
 on(canvas,'webglcontextlost',event=>{event.preventDefault();contextLost=true;loaded=false;initFallback()});
 resizeObserver=new ResizeObserver(size);resizeObserver.observe(hero);
 // The site's header is fixed over the top of the page, so a portrait scrolled
 // up behind it, or down to a sliver beneath it, counts as out of view.
 const headerHeight=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nv-hh'))||0;
 intersectionObserver=new IntersectionObserver(entries=>{const entry=entries[entries.length-1];const next=entry?(entry.isIntersecting&&entry.intersectionRatio>=.05):true;if(next===visible)return;visible=next;root.__gurudevLiquidSound?.setVisible(visible);interruptIdle(false);if(visible){request();armIdle()}else{cancelAnimationFrame(raf);raf=0;inside=false;trail=[];strokeData.fill(0)}},{rootMargin:`-${headerHeight}px 0px 0px 0px`,threshold:[0,.05]});intersectionObserver.observe(hero);
 removalObserver=new MutationObserver(()=>{if(!root.isConnected)cleanup()});removalObserver.observe(document.documentElement,{childList:true,subtree:true});
 hint.textContent=coarse.matches?'Drag across the portrait.':'Move across the portrait.';
 root.__gurudevPortrait={activate,reset(){reveal(false,false);full=targetFull=0;targetYaw=targetPitch=yaw=pitch=0;meshDirty=true;hero.dataset.explored='false';draw()},reveal,dispose:cleanup,inspect(){return{active,loaded,renderer:hero.dataset.renderer,reveal:'cursor-fluid-trail',inside,pinned,full,trailCount:trail.length,trailLifetime:settings.trail,idleFlow:inspectIdle(),packedStrokeIds:packedStrokeIds.slice(),maskSamples:Array.from(strokeData),automaticTrailCount:trail.filter(p=>p.automatic).length,strokeCount:Array.from(strokeData).filter((v,i)=>i%4===2&&v>.1).length,yaw:yaw/deg,pitch:pitch/deg,targetYaw:targetYaw/deg,targetPitch:targetPitch/deg,vertexCounts:models.map(m=>m.vertexCount),rafRunning:Boolean(raf),size:[width,height]}}};
 // The hero is hidden behind the opening film on a fresh visit. Its 2.8 MB
 // packed portrait payload is not needed until the portrait becomes visible.
 // activate(true) also covers deep links and the reduced-motion fast path.
 size();
 if(!hero.hidden)startInitialize();
})();
