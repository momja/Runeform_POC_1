import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from .models import EventData, ExtractedImage

DOWNLOADS_DIR = Path(__file__).parent.parent / "downloaded_images"


def parse_event_text(text: str) -> EventData:
    """Parse free-form event text into structured EventData.

    Simple keyword extraction — good enough for the text input box.
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]

    title = lines[0] if lines else "Untitled Event"

    date = None
    time = None
    location = None
    description_parts: list[str] = []

    date_keywords = {"monday", "tuesday", "wednesday", "thursday", "friday",
                     "saturday", "sunday", "jan", "feb", "mar", "apr", "may",
                     "jun", "jul", "aug", "sep", "oct", "nov", "dec"}
    time_keywords = {"am", "pm", "noon", "midnight"}
    location_keywords = {"at", "venue", "studio", "space", "room", "hall",
                         "theater", "theatre", "park", "outdoor"}

    for line in lines[1:]:
        lower = line.lower()
        words = set(lower.split())

        if not date and words & date_keywords:
            date = line
        elif not time and words & time_keywords:
            time = line
        elif not location and words & location_keywords:
            location = line
        else:
            description_parts.append(line)

    return EventData(
        title=title,
        date=date,
        time=time,
        location=location,
        description="\n".join(description_parts) if description_parts else None,
    )


def _fetch_page(url: str) -> tuple[str, str]:
    """Fetch page HTML. Returns (html, final_url) after redirects."""
    resp = httpx.get(url, follow_redirects=True, timeout=15)
    resp.raise_for_status()
    return resp.text, str(resp.url)


def _extract_page_content(html: str, base_url: str) -> tuple[str, list[dict]]:
    """Extract readable text and image metadata from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup.find_all(["script", "style", "nav", "footer", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    # Truncate to avoid blowing up the Claude context
    if len(text) > 6000:
        text = text[:6000] + "\n[truncated]"

    # Collect images
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or src.startswith("data:"):
            continue
        abs_url = urljoin(base_url, src)
        images.append({
            "url": abs_url,
            "alt": img.get("alt", ""),
            "classes": " ".join(img.get("class", [])),
            "width": img.get("width", ""),
            "height": img.get("height", ""),
        })

    # Also check for og:image meta tags
    for meta in soup.find_all("meta", property="og:image"):
        content = meta.get("content", "")
        if content:
            abs_url = urljoin(base_url, content)
            if not any(i["url"] == abs_url for i in images):
                images.append({
                    "url": abs_url,
                    "alt": "og:image",
                    "classes": "",
                    "width": "",
                    "height": "",
                })

    return text, images


def _claude_extract(page_text: str, images: list[dict], url: str) -> dict:
    """Send page content to Claude for structured event extraction."""
    import anthropic

    client = anthropic.Anthropic()

    image_summary = "\n".join(
        f"  [{i+1}] url={img['url']}  alt=\"{img['alt']}\"  classes=\"{img['classes']}\""
        for i, img in enumerate(images[:30])  # cap at 30 images
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": f"""Extract event information from this web page.

URL: {url}

PAGE TEXT:
{page_text}

IMAGES FOUND ON PAGE:
{image_summary if image_summary else "(none)"}

Return ONLY valid JSON with this structure:
{{
  "title": "event title",
  "date": "date string or null",
  "time": "time string or null",
  "location": "venue/location or null",
  "description": "brief description of the event or null",
  "category": "one of: workshop, class, performance, social, market, talk, other",
  "images": [
    {{"index": 1, "role": "hero or logo", "reason": "why this image"}}
  ]
}}

For images, identify:
- "logo": venue/organization logos, brand marks
- "hero": main event photos, featured images, banners — NOT icons, avatars, or tiny UI elements

Only include images that are actually useful for a marketing graphic. Skip tracking pixels, icons, social media badges, and decorative UI elements. If unsure, skip it."""}],
    )

    text = response.content[0].text.strip()
    return json.loads(text[text.find("{"):text.rfind("}") + 1])


def _download_image(url: str) -> Path | None:
    """Download an image to local storage. Returns path or None on failure."""
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    # Deterministic filename from URL
    ext = Path(url.split("?")[0]).suffix or ".jpg"
    name = hashlib.sha256(url.encode()).hexdigest()[:16] + ext
    path = DOWNLOADS_DIR / name
    if path.exists():
        return path
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type and not path.suffix:
            return None
        path.write_bytes(resp.content)
        return path
    except Exception:
        return None


def parse_event_url(url: str) -> EventData:
    """Fetch a URL, extract event data and images using Claude."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return EventData(
            title="Community Event",
            description=f"(No API key — could not parse {url})",
            category="general",
        )

    html, final_url = _fetch_page(url)
    page_text, page_images = _extract_page_content(html, final_url)
    extracted = _claude_extract(page_text, page_images, final_url)

    # Build extracted images list, downloading each
    images: list[ExtractedImage] = []
    for img_ref in extracted.get("images", []):
        idx = img_ref.get("index", 0) - 1
        if 0 <= idx < len(page_images):
            img_url = page_images[idx]["url"]
            local_path = _download_image(img_url)
            images.append(ExtractedImage(
                url=img_url,
                role=img_ref.get("role", "unknown"),
                alt=page_images[idx].get("alt", ""),
                path=local_path,
            ))

    return EventData(
        title=extracted.get("title", "Untitled Event"),
        date=extracted.get("date"),
        time=extracted.get("time"),
        location=extracted.get("location"),
        description=extracted.get("description"),
        category=extracted.get("category", "other"),
        images=images,
    )
