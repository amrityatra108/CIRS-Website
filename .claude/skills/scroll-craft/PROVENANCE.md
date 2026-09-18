# Where this came from

`scroll-craft` is Nate Herk's skill, vendored here from

    https://github.com/nateherkai/scroll-craft
    plugins/nateherk-design/skills/scroll-craft
    commit 0b81622

It is MIT licensed; `LICENSE` beside this file is the upstream copy, unchanged.

It is checked in as a **project skill** rather than installed from the plugin
marketplace so that every session working on this repository has it without a
per-machine install. The trade is that it does not update itself. To take a
newer version, re-copy that directory from upstream and update the commit
above; nothing here has been edited, so there is nothing to merge.

The alternative, if you would rather track upstream than vendor it:

    /plugin marketplace add nateherkai/scroll-craft
    /plugin install nateherk-design@nateherk

## It needs no key for this site

`scripts/kie.mjs` talks to api.kie.ai to GENERATE imagery and video, and that
is the only thing in here that reaches the network. CIRS builds from the
school's own photographs, so that path is unused and `KIE_AI_API_KEY` is not
set. The skill treats bring-your-own-assets as a first-class route, not a
fallback.

## Where it disagrees with this site

Read these before applying its hard rules to CIRS. The skill is a house style,
and it is not this house.

- **Em dashes.** It bans them from visible copy. This site's writing uses them
  throughout, deliberately. The site wins; it is the owner's voice.
- **Sequence numbers.** It bans `01 / 06` section counters. The numbers beside
  the photographs in the home page run are archive indices the owner asked for
  by name, not section counters, so they stay.
- **Workspace.** It wants a `scrollcraft/` workspace at the project root for
  builds and a fingerprint registry. Nothing in this repository is built that
  way. If a scroll-craft build is ever made for CIRS, drop a `.scrollcraft.json`
  pointing somewhere outside the deploy, or `tools/stage-deploy.py` will have
  opinions about the stray HTML.
- **Its verification scripts overlap ours.** `scripts/shoot.mjs` walks scroll
  positions and measures contrast on the composited page. That is the same job
  as `tools/check-contrast.py`, which already knows this site's selectors and
  its hero video. Prefer ours here; read theirs for the parts it does that ours
  does not, chiefly dead-scroll detection and the per-act contact sheet.
