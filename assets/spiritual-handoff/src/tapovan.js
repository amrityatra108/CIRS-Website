import * as THREE from '../vendor/three.module.js';

// This chapter has one reversible scroll clock. The opening rush reaches the
// summit before any stone or phrase appears; the remaining scroll descends.
const section = document.querySelector('#tapovan-journey');
const stage = section.querySelector('.tapovan-sticky');
const canvas = section.querySelector('#tapovan-steps');
const video = section.querySelector('.tapovan-video');
const veil = section.querySelector('.tapovan-entry-veil');
const beats = [...section.querySelectorAll('.tapovan-beat')];
const number = section.querySelector('#tapovan-number');
const counter = section.querySelector('.tapovan-progress');
const scrollHint = section.querySelector('.tapovan-scroll-hint');
const reducedList = section.querySelector('.tapovan-reduced-list');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const mobile = matchMedia('(max-width: 700px)');
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const mix = (a, b, t) => a + (b - a) * t;
const smooth = (a, b, x) => {
  const t = clamp((x - a) / Math.max(.00001, b - a));
  return t * t * (3 - 2 * t);
};
const hash = n => {
  const value = Math.sin(n * 127.1 + 29.7) * 43758.5453;
  return value - Math.floor(value);
};
const SETTINGS = Object.freeze({
  arrivalEnd: .135,
  firstStones: .145,
  formationEnd: .255,
  wordsStart: .29,
  descentEnd: .965,
  end: .99,
  peakTime: 2.45,
  formationTime: 3.55,
  videoEnd: 15.05,
  stoneCount: 92,
  angle: .291,
  radius: 3.18,
  drop: .287,
  topY: 10.05
});

let renderer, scene, camera, maskPlane, maskCanvas, maskContext, maskTexture;
let profiles = null, bundles = null, stoneSteps = [], stepMaterials = [];
let raf = 0, previousFrame = 0, progress = 0, videoTarget = 0;
let visible = false, disposed = false, reduced = motion.matches;
let loadPromise = null, renderError = null, seeking = false, maskTime = -1;
let activeStones = 0, formedStones = 0;
const listeners = [];
function listen(target, name, fn, options) {
  target.addEventListener(name, fn, options);
  listeners.push(() => target.removeEventListener(name, fn, options));
}

function readProgress() {
  const rect = section.getBoundingClientRect();
  return clamp(-rect.top / Math.max(1, rect.height - innerHeight));
}

function phaseAt(p) {
  if (p < SETTINGS.arrivalEnd) return 'arrival';
  if (p < SETTINGS.formationEnd) return 'forming';
  return 'descent';
}

function timeAt(p) {
  if (p <= SETTINGS.arrivalEnd) {
    const t = clamp(p / SETTINGS.arrivalEnd);
    return mix(.04, SETTINGS.peakTime, Math.pow(t, .78));
  }
  if (p <= SETTINGS.formationEnd) {
    return mix(SETTINGS.peakTime, SETTINGS.formationTime,
      (p - SETTINGS.arrivalEnd) / (SETTINGS.formationEnd - SETTINGS.arrivalEnd));
  }
  return mix(SETTINGS.formationTime, SETTINGS.videoEnd,
    smooth(SETTINGS.formationEnd, SETTINGS.end, p));
}

function syncVideo(time) {
  videoTarget = time;
  if (reduced || !video.readyState || seeking || disposed) return;
  if (Math.abs(video.currentTime - time) < .055) return;
  try {
    seeking = true;
    video.currentTime = clamp(time, 0, Math.max(.1, (video.duration || 15.14) - .04));
  } catch (_) {
    seeking = false;
  }
}

function updateCopy(p) {
  const wordsActive = p >= SETTINGS.wordsStart;
  const chapter = clamp((p - SETTINGS.wordsStart) /
    (SETTINGS.descentEnd - SETTINGS.wordsStart) * beats.length, 0, 4.9999);
  const current = Math.floor(chapter);
  const phase = chapter - current;
  number.textContent = String(current + 1).padStart(2, '0');
  counter.style.opacity = wordsActive ? String(smooth(SETTINGS.wordsStart,
    SETTINGS.wordsStart + .025, p)) : '0';
  beats.forEach((beat, i) => {
    let opacity = 0, y = 22, blur = 6;
    if (wordsActive && i === current) {
      const enter = smooth(0, .17, phase);
      const exit = i === beats.length - 1 ? 1 : 1 - smooth(.78, 1, phase);
      opacity = enter * exit;
      y = 22 * (1 - enter) - 13 * (1 - exit);
      blur = 6 * (1 - enter) + 2.5 * (1 - exit);
    }
    beat.style.opacity = opacity.toFixed(3);
    beat.style.transform = 'translate3d(0,' + y.toFixed(1) + 'px,0)';
    beat.style.filter = 'blur(' + blur.toFixed(1) + 'px)';
  });
  veil.style.opacity = String(.50 * (1 - smooth(.003, .045, p)));
  scrollHint.style.opacity = String(.65 * (1 - smooth(.11, .22, p)));
  section.dataset.phase = phaseAt(p);
  section.dataset.step = wordsActive ? String(current + 1) : '0';
}

async function loadStones() {
  const base = new URL('../assets/stones/', import.meta.url);
  const manifestResponse = await fetch(new URL('manifest.json', base));
  if (!manifestResponse.ok) throw new Error('Stone manifest unavailable');
  const manifest = await manifestResponse.json();
  if (manifest.format !== 'crossroads-stones-v1' || manifest.stones.length !== 4) {
    throw new Error('Unexpected stone bundle format');
  }
  const loader = new THREE.TextureLoader();
  return Promise.all(manifest.stones.map(async entry => {
    const meshResponse = await fetch(new URL(entry.mesh, base));
    if (!meshResponse.ok) throw new Error('Stone mesh unavailable: ' + entry.id);
    const buffer = await meshResponse.arrayBuffer();
    const field = name => {
      const spec = entry.fields[name];
      return new THREE.BufferAttribute(new Float32Array(buffer, spec.offset,
        spec.count * spec.itemSize), spec.itemSize);
    };
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', field('position'));
    geometry.setAttribute('normal', field('normal'));
    geometry.setAttribute('uv', field('uv'));
    const index = entry.fields.index;
    geometry.setIndex(new THREE.BufferAttribute(new Uint32Array(buffer,
      index.offset, index.count), 1));
    entry.groups.forEach(group => geometry.addGroup(group.start,
      group.count, group.materialIndex));
    geometry.computeBoundingSphere();
    const textures = {};
    await Promise.all(Object.entries(entry.textures).map(async ([key, file]) => {
      const texture = await loader.loadAsync(new URL(file, base).href);
      texture.flipY = false;
      texture.anisotropy = 4;
      texture.wrapS = THREE.RepeatWrapping;
      texture.wrapT = THREE.ClampToEdgeWrapping;
      if (key.endsWith('Color')) texture.colorSpace = THREE.SRGBColorSpace;
      textures[key] = texture;
    }));
    const props = { roughness: .96, metalness: 0,
      normalScale: new THREE.Vector2(.55, .55),
      transparent: true, depthWrite: true, side: THREE.DoubleSide };
    const materials = [
      new THREE.MeshStandardMaterial({ ...props, map: textures.topColor,
        normalMap: textures.topNormal }),
      new THREE.MeshStandardMaterial({ ...props, map: textures.sideColor,
        normalMap: textures.sideNormal })
    ];
    return { entry, geometry, materials, textures };
  }));
}

async function prepare() {
  if (loadPromise || disposed || reduced) return loadPromise;
  loadPromise = Promise.all([
    loadStones(),
    fetch(new URL('../assets/mountain-mattes/mountain-foreground-profiles.json',
      import.meta.url)).then(response => response.ok ? response.json() : null)
  ]).then(([models, matte]) => {
    if (disposed) return;
    bundles = models;
    profiles = matte;
    createScene();
    requestDraw();
  }).catch(error => {
    renderError = String(error?.message || error);
    stage.classList.add('is-reduced');
    reducedList.hidden = false;
    console.error('Tapovan descent:', error);
  });
  return loadPromise;
}

function makeMaskPlane() {
  if (!profiles?.keyframes?.length) return;
  maskCanvas = document.createElement('canvas');
  maskContext = maskCanvas.getContext('2d', { willReadFrequently: false });
  maskTexture = new THREE.CanvasTexture(maskCanvas);
  maskTexture.minFilter = THREE.LinearFilter;
  maskTexture.magFilter = THREE.LinearFilter;
  maskTexture.generateMipmaps = false;
  const material = new THREE.MeshBasicMaterial({
    color: 0xffffff, alphaMap: maskTexture, alphaTest: .46,
    colorWrite: false, depthWrite: true, depthTest: true,
    side: THREE.DoubleSide
  });
  maskPlane = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), material);
  maskPlane.position.set(0, 0, -12.2);
  maskPlane.renderOrder = -100;
  maskPlane.frustumCulled = false;
  camera.add(maskPlane);
  scene.add(camera);
}

function chooseType(i, previous) {
  let candidate = Math.floor(hash(i * 17 + Math.floor(i / 4) * 23) * 4);
  if (candidate === previous) candidate = (candidate + 1 + (i % 2)) % 4;
  return candidate;
}

function createScene() {
  if (renderer || reduced || disposed || !bundles) return;
  renderer = new THREE.WebGLRenderer({
    canvas, alpha: true, antialias: true, powerPreference: 'high-performance'
  });
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.14;
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(43, 1, .1, 80);
  scene.add(new THREE.AmbientLight(0xffe9c9, 1.45));
  const sun = new THREE.DirectionalLight(0xffd6a1, 2.4);
  sun.position.set(-7, 8, 6);
  scene.add(sun);
  const sky = new THREE.DirectionalLight(0xd4e2e9, .55);
  sky.position.set(5, 2, -4);
  scene.add(sky);
  makeMaskPlane();
  let previousType = -1;
  for (let i = 0; i < SETTINGS.stoneCount; i++) {
    const type = chooseType(i, previousType);
    previousType = type;
    const bundle = bundles[type];
    const materials = bundle.materials.map(material => material.clone());
    stepMaterials.push(...materials);
    const stone = new THREE.Mesh(bundle.geometry, materials);
    const angle = i * SETTINGS.angle + .15;
    const scale = .72 * (.93 + hash(i * 9 + 2) * .15);
    const y = SETTINGS.topY - i * SETTINGS.drop -
      bundle.entry.bounds.max[1] * scale;
    const radius = SETTINGS.radius + .72 * i / (SETTINGS.stoneCount - 1);
    const x = .58 + Math.sin(angle) * radius;
    const z = Math.cos(angle) * radius;
    stone.position.set(x, y, z);
    stone.rotation.set((hash(i * 5 + 4) - .5) * .065,
      angle + Math.PI * .5 + (hash(i * 3 + 7) - .5) * .12,
      (hash(i * 11 + 6) - .5) * .06);
    stone.userData = { index: i, scale, x, y, z, type };
    stone.scale.setScalar(.001);
    stone.visible = false;
    stone.renderOrder = 1;
    scene.add(stone);
    stoneSteps.push(stone);
  }
  resize();
}

function resize() {
  if (!renderer || !camera) return;
  const w = Math.max(1, stage.clientWidth);
  const h = Math.max(1, stage.clientHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, mobile.matches ? 1.25 : 1.6));
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.fov = mobile.matches ? 49 : 43;
  camera.updateProjectionMatrix();
  if (maskPlane) {
    maskPlane.position.z = mobile.matches ? -14.0 : -12.2;
    const distance = -maskPlane.position.z;
    const height = 2 * distance * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    maskPlane.scale.set(height * camera.aspect, height, 1);
    maskCanvas.width = 512;
    maskCanvas.height = Math.max(256, Math.round(512 * h / w));
    maskTime = -1;
  }
  requestDraw();
}

function updateMask(time) {
  if (!maskPlane || !maskContext || !profiles || Math.abs(time - maskTime) < .025) return;
  maskTime = time;
  const keyframes = profiles.keyframes;
  let next = keyframes.findIndex(frame => frame.time >= time);
  if (next < 0) next = keyframes.length - 1;
  const before = keyframes[Math.max(0, next - 1)];
  const after = keyframes[next];
  const blend = before === after ? 1 : clamp((time - before.time) /
    Math.max(.0001, after.time - before.time));
  const w = maskCanvas.width, h = maskCanvas.height;
  const sw = profiles.sourceWidth || 1920, sh = profiles.sourceHeight || 1080;
  const stageW = Math.max(1, stage.clientWidth), stageH = Math.max(1, stage.clientHeight);
  const cover = Math.max(stageW / sw, stageH / sh);
  const drawW = sw * cover, drawH = sh * cover;
  const positionX = mobile.matches ? .62 : .58;
  const cropX = (drawW - stageW) * positionX;
  const cropY = (drawH - stageH) * .5;
  maskContext.clearRect(0, 0, w, h);
  maskContext.fillStyle = '#fff';
  maskContext.beginPath();
  const ridgeA = before.ridgeY, ridgeB = after.ridgeY;
  const sampleX = profiles.sampleX;
  for (let i = 0; i < sampleX.length; i++) {
    const x = (sampleX[i] * drawW - cropX) / stageW * w;
    const ridge = mix(ridgeA[i], ridgeB[i], blend);
    const y = (ridge * drawH - cropY) / stageH * h;
    if (i === 0) maskContext.moveTo(x, y);
    else maskContext.lineTo(x, y);
  }
  maskContext.lineTo((drawW - cropX) / stageW * w, h + 2);
  maskContext.lineTo(-cropX / stageW * w, h + 2);
  maskContext.closePath();
  maskContext.fill();
  maskTexture.needsUpdate = true;
}

function birthAt(i) {
  if (i < 17) return SETTINGS.firstStones +
    i / 17 * (SETTINGS.formationEnd - SETTINGS.firstStones);
  return SETTINGS.formationEnd + (i - 17) /
    (SETTINGS.stoneCount - 17) * .665;
}

function updateStones(p) {
  if (!camera || !stoneSteps.length) return;
  const travel = smooth(SETTINGS.formationEnd, SETTINGS.descentEnd, p);
  const focus = travel * (SETTINGS.stoneCount - 5);
  const focusY = SETTINGS.topY - focus * SETTINGS.drop;
  const sway = Math.sin(travel * Math.PI * 3.2) * .82;
  camera.position.set(.58 + sway, focusY + 3.65, mobile.matches ? 14.0 : 11.7);
  const lookOffset = mix(-.60, .56, smooth(.18, .36, p));
  camera.lookAt(.58 + sway * .30, focusY + lookOffset, 0);
  camera.updateMatrixWorld();
  formedStones = 0;
  activeStones = 0;
  for (const stone of stoneSteps) {
    const i = stone.userData.index;
    const birth = birthAt(i);
    const emerge = smooth(birth, birth + .026, p);
    if (emerge > .99) formedStones++;
    const distance = i - focus;
    const windowed = distance > (mobile.matches ? -10 : -14) &&
      distance < (mobile.matches ? 14 : 20);
    stone.visible = emerge > .015 && windowed;
    if (!stone.visible) continue;
    activeStones++;
    const edge = distance < 0 ?
      1 - smooth(mobile.matches ? 7 : 10, mobile.matches ? 10 : 14, -distance) :
      1 - smooth(mobile.matches ? 10 : 15, mobile.matches ? 14 : 20, distance);
    const opacity = clamp(emerge * edge, .012, 1);
    stone.material.forEach(material => { material.opacity = opacity; });
    const scale = stone.userData.scale * (mobile.matches ? .82 : 1) *
      mix(.12, 1, emerge);
    stone.scale.setScalar(scale);
    stone.position.x = mobile.matches ?
      .58 + (stone.userData.x - .58) * .56 : stone.userData.x;
    stone.position.z = mobile.matches ?
      stone.userData.z * .67 : stone.userData.z;
    stone.position.y = stone.userData.y + (1 - emerge) * .37;
  }
}

function draw(stamp) {
  raf = 0;
  if (disposed || reduced || !visible) return;
  const dt = previousFrame ? Math.min(.05, (stamp - previousFrame) / 1000) : 1 / 60;
  previousFrame = stamp;
  const target = readProgress();
  progress += (target - progress) * (1 - Math.exp(-dt * 13));
  if (Math.abs(target - progress) > .00035) requestDraw();
  const videoTime = timeAt(progress);
  syncVideo(videoTime);
  updateCopy(progress);
  if (!renderer) return;
  updateMask(videoTime);
  updateStones(progress);
  renderer.render(scene, camera);
}

function requestDraw() {
  if (!raf && !disposed && visible && !reduced) raf = requestAnimationFrame(draw);
}

function updateMotion() {
  reduced = motion.matches;
  stage.classList.toggle('is-reduced', reduced);
  reducedList.hidden = !reduced;
  video.pause();
  if (reduced) {
    veil.style.opacity = '0';
    cancelAnimationFrame(raf);
    raf = 0;
  } else if (visible) {
    if (bundles && !renderer) createScene();
    else prepare();
    requestDraw();
  }
}

const observer = new IntersectionObserver(entries => {
  visible = entries[0].isIntersecting;
  if (visible && !reduced) {
    prepare();
    requestDraw();
  } else {
    cancelAnimationFrame(raf);
    raf = 0;
    previousFrame = 0;
    video.pause();
  }
}, { rootMargin: '110% 0px' });
observer.observe(section);
listen(window, 'scroll', requestDraw, { passive: true });
listen(window, 'resize', resize, { passive: true });
listen(video, 'loadedmetadata', () => { video.pause(); syncVideo(videoTarget); });
listen(video, 'seeked', () => {
  seeking = false;
  if (visible && !reduced && Math.abs(video.currentTime - videoTarget) > .085) {
    syncVideo(videoTarget);
  }
});
listen(document, 'visibilitychange', () => {
  video.pause();
  if (!document.hidden) requestDraw();
});
listen(motion, 'change', updateMotion);
updateMotion();

window.__tapovan = {
  inspect: () => ({
    progress, phase: phaseAt(progress), videoTarget,
    videoTime: video.currentTime, videoPaused: video.paused,
    formedStones, activeStones, stoneCount: stoneSteps.length,
    stoneTypes: [...new Set(stoneSteps.map(step => step.userData.type))].length,
    maskLoaded: Boolean(profiles), maskTime,
    activeStep: section.dataset.step || '0',
    reduced, visible, rendererReady: Boolean(renderer), renderError,
    scrollHeight: section.getBoundingClientRect().height
  }),
  destroy: () => {
    if (disposed) return;
    disposed = true;
    observer.disconnect();
    cancelAnimationFrame(raf);
    video.pause();
    listeners.forEach(off => off());
    stepMaterials.forEach(material => material.dispose());
    bundles?.forEach(bundle => {
      bundle.geometry.dispose();
      bundle.materials.forEach(material => material.dispose());
      Object.values(bundle.textures).forEach(texture => texture.dispose());
    });
    maskPlane?.geometry.dispose();
    maskPlane?.material.dispose();
    maskTexture?.dispose();
    renderer?.dispose();
  }
};
