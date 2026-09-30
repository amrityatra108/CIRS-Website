// Terrain occlusion for the fixed-camera Tapovan video. The source has no depth
// map: these hand-keyed masks are a deliberately limited 2.5D foreground proxy.
// Supply the *presented* video's mediaTime, not a scroll-predicted target time.

const clamp = (value, a = 0, b = 1) => Math.max(a, Math.min(b, value));
const lerp = (a, b, t) => a + (b - a) * t;
const smooth = (a, b, value) => {
  const t = clamp((value - a) / Math.max(0.00001, b - a));
  return t * t * (3 - 2 * t);
};

function enclosingKeys(frames, time) {
  if (!frames?.length) return null;
  if (time <= frames[0].time) return [frames[0], frames[0], 0];
  const last = frames.length - 1;
  if (time >= frames[last].time) return [frames[last], frames[last], 0];
  let low = 0, high = last;
  while (high - low > 1) {
    const mid = (low + high) >> 1;
    if (frames[mid].time <= time) low = mid;
    else high = mid;
  }
  return [frames[low], frames[high],
    clamp((time - frames[low].time) /
      Math.max(0.00001, frames[high].time - frames[low].time))];
}

function sampleLine(xs, ys, x) {
  if (!xs?.length || !ys?.length) return 1;
  if (x <= xs[0]) return ys[0];
  const last = Math.min(xs.length, ys.length) - 1;
  if (x >= xs[last]) return ys[last];
  let low = 0, high = last;
  while (high - low > 1) {
    const mid = (low + high) >> 1;
    if (xs[mid] <= x) low = mid;
    else high = mid;
  }
  return lerp(ys[low], ys[high],
    clamp((x - xs[low]) / Math.max(0.00001, xs[high] - xs[low])));
}

export function sampleRidge(profiles, time, sourceX) {
  const keys = enclosingKeys(profiles?.keyframes, time);
  if (!keys) return 1;
  const [before, after, blend] = keys;
  return lerp(
    sampleLine(profiles.sampleX, before.ridgeY, sourceX),
    sampleLine(profiles.sampleX, after.ridgeY, sourceX), blend
  );
}

function samplePolygon(track, time) {
  const keys = enclosingKeys(track.keyframes, time);
  if (!keys) return null;
  const [before, after, blend] = keys;
  if (before.polygon.length !== after.polygon.length) return before.polygon;
  return before.polygon.map((point, i) => [
    lerp(point[0], after.polygon[i][0], blend),
    lerp(point[1], after.polygon[i][1], blend)
  ]);
}

function trackStrength(track, time) {
  const [start, end] = track.active;
  if (time < start || time > end) return 0;
  const fade = Math.max(0.001, track.fadeSeconds || 0.12);
  return Math.min(smooth(start, start + fade, time),
    1 - smooth(end - fade, end, time));
}

function pointInPolygon(x, y, polygon) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const a = polygon[i], b = polygon[j];
    if ((a[1] > y) !== (b[1] > y) &&
      x < (b[0] - a[0]) * (y - a[1]) /
      (b[1] - a[1]) + a[0]) inside = !inside;
  }
  return inside;
}

export function sampleCloudAlpha(cloud, time, sourceX, sourceY) {
  const keys = enclosingKeys(cloud?.keyframes, time);
  if (!keys) return 0;
  const [before, after, blend] = keys;
  const strength = lerp(before.strength, after.strength, blend);
  if (strength <= 0) return 0;
  const boundary = lerp(
    sampleLine(cloud.sampleX, before.boundary, sourceX),
    sampleLine(cloud.sampleX, after.boundary, sourceX), blend
  );
  const feather = cloud.feather || 0.07;
  return strength * smooth(boundary - feather, boundary + feather, sourceY);
}

// CSS object-fit:cover/object-position percentage mapping. Coordinates are
// normalized against the 1920x1080 source and the current viewport respectively.
export function createCoverMapping({
  sourceWidth = 1920, sourceHeight = 1080,
  viewportWidth, viewportHeight, positionX = 0.5, positionY = 0.5
}) {
  const width = Math.max(1, viewportWidth), height = Math.max(1, viewportHeight);
  const scale = Math.max(width / sourceWidth, height / sourceHeight);
  const drawnWidth = sourceWidth * scale;
  const drawnHeight = sourceHeight * scale;
  const cropX = (drawnWidth - width) * clamp(positionX);
  const cropY = (drawnHeight - height) * clamp(positionY);
  return {
    sourceWidth, sourceHeight, viewportWidth: width, viewportHeight: height,
    positionX, positionY, scale, cropX, cropY, drawnWidth, drawnHeight,
    sourceToViewport(x, y) {
      return [(x * drawnWidth - cropX) / width,
        (y * drawnHeight - cropY) / height];
    },
    viewportToSource(x, y) {
      return [(x * width + cropX) / drawnWidth,
        (y * height + cropY) / drawnHeight];
    }
  };
}

function positionFraction(token, fallback) {
  if (!token) return fallback;
  if (token === 'left' || token === 'top') return 0;
  if (token === 'center') return 0.5;
  if (token === 'right' || token === 'bottom') return 1;
  if (token.endsWith('%')) return clamp(Number.parseFloat(token) / 100);
  return fallback;
}

export function currentVideoCoverMapping(video, stage, sourceWidth = 1920,
  sourceHeight = 1080) {
  const style = getComputedStyle(video);
  const position = style.objectPosition.trim().split(/\s+/);
  const positionX = positionFraction(position[0], 0.5);
  const positionY = positionFraction(position[1], 0.5);
  return createCoverMapping({
    sourceWidth, sourceHeight,
    viewportWidth: stage.clientWidth,
    viewportHeight: stage.clientHeight,
    positionX, positionY
  });
}

const DEPTH_MASK_VERTEX = `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;

// Depth-only fractional coverage. At the cloud edge, deterministic subpixel
// dithering reveals the already-colour-graded HTML video beneath the stones.
const DEPTH_MASK_FRAGMENT = `
uniform sampler2D uMask;
varying vec2 vUv;
float noise(vec2 pixel) {
  return fract(52.9829189 * fract(dot(pixel, vec2(0.06711056, 0.00583715))));
}
void main() {
  float coverage = texture2D(uMask, vUv).a;
  if (coverage <= noise(floor(gl_FragCoord.xy))) discard;
  gl_FragColor = vec4(1.0);
}`;

function makeDepthPlane(THREE, camera, distance, renderOrder, width) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = Math.round(width * 9 / 16);
  const context = canvas.getContext('2d');
  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.generateMipmaps = false;
  const material = new THREE.ShaderMaterial({
    uniforms: { uMask: { value: texture } },
    vertexShader: DEPTH_MASK_VERTEX,
    fragmentShader: DEPTH_MASK_FRAGMENT,
    side: THREE.DoubleSide,
    depthTest: true,
    depthWrite: true,
    colorWrite: false,
    transparent: false,
    toneMapped: false
  });
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), material);
  plane.position.z = -distance;
  plane.renderOrder = renderOrder;
  plane.frustumCulled = false;
  camera.add(plane);
  return { canvas, context, texture, material, plane, distance };
}

function scaleDepthPlane(THREE, layer, camera, mapping, canvasWidth) {
  const height = 2 * layer.distance *
    Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  layer.plane.scale.set(height * camera.aspect, height, 1);
  layer.canvas.width = canvasWidth;
  layer.canvas.height = Math.max(2,
    Math.round(canvasWidth * mapping.viewportHeight / mapping.viewportWidth));
  layer.texture.needsUpdate = true;
}

function drawPolygon(context, polygon, mapping, canvas) {
  context.beginPath();
  polygon.forEach(([sourceX, sourceY], index) => {
    const [x, y] = mapping.sourceToViewport(sourceX, sourceY);
    if (index === 0) context.moveTo(x * canvas.width, y * canvas.height);
    else context.lineTo(x * canvas.width, y * canvas.height);
  });
  context.closePath();
  context.fill();
}

function drawSilhouette(layer, profiles, time, mapping) {
  const { canvas, context } = layer;
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = '#fff';
  const polygon = profiles.sampleX.map(x =>
    [x, sampleRidge(profiles, time, x)]);
  polygon.push([1, 1], [0, 1]);
  drawPolygon(context, polygon, mapping, canvas);
  layer.texture.needsUpdate = true;
}

function drawHoldout(layer, track, time, mapping) {
  const strength = trackStrength(track, time);
  layer.plane.visible = strength > 0.001;
  if (!layer.plane.visible) return;
  const { canvas, context } = layer;
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = '#fff';
  context.globalAlpha = strength;
  drawPolygon(context, samplePolygon(track, time), mapping, canvas);
  context.globalAlpha = 1;
  layer.texture.needsUpdate = true;
}

function drawCloud(layer, cloud, time, mapping) {
  const { canvas, context } = layer;
  const width = canvas.width, height = canvas.height;
  const keys = enclosingKeys(cloud.keyframes, time);
  const [before, after, blend] = keys;
  const strength = lerp(before.strength, after.strength, blend);
  if (strength <= 0.001) {
    layer.plane.visible = false;
    return;
  }
  const pixels = context.createImageData(width, height);
  const data = pixels.data;
  let hasCoverage = false;
  const sourceY = new Float32Array(height);
  for (let iy = 0; iy < height; iy++) {
    sourceY[iy] = mapping.viewportToSource(0, (iy + 0.5) / height)[1];
  }
  const feather = cloud.feather || 0.07;
  for (let ix = 0; ix < width; ix++) {
    const sourceX = mapping.viewportToSource((ix + 0.5) / width, 0)[0];
    const boundary = lerp(
      sampleLine(cloud.sampleX, before.boundary, sourceX),
      sampleLine(cloud.sampleX, after.boundary, sourceX), blend
    );
    for (let iy = 0; iy < height; iy++) {
      const alpha = Math.round(255 * strength *
        smooth(boundary - feather, boundary + feather, sourceY[iy]));
      if (alpha) hasCoverage = true;
      const offset = (iy * width + ix) * 4;
      data[offset] = data[offset + 1] = data[offset + 2] = 255;
      data[offset + 3] = alpha;
    }
  }
  layer.plane.visible = hasCoverage;
  if (hasCoverage) {
    context.putImageData(pixels, 0, 0);
    layer.texture.needsUpdate = true;
  }
}

export async function createTapovanTerrain({
  THREE, scene, camera, stage, video,
  profiles: suppliedProfiles, holdouts: suppliedHoldouts,
  silhouetteDistance = 24,
  cloudDistance,
  distanceOverrides = {},
  canvasWidth = 512
}) {
  if (!THREE || !scene || !camera || !stage || !video) {
    throw new Error('Tapovan terrain requires THREE, scene, camera, stage and video');
  }
  const [profiles, holdouts] = await Promise.all([
    suppliedProfiles || fetch(new URL('../assets/mountain-mattes/mountain-foreground-profiles.json',
      import.meta.url)).then(response => {
      if (!response.ok) throw new Error('Mountain silhouette data unavailable');
      return response.json();
    }),
    suppliedHoldouts || fetch(new URL('../assets/mountain-mattes/mountain-local-holdouts.json',
      import.meta.url)).then(response => {
      if (!response.ok) throw new Error('Mountain holdout data unavailable');
      return response.json();
    })
  ]);
  const sourceWidth = profiles.sourceWidth || 1920;
  const sourceHeight = profiles.sourceHeight || 1080;
  if (holdouts.sourceWidth !== sourceWidth ||
      holdouts.sourceHeight !== sourceHeight) {
    throw new Error('Mountain mask and video source dimensions differ');
  }
  if (!camera.parent) scene.add(camera);
  const silhouette = makeDepthPlane(THREE, camera,
    silhouetteDistance, -120, canvasWidth);
  const tracks = holdouts.tracks.map((track, index) => ({
    track,
    layer: makeDepthPlane(THREE, camera,
      distanceOverrides[track.id] || track.distance, -110 + index,
      canvasWidth)
  }));
  const clouds = makeDepthPlane(THREE, camera,
    cloudDistance || holdouts.cloud.distance, -100, canvasWidth);
  const layers = [silhouette, ...tracks.map(({ layer }) => layer), clouds];
  let mapping = null;
  let layoutKey = '';
  let lastTime = Number.NaN;
  let disposed = false;

  function refreshMapping() {
    const next = currentVideoCoverMapping(video, stage, sourceWidth, sourceHeight);
    const key = [next.viewportWidth, next.viewportHeight,
      next.positionX, next.positionY, camera.fov, camera.aspect].join(':');
    if (key === layoutKey) return false;
    layoutKey = key;
    mapping = next;
    layers.forEach(layer => scaleDepthPlane(THREE, layer, camera,
      mapping, canvasWidth));
    lastTime = Number.NaN;
    return true;
  }

  function update(presentedMediaTime) {
    if (disposed || !Number.isFinite(presentedMediaTime)) return;
    refreshMapping();
    if (Math.abs(lastTime - presentedMediaTime) < 1 / 60) return;
    lastTime = presentedMediaTime;
    drawSilhouette(silhouette, profiles, presentedMediaTime, mapping);
    tracks.forEach(({ track, layer }) =>
      drawHoldout(layer, track, presentedMediaTime, mapping));
    drawCloud(clouds, holdouts.cloud, presentedMediaTime, mapping);
  }

  function sampleAt(sourceX, sourceY, time, cameraDistance) {
    const rock = cameraDistance > silhouette.distance &&
      sourceY >= sampleRidge(profiles, time, sourceX);
    const local = tracks.filter(({ layer, track }) =>
      cameraDistance > layer.distance && trackStrength(track, time) > 0.5 &&
      pointInPolygon(sourceX, sourceY, samplePolygon(track, time))
    ).map(({ track }) => track.id);
    const cloud = cameraDistance > clouds.distance ?
      sampleCloudAlpha(holdouts.cloud, time, sourceX, sourceY) : 0;
    return { rock, local, cloud };
  }

  function dispose() {
    if (disposed) return;
    disposed = true;
    layers.forEach(layer => {
      camera.remove(layer.plane);
      layer.plane.geometry.dispose();
      layer.material.dispose();
      layer.texture.dispose();
    });
  }

  refreshMapping();
  return {
    profiles, holdouts,
    update, resize: refreshMapping,
    getMapping: () => mapping,
    sampleAt, dispose,
    planes: {
      silhouette: silhouette.plane,
      holdouts: Object.fromEntries(tracks.map(({ track, layer }) =>
        [track.id, layer.plane])),
      clouds: clouds.plane
    }
  };
}
