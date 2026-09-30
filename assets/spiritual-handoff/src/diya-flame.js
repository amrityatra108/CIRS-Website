// The archive contains the original bowl, oil, and cotton wick, but no exported
// TurbulenceFD fire volume. This small flame is anchored to that actual wick tip.
// Animation is shader-only, with no sprites or per-frame geometry allocation.
export function createDiyaFlame({ THREE, group, anchor: wickAnchor, height = .75 }) {
  if (!wickAnchor?.isVector3 || !wickAnchor.toArray().every(Number.isFinite)) {
    throw new Error('The diya flame requires the actual wick-tip anchor.');
  }
  const flameHeight = Number.isFinite(height) ? Math.max(.05, height) : .75;
  const profile = [];
  for (let i = 0; i <= 40; i++) {
    const h = i / 40;
    const radius = Math.pow(Math.sin(h * Math.PI), .86) * (.21 - .07 * h) * flameHeight;
    profile.push(new THREE.Vector2(Math.max(0, radius), h * flameHeight));
  }
  const ownedGeometry = new THREE.LatheGeometry(profile, 48);
  const positions = ownedGeometry.getAttribute('position');
  for (let i = 0; i < positions.count; i++) {
    const h = positions.getY(i) / flameHeight;
    positions.setXYZ(i,
      positions.getX(i) + wickAnchor.x + Math.pow(h, 2.5) * flameHeight * .035,
      positions.getY(i) + wickAnchor.y,
      positions.getZ(i) * .83 + wickAnchor.z);
  }
  ownedGeometry.computeVertexNormals();
  ownedGeometry.computeBoundingBox();
  if (!ownedGeometry.getAttribute('normal')) ownedGeometry.computeVertexNormals();
  const box = ownedGeometry.boundingBox.clone();
  const size = box.getSize(new THREE.Vector3());
  if (![size.x, size.y, size.z].every(Number.isFinite) || size.y <= 0) {
    ownedGeometry.dispose();
    throw new Error('The supplied diya flame has invalid bounds.');
  }
  const center = box.getCenter(new THREE.Vector3());
  const wick = wickAnchor.clone();
  const anchor = new THREE.Vector3(center.x, box.min.y + size.y * .47, center.z);
  const half = new THREE.Vector3(Math.max(size.x * .5, .0001), size.y, Math.max(size.z * .5, .0001));
  const container = new THREE.Group();
  container.name = 'animated-diya-fire-at-original-wick';
  group.add(container);

  const shared = {
    uTime: { value: 0 }, uOpacity: { value: 1 },
    uWick: { value: wick }, uScale: { value: half }
  };
  const vertexShader = `
    uniform float uTime,uCore;
    uniform vec3 uWick,uScale;
    varying vec3 vFlame,vViewNormal,vViewDirection;
    varying float vHeight;
    void main(){
      vec3 q=(position-uWick)/uScale;
      float h=clamp(q.y,0.,1.);
      vec3 p=position;
      // The wick remains fixed while the tip gently bends and breathes.
      float lean=pow(h,1.85);
      float sway=sin(uTime*8.1)+.42*sin(uTime*13.7+1.3)+.16*sin(uTime*23.4);
      float back=sin(uTime*6.8+.8)+.35*sin(uTime*11.9);
      p.x+=sway*uScale.y*.016*lean;
      p.z+=back*uScale.y*.011*lean;
      p.y+=sin(uTime*10.2+.35*sin(uTime*3.1))*uScale.y*.020*h;
      // An inner envelope produces a luminous warm core.
      p.x=mix(p.x,uWick.x+(p.x-uWick.x)*.57,uCore);
      p.z=mix(p.z,uWick.z+(p.z-uWick.z)*.57,uCore);
      p.y=mix(p.y,uWick.y+(p.y-uWick.y)*.88,uCore);
      vFlame=q;vHeight=h;
      vec4 view=modelViewMatrix*vec4(p,1.);
      vViewNormal=normalize(normalMatrix*normal);
      vViewDirection=-view.xyz;
      gl_Position=projectionMatrix*view;
    }
  `;
  const fragmentShader = `
    uniform float uTime,uOpacity,uCore;
    varying vec3 vFlame,vViewNormal,vViewDirection;
    varying float vHeight;
    float hash(vec3 p){
      p=fract(p*.3183099+vec3(.1,.2,.3));p*=17.;
      return fract(p.x*p.y*p.z*(p.x+p.y+p.z));
    }
    float noise(vec3 p){
      vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
      return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),
                     mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),
                 mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),
                     mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);
    }
    void main(){
      float h=vHeight;
      vec3 stream=vec3(vFlame.x*2.7,h*4.2-uTime*2.8,vFlame.z*2.7);
      float heat=noise(stream)*.73+noise(stream*2.03+vec3(1.7,-uTime*.6,2.1))*.27;
      float facing=abs(dot(normalize(vViewNormal),normalize(vViewDirection)));
      float body=exp(-abs(vFlame.x)*2.9)*(1.-smoothstep(.64,1.,h));
      float ribbon=sin(vFlame.x*7.+heat*4.5+h*2.3-uTime*1.15)*.5+.5;
      float core=clamp(body*.57+facing*.19+heat*.18+ribbon*.07+uCore*.40,0.,1.);
      vec3 ember=vec3(.90,.115,.009);
      vec3 amber=vec3(1.,.46,.042);
      vec3 ivory=vec3(1.,.92,.65);
      vec3 color=mix(ember,amber,smoothstep(.05,.53,core));
      color=mix(color,ivory,smoothstep(.48,.95,core));
      // A restrained cooler base anchors the flame at the physical wick.
      float base=(1.-smoothstep(.025,.13,h))*.15;
      color=mix(color,vec3(.33,.40,.63),base);
      float breath=.94+.045*sin(uTime*10.2)+.015*sin(uTime*19.7);
      float alpha=mix(.54,.87,core)*breath;
      // At the opening macro distance, reveal the fire's moving hot layers.
      float macro=1.-smoothstep(.16,.55,length(vViewDirection));
      float innerHeat=noise(stream*5.5+vec3(0.,-uTime*2.,0.));
      color=mix(color,mix(vec3(1.,.32,.035),ivory,smoothstep(.20,.78,innerHeat)),macro*.78);
      alpha=mix(alpha,.98,macro);
      alpha*=mix(1.,.82,uCore);
      alpha*=smoothstep(0.,.025,h)*(1.-smoothstep(.945,1.,h)*.63);
      gl_FragColor=vec4(color,alpha*uOpacity);
      #include <colorspace_fragment>
    }
  `;
  const materials = [0, 1].map(core => new THREE.ShaderMaterial({
    uniforms: { ...shared, uCore: { value: core } },
    vertexShader, fragmentShader, transparent: true, depthWrite: false,
    side: THREE.DoubleSide, blending: THREE.NormalBlending, toneMapped: false
  }));
  const mesh = new THREE.Mesh(ownedGeometry, materials[0]);
  mesh.name = 'diya-fire-amber-envelope';
  mesh.frustumCulled = false;
  mesh.renderOrder = 3;
  const core = new THREE.Mesh(ownedGeometry, materials[1]);
  core.name = 'diya-fire-ivory-core';
  core.frustumCulled = false;
  core.renderOrder = 4;
  container.add(mesh, core);
  const light = new THREE.PointLight(0xffb956, 1.25, Math.max(2.4, size.y * 8), 2);
  light.position.copy(anchor);
  container.add(light);
  let lastTime = 0, lastOpacity = 1, disposed = false;

  function update({ time = lastTime, opacity = 1 } = {}) {
    if (disposed) return;
    lastTime = Number.isFinite(time) ? time : lastTime;
    lastOpacity = Number.isFinite(opacity) ? Math.max(0, Math.min(1, opacity)) : 0;
    shared.uTime.value = lastTime;
    shared.uOpacity.value = lastOpacity;
    container.visible = lastOpacity > .001;
    light.intensity = lastOpacity * (1.25 + .10 * Math.sin(lastTime * 8.1) + .035 * Math.sin(lastTime * 19.7));
  }
  function dispose() {
    if (disposed) return;
    disposed = true;
    container.removeFromParent();
    ownedGeometry.dispose();
    materials.forEach(material => material.dispose());
    light.dispose?.();
  }
  return {
    update, anchor, wick, mesh, dispose,
    inspect() {
      return { disposed, time: lastTime, opacity: lastOpacity, visible: container.visible,
        fireVertices: ownedGeometry.getAttribute('position').count,
        generatedFireAtOriginalWick: true,
        bounds: { min: box.min.toArray(), max: box.max.toArray() },
        anchor: anchor.toArray(), wick: wick.toArray(), shaderFlicker: true };
    }
  };
}
