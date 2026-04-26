#!/usr/bin/env python3
"""
Inject heirloom CSS, Caveat font, and translation switcher JS
into all chapter-level HTML pages.

Adds:
  - Google Fonts: Caveat (handwritten font for footnotes)
  - assets/css/heirloom.css (heirloom styles)
  - assets/js/translation-switcher.js (client-side switcher)
  - data attributes for book slug and chapter number

Only targets chapter pages (bible/{book}/{chapter}/index.html),
not the book index pages or root pages.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLE_DIR = os.path.join(BASE_DIR, "bible")

# Assets to inject (using base href="/", so paths are from root)
CAVEAT_FONT = '<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400..700&display=swap" rel="stylesheet">'
HEIRLOOM_CSS = '<link rel="stylesheet" href="assets/css/heirloom.css">'
SWITCHER_JS = '<script src="assets/js/translation-switcher.js" defer></script>'

def get_book_slug_and_chapter(html_path):
    """Extract book slug and chapter from the file path."""
    # path: .../bible/{book-slug}/{chapter}/index.html
    parts = html_path.replace(BIBLE_DIR, '').strip('/').split('/')
    if len(parts) >= 2:
        book_slug = parts[0]
        try:
            chapter = int(parts[1])
            return book_slug, chapter
        except ValueError:
            return None, None
    return None, None


def inject_into_chapter(html_path, book_slug, chapter):
    """Inject assets into a chapter HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 1. Inject Caveat font (after existing Lora font link)
    if 'Caveat' not in content:
        content = content.replace(
            'family=Lora:ital,wght@0,400..700;1,400..700&display=swap" rel="stylesheet">',
            'family=Lora:ital,wght@0,400..700;1,400..700&display=swap" rel="stylesheet">\n  ' + CAVEAT_FONT
        )
        modified = True
    
    # 2. Inject heirloom CSS (before </head>)
    if 'heirloom.css' not in content:
        content = content.replace('</head>', '  ' + HEIRLOOM_CSS + '\n</head>')
        modified = True
    
    # 3. Inject switcher JS (before </body>)
    if 'translation-switcher.js' not in content:
        content = content.replace('</body>', '  ' + SWITCHER_JS + '\n</body>')
        modified = True
    
    # 4. Add data attributes to verse container for JS to pick up
    if 'data-book-slug' not in content:
        # Add data attributes to the verse-container div
        content = content.replace(
            '<div class="verse-container">',
            '<div class="verse-container" data-book-slug="' + book_slug + '" data-chapter="' + str(chapter) + '">'
        )
        # Also try the class with quotes variation
        content = content.replace(
            "class=\"verse-container\">",
            'class="verse-container" data-book-slug="' + book_slug + '" data-chapter="' + str(chapter) + '">',
        )
        modified = True
    
    if modified:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return modified


def main():
    total = 0
    injected = 0
    
    for book_slug in sorted(os.listdir(BIBLE_DIR)):
        book_dir = os.path.join(BIBLE_DIR, book_slug)
        if not os.path.isdir(book_dir) or book_slug.startswith('.'):
            continue
        
        for chapter_name in sorted(os.listdir(book_dir)):
            chapter_dir = os.path.join(book_dir, chapter_name)
            if not os.path.isdir(chapter_dir):
                continue
            
            html_path = os.path.join(chapter_dir, 'index.html')
            if not os.path.exists(html_path):
                continue
            
            try:
                chapter_num = int(chapter_name)
            except ValueError:
                continue
            
            total += 1
            if inject_into_chapter(html_path, book_slug, chapter_num):
                injected += 1
            
            if total % 200 == 0:
                print(f"  Processed {total} chapters...")
    
    print(f"\nDone! Processed {total} chapter pages, injected into {injected}.")


if __name__ == "__main__":
    main()
