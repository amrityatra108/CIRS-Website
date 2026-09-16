#!/usr/bin/env python3
"""The Founder page's photographs, and what stands in for the ones we lack.

The page tells a story that runs from 1916 to the present, and the school's
archive of Pujya Gurudev is one frame: a colour transparency made at Sidhbari,
which tools/make-founder.py cuts three ways. Everything else the narrative
wants — the young journalist, the Uttarkashi years, the first yajnas — is not
in this repository and must not be invented or lifted off the web.

So a slot whose file is missing renders as a marked placeholder that says what
belongs there, exactly as tools/documents.py does for a PDF nobody has sent
yet. The page stays complete and honest, and a scan dropped in later needs no
markup change — only the file, and a rebuild.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# id -> (file under assets/img/founder, alt text, the label a gap shows)
SLOTS = {
    "hero": ("gurudev-hero.jpg",
             "Pujya Gurudev Swami Chinmayananda seated before the Himalaya at Sidhbari, "
             "one hand raised mid-sentence",
             "Archival portrait of Pujya Gurudev"),
    "portrait": ("gurudev-portrait.jpg",
                 "Pujya Gurudev Swami Chinmayananda in close view, speaking, "
                 "his raised hand holding a gesture",
                 "Archival portrait of Pujya Gurudev"),
    "himalaya": ("gurudev-himalaya.jpg",
                 "Pujya Gurudev Swami Chinmayananda seated beneath the Himalayan range",
                 "Archival photograph in the Himalaya"),
    # Not in the archive yet. Each says so on the page rather than borrowing
    # a photograph that is not the school's to use.
    "young": (None, "", "Balakrishna Menon before sannyasa — 1930s or 1940s"),
    "uttarkashi": (None, "", "The Uttarkashi years, under Swami Tapovan Maharaj"),
    "yajna": (None, "", "An early Jnana Yajna — the 1950s or 1960s"),
    "campus": ("../aerial-duo.jpg",
               "The CIRS campus in the Siruvani foothills from the air", ""),
    "students": ("../student-life.jpg",
                 "CIRS students on campus", ""),
}


def path(slot):
    """The deployable path for a slot, or None when the file is not here."""
    name = SLOTS[slot][0]
    if name is None:
        return None
    rel = os.path.normpath(os.path.join("assets/img/founder", name)).replace(os.sep, "/")
    return rel if os.path.exists(os.path.join(ROOT, rel)) else None


def missing():
    return [s for s in SLOTS if path(s) is None]
