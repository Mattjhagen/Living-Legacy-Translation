# Reader browser regressions

This repository is a static site with no package manifest, lint/type-check task,
production build, or pre-existing test runner. Tests use Node's built-in runner
and Playwright, installed separately so the site gains no runtime dependencies.

From the repository root:

```sh
npm install --prefix /tmp/llt-browser-tests playwright
python3 -m http.server 8765 --bind 127.0.0.1
# In another terminal:
NODE_PATH=/tmp/llt-browser-tests/node_modules node --test tests/footnotes.cjs
node --check assets/js/bible-reader.js
node --check assets/js/translation-switcher.js
git diff --check
```

Chromium defaults to `/usr/bin/google-chrome`; override with `CHROME_PATH`.
Set `LLT_TEST_URL` for another static server. For WebKit:

```sh
/tmp/llt-browser-tests/node_modules/.bin/playwright install webkit
NODE_PATH=/tmp/llt-browser-tests/node_modules LLT_TEST_ENGINE=webkit node --test tests/footnotes.cjs
```

## Root cause and validation

The two reader scripts independently owned stars, verse click handlers, panel
content, and state. `translation-switcher.js` reused the injected `#verse-sheet`
but expected `.sheet-verse-ref` and `.sheet-body`, which the injected markup
lacked. Its opener threw while setting the missing reference's `textContent`,
before activating the sheet. The older reader also independently fetched LLT
notes and attached tiny non-button stars to whichever translation was displayed,
creating timing-dependent behavior. This was reproducible on mobile emulation;
the broken LLT opener was not exclusive to mobile.

The original failure was verified with:

```sh
NODE_PATH=/tmp/llt-browser-tests/node_modules LLT_TEST_BASELINE=1 LLT_TEST_BASELINE_REF=ba7e588364cdbbc0472a67834cfd9f3a11542f79 node --test tests/footnotes.cjs
```

The fix gives the existing injected panel one owner, supplies its header and
scrollable body at runtime, and gives the translation renderer semantic star
buttons with a single click handler. No generated chapter pages, Scripture, or
commentary are changed. The desktop panel retains its 600px width and placement;
the mobile panel is capped at 80vh/80dvh with safe-area padding.

Chrome desktop and touch emulation at 320px cover Leviticus 4:1, 4:2, and 4:35,
correct commentary/text, keyboard activation and focus trapping/restoration,
reopening, backdrop/close/Escape dismissal, internal scrolling, background scroll
restoration, width/height bounds, translation switching, chapter navigation,
Copy/Share and their fallback/cancellation, Highlight and Save persistence, and
storage failures. Clipboard and native Share are stubbed to verify their payloads.

Highlight previously had no handler and Save only showed a success toast; the
site had no implemented account persistence. These now store by book/chapter/verse
in `llt-highlights` and `llt-journal` in localStorage. Save reports “Saved on this
device”; no cloud/authentication integration is introduced.

WebKit was downloaded but could not launch here because required host libraries
were missing (GStreamer plugins, harfbuzz-icu, manette, enchant, hyphen). Physical
iPhone Safari/Chrome and Android Chrome, native clipboard/share UI, dynamic
browser chrome, and actual notch safe-area behavior remain unverified. Run the
same suite with WebKit dependencies installed, then check those devices manually.
