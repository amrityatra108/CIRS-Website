# Managing the Important Documents portal

The Important Documents portal (`important-documents.html`) and the document list on the
School Information page (`school-info.html#doclist`) are both generated from a single list —
`tools/documents.py`. There is no separate upload form and no database: the PDF files
themselves, sitting in the repository, **are** the storage, and the manifest **is** the
admin panel. This matches how every other page on this site is already maintained (see
`CLAUDE.md`) — content lives in files under `tools/`, and a build step turns it into the
published pages.

Both pages regenerate from the same list every time the site is built, so the portal and
the document list on School Information can never drift out of sync with each other.

## 1. Where PDFs are uploaded

`assets/documents/school-info/` — a plain folder in the repository. Each document is one PDF
file in that folder.

To add a file there without installing anything: open the folder on GitHub
(`assets/documents/school-info/` in this repository), use **Add file → Upload files**, drop
the PDF in, and commit directly to the working branch (or open a pull request, if that is
this project's convention at the time).

## 2. How to add a new document

1. Upload the PDF into `assets/documents/school-info/` (step 1 above). Give the file a plain,
   lowercase, hyphenated name — e.g. `fee-structure-2027.pdf`.
2. Open `tools/documents.py` and add one entry to the `DOCUMENTS` list:
   ```python
   {"id": "fee-structure-2027", "category": "Administration & governance",
    "title": "Fee Structure, 2027",
    "note": "The school's current fee structure.",
    "file": "fee-structure-2027.pdf",
    "period": "2027–28", "status": "current"},
   ```
   - `id` — unique, used only to build the document's own link on the page (`#doc-<id>`).
   - `category` — must be one of the names in `CATEGORY_ORDER` near the top of the same file,
     or add a new category name to that list too.
   - `title` / `note` — what appears on the portal and, for `title`, on the document list.
   - `file` — the exact filename from step 1, including case.
   - the date — read it off the document and write it as the document states it:
     `"issued"` (e.g. `"18 Aug 2025"`), `"valid_until"` (e.g. `"17 Aug 2026"`, always
     day, three-letter month, year) or `"period"` (e.g. `"2027–28"`). Use whichever the
     document has; both pages show the most useful one.
   - `status` — what a visitor is told about it:
     - `"current"` — in force now (shows "Valid until …", "Covers …" or "Issued …");
     - `"permanent"` — issued once, no expiry (a registration, the NOC);
     - `"dated"` — a record of its date with no validity to lapse (a test report);
     - `"stale"` — an old edition the school still has to replace (shown with "newer edition awaited");
     - `"expired"` — past its `valid_until` (shown as "Expired … renewal awaited");
     - `"undated"` — the date is not known yet.
     The status is set by hand, with one exception: once a `"current"` document's
     `valid_until` has passed, the build publishes it as expired regardless, and prints a
     **NOTE** naming it. From that day the committed pages no longer match a fresh build,
     so CI's rebuild check fails until you act: upload the renewal and update its dates,
     or change its status to `"expired"`, then rebuild and commit.
   - `availability` — leave it out for a public document. `"on-request"` keeps a document
     off the site: both pages list its title with "Available from the school office on
     request", and no file is linked. Delete its PDF from the folder as well.
3. Rebuild and commit the regenerated pages (step 5 below).

## 3. How to replace/update an existing PDF

- **Same content, keep the name** (e.g. this year's fee card replaces last year's, same
  filename): upload the new file over the old one in `assets/documents/school-info/`. Nothing
  in `tools/documents.py` needs to change.
- **New filename** (e.g. `fee-structure-2027.pdf` → `fee-structure-2028.pdf`): upload the new
  file, update that document's `"file"` value in `tools/documents.py` to match, and delete the
  old file from the folder.
- To change only the title or description a document shows, edit `"title"` / `"note"` in
  `tools/documents.py` — no change to the PDF itself is needed.

## 4. How to remove a PDF

- **Keep it listed, but off the public site** (for example, a document with personal
  details in it): set `"availability": "on-request"` on its entry and delete the PDF from
  `assets/documents/school-info/`. Deleting it does not remove it from the repository's
  history or from anyone who has already downloaded it.

- **Remove it from the portal but keep the entry as "coming later"**: delete the file from
  `assets/documents/school-info/` and leave its entry in `tools/documents.py` as is. It will
  show as "Awaiting upload" instead of disappearing.
- **Remove it entirely**: delete both the file from `assets/documents/school-info/` and its
  entry from the `DOCUMENTS` list in `tools/documents.py`.

## 5. How a document appears in the portal, and on the document list — automatically

Both pages are generated by `tools/build-site.py`, which reads `tools/documents.py` and:

- lists every document in `DOCUMENTS`, grouped by `category`, on **both** pages;
- on both, prints the document's date and status under its title;
- on both, gives each one **View** and **Download** if its `file` exists in
  `assets/documents/school-info/`, an **Awaiting upload** notice if it does not yet, or the
  school office's address if it is `"on-request"`.

On School Information the list is the **document register** (`school-info.html#documents`):
searchable by title, filterable by category, and each row wears one label worked out from the
entry — *Valid*, *Current*, *Permanent*, *On file*, *Newer edition awaited* (`stale`),
*Expired*, *Awaiting upload* or *Available from the school on request*. The **records update
notice** at the foot of that page lists every expired, stale, missing and on-request document by
name, counted from the same list, so it too needs nothing by hand.

The page opens on four of these PDFs shown as sheets of paper — the State Government
recognition, the State NOC, the CBSE affiliation letter and the land certificate. Their labels
come from `tools/documents.py` like everything else, but the pictures are cut from the PDFs by
`tools/make-record-previews.py`. **If you replace one of those four PDFs, re-run that script**
(it needs `pip install pymupdf`) and commit the images it rewrites in `assets/img/records/`.

Nothing needs to be added to either page's HTML by hand — editing `tools/documents.py` (and the
PDF folder) is the whole job. After any change, rebuild so the published pages catch up:

```sh
python3 tools/build-site.py
```

Then commit **both** the change to `tools/documents.py` (and the PDF) **and** the regenerated
`school-info.html` / `important-documents.html` at the repository root, and push. CI checks
that the committed pages match a fresh build (`tools/check-links.py` and the rebuild-and-diff
step in `CLAUDE.md`) — a push that adds a document without rebuilding will fail that check.
