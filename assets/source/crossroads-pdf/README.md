# Crossroads issue PDFs go here — the originals

This is the school's own copy of each issue, at whatever size it came in.
**Nothing here is ever deployed.** `tools/stage-deploy.py` copies only what a
page references, and no page references this folder.

What the site serves is derived from these:

    python3 tools/make-crossroads-pdfs.py

which writes a smaller copy of each one to `assets/documents/crossroads/`,
and that is the copy the archive page links to.

Name each file for its issue number and nothing else needs editing — the
archive page discovers it on the next build and the placeholder becomes a
cover you can open:

    crossroads-issue-01.pdf
    crossroads-issue-02.pdf
    ...
    crossroads-issue-32.pdf

## Why they are not served as they are

They are print masters. The 32 issues are 352 MB between them and one of them
is 30 MB on its own, which is what a visitor on a phone downloads to read it.
The images inside are stored at print resolution and print quality; the text
is real text and is left alone, so an issue is still searchable and selectable
after the pass, and still looks like itself.

Run the tool with `--check` to see the evidence: it re-renders every page of
every issue before and after and reports the worst difference it can find,
along with the page count and the number of characters of text.

    python3 tools/make-crossroads-pdfs.py --check

## Do not optimise in place

If you shrink a file here and delete the original, the next person has no way
back — and the settings in the tool are a judgement that may need revisiting
when someone looks at these on a bigger screen. The originals are the record.
