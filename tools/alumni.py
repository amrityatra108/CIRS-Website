#!/usr/bin/env python3
"""Approved records rendered on the CIRS Alumni page.

The destination list was already published by CIRS. The four alumni names and
three quotations also appeared on the school page. Biography updates link to
public sources. Batch years are omitted until confirmed. Photographs were
supplied for the four named alumni; CIRS confirmed publication rights.
"""

from html import escape

REGIONS = [
    ("india", "India"),
    ("uk", "United Kingdom"),
    ("us", "United States"),
    ("apac", "Asia&ndash;Pacific"),
]

# key, institution name, country/location, display region
DESTINATIONS = [
    ("iitm", "IIT Madras", "India", "india"),
    ("srcc", "Shri Ram College of Commerce", "India", "india"),
    ("nid", "National Institute of Design", "India", "india"),
    ("cvv", "Chinmaya Vishwa Vidyapeeth", "India", "india"),
    ("durham", "Durham University", "United Kingdom", "uk"),
    ("manchester", "The University of Manchester", "United Kingdom", "uk"),
    ("warwick", "University of Warwick", "United Kingdom", "uk"),
    ("imperial", "Imperial College London", "United Kingdom", "uk"),
    ("lse", "The London School of Economics and Political Science", "United Kingdom", "uk"),
    ("nus", "National University of Singapore", "Singapore", "apac"),
    ("ntu", "Nanyang Technological University", "Singapore", "apac"),
    ("hkust", "The Hong Kong University of Science and Technology", "Hong Kong", "apac"),
    ("northwestern", "Northwestern University", "United States", "us"),
    ("chicago", "University of Chicago", "United States", "us"),
    ("purdue", "Purdue University", "United States", "us"),
    ("virginia", "University of Virginia", "United States", "us"),
    ("nyu", "New York University", "United States", "us"),
    ("parsons", "The New School — Parsons", "United States", "us"),
    ("boston", "Boston University", "United States", "us"),
]

ALUMNI = [
    {
        "key": "hari-om-jani",
        "photo": "assets/img/alumni/hari-om-jani.png",
        "photo_alt": "Hari Om Jani wearing glasses and a navy jacket against a plain background.",
        "photo_width": 732,
        "photo_height": 732,
        "name": "Hari Om Jani",
        "role": "Materials research, University of Oxford",
        "biography": (
            "He studied Physics at the National University of Singapore for his "
            "bachelor’s degree and PhD, then moved to Oxford in 2022. In 2024, he "
            "established a research group through a Royal Society University Research "
            "Fellowship. He took up a position at The Queen’s College and Oxford’s "
            "Department of Materials in 2026."
        ),
        "sources": [
            ("The Queen’s College profile", "https://www.queens.ox.ac.uk/people/prof-hariom-jani/"),
        ],
    },
    {
        "key": "soham-desai",
        "photo": "assets/img/alumni/soham-desai.png",
        "photo_alt": "Soham Desai standing with his arms folded in a navy sports shirt.",
        "photo_width": 497,
        "photo_height": 618,
        "name": "Soham Desai",
        "role": "Strength and conditioning coach",
        "biography": (
            "He spent five years as strength and conditioning coach for India’s men’s "
            "cricket team. In 2026, he shared that he had joined Lucknow Super Giants "
            "ahead of the IPL season."
        ),
        "sources": [
            ("Indian Express profile", "https://indianexpress.com/article/sports/cricket/strength-and-conditioning-coach-soham-desai-jasprit-bumrah-ind-vs-eng-10134895/"),
            ("Soham Desai’s 2026 update", "https://www.linkedin.com/posts/soham-desai-91799698_ipl2026-strengthandconditioning-activity-7444994473845219328-afGw"),
        ],
    },
    {
        "key": "divyaj-dt",
        "photo": "assets/img/alumni/divyaj-dt.png",
        "photo_alt": "Divyaj DT, on the right in a red football kit, standing with another person.",
        "photo_width": 387,
        "photo_height": 516,
        "name": "Divyaj DT",
        "role": "Goalkeeper in India youth squads",
        "biography": (
            "The All India Football Federation named him among the goalkeepers selected "
            "for India’s 2023 SAFF U19 Championship squad and 2025 AFC U20 Asian Cup "
            "qualifying squad."
        ),
        "sources": [
            ("AIFF: 2023 SAFF U19 squad", "https://www.the-aiff.com/index.php/article/india-squad-for-saff-u-19-championship-announced"),
            ("AIFF: 2025 AFC U20 qualifying squad", "https://www.the-aiff.com/article/india-squad-for-2025-afc-u20-asian-cup-qualifiers-in-laos-announced"),
        ],
    },
    {
        "key": "shashwat-santosh",
        "photo": "assets/img/alumni/shashwath-santosh.png",
        "photo_alt": "Shashwath Santosh seated outdoors and speaking into a microphone.",
        "photo_width": 1194,
        "photo_height": 796,
        "name": "Shashwath Santosh",
        "role": "Designer, Google Creative Lab",
        "biography": (
            "A designer based in New York, he currently works at Google Creative Lab. "
            "His portfolio documents work with Google teams on projects including "
            "Gemini, Project Astra and Project Genie."
        ),
        "sources": [
            ("Shashwath Santosh’s portfolio", "https://shashwathsantosh.com/"),
        ],
    },
]

VOICES = [
    {"key": "kavya-s", "name": "Kavya S", "quote": "CIRS is an <em>emotion.</em>"},
    {"key": "roshan-b", "name": "Roshan B", "quote": "I learned the value of <em>balance</em> in my life over those seven years there."},
    {"key": "mugdha-sultania", "name": "Mugdha Sultania", "quote": "I would literally trade anything to just go back and <em>re-live</em> each and every moment spent there."},
]


def count():
    return len(DESTINATIONS)


def count_word():
    words = {
        1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
        7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
        12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
        16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
        20: "twenty",
    }
    return words.get(count(), str(count()))


def region_count(region):
    return sum(1 for item in DESTINATIONS if item[3] == region)


def country_count():
    return len({item[2] for item in DESTINATIONS})


def destinations_html():
    groups = []
    for region, label in REGIONS:
        rows = []
        for key, name, country, item_region in DESTINATIONS:
            if item_region != region:
                continue
            rows.append(
                '<li class="ajd__row" data-region="%s" data-search="%s">'
                '<span class="ajd__name">%s</span>'
                '<span class="ajd__country">%s</span></li>' % (
                    escape(region, quote=True),
                    escape((name + " " + country).casefold(), quote=True),
                    escape(name), escape(country),
                )
            )
        groups.append(
            '<section class="ajd__group" data-region="%s">'
            '<h3 class="ajd__region"><span class="sc">%s</span>'
            '<span class="ajd__n">%s<span class="sr-only"> destinations</span></span></h3>'
            '<ul class="ajd__rows">%s</ul></section>' % (
                escape(region, quote=True), label, region_count(region), "".join(rows),
            )
        )

    return '''<div class="ajd" data-destinations>
  <div class="ajd__search" hidden>
    <label class="ajd__label" for="ajd-q">Search the destinations</label>
    <input class="ajd__input" id="ajd-q" type="search" autocomplete="off"
           placeholder="University or country" aria-describedby="ajd-count">
    <p class="ajd__count" id="ajd-count" data-destinations-count role="status">%d institutions across %d locations.</p>
  </div>
  <div class="ajd__groups">%s</div>
  <p class="ajd__empty" data-destinations-empty hidden>No destination matches that search.</p>
</div>''' % (count(), country_count(), "".join(groups))


def people_html():
    articles = []
    for person in ALUMNI:
        source_links = " ".join(
            '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' %
            (escape(url, quote=True), escape(label))
            for label, url in person["sources"]
        )
        articles.append(
            '<article class="alumni-story" id="alumnus-%s">'
            '<div class="alumni-story__photo alumni-story__photo--%s">'
            '<img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></div>'
            '<div class="alumni-story__content">'
            '<div class="alumni-story__heading"><h3>%s</h3><p>%s</p></div>'
            '<div class="alumni-story__body"><p>%s</p>'
            '<p class="alumni-story__sources">%s</p></div></div></article>' % (
                escape(person["key"], quote=True), escape(person["key"], quote=True),
                escape(person["photo"], quote=True), escape(person["photo_alt"], quote=True),
                person["photo_width"], person["photo_height"], escape(person["name"]),
                escape(person["role"]), escape(person["biography"]), source_links,
            )
        )
    return "\n".join(articles)


def voices_html():
    return "\n".join(
        '<figure class="alumni-voice" data-voice="%s">'
        '<blockquote><p>%s</p></blockquote><figcaption>%s</figcaption></figure>' %
        (escape(voice["key"], quote=True), voice["quote"], escape(voice["name"]))
        for voice in VOICES
    )


# Kept as no-op builder hooks: build-site.py resolves these placeholders on
# every page, while the refreshed Alumni template no longer uses either block.
def constellation_html():
    return ""


def pathways_html():
    return ""
