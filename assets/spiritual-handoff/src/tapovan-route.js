// Proposed route copied from the cyan step-centre dots on the user's
// "MOUNTAIN STEPS / PROPOSED ROUTE BOARD" (2026-09-28). Each [u, v] is
// normalized to the 960 x 540 source-video panel, not to the whole JPG.
// These are composition anchors at eight sampled video frames. They are NOT
// camera-tracked positions, a 3D mountain reconstruction, or a guarantee
// that a stone at one anchor corresponds to a stone in the next frame.
// Register and interpolate against stable rock/snow features before use.

export const TAPOVAN_ROUTE_SOURCE = Object.freeze({
  video: 'My Movie 8.mp4',
  width: 1920,
  height: 1080,
  durationSeconds: 15.14,
  frameRate: 23.976,
  boardPanelWidth: 960,
  boardPanelHeight: 540,
  coordinateSpace: 'normalized source-video frame',
  status: 'proposed blocking; not camera-solved',
  // Cyan-dot centroid extraction from the compressed board is accurate to
  // about 2 panel pixels. Terrain registration is the larger uncertainty.
  digitizationUncertaintyPanelPixels: 2
});

// Points are ordered along the proposed descending trail. `hiddenBefore`
// and `hiddenAfter` describe the board's dashed continuation, not automatic
// visibility instructions. Only actual terrain/cloud/frame occlusion may
// conceal a stone in the final composite.
export const TAPOVAN_ROUTE_FRAMES = Object.freeze([
  {
    time: 0.50, frame: 13, id: 'sunlit-face',
    description: 'Begin below the summit; bend across the bright face.',
    hiddenBefore: false, hiddenAfter: true,
    points: [
      [0.58958, 0.30000], [0.55521, 0.38519],
      [0.51979, 0.48519], [0.53542, 0.57037],
      [0.60521, 0.60926], [0.66979, 0.65556]
    ]
  },
  {
    time: 2.50, frame: 61, id: 'approach',
    description: 'The first run enlarges and exits toward the near right shoulder.',
    hiddenBefore: false, hiddenAfter: true,
    points: [
      [0.56458, 0.34444], [0.53958, 0.44074],
      [0.56042, 0.53519], [0.63542, 0.62037],
      [0.73958, 0.74074]
    ]
  },
  {
    time: 4.50, frame: 109, id: 'ridge-pass',
    description: 'A short visible run through the snowy trough, after foreground concealment.',
    hiddenBefore: true, hiddenAfter: false,
    points: [
      [0.61042, 0.52037], [0.64479, 0.62593],
      [0.60521, 0.73519], [0.52500, 0.82593]
    ]
  },
  {
    time: 6.51, frame: 157, id: 'snowy-saddle',
    description: 'Descend through the saddle and bend around the foreground outcrop.',
    hiddenBefore: false, hiddenAfter: true,
    points: [
      [0.28542, 0.32963], [0.32500, 0.43519],
      [0.36458, 0.54444], [0.42500, 0.64444],
      [0.50521, 0.70000]
    ]
  },
  {
    time: 8.51, frame: 205, id: 'lower-cloud-band',
    description: 'Carry the trail down the lower face toward cloud concealment.',
    hiddenBefore: false, hiddenAfter: true,
    points: [
      [0.30521, 0.47037], [0.36042, 0.55000],
      [0.42500, 0.62593], [0.48958, 0.70000]
    ]
  },
  {
    time: 10.51, frame: 253, id: 'wide-reveal',
    description: 'A smaller continuation on the lower mountain, ending in cloud.',
    hiddenBefore: false, hiddenAfter: true,
    points: [
      [0.54479, 0.45926], [0.58021, 0.50000],
      [0.61979, 0.54444], [0.66042, 0.59074],
      [0.70521, 0.62963], [0.75000, 0.67407]
    ]
  },
  {
    time: 12.51, frame: 301, id: 'right-shoulder',
    description: 'Continue downhill as the camera turns toward the right shoulder.',
    hiddenBefore: false, hiddenAfter: true,
    points: [
      [0.38542, 0.42037], [0.44479, 0.47037],
      [0.51042, 0.51481], [0.58021, 0.56481],
      [0.65521, 0.61481]
    ]
  },
  {
    time: 14.51, frame: 349, id: 'lower-basin',
    description: 'Larger near stones descend into the lower basin and leave the view.',
    hiddenBefore: false, hiddenAfter: true,
    points: [
      [0.39479, 0.54444], [0.45521, 0.62037],
      [0.51979, 0.69444], [0.58542, 0.77407],
      [0.65000, 0.85556]
    ]
  }
]);
