#!/usr/bin/env python3
"""
Inject apple-touch-icon and manifest link into all HTML pages.
This ensures the app has a high-quality icon when added to the iOS Home Screen.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLE_DIR = os.path.join(BASE_DIR, "bible")

# Tags to inject
APPLE_ICON = '<link rel="apple-touch-icon" href="assets/images/favicon.png">'
MANIFEST_LINK = '<link rel="manifest" href="manifest.json">'
IOS_META = """  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-title" content="LLT Bible">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">"""

def process_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # Inject apple-touch-icon after favicon
    if 'apple-touch-icon' not in content:
        if '<link rel="icon" type="image/png" href="assets/images/favicon.png">' in content:
            content = content.replace(
                '<link rel="icon" type="image/png" href="assets/images/favicon.png">',
                '<link rel="icon" type="image/png" href="assets/images/favicon.png">\n  ' + APPLE_ICON
            )
            modified = True
        elif '<link rel="icon" href="assets/images/favicon.png">' in content:
             content = content.replace(
                '<link rel="icon" href="assets/images/favicon.png">',
                '<link rel="icon" href="assets/images/favicon.png">\n  ' + APPLE_ICON
            )
             modified = True

    # Inject manifest link before </head>
    if 'manifest.json' not in content:
        content = content.replace('</head>', '  ' + MANIFEST_LINK + '\n</head>')
        modified = True

    # Inject iOS meta tags before </head>
    if 'apple-mobile-web-app-capable' not in content:
        content = content.replace('</head>', IOS_META + '\n</head>')
        modified = True
        
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return modified

def main():
    # 1. Process root index.html
    root_index = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(root_index):
        if process_html_file(root_index):
            print(f"Updated {root_index}")

    # 2. Process bible/index.html
    bible_index = os.path.join(BIBLE_DIR, "index.html")
    if os.path.exists(bible_index):
        if process_html_file(bible_index):
            print(f"Updated {bible_index}")

    # 3. Process all chapter pages
    total = 0
    updated = 0
    
    for root, dirs, files in os.walk(BIBLE_DIR):
        for file in files:
            if file == "index.html":
                filepath = os.path.join(root, file)
                # Skip the one we already did
                if filepath == bible_index:
                    continue
                
                total += 1
                if process_html_file(filepath):
                    updated += 1
                
                if total % 500 == 0:
                    print(f"  Processed {total} pages...")

    print(f"\nDone! Processed {total} additional pages, updated {updated}.")

if __name__ == "__main__":
    main()
