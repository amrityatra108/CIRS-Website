# Temporary homepage intro preview

Open http://127.0.0.1:8765/temp-home-intro/ while the local server is running, or open index.html directly. All work is isolated in this folder; the production homepage and existing changes are untouched.

This is the integration prototype, not a finished campus-construction film. The reference video has now been supplied at C:/Users/YEP15/Downloads/start sample.mp4 and inspected; see REFERENCE-ANALYSIS.md and reference/contact-sheet.jpg. Architectural school imagery and CIRS construction footage remain missing. Cinematic final-frame alignment is not yet testable.

The existing hero poster is a 1280 x 720 front-of-school photograph, not an aerial image. The production hero uses campus-loop video. This preview intentionally substitutes the poster for that loop, and disables hero parallax only in its copied script, so the still handoff has consistent framing. It retains the original homepage layout, fonts, content, menus and other interactions.

The placeholder runs for 1.2 seconds after shared initialization, then crossfades for 350ms. It does not simulate school construction. A labelled overlay makes this limitation explicit. Replay preview clears only cirsHomeIntroSeen and reloads. Reduced motion, unavailable storage, no JavaScript and browser back navigation bypass the cover.

Files:
- build-preview.py creates index.html and cirs-preview.js from the current generated homepage and shared script without altering either input.
- intro.css and intro.js provide the temporary overlay and playback handling.
- check.cjs runs the browser checks; test-results.json and viewport PNGs record the results.

To regenerate: python temp-home-intro/build-preview.py
To serve from repository root: python -m http.server 8765 --bind 127.0.0.1
To test: node temp-home-intro/check.cjs

For supplied construction footage, set data-webm / data-mp4 and optional data-mobile-webm / data-mobile-mp4 in build-preview.py, then regenerate. Paths resolve relative to the repository root. WebM is preferred, MP4 is the fallback. Mobile stays on the still placeholder without portrait sources. Playback is muted; ended/timeupdate drives completion, with source errors, stalls, rejection and a watchdog releasing the cover. The final hero decode is awaited, with a bounded failure escape. No new media or fonts were added; video asset size, codec and exact cinematic duration remain pending.

Before production integration, supply the architectural image, aligned final aerial hero and desktop/portrait films; inspect and test their final frames, transfer costs, slow-network playback and crop alignment. The 6.5-second watchdog starts at document parsing and therefore can cut short slow-starting footage. This preview has no production build changes and does not claim full site regression certification.
