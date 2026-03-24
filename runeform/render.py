"""Render composed layouts to PNG images using Pillow.

Production target is pycairo; Pillow used for PoC simplicity.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .archetypes import CANVAS_H, CANVAS_W
from .models import ComposedLayout, ElementType

BACKGROUND = (248, 244, 238)
GRID_COLOR = (235, 231, 225)
OVERLAY_BG = (0, 0, 0, 140)  # semi-transparent for text overlays on hero


def _draw_text_fitted(
    draw: ImageDraw.ImageDraw,
    text: str,
    bounds: tuple[float, float, float, float],
    fill: tuple[int, ...] = (255, 255, 255),
    max_size: int = 48,
    min_size: int = 14,
):
    """Draw text fitted within bounds, shrinking font if needed."""
    x1, y1, x2, y2 = bounds
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    max_w = x2 - x1 - 20
    max_h = y2 - y1 - 10

    for size in range(max_size, min_size - 1, -2):
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except (OSError, IOError):
            font = ImageFont.load_default()

        bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        if tw <= max_w and th <= max_h:
            draw.multiline_text(
                (cx, cy), text, fill=fill, font=font, anchor="mm", align="center",
            )
            return

    # Fallback: draw at min size regardless
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", min_size)
    except (OSError, IOError):
        font = ImageFont.load_default()
    draw.multiline_text(
        (cx, cy), text, fill=fill, font=font, anchor="mm", align="center",
    )


def render_layout(layout: ComposedLayout, index: int, output_dir: Path) -> Path:
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), BACKGROUND)
    draw = ImageDraw.Draw(img)

    # Subtle grid
    for x in range(0, CANVAS_W, 108):
        draw.line([(x, 0), (x, CANVAS_H)], fill=GRID_COLOR, width=1)
    for y in range(0, CANVAS_H, 108):
        draw.line([(0, y), (CANVAS_W, y)], fill=GRID_COLOR, width=1)

    for placement in layout.placements:
        b = placement.zone.bounds
        x1, y1 = int(b.x), int(b.y)
        x2, y2 = int(b.x + b.width), int(b.y + b.height)

        has_photo = placement.content.photo and placement.content.photo.path and placement.content.photo.path.exists()

        if has_photo and placement.content.element_type in (ElementType.HERO, ElementType.LOGO):
            photo = Image.open(placement.content.photo.path)
            zone_w, zone_h = x2 - x1, y2 - y1
            if placement.content.element_type == ElementType.LOGO:
                # Fit logo preserving aspect ratio
                photo.thumbnail((zone_w, zone_h), Image.Resampling.LANCZOS)
                paste_x = x1 + (zone_w - photo.width) // 2
                paste_y = y1 + (zone_h - photo.height) // 2
                if photo.mode == "RGBA":
                    img.paste(photo, (paste_x, paste_y), photo)
                else:
                    img.paste(photo, (paste_x, paste_y))
            else:
                photo = photo.resize((zone_w, zone_h), Image.Resampling.LANCZOS)
                img.paste(photo, (x1, y1))
        elif placement.content.element_type == ElementType.HERO:
            draw.rectangle([x1, y1, x2, y2], fill=placement.content.color, outline=(20, 20, 20), width=2)
            _draw_text_fitted(draw, "HERO IMAGE", (x1, y1, x2, y2))
        elif placement.content.element_type in (ElementType.HEADLINE, ElementType.SUBHEAD):
            # Text elements with colored background
            draw.rectangle([x1, y1, x2, y2], fill=placement.content.color, outline=None)
            text = placement.content.text or placement.content.element_type.value.upper()
            max_size = 52 if placement.content.element_type == ElementType.HEADLINE else 28
            _draw_text_fitted(draw, text, (x1, y1, x2, y2), fill=(255, 255, 255), max_size=max_size)
        elif placement.content.element_type == ElementType.BODY:
            draw.rectangle([x1, y1, x2, y2], fill=(240, 236, 230), outline=None)
            text = placement.content.text or "Event details here"
            _draw_text_fitted(draw, text, (x1, y1, x2, y2), fill=(60, 60, 60), max_size=22, min_size=12)
        elif placement.content.element_type == ElementType.LOGO:
            draw.rectangle([x1, y1, x2, y2], fill=placement.content.color, outline=None)
            _draw_text_fitted(draw, "LOGO", (x1, y1, x2, y2), fill=(255, 255, 255), max_size=24)
        else:
            draw.rectangle([x1, y1, x2, y2], fill=placement.content.color, outline=(20, 20, 20), width=2)

    # Layout label at top
    try:
        label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except (OSError, IOError):
        label_font = ImageFont.load_default()
    label = f"#{index} {layout.archetype.label} (score: {layout.heuristic_score:.2f})"
    draw.text((12, 12), label, fill=(120, 120, 120), font=label_font)

    path = output_dir / f"layout_{index:02d}.png"
    img.save(path)
    return path


def render_all(layouts: list[ComposedLayout], output_dir: Path) -> list[Path]:
    output_dir.mkdir(exist_ok=True)
    paths = []
    for i, layout in enumerate(layouts, 1):
        path = render_layout(layout, i, output_dir)
        paths.append(path)
    return paths
