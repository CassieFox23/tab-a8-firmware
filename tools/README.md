# tools

small python scripts, standard library only apart from the chart one. each takes file paths as arguments, so keep the firmware wherever you like.

| script | what it does | needs |
|---|---|---|
| `md5_check.py` | checks a `.tar.md5` bundle against the md5 line at its end | python 3 |
| `pit_table.py` | turns `samloader print-pit -f <file.pit>` output into a markdown table | python 3, [`samloader`](https://github.com/topjohnwu/samloader-rs) for the input |
| `partition_chart.py` | draws every partition in a PIT as a bar chart, coloured by which bundle ships an image for it | python 3, matplotlib, `samloader` for the input |
| `treble_fit_chart.py` | draws each device's vendor Treble level against the levels its GSI ships; the numbers are written in the script | python 3, matplotlib |
| `dt_root.py` | prints the root `model` and `compatible` of each device tree in a `.dtb` or an Android `dt_table` (like `dtbo.img`), with node counts | python 3 |
