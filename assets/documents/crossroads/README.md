# Crossroads issue PDFs go here

Name each file for its issue number and nothing else needs editing — the
archive page discovers it on the next build and the placeholder becomes a
cover you can open:

    crossroads-issue-01.pdf
    crossroads-issue-02.pdf
    ...
    crossroads-issue-32.pdf

Covers are separate and optional: put a scan of the printed cover at
`assets/img/crossroads/issue-07.jpg` and Issue 07 shows that instead of its
typographic placeholder. Either can arrive without the other.

If one file cannot follow the naming, add it to `OVERRIDES` in
`tools/crossroads.py` rather than renaming the convention for everyone.

See tools/crossroads.py for the whole of the logic — there is no database.
