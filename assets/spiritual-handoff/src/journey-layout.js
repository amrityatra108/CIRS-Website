// The mountain, bridge and embedded chapter journey share this measured map.
// A viewport means the actual sticky stage height, including mobile svh rules.
let layout = null;
function ensureSanctuaryApproach() {
  const sanctuary = document.querySelector('#spiritual');
  if (!sanctuary) return null;
  let approach = sanctuary.parentElement;
  if (!approach.classList.contains('sanctuary-approach')) {
    approach = document.createElement('div');
    approach.className = 'sanctuary-approach';
    sanctuary.before(approach); approach.append(sanctuary);
  }
  return { sanctuary, approach };
}
export function measureJourneyLayout() {
  const mountain=document.querySelector('#tapovan-journey');
  const stage=mountain?.querySelector('.tapovan-sticky');
  const host=document.querySelector('#crossroads-helix');
  if(!mountain||!stage||!host)return layout;
  const h=stage.offsetHeight||innerHeight;
  const isStatic=matchMedia('(prefers-reduced-motion: reduce)').matches||mountain.classList.contains('is-static');
  const entry = ensureSanctuaryApproach();
  if (entry) {
    // The same live sanctuary stays pinned while the real first mountain frame
    // is revealed above it. Native mountain scrolling begins at the endpoint.
    entry.approach.classList.toggle('is-static', isStatic);
    entry.approach.style.height=`${entry.sanctuary.offsetHeight+(isStatic?0:1.8*h)}px`;
    mountain.style.marginTop=isStatic?'0px':`${-h}px`;
  }
  mountain.style.height=isStatic?`${h}px`:`${9*h}px`;
  const tapovanStart=mountain.getBoundingClientRect().top+scrollY;
  const sanctuaryStart=entry?entry.approach.getBoundingClientRect().top+scrollY:tapovanStart-h;
  const entryEnd=tapovanStart, entryStart=entryEnd-(isStatic?0:1.3*h);
  const filmStart=tapovanStart;
  const phraseSpan=isStatic?0:6*h;
  const holdStart=filmStart+phraseSpan;
  const bridgeStart=holdStart+(isStatic?0:.5*h);
  const bridgeEnd=bridgeStart+(isStatic?0:1.5*h);
  const hostTop=isStatic?tapovanStart+mountain.offsetHeight:holdStart;
  layout=Object.freeze({sanctuaryStart,entryStart,entryEnd,filmStart,tapovanStart,phraseSpan,holdStart,bridgeStart,bridgeEnd,helixStart:isStatic?hostTop:bridgeEnd,hostTop,viewportHeight:h,isStatic});
  host.style.marginTop=isStatic?'0px':`${-3*h}px`;
  dispatchEvent(new CustomEvent('cirs:journey-layout',{detail:layout}));
  return layout;
}
export function getJourneyLayout(){return layout||measureJourneyLayout();}
export const clamp01=value=>Math.max(0,Math.min(1,value));
export const smooth=value=>{const p=clamp01(value);return p*p*p*(p*(p*6-15)+10);};
export function evaluateJourneyBridge(progress){
  const p=clamp01(progress),r=(a,b)=>smooth((p-a)/(b-a));
  // A lower-density veil reveals the first mountain image earlier, so the room
  // and its warm sky coexist through one broad, gentle arrival rather than
  // first obscuring the whole room and then exposing a separate scene.
  return {progress:p,reveal:r(.16,.88),veil:r(.04,.28)*(1-r(.60,.94)),lift:100-190*r(.06,.94),drift:3.3*Math.sin(Math.PI*p),finished:p===1};
}

// An aperture in a stationary, live viewport. The first geometry is circular;
// its bounds then widen into a rounded rectangle without scaling its contents.
// All lengths use the actual stage pixels, so a circle stays circular on phones.
export function evaluateLivePortal(progress, width, height) {
  const p=clamp01(progress), w=Math.max(1,width), h=Math.max(1,height);
  const circleSize=Math.min(w,h)*.62;
  const establish=smooth(p/.3);
  const expand=smooth((p-.3)/.7);
  const diameter=circleSize*establish;
  const outset=p===1?2:2*smooth((p-.9)/.1);
  const apertureWidth=diameter+(w-diameter)*expand+outset*2;
  const apertureHeight=diameter+(h-diameter)*expand+outset*2;
  const centerX=w*.5, centerY=h*(.59-.09*smooth(p/.3));
  const radius=(diameter*.5)*(1-smooth((p-.38)/.62));
  const top=centerY-apertureHeight*.5;
  const left=centerX-apertureWidth*.5;
  const bottom=h-centerY-apertureHeight*.5;
  const right=w-centerX-apertureWidth*.5;
  const clipPath=`inset(${top}px ${right}px ${bottom}px ${left}px round ${radius}px)`;
  return Object.freeze({progress:p,centerX,centerY,width:apertureWidth,height:apertureHeight,radius,outset,
    top,right,bottom,left,clipPath,uiOpacity:smooth((p-.82)/.18),finished:p===1});
}
