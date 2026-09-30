# CIRS sequence assets

These assets use the approved CIRS wordmark geometry. Rebuild the generated
data from any working directory with:

```sh
python3 /Users/nishanth/Documents/Codex/2026-09-25/new-chat/outputs/spiritual-landing/tools/build-cirs-assets.py
```

The builder needs Pillow, NumPy, and SciPy. The approved SVG, mask, and latest
hospital photograph are snapshotted here and verified
against the locked SHA-256 values in `manifest.json`. No clipboard image or
earlier prototype directory is required after this snapshot exists.

`wordmark-data.png` is a 1600 × 900 RGBA **data texture**. RG stores a signed
distance clamped to −256…+256 pixels, B stores the exact approved mask alpha,
and A is opaque. Decode normalized RG samples with
`dot(texel.rg, vec2(65280.0, 255.0)) / 65535.0 * 512.0 - 256.0`.
Negative distances are inside the wordmark. Sample as linear data, without
sRGB conversion or mipmaps. For the final settled frame, use B directly so
the silhouette and counters match the approved raster exactly.

`reveal-order.png` is a stable, authored left-to-right wave in its R channel.
`exit-map.png` holds per-glyph withdrawal thresholds in R. A pixel remains
visible while departure progress is below its threshold. The mask alpha
determines where the map can affect visible pixels. `static-fallback.svg`
contains the same approved shapes against black for asset or renderer failure.

The hospital photo is a byte-for-byte copy of the user's latest supplied
1637 × 1033 grayscale source. The surrounding patterned field is drawn by
the site shader as a continuous, deterministic shape system; it has no atlas
dependency. Exact source and output hashes are listed in `manifest.json`.
