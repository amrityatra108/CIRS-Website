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
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_DIR = "assets/documents/school-info"

# Order here is the order documents appear within their category, on both
# the portal page and the School Information document list.
DOCUMENTS = [
    # ---- Affiliation &amp; recognition -----------------------------------
    {"id": "cbse-affiliation-letter", "category": "Affiliation &amp; recognition",
     "title": "CBSE Affiliation Letter",
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

    # ---- Safety &amp; compliance certificates -----------------------------
    {"id": "school-safety-policy", "category": "Safety &amp; compliance",
     "title": "CIRS School Safety Policy",
     "note": "The school's own safety policy document.",
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
    {"id": "self-affidavit", "category": "Safety &amp; compliance",
     "title": "Self Affidavit",
     "note": "The school's self-affidavit submitted to the affiliating authority.",
     "file": "self-affidavit.pdf"},

    # ---- Academics &amp; results ------------------------------------------
    {"id": "cbse-results-three-year", "category": "Academics &amp; results",
     "title": "CBSE Results &mdash; Past Three Years",
     "note": "CBSE board examination results for the last three academic years.",
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

    # ---- Faculty --------------------------------------------------------
    {"id": "faculty-details", "category": "Faculty",
     "title": "Faculty &amp; Teacher Details",
     "note": "Details of the school's teaching faculty.",
     "file": "faculty-details.pdf"},

    # ---- School circulars ------------------------------------------------
    {"id": "circular-anand-utsav", "category": "School circulars",
     "title": "Circular &mdash; Anand Utsav",
     "note": "Circular issued for the Anand Utsav celebration.",
     "file": "circular-anand-utsav.pdf"},
    {"id": "circular-khel-mela", "category": "School circulars",
     "title": "Circular &mdash; Khel Mela",
     "note": "Circular issued for the Khel Mela sports event.",
     "file": "circular-khel-mela.pdf"},
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


def is_uploaded(doc):
    return os.path.exists(os.path.join(ROOT, asset_path(doc)))


def by_category():
    """DOCUMENTS grouped into CATEGORY_ORDER, each a list of documents."""
    groups = {c: [] for c in CATEGORY_ORDER}
    for doc in DOCUMENTS:
        groups[doc["category"]].append(doc)
    return [(c, groups[c]) for c in CATEGORY_ORDER if groups[c]]
