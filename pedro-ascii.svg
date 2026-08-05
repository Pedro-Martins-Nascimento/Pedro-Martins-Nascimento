"""
Downsamples source-prepped.png to a character grid and picks a glyph per
cell from a brightness ramp (sparse -> dense). Monochrome, high contrast.
Each row wipes left-to-right (SMIL clip-path animate), staggered top to
bottom, prints once and freezes. Output: avi-ascii.svg (repo root) —
here written as pedro-ascii.svg.
"""
import os

from PIL import Image

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
#        ^ leading space clears the background to nothing

COLS = 100
ROWS = 53
CHAR_W = 6.2
CHAR_H = 11
FILL = "#9ba7b4"   # single light-gray fill — no per-character color

IN_PATH = os.path.join(os.path.dirname(__file__), "..", "source-prepped.png")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "pedro-ascii.svg")


def to_grid(path, cols, rows):
    im = Image.open(path).convert("L")
    # character cells are taller than wide, so undersample vertically
    # to keep the portrait's proportions from looking squashed
    im = im.resize((cols, rows), Image.LANCZOS)
    px = im.load()
    grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            brightness = px[x, y] / 255.0
            idx = int((1 - brightness) * (len(RAMP) - 1))
            row.append(RAMP[idx])
        grid.append("".join(row))
    return grid


def esc(ch):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def render(grid):
    width = COLS * CHAR_W
    height = ROWS * CHAR_H
    row_delay = 0.045

    rows_svg = []
    for ry, row in enumerate(grid):
        y = (ry + 1) * CHAR_H
        text = "".join(esc(c) for c in row)
        delay = ry * row_delay
        dur = 0.5
        clip_id = f"wipe{ry}"
        rows_svg.append(f"""
  <clipPath id="{clip_id}">
    <rect x="0" y="{y - CHAR_H}" width="0" height="{CHAR_H + 2}">
      <animate attributeName="width" from="0" to="{width}" begin="{delay:.3f}s"
               dur="{dur}s" fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1"/>
    </rect>
  </clipPath>
  <text x="0" y="{y}" class="row" clip-path="url(#{clip_id})" xml:space="preserve">{text}</text>
  <rect class="cursor" x="0" y="{y - CHAR_H + 1}" width="{CHAR_W}" height="{CHAR_H}">
    <animate attributeName="x" from="0" to="{width}" begin="{delay:.3f}s"
             dur="{dur}s" fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1"/>
    <animate attributeName="opacity" from="1" to="0" begin="{delay + dur:.3f}s" dur="0.15s" fill="freeze"/>
  </rect>""")

    svg = f"""<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, Menlo, Consolas, monospace">
  <style>
    .row {{ fill: {FILL}; font-size: {CHAR_H}px; letter-spacing: 0px; white-space: pre; }}
    .cursor {{ fill: #39d353; }}
  </style>
  {''.join(rows_svg)}
</svg>"""
    return svg


def main():
    grid = to_grid(IN_PATH, COLS, ROWS)
    svg = render(grid)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} ({COLS}x{ROWS} chars)")


if __name__ == "__main__":
    main()
