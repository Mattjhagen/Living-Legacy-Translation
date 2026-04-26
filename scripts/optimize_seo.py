#!/usr/bin/env python3
"""
Standardize SEO meta tags and Schema.org JSON-LD across all HTML pages.
Implements the 'MetaManager' logic for static pages.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLE_DIR = os.path.join(BASE_DIR, "bible")

def process_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 1. Update Title and Meta Description branding
    if "Living Legacy Translation" in content:
        content = content.replace("Living Legacy Translation", "Rooted Daily Bible (LLT)")
        modified = True
        
    # 2. Add/Update Open Graph tags for better social sharing
    if 'property="og:site_name"' not in content:
        content = content.replace('</head>', '  <meta property="og:site_name" content="Rooted Daily">\n</head>')
        modified = True

    if 'name="twitter:image"' not in content:
        # Using the favicon as a fallback image if no other image is specified
        content = content.replace('</head>', '  <meta name="twitter:image" content="https://llt.rootedapp.space/assets/images/favicon.png">\n</head>')
        modified = True

    # 3. Enhance JSON-LD Schema.org
    # Look for existing Book/Chapter schema and add potentialAction if missing
    if '"@type": "Chapter"' in content and '"potentialAction"' not in content:
        read_action = ', "potentialAction": {"@type": "ReadAction", "target": "https://llt.rootedapp.space/bible"}'
        content = content.replace('}]}', '}]' + read_action + '}')
        modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return modified

def main():
    total = 0
    updated = 0
    
    # Root index
    root_index = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(root_index):
        if process_html_file(root_index):
            print(f"Updated {root_index}")

    # Bible index
    bible_index = os.path.join(BIBLE_DIR, "index.html")
    if os.path.exists(bible_index):
        if process_html_file(bible_index):
            print(f"Updated {bible_index}")

    # Chapter pages
    for root, dirs, files in os.walk(BIBLE_DIR):
        for file in files:
            if file == "index.html":
                filepath = os.path.join(root, file)
                if filepath == bible_index:
                    continue
                
                total += 1
                if process_html_file(filepath):
                    updated += 1
                
                if total % 500 == 0:
                    print(f"  Processed {total} pages...")

    print(f"\nSEO Optimization Done! Processed {total} pages, updated {updated}.")

if __name__ == "__main__":
    main()
