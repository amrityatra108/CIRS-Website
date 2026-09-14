#!/usr/bin/env python3
"""Derive the published Crossroads PDFs from the originals.

    assets/source/crossroads-pdf/*.pdf   the issues as the school supplied them
    assets/documents/crossroads/*.pdf    what the site serves

The originals are print masters: 352 MB across 32 issues, one of them 30 MB.
A visitor opening an issue on a phone downloads the whole file, so they are
re-cut here the way the photographs are, and for the same reason — the crop,
the size and the quality of each one recorded rather than remembered.

Only the images are touched. In most issues the text is real text rather than
a picture of text, so it comes through untouched and still selectable; what
shrinks is the photographs behind it, stored at print resolution and print
quality.

Fifteen issues are not like that — 06, 07, 08, 10, 11, 12, 13, 14, 15, 16,
19, 23, 24, 28 and 29 carry no text layer at all, because the words in them
ARE pixels. A run marks them "pages are pictures"; the check is simply whether
an issue has any extractable text, so it stays true if the set changes.

Several of those are already near 1328x1889, roughly 150dpi and close to the
floor for legible body text, which is why they barely shrink. That is the
point: CAP_PX and QUALITY are set where they are because below about 1500px
those pages stop being comfortable to read, while the issues with real text
would happily go further. One setting has to serve both, so it is set by the
ones that can least afford it.

Run with --check and look at the "worst page" column before changing either
number. A page-as-image issue will show the damage there first.

    python3 tools/make-crossroads-pdfs.py            # rebuild
    python3 tools/make-crossroads-pdfs.py --check    # compare against the originals

Three things go wrong quietly if the images are decoded naively, and all three
were seen in these very files before the decoding below was settled on:

  * A CMYK JPEG converted by hand comes back inverted — a photograph of a
    garden rendered near-black and purple.
  * An image with an /SMask must be read WITHOUT its mask applied. Composite
    it and the transparency is burnt in against black.
  * A /DeviceN or /Separation image's samples are ink coverage, not light.
    Written back as /DeviceGray, a line drawing becomes a black box: the one
    on page 6 of issue 05 did exactly that.

So every image is put through MuPDF's own colour conversion to RGB rather than
read channel-by-channel, whatever colourspace it claims.

Needs pymupdf and pikepdf, neither of which is in the repository:

    pip install pymupdf pikepdf
"""

import io
import os
import sys

try:
    import pikepdf
    import pymupdf
    from PIL import Image
except ImportError as missing:      # pragma: no cover - a setup problem, not a bug
    sys.exit(f"make-crossroads-pdfs: {missing.name} is not installed — "
             "pip install pymupdf pikepdf")

Image.MAX_IMAGE_PIXELS = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/source/crossroads-pdf")
OUT = os.path.join(ROOT, "assets/documents/crossroads")

# A full page is about 8.8 inches across, so 1900px is a little over 200dpi —
# more than a screen shows, enough to zoom into, far less than print. Read the
# note at the top before lowering either: nine issues are pictures of pages,
# and these two numbers are what keeps their text readable.
CAP_PX = 1900
QUALITY = 78
MIN_BYTES = 8000          # below this there is nothing to win
KEEP_RATIO = 0.95         # only replace an image that is meaningfully smaller

DCT = pikepdf.Name("/DCTDecode")


def as_rgb(doc, xref):
    """The base image at `xref`, RGB or greyscale, or None if it can't be read.

    Always through MuPDF's colour conversion: see the note at the top about
    CMYK, /DeviceN and /Separation.
    """
    try:
        pix = pymupdf.Pixmap(doc, xref)
    except Exception:
        return None
    try:
        if pix.alpha:                       # the base image; the mask stays put
            pix = pymupdf.Pixmap(pix, 0)
        if pix.colorspace is None:          # a stencil mask, not a picture
            return None
        if pix.colorspace.name != pymupdf.csRGB.name:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    except Exception:
        return None
    # Greyscale in all but name — half the bytes, no visible difference.
    r, g, b = im.split()
    if max(abs(a - c) for a, c in zip(r.histogram(), g.histogram())) == 0 and \
            max(abs(a - c) for a, c in zip(g.histogram(), b.histogram())) == 0:
        return im.convert("L")
    return im


def optimise(src, out, cap_px=CAP_PX, quality=QUALITY):
    doc = pymupdf.open(src)
    pdf = pikepdf.open(src)
    stats = dict(rewritten=0, kept=0, skipped=0)

    for xref in range(1, doc.xref_length()):
        if doc.xref_get_key(xref, "Subtype")[1] != "/Image":
            continue
        try:
            obj = pdf.get_object(xref, 0)
            if not isinstance(obj, pikepdf.Stream):
                raise ValueError
            raw = len(obj.read_raw_bytes())
        except Exception:
            stats["skipped"] += 1
            continue

        # Line art and stencils stay exactly as they are: JPEG cannot hold a
        # 1-bit image without smearing its edges.
        if raw < MIN_BYTES or int(obj.get("/BitsPerComponent", 8)) == 1 \
                or bool(obj.get("/ImageMask", False)):
            stats["skipped"] += 1
            continue

        im = as_rgb(doc, xref)
        if im is None:
            stats["skipped"] += 1
            continue
        if max(im.size) > cap_px:
            s = cap_px / max(im.size)
            im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                           Image.LANCZOS)

        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True)
        new = buf.getvalue()
        if len(new) >= raw * KEEP_RATIO:
            stats["kept"] += 1
            continue

        obj.write(new, filter=DCT)
        obj["/Width"], obj["/Height"] = im.width, im.height
        obj["/BitsPerComponent"] = 8
        obj["/ColorSpace"] = pikepdf.Name(
            "/DeviceGray" if im.mode == "L" else "/DeviceRGB")
        for gone in ("/DecodeParms", "/Decode"):
            if gone in obj:
                del obj[gone]
        stats["rewritten"] += 1

    doc.close()
    pdf.save(out, compress_streams=True,
             object_stream_mode=pikepdf.ObjectStreamMode.generate)
    pdf.close()
    return stats


def pages_match(a, b, dpi=90):
    """Render both and report (page count agreement, worst page RMS difference)."""
    import math
    from PIL import ImageChops
    da, db = pymupdf.open(a), pymupdf.open(b)
    if da.page_count != db.page_count:
        da.close(); db.close()
        return False, 255.0, -1
    worst, where = 0.0, -1
    for i in range(da.page_count):
        pa, pb = da[i].get_pixmap(dpi=dpi), db[i].get_pixmap(dpi=dpi)
        ia = Image.frombytes("RGB", (pa.width, pa.height), pa.samples)
        ib = Image.frombytes("RGB", (pb.width, pb.height), pb.samples)
        if ia.size != ib.size:
            ib = ib.resize(ia.size)
        h = ImageChops.difference(ia, ib).convert("L").histogram()
        n = sum(h)
        rms = math.sqrt(sum(v * v * c for v, c in enumerate(h)) / n)
        if rms > worst:
            worst, where = rms, i
    da.close(); db.close()
    return True, worst, where


def text_len(path):
    doc = pymupdf.open(path)
    n = sum(len(p.get_text().strip()) for p in doc)
    doc.close()
    return n


def main():
    check = "--check" in sys.argv
    if not os.path.isdir(SRC):
        sys.exit(f"make-crossroads-pdfs: no originals at {SRC}")
    os.makedirs(OUT, exist_ok=True)
    names = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".pdf"))
    if not names:
        sys.exit(f"make-crossroads-pdfs: no PDFs in {SRC}")

    before = after = 0
    problems = []
    print(f"  {'issue':<26}{'was':>8}{'now':>8}{'':>6}  {'images':>16}"
          + ("   worst page" if check else ""))
    for name in names:
        s, o = os.path.join(SRC, name), os.path.join(OUT, name)
        st = optimise(s, o)
        a, b = os.path.getsize(s), os.path.getsize(o)
        image_only = text_len(s) < 200
        before += a
        after += b
        line = (f"  {name:<26}{a/1e6:>7.1f}M{b/1e6:>7.1f}M{100*b/a:>5.0f}%  "
                f"{st['rewritten']:>4} cut {st['kept']:>3} kept {st['skipped']:>3} left"
                + ("  pages are pictures" if image_only else ""))
        if check:
            same, rms, page = pages_match(s, o)
            ta, tb = text_len(s), text_len(o)
            line += f"   p{page} {rms:>5.1f}"
            if not same:
                problems.append(f"{name}: page count changed")
            if rms > 30:
                problems.append(f"{name}: page {page} differs by {rms:.0f}/255")
            if tb < ta * 0.999:
                problems.append(f"{name}: text shrank {ta} -> {tb} characters")
        print(line)

    print(f"\n  {len(names)} issues, {before/1e6:.0f} MB -> {after/1e6:.0f} MB "
          f"({100*after/before:.0f}%, {(before-after)/1e6:.0f} MB saved)")
    if problems:
        print("\n  PROBLEMS")
        for p in problems:
            print("   ", p)
        sys.exit(1)
    if check:
        print("  every issue: same pages, same text, no page visibly changed")


if __name__ == "__main__":
    main()
