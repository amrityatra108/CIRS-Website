/* ============================================================
   Math Challenge — the sculpture
   216 bevelled blocks, one instanced mesh, one renderer, one
   render loop that runs only while something is moving.

   Every block keeps one id through three precomputed states:
     A  a 6x6x6 cube with narrow gaps
     B  an 18x12 field, lifted into a wave
     C  the same 18x12 cells sampled around a torus
   Each layer of the cube becomes a 6x6 tile of the field, and each
   column of the field becomes one ring of the torus, so the pieces
   travel somewhere that belongs to them. These are constructions
   to look at, not a theorem.

   The layers are kept apart:
     base      the precomputed states               (build)
     scroll    progress 0..1 from matharena.js      (pose)
     offsets   pointer, pulse and tap, on springs   (react)
     camera    framing per state, from the layout   (frame)

   Loaded only on this page, by matharena.js, which falls back to
   the drawn cube if anything here fails. The still drawings are
   made from the same numbers by tools/make-math-sculpture.py; keep
   the constants below and those in step.
   ============================================================ */
import * as THREE from "../founder-opening/vendor/three.module.min.js";

const N = 6, COLS = 18, ROWS = 12, COUNT = N * N * N;
const BLOCK = 0.34, PITCH = 0.40, BEVEL = 0.1;
const FIELD_PITCH = 0.42;
const TORUS_R = 2.0, TORUS_r = 0.78, TORUS_U0 = -0.75 * Math.PI;
const GOLD_COL = 9;
const DIST = 12, RADIUS_A = 2.2, RADIUS_B = 4.5, RADIUS_C = 3.05;
const VIEW = {
  A: [0.50, -0.70, 0], A2: [0.50, -0.86, 0],
  B: [0.66, -0.22, 0], C: [1.02, 0.35, 0], D: [0.70, 0.98, 0],
  // On a portrait screen the field turns lengthwise to fill it.
  Bt: [0.86, -1.32, 0]
};
const IVORY = new THREE.Color("#c49a48");
const STONE = new THREE.Color("#a57d36");
const GOLD = new THREE.Color("#d4af62");

const clamp = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const range = (p, a, b) => clamp((p - a) / (b - a));
const smooth = (t) => t * t * t * (t * (t * 6 - 15) + 10);
const lerp = (a, b, t) => a + (b - a) * t;
function hash01(i) {
  const s = Math.sin(i * 12.9898 + 4.1414) * 43758.5453;
  return s - Math.floor(s);
}

/* ---------- One block: a box whose edges are chamfered ---------- */
function bevelledBox(size, bevel) {
  const g = new THREE.BoxGeometry(1, 1, 1, 3, 3, 3);
  const pos = g.attributes.position, nor = g.attributes.normal;
  const inner = 0.5 - bevel;
  const v = new THREE.Vector3(), c = new THREE.Vector3(), n = new THREE.Vector3();
  const pull = (x) => (Math.abs(x) < 0.49 ? Math.sign(x) * inner : x);
  const hold = (x) => Math.max(-inner, Math.min(inner, x));
  for (let i = 0; i < pos.count; i++) {
    v.set(pull(pos.getX(i)), pull(pos.getY(i)), pull(pos.getZ(i)));
    c.set(hold(v.x), hold(v.y), hold(v.z));
    n.subVectors(v, c).normalize();
    v.copy(c).addScaledVector(n, bevel).multiplyScalar(size);
    pos.setXYZ(i, v.x, v.y, v.z);
    nor.setXYZ(i, n.x, n.y, n.z);
  }
  g.computeBoundingSphere();
  return g;
}

/* ---------- The three states, computed once ---------- */
function build() {
  const S = {
    posA: new Float32Array(COUNT * 3), posB: new Float32Array(COUNT * 3), posC: new Float32Array(COUNT * 3),
    sclC: new Float32Array(COUNT * 3),
    qA: [], qB: [], qC: [], tumble: [],
    dAB: new Float32Array(COUNT), dBC: new Float32Array(COUNT),
    liftA: new Float32Array(COUNT), ao: new Float32Array(COUNT),
    base: [], gold: new Uint8Array(COUNT)
  };
  const up = new THREE.Vector3(0, 1, 0), n = new THREE.Vector3();
  const ax = new THREE.Vector3(), ay = new THREE.Vector3(), az = new THREE.Vector3();
  const m = new THREE.Matrix4();
  for (let y = 0; y < N; y++) for (let z = 0; z < N; z++) for (let x = 0; x < N; x++) {
    const i = x + N * z + N * N * y;
    const col = x + N * (y % 3), row = z + N * Math.floor(y / 3);
    const o = i * 3;

    // A: the cube.
    S.posA[o] = (x - 2.5) * PITCH; S.posA[o + 1] = (y - 2.5) * PITCH; S.posA[o + 2] = (z - 2.5) * PITCH;
    S.qA[i] = new THREE.Quaternion();

    // B: the field, and each block tilted to the wave's normal.
    const fx = (col - 8.5) * FIELD_PITCH, fz = (row - 5.5) * FIELD_PITCH;
    const a = 0.95 * fx + 0.45 * fz + 0.6, b = 1.7 * fz - 0.6 * fx;
    const h = 0.38 * Math.sin(a) + 0.16 * Math.sin(b);
    const hx = 0.38 * 0.95 * Math.cos(a) - 0.16 * 0.6 * Math.cos(b);
    const hz = 0.38 * 0.45 * Math.cos(a) + 0.16 * 1.7 * Math.cos(b);
    S.posB[o] = fx; S.posB[o + 1] = h; S.posB[o + 2] = fz;
    S.qB[i] = new THREE.Quaternion().setFromUnitVectors(up, n.set(-hx, 1, -hz).normalize());

    // C: the torus. Tiles widen with their ring so it reads as a surface.
    const u = col / COLS * Math.PI * 2 + TORUS_U0, v = row / ROWS * Math.PI * 2;
    const ring = TORUS_R + TORUS_r * Math.cos(v);
    S.posC[o] = ring * Math.cos(u); S.posC[o + 1] = TORUS_r * Math.sin(v); S.posC[o + 2] = ring * Math.sin(u);
    ax.set(-Math.sin(u), 0, Math.cos(u));
    ay.set(Math.cos(v) * Math.cos(u), Math.sin(v), Math.cos(v) * Math.sin(u));
    az.crossVectors(ax, ay);
    S.qC[i] = new THREE.Quaternion().setFromRotationMatrix(m.makeBasis(ax, ay, az));
    S.sclC[o] = Math.min(1.9, ring * Math.PI * 2 / COLS * 0.8 / BLOCK); S.sclC[o + 1] = 0.78; S.sclC[o + 2] = 0.94;

    // Phasing: the cube opens from its top layer down; the field wraps
    // column by column. Each block also has a little tumble of its own.
    S.dAB[i] = 0.4 * (0.72 * (5 - y) / 5 + 0.28 * (x + z) / 10);
    S.dBC[i] = 0.4 * (0.82 * col / (COLS - 1) + 0.18 * row / (ROWS - 1));
    S.liftA[i] = 0.35 + 0.75 * y / 5;
    const r = hash01(i + 7);
    S.tumble[i] = new THREE.Vector3(r - 0.5, 0.35, hash01(i + 19) - 0.5).normalize();

    const k = Math.min(x, 5 - x, y, 5 - y, z, 5 - z);
    S.ao[i] = [1, 0.72, 0.55][Math.min(k, 2)];
    S.gold[i] = col === GOLD_COL ? 1 : 0;
    S.base[i] = S.gold[i] ? GOLD.clone() : IVORY.clone().lerp(STONE, hash01(i) * 0.6);
  }
  return S;
}

function viewQuat(e) {
  return new THREE.Quaternion().setFromEuler(new THREE.Euler(e[0], e[1], e[2], "XYZ"));
}

/* Original, small HDR studio map. Soft rectangular reflection sources are
   prefiltered once by PMREM, so metal receives broad reflections without
   a downloaded HDR asset, bloom, or another per-frame render pass. */
function studioEnvironment(renderer) {
  const w = 256, h = 128, data = new Float32Array(w * h * 4);
  const panels = [
    [-.9, .7, .7, .58, .34, 3.3, [1, .86, .66]],
    [1, .2, .6, .35, .62, 1.25, [.86, .92, 1]],
    [.3, .5, -1, .22, .58, 3.2, [1, .91, .73]],
    [0, 1, 0, .9, .35, 1.0, [1, .96, .88]]
  ].map(([x,y,z,a,b,power,colour]) => ({dir:new THREE.Vector3(x,y,z).normalize(),a,b,power,colour}));
  const dir=new THREE.Vector3(), horizontal=new THREE.Vector3(), vertical=new THREE.Vector3();
  for(let y=0;y<h;y++) for(let x=0;x<w;x++) {
    const theta=(y+.5)/h*Math.PI, phi=(x+.5)/w*Math.PI*2;
    dir.set(-Math.sin(theta)*Math.cos(phi),Math.cos(theta),Math.sin(theta)*Math.sin(phi));
    const rgb=[.07,.075,.085];
    for(const panel of panels) {
      horizontal.crossVectors(new THREE.Vector3(0,1,0),panel.dir);
      if(horizontal.lengthSq()<.001) horizontal.set(1,0,0);
      horizontal.normalize(); vertical.crossVectors(panel.dir,horizontal);
      const facing=dir.dot(panel.dir);
      if(facing<=0)continue;
      const u=dir.dot(horizontal)/facing/panel.a,v=dir.dot(vertical)/facing/panel.b;
      const intensity=panel.power*Math.exp(-Math.pow(u,4)-Math.pow(v,4));
      for(let c=0;c<3;c++)rgb[c]+=intensity*panel.colour[c];
    }
    const i=(y*w+x)*4;data[i]=rgb[0];data[i+1]=rgb[1];data[i+2]=rgb[2];data[i+3]=1;
  }
  const texture=new THREE.DataTexture(data,w,h,THREE.RGBAFormat,THREE.FloatType);
  texture.mapping=THREE.EquirectangularReflectionMapping;texture.needsUpdate=true;
  const pmrem=new THREE.PMREMGenerator(renderer), target=pmrem.fromEquirectangular(texture);
  texture.dispose();pmrem.dispose();return target;
}

/* ============================================================
   mount(api) — api comes from matharena.js
   ============================================================ */
export function mount(api) {
  const { canvas, art, fallback, view, pulse } = api;
  const compact = () => window.matchMedia("(max-width: 760px), (pointer: coarse)").matches;
  const portrait = () => window.matchMedia("(max-width: 760px), (max-aspect-ratio: 4/5)").matches;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas, alpha: true, antialias: true,
      powerPreference: compact() ? "low-power" : "high-performance"
    });
  } catch (err) {
    return null;
  }
  renderer.setClearColor(0x000000, 0);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  const S = build();
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
  camera.position.set(0, 0, DIST);
  const group = new THREE.Group();
  scene.add(group);

  const environment = studioEnvironment(renderer);
  scene.environment = environment.texture;
  scene.add(new THREE.HemisphereLight(0xfff2db, 0x24232c, .45));
  const key = new THREE.DirectionalLight(0xffe1ad, 3.2);
  key.position.set(-0.62, 0.66, 0.58).multiplyScalar(10);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xe6edff, 1.1);
  fill.position.set(0.72, -0.08, 0.42).multiplyScalar(10);
  scene.add(fill);
  const rim = new THREE.DirectionalLight(0xffe7bd, 2.0);
  rim.position.set(4, 5, -6);
  scene.add(rim);

  const geometry = bevelledBox(BLOCK, BEVEL);
  const material = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: .30, metalness: .85, envMapIntensity: 1.15 });
  const mesh = new THREE.InstancedMesh(geometry, material, COUNT);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  for (let i = 0; i < COUNT; i++) mesh.setColorAt(i, S.base[i]);
  mesh.instanceColor.setUsage(THREE.DynamicDrawUsage);
  group.add(mesh);

  const VQ = {};
  Object.keys(VIEW).forEach((k) => { VQ[k] = viewQuat(VIEW[k]); });
  const qView = new THREE.Quaternion(), qInv = new THREE.Quaternion();

  // Springs for the offsets: position and a small rotation, per block.
  const off = new Float32Array(COUNT * 3), vel = new Float32Array(COUNT * 3);
  const rot = new Float32Array(COUNT * 3), rvel = new Float32Array(COUNT * 3);
  const tgt = new Float32Array(COUNT * 3), rtgt = new Float32Array(COUNT * 3);
  const screen = new Float32Array(COUNT * 2);

  // Reused every frame.
  const P = new THREE.Vector3(), Q = new THREE.Quaternion(), Qt = new THREE.Quaternion();
  const Sc = new THREE.Vector3(), M = new THREE.Matrix4(), V = new THREE.Vector3();
  const W = new THREE.Vector3(), R = new THREE.Vector3(), C = new THREE.Color();

  let width = 1, height = 1, frames = null, tallView = false;
  let raf = 0, last = 0, visible = true, lost = false, live = false, destroyed = false;
  let progress = api.progress(), shownProgress = -1, displayedProgress = progress;
  let pointer = { x: 0, y: 0, on: false, strength: 0 };
  let pulseAt = -1, pulseOrigin = null;
  let pokes = [];
  let shadedAt = -1;

  /* ---------- frame: where each state sits in the window ---------- */
  function layout() {
    const w = Math.max(1, canvas.clientWidth), h = Math.max(1, canvas.clientHeight);
    const dpr = Math.min(window.devicePixelRatio || 1, compact() ? 1.5 : 1.75);
    renderer.setPixelRatio(dpr);
    renderer.setSize(w, h, false);
    width = w; height = h;

    // State A is framed on the drawing, so the first frame lands on it.
    let ax = w / 2, ay = h / 2, as = Math.min(w, h);
    if (api.kinetic()) {
      canvas.style.cssText = "";
      ax = fallback.offsetLeft + fallback.offsetWidth / 2;
      ay = fallback.offsetTop + fallback.offsetHeight / 2;
      as = fallback.offsetWidth;
    } else {
      canvas.style.cssText = `left:${fallback.offsetLeft}px;top:${fallback.offsetTop}px;` +
        `width:${fallback.offsetWidth}px;height:${fallback.offsetHeight}px`;
      const cw = fallback.offsetWidth || w;
      if (cw !== w) { renderer.setSize(cw, cw, false); width = height = cw; }
      ax = ay = as = width;
      ax /= 2; ay /= 2;
    }
    const fpx = (as / 2) * DIST / RADIUS_A;
    camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan((height / 2) / fpx));
    const at = (r, size) => r * fpx / (size / 2);
    const tall = portrait();
    tallView = tall;
    frames = {
      A: [ax, ay, DIST],
      A2: [ax, ay - height * 0.01, DIST / 1.04],
      B: tall ? [width * 0.5, height * 0.52, at(RADIUS_B, Math.min(height * 0.92, width * 2.4))]
              : [width * 0.5, height * 0.51, at(RADIUS_B, Math.min(width * .78, height * 1.02))],
      C: tall ? [width * 0.5, height * 0.5, at(RADIUS_C, width * .92)]
              : [width * 0.74, height * 0.51, at(RADIUS_C, Math.min(height * 0.76, width * 0.48))],
      D: tall ? [width * 0.5, height * 0.5, at(RADIUS_C, width * .9)]
              : [width * 0.74, height * 0.51, at(RADIUS_C, Math.min(height * 0.76, width * 0.46))]
    };
    shownProgress = -1;
    wake();
  }

  /* ---------- pose: the structure at this progress ---------- */
  function pose(p, now) {
    const e0 = smooth(range(p, 0, 0.18));
    const sAB = range(p, 0.18, 0.48), sBC = range(p, 0.48, 0.76);
    const gAB = smooth(sAB), gBC = smooth(sBC), gD = smooth(range(p, 0.76, 0.96));

    // Camera: one framing, interpolated through the states.
    const f = frames;
    let cx = lerp(f.A[0], f.A2[0], e0), cy = lerp(f.A[1], f.A2[1], e0), d = lerp(f.A[2], f.A2[2], e0);
    cx = lerp(cx, f.B[0], gAB); cy = lerp(cy, f.B[1], gAB); d = lerp(d, f.B[2], gAB);
    cx = lerp(cx, f.C[0], gBC); cy = lerp(cy, f.C[1], gBC); d = lerp(d, f.C[2], gBC);
    cx = lerp(cx, f.D[0], gD); cy = lerp(cy, f.D[1], gD); d = lerp(d, f.D[2], gD);
    camera.position.set(0, 0, d);
    camera.aspect = width / height;
    camera.setViewOffset(width, height, -(cx - width / 2), -(cy - height / 2), width, height);
    camera.updateProjectionMatrix();

    qView.copy(VQ.A).slerp(VQ.A2, e0).slerp(tallView ? VQ.Bt : VQ.B, gAB).slerp(VQ.C, gBC).slerp(VQ.D, gD);
    if (!compact() && !api.reduced()) {
      Qt.setFromEuler(new THREE.Euler((pointer.y / height - .5) * .07 * pointer.strength,
        (pointer.x / width - .5) * .09 * pointer.strength, 0));
      qView.multiply(Qt);
    }
    group.quaternion.copy(qView);
    group.updateMatrixWorld(true);
    qInv.copy(qView).invert();

    // The cube's inner blocks sit in their neighbours' shade until it opens.
    const recolour = sAB !== shadedAt;
    shadedAt = sAB;
    for (let i = 0; i < COUNT; i++) {
      const o = i * 3;
      const tA = smooth(clamp((sAB - S.dAB[i]) / 0.6));
      const tB = smooth(clamp((sBC - S.dBC[i]) / 0.6));
      const arcA = Math.sin(Math.PI * tA), arcB = Math.sin(Math.PI * tB);

      // Position: A to B, then B to C, each on an arc.
      P.set(lerp(S.posA[o], S.posB[o], tA), lerp(S.posA[o + 1], S.posB[o + 1], tA), lerp(S.posA[o + 2], S.posB[o + 2], tA));
      P.y += arcA * 0.9 * S.liftA[i];
      P.set(lerp(P.x, S.posC[o], tB), lerp(P.y, S.posC[o + 1], tB) + arcB * 0.7, lerp(P.z, S.posC[o + 2], tB));

      // Orientation, with the block's own tumble while it travels.
      Q.copy(S.qA[i]).slerp(S.qB[i], tA).slerp(S.qC[i], tB);
      if (arcA > 0 || arcB > 0) Q.multiply(Qt.setFromAxisAngle(S.tumble[i], arcA * 0.6 + arcB * 0.45));

      Sc.set(lerp(lerp(1, 0.94, tA), S.sclC[o], tB), lerp(lerp(1, 0.94, tA), S.sclC[o + 1], tB),
        lerp(lerp(1, 0.94, tA), S.sclC[o + 2], tB));

      // Where it sits on screen, before any reaction, for the pointer.
      V.copy(P).applyMatrix4(group.matrixWorld).project(camera);
      screen[i * 2] = (V.x + 1) / 2 * width;
      screen[i * 2 + 1] = (1 - V.y) / 2 * height;

      // The reaction, from the springs, in the sculpture's own space.
      P.x += off[o]; P.y += off[o + 1]; P.z += off[o + 2];
      R.set(rot[o], rot[o + 1], rot[o + 2]);
      const angle = R.length();
      if (angle > 1e-5) Q.premultiply(Qt.setFromAxisAngle(R.multiplyScalar(1 / angle), angle));

      M.compose(P, Q, Sc);
      mesh.setMatrixAt(i, M);
      if (recolour) {
        C.copy(S.base[i]).multiplyScalar(lerp(S.ao[i], 1, tA));
        mesh.setColorAt(i, C);
      }
    }
    if (recolour) mesh.instanceColor.needsUpdate = true;
    mesh.instanceMatrix.needsUpdate = true;
    // The blocks leave the geometry's own bounds as they travel; keep
    // the instanced bounds true so nothing is culled at the wrong moment.
    mesh.computeBoundingSphere();
  }

  /* ---------- react: pointer, pulse and taps drive spring targets ---------- */
  function targets(now) {
    tgt.fill(0); rtgt.fill(0);
    const reach = Math.min(width, height) * (compact() ? 0.2 : 0.15);
    const reach2 = reach * reach;
    const sources = [];
    // Restore the local cursor response using the existing damped block springs.
    if (pointer.strength > 0.002) sources.push([pointer.x, pointer.y, pointer.strength, reach2]);
    pokes = pokes.filter((k) => now - k.t < 700);
    pokes.forEach((k) => {
      const age = (now - k.t) / 700;
      sources.push([k.x, k.y, Math.sin(Math.PI * Math.min(1, age * 2.2)) * (1 - age) * 1.2, reach2 * 1.4]);
    });
    for (const [px, py, strength, r2] of sources) {
      for (let i = 0; i < COUNT; i++) {
        const dx = screen[i * 2] - px, dy = screen[i * 2 + 1] - py;
        const d2 = dx * dx + dy * dy;
        const inf = Math.exp(-d2 / r2) * strength;
        if (inf < 0.003) continue;
        const len = Math.sqrt(d2) || 1, ux = dx / len, uy = dy / len;
        push(i, ux, uy, inf);
      }
    }
    if (pulseAt >= 0) {
      const t = (now - pulseAt) / 1500;
      if (t >= 1) { pulseAt = -1; if(pulse) {pulse.setAttribute("aria-pressed","false");pulse.classList.remove("is-pulsing");} }
      else {
        const [ox, oy, span] = pulseOrigin;
        const front = t * 1.35;
        for (let i = 0; i < COUNT; i++) {
          const dx = screen[i * 2] - ox, dy = screen[i * 2 + 1] - oy;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const rho = dist / span;
          const wave = Math.exp(-Math.pow((rho - front) / 0.16, 2)) * (1 - t) * .32;
          if (wave < 0.003) continue;
          push(i, dx / dist, dy / dist, wave);
        }
      }
    }
  }
  // A push away from the source across the screen, out towards the viewer,
  // and a tilt about the axis between them. Worked in the window's terms,
  // then turned into the sculpture's own space.
  function push(i, ux, uy, inf) {
    const o = i * 3;
    W.set(ux * 0.26 * inf, -uy * 0.26 * inf, 0.5 * inf).applyQuaternion(qInv);
    tgt[o] += W.x; tgt[o + 1] += W.y; tgt[o + 2] += W.z;
    W.set(uy, ux, 0).multiplyScalar(0.85 * inf).applyQuaternion(qInv);
    rtgt[o] += W.x; rtgt[o + 1] += W.y; rtgt[o + 2] += W.z;
  }

  function springs(dt) {
    const k = 100, c = 2 * Math.sqrt(k) * .95;
    let moving = 0;
    for (let j = 0; j < COUNT * 3; j++) {
      const a = k * (tgt[j] - off[j]) - c * vel[j];
      vel[j] += a * dt; off[j] += vel[j] * dt;
      const b = k * (rtgt[j] - rot[j]) - c * rvel[j];
      rvel[j] += b * dt; rot[j] += rvel[j] * dt;
      moving = Math.max(moving, Math.abs(vel[j]), Math.abs(rvel[j]),
        Math.abs(tgt[j] - off[j]), Math.abs(rtgt[j] - rot[j]));
    }
    return moving > 0.0008;
  }

  /* ---------- the loop ---------- */
  function frame(now) {
    raf = 0;
    if (destroyed || lost || !visible || document.hidden || !frames) return;
    const dt = Math.min(0.05, last ? (now - last) / 1000 : 1 / 60);
    last = now;

    const motion = !api.reduced();
    displayedProgress = motion ? lerp(displayedProgress, progress, 1 - Math.exp(-dt * 7)) : progress;
    if (Math.abs(displayedProgress-progress)<.00005)displayedProgress=progress;
    const target = displayedProgress;
    const hover = pointer.on && motion && !compact();
    pointer.strength += ((hover ? 1 : 0) - pointer.strength) * Math.min(1, dt * 7);

    // Pose once for the screen positions, react, then pose with the result.
    pose(target, now);
    let moving = false;
    if (motion) {
      targets(now);
      moving = springs(dt);
      pose(target, now);
    }
    renderer.render(scene, camera);
    shownProgress = target;

    if (!live) {
      live = true;
      art.classList.add("is-live");
      if (pulse) pulse.hidden = !motion;
    }
    const busy = moving || pulseAt >= 0 || pokes.length || Math.abs(pointer.strength-(hover?1:0))>.002 || Math.abs(displayedProgress-progress)>.00005;
    if (busy) raf = requestAnimationFrame(frame);
    else last = 0;
  }
  function wake() {
    if (raf || destroyed || lost || !visible || document.hidden) return;
    raf = requestAnimationFrame(frame);
  }

  /* ---------- the first frame arrives settling, not appearing ---------- */
  if (!api.reduced() && api.progress() < 0.05) {
    for (let i = 0; i < COUNT; i++) {
      const o = i * 3, s = .025 + .035 * hash01(i + 3);
      off[o] = S.posA[o] * s; off[o + 1] = S.posA[o + 1] * s + 0.12; off[o + 2] = S.posA[o + 2] * s;
      rot[o + 1] = (hash01(i + 11) - 0.5) * 0.5;
    }
  }

  /* ---------- listeners, all scoped to the stage ---------- */
  function local(e) {
    const r = canvas.getBoundingClientRect();
    return [e.clientX - r.left, e.clientY - r.top];
  }
  function onMove(e) {
    if (e.pointerType === "touch" || compact() || e.target.closest("a,button")) return;
    [pointer.x, pointer.y] = local(e);
    pointer.on = true;
    wake();
  }
  function onLeave() { pointer.on = false; wake(); }
  function onDown(e) {
    // Touch leaves the model still; Pulse is the explicit motion control.
  }
  function onPulse() {
    if (api.reduced()) return;
    const r = canvas.getBoundingClientRect();
    // From the middle of what is on screen now.
    let sx = 0, sy = 0;
    for (let i = 0; i < COUNT; i++) { sx += screen[i * 2]; sy += screen[i * 2 + 1]; }
    sx /= COUNT; sy /= COUNT;
    let far = 1;
    for (let i = 0; i < COUNT; i++) far = Math.max(far, Math.hypot(screen[i * 2] - sx, screen[i * 2 + 1] - sy));
    pulseOrigin = [sx, sy, far || Math.min(r.width, r.height) / 3];
    pulseAt = performance.now();
    pulse.setAttribute("aria-pressed", "true");
    pulse.classList.remove("is-pulsing");
    void pulse.offsetWidth;
    pulse.classList.add("is-pulsing");
    wake();
  }
  api.onProgress((p) => {
    progress = p;
    if (p !== shownProgress) wake();
  });
  api.onMode(() => {
    if (api.reduced()) {
      pointer.on=false; pointer.strength=0; pulseAt=-1; pokes=[];
      off.fill(0); vel.fill(0); rot.fill(0); rvel.fill(0);
      if(pulse){pulse.setAttribute("aria-pressed","false");pulse.classList.remove("is-pulsing");}
    }
    if(pulse)pulse.hidden=api.reduced()||!live;
    requestAnimationFrame(layout);
  });

  view.addEventListener("pointermove", onMove, { passive: true });
  view.addEventListener("pointerleave", onLeave, { passive: true });
  view.addEventListener("pointerdown", onDown, { passive: true });
  if (pulse) pulse.addEventListener("click", onPulse);

  const resizer = new ResizeObserver(() => layout());
  resizer.observe(canvas);
  resizer.observe(fallback);
  const seen = new IntersectionObserver((entries) => {
    visible = entries[entries.length - 1].isIntersecting;
    if (visible) wake();
    else if (raf) { cancelAnimationFrame(raf); raf = 0; last = 0; }
  });
  seen.observe(view);
  function onVisibility() {
    if (document.hidden) { cancelAnimationFrame(raf); raf = 0; last = 0; }
    else wake();
  }
  document.addEventListener("visibilitychange", onVisibility);

  // A lost context shows the drawing again until the context returns.
  function onLost(e) {
    e.preventDefault();
    lost = true; live = false;
    cancelAnimationFrame(raf); raf = 0;
    art.classList.remove("is-live");
    if (pulse) pulse.hidden = true;
  }
  function onRestored() {
    lost = false;
    mesh.instanceMatrix.needsUpdate = true;
    shadedAt = -1;
    shownProgress = -1;
    layout();
  }
  canvas.addEventListener("webglcontextlost", onLost);
  canvas.addEventListener("webglcontextrestored", onRestored);

  function destroy() {
    destroyed = true;
    cancelAnimationFrame(raf);
    resizer.disconnect(); seen.disconnect();
    view.removeEventListener("pointermove", onMove);
    view.removeEventListener("pointerleave", onLeave);
    view.removeEventListener("pointerdown", onDown);
    if (pulse) pulse.removeEventListener("click", onPulse);
    document.removeEventListener("visibilitychange", onVisibility);
    canvas.removeEventListener("webglcontextlost", onLost);
    canvas.removeEventListener("webglcontextrestored", onRestored);
    geometry.dispose(); material.dispose(); mesh.dispose(); environment.dispose(); renderer.dispose();
  }
  window.addEventListener("pagehide", (e) => { if (!e.persisted) destroy(); });
  window.addEventListener("pageshow", (e) => { if (e.persisted) { shownProgress = -1; layout(); } });

  layout();
  return { destroy };
}
