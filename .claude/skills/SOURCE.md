# Where these skills came from

The 141 skill folders alongside this file were installed from
**https://github.com/MengTo/skills** (Meng To's designer-focused agent skills),
cloned at commit `5f47e389dac3`.

They were flattened out of the upstream `agent-skills/<category>/` layout,
because Claude Code discovers skills one level deep — `.claude/skills/<name>/SKILL.md`.
The upstream categories were:

| category | count |
| --- | --- |
| web-design | 88 |
| codex | 20 |
| game-development | 20 |
| 3d | 8 |
| ui | 3 |
| media | 2 |

Demo assets (screenshots, sample pages, a few short videos) came with them,
which is most of the ~96 MB under this directory. Nothing here is part of the
site: `tools/check-links.py` walks only `assets/img` and `assets/video`,
`tools/stage-deploy.py` copies only assets a page references, and html-validate
runs against the root `*.html` pages, so none of this reaches a deploy.

The eight skills that predate this install — `animate`, `animation-vocabulary`,
`apple-design`, `emil-design-eng`, `find-animation-opportunities`,
`improve-animations`, `mobile-native`, `review-animations` — are not from that
repository and are unaffected.

Upstream is MIT licensed; see `LICENSE-MengTo-skills`.
