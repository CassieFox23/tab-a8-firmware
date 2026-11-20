#!/usr/bin/env python3
"""Find the code in a raw ARM64 image that points at given addresses.

Decodes ADRP+ADD and ADR, the two ways ARM64 code builds an address, and
prints each place that lands on a target, with the start of the function it
sits in (the nearest `stp x29, x30, [sp, #-N]!` above it). A target can be a
hex address or a quoted string to look up in the image.

usage: python3 tools/a64_refs.py IMAGE BASE TARGET [TARGET...]
  e.g. python3 tools/a64_refs.py lk.body 0x9f000000 0x9f14c5d0 "KG locked"
"""
import struct
import sys

path, base = sys.argv[1], int(sys.argv[2], 0)
data = open(path, "rb").read()
n = len(data) & ~3
words = struct.unpack(f"<{n // 4}I", data[:n])


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def func_start(index):
    for j in range(index, max(index - 4000, -1), -1):
        w = words[j]
        if w & 0xFFC07FFF == 0xA9807BFD:      # stp x29, x30, [sp, #-N]!
            return base + j * 4
        if w & 0xFF0003FF == 0xD10003FF and j and words[j - 1] == 0xD65F03C0:
            return base + j * 4               # sub sp, sp, #N right after a ret
    return None


targets = {}
for arg in sys.argv[3:]:
    try:
        targets[int(arg, 16)] = arg
    except ValueError:
        needle = arg.encode()
        pos = data.find(needle)
        while pos >= 0:
            start = pos
            while start and 32 <= data[start - 1] < 127:
                start -= 1
            targets[base + start] = data[start:data.index(b"\0", start)].decode(errors="replace")[:60]
            pos = data.find(needle, pos + 1)

hits = {t: [] for t in targets}
for i, w in enumerate(words):
    pc = base + i * 4
    if w & 0x9F000000 == 0x10000000:          # adr
        imm = sx(((w >> 5) & 0x7FFFF) << 2 | (w >> 29) & 3, 21)
        if pc + imm in hits:
            hits[pc + imm].append(i)
    elif w & 0x9F000000 == 0x90000000:        # adrp
        rd = w & 31
        page = (pc & ~0xFFF) + (sx(((w >> 5) & 0x7FFFF) << 2 | (w >> 29) & 3, 21) << 12)
        for j in range(i + 1, min(i + 6, len(words))):
            x = words[j]
            if x & 0xFFC00000 == 0x91000000 and (x >> 5) & 31 == rd:   # add xN, xRd, #imm
                addr = page + ((x >> 10) & 0xFFF)
                if addr in hits:
                    hits[addr].append(j)
                break
            if x & 31 == rd and x & 0x9F000000 in (0x90000000, 0x10000000):
                break

for t, label in targets.items():
    print(f"{t:#x}  {label}")
    for i in hits[t]:
        fs = func_start(i)
        print(f"    used at {base + i * 4:#x}, in the function starting {fs:#x}" if fs else
              f"    used at {base + i * 4:#x}")
    if not hits[t]:
        print("    no ADRP+ADD or ADR lands here")
