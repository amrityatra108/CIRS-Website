"""Place the supplied Swami Chinmayananda cutout on the square stage.

The PNG master stays under assets/source; tools/make-media.py cuts the live
WebP texture from it, preserving the silhouette's alpha channel.
"""

from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "source" / "founder-opening"
SIZE = 2048
TARGET_EYE_MID = (1024.0, 460.0)
TARGET_EYE_SPAN = 190.0

PORTRAITS = {
    "swami-chinmayananda": {
        "source": "swami-chinmayananda-cutout.png",
        "eyes": ((415.0, 306.0), (541.0, 287.0)),
    },
}


for name, info in PORTRAITS.items():
    source = cv2.imread(str(ASSETS / info["source"]), cv2.IMREAD_UNCHANGED)
    if source is None or source.shape[2] != 4:
        raise ValueError(f"Expected a transparent RGBA PNG: {info['source']}")
    (lx, ly), (rx, ry) = info["eyes"]
    midpoint = ((lx + rx) / 2, (ly + ry) / 2)
    span = np.hypot(rx - lx, ry - ly)
    angle = np.degrees(np.arctan2(ry - ly, rx - lx))
    transform = cv2.getRotationMatrix2D(midpoint, angle, TARGET_EYE_SPAN / span)
    transform[0, 2] += TARGET_EYE_MID[0] - midpoint[0]
    transform[1, 2] += TARGET_EYE_MID[1] - midpoint[1]
    result = cv2.warpAffine(
        source, transform, (SIZE, SIZE), flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0),
    )
    # Fade only the lower book edge into the paper; the supplied matte is kept.
    fade = np.ones(SIZE, np.float32)
    fade[1900:2048] = np.linspace(1.0, 0.0, 148)
    result[:, :, 3] = np.asarray(result[:, :, 3] * fade[:, None], dtype=np.uint8)
    destination = ASSETS / f"{name}-registered.png"
    cv2.imwrite(str(destination), result)
    print(name, source.shape[:2], "->", destination.name, destination.stat().st_size)
