# Additional CIRS Captures photographs

Source: `C:\Users\YEP15\Downloads\cirs captures photo.zip`, supplied on
2026-09-24. The ZIP has 44 numbered PNG frames at 1920 × 1080. Frames 1–43
contain photographs; frame 44 is entirely white and contains no photograph.

These 34 JPEGs retain the complete photographic area of the new frames. The
PNG export placed each photo on a white canvas, so the exact white outer
margin was removed before saving at high quality. The numbered filename
points back to the corresponding PNG frame. Photographer, date and precise
location were not supplied and are not inferred in the page captions.

Nine frames repeat photographs already held in
`assets/source/captures-2026-09-24/`. The page uses those existing source
files once, rather than storing or displaying a second copy:

| ZIP frame | Existing source file |
| --- | --- |
| 23 | `img-2031.jpg` |
| 24 | `img-4491.jpg` |
| 25 | `img-1887.jpg` |
| 27 | `img-4562.jpg` |
| 33 | `img-1396.jpg` |
| 34 | `img-1007.jpg` |
| 37 | `img-9515.jpg` |
| 40 | `dsc00453.jpg` |
| 41 | `dsc02269.jpg` |

`tools/captures.py` gives every unique photograph its place and caption.
`tools/make-captures-gallery.py` and `tools/make-captures-shot.py` make the
smaller images used by the site. Source files stay out of the staged site.
