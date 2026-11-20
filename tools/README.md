# tools

small python scripts, standard library only. each takes file paths as arguments, so keep the firmware wherever you like.

| script | what it does | needs |
|---|---|---|
| `md5_check.py` | checks a `.tar.md5` bundle against the md5 line at its end | python 3 |
| `pit_table.py` | turns `samloader print-pit -f <file.pit>` output into a markdown table | python 3, [`samloader`](https://github.com/topjohnwu/samloader-rs) for the input |
| `dt_root.py` | prints the root `model` and `compatible` of each device tree in a `.dtb` or an Android `dt_table` (like `dtbo.img`), with node counts | python 3 |
