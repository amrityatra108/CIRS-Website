/* Spiritual Life: one Three.js scene, four draw calls, and an actual camera passage.
   Reuse the site's MIT-licensed Three r186; the page controller owns the RAF.
   All motion follows render(progress, seconds, pointerX, pointerY) directly. */
import * as THREE from "../founder-opening/vendor/three.module.min.js";

const TAU = Math.PI * 2;
const GOLD = new THREE.Color("#c8ab79");
const IVORY = new THREE.Color("#eee4cd");

function clamp(value, min = 0, max = 1) {
  return Math.min(max, Math.max(min, Number(value) || 0));
}

function phase(progress, start, end) {
  return clamp((progress - start) / (end - start));
}

function smooth(value) {
  return value * value * (3 - 2 * value);
}

function randomSequence() {
  let seed = 4319;
  return () => {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };
}

function createSacredGeometry(compact) {
  const layers = [];
  const steps = compact ? 144 : 288;

  // Each band is a single draw call. Small depth variation within a band and
  // the wider separation between bands remain real world-space coordinates.
  for (let layer = 0; layer < 3; layer++) {
    const vertices = [];
    const colours = [];

    function vertex(position, brightness, highlight = 0) {
      vertices.push(...position);
      const colour = GOLD.clone().lerp(IVORY, highlight).multiplyScalar(brightness);
      colours.push(colour.r, colour.g, colour.b);
    }

    function curve(radius, depth, brightness, petals = 0, amplitude = 0, offset = 0, dashed = false) {
      function position(angle) {
        const r = radius + Math.cos(angle * petals + offset) * amplitude;
        return [Math.cos(angle) * r, Math.sin(angle) * r,
          depth + Math.sin(angle * 3 + offset) * amplitude * 0.7];
      }
      for (let i = 0; i < steps; i++) {
        if (dashed && i % 6 === 0) continue;
        const angle = i / steps * TAU;
        const highlight = Math.pow(Math.max(0, Math.cos(angle - 1.1)), 8) * 0.32;
        vertex(position(angle), brightness, highlight);
        vertex(position((i + 1) / steps * TAU), brightness, highlight);
      }
    }

    if (layer === 0) {
      curve(1.13, 0.035, 0.56);
      curve(1.16, 0, 0.29);
      curve(1.31, -0.015, 0.75, 12, 0.088);
      curve(1.35, -0.075, 0.46, 12, 0.09, Math.PI);
      curve(1.46, -0.1, 0.52);
    } else if (layer === 1) {
      curve(1.51, 0.065, 0.56);
      curve(1.54, 0.015, 0.27, 0, 0, 0, true);
      curve(1.73, -0.015, 0.76, 12, 0.16);
      curve(1.73, -0.08, 0.43, 12, 0.16, Math.PI);
      curve(1.94, -0.11, 0.49);
    } else {
      curve(1.98, 0.04, 0.40);
      curve(2.03, 0, 0.55, 24, 0.032);
      curve(2.14, -0.045, 0.29, 0, 0, 0, true);

      const marks = compact ? 72 : 144;
      for (let i = 0; i < marks; i++) {
        const angle = i / marks * TAU;
        const principal = i % (marks / 12) === 0;
        const inner = principal ? 2.155 : 2.164;
        const outer = principal ? 2.24 : 2.19;
        vertex([Math.cos(angle) * inner, Math.sin(angle) * inner, -0.1], principal ? 0.7 : 0.35);
        vertex([Math.cos(angle) * outer, Math.sin(angle) * outer, -0.1], principal ? 0.7 : 0.35);
      }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colours, 3));
    geometry.computeBoundingSphere();
    const material = new THREE.LineBasicMaterial({
      vertexColors: true, transparent: true, opacity: 0.75,
      depthWrite: false, toneMapped: false,
    });
    const lines = new THREE.LineSegments(geometry, material);
    lines.name = ["inner-filigree", "interwoven-band", "outer-light-ring"][layer];
    lines.userData.baseZ = 0.72 - layer * 0.72;
    lines.userData.baseOpacity = [0.79, 0.72, 0.64][layer];
    layers.push(lines);
  }
  return layers;
}

function createParticles(compact) {
  const random = randomSequence();
  const count = compact ? 360 : 960;
  const vertices = new Float32Array(count * 3);
  const colours = new Float32Array(count * 3);

  for (let i = 0; i < count; i++) {
    // Most light follows the bands. The distant field follows sparse, curved
    // arcs, rather than a uniform random rectangle of stars.
    const distant = i > count * 0.82;
    const band = i % 5;
    const angle = random() * TAU + band * 0.43;
    const radius = distant ? 2.6 + random() * 4.0 : 1.19 + band * 0.235 + (random() - 0.5) * 0.14;
    const z = distant ? -3.0 - random() * 7 : 0.6 - band * 0.35 + Math.sin(angle * 3) * 0.16 + random() * 0.25;
    vertices[i * 3] = Math.cos(angle) * radius;
    vertices[i * 3 + 1] = Math.sin(angle) * radius;
    vertices[i * 3 + 2] = z;
    const colour = GOLD.clone().lerp(IVORY, random() * 0.3)
      .multiplyScalar(distant ? 0.17 + random() * 0.27 : 0.40 + random() * 0.60);
    colours.set([colour.r, colour.g, colour.b], i * 3);
  }

  // A 16px procedural soft disc prevents square points. No external texture,
  // loading dependency, bloom pass, or custom shader is needed.
  const pixels = new Uint8Array(16 * 16 * 4);
  for (let y = 0; y < 16; y++) {
    for (let x = 0; x < 16; x++) {
      const distance = Math.hypot((x - 7.5) / 7.5, (y - 7.5) / 7.5);
      const offset = (y * 16 + x) * 4;
      pixels[offset] = pixels[offset + 1] = pixels[offset + 2] = 255;
      pixels[offset + 3] = Math.round(255 * Math.pow(Math.max(0, 1 - distance), 1.2));
    }
  }
  const texture = new THREE.DataTexture(pixels, 16, 16, THREE.RGBAFormat);
  texture.magFilter = THREE.LinearFilter;
  texture.minFilter = THREE.LinearFilter;
  texture.generateMipmaps = false;
  texture.needsUpdate = true;
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colours, 3));
  const material = new THREE.PointsMaterial({
    size: compact ? 0.025 : 0.021,
    sizeAttenuation: true, vertexColors: true, map: texture,
    transparent: true, opacity: 0.65, depthWrite: false,
    toneMapped: false, alphaTest: 0.01,
  });
  const particles = new THREE.Points(geometry, material);
  particles.name = "orbital-light-and-distant-dust";
  return particles;
}

// Smooth derivatives at each stop avoid abrupt changes in camera velocity.
function cameraPosition(progress, compact) {
  const stops = compact
    ? [[0, 12.8], [0.15, 12.62], [0.40, 5.6], [0.70, -1.25], [0.90, -3.4], [1, -3.7]]
    : [[0, 12.0], [0.15, 11.82], [0.40, 5.2], [0.70, -1.25], [0.90, -3.8], [1, -4.2]];
  for (let i = 1; i < stops.length; i++) {
    if (progress <= stops[i][0]) {
      const [startProgress, startZ] = stops[i - 1];
      const [endProgress, endZ] = stops[i];
      const t = smooth(phase(progress, startProgress, endProgress));
      return THREE.MathUtils.lerp(startZ, endZ, t);
    }
  }
  return stops[stops.length - 1][1];
}

export function createSpiritualScene(canvas, options = {}) {
  if (!canvas || !canvas.getContext) return null;
  const compact = !!options.compact;
  const reducedMotion = !!options.reducedMotion;
  let context;
  let renderer;
  try {
    // Testing support first avoids Three's error logging on unavailable WebGL.
    context = canvas.getContext("webgl2", {
      alpha: true, antialias: true, depth: true, stencil: false,
      powerPreference: "low-power", failIfMajorPerformanceCaveat: true,
    });
    if (!context) return null;
    renderer = new THREE.WebGLRenderer({ canvas, context, alpha: true, antialias: true });
  } catch (error) {
    return null;
  }
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0x000000, 0);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, compact ? 1.25 : 1.5));

  const scene = new THREE.Scene();
  scene.name = "CIRS-sacred-light";
  const camera = new THREE.PerspectiveCamera(compact ? 43 : 42, 1, 0.025, 60);
  const structure = new THREE.Group();
  const layers = createSacredGeometry(compact);
  const particles = createParticles(compact);
  layers.forEach(layer => structure.add(layer));
  scene.add(structure, particles);

  let destroyed = false;
  let contextUnavailable = false;
  let previousTime = null;
  let pointer = { x: 0, y: 0 };
  let lastFrame = [0, 0, 0, 0];
  let lastProgress = 0;

  function updateScene(progress, seconds, pointerX, pointerY) {
    const p = clamp(progress);
    const time = reducedMotion ? 0 : Math.max(0, Number(seconds) || 0);
    const delta = previousTime === null ? 1 / 60 : clamp(time - previousTime, 0, 0.1);
    previousTime = time;
    const response = 1 - Math.exp(-delta * 3.6);
    pointer.x += ((compact || reducedMotion ? 0 : clamp(pointerX, -1, 1)) - pointer.x) * response;
    pointer.y += ((compact || reducedMotion ? 0 : clamp(pointerY, -1, 1)) - pointer.y) * response;

    const passage = reducedMotion ? 0 : smooth(phase(p, 0.15, 0.76));
    const dissolve = reducedMotion ? 1 - smooth(phase(p, 0.30, 0.80)) : 1 - smooth(phase(p, 0.76, 0.98));
    const breath = 1 + Math.sin(time * 0.20) * 0.0075;
    structure.scale.setScalar(breath);
    structure.rotation.x = 0.055 + pointer.y * 0.026;
    structure.rotation.y = -0.045 + pointer.x * 0.043;

    layers.forEach((layer, index) => {
      layer.position.z = layer.userData.baseZ + (1 - index) * passage * (compact ? 0.64 : 0.85);
      layer.rotation.z = time * (index === 1 ? -0.0055 : 0.004) + passage * (index === 1 ? -0.17 : 0.13);
      layer.rotation.x = Math.sin(time * 0.085 + index * 1.4) * 0.018;
      layer.material.opacity = layer.userData.baseOpacity * dissolve;
    });

    particles.rotation.z = time * 0.0028 + passage * 0.035;
    particles.rotation.x = Math.sin(time * 0.065) * 0.008;
    particles.material.opacity = 0.65 * (1 - smooth(phase(p, reducedMotion ? 0.3 : 0.58, 1)));

    camera.position.set(pointer.x * 0.038, -pointer.y * 0.025,
      reducedMotion ? cameraPosition(0, compact) : cameraPosition(p, compact));
    // Keep the camera facing through the aperture even after it has passed it.
    // Looking back at the origin would turn the view around halfway through.
    camera.rotation.set(0, 0, 0);
    lastProgress = p;
  }

  function render(progress = 0, seconds = 0, pointerX = 0, pointerY = 0) {
    if (destroyed || contextUnavailable) return false;
    lastFrame = [progress, seconds, pointerX, pointerY];
    updateScene(...lastFrame);
    renderer.render(scene, camera);
    return true;
  }

  function resize() {
    if (destroyed || contextUnavailable) return;
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.round(rect.width));
    const height = Math.max(1, Math.round(rect.height));
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, compact ? 1.25 : 1.5));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  function contextLost(event) {
    event.preventDefault();
    contextUnavailable = true;
    canvas.dataset.webgl = "lost";
  }

  function contextRestored() {
    if (destroyed) return;
    contextUnavailable = false;
    canvas.dataset.webgl = "ready";
    resize();
    render(...lastFrame);
  }

  function destroy() {
    if (destroyed) return;
    destroyed = true;
    canvas.removeEventListener("webglcontextlost", contextLost);
    canvas.removeEventListener("webglcontextrestored", contextRestored);
    scene.traverse(object => {
      if (object.geometry) object.geometry.dispose();
      if (object.material) {
        if (object.material.map) object.material.map.dispose();
        object.material.dispose();
      }
    });
    renderer.dispose();
    delete canvas.dataset.webgl;
  }

  function getDiagnostics() {
    return {
      revision: THREE.REVISION,
      progress: lastProgress,
      cameraZ: camera.position.z,
      layerZ: layers.map(layer => layer.position.z),
      particles: particles.geometry.attributes.position.count,
      drawCalls: renderer.info.render.calls,
      pixelRatio: renderer.getPixelRatio(),
      reducedMotion,
      contextUnavailable,
      destroyed,
    };
  }

  canvas.addEventListener("webglcontextlost", contextLost, false);
  canvas.addEventListener("webglcontextrestored", contextRestored, false);
  resize();
  render();
  canvas.dataset.webgl = "ready";
  return { render, resize, destroy, getDiagnostics };
}
