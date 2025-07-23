import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def build_summary_and_minimal_html(context_dict: Dict[str, Any]) -> tuple:
    """
    Build a summary JSON object and focused HTML content from the scraped context.
    """
    logger.info("      → Building summary and focused HTML content...")
    
    title = context_dict.get("title", "Untitled")
    images = context_dict.get("images", [])
    summary = context_dict.get("summary", "")
    html_content = context_dict.get("html", "")
    
    # Create summary JSON object
    summary_json_obj = {
        "title": title,
        "image_count": len(images),
        "images": images[:15],  # Include more images
        "summary": summary
    }
    logger.info(f"      → Summary created: {summary_json_obj}")
    
    # Extract the most important parts of the HTML structure
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove problematic elements but keep structure
    for element in soup(["script", "noscript", "iframe", "object", "embed"]):
        element.decompose()
    
    # Extract key structural elements
    key_elements = []
    
    # Get the main structural elements
    for tag in soup.find_all(['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']):
        key_elements.append(str(tag))
    
    # If no structural elements found, get the body content
    if not key_elements:
        body = soup.find('body')
        if body:
            key_elements.append(str(body))
    
    # Combine key elements
    if key_elements:
        focused_html = '\n'.join(key_elements)
    else:
        # Fallback to the full HTML
        focused_html = str(soup)
    
    logger.info(f"      → Focused HTML content prepared: {len(focused_html)} characters")
    
    return summary_json_obj, focused_html


def build_critical_css(filtered_css: str) -> str:
    """
    Build critical CSS from filtered CSS content.
    """
    logger.info("      → Building critical CSS...")
    
    if not filtered_css:
        logger.warning("      ⚠️  No filtered CSS provided")
        return ""
    
    # For now, return the filtered CSS as critical CSS
    # In a more sophisticated implementation, you might:
    # - Analyze which CSS rules are most important
    # - Prioritize above-the-fold styles
    # - Remove unused or redundant rules
    
    logger.info(f"      ✅ Critical CSS created: {len(filtered_css)} characters")
    return filtered_css


def format_prompt(summary_json_obj: Dict[str, Any], focused_html: str, critical_css: str) -> str:
    """
    Format a prompt for Claude to recreate the website.
    """
    logger.info("      → Formatting prompt for Claude AI...")
    
    # Send focused content that fits within token limits
    html_preview = focused_html[:12000]  # Send more focused HTML
    css_preview = critical_css[:8000]    # Send more CSS
    
    prompt = f"""
You are an expert web developer creating an EXACT replica of a website. Study the provided HTML structure and CSS styles carefully, then recreate the website with identical appearance and layout.

## Website Information
{json.dumps(summary_json_obj, indent=2)}

## Key HTML Structure (Study this carefully)
```html
{html_preview}
```

## Original CSS Styles (Use these as your base)
```css
{css_preview}
```

## CRITICAL INSTRUCTIONS:

1. **EXACT REPLICATION**: Your HTML must match the original structure EXACTLY
2. **PRESERVE ALL ELEMENTS**: Keep all divs, sections, headers, navigation, footers exactly as they appear
3. **MAINTAIN CLASSES**: Use the exact same CSS classes and IDs from the original
4. **INCLUDE ALL IMAGES**: Use the provided image URLs in their exact locations
5. **MATCH STYLING**: Your CSS must recreate the original colors, fonts, spacing, and layout
6. **RESPONSIVE DESIGN**: Ensure the layout works on all screen sizes
7. **SEMANTIC HTML**: Use proper HTML5 semantic elements where appropriate

## YOUR TASK:
Create a complete HTML document that looks EXACTLY like the original website. The HTML should include:
- The same header/navigation structure
- The same content sections and layout
- The same images in their original positions
- The same footer and other structural elements

## CSS REQUIREMENTS:
Your CSS must include:
- All the original colors and fonts
- The exact same layout and positioning
- Responsive breakpoints for different screen sizes
- All hover effects and interactions
- The same spacing, margins, and padding

## OUTPUT FORMAT - YOU MUST FOLLOW THIS EXACTLY:

You MUST provide your response in EXACTLY this format with the code blocks:

```html
[Complete HTML document that recreates the original website structure]
```

```css
[Complete CSS that matches the original styling exactly]
```

IMPORTANT: 
- The final result should look IDENTICAL to the original website
- Pay attention to every detail including colors, fonts, spacing, layout, and structure
- You MUST include both the ```html and ```css code blocks in your response
- Do not include any text outside of the code blocks
"""
    
    logger.info(f"      ✅ Prompt formatted: {len(prompt)} characters")
    return prompt 