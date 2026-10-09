"""The grade the CIRS Cultural Gallery's photographs share.

The gallery gathers photographs from a dozen sources: a DSLR at a lit stage, a
phone in a classroom, a scan of a child's painting in a magazine. Left as they
came they look like a dozen sources. This module gives them one look, in two
parts, and only the first is a correction.

  1. Correct. Each photograph is judged on its own: its black and white points
     are set, a dark or a bright frame is brought towards the middle, a colour
     cast in the near-neutral parts is eased out, colour noise is smoothed, and
     the colour is lifted where it is flat and pulled in where a stage light
     has driven it to neon. Faces are left alone by the lift.
  2. Tie together. A very light split tone leans the shadows towards the
     site's plum and the highlights towards its warm ivory, so a stage, a
     festival and a classroom read as one set on the dark ground of the wall.

Every step is done in OKLab, where lightness and colour can be moved apart:
brightening a dark frame does not wash its colour out, and taming a magenta
does not darken it. Nothing here is a filter preset; all of it is decided from
the photograph being graded, which is why the numbers below are limits, not
fixed amounts.

Paintings and drawings (kind="art") get the correction and none of the tone:
a child's colours are the child's, and the paper should stay paper white.
"""

import numpy as np
from PIL import Image, ImageFilter

# The palette the tone leans towards (sRGB). The same plum and ivory the wall's
# earlier grade used, so the move to this one changes the look, not the family.
SHADOW_TONE = (36, 26, 56)
HIGHLIGHT_TONE = (240, 229, 212)

# Limits, not amounts. Each step moves a photograph only as far as it needs to,
# up to these.
MID_TARGET = 0.56          # OKLab L the median is eased towards (sRGB grey ~0.45)
MAX_LIFT = 0.74            # smallest gamma exponent: how hard a dark frame is lifted
MAX_DROP = 1.22            # largest gamma exponent: how hard a bright frame is held
CAST_LIMIT = 0.028         # largest a/b shift the cast correction may make
CAST_STRENGTH = 0.55       # how much of a measured cast is removed
LIGHT_LIMIT = 0.034        # the same, for a whole frame lit one colour (see below)
LIGHT_STRENGTH = 0.30
CONTRAST = 0.24            # blend of an S-curve over lightness
CLARITY = 0.10             # local contrast
VIBRANCE = 0.26            # lift for flat colour
CHROMA_KNEE = 0.19         # above this colour is pulled in ...
CHROMA_SLOPE = 0.62        # ... to this fraction of the excess
TONE_SHADOW = 0.011        # split-tone chroma in the shadows
TONE_HIGHLIGHT = 0.009     # and in the highlights


# --------------------------------------------------------------------- OKLab
def _to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _from_linear(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def rgb_to_oklab(rgb):
    """rgb: float32 (h, w, 3) in 0..1, sRGB-encoded. Returns L, a, b planes."""
    lin = _to_linear(rgb)
    r, g, b = lin[..., 0], lin[..., 1], lin[..., 2]
    l = np.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = np.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = np.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def _oklab_to_linear(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return np.stack([4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
                     -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
                     -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s], axis=-1)


def oklab_to_rgb(L, a, b):
    """Back to sRGB, pulling the colour of any pixel that falls outside the
    gamut towards grey until it fits, rather than clipping its hue away."""
    lin = _oklab_to_linear(L, a, b)
    for _ in range(7):
        bad = (lin.min(axis=-1) < -0.0005) | (lin.max(axis=-1) > 1.0005)
        if not bad.any():
            break
        a = np.where(bad, a * 0.86, a)
        b = np.where(bad, b * 0.86, b)
        lin = _oklab_to_linear(L, a, b)
    return _from_linear(lin)


def _target_ab(rgb8):
    """The direction (a, b) a tone colour leans in, with its lightness removed."""
    px = np.array([[rgb8]], dtype=np.float32) / 255.0
    _, a, b = rgb_to_oklab(px)
    a, b = float(a[0, 0]), float(b[0, 0])
    n = (a * a + b * b) ** 0.5 or 1.0
    return a / n, b / n


_SHADOW_AB = _target_ab(SHADOW_TONE)
_HIGHLIGHT_AB = _target_ab(HIGHLIGHT_TONE)


# ------------------------------------------------------------------- helpers
def _smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def _blur_plane(plane, radius):
    """Gaussian blur of a 0..1 float plane (8-bit precision is plenty here)."""
    im = Image.fromarray((np.clip(plane, 0, 1) * 255 + 0.5).astype(np.uint8), "L")
    return np.asarray(im.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32) / 255.0


def _analysis(L):
    """The part of the frame the statistics are taken from: the middle, so a
    black letterbox or a white scan margin does not set the exposure."""
    h, w = L.shape
    dy, dx = int(h * 0.06), int(w * 0.06)
    core = L[dy:h - dy or None, dx:w - dx or None]
    # A stride keeps this cheap on a 2-megapixel frame without changing the answer.
    return core[::2, ::2].ravel()


# --------------------------------------------------------------------- grade
def grade(im, kind="photo"):
    """Return the graded copy of a PIL image (RGB), the same size.

    kind="photo" is the full grade. kind="art" is the correction without the
    tone, for scans of paintings and drawings.
    """
    art = kind == "art"
    rgb = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    L, a, b = rgb_to_oklab(rgb)

    # 1. Black and white points, from the lightness of the frame itself.
    sample = _analysis(L)
    lo = float(np.clip(np.percentile(sample, 0.6), 0.0, 0.22))
    hi = float(np.clip(np.percentile(sample, 99.6), 0.80 if art else 0.74, 1.0))
    lo_eff = lo * (0.85 if not art else 0.9)
    hi_eff = hi if not art else min(hi, 0.985)
    L = np.clip((L - lo_eff) / max(hi_eff - lo_eff, 0.2), 0.0, 1.0)
    if art:
        L = L * 0.985 + 0.015       # paper white, not blown white

    # 2. Mid-tones: a dark frame is lifted and a bright one held, only as far
    # as needed and never past the limits. A night stage stays a night stage.
    med = float(np.clip(np.median(_analysis(L)), 0.04, 0.96))
    if not art:
        g = np.log(MID_TARGET) / np.log(med)
        g = float(np.clip(g, MAX_LIFT, MAX_DROP))
        g = 1.0 + (g - 1.0) * 0.85
        L = np.power(np.clip(L, 0, 1), g)

    # 3. A colour cast. Two kinds. In the parts of the frame that ought to be
    # neutral (a wall, a sleeve, paper) any colour is the light, and most of it
    # comes out. And a whole frame can be washed one colour by a stage light:
    # when nearly everything leans the same way, towards magenta, violet or
    # blue, a third of that lean comes out too. Gold, green and skin never
    # qualify, so a festival lit by lamps stays lit by lamps.
    chroma = np.hypot(a, b)
    neutral = (chroma < 0.05) & (L > 0.30) & (L < (0.995 if art else 0.97))
    if neutral.mean() > 0.02:
        ma, mb = float(a[neutral].mean()), float(b[neutral].mean())
        strength, limit = (0.9, 0.045) if art else (CAST_STRENGTH, CAST_LIMIT)
        a = a - float(np.clip(ma * strength, -limit, limit))
        b = b - float(np.clip(mb * strength, -limit, limit))
    elif not art:
        body = (L > 0.12) & (L < 0.95)
        if body.mean() > 0.2:
            ma, mb = float(a[body].mean()), float(b[body].mean())
            lean = np.degrees(np.arctan2(mb, ma))
            if np.hypot(ma, mb) > 0.07 and -130 <= lean <= 5:
                a = a - float(np.clip(ma * LIGHT_STRENGTH, -LIGHT_LIMIT, LIGHT_LIMIT))
                b = b - float(np.clip(mb * LIGHT_STRENGTH, -LIGHT_LIMIT, LIGHT_LIMIT))

    # 4. Contrast: an S-curve, lighter in the shadows so a dark frame keeps its
    # depth, and a short roll-off at the top so a lamp is a lamp, not a hole.
    s_curve = _smoothstep(L)
    L = L * (1 - CONTRAST) + s_curve * CONTRAST
    L = np.where(L > 0.90, 0.90 + (L - 0.90) * 0.72, L)
    L = L * 0.97 + 0.012            # a hair of matte at the bottom

    # 5. Clarity: local contrast, from the lightness alone.
    if not art:
        radius = max(im.size) / 55.0
        base = _blur_plane(L, radius)
        mid = 1.0 - np.abs(L - 0.5) * 1.6          # fades out in deep shadow and highlight
        L = L + CLARITY * (L - base) * np.clip(mid, 0.25, 1.0)

    # 6. Colour. Noise first (a phone in a dark hall is mostly colour speckle),
    # then lift flat colour and pull in neon.
    sm = max(im.size) / 1500.0
    if sm >= 0.5:
        for plane in (a, b):
            plane[...] = _blur_plane(plane * 2 + 0.5, 1.1 * sm) * 0.5 - 0.25
    chroma = np.hypot(a, b)
    hue = np.arctan2(b, a)
    # OKLab hue of skin sits around 40-70 degrees; the lift eases off there.
    skin = np.exp(-(((hue - np.radians(52)) / np.radians(28)) ** 2))
    v = VIBRANCE * (0.55 if art else 1.0) * (1 - 0.65 * skin)
    boost = 1 + v * np.clip(1 - chroma / 0.26, 0, 1)
    new_chroma = chroma * boost
    # Magenta and hot pink are where a coloured stage light turns neon, so
    # they are pulled in a little earlier than the rest.
    neon = np.exp(-(((hue - np.radians(-8)) / np.radians(34)) ** 2))
    knee = CHROMA_KNEE * (1 - 0.22 * neon)
    slope = CHROMA_SLOPE * (1 - 0.18 * neon)
    over = np.maximum(new_chroma - knee, 0)
    new_chroma = np.minimum(new_chroma, knee) + over * slope
    scale = np.where(chroma > 1e-6, new_chroma / np.maximum(chroma, 1e-6), 1.0)
    a, b = a * scale, b * scale

    # 7. The tie: the lightest touch of plum in the shadows and ivory in the
    # highlights. Added, so a grey frame picks it up and a colourful one barely
    # notices.
    if not art:
        sh = np.clip(1 - L / 0.5, 0, 1) ** 1.5
        hl = np.clip((L - 0.55) / 0.45, 0, 1) ** 1.5
        a = a + sh * TONE_SHADOW * _SHADOW_AB[0] + hl * TONE_HIGHLIGHT * _HIGHLIGHT_AB[0]
        b = b + sh * TONE_SHADOW * _SHADOW_AB[1] + hl * TONE_HIGHLIGHT * _HIGHLIGHT_AB[1]

    out = oklab_to_rgb(np.clip(L, 0, 1), a, b)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGB")


def sharpen(im, amount=0.55):
    """The finishing sharpen, after the resize. `amount` scales a fixed mask."""
    return im.filter(ImageFilter.UnsharpMask(radius=0.7, percent=int(120 * amount), threshold=2))


def fit(im, edge):
    """Longest edge to `edge`, aspect kept. Never upscales."""
    if max(im.size) <= edge:
        return im.copy()
    s = edge / max(im.size)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
