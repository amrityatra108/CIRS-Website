# Deploying the new site to new.cirschool.org (cPanel)

This folder is for putting the new site on the **staging subdomain**. Nothing
here touches `www.cirschool.org`. An `.htaccess` governs only the directory it
sits in and the directories below it, so uploading one into the subdomain's own
document root cannot change how the existing site behaves.

## What the site is

Plain static files. No Node, no PHP, no database, no API, no environment
variables, no server-side code of any kind. Twenty-five menu pages plus the
article and edition pages — 95 HTML files in all — and the assets they
reference. Apache serves it directly.

The only Vercel-specific behaviour is in `vercel.json`, and `.htaccess` in this
folder reproduces all of it: extensionless URLs, no trailing slash, the one
`student-life` redirect, the `noindex` header and the 404 page.

## Build it

On any machine with **Python 3.9 or newer** — no packages to install:

```sh
git clone https://github.com/amrityatra108/CIRS-Website.git
cd CIRS-Website
python3 tools/build-site.py      # writes the 95 pages
python3 tools/stage-deploy.py    # copies only what a page references, into _site/
```

`_site/` is the whole website. It is generated and git-ignored, so it is built,
never committed.

Then make it upload-ready:

```sh
cp deploy/cpanel/.htaccess _site/.htaccess    # the Apache configuration
rm -f _site/_headers                          # Netlify's file; inert on Apache
cd _site && zip -r ../cirs-new-site.zip . -x '.DS_Store'
```

## Upload it

1. **cPanel → Domains** (or *Subdomains*). Find `new.cirschool.org` and read its
   *Document Root*. It is usually `/home/<account>/public_html/new` or
   `/home/<account>/new.cirschool.org`. **Whatever it says, it must not be
   `public_html` itself** — that is the existing website.
2. **File Manager → go to that document root.** It should be empty or hold only
   a default `index.html` / `cgi-bin`. If you see the existing site's files, you
   are in the wrong folder: stop and re-read step 1.
3. **Upload `cirs-new-site.zip`** into that folder, then **Extract** it there.
   One archive rather than 2,200 files over FTP — the upload is about 590 MB and
   file-by-file transfer of that many small files is what usually fails.
4. **Delete the zip** once extracted.
5. Confirm `index.html`, `assets/` and `.htaccess` sit directly in the document
   root — not inside a nested `_site/` folder. (In File Manager, *Settings →
   Show Hidden Files* to see `.htaccess`.)
6. **SSL:** cPanel → *SSL/TLS Status* → tick `new.cirschool.org` → *Run AutoSSL*.
   Let's Encrypt issues a certificate for the subdomain only; the existing
   certificate for `www.cirschool.org` is a separate entry and is not reissued
   or replaced.

## Check it

- Open `https://new.cirschool.org/` — the home page, with the hero video playing.
- Open the browser console (F12 → Console) and reload: it should be empty.
- F12 → Network → reload → sort by Status: no 404s.
- F12 → device toolbar (Ctrl+Shift+M) → iPhone SE: the menu opens, nothing
  scrolls sideways.
- `https://new.cirschool.org/nope` must show the site's own "Page not found"
  page, and the Network tab must show status **404**, not 200.
- `https://new.cirschool.org/student-life` must land on The CIRS Experience.
- `https://new.cirschool.org/robots.txt` must say `Disallow: /`.

## Keep it out of Google

The staging site carries `robots.txt` (`Disallow: /`) and `.htaccess` sends
`X-Robots-Tag: noindex, nofollow`. **Keep both** while the pages still hold
bracketed placeholders. Removing them is part of the real launch, not of this
deployment.

## Later: moving to www.cirschool.org

Nothing about the site changes. What changes is where the files sit:

1. **Back up the existing site first** — cPanel → *Backup* → *Home Directory*,
   or zip `public_html` and download it. This is the step that makes the move
   reversible.
2. Upload the same zip into `public_html` and extract it.
3. Delete `robots.txt` and the `X-Robots-Tag` block from `.htaccess`, so the
   finished site can be indexed.
4. Add a sitemap if one is wanted; the site does not generate one today.
5. The `<link rel="canonical">` on every page already points at
   `https://www.cirschool.org/…`, so nothing has to be rewritten at that point.
