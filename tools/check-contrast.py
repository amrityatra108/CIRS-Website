#!/usr/bin/env python3
"""Measure the banner text against the pixels actually behind it.

A hero is the one place where text sits on a photograph, so its contrast
cannot be read off a stylesheet — it depends on the picture, the scrim and
where the words land. This samples the rendered page: for each piece of text
in the banner it averages the background under its box and reports the ratio,
against the WCAG AA floors (4.5:1 for body text, 3:1 for large text).

    python3 tools/check-contrast.py            # needs a server on :8990
"""
import json, subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = r'''
const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('http://localhost:8990/admissions.html', { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  // The contact panel opens over the banner on load. Measuring through it
  // reads the white card as "the background", which is how a perfectly
  // legible headline first appeared to fail at 2.3:1. Dismiss it first.
  const closer = await p.$('.pop__close, [data-pop-close]');
  if (closer) { await closer.click(); await p.waitForTimeout(700); }
  const boxes = await p.evaluate(() => {
    const out = [];
    document.querySelectorAll('.pagehero .sc, .pagehero h1, .pagehero .lead, .pagehero__dates dt, .pagehero__dates dd').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) return;
      const cs = getComputedStyle(el);
      out.push({ what: (el.className || el.tagName).toString().split(' ')[0],
                 text: el.textContent.trim().slice(0, 28),
                 color: cs.color, size: parseFloat(cs.fontSize), weight: cs.fontWeight,
                 x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) });
    });
    return out;
  });
  // hide the text, photograph what is behind it
  await p.addStyleTag({ content: '.pagehero .wrap{visibility:hidden!important}' });
  await p.waitForTimeout(300);
  const shot = await p.screenshot({ clip: { x: 0, y: 0, width: 1440, height: 900 } });
  console.log(JSON.stringify({ boxes, png: shot.toString('base64') }));
  await b.close();
})();
'''

def lum(rgb):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)

def main():
    # playwright-core is installed in the scratchpad, and node resolves
    # modules relative to the script, so the script has to live there too.
    work = os.environ.get("CIRS_BROWSER_DIR",
        "/tmp/claude-0/-home-user-CIRS-Website/6d0b201c-2b08-519d-94f9-82eb38a29cd4/scratchpad")
    tmp = os.path.join(work, "_contrast.js")
    open(tmp, "w").write(JS)
    out = subprocess.run(["node", tmp], capture_output=True, text=True, cwd=work)
    if out.returncode:
        sys.exit("check-contrast: " + out.stderr[-500:])
    data = json.loads(out.stdout)
    import base64, io
    from PIL import Image
    im = Image.open(io.BytesIO(base64.b64decode(data["png"]))).convert("RGB")

    worst = 0.0
    fails = []
    print(f"{'ratio':>8}  {'floor':>5}  element                text")
    for box in data["boxes"]:
        crop = im.crop((box["x"], box["y"], box["x"] + box["w"], box["y"] + box["h"]))
        px = list(crop.getdata())
        avg = tuple(sum(c[i] for c in px) // len(px) for i in range(3))
        fg = tuple(int(v) for v in box["color"].strip("rgba() ").split(",")[:3])
        r = ratio(fg, avg)
        large = box["size"] >= 24 or (box["size"] >= 18.66 and int(box["weight"]) >= 700)
        floor = 3.0 if large else 4.5
        ok = r >= floor
        if not ok:
            fails.append((box, r, floor))
        worst = max(worst, floor - r)
        print(f"{r:8.2f}  {floor:5.1f}  {'ok  ' if ok else 'FAIL'} {box['what']:<16} \"{box['text']}\"")

    if fails:
        print(f"\n{len(fails)} element(s) below the floor")
        sys.exit(1)
    print("\nall banner text clears WCAG AA against the pixels behind it")

if __name__ == "__main__":
    main()
