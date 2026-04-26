#!/usr/bin/env python3
"""
Generate LLT (Living Legacy Translation) JSON scaffold.
Creates json/llt/{book}/{chapter}.json for every chapter.

The LLT verse text starts as a copy of WEB (to be replaced with actual LLT text).
Adds an empty footnotes array ready for heirloom-style AI insights.
"""

import os
import json
import copy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(BASE_DIR, "json", "web")
LLT_DIR = os.path.join(BASE_DIR, "json", "llt")


def main():
    total_chapters = 0
    
    for book_slug in sorted(os.listdir(WEB_DIR)):
        book_dir = os.path.join(WEB_DIR, book_slug)
        if not os.path.isdir(book_dir):
            continue
        
        output_book_dir = os.path.join(LLT_DIR, book_slug)
        os.makedirs(output_book_dir, exist_ok=True)
        
        for chapter_file in sorted(os.listdir(book_dir), key=lambda x: int(x.replace('.json', '')) if x.endswith('.json') else 0):
            if not chapter_file.endswith('.json'):
                continue
            
            web_path = os.path.join(book_dir, chapter_file)
            with open(web_path, "r", encoding="utf-8") as f:
                web_data = json.load(f)
            
            # Create LLT version
            llt_data = {
                "translation": "LLT",
                "translation_name": "Living Legacy Translation",
                "book": web_data["book"],
                "book_slug": web_data["book_slug"],
                "testament": web_data["testament"],
                "chapter": web_data["chapter"],
                "verse_count": web_data["verse_count"],
                "verses": copy.deepcopy(web_data["verses"]),
                "footnotes": []
            }
            
            # Add placeholder footnotes for key verses
            # (These will be replaced with actual AI-generated insights)
            # For now, add a sample for the first verse of each chapter
            if llt_data["verses"]:
                llt_data["footnotes"].append({
                    "verse": 1,
                    "content": "",
                    "author": "LLT Insight",
                    "year": 2026,
                    "is_public": True,
                    "type": "insight"
                })
            
            output_path = os.path.join(output_book_dir, chapter_file)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(llt_data, f, ensure_ascii=False, indent=2)
            
            total_chapters += 1
            if total_chapters % 100 == 0:
                print(f"  Scaffolded {total_chapters} chapters...")
    
    print(f"\nDone! Created LLT scaffold for {total_chapters} chapters.")
    print(f"Output: {LLT_DIR}")
    print("\nNext steps:")
    print("  1. Replace verse text with actual LLT translation")
    print("  2. Populate footnotes with AI-generated insights")


if __name__ == "__main__":
    main()
