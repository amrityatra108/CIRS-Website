---
name: add-math-challenge
description: Add a month's Math Challenge winners' bulletins (PDFs) to the Math Challenge page and publish them, to Vercel and then cirschool.org. Use when the owner says something like "add the Math Challenge for November 2026", "here are this month's maths winners", or hands over Math Challenge PDFs. Also covers replacing or removing a month's bulletin.
---

# Add a month to the Math Challenge page

The page (`math-challenge.html`) lists the school's monthly winners' bulletins. Each month is
a folder of PDFs, and that is the only thing to change: `tools/mathchallenge.py` reads the
months from the folders, so its code is never edited for a new month.

```
assets/documents/math-challenge/<yyyy-mm>/grades-5-6.pdf
                                         grades-7-8.pdf
                                         grades-9-10.pdf
                                         grades-11-12.pdf
```

A month has only the grade groups the school published. Never make up a missing one, copy
one month's PDF into another, or add a month that has no PDFs.

These are **winners' bulletins, not problem papers**. Call them that when you talk about them.

## What you need from the owner

- **The month.** If they don't say, ask. Don't assume it's the current month: bulletins often
  come out the month after.
- **The PDFs.** These might be attached, in a folder they name, or in Downloads. If you can't
  find them, ask where they are.

## Steps

1. **Start from the latest `main` on a branch of its own:**
   `git switch main && git pull && git switch -c claude/math-challenge-<yyyy-mm>`.
2. **Work out each PDF's grade group.** Go by the file name if it's clear. If not, read the
   first page. If you still can't tell, ask the owner, and never guess. Two files for the
   same group, or a group outside 5–6, 7–8, 9–10 and 11–12: ask.
3. **Copy them in, renamed:** `assets/documents/math-challenge/<yyyy-mm>/grades-<group>.pdf`.
   Copy, don't move: leave the owner's originals where they were. If a file is over about
   3 MB, tell the owner its size. The earlier bulletins are 0.3–2 MB each.
4. **Build and check**, as in CLAUDE.md:

   ```sh
   python tools/build-site.py
   npx --yes html-validate@11 *.html
   python tools/check-links.py
   python tools/build-site.py && git diff --quiet -- '*.html'
   ```

   If the build stops with `mathchallenge: ... is not one of grades-5-6.pdf, ...`, a file in
   the month's folder has the wrong name. Fix the name, never the check.
   `git diff --stat` should show the new PDFs, `math-challenge.html` and nothing else.
5. **Commit** with a message like `Math Challenge: the November 2026 winners' bulletins
   (Grades 5–6, 7–8, 9–10)`.
6. **Ask the owner before merging.** Tell them the month and the grade groups added, plus
   any group that's missing. Then merge on their yes:
   `git switch main && git merge --no-ff <branch> -m "Merge branch '<branch>': Math Challenge has the November 2026 winners"`
   and `git push`. Vercel deploys on push. Hand back
   `https://cirs-website.vercel.app/math-challenge.html#archive-<yyyy-mm>`, and give it a
   minute or two to build before you open it.
7. **Offer to publish to cirschool.org** with the `deploy-cirschool` skill: dry run, the
   owner's yes, then `--go`. The dry run should list `math-challenge.html` and the new PDFs.
   Anything else needs explaining before you go ahead. Afterwards, give the owner
   `https://www.cirschool.org/math-challenge.html` and remind them to press Ctrl+F5.
8. **Delete the branch** once it's merged: `git branch -d <branch>`.

## Replacing or removing a bulletin

To replace a bulletin, overwrite the file with the same name. To remove a grade group, delete
its PDF. To remove a month, delete the whole folder. Then follow steps 4 to 8 the same way.
The page, the counts and the filters follow the files.
