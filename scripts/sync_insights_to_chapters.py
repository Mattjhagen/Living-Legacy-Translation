#!/usr/bin/env python3
"""
Sync insights from data/insights/<book>.json into json/llt/<book>/<chapter>.json
Converts insights format to footnotes format expected by the reader.
"""

import json
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
INSIGHTS_DIR = ROOT / 'data' / 'insights'
LLT_DIR = ROOT / 'json' / 'llt'

def book_to_slug(book_name):
    """Convert book name to slug format"""
    mapping = {
        "1 Samuel": "1-samuel", "2 Samuel": "2-samuel",
        "1 Kings": "1-kings", "2 Kings": "2-kings",
        "1 Chronicles": "1-chronicles", "2 Chronicles": "2-chronicles",
        "Song of Solomon": "song-of-solomon",
        "1 Corinthians": "1-corinthians", "2 Corinthians": "2-corinthians",
        "1 Thessalonians": "1-thessalonians", "2 Thessalonians": "2-thessalonians",
        "1 Timothy": "1-timothy", "2 Timothy": "2-timothy",
        "1 Peter": "1-peter", "2 Peter": "2-peter",
        "1 John": "1-john", "2 John": "2-john", "3 John": "3-john",
    }
    if book_name in mapping:
        return mapping[book_name]
    return book_name.lower().replace(' ', '-')

def sync_book(book_name, book_slug=None):
    """Sync insights for one book into its chapter JSONs"""
    if book_slug is None:
        book_slug = book_to_slug(book_name)

    insights_file = INSIGHTS_DIR / f'{book_slug}.json'
    if not insights_file.exists():
        print(f"No insights file for {book_name} at {insights_file}")
        return

    # Load all insights for this book
    with open(insights_file) as f:
        insights = json.load(f)

    # Group by chapter
    by_chapter = {}
    for entry in insights:
        ch = entry['chapter']
        if ch not in by_chapter:
            by_chapter[ch] = []
        by_chapter[ch].append(entry)

    print(f"\n{book_name}: Found {len(insights)} insights across {len(by_chapter)} chapters")

    # Update each chapter file
    for chapter_num, chapter_insights in by_chapter.items():
        chapter_file = LLT_DIR / book_slug / f'{chapter_num}.json'
        if not chapter_file.exists():
            print(f"  Chapter {chapter_num}: file not found at {chapter_file}")
            continue

        # Load chapter data
        with open(chapter_file) as f:
            chapter_data = json.load(f)

        # Remove old insight footnotes (keep only non-insight ones)
        old_footnotes = chapter_data.get('footnotes', [])
        kept_footnotes = [fn for fn in old_footnotes if fn.get('type') != 'insight']

        # Convert insights to footnotes format
        new_footnotes = []
        for insight in chapter_insights:
            # Extract just "LLT Insight" from "LLT Insight (2026)"
            attribution = insight['attribution']
            author = attribution.split(' (')[0] if ' (' in attribution else attribution

            new_footnotes.append({
                'verse': insight['verse'],
                'content': insight['note'],
                'author': author,
                'year': 2026,
                'is_public': True,
                'type': 'insight'
            })

        # Combine: kept non-insights + new insights, sorted by verse
        chapter_data['footnotes'] = sorted(kept_footnotes + new_footnotes, key=lambda x: x['verse'])

        # Write back
        with open(chapter_file, 'w') as f:
            json.dump(chapter_data, f, indent=2, ensure_ascii=False)

        print(f"  Chapter {chapter_num}: Updated with {len(new_footnotes)} insights")

def main():
    import sys

    if len(sys.argv) > 1:
        # Sync specific books
        for book_name in sys.argv[1:]:
            sync_book(book_name)
    else:
        # Sync all books that have insights
        for insights_file in sorted(INSIGHTS_DIR.glob('*.json')):
            if insights_file.name.startswith('_'):
                continue  # Skip _progress.json
            book_slug = insights_file.stem
            # Try to derive book name from slug (reverse mapping)
            # For now, just use the slug as-is
            sync_book(book_slug, book_slug=book_slug)

if __name__ == '__main__':
    main()
