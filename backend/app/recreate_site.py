import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def build_summary_and_minimal_html(context_dict: Dict[str, Any]) -> tuple:
    """
    Build a summary JSON object and actual HTML content from the scraped context.
    """
    logger.info("      → Building summary and HTML content...")
    
    title = context_dict.get("title", "Untitled")
    images = context_dict.get("images", [])
    summary = context_dict.get("summary", "")
    html_content = context_dict.get("html", "")
    
    # Create summary JSON object
    summary_json_obj = {
        "title": title,
        "image_count": len(images),
        "images": images[:10],  # Limit to first 10 images
        "summary": summary
    }
    logger.info(f"      → Summary created: {summary_json_obj}")
    
    # Use the actual scraped HTML content instead of a minimal snippet
    # Clean up the HTML to remove scripts and other unnecessary elements
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script tags and other unnecessary elements
    for script in soup(["script", "noscript", "style"]):
        script.decompose()
    
    # Keep the main structure but clean it up
    actual_html = str(soup)
    logger.info(f"      → Actual HTML content prepared: {len(actual_html)} characters")
    
    return summary_json_obj, actual_html


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


def format_prompt(summary_json_obj: Dict[str, Any], actual_html: str, critical_css: str) -> str:
    """
    Format a prompt for Claude to recreate the website.
    """
    logger.info("      → Formatting prompt for Claude AI...")
    
    prompt = f"""
You are a web developer tasked with recreating a website based on the following information:

## Website Summary
{json.dumps(summary_json_obj, indent=2)}

## Original Website HTML Structure
```html
{actual_html[:5000]}  # First 5000 characters of the actual HTML
```

## Critical CSS from Original
```css
{critical_css}
```

## Task
Please recreate this website by providing BOTH HTML and CSS code blocks that closely match the original.

## Requirements
- Recreate the EXACT layout and structure of the original website
- Use the same HTML elements and structure as the original
- Include all images from the original website (use the image URLs provided)
- Match the original styling, colors, fonts, and layout as closely as possible
- Use the CSS from the original website as a base and improve upon it
- Create a responsive design that works on different screen sizes
- Maintain the original navigation, headers, footers, and content sections
- Use semantic HTML5 elements where appropriate
- Include proper accessibility features

## IMPORTANT: You MUST provide BOTH HTML and CSS code blocks in your response.

Please provide your response in EXACTLY this format:

```html
[Your complete HTML code here - recreate the original website structure]
```

```css
[Your complete CSS code here - match the original styling and layout]
```

Make sure the HTML and CSS work together to create a functional, styled webpage that looks EXACTLY like the original website. The CSS should be comprehensive and include all necessary styles for the layout, typography, colors, images, and responsive design.
"""
    
    logger.info(f"      ✅ Prompt formatted: {len(prompt)} characters")
    return prompt 