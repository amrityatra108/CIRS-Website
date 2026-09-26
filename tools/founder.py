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
    "portrait": ("archive/p607-portrait.webp",
                 "A warm close portrait of Pujya Gurudev Swami Chinmayananda",
                 "Archival portrait of Pujya Gurudev"),
    "enquiry": ("gurudev-enquiry.jpg",
                "Pujya Gurudev Swami Chinmayananda holding a laboratory flask up to the "
                "light, examining it",
                "Archival photograph of Pujya Gurudev"),
    "vision": ("archive/2353-yr67-community.webp",
               "Swami Chinmayananda welcomed by a community gathered around him", ""),
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


# Supplied with the sets above and kept, but shown nowhere. The page used to
# carry them in an inert <template>, which did nothing but make
# stage-deploy.py upload every one of them. Naming them here keeps them in
# the repository, and out of the deploy, until a slot wants one.
RETAINED = [
    # Earlier Founder treatments and photographs remain available as source
    # media; the current page does not request or deploy them.
    "assets/img/founder/gurudev-hero.jpg",
    "assets/source/founder/amrit-vahini/body-no-wheels.png",
    "assets/source/founder/amrit-vahini/side.png",
    "assets/source/founder/amrit-vahini/wheel-complete.png",
    "assets/img/founder/archive/1277-yr60-mission.webp",
    "assets/img/founder/archive/1352-yr62-teaching.webp",
    "assets/img/founder/archive/1499-yr67-lecture.webp",
    "assets/img/founder/archive/2033-yr65-vhp.webp",
    "assets/img/founder/archive/2451-yr71-audience.webp",
    "assets/img/founder/archive/2633-yr80-writing.webp",
    "assets/img/founder/archive/bsan3-education.webp",
    "assets/img/founder/archive/bsan39-early-years.webp",
    "assets/img/founder/archive/esan93-sannyasa.webp",
    "assets/img/founder/archive/official-chinmaya-context.webp",
    "assets/img/founder/archive/p638-himalaya.webp",
    "assets/img/founder/archive/r664-contemplative.webp",
    # Earlier vehicle views remain in the source collection for future use.
    "assets/source/founder/amrit-vahini/front-three-quarter.png",
    "assets/source/founder/amrit-vahini/overhead-turn.png",
    "assets/source/founder/amrit-vahini/rear-three-quarter.png",
    # Archive variants from the supplied set that no slot uses.
    "assets/source/founder/archive/p46-hero.webp",
    "assets/source/founder/archive/p53-portrait.webp",
    "assets/source/founder/archive/r664-early.webp",
]


def path(slot):
    """The deployable path for a slot, or None when the file is not here."""
    name = SLOTS[slot][0]
    if name is None:
        return None
    rel = os.path.normpath(os.path.join("assets/img/founder", name)).replace(os.sep, "/")
    return rel if os.path.exists(os.path.join(ROOT, rel)) else None


# The media manifest records dimensions and available 800px cuts for the
# archival photographs still used below the new life story.
SIZES = {
    "children": "(max-width: 899px) 92vw, (max-width: 1100px) 68vw, 62vw",
}
UNCUT = {"students"}
IMAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "founder-images.json")


def size(slot):
    """(width, height, smaller cut or None) for a deployed Founder slot."""
    import json
    try:
        with open(IMAGES, encoding="utf-8") as source:
            info = json.load(source).get(SLOTS[slot][0])
    except FileNotFoundError:
        return None
    return (info["w"], info["h"], info.get("small")) if info else None


def missing():
    return [s for s in SLOTS if path(s) is None]
