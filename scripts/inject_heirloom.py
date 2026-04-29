import os
import re

# This script scans the bible/ directory and injects the Heirloom study sheet 
# and necessary scripts into every chapter's index.html.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLE_DIR = os.path.join(BASE_DIR, "bible")

# Assets to inject (using relative paths for local/sub-path compatibility)
# Since chapters are at bible/book/chapter/index.html, we need ../../../ to reach assets/
SUPABASE_JS = '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'
REL_PREFIX = "../../../"
CAVEAT_FONT = '<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400..700&display=swap" rel="stylesheet">'
HEIRLOOM_CSS = f'<link rel="stylesheet" href="{REL_PREFIX}assets/css/heirloom.css">'
READER_JS = f'<script src="{REL_PREFIX}assets/js/bible-reader.js" defer></script>'
SWITCHER_JS = f'<script src="{REL_PREFIX}assets/js/translation-switcher.js" defer></script>'

VERSE_SHEET_HTML = """
  <!-- Verse Sheet (Bottom Pop-up) -->
  <div id="verse-sheet" class="verse-sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-actions-top">
      <button class="sheet-action-btn" id="sheet-copy" title="Copy"><i class="icon-copy"></i> Copy</button>
      <button class="sheet-action-btn" id="sheet-share" title="Share"><i class="icon-share"></i> Share</button>
      <button class="sheet-action-btn" id="sheet-highlight" title="Highlight"><i class="icon-highlighter"></i> Highlight</button>
      <button class="sheet-action-btn" id="sheet-save" title="Save to Journal"><i class="icon-bookmark"></i> Save</button>
    </div>
    <div id="sheet-content"></div>
  </div>
  <div id="sheet-overlay" class="sheet-overlay"></div>
"""

def clean_and_inject(html_path, book_slug, chapter):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # 1. Ensure Caveat font is in <head>
    if 'fonts.googleapis.com/css2?family=Caveat' not in content:
        content = content.replace('</head>', f'  {CAVEAT_FONT}\n</head>')
        modified = True

    # 2. Ensure HEIRLOOM_CSS is in <head> (remove old/incorrect versions)
    if HEIRLOOM_CSS not in content:
        # Remove any existing heirloom.css link (absolute or relative)
        content = re.sub(r'<link rel="stylesheet" href="[^"]*heirloom\.css">', '', content)
        content = content.replace('</head>', f'  {HEIRLOOM_CSS}\n</head>')
        modified = True

    # 3. Ensure VERSE_SHEET_HTML and scripts are at the end of <body>
    if READER_JS not in content or VERSE_SHEET_HTML not in content:
        # Remove old versions of these scripts
        content = re.sub(r'<script src="[^"]*translation-switcher\.js".*?></script>', '', content)
        content = re.sub(r'<script src="[^"]*bible-reader\.js".*?></script>', '', content)
        # Remove old verse sheet if exists
        content = re.sub(r'<!-- Verse Sheet.*?-->.*?<div id="verse-sheet".*?</div>.*?<div id="sheet-overlay".*?</div>', '', content, flags=re.DOTALL)
        
        # Inject new bundle
        content = content.replace('</body>', f'\n  {VERSE_SHEET_HTML}\n  {SWITCHER_JS}\n  {READER_JS}\n</body>')
        modified = True

    # 4. Ensure verse-container has data attributes
    if 'data-book-slug' not in content:
        # Handle variations of verse-container class
        content = re.sub(
            r'<div class=["\']verse-container["\']>',
            f'<div class="verse-container" data-book-slug="{book_slug}" data-chapter="{chapter}">',
            content
        )
        modified = True

    if modified:
        # Clean up any excessive newlines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    return modified

def main():
    processed = 0
    injected = 0

    if not os.path.exists(BIBLE_DIR):
        print(f"Error: {BIBLE_DIR} not found.")
        return

    for book in os.listdir(BIBLE_DIR):
        book_path = os.path.join(BIBLE_DIR, book)
        if not os.path.isdir(book_path): continue
        
        for chapter in os.listdir(book_path):
            chapter_path = os.path.join(book_path, chapter)
            if not os.path.isdir(chapter_path): continue
            
            index_path = os.path.join(chapter_path, "index.html")
            if os.path.exists(index_path):
                try:
                    if clean_and_inject(index_path, book, chapter):
                        injected += 1
                    processed += 1
                except Exception as e:
                    print(f"Error processing {index_path}: {e}")

    print(f"Done! Processed {processed} chapters, updated {injected}.")

if __name__ == "__main__":
    main()
