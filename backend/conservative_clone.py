#!/usr/bin/env python3
"""
Conservative Website Cloner

This script uses the conservative approach to clone websites,
preserving the original HTML structure and CSS exactly as-is,
only making minimal technical fixes needed for standalone functionality.
"""

import sys
import asyncio
from pathlib import Path
from section_processor import SectionProcessor

def conservative_clone_website(url: str, output_dir: str = "generated") -> None:
    """
    Clone a website using the conservative approach.
    
    Args:
        url: The website URL to clone
        output_dir: Directory to save the cloned files
    """
    print(f"🔄 Starting conservative clone of: {url}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Initialize processor
    processor = SectionProcessor()
    
    # Perform conservative clone
    result = processor.conservative_clone(url)
    
    # Save the cloned website
    html_file = output_path / "conservative_clone.html"
    html_file.write_text(result["combined_html"])
    
    print(f"✅ Conservative clone completed!")
    print(f"📁 Saved to: {html_file}")
    print(f"📊 Method: {result['method']}")
    print(f"📏 HTML size: {result['scraped_html_length']:,} characters")
    print(f"🎨 CSS size: {result['scraped_css_length']:,} characters")
    print(f"🔗 Original URL: {result['original_url']}")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        print("Usage: python conservative_clone.py <url>")
        print("Example: python conservative_clone.py https://www.bu.edu")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        conservative_clone_website(url)
    except Exception as e:
        print(f"❌ Error during conservative clone: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 