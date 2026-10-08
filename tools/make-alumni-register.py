#!/usr/bin/env python3
"""Turn an export of the Alumni Registration Form into tools/alumniregister.py.

    python3 tools/make-alumni-register.py path/to/responses.xlsx

The export is the Google Form's response sheet, downloaded as .xlsx. It is
NEVER committed: alongside each alumnus's name it holds their phone number,
email address, date of birth, roll number and gender. Run this on your own
machine, look at what it prints, and commit only tools/alumniregister.py.

WHAT IS PUBLISHED. For each registration, three things and nothing else:
the alumnus's name, the years they were at CIRS, and their course. That is
what the school chose to show, in October 2026 (see ALUMNI-CONTENT.md).
Every other column is read past and never leaves this script. To publish
more, change PUBLISH_FIELDS below and record the decision in
ALUMNI-CONTENT.md — it is a decision about people, not about layout.

WHERE EACH ONE GOES. The institutions are the reviewed list in
tools/alumni-destinations.json, which was itself built from this form; its
keys are the answers as typed, made into slugs. So an answer whose slug is
a key goes there, and ALIASES below carries every spelling that does not —
"Christ University Bangalore" is christ-university. An answer that matches
neither stops the script and is printed, so a new answer cannot quietly
fall off the page: add it to ALIASES and run again.

WHAT IT DOES TO THE ANSWERS.

  Duplicates    Several people registered more than once. One person at one
                institution appears once, from their latest response; the
                same person at two institutions appears at both.
  Names         Typed in capitals or in lower case are set in title case,
                and an initial after a full stop is capitalised; anything
                else is left exactly as written.
  CIRS years    "2010 - 2015", "2010-15" and "2015.0" become "2010–2015",
                "2010–2015" and "2015". A range with a typo in one end keeps
                the end that is a real year: "from 1998", "until 2008".
"""

import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "alumniregister.py")
DESTINATIONS = os.path.join(HERE, "alumni-destinations.json")

# The form's own column headings, so a reordered export still reads right.
COL_TIME = "Timestamp"
COL_NAME = "Full Name:"
COL_YEARS = "Which years did you attend CIRS?"
COL_UNI = "University:"
COL_COURSE = "Course:"
PUBLISH_FIELDS = ("name", "years", "course")

# Anyone who has asked not to be named on the site, as they appear in the
# form (any capitalisation). They are left out entirely, not anonymised.
WITHHELD = set()

# ------------------------------------------------------------------
# Answers whose slug is not a key in alumni-destinations.json, folded to
# lower-case words. None means "read, and deliberately not placed".
# ------------------------------------------------------------------
NOT_PLACED = None
ALIASES = {
    # ---- answers that are not an institution ----
    "": NOT_PLACED,
    "n a": NOT_PLACED,
    "nil": NOT_PLACED,
    "yet to get admission": NOT_PLACED,
    "not yet done my school": NOT_PLACED,
    # "NIT" with no campus: there are thirty-one of them.
    "nit": NOT_PLACED,
    # The one "Oxford" response gives "How to party hard" as its course and
    # 2030 as its graduation year. It is not a registration.
    "oxford": NOT_PLACED,
    # Neither is in the reviewed institution list. Add them there first —
    # with whatever review that list asks for — and then point these at them.
    "gii": NOT_PLACED,
    "rr college of medial": NOT_PLACED,

    # ---- spellings of institutions that are in the list ----
    "indian institute of technology madras": ["iitm"],
    "shri ram college of commerce delhi university": ["srcc"],
    "new york university": ["nyu"],
    "purdue university": ["purdue"],
    "university of warwick": ["warwick"],
    "hong kong university of science and technology": ["hkust"],
    "the hong kong university of science and technology": ["hkust"],
    "christ university bangalore": ["christ-university"],
    "amrita": ["amrita-vishwa-vidyapeetham"],
    "amrita university": ["amrita-vishwa-vidyapeetham"],
    "psg tech": ["psg-college-of-technology"],
    "srm": ["srm-institute-of-science-and-technology"],
    "nitt": ["national-institute-of-technology-tiruchirappalli"],
    "national institute of technology nit tiruchirapalli": ["national-institute-of-technology-tiruchirappalli"],
    "national institute of technology trichy": ["national-institute-of-technology-tiruchirappalli"],
    "m o p vaishnav college": ["m-o-p-vaishnav-college-for-women"],
    "mop vaishnav college": ["m-o-p-vaishnav-college-for-women"],
    "st joseph s college of arts and sciences": ["st-joseph-s-college-of-arts-and-science"],
    "st joseph college of arts and science": ["st-joseph-s-college-of-arts-and-science"],
    "university of wollongong dubai": ["university-of-wollongong-in-dubai"],
    "manipal university of technology": ["manipal-institute-of-technology"],
    "vtu": ["visvesvaraya-technological-university"],
    "symbiosis center for management studies": ["symbiosis-centre-for-management-studies"],
    "symbiosis center of media and communication": ["symbiosis-centre-for-media-and-communication"],
    "symbiosis institute of media and communications": ["symbiosis-institute-of-media-and-communication"],
    "pune university": ["savitribai-phule-pune-university"],
    "university of pune": ["savitribai-phule-pune-university"],
    "nmims university": ["nmims"],
    "mumbai university": ["university-of-mumbai"],
    "st xaviers college kolkata": ["st-xavier-s-college-kolkata"],
    "kirori mal collge": ["kirori-mal-college"],
    "icai": ["institute-of-chartered-accountants-of-india"],
    "jdbi jadavpur university american graduate school in paris":
        ["j-d-birla-institute", "american-graduate-school-in-paris"],
    "royal holloway university of london university of westminster":
        ["royal-holloway-university-of-london", "university-of-westminster"],
    "hotel and tourism management institute": ["htmi-switzerland"],
    "cornell": ["cornell-university"],
    "flame": ["flame-university"],
    "curtin university of technology": ["curtin-university"],
    "james cook university": ["james-cook-university-singapore"],
    # Both registrants gave Singapore as their country, which is how the
    # reviewed list already files these two.
    "university of bradford": ["university-of-bradford-singapore"],
    "university of london": ["university-of-london-singapore"],
    "bits": ["bits-pilani-dubai-campus"],
}


def fold(s):
    """An answer reduced to lower-case words."""
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def slug(s):
    return fold(s).replace(" ", "-")


# ------------------------------------------------------------------
# Reading the export, with nothing but the standard library
# ------------------------------------------------------------------
_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def _col(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_rows(path):
    """The first sheet, as a list of dicts keyed by the header row."""
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", _NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % _NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in rels}
    first = wb.find("m:sheets", _NS)[0]
    t = target[first.get("{%s}id" % _NS["r"])].lstrip("/")
    t = t if t.startswith("xl/") else "xl/" + t
    grid = []
    for row in ET.fromstring(z.read(t)).iter("{%s}row" % _NS["m"]):
        cells = {}
        for c in row.findall("m:c", _NS):
            v, inline = c.find("m:v", _NS), c.find("m:is", _NS)
            if c.get("t") == "s" and v is not None:
                val = shared[int(v.text)]
            elif c.get("t") == "inlineStr" and inline is not None:
                val = "".join(x.text or "" for x in inline.iter("{%s}t" % _NS["m"]))
            else:
                val = v.text if v is not None else ""
            cells[_col(c.get("r"))] = val
        if cells:
            grid.append([cells.get(i, "") for i in range(max(cells) + 1)])
    head = [h.strip() for h in grid[0]]
    return [dict(zip(head, r + [""] * (len(head) - len(r)))) for r in grid[1:]]


# ------------------------------------------------------------------
# Tidying the three published fields
# ------------------------------------------------------------------
def tidy_name(s):
    s = re.sub(r"\s+", " ", s).strip()
    if s and (s == s.upper() or s == s.lower()):
        s = " ".join(w[:1].upper() + w[1:].lower() for w in s.split(" "))
    # An initial typed in lower case after a full stop: "K.p.shrinidhi".
    return re.sub(r"(^|[ .])([a-z])", lambda m: m.group(1) + m.group(2).upper(), s)


def tidy_years(s):
    s = re.sub(r"\s+", "", s).replace("_", "-")
    m = re.fullmatch(r"((?:19|20)\d\d)(?:\.0)?", s)
    if m:
        return m.group(1)
    m = re.fullmatch(r"((?:19|20)\d\d)-(\d{2}|\d{4})", s)
    if m:
        a, b = m.group(1), m.group(2)
        if len(b) == 2:
            b = a[:2] + b
        return a + "–" + b
    # A typo ("1998-201", "2206-2008"): keep whichever end is a real CIRS
    # year and say which end it is, rather than guess at the other.
    ends = s.split("-")
    real = lambda y: re.fullmatch(r"\d{4}", y) and 1996 <= int(y) <= 2035
    if len(ends) == 2 and real(ends[0]):
        return "from " + ends[0]
    if len(ends) == 2 and real(ends[1]):
        return "until " + ends[1]
    return s


def tidy_course(s):
    s = re.sub(r"\s+", " ", s).strip()
    if fold(s) in ("", "n a", "na", "nil", "none"):
        return ""
    return s[:1].upper() + s[1:]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rows = read_rows(sys.argv[1])
    with open(DESTINATIONS, encoding="utf-8") as fh:
        keys = {d["key"] for d in json.load(fh)}

    def targets(answer):
        f = fold(answer)
        if f in ALIASES:
            return ALIASES[f]
        if slug(answer) in keys:
            return [slug(answer)]
        raise KeyError(answer)

    unknown = set()
    for r in rows:
        try:
            targets(r[COL_UNI])
        except KeyError:
            unknown.add(r[COL_UNI].strip())
    if unknown:
        print("Answers that match no institution — add each to ALIASES, then run again:")
        for u in sorted(unknown):
            print("   %r  ->  fold %r, slug %r" % (u, fold(u), slug(u)))
        sys.exit(1)
    missing = sorted({k for v in ALIASES.values() if v for k in v} - keys)
    if missing:
        sys.exit("ALIASES names institutions alumni-destinations.json does not have: %s" % missing)

    # Latest response wins for one person at one institution. The form's
    # timestamps are spreadsheet serial numbers, which sort as numbers.
    def when(r):
        try:
            return float(r[COL_TIME])
        except ValueError:
            return 0.0

    best, not_placed, odd_years, withheld = {}, [], [], 0
    withheld_names = {fold(n) for n in WITHHELD}
    for r in sorted(rows, key=when):
        if fold(r[COL_NAME]) in withheld_names:
            withheld += 1
            continue
        where = targets(r[COL_UNI])
        if not where:
            not_placed.append(r[COL_UNI].strip() or "(blank)")
            continue
        name = tidy_name(r[COL_NAME])
        if not name:
            continue
        years = tidy_years(r[COL_YEARS])
        if not re.fullmatch(r"\d{4}(–\d{4})?", years):
            odd_years.append(years)
        for key in where:
            best[(key, fold(name))] = (key, name, years, tidy_course(r[COL_COURSE]))

    register = sorted(best.values(), key=lambda e: (e[0], fold(e[1])))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write('''"""Alumni registered through the Alumni Registration Form — generated, do not edit.

Written by tools/make-alumni-register.py from an export of the form's
responses, which is not in this repository. Each entry is the only thing the
school publishes from a registration:

    (institution key in alumni-destinations.json, name, years at CIRS, course)

%d entries from %d responses. %d responses named no institution that can be
placed and are left out.
"""

REGISTER = [
%s
]
''' % (len(register), len(rows), len(not_placed),
       "\n".join("    (%r, %r, %r, %r)," % e for e in register)))

    print("tools/alumniregister.py: %d entries from %d responses" % (len(register), len(rows)))
    print("  not placed: %d  %s" % (len(not_placed), sorted(set(not_placed))))
    print("  withheld at their request: %d" % withheld)
    if odd_years:
        print("  CIRS years with a typo, kept partly: %s" % sorted(set(odd_years)))
    print("  institutions with registrations: %d of %d" % (len({e[0] for e in register}), len(keys)))


if __name__ == "__main__":
    main()
