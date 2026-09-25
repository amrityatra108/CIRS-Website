# Art Attack photographs from the school's Drive

Renditions of photographs that live in the CIRS Studio Drive, kept here so
that `tools/make-art-attack.py` runs offline. **Nothing here is deployed**:
the tool writes the page's own cuts to `assets/img/art-attack/photos/`.

Each file is named for the camera file it came from. Its Drive file id and
the folder it sits in are recorded in `tools/art-attack.json`, and

    python3 tools/make-art-attack.py --fetch

downloads any that are missing, at 2400px wide, from Drive's image endpoint.
The folder names are the only source for the occasions the captions name
(Pongal, Fine Arts Week, the IB Visual Arts exhibition); where a folder names
no occasion, the caption names none either.
