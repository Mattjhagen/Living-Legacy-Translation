const CURRENT_VERSION = '0.0.9';
let activeVerse = null;
let returnFocus = null;
let scrollPosition = 0;
let savedBodyStyle = null;
let backgroundElements = [];

function verseKey(num) {
    const container = document.querySelector('.verse-container');
    return `${container.dataset.bookSlug}/${container.dataset.chapter}/${num}`;
}
function readStored(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) || fallback; }
    catch { return fallback; }
}
function restoreHighlight(verse, num) {
    verse.classList.toggle('llt-highlight', !!readStored('llt-highlights', {})[verseKey(num)]);
}

function initReader() {
    const sheet = document.getElementById('verse-sheet');
    if (!sheet) return;
    sheet.setAttribute('role', 'dialog');
    sheet.setAttribute('aria-modal', 'true');
    sheet.setAttribute('aria-labelledby', 'sheet-title');
    sheet.setAttribute('aria-hidden', 'true');
    sheet.inert = true;
    const header = document.createElement('div');
    header.className = 'sheet-header';
    header.innerHTML = '<span id="sheet-title" class="sheet-verse-ref"></span><button type="button" class="sheet-close" aria-label="Close footnote">×</button>';
    sheet.querySelector('.sheet-handle').after(header);
    header.querySelector('button').addEventListener('click', closeSheet);
    document.getElementById('sheet-content').classList.add('sheet-body');
    document.getElementById('sheet-overlay').addEventListener('click', closeSheet);
    document.getElementById('sheet-copy').addEventListener('click', copyVerse);
    document.getElementById('sheet-share').addEventListener('click', shareVerse);
    document.getElementById('sheet-highlight').addEventListener('click', highlightVerse);
    document.getElementById('sheet-save').addEventListener('click', saveToJournal);
    document.addEventListener('keydown', event => {
        if (!sheet.classList.contains('active')) return;
        if (event.key === 'Escape') closeSheet();
        if (event.key === 'Tab') {
            const buttons = [...sheet.querySelectorAll('button')];
            const first = buttons[0], last = buttons[buttons.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault(); last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault(); first.focus();
            }
        }
    });
    checkWhatsNew();
}

function showVerseSheet(num, text, notes, trigger) {
    const sheet = document.getElementById('verse-sheet');
    if (!sheet) return;
    if (!sheet.classList.contains('active')) {
        returnFocus = trigger || document.activeElement;
        scrollPosition = window.scrollY;
        savedBodyStyle = document.body.getAttribute('style');
        Object.assign(document.body.style, {
            position: 'fixed', top: `-${scrollPosition}px`, width: '100%', overflow: 'hidden'
        });
        backgroundElements = [...document.body.children].filter(el =>
            el !== sheet && el.id !== 'sheet-overlay' && el.tagName !== 'SCRIPT');
        backgroundElements = backgroundElements.map(el => [el, el.inert]);
        backgroundElements.forEach(([el]) => { el.inert = true; });
    }
    activeVerse = { num, text, key: verseKey(num) };
    const title = document.querySelector('h1').textContent.trim() + ':' + num;
    document.getElementById('sheet-title').textContent = title;
    const content = document.getElementById('sheet-content');
    content.replaceChildren();
    const verse = document.createElement('div');
    verse.className = 'sheet-verse-text';
    verse.textContent = text;
    content.appendChild(verse);
    notes.forEach(note => {
        if (!note.content || !note.content.trim()) return;
        const card = document.createElement('div');
        card.className = 'footnote-item';
        const heading = document.createElement('h4');
        heading.textContent = note.type === 'insight' ? 'Heirloom Insight' : 'Translation Note';
        const body = document.createElement('div');
        body.className = 'footnote-content';
        body.textContent = note.content;
        const attribution = document.createElement('div');
        attribution.className = 'footnote-meta';
        attribution.textContent = `— ${note.author || 'LLT Insight'} (${note.year || '2026'})`;
        card.append(heading, body, attribution);
        content.appendChild(card);
    });
    document.getElementById('sheet-highlight').setAttribute('aria-pressed',
        String(!!readStored('llt-highlights', {})[activeVerse.key]));
    content.scrollTop = 0;
    sheet.inert = false;
    sheet.setAttribute('aria-hidden', 'false');
    sheet.classList.add('active');
    document.getElementById('sheet-overlay').classList.add('active');
    sheet.querySelector('.sheet-close').focus({ preventScroll: true });
}
function closeSheet() {
    const sheet = document.getElementById('verse-sheet');
    if (!sheet || !sheet.classList.contains('active')) return;
    sheet.classList.remove('active');
    document.getElementById('sheet-overlay').classList.remove('active');
    backgroundElements.forEach(([el, inert]) => { el.inert = inert; });
    if (savedBodyStyle === null) document.body.removeAttribute('style');
    else document.body.setAttribute('style', savedBodyStyle);
    window.scrollTo(0, scrollPosition);
    if (returnFocus && returnFocus.isConnected) returnFocus.focus({ preventScroll: true });
    sheet.inert = true;
    sheet.setAttribute('aria-hidden', 'true');
    activeVerse = null;
}
async function copyVerse() {
    if (!activeVerse) return;
    const text = `${activeVerse.text} (${document.getElementById('sheet-title').textContent})`;
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard');
    } catch { showToast('Unable to copy. Please select and copy the verse.'); }
}
async function shareVerse() {
    if (!activeVerse) return;
    if (!navigator.share) return copyVerse();
    try {
        await navigator.share({ title: document.getElementById('sheet-title').textContent,
            text: activeVerse.text, url: window.location.href });
    } catch (error) {
        if (error.name !== 'AbortError') showToast('Unable to share this verse.');
    }
}
function highlightVerse() {
    if (!activeVerse) return;
    const highlights = readStored('llt-highlights', {});
    highlights[activeVerse.key] = !highlights[activeVerse.key];
    try { localStorage.setItem('llt-highlights', JSON.stringify(highlights)); }
    catch { showToast('Unable to save highlight on this device.'); return; }
    document.querySelectorAll('.verse').forEach(verse => {
        restoreHighlight(verse, Number(verse.querySelector('.verse-num').textContent));
    });
    document.getElementById('sheet-highlight').setAttribute('aria-pressed', String(highlights[activeVerse.key]));
}
function saveToJournal() {
    if (!activeVerse) return;
    const journal = readStored('llt-journal', {});
    journal[activeVerse.key] = { ...activeVerse, ref: document.getElementById('sheet-title').textContent };
    try { localStorage.setItem('llt-journal', JSON.stringify(journal)); }
    catch { showToast('Unable to save on this device.'); return; }
    showToast('Saved on this device');
}
function showToast(msg) {
    const toast = document.createElement('div');
    toast.className = 'heirloom-toast';
    toast.setAttribute('role', 'status');
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
window.LLTReader = { open: showVerseSheet, close: closeSheet, restoreHighlight };
document.addEventListener('DOMContentLoaded', initReader);

function checkWhatsNew() {
    const lastSeen = localStorage.getItem('llt_version');
    if (lastSeen !== CURRENT_VERSION) {
        showWhatsNewModal();
    }
}

function showWhatsNewModal() {
    const modal = document.createElement('div');
    modal.className = 'whats-new-modal';
    modal.innerHTML = `
        <div class="wn-content">
            <div class="wn-header">✨ What's New</div>
            <div class="wn-feature">
                <strong>🎙️ Use Your Own Voice</strong>
                <p>Now in the mobile app! Clone your voice to hear Scripture.</p>
            </div>
            <div class="wn-feature">
                <strong>✦ Heirloom Insights</strong>
                <p>Tap the glowing stars to discover deep theological study notes.</p>
            </div>
            <div class="wn-feature">
                <strong>🔄 Instant Sync</strong>
                <p>Your journal now syncs perfectly across all your devices.</p>
            </div>
            <button class="wn-btn" id="wn-close">Explore Version ${CURRENT_VERSION}</button>
        </div>
    `;
    document.body.appendChild(modal);
    document.getElementById('wn-close').addEventListener('click', () => {
        localStorage.setItem('llt_version', CURRENT_VERSION);
        modal.remove();
    });
}
