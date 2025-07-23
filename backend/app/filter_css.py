import re
from typing import Set
import logging

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


def filter_css_from_html_and_css(html: str, css: str) -> str:
    """
    Filter CSS to only include selectors that are present in the HTML.
    """
    logger.info("      → Starting CSS filtering process...")
    
    if not css or not html:
        logger.warning("      ⚠️  Empty CSS or HTML, returning empty string")
        return ""
    
    # Extract CSS selectors
    css_selectors = extract_css_selectors(css)
    
    # Extract HTML elements, classes, and IDs
    html_elements = extract_html_elements(html)
    
    # Filter CSS rules
    logger.info("      → Filtering CSS rules...")
    filtered_css = ""
    
    # Remove comments first
    css_no_comments = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    # Split CSS into rules
    rules = re.findall(r'([^{]+)\s*\{([^}]*)\}', css_no_comments)
    logger.info(f"      → Processing {len(rules)} CSS rules")
    
    kept_rules = 0
    for selector_part, properties in rules:
        # Split by comma to handle multiple selectors
        selector_list = selector_part.split(',')
        
        keep_rule = False
        for selector in selector_list:
            selector = selector.strip()
            
            # Check if selector matches any HTML element
            if selector in html_elements:
                keep_rule = True
                break
            
            # Check for class selectors
            if selector.startswith('.'):
                class_name = selector[1:]
                if class_name in html_elements:
                    keep_rule = True
                    break
            
            # Check for ID selectors
            if selector.startswith('#'):
                id_name = selector[1:]
                if id_name in html_elements:
                    keep_rule = True
                    break
        
        if keep_rule:
            filtered_css += f"{selector_part} {{\n{properties}\n}}\n\n"
            kept_rules += 1
    
    logger.info(f"      ✅ CSS filtering complete: {kept_rules}/{len(rules)} rules kept")
    return filtered_css 