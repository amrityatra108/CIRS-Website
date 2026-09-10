#!/usr/bin/env python3
"""Rebuild the deployable site from a Claude artifact export.

The artifact is a single self-contained HTML file: styles inline, scripts
inline, every photograph and the campus video embedded as base64 data URIs.
That is fine to preview and impossible to host, so this script splits it back
into the shape the web server wants:

    assets/css/cirs.css     the artifact's <style> blocks
    assets/js/cirs.js       the artifact's inline <script> blocks
    assets/img/*, video/*   every data URI, written out as a real file
    index.html              the markup, with the curated <head> from
                            tools/head.html and external asset references

Media files are identified by the md5 of their decoded bytes, so re-running
this on an unchanged artifact is a no-op and a changed photograph keeps its
filename. A digest the table below does not know about is an error: name it
here first, so nothing lands in the repo as `image-7.jpg`.

    python3 tools/sync-from-artifact.py <artifact.html>
"""

import hashlib
import os
import re
import sys
from base64 import b64decode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CACHE_BUST = "b=4"


def fail(msg):
    sys.exit("sync-from-artifact: " + msg)


def load_media_table():
    """Read the digest -> filename table from the bottom of this file."""
    table = {}
    path = os.path.join(ROOT, "tools", "media.tsv")
    if not os.path.exists(path):
        fail("missing tools/media.tsv")
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            fail(f"tools/media.tsv:{n}: expected '<md5>\\t<path>'")
        table[parts[0]] = parts[1]
    return table


def main():
    if len(sys.argv) != 2:
        fail("usage: sync-from-artifact.py <artifact.html>")
    src = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    table = load_media_table()

    # The artifact host wraps the author's markup in its own <head>, carrying a
    # small reset of its own. Only what follows <body> is the design; taking
    # styles and scripts from the whole file would drag that reset in too.
    authored = re.sub(r"^.*?<body[^>]*>", "", src, count=1, flags=re.S)

    # --- styles and scripts -------------------------------------------------
    styles = re.findall(r"<style[^>]*>(.*?)</style>", authored, re.S)
    if not styles:
        fail("no <style> block found in the artifact")

    inline_js = [
        m.group(1)
        for m in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", authored, re.S)
    ]
    if not inline_js:
        fail("no inline <script> block found in the artifact")

    # --- media --------------------------------------------------------------
    written, unknown = set(), []

    def swap(m):
        raw = b64decode(m.group(2) + "===")
        digest = hashlib.md5(raw).hexdigest()
        dest = table.get(digest)
        if dest is None:
            unknown.append((digest, m.group(1), len(raw), m.start()))
            return m.group(0)
        path = os.path.join(ROOT, dest)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path) or open(path, "rb").read() != raw:
            open(path, "wb").write(raw)
            print(f"  media  {dest} ({len(raw):,} bytes)")
        written.add(dest)
        return dest

    body = re.sub(r"data:(image/[a-z0-9+]+|video/[a-z0-9]+);base64,([A-Za-z0-9+/=]+)",
                  swap, authored)

    if unknown:
        lines = "\n".join(
            f"  {d}\t<name>.{t.split('/')[1]}\t({n:,} bytes, at offset {o:,})"
            for d, t, n, o in unknown
        )
        fail(
            "the artifact contains media this repo has no name for.\n"
            "Add a row for each to tools/media.tsv, then re-run:\n" + lines
        )

    # --- markup -------------------------------------------------------------
    # Everything the wrapper or the head owns is dropped; what is left is the
    # document body exactly as the artifact author wrote it.
    body = re.sub(r"</body>.*$", "", body, count=1, flags=re.S)
    body = re.sub(r"<title>.*?</title>", "", body, count=1, flags=re.S)
    body = re.sub(r"<style[^>]*>.*?</style>", "", body, flags=re.S)
    body = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.S)
    body = re.sub(r'<link[^>]*href="https://fonts\.[^"]*"[^>]*>', "", body)
    body = normalise(body)
    body = body.strip("\n") + "\n"

    head = open(os.path.join(ROOT, "tools", "head.html"), encoding="utf-8").read()
    head = head.replace("{{CACHE_BUST}}", CACHE_BUST)

    ext_js = re.findall(r'<script[^>]*\bsrc="(https://[^"]+)"', authored)
    tags = "".join(f'<script src="{u}" defer></script>\n' for u in ext_js)
    tags += f'<script src="assets/js/cirs.js?{CACHE_BUST}" defer></script>\n'

    write(os.path.join(ROOT, "assets/css/cirs.css"), "\n".join(s.strip() for s in styles) + "\n")
    write(os.path.join(ROOT, "assets/js/cirs.js"), "\n".join(s.strip() for s in inline_js) + "\n")
    write(os.path.join(ROOT, "index.html"), head + "<body>\n" + body + tags + "</body>\n</html>\n")

    stale = sorted(
        os.path.relpath(os.path.join(r, f), ROOT)
        for r, _, fs in os.walk(os.path.join(ROOT, "assets/img"))
        for f in fs
    ) + sorted(
        os.path.relpath(os.path.join(r, f), ROOT)
        for r, _, fs in os.walk(os.path.join(ROOT, "assets/video"))
        for f in fs
    )
    orphans = [p for p in stale if p not in written]
    if orphans:
        print("  note: not referenced by this artifact: " + ", ".join(orphans))


def normalise(body):
    """Small corrections the artifact does not carry, reapplied on every sync.

    Keep this function tiny and mechanical. It exists because the artifact is
    the design tool's output and cannot be edited here; anything larger than an
    attribute belongs upstream in the artifact, not in a rewrite step.

    A <button> with no type defaults to type="submit". Neither button here has
    a form ancestor, so nothing actually submits, but the CI accessibility pass
    asks for the attribute and it costs nothing to be explicit.
    """
    return re.sub(r"<button(?![^>]*\btype=)", "<button type=\"button\"", body)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and open(path, encoding="utf-8").read() == text:
        return
    open(path, "w", encoding="utf-8").write(text)
    print(f"  write  {os.path.relpath(path, ROOT)} ({len(text):,} chars)")


if __name__ == "__main__":
    main()
