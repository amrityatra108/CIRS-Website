"""The document list behind the Important Documents portal.

This is the whole "admin backend" for that portal, by design: the site has no
server and no database, so the manifest below IS the database. An
administrator adds a document by dropping a PDF into assets/documents/school-info/
and adding one entry here; both the portal page and the document-list section
on School Information are generated from this one list, so they can never
drift apart. See ADMIN-DOCUMENTS.md for the full walkthrough.

A document whose file is not yet on disk renders as "Awaiting upload" rather
than a dead link — check-links.py never sees an href to a file that does not
exist. Add the PDF later and rebuild; nothing else about the entry changes.
<<<<<<< HEAD
"""

import os
=======

Each entry also says how current it is, read off the document itself:
"issued", "valid_until" or "period" (as the document states them) and a
"status" — current, permanent, dated, stale, expired or undated. Both pages
print that beside the title, so an expired certificate is never presented as
current. "availability": "on-request" keeps a document off the public site
altogether: it is listed, with a note to ask the school office, and no file
is linked. See ADMIN-DOCUMENTS.md.
"""

import os
from datetime import date, datetime
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_DIR = "assets/documents/school-info"

# Order here is the order documents appear within their category, on both
# the portal page and the School Information document list.
DOCUMENTS = [
    # ---- Affiliation &amp; recognition -----------------------------------
    {"id": "cbse-affiliation-letter", "category": "Affiliation &amp; recognition",
     "title": "CBSE Affiliation Letter",
<<<<<<< HEAD
     "note": "The school's current affiliation letter from the Central Board of Secondary Education.",
     "file": "cbse-affiliation-letter.pdf"},
    {"id": "state-recognition", "category": "Affiliation &amp; recognition",
     "title": "Recognition from State Government",
     "note": "The Government of Tamil Nadu's recognition of the school.",
     "file": "state-government-recognition.pdf"},
    {"id": "state-noc", "category": "Affiliation &amp; recognition",
     "title": "No Objection Certificate from State Government",
     "note": "The State Government's NOC for the school's establishment.",
     "file": "state-noc.pdf"},
    {"id": "ccmt-trust-registration", "category": "Affiliation &amp; recognition",
     "title": "CCMT Trust Registration Certificate",
     "note": "Registration certificate of the Central Chinmaya Mission Trust, the school's managing trust.",
     "file": "ccmt-trust-registration-certificate.pdf"},
    {"id": "affiliation-self-certification", "category": "Affiliation &amp; recognition",
     "title": "Self-Certification for Extension of Affiliation",
     "note": "The school's self-certification submitted for extension of CBSE affiliation.",
     "file": "self-certification-extension-of-affiliation.pdf"},
    {"id": "mandatory-public-disclosure", "category": "Affiliation &amp; recognition",
     "title": "Mandatory Public Disclosure",
     "note": "The CBSE-mandated public disclosure statement.",
     "file": "mandatory-public-disclosure.pdf"},
=======
     "note": "The most recent affiliation letter from the Central Board of Secondary Education on file.",
     "file": "cbse-affiliation-letter.pdf",
     # The letter is dated 3 Oct 2020 and grants extension "01.04.2020 to
     # 31.03.2025".
     "issued": "3 Oct 2020", "period": "2020–2025", "valid_until": "31 Mar 2025",
     "status": "expired"},
    {"id": "state-recognition", "category": "Affiliation &amp; recognition",
     "title": "Recognition from State Government",
     "note": "The Government of Tamil Nadu's recognition of the school.",
     "file": "state-government-recognition.pdf",
     "issued": "July 2026", "valid_until": "8 Sep 2027", "status": "current"},
    {"id": "state-noc", "category": "Affiliation &amp; recognition",
     "title": "No Objection Certificate from State Government",
     "note": "The State Government's NOC for the school's establishment.",
     "file": "state-noc.pdf",
     "issued": "15 Jul 1996", "status": "permanent"},
    {"id": "ccmt-trust-registration", "category": "Affiliation &amp; recognition",
     "title": "CCMT Trust Registration Certificate",
     "note": "Registration certificate of the Central Chinmaya Mission Trust, the school's managing trust.",
     "file": "ccmt-trust-registration-certificate.pdf",
     "issued": "10 Jul 1964", "status": "permanent"},
    {"id": "affiliation-self-certification", "category": "Affiliation &amp; recognition",
     "title": "Self-Certification for Extension of Affiliation",
     "note": "The school's self-certification submitted for extension of CBSE affiliation.",
     "file": "self-certification-extension-of-affiliation.pdf",
     "issued": "28 Mar 2024", "status": "dated"},
    {"id": "mandatory-public-disclosure", "category": "Affiliation &amp; recognition",
     "title": "Mandatory Public Disclosure",
     "note": "The CBSE-mandated public disclosure statement.",
     "file": "mandatory-public-disclosure.pdf",
     "issued": "4 Apr 2024", "status": "stale"},
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

    # ---- Safety &amp; compliance certificates -----------------------------
    {"id": "school-safety-policy", "category": "Safety &amp; compliance",
     "title": "CIRS School Safety Policy",
     "note": "The school's own safety policy document.",
<<<<<<< HEAD
     "file": "school-safety-policy.pdf"},
    {"id": "fire-safety-certificate", "category": "Safety &amp; compliance",
     "title": "Fire Safety Certificate",
     "note": "Certificate confirming the campus's fire safety compliance.",
     "file": "fire-safety-certificate.pdf"},
    {"id": "building-safety-certificate", "category": "Safety &amp; compliance",
     "title": "Building Safety Certificate",
     "note": "Certificate confirming the structural safety of school buildings.",
     "file": "building-safety-certificate.pdf"},
    {"id": "land-certificate", "category": "Safety &amp; compliance",
     "title": "Land Certificate",
     "note": "Certificate confirming the school's title to its campus land.",
     "file": "land-certificate.pdf"},
    {"id": "sanitation-certificate", "category": "Safety &amp; compliance",
     "title": "Water, Health and Sanitation Certificate",
     "note": "Certificate covering the campus's water supply, health and sanitation.",
     "file": "water-health-sanitation-certificate.pdf"},
    {"id": "water-quality-test", "category": "Safety &amp; compliance",
     "title": "Water Quality Test Report",
     "note": "Independent laboratory analysis of the campus drinking water.",
     "file": "water-quality-test-report.pdf"},
    {"id": "self-affidavit", "category": "Safety &amp; compliance",
     "title": "Self Affidavit",
     "note": "The school's self-affidavit submitted to the affiliating authority.",
     "file": "self-affidavit.pdf"},
=======
     "file": "school-safety-policy.pdf",
     "issued": "July 2018 (second edition)", "status": "dated"},
    {"id": "fire-safety-certificate", "category": "Safety &amp; compliance",
     "title": "Fire Safety Certificate",
     "note": "Certificate confirming the campus's fire safety compliance.",
     "file": "fire-safety-certificate.pdf",
     "issued": "18 Aug 2025", "valid_until": "17 Aug 2026", "status": "expired"},
    {"id": "building-safety-certificate", "category": "Safety &amp; compliance",
     "title": "Building Safety Certificate",
     "note": "Certificate confirming the structural safety of school buildings.",
     "file": "building-safety-certificate.pdf",
     "issued": "10 Sep 2024", "valid_until": "8 Sep 2027", "status": "current"},
    {"id": "land-certificate", "category": "Safety &amp; compliance",
     "title": "Land Certificate",
     "note": "Certificate confirming the school's title to its campus land.",
     "file": "land-certificate.pdf",
     "issued": "24 Jan 2020", "status": "dated"},
    {"id": "sanitation-certificate", "category": "Safety &amp; compliance",
     "title": "Water, Health and Sanitation Certificate",
     "note": "Certificate covering the campus's water supply, health and sanitation.",
     "file": "water-health-sanitation-certificate.pdf",
     "issued": "24 Feb 2026", "valid_until": "23 Feb 2027", "status": "current"},
    {"id": "water-quality-test", "category": "Safety &amp; compliance",
     "title": "Water Quality Test Report",
     "note": "Independent laboratory analysis of the campus drinking water.",
     "file": "water-quality-test-report.pdf",
     "issued": "11 Aug 2026", "status": "dated"},
    {"id": "self-affidavit", "category": "Safety &amp; compliance",
     "title": "Self Affidavit",
     "note": "The school's self-affidavit submitted to the affiliating authority.",
     "file": "self-affidavit.pdf",
     "issued": "19 Jan 2019", "status": "stale"},
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

    # ---- Academics &amp; results ------------------------------------------
    {"id": "cbse-results-three-year", "category": "Academics &amp; results",
     "title": "CBSE Results &mdash; Past Three Years",
     "note": "CBSE board examination results for the last three academic years.",
<<<<<<< HEAD
     "file": "cbse-results-past-three-years.pdf"},
    {"id": "transfer-certificates", "category": "Academics &amp; results",
     "title": "Transfer Certificates",
     "note": "The register of transfer certificates issued by the school.",
     "file": "transfer-certificates.pdf"},
    {"id": "textbooks-declaration", "category": "Academics &amp; results",
     "title": "Declaration on Use of Textbooks Published by Private Publishers",
     "note": "The school's declaration on its use of privately published textbooks.",
     "file": "textbooks-declaration.pdf"},
    {"id": "academic-calendar", "category": "Academics &amp; results",
     "title": "Annual Academic Calendar",
     "note": "The school's calendar of academic dates and events for the year.",
     "file": "annual-academic-calendar.pdf"},

    # ---- Administration &amp; governance -----------------------------------
    {"id": "annual-report", "category": "Administration &amp; governance",
     "title": "Annual Report",
     "note": "The school's published annual report.",
     "file": "annual-report.pdf"},
    {"id": "pta-list", "category": "Administration &amp; governance",
     "title": "Parent Teacher Association",
     "note": "The current Parent Teacher Association member list.",
     "file": "pta-list.pdf"},
    {"id": "fee-structure", "category": "Administration &amp; governance",
     "title": "Fee Structure",
     "note": "The school's current fee structure.",
     "file": "fee-structure.pdf"},
=======
     "file": "cbse-results-past-three-years.pdf",
     "period": "2023–24 to 2025–26", "status": "current"},
    {"id": "transfer-certificates", "category": "Academics &amp; results",
     "title": "Transfer Certificates",
     "note": "The register of transfer certificates issued by the school.",
     "file": "transfer-certificates.pdf",
     "period": "2022–23", "status": "dated", "availability": "on-request"},
    {"id": "textbooks-declaration", "category": "Academics &amp; results",
     "title": "Declaration on Use of Textbooks Published by Private Publishers",
     "note": "The school's declaration on its use of privately published textbooks.",
     "file": "textbooks-declaration.pdf",
     "period": "2019–20", "status": "stale"},
    {"id": "academic-calendar", "category": "Academics &amp; results",
     "title": "Annual Academic Calendar",
     "note": "The school's calendar of academic dates and events for the year.",
     "file": "annual-academic-calendar.pdf",
     "period": "2024–25", "status": "stale"},

    # ---- Administration &amp; governance -----------------------------------
    {"id": "school-management-committee", "category": "Administration &amp; governance",
     "title": "School Management Committee",
     "note": "The current School Management Committee, as CBSE's mandatory disclosure requires.",
     "file": "school-management-committee.pdf",
     "status": "undated"},
    {"id": "annual-report", "category": "Administration &amp; governance",
     "title": "Annual Report",
     "note": "The school's published annual report.",
     "file": "annual-report.pdf",
     "issued": "15 Oct 2019", "status": "stale"},
    {"id": "pta-list", "category": "Administration &amp; governance",
     "title": "Parent Teacher Association",
     "note": "The Parent Teacher Association member list.",
     "file": "pta-list.pdf",
     "status": "undated", "availability": "on-request"},
    {"id": "fee-structure", "category": "Administration &amp; governance",
     "title": "Fee Structure",
     "note": "The school's current fee structure.",
     "file": "fee-structure.pdf",
     "period": "2027–29", "status": "current"},
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

    # ---- Faculty --------------------------------------------------------
    {"id": "faculty-details", "category": "Faculty",
     "title": "Faculty &amp; Teacher Details",
     "note": "Details of the school's teaching faculty.",
<<<<<<< HEAD
     "file": "faculty-details.pdf"},
=======
     "file": "faculty-details.pdf",
     "status": "undated", "availability": "on-request"},
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

    # ---- School circulars ------------------------------------------------
    {"id": "circular-anand-utsav", "category": "School circulars",
     "title": "Circular &mdash; Anand Utsav",
     "note": "Circular issued for the Anand Utsav celebration.",
<<<<<<< HEAD
     "file": "circular-anand-utsav.pdf"},
    {"id": "circular-khel-mela", "category": "School circulars",
     "title": "Circular &mdash; Khel Mela",
     "note": "Circular issued for the Khel Mela sports event.",
     "file": "circular-khel-mela.pdf"},
=======
     "file": "circular-anand-utsav.pdf",
     "issued": "22 Aug 2019", "status": "stale"},
    {"id": "circular-khel-mela", "category": "School circulars",
     "title": "Circular &mdash; Khel Mela",
     "note": "Circular issued for the Khel Mela sports event.",
     "file": "circular-khel-mela.pdf",
     "issued": "21 Oct 2019", "status": "stale"},
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
]

# The order categories are grouped in, on both pages.
CATEGORY_ORDER = [
    "Affiliation &amp; recognition",
    "Safety &amp; compliance",
    "Academics &amp; results",
    "Administration &amp; governance",
    "Faculty",
    "School circulars",
]


def asset_path(doc):
    return f"{DOC_DIR}/{doc['file']}"


<<<<<<< HEAD
def is_uploaded(doc):
    return os.path.exists(os.path.join(ROOT, asset_path(doc)))
=======
def is_on_request(doc):
    """A document the school keeps off the public site. Neither page links to
    a file for it, so tools/stage-deploy.py — which copies only what a page
    references — never publishes it. Delete its PDF from DOC_DIR as well:
    an unlinked copy is still a copy in the repository."""
    return doc.get("availability", "public") == "on-request"


def is_uploaded(doc):
    return not is_on_request(doc) and os.path.exists(os.path.join(ROOT, asset_path(doc)))


# What a visitor is told about a document's date. The status is written by
# hand after reading the document. The one thing the build decides for itself
# is expiry: a document marked current whose valid_until has passed is shown
# as expired, so a certificate can never go on being published as current
# just because nobody edited this file. On the day that happens the committed
# pages no longer match a fresh build, and CI's rebuild-and-diff check fails
# until someone reviews the entry — which is the point.
STATUS_TEXT = {
    "current":   "{when}",
    "permanent": "{when} &middot; no expiry",
    "dated":     "{when}",
    "stale":     "{when} &middot; newer edition awaited",
    "expired":   "Expired {valid_until} &middot; renewal awaited",
    "undated":   "Date not supplied",
}


def _lapsed(doc, today):
    return (doc.get("status") == "current" and bool(doc.get("valid_until"))
            and datetime.strptime(doc["valid_until"], "%d %b %Y").date() < today)


def effective_status(doc, today=None):
    """The status a visitor is shown: the manifest's own, unless it says
    current and the validity date has gone by."""
    if _lapsed(doc, today or date.today()):
        return "expired"
    return doc.get("status", "undated")


def when(doc):
    """The one phrase that says when a document is from, or until when it holds."""
    if doc.get("valid_until"):
        return f"Valid until {doc['valid_until']}"
    if doc.get("period"):
        return f"Covers {doc['period']}"
    if doc.get("issued"):
        return f"Issued {doc['issued']}"
    return "Date not supplied"


def status_text(doc, today=None):
    return STATUS_TEXT[effective_status(doc, today)].format(
        when=when(doc), valid_until=doc.get("valid_until", ""))


def check_dates(today):
    """Documents marked current whose validity has passed — shown as expired
    by the build, and named so the manifest can be brought up to date."""
    return [doc["title"] for doc in DOCUMENTS if _lapsed(doc, today)]


def validate():
    """Refuse a manifest the renderers would misread. A misspelt
    "availability" would otherwise fall through to public and link a
    document the school withheld; a misspelt status has no text to show."""
    for doc in DOCUMENTS:
        if doc.get("availability", "public") not in ("public", "on-request"):
            raise ValueError(f'{doc["id"]}: unknown availability {doc["availability"]!r}')
        if doc.get("status", "undated") not in STATUS_TEXT:
            raise ValueError(f'{doc["id"]}: unknown status {doc["status"]!r}')
        if doc.get("valid_until"):
            datetime.strptime(doc["valid_until"], "%d %b %Y")  # raises on a bad date


validate()
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168


def by_category():
    """DOCUMENTS grouped into CATEGORY_ORDER, each a list of documents."""
    groups = {c: [] for c in CATEGORY_ORDER}
    for doc in DOCUMENTS:
        groups[doc["category"]].append(doc)
    return [(c, groups[c]) for c in CATEGORY_ORDER if groups[c]]
