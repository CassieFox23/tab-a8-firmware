#!/usr/bin/env python3
"""Chart: each device's vendor Treble level against the framework matrix
levels its GSI ships. A system image pairs with a vendor only where the two
levels are equal.

No firmware needed, the numbers are written in below:
- Tab A8: vendor target-level 5 and the LineageOS 22.2 GSI's matrices
  (5, 6, 7, 8, 202404), both read in Tab-A8-teardown.md, "why a GSI fits".
- A10e: vendor target-level 3 and a LineageOS 21 GSI shipping levels 4 to 8,
  as written up in a10e-firmware (its teardown, "Could it run LineageOS?").

usage: python3 tools/treble_fit_chart.py [output.png]
Colours and style follow the charts in a10e-firmware.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

BG = "#020617"; FG = "#e2e8f0"; MUTED = "#94a3b8"; GRID = "#1e293b"
BOX = "#1e293b"; HIT = "#a6e3a1"; MISS = "#f38ba8"; VENDOR = "#cba6f7"

SLOTS = ["3", "4", "5", "6", "7", "8", "202404"]
ROWS = [
    ("Galaxy A10e (SM-A102U)", "LineageOS 21 GSI", "3", ["4", "5", "6", "7", "8"]),
    ("Galaxy Tab A8 (SM-X200)", "LineageOS 22.2 GSI", "5", ["5", "6", "7", "8", "202404"]),
]

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "figures", "treble-fit.png")

plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
                     "text.color": FG, "font.size": 11, "font.family": "DejaVu Sans"})
fig, ax = plt.subplots(figsize=(12, 4.6), dpi=170)
ax.set_xlim(-3.6, len(SLOTS) + 2.4)
ax.set_ylim(-0.9, len(ROWS) * 2 - 0.1)
ax.axis("off")

for i, slot in enumerate(SLOTS):
    ax.text(i + 0.5, len(ROWS) * 2 - 0.45, slot, ha="center", va="center", color=MUTED, fontsize=10)
ax.text(-3.5, len(ROWS) * 2 - 0.45, "Treble level", ha="left", va="center", color=MUTED, fontsize=10)

for r, (device, gsi, vendor, ships) in enumerate(ROWS):
    y = (len(ROWS) - 1 - r) * 2
    fits = vendor in ships
    ax.text(-3.5, y + 0.62, device, ha="left", va="center", fontsize=12, fontweight="bold")
    ax.text(-3.5, y + 0.18, gsi, ha="left", va="center", fontsize=9.5, color=MUTED)
    for i, slot in enumerate(SLOTS):
        shipped = slot in ships
        is_vendor = slot == vendor
        face = (HIT if fits else BOX) if (shipped and is_vendor) else (BOX if shipped else BG)
        edge = VENDOR if is_vendor else (GRID if not shipped else "#475569")
        ax.add_patch(FancyBboxPatch((i + 0.08, y + 0.02), 0.84, 0.76,
                                    boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=face, ec=edge, lw=2.2 if is_vendor else 1,
                                    ls="-" if (shipped or is_vendor) else ":"))
        if shipped:
            ax.text(i + 0.5, y + 0.4, "GSI", ha="center", va="center", fontsize=9,
                    color=BG if (is_vendor and fits) else MUTED)
        if is_vendor:
            ax.text(i + 0.5, y - 0.22, "vendor", ha="center", va="center", fontsize=9, color=VENDOR)
    ax.text(len(SLOTS) + 0.3, y + 0.4,
            "a match - it pairs" if fits else "no match - can't pair",
            ha="left", va="center", fontsize=11, color=HIT if fits else MISS)

fig.text(0.02, 0.03, "a box marked GSI is a framework matrix level that GSI ships. "
         "the outlined box is the level the device's vendor partition declares.",
         fontsize=9, color=MUTED)
fig.savefig(out, bbox_inches="tight", pad_inches=0.3)
print(out)
