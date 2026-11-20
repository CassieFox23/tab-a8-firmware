#!/usr/bin/env python3
"""Chart: where the Tab A8's boot stages and buffers sit in memory.

No firmware needed, the addresses are written in below. Each one is read in
Tab-A8-teardown.md: the two load addresses in "pinning the load addresses",
the TEE addresses in "what the SPL does", and the rest in "what lk does about
verified boot" (the functions named in the notes column).

A bar is drawn where the size is known. A dot is an address with no size read.

usage: python3 tools/memory_map_chart.py [output.png]
Colours and style follow the charts in a10e-firmware.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BG = "#020617"; FG = "#e2e8f0"; MUTED = "#94a3b8"; GRID = "#1e293b"
CODE = "#a6e3a1"; TEE = "#f38ba8"; BUF = "#89b4fa"; IMG = "#cba6f7"

MIB = 1 << 20
# name, address, size in bytes or None, colour, note
ROWS = [
    ("download buffer", 0x82000000, 256 * MIB, BUF, "256 MiB, set when Download Mode starts"),
    ("l_agdsp image", 0x89000000, 6 * MIB, IMG, "6 MiB, inside the download buffer's range"),
    ("sml (BL31)", 0x94000000, None, TEE, "where the SPL's TEE config points to start with"),
    ("teecfg", 0x94040000, None, TEE, "loaded by the SPL"),
    ("trustos (Trusty)", 0x94060000, None, TEE, "where the SPL's TEE config points to start with"),
    ("staging buffer", 0x9A000000, None, BUF, "images are copied out of here after the check"),
    ("lk, the bootloader", 0x9F000000, 4402800, CODE, "4.2 MiB body, header just below at 0x9efffe00"),
    ("boot / recovery image", 0xB0000000, None, IMG, "loaded here to be checked"),
    ("vbmeta read buffer", 0xD0000000, None, BUF, "used by Samsung's official-or-custom tally"),
]
LO, HI = 0x80000000, 0xD8000000

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "figures", "memory-map.png")

plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
                     "text.color": FG, "font.size": 11, "font.family": "DejaVu Sans"})
fig, ax = plt.subplots(figsize=(13, 6.4), dpi=170)
n = len(ROWS)
span = HI - LO
ax.set_xlim(LO - span * 0.50, HI + span * 0.62)
ax.set_ylim(-1.9, n + 0.9)
ax.axis("off")

for tick in range(LO, HI + 1, 0x10000000):
    ax.plot([tick, tick], [-0.5, n - 0.3], color=GRID, lw=1, zorder=0)
    ax.text(tick, n - 0.05, f"0x{tick:08x}", ha="center", va="bottom", color=MUTED,
            fontsize=8, rotation=45, rotation_mode="anchor")

for i, (name, addr, size, colour, note) in enumerate(ROWS):
    y = n - 1 - i
    ax.text(LO - span * 0.49, y + 0.12, name, ha="left", va="center", fontsize=11.5, fontweight="bold")
    ax.text(LO - span * 0.49, y - 0.26, f"0x{addr:08x}", ha="left", va="center", fontsize=9.5,
            color=MUTED, family="DejaVu Sans Mono")
    if size:
        width = max(size, span * 0.006)
        ax.barh(y, width, left=addr, height=0.5, color=colour, zorder=2)
    else:
        ax.plot([addr], [y], marker="o", ms=9, color=colour, zorder=2)
    ax.text(HI + span * 0.03, y, note, ha="left", va="center", fontsize=9.5, color=MUTED)

ax.text(LO - span * 0.49, -1.05,
        "not on this scale: the SPL, the first stage, runs far below all of this at 0x00005700 (59 KiB, header at 0x5500)",
        ha="left", va="center", fontsize=10, color=CODE)

for j, (colour, label) in enumerate([(CODE, "bootloader code"), (TEE, "secure world"),
                                     (IMG, "an image being checked"), (BUF, "a buffer")]):
    x = LO - span * 0.48 + j * span * 0.46
    ax.plot([x], [-1.62], marker="s", ms=9, color=colour)
    ax.text(x + span * 0.02, -1.62, label, ha="left", va="center", fontsize=9.5, color=MUTED)

fig.savefig(out, bbox_inches="tight", pad_inches=0.3)
print(out)
