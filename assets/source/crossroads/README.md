# Crossroads cover scans — originals

The school's own cover scans, at whatever resolution they arrived in. Like the
rest of `assets/source/`, **nothing here is deployed** — `tools/stage-deploy.py`
copies only files a page actually references.

Name each one for its issue number:

    issue-01.jpg
    issue-02.jpg
    ...

then run `python3 tools/make-covers.py`, which writes the cropped 720x1008
copies the archive page ships into `assets/img/crossroads/`.
