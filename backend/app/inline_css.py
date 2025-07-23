import re
from typing import Tuple


def extract_code_blocks(text: str) -> Tuple[str, str]:
    """
    Extract HTML and CSS code blocks from Claude's response.
    """
    html_code = ""
    css_code = ""
    
    # Find HTML code block
    html_match = re.search(r'```html\s*\n(.*?)\n```', text, re.DOTALL)
    if html_match:
        html_code = html_match.group(1).strip()
    
    # Find CSS code block
    css_match = re.search(r'```css\s*\n(.*?)\n```', text, re.DOTALL)
    if css_match:
        css_code = css_match.group(1).strip()
    
    return html_code, css_code


def inline_css(html: str, css: str) -> str:
    """
    Inline CSS into HTML by adding a <style> tag in the <head>.
    """
    if not html or not css:
        return html
    
    # Check if HTML has a head tag
    if '<head>' in html:
        # Insert style tag in head
        style_tag = f'<style>\n{css}\n</style>'
        html = html.replace('<head>', f'<head>\n{style_tag}')
    else:
        # If no head tag, add one with style
        style_tag = f'<head>\n<style>\n{css}\n</style>\n</head>'
        html = html.replace('<html>', f'<html>\n{style_tag}')
    
    return html


def combine_html_and_css(html: str, css: str) -> str:
    """
    Combine HTML and CSS into a single HTML document.
    """
    if not html:
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
    else:
        # Inline CSS into existing HTML
        html = inline_css(html, css)
    
    return html 