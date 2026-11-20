# how the code was read

most of this teardown is files unpacked and read with ordinary tools - `debugfs` into the vendor and system images, `avbtool` on vbmeta, `strings`, and the small scripts in [`tools/`](../tools/README.md). those reads each carry their own command in the [teardown](../Tab-A8-teardown.md), next to what they found.

the bootloader (`lk`) and the secure world (`trustos`) are different. they're raw ARM64 code with no headers and no symbol names - just megabytes of instructions. to read those, the teardown uses [REA](https://github.com/morluto/rea), which drives a [Ghidra](https://github.com/NationalSecurityAgency/ghidra) analysis engine: you open the raw image, tell it the CPU and the address it loads at (worked out first with [`tools/pin_base.py`](../tools/README.md)), then ask about functions by address. only a handful of functions in each image were read - the ones on the paths that answer a question - not the whole binary.

these are the REA tools that did it, grouped by what they're for; how many of each it took is in [what it took](what-it-took.md).

## getting a file open

| tool | what it's for |
|---|---|
| `open_binary` | loads a raw image and analyses it. these blobs have no header, so you pass the architecture (`arm64`) and the load address, and then every reference lands on the right place |
| `close_binary` | frees the analysis engine when you're done. REA runs one engine at a time, so you close one image before opening the next |
| `binary_session` | reports what's open and which engine is available, without starting any analysis |

## reading a function

| tool | what it's for |
|---|---|
| `procedure_pseudo_code` | the workhorse - turns one function's machine code back into readable C-like pseudocode. this is what "reading a function" means here |
| `batch_decompile` | the same, for several functions at once |

## following the threads between functions

these are the cheap ones. a single function can be ten thousand characters; often you don't need to read it, just to know what it touches. these answer that without a full decompile.

| tool | what it's for |
|---|---|
| `procedure_callees` | lists the functions this one calls. the callees' names often say what a function does before you read a line of it - that's how the secure world's vbmeta handler was spotted as the AVB path |
| `procedure_callers` | lists what calls this function. "nothing calls it" is a real answer - it's how the dead-twin `0x9f1206d0` was caught |
| `xrefs` | every place in the code that touches one address - used to find everything that sets and reads the boot-state variable |
| `resolve_containing_procedure` | given any address (say, the code at a log string), the function it sits inside, and that function's size |

the pattern is always the same: `open` the image, `procedure_pseudo_code` to read a function, and the relationship tools to follow threads to the next function worth reading - so a question gets answered without decompiling the whole thing.

## reproducing it

the two images are carved from the stock BL bundle:

- `lk.body` is the 4,402,800-byte body of `lk-sign.bin` - the bytes after the 512-byte DHTB header and before the trailing certificate: `tail -c +513 lk-sign.bin | head -c 4402800` - loaded at `0x9f000000`
- `tos-kernel.body` is the first `0xbc000` bytes of `tos-sign.bin`'s body (the Trusty kernel, before the packed apps): `tail -c +513 tos-sign.bin | head -c 770048` - loaded at `0xffffffffe0000000`

both load addresses come from `tools/pin_base.py`. open either image at its address in REA and the function addresses named in the [teardown](../Tab-A8-teardown.md) resolve.

the tool-call counts, the token totals and an API-price cost estimate for building the repo are on their own page: [what it took](what-it-took.md).
