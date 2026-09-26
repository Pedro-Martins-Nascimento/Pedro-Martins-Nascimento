"""
Renders a modern, self-contained stats card — total contributions, current/longest
streak (from data/contributions.json) plus top languages — with a sleek, high-contrast
Bento Dark design. No third-party rendering downtime and no rate limits.
Output: github-stats.svg (repo root).
"""
import json
import os

USERNAME = os.environ.get("GITHUB_USERNAME", "Pedro-Martins-Nascimento")
REPOS_URL = f"https://github.com/{USERNAME}?tab=repositories"

EXCLUDE_REPOS = {USERNAME, "skills-communicate-using-markdown", "skills-introduction-to-github"}

CONTRIB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
LANG_CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "languages.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "github-stats.svg")

LANG_COLORS = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#563d7c", "Vue": "#41b883", "Dart": "#00B4AB",
    "Shell": "#89e051", "Dockerfile": "#384d54", "EJS": "#a91e50", "C#": "#178600",
    "PLpgSQL": "#336790", "Jupyter Notebook": "#DA5B0B", "Mermaid": "#ff3670",
}
DEFAULT_COLOR = "#8b949e"


def fetch_top_languages():
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    counts = {}
    page = 1
    while True:
        resp = requests.get(REPOS_URL, params={"page": page}, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select("li[itemprop=owns]")
        if not items:
            break

        for li in items:
            name_el = li.select_one('a[itemprop="name codeRepository"]')
            lang_el = li.select_one("span[itemprop=programmingLanguage]")
            if not name_el or not lang_el:
                continue
            name = name_el.text.strip()
            if name in EXCLUDE_REPOS:
                continue
            lang = lang_el.text.strip()
            counts[lang] = counts.get(lang, 0) + 1

        next_link = soup.select_one('a[rel=next]')
        if not next_link:
            break
        page += 1
        if page > 5:
            break

    total = sum(counts.values())
    if total == 0:
        return []
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return [{"name": name, "pct": round(100 * n / total, 1)} for name, n in ranked]


def get_languages():
    try:
        langs = fetch_top_languages()
        if langs:
            os.makedirs(os.path.dirname(LANG_CACHE_PATH), exist_ok=True)
            with open(LANG_CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(langs, f, ensure_ascii=False, indent=2)
            return langs
    except Exception as e:
        print(f"Warning: language fetch failed ({e}); reusing cached data.")

    if os.path.exists(LANG_CACHE_PATH):
        with open(LANG_CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def render(stats, languages):
    total = stats.get("total", 0)
    current = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)

    width = 860
    height = 160

    left_w = 420

    def stat_block(cx, value, label, color="#22c55e"):
        return f'''
    <g transform="translate({cx}, 0)">
      <text x="0" y="74" text-anchor="middle" class="num" fill="{color}">{value}</text>
      <text x="0" y="98" text-anchor="middle" class="lbl">{label}</text>
    </g>'''

    stats_svg = (
        stat_block(75, total, "Contribuições", "#38bdf8")
        + stat_block(210, f"{current} dias", "Streak Atual 🔥", "#22c55e")
        + stat_block(345, f"{longest} dias", "Maior Streak", "#a855f7")
    )

    bar_x = left_w + 35
    bar_w = width - bar_x - 35
    bars = []
    if languages:
        for i, lang in enumerate(languages[:5]):
            y = 44 + i * 22
            color = LANG_COLORS.get(lang["name"], DEFAULT_COLOR)
            fill_w = max(4, bar_w * (lang["pct"] / 100))
            bars.append(f'''
    <circle cx="{bar_x}" cy="{y - 5}" r="4" fill="{color}" />
    <text x="{bar_x + 12}" y="{y - 1}" class="lang-name">{lang["name"]}</text>
    <text x="{bar_x + bar_w}" y="{y - 1}" text-anchor="end" class="lang-pct">{lang["pct"]}%</text>
    <rect x="{bar_x}" y="{y + 4}" width="{bar_w}" height="5" rx="2.5" fill="#21262d"/>
    <rect x="{bar_x}" y="{y + 4}" width="{fill_w:.1f}" height="5" rx="2.5" fill="{color}" class="bar" style="animation-delay:{i * 0.08:.2f}s"/>''')
    else:
        bars.append(f'<text x="{bar_x}" y="80" class="lbl">Carregando linguagens...</text>')

    svg = f"""<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#161b22" />
    </linearGradient>
  </defs>
  <style>
    .bg {{ fill: url(#cardGrad); stroke: #30363d; stroke-width: 1.2; }}
    .num {{ font-size: 24px; font-weight: 800; letter-spacing: -0.5px; }}
    .lbl {{ fill: #8b949e; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
    .divider {{ stroke: #30363d; stroke-width: 1; stroke-dasharray: 4 4; }}
    .section-title {{ fill: #c9d1d9; font-size: 13px; font-weight: 700; letter-spacing: 0.3px; }}
    .lang-name {{ fill: #e6edf3; font-size: 12px; font-weight: 600; }}
    .lang-pct {{ fill: #8b949e; font-size: 11px; font-weight: 600; }}
    .bar {{
      transform-origin: left;
      transform: scaleX(0);
      animation: grow 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    @keyframes grow {{ to {{ transform: scaleX(1); }} }}
  </style>
  <rect class="bg" x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" ry="14"/>
  
  <text x="35" y="28" class="section-title">📊 GitHub Overview</text>
  <text x="{bar_x}" y="28" class="section-title">💻 Top Linguagens</text>
  
  <line class="divider" x1="{left_w}" y1="20" x2="{left_w}" y2="{height - 20}"/>
  
  {stats_svg}
  {''.join(bars)}
</svg>"""
    return svg


def main():
    with open(CONTRIB_PATH, encoding="utf-8") as f:
        payload = json.load(f)
    languages = get_languages()
    svg = render(payload["stats"], languages)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} ({len(languages)} languages)")


if __name__ == "__main__":
    main()
