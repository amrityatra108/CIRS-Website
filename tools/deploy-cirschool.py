#!/usr/bin/env python3
"""Publish the site to cirschool.org, the school's own host, over FTPS.

Vercel deploys itself on every push to main. cirschool.org does not: it is a
shared host reached only by FTP, and until now it was updated by hand in
FileZilla. That went wrong in a way that is invisible from the uploading end.
The host keeps ready-compressed copies beside each page and stylesheet
(admissions.html.br, admissions.html.gz) and hands those to any browser that
can read them, which is every browser. Upload a new admissions.html and leave
the old .br and .gz in place, and the server goes on serving the old page to
everyone while a plain fetch shows the new one. So this script never uploads
a text file without also writing its compressed copies fresh.

    python3 tools/deploy-cirschool.py            # build, compare, ask, publish
    python3 tools/deploy-cirschool.py --dry-run  # only list what would change
    python3 tools/deploy-cirschool.py --go       # publish without asking
    python3 tools/deploy-cirschool.py --setup    # once per computer: credentials
    python3 tools/deploy-cirschool.py --baseline # once: record the starting point
    python3 tools/deploy-cirschool.py --check    # compare the live site, no FTP

cirschool.org is not a copy of this repository. On 5 October 2026 it was
published from a separate production build (bundled and minified styles,
resized photographs, a loading screen, a pointer ring, the hall/ and snake/
pages) whose source is not here. The owner chose to keep that build and
publish only what changes in this repository from now on. So this script
never compares the whole site: it compares this commit's build with the
build of the commit it last published, and uploads the difference.

What a run does:

1. Refuses unless the checkout is `main` with nothing uncommitted, so what
   goes live is always a commit someone can point to.
2. Runs tools/build-site.py and tools/stage-deploy.py, so _site/ is current.
3. Reads .deploy-manifest.json from the server: the hash of every file in the
   build of the commit last published (or of the starting point --baseline
   recorded), plus which files the 5 October build already had. Any file whose
   hash differs, or that is new, is to be published. A file this script once
   uploaded and someone has since changed by hand on the server is too.
4. Lists them: pages (marking any that replace a 5 October page), other files,
   and, separately, files the 5 October pages also load, because changing
   those changes those pages too. Then asks, unless --go or --dry-run.
5. Uploads assets before pages, so no new page goes live pointing at a file
   that is not there yet. Each text file goes up with fresh .br and .gz copies
   wherever the server's convention calls for them.
6. Writes the manifest, then fetches every published page, stylesheet and
   script back from https://cirschool.org as Brotli, as gzip and uncompressed,
   and fails loudly if any of the three is not the file just published.

It never deletes anything on the server. A file that has left the site is
listed so someone can decide; the old site's folders that this repository
does not build are never touched.

`robots.txt` and `_headers` are not published. stage-deploy.py writes them to
keep the Vercel review copy out of search results; cirschool.org is the
school's real site and keeps its own robots.txt, which allows indexing.

Credentials stay off GitHub: the FTP host and user live in .env (git-ignored)
and the password in the Windows Credential Manager (or the macOS Keychain),
both written by --setup. Needs `pip install brotli keyring`;
tools/deploy-cirschool.bat installs them and runs this.
"""

import argparse
import base64
import ftplib
import getpass
import gzip
import hashlib
import http.client
import io
import json
import os
import posixpath
import ssl
import subprocess
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "_site")
ENV_FILE = os.path.join(ROOT, ".env")
MANIFEST = ".deploy-manifest.json"
KEYRING_SERVICE = "cirschool.org FTP"

# Written by stage-deploy.py for the review preview only. See the docstring.
NOT_PUBLISHED = {"_headers", "robots.txt"}
# Files a browser may receive compressed. Only these ever get .br/.gz copies.
TEXT = {".html", ".htm", ".css", ".js", ".mjs", ".json", ".svg", ".txt",
        ".xml", ".map", ".md", ".webmanifest"}
ENCODINGS = (("br", ".br"), ("gzip", ".gz"))

DEFAULTS = {
    "CIRS_FTP_HOST": "ftp.cirschool.org",
    "CIRS_FTP_PORT": "21",
    "CIRS_FTP_ROOT": "/",
    # The host's certificate is issued to the shared server, not to
    # ftp.cirschool.org, so it is checked against the server's own name.
    "CIRS_FTP_TLS_HOSTNAME": "mis.domain2space.in",
    "CIRS_SITE_URL": "https://cirschool.org",
}

try:
    import brotli
except ImportError:
    brotli = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")


def say(msg=""):
    print(msg, flush=True)


def fail(msg):
    raise SystemExit(f"\ndeploy-cirschool: {msg}")


# ---------------------------------------------------------------- settings --

def load_env():
    values = {}
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    settings = dict(DEFAULTS)
    settings.update(values)
    for key in list(DEFAULTS) + ["CIRS_FTP_USER", "CIRS_FTP_PASSWORD", "CIRS_FTP_CAFILE"]:
        if os.environ.get(key):
            settings[key] = os.environ[key]
    return settings


def write_env(updates):
    lines = open(ENV_FILE, encoding="utf-8").read().splitlines() if os.path.exists(ENV_FILE) else []
    done = set()
    for i, line in enumerate(lines):
        key = line.split("=", 1)[0].strip()
        if key in updates:
            lines[i] = f"{key}={updates[key]}"
            done.add(key)
    if not any(l.startswith("# cirschool.org deploy") for l in lines):
        lines.append("# cirschool.org deploy (tools/deploy-cirschool.py). The password is not kept here.")
    lines += [f"{k}={v}" for k, v in updates.items() if k not in done]
    open(ENV_FILE, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def keyring_module():
    try:
        import keyring
        return keyring
    except ImportError:
        return None


def password_for(settings, interactive):
    if settings.get("CIRS_FTP_PASSWORD"):
        return settings["CIRS_FTP_PASSWORD"]
    kr = keyring_module()
    if kr:
        try:
            stored = kr.get_password(KEYRING_SERVICE, settings["CIRS_FTP_USER"])
        except Exception:
            stored = None
        if stored:
            return stored
    if interactive:
        return getpass.getpass(f"FTP password for {settings['CIRS_FTP_USER']}: ")
    fail("no FTP password is saved on this computer. Run once, yourself:\n"
         "    python tools/deploy-cirschool.py --setup")


def filezilla_sites():
    """Sites saved in FileZilla's Site Manager, for --setup --from-filezilla."""
    base = os.environ.get("APPDATA") or os.path.expanduser("~/.config")
    path = os.path.join(base, "FileZilla", "sitemanager.xml")
    if not os.path.exists(path):
        return []
    sites = []
    for server in ET.parse(path).getroot().iter("Server"):
        entry = {tag: (server.findtext(tag) or "") for tag in ("Host", "Port", "User", "Name")}
        node = server.find("Pass")
        entry["Pass"] = None
        if node is not None and node.text and node.get("encoding") == "base64":
            entry["Pass"] = base64.b64decode(node.text).decode("utf-8")
        sites.append(entry)
    return sites


def setup(args):
    settings = load_env()
    kr = keyring_module()
    if not kr:
        fail("the 'keyring' package is missing. Run:  python -m pip install keyring brotli")
    host, user, password = settings["CIRS_FTP_HOST"], settings.get("CIRS_FTP_USER", ""), None
    if args.from_filezilla:
        matches = [s for s in filezilla_sites() if s["Host"].lower() == host.lower()]
        if not matches:
            fail(f"FileZilla's Site Manager has no saved site for {host}.")
        site = matches[0]
        user, password = site["User"], site["Pass"]
        say(f"Using FileZilla's saved site '{site['Name']}' ({user}@{host}).")
        if not password:
            say("FileZilla keeps that password locked behind its master password.")
    if not user:
        user = input(f"FTP user for {host}: ").strip()
    if not password:
        password = getpass.getpass(f"FTP password for {user}: ")
    write_env({"CIRS_FTP_HOST": host, "CIRS_FTP_USER": user,
               "CIRS_FTP_TLS_HOSTNAME": settings["CIRS_FTP_TLS_HOSTNAME"]})
    kr.set_password(KEYRING_SERVICE, user, password)
    settings = load_env()
    say("Saved. Testing the connection...")
    ftp = connect(settings, password)
    say(f"Connected to {host} as {user}. Setup is done.")
    ftp.quit()


# ------------------------------------------------------------------ FTPS ----

class FTPS(ftplib.FTP_TLS):
    """FTP over explicit TLS that checks the certificate against a chosen
    name, and resumes the control connection's TLS session on every data
    connection, which many shared hosts insist on."""

    tls_hostname = None

    def auth(self):
        real, self.host = self.host, self.tls_hostname or self.host
        try:
            return super().auth()
        finally:
            self.host = real

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn, server_hostname=self.tls_hostname or self.host,
                session=self.sock.session)
        return conn, size


def connect(settings, password):
    context = ssl.create_default_context(cafile=settings.get("CIRS_FTP_CAFILE") or None)
    ftp = FTPS(context=context, timeout=90)
    ftp.tls_hostname = settings["CIRS_FTP_TLS_HOSTNAME"]
    ftp.encoding = "utf-8"
    try:
        ftp.connect(settings["CIRS_FTP_HOST"], int(settings["CIRS_FTP_PORT"]))
        ftp.login(settings["CIRS_FTP_USER"], password)
        ftp.prot_p()
    except ssl.SSLCertVerificationError as error:
        fail(f"the server's security certificate did not check out ({error.verify_message}).\n"
             f"It is checked against the name {ftp.tls_hostname!r} (CIRS_FTP_TLS_HOSTNAME in .env).\n"
             "If the host has changed its certificate, open the site in FileZilla, note the\n"
             "'Common name' it shows, and put that in .env.")
    except ftplib.error_perm as error:
        fail(f"the server refused the login: {error}")
    except (OSError, EOFError) as error:
        fail(f"could not reach {settings['CIRS_FTP_HOST']}: {error}")
    ftp.set_pasv(True)
    return ftp


def remote_path(settings, rel):
    return posixpath.join(settings["CIRS_FTP_ROOT"], rel)


def remote_listing(ftp, settings, local):
    """Sizes of every file on the server under the directories this site
    uses. The old site's other folders are never walked."""
    wanted_dirs = {rel.split("/")[0] for rel in local if "/" in rel}
    sizes, stack = {}, [""]
    while stack:
        rel = stack.pop()
        try:
            entries = list(ftp.mlsd(remote_path(settings, rel) if rel else settings["CIRS_FTP_ROOT"],
                                    facts=["type", "size"]))
        except ftplib.error_perm as error:
            if str(error).startswith("550"):
                continue
            if str(error).startswith("500"):
                fail("the server does not support MLSD listings, which this script relies on.")
            raise
        for name, facts in entries:
            if name in (".", ".."):
                continue
            child = f"{rel}/{name}" if rel else name
            kind = facts.get("type", "")
            if kind == "dir" and (rel or name in wanted_dirs):
                stack.append(child)
            elif kind == "file":
                sizes[child] = int(facts.get("size", -1))
    return sizes


def read_remote(ftp, settings, rel):
    buf = io.BytesIO()
    try:
        ftp.retrbinary("RETR " + remote_path(settings, rel), buf.write)
    except ftplib.error_perm:
        return None
    return buf.getvalue()


class Uploader:
    def __init__(self, ftp, settings):
        self.ftp, self.settings, self.made = ftp, settings, set()

    def ensure_dir(self, rel_dir):
        parts = [p for p in rel_dir.split("/") if p]
        for i in range(1, len(parts) + 1):
            sub = "/".join(parts[:i])
            if sub in self.made:
                continue
            try:
                self.ftp.mkd(remote_path(self.settings, sub))
            except ftplib.error_perm:
                pass  # already there
            self.made.add(sub)

    def put(self, rel, data):
        self.ensure_dir(posixpath.dirname(rel))
        target = remote_path(self.settings, rel)
        for attempt in range(3):
            try:
                self.ftp.storbinary("STOR " + target, io.BytesIO(data), blocksize=65536)
                return
            except (ftplib.error_temp, OSError):
                if attempt == 2:
                    raise
                time.sleep(2 + attempt * 3)


# ------------------------------------------------------------------ HTTP ----

class Web:
    """Fetch pages from the live site the way browsers do. Keeps one
    connection open; honours HTTPS_PROXY when a network needs one."""

    def __init__(self, base_url):
        u = urllib.parse.urlsplit(base_url)
        self.host, self.base = u.hostname, u.path.rstrip("/")
        self.proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        self.ctx = ssl.create_default_context()
        if self.proxy and os.environ.get("SSL_CERT_FILE"):
            self.ctx = ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])
        self.conn = None

    def _open(self):
        if self.proxy:
            # CONNECT through the proxy in the clear, then TLS to the site.
            p = urllib.parse.urlsplit(self.proxy)
            conn = http.client.HTTPSConnection(p.hostname, p.port or 80, timeout=60, context=self.ctx)
            headers = {}
            if p.username:
                token = base64.b64encode(f"{urllib.parse.unquote(p.username)}:"
                                         f"{urllib.parse.unquote(p.password or '')}".encode()).decode()
                headers["Proxy-Authorization"] = "Basic " + token
            conn.set_tunnel(self.host, 443, headers=headers)
            return conn
        return http.client.HTTPSConnection(self.host, 443, timeout=60, context=self.ctx)

    def get(self, rel, accept):
        path = self.base + "/" + urllib.parse.quote(rel)
        headers = {"Accept-Encoding": accept, "Cache-Control": "no-cache",
                   "User-Agent": "cirs-deploy-check/1 (like Chrome)"}
        for attempt in range(3):
            try:
                if self.conn is None:
                    self.conn = self._open()
                self.conn.request("GET", path, headers=headers)
                r = self.conn.getresponse()
                body = r.read()
                enc = (r.getheader("Content-Encoding") or "").lower()
                if r.getheader("Connection", "").lower() == "close":
                    self.conn.close()
                    self.conn = None
                if enc == "br":
                    if brotli is None:
                        fail("the 'brotli' package is missing. Run:  python -m pip install brotli keyring")
                    body = brotli.decompress(body)
                elif enc in ("gzip", "x-gzip"):
                    body = gzip.decompress(body)
                return r.status, body
            except (http.client.HTTPException, OSError):
                if self.conn:
                    self.conn.close()
                self.conn = None
                if attempt == 2:
                    raise
                time.sleep(1 + attempt)


def text_sha(data):
    """A text file's hash with Windows line endings folded, so a checkout
    made on Windows and one made elsewhere compare as the same file."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def http_mismatches(web, rel, local_sha):
    """Every encoding in which the live site does not serve `rel` as this
    checkout has it. `local_sha` is text_sha() of the local file."""
    wrong = []
    for label, accept in (("Brotli", "br"), ("gzip", "gzip"), ("uncompressed", "identity")):
        status, body = web.get(rel, accept)
        if status != 200:
            wrong.append(f"{label}: HTTP {status}")
        elif text_sha(body) != local_sha:
            wrong.append(f"{label}: an older copy")
    return wrong


# ------------------------------------------------------------------ local ---

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def require_clean_main(allow_dirty):
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    dirty = git("status", "--porcelain", "--untracked-files=no")
    if allow_dirty:
        return
    if branch != "main":
        fail(f"this checkout is on '{branch}'. Only main is published: merge first, then run this.")
    if dirty:
        fail("there are uncommitted changes. Commit or discard them first, so the live site\n"
             "is always a commit that can be pointed to.\n" + dirty)


def build():
    for script in ("build-site.py", "stage-deploy.py"):
        say(f"  running tools/{script}")
        result = subprocess.run([sys.executable, os.path.join(ROOT, "tools", script)], cwd=ROOT)
        if result.returncode:
            fail(f"tools/{script} failed; nothing was published.")


def local_files():
    files = {}
    for directory, _, names in os.walk(SITE):
        for name in names:
            full = os.path.join(directory, name)
            rel = os.path.relpath(full, SITE).replace(os.sep, "/")
            if rel in NOT_PUBLISHED:
                continue
            data = open(full, "rb").read()
            # Text files are hashed with line endings folded, so a checkout on
            # Windows and one elsewhere agree on what has changed.
            sha = text_sha(data) if is_text(rel) else hashlib.sha256(data).hexdigest()
            files[rel] = {"sha256": sha, "size": len(data), "text_sha": sha if is_text(rel) else None}
    return files


def is_text(rel):
    return os.path.splitext(rel)[1].lower() in TEXT


def sibling_plan(rel, remote, conventions):
    """Which compressed copies `rel` must go up with: any the server already
    has for it, and any its kind of file carries elsewhere on the server."""
    if not is_text(rel):
        return []
    ext = os.path.splitext(rel)[1].lower()
    return [suffix for _, suffix in ENCODINGS
            if rel + suffix in remote or ext in conventions[suffix]]


# ------------------------------------------------------------------- run ----

def human(n):
    for unit in ("bytes", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "bytes" else f"{n:.1f} {unit}"
        n /= 1024


def check_live(args):
    """--check: compare pages, styles and scripts with the live site, no FTP."""
    settings = load_env()
    if not args.no_build:
        build()
    local = local_files()
    web = Web(settings["CIRS_SITE_URL"])
    texts = sorted(r for r in local if is_text(r))
    say(f"Comparing {len(texts)} pages, styles and scripts with {settings['CIRS_SITE_URL']} ...")
    stale = {}
    for i, rel in enumerate(texts, 1):
        wrong = http_mismatches(web, rel, local[rel]["text_sha"])
        if wrong:
            stale[rel] = wrong
        if i % 50 == 0:
            say(f"  {i}/{len(texts)}")
    if not stale:
        say("Every page, stylesheet and script on the live site matches this checkout.")
        return
    say(f"\n{len(stale)} differ from this checkout:")
    for rel, wrong in stale.items():
        say(f"  {rel}  ({'; '.join(wrong)})")
    sys.exit(1)


def connect_and_list(settings, local, interactive):
    password = password_for(settings, interactive)
    ftp = connect(settings, password)
    remote = remote_listing(ftp, settings, local)
    raw = read_remote(ftp, settings, MANIFEST)
    return ftp, remote, (json.loads(raw) if raw else None)


def start_here(settings, local, commit, interactive):
    """--baseline: record this commit as what cirschool.org already shows,
    and the older build's files as shared, without uploading anything."""
    ftp, remote, manifest = connect_and_list(settings, local, interactive)
    if manifest:
        ftp.quit()
        fail(f"a starting point is already recorded (commit {manifest.get('commit')}). "
             "Nothing changed.")
    older = sorted(r for r in remote
                   if not r.endswith((".br", ".gz")) and not r.endswith(".html")
                   and r != MANIFEST)
    record = {"schema": 2, "commit": commit, "baseline": commit,
              "published": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
              "note": "Written by tools/deploy-cirschool.py. Do not edit.",
              "files": {r: {"sha256": i["sha256"], "size": i["size"], "uploaded": False}
                        for r, i in local.items()},
              "older_build": older}
    Uploader(ftp, settings).put(MANIFEST, json.dumps(record, indent=1, sort_keys=True).encode())
    ftp.quit()
    say(f"Starting point recorded: commit {commit}. Nothing else was uploaded.\n"
        f"From now on a deploy publishes only what changes after this commit.\n"
        f"{len(older)} file(s) of the older build are marked as shared; a deploy that would\n"
        "replace one of them says so before it does.")


def deploy(args):
    settings = load_env()
    if not settings.get("CIRS_FTP_USER"):
        fail("this computer is not set up yet. Run once, yourself:\n"
             "    python tools/deploy-cirschool.py --setup --from-filezilla")
    if brotli is None:
        fail("the 'brotli' package is missing. Run:  python -m pip install brotli keyring")
    interactive = sys.stdin.isatty()

    say("1/5  Checking the checkout")
    require_clean_main(args.allow_dirty)
    commit = git("rev-parse", "--short", "HEAD") or "unknown"

    say("2/5  Building the site")
    if not args.no_build:
        build()
    local = local_files()

    if args.baseline:
        start_here(settings, local, commit, interactive)
        return

    say(f"3/5  Comparing with what was last published to {settings['CIRS_FTP_HOST']}")
    ftp, remote, manifest = connect_and_list(settings, local, interactive)
    if not manifest:
        ftp.quit()
        fail("cirschool.org has no starting point recorded, so there is nothing to compare\n"
             "against. If the live site already shows this commit, record it once:\n"
             "    python tools/deploy-cirschool.py --baseline")
    published = manifest.get("files", {})
    older = set(manifest.get("older_build", []))
    conventions = {suffix: {os.path.splitext(r[:-len(suffix)])[1].lower()
                            for r in remote if r.endswith(suffix)}
                   for _, suffix in ENCODINGS}

    changes = {}
    for rel, info in sorted(local.items()):
        before = published.get(rel)
        on_server = remote.get(rel)
        if before is None:
            changes[rel] = "new"
        elif before["sha256"] != info["sha256"]:
            changes[rel] = "changed"
        elif before.get("uploaded"):
            missing = [s for s in sibling_plan(rel, remote, conventions) if rel + s not in remote]
            if on_server is not None and on_server != info["size"]:
                changes[rel] = "edited on the server by hand since"
            elif on_server is None:
                changes[rel] = "missing from the server"
            elif missing:
                changes[rel] = "compressed copy missing"
    gone = sorted(r for r in published if r not in local)

    say(f"     last published: commit {manifest.get('commit', '?')} on {manifest.get('published', '?')}")
    log = git("log", "--oneline", f"{manifest.get('commit')}..HEAD") if manifest.get("commit") else ""
    if log:
        say("     commits since then:\n       " + log.replace("\n", "\n       "))
    say(f"     this checkout: commit {commit}")

    if not changes:
        say("\nNothing has changed since the last publish.")
        ftp.quit()
        return

    order = sorted(changes, key=lambda r: (r.endswith(".html"), r))
    pages = [r for r in order if r.endswith(".html")]
    shared = [r for r in order if r in older and not r.endswith(".html")]
    files = [r for r in order if r not in pages and r not in shared]
    replaced = [r for r in pages if r in remote and not published.get(r, {}).get("uploaded")]
    total = sum(local[r]["size"] for r in order)

    say(f"\n{len(order)} file(s) to publish, {human(total)} before compression.")
    if pages:
        say(f"\nPages ({len(pages)}):")
        for rel in pages:
            note = "; replaces the 5 October version" if rel in replaced else ""
            say(f"  {rel}  ({changes[rel]}{note})")
    if files:
        say(f"\nOther files ({len(files)}):")
        for rel in files[:200]:
            say(f"  {rel}  ({changes[rel]})")
        if len(files) > 200:
            say(f"  ... and {len(files) - 200} more")
    if shared:
        say(f"\n!! Also used by the pages of the 5 October build ({len(shared)}). Publishing\n"
            "   these changes those pages too, so look at a few of them afterwards:")
        for rel in shared:
            say(f"  {rel}  ({changes[rel]})")
    if gone:
        say(f"\nNo longer part of the site, left on the server untouched ({len(gone)}):")
        for rel in gone[:50]:
            say(f"  {rel}")

    if args.dry_run:
        say("\nDry run: nothing was uploaded.")
        ftp.quit()
        return
    if not args.go:
        if not interactive:
            fail("not confirmed. Run again with --go to publish.")
        if input("\nPublish these to cirschool.org now? [y/N] ").strip().lower() not in ("y", "yes"):
            say("Nothing was uploaded.")
            ftp.quit()
            return

    say("\n4/5  Uploading")
    up = Uploader(ftp, settings)
    for i, rel in enumerate(order, 1):
        data = open(os.path.join(SITE, *rel.split("/")), "rb").read()
        up.put(rel, data)
        for suffix in sibling_plan(rel, remote, conventions):
            packed = brotli.compress(data, quality=11) if suffix == ".br" else \
                gzip.compress(data, compresslevel=9, mtime=0)
            up.put(rel + suffix, packed)
        say(f"  [{i}/{len(order)}] {rel}")

    record = dict(manifest)
    record.update({
        "schema": 2, "commit": commit,
        "published": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "files": {r: {"sha256": i["sha256"], "size": i["size"],
                      "uploaded": r in changes or published.get(r, {}).get("uploaded", False)}
                  for r, i in local.items()},
    })
    up.put(MANIFEST, json.dumps(record, indent=1, sort_keys=True).encode("utf-8"))
    ftp.quit()

    say(f"\n5/5  Checking {settings['CIRS_SITE_URL']}")
    web = Web(settings["CIRS_SITE_URL"])
    problems = []
    for rel in order:
        if is_text(rel):
            wrong = http_mismatches(web, rel, local[rel]["text_sha"])
            if wrong:
                problems.append(f"{rel}: {'; '.join(wrong)}")
    if problems:
        say("These are not yet what was published:")
        for p in problems:
            say(f"  {p}")
        fail("published, but the live site does not match everywhere (see above).")
    say(f"Done. cirschool.org now has commit {commit}: {len(order)} file(s) published, "
        "and every page, stylesheet and script among them checked in all three encodings.")


def main():
    parser = argparse.ArgumentParser(description="Publish _site/ to cirschool.org over FTPS.")
    parser.add_argument("--setup", action="store_true", help="save FTP credentials on this computer")
    parser.add_argument("--from-filezilla", action="store_true", help="with --setup: take them from FileZilla")
    parser.add_argument("--check", action="store_true", help="compare the live site with this checkout; no FTP")
    parser.add_argument("--dry-run", action="store_true", help="list what would be published, upload nothing")
    parser.add_argument("--go", action="store_true", help="publish without asking")
    parser.add_argument("--baseline", action="store_true",
                        help="record this commit as what the live site already shows; upload nothing")
    parser.add_argument("--no-build", action="store_true", help="publish _site/ as it is")
    parser.add_argument("--allow-dirty", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.setup:
        setup(args)
    elif args.check:
        check_live(args)
    else:
        deploy(args)


if __name__ == "__main__":
    main()
