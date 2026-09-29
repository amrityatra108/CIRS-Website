/* Independent finite-camera implementation informed by CurveGallery's
   tutorial; no reference-repository code or imagery is incorporated.
   Three.js is the site's existing locally hosted MIT library. */
import * as THREE from '../founder-opening/vendor/three.module.min.js';

export function createWorld(canvas, stations, onDirty) {
  let renderer;
  try { renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:false, powerPreference:'default'}); }
  catch { return null; }
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0x180f23, 1);
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x180f23, 18, 52);
  const camera = new THREE.PerspectiveCamera(40, 1, .1, 100);
  camera.up.set(0,1,0);
  const points = stations.map((_,i)=>new THREE.Vector3(1.4*Math.sin(i*.74), -.55*i + .22*Math.sin(i*.9), -12*i));
  // Open curve: gentle descending partial spiral, no loop or roll.
  const curve = new THREE.CatmullRomCurve3(points, false, 'catmullrom', .18);
  const loader = new THREE.TextureLoader(), planes = [],textures=new Map();
  let dead=false, width=0, height=0;
  const position = new THREE.Vector3(), ahead = new THREE.Vector3(),focus = new THREE.Vector3();
  stations.forEach((station,index)=>{
    (station.images || []).forEach((image,layer)=>{
      const geometry = new THREE.PlaneGeometry(1,1);
      const material = new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0,side:THREE.DoubleSide,depthWrite:true});
      const mesh = new THREE.Mesh(geometry,material);
      mesh.userData={index,layer,ratio:image.ratio,src:image.src,loaded:false,loading:false};
      mesh.rotation.y = layer ? -.06 : .015;
      scene.add(mesh); planes.push(mesh);
    });
  });
  function requestImages(active){
    planes.filter(p=>Math.abs(p.userData.index-active)<=1).forEach(mesh=>{
      const d=mesh.userData;
      if(d.loaded || d.loading || d.failed)return;
      d.loading=true;
      const assign=texture=>{mesh.material.map=texture;mesh.material.needsUpdate=true;d.loaded=true;};
      const existing=textures.get(d.src);
      if(existing){
        if(existing.texture)assign(existing.texture);
        else if(existing.failed)d.failed=true;
        else existing.waiting.push({assign,data:d});
        return;
      }
      const entry={texture:null,failed:false,waiting:[{assign,data:d}]};textures.set(d.src,entry);
      loader.load(d.src,texture=>{
        if(dead){texture.dispose();return;}
        texture.colorSpace=THREE.SRGBColorSpace;
        texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
        entry.texture=texture;entry.waiting.forEach(request=>request.assign(texture));entry.waiting=[];onDirty();
      },undefined,()=>{entry.failed=true;entry.waiting.forEach(request=>request.data.failed=true);entry.waiting=[];onDirty();});
    });
  }
  function resize(){
    width=canvas.clientWidth;height=canvas.clientHeight;
    if(!width || !height)return;
    renderer.setSize(width,height,false);
    camera.aspect=width/height;camera.updateProjectionMatrix();
    const viewHeight=2*8*Math.tan(THREE.MathUtils.degToRad(camera.fov/2)),viewWidth=viewHeight*camera.aspect;
    planes.forEach(mesh=>{
      const d=mesh.userData,point=points[d.index];
      const h=Math.min(viewHeight*.69,(viewWidth*.58)/d.ratio);
      mesh.scale.set(h*d.ratio,h,1);
      mesh.position.set(point.x+viewWidth*.21+d.layer*1.3,point.y+d.layer*.22,point.z-8-d.layer*2.5);
    });
  }
  function render(progress){
    if(dead || !width)return;
    const max=stations.length-1,k=Math.max(0,Math.min(max,progress)),t=k/max;
    curve.getPoint(t,position);curve.getPoint(Math.min(1,t+.025),ahead);
    camera.position.copy(position);
    // Smooth look-ahead and a fixed up vector keep the reader upright.
    focus.copy(position);focus.z-=12;
    if(t<.98){focus.x+=(ahead.x-position.x)*.14;focus.y+=(ahead.y-position.y)*.1;}
    camera.lookAt(focus);requestImages(Math.round(k));
    planes.forEach(mesh=>{
      const d=mesh.userData,delta=d.index-k;
      mesh.visible=d.loaded && delta>-.42 && delta<3.8;
      // Perspective supplies approach growth. Retire the plane beside the
      // camera before crossing it, so it never flies through the reader.
      mesh.material.opacity=mesh.visible ? Math.min(1,Math.max(0,(delta+.42)/.32))*(d.layer ? .65:1) : 0;
    });
    renderer.render(scene,camera);
  }
  const photoReady=index=>planes.some(p=>p.userData.index===index && p.userData.layer===0 && p.userData.loaded);
  const photoFailed=index=>planes.some(p=>p.userData.index===index && p.userData.layer===0 && p.userData.failed);
  function dispose(){
    dead=true;planes.forEach(p=>{p.geometry.dispose();p.material.dispose();});
    textures.forEach(entry=>entry.texture?.dispose());textures.clear();
    renderer.dispose();renderer.forceContextLoss();
  }
  resize();return {render,resize,dispose,photoReady,photoFailed};
}
