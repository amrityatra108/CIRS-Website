// A short editorial interlude after the original light orb. All motion is
// transform/opacity driven; one CSS timeline owns the entire reveal.
export function createIntroOverlay({root,onComplete=()=>{}}){
  const element=root.querySelector('#cirs-intro');
  const photo=element.querySelector('img');
  let playing=false;
  let disposed=false;
  let generation=0;
  // Start decoding with the already-loaded landing module, ahead of the
  // photograph's entrance beat. An image error leaves the word story usable.
  if(photo.decode)photo.decode().catch(()=>{photo.closest('.cirs-intro__photo-wrap').hidden=true;});

  function reset(){
    generation++;
    playing=false;
    element.classList.remove('is-playing');
    element.hidden=true;
    root.classList.remove('intro-active');
  }
  function play(){
    if(disposed||playing||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    generation++;
    playing=true;
    element.hidden=false;
    root.classList.add('intro-active');
    // Replaying from a visible end-state requires one style flush at the
    // interaction boundary, never during an animation frame.
    void element.offsetWidth;
    element.classList.add('is-playing');
  }
  function onAnimationEnd(event){
    if(event.target!==element||event.animationName!=='cirs-intro-out'||!playing)return;
    reset();
    onComplete();
  }
  element.addEventListener('animationend',onAnimationEnd);
  return {
    play,reset,
    inspect:()=>({playing,hidden:element.hidden,generation}),
    dispose(){disposed=true;reset();element.removeEventListener('animationend',onAnimationEnd);}
  };
}
