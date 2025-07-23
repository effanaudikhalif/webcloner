import asyncio
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pydantic import BaseModel
from typing import List, Dict, Any
import re
import json
import logging

logger = logging.getLogger(__name__)


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
    logger.info(f"   🕷️  Starting Playwright browser for {url}")
    async with async_playwright() as p:
        logger.info("   → Launching Chromium browser...")
        browser = await p.chromium.launch(headless=True)
        logger.info("   ✅ Browser launched successfully")
        
        logger.info("   → Creating new page...")
        page = await browser.new_page()
        logger.info("   ✅ Page created")
        
        try:
            # Navigate to the page
            logger.info(f"   → Navigating to {url}...")
            await page.goto(url, wait_until="networkidle")
            logger.info("   ✅ Navigation completed")
            
            # Get the HTML content
            logger.info("   → Extracting HTML content...")
            html = await page.content()
            logger.info(f"   ✅ HTML extracted: {len(html)} characters")
            
            # Parse with BeautifulSoup
            logger.info("   → Parsing HTML with BeautifulSoup...")
            soup = BeautifulSoup(html, 'html.parser')
            logger.info("   ✅ HTML parsed successfully")
            
            # Extract title
            logger.info("   → Extracting page title...")
            title = soup.title.string if soup.title else "Untitled"
            logger.info(f"   ✅ Title extracted: {title}")
            
            # Extract images
            logger.info("   → Extracting images...")
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    images.append(src)
            logger.info(f"   ✅ Images extracted: {len(images)} found")
            
            # Extract CSS
            logger.info("   → Extracting inline CSS...")
            css_contents = ""
            for style in soup.find_all('style'):
                css_contents += style.get_text() + "\n"
            logger.info(f"   ✅ Inline CSS extracted: {len(css_contents)} characters")
            
            # Extract external CSS
            logger.info("   → Extracting external CSS...")
            external_css_count = 0
            for link in soup.find_all('link', rel='stylesheet'):
                href = link.get('href')
                if href:
                    try:
                        logger.info(f"   → Fetching external CSS: {href}")
                        async with aiohttp.ClientSession() as session:
                            async with session.get(href) as response:
                                if response.status == 200:
                                    external_css = await response.text()
                                    css_contents += external_css + "\n"
                                    external_css_count += 1
                                    logger.info(f"   ✅ External CSS fetched: {len(external_css)} characters")
                                else:
                                    logger.warning(f"   ⚠️  Failed to fetch CSS from {href}: {response.status}")
                    except Exception as e:
                        logger.warning(f"   ⚠️  Error fetching CSS from {href}: {e}")
                        pass  # Skip if external CSS can't be loaded
            
            logger.info(f"   ✅ External CSS processed: {external_css_count} files")
            logger.info(f"   → Total CSS content: {len(css_contents)} characters")
            
            # Create summary
            logger.info("   → Creating summary...")
            summary = f"Website: {title}\nImages: {len(images)}\nCSS rules: {len(css_contents.split('}'))}"
            logger.info(f"   ✅ Summary created: {summary}")
            
            logger.info("   🎉 Scraping completed successfully!")
            
            return ScrapedContext(
                title=title,
                images=images,
                summary=summary,
                css_contents=css_contents,
                html=html,
                url=url
            )
            
        except Exception as e:
            logger.error(f"   ❌ Error during scraping: {e}")
            raise e
        finally:
            logger.info("   → Closing browser...")
            await browser.close()
            logger.info("   ✅ Browser closed") 