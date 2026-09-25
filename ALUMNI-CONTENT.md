<<<<<<< HEAD
# What the Alumni page still needs from the school

The Alumni page (`alumni.html`, *Where CIRS Takes You*) is built from one file:
**`tools/alumni.py`**. That file is the whole of the page's content — the destinations,
the alumni, the quotations and the pathways. There is no database and no upload form,
exactly as with the Important Documents portal (see `ADMIN-DOCUMENTS.md`): the list in
the repository **is** the admin panel, and the site rebuilds the page from it.

This document is the list of what is missing, in the order it is worth supplying.

---

## The rule this page was built under

**Nothing on the page was invented.** Every name, university, role and quotation on it
was either already published on the previous version of the Alumni page, or supplied by
the school afterwards — Nanyang Technological University came that way, which is the
route every further destination should take. Where something is not
known, the page says so in brackets rather than filling the gap:

> *[Portrait to be supplied by the school, with the alumnus's permission.]*

Those bracketed notes are deliberate and are the site's established convention. They are
not placeholders left by accident — each one marks a specific thing the school has not
yet said, and each one disappears on its own the moment the corresponding field in
`tools/alumni.py` is filled in. **Please do not ask for them to be replaced with
approximate or "representative" content.** A plausible-sounding batch year attached to a
real person's name is worse than a visible gap.

---

## 1. Portraits — the largest gap

There is **not one photograph of an alumnus anywhere in this repository.** Every portrait
frame on the page currently renders as a marked plate with the person's initials and a
line saying a photograph is awaited.

For each of the four named alumni we need:

| | Needed | Notes |
|---|---|---|
| Photograph | One portrait, at least 900 × 1200px | Portrait orientation; head and shoulders is fine |
| Permission | Written consent from the alumnus to publish it | Required before it goes on the site |
| Credit | Photographer, if the school does not own the image | |

A school-era photograph as well as a current one unlocks the **Then / Now** reveal the
page is already built for — the two images cross-fade to show the same person years
apart. Both halves must be genuine photographs of that person. Nothing is reconstructed
or generated.

**Where it goes:** put the file in `assets/img/alumni/` and set `"portrait"` (and
`"then_portrait"`) in that alumnus's entry in `tools/alumni.py`. The plate becomes an
image automatically; nothing else on the page changes.

## 2. Batch years

Not one batch or graduating year is recorded for any alumnus, including the three who
gave the quotations. Every alumnus and every quotation currently shows
*[Batch to be supplied]*.

Needed: the year or batch for **Hari Om Jani, Soham Desai, Divyaj DT, Shashwat Santosh,
Kavya S, Roshan B** and **Mugdha Sultania**.

Set `"batch"` in each entry.

## 3. Which alumnus went to which institution

The page lists nineteen institutions, and separately lists four alumni. **It never joins
the two**, because the join is not recorded anywhere. The destination panel says so:

> *[Which alumni read here, and in which years, to be supplied by the school.]*

Needed: for each alumnus, the institution they read at. Set `"institution"`.

Note that **Oxford University is deliberately not in the destination list.** It is where
Hari Om Jani *works*, which is not the same as where a CIRS student *read*, and the page
does not conflate the two.

## 4. More destinations

Adding one is two values: which of the galaxy's two arms it belongs on, and how far out
along that arm it sits. Regions run in unbroken stretches along an arm — arm 0 carries
India and then the United Kingdom, arm 1 carries Asia-Pacific and then the United States
— so a new destination goes at the end of its own region's stretch and the ones beyond
it shift out. The header comment in `tools/alumni.py` sets out the arithmetic.

## 5. More alumni

The school's own note on the previous page said "and many more". Four named alumni is a
thin showing for a school that has been teaching since 1996.

For each additional alumnus, the minimum that can be published is **a name and one
verified line** about what they do. Batch, institution, city, quotation and portrait all
appear as soon as they are added and are left out silently until then.

Worth prioritising, since the page has a pathway for each and only one or two names
behind most of them:

- Public service, medicine, law
- Business and finance
- Social impact and service
- Entrepreneurship
- Women alumni — three of the seven names on the page are women, and none of the four
  featured chapters is

## 6. Current cities or countries

No alumnus has a location recorded. Set `"place"`. This is what would let the page show
where the alumni community actually is today, as opposed to where its students went to
study.

## 7. The alumni association and how to reach it

The page currently ends by pointing at the school office
(`info@cirschool.org`, +91 422 261 3300), because **that is the only alumni contact route
this site can verify.** It says so in as many words.

Needed, if they exist:

- An alumni association email address or officer
- The alumni register or directory, if one is kept
- **Univariety** — the brief mentioned this. There is no Univariety link anywhere in this
  repository, so none was added. If the school uses it and the link is current, supply it.
- Reunion dates, if any are fixed
- Official alumni social accounts — only official ones

## 8. Quotations

Three quotations exist. They carry a whole chapter of the page between them and they do
it well, but three is not many.

For each new one, we need the **exact words**, the **name of the person who said them**,
and their permission to publish. Add to `VOICES` in `tools/alumni.py`.

---

## What the page does *not* need

- **University logos.** The destination index is text on purpose. Nineteen wordmarks
  would need nineteen licences and would read worse than a list.
- **Numbers of alumni per university, or any total.** None is recorded, and an
  impressive-looking figure nobody can source is exactly what this page avoids.
- **Stock photography of graduations or students.** Every photograph on the page is the
  school's own.

---

## After supplying anything

Edit `tools/alumni.py`, then from the repository root:

```sh
python3 tools/build-site.py
```

and run the checks in `CLAUDE.md` before pushing. The constellation, the region filters,
the searchable index, the counts, the pathway evidence lists and the editorial chapters
all rebuild from that one file.
=======
# Alumni page: source notes and details still needed from CIRS

The restored *Where CIRS Takes You* layout is built from `tools/pages/alumni.html`, `tools/alumni.py`, `assets/css/alumni.css`, and `assets/js/alumni-journey.js`. The original campus opening, destination map, quotations, alternating alumni chapters, pathway scenes, index, and closing scene remain. The scenes scroll in normal document flow.

## Material in use

- Four supplied photographs: Hari Om Jani, Soham Desai, Divyaj DT, and Shashwath Santosh. The Divyaj photo shows him on the right in the red kit. CIRS confirmed in the project conversation on 24 September 2026 that it has each alumnus's publication consent and the image rights, including any required credit arrangements. The underlying permission records remain with CIRS.
- Four short biographies with public source links in `tools/alumni.py`.
- Three alumni quotations and the school's 19 institution destination selection.
- The official alumni database form, school-office email, and telephone.

## Still needed from the school

- Preferred public spelling for **Hari Om Jani** (his Oxford profile uses **Hariom Jani**) and **Divyaj DT** (AIFF uses **Divyaj Dhaval Thakkar**).
- Graduating year or batch for **Hari Om Jani, Soham Desai, Divyaj DT, Shashwath Santosh, Kavya S, Roshan B, and Mugdha Sultania**. None is displayed without confirmation.
- Current alumni association or coordinator details, if an active association exists, plus its approved contact destination.
- Confirmation that the selected destination list is still current. It is presented as a selection, not a complete alumni register.

If a visible photographer credit is required for any supplied photo, CIRS should provide its exact wording.
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
