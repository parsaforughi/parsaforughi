#!/usr/bin/env python3
"""Studio contribution grid. Real counts from the public calendar.
The Platane/snk workflow replaces this with the official snake on `output`."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

QUERY = """
query {
  user(login: "parsaforughi") {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays { contributionCount weekday }
        }
      }
    }
  }
}
"""

DOTS = ["#161616", "#2c2c2c", "#555555", "#8a8a86", "#e8e8e6"]
SIZE = 11
GAP = 3
PAD = 8


def level(n: int, hi: int) -> int:
    if n <= 0:
        return 0
    if hi <= 1:
        return 4
    t = n / hi
    if t > 0.75:
        return 4
    if t > 0.45:
        return 3
    if t > 0.2:
        return 2
    return 1


def fetch_weeks() -> list[list[int]]:
    raw = subprocess.check_output(
        ["gh", "api", "graphql", "-f", f"query={QUERY}"],
        text=True,
    )
    data = json.loads(raw)
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    grid = []
    for week in weeks:
        col = [0] * 7
        for day in week["contributionDays"]:
            col[day["weekday"]] = day["contributionCount"]
        grid.append(col)
    return grid


def render(weeks: list[list[int]]) -> str:
    hi = max((n for col in weeks for n in col), default=1)
    cols = len(weeks)
    width = PAD * 2 + cols * SIZE + (cols - 1) * GAP
    height = PAD * 2 + 7 * SIZE + 6 * GAP

    rects: list[str] = []
    path_cells: list[tuple[int, int, int]] = []
    for x, col in enumerate(weeks):
        for y, n in enumerate(col):
            px = PAD + x * (SIZE + GAP)
            py = PAD + y * (SIZE + GAP)
            fill = DOTS[level(n, hi)]
            rects.append(
                f'<rect x="{px}" y="{py}" width="{SIZE}" height="{SIZE}" rx="2" fill="{fill}"/>'
            )
            if n > 0:
                path_cells.append((px + SIZE / 2, py + SIZE / 2, n))

    # Snake path: left-to-right, snake the rows that have work.
    values = []
    for i, (cx, cy, _) in enumerate(path_cells):
        values.append(f"{cx:.1f},{cy:.1f}")
    key_times = ""
    if values:
        n = len(values)
        key_times = ";".join(f"{i / max(n - 1, 1):.4f}" for i in range(n))

    snake = ""
    if values:
        snake = f"""
  <circle r="5.5" fill="#f3f2ee">
    <animate attributeName="cx" dur="18s" repeatCount="indefinite"
      values="{" ; ".join(v.split(',')[0] for v in values)}"
      keyTimes="{key_times}"/>
    <animate attributeName="cy" dur="18s" repeatCount="indefinite"
      values="{" ; ".join(v.split(',')[1] for v in values)}"
      keyTimes="{key_times}"/>
  </circle>
  <circle r="3.2" fill="#0a0a0a">
    <animate attributeName="cx" dur="18s" repeatCount="indefinite"
      values="{" ; ".join(v.split(',')[0] for v in values)}"
      keyTimes="{key_times}"/>
    <animate attributeName="cy" dur="18s" repeatCount="indefinite"
      values="{" ; ".join(v.split(',')[1] for v in values)}"
      keyTimes="{key_times}"/>
  </circle>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Contribution snake">
  <rect width="100%" height="100%" fill="#0a0a0a"/>
  {"".join(rects)}
  {snake}
</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    weeks = fetch_weeks()
    svg = render(weeks)
    dark = OUT / "github-contribution-grid-snake-dark.svg"
    light = OUT / "github-contribution-grid-snake.svg"
    dark.write_text(svg)
    light.write_text(svg.replace("#0a0a0a", "#ffffff").replace("#161616", "#ebedf0").replace("#f3f2ee", "#24292f"))
    print(f"wrote {dark.relative_to(ROOT)} ({len(weeks)} weeks)")


if __name__ == "__main__":
    main()
