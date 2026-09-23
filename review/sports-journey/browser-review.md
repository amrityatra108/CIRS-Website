# Our Sports — browser review

This review compares the built page to the [four-state storyboard](storyboard-correction.md) at **1440 × 900** and **390 × 844**. Captures were made in local Chrome after the shared opening curtain cleared.

## Opening and frame handoff

The opening keeps the supplied film full bleed and adds a small “Scroll to discover” cue. The cue fades as the film begins moving with scroll.

| State | 1440 × 900 | 390 × 844 |
| --- | --- | --- |
| Opening cue | [Still](browser-1440-opening-cue.jpg) | [Still](browser-390-opening-cue.jpg) |
| Film action | [Still](browser-1440-film-action.jpg) | [Still](browser-390-film-action.jpg) |
| Final film frame | [Before](browser-1440-handoff-before.jpg) | [Before](browser-390-handoff-before.jpg) |
| Matching still, one CSS pixel later | [After](browser-1440-handoff-after.jpg) | [After](browser-390-handoff-after.jpg) |

At the handoff, the video is held at **5.011667 seconds (frame 120)**. The next scene opens on the same extracted frame. The paired screenshots show the film title leaving while the ball, line, goal and horizon stay aligned. The incoming section remains transparent up to its start, so there is no dark flash or second full-screen frame below the film.

## MOVE transition

The runner photo arrives along a short curved edge from the field line. MOVE enters after most of the image is visible, holds legibly over that one photo, then travels upward as the separate wide finish image opens behind it. The word changes from CIRS gold to purple with a gold edge as it reaches the bright pavilion in the finish photo; the Athletics line resolves beneath it.

| State | Progress | 1440 × 900 | 390 × 844 |
| --- | ---: | --- | --- |
| Entry | 0.38 | [Capture](browser-1440-entry.jpg) | [Capture](browser-390-entry.jpg) |
| Hold | 0.52 | [Capture](browser-1440-midpoint-forward.jpg) | [Capture](browser-390-midpoint-forward.jpg) |
| Exit | 0.95 | [Capture](browser-1440-exit.jpg) | [Capture](browser-390-exit.jpg) |

The transition was scrubbed slowly through **0.10, 0.20, 0.30, 0.36, 0.44, 0.52, 0.61, 0.72, 0.82 and 0.95**, then jumped quickly to 0.92 and reversed to 0.52. The forward and reverse midpoint captures match: mean absolute pixel difference is **0.001/255 on desktop** and **0/255 on mobile**.

- [Desktop midpoint, forward](browser-1440-midpoint-forward.jpg) · [reverse](browser-1440-midpoint-reverse.jpg)
- [Mobile midpoint, forward](browser-390-midpoint-forward.jpg) · [reverse](browser-390-midpoint-reverse.jpg)

## Nine distinct photo scenes

Each scene uses a different photograph. The final team huddle moves into the quieter yoga image after the pinned sequence.

| Scene | 1440 × 900 | 390 × 844 |
| --- | --- | --- |
| 01 Basketball court | [Capture](browser-1440-chapter-court.jpg) | [Capture](browser-390-chapter-court.jpg) |
| 02 Swimming | [Capture](browser-1440-chapter-water.jpg) | [Capture](browser-390-chapter-water.jpg) |
| 03 Field hockey | [Capture](browser-1440-chapter-hockey.jpg) | [Capture](browser-390-chapter-hockey.jpg) |
| 04 Tennis | [Capture](browser-1440-chapter-tennis.jpg) | [Capture](browser-390-chapter-tennis.jpg) |
| 05 Basketball game | [Capture](browser-1440-chapter-game.jpg) | [Capture](browser-390-chapter-game.jpg) |
| 06 Table tennis | [Capture](browser-1440-chapter-table.jpg) | [Capture](browser-390-chapter-table.jpg) |
| 07 Strength training | [Capture](browser-1440-chapter-strength.jpg) | [Capture](browser-390-chapter-strength.jpg) |
| 08 Solo basketball | [Capture](browser-1440-chapter-drive.jpg) | [Capture](browser-390-chapter-drive.jpg) |
| 09 Team huddle | [Capture](browser-1440-chapter-together.jpg) | [Capture](browser-390-chapter-together.jpg) |

- [Desktop scene contact sheet](browser-1440-chapters-contact.jpg)
- [Mobile scene contact sheet](browser-390-chapters-contact.jpg)

The quiet yoga hold after the nine-scene sequence is also a separate photograph: [desktop](browser-1440-yoga.jpg) · [mobile](browser-390-yoga.jpg). The following facilities copy gives the image sequence a visual pause before the closing athletics photograph.

## Checks

- Both viewports opened at scroll position 0 after the intro. The mobile scene nav now scrolls horizontally to the selected item without moving the page vertically.
- No horizontal overflow, page errors, console errors or failed requests were recorded. The image elements loaded when the page reached its final scenes.
- Reduced motion keeps all nine chapter images in normal document flow; the [mobile capture](browser-390-reduced-motion.jpg) confirms the page remains within 390 px.
- The local MP4 preview supports byte-range requests (`206`), so its final frame can be sought during the handoff.
- `python tools/check-links.py` resolved all 4,903 references across 43 pages. The production host has not been checked in this local review.

See [`asset-sources.md`](asset-sources.md) for the original file mapping and Drive sources.
