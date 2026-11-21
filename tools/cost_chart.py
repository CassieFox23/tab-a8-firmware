#!/usr/bin/env python3
"""Chart: what building and reading this repo would have cost at API prices,
and the tokens behind it.

No firmware needed, the numbers are written in below. Tokens were counted from
the three sessions' transcripts (and their helper agents) at about 7:46 PM on
20 Nov 2026 with one session still going, so this is a snapshot. Prices are
USD per million tokens from models.dev, read the same day. The work ran on a
subscription: this is an estimate of the per-token price, not a bill.

The bars show the high end of the estimate, where the three main sessions'
one-hour cache writes are priced at twice the input rate. The low end, printed
beside each bar, prices every cache write at the listed rate.

usage: python3 tools/cost_chart.py [output.png]
Colours and style follow the charts in a10e-firmware.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BG = "#020617"; FG = "#e2e8f0"; MUTED = "#94a3b8"; GRID = "#1e293b"
OUT = "#a6e3a1"; READ = "#89b4fa"; WRITE = "#cba6f7"; NEW = "#f9e2af"

# model, where it ran, uncached in, output, cache read, cache write,
# prices (input, output, cache read, cache write), one-hour cache (True/False)
MODELS = [
    ("Fable 5.2", "the build and the review", 1096, 500848, 185727852, 1352769, (8, 40, 0.2, 10), True),
    ("Opus 4.8", "most of the secure world", 448, 365811, 91854082, 542882, (5, 25, 0.5, 6.25), True),
    ("Sonnet 5.5", "six helper agents", 672, 366253, 41777663, 1970862, (2, 10, 0.1, 2.5), False),
    ("Opus 5.5", "start of the secure world", 74, 24871, 3768173, 144437, (4, 20, 0.2, 5), True),
    ("Haiku 5.5", "one helper agent", 30, 36274, 637626, 81089, (0.1, 0.5, 0.01, 0.125), False),
]
# session, written, new input, re-read from cache (tokens)
SESSIONS = [
    ("the build", 240_000, 775_000, 71_400_000),
    ("the secure world", 427_000, 769_000, 96_300_000),
    ("the review", 627_000, 2_551_000, 156_100_000),
]

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "figures", "cost-and-tokens.png")

rows = []
for name, where, tin, tout, tread, twrite, (pin, pout, pread, pwrite), hour in MODELS:
    c_out = tout * pout / 1e6
    c_read = tread * pread / 1e6
    c_in = tin * pin / 1e6
    low_write = twrite * pwrite / 1e6
    high_write = twrite * (2 * pin if hour else pwrite) / 1e6
    rows.append((name, where, c_out, c_read, high_write, c_out + c_read + c_in + low_write,
                 c_out + c_read + c_in + high_write))
low = sum(r[5] for r in rows)
high = sum(r[6] for r in rows)

plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
                     "text.color": FG, "font.size": 11, "font.family": "DejaVu Sans"})
fig, (a, b) = plt.subplots(2, 1, figsize=(13, 8.2), dpi=170, gridspec_kw={"height_ratios": [5, 3.4]})

# panel 1: cost per model
top = max(r[6] for r in rows)
n = len(rows)
a.set_xlim(-top * 0.62, top * 1.42)
a.set_ylim(-1.25, n + 0.35)
a.axis("off")
a.text(-top * 0.61, n - 0.05, f"what it would cost at API prices: about \\${low:.0f} to \\${high:.0f}",
       ha="left", va="center", fontsize=13, fontweight="bold")
for i, (name, where, c_out, c_read, c_write, lo, hi) in enumerate(rows):
    y = n - 1.1 - i
    a.text(-top * 0.61, y + 0.13, name, ha="left", va="center", fontsize=12, fontweight="bold")
    a.text(-top * 0.61, y - 0.2, where, ha="left", va="center", fontsize=8.5, color=MUTED)
    left = 0
    for value, colour in ((c_out, OUT), (c_read, READ), (c_write, WRITE)):
        a.barh(y, value, left=left, height=0.5, color=colour)
        if value >= top * 0.07:
            a.text(left + value / 2, y, f"\\${value:.2f}", ha="center", va="center", fontsize=9.5, color=BG)
        left += value
    label = f"\\${hi:.2f}" if abs(hi - lo) < 0.005 else f"\\${lo:.2f} to \\${hi:.2f}"
    a.text(left + top * 0.02, y, label, ha="left", va="center", fontsize=11)
for j, (colour, text) in enumerate(((OUT, "what the models wrote"),
                                    (READ, "re-reading the conversation from cache"),
                                    (WRITE, "writing the conversation to cache"))):
    x = -top * 0.60 + j * top * 0.64
    a.plot([x], [-0.95], marker="s", ms=9, color=colour)
    a.text(x + top * 0.025, -0.95, text, ha="left", va="center", fontsize=9.5, color=MUTED)

# panel 2: tokens per session
m = len(SESSIONS)
wide = max(s[1] + s[2] for s in SESSIONS)
b.set_xlim(-wide * 0.62, wide * 1.42)
b.set_ylim(-1.25, m + 0.35)
b.axis("off")
b.text(-wide * 0.61, m - 0.05, "the tokens behind it, per session", ha="left", va="center",
       fontsize=13, fontweight="bold")
for i, (name, written, new, reread) in enumerate(SESSIONS):
    y = m - 1.1 - i
    b.text(-wide * 0.61, y, name, ha="left", va="center", fontsize=12, fontweight="bold")
    b.barh(y, written, height=0.5, color=OUT)
    b.text(written / 2, y, f"{written / 1000:.0f}k", ha="center", va="center", fontsize=9.5, color=BG)
    b.barh(y, new, left=written, height=0.5, color=NEW)
    b.text(written + new / 2, y, f"{new / 1000:.0f}k", ha="center", va="center", fontsize=9.5, color=BG)
    b.text(written + new + wide * 0.02, y, f"+ {reread / 1e6:.1f}M re-read", ha="left", va="center",
           fontsize=11, color=READ)
for j, (colour, text) in enumerate(((OUT, "written"), (NEW, "new input"),
                                    (READ, "re-read from cache - far too big to draw to scale"))):
    x = -wide * 0.60 + j * wide * 0.36
    b.plot([x], [-0.95], marker="s", ms=9, color=colour)
    b.text(x + wide * 0.025, -0.95, text, ha="left", va="center", fontsize=9.5, color=MUTED)

fig.text(0.02, 0.01, "an estimate, not a bill: the work ran on a subscription. counted from the sessions' transcripts "
         "at about 7:46 PM on 20 Nov 2026, one session still going. prices from models.dev.",
         fontsize=9, color=MUTED)
fig.subplots_adjust(hspace=0.08)
fig.savefig(out, bbox_inches="tight", pad_inches=0.3)
print(out, f"low {low:.2f} high {high:.2f}")
