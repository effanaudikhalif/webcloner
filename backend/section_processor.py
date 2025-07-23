# backend/section_processor.py

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import trafilatura
from bs4 import BeautifulSoup
from lxml import html
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class WebsiteSection:
    """Represents a detected section of a website"""
    name: str  # e.g., "header", "main-content", "sidebar", "footer"
    html: str
    css: str
    description: str
    priority: int  # 1 = highest priority (main content), 5 = lowest (footer)

class SectionProcessor:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    def conservative_clone(self, url: str) -> Dict[str, str]:
        """
        Conservative website cloning approach.
        
        This method preserves the original HTML structure and CSS exactly as-is,
        only making minimal technical fixes needed for standalone functionality.
        
        Args:
            url: The website URL to clone
            
        Returns:
            Dictionary containing the cloned HTML and metadata
        """
        print(f"DEBUG: Starting conservative clone of {url}")
        
        # Import scraper here to avoid circular imports
        from scraper import scrape_website
        import asyncio
        
        # Scrape the website
        context = asyncio.run(scrape_website(url))
        context_dict = context.model_dump()
        
        # Extract HTML and CSS
        full_html = context_dict.get("html", "")
        raw_css = context_dict.get("css_contents", "")
        
        print(f"DEBUG: Scraped {len(full_html)} characters of HTML and {len(raw_css)} characters of CSS")
        
        # Process with conservative approach
        result = self.process_entire_site_conservatively(full_html, raw_css, url)
        
        print(f"DEBUG: Conservative clone completed successfully")
        
        return {
            "combined_html": result["combined_html"],
            "sections": result["sections"],
            "section_count": len(result["sections"]),
            "method": "conservative",
            "original_url": url,
            "scraped_html_length": len(full_html),
            "scraped_css_length": len(raw_css)
        }

    def process_entire_site_conservatively(self, full_html: str, full_css: str, original_url: str = None) -> Dict[str, str]:
        """Process the entire site as one piece with minimal AI intervention"""
        print("DEBUG: Using conservative approach - processing entire site as one piece")
        
        # Parse HTML and fix links/images while preserving structure
        soup = BeautifulSoup(full_html, 'html.parser')
        
        # Fix image URLs to be absolute
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                if original_url:
                    from urllib.parse import urljoin
                    img['src'] = urljoin(original_url, src)
                elif src.startswith('/'):
                    img['src'] = f"https://www.bu.edu{src}"
                elif not src.startswith('http'):
                    img['src'] = f"https://www.bu.edu/{src}"
        
        # Fix picture elements for responsive images
        for picture in soup.find_all('picture'):
            for source in picture.find_all('source'):
                srcset = source.get('srcset', '')
                if srcset and not srcset.startswith('http'):
                    new_srcset = []
                    for src_item in srcset.split(','):
                        if ' ' in src_item:
                            url, size = src_item.strip().split(' ', 1)
                            if not url.startswith('http'):
                                if url.startswith('/'):
                                    url = f"https://www.bu.edu{url}"
                                else:
                                    url = f"https://www.bu.edu/{url}"
                            new_srcset.append(f"{url} {size}")
                        else:
                            url = src_item.strip()
                            if not url.startswith('http'):
                                if url.startswith('/'):
                                    url = f"https://www.bu.edu{url}"
                                else:
                                    url = f"https://www.bu.edu/{url}"
                            new_srcset.append(url)
                    source['srcset'] = ', '.join(new_srcset)
        
        # Fix external links to be #
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href and href.startswith('http'):
                link['href'] = '#'
        
        # Fix form actions
        for form in soup.find_all('form'):
            if form.get('action'):
                form['action'] = '#'
        
        # Get the fixed HTML
        fixed_html = str(soup)
        
        # Create the complete HTML document
        complete_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recreated Website</title>
    <style>
{full_css}
    </style>
</head>
<body>
{fixed_html}
</body>
</html>"""
        
        return {
            "combined_html": complete_html,
            "sections": [{
                "html": fixed_html,
                "css": full_css,
                "section_name": "entire-site",
                "description": "Entire website processed conservatively",
                "method": "conservative"
            }],
            "method": "conservative"
        }
    
    def detect_sections(self, full_html: str, full_css: str, original_url: str = None) -> List[WebsiteSection]:
        """Detect and extract different sections from the website"""
        sections = []
        
        # Parse HTML
        soup = BeautifulSoup(full_html, 'html.parser')
        
        # Extract and store all images for later use
        self.original_images = {}
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                # Make relative URLs absolute using the original website URL
                if original_url:
                    from urllib.parse import urljoin
                    src = urljoin(original_url, src)
                elif src.startswith('/'):
                    src = f"https://www.bu.edu{src}"
                elif not src.startswith('http'):
                    src = f"https://www.bu.edu/{src}"
                
                # Store image URL with a unique identifier
                img_id = f"img_{len(self.original_images)}"
                self.original_images[img_id] = src
                print(f"DEBUG: Found original image {img_id}: {src}")
        
        print(f"DEBUG: Total original images found: {len(self.original_images)}")
        
        # Try a different approach: extract sections based on visual structure
        # Instead of using trafilatura, let's preserve the original layout
        
        # 1. Extract header/navigation (keep visual structure)
        header = self._extract_header(soup)
        if header:
            header_css = self._extract_css_for_html(header, full_css)
            sections.append(WebsiteSection(
                name="header",
                html=header,
                css=header_css,
                description="Site header with navigation and branding",
                priority=2
            ))
        
        # 2. Extract hero/banner sections (keep visual structure)
        hero = self._extract_hero(soup)
        if hero:
            hero_css = self._extract_css_for_html(hero, full_css)
            sections.append(WebsiteSection(
                name="hero",
                html=hero,
                css=hero_css,
                description="Hero banner or main promotional section",
                priority=2
            ))
        
        # 3. Extract main content area (preserve visual structure)
        main_content = self._extract_main_content_visual(full_html)
        if main_content:
            main_css = self._extract_css_for_html(main_content, full_css)
            sections.append(WebsiteSection(
                name="main-content",
                html=main_content,
                css=main_css,
                description="Main content area with primary information",
                priority=1
            ))
        
        # 4. Extract sidebar (keep visual structure)
        sidebar = self._extract_sidebar(soup)
        if sidebar:
            sidebar_css = self._extract_css_for_html(sidebar, full_css)
            sections.append(WebsiteSection(
                name="sidebar",
                html=sidebar,
                css=sidebar_css,
                description="Sidebar with secondary navigation or content",
                priority=3
            ))
        
        # 5. Extract footer (keep visual structure)
        footer = self._extract_footer(soup)
        if footer:
            footer_css = self._extract_css_for_html(footer, full_css)
            sections.append(WebsiteSection(
                name="footer",
                html=footer,
                css=footer_css,
                description="Site footer with links and information",
                priority=4
            ))
        
        return sections
    
    def _extract_main_content_visual(self, html_content: str) -> Optional[str]:
        """Extract main content while preserving visual structure"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for the largest content area that's not header/footer/sidebar
        body = soup.find('body')
        if not body:
            return None
        
        # Find all major divs and sections
        content_candidates = []
        
        for element in body.find_all(['div', 'section', 'main', 'article']):
            # Skip if it's clearly header/footer/sidebar
            classes = ' '.join(element.get('class', [])).lower()
            if any(x in classes for x in ['header', 'footer', 'sidebar', 'nav', 'menu']):
                continue
            
            # Skip if it's too small
            if len(str(element)) < 500:
                continue
            
            content_candidates.append(element)
        
        if content_candidates:
            # Return the largest content area
            largest = max(content_candidates, key=lambda x: len(str(x)))
            print(f"DEBUG: Found main content area with {len(str(largest))} characters")
            return str(largest)
        
        return None
    
    def _extract_main_content(self, html_content: str) -> Optional[str]:
        """Extract main content - prefer visual structure over text extraction"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # First try to find main content areas that preserve visual structure
        main_selectors = [
            'main', '[role="main"]', '.main-content', '.content', '#content', '#main',
            '.page-content', '.site-content', '.entry-content', '.post-content'
        ]
        
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element:
                print(f"DEBUG: Found main content using selector: {selector}")
                return str(element)
        
        # If no semantic main content found, try to extract the largest content area
        # This preserves visual structure better than trafilatura
        body = soup.find('body')
        if body:
            # Find the largest div that's not header, nav, footer, sidebar
            content_areas = []
            for div in body.find_all('div'):
                if div.get('class'):
                    classes = ' '.join(div.get('class', []))
                    if not any(x in classes.lower() for x in ['header', 'nav', 'footer', 'sidebar', 'menu']):
                        content_areas.append(div)
            
            if content_areas:
                # Return the largest content area
                largest_area = max(content_areas, key=lambda x: len(str(x)))
                print(f"DEBUG: Using largest content area with {len(str(largest_area))} characters")
                return str(largest_area)
        
        # Last resort: use trafilatura but warn about it
        try:
            extracted = trafilatura.extract(html_content, include_formatting=True)
            if extracted:
                print("DEBUG: Using trafilatura extraction (may lose visual structure)")
                return extracted
        except Exception as e:
            print(f"Trafilatura extraction failed: {e}")
        
        return None
    
    def _extract_header(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract header/navigation section"""
        header_selectors = [
            'header', '[role="banner"]', '.header', '.site-header', 
            '.main-header', '.navigation', 'nav', '.nav'
        ]
        
        for selector in header_selectors:
            element = soup.select_one(selector)
            if element:
                return str(element)
        
        return None
    
    def _extract_sidebar(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract sidebar section"""
        sidebar_selectors = [
            'aside', '[role="complementary"]', '.sidebar', '.side-nav',
            '.secondary', '.widget-area'
        ]
        
        for selector in sidebar_selectors:
            element = soup.select_one(selector)
            if element:
                return str(element)
        
        return None
    
    def _extract_footer(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract footer section"""
        footer_selectors = [
            'footer', '[role="contentinfo"]', '.footer', '.site-footer',
            '.main-footer'
        ]
        
        for selector in footer_selectors:
            element = soup.select_one(selector)
            if element:
                return str(element)
        
        return None
    
    def _extract_hero(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract hero/banner section"""
        hero_selectors = [
            '.hero', '.banner', '.jumbotron', '.hero-section',
            '.main-banner', '[class*="hero"]', '[class*="banner"]'
        ]
        
        for selector in hero_selectors:
            element = soup.select_one(selector)
            if element:
                return str(element)
        
        return None
    
    def _extract_css_for_html(self, html_content: str, full_css: str) -> str:
        """Extract only the CSS that applies to the given HTML"""
        try:
            # For now, return the full CSS to ensure styling is preserved
            # The CSS filtering was too aggressive and removing important styles
            print(f"DEBUG: Using full CSS for section (length: {len(full_css)})")
            return full_css
        except Exception as e:
            print(f"CSS extraction failed: {e}")
            return full_css  # Fallback to full CSS
    
    def _selector_used_in_html(self, selector: str, html_content: str) -> bool:
        """Check if a CSS selector is used in the HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Simple check - you might want more sophisticated selector matching
        if selector.startswith('.'):
            # Class selector
            class_name = selector[1:]
            return soup.find(class_=class_name) is not None
        elif selector.startswith('#'):
            # ID selector
            id_name = selector[1:]
            return soup.find(id=id_name) is not None
        else:
            # Tag selector
            return soup.find(selector) is not None
    
    async def process_section(self, section: WebsiteSection) -> Dict[str, str]:
        """Process a single section with Claude AI"""
        prompt = self._format_section_prompt(section)
        
        try:
            # Add delay to avoid rate limiting
            import asyncio
            await asyncio.sleep(1)
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,  # Reduced from 4000
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract HTML and CSS from response
            content = response.content[0].text
            html_code = self._extract_code_block("html", content)
            css_code = self._extract_code_block("css", content)
            
            # Check if images are preserved in the AI output
            from bs4 import BeautifulSoup
            ai_soup = BeautifulSoup(html_code, 'html.parser')
            original_soup = BeautifulSoup(section.html, 'html.parser')
            
            ai_images = len(ai_soup.find_all('img'))
            original_images = len(original_soup.find_all('img'))
            
            print(f"DEBUG: Section {section.name} - Original images: {original_images}, AI output images: {ai_images}")
            
            # If AI didn't preserve images or structure, use original HTML with link fixes
            if ai_images < original_images or len(html_code) < len(section.html) * 0.5:
                print(f"DEBUG: AI didn't preserve structure properly, using original HTML with link fixes")
                fixed_html = self._fix_links_only(section.html)
                return {
                    "html": fixed_html,
                    "css": section.css,
                    "section_name": section.name,
                    "description": section.description,
                    "method": "original_with_fixes"
                }
            
            return {
                "html": html_code,
                "css": css_code,
                "section_name": section.name,
                "description": section.description,
                "method": "ai_generated"
            }
            
        except Exception as e:
            print(f"Error processing section {section.name}: {e}")
            return {
                "html": section.html,
                "css": section.css,
                "section_name": section.name,
                "description": section.description,
                "error": str(e)
            }
    
    def _fix_links_only(self, html_content: str) -> str:
        """Fix only links in HTML, preserve everything else"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Fix links - replace external URLs with #
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href and href.startswith('http'):
                link['href'] = '#'
        
        # Fix form actions
        for form in soup.find_all('form'):
            if form.get('action'):
                form['action'] = '#'
        
        return str(soup)
    
    def _format_section_prompt(self, section: WebsiteSection) -> str:
        """Format prompt for processing a specific section"""
        return f"""Recreate this {section.name} section with clean HTML and CSS. CRITICAL REQUIREMENTS:
- Keep ALL original styling and layout exactly as shown
- DO NOT CHANGE ANY img src attributes - keep them exactly as they are
- Replace all external navigation links with href="#"
- Preserve all visual elements, colors, fonts, spacing
- Make sure the result looks identical to the original
- IMPORTANT: Copy img tags exactly as they appear in the original
- Keep all CSS classes and styling intact

HTML:
```html
{section.html[:3000]}
```

CSS:
```css
{section.css[:3000]}
```

Return only:
```html
[recreated HTML with EXACT same img tags, classes, and # navigation links]
```

```css
[recreated CSS with exact original styling]
```"""
    
    def _extract_code_block(self, block_type: str, text: str) -> str:
        """Extract code from markdown code blocks"""
        pattern = f"```{block_type}\\n(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    async def process_all_sections(self, sections: List[WebsiteSection]) -> List[Dict[str, str]]:
        """Process all sections and return results"""
        results = []
        
        # Process sections in priority order
        sorted_sections = sorted(sections, key=lambda x: x.priority)
        
        for section in sorted_sections:
            result = await self.process_section(section)
            results.append(result)
        
        return results
    
    def combine_sections(self, processed_sections: List[Dict[str, str]]) -> Dict[str, str]:
        """Combine all processed sections into a complete website"""
        combined_html = []
        combined_css = []
        
        # Add basic HTML structure
        combined_html.append("<!DOCTYPE html>")
        combined_html.append('<html lang="en">')
        combined_html.append('<head>')
        combined_html.append('    <meta charset="UTF-8">')
        combined_html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        combined_html.append('    <title>Recreated Website</title>')
        combined_html.append('    <style>')
        
        # Add CSS from all sections
        for section in processed_sections:
            if section.get("css"):
                combined_css.append(f"/* {section['section_name']} styles */")
                combined_css.append(section["css"])
        
        combined_html.extend(combined_css)
        combined_html.append('    </style>')
        combined_html.append('</head>')
        combined_html.append('<body>')
        
        # Add HTML from all sections
        for section in processed_sections:
            if section.get("html"):
                combined_html.append(f"<!-- {section['section_name']} -->")
                combined_html.append(section["html"])
        
        combined_html.append('</body>')
        combined_html.append('</html>')
        
        # Process the combined HTML to fix image URLs and links
        final_html = self._process_combined_html('\n'.join(combined_html))
        
        return {
            "combined_html": final_html,
            "sections": processed_sections
        }
    
    def _process_combined_html(self, html_content: str) -> str:
        """Process combined HTML to fix images and links"""
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print(f"DEBUG: Found {len(soup.find_all('img'))} images in processed HTML")
        print(f"DEBUG: Original images available: {len(getattr(self, 'original_images', {}))}")
        
        # Process all images to make them absolute URLs
        for img in soup.find_all('img'):
            current_src = img.get('src', '')
            if current_src:
                # If it's already an absolute URL, keep it
                if current_src.startswith('http'):
                    continue
                
                # Make relative URLs absolute
                if current_src.startswith('/'):
                    img['src'] = f"https://www.bu.edu{current_src}"
                    print(f"DEBUG: Made image absolute: {current_src} -> https://www.bu.edu{current_src}")
                else:
                    img['src'] = f"https://www.bu.edu/{current_src}"
                    print(f"DEBUG: Made image absolute: {current_src} -> https://www.bu.edu/{current_src}")
        
        # Also process picture elements (for responsive images)
        for picture in soup.find_all('picture'):
            for source in picture.find_all('source'):
                srcset = source.get('srcset', '')
                if srcset and not srcset.startswith('http'):
                    # Make srcset URLs absolute
                    new_srcset = []
                    for src_item in srcset.split(','):
                        if ' ' in src_item:
                            url, size = src_item.strip().split(' ', 1)
                            if not url.startswith('http'):
                                if url.startswith('/'):
                                    url = f"https://www.bu.edu{url}"
                                else:
                                    url = f"https://www.bu.edu/{url}"
                            new_srcset.append(f"{url} {size}")
                        else:
                            url = src_item.strip()
                            if not url.startswith('http'):
                                if url.startswith('/'):
                                    url = f"https://www.bu.edu{url}"
                                else:
                                    url = f"https://www.bu.edu/{url}"
                            new_srcset.append(url)
                    source['srcset'] = ', '.join(new_srcset)
        
        # Fix links - replace external URLs with #
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href and href.startswith('http'):
                link['href'] = '#'
        
        # Fix form actions
        for form in soup.find_all('form'):
            if form.get('action'):
                form['action'] = '#'
        
        return str(soup) 