# AGENTS.md (Living Legacy Translation)

## Repo shape (static site, no build system)
- Static HTML/CSS/JS site. No `package.json`, no build/lint/test scripts. Content is pre-generated.
- Bible data: `json/llt/<book-slug>/<chapter>.json` (LLT structured text + `footnotes[]`). Also `json/web/` exists. `markdown/` has per-chapter markdown.
- Generated pages: `bible/<book-slug>/<chapter>/index.html` (and `bible/index.html`). Root `index.html`.
- Assets: `assets/js/` (`bible-reader.js`, `translation-switcher.js`), `assets/css/` (`heirloom.css`), `assets/img/`.
- Scripts: `scripts/` Python utilities (inject_heirloom.py, generate_footnotes.py, generate_llt_scaffold.py, generate_sitemap.py, merge_rooted_footnotes.py, etc.). Run directly with `python3`.

## Heirloom Insights (PERMANENT RULESET — merged from earlier prompt)
**HEIRLOOM INSIGHTS MERGED INTO AGENTS.MD (permanent).**

### Goal
Create a parallel Heirloom Insights layer for the whole Bible (Genesis → Revelation), written as grandparent margin notes: Christ-centered, humble, warm without sentimentality. Add only under `data/insights/`.

### Output schema (exact)
- File: `data/insights/<book-slug>.json` (array of entries)
- Entry (normal): `{"ref": "Book Ch:V", "chapter": N, "verse": N, "kind": "reflection|text|echo", "note": "...", "attribution": "LLT Insight (2026)"}`
- Echo: add `"asOf": "2026-10"` (echo-framed, never prediction). Max **1 echo per chapter**.
- Ranges: use `"verse": N, "verseEnd": M` with **one shared note** covering that range.
- **Every verse must be covered exactly once (no gaps/duplicates).** 
- Kinds: `reflection` (default), `text` (where a real anchor exists — aim **~1 in 6**), `echo` (max 1/chapter, dated, echo-framed).

### Voice & universal rules
- Voice: grandparent margin notes, Christ-centered, humble. Speak as one who has walked a while and looks to Jesus.
- **Never** modify Bible text, other data files, or site code. Only ADD insights files under `data/insights/`.
- No partisan politics, no date-setting/prediction, no medical/financial/legal advice, no denominational polemics.
- Narrative books: track the story itself — people, places, turning points.
- Max 1 echo per chapter. Echoes must be echo-framed (looking back in gratitude/recognition), never predictive. Include `"asOf": "2026-10"`.
- Match voice exactly. Prefer restraint over flourish.
- **Truth = _progress.json PLUS the acceptance gate.** Any chapter listed complete whose file passes coverage + >=0.90 unique is legitimate progress, including Genesis 1.

### Voice-anchor examples (for calibration)
1. **Reflection (typical):** *"I’ve noticed how quickly grace reaches a frightened heart. Long before we straighten up, the Lord is already drawing near to restore us."* (Christ-centered, humble, margin-note tone)
2. **Echo (max 1/chapter, dated):** *"Looking back from a longer road, I see now how often the Lord went before me in places I only noticed Him later. As of 2026-10, I’m grateful He still does."* (echo-framed, grateful, no prediction/date-setting)

### Progress tracking (source of truth)
- Progress file: `data/insights/_progress.json` with shape `{"completedBooks": [], "completedChapters": {"Book Name": [chapterNumbers...]}, "skipped": {"Book Name": [{"chapter": N, "error": "..."}]}}` (extend as needed)
- **Read it first on start/restart and RESUME — never regenerate a finished chapter.** Update after **EVERY chapter**.
- If context compacted or thread lost: re-read `AGENTS.md` and `data/insights/_progress.json` before writing anything else; the manifest (not memory) counts.

### Run workflow (unattended, whole Bible)
- Canonical order: Genesis → Revelation.
- Chapter by chapter: read the whole chapter first from `json/llt/<book-slug>/<chapter>.json` (use LLT text as base). Write notes for every verse once. Update `_progress.json` after EVERY chapter.
- After each book closes: **validate the book's JSON parses**. If fails, fix and re-validate. If still fails, record that chapter(s) in `_progress.json` under `"skipped"` with the error and **KEEP GOING** (run never stalls).
- **NO stopping between books.** After each book, print a one-line summary (book, coverage, counts by kind) and immediately start the next book.
- Kind balance: `text` notes where a real anchor exists (aim ~1 in 6); `echo` max 1 per chapter, dated, echo-framed, never prediction.
- Narrative books: track people, places, turning points.
- **The ONLY full stop is the end of Revelation 22.** Then print the grand summary: books complete, total verses covered, counts by kind, and any skipped chapters.

### Current state (as of now)
- `data/insights/` created, `_progress.json` exists.
- **1 Timothy is complete** (all chapters 1-6 done). Resume from next uncompleted book in canonical order starting at Genesis (skip 1 Timothy).

## Key files to know
- `json/llt/1-timothy/1.json` - example LLT chapter structure (use LLT text as base)
- `assets/js/bible-reader.js:87` - renders insight cards
- `scripts/inject_heirloom.py` - injects heirloom UI/scripts into chapter HTML

## Constraints
- **NEVER** modify Bible text, other data files, or site code. Only ADD insights files under `data/insights/`.
- Validate each book file parses as JSON before moving on.
