import asyncio
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pydantic import BaseModel
from typing import List, Dict, Any
import re
import json
import logging
from urllib.parse import urlparse, urljoin

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
                    # Convert relative URLs to absolute URLs
                    if src.startswith('//'):
                        img_url = f"https:{src}"
                    elif src.startswith('/'):
                        # Get the base URL
                        parsed_url = urlparse(url)
                        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                        img_url = f"{base_url}{src}"
                    elif src.startswith('http'):
                        img_url = src
                    else:
                        # Relative URL
                        img_url = urljoin(url, src)
                    
                    images.append(img_url)
            logger.info(f"   ✅ Images extracted: {len(images)} found")
            if images:
                logger.info(f"   → Sample images: {images[:3]}")
            
            # Extract CSS
            logger.info("   → Extracting inline CSS...")
            css_contents = ""
            for style in soup.find_all('style'):
                css_contents += style.get_text() + "\n"
            logger.info(f"   ✅ Inline CSS extracted: {len(css_contents)} characters")
            
            # Extract external CSS
            logger.info("   → Extracting external CSS...")
            external_css_count = 0
            css_files_processed = 0
            
            for link in soup.find_all('link', rel='stylesheet'):
                if css_files_processed >= 8:  # Increased from 5 to 8 files
                    logger.info(f"   → Skipping additional CSS files (limit reached)")
                    break
                    
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute URLs
                    if href.startswith('//'):
                        css_url = f"https:{href}"
                    elif href.startswith('/'):
                        # Get the base URL
                        parsed_url = urlparse(url)
                        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                        css_url = f"{base_url}{href}"
                    elif href.startswith('http'):
                        css_url = href
                    else:
                        # Relative URL
                        css_url = urljoin(url, href)
                    
                    try:
                        logger.info(f"   → Fetching external CSS: {css_url}")
                        async with aiohttp.ClientSession() as session:
                            async with session.get(css_url, timeout=15) as response:
                                if response.status == 200:
                                    external_css = await response.text()
                                    # Limit each CSS file to 15KB (increased from 10KB)
                                    if len(external_css) > 15000:
                                        external_css = external_css[:15000]
                                        logger.info(f"   ⚠️  CSS file truncated to 15KB")
                                    
                                    css_contents += external_css + "\n"
                                    external_css_count += 1
                                    logger.info(f"   ✅ External CSS fetched: {len(external_css)} characters")
                                else:
                                    logger.warning(f"   ⚠️  Failed to fetch CSS from {css_url}: {response.status}")
                    except Exception as e:
                        logger.warning(f"   ⚠️  Error fetching CSS from {css_url}: {e}")
                        pass  # Skip if external CSS can't be loaded
                
                css_files_processed += 1
            
            logger.info(f"   ✅ External CSS processed: {external_css_count} files")
            logger.info(f"   → Total CSS content: {len(css_contents)} characters")
            
            # Also extract computed styles from the page
            logger.info("   → Extracting computed styles...")
            try:
                # Get computed styles for key elements
                computed_styles = await page.evaluate("""
                    () => {
                        const styles = {};
                        const elements = document.querySelectorAll('*');
                        elements.forEach((el, index) => {
                            if (index < 100) { // Limit to first 100 elements
                                const computed = window.getComputedStyle(el);
                                const tagName = el.tagName.toLowerCase();
                                const className = el.className;
                                const id = el.id;
                                
                                if (className || id) {
                                    const selector = id ? `#${id}` : `.${className.split(' ')[0]}`;
                                    if (!styles[selector]) {
                                        styles[selector] = {
                                            'background-color': computed.backgroundColor,
                                            'color': computed.color,
                                            'font-family': computed.fontFamily,
                                            'font-size': computed.fontSize,
                                            'margin': computed.margin,
                                            'padding': computed.padding,
                                            'display': computed.display,
                                            'position': computed.position
                                        };
                                    }
                                }
                            }
                        });
                        return styles;
                    }
                """)
                
                # Convert computed styles to CSS
                for selector, properties in computed_styles.items():
                    css_contents += f"\n{selector} {{\n"
                    for prop, value in properties.items():
                        if value and value != 'initial' and value != 'normal':
                            css_contents += f"    {prop}: {value};\n"
                    css_contents += "}\n"
                
                logger.info(f"   ✅ Computed styles extracted: {len(computed_styles)} selectors")
            except Exception as e:
                logger.warning(f"   ⚠️  Error extracting computed styles: {e}")
            
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