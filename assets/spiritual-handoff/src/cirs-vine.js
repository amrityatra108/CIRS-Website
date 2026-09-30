// The exact Final Vine.html painting, baked once into one alpha atlas.
// All twenty quads share one draw call. No runtime cropping, GSAP ticker,
// canvas extraction, texture upload loop, or additional WebGL renderer.
(() => {
  const data = window.CIRS_KALAMKARI;
  const angleAt = (layer, seconds) => -layer.amplitude * data.strength *
    Math.cos(Math.PI * (seconds + layer.phase) / layer.duration);
  window.CirsKalamkariMotion = Object.freeze({ angleAt });
  window.createCirsKalamkariVine = ({ THREE: T, axis, renderer, requestFrame }) => {
    if (!data || data.layers.length !== 20) throw Error('Kalamkari layer manifest is unavailable.');
    const unit = 13.2 / data.viewBox[3];
    const centerX = data.viewBox[0] + data.viewBox[2] / 2;
    const centerY = data.viewBox[1] + data.viewBox[3] / 2;
    const originY = 1.0;
    const positions = [], uvs = [], pivots = [], motions = [], indices = [];
    const [atlasWidth, atlasHeight] = data.atlasSize;
    for (const [index, layer] of data.layers.entries()) {
      const [left, top, right, bottom] = layer.sourceBounds;
      const [x, y, width, height] = layer.atlasBounds;
      const corners = [[left, top, x, y], [right, top, x + width, y],
        [right, bottom, x + width, y + height], [left, bottom, x, y + height]];
      for (const [px, py, tx, ty] of corners) {
        positions.push((px - centerX) * unit, (centerY - py) * unit + originY, 0);
        uvs.push(tx / atlasWidth, 1 - ty / atlasHeight);
        pivots.push((layer.pivot[0] - centerX) * unit, (centerY - layer.pivot[1]) * unit + originY);
        motions.push(layer.amplitude * data.strength * Math.PI / 180, layer.duration, layer.phase);
      }
      const i = index * 4; indices.push(i, i + 2, i + 1, i, i + 3, i + 2);
    }
    const geometry = new T.BufferGeometry();
    geometry.setAttribute('position', new T.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('uv', new T.Float32BufferAttribute(uvs, 2));
    geometry.setAttribute('aVinePivot', new T.Float32BufferAttribute(pivots, 2));
    geometry.setAttribute('aVineMotion', new T.Float32BufferAttribute(motions, 3));
    geometry.setIndex(indices); geometry.computeBoundingSphere();
    geometry.boundingSphere.radius += .2; // The authored ±14° wings stay within this margin.
    const timeUniform = { value: 0 };
    let disposed = false, loaded = false, travel = 0;
    let resolveReady, rejectReady;
    const ready = new Promise((resolve, reject) => { resolveReady = resolve; rejectReady = reject; });
    const texture = new T.TextureLoader().load(`assets/kalamkari/${data.atlas}`, () => {
      if (disposed) { texture.dispose(); resolveReady(false); return; }
      loaded = true; resolveReady(true); requestFrame();
    }, undefined, rejectReady);
    texture.encoding = T.sRGBEncoding;
    texture.generateMipmaps = false;
    texture.minFilter = texture.magFilter = T.LinearFilter;
    texture.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
    const material = new T.MeshBasicMaterial({ map: texture, transparent: true,
      depthTest: true, depthWrite: false, side: T.DoubleSide, toneMapped: false, fog: false });
    material.onBeforeCompile = shader => {
      shader.uniforms.uVineTime = timeUniform;
      shader.vertexShader = shader.vertexShader.replace('#include <common>', `#include <common>
        attribute vec2 aVinePivot;
        attribute vec3 aVineMotion;
        uniform float uVineTime;`);
      shader.vertexShader = shader.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
        // SVG positive rotation is clockwise (y down). Convert to Three y up.
        // This cosine is exactly the source's sine.inOut repeated yoyo tween.
        float angle = aVineMotion.x * cos(3.141592653589793 * (uVineTime + aVineMotion.z) / aVineMotion.y);
        float c = cos(angle), s = sin(angle);
        vec2 local = transformed.xy - aVinePivot;
        transformed.xy = aVinePivot + vec2(c * local.x - s * local.y, s * local.x + c * local.y);`);
    };
    material.customProgramCacheKey = () => 'cirs-kalamkari-source-motion-v1';
    const mesh = new T.Mesh(geometry, material);
    mesh.name = 'authored-kalamkari-vine-20-layer-batch';
    mesh.raycast = () => {}; // Panel selection alone owns pointer input.
    axis.add(mesh);
    return {
      ready,
      setTravel(value) { travel = value; axis.rotation.y = 0; },
      animate(activeMilliseconds) { timeUniform.value = Math.max(0, activeMilliseconds) * .001; },
      inspect() { return { kind: 'authored-kalamkari', ready: loaded, sourceSha256: data.sourceSha256,
        activeSeconds: timeUniform.value, globalTravel: travel, viewBox: data.viewBox,
        worldHeight: 13.2, depth: { test: material.depthTest, write: material.depthWrite, renderOrder: mesh.renderOrder, z: axis.position.z }, staticLayers: 1, animatedLayers: 19, drawCalls: 1,
        layers: data.layers.slice(1).map(layer => ({ name: layer.name, degrees: angleAt(layer, timeUniform.value),
          pivot: layer.pivot, duration: layer.duration, amplitude: layer.amplitude, phase: layer.phase })) }; },
      dispose() { if (disposed) return; disposed = true; axis.remove(mesh); geometry.dispose(); material.dispose(); texture.dispose(); }
    };
  };
})();
