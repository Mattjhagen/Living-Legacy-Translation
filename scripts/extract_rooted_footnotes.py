#!/usr/bin/env python3
"""
Extract Translation Notes from the Rooted_Daily GitHub repo and inject them
into the LLT JSON files in the Living-Legacy-Translation project.

Fetches each chapter's HTML from GitHub raw content, parses the 
footnotes-section, and writes them into json/llt/{book}/{chapter}.json.
"""

import os
import sys
import json
import re
import time
from html.parser import HTMLParser
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LLT_DIR = os.path.join(BASE_DIR, "json", "llt")
GITHUB_RAW = "https://raw.githubusercontent.com/Mattjhagen/Rooted_Daily/main"

# Books that have chapter directories in the Rooted_Daily repo
# Based on the repo structure: bible/{book}/{chapter}/index.html
# AND some books at root level: {book}/{chapter}/index.html


class FootnoteParser(HTMLParser):
    """Parse HTML and extract footnotes from the footnotes-section."""
    
    def __init__(self):
        super().__init__()
        self.in_footnotes = False
        self.in_p = False
        self.in_strong = False
        self.footnotes = []
        self.current_note = ""
        self.current_strong = ""
        self.current_verse = None
        self.found_notes_header = False
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        
        if tag == "div" and "footnotes-section" in cls:
            self.in_footnotes = True
        
        if self.in_footnotes:
            if tag == "p":
                self.in_p = True
                self.current_note = ""
                self.current_strong = ""
                self.current_verse = None
                # Check for id like "fn1", "fn2" etc.
                note_id = attrs_dict.get("id", "")
                if note_id.startswith("fn"):
                    try:
                        self.current_verse = int(note_id[2:])
                    except ValueError:
                        pass
            elif tag == "strong":
                self.in_strong = True
    
    def handle_endtag(self, tag):
        if tag == "div" and self.in_footnotes:
            self.in_footnotes = False
        
        if self.in_footnotes and tag == "p" and self.in_p:
            self.in_p = False
            if self.current_note.strip():
                note_text = self.current_note.strip()
                # Remove leading sup number
                note_text = re.sub(r'^\d+\s*', '', note_text)
                
                self.footnotes.append({
                    "verse": self.current_verse or len(self.footnotes) + 1,
                    "content": note_text,
                    "term": self.current_strong.strip() if self.current_strong else "",
                    "author": "Rooted Translation",
                    "year": 2026,
                    "is_public": True,
                    "type": "translation_note"
                })
        
        if tag == "strong" and self.in_strong:
            self.in_strong = False
    
    def handle_data(self, data):
        if self.in_p and self.in_footnotes:
            self.current_note += data
        if self.in_strong and self.in_footnotes:
            self.current_strong += data


def fetch_chapter_html(book_slug, chapter):
    """Try to fetch chapter HTML from GitHub."""
    # Try bible/{book}/{chapter}/index.html first
    urls = [
        f"{GITHUB_RAW}/bible/{book_slug}/{chapter}/index.html",
        f"{GITHUB_RAW}/{book_slug}/{chapter}/index.html",
    ]
    
    for url in urls:
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8', errors='replace')
        except (HTTPError, URLError):
            continue
    
    return None


def extract_footnotes_from_html(html_content):
    """Extract footnotes from HTML content."""
    parser = FootnoteParser()
    parser.feed(html_content)
    
    # Also try regex-based extraction as fallback
    if not parser.footnotes:
        # Look for footnote patterns in the HTML
        # Pattern: <p id="fn1"><sup>1</sup> <strong>Term:</strong> Description</p>
        pattern = r'<p[^>]*id="fn(\d+)"[^>]*>\s*<sup>\d+</sup>\s*<strong>(.*?)</strong>\s*(.*?)</p>'
        matches = re.findall(pattern, html_content, re.DOTALL)
        for fn_num, term, content in matches:
            clean_content = re.sub(r'<[^>]+>', '', content).strip()
            clean_term = re.sub(r'<[^>]+>', '', term).strip()
            full_content = f"{clean_term} {clean_content}" if clean_term else clean_content
            parser.footnotes.append({
                "verse": int(fn_num),
                "content": full_content,
                "term": clean_term,
                "author": "Rooted Translation",
                "year": 2026,
                "is_public": True,
                "type": "translation_note"
            })
    
    return parser.footnotes


def get_books_from_llt():
    """Get list of books from existing LLT JSON files."""
    books = {}
    for book_slug in sorted(os.listdir(LLT_DIR)):
        book_dir = os.path.join(LLT_DIR, book_slug)
        if not os.path.isdir(book_dir):
            continue
        chapters = []
        for f in os.listdir(book_dir):
            if f.endswith('.json'):
                try:
                    chapters.append(int(f.replace('.json', '')))
                except ValueError:
                    pass
        books[book_slug] = sorted(chapters)
    return books


def main():
    books = get_books_from_llt()
    total_notes = 0
    chapters_with_notes = 0
    chapters_checked = 0
    failed = 0
    
    print(f"Scanning {len(books)} books for Translation Notes from Rooted_Daily repo...\n")
    
    for book_slug, chapters in books.items():
        book_notes_count = 0
        
        for chapter in chapters:
            chapters_checked += 1
            
            # Rate limiting
            if chapters_checked > 1:
                time.sleep(0.1)  # Be gentle with GitHub
            
            html = fetch_chapter_html(book_slug, chapter)
            if not html:
                failed += 1
                continue
            
            footnotes = extract_footnotes_from_html(html)
            
            if footnotes:
                # Update the LLT JSON file
                llt_path = os.path.join(LLT_DIR, book_slug, f"{chapter}.json")
                if os.path.exists(llt_path):
                    with open(llt_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    data["footnotes"] = footnotes
                    
                    with open(llt_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    chapters_with_notes += 1
                    book_notes_count += len(footnotes)
                    total_notes += len(footnotes)
            
            if chapters_checked % 50 == 0:
                print(f"  Checked {chapters_checked} chapters, found {total_notes} notes so far...")
        
        if book_notes_count > 0:
            print(f"  {book_slug}: {book_notes_count} notes")
    
    print(f"\n{'='*50}")
    print(f"Done! Extracted {total_notes} Translation Notes from {chapters_with_notes} chapters.")
    print(f"Checked {chapters_checked} total, {failed} not found in Rooted_Daily repo.")


if __name__ == "__main__":
    main()
