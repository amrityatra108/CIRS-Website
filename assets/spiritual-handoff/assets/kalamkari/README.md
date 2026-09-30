# Kalamkari source and reproducible build

The artwork and motion were supplied in `Final Vine.html`. The packaged inputs
are sufficient to rebuild the live assets; the original HTML is optional.

## Packaged inputs

- `source-art.png`: the exact embedded 1024×1536 RGBA PNG, with its alpha intact.
- `source-layers.json`: the 19 authored polygons, stacking order, pivots,
  amplitudes, durations, easing, initial phases, strength and SVG viewBox.
  This is the input contract; `manifest.json` is generated output.
- `../../tools/build-kalamkari.py`: the deterministic extraction, mask and atlas
  build. Use Python 3 and Pillow **12.2.0** for the verified byte-identical output.

From the website directory:

```sh
python3 tools/build-kalamkari.py
```

This command uses only the packaged PNG and contract. To verify without
overwriting the live assets:

```sh
python3 tools/build-kalamkari.py --output /tmp/kalamkari-rebuild
```

To import the original supplied file again:

```sh
python3 tools/build-kalamkari.py --source '/path/to/Final Vine.html'
```

The build checks the packaged PNG hash before extraction. It preserves RGB,
uses 4× antialiased polygon masks, removes wing/tail cutouts from bird bodies,
and packs cropped layers with 4px padding into a 1024×2048 straight-alpha atlas.
The layer order and original pivot coordinates are retained. It writes the
atlas, manifest and browser data file; `reconstruction-zero.png` is diagnostic
evidence and is not used by the live animation.

## Provenance and verified hashes

| File | SHA-256 |
| --- | --- |
| Supplied `Final Vine.html` | `548a27aacf0a221fc78ce20170138caa358eb17c83b634be06748cd5dad8a27f` |
| Exact `source-art.png` | `6b0ef7cb6e04c796db175c15079c234fdfd1c0c4da743368e1310ab358f2cfc3` |
| Live `layers-atlas.png` | `3fa75eedf3486c63885aefdbb43e8b5c7f0ae84b335b6d0bdfaa7a84449fd16d` |

The packaged-input rebuild and original-HTML import were compared byte for byte:
PNG source, atlas, manifest, browser data and diagnostic reconstruction match.
The original-source test additionally verifies all 19 layer definitions and
171 motion samples against the supplied GSAP 3.13.0 implementation:

```sh
node tests/kalamkari-source.test.mjs '/path/to/Final Vine.html'
```

That optional provenance test requires the original HTML. The production page
and packaged-input build do not require or include its GSAP runtime. No painting
is generated, recoloured, flattened into the live vine, or extracted at runtime.
