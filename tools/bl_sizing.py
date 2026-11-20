#!/usr/bin/env python3
"""Size up the files in the SM-X200 BL bundle without disassembling anything.

For each file: which container it is, whether the hashes and signatures in it
check out, how random the bytes look, and how much readable text there is.

What it knows how to read:
- the "DHTB" container: a 512-byte header holding the payload size (0x30) and
  the payload's SHA-256 (0x08), the payload, a "SIMGHDR" block giving the
  certificate's offset and size, the certificate, then a 512-byte
  "SignerVer02" block.
- the certificate: type, RSA key (bits, e, modulus), SHA-256 of the payload,
  for type 1 a SHA-256 of the next stage's key, two words, then an
  RSASSA-PSS signature (SHA-256, MGF1, 32-byte salt) over everything from the
  payload hash up to the signature.
- an AVB footer, by its "AVBf" magic in the last 64 bytes.

usage: python3 tools/bl_sizing.py [--vbmeta vbmeta.img] [--plot out.png] FILE [FILE...]
--vbmeta lets it say whether a "next key" hash is the AVB key in that image.
--plot needs matplotlib.
"""
import collections
import hashlib
import math
import os
import re
import struct
import sys


def entropy(data):
    if not data:
        return 0.0
    n = len(data)
    return -sum(c / n * math.log2(c / n) for c in collections.Counter(data).values())


def windows(data, size=4096):
    return [entropy(data[i:i + size]) for i in range(0, len(data), size)]


def mgf1(seed, length):
    out, i = b"", 0
    while len(out) < length:
        out += hashlib.sha256(seed + i.to_bytes(4, "big")).digest()
        i += 1
    return out[:length]


def pss_ok(em, mhash):
    if em[-1] != 0xBC:
        return False
    h, masked = em[-33:-1], em[:-33]
    db = bytes(a ^ b for a, b in zip(masked, mgf1(h, len(masked))))
    db = bytes([db[0] & 0x7F]) + db[1:]
    one = db.find(b"\x01")
    if one < 0 or any(db[:one]):
        return False
    return hashlib.sha256(b"\0" * 8 + mhash + db[one + 1:]).digest() == h


def key_id(cert):
    """SHA-256 over key bits + exponent + modulus, as a type 1 cert stores it."""
    return hashlib.sha256(cert[4:268]).digest()


def read_dhtb(data):
    size = struct.unpack_from("<I", data, 0x30)[0]
    payload = data[512:512 + size]
    info = {"payload": payload,
            "header_hash_ok": hashlib.sha256(payload).digest() == data[8:40]}
    simg = 512 + size
    if data[simg:simg + 7] != b"SIMGHDR":
        return info
    cert_size, cert_off = struct.unpack_from("<QQ", data, simg + 32)
    cert = data[cert_off:cert_off + cert_size]
    ctype, bits = struct.unpack_from("<II", cert, 0)
    n = int.from_bytes(cert[12:268], "big")
    em = pow(int.from_bytes(cert[-256:], "big"), int.from_bytes(cert[8:12], "big"), n)
    info.update(
        cert_type=ctype, key_bits=bits, key_id=key_id(cert),
        cert_hash_ok=cert[268:300] == hashlib.sha256(payload).digest(),
        next_key=cert[300:332] if ctype == 1 else None,
        sig_ok=pss_ok(em.to_bytes(256, "big"), hashlib.sha256(cert[268:-256]).digest()),
        signer=[s.decode() for s in re.findall(rb"[ -~]{6,}", data[cert_off + cert_size:])[:5]],
    )
    return info


def avb_key_hash(path):
    vb = open(path, "rb").read()
    auth = struct.unpack_from(">Q", vb, 0x0C)[0]
    off, size = struct.unpack_from(">QQ", vb, 0x40)
    return hashlib.sha256(vb[256 + auth + off:256 + auth + off + size]).digest()


args = sys.argv[1:]
plot = vbmeta = None
while args and args[0].startswith("--"):
    flag = args.pop(0)
    if flag == "--plot":
        plot = args.pop(0)
    elif flag == "--vbmeta":
        vbmeta = args.pop(0)
avb = avb_key_hash(vbmeta) if vbmeta else None

rows = []
for path in args:
    data = open(path, "rb").read()
    name = os.path.basename(path)
    row = {"name": name, "size": len(data), "data": data, "body": data, "kind": "no known header"}
    if data[:4] == b"DHTB":
        row.update(read_dhtb(data))
        row["kind"] = "DHTB signed"
        row["body"] = row["payload"]
    elif data[-64:-60] == b"AVBf":
        original = struct.unpack_from(">Q", data, len(data) - 64 + 12)[0]
        row["kind"] = "AVB footer"
        row["body"] = data[:original]
    body = row["body"]
    row["entropy"] = entropy(body)
    row["strings"] = len(re.findall(rb"[ -~]{8,}", body))
    row["a64_ret"] = sum(1 for i in range(0, len(body) - 3, 4) if body[i:i + 4] == b"\xc0\x03\x5f\xd6")
    rows.append(row)

ids = {r["key_id"]: r["name"] for r in rows if r.get("cert_type") is not None}
print("| file | bytes | container | body bytes | entropy | strings (8+) | AArch64 `ret` | hashes | signature | signing key | carries hash of |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    if r["kind"] == "DHTB signed":
        hashes = "ok" if r["header_hash_ok"] and r.get("cert_hash_ok") else "MISMATCH"
        sig = "ok" if r.get("sig_ok") else "FAILS"
        key = r["key_id"].hex()[:12]
        nk = r.get("next_key")
        if nk is None:
            nxt = "-"
        elif avb and nk == avb:
            nxt = "the AVB key in vbmeta"
        else:
            users = [x["name"] for x in rows if x.get("key_id") == nk]
            nxt = f"key {nk.hex()[:12]}" + (f" (signs {', '.join(users)})" if users else "")
    else:
        hashes = sig = key = nxt = "-"
    print(f"| `{r['name']}` | {r['size']} | {r['kind']} | {len(r['body'])} | {r['entropy']:.2f} | "
          f"{r['strings']} | {r['a64_ret']} | {hashes} | {sig} | {key} | {nxt} |")
for r in rows:
    if r.get("signer"):
        print(f"\n{r['name']} signer block: {' / '.join(r['signer'])}")
        break

if plot:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    BG = "#020617"; FG = "#e2e8f0"; MUTED = "#94a3b8"; GRID = "#1e293b"
    COL = {"DHTB signed": "#cba6f7", "AVB footer": "#89dceb", "no known header": "#f9e2af"}
    plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
                         "text.color": FG, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.edgecolor": GRID, "grid.color": GRID,
                         "font.size": 10, "font.family": "DejaVu Sans"})
    order = sorted(rows, key=lambda r: -r["size"])
    fig, axes = plt.subplots(len(order), 1, figsize=(12, 1.55 * len(order) + 1.2), dpi=170)
    for ax, r in zip(axes, order):
        w = windows(r["data"])
        xs = [i * 4096 / 1024 for i in range(len(w))]
        ax.fill_between(xs, w, color=COL[r["kind"]], alpha=0.85, linewidth=0)
        ax.set_ylim(0, 8.3); ax.set_xlim(0, max(xs[-1], 1))
        ax.set_yticks([0, 4, 8]); ax.grid(True, axis="y", lw=0.6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(length=0, labelsize=8)
        ax.set_title(f"{r['name']}   {r['size'] / 1024:,.0f} KiB   {r['kind']}   "
                     f"body entropy {r['entropy']:.2f}", loc="left", fontsize=10, pad=4)
    axes[-1].set_xlabel("offset in file, KiB (each file on its own scale)")
    fig.text(0.008, 0.5, "entropy per 4 KiB, bits per byte", rotation=90, va="center",
             color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0.02, 0, 1, 1))
    fig.savefig(plot)
    print(f"\n{plot}")
