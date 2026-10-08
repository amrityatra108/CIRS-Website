// All times are relative to the beginning of a page entrance. The particle
// field in intro-particles.js shares this clock and the same 1.35-unit radius.
// These layers add the warm flowing surface and the six supplied photographs.
// No additional render loop, event listeners, external requests, or audio.
import { energyClock, energyPulse, morphProgress } from './orb-motion.js?v=83bf040586';

export const ORB_SETTINGS = Object.freeze({
  radius: 1.35,
  formedAt: .85,
  photoSeconds: 4,
  formationAt: 4.85,
  completeAt: 6.4,
  photoPeakOpacity: .64,
  filaments: 24
});

const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
const smooth = (a, b, value) => { const x = clamp((value - a) / (b - a)); return x * x * (3 - 2 * x); };

// A square view into each original image, centered on the person. Texture
// coordinates provide the crop; the distributed WebPs remain uncropped.
const PHOTO_FRAMING = [
  { aspect: 1172 / 1430, center: [.5, .59] },
  { aspect: 1018 / 1426, center: [.5, .58] },
  { aspect: 944 / 1436, center: [.5, .59] },
  { aspect: 950 / 1432, center: [.5, .51] },
  { aspect: 1964 / 1274, center: [.61, .5] },
  { aspect: 1062 / 1404, center: [.5, .61] }
];

const noiseGLSL = `
  float hash31(vec3 p){
    p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);
  }
  float noise3(vec3 p){
    vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
    return mix(mix(mix(hash31(i),hash31(i+vec3(1,0,0)),f.x),
                   mix(hash31(i+vec3(0,1,0)),hash31(i+vec3(1,1,0)),f.x),f.y),
               mix(mix(hash31(i+vec3(0,0,1)),hash31(i+vec3(1,0,1)),f.x),
                   mix(hash31(i+vec3(0,1,1)),hash31(i+vec3(1,1,1)),f.x),f.y),f.z);
  }
`;

export async function createEnergyOrb({ THREE, parent }) {
  const group = new THREE.Group();
  group.name = 'warm-energy-orb-and-six-gurudev-photographs';
  parent.add(group);
  const geometries = [], materials = [], textures = [];
  const shared = { uTime: { value: 0 }, uOpacity: { value: 0 }, uPulse: { value: 1 }, uMorph: { value: 0 }, uPower: { value: 0 } };
  const hazeOpacity = { value: 0 };
  let disposed = false, lastTime = 0, lastIntro = 0, lastOpacity = 0, lastMorph = 0, lastClock = 0;
  let activePhotos = [], photoWeights = new Array(6).fill(0);

  // Give every flowing ribbon a real destination on the exact supplied logo.
  // Arc-length spacing covers small detached marks and both interior holes,
  // without connecting separate contours with stray diagonal strokes.
  let contourData;
  try {
    const response = await fetch(new URL('../assets/logo-solid-outline.json', import.meta.url));
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    contourData = await response.json();
  } catch (error) {
    group.removeFromParent();
    throw new Error(`The orb-to-logo contour could not be loaded: ${error.message}`);
  }
  const contours = contourData.shapes.flatMap(shape => [shape.outline, ...(shape.holes || [])]).map(points => {
    const lengths = [0];
    for (let i = 0; i < points.length; i++) {
      const a = points[i], b = points[(i + 1) % points.length];
      lengths.push(lengths[i] + Math.hypot(b[0] - a[0], b[1] - a[1]));
    }
    return { points, lengths, length: lengths.at(-1), strands: 1 };
  });
  if (!contours.length || contours.some(contour => !Number.isFinite(contour.length) || contour.length <= 0)) {
    group.removeFromParent();throw new Error('The orb requires finite original logo contours.');
  }
  for (let remaining = ORB_SETTINGS.filaments - contours.length; remaining > 0; remaining--) {
    contours.reduce((best, contour) => contour.length / contour.strands > best.length / best.strands ? contour : best).strands++;
  }
  const strandTargets = contours.flatMap(contour => Array.from({ length: contour.strands }, (_, part) => ({ contour, part })));
  function sampleContour(contour, fraction) {
    const distance = clamp(fraction) * contour.length;
    let low = 0, high = contour.points.length - 1;
    while (low < high) { const mid = Math.floor((low + high) / 2); if (contour.lengths[mid + 1] < distance) low = mid + 1; else high = mid; }
    const index = low, a = contour.points[index], b = contour.points[(index + 1) % contour.points.length];
    const ratio = clamp((distance - contour.lengths[index]) / Math.max(.000001, contour.lengths[index + 1] - contour.lengths[index]));
    return [a[0] + (b[0] - a[0]) * ratio, a[1] + (b[1] - a[1]) * ratio, contourData.zMax + .006];
  }

  const loader = new THREE.TextureLoader();
  try {
    const outcomes = await Promise.allSettled(Array.from({ length: 6 }, (_, index) =>
      loader.loadAsync(new URL(`../assets/orb-photos/gurudev-${String(index + 1).padStart(2, '0')}.webp`, import.meta.url).href)
    ));
    const loaded=outcomes.filter(result=>result.status==='fulfilled').map(result=>result.value);
    const failure=outcomes.find(result=>result.status==='rejected');
    if(failure){loaded.forEach(texture=>texture.dispose());throw failure.reason;}
    loaded.forEach(texture => {
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.magFilter = THREE.LinearFilter;
      texture.anisotropy = 4;
      textures.push(texture);
    });
  } catch (error) {
    group.removeFromParent();
    textures.forEach(texture => texture.dispose());
    throw new Error(`The orb photographs could not be loaded: ${error.message}`);
  }

  // A translucent, lightly copper-coloured volume lets the photographs remain
  // part of an energy sphere instead of becoming hard-edged picture cards.
  const hazeGeometry = new THREE.SphereGeometry(ORB_SETTINGS.radius, 48, 32);
  geometries.push(hazeGeometry);
  const hazeMaterial = new THREE.ShaderMaterial({
    uniforms: { ...shared, uOpacity: hazeOpacity },
    vertexShader: `
      uniform float uTime,uPulse;
      varying vec3 vPosition,vNormal,vView;
      void main(){
        vec3 p=position*uPulse;
        p*=1.+.015*sin(p.y*6.+uTime*2.)*sin(p.x*5.-uTime*1.4);
        vec4 view=modelViewMatrix*vec4(p,1.);
        vPosition=position;vNormal=normalMatrix*normal;vView=-view.xyz;
        gl_Position=projectionMatrix*view;
      }
    `,
    fragmentShader: `
      uniform float uTime,uOpacity;
      varying vec3 vPosition,vNormal,vView;
      ${noiseGLSL}
      void main(){
        vec3 p=vPosition;
        float a=uTime*1.4+p.y*1.3;
        p.xz=mat2(cos(a),-sin(a),sin(a),cos(a))*p.xz;
        float n=noise3(p*3.5+vec3(0.,-uTime*1.2,0.));
        float n2=noise3(p*7.8+vec3(uTime*.39,0.,uTime*.61));
        float rim=pow(1.-abs(dot(normalize(vNormal),normalize(vView))),2.2);
        float veil=smoothstep(.36,.76,n*.75+n2*.25);
        vec3 color=mix(vec3(.065,.019,.003),vec3(.64,.31,.085),veil);
        float alpha=(.24+rim*.14+veil*.18)*uOpacity;
        gl_FragColor=vec4(color,alpha);
        #include <colorspace_fragment>
      }
    `,
    transparent: true, depthWrite: false, side: THREE.FrontSide, toneMapped: false
  });
  materials.push(hazeMaterial);
  const haze = new THREE.Mesh(hazeGeometry, hazeMaterial);
  haze.name = 'translucent-orb-volume';haze.renderOrder = 2;
  group.add(haze);

  const photoGeometry = new THREE.PlaneGeometry(2.18, 2.18);
  geometries.push(photoGeometry);
  const photoMeshes = textures.map((texture, index) => {
    const framing = PHOTO_FRAMING[index];
    const crop = framing.aspect < 1 ? new THREE.Vector2(1, framing.aspect) : new THREE.Vector2(1 / framing.aspect, 1);
    const uniforms = {
      uPhoto: { value: texture }, uWeight: { value: 0 },
      uTime: shared.uTime, uLife: { value: 0 },
      uCrop: { value: crop }, uCenter: { value: new THREE.Vector2(...framing.center) }
    };
    const material = new THREE.ShaderMaterial({
      uniforms,
      vertexShader: `
        uniform float uLife;
        varying vec2 vUv;
        void main(){
          vUv=uv;
          vec3 p=position;
          // Keep faces undistorted; only a slight photographic breathing zoom.
          p.xy*=.985+.025*uLife;
          gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);
        }
      `,
      fragmentShader: `
        uniform sampler2D uPhoto;
        uniform float uWeight,uTime,uLife;
        uniform vec2 uCrop,uCenter;
        varying vec2 vUv;
        ${noiseGLSL}
        void main(){
          vec2 q=(vUv-.5)*2.;
          float radial=length(q);
          float peripheral=smoothstep(.45,.95,radial);
          float flow=noise3(vec3(q*4.1,uTime*.7));
          // The feather develops in the circulating energy; the face is stable.
          float edge=.99+(.055*(flow-.5))*peripheral;
          float mask=1.-smoothstep(.70,edge,radial);
          if(mask*uWeight<.002)discard;
          vec2 uv=(vUv-.5)*uCrop+uCenter;
          vec3 color=texture2D(uPhoto,clamp(uv,vec2(.001),vec2(.999))).rgb;
          float luminance=dot(color,vec3(.2126,.7152,.0722));
          color=mix(color,vec3(luminance)*vec3(1.10,1.015,.89),.18);
          color=mix(color,vec3(.94,.79,.49),peripheral*.07*(.5+.5*flow));
          gl_FragColor=vec4(color,mask*uWeight);
          #include <colorspace_fragment>
        }
      `,
      transparent: true, depthWrite: false, depthTest: false, toneMapped: false
    });
    materials.push(material);
    const mesh = new THREE.Mesh(photoGeometry, material);
    mesh.name = `orb-memory-photograph-${index + 1}`;
    mesh.position.z = .42 + index * .001;
    mesh.renderOrder = 5;mesh.frustumCulled = false;
    group.add(mesh);
    return mesh;
  });

  // Flowing ribbons follow different curved paths on and just inside the
  // sphere. They are tapered, variable-width wisps rather than rigid rings.
  const segments = 176;
  const position = new Float32Array((segments + 1) * 2 * ORB_SETTINGS.filaments * 3);
  const coordinates = new Float32Array((segments + 1) * 2 * ORB_SETTINGS.filaments * 3);
  const logoTargets = new Float32Array(position.length);
  const logoNextTargets = new Float32Array(position.length);
  const indices = new Uint32Array(segments * 6 * ORB_SETTINGS.filaments);
  let cursor = 0, offset = 0;
  for (let strand = 0; strand < ORB_SETTINGS.filaments; strand++) {
    const base = strand * (segments + 1) * 2;
    const { contour, part } = strandTargets[strand];
    for (let step = 0; step <= segments; step++) {
      const target = sampleContour(contour, (part + step / segments) / contour.strands);
      const nextTarget = sampleContour(contour, (part + Math.min(1, (step + 1) / segments)) / contour.strands);
      // At the final vertex use the previous segment's forward direction.
      if (step === segments) {
        const previous = sampleContour(contour, (part + (step - 1) / segments) / contour.strands);
        nextTarget[0] = target[0] + (target[0] - previous[0]);
        nextTarget[1] = target[1] + (target[1] - previous[1]);
      }
      for (const side of [-1, 1]) {
        coordinates.set([step / segments, side, strand], cursor);
        logoTargets.set(target, cursor);logoNextTargets.set(nextTarget, cursor);cursor += 3;
      }
      if (step < segments) {
        const a = base + step * 2;
        indices.set([a, a + 1, a + 2, a + 1, a + 3, a + 2], offset);offset += 6;
      }
    }
  }
  const filamentGeometry = new THREE.BufferGeometry();
  filamentGeometry.setAttribute('position', new THREE.BufferAttribute(position, 3));
  filamentGeometry.setAttribute('aFlow', new THREE.BufferAttribute(coordinates, 3));
  filamentGeometry.setAttribute('aLogo', new THREE.BufferAttribute(logoTargets, 3));
  filamentGeometry.setAttribute('aLogoNext', new THREE.BufferAttribute(logoNextTargets, 3));
  filamentGeometry.setIndex(new THREE.BufferAttribute(indices, 1));
  geometries.push(filamentGeometry);
  const filamentMaterial = new THREE.ShaderMaterial({
    uniforms: shared,
    vertexShader: `
      attribute vec3 aFlow,aLogo,aLogoNext;
      uniform float uTime,uPulse,uMorph;
      varying float vSide,vLife,vSeed,vFront,vRim,vProgress;
      const float TAU=6.28318530718;
      mat3 rotationX(float a){float c=cos(a),s=sin(a);return mat3(1,0,0,0,c,s,0,-s,c);}
      mat3 rotationY(float a){float c=cos(a),s=sin(a);return mat3(c,0,-s,0,1,0,s,0,c);}
      mat3 rotationZ(float a){float c=cos(a),s=sin(a);return mat3(c,s,0,-s,c,0,0,0,1);}
      vec3 stream(float u,float seed){
        float phase=uTime*(1.75+fract(seed*.37)*1.45)+seed*2.399963;
        float angle=u*(4.5+fract(seed*.174)*3.3)+phase;
        // Each stream folds inward and unfurls again. The path itself changes
        // as energy circulates, rather than spinning an undeformed wire ring.
        float fold=.5+.5*sin(u*6.1+seed*.73-uTime*1.83);
        float r=1.35*(.40+.47*fold+.025*sin(angle*2.3+seed+uTime*1.39));
        float bend=.44*sin(angle*1.6+seed-uTime*.94)+.24*sin(angle*2.8-uTime*1.72);
        vec3 p=vec3(cos(angle)*cos(bend),sin(angle)*cos(bend),sin(bend))*r;
        p=rotationX(seed*1.317+sin(uTime*1.18+seed)*.42)*rotationY(seed*.71-uTime*.43)*rotationZ(seed*.53)*p;
        return p*uPulse;
      }
      void main(){
        float u=aFlow.x,seed=aFlow.z;
        vec3 p=mix(stream(u,seed),aLogo,uMorph);
        vec3 next=mix(stream(u+1./176.,seed),aLogoNext,uMorph);
        vec4 view=modelViewMatrix*vec4(p,1.);
        vec3 tangent=(modelViewMatrix*vec4(next-p,0.)).xyz;
        vec2 perpendicular=normalize(vec2(-tangent.y,tangent.x)+vec2(.00001));
        float taper=mix(pow(max(0.,sin(u*3.14159265)),.78),1.,uMorph);
        float broad=1.-step(1.,mod(seed,3.));
        float width=mix(.029+fract(seed*.319)*.032,.095+fract(seed*.319)*.075,broad)*taper;
        width*=.71+.19*sin(u*13.+seed*3.+uTime*4.1)+.10*sin(u*29.-uTime*3.6);
        width=mix(width,mix(.016,.035,broad),uMorph);
        view.xy+=perpendicular*aFlow.y*width;
        vSide=aFlow.y;vLife=taper;vSeed=seed;
        vFront=mix(smoothstep(-.35,.75,p.z),1.,uMorph);
        vRim=smoothstep(.24,1.05,length(p.xy));
        vProgress=u;
        gl_Position=projectionMatrix*view;
      }
    `,
    fragmentShader: `
      uniform float uTime,uOpacity,uPower,uMorph;
      varying float vSide,vLife,vSeed,vFront,vRim,vProgress;
      void main(){
        float side=abs(vSide);
        float broad=1.-step(1.,mod(vSeed,3.));
        float glow=pow(max(0.,1.-side),1.9);
        float core=1.-smoothstep(.0,mix(.30,.70,broad),side);
        float textureFlow=.83+.11*sin(vProgress*27.+vSeed-uTime*4.3)+.06*sin(vProgress*51.+uTime*3.8);
        float brightness=(.83+.17*sin(vSeed*2.1+uTime*3.8))*(.82+.30*uPower);
        vec3 copper=vec3(.17,.035,.005);
        vec3 gold=vec3(.82,.40,.075);
        vec3 warmWhite=vec3(1.,.95,.79);
        vec3 color=mix(copper,gold,glow*.69);
        color=mix(color,warmWhite,core*mix(.70,.82,broad));
        color=mix(color,vec3(.43,.20,.055),smoothstep(.55,1.,uMorph)*.55);
        float alpha=(glow*.95+core*.32)*vLife*brightness*textureFlow;
        // Rear wisps stay quiet; the flowing front catches warm highlights.
        alpha*=mix(.56,1.,vFront)*mix(.68,1.,vRim)*uOpacity;
        gl_FragColor=vec4(color,min(1.,alpha));
        #include <colorspace_fragment>
      }
    `,
    transparent: true, depthWrite: false, depthTest: false,
    side: THREE.DoubleSide, toneMapped: false
  });
  materials.push(filamentMaterial);
  const filaments = new THREE.Mesh(filamentGeometry, filamentMaterial);
  filaments.name = 'internally-revolving-energy-wisps';
  filaments.frustumCulled = false;filaments.renderOrder = 6;
  group.add(filaments);

  function update({ time = 0, introSeconds = 0, reduced = false } = {}) {
    if (disposed) return;
    lastTime = Number.isFinite(time) ? time : lastTime;
    lastIntro = Number.isFinite(introSeconds) ? Math.max(0, introSeconds) : ORB_SETTINGS.completeAt;
    lastClock = energyClock(lastIntro);
    lastMorph = morphProgress(lastIntro);
    shared.uTime.value = lastClock;
    shared.uMorph.value = lastMorph;
    // The ribbons remain one visible body as their actual vertices settle
    // onto the logo. Only the final handover softens their energy highlights.
    lastOpacity = reduced ? 0 : smooth(.29, ORB_SETTINGS.formedAt, lastIntro) * (1 - smooth(.90, 1, lastMorph));
    shared.uOpacity.value = lastOpacity;
    const photoTime = lastIntro - ORB_SETTINGS.formedAt;
    shared.uPulse.value = energyPulse(lastClock);
    shared.uPower.value = clamp((1.017 - shared.uPulse.value) / .174);
    hazeOpacity.value = reduced ? 0 : smooth(.29, ORB_SETTINGS.formedAt, lastIntro) * (1 - smooth(.03, .53, lastMorph));
    group.scale.setScalar(1);
    group.visible = !reduced && lastIntro < ORB_SETTINGS.completeAt && lastOpacity > .001;
    activePhotos = [];
    photoWeights = photoMeshes.map((mesh, index) => {
      const duration = ORB_SETTINGS.photoSeconds / 6;
      const center = (index + .5) * duration;
      const offset = Math.abs(photoTime - center);
      const window = 1 - smooth(duration * .20, duration * .67, offset);
      const timelineGate = smooth(0, .12, photoTime) * (1 - smooth(3.84, 4, photoTime));
      const weight = reduced ? 0 : window * timelineGate * ORB_SETTINGS.photoPeakOpacity * (1 - shared.uPower.value * .08);
      mesh.material.uniforms.uWeight.value = weight;
      mesh.material.uniforms.uLife.value = clamp((photoTime - index * duration + .1) / (duration + .2));
      // Keep zero-alpha meshes present for compileAsync's shader prewarm.
      if (weight > .05) activePhotos.push(index + 1);
      return weight;
    });
  }
  function dispose() {
    if (disposed) return;
    disposed = true;group.removeFromParent();
    geometries.forEach(geometry => geometry.dispose());
    materials.forEach(material => material.dispose());
    textures.forEach(texture => texture.dispose());
  }
  return {
    update, dispose,
    prewarm(renderer){if(!disposed)textures.forEach(texture=>renderer.initTexture(texture));},
    inspect() {
      return { disposed, loaded: textures.length === 6, visible: group.visible,
        time: lastTime, introSeconds: lastIntro, opacity: lastOpacity,
        morph: lastMorph, energyClock: lastClock, pulse: shared.uPulse.value,
        morphsActualGeometry: true, logoContours: contours.length,
        targetVertexCount: logoTargets.length / 3,
        radius: ORB_SETTINGS.radius, photoSeconds: ORB_SETTINGS.photoSeconds,
        photoCount: textures.length, activePhotos: [...activePhotos],
        photoWeights: photoWeights.map(value => Number(value.toFixed(4))),
        filamentCount: ORB_SETTINGS.filaments, ownAnimationLoop: false };
    }
  };
}
