// Run against a local static server; see tests/README.md.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium, webkit } = require('playwright');
const chapter = require('../json/llt/leviticus/4.json');
const { execFileSync } = require('node:child_process');
const base = process.env.LLT_TEST_URL || 'http://127.0.0.1:8765';
const engine = process.env.LLT_TEST_ENGINE === 'webkit' ? webkit : chromium;
const launch = engine === chromium ? { executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', args: ['--no-sandbox'] } : {};

async function setup(t, mobile, original = false, translation = 'llt') {
  const browser = await engine.launch(launch);
  t.after(() => browser.close());
  const context = await browser.newContext({ viewport: mobile ? { width: 320, height: 740 } : { width: 1280, height: 900 }, isMobile: mobile, hasTouch: mobile });
  await context.addInitScript(translation => {
    localStorage.setItem('llt_version', '0.0.9');
    localStorage.setItem('llt-translation', translation);
    window.copied = []; window.shared = [];
    Object.defineProperty(navigator, 'clipboard', { value: { writeText: async text => window.copied.push(text) } });
    Object.defineProperty(navigator, 'share', { configurable: true, value: async data => window.shared.push(data) });
  }, translation);
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.route(/https:\/\/(fonts\.|www.googletagmanager)/, route => route.abort());
  if (original) {
    for (const file of ['bible-reader.js', 'translation-switcher.js']) {
      const source = execFileSync('git', ['show', `${process.env.LLT_TEST_BASELINE_REF || 'HEAD'}:assets/js/${file}`], { encoding: 'utf8' });
      await page.route(`**/assets/js/${file}`, route => route.fulfill({ contentType: 'application/javascript', body: source }));
    }
  }
  await page.goto(`${base}/bible/leviticus/4/`);
  if (translation === 'llt') await page.locator('.fn-marker').first().waitFor();
  else await page.waitForFunction(() => document.querySelector('#translation-switcher'));
  if (!original) t.after(() => assert.deepEqual(errors, [], 'No uncaught browser errors'));
  return { page, errors, context };
}

if (process.env.LLT_TEST_BASELINE) {
  test('original LLT star handler fails against the injected panel', async t => {
    const { page, errors } = await setup(t, true, true);
    await page.locator('.fn-marker').first().tap();
    assert.ok(errors.some(error => /null|textContent/.test(error)), errors.join('\n'));
    assert.equal(await page.locator('#verse-sheet').getAttribute('class'), 'verse-sheet');
  });
} else {
  for (const mobile of [false, true]) {
    test(`${mobile ? 'mobile tap' : 'desktop click'}: correct notes, actions, focus, scrolling, translation`, async t => {
      const { page } = await setup(t, mobile);
      const sheet = page.locator('#verse-sheet');
      const stars = page.locator('button.fn-marker');
      const activate = async locator => mobile ? locator.tap() : locator.click();
      await page.evaluate(() => window.scrollTo(0, 200));
      await stars.first().scrollIntoViewIfNeeded();
      const before = await page.evaluate(() => window.scrollY);
      await activate(stars.first());
      await page.waitForFunction(() => document.querySelector('#verse-sheet').getAttribute('aria-hidden') === 'false');
      assert.equal(await sheet.getAttribute('role'), 'dialog');
      assert.equal(await page.locator('#sheet-title').textContent(), 'Leviticus 4:1');
      assert.equal(await sheet.locator('.sheet-verse-text').textContent(), chapter.verses[0].text);
      assert.ok((await sheet.textContent()).includes(chapter.footnotes.find(n => n.verse === 1).content));
      assert.equal(await page.evaluate(() => document.body.style.position), 'fixed');
      await page.waitForTimeout(400);
      const box = await sheet.boundingBox();
      if (mobile) assert.ok(box.height <= 740 * .81 && box.x >= 0 && box.x + box.width <= 321);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      const starBox = await stars.first().boundingBox();
      assert.ok(starBox.width >= 44 && starBox.height >= 44);
      await page.locator('#sheet-copy').click();
      assert.ok((await page.evaluate(() => window.copied[0])).includes('Leviticus 4:1'));
      await page.locator('#sheet-share').click();
      assert.equal((await page.evaluate(() => window.shared[0])).text, chapter.verses[0].text);
      await page.locator('#sheet-highlight').click();
      assert.equal(await page.locator('#sheet-highlight').getAttribute('aria-pressed'), 'true');
      await page.locator('#sheet-save').click();
      assert.equal(await page.evaluate(() => JSON.parse(localStorage.getItem('llt-journal'))['leviticus/4/1'].text), chapter.verses[0].text);
      // Long commentary remains scrollable without moving the background.
      await sheet.locator('.footnote-content').first().evaluate(el => { el.textContent = el.textContent.repeat(40); });
      assert.ok(await sheet.locator('.sheet-body').evaluate(el => { el.scrollTop = 100; return el.scrollTop > 0; }));
      await sheet.locator('.sheet-close').click();
      assert.equal(await page.evaluate(() => window.scrollY), before);
      assert.equal(await page.evaluate(() => document.activeElement.className), 'fn-marker');
      assert.equal(await page.evaluate(() => document.body.style.position), '');
      await activate(stars.nth(1));
      assert.equal(await page.locator('#sheet-title').textContent(), 'Leviticus 4:2');
      assert.ok((await sheet.textContent()).includes(chapter.footnotes.find(n => n.verse === 2).content));
      await page.keyboard.press('Escape');
      await activate(stars.first());
      assert.equal(await page.locator('#sheet-highlight').getAttribute('aria-pressed'), 'true');
      await page.locator('#sheet-overlay').click({ position: { x: 5, y: 5 } });
      await page.waitForTimeout(400);
      await page.evaluate(() => window.scrollTo(0, 500));
      assert.ok(await page.evaluate(() => window.scrollY >= 499));
      await page.locator('[data-translation="web"]').click();
      await page.waitForFunction(() => !document.querySelector('.verse.llt-mode'));
      assert.equal(await sheet.getAttribute('aria-hidden'), 'true');
      assert.equal(await stars.count(), 0);
      await page.locator('[data-translation="llt"]').click();
      await stars.first().waitFor();
      await stars.first().focus();
      await page.keyboard.press('Space');
      assert.equal(await sheet.getAttribute('aria-hidden'), 'false');
      await page.keyboard.press('Shift+Tab');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'sheet-save');
      await page.keyboard.press('Escape');
      await page.reload();
      await stars.first().waitFor();
      assert.ok(await page.locator('.verse').first().evaluate(el => el.classList.contains('llt-highlight')));
      await activate(stars.last());
      assert.equal(await page.locator('#sheet-title').textContent(), 'Leviticus 4:35');
      await page.keyboard.press('Escape');
      await page.locator('.verse-text').first().click({ position: { x: 5, y: 5 } });
      await page.keyboard.press('Escape');
      assert.ok(await page.locator('.verse').first().evaluate(el => document.activeElement === el));
      await page.locator('.ch-nav a').first().click();
      await page.waitForURL('**/bible/leviticus/3/');
      assert.equal(await page.locator('h1').textContent(), 'Leviticus 3');
    });
  }
  test('WEB initial load, Share fallback, cancellation and storage failure', async t => {
    const { page } = await setup(t, true, false, 'web');
    await page.waitForFunction(() => document.querySelector('#translation-switcher'));
    assert.equal(await page.locator('.fn-marker').count(), 0);
    await page.locator('[data-translation="llt"]').click();
    await page.locator('.fn-marker').first().tap();
    await page.evaluate(() => Object.defineProperty(navigator, 'share', { value: undefined }));
    await page.locator('#sheet-share').click();
    assert.equal(await page.evaluate(() => window.copied.length), 1);
    await page.evaluate(() => Object.defineProperty(navigator, 'share', { value: async () => { throw new DOMException('Cancelled', 'AbortError'); } }));
    await page.locator('#sheet-share').click();
    await page.evaluate(() => { Storage.prototype.setItem = () => { throw new Error('Storage full'); }; });
    await page.locator('#sheet-save').click();
    assert.ok((await page.locator('.heirloom-toast').last().textContent()).includes('Unable to save'));
  });
}
