// Explicit developer controls only. No capture/readback or polling is installed
// for ordinary visitors. Exports are composed from the actual plate + WebGL frame.
export function installSanctuaryReview({ root, renderer, scene, camera, inspect, refresh }) {
  if(!new URLSearchParams(location.search).has('sanctuaryDebug'))return ()=>{};
  const panel=document.createElement('aside');panel.className='sanctuary-review';panel.setAttribute('aria-label','Sanctuary review');
  panel.innerHTML='<button type="button" data-save>Save landing frame</button><button type="button" data-report>Save landing report</button><output></output><pre id="sanctuary-runtime-report" hidden></pre>';
  document.body.append(panel);
  const report=panel.querySelector('pre'),output=panel.querySelector('output');
  function update(){const state=inspect();report.textContent=JSON.stringify(state,null,2);output.textContent=`${state.width} × ${state.height} · ${state.affected} contacted · ${state.solidLogo?.liquidEnergy?.toFixed(3)||0} energy`;}
  const timer=setInterval(update,350);update();
  window.__sanctuaryCapture=()=>{refresh();renderer.render(scene,camera);return {canvas:renderer.domElement,state:inspect()};};
  function download(blob,name){const link=document.createElement('a'),url=URL.createObjectURL(blob);link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  panel.querySelector('[data-report]').onclick=()=>download(new Blob([report.textContent],{type:'application/json'}),'sanctuary-runtime.json');
  panel.querySelector('[data-save]').onclick=async()=>{
    await document.fonts.ready;refresh();renderer.render(scene,camera);
    const state=inspect(),w=state.width,h=state.height,l=state.chamber.layout;
    const capture=document.createElement('canvas');capture.width=w;capture.height=h;
    const ctx=capture.getContext('2d'),img=root.querySelector('.sanctuary-plate img');
    ctx.drawImage(img,l.left,l.top,l.imageWidth,l.imageHeight);
    const shadow=l.shadow,g=ctx.createRadialGradient(shadow.x,shadow.y,0,shadow.x,shadow.y,shadow.width*.5);
    ctx.save();ctx.translate(shadow.x,shadow.y);ctx.scale(1,shadow.height/shadow.width);ctx.translate(-shadow.x,-shadow.y);g.addColorStop(0,'#51473730');g.addColorStop(1,'#51473700');ctx.fillStyle=g;ctx.fillRect(shadow.x-shadow.width,shadow.y-shadow.width,shadow.width*2,shadow.width*2);ctx.restore();
    ctx.drawImage(renderer.domElement,0,0,w,h);
    const base=root.getBoundingClientRect();
    function text(el, value, yOffset=0){const r=el.getBoundingClientRect(),s=getComputedStyle(el);ctx.font=`${s.fontWeight} ${s.fontSize} ${s.fontFamily}`;ctx.fillStyle=s.color;ctx.textAlign='left';ctx.textBaseline='middle';ctx.fillText(value,r.left-base.left,r.top-base.top+r.height/2+yOffset);}
    text(root.querySelector('.wordmark'),'GURUDEV');text(root.querySelector('.masthead h1'),'•  Spiritual');
    const plaque=root.querySelector('.invocation'),ps=getComputedStyle(plaque);ctx.font=`${ps.fontWeight} ${ps.fontSize} ${ps.fontFamily}`;ctx.fillStyle=ps.color;ctx.textAlign='center';ctx.textBaseline='middle';
    const words=plaque.textContent.split(' '),lines=[];let line='';
    for(const word of words){const next=line?line+' '+word:word;if(line&&ctx.measureText(next).width>l.plaque.width-6){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);
    lines.forEach((line,i)=>ctx.fillText(line,l.plaque.x,l.plaque.y+(i-(lines.length-1)/2)*parseFloat(ps.fontSize)*1.1));
    for(const button of root.querySelectorAll('.actions button'))text(button,button.textContent.replace(/\s+/g,' ').trim());
    const hint=root.querySelector('.hint');if(parseFloat(getComputedStyle(hint).opacity)>.1)text(hint,hint.textContent);
    capture.toBlob(blob=>download(blob,`Gurudev-marble-${w}x${h}.png`),'image/png');
  };
  return()=>{clearInterval(timer);panel.remove();delete window.__sanctuaryCapture;};
}
