# How the code was read

Most of this teardown is files unpacked and read with ordinary tools: `debugfs` into the vendor and system images, `avbtool` on vbmeta, `strings`, and the small scripts in [`tools/`](../tools/README.md). Those reads each carry their own command in the [teardown](../Tab-A8-teardown.md), next to what they found.

The bootloader (`lk`) and the secure world (`trustos`) are different. They're raw ARM64 code with no headers and no symbol names, just megabytes of instructions. To read those, the teardown uses [REA](https://github.com/morluto/rea), which drives a [Ghidra](https://github.com/NationalSecurityAgency/ghidra) analysis engine: you open the raw image, tell it the CPU and the address it loads at (worked out first with [`tools/pin_base.py`](../tools/README.md)), then ask about functions by address. Only a handful of functions in each image were read, the ones on the paths that answer a question, not the whole binary.

These are the REA tools that did it, grouped by what they're for. How many of each it took is in [what it took](what-it-took.md).

## Getting a file open

| Tool | What it's for |
|---|---|
| `open_binary` | Loads a raw image and analyses it. These blobs have no header, so you pass the architecture (`arm64`) and the load address, and then every reference lands on the right place |
| `close_binary` | Frees the analysis engine when you're done. REA runs one engine at a time, so you close one image before opening the next |
| `binary_session` | Reports what's open and which engine is available, without starting any analysis |

## Reading a function

| Tool | What it's for |
|---|---|
| `procedure_pseudo_code` | The workhorse: turns one function's machine code back into readable C-like pseudocode. This is what "reading a function" means here |
| `batch_decompile` | The same, for several functions at once |

## Following the threads between functions

These are the cheap ones. A single function can be ten thousand characters; often you don't need to read it, just to know what it touches. These answer that without a full decompile.

| Tool | What it's for |
|---|---|
| `procedure_callees` | Lists the functions this one calls. The callees' names often say what a function does before you read a line of it. That's how the secure world's vbmeta handler was spotted as the AVB path |
| `procedure_callers` | Lists what calls this function. "Nothing calls it" is a real answer. It's how the dead-twin `0x9f1206d0` was caught |
| `xrefs` | Every place in the code that touches one address, used to find everything that sets and reads the boot-state variable |
| `resolve_containing_procedure` | Given any address (say, the code at a log string), the function it sits inside, and that function's size |

The pattern is always the same: `open` the image, `procedure_pseudo_code` to read a function, and the relationship tools to follow threads to the next function worth reading, so a question gets answered without decompiling the whole thing.

## Reproducing it

The two images are carved from the stock BL bundle:

- `lk.body` is the 4,402,800-byte body of `lk-sign.bin`, the bytes after the 512-byte DHTB header and before the trailing certificate (`tail -c +513 lk-sign.bin | head -c 4402800`), loaded at `0x9f000000`
- `tos-kernel.body` is the first `0xbc000` bytes of `tos-sign.bin`'s body (the Trusty kernel, before the packed apps): `tail -c +513 tos-sign.bin | head -c 770048`, loaded at `0xffffffffe0000000`

Both load addresses come from `tools/pin_base.py`. Open either image at its address in REA and the function addresses named in the [teardown](../Tab-A8-teardown.md) resolve.

The tool-call counts, the token totals and an API-price cost estimate for building the repo are on their own page: [what it took](what-it-took.md).
