import re
from typing import Set


def extract_css_selectors(css: str) -> Set[str]:
    """
    Extract all CSS selectors from CSS content.
    """
    selectors = set()
    
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    # Find all CSS rules
    rules = re.findall(r'([^{]+)\s*\{[^}]*\}', css)
    
    for rule in rules:
        # Split by comma to handle multiple selectors
        parts = rule.split(',')
        for part in parts:
            selector = part.strip()
            if selector:
                selectors.add(selector)
    
    return selectors


def extract_html_elements(html: str) -> Set[str]:
    """
    Extract all HTML element types and classes from HTML content.
    """
    elements = set()
    
    # Extract element types
    element_types = re.findall(r'<(\w+)', html)
    elements.update(element_types)
    
    # Extract class names
    class_names = re.findall(r'class=["\']([^"\']*)["\']', html)
    for class_list in class_names:
        classes = class_list.split()
        elements.update(classes)
    
    # Extract IDs
    id_names = re.findall(r'id=["\']([^"\']*)["\']', html)
    elements.update(id_names)
    
    return elements


def filter_css_from_html_and_css(html: str, css: str) -> str:
    """
    Filter CSS to only include selectors that are present in the HTML.
    """
    if not css or not html:
        return ""
    
    # Extract CSS selectors
    css_selectors = extract_css_selectors(css)
    
    # Extract HTML elements, classes, and IDs
    html_elements = extract_html_elements(html)
    
    # Filter CSS rules
    filtered_css = ""
    
    # Remove comments first
    css_no_comments = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    # Split CSS into rules
    rules = re.findall(r'([^{]+)\s*\{([^}]*)\}', css_no_comments)
    
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
    
    return filtered_css 