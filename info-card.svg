"""
Renders data/contributions.json as the classic 53-week x 7-day calendar of
rounded, colored boxes. Reveals once with a diagonal, line-after-line
slide-down (CSS keyframes, play-on-load, no looping), plus a legend and a
stats footer. Output: contrib-heatmap.svg (at repo root).
"""
import json
import os
from collections import defaultdict
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none ->                                        brightest (neon top end)

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 28
TOP_PAD = 34
BOTTOM_PAD = 46
MONTH_NAMES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
               "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def level_for(count, max_count):
    if count == 0:
        return 0
    if max_count <= 0:
        return 1
    ratio = count / max_count
    if ratio > 0.85:
        return 5
    if ratio > 0.6:
        return 4
    if ratio > 0.35:
        return 3
    if ratio > 0.1:
        return 2
    return 1


def build_weeks(days):
    """Group days into weeks (columns), Sunday-first, like GitHub's grid."""
    by_date = {d["date"]: d for d in days}
    ordered = sorted(by_date.values(), key=lambda d: d["date"])
    if not ordered:
        return []

    weeks = []
    current_week = [None] * 7
    first_date = datetime.strptime(ordered[0]["date"], "%Y-%m-%d")
    # pad to align first day under its real weekday (0=Sunday)
    start_dow = (first_date.weekday() + 1) % 7  # python Mon=0 -> convert to Sun=0
    for i in range(start_dow):
        current_week[i] = None

    dow = start_dow
    for d in ordered:
        current_week[dow] = d
        dow += 1
        if dow == 7:
            weeks.append(current_week)
            current_week = [None] * 7
            dow = 0
    if any(c is not None for c in current_week):
        weeks.append(current_week)
    return weeks


def month_labels(weeks):
    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        for day in week:
            if day is None:
                continue
            month = day["date"][5:7]
            if month != last_month:
                labels.append((wi, MONTH_NAMES[int(month) - 1]))
                last_month = month
            break
    return labels


def render(payload):
    days = payload["days"]
    stats = payload["stats"]
    username = payload["username"]
    max_count = max((d["count"] for d in days), default=0)
    weeks = build_weeks(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * CELL + 20
    height = TOP_PAD + 7 * CELL + BOTTOM_PAD

    boxes = []
    delay_step = 0.006  # diagonal stagger
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            x = LEFT_PAD + wi * CELL
            y = TOP_PAD + di * CELL
            if day is None:
                continue
            level = level_for(day["count"], max_count)
            color = PALETTE[level]
            delay = (wi + di) * delay_step
            title = f"{day['count']} contribuições em {day['date']}" if day["count"] else f"Sem contribuições em {day['date']}"
            boxes.append(
                f'<rect class="cell" x="{x}" y="{y - 8}" width="{BOX}" height="{BOX}" '
                f'rx="2.5" ry="2.5" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{title}</title></rect>'
            )

    labels = month_labels(weeks)
    month_svg = "".join(
        f'<text x="{LEFT_PAD + wi * CELL}" y="{TOP_PAD - 14}" '
        f'class="month">{name}</text>'
        for wi, name in labels
    )

    legend_x = LEFT_PAD + n_weeks * CELL - 130
    legend_y = height - 20
    legend_boxes = "".join(
        f'<rect x="{legend_x + 34 + i * 14}" y="{legend_y - 9}" width="{BOX}" height="{BOX}" '
        f'rx="2.5" ry="2.5" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )

    total = stats.get("total", 0)
    streak = stats.get("longest_streak", 0)

    svg = f"""<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     xmlns="http://www.w3.org/2000/svg" font-family="'Segoe UI', ui-monospace, Menlo, Consolas, monospace">
  <style>
    .bg {{ fill: #0d1117; }}
    .month {{ fill: #7d8590; font-size: 11px; }}
    .legend {{ fill: #7d8590; font-size: 10px; }}
    .footer {{ fill: #58a6ff; font-size: 11.5px; }}
    .cell {{
      opacity: 0;
      transform: translateY(-6px);
      animation: reveal 0.45s ease-out forwards;
    }}
    @keyframes reveal {{
      to {{ opacity: 1; transform: translateY(0); }}
    }}
  </style>
  <rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="8" ry="8"/>
  {month_svg}
  {''.join(boxes)}
  <text x="{legend_x - 34}" y="{legend_y + 3}" class="legend">Menos</text>
  {legend_boxes}
  <text x="{legend_x + 34 + len(PALETTE) * 14 + 6}" y="{legend_y + 3}" class="legend">Mais</text>
  <text x="{LEFT_PAD}" y="{legend_y + 3}" class="footer">{total} contribuições no último ano · streak recorde: {streak} dias</text>
</svg>"""
    return svg


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        payload = json.load(f)
    svg = render(payload)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
