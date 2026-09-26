#!/usr/bin/env python3
"""Build self-hosted WOFF2 fonts from pinned upstream revisions.

Requires fonttools[woff]==4.62.1 (only for this optional asset-generation step).
The ordinary site build needs no font tooling or network connection.
Full glyph sets and OpenType shaping tables are preserved. Bodoni Moda's optical
size is pinned at its 11-point default while its weight axis stays variable.

Three open-font sources, each verified against the metadata inside the font rather
than its filename:

  * google/fonts at a pinned revision — the existing editorial faces.
  * github/mona-sans at a pinned release — the English body and interface
    face. Its own variable WOFF2s are served byte for byte: the OFL reserves
    the name "Mona", so a re-encoded copy is kept out of the question.
  * indestructible-type/Bodoni at a pinned revision — the open display face.

Commercial Brier is deliberately outside this generator. The seller's terms
prohibit converting or renaming the font software. Seller-supplied webfont files
must be staged privately, byte for byte, for the licensed production domain.
"""
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
import hashlib
import json
import os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets/fonts'
REVISION = 'f2bd09badbc763d8757951d52deec29da27e85fb'
BASE = f'https://raw.githubusercontent.com/google/fonts/{REVISION}/ofl/'
# Bodoni Moda handles display type. Newsreader, Literata and EB Garamond remain
# available for their other assigned roles; Mona Sans handles English body and
# interface text, including the thin lettering of the film openings.
FAMILIES = [
    ('Newsreader', 'newsreader', 'Newsreader[opsz,wght].ttf', 'Newsreader-Italic[opsz,wght].ttf', '200 800'),
    ('Literata', 'literata', 'Literata[opsz,wght].ttf', 'Literata-Italic[opsz,wght].ttf', '200 900'),
    ('EB Garamond', 'ebgaramond', 'EBGaramond[wght].ttf', 'EBGaramond-Italic[wght].ttf', '400 800'),
    ('Tiro Devanagari Hindi', 'tirodevanagarihindi', 'TiroDevanagariHindi-Regular.ttf', 'TiroDevanagariHindi-Italic.ttf', '400'),
]

MONA_REVISION = '0f7dc66ddd766605eb0e75c3f47bf9d1dd38ceca'  # tag v2.0.27
MONA_BASE = f'https://raw.githubusercontent.com/github/mona-sans/{MONA_REVISION}/'
# The upright text file has no width axis and is what nearly every page
# needs. The width-axis file is declared only for stretches other than 100%,
# so the browser fetches it only where something asks for one (the film
# titles, at present). The italic is for emphasis in prose; the upstream
# [opsz,wght] italic pins opsz at its text design, which is all prose needs.
MONA = [
    # (css style, css stretch, upstream file, expected axes, local name)
    ('normal', '100%', 'MonaSansVF[opsz,wght].woff2',
     {'wght': (200, 900), 'opsz': (0, 100)}, 'monasans-normal.woff2'),
    ('normal', '75% 99%', 'MonaSansVF[wdth,opsz,wght].woff2',
     {'wdth': (75, 125), 'wght': (200, 900), 'opsz': (0, 100)}, 'monasans-width.woff2'),
    ('normal', '101% 125%', 'MonaSansVF[wdth,opsz,wght].woff2',
     {'wdth': (75, 125), 'wght': (200, 900), 'opsz': (0, 100)}, 'monasans-width.woff2'),
    ('italic', '100%', 'MonaSansVF-Italic[opsz,wght].woff2',
     {'wght': (200, 900), 'opsz': (0, 0)}, 'monasans-italic.woff2'),
]
# Mona Sans sets larger than Newsreader at the same font-size: a taller
# x-height and wider letters. Scaling the face once, here, keeps every
# page's existing sizes, wraps and hierarchy instead of re-sizing each of
# them; its x-height still stands above Newsreader's, which small text needs.
MONA_SIZE_ADJUST = '92%'

BODONI_REVISION = '30ce6cdc354ef179a3b72ba0f0e71826e599348c'
BODONI_BASE = f'https://raw.githubusercontent.com/indestructible-type/Bodoni/{BODONI_REVISION}/'
BODONI_LICENSE_SHA256 = '86279342767d5f3e6b07b49dd591f196dcb0ec9ec8b9ea339c09221e61863d46'
BODONI_AXES = {'wght': (400, 900), 'opsz': (6, 96)}
BODONI_DISPLAY_OPSZ = 11
BODONI_OUTPUT_AXES = {'wght': (400, 900)}
BODONI_REQUIRED_TABLES = {'GDEF', 'GPOS', 'GSUB', 'HVAR', 'STAT', 'fvar', 'gvar'}
BODONI = [
    ('normal', 'BodoniModa[opsz,wght].ttf',
     '550f5e34ee0a828d7941b1fe9bc58b34e5260d3f33a61532e6d0a0114e79a5cf'),
    ('italic', 'BodoniModa-Italic[opsz,wght].ttf',
     'dfff1619f8f6871c6372f8855b67211f9a73b4e93d45aca868cd8f46a48622de'),
]

BRIER_REQUIRED = 'LICENSED BRIER FONT FILE REQUIRED'

def put(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)

def clean_notice(notice):
    # Preserve the full notice while keeping generated text whitespace-clean.
    return b'\n'.join(line.rstrip(b' \t\r') for line in notice.splitlines()) + b'\n'

def face(family, style, weights, name, stretch=None, size_adjust=None):
    lines = [f"  font-family: '{family}';", f'  font-style: {style};', f'  font-weight: {weights};']
    if stretch:
        lines.append(f'  font-stretch: {stretch};')
    lines.append('  font-display: swap;')
    if size_adjust:
        lines.append(f'  size-adjust: {size_adjust};')
    lines.append(f"  src: url('../fonts/{name}') format('woff2');")
    return '@font-face {\n' + '\n'.join(lines) + '\n}'

def google_fonts(rules, manifest):
    for family, slug, normal, italic, weights in FAMILIES:
        license_url = BASE + slug + '/OFL.txt'
        notice = urlopen(license_url).read()
        if b'SIL OPEN FONT LICENSE Version 1.1' not in notice:
            raise ValueError(f'Unexpected license for {family}')
        put(OUT / 'licenses' / (slug + '-OFL.txt'), clean_notice(notice))
        for style, source in [('normal', normal), ('italic', italic)]:
            if source is None:
                continue
            url = BASE + slug + '/' + quote(source)
            raw = urlopen(url).read()
            font = TTFont(BytesIO(raw), recalcTimestamp=False)
            # Verify embedded metadata before declaring a CSS face; filenames are not evidence.
            axes = {a.axisTag: a for a in font['fvar'].axes} if 'fvar' in font else {}
            axis = axes.get('wght')
            embedded_weights = (f'{axis.minValue:g} {axis.maxValue:g}' if axis
                                else str(font['OS/2'].usWeightClass))
            embedded_style = 'italic' if font['OS/2'].fsSelection & 1 else 'normal'
            if embedded_weights != weights or embedded_style != style:
                raise ValueError(f'Face metadata mismatch for {family}: '
                                 f'{embedded_weights}, {embedded_style}')
            font.flavor = 'woff2'
            buffer = BytesIO()
            font.save(buffer)
            name = f'{slug}-{style}.woff2'
            data = buffer.getvalue()
            put(OUT / name, data)
            manifest.append({'family': family, 'style': style, 'weights': weights,
                             'file': name, 'source': url, 'license': license_url,
                             'source_sha256': hashlib.sha256(raw).hexdigest(),
                             'woff2_sha256': hashlib.sha256(data).hexdigest(),
                             'bytes': len(data)})
            rules.append(face(family, style, weights, name))

def mona_sans(rules, manifest):
    license_url = MONA_BASE + 'OFL.txt'
    notice = urlopen(license_url).read()
    if b'SIL Open Font License, Version 1.1' not in notice:
        raise ValueError('Unexpected license for Mona Sans')
    put(OUT / 'licenses' / 'monasans-OFL.txt', clean_notice(notice))
    fetched = {}
    for style, stretch, source, expected, name in MONA:
        url = MONA_BASE + 'fonts/webfonts/variable/' + quote(source)
        if url not in fetched:
            raw = urlopen(url).read()
            font = TTFont(BytesIO(raw), recalcTimestamp=False)
            axes = {a.axisTag: (a.minValue, a.maxValue) for a in font['fvar'].axes}
            embedded_style = 'italic' if font['OS/2'].fsSelection & 1 else 'normal'
            family = font['name'].getDebugName(16) or font['name'].getDebugName(1)
            if axes != expected or embedded_style != style or not family.startswith('Mona Sans'):
                raise ValueError(f'Face metadata mismatch for {source}: {family}, {axes}, {embedded_style}')
            put(OUT / name, raw)
            fetched[url] = raw
            manifest.append({'family': 'Mona Sans', 'style': style, 'weights': '200 900',
                             'axes': {k: list(v) for k, v in axes.items()},
                             'file': name, 'source': url, 'license': license_url,
                             'source_sha256': hashlib.sha256(raw).hexdigest(),
                             'woff2_sha256': hashlib.sha256(raw).hexdigest(),
                             'bytes': len(raw)})
        rules.append(face('Mona Sans', style, '200 900', name, stretch, MONA_SIZE_ADJUST))

def bodoni_moda(rules, manifest):
    license_url = BODONI_BASE + 'OFL.txt'
    notice = urlopen(license_url).read()
    if (hashlib.sha256(notice).hexdigest() != BODONI_LICENSE_SHA256 or
            b'SIL OPEN FONT LICENSE Version 1.1' not in notice):
        raise ValueError('Unexpected license for Bodoni Moda')
    put(OUT / 'licenses' / 'bodonimoda-OFL.txt', clean_notice(notice))
    for style, source, expected_sha256 in BODONI:
        url = BODONI_BASE + 'fonts/variable/' + quote(source)
        raw = urlopen(url).read()
        source_sha256 = hashlib.sha256(raw).hexdigest()
        if source_sha256 != expected_sha256:
            raise ValueError(f'Unexpected source checksum for Bodoni Moda {style}')
        font = TTFont(BytesIO(raw), recalcTimestamp=False)
        axes = {a.axisTag: (a.minValue, a.maxValue) for a in font['fvar'].axes}
        embedded_style = 'italic' if font['OS/2'].fsSelection & 1 else 'normal'
        family = font['name'].getDebugName(16) or font['name'].getDebugName(1)
        if axes != BODONI_AXES or embedded_style != style or family != 'Bodoni Moda':
            raise ValueError(f'Face metadata mismatch for {source}: '
                             f'{family}, {axes}, {embedded_style}')
        optical_axis = next((a for a in font['fvar'].axes if a.axisTag == 'opsz'), None)
        if optical_axis is None or optical_axis.defaultValue != BODONI_DISPLAY_OPSZ:
            raise ValueError(f'Unexpected default optical size for {source}')
        glyphs = font.getGlyphOrder()
        cmap = font.getBestCmap()
        if not BODONI_REQUIRED_TABLES.issubset(font.keys()):
            raise ValueError(f'Missing source shaping or variation table for {source}')
        instance = instantiateVariableFont(font, {'opsz': BODONI_DISPLAY_OPSZ}, inplace=False)
        output_axes = {a.axisTag: (a.minValue, a.maxValue) for a in instance['fvar'].axes}
        if (output_axes != BODONI_OUTPUT_AXES or instance.getGlyphOrder() != glyphs or
                instance.getBestCmap() != cmap or
                not BODONI_REQUIRED_TABLES.issubset(instance.keys())):
            raise ValueError(f'Optical-size instancing lost weight variation or glyphs for {source}')
        tables = set(instance.keys())
        instance.flavor = 'woff2'
        buffer = BytesIO()
        instance.save(buffer)
        data = buffer.getvalue()
        rebuilt = TTFont(BytesIO(data), recalcTimestamp=False)
        if (rebuilt.getGlyphOrder() != glyphs or rebuilt.getBestCmap() != cmap or
                set(rebuilt.keys()) != tables or
                {a.axisTag: (a.minValue, a.maxValue) for a in rebuilt['fvar'].axes} != BODONI_OUTPUT_AXES or
                ('italic' if rebuilt['OS/2'].fsSelection & 1 else 'normal') != style):
            raise ValueError(f'WOFF2 conversion lost glyphs or tables for {source}')
        name = f'bodonimoda-{style}.woff2'
        put(OUT / name, data)
        manifest.append({'family': 'Bodoni Moda', 'style': style, 'weights': '400 900',
                         'axes': {key: list(value) for key, value in output_axes.items()},
                         'pinned_axes': {'opsz': BODONI_DISPLAY_OPSZ},
                         'file': name, 'source': url, 'license': license_url,
                         'source_sha256': source_sha256,
                         'woff2_sha256': hashlib.sha256(data).hexdigest(),
                         'bytes': len(data)})
        rules.append(face('Bodoni Moda', style, '400 900', name))

def brier_artifacts():
    """Refuse commercial-font artifacts in the open-font source directory."""
    fonts = (p for p in OUT.rglob('*')
             if p.is_file() and 'brier' in p.stem.lower() and
             p.suffix.lower() in {'.woff', '.woff2', '.ttf', '.otf'})
    notices = (p for p in (OUT / 'licenses').iterdir()
               if 'brier' in p.name.lower())
    return sorted((*fonts, *notices), key=str)


def check_no_brier_input():
    """Never read, inspect, transform, or publish a commercial Brier file."""
    configured = sorted(name for name in os.environ if name.startswith('CIRS_BRIER_'))
    artifacts = brier_artifacts()
    if configured:
        raise ValueError(f'{BRIER_REQUIRED}: tools/make-fonts.py only regenerates open fonts; '
                         'private production staging must handle seller-supplied Brier WOFF2 files. '
                         'Unset ' + ', '.join(configured) + ' before running this command.')
    if artifacts:
        raise ValueError(f'{BRIER_REQUIRED}: commercial-font output is present in the '
                         'public source tree: '
                         + ', '.join(str(p.relative_to(ROOT)) for p in artifacts)
                         + '. Remove it from the public tree before regenerating.')
def main():
    check_no_brier_input()
    rules, manifest = [], []
    mona_sans(rules, manifest)
    bodoni_moda(rules, manifest)
    google_fonts(rules, manifest)
    put(ROOT / 'assets/css/fonts.css', ('/* Generated by tools/make-fonts.py. Local fonts only; licenses in assets/fonts/licenses/. */\n\n' + '\n\n'.join(rules) + '\n').encode())
    put(OUT / 'manifest.json', (json.dumps({'revision': REVISION, 'mona_sans_revision': MONA_REVISION,
                                            'bodoni_moda_revision': BODONI_REVISION,
                                            'fonts': manifest}, indent=2) + '\n').encode())
    files = {f['file']: f['bytes'] for f in manifest}
    print(f'Built {len(files)} WOFF2 files; {sum(files.values()):,} bytes; '
          f'{len(list((OUT / "licenses").iterdir()))} licence notices retained.')

if __name__ == '__main__':
    main()
