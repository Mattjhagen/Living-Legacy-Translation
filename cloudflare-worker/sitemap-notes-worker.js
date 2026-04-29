/**
 * LLT Dynamic Sitemap & Note SEO Worker
 * Handles:
 * 1. /sitemap-notes.xml - Dynamic XML sitemap of all public notes
 * 2. /notes/[id] - SEO-injected note page
 */

const SUPABASE_URL = 'https://xphxtkdsshqsddajzlkj.supabase.co';
const SUPABASE_KEY = '(REPLACE_WITH_ANON_KEY_IN_DASHBOARD)';
const BASE_URL = 'https://llt.rootedapp.space';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const supabaseKey = env.SUPABASE_ANON_KEY || SUPABASE_KEY;

    // 1. Handle Dynamic Sitemap
    if (url.pathname === '/sitemap-notes.xml') {
      return handleSitemap(supabaseKey);
    }

    // 2. Handle Individual Note Pages (SEO Injection)
    if (url.pathname.startsWith('/notes/')) {
      const noteId = url.pathname.split('/')[2];
      return handleNotePage(noteId, supabaseKey);
    }

    // Fallback to static site
    return fetch(request);
  }
};

async function handleSitemap(key) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/journal?is_public=eq.true&select=id,updated_at`, {
    headers: { 'apikey': key, 'Authorization': `Bearer ${key}` }
  });
  const notes = await res.json();

  let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`;

  notes.forEach(note => {
    xml += `
  <url>
    <loc>${BASE_URL}/notes/${note.id}</loc>
    <lastmod>${new Date(note.updated_at).toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
  </url>`;
  });

  xml += `\n</urlset>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml', 'Cache-Control': 'public, max-age=3600' }
  });
}

async function handleNotePage(noteId, key) {
  // Fetch note content for metadata
  const res = await fetch(`${SUPABASE_URL}/rest/v1/journal?id=eq.${noteId}&select=content,verse_ref,user_id`, {
    headers: { 'apikey': key, 'Authorization': `Bearer ${key}` }
  });
  const [note] = await res.json();

  // Fetch base HTML
  const response = await fetch(`${BASE_URL}/note.html`);
  let html = await response.text();

  if (note) {
    const title = `Reflection on ${note.verse_ref} | Rooted Daily`;
    const description = note.content.substring(0, 160) + '...';

    // Inject SEO tags
    html = html.replace(/<title>.*?<\/title>/, `<title>${title}</title>`);
    html = html.replace(/<meta name="description" content=".*?">/, `<meta name="description" content="${description}">`);
    
    // Inject OpenGraph
    html = html.replace('</head>', `
      <meta property="og:title" content="${title}">
      <meta property="og:description" content="${description}">
      <meta property="og:url" content="${BASE_URL}/notes/${noteId}">
      <meta property="og:type" content="article">
      <meta name="twitter:card" content="summary">
    </head>`);
  }

  return new Response(html, {
    headers: { 'Content-Type': 'text/html' }
  });
}
