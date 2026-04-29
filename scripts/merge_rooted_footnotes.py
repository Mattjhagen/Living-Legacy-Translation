#!/usr/bin/env python3
import json
import os
import re

# Paths
SOURCE_BIBLE_JSON = "/Users/matt/Rooted-Daily-static-site/data/bible.json"
TARGET_JSON_DIR = "/Users/matt/Living-Legacy-Translation/json/llt"

BOOK_NAMES = [
    "Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth",
    "1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra",
    "Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon",
    "Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos",
    "Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah",
    "Malachi","Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians",
    "2 Corinthians","Galatians","Ephesians","Philippians","Colossians",
    "1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon",
    "Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"
]

def clean_slug(name):
    return name.lower().replace(" ", "-")

def main():
    print(f"Loading source footnotes from {SOURCE_BIBLE_JSON}...")
    try:
        with open(SOURCE_BIBLE_JSON, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
    except Exception as e:
        print(f"Error loading source: {e}")
        return

    merged_count = 0
    skipped_count = 0

    for i, book_data in enumerate(source_data.get('books', [])):
        if i >= len(BOOK_NAMES):
            print(f"Warning: Book index {i} out of range for BOOK_NAMES")
            break
            
        book_name = BOOK_NAMES[i]
        book_slug = clean_slug(book_name)
        
        # Get footnotes for this book
        # Structure: book_data['footnotes'][chapter_str][verse_str] -> list of fns
        book_footnotes = book_data.get('footnotes', {})
        if not book_footnotes:
            continue
            
        print(f"Processing {book_name}... (Found {len(book_footnotes)} chapters with footnotes)")
        
        for chap_str, verses_fns in book_footnotes.items():
            chapter_num = int(chap_str)
            target_path = os.path.join(TARGET_JSON_DIR, book_slug, f"{chapter_num}.json")
            
            if not os.path.exists(target_path):
                # print(f"  Target not found: {target_path}")
                skipped_count += 1
                continue
            
            print(f"  Chapter {chapter_num}: Found {len(verses_fns)} verses with notes")
                
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    target_chapter = json.load(f)
            except Exception as e:
                print(f"  Error reading {target_path}: {e}")
                continue

            if 'footnotes' not in target_chapter:
                target_chapter['footnotes'] = []
            
            # Existing contents to avoid exact duplicates
            existing_contents = set(fn.get('content', '') for fn in target_chapter['footnotes'])
            
            new_fns_added = 0
            for v_str, fns_list in verses_fns.items():
                verse_num = int(v_str)
                for source_fn in fns_list:
                    if isinstance(source_fn, str):
                        content = source_fn.strip()
                    elif isinstance(source_fn, dict):
                        content = (source_fn.get("content") or source_fn.get("text") or 
                                   source_fn.get("note") or source_fn.get("body") or "").strip()
                    else:
                        content = ""
                    
                    if not content:
                        print(f"    Verse {verse_num}: Empty content in source footnote. Full object: {source_fn}")
                        continue
                        
                    if content in existing_contents:
                        # print(f"    Verse {verse_num}: Content already exists")
                        continue
                        
                    # Create LLT-style footnote
                    new_fn = {
                        "verse": verse_num,
                        "content": content,
                        "author": "Rooted Daily",
                        "year": 2026,
                        "is_public": True,
                        "type": "insight"
                    }
                    target_chapter['footnotes'].append(new_fn)
                    existing_contents.add(content)
                    new_fns_added += 1
                    merged_count += 1
            
            if new_fns_added > 0:
                # Sort footnotes by verse
                target_chapter['footnotes'].sort(key=lambda x: x.get('verse', 0))
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(target_chapter, f, indent=2, ensure_ascii=False)
                # print(f"  Merged {new_fns_added} notes into {book_name} {chapter_num}")

    print("\nMerge complete!")
    print(f"Total notes merged: {merged_count}")
    print(f"Chapters skipped (no target JSON): {skipped_count}")

if __name__ == "__main__":
    main()
