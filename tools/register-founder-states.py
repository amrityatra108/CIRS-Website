#!/usr/bin/env python3
"""Register the two founder portraits onto one head frame.

The opening dissolves a photograph of Balakrishna Menon into one of Swami
Chinmayananda. The two are different photographs at different crops, and
as cut they do not agree about where the head is: measured from the alpha,
Gurudev's crown sits 90px lower than Menon's and his figure is 141px wider
in a 2048px square. Any reveal that crosses the head therefore steps, and
the step reads as a tear through the forehead rather than as a man ageing.

This aligns the second state to the first on the two anchors the alpha
gives reliably -- the crown of the head and the head's centre line -- and
scales it so the two heads are the same width. It does not pretend to be
a facial registration: the beards differ, the framing differs, and putting
the eyes on the eyes needs landmarks this has no way to find. It gets the
heads concentric, which is what a soft dissolve needs and what the torn
reveal never had.

Re-run it after recutting either state and commit what changes.
"""
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent.parent / "assets" / "founder-opening" / "assets"
BASE = HERE / "menon-state-2048.png"
MOVE = HERE / "gurudev-state-2048.png"
OUT  = HERE / "gurudev-state-2048.png"   # written in place; git shows the delta


def anchors(path):
    """Crown row, head centre line and head width, read from the alpha."""
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A")
    w, h = im.size
    px = a.load()
    box = a.point(lambda v: 255 if v > 16 else 0).getbbox()
    if not box:
        sys.exit(f"{path.name}: no opaque pixels")
    crown = box[1]

    # Width and centre line every few rows down from the crown. The head's
    # widest row is the anchor for scale; sampling every other column is
    # plenty at this size and keeps the scan quick.
    #
    # The window stops well above the shoulders on purpose. Run to 900 rows
    # it picks up Gurudev's beard and then his shoulders, and the "head"
    # comes back 1116px wide against Menon's 670 -- a scale of 0.60, which
    # shrinks him to a child. 420 rows is past the widest part of both heads
    # and short of either figure's shoulder line.
    rows = []
    for y in range(crown, min(crown + 420, h), 4):
        xs = [x for x in range(0, w, 2) if px[x, y] > 16]
        if xs:
            rows.append((y, xs[-1] - xs[0], (xs[0] + xs[-1]) // 2))
    if not rows:
        sys.exit(f"{path.name}: no head rows")
    y, width, centre = max(rows, key=lambda r: r[1])
    return im, crown, centre, width


def main():
    base, base_crown, base_cx, base_w = anchors(BASE)
    move, move_crown, move_cx, move_w = anchors(MOVE)

    scale = base_w / move_w
    print(f"menon   crown={base_crown:4d} cx={base_cx:4d} headW={base_w:4d}")
    print(f"gurudev crown={move_crown:4d} cx={move_cx:4d} headW={move_w:4d}")
    print(f"scale ×{scale:.4f}  crown {move_crown} → {base_crown}  centre {move_cx} → {base_cx}")

    # PIL's AFFINE wants the inverse map: for each output pixel it asks which
    # source pixel to read. Forward is out = (src - move_anchor)*scale +
    # base_anchor, so the inverse is src = (out - base_anchor)/scale +
    # move_anchor, which is what goes in the matrix.
    inv = 1.0 / scale
    matrix = (
        inv, 0.0, move_cx    - base_cx    * inv,
        0.0, inv, move_crown - base_crown * inv,
    )
    out = move.transform(move.size, Image.AFFINE, matrix, resample=Image.BICUBIC)

    # Bicubic overshoots at a hard alpha edge and leaves a faint rim of
    # almost-transparent pixels carrying colour. Those show as a halo once
    # the dissolve lifts them, so anything nearly clear is cleared.
    alpha = out.getchannel("A").point(lambda v: 0 if v < 8 else v)
    out.putalpha(alpha)

    out.save(OUT)
    print(f"wrote {OUT.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
