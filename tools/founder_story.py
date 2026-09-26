#!/usr/bin/env python3
"""Build the supplied Gurudev life story as accessible Founder page markup."""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "tools", "data", "founder-gurudev-events.json")
MEDIA = "assets/img/founder/gurudev-journey"
PHOTO_IDS = {"A202", "A203", "A209", "A210", "A213", "A214", "A218"}


def esc(value):
    return html.escape(str(value), quote=True)


def _scene(event, index):
    classes = ["founder-gurudev-journey__scene"]
    if event["id"] == "E05":
        classes.append("is-long")
    if event["id"] == "END":
        classes.append("is-ending")

    paragraphs = "\n".join(
        f"        <p>{esc(paragraph)}</p>" for paragraph in event["paragraphs"]
    )
    if event.get("asset") in PHOTO_IDS:
        image = f"{MEDIA}/{esc(event['asset'])}.jpg"
        media = (
            '      <figure class="founder-gurudev-journey__media">\n'
            f'        <img src="{image}" alt="{esc(event["alt"])}" '
            'loading="lazy" decoding="async">\n'
            f'        <figcaption>{esc(event["caption"])}</figcaption>\n'
            "      </figure>"
        )
    else:
        art = event["art"]
        media = (
            '      <div class="founder-gurudev-journey__type-art" aria-hidden="true">\n'
            f'        <span>{esc(art[0])}</span>\n'
            f'        <strong>{esc(art[1])}</strong>\n'
            f'        <span>{esc(art[2])}</span>\n'
            "      </div>"
        )

    return (
        f'    <article class="{" ".join(classes)}" data-story-scene '
        f'data-event="{esc(event["id"])}" aria-hidden="false">\n'
        '      <div class="founder-gurudev-journey__copy">\n'
        f'        <p class="founder-gurudev-journey__kicker">{esc(event["kicker"])}</p>\n'
        f'        <p class="founder-gurudev-journey__date">{esc(event["date"])}</p>\n'
        f'        <h2>{esc(event["title"])}</h2>\n'
        f'        <div class="founder-gurudev-journey__body">\n{paragraphs}\n        </div>\n'
        "      </div>\n"
        f"{media}\n"
        "    </article>"
    )


def journey_html():
    """Return the twelve events and closing image in both reading modes."""
    with open(DATA, encoding="utf-8") as source:
        events = json.load(source)
    if len(events) != 13 or events[-1].get("id") != "END":
        raise ValueError("Founder story data must contain E01–E12 followed by END")

    scenes = "\n".join(_scene(event, index) for index, event in enumerate(events))
    vehicle = f"{MEDIA}/vehicle.webp"

    return f'''<section class="founder-gurudev-journey" id="life" data-gurudev-journey
         aria-label="Gurudev's life story">
  <h2 class="sr-only">Gurudev's life story</h2>
  <div class="founder-gurudev-journey__runway" data-story-runway>
    <div class="founder-gurudev-journey__stage" data-story-stage>
      <div class="founder-gurudev-journey__viewport" data-story-viewport>
        <div class="founder-gurudev-journey__world" data-story-world>
          <svg class="founder-gurudev-journey__route" data-story-route aria-hidden="true">
            <path class="founder-gurudev-journey__road-edge" data-route-path></path>
            <path class="founder-gurudev-journey__road-surface" data-route-overlay></path>
            <path class="founder-gurudev-journey__road-marks" data-route-center></path>
          </svg>
          <div class="founder-gurudev-journey__scenes" data-story-scenes>
{scenes}
          </div>
          <div class="founder-gurudev-journey__vehicle" data-story-vehicle aria-hidden="true">
            <div class="founder-gurudev-journey__vehicle-art" data-vehicle-art>
              <img class="founder-gurudev-journey__vehicle-body" src="{vehicle}" alt="">
              <span class="founder-gurudev-journey__wheel founder-gurudev-journey__wheel--rear" data-wheel="rear"><img src="{vehicle}" alt=""></span>
              <span class="founder-gurudev-journey__wheel founder-gurudev-journey__wheel--front" data-wheel="front"><img src="{vehicle}" alt=""></span>
            </div>
          </div>
        </div>
      </div>
      <div class="founder-gurudev-journey__topline">
        <span>GURUDEV <span class="founder-gurudev-journey__topline-note">/ THE LIFE STORY</span></span>
        <span class="founder-gurudev-journey__counter" data-story-count aria-live="polite">01 / 12</span>
      </div>
    </div>
  </div>
</section>'''
