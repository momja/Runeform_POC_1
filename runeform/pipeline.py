"""End-to-end generation pipeline.

1. Parse event data
2. Retrieve photo candidates from library
3. For each photo candidate × archetype: compose layout
4. Score with heuristics, filter weak ones
5. Filter by non-repetition history
6. Rank survivors with Claude (or heuristic fallback)
7. Return top results
"""

from pathlib import Path

from .archetypes import ARCHETYPES
from .compose import build_content_items, compose
from .history import filter_by_history, record_usage
from .intake import parse_event_text, parse_event_url
from .models import EventData, GenerationResult, PhotoCandidate
from .photos import retrieve_photos
from .ranking import rank
from .render import render_all
from .scoring import filter_and_score

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def generate(
    event_text: str | None = None,
    event_url: str | None = None,
    venue_id: str = "default",
    event_category: str = "general",
    top_k_photos: int = 2,
) -> GenerationResult:
    """Run the full generation pipeline."""

    # 1. Parse event data
    if event_url:
        event = parse_event_url(event_url)
    elif event_text:
        event = parse_event_text(event_text)
    else:
        raise ValueError("Provide event_text or event_url")

    if not event.category:
        event.category = event_category

    event_context = _build_context(event)

    # 2. Extract images from URL parsing, or retrieve from photo library
    logo_candidate: PhotoCandidate | None = None
    hero_candidates: list[PhotoCandidate] = []

    # Use images extracted from the page if available
    for img in event.images:
        if img.path and img.path.exists():
            candidate = PhotoCandidate(
                asset_id=img.url,
                score=0.9,
                label=img.alt or img.role,
                path=img.path,
            )
            if img.role == "logo" and not logo_candidate:
                logo_candidate = candidate
            elif img.role == "hero":
                hero_candidates.append(candidate)

    # Fall back to photo library if no hero images extracted
    if not hero_candidates:
        hero_candidates = retrieve_photos(event_context, top_k=top_k_photos)

    # 3. Compose: each photo × each archetype
    all_layouts = []
    for photo in hero_candidates:
        subtitle_parts = []
        if event.date:
            subtitle_parts.append(event.date)
        if event.time:
            subtitle_parts.append(event.time)
        if event.location:
            subtitle_parts.append(event.location)

        content_items = build_content_items(
            title=event.title,
            subtitle=" | ".join(subtitle_parts) if subtitle_parts else None,
            body=event.description,
            photo=photo,
            logo=logo_candidate,
        )
        layouts = compose(ARCHETYPES, content_items)
        all_layouts.extend(layouts)

    # 4. Heuristic scoring + filter
    scored = filter_and_score(all_layouts, min_score=0.2)

    # 5. Non-repetition filter
    filtered = filter_by_history(scored, venue_id, event_category)

    # 6. Render
    paths = render_all(filtered, OUTPUT_DIR)

    # 7. Rank
    best_i, reasoning = rank(paths, filtered, event_context)

    # Record usage for winner
    record_usage(filtered[best_i], venue_id, event_category)

    return GenerationResult(
        layouts=filtered,
        rendered_paths=paths,
        best_index=best_i,
        reasoning=reasoning,
    )


def _build_context(event: EventData) -> str:
    """Build a text description for photo retrieval and ranking."""
    parts = [event.title]
    if event.date:
        parts.append(f"Date: {event.date}")
    if event.time:
        parts.append(f"Time: {event.time}")
    if event.location:
        parts.append(f"Location: {event.location}")
    if event.description:
        parts.append(event.description)
    if event.category:
        parts.append(f"Category: {event.category}")
    return " | ".join(parts)
