# Curriculum cinematic refinement QA

30 September 2026. Continued local Curriculum source commit `42405e473944df587dd6f622cad28b1815e8409e` in the isolated `codex/curriculum-cinematic-review-20260930` branch.

- Bright-gold opening and Diploma core, pale-gold full-width fork and warm-white reading sections. The user's explicit no-purple constraint supersedes the earlier proposed plum palette. Existing illustrated hero and all photographs preserved.
- Junior and Senior photographs alternate on desktop/tablet. The road crosses their actual intervening gap. Mobile keeps prose followed by its photograph and a vertical gutter road.
- Route meets waypoint and choice icons at their edges. The school photographs reveal once; reduced-motion photographs and paths remain static and complete.
- Returning via browser Back to the initial URL now clears the selected route. Existing route selection, switching, focus and real history remain.
- Built only Curriculum through the repository generator. No other page was written. HTML validation, JavaScript syntax and diff whitespace checks pass.
- Integrated upstream `b862292`: retained the current Senior overview and CBSE/IB context, including the two newer laboratory photographs. Existing academic fragment aliases remain usable.
- 167 browser assertions pass in headless Edge at 1440, 768, 390 and 320 pixels: original content and destinations preserved, seven loaded photographs, monotonic illumination, no horizontal overflow throughout the page, left CBSE/right IB paths, keyboard selection, route switching, Back/Forward, return focus, 44px route controls, reduced motion and JavaScript-disabled reading/navigation.
- No browser JavaScript errors or failed HTTP resources. Thirty-four final screenshots captured; desktop, tablet and phone opening/school/fork views visually reviewed.
- After integration with main `b2388d7`, the Curriculum-only release's link checker passes: 120 pages and 17,918 references all resolve. Read-only comparison of all 120 generated pages passes. Full HTML validation, eight media lifecycle regression tests and read-only anthology integrity pass.
- Separate palette checks confirm bright gold `#FFC308`, visible hero illustration and zero overflow at all four widths. Desktop and mobile opening/fork/core screenshots reviewed. Header text uses the existing light-header mode to remain readable on gold.
- Creative Writing, Alumni, Art, Maths, Blog, playback fixes and shared styling are untouched in this release. The separately requested Blog palette restoration is held on a separate prepared branch.

Evidence and repeatable build/browser scripts are in the task workspace next to the checkout: `evidence/verification.json`, `evidence/gold-palette-verification.json`, `evidence/final-*.png`, `evidence/gold-*.png`, `build-curriculum.py`, `verify.cjs`. Preview: `http://127.0.0.1:8019/curriculum.html`.

Physical-phone behavior was not tested; responsive browser, keyboard and reduced-motion behavior was tested.
