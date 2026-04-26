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
    return fetch('/json/translations.json')
      .then(function (res) { return res.json(); })
      .then(function (data) { translationsIndex = data; return data; })
      .catch(function (e) { console.warn('Could not load translations index:', e); return null; });
  }

  function fetchChapter(translationId, bookSlug, chapter) {
    var key = translationId + '/' + bookSlug + '/' + chapter;
    if (chapterCache[key]) return Promise.resolve(chapterCache[key]);
    return fetch('/json/' + translationId + '/' + bookSlug + '/' + chapter + '.json')
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

      var numSpan = document.createElement('span');
      numSpan.className = 'verse-num';
      numSpan.textContent = verse.number;

      var textSpan = document.createElement('span');
      textSpan.className = 'verse-text';
      textSpan.textContent = verse.text;

      div.appendChild(numSpan);
      div.appendChild(textSpan);

      // Add footnote indicator if LLT mode and verse has notes with content
      var notes = footnoteMap[verse.number];
      var hasNotes = notes && notes.some(function (n) { return n.content && n.content.trim() !== ''; });

      if (currentTranslation === 'llt' && hasNotes) {
        div.classList.add('has-footnote');

        var indicator = document.createElement('span');
        indicator.className = 'footnote-indicator';
        indicator.textContent = '✦';
        indicator.setAttribute('aria-label', 'View insight for verse ' + verse.number);
        indicator.setAttribute('role', 'button');
        indicator.setAttribute('tabindex', '0');

        // Click to open bottom sheet
        (function (verseNum, verseNotes) {
          indicator.addEventListener('click', function (e) {
            e.stopPropagation();
            openFootnoteSheet(data.book, verseNum, verseNotes);
          });
          indicator.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              e.stopPropagation();
              openFootnoteSheet(data.book, verseNum, verseNotes);
            }
          });
          div.addEventListener('click', function () {
            openFootnoteSheet(data.book, verseNum, verseNotes);
          });
        })(verse.number, notes);

        textSpan.appendChild(indicator);
      }

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

  // ── Bottom Sheet ──────────────────────────────────────────────────────
  var sheetEl = null;
  var overlayEl = null;
  var touchStartY = 0;
  var sheetTranslateY = 0;

  function createBottomSheet() {
    // Overlay
    overlayEl = document.createElement('div');
    overlayEl.className = 'footnote-overlay';
    overlayEl.addEventListener('click', closeFootnoteSheet);

    // Sheet
    sheetEl = document.createElement('div');
    sheetEl.className = 'footnote-sheet';
    sheetEl.setAttribute('role', 'dialog');
    sheetEl.setAttribute('aria-label', 'Verse insight');
    sheetEl.innerHTML =
      '<div class="sheet-handle"><div class="sheet-handle-bar"></div></div>' +
      '<div class="sheet-header">' +
        '<span class="sheet-verse-ref"></span>' +
        '<button class="sheet-close" aria-label="Close">&times;</button>' +
      '</div>' +
      '<div class="sheet-body"></div>';

    // Close button
    sheetEl.querySelector('.sheet-close').addEventListener('click', closeFootnoteSheet);

    // Touch-to-dismiss (swipe down)
    var handle = sheetEl.querySelector('.sheet-handle');
    handle.addEventListener('touchstart', onSheetTouchStart, { passive: true });
    handle.addEventListener('touchmove', onSheetTouchMove, { passive: false });
    handle.addEventListener('touchend', onSheetTouchEnd, { passive: true });

    // Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sheetEl.classList.contains('open')) {
        closeFootnoteSheet();
      }
    });

    document.body.appendChild(overlayEl);
    document.body.appendChild(sheetEl);
  }

  function openFootnoteSheet(bookName, verseNum, notes) {
    if (!sheetEl) createBottomSheet();

    var ref = sheetEl.querySelector('.sheet-verse-ref');
    ref.textContent = bookName + ' · Verse ' + verseNum;

    var body = sheetEl.querySelector('.sheet-body');
    body.innerHTML = '';

    var hasContent = false;
    notes.forEach(function (note) {
      if (!note.content || note.content.trim() === '') return;
      hasContent = true;

      var noteDiv = document.createElement('div');
      noteDiv.className = 'llt-footnote';
      if (note.is_public === false) {
        noteDiv.classList.add('personal-note');
      }

      // Subtle random tilt
      var tilt = (Math.random() * 0.8 - 0.4).toFixed(2);
      noteDiv.style.transform = 'rotate(' + tilt + 'deg)';

      var content = document.createElement('span');
      content.className = 'llt-note-content';
      content.textContent = note.content;

      var sig = document.createElement('span');
      sig.className = 'llt-note-sig';
      sig.textContent = '— ' + (note.author || 'LLT Insight') + ', ' + (note.year || '2026');

      noteDiv.appendChild(content);
      noteDiv.appendChild(sig);
      body.appendChild(noteDiv);
    });

    if (!hasContent) {
      body.innerHTML =
        '<div class="sheet-empty">' +
          '<div class="sheet-empty-icon">📜</div>' +
          '<p>No insights for this verse yet.</p>' +
        '</div>';
    }

    // Open with animation
    overlayEl.classList.add('open');
    sheetEl.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeFootnoteSheet() {
    if (!sheetEl) return;
    overlayEl.classList.remove('open');
    sheetEl.classList.remove('open');
    sheetEl.style.transform = '';
    document.body.style.overflow = '';
  }

  // ── Touch-to-dismiss ──────────────────────────────────────────────────
  function onSheetTouchStart(e) {
    touchStartY = e.touches[0].clientY;
    sheetTranslateY = 0;
    sheetEl.style.transition = 'none';
  }

  function onSheetTouchMove(e) {
    var deltaY = e.touches[0].clientY - touchStartY;
    if (deltaY < 0) deltaY = 0; // Only allow downward drag
    sheetTranslateY = deltaY;
    sheetEl.style.transform = 'translateY(' + deltaY + 'px)';
    if (deltaY > 10) e.preventDefault();
  }

  function onSheetTouchEnd() {
    sheetEl.style.transition = '';
    if (sheetTranslateY > 100) {
      closeFootnoteSheet();
    } else {
      sheetEl.style.transform = '';
    }
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
    closeFootnoteSheet();

    // Load and render
    var bookSlug = getBookSlug();
    var chapter = getChapterNum();
    if (!bookSlug || !chapter) return;

    fetchChapter(translationId, bookSlug, chapter).then(function (data) {
      if (data) renderVerses(data);
    });
  }

  // ── Init ───────────────────────────────────────────────────────────────
  function init() {
    fetchTranslationsIndex().then(function () {
      createSwitcherUI();
      document.body.classList.toggle('llt-mode', currentTranslation === 'llt');

      if (currentTranslation !== DEFAULT_TRANSLATION) {
        var bookSlug = getBookSlug();
        var chapter = getChapterNum();
        if (bookSlug && chapter) {
          fetchChapter(currentTranslation, bookSlug, chapter).then(function (data) {
            if (data) renderVerses(data);
          });
        }
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
