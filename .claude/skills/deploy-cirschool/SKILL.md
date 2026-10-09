---
name: deploy-cirschool
description: Publish merged changes to the school's live site, cirschool.org, over FTPS with tools/deploy-cirschool.py. Use after a change is merged to main and the owner wants it live on cirschool.org, or when the owner says "deploy", "publish", "push live" or "update cirschool.org".
---

# Publish to cirschool.org

cirschool.org is the school's real site, on a shared host reached only by FTP. Vercel
(`cirs-website.vercel.app`) deploys itself on every push to `main`; cirschool.org never
does. This skill is the one way it gets updated. Never upload to it any other way, and
never hand the owner files to drag into FileZilla: a hand upload leaves the server's old
`.br`/`.gz` copies in place, and every browser keeps getting the old page.

**cirschool.org is not a copy of this repository.** Most of it is a separate 5 October
production build whose source is not in the repository (bundled CSS, a loading screen,
a pointer ring, the hall/ and snake/ pages). The owner chose to keep that build and publish
only what changes here from now on. The tool works that way. Do not "fix" it into a full
mirror, and never suggest replacing the whole live site with this repository's build.

## Steps

1. **Only after the change is merged to `main`**, with the checks in CLAUDE.md passing.
   The tool refuses any other branch, and any uncommitted change.
2. **Pull**, so the checkout is the merged `main`: `git checkout main && git pull`.
3. **Dry run**, and show the owner the result in full:

   ```sh
   python tools/deploy-cirschool.py --dry-run
   ```

   Read it before you show it. Point out in plain words:
   - each page marked *replaces the 5 October version*. That page loses the older
     build's loading screen and bundled styles and becomes this repository's page.
   - anything under **"Also used by the pages of the 5 October build"**. Those files
     change pages nobody edited. Name a couple of those pages for the owner to look at
     afterwards.
   - a long list the change does not explain (for example every page, after a partial
     changed). Say why it happened before going ahead.
4. **Ask the owner to confirm.** Publishing changes the public school website, so it
   always needs a clear yes in the conversation. One yes covers one publish.
5. **Publish:**

   ```sh
   python tools/deploy-cirschool.py --go
   ```

   It uploads assets before pages, writes fresh `.br` and `.gz` copies for every text
   file, records what it published on the server, then fetches each published page,
   stylesheet and script from https://cirschool.org as Brotli, gzip and uncompressed.
   It exits non-zero if any of them is not the new file.
6. **Report back**: the commit now live, how many files, and the page addresses on
   `https://www.cirschool.org/` to open. Remind the owner that Ctrl+F5 skips their
   browser's saved copy.

## When it stops

- **"this computer is not set up yet"** or **"no FTP password is saved"**: the owner
  runs, themselves, `python tools/deploy-cirschool.py --setup --from-filezilla` (or
  double-clicks `tools/deploy-cirschool.bat` with `--setup`). It copies the host, user and
  password from FileZilla's saved site into `.env` and the Windows Credential Manager.
  Never ask for the password in chat, never type it, and never write it into a file.
- **"no starting point recorded"**: this has happened only before the first ever publish.
  `--baseline` records the current commit as what the live site already shows, uploading
  nothing else. Run it only when the owner confirms that is true. Never run it to clear
  an error: on a site that already has a starting point, it refuses.
- **Certificate error**: the host's certificate is issued to its shared server name
  (`mis.domain2space.in`), not to ftp.cirschool.org. If the host changes it, the owner
  checks the new name in FileZilla and sets `CIRS_FTP_TLS_HOSTNAME` in `.env`.
- **"the host closed the connection ... logging in again"** while uploading: expected, not
  a fault. The host drops a session after about sixty uploads; the tool logs in again and
  sends the file it cut off from the start, then carries on, and says how many times it
  did at the end. Only if it stops with **"could not send ..."** (five tries on one file)
  has something else gone wrong: run the same command again, which is safe because the
  manifest of what is published is written last. Do not upload anything by hand.
- **One run at a time.** Every run, `--dry-run` included, rebuilds and re-stages the shared
  `_site/` folder, so two runs (two sessions, say) pull files out from under each other:
  an upload then stops with "No such file or directory" under `_site/`. Before starting,
  check nothing else is running the tool, and wait for it if so.
- **"the live site does not match"** after a publish: run the same command again. A file
  that failed mid-upload is published again. If it still fails, report which files and
  encodings are wrong. Do not upload anything by hand.

## Other commands

- `python tools/deploy-cirschool.py --check` compares every page, stylesheet and script
  on the live site with this checkout over HTTPS. No FTP, nothing changes. Expect most of
  the site to differ, because of the 5 October build. It is for diagnosis, not a gate.
- `tools/deploy-cirschool.bat` is the owner's double-click version of step 5 with a
  confirmation prompt.
