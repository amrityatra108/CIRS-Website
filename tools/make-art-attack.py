#!/usr/bin/env python3
"""Cut the CIRS Art Attack page's images from their sources.

    tools/art-attack.json                     the manifest: every work and photograph,
                                              where it came from, and what is known of it
    assets/img/art-attack/works/<id>.webp     a work as the viewer shows it
    assets/img/art-attack/works/<id>-t.webp   the same work, as the wall draws it
    assets/img/art-attack/photos/<id>.webp    a process or exhibition photograph
    assets/img/art-attack/photos/<id>-m.webp  the same, at the width a phone asks for

The sizes written go back into the manifest, which is what tools/artattack.py
reads, so the site build itself never needs an image library.

WHERE THE WORKS COME FROM. Almost every work on the page was printed in the
Creative Corner of The Crossroads, the school's monthly magazine, over its
thirty-two issues. The originals of those issues are in
assets/source/crossroads-pdf (never deployed), and each work is cut from
them in one of two ways, recorded in its "source":

  * "xref"  — the issue carries the picture as an image of its own. It is
    read out whole, at the resolution the magazine was given, and turned the
    way the page turned it ("orient"). Nothing the layout laid over it comes
    with it.
  * "box"   — fifteen issues are pictures of pages: the words and the works
    are one flat image. The work is cut from that image at "box", fractions
    of the page, which were read by hand and then snapped to the edge of the
    work. These are as sharp as the page is, and no sharper.

Every work keeps its own proportions: the output is the whole cut, resized,
never cropped to a shape the layout would prefer.

The five paintings the page has always shown are from the school's archive
(assets/source/archive), at the only size the archive holds.

The photographs are the school's own: camera originals in assets/source, and
renditions of files in the school's Drive, kept in assets/source/art-attack
so that this runs offline. --fetch downloads any that are missing, from the
Drive file id in the manifest (the files are shared by link).

Needs pymupdf and Pillow:

    pip install pymupdf Pillow
    python3 tools/make-art-attack.py            # cut everything
    python3 tools/make-art-attack.py --fetch    # first fetch any missing Drive files
"""

import io
import json
import os
import sys
import urllib.request

try:
    import pymupdf
    from PIL import Image, ImageOps
except ImportError as missing:      # pragma: no cover - a setup problem, not a bug
    sys.exit(f"make-art-attack: {missing.name} is not installed — pip install pymupdf Pillow")

Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(HERE, "art-attack.json")
PDFS = os.path.join(ROOT, "assets/source/crossroads-pdf")
CAMERA = os.path.join(ROOT, "assets/source")
ARCHIVE = os.path.join(ROOT, "assets/source/archive")
DRIVE = os.path.join(ROOT, "assets/source/art-attack")
OUT = "assets/img/art-attack"

FULL_LONG_EDGE = 1600      # the viewer; never enlarged beyond the source
THUMB_HEIGHT = 440         # the wall draws a row at most ~220px tall: 2x
PHOTO_WIDTHS = (1800, 900) # a photograph, and the cut a phone asks for
QUALITY_FULL, QUALITY_THUMB = 88, 80


def orient(img, code):
    """Turn an image the way the page placed it.

    code is two of x+ x- y+ y-: where the image's own x axis and y axis point
    on the page. ["x+", "y+"] is upright; ["y-", "x+"] was placed turned a
    quarter anticlockwise, and so on.
    """
    ux, uy = code
    if ux[0] == "y":            # the axes swap: transpose first
        img = img.transpose(Image.TRANSPOSE)
        if ux[1] == "-":
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        if uy[1] == "-":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
    else:
        if uy[1] == "-":
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        if ux[1] == "-":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def embedded(doc, xref):
    """An image as the issue holds it, through MuPDF's own colour conversion.

    See tools/make-crossroads-pdfs.py for why: a CMYK JPEG read by hand comes
    back inverted, and a soft mask must not be burnt in.
    """
    pix = pymupdf.Pixmap(doc, xref)
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)
    if pix.colorspace is None or pix.colorspace.n != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    # A soft mask is the picture's own transparency. Read without it, what the
    # page showed as white paper comes out black (a red drawing in issue 04
    # became red on black), so it is laid on white here. The mask can also
    # carry a drop shadow the layout added: only the fully opaque part is the
    # work, so the cut stops there, and a cut-out object (whose opaque part is
    # not a rectangle) is given a margin of white so it is not cropped tight.
    kind, ref = doc.xref_get_key(xref, "SMask")
    if kind == "xref":
        mask = pymupdf.Pixmap(doc, int(ref.split()[0]))
        alpha = Image.frombytes("L", (mask.width, mask.height), mask.samples[::mask.n])
        if alpha.size != im.size:
            alpha = alpha.resize(im.size, Image.LANCZOS)
        solid = alpha.point(lambda v: 255 if v >= 250 else 0)
        box = solid.getbbox() or (0, 0) + im.size
        white = Image.new("RGB", im.size, "white")
        im = Image.composite(im, white, alpha).crop(box)
        area = (box[2] - box[0]) * (box[3] - box[1])
        filled = sum(solid.crop(box).histogram()[255:]) / max(1, area)
        if filled < 0.9:
            pad = round(0.06 * max(im.size))
            framed = Image.new("RGB", (im.width + 2 * pad, im.height + 2 * pad), "white")
            framed.paste(im, (pad, pad))
            im = framed
    return im


def flat_page(doc, page_no):
    """A page that is one picture, rendered at that picture's own size."""
    page = doc[page_no - 1]
    info = max(page.get_image_info(), key=lambda i: i["width"] * i["height"])
    zoom = info["height"] / page.rect.height
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def trim_bands(im, limit=0.14):
    """Take off a strip of the page's own design caught at the edge of a cut.

    On a flat page the magazine's coloured rules and header bars run right up
    to some of the works, and a cut snapped to the work can keep a few rows
    of one. Such a strip is flat — every row in it the same even colour —
    and it ends at a hard edge where the work begins. Paper, or a sky in a
    painting, is never both, so only a strip that is is removed, and never
    more than `limit` of the work.
    """
    px = im.convert("RGB").load()
    w, h = im.size

    def line(k, horizontal):
        if horizontal:
            return [px[x, k] for x in range(0, w, max(1, w // 64))]
        return [px[k, y] for y in range(0, h, max(1, h // 64))]

    def stats(vals):
        n = len(vals)
        mean = [sum(v[c] for v in vals) / n for c in range(3)]
        spread = max((sum((v[c] - mean[c]) ** 2 for v in vals) / n) ** 0.5 for c in range(3))
        return mean, spread

    def band(horizontal, forward):
        size = h if horizontal else w
        order = range(size) if forward else range(size - 1, -1, -1)
        first, count = None, 0
        for k in order:
            mean, spread = stats(line(k, horizontal))
            if spread > 16:
                break
            if first is None:
                first = mean
            elif max(abs(mean[c] - first[c]) for c in range(3)) > 18:
                break
            count += 1
            if count > limit * size:
                return 0
        if count == 0 or count >= limit * size:
            return 0
        k = count if forward else size - 1 - count
        after, _ = stats(line(k, horizontal))
        return count if max(abs(after[c] - first[c]) for c in range(3)) > 40 else 0

    top, bottom = band(True, True), band(True, False)
    left, right = band(False, True), band(False, False)
    if top or bottom or left or right:
        im = im.crop((left, top, w - right, h - bottom))
    return im


def fit_long(im, edge):
    s = min(1.0, edge / max(im.size))
    return im if s == 1.0 else im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


def fit_height(im, height):
    s = min(1.0, height / im.height)
    return im if s == 1.0 else im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


def fit_width(im, width):
    s = min(1.0, width / im.width)
    return im if s == 1.0 else im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


def save(im, rel, quality):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "WEBP", quality=quality, method=6)
    return list(im.size)


def work_image(src, docs, pages):
    if "archive" in src:
        return Image.open(os.path.join(ARCHIVE, src["archive"])).convert("RGB")
    issue = src["crossroads"]
    if issue not in docs:
        docs[issue] = pymupdf.open(os.path.join(PDFS, f"crossroads-issue-{issue:02d}.pdf"))
    doc = docs[issue]
    if "xref" in src:
        im = orient(embedded(doc, src["xref"]), src.get("orient", ["x+", "y+"]))
    else:
        key = (issue, src["page"])
        if key not in pages:
            pages[key] = flat_page(doc, src["page"])
        page = pages[key]
        x0, y0, x1, y1 = src["box"]
        im = trim_bands(page.crop((round(x0 * page.width), round(y0 * page.height),
                                   round(x1 * page.width), round(y1 * page.height))))
    if "trim" in src:          # fractions of the cut, where the source carries a border
        t = src["trim"]
        im = im.crop((round(t[0] * im.width), round(t[1] * im.height),
                      round(t[2] * im.width), round(t[3] * im.height)))
    return im


def photo_image(src):
    if "camera" in src:
        path = os.path.join(CAMERA, src["camera"])
    elif "drive" in src:
        path = os.path.join(DRIVE, src["file"])
    else:
        path = os.path.join(ROOT, src["crossroads_page"])  # not used; kept for shape
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if "crop" in src:          # fractions of the frame
        c = src["crop"]
        im = im.crop((round(c[0] * im.width), round(c[1] * im.height),
                      round(c[2] * im.width), round(c[3] * im.height)))
    return im


def fetch(manifest):
    os.makedirs(DRIVE, exist_ok=True)
    for p in manifest["photos"]:
        src = p["source"]
        if "drive" not in src:
            continue
        dest = os.path.join(DRIVE, src["file"])
        if os.path.exists(dest):
            continue
        url = f"https://drive.google.com/thumbnail?id={src['drive']}&sz=w2400"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=90).read()
        Image.open(io.BytesIO(data)).verify()
        open(dest, "wb").write(data)
        print(f"  fetch  {src['file']} ({len(data):,} bytes)")


def main():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    if "--fetch" in sys.argv:
        fetch(manifest)

    written = set()
    docs, pages = {}, {}
    for w in manifest["works"]:
        im = work_image(w["source"], docs, pages)
        full, thumb = f"{OUT}/works/{w['id']}.webp", f"{OUT}/works/{w['id']}-t.webp"
        w["size"] = save(fit_long(im, FULL_LONG_EDGE), full, QUALITY_FULL)
        w["thumb"] = save(fit_height(im, THUMB_HEIGHT), thumb, QUALITY_THUMB)
        # Recorded so tools/check-links.py can see every file this writes:
        # a page names the second of a srcset pair only in the srcset.
        w["files"] = [full, thumb]
        written.update((full, thumb))

    for p in manifest["photos"]:
        im = photo_image(p["source"])
        big, small = f"{OUT}/photos/{p['id']}.webp", f"{OUT}/photos/{p['id']}-m.webp"
        p["size"] = save(fit_width(im, PHOTO_WIDTHS[0]), big, QUALITY_FULL)
        p["mobile"] = save(fit_width(im, PHOTO_WIDTHS[1]), small, QUALITY_THUMB)
        p["files"] = [big, small]
        written.update((big, small))

    # A work or photograph taken out of the manifest must not stay behind:
    # tools/check-links.py would rightly report it as an orphan.
    for folder in ("works", "photos"):
        base = os.path.join(ROOT, OUT, folder)
        if not os.path.isdir(base):
            continue
        for name in os.listdir(base):
            rel = f"{OUT}/{folder}/{name}"
            if rel not in written:
                os.remove(os.path.join(ROOT, rel))
                print(f"  remove {rel}")

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"make-art-attack: {len(manifest['works'])} works, {len(manifest['photos'])} photographs")


if __name__ == "__main__":
    main()
