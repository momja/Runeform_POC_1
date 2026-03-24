"""Runeform web server — dead simple intake form."""

import shutil
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from runeform.pipeline import generate, OUTPUT_DIR

app = FastAPI(title="Runeform")

# Serve rendered output images
OUTPUT_DIR.mkdir(exist_ok=True)
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

HTML_FORM = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Runeform</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #f8f4ee;
    color: #333;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 60px 20px;
  }
  h1 { font-size: 2rem; margin-bottom: 8px; letter-spacing: -0.02em; }
  .subtitle { color: #888; margin-bottom: 40px; font-size: 0.95rem; }
  form {
    background: white;
    border-radius: 12px;
    padding: 32px;
    max-width: 520px;
    width: 100%;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  }
  label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 0.9rem; }
  .hint { color: #999; font-size: 0.8rem; margin-bottom: 12px; }
  input, textarea {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 0.95rem;
    font-family: inherit;
    margin-bottom: 20px;
  }
  textarea { resize: vertical; min-height: 100px; }
  input:focus, textarea:focus { outline: none; border-color: #666; }
  button {
    width: 100%;
    padding: 12px;
    background: #333;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }
  button:hover { background: #555; }
  .or { text-align: center; color: #bbb; margin: 0 0 20px 0; font-size: 0.85rem; }
</style>
</head>
<body>
  <h1>Runeform</h1>
  <p class="subtitle">Paste a link or describe your event. Get ready-to-post graphics.</p>
  <form method="POST" action="/generate">
    <label for="url">Event URL</label>
    <p class="hint">Paste a link to your event page</p>
    <input type="url" id="url" name="url" placeholder="https://...">
    <p class="or">&mdash; or &mdash;</p>
    <label for="text">Describe your event</label>
    <p class="hint">Title, date, time, location, any details</p>
    <textarea id="text" name="text" placeholder="Morning Flow Yoga&#10;Sunday 9 AM&#10;Serenity Woods Outdoor Studio&#10;Beginner-friendly, mats provided"></textarea>
    <button type="submit">Generate Graphics</button>
  </form>
</body>
</html>"""


def _results_html(count: int, reasoning_html: str, cards_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Runeform — Results</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #f8f4ee;
    color: #333;
    min-height: 100vh;
    padding: 40px 20px;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 4px; }}
  .back {{ color: #888; text-decoration: none; font-size: 0.85rem; }}
  .back:hover {{ text-decoration: underline; }}
  .meta {{ color: #888; margin-bottom: 30px; font-size: 0.85rem; }}
  .best-label {{
    display: inline-block;
    background: #333;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 8px;
  }}
  .reasoning {{
    background: white;
    padding: 16px 20px;
    border-radius: 8px;
    margin-bottom: 30px;
    font-size: 0.9rem;
    color: #555;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }}
  .card {{
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: transform 0.15s;
  }}
  .card:hover {{ transform: translateY(-2px); }}
  .card.winner {{ outline: 3px solid #333; box-shadow: 0 4px 20px rgba(0,0,0,0.12); }}
  .card img {{ width: 100%; display: block; }}
  .card-info {{ padding: 12px 16px; }}
  .card-info h3 {{ font-size: 0.9rem; margin-bottom: 4px; }}
  .card-info .score {{ color: #999; font-size: 0.8rem; }}
</style>
</head>
<body>
<div class="container">
  <a href="/" class="back">&larr; New generation</a>
  <h1>Generated Layouts</h1>
  <p class="meta">{count} variants generated</p>
  {reasoning_html}
  {cards_html}
</div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_FORM


@app.post("/generate", response_class=HTMLResponse)
async def do_generate(
    url: str = Form(default=""),
    text: str = Form(default=""),
):
    url = url.strip()
    text = text.strip()

    if not url and not text:
        return HTMLResponse(
            "<p>Please provide a URL or event description.</p><a href='/'>Back</a>",
            status_code=400,
        )

    result = generate(
        event_text=text or None,
        event_url=url or None,
    )

    # Build result cards
    cards = []
    for i, path in enumerate(result.rendered_paths):
        layout = result.layouts[i]
        is_best = i == result.best_index
        winner_class = " winner" if is_best else ""
        best_badge = '<span class="best-label">BEST</span>' if is_best else ""
        cards.append(f"""
        <div class="card{winner_class}">
          {best_badge}
          <img src="/output/{path.name}" alt="{layout.archetype.label}">
          <div class="card-info">
            <h3>{layout.archetype.label}</h3>
            <span class="score">Score: {layout.heuristic_score:.2f}</span>
          </div>
        </div>""")

    reasoning_html = ""
    if result.reasoning:
        reasoning_html = f'<div class="reasoning">{result.reasoning}</div>'

    html = _results_html(
        count=len(result.rendered_paths),
        reasoning_html=reasoning_html,
        cards_html="\n".join(cards),
    )
    return HTMLResponse(html)


@app.get("/best")
async def get_best():
    """Return the most recently generated best layout image."""
    best = OUTPUT_DIR / "best_layout.png"
    if best.exists():
        return FileResponse(best)
    return HTMLResponse("<p>No generation yet.</p>", status_code=404)
