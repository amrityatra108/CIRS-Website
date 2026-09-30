# Parent Portal design verification

Verified locally on 30 September 2026 against main `cd05b21`.

The existing orientation photograph fills the first viewport immediately, with
one visible Parent Portal h1. The original banner introduction now sits on the
photograph. The shared curtain and the former Portal entrance/parallax scripts
are excluded from this page. Service content has no reveal or split hooks.

The service section uses the site's ivory and ink roles, gold accents, an ivory
contact panel, and a decorative open-book drawing. Styles are scoped to
`body.parent-portal`. All seven service/contact/navigation links and original
service copy match the baseline; destinations, new-tab instructions and
`rel="noopener"` remain intact. The responsive image sources and photograph
alt text remain intact. Header, drawer and footer markup match the baseline
apart from asset cache queries and the existing header start mode changing from
`content` to `hero` for the full-screen photograph. Shared partials and scripts
are unchanged. Portal assets use the scoped `-portal-photo-2` cache suffix.

## Checks

- `npx --yes --cache /tmp/npm-cache html-validate@11 '*.html'`: passed.
- `python3 tools/check-links.py`: 120 pages, 17,957 references, all resolve.
- `python3 tools/build-site.py`: repeated build produced no unstaged HTML drift.
- `git diff --check`: passed.
- Chromium/Playwright: 1440×900 desktop, 768×1024 tablet, 390×844 phone,
  320×568 narrow phone and 844×390 landscape; also reduced motion at 1440×900
  and JavaScript disabled at 390×844. Each hero equals viewport height;
  photograph, h1 and entry are visible with no clipping, transform or opacity
  gate. No horizontal overflow, page/console errors or failed local assets.
- Entry click lands on `#portal` with the content below the shared header in
  all seven modes. No hidden service content.
- Keyboard: skip link, entry activated with Enter, fee payment → parent login →
  school phone order, visible focus, shared Menu opening and Escape closing pass.
- Contrast: a temporary adapter of `tools/check-contrast.py` uses the Portal
  selectors, the installed Chromium and local port 8993. All four hero text
  elements pass at all five viewport sizes; lowest sampled ratio is 8.64:1
  (large heading; required 3:1). The label and entry have opaque ink backings.
  Service text uses the site's ink on ivory/cream/gold-pale surfaces.
- Integrity: original service text and ordered hrefs compare identically with
  `origin/main`; original banner introduction retained verbatim. One h1. No
  generated files outside Parent Portal changed. Creative Writing unchanged.

Local evidence is in `/tmp/portal-evidence/`: `report.json`, `keyboard.json`,
`contrast.log`, `html-validate.log`, `check-links.log`, browser scripts and hero/
service screenshots for every mode. Third-party sign-ins were not submitted.
Publication and live verification are reserved for the coordinating agent.
