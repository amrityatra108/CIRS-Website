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
  * every href="#" — there is no longer anywhere on the site such a link is
    meant to be, so one appearing again is a dead link, not a placeholder
  * every assets/... reference exists on disk, at the exact case used
  * every file in assets/img and assets/video is referenced by some page
  * external references are absolute https:// URLs

    python3 tools/check-links.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directories that hold no page of the site, so the walk below does not
# descend into them. _site is the staged deploy — a copy of every page — and
# walking it would check the whole site twice and report each page as its own
# duplicate.
def pages():
    """Every page of this site — which is exactly what build-site.py writes.

    Asking the builder rather than listing *.html is what keeps the two in
    step. The repository also holds Digital/, docs/ and pdf/, material from
    the old website that nothing here links to and that stage-deploy.py has
    never copied; a walk of the tree checked those as though they were pages
    of this site and reported their old links as faults. And a slug may name
    a directory now — "curriculum/ib-diploma" — which a flat listing missed
    altogether, leaving its links unchecked.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "buildsite", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "build-site.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return sorted(f"{slug}.html" for slug in mod.PAGES)


def resolve(name, ref):
    """A reference as the browser reads it: relative to the page it is on.

    "../assets/img/x.jpg" on curriculum/ib-diploma.html is assets/img/x.jpg;
    the same string on a page at the root would point outside the site.
    """
    joined = os.path.join(os.path.dirname(name), ref)
    return os.path.normpath(joined).replace(os.sep, "/")


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
            if ref == "#":
                # This used to be allowed: the footer and drawer carried a
                # handful as placeholders for pages nobody had built. They
                # have all since been pointed at real pages or removed, so
                # the allowance now only hides the next dead link.
                problems.append(f'{name}: href="#" — goes nowhere; link it or remove it')

            elif ref.startswith("#"):
                if ref[1:] not in ids[name]:
                    problems.append(f'{name}: href="{ref}" — no element with that id on this page')

            elif ref.startswith("http://"):
                problems.append(f"{name}: {ref} — http, should be https")

            elif ref.startswith(("https://", "mailto:", "tel:", "data:")):
                pass    # external, and deliberately never fetched

            elif ref.endswith(".html") or ".html#" in ref:
                target, _, anchor = ref.partition("#")
                target = resolve(name, target)
                if target not in docs:
                    problems.append(f"{name}: {ref} — links to a page that does not exist")
                elif anchor and anchor not in ids[target]:
                    problems.append(f"{name}: {ref} — {target} has no element with id \"{anchor}\"")

            elif "assets/" in ref.split("?", 1)[0]:
                path = resolve(name, ref.split("?", 1)[0])
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
