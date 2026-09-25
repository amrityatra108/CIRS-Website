"""Export the approved transparent portrait layers at matching 4K height."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]

PORTRAITS = (
    (ROOT / "assets" / "balakrishna-final-source.png", ROOT / "assets" / "balakrishna-menon-4k-final.png"),
    (ROOT / "assets" / "gurudev-final-source.png", ROOT / "assets" / "gurudev-4k-final.png"),
)


def clean(source: Path, destination: Path) -> None:
    cleaned = Image.open(source).convert("RGBA")
    target_height = 4096
    target_width = round(cleaned.width * target_height / cleaned.height)
    cleaned = cleaned.resize((target_width, target_height), Image.Resampling.LANCZOS)
    cleaned.save(destination, optimize=True)
    print(f"wrote {destination.name}: {cleaned.width}x{cleaned.height}")


def main() -> None:
    for source, destination in PORTRAITS:
        clean(source, destination)


if __name__ == "__main__":
    main()
