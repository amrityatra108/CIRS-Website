# Marble sanctuary plates

The supplied `NEW_LANDING_REFERENCE.png` guided the environment. Built-in image generation edited the environment to remove the frozen emblem and all text/UI. The exact source emblem, invocation and controls are rendered separately in the webpage. The archival hospital photograph was not generated or retouched.

## Desktop edit direction

Preserve the warm ivory marble room, curved wall, frontal perspective, carved rectangular stepped altar, lotus/paisley/temple reliefs, pink floor lotuses, light direction and framing. Remove only the floating emblem, its associated shadow, GURUDEV, Spiritual, the plaque inscription, footer controls and sparkle. Reconstruct a clean marble wall and blank inset plaque. Do not add a new object, lettering or emblem.

Saved master: `altar-desktop.png`, 1661 × 947.

## Portrait edit direction

Adapt the same clean architectural plate to a tall phone composition, preserving the carving and warm lighting. Keep the frontal camera, a broad intact altar in the lower part of the composition, generous wall space above for the live emblem, and pink lotuses on the floor. Keep the plaque blank and omit all emblems, labels, UI and sparkle.

Saved master: `altar-mobile.png`, 941 × 1672.

## Reproducible derivatives

`tools/prepare-marble-assets.py` saves the WebP assets at quality 92 with method 6. It also makes `emblem-static.svg` from the existing native fallback outline with an ivory/blue-grey fill. It performs format preparation; it does not redraw the photograph or emblem geometry. `manifest.json` records SHA-256 hashes of all delivered masters and derivatives.

Generated image masters are included because a generative edit cannot be reproduced byte-for-byte from its prompt alone. No remote generation dependency exists at website runtime.
