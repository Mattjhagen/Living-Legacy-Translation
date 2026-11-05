# Living Legacy Translation publication audit

Prepared November 5, 2026. Source revision e74570b23c94800202042424a76af5bec848db01.

## Decision

The repository has been converted into eight print-formatted interior PDFs preserving all repository Scripture and every nonempty active insight. The manuscript remains an editorial proof. Confirmed note errors, unverified factual claims, and the commentary rights scope require resolution before publication. No book has been uploaded, published, or submitted for sale.

## Source completeness

The source snapshot contains 66 books, 1,190 chapters, 31,109 verse records, and 752,711 Scripture words. All verse texts are nonempty; every chapter has consecutive verse numbers and a matching declared verse count. The 1,190th chapter is Psalm 151, whose seven verses are preserved with an explanation of its differing canonical status. This is the repository's full 66-book collection with an additional psalm, not every book in every Christian canon.

Every LLT chapter has exactly the same verse array as its corresponding stored WEB chapter. The scaffold generator explicitly copied WEB verse data and describes it as a starting scaffold. The README's claims of a proprietary modern translation and premier scholarship are not substantiated by a documented translation process in this repository. This edition therefore identifies its source honestly and does not claim a new original-language translation.

The independent comparison used the publisher's current Classic WEB HTML archive at https://ebible.org/Scriptures/eng-web_html.zip. It found 12,074 verse text differences after whitespace normalization, including punctuation and substantive wording differences. These are edition/transcription differences, not a count of confirmed errors. No source wording was replaced. The full comparison is in publisher-text-differences.csv. A preliminary reference comparison found an additional marker at Romans 16:25; it carries only a publisher footnote. The doxology is present at Romans 14:24-26. No missing nonempty verse body was found in that comparison. Psalm 151's superscription is included in the source's verse 1; the publisher displays it separately.

The publisher comparison establishes reference coverage against one current English edition. It does not certify the repository against Hebrew/Greek manuscripts, verify every word-level difference, or identify which historical WEB release supplied the source. Those remain separate editorial tasks.

## Insights and footnotes

There are 30,921 active records across 67 files, including the additional exodus-20.json file. Exact duplicates at the same verse or range are consolidated for print, yielding 30,894 printed notes with 1,209,483 words. Every source record remains in the JSONL ledger with its original fields and a printed note identifier. All 19,627 chapter footnote records were inspected: 476 are empty placeholders, and every nonempty chapter note is represented in the active notes. Synced chapter copies that lost a range endpoint are mapped back to their matching active range note.

No verse lacks an active note. There are 318 verses with overlapping retained note ranges or alternative notes; overlaps are recorded in audit-data.json. Overlap is not automatically an error in a printed commentary, but the repository's stated exactly-once insight gate is not fully satisfied. The progress manifest alone is not proof of that gate. There are 21 source records with missing or inconsistent schema fields. The print mapping accepts verse_end as a range endpoint, know/key as category fallbacks, and retains missing kinds as unclassified. The Ezekiel 8 record without a verse is presented as a chapter note. All original metadata remains unchanged in the ledger.

Four echo notes lack their expected asOf date: 2-kings 8:29, acts 13:52, genesis 43:34, numbers 1:53. No date has been invented. The original words, including first-person statements, remain intact. Front matter explains that the AI-generated grandparent voice does not establish actual human memories.

The quarantine contains 30,996 records with only 3 different note texts. The separate Archived Insights Reference Register prints the three full texts once and supplies every verse assignment, kind, attribution, and date; original individual records remain in quarantined-notes.jsonl. It is an archival companion, not recommended as a separate commercial KDP title. Empty footnotes are represented in the ledger rather than printed as blank notes.

## Factual claim audit

The audit combines complete structural checks and publisher-edition comparison with keyword screening of every printed note and targeted review of selected factual claims. 2,759 notes were flagged for further review based on language, history, absolute claims, or authorship terms. These flags are triage indicators, not findings of error. The reviewed-claims.csv file distinguishes confirmed errors, qualified interpretations, and supported observations. The full commentary has not received independent scholarly verification or a line-by-line human fact check.

Original notes have not been silently corrected. The following corrections or qualifications are proposed for the next editorial edition.

### F01 genesis 1:27

Confirmed error. The note counts image three times. The stored verse and publisher text contain image twice. Suggested action: Change Three times to Twice; preserve the original in the archive. Evidence: https://ebible.org/eng-web/GEN01.htm

### F02 genesis 1:1

Lexical overstatement. The note presents creation from nothing as the necessary meaning of bara. NET notes explain that the verb does not itself require that meaning. Suggested action: Separate a theological belief in creation from nothing from a claim about the lexical meaning. Evidence: https://classic.net.bible.org/passage.php?mode=print&passage=gen+1:1,26

### F03 esther 3:7

Confirmed error. The note says Pur gives the book Purim its name. The book is Esther; Purim is the festival named in Esther 9:26. Suggested action: Replace book with festival. Evidence: https://ebible.org/eng-web/EST09.htm

### F04 genesis 1:16

Interpretation stated as fact. The text omits the ordinary names sun and moon; the note attributes a specific anti-idolatry purpose to Moses. Intent and authorship are interpretive claims. Suggested action: Qualify as a possible literary reading; identify Mosaic authorship as traditional attribution. Evidence: https://www.americanbible.org/engage/bible-resources/articles/the-pentateuch/

### F05 genesis 1:31

Narrative conflation. The note locates humanity in the garden in its account of Genesis 1:31. The garden is introduced in Genesis 2:8. Suggested action: Remove in the garden here or explicitly identify the connection to chapter 2. Evidence: https://ebible.org/eng-web/GEN02.htm

### F06 exodus 20:1

Qualification needed. The opening divine speech is direct, but the note generalizes that the law comes without a mediator. Exodus 20:19-22 subsequently presents Moses as intermediary. Suggested action: Limit the observation to the opening words and acknowledge the later mediation. Evidence: https://ebible.org/eng-web/EXO20.htm

### F07 john 20:1

Unstated narrative detail. The note supplies grief keeping Mary awake and nobody else looking. John 20:1 states an early visit in darkness; it does not establish those details. Suggested action: Mark these details as imaginative devotional reflection. Evidence: https://ebible.org/eng-web/JHN20.htm

### F08 genesis 1:2

Lexical connection supported. The hovering connection is supported: the Genesis and Deuteronomy interlinears identify the same Hebrew root, Strong 7363. Shared root does not mean identical inflected form. Suggested action: Retain the root connection; qualify the separate Mosaic authorship language. Evidence: https://classic.net.bible.org/verse.php?book=Deu&chapter=32&verse=11

### F09 john 21:11

Textual fact supported; interpretation distinct. The count of 153 fish is in the verse. The note already signals its symbolic interpretation with some say. Suggested action: Keep the distinction between the explicit count and the proposed symbolism. Evidence: https://ebible.org/eng-web/JHN21.htm

### F10 1-timothy 2:12

Theological interpretation. The note prescribes a contextual reading of a disputed passage. That is an interpretive stance rather than an established historical finding. Suggested action: Identify the reading as one interpretation if the intended edition serves multiple traditions. Evidence: Repository note compared with 1 Timothy 2:12 and its surrounding text

### F11 psalms 151:1

Canonical and authorship distinction. The source includes a superscription describing the psalm as genuine Davidic work. Retaining that historical text does not authenticate Davidic authorship. Psalm 151 has different status across traditions. Suggested action: Retain the source and the added canonical explanation; avoid marketing a universal 66-book canon with an unexplained 151st psalm. Evidence: https://ebible.org/eng-web/PS201.htm

## Scripture licensing and commentary rights

The WEB publisher declares its translation public domain and allows print reproduction and sale. The translation name is a trademark identifying faithful copies; the current repository differs from the current publisher text. This manuscript uses The Rooted Translation as its edition title and identifies WEB as its source without claiming official WEB certification. Publisher rights evidence: https://worldenglish.bible/ and https://ebible.org/eng-web/copyright.htm.

The repository LICENSE is MIT with Copyright (c) 2026 Matty, while the README calls the rendering proprietary and says Published by PacMac Mobile LLC, all rights reserved. The MIT text refers to software and associated documentation; the repository does not clearly explain its intended scope for commentary rights. The permission notice is reproduced in every volume, but no assumption is made that it settles all third-party rights or ownership of every annotation. Before commercial release, the rights holder should confirm the commentary's publishing permission, the publisher/imprint, and any contributor credits. No exclusive copyright in the underlying public-domain Scripture is asserted. No new copyright notice or invented author credit has been added.

## KDP format and preflight

Each interior uses single 7 × 10 inch pages, black text, no bleed, embedded Liberation Serif fonts, 10.5 point Scripture and notes, 13.5 point leading, mirrored 0.875 inch inside and 0.625 inch outside margins, and approximately 0.65 inch top and bottom margins. Page numbers sit within safe trim margins. There are no illustrations, crop marks, encryption, PDF comments, or bookmarks. Metadata is removed from submission PDFs. Notes are chapter endnotes with explicit references; they are not bottom-of-page footnotes.

All 31,109 source verse texts and all 30,894 printed note texts were found in the exported PDFs. Mechanical checks cover every interior page for dimensions, embedded fonts, word bounds, page counts, and annotations. Representative rendered pages were visually inspected, including front matter, Scripture, notes, volume boundaries, and archive pages. This is not an assertion that all 4,493 pages received a human visual proofread at full size. KDP Print Previewer and a physical proof are still required before release.

The eight Scripture volumes total 4,493 pages. The archival register is 78 pages.

- Volume 1: Genesis 1 to Numbers 13 — 587 pages; 4,109 verses; 4,005 notes.
- Volume 2: Numbers 14 to 2 Samuel 2 — 588 pages; 3,973 verses; 3,919 notes.
- Volume 3: 2 Samuel 3 to Ezra 2 — 590 pages; 4,016 verses; 3,986 notes.
- Volume 4: Ezra 3 to Psalms 146 — 587 pages; 4,254 verses; 4,234 notes.
- Volume 5: Psalms 147 to Lamentations 1 — 586 pages; 3,988 verses; 3,987 notes.
- Volume 6: Lamentations 2 to Matthew 28 — 584 pages; 3,883 verses; 3,883 notes.
- Volume 7: Mark 1 to 1 Corinthians 5 — 588 pages; 4,252 verses; 4,245 notes.
- Volume 8: 1 Corinthians 6 to Revelation 22 — 383 pages; 2,634 verses; 2,635 notes.

Use paperback, black ink, white paper, 7 × 10 inches, no bleed. KDP currently permits 24-828 pages for this configuration. Every volume fits; several exceed the hardcover maximum of 550 pages, so these files are not specified for hardcover. Each paperback is a separate KDP title; an eight-volume bundle is not one printable interior. These settings are based on https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6 and https://kdp.amazon.com/en_US/help/topic/G201857950.

## Publication steps remaining

Resolve the confirmed note errors and reviewed qualifications, then complete the factual review queue. Confirm commentary rights and final imprint/contributor credits. Keep Psalm 151's scope explicit. Review the source-edition wording differences before making any claim of an official WEB text. Regenerate and recheck the files after any editorial changes.

KDP requires disclosure of AI-generated text, including substantially edited AI-generated material. The notes fall within that category. A Bible public-domain edition also needs appropriate differentiation; KDP recognizes original annotations but acceptance is not guaranteed by word count or AI generation. If using its public-domain annotated edition route, the title field must include (Annotated), and the description must explain the differentiation as its policy specifies. These requirements do not establish ownership of the annotations. See https://kdp.amazon.com/en_US/help/topic/G200672390 and https://kdp.amazon.com/en_US/help/topic/G200743940.

Finalize matching title/cover metadata, ISBN choice and imprint, a separate cover for each volume, pricing and territories, KDP Print Previewer review, and physical proof review. No cover, ISBN, author identity, price, or publication approval has been invented. Publication requires the user's approval.

## Editable files

The editable archive contains one Markdown manuscript per volume, original Scripture JSONL, all original active and chapter-note records with a source-to-print ledger, all quarantined records, the full text repository snapshot, a chapter-to-PDF-page index, the complete publisher comparison, reviewed claims, the factual review queue, build records, and SHA-256 preflight evidence. Markdown and JSONL preserve the text and can be edited with standard tools; this delivery does not include Word DOCX. The source snapshot is fixed to the revision above. The build script records the local construction process; its runtime/font paths require configuration to rebuild elsewhere.
