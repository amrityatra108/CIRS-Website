/* ============================================================
   School History — the world the camera travels through
   ------------------------------------------------------------
   One Three.js scene, laid out along -z, and one authored camera
   path through it. history-journey.js owns the scroll and calls
   render(P, velocity) with P = 0 at the top of the page and P = k
   when moment k's text is held; P = 10 is the last photograph.

   Nothing here is decoration. Each element stands for something:
     contours      the land, before anything was built (1970s–1984);
                   gone by the silence of 1993
     three rings   one rupee at a time — thin, almost missed
     line drawing  1994–96: loose strokes that close into a building
                   as the school is made; the camera enters by its door
     96 · 11       the first school, set as type at different depths
     photographs   the archive's own exhibits, never tinted: they sit
                   nearer than the fog begins when they are read

   Technique, not code, from three MIT-licensed Codrops studies the
   owner supplied: depth-staggered image planes and a velocity term
   that only nudges (codrops-depth-gallery), and a WebGL plane handed
   over to the DOM image at the same rectangle (gsap-threejs-codrops).
   The third, cursor-shader-trail, is a pointer effect and is not used.
   ============================================================ */
import * as THREE from "../founder-opening/vendor/three.module.min.js";

const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, t) => a + (b - a) * t;
const smooth = (t) => { const c = clamp(t); return c * c * (3 - 2 * c); };
const win = (p, a, b, c, d) => smooth((p - a) / (b - a)) * (1 - smooth((p - c) / (d - c)));

const PLUM = 0x1e1626;      // --dark-deep, the page ground
const IVORY = "#EEE9DE";    // --rule-soft
const BRASS = 0xb8973f;     // a muted gold for the rings, never lettering

/* ---- the path ----------------------------------------------------------
   Control points: c = camera, l = where it looks. "s" marks a station,
   the pose for P = s. The rest are waypoints that take the camera round
   a photograph rather than through it. */
const PATH = [
  { s: 0,  c: [0.2, 0.9, 6.5],     l: [0, -0.55, -2] },
  { s: 1,  c: [0.05, 0.1, 0.4],    l: [0, 0.02, -4] },
  {        c: [-1.75, 0.25, -4.6], l: [-0.7, 0.15, -12.5] },
  { s: 2,  c: [-0.5, 0.2, -8.2],   l: [-0.4, 0.15, -12.5] },
  {        c: [-1.6, 0.45, -13.6], l: [-0.8, 0.3, -24] },
  { s: 3,  c: [-0.8, 0.45, -19],   l: [-0.6, 0.3, -27] },
  { s: 4,  c: [0.4, 0.32, -26.4],  l: [0.85, 0.2, -36] },
  { s: 5,  c: [0.85, 0.38, -31.5], l: [0.85, 0.5, -36] },
  {        c: [0.85, 0.0, -36.2],  l: [0.8, 0.05, -45] },
  { s: 6,  c: [0.5, 0.12, -41.8],  l: [0.7, 0.2, -46.5] },
  {        c: [2.2, 0.3, -48.2],   l: [1.6, 0.15, -57] },
  { s: 7,  c: [1.0, 0.25, -52.2],  l: [1.35, 0.1, -58] },
  {        c: [-1.0, 0.4, -58.6],  l: [1.0, 0.15, -69] },
  { s: 8,  c: [1.25, 0.3, -64.2],  l: [1.55, 0.15, -69.5] },
  {        c: [-1.3, 0.85, -71.2], l: [0.8, -0.6, -84] },
  { s: 9,  c: [0.85, 2.45, -79.9], l: [0.85, -1.3, -84.4] },
  {        c: [0.85, 1.55, -86.6], l: [0.85, 0.36, -96] },
  { s: 10, c: [0.85, 0.35, -91.1], l: [0.85, 0.35, -96] },
];
const N = 10;
// Fog near/far and how far right of centre the view is weighted (the
// text column is on the left), per station.
const FOG =   [[6, 22], [5, 20], [5, 18], [3.2, 11], [5, 18], [5.6, 22], [5.6, 25], [6.4, 28], [7, 32], [9, 42], [14, 60]];
const SHIFT = [0.07, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.12, 0.13, 0.11, 0];

/* ---- the exhibits -------------------------------------------------------
   h = height in world units; ry, rx = a small, deliberate angle. */
const PLATES = {
  "gurudev":          { k: 1,  at: [0, 0, -4],          h: 1.8 },
  "noc-1996":         { k: 6,  at: [0.5, 0.05, -46.5],  h: 1.7 },
  "kalam-2007":       { k: 7,  at: [1.0, 0.05, -56.8],  h: 1.55, ry: 0.06 },
  "sakshi-2008":      { k: 7,  at: [2.0, 0.15, -58.7],  h: 1.7, ry: -0.05 },
  "reflections-2010": { k: 7,  at: [3.0, 0.0, -60.7],   h: 1.5, ry: -0.14 },
  "vision-2012":      { k: 8,  at: [1.75, 0.15, -69.2], h: 1.5 },
  "brainfeed-2017":   { k: 8,  at: [3.15, 0.1, -72.2],  h: 1.45, ry: -0.1 },
  "report-2019":      { k: 8,  at: [4.2, -0.05, -75.0], h: 1.4, ry: -0.2 },
  "forest-air":       { k: 9,  at: [0.85, -1.4, -84.2], h: 2.3, rx: -1.0 },
  "campus-band":      { k: 10, at: [0.85, 0.35, -96],   h: 2.2 },
};

export function createWorld(canvas, sources, opts = {}) {
  let gl;
  try {
    gl = canvas.getContext("webgl2", { alpha: false, antialias: true, powerPreference: "high-performance",
                                        failIfMajorPerformanceCaveat: true });
  } catch (e) { gl = null; }
  if (!gl) return null;
  const renderer = new THREE.WebGLRenderer({ canvas, context: gl, antialias: true });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(PLUM, 1);
  const dpr = () => Math.min(window.devicePixelRatio || 1, 1.5);
  renderer.setPixelRatio(dpr());

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(PLUM, 6, 22);
  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 80);
  const dirty = () => { if (opts.onDirty) opts.onDirty(); };
  const disposables = [];
  const keep = (x) => (disposables.push(x), x);

  /* ---- the path, as two curves ---------------------------------------- */
  const camCurve = new THREE.CatmullRomCurve3(PATH.map((p) => new THREE.Vector3(...p.c)), false, "centripetal");
  const lookCurve = new THREE.CatmullRomCurve3(PATH.map((p) => new THREE.Vector3(...p.l)), false, "centripetal");
  const stationT = [];
  PATH.forEach((p, i) => { if (p.s !== undefined) stationT[p.s] = i / (PATH.length - 1); });

  // Between two stations the camera eases out of one pose and into the
  // next, with a slow drift through the held part so it never locks.
  function curveT(P) {
    const k = Math.min(N - 1, Math.floor(clamp(P, 0, N)));
    const f = clamp(P - k, 0, 1);
    const s = 0.08 * f + 0.92 * smooth((f - 0.1) / 0.8);
    return lerp(stationT[k], stationT[k + 1], s);
  }
  function station(P, table) {
    const k = Math.min(N - 1, Math.floor(clamp(P, 0, N)));
    const f = smooth(P - k);
    const a = table[k], b = table[k + 1];
    return Array.isArray(a) ? a.map((v, i) => lerp(v, b[i], f)) : lerp(a, b, f);
  }

  /* ---- the land: faint contours on the ground -------------------------- */
  const land = new THREE.Group();
  const landMat = keep(new THREE.LineBasicMaterial({ color: IVORY, transparent: true, opacity: 0.1, fog: true, depthWrite: false }));
  for (let i = 0; i < 9; i++) {
    const R = 1.2 + i * 0.95, pts = [];
    for (let j = 0; j <= 160; j++) {
      const t = (j / 160) * Math.PI * 2;
      const r = R * (1 + 0.07 * Math.sin(3 * t + i * 0.9) + 0.045 * Math.sin(5 * t + i * 1.7) + 0.03 * Math.sin(8 * t + i));
      pts.push(new THREE.Vector3(-1.6 + Math.cos(t) * r * 1.25, 0, -7 + Math.sin(t) * r * 2.1));
    }
    const g = keep(new THREE.BufferGeometry().setFromPoints(pts));
    land.add(new THREE.Line(g, landMat));
  }
  land.position.y = -1.3;
  scene.add(land);

  /* ---- one rupee at a time: three thin rings --------------------------- */
  const ringMat = keep(new THREE.LineBasicMaterial({ color: BRASS, transparent: true, opacity: 0, fog: true, depthWrite: false }));
  const rings = [[1.75, 0.9, -10.6, 0.3], [-1.3, -0.75, -14.4, 0.18], [2.5, 0.15, -16.2, 0.46]].map(([x, y, z, r], i) => {
    const pts = [];
    for (let j = 0; j <= 96; j++) { const t = (j / 96) * Math.PI * 2; pts.push(new THREE.Vector3(Math.cos(t) * r, Math.sin(t) * r, 0)); }
    const line = new THREE.Line(keep(new THREE.BufferGeometry().setFromPoints(pts)), ringMat);
    line.position.set(x, y, z);
    line.rotation.set(0.3 * i, 0.9 + i * 0.7, 0);
    scene.add(line);
    return line;
  });

  /* ---- 1994–96: strokes that close into a building --------------------- */
  const FX = 0.85, FZ = -36, G = -1.1;
  const segs = [];
  const seg = (a, b) => segs.push([a, b]);
  seg([-1.62, G, 0], [1.62, G, 0]); seg([-1.62, G + 0.15, 0], [1.62, G + 0.15, 0]);
  seg([-1.62, 0.55, 0], [-0.5, 0.55, 0]); seg([0.5, 0.55, 0], [1.62, 0.55, 0]); seg([-0.5, 0.55, 0], [0.5, 0.55, 0]);
  seg([-1.78, 1.25, 0], [1.78, 1.25, 0]);
  seg([-1.78, 1.25, 0], [0, 1.86, 0]); seg([0, 1.86, 0], [1.78, 1.25, 0]);
  for (const x of [-1.5, -1.0, -0.5, 0.5, 1.0, 1.5]) seg([x, G + 0.15, 0], [x, 0.55, 0]);
  for (const x of [-1.25, -0.75, 0.75, 1.25]) seg([x, 0.72, 0], [x, 1.1, 0]);
  seg([-1.62, G, 0], [-1.62, G, -0.9]); seg([1.62, G, 0], [1.62, G, -0.9]);
  seg([-1.78, 1.25, 0], [-1.78, 1.25, -0.9]); seg([1.78, 1.25, 0], [1.78, 1.25, -0.9]);
  seg([-1.62, G, -0.9], [-1.62, 1.25, -0.9]); seg([1.62, G, -0.9], [1.62, 1.25, -0.9]);
  // Each stroke starts somewhere else — a fixed, not random, scatter.
  const scatter = segs.map((_, i) => [Math.sin(i * 12.9898) * 1.7, Math.cos(i * 7.233) * 0.9, Math.sin(i * 3.71 + 1) * 3.2 + 1.2]);
  const archPos = new Float32Array(segs.length * 6);
  const archGeo = keep(new THREE.BufferGeometry());
  archGeo.setAttribute("position", new THREE.BufferAttribute(archPos, 3));
  const archMat = keep(new THREE.LineBasicMaterial({ color: IVORY, transparent: true, opacity: 0, fog: true, depthWrite: false }));
  const arch = new THREE.LineSegments(archGeo, archMat);
  arch.position.set(FX, 0, FZ);
  arch.scale.set(0.88, 1, 1);
  arch.frustumCulled = false;
  scene.add(arch);
  let lastAssemble = -1;
  function assemble(a) {
    if (Math.abs(a - lastAssemble) < 1e-4) return;
    lastAssemble = a;
    const k = 1 - a;
    segs.forEach(([p, q], i) => {
      const o = scatter[i], tw = 1 + (i % 3) * 0.35;     // strokes settle at slightly different rates
      const kk = Math.pow(k, tw);
      archPos.set([p[0] + o[0] * kk, p[1] + o[1] * kk, p[2] + o[2] * kk, q[0] + o[0] * kk, q[1] + o[1] * kk, q[2] + o[2] * kk], i * 6);
    });
    archGeo.attributes.position.needsUpdate = true;
  }
  assemble(0);

  /* ---- type set in space ------------------------------------------------ */
  const unit = keep(new THREE.PlaneGeometry(1, 1));
  const typePlates = [];
  function typePlate({ text, sub, h, at, font, color = IVORY, alpha = 1 }) {
    const cv = document.createElement("canvas");
    const tex = keep(new THREE.CanvasTexture(cv));
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;
    const mat = keep(new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: 0, fog: true, depthWrite: false, toneMapped: false }));
    const mesh = new THREE.Mesh(unit, mat);
    mesh.position.set(...at);
    scene.add(mesh);
    const draw = () => {
      const PX = 360, c = cv.getContext("2d");
      c.font = `400 ${PX}px ${font}`;
      const w = Math.ceil(Math.max(c.measureText(text).width, sub ? PX * 1.6 : 0) + PX * 0.2);
      const hh = Math.ceil(PX * (sub ? 1.5 : 1.15));
      cv.width = w; cv.height = hh;
      c.font = `400 ${PX}px ${font}`;
      c.fillStyle = color; c.textBaseline = "alphabetic";
      c.fillText(text, PX * 0.08, PX * 0.95);
      if (sub) { c.font = `400 ${PX * 0.16}px "Mona Sans", Arial, sans-serif`; c.fillText(sub, PX * 0.12, PX * 1.32); }
      mesh.scale.set(h * (w / hh), h, 1);
      tex.needsUpdate = true;
    };
    draw();
    const p = { mesh, mat, alpha, draw };
    typePlates.push(p);
    return p;
  }
  const serif = '"Bodoni Moda", "Literata", Georgia, serif';
  const rupee = typePlate({ text: "₹1", h: 2.1, at: [-0.4, 0.15, -12.6], font: serif, alpha: 0.9 });
  const date = typePlate({ text: "6 June 1996", h: 0.34, at: [FX, 0.9, FZ + 0.05], font: serif, alpha: 0.95 });
  const n96 = typePlate({ text: "96", sub: "students", h: 2.6, at: [3.9, 1.35, -53.4], font: serif, alpha: 0.8 });
  const n11 = typePlate({ text: "11", sub: "academic staff", h: 0.85, at: [2.3, -0.18, -44.4], font: serif, alpha: 0.85 });
  if (document.fonts && document.fonts.load) {
    Promise.all([document.fonts.load(`400 60px "Bodoni Moda"`), document.fonts.load(`400 60px "Literata"`),
                 document.fonts.load(`400 20px "Mona Sans"`)])
      .catch(() => {}).then(() => { typePlates.forEach((p) => p.draw()); dirty(); });
  }

  /* ---- the photographs --------------------------------------------------- */
  const loader = new THREE.TextureLoader();
  const photos = {};
  Object.entries(PLATES).forEach(([name, cfg]) => {
    const src = sources[name];
    if (!src) return;
    const ratio = src.ratio || 1;
    const mat = keep(new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, fog: true, toneMapped: false }));
    const mesh = new THREE.Mesh(unit, mat);
    mesh.scale.set(cfg.h * ratio, cfg.h, 1);
    mesh.position.set(...cfg.at);
    mesh.rotation.set(cfg.rx || 0, cfg.ry || 0, 0, "YXZ");
    mesh.visible = false;
    scene.add(mesh);
    const p = { mesh, mat, cfg, ratio, ready: false, base: mesh.position.clone(), baseRy: cfg.ry || 0 };
    loader.load(src.url, (tex) => {
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
      keep(tex);
      mat.map = tex; mat.needsUpdate = true;
      p.ready = true; p.born = performance.now();
      mesh.visible = true;
      dirty();
    });
    photos[name] = p;
  });
  let lastHidden = false;

  /* ---- a frame ------------------------------------------------------------ */
  const cam = new THREE.Vector3(), look = new THREE.Vector3();
  let W = 1, H = 1, shift = 0;
  let busy = false;
  // Returns true while something is still changing on its own (a
  // photograph fading in), so the caller keeps drawing until it settles.
  function render(P, vel = 0) {
    busy = false;
    const t = curveT(P);
    camCurve.getPoint(t, cam);
    lookCurve.getPoint(t, look);
    camera.position.copy(cam);
    camera.up.set(0, 1, 0);
    camera.lookAt(look);

    const fog = station(P, FOG);
    scene.fog.near = fog[0]; scene.fog.far = fog[1];
    const s = station(P, SHIFT);
    if (Math.abs(s - shift) > 1e-4 || !camera.view) { shift = s; frame(); }

    landMat.opacity = 0.11 * (1 - smooth((P - 2.1) / 0.9));
    land.visible = landMat.opacity > 0.002;
    ringMat.opacity = 0.55 * win(P, 1.2, 1.8, 2.5, 3.0);
    rings.forEach((r, i) => { r.visible = ringMat.opacity > 0.002; r.rotation.y = 0.9 + i * 0.7 + P * 0.35 + vel * 0.02; });
    rupee.mat.opacity = rupee.alpha * win(P, 1.25, 1.85, 2.45, 2.9);

    // The drawing gathers from 1994 and is whole by the opening; it stays
    // faint behind the first school, then is left behind.
    assemble(smooth((P - 3.2) / 1.7));
    archMat.opacity = 0.42 * smooth((P - 3.0) / 0.8) * (1 - 0.5 * smooth((P - 5.3) / 0.8));
    arch.visible = archMat.opacity > 0.002;
    date.mat.opacity = date.alpha * smooth((P - 4.35) / 0.5) * (1 - smooth((P - 5.4) / 0.4));
    n11.mat.opacity = n11.alpha * win(P, 5.15, 5.7, 6.4, 6.8);
    n96.mat.opacity = n96.alpha * win(P, 5.2, 5.9, 6.2, 6.5);
    typePlates.forEach((p) => { p.mesh.visible = p.mat.opacity > 0.002; });

    // Photographs fade in as they load, and move only with fast scrolling:
    // a lean of at most about two degrees, gone as soon as the page stops.
    const now = performance.now();
    Object.values(photos).forEach((p) => {
      if (!p.ready) return;
      // Each photograph comes out of the dark as its moment approaches,
      // rather than waiting in view from the start of the page.
      const fade = Math.min(1, (now - p.born) / 600);
      if (fade < 1) busy = true;
      p.mat.opacity = fade * smooth((P - (p.cfg.k - 0.9)) / 0.5);
      p.mesh.visible = p.mat.opacity > 0.002;
      p.mesh.rotation.y = p.baseRy + vel * 0.012;
      p.mesh.position.y = p.base.y - vel * 0.012;
    });
    if (photos["campus-band"] && lastHidden) photos["campus-band"].mesh.visible = false;

    renderer.render(scene, camera);
    return busy;
  }

  // Weight the view to the right of the text column: the frustum is cut
  // from a wider virtual frame so the look target sits right of centre.
  function frame() {
    const F = W * (1 + 2 * shift);
    camera.aspect = F / H;
    camera.setViewOffset(F, H, 0, 0, W, H);
    camera.updateProjectionMatrix();
  }
  function resize() {
    W = Math.max(1, innerWidth); H = Math.max(1, innerHeight);
    renderer.setPixelRatio(dpr());
    renderer.setSize(W, H, false);
    frame();
  }
  resize();

  /* Where each photograph is on screen, in CSS pixels, and whether it is
     turned towards the camera and wholly in front of it. */
  const v = new THREE.Vector3(), n = new THREE.Vector3(), toCam = new THREE.Vector3();
  const corners = [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]];
  function plateRects() {
    const out = {};
    camera.updateMatrixWorld();
    Object.entries(photos).forEach(([name, p]) => {
      if (!p.ready) return;
      p.mesh.updateMatrixWorld();
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity, ok = true;
      for (const [cx, cy] of corners) {
        v.set(cx, cy, 0).applyMatrix4(p.mesh.matrixWorld).project(camera);
        if (v.z > 1 || v.z < -1) ok = false;
        const sx = (v.x + 1) / 2 * W, sy = (1 - v.y) / 2 * H;
        x0 = Math.min(x0, sx); x1 = Math.max(x1, sx); y0 = Math.min(y0, sy); y1 = Math.max(y1, sy);
      }
      n.set(0, 0, 1).applyQuaternion(p.mesh.getWorldQuaternion(new THREE.Quaternion()));
      toCam.copy(camera.position).sub(p.mesh.getWorldPosition(new THREE.Vector3())).normalize();
      const onScreen = x1 > 0 && x0 < W && y1 > 0 && y0 < H;
      out[name] = { x: x0, y: y0, w: x1 - x0, h: y1 - y0, facing: ok && onScreen && n.dot(toCam) > 0.55,
                    area: (x1 - x0) * (y1 - y0) };
    });
    return out;
  }

  function showLast(on) {
    const hidden = !on;
    if (hidden !== lastHidden) { lastHidden = hidden; dirty(); }
  }

  let lost = false;
  const onLost = (e) => { e.preventDefault(); lost = true; if (opts.onLost) opts.onLost(); };
  canvas.addEventListener("webglcontextlost", onLost);

  function destroy() {
    canvas.removeEventListener("webglcontextlost", onLost);
    disposables.forEach((d) => d.dispose && d.dispose());
    renderer.dispose();
  }
  function info() {
    return { calls: renderer.info.render.calls, textures: renderer.info.memory.textures,
             dpr: renderer.getPixelRatio(), lost, revision: THREE.REVISION };
  }

  render(0, 0);
  return { render, resize, plateRects, showLast, destroy, info };
}
