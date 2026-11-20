# tools

small python scripts, standard library only, apart from matplotlib for the charts and numpy for `pin_base.py`. each takes file paths as arguments, so keep the firmware wherever you like.

| script | what it does | needs |
|---|---|---|
| `md5_check.py` | checks a `.tar.md5` bundle against the md5 line at its end | python 3 |
| `pit_table.py` | turns `samloader print-pit -f <file.pit>` output into a markdown table | python 3, [`samloader`](https://github.com/topjohnwu/samloader-rs) for the input |
| `partition_chart.py` | draws every partition in a PIT as a bar chart, coloured by which bundle ships an image for it | python 3, matplotlib, `samloader` for the input |
| `treble_fit_chart.py` | draws each device's vendor Treble level against the levels its GSI ships; the numbers are written in the script | python 3, matplotlib |
| `bl_sizing.py` | sizes up the BL bundle's files: container, body hash, certificate, RSA-PSS signature check, which key names which, entropy, strings. `--plot` draws the entropy chart | python 3, matplotlib only for `--plot` |
| `pin_base.py` | finds the load address of a raw ARM64 image: votes on pointer-minus-string offsets, then checks the ADRP page phase | python 3, numpy |
| `a64_refs.py` | finds the code in a raw ARM64 image that points at an address or a string, and the function it sits in | python 3 |
| `dt_root.py` | prints the root `model` and `compatible` of each device tree in a `.dtb` or an Android `dt_table` (like `dtbo.img`), with node counts | python 3 |
