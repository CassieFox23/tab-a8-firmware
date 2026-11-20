#!/usr/bin/env python3
"""Print the root `model` and `compatible` of every device tree in a file.

Reads a plain .dtb, or an Android dt_table container (magic d7b7ab1e, the
format of dtbo.img and of the dtb area in a v2 boot.img). Also counts the
nodes and the distinct `compatible` strings in each tree.

usage: python3 tools/dt_root.py <dtb-or-dt_table> [...]
"""
import struct
import sys

FDT_MAGIC = 0xD00DFEED
TABLE_MAGIC = 0xD7B7AB1E


def trees(blob):
    magic = struct.unpack_from(">I", blob, 0)[0]
    if magic == FDT_MAGIC:
        yield 0, blob
        return
    if magic != TABLE_MAGIC:
        raise SystemExit("not a dtb or a dt_table")
    (_m, _total, _hsize, esize, ecount, eoff, _page, _ver) = struct.unpack_from(">8I", blob, 0)
    for i in range(ecount):
        size, off = struct.unpack_from(">2I", blob, eoff + i * esize)
        yield i, blob[off:off + size]


def walk(dtb):
    (magic, _total, off_struct, off_strings) = struct.unpack_from(">4I", dtb, 0)
    if magic != FDT_MAGIC:
        raise SystemExit("entry is not a flattened device tree")
    pos, depth, nodes = off_struct, 0, 0
    root, compat = {}, set()
    while True:
        token = struct.unpack_from(">I", dtb, pos)[0]
        pos += 4
        if token == 1:
            end = dtb.index(b"\0", pos)
            pos = (end + 4) & ~3
            depth += 1
            nodes += 1
        elif token == 2:
            depth -= 1
        elif token == 3:
            length, nameoff = struct.unpack_from(">2I", dtb, pos)
            pos += 8
            value = dtb[pos:pos + length]
            pos = (pos + length + 3) & ~3
            start = off_strings + nameoff
            name = dtb[start:dtb.index(b"\0", start)].decode()
            if name == "compatible":
                strings = [s.decode(errors="replace") for s in value.split(b"\0") if s]
                compat.update(strings)
                if depth == 1:
                    root[name] = strings
            elif name == "model" and depth == 1:
                root[name] = value.rstrip(b"\0").decode(errors="replace")
        elif token == 4:
            continue
        elif token == 9:
            break
        else:
            raise SystemExit(f"bad token {token:#x} at {pos - 4:#x}")
    return root, nodes, compat


for path in sys.argv[1:]:
    blob = open(path, "rb").read()
    for index, dtb in trees(blob):
        root, nodes, compat = walk(dtb)
        print(f"{path} [{index}] {len(dtb)} bytes, {nodes} nodes, {len(compat)} distinct compatible strings")
        print(f"  model:      {root.get('model', '-')}")
        print(f"  compatible: {', '.join(root.get('compatible', ['-']))}")
