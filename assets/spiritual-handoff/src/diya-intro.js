import { createDiyaFlame } from './diya-flame.js?v=fac0627088';
import { INTRO } from './intro-particles.js?v=0606b9b064';

// The render geometry is derived from the supplied FBX; no proxy bowl is used.
export async function createDiyaIntro({ THREE, scene }) {
  const [metaResponse,dataResponse]=await Promise.all([
    fetch(new URL('../assets/diya-metadata.json',import.meta.url)),
    fetch(new URL('../assets/diya-mesh.bin',import.meta.url))
  ]);
  if(!metaResponse.ok||!dataResponse.ok)throw new Error('The diya could not load.');
  const [metadata,data]=await Promise.all([metaResponse.json(),dataResponse.arrayBuffer()]);
  const group=new THREE.Group();group.name='original-diya-entrance';
  group.position.set(0,-1.802,-.60);group.rotation.y=-.18;scene.add(group);
  const dissolve={value:0}, geometries=[], materials=[];
  const meshes=[];
  function makeMaterial(name){
    const values=name==='oil'?{color:0x60401c,metalness:.04,roughness:.16,clearcoat:.8,clearcoatRoughness:.2}:
      name==='wick'?{color:0xcdbb86,metalness:0,roughness:.94}:
      {color:0x9a5d32,metalness:.50,roughness:.36};
    const mat=new THREE.MeshPhysicalMaterial(values);
    mat.onBeforeCompile=shader=>{
      shader.uniforms.uDissolve=dissolve;
      shader.vertexShader='varying vec3 vDiyaPosition;\n'+shader.vertexShader;
      shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvDiyaPosition=position;');
      shader.fragmentShader=`uniform float uDissolve;varying vec3 vDiyaPosition;
      float dh(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
      float dn(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
      return mix(mix(mix(dh(i),dh(i+vec3(1,0,0)),f.x),mix(dh(i+vec3(0,1,0)),dh(i+vec3(1,1,0)),f.x),f.y),mix(mix(dh(i+vec3(0,0,1)),dh(i+vec3(1,0,1)),f.x),mix(dh(i+vec3(0,1,1)),dh(i+vec3(1,1,1)),f.x),f.y),f.z);}
      `+shader.fragmentShader;
      shader.fragmentShader=shader.fragmentShader.replace('#include <alphatest_fragment>',`#include <alphatest_fragment>
        float field=dn(vDiyaPosition*17.)*.68+dn(vDiyaPosition*41.)*.32;
        float cut=uDissolve*1.24-.12;
        if(field<cut)discard;
        float edge=(1.-smoothstep(cut,cut+.12,field))*step(.001,uDissolve);
        diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.95,.47,.11),edge*.85);
      `);
    };
    materials.push(mat);return mat;
  }
  for(const part of metadata.parts){
    const geometry=new THREE.BufferGeometry();
    for(const name of ['position','normal']){
      const a=part.attributes[name];
      geometry.setAttribute(name,new THREE.BufferAttribute(new Float32Array(data,a.byteOffset,a.count*a.components),a.components));
    }
    const a=part.attributes.index;
    geometry.setIndex(new THREE.BufferAttribute(new Uint32Array(data,a.byteOffset,a.count),1));
    geometry.computeBoundingSphere();geometries.push(geometry);
    const mesh=new THREE.Mesh(geometry,makeMaterial(part.name));mesh.name='supplied-diya-'+part.name;
    group.add(mesh);meshes.push(mesh);
  }
  const wick=new THREE.Vector3(...metadata.flame.anchor);
  const fire=createDiyaFlame({THREE,group,anchor:wick,height:metadata.flame.suggestedHeight||.72});
  group.updateMatrixWorld(true);
  const flameCenter=fire.anchor.clone().applyMatrix4(group.matrixWorld);
  const source=fire.anchor.clone().add(new THREE.Vector3(0,.17,0)).applyMatrix4(group.matrixWorld);

  // A few fragments leave the actual vessel's surface as it dematerializes.
  const body=meshes.find(mesh=>mesh.name==='supplied-diya-body').geometry.attributes.position;
  const count=4800,points=new Float32Array(count*3),seeds=new Float32Array(count);
  for(let i=0;i<count;i++){
    const n=(i*7919)%body.count;
    points.set([body.getX(n),body.getY(n),body.getZ(n)],i*3);
    seeds[i]=Math.abs(Math.sin(i*76.13)*43758.5453)%1;
  }
  const dustGeometry=new THREE.BufferGeometry();
  dustGeometry.setAttribute('position',new THREE.BufferAttribute(points,3));
  dustGeometry.setAttribute('aSeed',new THREE.BufferAttribute(seeds,1));
  const dustMaterial=new THREE.ShaderMaterial({
    transparent:true,depthWrite:false,uniforms:{uDissolve:dissolve},
    vertexShader:`attribute float aSeed;uniform float uDissolve;varying float vAlpha;
    void main(){float d=uDissolve;float g=smoothstep(aSeed*.3,.7+aSeed*.3,d);vec3 p=position;
    float a=d*8.5+aSeed*6.283;vec3 swirl=vec3(cos(a)*(.3+aSeed),2.3+aSeed*1.2,sin(a)*.5);
    p=mix(p,swirl,g);vec4 view=modelViewMatrix*vec4(p,1.);gl_Position=projectionMatrix*view;
    gl_PointSize=clamp((1.+aSeed)*9./max(.1,-view.z),1.,4.);
    vAlpha=sin(clamp(d,0.,1.)*3.14159)*(.3+aSeed*.6);}`,
    fragmentShader:`varying float vAlpha;void main(){float d=length(gl_PointCoord-.5)*2.;if(d>1.)discard;gl_FragColor=vec4(.74,.39,.13,(1.-d)*vAlpha);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}`
  });
  const fragments=new THREE.Points(dustGeometry,dustMaterial);fragments.frustumCulled=false;group.add(fragments);
  let time=0,progress=0,disposed=false;
  return {
    flameCenter,source,
    update({time:now,introSeconds,reduced=false}){
      if(disposed)return;time=now;
      progress=reduced?1:THREE.MathUtils.smoothstep(introSeconds,INTRO.formationStart,INTRO.diyaGone);
      dissolve.value=progress;group.visible=!reduced&&introSeconds<INTRO.diyaGone;
      fire.update({time:now,opacity:1-THREE.MathUtils.smoothstep(progress,.10,.83)});
      fragments.visible=progress>0&&progress<1;
    },
    inspect:()=>({visible:group.visible,dissolve:progress,time,flame:fire.inspect(),flameCenter:flameCenter.toArray(),source:source.toArray(),triangles:metadata.parts.reduce((n,p)=>n+p.triangles,0),originalModel:true}),
    dispose(){if(disposed)return;disposed=true;fire.dispose();group.removeFromParent();geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());dustGeometry.dispose();dustMaterial.dispose();}
  };
}
