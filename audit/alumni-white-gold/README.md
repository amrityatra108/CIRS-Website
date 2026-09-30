# Alumni white-and-gold review

Alumni-only implementation. No production merge is authorized for this task.

- 240 Natural Earth country/territory polygons use the existing Robinson projection. The original 19 verified markers, origin, nudges and route generation are unchanged. All 166 institution records and 14 destination countries are preserved; unresolved coordinates remain unplotted.
- Country hover/focus shows the name and institution count. Geographic clicks, keyboard arrows/Enter, country selection and region controls open a native directory dialog. Search, browse all, honest empty states, sticky Close, Escape, Tab containment, background scroll locking and opener/scroll restoration work without GSAP.
- All three complete quotations and attributions are visible in a responsive card grid. Existing hero, photographs, biographies, links and five pathways/evidence remain intact.
- The existing pathway scroll controller synchronizes five pale grounds on forward/reverse scrolling and direct selection. Mobile, short windows, no JavaScript and reduced motion retain stacked scenes. No second scroll controller.
- The closing section has white surfaces, dark text, muted gold details, a quiet contour motif and the retained valley photograph. Shared navigation/footer are unchanged.

## Evidence

[Map](map.png) · [Quotes](quotes.png) · [Pathway](pathway.png) · [Stay connected](connected.png) · [Mobile directory](mobile-directory.png)

[Browser results](browser-results.json) · [Accessibility results](accessibility.json)

Checks performed with Chromium and Playwright:

- Desktop 1440×1000, tablet 768×1024, touch phone 390×844, narrow phone 320×640, short desktop 1440×650.
- Three repeated open/search/empty/reset/close cycles; scroll lock and restoration; Shift+Tab/Tab containment; Escape and visible Close; opener focus restored.
- Country keyboard traversal, actual polygon pointer hit, region/country counts, empty-country honesty, all 166 rows through Browse all.
- All five scene colours, direct navigation, reverse scrolling, resize teardown/rebuild and active navigation.
- No horizontal overflow; no browser runtime errors. No-JavaScript/reduced-motion views preserve three quotes, five pathways, all 166 institution entries and `#pathways`.
- `html-validate@11` across root and Curriculum HTML; `tools/check-links.py`; build/freshness; JavaScript syntax.
- AST comparison against starting commit `29e15d7` confirms unchanged ALUMNI, VOICES, PATHWAYS, origin, projection calls and route generation. The institution JSON is byte-identical. Hero markup, all original image sources and original links are retained.
- Axe WCAG 2 A/AA and 2.1 AA: no violations in map, quotes, pathways, connection section or dialog. Map-label contrast remains an automated manual-review item because of overlapping SVG/pseudo-elements. Explicit label colours were checked: small labels `#54534d` on white **7.72:1**; map names `#1f1f1b` on white **16.53:1**; focus `#76581f` on white **6.59:1**. Body text on the darkest static pathway ground is **5.06:1**.

## Reproduce browser checks

Serve the repository with `python3 -m http.server 8000`. Install Playwright outside the repository, then:

```sh
CIRS_BROWSER_DIR=/path/to/node_modules node tools/check-alumni-browser.cjs
```

Optional variables: `CIRS_CHROMIUM`, `CIRS_ALUMNI_URL`, `CIRS_ALUMNI_REVIEW_DIR`. Screenshots default to `/tmp/cirs-alumni-review`.

## Geometry provenance

Natural Earth 1:50m admin-0 boundaries, public domain, distributed in `world-atlas@2.0.2/countries-50m.json`. World-atlas copyright/license is retained in [world-atlas-LICENSE.txt](world-atlas-LICENSE.txt).

Source SHA-256: `04342cdc1e3016bcd7db1630de95684d67b79fe3c8c460321e87aef469502394`.

Regenerate with `python3 tools/make-alumni-countries.py /path/to/world-atlas/countries-50m.json`. The tool verifies the source hash and uses the existing Robinson projection, latitude crop and antimeridian handling; output is committed so normal builds need no network. No island-area threshold is applied. Boundaries are illustrative, not a statement of political recognition; text controls make tiny territories accessible. Antarctica remains outside the original map crop.

## Remaining limits

Touch is browser-emulated, not a physical iOS/Android device test. Safari/VoiceOver, physical on-screen keyboards and safe-area/rubber-band behaviour still need device review. Automated checks cannot establish the subjective feel of animation. External institutions/biography/form links were preserved; the repository link check is offline and does not revalidate third-party availability or alumni relationships.
