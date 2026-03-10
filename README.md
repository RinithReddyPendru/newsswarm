# 🗞️ NewsSwarm — Daily AI Newsletter

> 8 AI agents generate your daily news briefing every morning at 8:00 AM IST. Fully free. Your PC can be off.

---

## How it works

```
GitHub Actions (8 AM IST)
    ↓
8 Topic Agents run in parallel (Groq API — free)
    ↓
1 Newsletter Agent synthesizes everything
    ↓
HTML page deployed to GitHub Pages
    ↓
Your daily briefing URL is ready to open!
```

---

## Setup (5 minutes)

### Step 1 — Fork or create this repo on GitHub
- Go to github.com → New Repository
- Name it: `newsswarm`
- Upload all these files keeping the same folder structure

### Step 2 — Get free Groq API key
- Go to: console.groq.com
- Sign in with Google → Create API Key
- Copy the key (starts with gsk_...)

### Step 3 — Add secret to GitHub
- Go to your repo → Settings → Secrets and variables → Actions
- Click "New repository secret"
- Name: `GROQ_API_KEY`
- Value: paste your Groq key
- Click "Add secret"

### Step 4 — Enable GitHub Pages
- Go to repo → Settings → Pages
- Source: Deploy from branch
- Branch: `gh-pages` → `/ (root)`
- Click Save

### Step 5 — Enable GitHub Actions
- Go to repo → Actions tab
- Click "I understand my workflows, go ahead and enable them"

### Step 6 — Test it manually
- Go to Actions → "Daily Newsletter — 8 AM"
- Click "Run workflow" → Run workflow
- Wait ~2 minutes
- Go to: `https://YOURUSERNAME.github.io/newsswarm/`

---

## Your daily URL
```
https://YOURUSERNAME.github.io/newsswarm/
```
Bookmark this. Every morning at 8 AM IST it will have fresh content!

---

## Schedule
Runs at **8:00 AM IST** every day (2:30 AM UTC).
To change the time, edit `.github/workflows/newsletter.yml`:
```yaml
- cron: '30 2 * * *'   # Change this (UTC time)
```

UTC to IST: subtract 5 hours 30 minutes.
Examples:
- 7:00 AM IST = `30 1 * * *`
- 8:00 AM IST = `30 2 * * *`
- 9:00 AM IST = `30 3 * * *`

---

## Topics covered
💻 Technology · 🏛️ Politics · ⚽ Sports · 📈 Business & Finance
🔬 Science · 🎬 Entertainment · 🏥 Health · 🌍 World News

---

## Cost
- GitHub Actions: **FREE** (2000 min/month, this uses ~2 min/day)
- Groq API: **FREE** (14,400 req/day, this uses 9 req/day)
- GitHub Pages: **FREE**
- **Total: $0.00/month**
