#!/usr/bin/env python3
"""Chart: how many tool calls each Claude Code session made while this repo
was built and read, split by kind.

No firmware needed, the numbers are written in below. They were counted from
the three sessions' own transcripts (and their helper agents) at about
5:19 PM on 20 Nov 2026, while two of the sessions were still going - a
snapshot, not a final tally. The transcripts aren't in the repo.

usage: python3 tools/tool_calls_chart.py [output.png]
Colours and style follow the charts in a10e-firmware.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BG = "#020617"; FG = "#e2e8f0"; MUTED = "#94a3b8"; GRID = "#1e293b"
KINDS = [("shell commands", "#89b4fa"), ("REA (Ghidra)", "#a6e3a1"),
         ("file tools", "#cba6f7"), ("everything else", "#f9e2af")]
# session, what it did, [shell, REA, file tools, everything else]
ROWS = [
    ("the build", "phases 0 to 4: the outline, the how-to, the first bootloader read", [224, 21, 14, 10]),
    ("the secure world", "phases 5 and 6: Trusty, the comparison, the README", [120, 15, 49, 10]),
    ("the review", "checking the claims, then the deep read of lk", [117, 42, 9, 22]),
]

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "figures", "tool-calls.png")

plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
                     "text.color": FG, "font.size": 11, "font.family": "DejaVu Sans"})
fig, ax = plt.subplots(figsize=(13, 4.8), dpi=170)
n = len(ROWS)
top = max(sum(r[2]) for r in ROWS)
ax.set_xlim(-top * 0.92, top * 1.18)
ax.set_ylim(-1.15, n - 0.3)
ax.axis("off")

for i, (name, what, counts) in enumerate(ROWS):
    y = n - 1 - i
    ax.text(-top * 0.91, y + 0.13, name, ha="left", va="center", fontsize=12, fontweight="bold")
    ax.text(-top * 0.91, y - 0.2, what, ha="left", va="center", fontsize=8.5, color=MUTED)
    left = 0
    for (kind, colour), count in zip(KINDS, counts):
        ax.barh(y, count, left=left, height=0.5, color=colour)
        if count >= 14:
            ax.text(left + count / 2, y, str(count), ha="center", va="center", fontsize=10, color=BG)
        left += count
    ax.text(left + top * 0.02, y, f"{left} calls", ha="left", va="center", fontsize=11)

for j, (kind, colour) in enumerate(KINDS):
    x = -top * 0.90 + j * top * 0.48
    ax.plot([x], [-0.85], marker="s", ms=9, color=colour)
    ax.text(x + top * 0.02, -0.85, kind, ha="left", va="center", fontsize=9.5, color=MUTED)

total = sum(sum(r[2]) for r in ROWS)
rea = sum(r[2][1] for r in ROWS)
fig.text(0.02, 0.01, f"{total} tool calls in all, {rea} of them REA. counted from the sessions' transcripts "
         "at about 5:19 PM on 20 Nov 2026, with two sessions still going.", fontsize=9, color=MUTED)
fig.savefig(out, bbox_inches="tight", pad_inches=0.3)
print(out)
