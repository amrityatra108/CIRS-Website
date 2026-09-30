/**
 * Decorative, logo-contact-driven particle arrows.
 *
 * Integration: call update once from the page's existing render loop, after the
 * camera and sculpture matrices have been updated. `time` and `dt` are seconds.
 * `hoveringLogo` must be a real logo hit, not a section/pointer-moving test.
 * The module owns neither pointer listeners nor a requestAnimationFrame loop.
 */
export const FLOW_ARROW_SETTINGS = Object.freeze({
  idleSeconds: 1.5,
  cadenceSeconds: 1.5,
  lifetimeSeconds: 1,
  words: Object.freeze(['Seva', 'Study', 'Sadhana']),
  ribbonSegments: 72,
  particleCount: 280
});

const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
const smooth = (a, b, value) => {
  const t = clamp((value - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};
const range = (a, b) => a + Math.random() * (b - a);

/** Pure scheduler, also exported so logo-contact timing can be tested alone. */
export class FlowArrowClock {
  constructor() { this.reset(0); }
  reset(time = 0) {
    this.nextAt = null;
    this.hovering = false;
    this.ready = false;
    this.lastTime = Number.isFinite(time) ? time : 0;
  }
  suspend(time = this.lastTime) { this.reset(time); }
  update(time, ready, hoveringLogo, reduced = false) {
    if (!Number.isFinite(time)) return false;
    const hovering = Boolean(hoveringLogo);
    if (time < this.lastTime || !ready || reduced) {
      this.reset(time);
      this.hovering = hovering;
      return false;
    }
    this.lastTime = time;
    if (hovering) {
      this.hovering = true;
      this.ready = true;
      this.nextAt = null;
      return false;
    }
    if (!this.ready || this.hovering || this.nextAt === null) {
      this.nextAt = time + FLOW_ARROW_SETTINGS.idleSeconds;
      this.ready = true;
      this.hovering = false;
      return false;
    }
    this.hovering = false;
    if (time + 1e-7 < this.nextAt) return false;
    // Use actual time instead of catching up missed emissions after a pause.
    this.nextAt = time + FLOW_ARROW_SETTINGS.cadenceSeconds;
    return true;
  }
}

export function createFlowArrows({ THREE, scene, sculpture, root, camera, rest, width = 1, height = 1 }) {
  const settings = FLOW_ARROW_SETTINGS;
  const clock = new FlowArrowClock();
  const group = new THREE.Group();
  group.name = 'Spiritual flowing intentions';
  scene.add(group);
  const overlay = document.createElement('div');
  overlay.className = 'spiritual-flow-labels';
  overlay.setAttribute('aria-hidden', 'true');
  Object.assign(overlay.style, { position: 'absolute', inset: '0', pointerEvents: 'none', overflow: 'hidden', zIndex: '1' });
  root.append(overlay);
  const label = document.createElement('span');
  Object.assign(label.style, {
    position: 'absolute', left: '0', top: '0', display: 'none', whiteSpace: 'nowrap',
    fontFamily: 'Newsreader, Georgia, serif', fontWeight: '450', fontStyle: 'italic',
    letterSpacing: '.015em', lineHeight: '1', color: '#6f442d',
    textShadow: '0 1px 8px #F6F0E2, 0 0 3px #F6F0E2, 0 0 3px #F6F0E2',
    willChange: 'transform, opacity'
  });
  overlay.append(label);

  const ribbonCount = (settings.ribbonSegments + 1) * 2 + 3;
  const ribbonPositions = new Float32Array(ribbonCount * 3);
  const ribbonAlpha = new Float32Array(ribbonCount);
  const ribbonGeometry = new THREE.BufferGeometry();
  ribbonGeometry.setAttribute('position', new THREE.BufferAttribute(ribbonPositions, 3).setUsage(THREE.DynamicDrawUsage));
  ribbonGeometry.setAttribute('aAlpha', new THREE.BufferAttribute(ribbonAlpha, 1).setUsage(THREE.DynamicDrawUsage));
  const indices = [];
  for (let i = 0; i < settings.ribbonSegments; i++) {
    const k = i * 2;
    indices.push(k, k + 1, k + 2, k + 1, k + 3, k + 2);
  }
  indices.push(ribbonCount - 3, ribbonCount - 2, ribbonCount - 1);
  ribbonGeometry.setIndex(indices);
  const ribbonMaterial = new THREE.ShaderMaterial({
    uniforms: { uColor: { value: new THREE.Color('#A66A3F') }, uAlpha: { value: 0 } },
    transparent: true, depthWrite: false, depthTest: false, side: THREE.DoubleSide,
    vertexShader: `attribute float aAlpha;varying float vAlpha;void main(){vAlpha=aAlpha;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader: `uniform vec3 uColor;uniform float uAlpha;varying float vAlpha;void main(){gl_FragColor=vec4(uColor,uAlpha*vAlpha);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}`
  });
  const ribbon = new THREE.Mesh(ribbonGeometry, ribbonMaterial);
  ribbon.frustumCulled = false;
  ribbon.renderOrder = 12;
  group.add(ribbon);

  const dustPositions = new Float32Array(settings.particleCount * 3);
  const dustAlpha = new Float32Array(settings.particleCount);
  const dustSize = new Float32Array(settings.particleCount);
  const dustSeeds = new Float32Array(settings.particleCount * 4);
  for (let i = 0; i < dustSeeds.length; i++) dustSeeds[i] = Math.random();
  const dustGeometry = new THREE.BufferGeometry();
  dustGeometry.setAttribute('position', new THREE.BufferAttribute(dustPositions, 3).setUsage(THREE.DynamicDrawUsage));
  dustGeometry.setAttribute('aAlpha', new THREE.BufferAttribute(dustAlpha, 1).setUsage(THREE.DynamicDrawUsage));
  dustGeometry.setAttribute('aSize', new THREE.BufferAttribute(dustSize, 1).setUsage(THREE.DynamicDrawUsage));
  const dustMaterial = new THREE.ShaderMaterial({
    uniforms: { uAlpha: { value: 0 }, uDpr: { value: Math.min(globalThis.devicePixelRatio || 1, 1.75) } },
    transparent: true, depthWrite: false, depthTest: false,
    vertexShader: `attribute float aAlpha;attribute float aSize;uniform float uDpr;varying float vAlpha;void main(){vAlpha=aAlpha;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);gl_PointSize=aSize*uDpr;}`,
    fragmentShader: `uniform float uAlpha;varying float vAlpha;void main(){float d=length(gl_PointCoord-.5)*2.;if(d>1.)discard;vec3 c=mix(vec3(.39,.22,.12),vec3(.65,.42,.25),vAlpha);gl_FragColor=vec4(c,(1.-smoothstep(.35,1.,d))*vAlpha*uAlpha);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}`
  });
  const dust = new THREE.Points(dustGeometry, dustMaterial);
  dust.frustumCulled = false;
  dust.renderOrder = 13;
  group.add(dust);
  group.visible = false;

  let active = null, spawnCount = 0, destroyed = false;
  let lastAngle = -20, lastWord = -1;
  const history = [];
  const source = new THREE.Vector3(), projection = new THREE.Vector3();
  const cameraRight = new THREE.Vector3(), cameraUp = new THREE.Vector3();
  const point = new THREE.Vector3(), nextPoint = new THREE.Vector3(), tangent = new THREE.Vector3();
  const side = new THREE.Vector3(), view = new THREE.Vector3(), offset = new THREE.Vector3();

  function screenPoint(local, target = new THREE.Vector3()) {
    return target.copy(local).applyMatrix4(sculpture.matrixWorld).project(camera);
  }
  function fromScreen(x, y, depth) {
    return new THREE.Vector3(x / width * 2 - 1, 1 - y / height * 2, depth).unproject(camera);
  }
  function safeBox() {
    const bounds = root.getBoundingClientRect();
    const mantra = root.querySelector('.invocation');
    const mantraTop = mantra ? mantra.getBoundingClientRect().top - bounds.top - 24 : height * .77;
    const margin = width < 650 ? 26 : Math.max(46, width * .055);
    return { left: margin, right: width - margin, top: Math.max(88, height * .13), bottom: Math.max(height * .51, Math.min(height * .77, mantraTop)) };
  }
  function limitPoint(p, box) {
    return { x: clamp(p.x, box.left, box.right), y: clamp(p.y, box.top, box.bottom) };
  }
  function makeTrajectory() {
    sculpture.updateMatrixWorld(true);
    camera.updateMatrixWorld(true);
    const samples = [], step = Math.max(1, Math.floor(rest.length / 3 / 900));
    let xmin = Infinity, xmax = -Infinity, ymin = Infinity, ymax = -Infinity;
    for (let i = 0; i < rest.length / 3; i += step) {
      const j = i * 3;
      source.set(rest[j], rest[j + 1], rest[j + 2]);
      screenPoint(source, projection);
      const x = (projection.x + 1) * width * .5, y = (1 - projection.y) * height * .5;
      if (!Number.isFinite(x) || !Number.isFinite(y) || projection.z < -1 || projection.z > 1) continue;
      samples.push({ x, y, depth: projection.z, index: i });
      xmin = Math.min(xmin, x); xmax = Math.max(xmax, x); ymin = Math.min(ymin, y); ymax = Math.max(ymax, y);
    }
    if (!samples.length) return null;
    const center = { x: (xmin + xmax) * .5, y: (ymin + ymax) * .5 };
    const box = safeBox();
    let chosen = null;
    for (let attempt = 0; attempt < 24; attempt++) {
      const angle = range(0, Math.PI * 2), dx = Math.cos(angle), dy = Math.sin(angle);
      if (Math.abs(Math.atan2(Math.sin(angle - lastAngle), Math.cos(angle - lastAngle))) < .42 && attempt < 16) continue;
      // Pick an actual surface sample toward this direction, never the model's
      // bounding-box center (which may be an empty gap in the calligraphy).
      let start = null, best = -Infinity;
      const crossBias = range(-.22, .22);
      for (const s of samples) {
        if (s.x < box.left || s.x > box.right || s.y < box.top || s.y > box.bottom) continue;
        const x = s.x - center.x, y = s.y - center.y;
        const score = x * dx + y * dy - Math.abs(-x * dy + y * dx) * .24 + (-x * dy + y * dx) * crossBias;
        if (score > best) { best = score; start = s; }
      }
      if (!start) continue;
      const roomX = Math.abs(dx) < .0001 ? Infinity : (dx > 0 ? box.right - start.x : start.x - box.left) / Math.abs(dx);
      const roomY = Math.abs(dy) < .0001 ? Infinity : (dy > 0 ? box.bottom - start.y : start.y - box.top) / Math.abs(dy);
      const room = Math.min(roomX, roomY);
      const length = Math.min(room - 8, range(width < 650 ? 78 : 130, width < 650 ? 125 : 230));
      if (length < 47) continue;
      const bend = length * range(.24, .48) * (Math.random() < .5 ? -1 : 1);
      const end = limitPoint({ x: start.x + dx * length, y: start.y + dy * length }, box);
      const c1 = limitPoint({ x: start.x + dx * length * .28 - dy * bend, y: start.y + dy * length * .28 + dx * bend }, box);
      const c2 = limitPoint({ x: start.x + dx * length * .67 + dy * bend * .68, y: start.y + dy * length * .67 - dx * bend * .68 }, box);
      chosen = { start, end, c1, c2, angle, length, box, center };
      break;
    }
    if (!chosen) return null;
    lastAngle = chosen.angle;
    const { start, end, c1, c2 } = chosen;
    const curve = new THREE.CubicBezierCurve3(fromScreen(start.x, start.y, start.depth), fromScreen(c1.x, c1.y, start.depth), fromScreen(c2.x, c2.y, start.depth), fromScreen(end.x, end.y, start.depth));
    const pixelScale = fromScreen(start.x + 1, start.y, start.depth).distanceTo(curve.v0);
    return { ...chosen, curve, pixelScale };
  }
  function spawn(time) {
    const path = makeTrajectory();
    if (!path) return;
    let wordIndex = Math.floor(Math.random() * settings.words.length);
    if (wordIndex === lastWord) wordIndex = (wordIndex + 1 + Math.floor(Math.random() * 2)) % settings.words.length;
    lastWord = wordIndex;
    active = { ...path, born: time, word: settings.words[wordIndex], progress: 0, seed: Math.random() * 100, labelPosition: null };
    spawnCount++;
    const entry = { number: spawnCount, time, word: active.word, sourceIndex: path.start.index, start: { x: path.start.x, y: path.start.y }, end: { ...path.end }, control1: { ...path.c1 }, control2: { ...path.c2 }, lifetime: settings.lifetimeSeconds };
    history.push(entry);
    if (history.length > 16) history.shift();
    label.textContent = active.word;
    label.style.fontSize = width < 650 ? '20px' : '25px';
    label.style.display = 'block';
    group.visible = true;
  }
  function hideArrow() {
    active = null;
    group.visible = false;
    label.style.display = 'none';
    label.style.opacity = '0';
  }
  function setVertex(array, index, value) {
    const k = index * 3; array[k] = value.x; array[k + 1] = value.y; array[k + 2] = value.z;
  }
  function sample(u, target = point) { return active.curve.getPoint(clamp(u, 0, 1), target); }
  function direction(u) {
    sample(u, point); sample(Math.min(1, u + .006), nextPoint);
    if (u > .994) { sample(u - .006, nextPoint); tangent.copy(point).sub(nextPoint); }
    else tangent.copy(nextPoint).sub(point);
    tangent.normalize(); view.copy(camera.position).sub(point).normalize();
    side.crossVectors(tangent, view).normalize();
  }
  function draw(time) {
    if (!active) return;
    const age = (time - active.born) / settings.lifetimeSeconds;
    active.progress = age;
    if (age >= 1) { hideArrow(); return; }
    const head = smooth(0, .77, age), tail = Math.max(0, head - .82 + smooth(.48, 1, age) * .28);
    const dissolve = smooth(.58, 1, age);
    const visibility = smooth(0, .12, age) * (1 - smooth(.65, 1, age));
    const px = active.pixelScale;
    cameraRight.setFromMatrixColumn(camera.matrixWorld, 0).normalize();
    cameraUp.setFromMatrixColumn(camera.matrixWorld, 1).normalize();
    for (let i = 0; i <= settings.ribbonSegments; i++) {
      const fraction = i / settings.ribbonSegments;
      const u = tail + (head - tail) * fraction;
      direction(u);
      const body = Math.sin(Math.PI * Math.min(.99, fraction) * .88);
      const halfWidth = px * (width < 650 ? 2.1 : 2.7) * body * (1 - dissolve * .8);
      offset.copy(side).multiplyScalar(halfWidth);
      setVertex(ribbonPositions, i * 2, nextPoint.copy(point).add(offset));
      setVertex(ribbonPositions, i * 2 + 1, nextPoint.copy(point).sub(offset));
      const alpha = smooth(0, .22, fraction) * (1 - dissolve);
      ribbonAlpha[i * 2] = alpha; ribbonAlpha[i * 2 + 1] = alpha;
    }
    direction(head);
    const tip = point.clone(), wingWidth = px * (width < 650 ? 6.5 : 8.5) * (1 - dissolve * .6);
    const rear = point.clone().addScaledVector(tangent, -px * (width < 650 ? 13 : 17));
    const endIndex = ribbonCount - 3;
    setVertex(ribbonPositions, endIndex, tip);
    setVertex(ribbonPositions, endIndex + 1, nextPoint.copy(rear).addScaledVector(side, wingWidth));
    setVertex(ribbonPositions, endIndex + 2, nextPoint.copy(rear).addScaledVector(side, -wingWidth));
    ribbonAlpha.fill(1 - dissolve, endIndex);
    ribbonMaterial.uniforms.uAlpha.value = visibility * .88;
    ribbonGeometry.attributes.position.needsUpdate = true;
    ribbonGeometry.attributes.aAlpha.needsUpdate = true;
    for (let i = 0; i < settings.particleCount; i++) {
      const k = i * 4, seed = dustSeeds[k], signed = dustSeeds[k + 1] * 2 - 1;
      const u = tail + (head - tail) * seed;
      sample(u, point);
      const phase = active.seed + seed * 18 + age * (3 + dustSeeds[k + 2] * 5);
      const spread = (1.4 + dissolve * (10 + dustSeeds[k + 3] * 17)) * px;
      point.addScaledVector(cameraRight, (Math.sin(phase) * .6 + signed) * spread);
      point.addScaledVector(cameraUp, (Math.cos(phase * .83) * .6 + dustSeeds[k + 2] - .5) * spread);
      setVertex(dustPositions, i, point);
      dustAlpha[i] = (.25 + dustSeeds[k + 1] * .75) * smooth(0, .15, seed) * (1 - dissolve * .35);
      dustSize[i] = 1.1 + dustSeeds[k + 3] * 1.7;
    }
    dustMaterial.uniforms.uAlpha.value = visibility * (.48 + dissolve * .7);
    dustGeometry.attributes.position.needsUpdate = true;
    dustGeometry.attributes.aAlpha.needsUpdate = true;
    dustGeometry.attributes.aSize.needsUpdate = true;
    const labelU = clamp(head * .62 + .04, tail, head);
    sample(labelU, projection).project(camera);
    const labelX = clamp((projection.x + 1) * width * .5, active.box.left + 35, active.box.right - 35);
    const labelY = clamp((1 - projection.y) * height * .5 - 15, active.box.top + 15, active.box.bottom - 20);
    active.labelPosition = { x: labelX, y: labelY };
    label.style.transform = `translate(${labelX.toFixed(2)}px,${labelY.toFixed(2)}px) translate(-50%,-100%)`;
    label.style.opacity = String(smooth(.10, .26, age) * (1 - smooth(.70, .98, age)));
  }
  return {
    update({ time, dt, ready, reduced, hoveringLogo, width: nextWidth, height: nextHeight }) {
      if (destroyed) return;
      if (Number.isFinite(nextWidth) && nextWidth > 0) width = nextWidth;
      if (Number.isFinite(nextHeight) && nextHeight > 0) height = nextHeight;
      if (!ready || reduced) {
        clock.update(time, false, hoveringLogo, reduced);
        hideArrow();
        return;
      }
      if (clock.update(time, true, hoveringLogo, false)) spawn(time);
      // A cursor returning to the logo cancels new emissions. The existing
      // short-lived arrow finishes naturally, avoiding a visible hard cut.
      draw(time);
    },
    reset(time = 0) { clock.reset(time); hideArrow(); },
    suspend(time = clock.lastTime) { clock.suspend(time); hideArrow(); },
    dispose() {
      if (destroyed) return;
      destroyed = true; hideArrow(); scene.remove(group); overlay.remove();
      ribbonGeometry.dispose(); ribbonMaterial.dispose(); dustGeometry.dispose(); dustMaterial.dispose();
    },
    inspect() {
      return {
        spawnCount, nextAt: clock.nextAt, hovering: clock.hovering, ready: clock.ready,
        lifetimeSeconds: settings.lifetimeSeconds, idleSeconds: settings.idleSeconds,
        active: active ? { word: active.word, born: active.born, progress: active.progress,
          start: { x: active.start.x, y: active.start.y }, end: { ...active.end },
          sourceIndex: active.start.index, labelPosition: active.labelPosition } : null,
        history: history.map(item => ({ ...item, start: { ...item.start }, end: { ...item.end }, control1: { ...item.control1 }, control2: { ...item.control2 } }))
      };
    }
  };
}
