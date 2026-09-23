# Our Sports — browser review

The storyboard in [`storyboard.md`](storyboard.md) was completed before the page-source changes. These captures are from the rebuilt page in Chrome at **1440 × 900** and **390 × 844**. The opening film is the MP4 supplied for this page.

## Opening and exact frame handoff

The opening clip scrubs from its first frame to frame 120 at **5.011667 seconds**. At each viewport, the handoff was captured on the last video frame and again one CSS pixel later, when the new scene is at progress `0` and its background is the image extracted from that exact video frame.

| Viewport | Moving film | Last video frame | New scene, 1 px later |
| --- | --- | --- | --- |
| 1440 × 900 | [Film action](browser-1440-film-action.jpg) | [Frame 120](browser-1440-handoff-before.jpg) | [Handoff start](browser-1440-handoff-after.jpg) |
| 390 × 844 | [Film action](browser-390-film-action.jpg) | [Frame 120](browser-390-handoff-before.jpg) | [Handoff start](browser-390-handoff-after.jpg) |

The recorded time is `5.011667 s` on both sides of the handoff. The outgoing and incoming image plates come from the same final frame; the transition begins over that still composition.

## MOVE transition

The user-supplied sprint photograph enters once over the held field frame. At the midpoint, the same single scene holds while the word remains legible over the runners. A different, wide finish photograph then wipes up through the track foreground, and MOVE resolves into the athletics line. The earlier repeated runner section and photo-filled text treatment are gone.

| State | 1440 × 900 | 390 × 844 |
| --- | --- | --- |
| Entry (`0.25`) | [Capture](browser-1440-entry.jpg) | [Capture](browser-390-entry.jpg) |
| Midpoint (`0.56`) | [Capture](browser-1440-midpoint.jpg) | [Capture](browser-390-midpoint.jpg) |
| Exit (`0.95`) | [Capture](browser-1440-exit.jpg) | [Capture](browser-390-exit.jpg) |

The midpoint was reached in both directions after a fast jump to `0.91`. Forward and reverse landed on progress `0.56`; the scroll-linked scale and finish-photo clip values matched. Forward/reverse screenshot mean absolute pixel differences were **0.36/255** on desktop and **0.42/255** on mobile.

- [Desktop midpoint, forward](browser-1440-midpoint-forward.jpg) · [reverse](browser-1440-midpoint-reverse.jpg)
- [Mobile midpoint, forward](browser-390-midpoint-forward.jpg) · [reverse](browser-390-midpoint-reverse.jpg)

The action-image reveal and word were also stepped slowly through progress `0.12`, `0.20`, `0.28` and `0.36`. At both viewport widths the finish photo returns to fully clipped when scrolling backward to the midpoint.

## Distinct scenes after the transition

Court and pool use different CIRS Drive photographs. The supplied yoga photograph is the later quiet hold.

| Scene | 1440 × 900 | 390 × 844 |
| --- | --- | --- |
| Basketball | [Capture](browser-1440-chapter-court.jpg) | [Capture](browser-390-chapter-court.jpg) |
| Swimming | [Capture](browser-1440-chapter-water.jpg) | [Capture](browser-390-chapter-water.jpg) |
| Yoga | [Capture](browser-1440-yoga.jpg) | [Capture](browser-390-yoga.jpg) |

## Review results

- The film and all transition photos loaded; the local preview returned HTTP `206` for a byte-range request, allowing the MP4 to seek while scrolling.
- No page errors, console errors or failed requests were recorded. Document width matched the viewport at both sizes, and the reduced-motion mobile page also had no horizontal overflow.
- In reduced motion, the scroll-pinned scenes are removed and the page stays in normal flow.
- The forward and reverse states matched at the same progress. The production host's video range behavior was not checked by this local preview.

See [`asset-sources.md`](asset-sources.md) for the supplied-photo mapping.
