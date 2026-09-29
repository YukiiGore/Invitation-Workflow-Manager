"""Generate assets/icon.ico.

Run from the project root:

    python tools/make_icon.py

The icon is drawn at 4x and downsampled so the rounded corners and the
envelope edges stay smooth at 16px.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

SUPERSAMPLE = 4
BASE_SIZE = 256
SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

ACCENT_TOP = (143, 114, 255)
ACCENT_BOTTOM = (106, 76, 224)
WHITE = (255, 255, 255)
HEART = (255, 138, 180)
FOLDER_TAB = (255, 255, 255, 90)


def _vertical_gradient(size: int) -> Image.Image:
    gradient = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(gradient)

    for y in range(size):
        ratio = y / max(size - 1, 1)
        colour = tuple(
            round(ACCENT_TOP[i] + (ACCENT_BOTTOM[i] - ACCENT_TOP[i]) * ratio)
            for i in range(3)
        )
        draw.line([(0, y), (size, y)], fill=colour + (255,))

    return gradient


def _draw_envelope(draw: ImageDraw.ImageDraw, s: int) -> None:
    """Draw a white invitation envelope on an s x s canvas."""
    left, top = round(0.16 * s), round(0.30 * s)
    right, bottom = round(0.84 * s), round(0.74 * s)
    width = max(round(0.035 * s), 2)
    radius = round(0.04 * s)

    # body
    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=radius,
        fill=WHITE + (255,),
        outline=None,
    )

    # flap: two diagonals from the top corners meeting at mid-height
    flap_y = top + round((bottom - top) * 0.52)
    draw.line(
        [(left, top), ((left + right) // 2, flap_y), (right, top)],
        fill=(106, 76, 224, 255),
        width=width,
        joint="curve",
    )

    # a small heart centred on the flap
    cx, cy = (left + right) // 2, flap_y
    r = round(0.075 * s)
    draw.ellipse((cx - r, cy - r, cx, cy), fill=HEART + (255,))
    draw.ellipse((cx, cy - r, cx + r, cy), fill=HEART + (255,))
    draw.polygon(
        [
            (cx - r, cy - round(0.15 * r)),
            (cx + r, cy - round(0.15 * r)),
            (cx, cy + round(1.5 * r)),
        ],
        fill=HEART + (255,),
    )


def build_icon() -> Image.Image:
    s = BASE_SIZE * SUPERSAMPLE

    icon = _vertical_gradient(s)

    # rounded-corner mask
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, s - 1, s - 1),
        radius=round(0.22 * s),
        fill=255,
    )
    icon.putalpha(mask)

    _draw_envelope(ImageDraw.Draw(icon), s)

    return icon.resize((BASE_SIZE, BASE_SIZE), Image.LANCZOS)


def main() -> int:
    target = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
    target.parent.mkdir(parents=True, exist_ok=True)

    icon = build_icon()
    icon.save(target, format="ICO", sizes=SIZES)

    print(f"wrote {target}")
    print(f"sizes: {', '.join(str(w) for w, _ in SIZES)}")

    preview = target.with_suffix(".png")
    icon.save(preview)
    print(f"preview: {preview}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
