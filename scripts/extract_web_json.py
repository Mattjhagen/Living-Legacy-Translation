#!/usr/bin/env python3
"""
Extract WEB verse data from existing HTML chapter pages into structured JSON.
Creates json/web/{book}/{chapter}.json for every chapter.
"""

import os
import re
import json
from html.parser import HTMLParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLE_DIR = os.path.join(BASE_DIR, "bible")
OUTPUT_DIR = os.path.join(BASE_DIR, "json", "web")

class VerseExtractor(HTMLParser):
    """Parse chapter HTML and extract verse numbers + text."""
    
    def __init__(self):
        super().__init__()
        self.verses = []
        self.in_verse_num = False
        self.in_verse_text = False
        self.current_num = ""
        self.current_text = ""
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        if tag == "span" and "verse-num" in cls:
            self.in_verse_num = True
            self.current_num = ""
        elif tag == "span" and "verse-text" in cls:
            self.in_verse_text = True
            self.current_text = ""
    
    def handle_endtag(self, tag):
        if tag == "span" and self.in_verse_num:
            self.in_verse_num = False
        elif tag == "span" and self.in_verse_text:
            self.in_verse_text = False
            if self.current_num.strip():
                self.verses.append({
                    "number": int(self.current_num.strip()),
                    "text": self.current_text.strip()
                })
    
    def handle_data(self, data):
        if self.in_verse_num:
            self.current_num += data
        elif self.in_verse_text:
            self.current_text += data


def extract_book_info(html_content):
    """Extract book name and chapter number from the HTML title."""
    title_match = re.search(r'<title>(.*?)\|', html_content)
    if title_match:
        parts = title_match.group(1).strip().split()
        # e.g., "Genesis 1" or "1 Samuel 5"
        # Find the last number which is the chapter
        chapter_num = parts[-1]
        book_name = " ".join(parts[:-1])
        return book_name, int(chapter_num)
    return None, None


def get_testament(book_slug, books_index):
    """Look up testament from books index."""
    for book in books_index.get("books", []):
        if book["slug"] == book_slug:
            return book.get("testament", "OT")
    return "OT"


def process_chapter(html_path, book_slug, chapter_num, books_index):
    """Process a single chapter HTML file and return structured data."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    book_name, ch_num = extract_book_info(content)
    if not book_name:
        book_name = book_slug.replace("-", " ").title()
        ch_num = chapter_num
    
    parser = VerseExtractor()
    parser.feed(content)
    
    testament = get_testament(book_slug, books_index)
    
    return {
        "translation": "WEB",
        "translation_name": "World English Bible",
        "book": book_name,
        "book_slug": book_slug,
        "testament": testament,
        "chapter": ch_num or chapter_num,
        "verse_count": len(parser.verses),
        "verses": parser.verses
    }


def main():
    # Load books index for metadata
    books_index_path = os.path.join(BASE_DIR, "json", "books_index.json")
    books_index = {}
    if os.path.exists(books_index_path):
        with open(books_index_path, "r", encoding="utf-8") as f:
            books_index = json.load(f)
    
    total_chapters = 0
    total_verses = 0
    
    # Iterate through all book directories
    for book_slug in sorted(os.listdir(BIBLE_DIR)):
        book_dir = os.path.join(BIBLE_DIR, book_slug)
        if not os.path.isdir(book_dir) or book_slug.startswith("."):
            continue
        
        # Skip the bible/index.html (it's the book listing page)
        output_book_dir = os.path.join(OUTPUT_DIR, book_slug)
        os.makedirs(output_book_dir, exist_ok=True)
        
        for chapter_name in sorted(os.listdir(book_dir), key=lambda x: int(x) if x.isdigit() else 0):
            chapter_dir = os.path.join(book_dir, chapter_name)
            if not os.path.isdir(chapter_dir):
                continue
            
            html_path = os.path.join(chapter_dir, "index.html")
            if not os.path.exists(html_path):
                continue
            
            try:
                chapter_num = int(chapter_name)
            except ValueError:
                continue
            
            data = process_chapter(html_path, book_slug, chapter_num, books_index)
            
            output_path = os.path.join(output_book_dir, f"{chapter_num}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            total_chapters += 1
            total_verses += len(data["verses"])
            
            if total_chapters % 100 == 0:
                print(f"  Processed {total_chapters} chapters...")
    
    print(f"\nDone! Extracted {total_chapters} chapters with {total_verses} total verses.")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
