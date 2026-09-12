"""The Crossroads archive — thirty-two editions of the CIRS monthly magazine.

The archive is deliberately convention over manifest. An issue needs no entry
here at all: drop

    assets/documents/crossroads/crossroads-issue-07.pdf
    assets/img/crossroads/issue-07.jpg

and Issue 07 stops being a placeholder and becomes a cover you can open. Both
are optional and independent — a cover with no PDF still reads as a cover, a
PDF with no cover still opens from the designed placeholder. Nothing else
changes, and nobody has to edit a list to publish an issue.

OVERRIDES is the escape hatch for the one file that will not follow the
naming, and for a title an issue has earned beyond its number.

Until the school supplies them every issue renders as an art-directed
typographic cover that says plainly that the PDF is coming, rather than as a
grey box or an invented magazine cover.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The school has published thirty-two editions. Raise this as they publish.
COUNT = 32

PDF_DIR = "assets/documents/crossroads"
COVER_DIR = "assets/img/crossroads"

# issue number -> any of {"pdf", "cover", "title"} to override the convention.
OVERRIDES = {}

# Four cover compositions, cycled so the wall has rhythm without becoming a
# scrapbook: where the number sits, and which rule it hangs from. The fifth
# is the standing "latest" treatment, given to the highest-numbered issue.
VARIANTS = 4


def _exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))


def _resolve(number, key, default_rel):
    over = OVERRIDES.get(number, {}).get(key)
    rel = over or default_rel
    return rel if _exists(rel) else None


def issues():
    """Every edition, newest first — an archive is read from the top."""
    out = []
    for n in range(COUNT, 0, -1):
        pdf = _resolve(n, "pdf", f"{PDF_DIR}/crossroads-issue-{n:02d}.pdf")
        cover = _resolve(n, "cover", f"{COVER_DIR}/issue-{n:02d}.jpg")
        out.append({
            "number": n,
            "label": f"Issue {n:02d}",
            "title": OVERRIDES.get(n, {}).get("title"),
            "pdf": pdf,
            "cover": cover,
            "status": "available" if pdf else "coming-soon",
            "variant": (n - 1) % VARIANTS + 1,
            "latest": n == COUNT,
        })
    return out


def published():
    return sum(1 for i in issues() if i["status"] == "available")
