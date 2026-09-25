#!/usr/bin/env python3
"""Measure the banner text against the pixels actually behind it.

Where the banner is a looping video, one sample proves nothing: the cells
cross-fade, so the pixels behind the headline are brightest somewhere in the
middle of the loop and a single reading can easily catch it at its darkest.
This seeks through the video and reports the worst moment.

A hero is the one place where text sits on a photograph, so its contrast
cannot be read off a stylesheet — it depends on the picture, the scrim and
where the words land. This samples the rendered page: for each piece of text
in the banner it averages the background under its box and reports the ratio,
against the WCAG AA floors (4.5:1 for body text, 3:1 for large text).

    python3 tools/check-contrast.py                   # Admissions, the default
    python3 tools/check-contrast.py news.html         # any page with a .pagehero
    python3 tools/check-contrast.py crossroads.html   # the drifting cover wall
    python3 tools/check-contrast.py founder.html      # the Founder banner
    python3 tools/check-contrast.py cultural-gallery.html   # the fold over the photograph wall
    python3 tools/check-contrast.py why-cirs.html     # the lines over the About photographs
    python3 tools/check-contrast.py captures.html    # the line over the last frame of the camera
    python3 tools/check-contrast.py sports.html      # the line over the last frame of the field
    python3 tools/check-contrast.py the-cirs-experience.html # the headline in the campus band's gradient

Admissions and News are a .pagehero over a looping video and are seeked
through it. Crossroads is a wall of covers drifting behind the masthead,
which cannot be seeked — that one is simply left to run between shots.
Needs a server on :8990.
"""
import json, subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = r'''
const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('http://localhost:8990/__PAGE__', { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  // The contact panel opens over the banner on load. Measuring through it
  // reads the white card as "the background", which is how a perfectly
  // legible headline first appeared to fail at 2.3:1. Dismiss it first.
  const closer = await p.$('.pop__close, [data-pop-close]');
  if (closer) { await closer.click(); await p.waitForTimeout(700); }

  // Student Life's photograph band is not at the top of the page, and
  // scrolling to it fights the smooth-scroll library. The band is
  // self-contained — one full-height section with its own picture and its
  // own gradient — so hiding the hero above it brings the band to the top of
  // the viewport rendering exactly as it does in place.
  if (await p.$('.lifeband')) {
    await p.addStyleTag({ content: '.slhero{display:none!important}' });
    await p.waitForTimeout(600);
  }

  // CIRS Captures and Our Sports open on a film the reader scrubs with the
  // scroll, and the one line of type is not drawn at all until that film has
  // finished. At the top of the page there is nothing to measure; the
  // composition worth measuring is the one where the line is up. On a page
  // whose opening goes on to a photograph (Captures), the line leaves under
  // it at the end, so that is the moment it is being read — between the
  // third and fourth phase boundaries — rather than the foot of the opening.
  if (await p.$('[data-film]')) {
    await p.evaluate(() => {
      const opening = document.querySelector('[data-film]');
      const ph = (opening.getAttribute('data-film-phases') || '')
        .trim().split(/\s+/).map(Number);
      const at = ph.length >= 4 ? (ph[2] + ph[3]) / 2 : 1;
      // Instant, not the site's smooth scroll: a smooth scroll of three
      // screens is still under way when the photograph is taken, and it
      // measured the line mid-film, where it is not yet drawn.
      window.scrollTo({ top: (opening.offsetHeight - window.innerHeight) * at, behavior: 'instant' });
    });
    await p.waitForTimeout(2500);
  }

  // A looping video behind the text: sample across the loop, not once.
  const times = await p.evaluate(() => {
    const v = document.querySelector('.pagehero__video, .hero__video, .hseq__video');
    if (!v) return null;
    v.pause();
    const d = v.duration && isFinite(v.duration) ? v.duration : 8;
    return [0, 0.2, 0.4, 0.6, 0.8].map(f => +(d * f).toFixed(2));
  });
  // The Crossroads banner has no video but is no more static for it: 29
  // covers drift past the headline, so it needs the same treatment. There
  // is nothing to seek — we simply let it run between shots.
  // The Arts wall is the same case again: a field of photographs that the
  // fold sits on top of, with a scrim between them.
  const drifting = await p.evaluate(() => !!document.querySelector('.crwall, #p1-stage'));
  const boxes = await p.evaluate(() => {
    const out = [];
    document.querySelectorAll('.pagehero .sc, .pagehero h1, .pagehero .lead, .pagehero__dates dt, .pagehero__dates dd, .newsflash__label, .newsflash__item.is-on .newsflash__when, .newsflash__item.is-on .newsflash__what, .hero .sc, .hero h1, .hero__scroll, .hseq__type .sc, .hseq__type h1, .crhero .sc, .crhero__word, .crhero__lead, .crhero__note, .crmeter__n, .crmeter__t, .crhero__scroll, .fhero .fmeta, .fhero__name, .fhero__dates, .fhero__say, .fhero__sig, .fhero__cue, .p1-hero__eyebrow, .p1-hero-text, .p1-hero__cue, .p1-hud, .saga__eyebrow, .saga__line, .saga__by, .saga__more, .lifeband__say .sc, .lifeband__say h2, .lifeband__say .copy, .lifeband__cta .btn, .film__line').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) return;
      const cs = getComputedStyle(el);
      if (el.classList.contains('soft')) return;          // the pre-blurred copy of the title
      // Text painted with background-clip reports colour transparent. The
      // gradient's darkest stop is the worst the reader actually sees.
      let colour = cs.color;
      if (/rgba\(\d+, ?\d+, ?\d+, ?0\)/.test(colour) && cs.backgroundImage !== 'none') {
        const stops = [...cs.backgroundImage.matchAll(/rgba?\(([^)]+)\)/g)]
          .map(m => m[1].split(',').slice(0, 3).map(Number))
          .filter(c => c.length === 3 && c.every(v => !isNaN(v)));
        if (stops.length) {
          const lum = c => c[0] * .2126 + c[1] * .7152 + c[2] * .0722;
          const worst = stops.reduce((a, b) => lum(a) < lum(b) ? a : b);
          colour = `rgb(${worst.join(', ')})`;
        }
      }
      out.push({ what: (el.className || el.tagName).toString().split(' ')[0],
                 text: el.textContent.trim().slice(0, 28),
                 color: colour, bg: cs.backgroundColor,
                 size: parseFloat(cs.fontSize), weight: cs.fontWeight,
                 x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) });
    });
    return out;
  });
  // hide the text, photograph what is behind it
  await p.addStyleTag({ content: '.pagehero .wrap, .hero .wrap, .crhero .wrap, .p1-hero > *, .p1-hud, .saga__inner, .lifeband__say, .film__title, .film__shot{visibility:hidden!important}' });
  await p.waitForTimeout(300);
  const shots = [];
  const passes = times || (drifting ? [null, null, null, null, null] : [null]);
  for (const t of passes) {
    if (t === null && drifting && shots.length) await p.waitForTimeout(1600);
    if (t !== null) {
      await p.evaluate(async (tt) => {
        const v = document.querySelector('.pagehero__video, .hero__video, .hseq__video');
        v.currentTime = tt;
        await new Promise(r => { v.onseeked = r; setTimeout(r, 900); });
      }, t);
      await p.waitForTimeout(250);
    }
    const shot = await p.screenshot({ clip: { x: 0, y: 0, width: 1440, height: 900 } });
    shots.push({ t, png: shot.toString('base64') });
  }
  console.log(JSON.stringify({ boxes, shots }));
  await b.close();
})();
'''

def lum(rgb):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def opaque(css):
    """The element's own background as RGB, or None if it lets what is
    behind it through."""
    parts = css.strip("rgba() ").split(",")
    if len(parts) < 3 or not parts[0].strip():
        return None
    if len(parts) > 3 and float(parts[3]) < 1:     # translucent: the photo shows through
        return None
    return tuple(int(float(v)) for v in parts[:3])


def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)

def main():
    # playwright-core is installed in the scratchpad, and node resolves
    # modules relative to the script, so the script has to live there too.
    work = os.environ.get("CIRS_BROWSER_DIR",
        "/tmp/claude-0/-home-user-CIRS-Website/6d0b201c-2b08-519d-94f9-82eb38a29cd4/scratchpad")
    page = sys.argv[1] if len(sys.argv) > 1 else "admissions.html"
    print(f"measuring {page}\n")
    tmp = os.path.join(work, "_contrast.js")
    open(tmp, "w").write(JS.replace("__PAGE__", page))
    out = subprocess.run(["node", tmp], capture_output=True, text=True, cwd=work)
    if out.returncode:
        sys.exit("check-contrast: " + out.stderr[-500:])
    data = json.loads(out.stdout)
    import base64, io
    from PIL import Image

    worst = {}
    for shot in data["shots"]:
        im = Image.open(io.BytesIO(base64.b64decode(shot["png"]))).convert("RGB")
        for box in data["boxes"]:
            own = opaque(box.get("bg", ""))
            if own:
                # The element paints its own opaque ground — a pill, a card —
                # so the photograph behind it is not what the text sits on.
                # Measuring through it is how a checker once read 2.32:1 on
                # a headline that was never in front of the thing it sampled.
                avg = own
            else:
                crop = im.crop((box["x"], box["y"], box["x"] + box["w"], box["y"] + box["h"]))
                px = list(crop.getdata())
                avg = tuple(sum(c[i] for c in px) // len(px) for i in range(3))
            fg = tuple(int(v) for v in box["color"].strip("rgba() ").split(",")[:3])
            r = ratio(fg, avg)
            key = box["what"] + "|" + box["text"]
            if key not in worst or r < worst[key][0]:
                worst[key] = (r, box, shot["t"])

    if len(data["shots"]) > 1:
        print(f"sampled {len(data['shots'])} points across the loop; "
              f"showing the worst for each line\n")
    fails = []
    print(f"{'ratio':>8}  {'floor':>5}  {'at':>5}  element                text")
    for key, (r, box, t) in worst.items():
        large = box["size"] >= 24 or (box["size"] >= 18.66 and int(box["weight"]) >= 700)
        floor = 3.0 if large else 4.5
        ok = r >= floor
        if not ok:
            fails.append(key)
        at = "still" if t is None else f"{t:>4.1f}s"
        print(f"{r:8.2f}  {floor:5.1f}  {at:>5}  {'ok  ' if ok else 'FAIL'} "
              f"{box['what']:<16} \"{box['text']}\"")

    if fails:
        print(f"\n{len(fails)} element(s) below the floor")
        sys.exit(1)
    print("\nall banner text clears WCAG AA at every point sampled in the loop")


if __name__ == "__main__":
    main()
