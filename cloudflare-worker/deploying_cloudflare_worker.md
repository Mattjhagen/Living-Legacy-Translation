# Deploying the LLT Dynamic Sitemap & SEO Worker

Follow these steps to connect your static website to the real-time Supabase indexing engine.

## 1. Create the Worker
1. Log in to [dash.cloudflare.com](https://dash.cloudflare.com).
2. Navigate to **Workers & Pages** > **Create application** > **Create Worker**.
3. Name your worker: `llt-sitemap-worker`.
4. Click **Deploy** (you will edit the code in the next step).

## 2. Upload the Logic
1. On the worker's overview page, click **Edit Code**.
2. Open the file [sitemap-notes-worker.js](file:///Users/matt/Living-Legacy-Translation/cloudflare-worker/sitemap-notes-worker.js) in your editor.
3. Copy the entire contents and paste it into the Cloudflare online editor, replacing the "Hello World" boilerplate.
4. Click **Save and Deploy**.

## 3. Secure Your Credentials
Your worker needs to talk to Supabase. **Never** hardcode these keys in the script; use environment variables instead:
1. Go back to the **llt-sitemap-worker** dashboard.
2. Click **Settings** > **Variables and Secrets**.
3. Under **Variables**, click **Add variable**:
   - **Variable name**: `SUPABASE_URL`
   - **Value**: `https://xphxtkdsshqsddajzlkj.supabase.co`
4. Click **Add variable** again:
   - **Variable name**: `SUPABASE_ANON_KEY`
   - **Value**: (Paste your long anon key from your `.env` file)
5. Click **Save and Deploy**.

## 4. Connect Your Domain
For the sitemap to be valid, it must appear on your own domain:
1. In the worker dashboard, click **Settings** > **Domains & Routes**.
2. Click **Add Route**.
3. **Route**: `llt.rootedapp.space/*`
4. **Zone**: `rootedapp.space`
5. Click **Save**.

## 5. Verification
Once deployed, you can verify it by visiting:
- `https://llt.rootedapp.space/sitemap-notes.xml` -> Should see an XML feed of public notes.
- `https://llt.rootedapp.space/notes/any-note-id` -> Should see the reflection page with proper SEO meta tags.

---
**Note**: If you are using Netlify for the static site, Cloudflare will act as a "proxy," handling the sitemap/notes routes and passing everything else to Netlify automatically.
