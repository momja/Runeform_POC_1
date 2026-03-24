"""Mocked photo library — stands in for Immich + CLIP retrieval.

In production:
  - Index: fetch thumbnails from Immich album, run through CLIP, store embeddings
  - Retrieve: embed the event description, cosine similarity, return top-K
  - Render: fetch full-res by asset ID at render time

For the PoC we generate colored placeholder images and return them as candidates.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import PhotoCandidate

SAMPLE_DIR = Path(__file__).parent.parent / "sample_photos"


def _ensure_sample_photos() -> list[Path]:
    """Generate placeholder 'photos' if they don't exist."""
    SAMPLE_DIR.mkdir(exist_ok=True)

    samples = [
        ("workshop_woodworking", (62, 100, 58), "Woodworking\nWorkshop"),
        ("maker_electronics", (45, 72, 110), "Electronics\nLab"),
        ("studio_yoga", (130, 90, 60), "Yoga\nStudio"),
        ("community_event", (100, 55, 90), "Community\nGathering"),
        ("outdoor_nature", (50, 110, 70), "Outdoor\nSession"),
        ("art_painting", (120, 75, 45), "Art\nClass"),
    ]

    paths = []
    for name, color, label in samples:
        path = SAMPLE_DIR / f"{name}.png"
        if not path.exists():
            img = Image.new("RGB", (800, 800), color)
            draw = ImageDraw.Draw(img)
            # Add some visual texture — concentric rectangles
            for i in range(5):
                inset = 40 + i * 60
                lighter = tuple(min(255, c + 15 * (i + 1)) for c in color)
                draw.rectangle(
                    [inset, inset, 800 - inset, 800 - inset],
                    outline=lighter, width=3,
                )
            draw.multiline_text(
                (400, 400), label,
                fill=(255, 255, 255, 200), anchor="mm", align="center",
            )
            # Diagonal label
            draw.text((20, 20), f"[mock] {name}", fill=(255, 255, 255, 128))
            img.save(path)
        paths.append(path)
    return paths


def retrieve_photos(event_description: str, top_k: int = 3) -> list[PhotoCandidate]:
    """Mock CLIP retrieval — returns placeholder photo candidates.

    In production this would:
      1. Embed event_description with CLIP
      2. Query ChromaDB/numpy for nearest neighbors
      3. Return asset IDs + similarity scores
    """
    paths = _ensure_sample_photos()

    # Mock scoring based on simple keyword overlap
    keywords = set(event_description.lower().split())
    candidates = []
    for path in paths:
        stem = path.stem.lower()
        stem_words = set(stem.split("_"))
        overlap = len(keywords & stem_words)
        score = 0.5 + overlap * 0.15  # base score + keyword bonus
        candidates.append(PhotoCandidate(
            asset_id=path.stem,
            score=min(score, 1.0),
            label=path.stem.replace("_", " ").title(),
            path=path,
        ))

    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:top_k]
