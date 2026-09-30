/* A brief, reusable pigment transition. The moving object is the original
 * Three.js chapter panel; this shader takes over only once it fills the lens. */
window.createCirsChapterWash = ({ THREE: T, canvas }) => {
  let renderer, scene, material, texture, plane;
  let renderWidth = 0, renderHeight = 0;
  const camera = new T.OrthographicCamera(-1, 1, 1, -1, 0, 2);
  const uniforms = {
    uPainting: { value: null },
    uTime: { value: 0 },
    uDissolve: { value: -.25 },
    uDistortion: { value: 0 },
    uAspect: { value: 1.6 }
  };
  try {
    renderer = new T.WebGLRenderer({ canvas, alpha: true, antialias: false, powerPreference: 'high-performance', premultipliedAlpha: false });
    // The wash is moving pigment, so full device resolution adds GPU work
    // without adding visible detail during its short flight.
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1));
    renderer.setClearColor(0x000000, 0);
    scene = new T.Scene();
    material = new T.ShaderMaterial({
      uniforms, transparent: true, depthWrite: false, depthTest: false,
      vertexShader: `varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position.xy,0.0,1.0);}`,
      fragmentShader: `
        precision highp float;
        varying vec2 vUv;
        uniform sampler2D uPainting;
        uniform float uTime, uDissolve, uDistortion, uAspect;
        float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453123);}
        float noise(vec2 p){
          vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
          return mix(mix(hash(i),hash(i+vec2(1.0,0.0)),f.x),mix(hash(i+vec2(0.0,1.0)),hash(i+1.0),f.x),f.y);
        }
        float fbm(vec2 p){return .52*noise(p)+.29*noise(p*2.03)+.19*noise(p*4.09);}
        void main(){
          vec2 center=vUv-.5;
          float r=length(center);
          float ang=atan(center.y,center.x);
          vec2 field=center*vec2(6.2,5.2);
          float wet=fbm(field+vec2(uTime*.09,-uTime*.07));
          float whorl=sin(r*25.0-ang*5.0-uTime*2.0+wet*3.2);
          vec2 tangent=vec2(-center.y,center.x)/(r+.03);
          vec2 pull=tangent*(.012*whorl+.022*(wet-.5));
          pull+=normalize(center+vec2(.001))*(.017*sin(r*31.0-uTime*2.4+wet*4.0));
          vec2 uv=vUv+pull*uDistortion*(.48+.52*exp(-r*1.5));
          float viewportAspect=max(.1,uAspect);
          float sourceAspect=1.6;
          if(viewportAspect>sourceAspect) uv.y=(uv.y-.5)*sourceAspect/viewportAspect+.5;
          else uv.x=(uv.x-.5)*viewportAspect/sourceAspect+.5;
          uv=clamp(uv,vec2(.002),vec2(.998));
          vec4 ink=texture2D(uPainting,uv);
          float ragged=r*1.36+.17*fbm(field*1.25+wet*2.0)+.045*sin(ang*13.0+wet*8.0);
          float dissolve=1.0-smoothstep(uDissolve-.055,uDissolve+.075,ragged);
          // The open edge catches warm pigment before it feathers away.
          float edge=exp(-abs(ragged-uDissolve)*18.0)*clamp(uDistortion,0.0,1.0);
          ink.rgb=mix(ink.rgb,ink.rgb*vec3(1.08,.91,.72),edge*.42);
          gl_FragColor=vec4(ink.rgb,ink.a*(1.0-dissolve));
        }
      `
    });
    plane = new T.Mesh(new T.PlaneGeometry(2, 2), material);
    scene.add(plane);
  } catch (error) {
    console.warn('Pigment shader unavailable; the chapter remains accessible.', error);
    return { available: false, setPainting() {}, render() {}, resize() {}, prewarm() {}, dispose() {} };
  }
  function resize() {
    const width = Math.max(1, innerWidth), height = Math.max(1, innerHeight);
    if(width !== renderWidth || height !== renderHeight) {
      renderer.setSize(width, height, false);
      renderWidth = width; renderHeight = height;
    }
    uniforms.uAspect.value = width / height;
  }
  function setPainting(image) {
    if (!texture) {
      texture = new T.CanvasTexture(image);
      texture.encoding = T.sRGBEncoding;
      texture.minFilter = T.LinearFilter;
      texture.magFilter = T.LinearFilter;
    } else if (texture.image !== image) {
      texture.image = image;
      texture.needsUpdate = true;
    }
    uniforms.uPainting.value = texture;
    resize();
  }
  function prewarm() {
    // Compile and upload a tiny placeholder while the visitor is looking at
    // the spiral, so the first panel click does not pay the shader setup cost.
    const placeholder = new T.DataTexture(new Uint8Array([255, 248, 235, 255]), 1, 1, T.RGBAFormat);
    placeholder.needsUpdate = true;
    uniforms.uPainting.value = placeholder;
    renderer.compile(scene, camera);
    renderer.render(scene, camera);
    uniforms.uPainting.value = texture;
    placeholder.dispose();
  }
  function render({ dissolve = -.25, distortion = 0, time = 0 } = {}) {
    if (!texture) return;
    uniforms.uDissolve.value = dissolve;
    uniforms.uDistortion.value = distortion;
    uniforms.uTime.value = time;
    renderer.render(scene, camera);
  }
  resize();
  return { available: true, setPainting, render, resize, prewarm, dispose() { texture?.dispose(); plane.geometry.dispose(); material.dispose(); renderer.dispose(); } };
};
