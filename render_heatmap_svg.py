"""
Hand-authors a small neofetch-style SVG: a title bar, then colored key/value
rows. Each line fades + slides in on a short stagger. STATIC=1 emits a frozen
frame (for local Quick Look previews). Output: info-card.svg (repo root).
"""
import os

STATIC = os.environ.get("STATIC") == "1"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

WIDTH = 490
LINE_H = 26
PAD_TOP = 62
PAD_LEFT = 26
LABEL_COLOR = "#39d353"   # green, like the neofetch key color
VALUE_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"
TITLE_TEXT = "pedro@github"

# label, value(s) — a value can be a list to wrap onto stacked lines with no label repeat
ROWS = [
    ("OS", "Systems Developer @ Grupo Malwee"),
    ("Host", "Jaraguá do Sul, SC — Brasil"),
    ("Kernel", "Node.js · TypeScript · Python"),
    ("Shell", "N8N · REST APIs · integrações"),
    ("Uptime", "Foco: automação & chatbots"),
    ("Studying", "Eng. de Software — Católica SC (2025–2029)"),
]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render():
    height = PAD_TOP + len(ROWS) * LINE_H + 34

    rows_svg = []
    for i, (label, value) in enumerate(ROWS):
        y = PAD_TOP + i * LINE_H
        delay = i * 0.12
        anim = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        cls = "line" if not STATIC else "line line-static"
        rows_svg.append(
            f'<text x="{PAD_LEFT}" y="{y}" class="{cls}"{anim}>'
            f'<tspan class="label">{esc(label)}</tspan>'
            f'<tspan class="colon">: </tspan>'
            f'<tspan class="value">{esc(value)}</tspan>'
            f'</text>'
        )

    static_css = "" if not STATIC else "\n    .line-static { opacity: 1 !important; transform: none !important; }"

    svg = f"""<svg viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}"
     xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, Menlo, Consolas, monospace">
  <style>
    .panel {{ fill: {BG}; stroke: {BORDER}; stroke-width: 1; }}
    .titlebar {{ fill: #161b22; }}
    .dot {{ opacity: 0.85; }}
    .title {{ fill: #8b949e; font-size: 12.5px; }}
    .label {{ fill: {LABEL_COLOR}; font-size: 14px; font-weight: 600; }}
    .colon {{ fill: #6e7681; font-size: 14px; }}
    .value {{ fill: {VALUE_COLOR}; font-size: 14px; }}
    .line {{
      opacity: 0;
      transform: translateX(-8px);
      animation: line-in 0.4s ease-out forwards;
    }}
    @keyframes line-in {{
      to {{ opacity: 1; transform: translateX(0); }}
    }}{static_css}
  </style>
  <rect class="panel" x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" ry="10"/>
  <path class="titlebar" d="M0.5,10 a9.5,9.5 0 0 1 9.5,-9.5 h{WIDTH - 20} a9.5,9.5 0 0 1 9.5,9.5 v22 h-{WIDTH - 1} z"/>
  <circle class="dot" cx="20" cy="21" r="5.5" fill="#ff5f56"/>
  <circle class="dot" cx="38" cy="21" r="5.5" fill="#ffbd2e"/>
  <circle class="dot" cx="56" cy="21" r="5.5" fill="#27c93f"/>
  <text x="{WIDTH / 2}" y="25" text-anchor="middle" class="title">{esc(TITLE_TEXT)}</text>
  {''.join(rows_svg)}
</svg>"""
    return svg


def main():
    svg = render()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
