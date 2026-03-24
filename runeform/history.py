"""Non-repetition history — tracks which archetype+photo combos have been used.

Per-venue, per-event-category tracking. Previously used combinations are
deprioritized in subsequent generations.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import ComposedLayout, UsageRecord

HISTORY_FILE = Path(__file__).parent.parent / "usage_history.json"


def _load_history() -> list[UsageRecord]:
    if not HISTORY_FILE.exists():
        return []
    data = json.loads(HISTORY_FILE.read_text())
    return [UsageRecord(**r) for r in data]


def _save_history(records: list[UsageRecord]):
    HISTORY_FILE.write_text(
        json.dumps([r.model_dump() for r in records], indent=2)
    )


def get_used_combinations(
    venue_id: str,
    event_category: str,
) -> set[tuple[str, str | None]]:
    """Return set of (archetype_name, photo_asset_id) previously used."""
    records = _load_history()
    return {
        (r.archetype_name, r.photo_asset_id)
        for r in records
        if r.venue_id == venue_id and r.event_category == event_category
    }


def filter_by_history(
    layouts: list[ComposedLayout],
    venue_id: str,
    event_category: str,
) -> list[ComposedLayout]:
    """Deprioritize previously used archetype+photo combinations.

    Moves used combos to the end rather than removing them entirely,
    so there's always something to return.
    """
    used = get_used_combinations(venue_id, event_category)
    if not used:
        return layouts

    def _combo_key(layout: ComposedLayout) -> tuple[str, str | None]:
        photo_id = None
        for p in layout.placements:
            if p.content.photo:
                photo_id = p.content.photo.asset_id
                break
        return (layout.archetype.name, photo_id)

    fresh = [l for l in layouts if _combo_key(l) not in used]
    stale = [l for l in layouts if _combo_key(l) in used]
    return fresh + stale


def record_usage(
    layout: ComposedLayout,
    venue_id: str,
    event_category: str,
):
    """Record that this archetype+photo combo was used."""
    photo_id = None
    for p in layout.placements:
        if p.content.photo:
            photo_id = p.content.photo.asset_id
            break

    record = UsageRecord(
        venue_id=venue_id,
        event_category=event_category,
        archetype_name=layout.archetype.name,
        photo_asset_id=photo_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    records = _load_history()
    records.append(record)
    _save_history(records)
