export const DURATION=6.25;
export const clamp=x=>Math.min(1,Math.max(0,x));
export const smooth=x=>{x=clamp(x);return x*x*x*(x*(x*6-15)+10);};
export function evaluateSequence(seconds){
 const t=Math.max(0,Math.min(DURATION,Number(seconds)||0));
 const opening=smooth(Math.pow(clamp((t-2.65)/1.6),3.1));
 return Object.freeze({time:t,opening,angle:(1-opening)*88.9*Math.PI/180,
  expansion:.72+.284*smooth((t-2.65)/.57),bend:.13*Math.sin(Math.PI*opening),
  departure:clamp((t-4.5)/.85),
  headings:[5.2,5.36,5.52].map(start=>1-Math.pow(1-clamp((t-start)/.5),4)),
  phase:t<2.35?'formation':t<2.65?'hold':t<4.25?'photo-turn':t<4.5?'photo-hold':t<5.35?'departure':t<6.25?'headings':'hero'
 });
}
export function coverCrop(width,height,photoWidth=1672,photoHeight=941){
 const view=width/height,source=photoWidth/photoHeight;
 const xScale=Math.min(1,view/source),yScale=Math.min(1,source/view);
 const focusX=width<=700?.465:.5;
 return {scale:[xScale,yScale],offset:[(1-xScale)*focusX,1-yScale],objectPosition:`${focusX*100}% 0%`};
}
