import re
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def extract_code_blocks(text: str) -> Tuple[str, str]:
    """
    Extract HTML and CSS code blocks from Claude's response.
    """
    logger.info("      → Extracting code blocks from Claude response...")
    
    html_code = ""
    css_code = ""
    
    # Find HTML code block
    html_match = re.search(r'```html\s*\n(.*?)\n```', text, re.DOTALL)
    if html_match:
        html_code = html_match.group(1).strip()
        logger.info(f"      ✅ HTML code block found: {len(html_code)} characters")
    else:
        logger.warning("      ⚠️  No HTML code block found")
    
    # Find CSS code block
    css_match = re.search(r'```css\s*\n(.*?)\n```', text, re.DOTALL)
    if css_match:
        css_code = css_match.group(1).strip()
        logger.info(f"      ✅ CSS code block found: {len(css_code)} characters")
    else:
        logger.warning("      ⚠️  No CSS code block found")
    
    return html_code, css_code


def inline_css(html: str, css: str) -> str:
    """
    Inline CSS into HTML by adding a <style> tag in the <head>.
    """
    logger.info("      → Inlining CSS into HTML...")
    
    if not html or not css:
        logger.warning("      ⚠️  Empty HTML or CSS, returning original HTML")
        return html
    
    # Check if HTML has a head tag
    if '<head>' in html:
        # Insert style tag in head
        style_tag = f'<style>\n{css}\n</style>'
        html = html.replace('<head>', f'<head>\n{style_tag}')
        logger.info("      ✅ CSS inlined into existing <head> tag")
    else:
        # If no head tag, add one with style
        style_tag = f'<head>\n<style>\n{css}\n</style>\n</head>'
        html = html.replace('<html>', f'<html>\n{style_tag}')
        logger.info("      ✅ CSS inlined with new <head> tag")
    
    logger.info(f"      ✅ CSS inlining complete: {len(html)} characters")
    return html


def combine_html_and_css(html: str, css: str) -> str:
    """
    Combine HTML and CSS into a single HTML document.
    """
    logger.info("      → Combining HTML and CSS...")
    
    if not html:
        logger.warning("      ⚠️  Empty HTML, returning empty string")
        return ""
    
    # If HTML doesn't have proper structure, wrap it
    if not html.strip().startswith('<!DOCTYPE html>') and not html.strip().startswith('<html'):
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloned Website</title>
    <style>
{css}
    </style>
</head>
<body>
{html}
</body>
</html>"""
        logger.info("      ✅ HTML wrapped with complete document structure")
    else:
        # Inline CSS into existing HTML
        html = inline_css(html, css)
        logger.info("      ✅ CSS inlined into existing HTML structure")
    
    logger.info(f"      ✅ HTML and CSS combined: {len(html)} characters")
    return html 