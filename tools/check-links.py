#!/usr/bin/env python3
"""Check that every link and asset reference across the site resolves.

Deliberately offline. External URLs are checked for shape only, never fetched:
a CI job that reaches out to fonts.googleapis.com and a CDN fails on their bad
days rather than on ours, and a check that goes red for reasons nobody in this
repository can fix is a check people learn to ignore.

Since the site became ten pages, the menu is the navigation, so a broken link
between pages is a dead end with nothing to catch it. This therefore checks:

  * every href="page.html#anchor" — that the page exists AND that the anchor
    exists on that page, which is the failure a single-page checker misses
  * every same-page href="#id" points at an element on that page
  * every assets/... reference exists on disk, at the exact case used
  * every file in assets/img and assets/video is referenced by some page
  * external references are absolute https:// URLs

    python3 tools/check-links.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# href="#" is the site's own placeholder for a page that does not exist yet —
# the drawer and footer still carry a few. They are intentional, not broken.
PLACEHOLDER = "#"


def pages():
    return sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))


def main():
    docs = {name: open(os.path.join(ROOT, name), encoding="utf-8").read() for name in pages()}
    ids = {name: set(re.findall(r'\bid="([^"]+)"', html)) for name, html in docs.items()}
    problems, referenced, checked = [], set(), 0

    for name, html in docs.items():
        refs = re.findall(r'\b(?:href|src|poster)="([^"]+)"', html)
        refs += [c for c in re.findall(r'\bcontent="([^"]+)"', html)
                 if c.startswith(("assets/", "http://", "https://"))]
        checked += len(refs)

        for ref in refs:
            if ref.startswith("#"):
                if ref != PLACEHOLDER and ref[1:] not in ids[name]:
                    problems.append(f'{name}: href="{ref}" — no element with that id on this page')

            elif ref.startswith("http://"):
                problems.append(f"{name}: {ref} — http, should be https")

            elif ref.startswith(("https://", "mailto:", "tel:", "data:")):
                pass    # external, and deliberately never fetched

            elif ref.endswith(".html") or ".html#" in ref:
                target, _, anchor = ref.partition("#")
                if target not in docs:
                    problems.append(f"{name}: {ref} — links to a page that does not exist")
                elif anchor and anchor not in ids[target]:
                    problems.append(f"{name}: {ref} — {target} has no element with id \"{anchor}\"")

            elif ref.startswith("assets/"):
                path = ref.split("?", 1)[0]
                referenced.add(path)
                if not os.path.exists(os.path.join(ROOT, path)):
                    problems.append(f"{name}: {path} — referenced but not in the repository")

            elif re.match(r"^[\w./-]+$", ref) and "." in ref:
                problems.append(f"{name}: {ref} — relative reference outside assets/")

    # Walk, rather than list: assets/img has subdirectories now (the collage
    # keeps its hundred-odd tiles in assets/img/glimpses), and a flat listing
    # reported the directory itself as an unreferenced file.
    for folder in ("assets/img", "assets/video"):
        for dirpath, _, filenames in os.walk(os.path.join(ROOT, folder)):
            for filename in sorted(filenames):
                rel = os.path.relpath(os.path.join(dirpath, filename), ROOT).replace(os.sep, "/")
                if rel not in referenced:
                    problems.append(f"{rel} — in the repository but no page references it")

    if problems:
        print(f"check-links: {len(problems)} problem(s)\n")
        for p in problems:
            print("  " + p)
        sys.exit(1)

    print(f"check-links: {len(docs)} pages, {checked} references, all resolve")


if __name__ == "__main__":
    main()
