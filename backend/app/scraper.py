import asyncio
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pydantic import BaseModel
from typing import List, Dict, Any
import re
import json


class ScrapedContext(BaseModel):
    title: str
    images: List[str]
    summary: str
    css_contents: str
    html: str
    url: str


async def scrape_website(url: str) -> ScrapedContext:
    """
    Scrape a website and extract HTML, CSS, and metadata.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to the page
            await page.goto(url, wait_until="networkidle")
            
            # Get the HTML content
            html = await page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else "Untitled"
            
            # Extract images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    images.append(src)
            
            # Extract CSS
            css_contents = ""
            for style in soup.find_all('style'):
                css_contents += style.get_text() + "\n"
            
            # Extract external CSS
            for link in soup.find_all('link', rel='stylesheet'):
                href = link.get('href')
                if href:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(href) as response:
                                if response.status == 200:
                                    css_contents += await response.text() + "\n"
                    except:
                        pass  # Skip if external CSS can't be loaded
            
            # Create summary
            summary = f"Website: {title}\nImages: {len(images)}\nCSS rules: {len(css_contents.split('}'))}"
            
            return ScrapedContext(
                title=title,
                images=images,
                summary=summary,
                css_contents=css_contents,
                html=html,
                url=url
            )
            
        finally:
            await browser.close() 