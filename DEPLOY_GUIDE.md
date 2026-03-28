# AlignAI Landing Page — Deployment Guide

**What you're building:** A static HTML landing page at `alignai.business` that pulls live data from your Supabase database and is optimized for Google and AI answer engines.

**What you need:** Your Mac, a GitHub account (you have this), and a free Cloudflare account.

**Time estimate:** 30-45 minutes for first-time setup. After that, it updates itself automatically.

---

## The Big Picture

```
You have now:
  alignai.business → GoDaddy "Launching Soon" page

You'll have after:
  alignai.business     → SEO-optimized landing page (Cloudflare Pages, free)
  app.alignai.business → Streamlit app (Railway, when ready)
```

The landing page lives in its own GitHub repo. Every night, GitHub Actions runs `build.py`, which pulls fresh data from Supabase, renders the HTML, and pushes it. Cloudflare Pages auto-deploys whenever the repo updates. You never touch it again unless you want to change the design.

---

## Step 1: Create the GitHub Repo (5 minutes)

1. Go to **github.com/new**
2. Name it **`alignai-landing`**
3. Set it to **Public** (Cloudflare Pages needs to read it)
4. Do NOT add a README — we'll push our own files
5. Click **Create repository**

Now push the files I built to this repo. Open Terminal on your Mac:

```bash
# Navigate to wherever you want the project to live
cd ~/Documents

# Clone the empty repo
git clone https://github.com/InSpireWIRE/alignai-landing.git
cd alignai-landing
```

**Copy the project files into this folder.** You'll get them from the download I'm providing in this session. The folder should contain:

```
alignai-landing/
├── build.py              ← Pulls data from Supabase, renders HTML
├── template.html         ← The landing page template
├── requirements.txt      ← Python dependencies
├── .gitignore
├── .github/
│   └── workflows/
│       └── build-landing.yml  ← GitHub Actions automation
└── dist/
    └── index.html        ← The built page (auto-generated)
```

Then push it:

```bash
git add .
git commit -m "Initial landing page"
git push origin main
```

---

## Step 2: Add Supabase Secrets to GitHub (2 minutes)

The GitHub Action needs your Supabase credentials to pull live data. These are stored as encrypted secrets — nobody can see them.

1. Go to **github.com/InSpireWIRE/alignai-landing/settings/secrets/actions**
2. Click **New repository secret**
3. Add these two secrets (same values as your `.env` in the align-app repo):

| Name | Value |
|------|-------|
| `SUPABASE_URL` | Your Supabase project URL (starts with `https://`) |
| `SUPABASE_KEY` | Your Supabase anon/public key |

---

## Step 3: Run the First Build (2 minutes)

1. Go to **github.com/InSpireWIRE/alignai-landing/actions**
2. Click **"Build Landing Page"** in the left sidebar
3. Click **"Run workflow"** → **"Run workflow"** (the green button)
4. Wait ~60 seconds for it to complete (green check = success)
5. Go back to the repo — the `dist/index.html` file should now contain your real Supabase data

If it fails, click into the failed run to see the error. Most likely cause: the secrets weren't entered correctly.

---

## Step 4: Set Up Cloudflare Pages (10 minutes)

Cloudflare Pages is a free static site host. It watches your GitHub repo and auto-deploys whenever it changes.

1. Go to **pages.cloudflare.com** and sign up for a free account (or log in if you have one)
2. Click **"Create a project"** → **"Connect to Git"**
3. Select your GitHub account and authorize Cloudflare to access the `alignai-landing` repo
4. Configure the build:
   - **Production branch:** `main`
   - **Build command:** (leave EMPTY — we already build in GitHub Actions)
   - **Build output directory:** `dist`
5. Click **"Save and Deploy"**

Cloudflare will deploy your site to a temporary URL like `alignai-landing-abc.pages.dev`. Open it and confirm the page looks right.

---

## Step 5: Connect Your Domain (10-15 minutes)

This is the part where `alignai.business` stops showing the GoDaddy placeholder and starts showing your new landing page.

### 5a: Add your domain in Cloudflare Pages

1. In Cloudflare Pages, go to your `alignai-landing` project
2. Click **"Custom domains"** tab
3. Click **"Set up a custom domain"**
4. Enter **`alignai.business`**
5. Cloudflare will tell you to update your DNS records

### 5b: Update your DNS

Your domain is registered through Google (now Squarespace Domains). You need to point it at Cloudflare instead of GoDaddy.

**Option A — If you want Cloudflare to manage ALL your DNS (recommended):**

1. In Cloudflare, go to **Websites** → **Add a site** → enter `alignai.business`
2. Select the **Free** plan
3. Cloudflare will give you 2 nameservers (something like `ns1.cloudflare.com`, `ns2.cloudflare.com`)
4. Go to your domain registrar (Google Domains / Squarespace Domains):
   - Log in at **domains.squarespace.com** (Google Domains migrated here)
   - Find `alignai.business` → **DNS** → **Nameservers**
   - Switch from default to **Custom nameservers**
   - Enter the 2 Cloudflare nameservers
   - Save
5. Wait 15 minutes to 24 hours for DNS to propagate (usually under 1 hour)

**Option B — If you want to keep DNS at your registrar:**

1. Cloudflare Pages will give you a CNAME record to add
2. Go to your domain registrar's DNS settings
3. Add a CNAME record:
   - **Name:** `@` (or leave blank for root)
   - **Target:** `alignai-landing-abc.pages.dev` (Cloudflare will tell you the exact value)
4. If your registrar doesn't support CNAME on root domain, you may need Option A instead

### 5c: Remove the GoDaddy site

Your current "Launching Soon" page is a GoDaddy website builder site. Once DNS points to Cloudflare, GoDaddy's site stops showing automatically — but you should also:

1. Log into GoDaddy
2. Cancel / delete the website builder site for `alignai.business`
3. This ensures there's no confusion or billing

---

## Step 6: Set Up the Streamlit Subdomain (for later)

When you deploy the Streamlit app to Railway, you'll add a subdomain:

1. In Cloudflare DNS, add a CNAME record:
   - **Name:** `app`
   - **Target:** your Railway deployment URL
2. In Railway, add `app.alignai.business` as a custom domain
3. Now `app.alignai.business` serves your Streamlit app

This step can wait until Railway deployment is ready.

---

## What Happens Automatically After Setup

- **Every night at 11pm AZ time:** GitHub Actions runs `build.py`, pulls fresh numbers from Supabase, rebuilds `dist/index.html`, and pushes it
- **Cloudflare detects the push** and auto-deploys the updated page
- **Your landing page always shows current stats** — tool counts, review counts, top-scored tools

You can also trigger a manual rebuild anytime from GitHub Actions.

---

## Email Capture — Next Step

The email form on the page currently stores signups in the browser's localStorage (temporary — for testing only). Before launch, you need to connect it to one of:

**Option A — Supabase table (recommended, simplest):**
Create an `email_signups` table in Supabase and update the form's JavaScript to POST directly to Supabase using your anon key.

**Option B — Resend:**
Use the Resend API to send a confirmation email and store the signup. This gives you email delivery from day one.

I can build either of these in a follow-up session. The landing page works without it — the form just won't persist signups until this is wired up.

---

## File Reference

| File | What It Does |
|------|-------------|
| `build.py` | Connects to Supabase, pulls stats + top tools + categories, renders template → `dist/index.html` |
| `template.html` | Jinja2 template with full HTML, CSS, SEO meta tags, JSON-LD structured data, Open Graph tags |
| `dist/index.html` | The built output — this is what Cloudflare serves to visitors |
| `.github/workflows/build-landing.yml` | GitHub Actions: runs build.py nightly + on push + on manual trigger |
| `requirements.txt` | Python packages: jinja2, supabase |

---

## Testing Locally (Optional)

If you want to preview the page on your Mac before deploying:

```bash
cd ~/Documents/alignai-landing

# Build with fallback data (no Supabase needed)
python build.py

# Open the result in your browser
open dist/index.html
```

To build with real Supabase data locally:

```bash
export SUPABASE_URL="your-url-here"
export SUPABASE_KEY="your-key-here"
python build.py
open dist/index.html
```

---

## Troubleshooting

**GitHub Action fails:**
- Check that SUPABASE_URL and SUPABASE_KEY secrets are set correctly
- Click into the failed run → read the error output
- Most common: typo in the secret values

**Page shows fallback data instead of real data:**
- The secrets might not be set, or Supabase is rejecting the key
- Check the GitHub Actions log for the "⚠ Supabase error" message

**DNS not working after update:**
- DNS propagation takes 15 min to 24 hours
- Check propagation status at **dnschecker.org**
- Make sure you removed the old GoDaddy nameservers

**Page looks broken on mobile:**
- The template has responsive CSS built in
- If something looks off, it's likely a CSS issue — bring it back to our next session
