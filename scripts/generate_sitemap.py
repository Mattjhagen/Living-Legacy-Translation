#!/usr/bin/env python3
"""
Generate a comprehensive sitemap.xml for the Living Legacy Translation.
Includes the home page, bible index, book indices, and all chapter pages.
"""

import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://llt.rootedapp.space"
BIBLE_DIR = os.path.join(BASE_DIR, "bible")

def get_url_entry(path, priority="0.8", changefreq="monthly"):
    lastmod = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/{path}".rstrip('/') + '/'
    return f"""  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>\n"""

def main():
    entries = []
    
    # 1. Root and Bible Index
    entries.append(get_url_entry("", priority="1.0", changefreq="weekly"))
    entries.append(get_url_entry("bible", priority="1.0", changefreq="weekly"))
    
    # 2. Iterate through books
    for book_slug in sorted(os.listdir(BIBLE_DIR)):
        book_path = os.path.join(BIBLE_DIR, book_slug)
        if not os.path.isdir(book_path) or book_slug.startswith('.'):
            continue
        
        # Book index
        entries.append(get_url_entry(f"bible/{book_slug}", priority="0.9"))
        
        # Chapters
        for chapter in sorted(os.listdir(book_path), key=lambda x: int(x) if x.isdigit() else 0):
            chapter_path = os.path.join(book_path, chapter)
            if not os.path.isdir(chapter_path) or not chapter.isdigit():
                continue
            
            if os.path.exists(os.path.join(chapter_path, "index.html")):
                entries.append(get_url_entry(f"bible/{book_slug}/{chapter}", priority="0.8"))

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(entries)}
</urlset>
"""
    
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    
    print(f"Generated sitemap with {len(entries)} URLs at {sitemap_path}")

if __name__ == "__main__":
    main()
