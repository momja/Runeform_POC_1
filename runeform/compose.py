from .models import (
    Archetype, ComposedLayout, ContentItem, ElementType,
    PhotoCandidate, Placement,
)


def build_content_items(
    title: str,
    subtitle: str | None = None,
    body: str | None = None,
    photo: PhotoCandidate | None = None,
    logo: PhotoCandidate | None = None,
) -> list[ContentItem]:
    """Build content items from event data."""
    items = [
        ContentItem(
            element_type=ElementType.HEADLINE,
            text=title.upper(),
            color=(210, 70, 70),
        ),
    ]

    if logo:
        items.append(ContentItem(
            element_type=ElementType.LOGO,
            photo=logo,
            color=(60, 110, 200),
        ))
    else:
        items.append(ContentItem(
            element_type=ElementType.LOGO,
            text="LOGO",
            color=(60, 110, 200),
        ))

    if subtitle:
        items.append(ContentItem(
            element_type=ElementType.SUBHEAD,
            text=subtitle,
            color=(180, 120, 50),
        ))

    if body:
        items.append(ContentItem(
            element_type=ElementType.BODY,
            text=body,
            color=(100, 100, 100),
        ))

    if photo:
        items.append(ContentItem(
            element_type=ElementType.HERO,
            photo=photo,
            color=(80, 160, 90),
        ))

    return items


def compose(
    archetypes: list[Archetype],
    content_items: list[ContentItem],
) -> list[ComposedLayout]:
    """Place content items into archetype zones by matching element types."""
    content_by_type: dict[ElementType, ContentItem] = {}
    for item in content_items:
        content_by_type[item.element_type] = item

    layouts = []
    for arch in archetypes:
        placements = []
        for zone in arch.zones:
            for allowed in zone.allowed_elements:
                if allowed in content_by_type:
                    placements.append(Placement(
                        zone=zone,
                        content=content_by_type[allowed],
                    ))
                    break
        layouts.append(ComposedLayout(archetype=arch, placements=placements))

    return layouts
