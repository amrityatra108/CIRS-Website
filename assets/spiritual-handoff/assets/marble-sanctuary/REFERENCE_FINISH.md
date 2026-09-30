# Reference marble finish

The live emblem still uses `assets/logo-solid-outline.json` and the original local liquid/dispersal response. No face geometry, hole, interaction constant or audio code changed for this finish.

`reference-emblem-sample.png` is the unretouched 263 × 428 emblem rectangle sampled from the user's latest landing reference. `reference-veins-data.png` contains mineral pigment coverage, rather than the screenshot's lighting or backdrop. Its three channels are documented in `reference-veins-data.json`. The live shader attaches this map to the authoritative outline coordinates and applies physical lighting and deformation independently.

Reproduce the map using:

```sh
python3 assets/marble-sanctuary/build-reference-veins.py
```

Requires Python, Pillow and NumPy. The sample is included, so the source screenshot is not needed for reproducing the map. The texture uses `NoColorSpace`, bilinear/mipmap filtering and clamped coordinates. It is prepared once, reused during interaction and disposed with the logo.

The shoulder normal field spans the narrow strokes and smoothly relaxes at their centre. Relief direction is computed from a smoothed exact Euclidean Float32 distance field during preparation, before encoding RG signed directions and B depth into RGBA16F. The shader samples those directions linearly rather than differentiating quantized distance values; this removes the amplified stair bands. Half-float direction precision avoids visible glossy highlight bands. The relief texture is prepared once from the exact perimeter and disposed with the mesh. A cream base and balanced fill preserve dimensional shading without clipping the body to flat white.

The original outline is preserved exactly. Material shading and the reference vein pattern are matched; a live physically lit material cannot be a pixel-identical copy of a baked screenshot at every viewport or while it deforms.
