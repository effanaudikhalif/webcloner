# backend/main.py

import json
import re
from pathlib import Path
import asyncio
import os
from dotenv import load_dotenv
import logging

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
from inline_css import inline_css, extract_code_blocks, combine_html_and_css

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    1) Scrape the given URL (full HTML + raw CSS)
    2) Save raw context to generated/context.json
    3) Filter CSS to include only selectors present in HTML
    4) Build summary + minimal HTML snippet
    5) Build critical CSS from filtered CSS
    6) Format an Anthropic prompt
    7) Send prompt to Claude → receive two code fences: ```html``` + ```css```
    8) Extract those fences, inline CSS into HTML, and write generated files
    9) Return JSON { combined_html, html, css } to the caller
    """
    url = str(payload.url)
    
    logger.info(f"🚀 Starting website cloning process for URL: {url}")
    logger.info("=" * 60)

    # ─── 1) Scrape ─────────────────────────────
    logger.info("📡 Step 1: Starting website scraping...")
    try:
        logger.info(f"   → Attempting to scrape: {url}")
        context = await scrape_website(url)
        logger.info(f"   ✅ Scraping successful!")
        logger.info(f"   → Title: {context.title}")
        logger.info(f"   → Images found: {len(context.images)}")
        logger.info(f"   → CSS content length: {len(context.css_contents)} characters")
        logger.info(f"   → HTML content length: {len(context.html)} characters")
    except Exception as e:
        logger.error(f"   ❌ Exception in scraping: {e}")
        print("Exception in /generate:", e)
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Scraping failed: {e}")

    context_dict = context.model_dump()  # dict with keys: title, images, summary, css_contents, html, …

    # Create "generated" folder if not already present
    gen_dir = Path("generated")
    gen_dir.mkdir(exist_ok=True)
    logger.info(f"📁 Created/verified generated directory: {gen_dir.absolute()}")

    # ─── 2) Save raw context.json ─────────────────────────────
    logger.info("💾 Step 2: Saving raw context to context.json...")
    context_file = Path(gen_dir / "context.json")
    Path(context_file).write_text(
        json.dumps(context_dict, indent=2, default=str)
    )
    logger.info(f"   ✅ Saved context to: {context_file.absolute()}")

    # ─── 3) Filter CSS ─────────────────────────────
    logger.info("🔍 Step 3: Filtering CSS to include only HTML selectors...")
    full_html = context_dict.get("html", "")
    raw_css = context_dict.get("css_contents", "")
    logger.info(f"   → Raw CSS length: {len(raw_css)} characters")
    
    filtered_css = filter_css_from_html_and_css(full_html, raw_css)
    logger.info(f"   → Filtered CSS length: {len(filtered_css)} characters")
    logger.info(f"   → CSS reduction: {len(raw_css) - len(filtered_css)} characters removed")

    # ─── 4) Build summary + minimal HTML snippet ─────────────────────────────
    logger.info("📝 Step 4: Building summary and minimal HTML...")
    summary_json_obj, minimal_html = build_summary_and_minimal_html(context_dict)
    logger.info(f"   → Summary created: {summary_json_obj}")
    logger.info(f"   → Minimal HTML length: {len(minimal_html)} characters")

    # ─── 5) Build critical CSS from filtered CSS ─────────────────────────────
    logger.info("🎨 Step 5: Building critical CSS...")
    critical_css = build_critical_css(filtered_css)
    logger.info(f"   → Critical CSS length: {len(critical_css)} characters")

    # ─── 6) Format prompt for Claude ─────────────────────────────
    logger.info("🤖 Step 6: Formatting prompt for Claude AI...")
    prompt = format_prompt(summary_json_obj, minimal_html, critical_css)
    logger.info(f"   → Prompt length: {len(prompt)} characters")
    logger.info("   → Sending prompt to Claude...")

    # ─── 7) Send prompt to Claude ─────────────────────────────
    logger.info("🧠 Step 7: Sending request to Claude AI...")
    try:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        logger.info("   → Claude client initialized")
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )
        logger.info("   ✅ Claude response received successfully!")
        logger.info(f"   → Response length: {len(response.content[0].text)} characters")
    except Exception as e:
        logger.error(f"   ❌ Claude API error: {e}")
        raise HTTPException(status_code=500, detail=f"Claude API failed: {e}")

    # ─── 8) Extract raw Claude output, then pull out HTML/CSS fences ─────────────────────────────
    logger.info("🔧 Step 8: Extracting code blocks from Claude response...")
    raw_output = "".join(part.text for part in response.content if hasattr(part, "text"))
    logger.info(f"   → Raw output length: {len(raw_output)} characters")
    
    # Extract HTML and CSS code blocks from Claude's response
    html_generated, css_generated = extract_code_blocks(raw_output)
    logger.info(f"   → Extracted HTML length: {len(html_generated)} characters")
    logger.info(f"   → Extracted CSS length: {len(css_generated)} characters")
    
    if not html_generated:
        logger.warning("   ⚠️  No HTML code block found in Claude response!")
    if not css_generated:
        logger.warning("   ⚠️  No CSS code block found in Claude response!")

    # ─── 9) Inline CSS into the generated HTML ─────────────────────────────
    logger.info("🔗 Step 9: Inlining CSS into HTML...")
    combined_html = inline_css(html_generated, css_generated)
    logger.info(f"   → Combined HTML length: {len(combined_html)} characters")

    # Write files into "generated/"
    logger.info("💾 Step 10: Saving generated files...")
    Path(gen_dir / "recreated_page.html").write_text(html_generated)
    Path(gen_dir / "styles.css").write_text(css_generated)
    Path(gen_dir / "recreated_combined.html").write_text(combined_html)
    logger.info("   ✅ Files saved:")
    logger.info(f"      → recreated_page.html: {len(html_generated)} characters")
    logger.info(f"      → styles.css: {len(css_generated)} characters")
    logger.info(f"      → recreated_combined.html: {len(combined_html)} characters")

    # ─── 10) Return JSON for your React frontend ─────────────────────────────
    logger.info("✅ Step 11: Returning response to frontend...")
    logger.info("=" * 60)
    logger.info("🎉 Website cloning process completed successfully!")
    
    return {
        "combined_html": combined_html,
        "html": html_generated,
        "css": css_generated,
    }


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI backend!", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchids-challenge-api"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
