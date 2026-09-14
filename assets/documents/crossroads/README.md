# Crossroads issue PDFs — generated, do not edit by hand

**A PDF put here directly will be the only copy of itself, and the next
optimisation pass will not know about it.** The issues here are written by

    python3 tools/make-crossroads-pdfs.py

from the originals in `assets/source/crossroads-pdf/`, which is where a new
issue goes. See the README there.

Name each file for its issue number and nothing else needs editing — the
archive page discovers it on the next build and the placeholder becomes a
cover you can open:

    crossroads-issue-01.pdf
    crossroads-issue-02.pdf
    ...
    crossroads-issue-32.pdf

Covers are separate and optional. Put the school's own scan — at whatever
size it came in — at `assets/source/crossroads/issue-07.jpg`, then run

    python3 tools/make-covers.py

which crops it to the card's 5:7 and writes the 720x1008 copy the site ships
to `assets/img/crossroads/issue-07.jpg`. Issue 07 then shows that instead of
its typographic placeholder. Either the PDF or the cover can arrive without
the other.

Do not put a full-size scan straight into `assets/img/` — everything there is
deployed as-is, and the run of covers is 20 MB at print resolution against
3.6 MB generated.

If one file cannot follow the naming, add it to `OVERRIDES` in
`tools/crossroads.py` rather than renaming the convention for everyone.

See tools/crossroads.py for the whole of the logic — there is no database.
