#!/usr/bin/env python3
"""Render the temporary CIRS campus-construction intro from supplied stills."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent
MEDIA = ROOT / "media"
WIRE_PATH = MEDIA / "campus-wireframe.png"
FINAL_PATH = MEDIA / "campus-final.png"
FPS = 30
DURATION = 6.2
DESKTOP_SIZE = (1672, 940)
MOBILE_SIZE = (720, 1280)


def smoothstep(value: float | np.ndarray) -> float | np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def cover(frame: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    width, height = size
    source_height, source_width = frame.shape[:2]
    scale = max(width / source_width, height / source_height)
    resized = cv2.resize(
        frame,
        (round(source_width * scale), round(source_height * scale)),
        interpolation=cv2.INTER_LANCZOS4,
    )
    x = (resized.shape[1] - width) // 2
    y = (resized.shape[0] - height) // 2
    return resized[y : y + height, x : x + width]


def camera(frame: np.ndarray, scale: float, background: np.ndarray) -> np.ndarray:
    if abs(scale - 1.0) < 0.0001:
        return frame
    height, width = frame.shape[:2]
    resized = cv2.resize(
        frame,
        (round(width * scale), round(height * scale)),
        interpolation=cv2.INTER_LANCZOS4,
    )
    result = background.copy()
    x = (width - resized.shape[1]) // 2
    y = (height - resized.shape[0]) // 2
    result[y : y + resized.shape[0], x : x + resized.shape[1]] = resized
    return result


def open_writer(path: Path, size: tuple[int, int], codec: str):
    if codec == "libx264":
        params = [
            "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-an",
        ]
    else:
        params = [
            "-deadline", "good", "-cpu-used", "4", "-crf", "32", "-b:v", "0",
            "-pix_fmt", "yuv420p", "-an",
        ]
    writer = imageio_ffmpeg.write_frames(
        str(path), size, fps=FPS, codec=codec, pix_fmt_in="rgb24",
        output_params=params, macro_block_size=1,
    )
    writer.send(None)
    return writer


def main() -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    wire = np.asarray(Image.open(WIRE_PATH).convert("RGB"))[:940]
    final = np.asarray(Image.open(FINAL_PATH).convert("RGB"))[:940]
    if wire.shape != final.shape or wire.shape[1::-1] != DESKTOP_SIZE:
        raise ValueError(f"Expected matching 1672x940 inputs, got {wire.shape} and {final.shape}")

    height, width = wire.shape[:2]
    ivory = np.full_like(wire, (250, 249, 243))
    gold = np.array((201, 169, 97), dtype=np.float32)

    gray = cv2.cvtColor(wire, cv2.COLOR_RGB2GRAY)
    line_alpha = np.clip((238.0 - gray.astype(np.float32)) / 120.0, 0.0, 1.0)
    line_alpha = cv2.GaussianBlur(line_alpha, (0, 0), 0.55)
    glow_alpha = cv2.GaussianBlur(line_alpha, (0, 0), 5.0)

    yy, xx = np.mgrid[0:height, 0:width]
    centre_x, centre_y = width * 0.50, height * 0.62
    distance = np.sqrt(((xx - centre_x) / (width * 0.72)) ** 2 + ((yy - centre_y) / (height * 0.88)) ** 2)
    distance = np.clip(distance, 0.0, 1.0)

    outputs = {
        "desktop_mp4": open_writer(MEDIA / "cirs-campus-intro.mp4", DESKTOP_SIZE, "libx264"),
        "desktop_webm": open_writer(MEDIA / "cirs-campus-intro.webm", DESKTOP_SIZE, "libvpx-vp9"),
        "mobile_mp4": open_writer(MEDIA / "cirs-campus-intro-mobile.mp4", MOBILE_SIZE, "libx264"),
        "mobile_webm": open_writer(MEDIA / "cirs-campus-intro-mobile.webm", MOBILE_SIZE, "libvpx-vp9"),
    }

    frame_count = round(DURATION * FPS)
    first_frame = None
    for index in range(frame_count):
        t = index / FPS
        frame = ivory.astype(np.float32)

        # One deliberate construction mark grows across the campus centre.
        if 0.38 <= t < 1.15:
            progress = smoothstep((t - 0.38) / 0.77)
            mark = ivory.copy()
            start = (round(width * 0.465), round(height * 0.62))
            end = (round(width * (0.465 + 0.07 * progress)), round(height * 0.62))
            cv2.line(mark, start, end, (201, 169, 97), 2, cv2.LINE_AA)
            frame = mark.astype(np.float32)

        # The actual supplied architectural drawing resolves from the core out.
        if t >= 0.72:
            reveal_progress = smoothstep((t - 0.72) / 1.68)
            reveal = smoothstep((reveal_progress * 1.22 - distance + 0.05) * 6.0)
            structural_alpha = np.clip(line_alpha * reveal * 1.35, 0.0, 1.0)
            structural = ivory.astype(np.float32) * (1.0 - structural_alpha[..., None])
            structural += gold * structural_alpha[..., None]
            background_alpha = reveal[..., None] * smoothstep((t - 1.20) / 1.20) * 0.82
            structural = structural * (1.0 - background_alpha) + wire.astype(np.float32) * background_alpha
            frame = structural

            # A finite gold illumination ring travels through the linework.
            ring_radius = np.clip((t - 1.25) / 1.95, 0.0, 1.0) * 1.05
            ring = np.exp(-((distance - ring_radius) ** 2) / 0.0028)
            light = np.clip((ring * line_alpha + glow_alpha * ring * 0.45), 0.0, 1.0)
            frame = frame * (1.0 - light[..., None] * 0.48) + np.array((216, 188, 122)) * light[..., None] * 0.48

        # Natural colour grows outward from the central school blocks.
        if t >= 2.78:
            colour_progress = smoothstep((t - 2.78) / 1.70)
            colour_mask = smoothstep((colour_progress * 1.28 - distance + 0.06) * 5.0)
            frame = frame * (1.0 - colour_mask[..., None]) + final.astype(np.float32) * colour_mask[..., None]

        # Remove the last trace of the drawing and settle on the exact live frame.
        if t >= 4.22:
            settle = smoothstep((t - 4.22) / 0.98)
            frame = frame * (1.0 - settle) + final.astype(np.float32) * settle

        frame = np.clip(frame, 0, 255).astype(np.uint8)
        if t < 5.20:
            scale = 0.92 + 0.08 * smoothstep((t - 0.42) / 4.78)
            frame = camera(frame, scale, ivory)
        else:
            frame = final.copy()  # A full second of exact final-frame hold.

        if first_frame is None:
            first_frame = frame.copy()
        mobile = np.ascontiguousarray(cover(frame, MOBILE_SIZE))
        desktop = np.ascontiguousarray(frame)
        outputs["desktop_mp4"].send(desktop)
        outputs["desktop_webm"].send(desktop)
        outputs["mobile_mp4"].send(mobile)
        outputs["mobile_webm"].send(mobile)

    for writer in outputs.values():
        writer.close()

    Image.fromarray(first_frame).save(MEDIA / "intro-poster.jpg", quality=92)
    Image.fromarray(final).save(MEDIA / "final-frame.png", optimize=True)
    metadata = {
        "duration_seconds": DURATION,
        "fps": FPS,
        "frames": frame_count,
        "desktop_dimensions": list(DESKTOP_SIZE),
        "mobile_dimensions": list(MOBILE_SIZE),
        "handoff_hold_starts_seconds": 5.2,
        "sources": [WIRE_PATH.name, FINAL_PATH.name],
    }
    for path in sorted(MEDIA.glob("cirs-campus-intro*")):
        metadata[path.name] = {"bytes": path.stat().st_size}
    (MEDIA / "render-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
