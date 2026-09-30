import { sampleCloudAlpha } from './tapovan-terrain.js';

// Reuse the actual presented mountain-video frame as the foreground cloud.
// This gives the stones a soft, video-matched cover at the cloud boundary.
export function createTapovanCloudCover({ video, stage, cloud }) {
  const canvas=stage.querySelector('#tapovan-cloud-cover');
  const context=canvas.getContext('2d',{alpha:true});
  const mask=document.createElement('canvas');
  const maskContext=mask.getContext('2d',{alpha:true});
  let width=0,height=0;
  function resize() {
    const ratio=Math.min(devicePixelRatio||1,1.25);
    const nextWidth=Math.max(1,Math.round(stage.clientWidth*ratio));
    const nextHeight=Math.max(1,Math.round(stage.clientHeight*ratio));
    if(nextWidth===width&&nextHeight===height)return;
    width=canvas.width=nextWidth;
    height=canvas.height=nextHeight;
    mask.width=Math.max(128,Math.min(512,Math.round(width/2)));
    mask.height=Math.max(72,Math.round(mask.width*height/width));
  }
  function update(time,mapping) {
    if(video.readyState<2)return;
    resize();
    const mw=mask.width,mh=mask.height;
    const pixels=maskContext.createImageData(mw,mh),data=pixels.data;
    let visible=false;
    for(let y=0;y<mh;y++) {
      for(let x=0;x<mw;x++) {
        const [sx,sy]=mapping.viewportToSource((x+.5)/mw,(y+.5)/mh);
        const alpha=sampleCloudAlpha(cloud,time,sx,sy);
        const i=(y*mw+x)*4;
        data[i]=data[i+1]=data[i+2]=255;
        data[i+3]=Math.round(alpha*255);
        if(alpha>.001)visible=true;
      }
    }
    context.clearRect(0,0,width,height);
    if(!visible)return;
    maskContext.putImageData(pixels,0,0);
    const scale=width/Math.max(1,stage.clientWidth);
    context.filter='saturate(.92) contrast(1.035) brightness(.82)';
    context.drawImage(video,-mapping.cropX*scale,-mapping.cropY*scale,
      mapping.drawnWidth*scale,mapping.drawnHeight*scale);
    context.filter='none';
    context.globalCompositeOperation='destination-in';
    context.drawImage(mask,0,0,width,height);
    context.globalCompositeOperation='source-over';
  }
  return {update,resize,dispose(){context.clearRect(0,0,width,height);}};
}
