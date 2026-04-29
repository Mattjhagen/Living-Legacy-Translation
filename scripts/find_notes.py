import json

with open("/Users/matt/Rooted-Daily-static-site/data/bible.json", "r") as f:
    data = json.load(f)

found = False
for book in data["books"]:
    if "footnotes" in book:
        for chap, verse_fns in book["footnotes"].items():
            for v_str, fns in verse_fns.items():
                for fn in fns:
                    content = (fn.get("content") or "").strip()
                    if content:
                        print(f"Found note in {book.get('abbrev') or book.get('name')} {chap}:{v_str}")
                        print(f"Content: {content[:100]}...")
                        found = True
                        break
                if found: break
            if found: break
    if found: break

if not found:
    print("No non-empty footnotes found in bible.json")
