# Rooted Daily Global Bible — SEO Package

Generated: 2026-04-26  
Translation: Rooted Daily Global Bible  
Publisher: PacMac Mobile LLC

## Contents

### `/markdown/`
One folder per book (66 total), each containing:
- `README.md` — Book overview with description and chapter links
- `1.md`, `2.md`, … — One Markdown file per chapter with full verse text

**1,256 total Markdown files** covering all 66 books and 1,189 chapters.

### `/html/`
- `bible_index.html` — Enhanced Bible browser page (drop-in replacement for `/bible/index.html`)
- `[book-slug]/index.html` — One enhanced book index page per book (66 files)

All HTML pages include:
- Canonical URLs
- Open Graph + Twitter Card meta tags
- JSON-LD structured data (Schema.org `Book`, `Chapter`, `BreadcrumbList`)
- Google Analytics tag (G-HSEJQQEFLJ)
- SEO-optimized titles and meta descriptions

### `/json/`
- `sitemap.json` — Full structured sitemap with all books, chapters, and URLs
- `books_index.json` — Lightweight books list (abbrev, slug, description, chapter count)
- `chapters_index.json` — Flat list of all 1,189 chapters with verse counts and URLs

### `/sitemap.xml`
XML sitemap for submission to Google Search Console and Bing Webmaster Tools.  
Covers: Home, /bible/, all 66 book pages, all 1,189 chapter pages.  
**7,551 lines | 213KB**

## Deployment Notes

1. **Drop the enhanced HTML pages** into your GitHub Pages repo:
   - Replace `bible/index.html` with `html/bible_index.html`
   - Copy each `html/[book]/index.html` into the matching `bible/[book]/` folder

2. **Submit sitemap.xml** to Google Search Console at rootedapp.space

3. **Use `books_index.json`** as a lightweight API endpoint for the mobile app's Bible browser

4. **Serve Markdown files** as fallback plain-text content for RSS, AI indexing, or CLI tools
