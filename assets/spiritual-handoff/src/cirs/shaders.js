export const fullscreenVertex=`varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}`;
export const photoVertex=`
varying vec2 vUv;
uniform float uBend;
void main(){
 vUv=uv; vec3 p=position;
 // One sheet, with a shallow travelling bow. Both its image and coverage
 // share these vertices; the deformation becomes exactly zero at arrival.
 float edge=pow(abs(p.x)*2.,2.);
 p.z+=uBend*(edge-.30)*(0.70+0.30*cos(p.y*3.14159265));
 p.x+=uBend*.16*sin(p.y*3.14159265)*(1.-edge);
 gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);
}`;
export const photoFragment=`
varying vec2 vUv;
uniform sampler2D uPhoto;
uniform vec2 uCropScale,uCropOffset;
uniform float uOpening,uCalibration;
void main(){
 vec2 q=abs(vUv-.5)-vec2(.5-(1.-uOpening)*.025);
 float d=length(max(q,0.))+min(max(q.x,q.y),0.)-(1.-uOpening)*.025;
 float aa=max(fwidth(d),.00001);float a=1.-smoothstep(-aa,aa,d);
 // Undo the final .4% overscan in UVs so the permanent CSS cover crop agrees.
 vec2 uv=clamp((vUv-.5)*1.004+.5,0.,1.);
 uv=uCropOffset+uv*uCropScale;
 vec3 rgb=texture2D(uPhoto,uv).rgb;
 if(uCalibration>.5){rgb=vUv.x<.33?vec3(1.,0.,0.):vUv.x<.66?vec3(0.,.5,0.):vec3(0.,0.,1.);}
 // Linear, premultiplied RGBA. No blending or tone map in this pass.
 gl_FragColor=vec4(rgb*a,a);
}`;
export const compositeFragment=`
varying vec2 vUv;
uniform sampler2D uPhotoSurface,uWordmark,uReveal,uExit;
uniform vec2 uViewport;
uniform vec3 uCream;
uniform float uTime,uLogoScale,uDeparture,uMaskView;
float ss(float a,float b,float t){float x=clamp((t-a)/(b-a),0.,1.);return x*x*(3.-2.*x);}
float sdBox(vec2 p,vec2 b,float r){vec2 q=abs(p)-b+vec2(r);return length(max(q,0.))+min(max(q.x,q.y),0.)-r;}
float coverage(float d){float aa=max(fwidth(d),.00001);return 1.-smoothstep(-aa,aa,d);}
float field(vec2 p){
 const vec2 cell=vec2(68.,112.);
 vec2 index=floor(p/cell);float dist=1000.;
 for(int iy=-1;iy<=1;iy++)for(int ix=-1;ix<=1;ix++){
  vec2 id=index+vec2(float(ix),float(iy));
  vec2 center=(id+.5)*cell;
  center.x+=mod(id.y,2.)*cell.x*.5;
  float band=.10*id.x/24.+.06*sin(id.y*.65);
  float establish=ss(-.16+band,.55+band,uTime);
  float thicken=ss(.35,1.05,uTime);
  // A single broad diagonal travel field clears whole neighbouring regions.
  float retreat=ss(.84+band,2.09+band,uTime);
  float width=mix(10.,14.5,thicken)*establish;
  float halfLength=mix(36.,48.,thicken)*establish*(1.-.30*retreat);
  vec2 q=p-center+vec2(0.,9.*retreat);
  float stem=sdBox(q,vec2(max(width,.001),max(halfLength,.001)),min(width,9.));
  float connected=mod(id.x+id.y*2.,4.);
  if(connected<1.5){
   float side=mod(id.y,2.)<.5?1.:-1.;
   float bridge=sdBox(q-vec2(side*23.,halfLength*.30),vec2(25.,mix(6.,10.,thicken)),5.);
   stem=min(stem,bridge);
  }
  // Connected material drains along a vertical plane, then disappears.
  // This is continuous clipping, not islands that turn into blinking dots.
  float cut=(retreat*2.35-1.25)*(halfLength+16.);
  stem=max(stem,cut-q.y);
  dist=min(dist,stem);
 }
 return dist;
}
void main(){
 vec2 screen=vec2(vUv.x,1.-vUv.y);
 vec2 p=(screen-.5)*uViewport/min(uViewport.x/1600.,uViewport.y/900.);
 vec2 logoUV=vec2(.5+p.x/(1600.*uLogoScale),.5-p.y/(900.*uLogoScale));
 bool valid=all(greaterThanEqual(logoUV,vec2(0.)))&&all(lessThanEqual(logoUV,vec2(1.)));
 vec4 w=texture2D(uWordmark,clamp(logoUV,0.,1.));
 float sd=(dot(w.rg,vec2(65280.,255.))/65535.)*512.-256.;
 if(!valid)sd=256.;
 float order=texture2D(uReveal,clamp(logoUV,0.,1.)).r;
 vec2 lp=vec2(logoUV.x*1600.,(1.-logoUV.y)*900.);
 float front=290.+1080.*ss(.60,1.90,uTime);
 float edge=lp.x-front+24.*sin((lp.y-450.)/155.)+16.*(order-logoUV.x);
 // A moving material front fills full-weight portions of the original
 // silhouette. It never erodes the whole glyph into thin handwriting.
 float logo=coverage(max(sd,edge));
 float exact=valid?w.b:0.;
 logo=mix(logo,exact,ss(1.96,2.16,uTime));
 float f=field(p+vec2(800.,450.));
 // Negative space opens immediately behind the formation front. Filled
 // letters are unioned afterwards, so neither counters nor fields can
 // re-perforate a resolved glyph.
 float readingArea=sd-76.;
 float clearing=coverage(max(readingArea,edge+42.));
 float material=coverage(f)*(1.-clearing);
 if(uTime>=2.35)material=0.;
 float inkMask=max(logo,material);
 if(uTime>=2.35)inkMask=exact;
 if(uDeparture>0.){
  float orderOut=texture2D(uExit,clamp(logoUV,0.,1.)).r;
  float delta=orderOut-uDeparture;
  float aa=max(fwidth(delta),.002);
  inkMask*=smoothstep(-aa,aa,delta);
 }
 if(uDeparture>=1.)inkMask=0.;
 vec4 photo=texture2D(uPhotoSurface,vUv);
 float a=clamp(photo.a,0.,1.);
 vec3 scene=photo.rgb; // black background; RGB is already premultiplied.
 vec3 ink=mix(uCream,vec3(1.),a);
 vec3 rgb=mix(scene,ink,inkMask);
 if(uMaskView>.5)rgb=vec3(a);
 gl_FragColor=vec4(rgb,1.);
 #include <colorspace_fragment>
}`;
