#!/usr/bin/env python3
"""Check a Samsung .tar.md5 bundle against the md5 line at its end.

The file ends with one text line: "<md5>  <name>". In some bundles zero bytes
run right up to that line with no newline before it, so the cut is made at
the hash itself and not at the last newline before it.

usage: python3 tools/md5_check.py <bundle.tar.md5> [...]
"""
import hashlib
import os
import re
import sys

bad = 0
for path in sys.argv[1:]:
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        f.seek(max(0, size - 512))
        tail = f.read()
        m = re.search(rb"([0-9a-f]{32})  [^\n\0]+\n$", tail)
        if not m:
            print(f"{os.path.basename(path)}: no md5 line at the end")
            bad = 1
            continue
        want = m.group(1).decode()
        left = size - (len(tail) - m.start())
        f.seek(0)
        h = hashlib.md5()
        while left > 0:
            chunk = f.read(min(1 << 24, left))
            h.update(chunk)
            left -= len(chunk)
    ok = h.hexdigest() == want
    bad |= not ok
    print(f"{os.path.basename(path)}: {want} {'match' if ok else 'DIFFERS, got ' + h.hexdigest()}")
sys.exit(bad)
