# Tab A8 teardown

**in progress.** the first pass is in - the things you can read straight off the stock firmware without a disassembler. sections still marked *not read yet* are just the questions, the same kind the [A10e teardown](https://github.com/CassieFox23/a10e-firmware/blob/master/A10e-teardown.md) answered for the phone.

everything here is static - files unpacked and read on a PC. nothing was run and nothing touched the tablet.

## the device

| | |
|---|---|
| model | SM-X200, device `gta8wifi`, product `gta8wifixx` |
| build read | `X200XXS6DYG6`, CSC `X200XAR6DYG6` (the XAR region) |
| Android | system is 14 (sdk 34), vendor is 11 (sdk 30), first API level 30 |
| security patch | 2025-08-01 on both |
| build type | `user`, `release-keys` |
| chip | Unisoc UMS512 - `ro.board.platform=ums512`, `ro.soc.model=T618`, `ro.soc.manufacturer=Spreadtrum` |

the model, versions and chip come from `build.prop` in the vendor and system partitions:

```
debugfs -R 'cat /build.prop' vendor.img
debugfs -R 'cat /system/build.prop' system.img
```

the device tree says the same. the `dtb` in `boot.img` has root model `Unisoc UMS512 SoC`, compatible `sprd,ums512` (900 nodes, 234 distinct `compatible` strings). `dtbo.img` carries five board overlays: `sprd,ums512-1h10`, `-1h10-go`, `-25c10`, `-2h10` and a second `-25c10`. the vendor's `ro.product.board=ums512_25c10` matches the 25c10 ones - which of the two the tablet picks isn't read.

```
python3 tools/dt_root.py boot/unpacked/dtb dtbo.img
```

### the bundles

the firmware comes as four `.tar.md5` bundles. each one's md5 line matches its contents (`tools/md5_check.py`) - that shows they're intact, not who made them.

| bundle | what's in it |
|---|---|
| BL | `u-boot-spl-16k-sign.bin`, `teecfg-sign.bin`, `sml-sign.bin`, `tos-sign.bin`, `lk-sign.bin`, `sharkl5pro_cm4.bin`, `grd_fw.img` |
| AP | `super.img`, `boot.img`, `dtbo.img`, `socko.img`, `recovery.img`, `gnssmodem.bin`, `EXEC_KERNEL_IMAGE.bin`, `userdata.img`, `AGCP_DSP.bin`, `vbmeta.img`, `vbmeta_system.img`, `meta-data/fota.zip` |
| CSC | `GTA8WIFI_EUR_OPEN.pit`, `cache.img`, `omr.img`, `optics.img`, `prism.img`, `meta-data/fota.zip` |
| HOME_CSC | `cache.img`, `prism.img`, `optics.img`, `meta-data/download-list.txt` |

```
python3 tools/md5_check.py *.tar.md5
tar -tvf BL_*.tar.md5        # same for AP, CSC, HOME_CSC
```

### the partition layout

the PIT has 58 entries, all on the eMMC, project name `COM_TAR2`, CPU/bootloader tag `SPRD8735`. the full table is in [`docs/partition-map.md`](docs/partition-map.md).

the PIT ties each BL file to a partition, which is the first real hint of what the bootloader pieces are:

| partition | file | size |
|---|---|---|
| `splloader` | `u-boot-spl-16k-sign.bin` | 0.5 MiB |
| `trustos` (+ `trustos_bak`) | `tos-sign.bin` | 6 MiB |
| `sml` (+ `sml_bak`) | `sml-sign.bin` | 1 MiB |
| `pm_sys` | `sharkl5pro_cm4.bin` | 2 MiB |
| `teecfg` (+ `teecfg_bak`) | `teecfg-sign.bin` | 1 MiB |
| `uboot` (+ `uboot_bak`) | `lk-sign.bin` | 5 MiB |
| `grd_fw` | `grd_fw.img` | 1 MiB |

those are names, not a read of the files. what each one does is still open.

the PIT also has `steady`, `persistent`, `param`, `vendor_efs` and `sec_efs` partitions, and a `vbmeta_vendor` one that no bundle ships an image for.

`super` is 6,740,246,528 bytes and holds four logical partitions in one group, `group_unisoc`: `system`, `system_ext`, `vendor`, `product`. there are no `_a` / `_b` copies.

```
simg2img super.img super.raw
lpdump super.raw
lpunpack -p vendor -p system super.raw .    # gives the vendor.img and system.img read below
```

## the boot chain

*not read yet.*

- what the bootloader files are on this chip and how they're packed
- who verifies whom, stage by stage
- where the OEM-unlock state is stored and read

one thing the firmware does say: the vendor's `default.prop` has `ro.oem_unlock_supported=1`. the A10e had that same line and still wouldn't unlock, so on its own it settles nothing.

what settles it is the tablet: it does unlock. the OEM unlocking switch is there, a long press in Download Mode does the unlock and the wipe, and `ro.boot.flash.locked` reads `0` afterwards. the steps are in the [how-to](docs/lineageos-howto.md). before the unlock, the Download Mode screen read `OEM LOCK` on and `KG STATE` completed.

## verified boot

what `vbmeta.img` says, read with `avbtool info_image --image vbmeta.img`:

- signed `SHA256_RSA4096`, public key sha1 `3ddc850a07d1098ad2613023f0c226488c357af9`
- flags `0`, rollback index `0`
- eight **chained** partitions, all naming that same key: `dtbo`, `boot`, `recovery`, `pm_sys`, `l_agdsp`, `prism`, `optics`, `socko`. a chained partition carries its own vbmeta footer - `boot.img` was the one checked, and `avbtool info_image --image boot.img` shows a footer with a sha256 hash descriptor for `boot`, signed by that key
- three **hashtree** partitions, checked block by block with dm-verity (sha256): `system`, `vendor`, `product`
- version props: boot and vendor `11`, system `14`, all patch `2025-08-01`

`vbmeta_system.img` is signed with the same key and carries the same three hashtrees again (`system`, `vendor`, `product`). the main vbmeta has no chain entry pointing at it.

that key isn't the A10e's (`e553992a79ab561a4805371cce123d1ee73db21b`).

one thing seen on the real tablets, from the flash logs in the [how-to](docs/lineageos-howto.md): with the bootloader unlocked, a `system` image that isn't Samsung's booted, and no command in the logs ever wrote to `vbmeta` or turned verification off. after the unlock the tablet reported `ro.boot.verifiedbootstate` as `orange`. so once it's unlocked, the hashtree for `system` in vbmeta didn't stop a different system from starting. that's what happened, not a read of the code that decides it - and the `vbmeta` partition wasn't read back off the tablet to prove it's still the stock one.

*not read yet:*

- where the bootloader keeps the key it trusts
- what the bootloader does with an image signed by another key while **locked**
- the code path behind the unlocked behaviour above

## why a GSI fits

this is the wall the A10e hit second, and the tablet doesn't have it.

the rule, from Android's [VINTF match rules](https://source.android.com/docs/core/architecture/vintf/match-rules): a system image is paired with the vendor code using the framework matrix whose level equals the vendor's `target-level`.

| | A10e | Tab A8 |
|---|---|---|
| vendor `target-level` | 3 | **5** |
| vendor wants VNDK | 28 | **30** |
| kernel | 4.4.111 | **4.14.199** |

the A10e's numbers are from its teardown. the tablet's come from the vendor partition:

```
debugfs -R 'cat /etc/vintf/manifest.xml' vendor.img              # <manifest ... target-level="5">, <kernel target-level="5"/>
debugfs -R 'cat /etc/vintf/compatibility_matrix.xml' vendor.img  # <vendor-ndk><version>30
debugfs -R 'cat /build.prop' vendor.img                          # ro.vndk.version=30
```

and the GSI was checked the same way - `LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img`, Android 15 (sdk 35):

- `/system/etc/vintf/` has framework matrices for levels 5, 6, 7, 8 and 202404 - so there **is** a level 5 one
- that level 5 matrix takes a 4.14 kernel from `4.14.180` up, and the tablet's is `4.14.199`
- `/system/system_ext/apex/` has `com.android.vndk.v30.apex`, the VNDK the vendor asks for

```
debugfs -R 'ls -l /system/etc/vintf' GSI.img
debugfs -R 'cat /system/etc/vintf/compatibility_matrix.5.xml' GSI.img | grep -o '<kernel version="[^"]*" level="5">' | sort | uniq -c
debugfs -R 'ls -l /system/system_ext/apex' GSI.img
```

so all three line up. this is a read of the files, not a run of Android's own `checkvintf` tool, and the per-HAL rows inside the matrix weren't compared one by one.

Samsung's own stock system (Android 14) ships matrices for levels 4 to 8, so it leans on the same level 5 match - an Android 11 vendor under a newer system is how this tablet ships.

## the secure world

*not read yet.*

- which TEE this chip runs and what talks to it
- what the SELinux policy lets a normal app reach

## the kernel

`boot.img` is a header v2 image: os version `11.0.0`, patch level `2025-08`, 2048-byte pages, cmdline `console=ttyS1,115200n8`. the kernel inside is a raw ARM64 `Image` and says:

```
Linux version 4.14.199-29056031-abX200XXS6DYG6 ... clang version 11.0.1 ... #2 SMP PREEMPT Mon Jul 28 15:32:23 KST 2025
```

```
unpack_bootimg --boot_img boot.img --out boot/unpacked
strings -n 8 boot/unpacked/kernel | grep -m1 '^Linux version'
```

Samsung's published source for this build is the same `4.14.199` (its `Makefile`: `VERSION = 4`, `PATCHLEVEL = 14`, `SUBLEVEL = 199`) and has a `gta8wifi_eur_open_defconfig`. the `-29056031-abX200XXS6DYG6` part of the version isn't in that defconfig (`CONFIG_LOCALVERSION=""`). where it comes from isn't traced.

*not read yet:* whether that source builds into this exact kernel.

## what didn't work, and mistakes

kept on purpose, same as the A10e one.

- **the md5 check that failed for the wrong reason.** the first try at checking the bundles cut the md5 line off at the last newline before it, and the BL and AP bundles came out as mismatches. the last bytes show why (`tail -c 176 <bundle> | xxd`): in the CSC bundle the hash follows a text line ending in a newline (`original_tar_file_size:67543040`), so that cut works. in the BL bundle zero bytes run right up to the hash with no newline, so the cut lands somewhere earlier. cutting at the hash itself fixed it, and all four match. the AP bundle's tail wasn't looked at, it just passes the same fix. `tools/md5_check.py` does it the right way.
