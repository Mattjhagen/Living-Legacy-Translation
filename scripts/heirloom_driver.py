#!/usr/bin/env python3
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path('/home/matt/PurePulse/Rooted-Daily-static-site/Living-Legacy-Translation')
PROGRESS_PATH = ROOT / 'data' / 'insights' / '_progress.json'
INSIGHTS_DIR = ROOT / 'data' / 'insights'
TMP_DIR = INSIGHTS_DIR / '.tmp'
QUARANTINE_DIR = ROOT / 'data' / 'insights-quarantine'
LLT_DIR = ROOT / 'json' / 'llt'
LOG_PATH = ROOT / 'heirloom.log'

# Bedrock env
BEDROCK_ENV = os.environ.copy()
BEDROCK_ENV['CLAUDE_CODE_USE_BEDROCK'] = '1'
BEDROCK_ENV['AWS_REGION'] = BEDROCK_ENV.get('AWS_REGION', 'us-east-1')
BEDROCK_ENV['ANTHROPIC_MODEL'] = BEDROCK_ENV.get('ANTHROPIC_MODEL', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')
BEDROCK_ENV['ANTHROPIC_SMALL_FAST_MODEL'] = BEDROCK_ENV.get('ANTHROPIC_SMALL_FAST_MODEL', BEDROCK_ENV['ANTHROPIC_MODEL'])

# Canonical order
CANONICAL = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy",
    "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation"
]

def book_to_slug(book):
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
    if book in mapping:
        return mapping[book]
    return book.lower().replace(' ', '-')

def slug_to_dirname(slug):
    return slug

def count_verses_in_chapter(book, chapter):
    slug = book_to_slug(book)
    chapter_path = LLT_DIR / slug_to_dirname(slug) / f'{chapter}.json'
    if not chapter_path.exists():
        raise FileNotFoundError(f"Chapter file not found: {chapter_path}")
    with open(chapter_path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        if 'verses' in data:
            verses = data['verses']
            if isinstance(verses, list):
                return len(verses)
    elif isinstance(data, list):
        return len(data)
    return 0

def compute_coverage_and_unique(entries, book, chapter):
    covered_verses = set()
    for e in entries:
        v = e.get('verse')
        ve = e.get('verseEnd')
        if v is not None and ve is not None:
            for vv in range(int(v), int(ve) + 1):
                covered_verses.add(vv)
        elif v is not None:
            covered_verses.add(int(v))
    try:
        expected_count = count_verses_in_chapter(book, chapter)
    except Exception as ex:
        raise Exception(f"Could not determine expected verse count: {ex}")
    notes = [e.get('note', '') for e in entries]
    if not notes:
        unique_ratio = 0.0
    else:
        unique_ratio = len(set(notes)) / len(notes)
    return {
        'covered_count': len(covered_verses),
        'expected_count': expected_count,
        'coverage_ok': len(covered_verses) == expected_count,
        'unique_ratio': unique_ratio,
        'entry_count': len(entries)
    }

def load_progress():
    with open(PROGRESS_PATH) as f:
        return json.load(f)

def save_progress(progress):
    with open(PROGRESS_PATH, 'w') as f:
        json.dump(progress, f, indent=2)

def log_line(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')
        f.flush()

def is_auth_error(text):
    t = text.lower()
    if 'could not load aws credentials' in t:
        return True
    if 'session has expired' in t:
        return True
    if 'expired token' in t:
        return True
    if 'no credentials' in t:
        return True
    if 'unable to locate credentials' in t:
        return True
    if 'unauthorized' in t and 'aws' in t:
        return True
    return False

def is_quota_error(text):
    t = text.lower()
    if 'limit' in t and ('usage' in t or 'quota' in t or 'rate' in t):
        return True
    if 'free usage limit' in t:
        return True
    if 'throttl' in t:
        return True
    if 'too many requests' in t:
        return True
    return False

def process_chapter(book, chapter, progress):
    slug = book_to_slug(book)
    tmp_path = TMP_DIR / f'{slug}-{chapter}.json'
    book_json_path = INSIGHTS_DIR / f'{slug}.json'
    
    chapter_prompt = f'''Read chapter {chapter} of {book} from this project's LLT verse data. Compose a Heirloom Insight for EVERY verse and write ONLY a JSON array to {tmp_path}. Entry shape:
{{"ref": "{book} {chapter}:<V>", "chapter": {chapter}, "verse": <V>, "kind": "reflection", "note": "...", "attribution": "LLT Insight (2026)"}}.
Voice: a beloved grandparent's margin handwriting — warm, plainspoken, humble, Christ-centered. 2–4 sentences per note, specific to THIS verse: its people, place, action, or words. Never generic filler that could sit on any verse.
Kinds: "reflection" (default); "text" when the verse has a real anchor — a place, custom, or a cross-reference citation you are sure of (aim ~1 in 6); "echo" at most ONE per chapter, framed as a modern echo ("readers today hear an echo…"), never as fulfilled prediction, with "asOf": "2026-10".
Genealogy/list verses may share one range entry ("verseEnd"). Plain verses get short honest notes. No medical/financial advice, no denominational polemics, never contradict the plain sense of the text. Output the file, then reply with one line: chapter, entries written, done.'''
    
    for attempt in range(1, 4):
        try:
            start_time = time.time()
            result = subprocess.run(
                ['claude', '-p', '--model', 'haiku', '--dangerously-skip-permissions', chapter_prompt],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=600,
                env=BEDROCK_ENV
            )
            elapsed = time.time() - start_time
            stdout_text = result.stdout.decode('utf-8', errors='replace')
            stderr_text = result.stderr.decode('utf-8', errors='replace')
            combined = stdout_text + '\n' + stderr_text
            
            if result.returncode != 0:
                if is_auth_error(combined):
                    raise Exception(f"AUTH_ERROR: {combined[:300]}")
                if is_quota_error(combined):
                    raise Exception(f"QUOTA_ERROR: {combined[:300]}")
                raise Exception(f"claude failed with code {result.returncode}: {combined[:300]}")
            
            if not tmp_path.exists():
                raise Exception("Temp file not created")
            
            with open(tmp_path) as f:
                entries = json.load(f)
            
            if not isinstance(entries, list):
                raise Exception("Entries is not a list")
            
            stats = compute_coverage_and_unique(entries, book, chapter)
            if not stats['coverage_ok']:
                raise Exception(f"Coverage failed: got {stats['covered_count']} verses, expected {stats['expected_count']}")
            if stats['unique_ratio'] < 0.90:
                raise Exception(f"Unique ratio too low: {stats['unique_ratio']}")
            
            if book_json_path.exists():
                with open(book_json_path) as f:
                    book_data = json.load(f)
                if not isinstance(book_data, list):
                    book_data = []
            else:
                book_data = []
            
            book_data = [e for e in book_data if e.get('chapter') != chapter]
            book_data.extend(entries)
            book_data.sort(key=lambda x: (x.get('chapter', 0), x.get('verse', 0)))
            
            with open(book_json_path, 'w') as f:
                json.dump(book_data, f, indent=2)
            
            try:
                tmp_path.unlink()
            except Exception:
                pass
            
            if book not in progress['completedChapters']:
                progress['completedChapters'][book] = []
            if chapter not in progress['completedChapters'][book]:
                progress['completedChapters'][book].append(chapter)
                progress['completedChapters'][book].sort()
            # Remove from skipped if present
            if book in progress.get('skipped', {}):
                progress['skipped'][book] = [s for s in progress['skipped'][book] if s.get('chapter') != chapter]
                if not progress['skipped'][book]:
                    del progress['skipped'][book]
            save_progress(progress)
            
            log_line(f"{book} {chapter}: entries={stats['entry_count']} unique_ratio={stats['unique_ratio']:.3f} time={elapsed:.1f}s OK")
            return True
            
        except Exception as e:
            err_str = str(e)
            log_line(f"{book} {chapter}: attempt {attempt} failed: {err_str}")
            if err_str.startswith('AUTH_ERROR') or err_str.startswith('QUOTA_ERROR'):
                # Propagate auth/quota to halt
                raise
            if attempt < 3:
                time.sleep(60)
            else:
                if 'skipped' not in progress:
                    progress['skipped'] = {}
                if book not in progress['skipped']:
                    progress['skipped'][book] = []
                # Avoid duplicates
                exists = any(s.get('chapter') == chapter for s in progress['skipped'][book])
                if not exists:
                    progress['skipped'][book].append({'chapter': chapter, 'error': err_str})
                save_progress(progress)
                log_line(f"{book} {chapter}: SKIPPED after 3 attempts")
                return False

def check_book_gate(book, progress):
    slug = book_to_slug(book)
    book_json_path = INSIGHTS_DIR / f'{slug}.json'
    if not book_json_path.exists():
        return False, "File does not exist"
    try:
        with open(book_json_path) as f:
            book_data = json.load(f)
    except Exception as e:
        return False, f"JSON parse error: {e}"
    if not isinstance(book_data, list):
        return False, "Not a list"
    chapters = sorted(set(progress.get('completedChapters', {}).get(book, [])))
    if not chapters:
        return False, "No chapters marked complete"
    all_notes = []
    for chapter in chapters:
        try:
            expected = count_verses_in_chapter(book, chapter)
        except Exception as e:
            return False, f"Cannot count verses for ch {chapter}: {e}"
        covered = set()
        chapter_entries = []
        for e in book_data:
            if e.get('chapter') == chapter:
                chapter_entries.append(e)
                v = e.get('verse')
                ve = e.get('verseEnd')
                if v is not None and ve is not None:
                    for vv in range(int(v), int(ve) + 1):
                        covered.add(vv)
                elif v is not None:
                    covered.add(int(v))
        if len(covered) != expected:
            return False, f"Chapter {chapter} coverage: {len(covered)} vs {expected}"
        all_notes.extend([e.get('note','') for e in chapter_entries])
    if not all_notes:
        unique_ratio = 0.0
    else:
        unique_ratio = len(set(all_notes)) / len(all_notes)
    if unique_ratio < 0.90:
        return False, f"Book unique ratio too low: {unique_ratio}"
    return True, f"coverage_ok chapters={len(chapters)} unique_ratio={unique_ratio:.3f}"

def main(run_all=False, only_chapter=None):
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    
    progress = load_progress()
    # Fix: remove Genesis and Joshua from completedBooks if not complete
    for bad_book in ['Genesis', 'Joshua']:
        if bad_book in progress.get('completedBooks', []):
            progress['completedBooks'].remove(bad_book)
    save_progress(progress)
    
    consecutive_failures = 0
    for book in CANONICAL:
        if book in progress.get('completedBooks', []):
            continue
        try:
            slug = book_to_slug(book)
            book_dir = LLT_DIR / slug_to_dirname(slug)
            if not book_dir.exists():
                log_line(f"{book}: directory not found, skipping")
                continue
            chapter_files = sorted([int(f.stem) for f in book_dir.glob('*.json') if f.stem.isdigit()])
            if not chapter_files:
                continue
            max_chapter = max(chapter_files)
        except Exception as e:
            log_line(f"{book}: error finding chapters: {e}")
            continue
        
        completed_chapters = set(progress.get('completedChapters', {}).get(book, []))
        skipped_chapters = set([s.get('chapter') for s in progress.get('skipped', {}).get(book, [])])
        # Process all chapters not completed - including skipped ones
        chapters_to_try = set(range(1, max_chapter + 1))
        for chapter in sorted(chapters_to_try):
            if only_chapter is not None and chapter != only_chapter:
                continue
            if chapter in completed_chapters and only_chapter is None:
                continue
            log_line(f"{book} {chapter}: starting")
            try:
                success = process_chapter(book, chapter, progress)
            except Exception as e:
                err_str = str(e)
                if err_str.startswith('AUTH_ERROR') or err_str.startswith('QUOTA_ERROR'):
                    log_line(f"HALT: {err_str}")
                    return
                log_line(f"{book} {chapter}: HALT due to error: {err_str}")
                return
            if not success:
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    log_line(f"HALT: 3 consecutive chapters failed with limit/quota/usage")
                    return
                continue
            else:
                consecutive_failures = 0
                progress = load_progress()
                completed_chapters = set(progress.get('completedChapters', {}).get(book, []))
            if only_chapter is not None:
                break
        
        if only_chapter is not None:
            break
        
        gate_ok, gate_msg = check_book_gate(book, progress)
        if gate_ok:
            if book not in progress.get('completedBooks', []):
                progress['completedBooks'].append(book)
                save_progress(progress)
            log_line(f"{book}: BOOK COMPLETE - {gate_msg}")
        else:
            log_line(f"{book}: BOOK GATE FAILED - {gate_msg}")
            slug = book_to_slug(book)
            book_json_path = INSIGHTS_DIR / f'{slug}.json'
            if book_json_path.exists():
                quarantine_path = QUARANTINE_DIR / f'{slug}.json'
                try:
                    book_json_path.rename(quarantine_path)
                    log_line(f"{book}: moved to quarantine")
                except Exception as e:
                    log_line(f"{book}: failed to quarantine: {e}")
            if book in progress.get('completedChapters', {}):
                del progress['completedChapters'][book]
            save_progress(progress)
    
    log_line("Run complete or finished all books")

if __name__ == '__main__':
    import sys
    run_all = '--all' in sys.argv
    only_chapter = None
    for arg in sys.argv:
        if arg.startswith('--chapter='):
            only_chapter = int(arg.split('=')[1])
    main(run_all=run_all, only_chapter=only_chapter)
