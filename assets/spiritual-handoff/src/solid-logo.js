// The supplied GLB perimeter remains authoritative. The live mesh is
// retriangulated from that exact outline; only its finish changes to pale marble.
// Interaction timing and dispersal remain independent from the finish.
export const SOLID_LOGO_SETTINGS = Object.freeze({
  revealStart: 6.15, revealEnd: 6.4,
  maskWidth: 128, maskHeight: 208,
  displacementStart: .012, displacementFull: .105,
  attackSeconds: .035, releaseSeconds: .11,
  liquidAttackSeconds: .055, liquidReleaseSeconds: .13,
  liquidMaximum: .95
});

function createEdgeDistance(THREE,data,bounds,width=512,height=832){
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
  const context=canvas.getContext('2d',{willReadFrequently:true});
  const maxY=bounds.y+bounds.w;
  context.setTransform(width/bounds.z,0,0,-height/bounds.w,-bounds.x*width/bounds.z,maxY*height/bounds.w);
  for(const shape of data.shapes){
    context.beginPath();
    for(const loop of [shape.outline,...shape.holes]){
      loop.forEach(([x,y],i)=>i?context.lineTo(x,y):context.moveTo(x,y));
      context.closePath();
    }
    context.fill('evenodd');
  }
  const alpha=context.getImageData(0,0,width,height).data;
  // Exact separable Euclidean distance avoids chamfer-grid ridges in specular light.
  const distance=new Float32Array(width*height), far=1e12;
  const intermediate=new Float64Array(width*height);
  const count=Math.max(width,height), f=new Float64Array(count), d=new Float64Array(count);
  const sites=new Int32Array(count), boundaries=new Float64Array(count+1);
  function edt(n){
    let k=0;sites[0]=0;boundaries[0]=-Infinity;boundaries[1]=Infinity;
    for(let q=1;q<n;q++){
      let intersect=((f[q]+q*q)-(f[sites[k]]+sites[k]*sites[k]))/(2*(q-sites[k]));
      while(intersect<=boundaries[k]){k--;intersect=((f[q]+q*q)-(f[sites[k]]+sites[k]*sites[k]))/(2*(q-sites[k]));}
      k++;sites[k]=q;boundaries[k]=intersect;boundaries[k+1]=Infinity;
    }
    k=0;for(let q=0;q<n;q++){while(boundaries[k+1]<q)k++;const delta=q-sites[k];d[q]=delta*delta+f[sites[k]];}
  }
  for(let y=0;y<height;y++){
    for(let x=0;x<width;x++)f[x]=alpha[(y*width+x)*4+3]>128?far:0;
    edt(width);for(let x=0;x<width;x++)intermediate[y*width+x]=d[x];
  }
  for(let x=0;x<width;x++){
    for(let y=0;y<height;y++)f[y]=intermediate[y*width+x];
    edt(height);for(let y=0;y<height;y++)distance[y*width+x]=Math.sqrt(d[y]);
  }
  // Prepare the relief direction from the float distance field. Taking
  // derivatives of an 8-bit distance in the shader creates stair bands on
  // shallow curved shoulders, so smooth and differentiate once here instead.
  const horizontalDistance=new Float32Array(width*height);
  const smoothDistance=new Float32Array(width*height);
  const weights=[1,8,28,56,70,56,28,8,1];
  for(let y=0;y<height;y++)for(let x=0;x<width;x++){
    let sum=0;
    for(let k=-4;k<=4;k++)sum+=distance[y*width+Math.max(0,Math.min(width-1,x+k))]*weights[k+4];
    horizontalDistance[y*width+x]=sum/256;
  }
  for(let y=0;y<height;y++)for(let x=0;x<width;x++){
    let sum=0;
    for(let k=-4;k<=4;k++)sum+=horizontalDistance[Math.max(0,Math.min(height-1,y+k))*width+x]*weights[k+4];
    smoothDistance[y*width+x]=sum/256;
  }
  const output=new Uint16Array(width*height*4);
  const half=THREE.DataUtils.toHalfFloat;
  for(let y=0;y<height;y++)for(let x=0;x<width;x++){
    const i=y*width+x;
    const gx=(smoothDistance[y*width+Math.min(width-1,x+1)]-smoothDistance[y*width+Math.max(0,x-1)])*.5;
    const gy=(smoothDistance[Math.max(0,y-1)*width+x]-smoothDistance[Math.min(height-1,y+1)*width+x])*.5;
    const length=Math.max(1,Math.hypot(gx,gy));
    const destination=((height-1-y)*width+x)*4;
    output[destination]=half(gx/length*.5+.5);
    output[destination+1]=half(gy/length*.5+.5);
    output[destination+2]=half(Math.min(smoothDistance[i],30)/30);
    output[destination+3]=half(1);
  }
  const texture=new THREE.DataTexture(output,width,height,THREE.RGBAFormat,THREE.HalfFloatType);
  texture.colorSpace=THREE.NoColorSpace;
  texture.minFilter=THREE.LinearFilter;texture.magFilter=THREE.LinearFilter;
  texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;texture.generateMipmaps=false;
  texture.needsUpdate=true;
  return texture;
}

export async function createSolidLogo({ THREE, parent }) {
  const [response, finishResponse, veinTexture] = await Promise.all([
    fetch(new URL('../assets/logo-solid-outline.json', import.meta.url)),
    fetch(new URL('../assets/logo-polished-finish.json', import.meta.url)),
    new THREE.TextureLoader().loadAsync(new URL('../assets/marble-sanctuary/reference-veins-data.png?v=reference-3', import.meta.url).href)
  ]);
  if (!response.ok || !finishResponse.ok) throw new Error('Could not load the polished Chinmaya logo.');
  const [data, finish] = await Promise.all([response.json(), finishResponse.json()]);
  // Pigment coverage is data, not a colour photograph. It is decoded once and
  // remains attached to the undeformed, authoritative emblem coordinates.
  veinTexture.colorSpace=THREE.NoColorSpace;
  veinTexture.minFilter=THREE.LinearMipmapLinearFilter;veinTexture.magFilter=THREE.LinearFilter;
  veinTexture.wrapS=veinTexture.wrapT=THREE.ClampToEdgeWrapping;
  const shapes = data.shapes.map(item => {
    const shape = new THREE.Shape(item.outline.map(([x,y]) => new THREE.Vector2(x,y)));
    item.holes.forEach(loop => shape.holes.push(new THREE.Path(loop.map(([x,y]) => new THREE.Vector2(x,y)))));
    return shape;
  });
  const geometry = new THREE.ExtrudeGeometry(shapes, {
    depth: data.zMax-data.zMin, bevelEnabled: false,
    steps: 1, curveSegments: 1, material: 0, extrudeMaterial: 1
  });
  geometry.translate(0,0,data.zMin);
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();

  const settings = SOLID_LOGO_SETTINGS;
  const width = settings.maskWidth, height = settings.maskHeight, pixels = width*height;
  const bytes = new Uint8Array(pixels), target = new Float32Array(pixels);
  const horizontal = new Float32Array(pixels), dilated = new Float32Array(pixels);
  const blurred = new Float32Array(pixels), smoothed = new Float32Array(pixels);
  const texture = new THREE.DataTexture(bytes,width,height,THREE.RedFormat,THREE.UnsignedByteType);
  texture.minFilter=THREE.LinearFilter;texture.magFilter=THREE.LinearFilter;
  texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;
  texture.generateMipmaps=false;texture.needsUpdate=true;
  const minX=data.bounds.min[0]-.06,minY=data.bounds.min[1]-.06;
  const extentX=data.bounds.size[0]+.12,extentY=data.bounds.size[1]+.12;
  const logoBounds=new THREE.Vector4(minX,minY,extentX,extentY);
  const edgeDistance=createEdgeDistance(THREE,data,logoBounds);
  const uniforms={
    uSolidMask:{value:texture},uSolidReveal:{value:0},
    uSolidBounds:{value:logoBounds},uEdgeDistance:{value:edgeDistance},
    uMarbleVeins:{value:veinTexture},
    uMarbleBounds:{value:new THREE.Vector4(data.bounds.min[0],data.bounds.min[1],data.bounds.size[0],data.bounds.size[1])}
  };
  const MARBLE = [
    { name:'Reference ivory marble face', color:'#E8E6DE', roughness:.17, clearcoat:.58 },
    { name:'Reference ivory marble edge', color:'#E4E1D8', roughness:.20, clearcoat:.52 }
  ];
  const materials = MARBLE.map((source,index)=>{
    const surface=new THREE.MeshPhysicalMaterial({
      color:source.color, metalness:0, roughness:source.roughness,
      clearcoat:source.clearcoat,clearcoatRoughness:.25,
      opacity:1,dithering:true,transparent:true,depthWrite:false,
      side:THREE.FrontSide,alphaTest:.025
    });
    surface.name=source.name;
    surface.customProgramCacheKey=()=>`chinmaya-reference-marble-v2-${index}`;
    return surface;
  });
  const material=materials[0];
  uniforms.uLiquidPoint={value:new THREE.Vector2(0,0)};
  uniforms.uLiquidEnergy={value:0};
  uniforms.uLiquidTime={value:0};
  // All deformation consumers use this local field. Time affects only the
  // touched region; the marble's material coordinates never slide over it.
  const deformation=`
    uniform vec2 uLiquidPoint;
    uniform float uLiquidEnergy;
    uniform float uLiquidTime;
    float liquidField(vec2 point){
      vec2 d=point-uLiquidPoint;
      return exp(-dot(d,d)*10.)*uLiquidEnergy;
    }
    vec3 liquidDisplacement(vec3 point){
      vec2 d=point.xy-uLiquidPoint;
      float field=liquidField(point.xy);
      vec2 flow=vec2(
        sin(d.y*13.-uLiquidTime*8.)+sin(d.x*20.+uLiquidTime*5.)*.35,
        cos(d.x*12.+uLiquidTime*6.)-sin(d.y*18.-uLiquidTime*7.)*.35
      );
      return vec3(flow*field*.065,sin(length(d)*22.-uLiquidTime*9.)*field*.028);
    }
    vec3 liquidPosition(vec3 point){return point+liquidDisplacement(point);}
  `;
  for (const surface of materials) surface.onBeforeCompile=shader=>{
    Object.assign(shader.uniforms,uniforms);
    shader.vertexShader=shader.vertexShader.replace('#include <common>',`
      #include <common>
      ${deformation}
      varying vec3 vSolidLocal;
      varying vec3 vSolidFace;
      varying vec3 vSolidViewX;
      varying vec3 vSolidViewY;
    `).replace('#include <beginnormal_vertex>',`
      #include <beginnormal_vertex>
      // Jacobian tangents of the *same* deformation as position. This keeps
      // highlights attached to a liquid patch rather than an unrelated ripple.
      if(uLiquidEnergy>.0001){
        vec3 n=normalize(objectNormal);
        vec3 tangent=normalize(cross(abs(n.z)<.8?vec3(0.,0.,1.):vec3(0.,1.,0.),n));
        vec3 bitangent=cross(n,tangent);
        float epsilon=.001;
        vec3 alongT=liquidPosition(position+tangent*epsilon)-liquidPosition(position-tangent*epsilon);
        vec3 alongB=liquidPosition(position+bitangent*epsilon)-liquidPosition(position-bitangent*epsilon);
        objectNormal=normalize(cross(alongT,alongB));
      }
    `).replace('#include <begin_vertex>',`
      #include <begin_vertex>
      vSolidLocal=position;
      vSolidFace=normal;
      vSolidViewX=normalize(normalMatrix*vec3(1.,0.,0.));
      vSolidViewY=normalize(normalMatrix*vec3(0.,1.,0.));
      transformed=liquidPosition(position);
    `);
    shader.fragmentShader=shader.fragmentShader.replace('#include <common>',`
      #include <common>
      ${deformation}
      uniform sampler2D uSolidMask;
      uniform sampler2D uEdgeDistance;
      uniform float uSolidReveal;
      uniform vec4 uSolidBounds;
      uniform sampler2D uMarbleVeins;
      uniform vec4 uMarbleBounds;
      varying vec3 vSolidLocal;
      varying vec3 vSolidFace;
      varying vec3 vSolidViewX;
      varying vec3 vSolidViewY;
      // The reference's irregular mineral branches replace the prior evenly
      // spaced procedural cracks. Only pigment is sampled; PBR still supplies
      // all dimensional shading, highlights and the flowing local response.
      vec3 marblePigment(vec3 point){
        vec2 uv=(point.xy-uMarbleBounds.xy)/uMarbleBounds.zw;
        vec3 mineral=texture2D(uMarbleVeins,uv).rgb;
        vec3 body=mix(vec3(1.),vec3(.72,.77,.82),mineral.g*.26);
        body=mix(body,vec3(.20,.31,.47),mineral.b*.30);
        return mix(body,vec3(.028,.070,.190),mineral.r*.96);
      }
    `).replace('#include <color_fragment>',`
      #include <color_fragment>
      diffuseColor.rgb*=marblePigment(vSolidLocal);
    `).replace('#include <alphatest_fragment>',`
      vec2 solidUv=(vSolidLocal.xy-uSolidBounds.xy)/uSolidBounds.zw;
      vec2 meltDelta=vSolidLocal.xy-uLiquidPoint;
      float meltField=liquidField(vSolidLocal.xy);
      float moltenFlow=sin(meltDelta.y*23.-uLiquidTime*12.+sin(meltDelta.x*18.)*.8);
      solidUv+=vec2(moltenFlow*.010,sin(meltDelta.x*25.+uLiquidTime*9.)*.010)*meltField;
      float dispersal=texture2D(uSolidMask,solidUv).r;
      float surviving=1.-.83*smoothstep(.08,.78,dispersal);
      float formed=smoothstep(0.,1.,uSolidReveal);
      // Preserve the original local translucent dispersal/return envelope.
      float moltenSeam=meltField*smoothstep(-.10,.87,moltenFlow);
      diffuseColor.a*=clamp(surviving*(1.-.66*moltenSeam),.08,1.)*formed;
      #include <alphatest_fragment>
    `).replace('#include <normal_fragment_maps>',`
      #include <normal_fragment_maps>
      if(vSolidFace.z>.75){
        vec2 edgeUv=(vSolidLocal.xy-uSolidBounds.xy)/uSolidBounds.zw;
        vec3 relief=texture2D(uEdgeDistance,edgeUv).rgb;
        float edgeDepth=relief.b*30.;
        vec2 edgeGradient=relief.rg*2.-1.;
        // A broad rounded shoulder occupies the narrow strokes themselves,
        // rather than a thin dark border around a flat face. Keep the gradient
        // zero at a stroke's centre so opposite shoulders meet smoothly.
        float edgeBevel=sqrt(max(0.,1.-smoothstep(0.,25.,edgeDepth)));
        normal=normalize(normal-(vSolidViewX*edgeGradient.x+vSolidViewY*edgeGradient.y)*edgeBevel*.70);
      }
    `);
    // Do not override outgoingLight: the actual room lights, PBR normals and
    // restrained clearcoat now light both faces and edges consistently.
  };
  const mesh=new THREE.Mesh(geometry,materials);
  mesh.name='exact-solid-chinmaya-logo';
  geometry.boundingSphere.radius+=.16;
  geometry.boundingBox.expandByScalar(.16);
  mesh.renderOrder=3;
  mesh.visible=false;
  parent.add(mesh);

  let disposed=false,cachedRest=null,cachedTotal=0,cellIndex=null;
  let previousTime=null,peakMask=0,activeSamples=0,maximumDisplacement=0,textureUploads=0;
  let liquidEnergy=0;
  function cacheCells(rest,total){
    cachedRest=rest;cachedTotal=total;cellIndex=new Uint32Array(total);
    for(let i=0;i<total;i++){
      const j=i*3;
      const x=Math.max(0,Math.min(width-1,Math.floor((rest[j]-minX)/extentX*width)));
      const y=Math.max(0,Math.min(height-1,Math.floor((rest[j+1]-minY)/extentY*height)));
      cellIndex[i]=y*width+x;
    }
  }
  function clearMask(){
    if(peakMask>0){bytes.fill(0);smoothed.fill(0);texture.needsUpdate=true;textureUploads++;}
    peakMask=0;activeSamples=0;maximumDisplacement=0;
  }
  function update({introSeconds=0,positions,rest,total=0,reduced=false,cursor=null,impulse=0,updateMask=true}={}){
    if(disposed)return;
    const time=Number.isFinite(introSeconds)?introSeconds:0;
    let delta=previousTime===null?1/60:time-previousTime;
    if(delta<=0||delta>.1)delta=1/60;
    previousTime=time;
    const reveal=reduced?1:THREE.MathUtils.smoothstep(time,settings.revealStart,settings.revealEnd);
    uniforms.uSolidReveal.value=reveal;mesh.visible=reveal>.0001;
    const liquidTarget=reduced?0:Math.min(settings.liquidMaximum,Math.max(0,impulse));
    const liquidRate=liquidTarget>liquidEnergy?settings.liquidAttackSeconds:settings.liquidReleaseSeconds;
    liquidEnergy+=(liquidTarget-liquidEnergy)*(1-Math.exp(-delta/liquidRate));
    if(cursor&&Number.isFinite(cursor.x)&&Number.isFinite(cursor.y)){
      const point=uniforms.uLiquidPoint.value;
      const follow=1-Math.exp(-delta/.055);
      point.x+=(cursor.x-point.x)*follow;
      point.y+=(cursor.y-point.y)*follow;
    }
    uniforms.uLiquidEnergy.value=liquidEnergy;
    uniforms.uLiquidTime.value=time;
    if(reduced||reveal<.999||!positions||!rest||total<1||!updateMask){clearMask();return;}
    total=Math.min(total,Math.floor(rest.length/3),Math.floor(positions.length/3));
    if(cachedRest!==rest||cachedTotal!==total)cacheCells(rest,total);
    target.fill(0);activeSamples=0;maximumDisplacement=0;
    const start=settings.displacementStart,full=settings.displacementFull;
    for(let i=0;i<total;i++){
      const j=i*3,dx=positions[j]-rest[j],dy=positions[j+1]-rest[j+1],dz=positions[j+2]-rest[j+2];
      const square=dx*dx+dy*dy+dz*dz;
      if(square<=start*start)continue;
      const distance=Math.sqrt(square);
      if(!Number.isFinite(distance))continue;
      maximumDisplacement=Math.max(maximumDisplacement,distance);activeSamples++;
      const v=Math.min(1,(distance-start)/(full-start));
      const strength=v*v*(3-2*v),index=cellIndex[i];
      if(strength>target[index])target[index]=strength;
    }
    if(!activeSamples&&peakMask<.002){clearMask();return;}
    // Cover the small spaces between surface samples, including the mobile subset.
    // A three-cell dilation followed by a five-tap blur keeps the edge organic.
    for(let y=0;y<height;y++)for(let x=0;x<width;x++){
      const i=y*width+x;
      horizontal[i]=Math.max(target[i],target[y*width+Math.max(0,x-1)],target[y*width+Math.min(width-1,x+1)]);
    }
    for(let y=0;y<height;y++)for(let x=0;x<width;x++){
      const i=y*width+x;
      dilated[i]=Math.max(horizontal[i],horizontal[Math.max(0,y-1)*width+x],horizontal[Math.min(height-1,y+1)*width+x]);
    }
    for(let y=0;y<height;y++)for(let x=0;x<width;x++){
      const row=y*width;
      horizontal[row+x]=(dilated[row+Math.max(0,x-2)]+4*dilated[row+Math.max(0,x-1)]+6*dilated[row+x]+4*dilated[row+Math.min(width-1,x+1)]+dilated[row+Math.min(width-1,x+2)])/16;
    }
    for(let y=0;y<height;y++)for(let x=0;x<width;x++){
      const i=y*width+x;
      blurred[i]=(horizontal[Math.max(0,y-2)*width+x]+4*horizontal[Math.max(0,y-1)*width+x]+6*horizontal[i]+4*horizontal[Math.min(height-1,y+1)*width+x]+horizontal[Math.min(height-1,y+2)*width+x])/16;
    }
    const attack=1-Math.exp(-delta/settings.attackSeconds),release=1-Math.exp(-delta/settings.releaseSeconds);
    peakMask=0;
    for(let i=0;i<pixels;i++){
      const targetValue=blurred[i];
      smoothed[i]+=(targetValue-smoothed[i])*(targetValue>smoothed[i]?attack:release);
      peakMask=Math.max(peakMask,smoothed[i]);
      bytes[i]=Math.round(smoothed[i]*255);
    }
    texture.needsUpdate=true;textureUploads++;
  }
  function dispose(){
    if(disposed)return;
    disposed=true;mesh.removeFromParent();geometry.dispose();materials.forEach(item=>item.dispose());texture.dispose();edgeDistance.dispose();veinTexture.dispose();
    cellIndex=null;cachedRest=null;
  }
  return {
    update,dispose,mesh,
    get maxMask(){return peakMask;},
    get liquidEnergy(){return liquidEnergy;},
    inspect(){return {
      disposed,visible:mesh.visible,reveal:uniforms.uSolidReveal.value,
      exactSourcePerimeter:true,boundaryVertices:data.boundaryVertexCount,
      materialRelief:true,finish:'polished warm ivory marble with reference-derived deep blue mineral veins',bodyOpacity:material.opacity,
      deformationNormals:'finite-difference Jacobian of shared liquid displacement',veinSpace:'undeformed object coordinates',
      shoulderRelief:'float distance smoothed during preparation; RG signed direction/B depth, linear data sampling',
      metalness:material.metalness,roughness:material.roughness,liquidEnergy,
      clearcoat:material.clearcoat,edgeMetalness:materials[1].metalness,
      sourceSHA256:finish.sourceSHA256,
      sourceTriangles:data.sourceTriangleCount,
      renderedTriangles:geometry.getAttribute('position').count/3,
      maxMask:peakMask,activeSamples,maximumDisplacement,textureUploads,
      maskSize:[width,height],bounds:{min:geometry.boundingBox.min.toArray(),max:geometry.boundingBox.max.toArray()}
    };}
  };
}
