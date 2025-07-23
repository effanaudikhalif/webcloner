import re
from typing import Set
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_css_selectors(css: str) -> Set[str]:
    """
    Extract all CSS selectors from CSS content.
    """
    logger.info("      → Extracting CSS selectors...")
    selectors = set()
    
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    # Find all CSS rules
    rules = re.findall(r'([^{]+)\s*\{[^}]*\}', css)
    logger.info(f"      → Found {len(rules)} CSS rules")
    
    for rule in rules:
        # Split by comma to handle multiple selectors
        parts = rule.split(',')
        for part in parts:
            selector = part.strip()
            if selector:
                selectors.add(selector)
    
    logger.info(f"      ✅ Extracted {len(selectors)} unique selectors")
    return selectors


def extract_html_elements(html: str) -> Set[str]:
    """
    Extract all HTML element types and classes from HTML content.
    """
    logger.info("      → Extracting HTML elements and classes...")
    elements = set()
    
    # Extract element types
    element_types = re.findall(r'<(\w+)', html)
    elements.update(element_types)
    logger.info(f"      → Found {len(element_types)} HTML element types")
    
    # Extract class names
    class_names = re.findall(r'class=["\']([^"\']*)["\']', html)
    class_count = 0
    for class_list in class_names:
        classes = class_list.split()
        elements.update(classes)
        class_count += len(classes)
    logger.info(f"      → Found {class_count} CSS classes")
    
    # Extract IDs
    id_names = re.findall(r'id=["\']([^"\']*)["\']', html)
    elements.update(id_names)
    logger.info(f"      → Found {len(id_names)} HTML IDs")
    
    logger.info(f"      ✅ Total unique elements/classes/IDs: {len(elements)}")
    return elements


def filter_css_from_html_and_css(html_content: str, css_content: str) -> str:
    """
    Filter CSS to include only selectors that are present in the HTML content.
    """
    logger.info("      → Starting CSS filtering process...")
    
    if not css_content:
        logger.warning("      ⚠️  No CSS content provided")
        return ""
    
    # Extract CSS rules
    logger.info("      → Extracting CSS rules...")
    css_rules = re.findall(r'([^{}]+)\s*\{[^}]*\}', css_content)
    logger.info(f"      → Found {len(css_rules)} CSS rules")
    
    # Extract unique selectors
    selectors = set()
    for rule in css_rules:
        # Split by comma to handle multiple selectors
        rule_selectors = [s.strip() for s in rule.split(',')]
        for selector in rule_selectors:
            # Clean up the selector
            clean_selector = re.sub(r'[^\w\s\-\.#\[\]=]', '', selector).strip()
            if clean_selector:
                selectors.add(clean_selector)
    
    logger.info(f"      ✅ Extracted {len(selectors)} unique selectors")
    
    # Extract HTML elements and classes
    logger.info("      → Extracting HTML elements and classes...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get all element types
    elements = set()
    for tag in soup.find_all():
        elements.add(tag.name)
    logger.info(f"      → Found {len(elements)} HTML element types")
    
    # Get all CSS classes
    classes = set()
    for tag in soup.find_all(class_=True):
        class_list = tag.get('class', [])
        if isinstance(class_list, list):
            classes.update(class_list)
        else:
            classes.add(class_list)
    logger.info(f"      → Found {len(classes)} CSS classes")
    
    # Get all IDs
    ids = set()
    for tag in soup.find_all(id=True):
        ids.add(tag.get('id'))
    logger.info(f"      → Found {len(ids)} HTML IDs")
    
    # Combine all HTML selectors
    html_selectors = elements.union(classes).union(ids)
    logger.info(f"      ✅ Total unique elements/classes/IDs: {len(html_selectors)}")
    
    # Filter CSS rules - be less aggressive to preserve more styling
    logger.info("      → Filtering CSS rules...")
    filtered_rules = []
    total_rules = len(css_rules)
    
    # Priority selectors that we definitely want to keep
    priority_selectors = [
        'body', 'html', '*', 'head', 'meta', 'title', 'div', 'span', 'p', 
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img', 'ul', 'ol', 'li', 
        'nav', 'header', 'footer', 'main', 'section', 'article', 'aside',
        'button', 'input', 'form', 'label', 'table', 'tr', 'td', 'th'
    ]
    
    # Common layout and styling patterns
    layout_patterns = [
        'container', 'wrapper', 'header', 'footer', 'nav', 'menu', 
        'button', 'btn', 'card', 'grid', 'flex', 'row', 'col', 'sidebar',
        'content', 'main', 'hero', 'banner', 'section', 'block', 'page',
        'site', 'web', 'theme', 'style', 'layout', 'design'
    ]
    
    for rule in css_rules:
        # Check if any selector in this rule matches HTML content
        rule_selectors = [s.strip() for s in rule.split(',')]
        should_keep = False
        
        for selector in rule_selectors:
            # Clean the selector
            clean_selector = re.sub(r'[^\w\s\-\.#\[\]=]', '', selector).strip()
            
            # Check if this selector matches any HTML element/class/id
            if clean_selector in html_selectors:
                should_keep = True
                break
            
            # Keep priority selectors
            if clean_selector in priority_selectors:
                should_keep = True
                break
            
            # Keep media queries and keyframes
            if clean_selector.startswith('@media') or clean_selector.startswith('@keyframes') or ':' in clean_selector:
                should_keep = True
                break
            
            # Keep common layout patterns
            if any(pattern in clean_selector for pattern in layout_patterns):
                should_keep = True
                break
            
            # Keep any selector that might be important (less aggressive filtering)
            if len(clean_selector) > 2 and not clean_selector.startswith('_'):
                should_keep = True
                break
        
        if should_keep:
            # Find the complete CSS rule (including the declaration block)
            rule_start = css_content.find(rule)
            if rule_start != -1:
                # Find the closing brace for this rule
                brace_count = 0
                rule_end = rule_start
                for i in range(rule_start, len(css_content)):
                    if css_content[i] == '{':
                        brace_count += 1
                    elif css_content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            rule_end = i + 1
                            break
                
                if rule_end > rule_start:
                    complete_rule = css_content[rule_start:rule_end]
                    filtered_rules.append(complete_rule)
    
    logger.info(f"      ✅ CSS filtering complete: {len(filtered_rules)}/{total_rules} rules kept")
    
    # Combine filtered rules and limit total size
    filtered_css = '\n'.join(filtered_rules)
    
    # If still too large, truncate to reasonable size but keep more than before
    if len(filtered_css) > 100000:  # 100KB limit (increased from 50KB)
        filtered_css = filtered_css[:100000]
        logger.info(f"      ⚠️  CSS truncated to 100KB due to size limits")
    
    return filtered_css 