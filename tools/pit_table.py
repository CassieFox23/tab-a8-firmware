#!/usr/bin/env python3
"""Turn `samloader print-pit -f <file.pit>` output into a markdown table.

usage: samloader print-pit -f GTA8WIFI_EUR_OPEN.pit | python3 tools/pit_table.py
"""
import re
import sys

text = sys.stdin.read()
header = {}
for key in ("Entry Count", "Project Name", "CPU/bootloader tag"):
    m = re.search(rf"^{re.escape(key)}: (.*)$", text, re.M)
    if m:
        header[key] = m.group(1).strip()
print(" | ".join(f"{k}: {v}" for k, v in header.items()))
print()
print("| # | id | partition | start block | blocks | MiB (512 B blocks) | flash file |")
print("|---|---|---|---|---|---|---|")
for block in re.split(r"^--- Entry #", text, flags=re.M)[1:]:
    num = block.split(" ", 1)[0]

    def field(name):
        m = re.search(rf"^{re.escape(name)}: ?(.*)$", block, re.M)
        return m.group(1).strip() if m else ""

    count = int(field("Partition Block Count") or 0)
    print(
        f"| {num} | {field('Partition ID')} | {field('Partition Name')} | "
        f"{field('Start Block')} | {count} | {count * 512 / 1048576:.1f} | "
        f"{field('Flash Filename') or '-'} |"
    )
