// A circular, continuous chamber in the Founders palette. Geometry, lighting and
// textures are local; the main page owns the only animation loop.
export function createSanctuary({ THREE, scene }) {
  const group = new THREE.Group();
  group.name = 'ivory-circular-chamber';
  scene.add(group);
  const colors = {
    ivory: new THREE.Color('#F6F0E2'), sand: new THREE.Color('#E9DFCD'),
    ink: new THREE.Color('#342F27'), muted: new THREE.Color('#756A5B'),
    copper: new THREE.Color('#A66A3F')
  };
  const uniforms = {
    uTime: { value: 0 }, uEntrance: { value: 1 }, uInteraction: { value: 0 },
    uIvory: { value: colors.ivory }, uSand: { value: colors.sand },
    uInk: { value: colors.ink }, uMuted: { value: colors.muted },
    uCopper: { value: colors.copper }
  };
  const vertex = `
    varying vec2 vUv; varying vec3 vLocal,vWorld,vNormal;
    void main(){
      vUv=uv;vLocal=position;
      vNormal=normalize(mat3(modelMatrix)*normal);
      vec4 world=modelMatrix*vec4(position,1.);vWorld=world.xyz;
      gl_Position=projectionMatrix*viewMatrix*world;
    }
  `;
  const palette = `
    uniform vec3 uIvory,uSand,uInk,uMuted,uCopper;
    uniform float uTime,uEntrance,uInteraction;
    varying vec2 vUv; varying vec3 vLocal,vWorld,vNormal;
    float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
    float noise(vec2 p){
      vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
      return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),mix(hash(i+vec2(0.,1.)),hash(i+vec2(1.)),f.x),f.y);
    }
  `;
  function shader(fragment, options = {}) {
    return new THREE.ShaderMaterial({
      uniforms, vertexShader: vertex,
      fragmentShader: palette + `void main(){` + fragment + `
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`, side: THREE.DoubleSide, toneMapped: false, ...options
    });
  }
  function mesh(geometry,material,name,parent=group){
    const object=new THREE.Mesh(geometry,material);object.name=name;parent.add(object);return object;
  }
  const centreZ=-.60;

  // The back half of a real cylinder creates the enclosing spatial shape. It
  // remains open behind the camera, including at the narrow-screen camera pose.
  const wall=mesh(new THREE.CylinderGeometry(9.5,9.5,14,192,12,true,Math.PI/2,Math.PI),shader(`
    float angle=atan(vWorld.x,-(vWorld.z-1.8));
    float foot=exp(-max(0.,vWorld.y+2.32)*1.25);
    float sides=smoothstep(.04,1.02,abs(angle));
    float ceiling=exp(-pow((vWorld.y-4.45)/1.75,2.));
    vec3 color=mix(uIvory,uSand,.36+sides*.40);
    color=mix(color,uMuted,.018+foot*.24+sides*.18);
    // Broad reflected windows are dissolved into the limestone, never hard bars.
    float light=exp(-pow((angle+.30)/.27,2.))*.19;
    light+=exp(-pow((angle-.65)/.16,2.))*.09;
    float vertical=exp(-pow((vWorld.y-1.3)/4.8,2.));
    color=mix(color,uIvory,light*vertical+ceiling*.15);
    color+=(noise(vWorld.xy*.65)-.5)*.015;
    color+=(noise(vWorld.xy*90.)-.5)*.009;
    gl_FragColor=vec4(color,1.);
  `),'continuous-cylindrical-limestone-wall');
  wall.position.set(0,4.68,1.8);

  const floor=mesh(new THREE.PlaneGeometry(70,70),shader(`
    float r=length(vec2(vWorld.x,vWorld.z+.6));
    vec3 color=mix(uSand,uIvory,.16+smoothstep(3.,17.,r)*.20);
    color=mix(color,uMuted,exp(-pow((r-7.2)/1.5,2.))*.17);
    float reflected=exp(-pow((vWorld.x+vWorld.z*.25+2.0)/3.3,2.));
    color=mix(color,uIvory,reflected*.15);
    color+=(noise(vWorld.xz*82.)-.5)*.009;
    gl_FragColor=vec4(color,1.);
  `),'chamber-floor');
  floor.rotation.x=-Math.PI/2;floor.position.y=-2.36;

  // Soft contact shadows establish each broad stone terrace without shadow maps.
  function shadow(radius,y,opacity,name){
    const object=mesh(new THREE.PlaneGeometry(radius*2.7,radius*2.7),shader(`
      vec2 p=(vUv-.5)*2.;
      float a=exp(-dot(p,p)*3.4)*(1.-smoothstep(.65,1.,length(p)));
      gl_FragColor=vec4(uMuted,a*${opacity.toFixed(3)});
    `,{transparent:true,depthWrite:false}),name);
    object.rotation.x=-Math.PI/2;object.position.set(0,y,centreZ);return object;
  }
  shadow(7.3,-2.353,.18,'outer-terrace-contact-shadow');

  const stone=shader(`
    float up=clamp(vNormal.y,0.,1.);
    float lit=clamp(dot(normalize(vNormal),normalize(vec3(-.5,.8,.65))),0.,1.);
    float radius=length(vec2(vWorld.x,vWorld.z+.6));
    vec3 color=mix(uSand,uIvory,.06+up*.25+lit*.18);
    color=mix(color,uMuted,(1.-up)*.27);
    // Each upper terrace occludes a narrow strip of the lower stone. These
    // radial falloffs reveal the layered circular shape without dark outlines.
    float contact=exp(-pow((radius-4.88)/.19,2.))*(1.-smoothstep(-2.23,-2.18,vWorld.y));
    contact+=exp(-pow((radius-3.28)/.17,2.))*(1.-smoothstep(-2.09,-2.04,vWorld.y));
    contact+=exp(-pow((radius-1.88)/.16,2.))*(1.-smoothstep(-1.98,-1.88,vWorld.y));
    color=mix(color,uMuted,clamp(contact,0.,1.)*.24*up);
    float sheen=exp(-pow((vWorld.x+vWorld.z*.27+2.)/2.5,2.));
    color=mix(color,uIvory,sheen*.13*up);
    float polish=sin(radius*110. +noise(vWorld.xz*.3)*.6)*.0014;
    color+=polish+(noise(vWorld.xz*98.)-.5)*.009;
    gl_FragColor=vec4(color,1.);
  `);
  const edgeMaterial=new THREE.MeshBasicMaterial({color:colors.copper,transparent:true,opacity:.23,depthWrite:false,toneMapped:false});
  const seamMaterial=new THREE.MeshBasicMaterial({color:colors.muted,transparent:true,opacity:.27,depthWrite:false,toneMapped:false});
  const lightMaterial=new THREE.MeshBasicMaterial({color:0xfff8e6,transparent:true,opacity:.73,depthWrite:false,toneMapped:false});
  function circle(radius,y,tube,material,name){
    const ring=mesh(new THREE.TorusGeometry(radius,tube,6,192),material,name);
    ring.rotation.x=Math.PI/2;ring.position.set(0,y,centreZ);return ring;
  }
  function terrace(radius,bottom,top,name){
    const bevel=Math.min(.10,(top-bottom)*.3);
    const profile=[
      [0,bottom],[radius-.06,bottom],[radius,bottom+bevel],
      [radius,top-bevel],[radius-.025,top-.017],[radius-.075,top],[0,top]
    ].map(([x,y])=>new THREE.Vector2(x,y));
    const obj=mesh(new THREE.LatheGeometry(profile,192),stone,name);obj.position.z=centreZ;
    return obj;
  }
  // Low concentric terraces continue outside the frame, matching the reference's
  // circular floor rather than introducing freestanding architectural shapes.
  terrace(6.95,-2.35,-2.24,'outer-circular-terrace');
  circle(6.83,-2.235,.010,seamMaterial,'outer-terrace-cut');
  terrace(4.85,-2.237,-2.105,'middle-circular-terrace');
  circle(4.84,-2.132,.022,lightMaterial,'middle-recessed-ivory-light');
  circle(4.67,-2.098,.005,edgeMaterial,'middle-copper-inlay');
  terrace(3.25,-2.102,-1.995,'inner-circular-terrace');
  circle(3.22,-2.015,.013,lightMaterial,'inner-recessed-ivory-light');
  circle(3.03,-1.989,.0045,seamMaterial,'inner-stone-engraving');
  circle(2.67,-1.989,.004,seamMaterial,'inner-stone-engraving-two');
  shadow(2.03,-1.986,.31,'central-plinth-contact-shadow');
  terrace(1.85,-1.979,-1.745,'central-bevelled-stone-plinth');
  circle(1.83,-1.86,.012,lightMaterial,'plinth-recessed-edge-light');
  circle(1.69,-1.738,.0045,edgeMaterial,'plinth-copper-hairline');
  circle(1.53,-1.738,.0035,seamMaterial,'plinth-inner-engraving');
  const logoShadow=shadow(1.25,-1.732,.18,'suspended-logo-contact-shadow');
  const reflectedLight=mesh(new THREE.PlaneGeometry(3.3,2.8),shader(`
    vec2 p=(vUv-.5)*2.;
    float a=exp(-dot(p,p)*5.)*(1.-smoothstep(.6,1.,length(p)));
    gl_FragColor=vec4(mix(uCopper,uIvory,.69),a*(.025+uInteraction*.045));
  `,{transparent:true,depthWrite:false,blending:THREE.AdditiveBlending}),'emblem-light-on-plinth');
  reflectedLight.rotation.x=-Math.PI/2;reflectedLight.position.set(0,-1.728,centreZ);

  // Only the far arc of this high circular rim enters the main camera framing.
  // Its bright underside suggests a large soft ceiling aperture above the room.
  const ceilingMaterial=shader(`
    float under=clamp(-vNormal.y,0.,1.);
    vec3 color=mix(uSand,uIvory,.48+under*.37);
    color=mix(color,uMuted,(1.-under)*.065);
    gl_FragColor=vec4(color,1.);
  `);
  const rim=mesh(new THREE.TorusGeometry(5.75,.085,12,192),ceilingMaterial,'high-circular-ceiling-rim');
  rim.rotation.x=Math.PI/2;rim.position.set(0,4.78,centreZ);
  circle(5.70,4.718,.026,lightMaterial,'ceiling-rim-ivory-underside');
  circle(5.825,4.80,.006,edgeMaterial,'ceiling-rim-copper-inlay');

  const hemisphere=new THREE.HemisphereLight(0xfffaf0,0x746354,1.45);
  hemisphere.name='ivory-room-bounce';group.add(hemisphere);
  const key=new THREE.DirectionalLight(0xfff2d9,2.35);
  key.position.set(-4.4,7.4,4.5);key.name='large-high-left-window';group.add(key);
  const fill=new THREE.DirectionalLight(0xffffff,.38);
  fill.position.set(4.5,2,3);fill.name='soft-stone-fill';group.add(fill);

  // Sparse suspended dust and a very broad shaft supply atmosphere without
  // obscuring the sculpture or competing with its much denser entrance effect.
  const shaft=mesh(new THREE.PlaneGeometry(13,14),shader(`
    float diagonal=vLocal.x+vLocal.y*.44+1.1;
    float band=exp(-pow(diagonal/2.6,2.));
    float edge=smoothstep(-7.,-5.,vLocal.y)*(1.-smoothstep(4.6,7.,vLocal.y));
    gl_FragColor=vec4(uIvory,band*edge*.055);
  `,{transparent:true,depthWrite:false,blending:THREE.AdditiveBlending}),'soft-high-window-atmosphere');
  shaft.position.set(-.4,1.2,-4.5);
  const count=100,positions=new Float32Array(count*3),seeds=new Float32Array(count);
  function seeded(n){return Math.abs(Math.sin(n*127.1+45.32)*43758.5453)%1;}
  for(let i=0;i<count;i++){
    positions[i*3]=(seeded(i*3+1)-.5)*13;
    positions[i*3+1]=-1.4+seeded(i*3+2)*8;
    positions[i*3+2]=-5+seeded(i*3+3)*5.5;
    seeds[i]=seeded(i+7.3);
  }
  const moteGeometry=new THREE.BufferGeometry();
  moteGeometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
  moteGeometry.setAttribute('aSeed',new THREE.BufferAttribute(seeds,1));
  const moteMaterial=new THREE.ShaderMaterial({
    uniforms,transparent:true,depthWrite:false,toneMapped:false,
    vertexShader:`
      attribute float aSeed;uniform float uTime;varying float vAlpha;
      void main(){
        vec3 p=position;p.x+=sin(uTime*.105+aSeed*25.)*.10;p.y+=sin(uTime*.15+aSeed*12.)*.075;
        vec4 view=modelViewMatrix*vec4(p,1.);gl_Position=projectionMatrix*view;
        gl_PointSize=clamp((1.3+aSeed*1.6)*9./-view.z,1.,3.5);vAlpha=.07+pow(aSeed,3.)*.19;
      }
    `,
    fragmentShader:`
      uniform vec3 uCopper,uIvory;varying float vAlpha;
      void main(){
        float d=length(gl_PointCoord-.5)*2.;if(d>1.)discard;
        gl_FragColor=vec4(mix(uCopper,uIvory,.3),(1.-smoothstep(.1,1.,d))*vAlpha);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `
  });
  const motes=new THREE.Points(moteGeometry,moteMaterial);motes.name='sparse-chamber-dust';group.add(motes);
  let disposed=false;
  return {
    group,
    update({time=0,parallaxX=0,parallaxY=0,interaction=0,entrance=1}={}){
      if(disposed)return;
      uniforms.uTime.value=Number.isFinite(time)?time:0;
      uniforms.uEntrance.value=Number.isFinite(entrance)?entrance:1;
      uniforms.uInteraction.value=Math.max(0,Math.min(1,Number(interaction)||0));
      motes.rotation.y=(Number(parallaxX)||0)*.018;
      motes.position.y=(Number(parallaxY)||0)*.028;
      shaft.position.x=-.4+(Number(parallaxX)||0)*.045;
      logoShadow.scale.x=1+Math.sin(uniforms.uTime.value*.42)*.025;
    },
    inspect(){return {type:'circular-chamber',terraces:3,centralPlinth:true,wallRadius:9.5,ceilingRadius:5.75,disposed};},
    dispose(){
      if(disposed)return;disposed=true;
      const geometries=new Set(),materials=new Set();
      group.traverse(object=>{
        if(object.geometry)geometries.add(object.geometry);
        if(object.material){for(const item of(Array.isArray(object.material)?object.material:[object.material]))materials.add(item);}
      });
      for(const geometry of geometries)geometry.dispose();
      for(const material of materials)material.dispose();
      scene.remove(group);group.clear();
    }
  };
}
