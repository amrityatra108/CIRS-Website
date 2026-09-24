"""Create a transparent founder portrait without modifying the source pixels.

The RGB portrait layer is copied directly from the supplied historical scan.
Only its alpha matte and a separate, low-opacity aura layer are synthesized.
"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "assets" / "balakrishna-menon.png"
OUTPUT = HERE.parent / "assets" / "balakrishna-menon-original-cutout.png"


def main() -> None:
    source_bgr = cv2.imread(str(SOURCE), cv2.IMREAD_COLOR)
    if source_bgr is None:
        raise FileNotFoundError(SOURCE)

    height, width = source_bgr.shape[:2]
    # The studio field is almost neutral white. Select pixels close to the
    # border's paper tone, then remove only components connected to the outer
    # edge. This keeps equally pale facial pixels because they are enclosed by
    # the hair, ears, and jaw rather than connected to the background.
    lab = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    border_sample = np.concatenate(
        [lab[:30, :60].reshape(-1, 3), lab[:30, -60:].reshape(-1, 3)], axis=0
    )
    paper = np.median(border_sample, axis=0)
    paper_distance = np.linalg.norm(lab - paper, axis=2)
    background_candidate = (paper_distance < 40).astype(np.uint8)
    count, labels = cv2.connectedComponents(background_candidate, 8)
    edge_labels = np.unique(
        np.concatenate([labels[0], labels[:, 0], labels[:, -1]])
    )
    background = np.isin(labels, edge_labels[edge_labels != 0]).astype(np.uint8) * 255
    background = cv2.morphologyEx(
        background, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=1
    )
    foreground = 255 - background
    # Exclude the darker uneven paper at the lower-right edge. This polygon is
    # deliberately outside the true portrait contour and never touches the
    # face; it only prevents aged backdrop tones from joining the torso matte.
    allowed = np.zeros_like(foreground)
    contour_guard = np.array(
        [[100, 14], [386, 14], [399, 270], [410, 310], [414, 370],
         [423, 450], [438, 530], [464, 585], [width - 1, height - 1],
         [0, height - 1], [0, 330], [76, 295], [96, 260]],
        dtype=np.int32,
    )
    cv2.fillPoly(allowed, [contour_guard], 255)
    foreground = cv2.bitwise_and(foreground, allowed)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(foreground, 8)
    if count > 1:
        largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        foreground = np.where(labels == largest, 255, 0).astype(np.uint8)
    foreground = cv2.erode(foreground, np.ones((3, 3), np.uint8), iterations=1)
    foreground = cv2.GaussianBlur(foreground, (0, 0), 0.65)
    fade_start = int(height * 0.80)
    fade_end = int(height * 0.985)
    fade = np.ones(height, dtype=np.float32)
    fade[fade_start:fade_end] = np.linspace(1.0, 0.0, fade_end - fade_start)
    fade[fade_end:] = 0.0
    alpha = (foreground.astype(np.float32) * fade[:, None]).astype(np.uint8)

    original_rgb = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2RGB)
    subject = Image.fromarray(np.dstack((original_rgb, alpha)), "RGBA")

    # Aura sits behind the unchanged photograph. Its broad blur prevents a
    # traceable gold edge; a vertical weight favours crown over shoulders.
    alpha_image = Image.fromarray(alpha, "L")
    broad = alpha_image.filter(ImageFilter.GaussianBlur(24))
    outside_broad = np.maximum(
        np.asarray(broad, dtype=np.int16) - np.asarray(alpha_image, dtype=np.int16), 0
    ).astype(np.float32)
    vertical = np.linspace(1.0, 0.14, height, dtype=np.float32)[:, None]
    aura_alpha = np.clip(outside_broad * 0.13 * vertical, 0, 15).astype(np.uint8)
    aura = Image.new("RGBA", (width, height), (184, 126, 48, 0))
    aura.putalpha(Image.fromarray(aura_alpha, "L"))

    result = Image.alpha_composite(aura, subject)
    result.save(OUTPUT, optimize=True)
    print(f"wrote {OUTPUT} ({width}x{height})")


if __name__ == "__main__":
    main()
