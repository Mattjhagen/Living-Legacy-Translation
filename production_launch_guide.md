# Rooted Daily & LLT: Production Launch Guide (v0.0.9)

Follow these steps to deploy the new Heirloom features, Real-time Sitemap, and DM Push Notifications.

---

## Part 1: Real-Time SEO & Sitemap (Cloudflare)
*Goal: Allow Google and AI to index community reflections instantly.*

1. **Create Worker**: Log in to [Cloudflare](https://dash.cloudflare.com) > Workers & Pages > Create Worker. Name it `llt-sitemap-worker`.
2. **Deploy Code**: Click **Edit Code** and paste the contents of `cloudflare-worker/sitemap-notes-worker.js`.
3. **Set Secrets**: Go to **Settings > Variables** and add:
   - `SUPABASE_URL`: `https://xphxtkdsshqsddajzlkj.supabase.co`
   - `SUPABASE_ANON_KEY`: (Your anon key from .env)
4. **Configure Route**: Go to **Settings > Domains & Routes** and add `llt.rootedapp.space/*`.

---

## Part 2: Push Notification Database Setup (Supabase SQL)
*Goal: Prepare the database to track push tokens and trigger alerts.*

1. Open your [Supabase Dashboard](https://supabase.com/dashboard).
2. Go to the **SQL Editor** in the left sidebar.
3. Click **New Query** and paste the contents of `supabase/push-notification-setup.sql`.
4. Click **Run**.
   - *This adds the `push_token` column and the trigger for DM alerts.*

---

## Part 3: DM Notification Logic (Supabase Edge Functions)
*Goal: Deploy the serverless function that talks to Expo.*

1. **Install Supabase CLI** (if you haven't): `brew install supabase/tap/supabase` (Mac).
2. **Login**: `supabase login`
3. **Link Project**: `supabase link --project-ref xphxtkdsshqsddajzlkj`
4. **Deploy Function**: 
   ```bash
   supabase functions deploy send-dm-notification
   ```
5. **Verify**: Ensure the function appears in your Supabase dashboard under "Edge Functions".

---

## Part 4: Final App Store & Web Push
*Goal: Release the version 0.0.9 client.*

### For Mobile (Expo/EAS):
1. **Update Build**: Run `eas build --platform ios` (or android).
2. **Verify Version**: Ensure the version in the "What's New" modal matches the build version (0.0.9).
3. **Permissions**: When the app opens, accept the "Push Notifications" prompt to sync your token.

### For Web (Living Legacy Translation):
1. **Deploy Static Files**: Push your changes to Netlify/Cloudflare Pages.
2. **Verify Sitemap**: Visit `https://llt.rootedapp.space/sitemap-notes.xml` to see if the dynamic feed is live.

---

**Success!** Your suite is now fully integrated. Users will receive DM alerts, see their cloned voice settings, and discover community insights via search engines.
