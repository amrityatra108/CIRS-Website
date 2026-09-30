// Shared timing keeps the particle field, energy bands and photos in one body.
export const ORB_MOTION_GLSL = `
float morphProgress(float intro){
  float x=clamp((intro-4.85)/1.55,0.,1.);
  return x*x*x*(x*(x*6.-15.)+10.);
}
float energyClock(float intro){
  float t=max(0.,intro-.85);
  return t<=4.?t:4.+(1.-exp(-(t-4.)*3.))/3.;
}
float energyPulse(float clock){
  return .93+.075*cos(clock*9.42477796)+.012*sin(clock*22.7);
}
float energyTension(float clock){
  return clamp((1.017-energyPulse(clock))/.174,0.,1.);
}
`;
export function morphProgress(intro){const x=Math.max(0,Math.min(1,(intro-4.85)/1.55));return x*x*x*(x*(x*6-15)+10);}
export function energyClock(intro){const t=Math.max(0,intro-.85);return t<=4?t:4+(1-Math.exp(-(t-4)*3))/3;}
export function energyPulse(clock){return .93+.075*Math.cos(clock*9.42477796)+.012*Math.sin(clock*22.7);}
