#!/usr/bin/env python3
"""Build the two single-file bundles from index.html and assets/.

index.html is the source of truth; both bundles below are derived from it and
should never be hand-edited.

    dist/cirs-home.html   the whole site in one file — every stylesheet,
                          script, photograph and the campus video inlined.
                          Email it, open it from a USB stick, hand it to a
                          web host. Keeps the CDN <script> tags, so the
                          scroll choreography needs a connection; without
                          one the page still reads correctly.

    cirs-editor.html      the same page wrapped in the point-and-click
                          content editor. No CDN tags at all, so it works
                          with no internet whatsoever.

    python3 tools/build-bundles.py
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

    css = read("assets/css/cirs.css")
    html = re.sub(r'<link rel="stylesheet" href="assets/css/cirs\.css[^"]*">',
                  lambda _: "<style>\n" + css + "</style>", html)

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
    write("dist/cirs-home.html", build(editor=False))
    write("cirs-editor.html", build(editor=True))
