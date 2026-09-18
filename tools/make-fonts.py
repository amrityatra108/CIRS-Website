#!/usr/bin/env python3
"""Mirror the site's three typefaces from Google Fonts into the repository.

    assets/fonts/*.woff2      the font files
    assets/css/fonts.css      the @font-face rules that point at them

The site used to load these from fonts.googleapis.com. Self-hosting them
does three things:

  * It takes a render-blocking stylesheet on a third-party origin out of
    every page. A visitor in Coimbatore was paying a DNS lookup and a TLS
    handshake to Google before the first paint of any page on this site.
  * It stops every visitor's browser announcing itself to Google.
  * It makes the lettering checkable from a sandbox session. That was the
    largest remaining blind spot in CLAUDE.md: the proxy a session runs
    behind is not used by the browser, so fonts.googleapis.com was never
    reached and every screenshot rendered in the system fallback.

Only the subsets the site actually uses are kept. Every non-ASCII
character on the built site was checked against the unicode-ranges: latin,
latin-ext and devanagari cover all of them. The one exception is the arrow
U+2192, which none of these three families carries in any subset and which
therefore already falls back to a system face.

Re-run after changing a weight or adding a family, and commit what changes:

    python3 tools/make-fonts.py
"""

import hashlib
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FONTS = os.path.join(ROOT, "assets/fonts")
OUT_CSS = os.path.join(ROOT, "assets/css/fonts.css")

# The same request the <link> used to make. The Chrome user agent matters:
# Google serves woff2 to it and older, far larger formats to anything it
# does not recognise.
API = ("https://fonts.googleapis.com/css2"
       "?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500"
       "&family=Schibsted+Grotesk:wght@400;500;600;700"
       "&family=Tiro+Devanagari+Hindi&display=swap")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")

KEEP = {"latin", "latin-ext", "devanagari"}


def fetch(url, binary=False):
    r = subprocess.run(["curl", "-sS", "--fail", "-A", UA, url],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit(f"make-fonts: could not fetch {url[:80]}\n{r.stderr.decode()[:300]}")
    return r.stdout if binary else r.stdout.decode("utf-8")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main():
    css = fetch(API)
    os.makedirs(OUT_FONTS, exist_ok=True)

    rules, kept, dropped, seen = [], 0, 0, {}
    for block in re.split(r"(?=/\* [a-z-]+ \*/)", css):
        m = re.match(r"/\* ([a-z-]+) \*/", block.strip())
        if not m:
            continue
        subset = m.group(1)
        if subset not in KEEP:
            dropped += 1
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        sty = re.search(r"font-style:\s*(\w+)", block).group(1)
        wgt = re.search(r"font-weight:\s*(\d+)", block).group(1)
        rng = re.search(r"unicode-range:\s*([^;]+);", block, re.S).group(1)
        url = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", block).group(1)

        # Google serves these as variable fonts, so one file commonly backs
        # several weights: 400, 500 and 600 of EB Garamond latin are all the
        # same URL. The filename therefore belongs to the URL, not to the
        # rule — naming per rule wrote nine files and referenced twenty-one,
        # and the twelve that were never written would have 404'd in
        # production with the whole family falling back.
        if url in seen:
            name = seen[url]
        else:
            name = f"{slug(fam)}{'-italic' if sty == 'italic' else ''}-{subset}.woff2"
            # Distinct URLs must not collide on one name.
            if name in set(seen.values()):
                name = (f"{slug(fam)}-{wgt}"
                        f"{'-italic' if sty == 'italic' else ''}-{subset}.woff2")
            data = fetch(url, binary=True)
            path = os.path.join(OUT_FONTS, name)
            # Byte-identical downloads are not rewritten, so re-running this
            # leaves the working tree clean when nothing upstream has moved.
            if not (os.path.exists(path) and open(path, "rb").read() == data):
                with open(path, "wb") as f:
                    f.write(data)
            seen[url] = name
        rules.append(
            f"/* {fam} {wgt}{' italic' if sty == 'italic' else ''} — {subset} */\n"
            f"@font-face {{\n"
            f"  font-family: '{fam}';\n"
            f"  font-style: {sty};\n"
            f"  font-weight: {wgt};\n"
            f"  font-display: swap;\n"
            f"  src: url(../fonts/{name}) format('woff2');\n"
            f"  unicode-range: {' '.join(rng.split())};\n"
            f"}}"
        )
        kept += 1

    header = (
        "/* ============================================================\n"
        "   The site's three typefaces, served from this repository.\n"
        "   ------------------------------------------------------------\n"
        "   Generated by tools/make-fonts.py — do not edit by hand; the\n"
        "   next run overwrites it. Re-run that script after changing a\n"
        "   weight or adding a family.\n"
        f"   Subsets: {', '.join(sorted(KEEP))}. Everything else Google\n"
        "   offers for these families is dropped, because no character on\n"
        "   the built site falls in it.\n"
        "   ============================================================ */\n\n"
    )
    with open(OUT_CSS, "w", encoding="utf-8") as f:
        f.write(header + "\n\n".join(rules) + "\n")

    total = sum(os.path.getsize(os.path.join(OUT_FONTS, n)) for n in set(seen.values()))
    print(f"  {len(set(seen.values()))} files, {total // 1024} KB in assets/fonts/")
    print(f"  {kept} @font-face rules kept, {dropped} dropped as unused subsets")
    print(f"  wrote assets/css/fonts.css")


if __name__ == "__main__":
    main()
