// The room/altar is a locked photographic plate. Only the exact Chinmaya
// outline above it is 3D; camera, crop, plaque and contact shadow share one layout.
export function sanctuaryLayout(width, height) {
  const portrait = width / height < .8;
  const source = portrait ? [941, 1672] : [1661, 947];
  const scale = Math.max(width / source[0], height / source[1]);
  const imageWidth = source[0] * scale, imageHeight = source[1] * scale;
  const left = (width - imageWidth) / 2, top = (height - imageHeight) / 2;
  const plaque = portrait ? [.50, .692, .413, .043] : [.501, .748, .286, .067];
  // Desktop reference: the marble emblem settles slightly into the altar's
  // contact plane, with its top loop centred beneath the room's curved rim.
  const emblem = portrait ? [.5, .359, .475] : [.5, .374, .527];
  return { portrait, source, left, top, imageWidth, imageHeight,
    plaque: { x: left + imageWidth * plaque[0], y: top + imageHeight * plaque[1], width: imageWidth * plaque[2], height: imageHeight * plaque[3] },
    emblem: { x: left + imageWidth * emblem[0], y: top + imageHeight * emblem[1], height: imageHeight * emblem[2] },
    shadow: { x: left + imageWidth * .5, y: top + imageHeight * (portrait ? .632 : .641), width: imageWidth * (portrait ? .32 : .16), height: imageHeight * .016 }
  };
}

export function createMarbleSanctuary({ THREE, scene, root }) {
  const group = new THREE.Group(); group.name = 'marble-sanctuary-lighting'; scene.add(group);
  group.add(new THREE.HemisphereLight(0xfffcf6, 0xded5c3, .72));
  const key = new THREE.DirectionalLight(0xfff7e9, 1.8); key.position.set(-4.4, 7.4, 4.5); group.add(key);
  const fill = new THREE.DirectionalLight(0xe9f1fa, .52); fill.position.set(4.5, 2, 3); group.add(fill);
  const bounce = new THREE.DirectionalLight(0xfffcf6, .25); bounce.position.set(0,-2,5); group.add(bounce);
  const image = root.querySelector('.sanctuary-plate img');
  const shadow = root.querySelector('.emblem-contact-shadow');
  let layout, disposed = false, priorWidth=0, priorHeight=0, priorSculpture=null;
  return {
    ready: image.decode().catch(() => { root.classList.add('plate-unavailable'); }),
    layout(width, height, camera, sculpture) {
      if(layout && width===priorWidth && height===priorHeight && sculpture===priorSculpture)return layout;
      priorWidth=width;priorHeight=height;priorSculpture=sculpture;
      layout = sanctuaryLayout(width, height);
      for (const [key, value] of Object.entries(layout.plaque)) root.style.setProperty('--plaque-' + key, value + 'px');
      for (const [key, value] of Object.entries(layout.emblem)) root.style.setProperty('--emblem-' + key, value + 'px');
      for (const [key, value] of Object.entries(layout.shadow)) root.style.setProperty('--shadow-' + key, value + 'px');
      root.classList.toggle('is-portrait', layout.portrait);
      const halfHeight = Math.tan(THREE.MathUtils.degToRad(camera.fov) * .5) * camera.position.z;
      if (sculpture) {
        sculpture.scale.setScalar((layout.emblem.height / height) * halfHeight * 2 / 3.6);
        sculpture.position.set((layout.emblem.x / width - .5) * halfHeight * 2 * width / height, (.5 - layout.emblem.y / height) * halfHeight * 2, 0);
      }
      return layout;
    },
    update({ interaction = 0 } = {}) {
      if (shadow) shadow.style.opacity = String(.18 + Math.min(.08, interaction * .12));
    },
    inspect: () => ({ type: 'locked-clean-plate-with-live-3d-emblem', layout, plateReady: Boolean(image.naturalWidth), disposed }),
    dispose() { disposed = true; scene.remove(group); group.clear(); }
  };
}
