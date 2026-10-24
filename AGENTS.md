# AGENTS.md (Living Legacy Translation)

## Repo shape (static site, no build system)
- Static HTML/CSS/JS site. No `package.json`, no build/lint/test scripts. Content is pre-generated.
- Bible data: `json/llt/<book-slug>/<chapter>.json` (LLT structured text + `footnotes[]`). Also `json/web/` exists. `markdown/` has per-chapter markdown.
- Generated pages: `bible/<book-slug>/<chapter>/index.html` (and `bible/index.html`). Root `index.html`.
- Assets: `assets/js/` (`bible-reader.js`, `translation-switcher.js`), `assets/css/` (`heirloom.css`), `assets/img/`.
- Scripts: `scripts/` Python utilities (inject_heirloom.py, generate_footnotes.py, generate_llt_scaffold.py, generate_sitemap.py, merge_rooted_footnotes.py, etc.). Run directly with `python3`.

## Heirloom Insights (current task state)
- **Recon findings:** Existing insight layer lives inside chapter JSONs as `footnotes[]` with `type: "insight"`, `author: "LLT Insight"`, `year: 2026` (rendered by `assets/js/bible-reader.js` as "HEIRLOOM INSIGHT"). 
- **New parallel layer (as specified):** `data/insights/<book-slug>.json` with entries `{"ref": "Book Ch:V", "chapter": N, "verse": N, "kind": "reflection|text|echo", "note": "...", "attribution": "LLT Insight (2026)"}`. Echo entries add `"asOf": "2026-10"`. For ranges use `"verse": N, "verseEnd": M` with one shared note; **every verse must be covered exactly once (no gaps/duplicates)**.
- **Progress:** `data/insights/_progress.json` tracks `completedBooks` and `completedChapters` (e.g. `{"1 Timothy": [1,2]}`). **Read it first on start/restart and RESUME — never regenerate a finished chapter.** Update after every chapter.
- **Status (as of now):** Created `data/insights/` and `data/insights/_progress.json`. Completed **1 Timothy chapter 1 only** (`data/insights/1-timothy.json` has 20 entries covering all verses 1-20). Chapter 1 validated as JSON. Remaining for 1 Timothy: chapters 2-6 (95 more verses). Follow the exact workflow/rules in the task prompt.

## Key files to know
- `json/llt/1-timothy/1.json` - example LLT chapter structure (use LLT text as base)
- `assets/js/bible-reader.js:87` - renders insight cards
- `scripts/inject_heirloom.py` - injects heirloom UI/scripts into chapter HTML

## Constraints
- **NEVER** modify Bible text, other data files, or site code. Only ADD insights files under `data/insights/`.
- Match voice exactly as specified (grandparent margin notes, Christ-centered, humble). Max 1 echo per chapter, no partisan politics/date-setting, no medical/financial/legal advice, no denominational polemics.
- Validate each book file parses as JSON before moving on.
