from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class Rect(BaseModel):
    x: float
    y: float
    width: float
    height: float


class ElementType(str, Enum):
    HERO = "hero"
    HEADLINE = "headline"
    SUBHEAD = "subhead"
    BODY = "body"
    LOGO = "logo"
    NEGATIVE_SPACE = "negative_space"


class Zone(BaseModel):
    name: str
    bounds: Rect
    visual_weight: float = 1.0
    allowed_elements: list[ElementType]


class Archetype(BaseModel):
    name: str
    label: str
    zones: list[Zone]


class ExtractedImage(BaseModel):
    url: str
    role: Literal["logo", "hero", "unknown"] = "unknown"
    alt: str = ""
    path: Path | None = None  # local path once downloaded


class EventData(BaseModel):
    title: str
    date: str | None = None
    time: str | None = None
    location: str | None = None
    description: str | None = None
    category: str | None = None
    images: list[ExtractedImage] = []


class ImageSource(BaseModel):
    kind: Literal["immich"]
    base_url: str
    api_key: str
    album_id: str | None = None


class PhotoCandidate(BaseModel):
    asset_id: str
    score: float
    label: str
    path: Path | None = None  # local path once fetched


class ContentItem(BaseModel):
    element_type: ElementType
    text: str | None = None
    photo: PhotoCandidate | None = None
    color: tuple[int, int, int] = (100, 100, 100)


class Placement(BaseModel):
    zone: Zone
    content: ContentItem


class ComposedLayout(BaseModel):
    archetype: Archetype
    placements: list[Placement]
    heuristic_score: float = 0.0


class UsageRecord(BaseModel):
    venue_id: str
    event_category: str
    archetype_name: str
    photo_asset_id: str | None = None
    timestamp: str


class GenerationResult(BaseModel):
    layouts: list[ComposedLayout]
    rendered_paths: list[Path]
    best_index: int
    reasoning: str
