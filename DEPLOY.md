# Hosting the Dashboard — Step by Step

Two free options: **Railway** (easiest) or **Render** (also free).
Both give you a public URL like `https://kitchen-analytics.up.railway.app`

---

## Option A — Railway (Recommended, 5 minutes)

### Step 1 — Install Git (if not already)
Download from https://git-scm.com/download/win  
Run the installer with default options.

### Step 2 — Create a free Railway account
Go to https://railway.app → Sign up with GitHub

### Step 3 — Create a free GitHub account (if needed)
Go to https://github.com → Sign up (free)

### Step 4 — Put the project on GitHub

Open Command Prompt in the `kitchen_analytics` folder:
```
cd C:\path\to\kitchen_analytics
git init
git add .
git commit -m "initial"
```

Then on GitHub.com:
- Click **New repository** → name it `kitchen-analytics` → **Create repository**
- Copy the commands shown under "push an existing repository" and run them

### Step 5 — Deploy on Railway
1. Go to https://railway.app/new
2. Click **Deploy from GitHub repo**
3. Select your `kitchen-analytics` repo
4. Railway auto-detects the Procfile and deploys
5. Click **Generate Domain** → you get a public URL instantly

**Done.** Share that URL with anyone.

---

## Option B — Render (also free)

1. Go to https://render.com → Sign up
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT`
5. Click **Create Web Service**

Free tier spins down after 15 min inactivity (first load takes ~30s to wake up).
Railway free tier stays always-on.

---

## Notes

- The `data/reviews.pkl` file (pre-classified data) is included in the zip.
  This means the app loads in ~2 seconds on the server — no re-classification needed.
- Free Railway gives you 500 hours/month (enough for always-on for a month).
- To update data later: re-run `python prepare_data.py` locally, commit the new pkl, push to GitHub — Railway auto-redeploys.

---

## Quick Git commands reference

```bash
# First time setup (in kitchen_analytics folder)
git init
git add .
git commit -m "deploy"
git remote add origin https://github.com/YOUR_USERNAME/kitchen-analytics.git
git push -u origin main

# After any changes
git add .
git commit -m "update"
git push
```
