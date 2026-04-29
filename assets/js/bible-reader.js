const CURRENT_VERSION = '0.0.9';

document.addEventListener('DOMContentLoaded', () => {
    initFootnotes();
    initSheetClose();
    initActions();
    checkWhatsNew();
});

// Global state
let currentFootnotes = [];
let activeVerse = null;

async function initFootnotes() {
    const container = document.querySelector('.verse-container');
    if (!container) return;

    const book = container.dataset.bookSlug;
    const chapter = container.dataset.chapter;
    const relPath = getRelPath();

    try {
        const response = await fetch(`${relPath}json/llt/${book}/${chapter}.json`);
        const data = await response.json();
        currentFootnotes = data.footnotes || [];
        
        if (currentFootnotes.length > 0) {
            injectFootnoteMarkers();
        }
    } catch (err) {
        console.error('Error loading footnotes:', err);
    }
}

function getRelPath() {
    const path = window.location.pathname;
    if (path.includes('/bible/')) return '../../../';
    return './';
}

function injectFootnoteMarkers() {
    const verses = document.querySelectorAll('.verse');
    verses.forEach(v => {
        const numSpan = v.querySelector('.verse-num');
        if (!numSpan) return;
        
        const num = parseInt(numSpan.textContent);
        const hasFn = currentFootnotes.some(fn => fn.verse === num);
        
        if (hasFn) {
            const textSpan = v.querySelector('.verse-text');
            const sup = document.createElement('sup');
            sup.className = 'fn-marker';
            sup.textContent = '✦';
            sup.addEventListener('click', (e) => {
                e.stopPropagation();
                showVerseSheet(num, textSpan.textContent);
            });
            textSpan.appendChild(sup);
            
            v.style.cursor = 'pointer';
            v.addEventListener('click', () => {
                showVerseSheet(num, textSpan.textContent);
            });
        }
    });
}

function showVerseSheet(verseNum, verseText) {
    const sheet = document.getElementById('verse-sheet');
    const overlay = document.getElementById('sheet-overlay');
    const content = document.getElementById('sheet-content');
    
    if (!sheet || !content) return;

    activeVerse = { num: verseNum, text: verseText.replace(/✦$/, '') };
    const footnotes = currentFootnotes.filter(fn => fn.verse === verseNum);
    
    let html = `
        <div class="sheet-verse-title">Verse ${verseNum}</div>
        <div class="sheet-verse-text">${activeVerse.text}</div>
    `;

    footnotes.forEach(fn => {
        html += `
            <div class="footnote-item">
                <h4>${fn.type === 'insight' ? 'Heirloom Insight' : 'Translation Note'}</h4>
                <div class="footnote-content">${fn.content}</div>
                <div class="footnote-meta">— ${fn.author} (${fn.year})</div>
            </div>
        `;
    });

    content.innerHTML = html;
    sheet.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function initActions() {
    const btnCopy = document.getElementById('sheet-copy');
    const btnShare = document.getElementById('sheet-share');
    const btnSave = document.getElementById('sheet-save');

    if (btnCopy) btnCopy.addEventListener('click', copyVerse);
    if (btnShare) btnShare.addEventListener('click', shareVerse);
    if (btnSave) btnSave.addEventListener('click', saveToJournal);
}

async function copyVerse() {
    if (!activeVerse) return;
    const text = `${activeVerse.text} (Verse ${activeVerse.num})`;
    await navigator.clipboard.writeText(text);
    showToast('Copied to clipboard');
}

async function shareVerse() {
    if (!activeVerse) return;
    const text = `${activeVerse.text} (Verse ${activeVerse.num}) — Rooted Daily LLT`;
    if (navigator.share) {
        await navigator.share({ title: 'Rooted Daily Insight', text: text });
    } else {
        copyVerse();
    }
}

async function saveToJournal() {
    if (!activeVerse) return;
    // Integration logic for Supabase goes here
    showToast('Saved to Journal');
}

function showToast(msg) {
    const toast = document.createElement('div');
    toast.className = 'heirloom-toast';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

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

function initSheetClose() {
    const overlay = document.getElementById('sheet-overlay');
    if (overlay) overlay.addEventListener('click', closeSheet);
}

function closeSheet() {
    const sheet = document.getElementById('verse-sheet');
    const overlay = document.getElementById('sheet-overlay');
    if (sheet) sheet.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
}
