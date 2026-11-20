#!/usr/bin/env python3
"""Find the load address of a raw ARM64 image by voting.

Every 8-byte value in the image that could be a pointer is paired with every
string start; if the image is loaded at BASE, then pointer - string offset
equals BASE for each pointer that really points at a string. The right BASE
collects far more votes than anything else.

It then checks the answer a second way: ADRP instructions only work out if
the low 12 bits of BASE (the page phase) are right, so it counts how many
ADRP+ADD pairs land on a string for each phase.

usage: python3 tools/pin_base.py IMAGE [--skip N]
--skip N drops the first N bytes (0x200 for a DHTB file, to get to the body).
Needs numpy.
"""
import re
import sys

import numpy as np

path = sys.argv[1]
skip = int(sys.argv[sys.argv.index("--skip") + 1], 0) if "--skip" in sys.argv else 0
data = open(path, "rb").read()[skip:]
size = len(data)

strings = np.array([m.start() for m in re.finditer(rb"(?<![ -~])[ -~]{6,}\x00", data)], dtype=np.int64)
words = np.frombuffer(data[:size - size % 8], dtype="<u8")
cand = np.unique(words[(words > 0x10000) & (words < 0x1_0000_0000_0000)]).astype(np.int64)
print(f"{path}: body {size} bytes, {len(strings)} strings, {len(cand)} distinct pointer-sized values")

votes = {}
for chunk in np.array_split(strings, max(1, len(strings) // 400)):
    diff = (cand[:, None] - chunk[None, :]).ravel()
    diff = diff[diff > 0]
    vals, counts = np.unique(diff, return_counts=True)
    keep = counts >= 2
    for v, c in zip(vals[keep], counts[keep]):
        votes[int(v)] = votes.get(int(v), 0) + int(c)
top = sorted(votes.items(), key=lambda kv: -kv[1])[:5]
for base, n in top:
    print(f"  base {base:#x}: {n} pointers land on a string start")
if len(top) > 1:
    print(f"  winner leads the runner-up {top[0][1]} to {top[1][1]}")

# second check, independent of the first: ADRP works on 4 KiB pages, so the
# base's low 12 bits (its "page phase") decide where every ADRP+ADD lands.
# count, for each phase, how many of those land on a string start.
words = np.frombuffer(data[:size - size % 4], dtype="<u4").astype(np.int64)
string_set = set(strings.tolist())
pairs = []
for i in np.nonzero((words & 0x9F000000) == 0x90000000)[0]:
    w = int(words[i]); rd = w & 31
    imm = ((w >> 5) & 0x7FFFF) << 2 | (w >> 29) & 3
    imm = (imm - (1 << 21) if imm & (1 << 20) else imm) << 12
    for j in range(i + 1, min(i + 6, len(words))):
        x = int(words[j])
        if x & 0xFFC00000 == 0x91000000 and (x >> 5) & 31 == rd:
            pairs.append((int(i) * 4, imm, (x >> 10) & 0xFFF))
            break
scores = sorted(((sum(1 for off, imm, lo in pairs
                      if (((ph + off) & ~0xFFF) + imm + lo - ph) in string_set), ph)
                 for ph in range(0, 0x1000, 0x10)), reverse=True)[:3]
print(f"  ADRP+ADD pairs: {len(pairs)}; best page phases: "
      + ", ".join(f"{ph:#05x} ({n} land on strings)" for n, ph in scores))
