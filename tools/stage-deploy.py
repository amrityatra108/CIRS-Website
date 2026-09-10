#!/usr/bin/env python3
"""Stage exactly the files that should be published, into _site/.

The repository root holds the generated pages next to the things that build
them — tools/, .github/, the markdown, and node_modules when CI has run. A
deploy of the repository root would publish all of it. So the publishable
files are copied into _site/, and netlify.toml points Netlify at that
directory rather than the root.

What ships: the eleven pages, **only the assets a page actually references**,
and the two files that keep a review preview out of search results.

That last point stopped being a detail when the source photographs arrived.
assets/img now holds 150 MB of unedited originals — 8192px camera files that
tools/make-header.py crops and grades down to a 140 KB banner. They belong in
the repository, because the next banner will be made from them. They must not
be uploaded to a web host: a copy-everything stage produced a 153 MB deploy
of a 6 MB site. So the reference list, not the directory listing, decides.

    python3 tools/build-site.py     # pages first
    python3 tools/stage-deploy.py   # then stage them
"""

import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_site")

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

    # Every assets/ path any page mentions, in an attribute or a stylesheet.
    wanted = set()
    for name in pages:
        html = open(os.path.join(ROOT, name), encoding="utf-8").read()
        wanted |= {r.split("?")[0] for r in re.findall(r'"(assets/[^"]+)"', html)}
    for sheet in [w for w in sorted(wanted) if w.endswith(".css")]:
        css = open(os.path.join(ROOT, sheet), encoding="utf-8").read()
        for url in re.findall(r'url\(\s*[\'"]?(assets/[^)\'"]+)', css):
            wanted.add(url.split("?")[0])

    missing = [w for w in sorted(wanted) if not os.path.exists(os.path.join(ROOT, w))]
    if missing:
        raise SystemExit("stage-deploy: referenced but not in the repository:\n  "
                         + "\n  ".join(missing))

    kept = 0
    for rel in sorted(wanted):
        dest = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel), dest)
        kept += 1

    on_disk = sum(1 for _, _, fs in os.walk(os.path.join(ROOT, "assets")) for _ in fs)
    if on_disk > kept:
        print(f"  left behind {on_disk - kept} unreferenced asset(s) — "
              f"source photographs and the parked editor stay out of the deploy")

    open(os.path.join(OUT, "_headers"), "w", encoding="utf-8").write(HEADERS)
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(ROBOTS)

    total = sum(os.path.getsize(os.path.join(r, f))
                for r, _, fs in os.walk(OUT) for f in fs)
    print(f"  staged _site/  {len(pages)} pages, {kept} assets, "
          f"{total/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
