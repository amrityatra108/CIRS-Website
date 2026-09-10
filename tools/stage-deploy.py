#!/usr/bin/env python3
"""Stage exactly the files that should be published, into _site/.

The repository root holds the generated pages next to the things that build
them — tools/, .github/, the markdown, and node_modules when CI has run. A
deploy of the repository root would publish all of it. So the publishable
files are copied into _site/, and netlify.toml points Netlify at that
directory rather than the root.

What ships: the eleven pages, assets/ (minus the parked editor's sources),
and the two files that keep a review preview out of search results.

    python3 tools/build-site.py     # pages first
    python3 tools/stage-deploy.py   # then stage them
"""

import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_site")

# The editor is parked and its sources are never referenced by a page.
SKIP_ASSETS = {"assets/css/editor.css", "assets/js/editor.js"}

HEADERS = """# Review preview — keep it out of search results. The pages still carry
# placeholder copy and an under-construction note. Delete this file, and
# robots.txt, for the real launch.
/*
  X-Robots-Tag: noindex
"""

ROBOTS = """# Review preview. Delete this file for the real launch.
User-agent: *
Disallow: /
"""


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    pages = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
    for name in pages:
        shutil.copy2(os.path.join(ROOT, name), os.path.join(OUT, name))

    kept = 0
    for folder, _, files in os.walk(os.path.join(ROOT, "assets")):
        for name in files:
            src = os.path.join(folder, name)
            rel = os.path.relpath(src, ROOT)
            if rel.replace(os.sep, "/") in SKIP_ASSETS:
                continue
            dest = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            kept += 1

    open(os.path.join(OUT, "_headers"), "w", encoding="utf-8").write(HEADERS)
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(ROBOTS)

    total = sum(os.path.getsize(os.path.join(r, f))
                for r, _, fs in os.walk(OUT) for f in fs)
    print(f"  staged _site/  {len(pages)} pages, {kept} assets, "
          f"{total/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
