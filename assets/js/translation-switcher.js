/**
 * Bible Translation Switcher — Living Legacy Translation
 * 
 * Client-side JS that swaps verse text between WEB and LLT translations
 * and renders heirloom-styled footnotes in a bottom sheet panel.
 * 
 * Reads translation data from /json/{translation}/{book}/{chapter}.json
 */

(function () {
  'use strict';

  // ── State ──────────────────────────────────────────────────────────────
  var STORAGE_KEY = 'llt-translation';
  var DEFAULT_TRANSLATION = 'web';

  var currentTranslation = localStorage.getItem(STORAGE_KEY) || DEFAULT_TRANSLATION;
  var translationsIndex = null;
  var chapterCache = {};
  var currentChapterData = null;

  // ── DOM Helpers ────────────────────────────────────────────────────────
  function getBookSlug() {
    var el = document.querySelector('[data-book-slug]');
    if (el) return el.dataset.bookSlug;
    var canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) {
      var match = canonical.href.match(/\/bible\/([^/]+)\/(\d+)/);
      if (match) return match[1];
    }
    return null;
  }

  function getChapterNum() {
    var el = document.querySelector('[data-chapter]');
    if (el) return parseInt(el.dataset.chapter, 10);
    var canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) {
      var match = canonical.href.match(/\/bible\/[^/]+\/(\d+)/);
      if (match) return parseInt(match[1], 10);
    }
    return null;
  }

  function getBookName() {
    var h1 = document.querySelector('h1');
    if (h1) {
      var text = h1.textContent.trim();
      // "Genesis 1" -> "Genesis"
      return text.replace(/\s+\d+$/, '');
    }
    return '';
  }

  // ── Data Fetching ─────────────────────────────────────────────────────
  function fetchTranslationsIndex() {
    if (translationsIndex) return Promise.resolve(translationsIndex);
    return fetch('../../../json/translations.json')
      .then(function (res) { return res.json(); })
      .then(function (data) { translationsIndex = data; return data; })
      .catch(function (e) { console.warn('Could not load translations index:', e); return null; });
  }

  function fetchChapter(translationId, bookSlug, chapter) {
    var key = translationId + '/' + bookSlug + '/' + chapter;
    if (chapterCache[key]) return Promise.resolve(chapterCache[key]);
    return fetch('../../../json/' + translationId + '/' + bookSlug + '/' + chapter + '.json')
      .then(function (res) {
        if (!res.ok) return null;
        return res.json();
      })
      .then(function (data) {
        if (data) chapterCache[key] = data;
        return data;
      })
      .catch(function (e) {
        console.warn('Could not load ' + key + ':', e);
        return null;
      });
  }

  // ── Escape HTML ───────────────────────────────────────────────────────
  function escapeHtml(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }

  // ── Verse Rendering ───────────────────────────────────────────────────
  function renderVerses(data) {
    var container = document.querySelector('.verse-container');
    if (!container) return;

    window.LLTReader.close();
    currentChapterData = data;
    container.innerHTML = '';

    var footnoteMap = {};
    if (data.footnotes) {
      data.footnotes.forEach(function (fn) {
        if (!footnoteMap[fn.verse]) footnoteMap[fn.verse] = [];
        footnoteMap[fn.verse].push(fn);
      });
    }


    data.verses.forEach(function (verse) {
      var div = document.createElement('div');
      div.className = 'verse';
      div.tabIndex = -1; // Restore focus after opening from the verse text.
      if (currentTranslation === 'llt') div.classList.add('llt-mode');

      var numSpan = document.createElement('span');
      numSpan.className = 'verse-num';
      numSpan.textContent = verse.number;

      var textSpan = document.createElement('span');
      textSpan.className = 'verse-text';
      textSpan.textContent = verse.text;

      div.appendChild(numSpan);
      div.appendChild(textSpan);

      var notes = footnoteMap[verse.number] || [];
      var hasNotes = notes.some(function (n) { return n.content && n.content.trim() !== ''; });

      if (hasNotes) {
        div.classList.add('has-footnote');
        var indicator = document.createElement('button');
        indicator.type = 'button';
        indicator.setAttribute('aria-label', 'Open notes for ' + data.book + ' ' + data.chapter + ':' + verse.number);
        indicator.setAttribute('aria-haspopup', 'dialog');
        indicator.setAttribute('aria-controls', 'verse-sheet');
        indicator.addEventListener('click', function (event) {
          event.stopPropagation();
          window.LLTReader.open(verse.number, verse.text, notes, indicator);
        });
        indicator.className = 'fn-marker';
        indicator.textContent = '✦';
        textSpan.appendChild(indicator);
      }

      // Open sheet on any verse click
      div.style.cursor = 'pointer';
      div.addEventListener('click', function() {
        window.LLTReader.open(verse.number, verse.text, notes, div);
      });

      window.LLTReader.restoreHighlight(div, verse.number);
      container.appendChild(div);
    });

    // Update translation tag
    var tag = document.querySelector('.translation-tag');
    if (tag) {
      var info = getTranslationInfo(data.translation);
      var name = info ? info.name : data.translation_name;
      var testament = data.testament === 'OT' ? 'Old Testament' : 'New Testament';
      tag.textContent = name + ' · ' + testament;
    }
  }

  function getTranslationInfo(id) {
    if (!translationsIndex) return null;
    for (var i = 0; i < translationsIndex.translations.length; i++) {
      var t = translationsIndex.translations[i];
      if (t.id === id || t.abbrev === id) return t;
    }
    return null;
  }

  // ── Switcher UI ───────────────────────────────────────────────────────
  function createSwitcherUI() {
    if (!document.querySelector('.verse-container')) return;

    var nav = document.querySelector('.ch-nav');
    if (!nav) return;

    var switcher = document.createElement('div');
    switcher.className = 'translation-switcher';
    switcher.id = 'translation-switcher';

    var label = document.createElement('span');
    label.className = 'switcher-label';
    label.textContent = 'Translation:';

    var toggle = document.createElement('div');
    toggle.className = 'switcher-toggle';
    toggle.setAttribute('role', 'radiogroup');
    toggle.setAttribute('aria-label', 'Select translation');

    var webBtn = document.createElement('button');
    webBtn.className = 'switcher-btn' + (currentTranslation === 'web' ? ' active' : '');
    webBtn.textContent = 'WEB';
    webBtn.setAttribute('aria-pressed', String(currentTranslation === 'web'));
    webBtn.setAttribute('data-translation', 'web');
    webBtn.title = 'World English Bible';

    var lltBtn = document.createElement('button');
    lltBtn.className = 'switcher-btn' + (currentTranslation === 'llt' ? ' active' : '');
    lltBtn.setAttribute('aria-pressed', String(currentTranslation === 'llt'));
    lltBtn.setAttribute('data-translation', 'llt');
    lltBtn.title = 'Living Legacy Translation';

    var icon = document.createElement('span');
    icon.className = 'llt-icon';
    icon.textContent = '✦ ';
    lltBtn.appendChild(icon);
    lltBtn.appendChild(document.createTextNode('LLT'));

    toggle.appendChild(webBtn);
    toggle.appendChild(lltBtn);
    switcher.appendChild(label);
    switcher.appendChild(toggle);

    nav.parentNode.insertBefore(switcher, nav);

    webBtn.addEventListener('click', function () { switchTranslation('web'); });
    lltBtn.addEventListener('click', function () { switchTranslation('llt'); });
  }

  function switchTranslation(translationId) {
    if (translationId === currentTranslation) return;

    currentTranslation = translationId;
    localStorage.setItem(STORAGE_KEY, translationId);

    // Update buttons
    var btns = document.querySelectorAll('.switcher-btn');
    for (var i = 0; i < btns.length; i++) {
      var isActive = btns[i].getAttribute('data-translation') === translationId;
      btns[i].classList.toggle('active', isActive);
      btns[i].setAttribute('aria-pressed', String(isActive));
    }

    // Toggle body class
    document.body.classList.toggle('llt-mode', translationId === 'llt');

    // Close any open sheet
    window.LLTReader.close();

    // Load and render
    var bookSlug = getBookSlug();
    var chapter = getChapterNum();
    if (!bookSlug || !chapter) return;

    fetchChapter(translationId, bookSlug, chapter).then(function (data) {
      if (data && currentTranslation === translationId) renderVerses(data);
    });
  }

  // ── Init ───────────────────────────────────────────────────────────────
  function init() {
    fetchTranslationsIndex().then(function () {
      createSwitcherUI();
      document.body.classList.toggle('llt-mode', currentTranslation === 'llt');

      var bookSlug = getBookSlug();
      var chapter = getChapterNum();
      if (bookSlug && chapter) {
        var requestedTranslation = currentTranslation;
        fetchChapter(requestedTranslation, bookSlug, chapter).then(function (data) {
          if (data && currentTranslation === requestedTranslation) renderVerses(data);
        });
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
