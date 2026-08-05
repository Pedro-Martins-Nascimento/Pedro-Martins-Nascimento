"""
Scrapes the public contribution calendar for GITHUB_USERNAME from
https://github.com/users/<username>/contributions (no auth, no GraphQL token)
and writes data/contributions.json with raw days + derived stats.
"""
import json
import os
import re
import sys
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "Pedro-Martins-Nascimento")
URL = f"https://github.com/users/{GITHUB_USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

# "No contributions on August 3rd." / "3 contributions on August 4th." / "1 contribution on ..."
COUNT_RE = re.compile(r"^(No|\d+)\s+contribution")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        raise RuntimeError("No .ContributionCalendar-day cells found — GitHub markup may have changed.")

    # Build id -> count from the <tool-tip for="..."> elements (current GitHub markup
    # does NOT carry the count as a data-* attribute on the day cell itself).
    counts_by_id = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if not target:
            continue
        text = tip.get_text(strip=True)
        m = COUNT_RE.match(text)
        if not m:
            continue
        counts_by_id[target] = 0 if m.group(1) == "No" else int(m.group(1))

    days = []
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue
        level = cell.get("data-level")
        count = counts_by_id.get(cell.get("id"), 0)
        days.append({
            "date": date,
            "count": count,
            "level": int(level) if level is not None else None,
        })

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days):
    if not days:
        return {}

    total = sum(d["count"] for d in days)

    # streaks
    longest = current = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak = run ending at the last day with data
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"])

    monthly = defaultdict(int)
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] += d["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best_day["date"], "count": best_day["count"]},
        "monthly": dict(sorted(monthly.items())),
    }


def main():
    days = fetch_days()
    if not days:
        print(f"No contribution cells found for '{GITHUB_USERNAME}'. "
              f"GitHub may have changed its markup, or the profile has no public activity.",
              file=sys.stderr)
        sys.exit(1)

    payload = {
        "username": GITHUB_USERNAME,
        "days": days,
        "stats": derive_stats(days),
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUT_PATH} — {len(days)} days, {payload['stats']['total']} contributions.")


if __name__ == "__main__":
    main()
