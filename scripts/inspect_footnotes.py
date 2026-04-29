import json

with open("/Users/matt/Rooted-Daily-static-site/data/bible.json", "r") as f:
    data = json.load(f)

for book in data["books"]:
    if "footnotes" in book:
        print(f"Book: {book.get('abbrev') or book.get('name')}")
        print(f"Footnotes type: {type(book['footnotes'])}")
        if isinstance(book['footnotes'], dict):
            keys = list(book['footnotes'].keys())
            print(f"First 5 keys: {keys[:5]}")
            if keys:
                first_key = keys[0]
                first_val = book['footnotes'][first_key]
                print(f"Type of value for key {first_key}: {type(first_val)}")
                if isinstance(first_val, dict):
                    v_keys = list(first_val.keys())
                    print(f"Verse keys: {v_keys[:5]}")
                    if v_keys:
                        first_fn = first_val[v_keys[0]]
                        if isinstance(first_fn, list) and len(first_fn) > 0:
                            print(f"First footnote keys: {list(first_fn[0].keys())}")
                            print(f"First footnote full object: {first_fn[0]}")
                        elif isinstance(first_fn, dict):
                            print(f"First footnote keys: {list(first_fn.keys())}")
                            print(f"First footnote full object: {first_fn}")
        break
