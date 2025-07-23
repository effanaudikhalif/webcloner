import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def build_summary_and_minimal_html(context_dict: Dict[str, Any]) -> tuple:
    """
    Build a summary JSON object and minimal HTML snippet from the scraped context.
    """
    logger.info("      → Building summary and minimal HTML...")
    
    title = context_dict.get("title", "Untitled")
    images = context_dict.get("images", [])
    summary = context_dict.get("summary", "")
    
    # Create summary JSON object
    summary_json_obj = {
        "title": title,
        "image_count": len(images),
        "images": images[:5],  # Limit to first 5 images
        "summary": summary
    }
    logger.info(f"      → Summary created: {summary_json_obj}")
    
    # Create minimal HTML snippet
    minimal_html = f"""
    <div class="website-clone">
        <h1>{title}</h1>
        <div class="content">
            <p>This is a cloned version of the original website.</p>
            <p>Summary: {summary}</p>
        </div>
    </div>
    """
    logger.info(f"      → Minimal HTML created: {len(minimal_html)} characters")
    
    return summary_json_obj, minimal_html


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


def format_prompt(summary_json_obj: Dict[str, Any], minimal_html: str, critical_css: str) -> str:
    """
    Format a prompt for Claude to recreate the website.
    """
    logger.info("      → Formatting prompt for Claude AI...")
    
    prompt = f"""
You are a web developer tasked with recreating a website based on the following information:

## Website Summary
{json.dumps(summary_json_obj, indent=2)}

## Minimal HTML Structure
```html
{minimal_html}
```

## Critical CSS
```css
{critical_css}
```

## Task
Please recreate this website by providing BOTH HTML and CSS code blocks.

## Requirements
- Use semantic HTML5 elements
- Create a responsive design
- Include proper accessibility features
- Match the original styling as closely as possible
- Use modern CSS techniques (Flexbox, Grid, etc.)

## IMPORTANT: You MUST provide BOTH HTML and CSS code blocks in your response.

Please provide your response in EXACTLY this format:

```html
[Your complete HTML code here]
```

```css
[Your complete CSS code here]
```

Make sure the HTML and CSS work together to create a functional, styled webpage. The CSS should be comprehensive and include all necessary styles for the layout, typography, colors, and responsive design.
"""
    
    logger.info(f"      ✅ Prompt formatted: {len(prompt)} characters")
    return prompt 