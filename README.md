# Runeform

Compositional layout engine for brand marketing. Zero-friction content generation for small venue operators who would otherwise post nothing.

Paste a link or describe your event. Get ready-to-post graphics.

## How it works

1. **Intake** — Submit an event URL or free-text description via web form
2. **Parse** — Claude extracts structured event data and identifies logos/photos from the page
3. **Photo retrieval** — Pulls hero images from the page, or falls back to a private photo library (Immich integration mocked for now, uses CLIP semantic search in production)
4. **Compose** — Places content into 5 layout archetypes using semantic zones (headline, hero, body, logo)
5. **Score** — Pre-LLM heuristics filter weak layouts (visual weight balance, focal hierarchy, breathing room, rule of thirds)
6. **Non-repetition** — Tracks used archetype+photo combinations per venue to prevent repeats
7. **Rank** — Claude evaluates surviving layouts and picks the best one
8. **Return** — All variants rendered as PNGs, best one highlighted

## Setup

```bash
uv sync
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

## Run

```bash
uv run uvicorn server:app --reload --port 8001
```

Open http://localhost:8001

Without `ANTHROPIC_API_KEY`, URL parsing returns a placeholder and ranking falls back to heuristic scoring. The text input and full rendering pipeline work without it.

## Project structure

```
server.py              — FastAPI web form + results page
runeform/
  models.py            — Pydantic models (Zone, Archetype, EventData, etc.)
  archetypes.py        — 5 layout archetypes with semantic zones
  intake.py            — Event parsing: Claude-powered URL extraction + text parsing
  photos.py            — Photo retrieval (mocked Immich + CLIP)
  compose.py           — Zone assignment: content items → archetype slots
  scoring.py           — Pre-LLM compositional heuristics
  render.py            — Pillow rendering with fitted text and photo placement
  ranking.py           — Claude ranking with heuristic fallback
  history.py           — Non-repetition tracking per venue/category
  pipeline.py          — End-to-end orchestration
```

## Current status

Proof of concept. Immich integration is fully mocked. Rendering uses Pillow (production target: pycairo). Five archetypes defined. URL intake uses Claude for structured extraction and image identification.

![](screenshot_1.jpg)

![](screenshot_2.jpg)
