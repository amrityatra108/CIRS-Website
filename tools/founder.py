#!/usr/bin/env python3
"""The Founder page's school-supplied archival photographs.

The archive now includes colour portraits and dated documentary scans. Slots
remain explicit so every image is used for a specific narrative purpose and a
missing file still becomes an honest, labelled gap rather than a broken image.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# id -> (file under assets/img/founder, alt text, gap label[, archival caption])
SLOTS = {
    "hero": ("gurudev-hero.jpg",
             "Pujya Gurudev Swami Chinmayananda seated before the Himalaya at Sidhbari, "
             "one hand raised mid-sentence",
             "Archival portrait of Pujya Gurudev"),
    "portrait": ("archive/p607-portrait.webp",
                 "A warm close portrait of Pujya Gurudev Swami Chinmayananda",
                 "Archival portrait of Pujya Gurudev"),
    "enquiry": ("gurudev-enquiry.jpg",
                "Pujya Gurudev Swami Chinmayananda holding a laboratory flask up to the "
                "light, examining it",
                "Archival photograph of Pujya Gurudev"),
    "himalaya": ("archive/p638-himalaya.webp",
                 "Pujya Gurudev Swami Chinmayananda seated before the Himalayan range",
                 "Archival photograph in the Himalaya"),
    "vision": ("archive/2353-yr67-community.webp",
               "Swami Chinmayananda welcomed by a community gathered around him", ""),
    "beginning": ("archive/official-chinmaya-context.webp",
                  "Swami Chinmayananda standing before the Himalayan foothills in an official "
                  "Chinmaya Mission portrait", "",
                  "A later portrait from Chinmaya Mission; shown as biographical context, not the 1916 birth event."),
    "education": ("archive/bsan3-education.webp",
                  "Balakrishna Menon seated with members of his family in an archival portrait", ""),
    "freedom": ("archive/bsan39-early-years.webp",
                "Balakrishna Menon as a young man in an archival outdoor portrait", ""),
    "sannyasa": ("archive/esan93-sannyasa.webp",
                 "Swami Chinmayananda with fellow sannyasis beside the Ganga in 1949", ""),
    "teaching": ("archive/1352-yr62-teaching.webp",
                 "Swami Chinmayananda seated at a low teaching desk during a discourse", ""),
    "lecture": ("archive/1499-yr67-lecture.webp",
                "Swami Chinmayananda speaking from a lectern at an early lecture series", ""),
    "mission": ("archive/1277-yr60-mission.webp",
                "Swami Chinmayananda in discussion with organisers at a Chinmaya Mission gathering", ""),
    "audience": ("archive/2451-yr71-audience.webp",
                 "A large audience gathered around Swami Chinmayananda for a discourse", ""),
    "writing": ("archive/2633-yr80-writing.webp",
                "Swami Chinmayananda writing at a desk with companions standing nearby", ""),
    "vhp": ("archive/2033-yr65-vhp.webp",
            "Swami Chinmayananda walking with a group at a public gathering in 1965", "",
            "Archival public appearance from 1965; shown as period context."),
    "legacy": ("archive/r664-contemplative.webp",
               "Swami Chinmayananda seated with his hands clasped in quiet contemplation", ""),
    "children": ("archive/2481-yr79-children.webp",
                 "Swami Chinmayananda seated with a large circle of children and families", ""),
    "community": ("archive/54yr270-community.webp",
                  "Swami Chinmayananda surrounded by children and members of a community", ""),
    "children_group": ("archive/esan173-children.webp",
                       "Swami Chinmayananda seated with children and families in an archival group photograph", ""),
    "campus": ("../assembly-front.jpg",
               "The school assembled in front of the main building at CIRS", ""),
    "students": ("../students.jpg",
                 "CIRS students standing together at a school gathering", ""),
}


def path(slot):
    """The deployable path for a slot, or None when the file is not here."""
    name = SLOTS[slot][0]
    if name is None:
        return None
    rel = os.path.normpath(os.path.join("assets/img/founder", name)).replace(os.sep, "/")
    return rel if os.path.exists(os.path.join(ROOT, rel)) else None


# The width a figure is drawn at, where it is not the usual column
# ("(max-width: 899px) 92vw, 44vw", in tools/build-site.py), measured.
SIZES = {
    "children": "(max-width: 899px) 92vw, (max-width: 1100px) 68vw, 62vw",
}
# Drawn cover-fitted far wider than its column at every size, so a smaller
# cut would never be the right one.
UNCUT = {"students"}

IMAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "founder-images.json")


def size(slot):
    """(width, height, smaller cut or None) for a slot's file, from
    tools/founder-images.json (tools/make-media.py), or None if not listed."""
    import json
    try:
        with open(IMAGES, encoding="utf-8") as f:
            info = json.load(f).get(SLOTS[slot][0])
    except FileNotFoundError:
        return None
    return (info["w"], info["h"], info.get("small")) if info else None


def missing():
    return [s for s in SLOTS if path(s) is None]
