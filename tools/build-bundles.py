#!/usr/bin/env python3
"""Build the parked content editor as one self-contained file.

There used to be a dist/cirs-home.html here as well: the whole site inlined
into a single file to email or open from a USB stick. That made sense while
the site was one page. It is now ten, and a single file cannot carry them —
its menu links would all point at pages that are not in the bundle — so it is
gone. To hand someone the site, send them the Netlify preview or the zip of
index.html + assets/, both of which are the real thing.

What remains is the editor:

    cirs-editor.html      the page wrapped in the point-and-click content
                          editor — click any headline and type, click any
                          photo to replace it, download the result. No CDN
                          tags, so it works with no internet at all.

    python3 tools/build-bundles.py --editor

The editor is parked: not built by default, not committed, and its 11 MB is
why. Its sources, assets/css/editor.css and assets/js/editor.js, stay in the
repository and stay maintained, so this rebuilds a current editor rather than
a fossil.

Note it wraps index.html only, so today it edits the home page alone. Bringing
the editor back properly means teaching it the other nine pages, and restoring
a CI check that the committed copy is current — an unchecked bundle rots.
"""

import mimetypes
import os
import re
import sys
from base64 import b64encode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel, binary=False):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        sys.exit(f"build-bundles: missing {rel}")
    return open(path, "rb").read() if binary else open(path, encoding="utf-8").read()


def data_uri(rel):
    mime = mimetypes.guess_type(rel)[0] or "application/octet-stream"
    return f"data:{mime};base64," + b64encode(read(rel, binary=True)).decode("ascii")


def inline_media(html):
    """Replace every assets/img and assets/video reference with a data URI."""
    seen = {}

    def swap(m):
        rel = m.group(1)
        if rel not in seen:
            seen[rel] = data_uri(rel)
        return seen[rel]

    return re.sub(r'(assets/(?:img|video)/[A-Za-z0-9._-]+)(?:\?[^"\']*)?', swap, html)


def build(editor):
    html = read("index.html")

    for name in ("cirs", "pages"):
        css = read(f"assets/css/{name}.css")
        html = re.sub(rf'<link rel="stylesheet" href="assets/css/{name}\.css[^"]*">',
                      lambda _, c=css: "<style>\n" + c + "</style>", html)

    js = read("assets/js/cirs.js")
    html = re.sub(r'<script src="assets/js/cirs\.js[^"]*" defer></script>',
                  lambda _: "<script>\n" + js + "</script>", html)

    if editor:
        # The editor must work with no connection at all, so the CDN tags go.
        html = re.sub(r'<script src="https://[^"]*"[^>]*></script>\n?', "", html)
        html = html.replace("</head>", "<style>\n" + read("assets/css/editor.css") + "</style>\n</head>")
        html = html.replace("</body>", "<script>\n" + read("assets/js/editor.js") + "</script>\n</body>")
        html = re.sub(r"<title>[^<]*</title>",
                      lambda _: "<title>CIRS Content Editor</title>", html)

    return inline_media(html)


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)
    print(f"  write  {rel} ({len(text):,} chars)")


if __name__ == "__main__":
    if "--editor" not in sys.argv[1:]:
        sys.exit("build-bundles: nothing to do without --editor (see the "
                 "module docstring; the site bundle was retired when the site "
                 "became ten pages)")
    write("cirs-editor.html", build(editor=True))
