#!/usr/bin/env python3
"""Check that every link and asset reference in index.html resolves.

Deliberately offline. External URLs are checked for shape only, never fetched:
a CI job that reaches out to fonts.googleapis.com and a CDN fails on their bad
days rather than on ours, and a check that goes red for reasons nobody in this
repository can fix is a check people learn to ignore.

What it does check:

  * every in-page href="#id" points at an element that exists — the drawer and
    the footer are the site's only navigation, so a typo there is a dead end
    with nothing to catch it
  * every assets/... reference exists on disk, at the exact case used
  * every file in assets/img and assets/video is referenced by something
  * external references are absolute https:// URLs

    python3 tools/check-links.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "index.html"

# href="#" is the site's own placeholder for a page that does not exist yet —
# the drawer and footer are full of them. They are intentional, not broken.
PLACEHOLDER = "#"


def main():
    html = open(os.path.join(ROOT, PAGE), encoding="utf-8").read()
    problems = []

    ids = set(re.findall(r'\bid="([^"]+)"', html))

    # Every reference the page makes, from any attribute that takes a URL.
    # `content` is only a URL on the social-card metas — elsewhere it holds
    # prose and colours, so take only the values that look like a reference.
    refs = re.findall(r'\b(?:href|src|poster)="([^"]+)"', html)
    refs += [
        c for c in re.findall(r'\bcontent="([^"]+)"', html)
        if c.startswith(("assets/", "http://", "https://"))
    ]

    referenced = set()
    for ref in refs:
        if ref.startswith("#"):
            if ref != PLACEHOLDER and ref[1:] not in ids:
                problems.append(f"{PAGE}: href=\"{ref}\" — no element with that id")
        elif ref.startswith("assets/"):
            path = ref.split("?", 1)[0]
            referenced.add(path)
            if not os.path.exists(os.path.join(ROOT, path)):
                problems.append(f"{PAGE}: {path} — referenced but not in the repository")
        elif ref.startswith("http://"):
            problems.append(f"{PAGE}: {ref} — http, should be https")
        elif ref.startswith(("https://", "mailto:", "tel:", "data:")):
            pass
        elif re.match(r"^[\w./-]+$", ref) and "." in ref:
            problems.append(f"{PAGE}: {ref} — relative reference outside assets/")

    for folder in ("assets/img", "assets/video"):
        for name in sorted(os.listdir(os.path.join(ROOT, folder))):
            rel = f"{folder}/{name}"
            if rel not in referenced:
                problems.append(f"{rel} — in the repository but nothing references it")

    if problems:
        print(f"check-links: {len(problems)} problem(s)\n")
        for p in problems:
            print("  " + p)
        sys.exit(1)

    print(f"check-links: {len(refs)} references, all resolve")


if __name__ == "__main__":
    main()
