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
    
    # Find HTML code block - try multiple patterns
    html_patterns = [
        r'```html\s*\n(.*?)\n```',
        r'```HTML\s*\n(.*?)\n```',
        r'<html.*?</html>',
        r'<!DOCTYPE html.*?</html>',
        r'<html[^>]*>.*?</html>',
        r'<!DOCTYPE[^>]*>.*?</html>'
    ]
    
    for pattern in html_patterns:
        try:
            html_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if html_match and html_match.groups():
                html_code = html_match.group(1).strip()
                logger.info(f"      ✅ HTML code block found: {len(html_code)} characters")
                break
        except (IndexError, AttributeError) as e:
            logger.warning(f"      ⚠️  Error extracting HTML with pattern {pattern}: {e}")
            continue
    
    if not html_code:
        # Try to find any HTML-like content
        html_like = re.search(r'<[^>]+>.*?</[^>]+>', text, re.DOTALL)
        if html_like:
            html_code = html_like.group(0)
            logger.info(f"      ✅ HTML-like content found: {len(html_code)} characters")
        else:
            logger.warning("      ⚠️  No HTML code block found")
    
    # Find CSS code block - try multiple patterns
    css_patterns = [
        r'```css\s*\n(.*?)\n```',
        r'```CSS\s*\n(.*?)\n```',
        r'<style[^>]*>(.*?)</style>',
        r'/\*.*?\*/.*?\{.*?\}',  # Look for CSS rules with comments
    ]
    
    for pattern in css_patterns:
        try:
            css_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if css_match and css_match.groups():
                css_code = css_match.group(1).strip()
                logger.info(f"      ✅ CSS code block found: {len(css_code)} characters")
                break
        except (IndexError, AttributeError) as e:
            logger.warning(f"      ⚠️  Error extracting CSS with pattern {pattern}: {e}")
            continue
    
    if not css_code:
        # Try to extract any CSS-like content as fallback
        try:
            # Look for CSS rules in the text
            css_rules = re.findall(r'[.#]?[a-zA-Z][a-zA-Z0-9_-]*\s*\{[^}]*\}', text)
            if css_rules:
                css_code = '\n'.join(css_rules)
                logger.info(f"      ✅ CSS-like content found: {len(css_code)} characters")
            else:
                # Look for any content that might be CSS
                css_sections = re.findall(r'\{[^}]*\}', text)
                if css_sections:
                    css_code = '\n'.join(css_sections)
                    logger.info(f"      ✅ CSS sections found: {len(css_code)} characters")
                else:
                    logger.warning("      ⚠️  No CSS code block found")
        except Exception as e:
            logger.warning(f"      ⚠️  Error extracting CSS-like content: {e}")
    
    # If still no content, try to extract from the entire response
    if not html_code and not css_code:
        logger.warning("      ⚠️  No code blocks found, trying to extract from full response")
        # Look for HTML structure in the entire response
        if '<html' in text.lower() or '<!doctype' in text.lower():
            # Extract everything that looks like HTML
            html_start = text.lower().find('<html')
            if html_start == -1:
                html_start = text.lower().find('<!doctype')
            
            if html_start != -1:
                html_code = text[html_start:]
                logger.info(f"      ✅ Extracted HTML from full response: {len(html_code)} characters")
    
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