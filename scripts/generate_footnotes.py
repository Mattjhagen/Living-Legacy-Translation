#!/usr/bin/env python3
"""
Generate real LLT footnotes for all chapters.

Scans each chapter's verses and generates contextual insights for
theologically significant verses. Uses keyword patterns to identify
verses that merit footnotes, then provides relevant commentary.

This creates the "heirloom" AI insight layer for the Living Legacy Translation.
"""

import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LLT_DIR = os.path.join(BASE_DIR, "json", "llt")

# ── Keyword-based footnote generation ─────────────────────────────────
# Maps keyword patterns to insight templates. Each template is a function
# that returns a footnote given the verse context.

HEBREW_TERMS = {
    "In the beginning": "The Hebrew 'bereshit' (בְּרֵאשִׁית) opens Scripture with a declaration of absolute origin — not a philosophical argument, but a statement of faith: God was there first.",
    "the LORD": "The divine name YHWH (יהוה), rendered 'the LORD' in English Bibles, was considered so holy that ancient readers would substitute 'Adonai' (Lord) rather than speak it aloud.",
    "covenant": "The Hebrew 'berit' (בְּרִית) is more than a contract — it's a bond sealed by blood and oath. In the ancient world, covenants were the most solemn commitments two parties could make.",
    "steadfast love": "The Hebrew 'chesed' (חֶסֶד) is one of the richest words in the Old Testament — it combines loyalty, mercy, and unfailing kindness. No single English word captures it fully.",
    "lovingkindness": "This translates the Hebrew 'chesed' (חֶסֶד), a word that holds together covenant loyalty, tender mercy, and unfailing devotion. It describes God's character at its deepest.",
    "glory": "The Hebrew 'kavod' (כָּבוֹד) literally means 'weight' or 'heaviness.' God's glory is not decoration — it is the sheer gravity of His presence.",
    "holy": "The Hebrew 'qadosh' (קָדוֹשׁ) means 'set apart' — utterly different from anything created. Holiness is not about moral perfection alone; it's about being wholly other.",
    "righteousness": "The Hebrew 'tsedaqah' (צְדָקָה) goes beyond legal innocence. It describes right relationship — with God, with people, with the created order. To be righteous is to be in harmony with God's design.",
    "peace": "The Hebrew 'shalom' (שָׁלוֹם) means far more than the absence of conflict. It speaks of wholeness, completeness, and flourishing — the way things were meant to be.",
    "fear of the LORD": "In Hebrew, 'yirat YHWH' doesn't mean terror. It's reverential awe — the posture of a creature who knows they stand before the Creator. It's the beginning of all wisdom.",
    "salvation": "The Hebrew 'yeshua' (יְשׁוּעָה) — the same root as the name Jesus — means rescue, deliverance, spaciousness. God's salvation makes room for us to breathe again.",
    "mercy": "The Hebrew 'racham' (רַחַם) shares its root with 'womb' (rechem). God's mercy is maternal, visceral — the compassion of a mother who cannot abandon her child.",
    "soul": "The Hebrew 'nephesh' (נֶפֶשׁ) doesn't mean a disembodied spirit. It means the whole living person — your appetites, your breath, your very life. When the Psalmist says 'my soul thirsts for God,' he means his entire being aches.",
    "spirit": "The Hebrew 'ruach' (רוּחַ) means wind, breath, and spirit all at once. It's the animating force of life itself — invisible, powerful, and absolutely essential.",
    "word of the LORD": "In Hebrew thought, a word is not just sound — it's an event. When God speaks, reality shifts. The 'word of the LORD' is not information; it is power released.",
    "Selah": "'Selah' appears 71 times in the Psalms, and no one is entirely sure what it means. Most scholars believe it's a musical pause — a moment to let the weight of the words settle into your bones.",
}

GREEK_TERMS = {
    "grace": "The Greek 'charis' (χάρις) means unmerited favor — a gift given not because you earned it, but because the giver is generous. In the Roman world, 'charis' was the currency of patronage; Paul repurposed it to describe God's radical generosity.",
    "faith": "The Greek 'pistis' (πίστις) means more than intellectual belief. It's trust, loyalty, and faithful commitment. Biblical faith is not a feeling — it's a direction you walk in.",
    "gospel": "The Greek 'euangelion' (εὐαγγέλιον) was a political term before it was a religious one — it announced a king's victory or ascension. When the early church said 'gospel,' they were making a claim about who really rules the world.",
    "church": "The Greek 'ekklesia' (ἐκκλησία) meant 'assembly' or 'gathering' — a civic term for citizens called together to deliberate. The church is not a building; it's a people convened by God.",
    "repent": "The Greek 'metanoia' (μετάνοια) means a complete change of mind and direction — not just feeling sorry, but seeing the world differently and living accordingly.",
    "baptize": "The Greek 'baptizo' (βαπτίζω) means to immerse, plunge, or dip completely. In secular Greek, it was used for dyeing fabric — the cloth was so saturated it changed color permanently.",
    "eternal life": "The Greek 'zoe aionios' (ζωὴ αἰώνιος) is not just 'living forever.' It's a quality of life — God's own life shared with us. Eternal life starts now, not after death.",
    "love": "When the New Testament speaks of God's love, it uses 'agape' (ἀγάπη) — love that acts for the good of another regardless of cost. It's not a feeling; it's a decision made visible.",
    "abide": "The Greek 'meno' (μένω) means to remain, stay, dwell. Jesus doesn't invite casual visitors — He invites permanent residents. To abide is to make your home in Him.",
    "truth": "The Greek 'aletheia' (ἀλήθεια) literally means 'un-hidden' — truth is reality with the curtain pulled back. Jesus didn't just teach truth; He said He was truth.",
    "sin": "The Greek 'hamartia' (ἁμαρτία) comes from archery — it means 'to miss the mark.' Sin is not just rule-breaking; it's falling short of what you were designed to be.",
    "justify": "The Greek 'dikaioo' (δικαιόω) means to declare righteous — to announce a verdict of 'not guilty.' Justification is a courtroom word: God the Judge pronounces the prisoner free.",
    "flesh": "Paul's 'sarx' (σάρξ) doesn't just mean the physical body. It refers to the whole self organized around its own desires rather than God's purposes. The 'flesh' is the self that insists on being its own god.",
}

THEMATIC_INSIGHTS = {
    "created": "Creation in Scripture is never accidental. Every act of making is intentional, purposeful — an artist working with infinite care.",
    "blessed": "Biblical blessing is not a wish — it's a pronouncement. When God blesses, He is releasing power and purpose into someone's life.",
    "promised": "God's promises are the architecture of Scripture. Every covenant, every prophecy, every assurance builds toward the same future: God with His people, forever.",
    "forgive": "Forgiveness in Scripture is not pretending the wound doesn't exist. It's absorbing the cost so the relationship can live again.",
    "pray": "Prayer in the Bible is startlingly honest — it includes praise, rage, confusion, and silence. God doesn't require polished words; He requires an open heart.",
    "judge": "In the Bible, God's judgment is not vengeful — it's corrective. The Judge of all the earth will do right, and His verdicts restore what injustice has broken.",
    "king": "Every earthly king in Scripture is measured against the coming King. Some reflect God's heart; most don't. The story keeps asking: who will finally rule well?",
    "prophet": "The prophets were not primarily fortune-tellers. They were covenant attorneys — reminding Israel of the terms of their relationship with God and the consequences of betrayal.",
    "priest": "The priest stood between God and the people, carrying the sins of many. Every priest in Scripture pointed forward to a greater High Priest who would make the final sacrifice.",
    "temple": "The temple was never just a building — it was the place where heaven and earth overlapped. Where God chose to dwell with His people in tangible, localized presence.",
    "wilderness": "The wilderness in Scripture is a place of testing and transformation. It strips away pretense and reveals what's really in the heart.",
    "exile": "Exile was not the end of the story — it was a crucible. In Babylon, Israel learned to worship without a temple, to hope without a homeland, to trust a God they could not see.",
    "resurrection": "The resurrection is not just a miracle — it's a verdict. God declared that Jesus was right about everything, and death has been overruled.",
    "cross": "The cross was Rome's most brutal instrument of shame. That God chose this as His throne tells us everything about what kind of king He is.",
}


def generate_footnotes_for_chapter(chapter_data):
    """Generate contextual footnotes based on verse content."""
    footnotes = []
    verses = chapter_data.get("verses", [])
    book = chapter_data.get("book", "")
    chapter = chapter_data.get("chapter", 1)
    testament = chapter_data.get("testament", "OT")
    
    # Determine which term set to prioritize
    terms = {}
    terms.update(THEMATIC_INSIGHTS)
    if testament == "OT":
        terms.update(HEBREW_TERMS)
    else:
        terms.update(GREEK_TERMS)
    
    verses_with_footnotes = set()
    
    for verse in verses:
        text = verse.get("text", "")
        verse_num = verse.get("number", 0)
        
        # Skip if we already have too many footnotes (max ~5 per chapter)
        if len(footnotes) >= 5:
            break
        
        # Skip if this verse already has a footnote
        if verse_num in verses_with_footnotes:
            continue
        
        # Check for keyword matches
        for keyword, insight in terms.items():
            if keyword.lower() in text.lower():
                footnotes.append({
                    "verse": verse_num,
                    "content": insight,
                    "author": "LLT Insight",
                    "year": 2026,
                    "is_public": True,
                    "type": "insight"
                })
                verses_with_footnotes.add(verse_num)
                break  # One footnote per verse
    
    # If we got fewer than 2 footnotes, add one for the first verse
    # with a general contextual note
    if len(footnotes) < 1 and verses:
        first_verse = verses[0]
        footnotes.append({
            "verse": 1,
            "content": f"As you begin {book} {chapter}, pause here. Let the opening words settle before reading on. Scripture was written to be heard slowly — each line carrying weight the hurried reader misses.",
            "author": "LLT Insight",
            "year": 2026,
            "is_public": True,
            "type": "reflection"
        })
    
    return footnotes


def main():
    total_chapters = 0
    total_footnotes = 0
    skipped = 0
    
    for book_slug in sorted(os.listdir(LLT_DIR)):
        book_dir = os.path.join(LLT_DIR, book_slug)
        if not os.path.isdir(book_dir):
            continue
        
        for chapter_file in sorted(os.listdir(book_dir)):
            if not chapter_file.endswith('.json'):
                continue
            
            filepath = os.path.join(book_dir, chapter_file)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Skip Genesis 1 — we already have hand-crafted footnotes
            if data.get("book_slug") == "genesis" and data.get("chapter") == 1:
                skipped += 1
                continue
            
            # Generate footnotes
            footnotes = generate_footnotes_for_chapter(data)
            data["footnotes"] = footnotes
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            total_chapters += 1
            total_footnotes += len(footnotes)
            
            if total_chapters % 200 == 0:
                print(f"  Generated footnotes for {total_chapters} chapters ({total_footnotes} total notes)...")
    
    print(f"\nDone! Generated {total_footnotes} footnotes across {total_chapters} chapters.")
    print(f"Skipped {skipped} chapters (already had custom footnotes).")
    avg = total_footnotes / total_chapters if total_chapters > 0 else 0
    print(f"Average: {avg:.1f} footnotes per chapter.")


if __name__ == "__main__":
    main()
