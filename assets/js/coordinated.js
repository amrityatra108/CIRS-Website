/* Independent progressive enhancements. Never creates Lenis or a second library owner. */
(() => {
 'use strict';
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'), wide=matchMedia('(min-width:1000px) and (min-height:680px)');
 const controller=new AbortController(),{signal}=controller;let cleanups=[];
 function configure(){cleanups.forEach(f=>f());cleanups=[];
  const math=document.querySelector('[data-rd-math]');
  if(math){const buttons=[...math.querySelectorAll('[data-math-stage]')],display=math.querySelector('[data-math-display]'),scan=math.querySelector('.rd-math__scan'),reasons=[...document.querySelectorAll('[data-math-reason]')];let run=null,frame=0,current=-1;
   const texts=['Find two pairs of positive integers.','Construct cubes of sides 1, 12, 9 and 10.','1 + 1728 = 1729. 729 + 1000 = 1729.','Two different pairs. The same verified sum.'];
   const set=i=>{if(i===current)return;current=i;math.dataset.step=i;buttons.forEach((b,k)=>b.setAttribute('aria-pressed',String(k===i)));display.textContent=texts[i];run?.cancel();scan.style.display='none';if(i===1&&!reduced.matches){scan.style.display='block';run=scan.animate([{top:'0%',opacity:1},{top:'100%',opacity:1},{top:'100%',opacity:0}],{duration:900,easing:'linear'});run.onfinish=()=>{scan.style.display='none';};}};
   const click=e=>{const b=e.target.closest('[data-math-stage]');if(b)set(Number(b.dataset.mathStage));};math.addEventListener('click',click,{signal});
   if(!reduced.matches){document.documentElement.classList.add('rd-math-live');set(0);const update=()=>{frame=0;let i=0;reasons.forEach((r,k)=>{if(r.getBoundingClientRect().top<innerHeight*.55)i=k});set(i)};const queue=()=>{if(!frame)frame=requestAnimationFrame(update)};addEventListener('scroll',queue,{passive:true,signal});cleanups.push(()=>{removeEventListener('scroll',queue);cancelAnimationFrame(frame);});}else set(3);
   cleanups.push(()=>{math.removeEventListener('click',click);run?.cancel();scan.style.display='none';document.documentElement.classList.remove('rd-math-live');});
  }
  const magazine=document.querySelector('.rd-magazine');
  if(magazine&&!reduced.matches&&wide.matches&&window.gsap&&window.ScrollTrigger){
   document.documentElement.classList.add('rd-magazine-on');
   const context=gsap.context(()=>{
    const timeline=gsap.timeline({scrollTrigger:{trigger:magazine,start:'top 90px',end:'bottom bottom',scrub:true}});
    timeline.fromTo('.rd-magazine__cover',{rotation:-7,xPercent:35},{rotation:0,xPercent:0,ease:'none'},0)
     .fromTo('.rd-magazine__inside',{rotation:7,xPercent:-30,clipPath:'inset(0 0 100% 0)'},{rotation:0,xPercent:0,clipPath:'inset(0 0 0% 0)',ease:'none'},0);
   },magazine);cleanups.push(()=>{context.revert();document.documentElement.classList.remove('rd-magazine-on');});
  }
  document.querySelectorAll('[data-rd-chapters]').forEach(section=>{
   const links=[...section.querySelectorAll('nav a[href^="#"]')],panels=links.map(a=>document.querySelector(a.getAttribute('href')));let frame=0;
   const update=()=>{frame=0;let active=0;panels.forEach((p,i)=>{if(p&&p.getBoundingClientRect().top<innerHeight*.5)active=i;});links.forEach((a,i)=>{if(i===active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});};
   const queue=()=>{if(!frame)frame=requestAnimationFrame(update);};addEventListener('scroll',queue,{passive:true,signal});addEventListener('resize',queue,{signal});update();
   cleanups.push(()=>{removeEventListener('scroll',queue);removeEventListener('resize',queue);cancelAnimationFrame(frame);});
   if((section.classList.contains('rd-academic')||section.classList.contains('rd-laurels'))&&!reduced.matches&&wide.matches){
    const runs=new Set(),observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(!entry.isIntersecting)return;const image=entry.target.querySelector('img');if(!image||!image.animate)return;const run=image.animate([{clipPath:'inset(0 0 100% 0)',transform:section.classList.contains('rd-laurels')?'none':'rotate(1deg) scale(.98)'},{clipPath:'inset(0 0 0% 0)',transform:'none'}],{duration:650,easing:'cubic-bezier(.2,.7,.2,1)'});runs.add(run);run.onfinish=()=>runs.delete(run);});},{threshold:.15});
    panels.filter(Boolean).forEach(p=>observer.observe(p));cleanups.push(()=>{observer.disconnect();runs.forEach(r=>r.cancel());});
   }
  });
  const coin=document.querySelector('.rd-coin');
  if(coin&&!reduced.matches&&wide.matches&&window.gsap&&window.ScrollTrigger){
   const tween=gsap.to(coin,{xPercent:28,yPercent:20,rotationY:-38,rotation:8,scale:.65,ease:'none',scrollTrigger:{trigger:'.hj-hero',start:'top top',end:'bottom top',scrub:true}});
   cleanups.push(()=>{tween.scrollTrigger.kill();tween.kill();coin.removeAttribute('style');});
  }
 }
 reduced.addEventListener('change',configure,{signal});wide.addEventListener('change',configure,{signal});
 function boot(){configure();}
 if(document.readyState!=='complete')document.addEventListener('DOMContentLoaded',boot,{once:true,signal});else boot();
 addEventListener('pagehide',e=>{if(!e.persisted){cleanups.forEach(f=>f());controller.abort();}},{signal});
})();
