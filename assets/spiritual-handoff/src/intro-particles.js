import { ORB_MOTION_GLSL } from './orb-motion.js?v=83bf040586';
// One field rushes from every screen edge, circulates as an orb, then resolves to the exact logo.
export const INTRO = Object.freeze({ orbStart:.85, formationStart:4.85, complete:6.4, orbRadius:1.35 });
export const logoVertexShader = `
attribute vec3 aNormal;
attribute vec3 aRest;
attribute float aHeat;
attribute float aSeed;
uniform float uTime,uIntro,uDpr,uPointScale;
uniform vec2 uEdge;
varying vec3 vColor;
varying float vAlpha;
varying vec2 vTrailDirection;
varying float vTrail;
${ORB_MOTION_GLSL}
float random(float value){return fract(sin(value)*43758.5453);}
vec3 orb(float time){
  float a=random(aSeed*7183.9)*6.283185;
  float y=random(aSeed*3219.7)*2.-1.;
  float radial=sqrt(max(0.,1.-y*y));
  float swirl=time*(2.9+random(aSeed*5193.3)*1.5);
  a+=swirl+y*3.4+sin(time*3.1+y*6.)*.36;
  float shell=.94+.032*sin(a*5.+time*6.)+.021*sin(y*19.-time*4.);
  vec3 p=vec3(cos(a)*radial,y,sin(a)*radial)*1.35*shell;
  float tilt=.32*sin(time*1.8)+.13*sin(time*3.7);
  p.xy=mat2(cos(tilt),-sin(tilt),sin(tilt),cos(tilt))*p.xy;
  return p*energyPulse(time);
}
vec3 edge(){
  float a=random(aSeed*9321.3)*6.283185;
  vec2 ray=vec2(cos(a),sin(a));
  float stretch=min(uEdge.x/max(abs(ray.x),.001),uEdge.y/max(abs(ray.y),.001));
  return vec3(ray*stretch*(1.02+random(aSeed*719.1)*.38),(random(aSeed*381.3)-.5)*2.);
}
void main(){
  float t=uIntro;
  float formed=morphProgress(t);
  vec3 p=position;
  float clock=energyClock(t);
  if(t<.85){
    float arrival=clamp((t-aSeed*.12)/(.72-aSeed*.02),0.,1.);
    float ease=1.-pow(1.-arrival,2.);
    p=mix(edge(),orb(0.),ease);
    vec2 tangent=vec2(-p.y,p.x);
    p.xy+=tangent*sin(arrival*3.14159)*.22;
  }else if(t<4.85){
    p=orb(clock);
  }else if(t<6.4){
    p=mix(orb(clock),position,formed);
    p.z+=sin(formed*3.14159)*sin(aSeed*32.)*.12;
  }
  vec4 viewPosition=modelViewMatrix*vec4(p,1.);
  gl_Position=projectionMatrix*viewPosition;
  vec3 n=normalize(normalMatrix*aNormal);
  float lighting=.52+.48*max(dot(n,normalize(vec3(-.4,.8,1.))),0.);
  float grain=random(aSeed*5294.2);
  vec3 chrome=mix(vec3(.08,.095,.115),vec3(.72,.78,.86),grain)*lighting;
  vec3 dust=mix(vec3(.34,.15,.045),vec3(1.12,.73,.31),pow(aSeed,3.));
  vColor=mix(dust,chrome,formed);
  vColor=mix(vColor,vec3(.88,.93,1.),aHeat*.70);
  float incoming=1.-smoothstep(.55,.85,t);
  float population=step(random(aSeed*9182.3),mix(mix(.48,.72,incoming),1.,formed));
  vColor=mix(vColor,mix(vec3(.25,.10,.03),vec3(.72,.42,.13),aSeed),incoming);
  vTrail=incoming*step(.52,aSeed);
  vTrailDirection=normalize(p.xy+vec2(.001));
  float shellRim=smoothstep(.35,1.14,length(p.xy));
  float orbAlpha=mix((.23+.55*pow(aSeed,4.))*mix(.28,1.,shellRim),.80,incoming);
  orbAlpha*=1.+energyTension(clock)*.32;
  float displacement=length(position-aRest);
  // Dust becomes a quiet edge shimmer once the solid chrome emblem arrives.
  // Displaced grains remain bright, so a touch still reads as disintegration.
  float finalAlpha=mix(.012+grain*.010,.42,smoothstep(.025,.19,displacement));
  vAlpha=mix(orbAlpha,finalAlpha,formed)*population*smoothstep(0.,.09,t);
  float pointSize=mix(1.1+aSeed*1.25,1.15+aSeed*.85+aHeat*1.2,formed);
  pointSize=mix(pointSize,mix(2.0,7.0,vTrail),incoming);
  gl_PointSize=clamp(pointSize*uDpr*uPointScale*(8.2/max(.08,-viewPosition.z)),.8,14.);
}`;
export const logoFragmentShader = `
varying vec3 vColor;
varying float vAlpha;
varying vec2 vTrailDirection;
varying float vTrail;
void main(){
  vec2 q=(gl_PointCoord-.5)*2.;
  float along=dot(q,vTrailDirection),across=dot(q,vec2(-vTrailDirection.y,vTrailDirection.x));
  float d=length(vec2(along,across/mix(1.,.19,vTrail)));
  if(d>1.)discard;
  float alpha=(1.-smoothstep(.35,1.,d))*vAlpha;
  if(alpha<.025)discard;
  gl_FragColor=vec4(vColor,alpha);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;
