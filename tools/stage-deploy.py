#!/usr/bin/env python3
"""Stage exactly the files that should be published, into _site/.

The repository root holds the generated pages next to the things that build
them — tools/, .github/, the markdown, and node_modules when CI has run. A
deploy of the repository root would publish all of it. So the publishable
files are copied into _site/, and netlify.toml points Netlify at that
directory rather than the root.

What ships: every page, **only the assets a page actually references**,
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

    # The pages of the site are the ones build-site.py writes, which is not
    # the same as every .html in the tree: Digital/, docs/ and pdf/ hold
    # material from the old website that nothing here links to. Asking the
    # builder also picks up a page whose slug names a directory —
    # "curriculum/ib-diploma" — which a flat listing left out of the deploy
    # entirely, so the page 404'd in production while every check passed.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "buildsite", os.path.join(ROOT, "tools/build-site.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pages = sorted(f"{slug}.html" for slug in mod.PAGES)

    for name in pages:
        dest = os.path.join(OUT, name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, name), dest)

    # Every assets/ path any page mentions, in an attribute or a stylesheet.
    # A page inside a directory reaches them with "../assets/...", so each
    # reference is resolved against the page that makes it.
    wanted = set()
    for name in pages:
        html = open(os.path.join(ROOT, name), encoding="utf-8").read()
        here = os.path.dirname(name)
        for r in re.findall(r'"((?:\.\./)*assets/[^"]+)"', html):
            # A srcset holds several candidates, separated by commas, each
            # with a width or density descriptor after its path. Taking only
            # the first field of the whole value shipped the smallest cut
            # and left every larger one to 404 in production.
            for cand in r.split(","):
                path = cand.strip().split()[0].split("?")[0] if cand.strip() else ""
                if "assets/" not in path:
                    continue
                rel = os.path.normpath(os.path.join(here, path))
                wanted.add(rel.replace(os.sep, "/"))
    # A stylesheet's url() is resolved by the browser against the stylesheet,
    # not against the page — so "../fonts/x.woff2" in assets/css/fonts.css
    # means assets/fonts/x.woff2. Matching only paths that already begin
    # with "assets/" missed every relative one, and the fonts would have
    # deployed as 404s with the whole site falling back to system faces.
    for sheet in [w for w in sorted(wanted) if w.endswith(".css")]:
        css = open(os.path.join(ROOT, sheet), encoding="utf-8").read()
        # An inline SVG data: URI carries its own url(#id) for a filter, and
        # scanning the raw text picks that up as a path. Take the data URIs
        # out before looking for references.
        css = re.sub(r'url\(\s*[\'"]?data:[^)]*\)', 'url(data:)', css)
        base = os.path.dirname(sheet)
        for url in re.findall(r'url\(\s*[\'"]?([^)\'"]+)', css):
            url = url.split("?")[0].strip()
            if url.startswith(("http:", "https:", "data:", "//", "#")):
                continue
            rel = os.path.normpath(os.path.join(base, url)).replace(os.sep, "/")
            if rel.startswith("assets/"):
                wanted.add(rel)

    # The Founder iframe is a self-contained bundle with relative JS imports
    # and texture URLs. Ship its runtime files, not the directory as a file.
    founder_bundle = "assets/founder-opening"
    if any(w.rstrip("/") == founder_bundle or w.startswith(founder_bundle + "/")
           for w in wanted):
        wanted.discard(founder_bundle)
        wanted.discard(founder_bundle + "/")
        for directory, _, names in os.walk(os.path.join(ROOT, founder_bundle)):
            for name in names:
                if name == "gurudev-color.png":
                    continue  # Rejected generation, retained locally but not used.
                wanted.add(os.path.relpath(os.path.join(directory, name), ROOT).replace(os.sep, "/"))

    # Distribute the font licenses and provenance alongside the self-hosted files.
    for directory, _, names in os.walk(os.path.join(ROOT, "assets/fonts/licenses")):
        wanted.update(os.path.relpath(os.path.join(directory, name), ROOT).replace(os.sep, "/")
                      for name in names)
    wanted.add("assets/fonts/manifest.json")

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
