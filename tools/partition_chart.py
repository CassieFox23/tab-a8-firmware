#!/usr/bin/env python3
"""Bar chart of every partition in a PIT, coloured by which firmware bundle
ships an image for it.

usage: samloader print-pit -f GTA8WIFI_EUR_OPEN.pit | \\
       python3 tools/partition_chart.py figures/partition-map.png BL_*.tar.md5 AP_*.tar.md5 CSC_*.tar.md5

Sizes assume 512-byte blocks. A partition with a block count of 0 (userdata
here) is listed in the footnote and not drawn.
Colours and style follow the charts in a10e-firmware.
"""
import os
import re
import sys
import tarfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

BG = "#020617"; FG = "#e2e8f0"; MUTED = "#94a3b8"; GRID = "#1e293b"
COLOURS = {"BL": "#cba6f7", "AP": "#89dceb", "CSC": "#a6e3a1", None: "#475569"}
LABELS = {"BL": "image in the BL bundle", "AP": "image in the AP bundle",
          "CSC": "image in the CSC bundle", None: "no image in this firmware"}

out = sys.argv[1]
shipped = {}
for path in sys.argv[2:]:
    bundle = os.path.basename(path).split("_")[0]
    if bundle == "HOME":
        bundle = "CSC"
    with tarfile.open(path, "r:") as tar:
        for member in tar:
            if member.isfile():
                shipped.setdefault(os.path.basename(member.name), bundle)

text = sys.stdin.read()
rows, skipped = [], []
for block in re.split(r"^--- Entry #", text, flags=re.M)[1:]:
    def field(name):
        m = re.search(rf"^{re.escape(name)}: ?(.*)$", block, re.M)
        return m.group(1).strip() if m else ""
    name, count = field("Partition Name"), int(field("Partition Block Count") or 0)
    if count == 0:
        skipped.append(name)
        continue
    rows.append((name, count * 512 / 1048576, shipped.get(field("Flash Filename"))))

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": FG, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": FG,
    "axes.edgecolor": GRID, "grid.color": GRID, "font.size": 10, "font.family": "DejaVu Sans",
})
fig, ax = plt.subplots(figsize=(11, 0.27 * len(rows) + 2.4), dpi=170)
ys = range(len(rows))
ax.barh(ys, [r[1] for r in rows], color=[COLOURS[r[2]] for r in rows], height=0.72)
ax.set_xscale("log")
ax.set_xlim(0.01, max(r[1] for r in rows) * 12)
ax.set_yticks(list(ys))
ax.set_yticklabels([r[0] for r in rows], fontsize=8.5, family="DejaVu Sans Mono")
ax.set_ylim(len(rows) - 0.4, -0.6)
ax.grid(True, axis="x", lw=0.8)
ax.set_axisbelow(True)
ax.tick_params(axis="both", length=0)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for (name, mib, _bundle), y in zip(rows, ys):
    label = f"{mib:,.0f} MiB" if mib >= 1 else f"{mib * 1024:,.0f} KiB"
    ax.text(mib * 1.25, y, label, va="center", fontsize=8, color=MUTED)
ax.set_xlabel("size in MiB, log scale (512-byte blocks)", labelpad=8)
ax.set_title(f"{len(rows) + len(skipped)} partitions, in the order they sit on the eMMC",
             loc="left", fontsize=13, pad=14, color=FG)
used = [k for k in ("BL", "AP", "CSC", None) if any(r[2] == k for r in rows)]
ax.legend(handles=[Patch(color=COLOURS[k], label=LABELS[k]) for k in used],
          loc="lower right", frameon=False, fontsize=9)
if skipped:
    fig.text(0.01, 0.008, "not drawn (block count 0 in the PIT): " + ", ".join(skipped),
             fontsize=8.5, color=MUTED)
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(out)
print(f"{out}: {len(rows)} drawn, {len(skipped)} not drawn; "
      + ", ".join(f"{k or 'none'}={sum(r[2] == k for r in rows)}" for k in ("BL", "AP", "CSC", None)))
