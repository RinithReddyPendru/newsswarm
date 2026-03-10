import os
import json
import requests
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── CONFIG ─────────────────────────────────────────────────
GROQ_API = "https://api.groq.com/openai/v1/chat/completions"
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL    = "llama-3.3-70b-versatile"

TOPICS = [
    {"id": "technology",    "name": "Technology",        "icon": "💻", "color": "#1a4a7a", "desc": "AI, software, gadgets, startups, cybersecurity, and tech industry news"},
    {"id": "politics",      "name": "Politics",           "icon": "🏛️", "color": "#7a1a1a", "desc": "Government, elections, policy, international relations, and political developments"},
    {"id": "sports",        "name": "Sports",             "icon": "⚽", "color": "#1a6a2a", "desc": "Football, cricket, tennis, Olympics, athlete news, and match results"},
    {"id": "business",      "name": "Business & Finance", "icon": "📈", "color": "#6a4a1a", "desc": "Markets, stocks, startups, economy, mergers, and financial news"},
    {"id": "science",       "name": "Science",            "icon": "🔬", "color": "#2a4a6a", "desc": "Research breakthroughs, space exploration, climate science, and discoveries"},
    {"id": "entertainment", "name": "Entertainment",      "icon": "🎬", "color": "#6a1a5a", "desc": "Movies, music, celebrities, streaming, gaming, and pop culture"},
    {"id": "health",        "name": "Health",             "icon": "🏥", "color": "#1a6a5a", "desc": "Medical research, wellness trends, mental health, and healthcare news"},
    {"id": "world",         "name": "World News",         "icon": "🌍", "color": "#3a3a6a", "desc": "Global affairs, humanitarian issues, international events, and geopolitics"},
]

# ── GROQ CALL ───────────────────────────────────────────────
def call_groq(prompt, max_tokens=700):
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    res = requests.post(GROQ_API, headers=headers, json=body, timeout=60)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

# ── TOPIC AGENT ─────────────────────────────────────────────
def run_topic_agent(topic):
    date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
    prompt = f"""You are the {topic['name']} News Agent writing for a daily newsletter dated {date_str}.

Write a compelling {topic['name']} news briefing covering: {topic['desc']}

Write 150-200 words in flowing paragraphs (no bullet points, no headers).
Cover the most significant recent trends, developments, and what matters most right now.
Be engaging, informative, and concise. Start directly with the content."""

    try:
        print(f"  [{topic['name']}] Agent running...")
        text = call_groq(prompt)
        print(f"  [{topic['name']}] ✓ Done ({len(text.split())} words)")
        return {"id": topic["id"], "success": True, "text": text}
    except Exception as e:
        print(f"  [{topic['name']}] ✗ Error: {e}")
        return {"id": topic["id"], "success": False, "text": f"Unable to fetch {topic['name']} news today."}

# ── NEWSLETTER AGENT ────────────────────────────────────────
def run_newsletter_agent(results):
    date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
    sections = ""
    for t in TOPICS:
        r = next((x for x in results if x["id"] == t["id"]), None)
        if r:
            sections += f"\n\n[{t['name'].upper()}]\n{r['text']}"

    prompt = f"""You are the Newsletter Editor. Compile these 8 news sections into a polished daily email newsletter.

Date: {date_str}

NEWS SECTIONS:
{sections}

Write a complete newsletter with:
1. Subject line (prefix with "SUBJECT: ")
2. Warm greeting
3. 2-sentence highlights intro
4. Each section with its topic header and content
5. Brief sign-off

Use ——— as dividers between sections. Make it worth reading every morning."""

    print("  [Newsletter Agent] Synthesizing all sections...")
    text = call_groq(prompt, max_tokens=1500)
    print(f"  [Newsletter Agent] ✓ Done")
    return text

# ── BUILD HTML ──────────────────────────────────────────────
def build_html(topic_results, newsletter_text, date_str):
    # Build topic sections HTML
    topic_sections_html = ""
    for t in TOPICS:
        r = next((x for x in topic_results if x["id"] == t["id"]), None)
        content = r["text"] if r else "Content unavailable."
        status_color = t["color"] if (r and r["success"]) else "#888"
        status_label = "PUBLISHED" if (r and r["success"]) else "UNAVAILABLE"
        topic_sections_html += f"""
        <div class="topic-section">
          <div class="topic-header">
            <span class="topic-icon">{t['icon']}</span>
            <span class="topic-name">{t['name'].upper()}</span>
            <span class="topic-badge" style="background:{status_color};">{status_label}</span>
          </div>
          <div class="topic-content">{content}</div>
        </div>
        <hr class="topic-divider">
        """

    # Extract subject line
    import re
    subject_match = re.search(r'SUBJECT:\s*(.+)', newsletter_text, re.IGNORECASE)
    subject = subject_match.group(1).strip() if subject_match else f"NewsSwarm Daily — {date_str}"
    nl_clean = re.sub(r'SUBJECT:.+\n?', '', newsletter_text, flags=re.IGNORECASE).strip()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NewsSwarm — {date_str}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {{
  --ink: #0f0e0c;
  --paper: #f9f5ee;
  --cream: #f0ead8;
  --border: #c8bfa8;
  --muted: #8a8070;
  --accent: #c8360a;
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--paper); color:var(--ink); font-family:'Libre Baskerville',serif; }}

.wrap {{ max-width:900px; margin:0 auto; padding:0 24px 60px; }}

.masthead {{ border-bottom:4px double var(--border); padding:24px 0 16px; text-align:center; margin-bottom:24px; }}
.masthead-meta {{ font-family:'JetBrains Mono',monospace; font-size:10px; letter-spacing:3px; color:var(--muted); text-transform:uppercase; margin-bottom:8px; display:flex; justify-content:space-between; }}
.newspaper-name {{ font-family:'Bebas Neue',sans-serif; font-size:72px; letter-spacing:-2px; line-height:0.9; }}
.newspaper-name span {{ color:var(--accent); }}
.tagline {{ font-style:italic; font-size:12px; color:var(--muted); border-top:1px solid var(--border); border-bottom:1px solid var(--border); padding:4px 0; display:inline-block; margin-top:6px; }}

.date-bar {{ display:flex; justify-content:space-between; font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--muted); letter-spacing:1px; border-bottom:1px solid var(--border); padding-bottom:8px; margin-bottom:28px; text-transform:uppercase; }}

.topic-section {{ margin-bottom:28px; }}
.topic-header {{ display:flex; align-items:center; gap:12px; margin-bottom:14px; padding-bottom:8px; border-bottom:2px solid var(--ink); }}
.topic-icon {{ font-size:18px; }}
.topic-name {{ font-family:'Bebas Neue',sans-serif; font-size:28px; letter-spacing:1px; line-height:1; }}
.topic-badge {{ font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:2px; padding:3px 8px; border-radius:2px; text-transform:uppercase; color:white; margin-left:auto; }}
.topic-content {{ font-size:13px; line-height:2; color:#2a2520; columns:2; column-gap:24px; }}

@media(max-width:600px) {{ .topic-content {{ columns:1; }} }}

.topic-divider {{ border:none; border-top:1px solid var(--border); margin:28px 0; }}

.nl-section {{ margin-top:40px; }}
.nl-header {{ background:var(--ink); color:white; padding:16px 20px; border-radius:4px 4px 0 0; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }}
.nl-badge {{ background:var(--accent); font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:2px; padding:3px 10px; border-radius:2px; text-transform:uppercase; }}
.nl-title {{ font-family:'Bebas Neue',sans-serif; font-size:20px; letter-spacing:1px; }}
.nl-subject {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:#aaa; margin-left:auto; }}
.nl-actions {{ display:flex; gap:8px; margin-left:auto; }}
.nl-btn {{ background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:white; padding:6px 14px; font-family:'JetBrains Mono',monospace; font-size:10px; letter-spacing:1px; cursor:pointer; border-radius:3px; transition:all 0.2s; text-transform:uppercase; }}
.nl-btn:hover {{ background:rgba(255,255,255,0.2); }}
.nl-body {{ background:white; border:1px solid var(--border); border-top:none; border-radius:0 0 4px 4px; padding:28px 32px; font-size:13px; line-height:2; white-space:pre-wrap; }}

.stats {{ display:flex; gap:0; border:1px solid var(--border); border-radius:4px; overflow:hidden; margin-bottom:28px; }}
.stat {{ flex:1; text-align:center; padding:12px; border-right:1px solid var(--border); background:white; }}
.stat:last-child {{ border-right:none; }}
.stat-n {{ font-family:'Bebas Neue',sans-serif; font-size:28px; color:var(--accent); line-height:1; }}
.stat-l {{ font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--muted); letter-spacing:2px; text-transform:uppercase; margin-top:2px; }}

.gen-badge {{ display:inline-flex; align-items:center; gap:6px; background:var(--cream); border:1px solid var(--border); border-radius:999px; padding:4px 14px; font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--muted); letter-spacing:1px; margin-bottom:20px; }}
.gen-dot {{ width:6px; height:6px; border-radius:50%; background:#2d6a4f; }}
</style>
</head>
<body>
<div class="wrap">

  <div class="masthead">
    <div class="masthead-meta">
      <span>Vol. 1 · AI-Powered Edition</span>
      <span>{date_str}</span>
      <span>8 Agents · Daily Dispatch</span>
    </div>
    <div class="newspaper-name">News<span>Swarm</span></div>
    <div class="tagline">Eight intelligent agents. One daily briefing. Delivered at 8 AM.</div>
  </div>

  <div class="date-bar">
    <span>{date_str}</span>
    <span>AI-Generated · Groq + Llama 3.3</span>
    <span>Free · GitHub Actions</span>
  </div>

  <div class="gen-badge">
    <div class="gen-dot"></div>
    Generated automatically at 8:00 AM IST
  </div>

  <div class="stats">
    <div class="stat"><div class="stat-n">8</div><div class="stat-l">Topics</div></div>
    <div class="stat"><div class="stat-n">9</div><div class="stat-l">Agents</div></div>
    <div class="stat"><div class="stat-n">{sum(len(r['text'].split()) for r in topic_results)}</div><div class="stat-l">Words</div></div>
    <div class="stat"><div class="stat-n">$0</div><div class="stat-l">Cost</div></div>
  </div>

  {topic_sections_html}

  <div class="nl-section">
    <div class="nl-header">
      <span class="nl-badge">Newsletter</span>
      <span class="nl-title">Daily Email Digest</span>
      <span class="nl-subject">{subject}</span>
      <div class="nl-actions">
        <button class="nl-btn" onclick="copyEmail()">📋 Copy Email</button>
        <button class="nl-btn" onclick="openMail()">✉️ Open in Mail</button>
      </div>
    </div>
    <div class="nl-body" id="nlBody">{nl_clean}</div>
  </div>

</div>

<script>
const nlText = document.getElementById('nlBody').textContent;
function copyEmail() {{
  navigator.clipboard.writeText(nlText).then(() => alert('✅ Copied! Paste into Gmail or Outlook.'));
}}
function openMail() {{
  const subject = encodeURIComponent("{subject}");
  const body = encodeURIComponent(nlText);
  window.location.href = `mailto:?subject=${{subject}}&body=${{body}}`;
}}
</script>
</body>
</html>"""

# ── MAIN ────────────────────────────────────────────────────
def main():
    if not GROQ_KEY:
        raise ValueError("GROQ_API_KEY secret not set in GitHub repository!")

    date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
    print(f"\n🗞️  NewsSwarm — {date_str}")
    print("=" * 50)
    print(f"Model: {MODEL}")
    print(f"Agents: {len(TOPICS)} topic agents + 1 newsletter agent")
    print("=" * 50)

    # Run all topic agents in parallel (max 6 threads)
    print("\n📰 Running topic agents in parallel...")
    topic_results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(run_topic_agent, t): t for t in TOPICS}
        for future in as_completed(futures):
            result = future.result()
            topic_results.append(result)

    print(f"\n✅ {sum(1 for r in topic_results if r['success'])}/{len(TOPICS)} topic agents succeeded")

    # Run newsletter synthesis agent
    print("\n🧠 Running newsletter synthesis agent...")
    newsletter_text = run_newsletter_agent(topic_results)

    # Build HTML
    print("\n🏗️  Building HTML...")
    html = build_html(topic_results, newsletter_text, date_str)

    # Save output
    os.makedirs("output", exist_ok=True)
    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Also save a dated archive copy
    date_slug = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(f"output/{date_slug}.html", "w", encoding="utf-8") as f:
        f.write(html)

    total_words = sum(len(r['text'].split()) for r in topic_results)
    print(f"\n🎉 Newsletter generated!")
    print(f"   Total words: {total_words}")
    print(f"   Output: output/index.html")
    print(f"   Archive: output/{date_slug}.html")

if __name__ == "__main__":
    main()
