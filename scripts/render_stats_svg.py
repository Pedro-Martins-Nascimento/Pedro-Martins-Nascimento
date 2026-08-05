"""
Renders a self-contained stats card — total contributions, current/longest
streak (from data/contributions.json) plus top languages — in the same
terminal aesthetic as the rest of the profile art. No third-party rendering
service and no GitHub API token: languages come from scraping the public
repositories tab (https://github.com/<user>?tab=repositories), the same
technique fetch_contributions.py uses for the contribution calendar. If the
scrape fails for any reason, this script reuses the last successful
data/languages.json rather than erroring out or wiping the section.
Output: github-stats.svg (repo root).
"""
import json
import os

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "Pedro-Martins-Nascimento")
REPOS_URL = f"https://github.com/{USERNAME}?tab=repositories"

# Repos to leave out of the language mix: the profile repo itself has no
# language, and the skills-* repos are GitHub's own learning-exercise
# templates rather than real personal work.
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
    """Counts each repo's primary language across the repositories tab
    (paginating if there are more than one page) and turns that into a
    share-of-repos percentage — simple, and needs no auth or API calls."""
    counts = {}
    page = 1
    while True:
        resp = requests.get(REPOS_URL, params={"page": page}, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
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

    total = sum(counts.values())
    if total == 0:
        return []
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:6]
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
        print(f"Warning: language fetch failed ({e}); reusing cached data if available.")

    if os.path.exists(LANG_CACHE_PATH):
        with open(LANG_CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def render(stats, languages):
    total = stats.get("total", 0)
    current = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)

    width = 860
    height = 150

    # left block: three big numbers
    def stat_block(x, value, label):
        return f'''
  <text x="{x}" y="66" text-anchor="middle" class="num">{value}</text>
  <text x="{x}" y="88" text-anchor="middle" class="lbl">{label}</text>'''

    left_w = 430
    stats_svg = (
        stat_block(left_w * 0.22, total, "Total")
        + stat_block(left_w * 0.52, current, "Streak atual")
        + stat_block(left_w * 0.82, longest, "Streak recorde")
    )

    # right block: top languages as horizontal bars
    bar_x = left_w + 40
    bar_w = width - bar_x - 30
    bars = []
    if languages:
        for i, lang in enumerate(languages):
            y = 40 + i * 17
            color = LANG_COLORS.get(lang["name"], DEFAULT_COLOR)
            fill_w = bar_w * (lang["pct"] / 100)
            bars.append(f'''
  <text x="{bar_x}" y="{y - 3}" class="lang-name">{lang["name"]}</text>
  <text x="{bar_x + bar_w}" y="{y - 3}" text-anchor="end" class="lang-pct">{lang["pct"]}%</text>
  <rect x="{bar_x}" y="{y}" width="{bar_w}" height="5" rx="2.5" fill="#21262d"/>
  <rect x="{bar_x}" y="{y}" width="{fill_w:.1f}" height="5" rx="2.5" fill="{color}" class="bar" style="animation-delay:{i * 0.08:.2f}s"/>''')
    else:
        bars.append(f'<text x="{bar_x}" y="80" class="lbl">sem dados de linguagem</text>')

    svg = f"""<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, Menlo, Consolas, monospace">
  <style>
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
    .num {{ fill: #58a6ff; font-size: 26px; font-weight: 700; }}
    .lbl {{ fill: #8b949e; font-size: 11px; }}
    .divider {{ stroke: #30363d; stroke-width: 1; }}
    .lang-name {{ fill: #c9d1d9; font-size: 11px; }}
    .lang-pct {{ fill: #8b949e; font-size: 11px; }}
    .bar {{
      transform-origin: left;
      transform: scaleX(0);
      animation: grow 0.5s ease-out forwards;
    }}
    @keyframes grow {{ to {{ transform: scaleX(1); }} }}
  </style>
  <rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" ry="10"/>
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
