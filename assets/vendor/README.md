# The motion layer, vendored

GSAP, ScrollTrigger and Lenis are served from this site rather than from a
CDN. Three files, 125 KB between them.

| file | library | version | came from |
| --- | --- | --- | --- |
| `gsap.min.js` | GSAP | 3.12.5 (in its own header) | `cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js` |
| `ScrollTrigger.min.js` | ScrollTrigger | 3.12.5 (in its own header) | `cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js` |
| `lenis.min.js` | Lenis | 1.1.20 — see the note below | `cdn.jsdelivr.net/npm/lenis@1.1.20/dist/lenis.min.js` |

GSAP and ScrollTrigger carry their version in a comment at the top of the
file, so those two can be checked by opening them. Lenis's build carries no
version string at all; 1.1.20 is the version the pages pinned before this
change, and the file is the one that was fetched from that pinned URL. If you
ever need certainty, diff it against a fresh download.

## Why not the CDN

Three reasons, in the order they matter.

1. **The motion layer could not be tested.** Sandbox sessions working on this
   repository reach the internet through a proxy that answers 403 to both
   cdnjs and jsdelivr, so GSAP and Lenis never loaded and every browser check
   silently exercised the no-JS fallback path instead. Anything about the
   reveals, the pinned sections or the smooth scroll needed a person looking
   at the deployed site. Now it can be checked before it ships.
2. **One origin.** No third party sees a visitor's IP and user-agent on every
   page load, and the site does not go quiet if a CDN does.
3. **The versions stop drifting.** A pinned URL is only pinned until someone
   edits it; a file in the repository is what it is.

The cost is that updates are manual. There is no package manager here.

## Updating

Download the new version, replace the file, update the table above, and bump
`CACHE_BUST` in `tools/build-site.py` so browsers fetch it. Then load a page
and confirm the reveals still run — `assets/js/cirs.js` checks for GSAP with
`typeof window.gsap !== "undefined"` and quietly falls back to the static page when
it is missing, so a broken file looks like no animation rather than an error.

ScrollTrigger is retained byte-for-byte from the committed upstream copy. Its built-in debug-marker font stack is inactive because the site does not enable markers; it is not part of the four-family website typography configuration. Do not patch the vendor library solely to change debug typography.
