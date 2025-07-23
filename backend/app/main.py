# backend/main.py

import json
import re
from pathlib import Path
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn

import anthropic  # Anthropic SDK

# import our helper modules
from scraper import scrape_website
from filter_css import filter_css_from_html_and_css
from recreate_site import (
    build_summary_and_minimal_html,
    build_critical_css,
    format_prompt
)
from inline_css import inline_css
from section_processor import SectionProcessor


app = FastAPI(
    title="Orchids Challenge API",
    description="Backend with a /generate endpoint that reuses scraper, filter_css, recreate_site, inline_css",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # For local development; tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class URLSubmit(BaseModel):
    url: HttpUrl


@app.post("/generate")
async def generate(payload: URLSubmit):
    """
    Section-based website cloning:
    1) Scrape the given URL (full HTML + raw CSS)
    2) Detect and extract different sections (header, main content, sidebar, footer, etc.)
    3) Process each section separately with Claude AI
    4) Combine all sections back into a complete website
    5) Return JSON with combined result and individual sections
    """
    url = str(payload.url)

    # ─── 1) Scrape ─────────────────────────────
    try:
        context = await scrape_website(url)
    except Exception as e:
        print("Exception in /generate:", e)
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Scraping failed: {e}")

    context_dict = context.model_dump()  # dict with keys: title, images, summary, css_contents, html, …

    # Create "generated" folder if not already present
    gen_dir = Path("generated")
    gen_dir.mkdir(exist_ok=True)

    # ─── 2) Save raw context.json ─────────────────────────────
    Path(gen_dir / "context.json").write_text(
        json.dumps(context_dict, indent=2, default=str)
    )

    # ─── 3) Use conservative approach to preserve original structure ─────────────────────────────
    full_html = context_dict.get("html", "")
    raw_css = context_dict.get("css_contents", "")
    
    processor = SectionProcessor()
    
    # Use conservative approach by default - process entire site as one piece
    result = processor.process_entire_site_conservatively(full_html, raw_css, url)
    
    # Save the result
    Path(gen_dir / "recreated_combined.html").write_text(result["combined_html"])
    
    # ─── 4) Return JSON for your React frontend ─────────────────────────────
    return {
        "combined_html": result["combined_html"],
        "sections": result["sections"],
        "section_count": len(result["sections"]),
        "method": "conservative"
    }


async def _fallback_generate(context_dict: dict, gen_dir: Path):
    """Fallback to original method if section detection fails"""
    # ─── 3) Filter CSS ─────────────────────────────
    full_html = context_dict.get("html", "")
    raw_css = context_dict.get("css_contents", "")
    filtered_css = filter_css_from_html_and_css(full_html, raw_css)

    # ─── 4) Build summary + minimal HTML snippet ─────────────────────────────
    summary_json_obj, minimal_html = build_summary_and_minimal_html(context_dict)

    # ─── 5) Build critical CSS from filtered CSS ─────────────────────────────
    critical_css = build_critical_css(filtered_css)

    # ─── 6) Format prompt for Claude ─────────────────────────────
    prompt = format_prompt(summary_json_obj, minimal_html, critical_css)

    # ─── 7) Send prompt to Claude ─────────────────────────────
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )

    # ─── 8) Extract raw Claude output, then pull out HTML/CSS fences ─────────────────────────────
    raw_output = "".join(part.text for part in response.content if hasattr(part, "text"))

    def extract_code(block_type: str, text: str) -> str:
        fence_pattern = rf"```{block_type}\s*(.*?)\s*```"
        match = re.search(fence_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        if block_type == "css":
            start_pattern = r"```css\s*(.*)$"
            match2 = re.search(start_pattern, text, re.DOTALL)
            if match2:
                return match2.group(1).strip()
        return ""

    html_generated = extract_code("html", raw_output)
    css_generated = extract_code("css", raw_output)

    # ─── 9) Inline CSS into the generated HTML ─────────────────────────────
    combined_html = inline_css(html_generated, css_generated)

    # Write files into "generated/"
    Path(gen_dir / "recreated_page.html").write_text(html_generated)
    Path(gen_dir / "styles.css").write_text(css_generated)
    Path(gen_dir / "recreated_combined.html").write_text(combined_html)

    # ─── 10) Return JSON for your React frontend ─────────────────────────────
    return {
        "combined_html": combined_html,
        "html": html_generated,
        "css": css_generated,
        "method": "fallback"
    }


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI backend!", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchids-challenge-api"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
