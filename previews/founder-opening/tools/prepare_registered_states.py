from pathlib import Path

from PIL import Image, ImageChops, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = 2048


def registered_menon() -> None:
    source = Image.open(ASSETS / "balakrishna-menon-4k-final.png").convert("RGBA")
    scale = 0.55
    resized = source.resize(
        (round(source.width * scale), round(source.height * scale)),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (SIZE, SIZE))
    x = (SIZE - resized.width) // 2
    canvas.alpha_composite(resized, (x, -100))
    canvas.save(ASSETS / "menon-state-2048.png", optimize=True)


def registered_gurudev() -> None:
    source = Image.open(ASSETS / "gurudev-reveal-registered-v1.png").convert("RGBA")
    red, green, blue, alpha = source.split()

    # Remove the low-opacity generated halo while retaining a clean photographic edge.
    solid = alpha.point(lambda value: 255 if value >= 185 else 0)
    solid = solid.filter(ImageFilter.GaussianBlur(1.15))
    alpha = ImageChops.multiply(alpha, solid)

    pixels = source.load()
    alpha_pixels = alpha.load()
    for y in range(min(570, source.height)):
        for x in range(source.width):
            r, g, b, _ = pixels[x, y]
            warm = r > 150 and r > g * 1.08 and g > b * 1.08
            tilak = 470 <= x <= 770 and 175 <= y <= 365
            if warm and not tilak:
                alpha_pixels[x, y] = 0

    source.putalpha(alpha)

    # Keep the photograph archival; retain only a restrained warmth in the robe.
    grayscale = source.convert("L").convert("RGB")
    colour = source.convert("RGB")
    restrained = Image.blend(grayscale, colour, 0.16).convert("RGBA")
    restrained.putalpha(source.getchannel("A"))
    restrained = restrained.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    restrained.save(ASSETS / "gurudev-state-2048.png", optimize=True)


if __name__ == "__main__":
    registered_menon()
    registered_gurudev()
