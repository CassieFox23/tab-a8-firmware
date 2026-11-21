# Tools

Small Python scripts, standard library only, apart from matplotlib for the charts and numpy for `pin_base.py`. Most take file paths as arguments, so keep the firmware wherever you like. `pit_table.py` and `partition_chart.py` read `samloader print-pit` output on stdin instead. The four charts with their numbers written in (`memory_map_chart.py`, `treble_fit_chart.py`, `tool_calls_chart.py`, `cost_chart.py`) redraw their picture in `figures/` unless you give them another path.

| Script | What it does | Needs |
|---|---|---|
| `md5_check.py` | Checks a `.tar.md5` bundle against the md5 line at its end | Python 3 |
| `pit_table.py` | Turns `samloader print-pit -f <file.pit>` output into a Markdown table | Python 3, [`samloader`](https://github.com/topjohnwu/samloader-rs) for the input |
| `partition_chart.py` | Draws every partition in a PIT as a bar chart, coloured by which bundle ships an image for it | Python 3, matplotlib, `samloader` for the input |
| `cost_chart.py` | Draws what the work would cost at API prices per model, and the tokens per session behind it; the counts and prices are written in the script | Python 3, matplotlib |
| `memory_map_chart.py` | Draws where the boot stages and buffers sit in memory; the addresses are written in the script | Python 3, matplotlib |
| `tool_calls_chart.py` | Draws how many tool calls each session made while the repo was built, split by kind; the counts are written in the script | Python 3, matplotlib |
| `treble_fit_chart.py` | Draws each device's vendor Treble level against the levels its GSI ships; the numbers are written in the script | Python 3, matplotlib |
| `bl_sizing.py` | Sizes up the BL bundle's files: container, body hash, certificate, RSA-PSS signature check, which key names which, entropy, strings. `--plot` draws the entropy chart | Python 3, matplotlib only for `--plot` |
| `pin_base.py` | Finds the load address of a raw ARM64 image: votes on pointer-minus-string offsets, then checks the ADRP page phase. `--high` looks for pointers at the top of the 64-bit space (a kernel like Trusty's), `--end N` stops before data packed in behind the code | Python 3, numpy |
| `a64_refs.py` | Finds the code in a raw ARM64 image that points at an address or a string, and the function it sits in | Python 3 |
| `dt_root.py` | Prints the root `model` and `compatible` of each device tree in a `.dtb` or an Android `dt_table` (like `dtbo.img`), with node counts | Python 3 |
