// Lettering on the outermost stone terrace. Two curved strips follow its
// visible flanks, so the words lie flat on the base floor around the plinth.
export function createFloorInvocation({THREE,scene}){
  const strips=[];
  const centreZ=-.6;
  const terraceTop=-2.24;
  const phrases=[
    {text:'Om Shri Chinmaya',wide:[-1.55,-2.45],narrow:[-2.82,-3.07],name:'outer-floor-invocation-left'},
    {text:'Sadgurave Namah',wide:[2.45,1.55],narrow:[3.07,2.82],name:'outer-floor-invocation-right'}
  ];
  function makeGeometry(start,end){
    // The middle tier ends at radius 4.85. Both edges of the decal sit
    // safely in the outer annulus (5.04–5.88), just above its -2.24 top.
    const segments=80;
    const positions=[];const uvs=[];const indices=[];
    for(let i=0;i<=segments;i++){
      const u=i/segments;
      const angle=start+(end-start)*u;
      for(let edge=0;edge<2;edge++){
        const radius=edge?5.88:5.04;
        positions.push(Math.sin(angle)*radius,terraceTop+.016,centreZ+Math.cos(angle)*radius);
        uvs.push(u,edge);
      }
      if(i<segments){
        const n=i*2;
        indices.push(n,n+2,n+1,n+1,n+2,n+3);
      }
    }
    const geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
    geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    return geometry;
  }
  for(const phrase of phrases){
    const canvas=document.createElement('canvas');
    canvas.width=1536;canvas.height=256;
    const context=canvas.getContext('2d');
    const texture=new THREE.CanvasTexture(canvas);
    texture.colorSpace=THREE.SRGBColorSpace;
    texture.anisotropy=8;
    function draw(){
      context.clearRect(0,0,canvas.width,canvas.height);
      context.fillStyle='rgba(117,77,49,.97)';
      context.textAlign='center';
      context.textBaseline='middle';
      context.font='500 190px Newsreader, Georgia, serif';
      const naturalWidth=context.measureText(phrase.text).width;
      context.save();
      context.translate(canvas.width/2,canvas.height/2+5);
      context.scale(Math.min(1,canvas.width*.90/naturalWidth),1);
      context.fillText(phrase.text,0,0);
      context.restore();
      texture.needsUpdate=true;
    }
    draw();
    document.fonts?.load('500 190px Newsreader').then(draw).catch(()=>{});

    const geometry=makeGeometry(...phrase.wide);
    const material=new THREE.MeshBasicMaterial({map:texture,transparent:true,opacity:0,depthWrite:false,side:THREE.DoubleSide,toneMapped:false});
    const mesh=new THREE.Mesh(geometry,material);
    mesh.name=phrase.name;
    mesh.renderOrder=3;
    scene.add(mesh);
    strips.push({mesh,geometry,material,texture,phrase});
  }
  let narrow=false;
  return {
    update(seconds,aspect){
      const nextNarrow=aspect<.85;
      if(nextNarrow!==narrow){
        narrow=nextNarrow;
        for(const strip of strips){
          const replacement=makeGeometry(...strip.phrase[narrow?'narrow':'wide']);
          strip.mesh.geometry=replacement;
          strip.geometry.dispose();
          strip.geometry=replacement;
        }
      }
      const opacity=Math.max(0,Math.min(.96,(seconds-5.55)/.82*.96));
      for(const strip of strips)strip.material.opacity=opacity;
    },
    dispose(){
      for(const strip of strips){
        scene.remove(strip.mesh);
        strip.geometry.dispose();strip.material.dispose();strip.texture.dispose();
      }
    }
  };
}
