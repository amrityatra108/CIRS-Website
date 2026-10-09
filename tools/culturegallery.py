"""What the CIRS Cultural Gallery gathers, beyond its original photographs.

tools/artswall.py lists the wall's first seventy-five photographs. This module
lists everything else the school's other pages show of its arts, its music, its
theatre, its festivals and its students' own making, so that those photographs
can be in the wall as well. It reads each page's own record of its photographs
(tools/festivals.py, theatre.py, captures.py, art-attack.json, anandutsav.py,
cvpnews.py, sakshi.py) and takes from them nothing but the file, the occasion
and the words the school already published about it. No caption, date or name
is written here.

The groups, in the order a duplicate is settled in (the first to claim a
photograph keeps it):

    Theatre     tools/theatre.py       Anand Utsav 2025 and Masquerade 2025
    Festivals   tools/festivals.py     the seven festivals, 2023-2026
    Art Attack  tools/art-attack.json  the photographs, and the students'
                                       paintings, drawings and crafts the
                                       Art Attack page shows
    Captures    tools/captures.py      the photography journal
    News        anandutsav.py, cvpnews.py, sakshi.py, newsarticles.py
                                       the festival, performance and talent
                                       frames of the school's own reports

What is left out, and why:

  * Frames that are about something else. Of a report's photographs only those
    that show a festival, a performance or a student's own making are taken
    (NEWS below); an award line-up, a classroom or a parade stays on its own
    page. The selection is by what the frame shows, listed photograph by
    photograph, so adding a report here is a decision, not a side effect.
  * Photographs that are already on the wall under another name (DUPLICATES).
    The same occasion photographed twice is kept once; the list records which
    were set aside and which kept.
  * Anything the source modules themselves withhold. Their own rules (festival
    frames with an infant as the subject, art without a legible credit) are
    theirs, and this module inherits them rather than re-deciding.

tools/make-arts-wall.py cuts, grades and writes the files, and records what it
wrote in tools/culture-gallery.json, which tools/artswall.py reads; so the site
build needs no image library and one list says what is on the wall.
"""

import json
import os

import anandutsav
import artattack
import captures
import cvpnews
import festivals
import sakshi
import theatre

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# How often a photograph turns up when the wall picks one for a tile. A
# painting scanned from a magazine is one of two hundred and eighty; a photograph
# of a festival is one of a few hundred. Without this the wall would be mostly
# paper. 2 is the default; the paintings and the nature journal are 1.
WEIGHT = {"Theatre": 2, "Festivals": 2, "Art Attack": 2, "Work": 1, "Captures": 1, "News": 2}

# Photographs set aside because the wall already shows the same frame: name ->
# the photograph that stays. Found by tools/check-gallery-duplicates.py, which
# matches features rather than pixels, so a frame cut at another size or crop
# still matches, and checked by eye. Re-run it after adding anything here.
DUPLICATES = {
    # The Art Attack page's frames of the Fine Arts Week activities are the
    # wall's own, cut from the same camera originals.
    "aa-masks": "masks",
    "aa-floorwork": "floorwork",
    "aa-banner": "banner",
    "aa-handwork": "handwork",
    "aa-reading": "exhibition",
    # The CVP report's Masquerade frame is the Theatre page's roar.
    "news-masquerade-2025-1": "th-vasistha25-roar",
    # The Captures journal carries one kingfisher twice, once as a square cut
    # from a design file; the camera's own frame stays.
    "cap-kingfisher-blue-study": "cap-brown-bird-branch",
}

# Which photographs of each report the wall takes (1-based, as the report
# numbers them). A report not listed here is not on the wall.
NEWS = {
    # The school's CVP report, October 2025 - March 2026
    "cvp": {
        "diwali-2025":           ("Festivals", [1, 2, 3, 4]),
        "childrens-day-2025":    ("Festivals", [1, 2, 3]),
        "pongal-2026":           ("Festivals", [1, 2]),
        "vasant-panchami-2026":  ("Festivals", [1, 2]),
        "masquerade-2025":       ("Theatre",   [1, 2, 3]),
        "fine-arts-week-2026":   ("Arts",      [1, 2, 3, 4]),
        "inter-house-arts-2026": ("Arts",      [1, 2, 3, 4]),
        "french-and-talent-2025": ("Arts",     [1]),
        "language-week-2025":    ("Arts",      [1]),
    },
    # Chinmaya Sakshi, the Anand Utsav bulletin of October 2026
    "sakshi": {
        "holi-2026":                    ("Festivals", [1]),
        "ram-navami-2026":              ("Festivals", [1, 2, 3]),
        "hanuman-jayanti-2026":         ("Festivals", [1, 2]),
        "tamil-new-year-and-vishu-2026": ("Festivals", [1, 2]),
        "gurudev-jayanti-2026":         ("Festivals", [1, 2, 3]),
        "guru-poornima-2026":           ("Festivals", [1, 2, 3]),
        "gurudev-aaradhana-2026":       ("Festivals", [2, 3, 4]),
        "onam-2026":                    ("Festivals", [1, 2]),
        "raksha-bandhan-2026":          ("Festivals", [1, 2]),
        # Photograph 1 is a toddler in a Krishna costume: the Festivals page
        # leaves out any frame whose subject is an infant, and so does the wall.
        "krishna-janmashtami-2026":     ("Festivals", [2, 3]),
        "ganesh-chaturthi-2026":        ("Festivals", [1, 2, 3]),
        "teachers-day-2026":            ("Festivals", [1]),
        "interschool-competitions-2026": ("Arts",     [1]),
    },
}
# Anand Utsav 2026: the stage, the cake, the lamps. The speeches, the audience
# and the award line-ups are on the report's own page.
ANAND_UTSAV_2026 = [1, 4, 5, 6, 7, 8, 9, 10, 18]
# The two galleries the School published, of which only the festival is a
# festival; the Gayathri Havan is a ceremony and stays on its own page.
ARCHIVE_GALLERIES = ["vishu-tamil-puthandu"]


def _path(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def _item(name, group, cat, title, desc, src, kind="photo", weight=None):
    return {"name": name, "group": group, "cat": cat, "title": title, "desc": desc,
            "src": src, "kind": kind, "weight": weight or WEIGHT[group]}


def theatre_items():
    out = []
    for label, p in theatre.all_photos():
        if label == "Anand Utsav":
            cat = f"Theatre · {theatre.ANAND_UTSAV['event']}"
        elif label == "Masquerades":
            cat = "Theatre · Masquerade 2025"
        else:
            cat = f"Theatre · Masquerade 2025, {label} House"
        src = theatre.file(p, theatre.widths(p)[-1])
        out.append(_item(f"th-{p['name']}", "Theatre", cat, p["caption"], p["alt"], src))
    return out


def festival_items():
    out = []
    for name, (fest, year, when, caption, alt, *_rest) in festivals.PHOTOS.items():
        cat = f"Festivals · {festivals.NAMES[fest]}, {when}"
        out.append(_item(f"fest-{name}", "Festivals", cat, caption, alt,
                         f"assets/source/festivals/{name}.jpg"))
    return out


def art_attack_items():
    m = artattack.load()
    out = []
    for p in m["photos"]:
        src = p["files"][0]
        out.append(_item(f"aa-{p['id']}", "Art Attack", "Art Attack", p["caption"], p["alt"], src))
    for w in m["works"]:
        if not artattack.on_page(w):
            continue
        names, klass = artattack.credit(w)
        credit = ", ".join(x for x in (names, klass) if x)
        title = credit or artattack.source_line(w)
        desc = w["alt"] if not credit else f"{w['alt']}\n{artattack.source_line(w)}"
        label = artattack.CAT_LABEL.get(w["category"], "Work")
        out.append(_item(f"work-{w['id']}", "Work", f"Art Attack · {label}", title, desc,
                         w["files"][0], kind="art"))
    return out


def captures_items():
    m = json.load(open(os.path.join(HERE, "captures-gallery.json"), encoding="utf-8"))["images"]
    caption = {}
    for ch in captures.CHAPTERS:
        for row in ch["rows"]:
            for _src, name, text in row:
                caption[name] = text
    for _src, name, text, _w in captures.FEATURED:
        caption["featured/" + name] = text
    caption["end"] = captures.END[2]
    out = []
    for key, rec in m.items():
        out.append(_item("cap-" + key.replace("/", "-"), "Captures", "Captures", caption[key], "",
                         rec["full_path"]))
    # The frame the journal opens on is cut separately; its source is the same photograph.
    out.append(_item("cap-lead", "Captures", "Captures", captures.LEAD_CAPTION, "",
                     "assets/source/" + captures.LEAD_SOURCE))
    return out


def news_items():
    out = []
    for n in ANAND_UTSAV_2026:
        out.append(_item(f"au26-{n:02d}", "News", f"Festivals · Anand Utsav 2026, 5–7 October 2026",
                         "Anand Utsav 2026", anandutsav.PHOTOS[n - 1][2], anandutsav.photo_path(n)))
    for source, module in (("cvp", cvpnews), ("sakshi", sakshi)):
        by_slug = {a["slug"]: a for a in module.ARTICLES}
        for slug, (kind, numbers) in NEWS[source].items():
            art = by_slug[slug]
            for n in numbers:
                alt = art["photos"][n - 1][2]
                out.append(_item(f"news-{slug}-{n}", "News", f"{kind} · {art['date']}",
                                 art["title"], alt, module.photo_path(slug, n)))
    return out


def archive_items():
    import newsarticles
    out = []
    for art in newsarticles.ARTICLES:
        if art.get("gallery") not in ARCHIVE_GALLERIES:
            continue
        folder = f"assets/img/news-archive/{art['gallery']}"
        for f in sorted(os.listdir(_path(folder))):
            stem, ext = os.path.splitext(f)
            if ext not in (".jpg", ".webp") or stem.endswith(("-720", "-400", "-640", "-800")):
                continue
            out.append(_item(f"{art['gallery']}-{stem}", "News", f"Festivals · {art['date']}",
                             art["title"], "", f"{folder}/{f}"))
    return out


def collect():
    """Every photograph this module adds, in the order a duplicate is settled."""
    items = (theatre_items() + festival_items() + art_attack_items() + captures_items()
             + news_items() + archive_items())
    names = [i["name"] for i in items]
    assert len(names) == len(set(names)), "two photographs share a name"
    return [i for i in items if i["name"] not in DUPLICATES]


if __name__ == "__main__":
    items = collect()
    missing = [i["src"] for i in items if not os.path.exists(_path(i["src"]))]
    by = {}
    for i in items:
        by[i["group"]] = by.get(i["group"], 0) + 1
    print(len(items), "photographs", by)
    print("missing:", missing or "none")
