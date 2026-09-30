# Festivals intro and white/gold page

The supplied five-second film stays in the same hero from its first frame through its real ending. The copy appears over the final 1.2 seconds; no timer truncates healthy playback or replaces the hero with an underlying page. The opening poster is selected before first paint. The last video frame holds. Skip and replay use one keyboard-accessible control; reduced motion, rejected playback, failed media, missing page script and no JavaScript leave a readable static hero. The startup watchdog clears when the first decoded frame arrives.

The festival chapters now use white and warm gold grounds. A subtle rangoli of gold rings decorates the introduction margin. All colours are confined to Festivals; shared navigation/footer sources and other pages' palette tokens are unchanged.

Visible descriptions that merely narrate photographs were removed from chapter captions and archive tiles/viewer. Verified festival/date labels, camera times, original photograph alt text and source metadata remain. The requested final “From Grade V to Grade XII” section is removed; its useful photograph/date request and contact link remain with the archive.

## Checks

- HTML validation: all generated root, Curriculum and Creative Writing reader pages pass html-validate 11.
- Links/assets: 120 pages, 17,988 references resolve after current-main integration before publication.
- Native playback: desktop 1440×900, tablet 768×1024, mobile 390×844 and 720×450 viewport simulation. Early copy hidden, late copy reveal, actual ended/currentTime at duration, final video retained, Skip/replay and focus retained.
- Reduced motion, no JavaScript, both video sources blocked, page script blocked, rejected autoplay and live motion-preference change pass. Replay also recovers when failed media becomes available.
- Gallery filtering, viewer keyboard arrows/Escape/focus return and shared navigation work; no horizontal overflow or normal-mode runtime errors.
- Exact content checks preserve all 14 chapter description paragraphs, the school meaning passage, all 15 India calendar entries, all seven chapter names, 58 rendered image references/alt texts, navigation and footer. MP4/WebM/poster/final still bytes are unchanged.
- Rendered-pixel contrast: sampled final hero heading at least 3.11:1; supporting hero text at least 9.19:1. White/gold introduction text meets its 3:1 large-text and 4.5:1 supporting-text floors. These measurements hide glyphs before sampling their rendered text rectangles, disable CSS colour transitions, and keep the photograph/scrim behind them.
- Decoded frames at 0.2, 1.2, 2.5, 3.5 and 4.9 seconds on desktop/mobile preserve intro timing; sampled navigation text contrast at least 13.03:1 across these frames. This is sampled Chromium evidence, not certification of every frame/device.
- JavaScript syntax, eight media lifecycle regression tests and whitespace checks pass. Repeat rebuild produces no HTML drift.

Run the regression browser check against a range-capable preview server:

```sh
CIRS_BROWSER_DIR=/path/containing/node_modules \
CIRS_PREVIEW_URL=http://127.0.0.1:8878 \
node tools/test-festivals-browser.cjs
```

Local screenshots and detailed measurements are in `/tmp/clutch-review/festivals/`. Physical devices and production browser QA were not tested from this executor: its outbound production request returned proxy `403` (`CONNECT tunnel failed`). The coordinating parent will check the published site.
