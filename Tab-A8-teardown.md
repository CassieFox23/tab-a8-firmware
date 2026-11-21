# Tab A8 teardown

The read is in: the things you can read straight off the stock firmware without a disassembler, then the bootloader's first two stages and the secure world's kernel with one. What's still open is listed at the end of each section as *not read*. It's the same kind of question the [A10e teardown](https://github.com/CassieFox23/a10e-firmware/blob/master/A10e-teardown.md) answered for the phone.

The read is static: files unpacked and read on a PC, with none of the firmware's code run. Where something was seen on the real tablets it says so, and it comes from the flash logs behind the [how-to](docs/lineageos-howto.md).

If a word stops you (PIT, DHTB, `smc`, TEE), it's probably in [words used here](#words-used-here).

## The device

| | |
|---|---|
| Model | SM-X200, device `gta8wifi`, product `gta8wifixx` |
| Build read | `X200XXS6DYG6`, CSC `X200XAR6DYG6` (the XAR region) |
| Android | System is 14 (sdk 34), vendor is 11 (sdk 30), first API level 30 |
| Security patch | 2025-08-01 on both |
| Build type | `user`, `release-keys` |
| Chip | Unisoc UMS512: `ro.board.platform=ums512`, `ro.soc.model=T618`, `ro.soc.manufacturer=Spreadtrum` |

The model, versions and chip come from `build.prop` in the vendor and system partitions:

```
debugfs -R 'cat /build.prop' vendor.img
debugfs -R 'cat /system/build.prop' system.img
```

The device tree says the same. The `dtb` in `boot.img` has root model `Unisoc UMS512 SoC`, compatible `sprd,ums512` (900 nodes, 234 distinct `compatible` strings). `dtbo.img` carries five board overlays: `sprd,ums512-1h10`, `-1h10-go`, `-25c10`, `-2h10` and a second `-25c10`. The vendor's `ro.product.board=ums512_25c10` matches the 25c10 ones. Which of the two the tablet picks isn't read.

```
python3 tools/dt_root.py boot/unpacked/dtb dtbo.img
```

### The bundles

The firmware comes as four `.tar.md5` bundles. Each one's md5 line matches its contents (`tools/md5_check.py`). That shows they're intact, not who made them.

| Bundle | What's in it |
|---|---|
| BL | `u-boot-spl-16k-sign.bin`, `teecfg-sign.bin`, `sml-sign.bin`, `tos-sign.bin`, `lk-sign.bin`, `sharkl5pro_cm4.bin`, `grd_fw.img` |
| AP | `super.img`, `boot.img`, `dtbo.img`, `socko.img`, `recovery.img`, `gnssmodem.bin`, `EXEC_KERNEL_IMAGE.bin`, `userdata.img`, `AGCP_DSP.bin`, `vbmeta.img`, `vbmeta_system.img`, `meta-data/fota.zip` |
| CSC | `GTA8WIFI_EUR_OPEN.pit`, `cache.img`, `omr.img`, `optics.img`, `prism.img`, `meta-data/fota.zip` |
| HOME_CSC | `cache.img`, `prism.img`, `optics.img`, `meta-data/download-list.txt` |

```
python3 tools/md5_check.py *.tar.md5
tar -tvf BL_*.tar.md5        # same for AP, CSC, HOME_CSC
```

### The partition layout

![The partitions in on-disk order on a log scale (57 of the 58 are drawn: `userdata` has no size in the PIT), coloured by which firmware bundle ships an image for each](figures/partition-map.png)

The PIT (Samsung's partition table file, shipped in the CSC bundle) has 58 entries, all on the eMMC, project name `COM_TAR2`, CPU/bootloader tag `SPRD8735`. The full table is in [`docs/partition-map.md`](docs/partition-map.md).

The PIT ties each BL file to a partition, which is the first real hint of what the bootloader pieces are:

| Partition | File | Size |
|---|---|---|
| `splloader` | `u-boot-spl-16k-sign.bin` | 0.5 MiB |
| `trustos` (+ `trustos_bak`) | `tos-sign.bin` | 6 MiB |
| `sml` (+ `sml_bak`) | `sml-sign.bin` | 1 MiB |
| `pm_sys` | `sharkl5pro_cm4.bin` | 2 MiB |
| `teecfg` (+ `teecfg_bak`) | `teecfg-sign.bin` | 1 MiB |
| `uboot` (+ `uboot_bak`) | `lk-sign.bin` | 5 MiB |
| `grd_fw` | `grd_fw.img` | 1 MiB |

Those are names, not a read of the files. What each one does is in [the boot chain](#the-boot-chain) and [the secure world](#the-secure-world).

The PIT also has `steady`, `persistent`, `param`, `vendor_efs` and `sec_efs` partitions, and a `vbmeta_vendor` one that no bundle ships an image for.

`super` is 6,740,246,528 bytes and holds four logical partitions in one group, `group_unisoc`: `system`, `system_ext`, `vendor`, `product`. There are no `_a` / `_b` copies.

```
simg2img super.img super.raw
lpdump super.raw
lpunpack -p vendor -p system super.raw .    # gives the vendor.img and system.img read below
```

## The boot chain

### The plain version

No addresses, just the story. Everything here is backed by a section further down.

- **Starting the tablet is a relay.** The pieces of startup code that were read each check what they load before handing over. The first small loader carries the fingerprint of the key the next four files must be signed with, and the main bootloader carries the fingerprint of the key for the Android images. What checks the very first piece isn't in these files.
- **"Unlocked" isn't a switch the bootloader just believes.** It's a small record in storage, and the bootloader asks the secure world, a separate little system the normal one can't see into, whether that record is genuine.
- **The bootloader hands the boot image to the secure world to check**, and the answer becomes a colour: green for Samsung's key, yellow for someone else's key, orange for unlocked, red for a failed check. (The key names are the bootloader's own log lines; the colours are read from the code.)
- **Unlocked, it doesn't even ask.** The check on the boot image is skipped and the colour is orange. The real tablets then booted a system that isn't Samsung's, with the boot image still stock. The code that lets a different system through wasn't read.
- **Locked and failed, it goes red**, puts a message on the screen and drops into Download Mode, where it waits to be flashed. It doesn't carry on booting.
- **The bootloader also runs a check of its own** on the same signatures. In the code that was read, that second answer is logged and feeds the kernel's command line, but it isn't what sets the colour, as far as the decompiler showed that function.

![What happens when you press power: the first loader loads and checks the next stages against a key hash it carries, tries the backup copies before giving up, and jumps to sml; how control gets from sml and Trusty to lk wasn't read; lk asks the secure world whether the unlock record is genuine; unlocked skips the image check and goes orange, locked sends the boot image to the secure world and gets green, yellow or red; lk's own libavb check always runs but only feeds the command line; green and yellow boot, orange waits and then boots, red drops to Download Mode and, in the code as read, stays there](figures/power-on.png)

The same story as one flow. Grey boxes are things that weren't read. The interactive page is in `.archify/workflow-tab-a8-power-on-20261120-172500/`.

### Words used here

Short meanings, as this page uses them.

| Word | What it means here |
|---|---|
| BL, AP, CSC | The bundles a Samsung firmware comes in: the bootloader files, the Android images, and the region pack |
| PIT | Samsung's partition table file: one entry per partition, with its name and size |
| Download Mode, Odin | Samsung's flashing mode, and the protocol a PC uses to talk to it |
| SPL | The first small loader in the bundle (`u-boot-spl-16k-sign.bin`). It loads and checks the next stages |
| `lk` | "Little kernel", the small open-source kernel the main bootloader is built on. Trusty is built on it too, so both files greet with `welcome to lk` |
| DHTB | The four letters each signed bootloader file starts with, used here as the name of that container. The files don't say what they stand for |
| Secure world, TEE | A second small system on the same chip that the normal one can't see into. TEE is "trusted execution environment". This tablet's is Trusty |
| TOS | The "trusted OS" file, `tos-sign.bin`: Trusty's kernel and its apps |
| `sml`, BL31 | Going by its strings, `sml-sign.bin` holds BL31, the piece of ARM Trusted Firmware that normally sits between the normal world and the secure one and passes calls across. What it does on this tablet wasn't read |
| `smc` | "Secure monitor call", the ARM instruction normal-world code uses to call into the secure world |
| AVB, vbmeta, libavb | Android Verified Boot. `vbmeta` is its signed table of hashes and keys, and libavb is Google's code that checks it |
| Chained partition | A partition that carries its own signed vbmeta footer. The main vbmeta only names the key that footer must be signed with |
| Hashtree, dm-verity | A tree of hashes over a whole partition. The kernel's dm-verity checks each block against it as the block is read |
| Knox Guard (KG) | Samsung's remote lock for a device. `lk` keeps a KG state and looks at it before it allows an unlock or a flash |
| RPMB | A small area of the eMMC that only takes writes authenticated with a key, used for secure storage |
| Treble, VINTF | Android's split between the system and the vendor's code, and the files in which each side declares what it offers and needs |
| GSI | Generic system image: one Android system build made to run on many Treble devices |
| HAL | A vendor service that sits between Android and a piece of hardware |
| ADRP | An ARM64 instruction that loads the address of a memory page. Code uses it to point at strings and data, which is how the scripts find references |

### The sizing pass

The BL bundle has seven files. First comes a sizing pass over all of them: headers, hashes, signatures, entropy and strings, with nothing disassembled. It settled more than expected, because the files check each other with plain hashes. The read of the code in `lk` and the SPL starts at [pinning the load addresses](#pinning-the-load-addresses).

![The signing chain: key A signs the SPL, whose certificate names key B; key B signs sml, tos, teecfg and lk; lk's certificate names the AVB key, which signs vbmeta.img](figures/signing-chain.png)

### The seven files

| File | Goes to partition | Size | Container | What it is, by its strings |
|---|---|---|---|---|
| `u-boot-spl-16k-sign.bin` | `splloader` | 61 KiB | DHTB, signed | The first stage in the bundle. Almost no readable text |
| `sml-sign.bin` | `sml` | 72 KiB | DHTB, signed | ARM Trusted Firmware's BL31, with hooks for Trusty (`NOTICE:  BL31: %s`, `trusty_fast`) |
| `tos-sign.bin` | `trustos` | 3,388 KiB | DHTB, signed | A Trusty image (`lk/trusty/...`, `com.android.trusty.keymaster.secure`) |
| `teecfg-sign.bin` | `teecfg` | 122 KiB | DHTB, signed | A config table, starts `TEE_CONFIG_HEADER`, mostly zeros |
| `lk-sign.bin` | `uboot` | 4,301 KiB | DHTB, signed | The bootloader proper: little kernel (`welcome to lk`), with `fastboot_handler`, `odin_handler`, the `OEM LOCK` and `KG STATUS` screen text and the `androidboot.verifiedbootstate=` strings |
| `sharkl5pro_cm4.bin` | `pm_sys` | 2,048 KiB (579 KiB used) | AVB footer | Firmware for a Cortex-M4 side processor (`SPRD-AP_FIRMWARE`, `SHUB:`) |
| `grd_fw.img` | `grd_fw` | 221 KiB | Its own 256-byte header | Two blocks that look random end to end. Unknown |

The "what it is" column is names and strings only. A string in a file isn't proof the code behind it runs.

The numbers come from one script:

```
python3 tools/bl_sizing.py --vbmeta vbmeta.img --plot figures/bootloader-files.png \
    u-boot-spl-16k-sign.bin sml-sign.bin tos-sign.bin teecfg-sign.bin lk-sign.bin sharkl5pro_cm4.bin grd_fw.img
```

| File | Body bytes | Entropy | Strings (8+) | AArch64 `ret` | Hashes | Signature |
|---|---|---|---|---|---|---|
| `u-boot-spl-16k-sign.bin` | 60704 | 6.05 | 66 | 202 | ok | ok |
| `sml-sign.bin` | 71920 | 4.88 | 121 | 339 | ok | ok |
| `tos-sign.bin` | 3467296 | 6.29 | 14028 | 1934 | ok | ok |
| `teecfg-sign.bin` | 122880 | 0.72 | 207 | 0 | ok | ok |
| `lk-sign.bin` | 4402800 | 7.20 | 8203 | 7913 | ok | ok |
| `sharkl5pro_cm4.bin` | 592784 | 7.19 | 1686 | 0 | - | - |
| `grd_fw.img` | 226560 | 7.99 | 57 | 0 | - | - |

"AArch64 `ret`" counts the 4-byte `ret` instruction at aligned offsets, a cheap way to tell ARM64 code from everything else.

![Entropy along each of the seven files: lk and tos are code then data, the Cortex-M4 image is 579 KiB of code and then padding, grd_fw.img sits at the maximum the whole way, teecfg is almost empty](figures/bootloader-files.png)

### Nothing readable is encrypted, except maybe one

The five signed files aren't encrypted. Each body hashes to the SHA-256 stored in its own header, and four of the five are full of ARM64 code and plain strings. So the A10e's problem, an encrypted stage at the front of `sboot`, doesn't show up in these.

`grd_fw.img` is the odd one. It reads 7.99 bits per byte the whole way through, which is what compressed or encrypted data looks like, and it has no strings. What it's for isn't known.

### The DHTB container

The five `-sign.bin` files share a layout:

| Offset | What |
|---|---|
| `0x000` | `DHTB`, then a version word (`1`) |
| `0x008` | SHA-256 of the body |
| `0x030` | Body size |
| `0x200` | The body |
| After the body | A `SIMGHDR` block that gives the certificate's offset and size |
| After that | The certificate, 564 or 596 bytes |
| Last 512 bytes | A `SignerVer02` block: the build (`X200XXS6DYG6`), a timestamp, the key name `SM-X200_EUR_XX_UKEY0`, and some binary that wasn't parsed |

The certificate:

| Bytes | What |
|---|---|
| 4 | Type, `0` or `1` |
| 4 + 4 + 256 | An RSA-2048 public key: bit count, exponent `65537`, modulus |
| 32 | SHA-256 of the body, again |
| 32, type `1` only | SHA-256 of the **next stage's key** |
| 8 | Two words, `1` and `0x3f` in all five |
| 256 | The signature |

The signature is RSASSA-PSS (SHA-256, 32-byte salt) over the bytes from the body hash up to the signature, and all five verify against the key sitting in the same certificate. A certificate that checks out under its own key only shows the file is consistent. The trust has to come from the stage before it. That's what the type `1` field is for.

### The chain, from the hashes

- The SPL is signed with **key A** (`29f0d80a5959...`). Its certificate is type `1` and carries `3ca58836d04d...`.
- `sml`, `tos`, `teecfg` and `lk` are all signed with **key B**, and SHA-256 over key B (bit count + exponent + modulus) is exactly `3ca58836d04d...`. So the SPL's certificate names the key the next four files must be signed with.
- `lk`'s certificate is also type `1`, and the hash it carries is `a406eeb5ebc0...`, the SHA-256 of the AVB public key in `vbmeta.img`. So the **signed bootloader names the one vbmeta key it goes with**.
- That AVB key then signs `vbmeta.img` and the chained partitions, as in the next section. The Cortex-M4 image is one of them: it has no DHTB wrapper, just an AVB footer for `pm_sys` signed by the same key.

So an early question, where does the bootloader keep the key it trusts, has a first answer without reading any code: the vbmeta key's hash rides in `lk`'s own signed certificate.

The full key ids are SHA-256 values: key A `29f0d80a5959c8513e45c56596d3ff31d21713352706e0e1844fc8d2a17dfc29`, key B `3ca58836d04d90a9acff83ae763a085ca6c50d2444784042aa731e7b0eeaeffd`, AVB key blob `a406eeb5ebc07a5cafabdb1bf2f4ad74275a533f67cc68e680345d22ddc66cef`.

*Not read yet:*

- What trusts **key A**. Nothing in these files names it, so it's below the SPL, most likely in the chip, but that's a guess until something shows it
- The hashing and signature routines themselves, in any stage

### Inside lk

`lk-sign.bin` is where the next read goes. Its 4.2 MiB body splits three ways:

- ARM64 code up to about 1,314 KiB (the last `ret` is at body offset `0x148954`)
- Tables and strings after that: binwalk finds CRC32 tables, an AES S-box and SHA-256 constants around 1.4 to 1.7 MiB
- JPEG pictures from 1,828 KiB on (74 JPEG start markers), which is why the file's entropy reads so high. What they show wasn't looked at

The strings say everything the A10e read went looking for is in here: `avb` (58 lines), `vbmeta` (70), `unlock` (37), `rpmb` (70), `efuse` (30), `odin` (59), `fastboot` (38), plus `Custom Binary Blocked By OEM Lock` and `[KG] failed to malloc kg state block`. So this bootloader has Knox Guard text in it too. Whether a path behind it runs on this tablet is for the read.

Its load address isn't in the DHTB header, so that had to be worked out before any reference could be trusted. It's the same job that went wrong first time on the A10e.

### Who checks whom

![The boot chain in three lanes: on the eMMC (the stage files, the unlock record in miscdata at 0x2000, the OEM unlocking byte at the end of persistent, vbmeta and the AVB footers), the bootloader stages (whatever trusts key A, the SPL at 0x5700, lk at 0x9f000000, the unlocked flag, the boot state) and the secure world (command 0x33 judges the unlock record, command 0x20 checks vbmeta)](figures/boot-chain.png)

That's the read below in one picture. Green is bootloader code that was read, red is the secure world, read in [its own section](#the-secure-world).

### Pinning the load addresses

Both files are raw code with no load address in the header, so that came first. `tools/pin_base.py` finds it two ways that don't depend on each other:

| File | Absolute pointers that land on a string | ADRP page phase | Load address |
|---|---|---|---|
| `lk` body | 1856 at `0x9f000000`, runner-up 997 | `0x000` (4812 hits, next best 1719) | **`0x9f000000`** |
| SPL body | 11 at `0x5700`, runner-up 6 | `0x700` (29 hits, next best 11) | **`0x5700`** |

The SPL's is thin on its own: it only has 83 strings by this script's count (6 characters or more, ending in a zero byte; the sizing table's 66 counts 8 or more). But the two methods agree, and the SPL's own code settles `lk`'s: it loads the `uboot` partition to `0x9f000000` with the 512-byte header just below at `0x9efffe00`.

The SPL's phase is `0x700`, not `0`. That's the same trap as the A10e, where assuming phase 0 quietly pointed every reference at the wrong string.

```
python3 tools/pin_base.py lk.body
python3 tools/pin_base.py spl.body
python3 tools/a64_refs.py lk.body 0x9f000000 "is_oem_unlock_possible" "flashed due to KG locked."
```

### Where things sit in memory

![Where the boot stages and buffers sit in memory: the download buffer from 0x82000000 for 256 MiB with the l_agdsp image inside its range at 0x89000000, the three secure-world pieces together at 0x94000000 to 0x94060000, a staging buffer at 0x9a000000, lk at 0x9f000000, the boot or recovery image at 0xb0000000 and a vbmeta read buffer at 0xd0000000; the SPL is off the scale at 0x5700](figures/memory-map.png)

Every address the read turned up, on one line. A bar is a size that was read, a dot is an address with no size. The SPL isn't on the scale: it runs at `0x5700`, far below the rest. The numbers are written into the script, each from a section on this page. Two aren't quoted anywhere else: `0x89000000` (the `l_agdsp` image) and `0xd0000000` (the vbmeta read buffer) are constants in `0x9f0349a0`, Samsung's official-or-custom tally. Running the script redraws `figures/memory-map.png` in place:

```
python3 tools/memory_map_chart.py
```

### What the SPL does

From here to the end of the boot chain, the read is Ghidra's decompiler output (through [REA](https://github.com/morluto/rea)) for a handful of functions, named by address. It's a read of the paths that answer the open questions, not of the whole bootloader.

One function, at `0xf898`, does the loading:

1. Loads `teecfg` to `0x94040000`
2. Reads `tee_sml_addr` and `tee_tos_addr` out of it (the variables start at `0x94000000` and `0x94060000`)
3. Loads `sml`, `trustos` and `uboot`, the last one to `0x9f000000`
4. Checks each with the function at `0x10c24`. If a check fails it loads the `_bak` partition and checks that. If that fails too it sits in an endless loop
5. Jumps to `sml`, handing it the `trustos` and `teecfg` addresses. In one mode it skips the TEE files and jumps straight to `lk`. What picks that mode wasn't read

The check is the chain from the hashes, in code:

- `0x10c24` is called as `(0x5500, header of the next image)`. `0x5500` is the SPL's **own** header, 512 bytes below where it runs. It pulls 32 bytes out of its own image (`0x10bd8`)
- `0x10b78` then takes the next image's body size from header offset `0x30`, hashes the body (`0x107b4`), and passes the hash, those 32 bytes and the next image's certificate to `0x10940`

So the SPL carries the expected key hash in its own signed image and checks the next stage against it. That's what the certificates said, now seen in the code that uses them.

*Not read:* The insides of `0x10bd8`, `0x107b4` and `0x10940`. The SPL body has no SHA-256 constants in it, so where the hashing actually runs isn't known. And the SPL is the thing being checked at the very start, not the checker, so it doesn't say what trusts key A.

### What lk does about locking

![The unlock step by step in four lanes: by hand (OEM unlocking on, both volume keys, long-press Volume Up, the tablet wipes itself), the bootloader (is an unlock possible, reading the record on every boot after), the secure world (Trusty recomputes the expected 64 bytes) and storage (the last byte of persistent, the record at miscdata + 0x2000); what runs the unlock between the long press and the wipe, what writes the switch byte and the record, the extra Knox Guard check and the key derivation are marked not read](figures/unlock-steps.png)

The interactive page is in `.archify/workflow-tab-a8-unlock-20261120-173000/`.

**The unlock state is a record in `miscdata`, and the secure world judges it.**

- One global, at `0x9f4388a8`, holds "unlocked". Exactly one function writes it: `0x9f121324`
- That function reads 512 bytes from the `miscdata` partition at offset `0x2000` and hands the first 64 to `0x9f0108e8`
- `0x9f0108e8` copies them into a page-aligned buffer and sends **command `0x33`** to the secure world. It counts as unlocked only if the call returns `0` and a byte in the reply is set
- So `lk` doesn't decide by itself whether the tablet is unlocked. It asks the secure world and keeps the answer in that global. `0x9f121324` isn't run once and remembered for good: it's called from 19 places in `lk` (a scan for `bl` to it), among them `0x9f03536c`, `0x9f0352cc` and `0x9f124e64`, which were read, plus the Download Mode code and others that weren't. The verified-boot code in `0x9f120b00` and `0x9f121540` reads the stored flag instead. On the boot path the flag is set just before: `0x9f010c48` calls a small function, `0x9f01082c`, right ahead of `0x9f120b00`, and that function contains one of the 19 calls (at `0x9f010838`). `0x9f01082c` itself wasn't decompiled

The call itself: 27 small wrappers each load a command number (`0x1` to `0x50`) and call a dispatcher at `0x9f14325c`, which calls `0x9f147000`, where the `smc` instruction is (`0x9f147018`). There's a second `smc` in `lk` at `0x9f143d40` (bytes confirmed); what reaches it wasn't read.

"The secure world" in this section means whatever answers that `smc`. The read of `lk` stops at the instruction. What sits on the other side belongs to [the secure world](#the-secure-world).

That global then drives the kernel command line: `0x9f007b2c` appends `androidboot.flash.locked=0` when it's `1`, and `=1` otherwise.

**The "OEM unlocking" switch is one byte.** `0x9f0351d0` reads the last 512 bytes of the `persistent` partition and returns whether the very last byte is non-zero. That's the switch in Developer options.

**Whether an unlock is allowed** is `0x9f03536c`, and it logs its answer as `is_oem_unlock_possible`:

1. Already unlocked: yes
2. The switch byte is zero: no
3. Otherwise it depends on Knox Guard (`0x9f0352cc`): **no** if the KG state is `PRENORMAL`, `ACTIVE`, `LOCKED` or `ERROR`, or if one more check (`0x9f038880`, not read) returns `0x20`

The KG state names come from a table at `0x9f1c0b10`:

| Value | State |
|---|---|
| 0 | `PRENORMAL` |
| 1 | `CHECKING` |
| 2 | `ACTIVE` |
| 3 | `LOCKED` |
| 4 | `COMPLETED` |
| 5 | `ERROR` |
| 6 | `BROKEN` |
| 7 | `ALLZERO` |

This fits what the real tablets did: their Download Mode screen showed the Knox Guard state as completed, and they unlocked. (The how-to records that line as `KG STATE`; the label in `lk`'s strings is `KG STATUS`.)

**Knox Guard also gates flashing.** In the flash handler at `0x9f017010`, the code just before the message `All binaries are not allowed to be flashed due to KG locked.` is: KG state equals `3` (`LOCKED`), and a second function (`0x9f037540`, a bitmask test of a flags global at `0x9f45b290`) returns `0`. This one is from decoding the branches, not from the decompiler. The same message is used a second time, at `0x9f01845c` in a function starting `0x9f0179a0`, which wasn't read.

**The Download Mode screen** is printed by `0x9f0364fc`: `ODIN MODE`, `PRODUCT NAME`, `CURRENT BINARY` (Samsung Official or Custom), `FRP LOCK`, `OEM LOCK`, `KG STATUS`, `UNISOC SECURE BOOT`, `WARRANTY VOID`, `RP SWREV`, `SECURE DOWNLOAD` and `GRDM STATUS`. Its `OEM LOCK` line comes from the same `miscdata` check and the same switch byte.

### What lk does about verified boot

The boot flow runs through `0x9f010c48` (it logs `SECUREBOOT_ENABLE`): it picks `boot` or `recovery`, calls `0x9f120b00` on that name, then `0x9f121540`, sets the root of trust, and later checks `pm_sys` under a flag. Those two calls are the two halves of verified boot: the secure-world check first, then `lk`'s own libavb.

**The boot-state decision: `0x9f120b00`.** Given a partition name, it:

1. Loads the partition (`boot`/`recovery` to `0xb0000000`; the `vbmeta_*` names at size `0x1000`) and fills a request struct at `*0x9f9ab090`
2. If the name is `boot` or `recovery` **and the tablet is unlocked** (`0x9f4388a8 == 1`), it logs `Device Status is unlock, skip %s image verify!` and **doesn't call the secure world at all**
3. Otherwise it sends the image to the secure world with **command `0x20`** (wrapper `0x9f142de4`, struct size `0x68`). If the wrapper's return doesn't match the code in the reply, it logs `tos return error!` and **sits in an endless loop**
4. Then it sets the boot-state global `0x9f435010` from the result: unlocked → `2`; result `0` → `0` (unless the state is already `3`); result `5` → `1`; anything else → `3`

So the state the tablet boots with is set by the **secure-world** check, and on an unlocked `boot`/`recovery` that check is skipped and the state is `2`. That's the orange the real tablets showed: a non-Samsung system booted and the state went orange.

The number becomes a colour in `0x9f007a38`, which switches on the state and adds one string to the kernel command line:

| State | String |
|---|---|
| `1` | `androidboot.verifiedbootstate=yellow` |
| `2` | `androidboot.verifiedbootstate=orange` |
| `3` | `androidboot.verifiedbootstate=red` |
| `0`, or anything else | `androidboot.verifiedbootstate=green` |

Green is the fallback, so a state number the code doesn't know would also report green. (`tools/a64_refs.py` reports this function as starting at `0x9f007a3c`; Ghidra has `0x9f007a38`. The same four-byte gap shows on three functions further down: `0x9f1281e0`, `0x9f11f9a0` and `0x9f01098c` in Ghidra are `0x9f1281e4`, `0x9f11f9a4` and `0x9f010990` in the script. For those four this page uses Ghidra's.)

There's a near-twin, `0x9f1206d0`, with the same shape (footer, load vbmeta, command `0x20`, set `0x9f435010`) but a slightly different mapping (its locked-`5` goes to `3`, not `1`). Nothing was found calling it (no `bl`/`b`, no `ADRP`+`ADD`, not stored as data), so it reads like a dead or alternate copy, and the live numbers above are `0x9f120b00`'s.

**`lk` also checks vbmeta itself, after that.** `0x9f121540` always runs. First, only when the tablet is **not** unlocked and the name isn't `recovery` (and only once: a flag at `0x9f9ac025` remembers), it calls `0x9f120b00("vbmeta_system")` and logs that `vbmeta_vendor`, `odmko` and `socko` are skipped. Then, locked or not, it calls `0x9f11f9a0`, `lk`'s own libavb:

- `0x9f11f9a0` → `0x9f124e64` (`avb check image name`) → `avb_slot_verify` (`0x9f129684`) → `load_and_verify_vbmeta` (`0x9f1281e0`) → `avb_vbmeta_image_verify` (`0x9f12a868`)
- `0x9f12a868` calls SHA-256 and SHA-512 routines and an RSA check at `0x9f126f18` (`Signature length does not match key length.`), so vbmeta's hash and signature are checked by `lk`'s own code
- Whether that key is one to trust is asked through a function pointer, slot `+0x30` of a table at `0x9f9ae060`. The table sits past the end of the file, filled in while `lk` runs, so what's behind the slot wasn't read
- `0x9f124e64` turns on "allow verification errors" when a flag at `0x9f9af000` is `0` and the unlock check (`0x9f121324`) says unlocked, logging `avb allow verification error in UNLOCK status while normal booting`
- But `0x9f11f9a0` only logs `avb_check_image`'s return and builds the kernel cmdline from it; in what Ghidra shows that return isn't acted on (it flags a terminal call at `0x9f11fac8`, so the tail may be cut). So `lk`'s libavb feeds the kernel command line, while the **boot-state gate is the secure-world `0x20` check above**. A scan for stores to the state global finds them in three functions only, all of them `0x20` callers (the scan matches one instruction shape, so a store written another way would be missed): `0x9f120b00`, `0x9f1208b0` and the uncalled `0x9f1206d0`

The libavb names are its own, from each function's log strings.

**Command `0x20` has four callers.** Two are on the boot path read here: `0x9f120b00`, and `0x9f1208b0`, which `0x9f010c48` calls on `pm_sys` (the Cortex-M4 image) under a flag. That one wasn't read through. `0x9f120b00` has a third call site besides the two above, at `0x9f00efe4`. It's in `0x9f00ef18`, a general image loader (`load %s with backup img %s` is one of its log lines): given a name, a size and a destination, it sends any image that isn't `pm_sys` and has no backup copy through `0x9f120b00`, then copies it from `0x9a000000` to where it belongs. Which images come through that loader wasn't read. The other two callers are `0x9f123d88` (`check vbmeta image.`, by its string only; `0x9f123c24` uses the same string) and the uncalled twin `0x9f1206d0`.

`0x9f010c48` itself is reached by 18 plain branches from one stretch of code (`0x9f011eb4` to `0x9f01254c`), which wasn't read.

```
python3 tools/a64_refs.py lk.body 0x9f000000 "SECUREBOOT_ENABLE" "Device Status is unlock, skip" \
    "avb check image name" "Signature length does not match key length." "check vbmeta image."
```

**What reads the boot state.** Besides the colour function above (`0x9f007a38`), three functions load `0x9f435010`:

- **`0x9f01098c` acts on it.** `0x9f010c48` calls it right after `0x9f121540`, and it's a switch on the state:

  | State | What it does |
  |---|---|
  | `0` | Logs `WARNNING: OEM KEY VERIFY SUCCESS!!!` and returns |
  | `1` | Logs `WARNNING: USER KEY VERIFY SUCCESS!!!` and returns |
  | `2` | Calls `0x9f057548`, then polls `0x9f002680` every 10 ticks for up to 10000, then `0x9f05741c`. The unlocked path, so most likely the warning the tablets show at startup. The three calls weren't read |
  | `3` | Prints `TO be implement Reason` to the screen, calls `0x9f0121a8` (which goes into **Download Mode**), and only if that comes back logs `WARNNING: Oem Key & User Key Verify Failed!!!`, waits 60 x 100 ticks and returns |
  | Other | Logs `WARNNING: VERIFY RESULT UNKNOWN!!!` |

  So going by its own log lines the numbers are `0` Samsung's key, `1` a user key, `2` unlocked, `3` failed, which matches the colours in the table above.

  **So a locked tablet that fails the check lands in Download Mode.** `0x9f0121a8` logs `enter [%s]` filled in with `fastboot_mode`, sets the mode name to `fastboot`, logs `enter odin_mode` and jumps to `0x9f018748`. That one logs `start Odin Mode...`, draws the download logo and the Download Mode screen (`0x9f0364fc`, the same one as above), brings USB up and then loops on the Odin handler with no way out of the loop. There's one check before the loop that would let it return: a setup call, `0x9f0164fc`. But that call can't fail: it sets the download buffer to `0x82000000`, 256 MiB long, logs it and returns `0`. So in the code as read, the tablet stays in Download Mode
- **`0x9f0349a0` is Samsung's own tally** (`check_secure_boot` in its log lines). It goes through `vbmeta` and then `boot`, `l_agdsp`, `uboot`, `trustos` and `super` (or just `recovery`), and marks each `SAMSUNG` or `CUSTOM`. It only looks at the boot state to skip some of the marking when the state is `3`. This is where the official-or-custom binary status comes from, not a gate
- **`0x9f112fe4` copies it out** (`[I] populate_rot_info_for_grdm`): the state, whether the tablet is locked, a hash taken from `lk`'s own header at `0x9efffe00`, and the OS version and patch levels, into one record. What `grdm` is wasn't read

An earlier pass of this page listed a fourth reader, `0x9f014508`. That was wrong: it reads offset `0x10` of the boot image header, which sits in the same memory page at `0x9f435aa0`.

```
python3 tools/a64_refs.py lk.body 0x9f000000 "WARNNING: OEM KEY" "WARNNING: USER KEY" "start Odin Mode"
```

The other two were found by scanning for loads of `0x9f435010` and then decompiled; their log strings are built in ways `a64_refs.py` doesn't follow.

*Not read:*

- What Trusty does with commands `0x20` and `0x33`. That's the secure world's side, [below](#the-secure-world)
- What sits behind `lk`'s "is this key trusted" slot (`0x9f9ae060` + `0x30`)
- Who writes the `miscdata` record when you unlock. What its 64 bytes have to be is worked out on the other side, in [what Trusty does with lk's two commands](#what-trusty-does-with-lks-two-commands)
- The second flash-gate helper `0x9f038880` (the first, `0x9f037540`, is a bitmask test of a flags global at `0x9f45b290`, not a secure-world call)
- The warranty bit

### Against the A10e's sboot

| | A10e `sboot` | Tab A8 |
|---|---|---|
| Shape | One 4 MB image with an encrypted stage at the front | Separate files per stage, none of the signed ones encrypted |
| Finding the load address | One address, and the page phase was the trap | Two addresses, same trap in the SPL (phase `0x700`) |
| Who checks the vbmeta key | The bootloader itself, calling libavb | Both, and the secure world's answer sets the boot state: `lk` hands the image to the secure world (command `0x20`) and the state comes from that; its own libavb runs too, checking the signature and building the cmdline |
| Who holds the unlock state | Read inside the bootloader | A record in `miscdata` that the secure world judges |
| Knox Guard | Gates flashing in Download Mode | Gates flashing, and gates unlocking too |
| Can it unlock | No, on that unit | Yes |

The A10e column is from its [teardown](https://github.com/CassieFox23/a10e-firmware/blob/master/A10e-teardown.md).

The big difference is where the decisions sit. On the A10e they're in the bootloader you can read. Here the bootloader asks the secure world about both: the unlock state, and the vbmeta check whose answer sets the boot state. `lk` runs its own libavb too, but that feeds the kernel cmdline. The orange/green/red gate comes from the secure-world check. What's behind the `smc` belongs to [the secure world](#the-secure-world).

One thing the firmware does say: the vendor's `default.prop` has `ro.oem_unlock_supported=1`. The A10e had that same line and still wouldn't unlock, so on its own it settles nothing.

What settles it is the tablet: it does unlock. The OEM unlocking switch is there, a long press in Download Mode does the unlock and the wipe, and `ro.boot.flash.locked` reads `0` afterwards. The steps are in the [how-to](docs/lineageos-howto.md). Before the unlock, the Download Mode screen read `OEM LOCK` on and the Knox Guard state as completed.

## Verified boot

![What vbmeta.img covers: one RSA-4096 key (sha1 3ddc850a...), flags 0, with eight chained partitions each named with the same key (dtbo, boot, recovery, pm_sys, l_agdsp, prism, optics, socko) and three dm-verity hashtree partitions inside super (system, vendor, product)](figures/vbmeta-covers.png)

What `vbmeta.img` says, read with `avbtool info_image --image vbmeta.img`:

- Signed `SHA256_RSA4096`, public key sha1 `3ddc850a07d1098ad2613023f0c226488c357af9`
- Flags `0`, rollback index `0`
- Eight **chained** partitions, all naming that same key: `dtbo`, `boot`, `recovery`, `pm_sys`, `l_agdsp`, `prism`, `optics`, `socko`. A chained partition carries its own vbmeta footer: `boot.img` was the one checked, and `avbtool info_image --image boot.img` shows a footer with a sha256 hash descriptor for `boot`, signed by that key
- Three **hashtree** partitions, checked block by block with dm-verity (sha256): `system`, `vendor`, `product`
- Version props: boot and vendor `11`, system `14`, all patch `2025-08-01`

`vbmeta_system.img` is signed with the same key and carries the same three hashtrees again (`system`, `vendor`, `product`). The main vbmeta has no chain entry pointing at it.

That key isn't the A10e's (`e553992a79ab561a4805371cce123d1ee73db21b`).

One thing seen on the real tablets, from the flash logs in the [how-to](docs/lineageos-howto.md): with the bootloader unlocked, a `system` image that isn't Samsung's booted, and no command in the logs ever wrote to `vbmeta` or turned verification off. After the unlock the tablet reported `ro.boot.verifiedbootstate` as `orange`. So once it's unlocked, the hashtree for `system` in vbmeta didn't stop a different system from starting. That's what happened, not a read of the code that decides it. And the `vbmeta` partition wasn't read back off the tablet to prove it's still the stock one.

The hash of this key is carried in the bootloader's own signed certificate. See [the chain, from the hashes](#the-chain-from-the-hashes).

The code behind that is in [what lk does about verified boot](#what-lk-does-about-verified-boot): when the tablet is unlocked, the secure-world check on the boot image is skipped and the boot state is set to orange without it.

And a failed check while **locked** ends in Download Mode. The same section has the read.

## Why a GSI fits

This is the second wall the A10e hit. The tablet doesn't have it.

![Treble levels side by side: the A10e's vendor declares level 3 and its LineageOS 21 GSI ships levels 4 to 8, so nothing matches; the Tab A8's vendor declares level 5 and its LineageOS 22.2 GSI ships 5, 6, 7, 8 and 202404, so level 5 matches](figures/treble-fit.png)

The rule, from Android's [VINTF match rules](https://source.android.com/docs/core/architecture/vintf/match-rules): a system image is paired with the vendor code using the framework matrix whose level equals the vendor's `target-level`.

| | A10e | Tab A8 |
|---|---|---|
| Vendor `target-level` | 3 | **5** |
| Vendor wants VNDK | 28 | **30** |
| Kernel | 4.4.111 | **4.14.199** |

The A10e's numbers are from its teardown. The tablet's come from the vendor partition:

```
debugfs -R 'cat /etc/vintf/manifest.xml' vendor.img              # <manifest ... target-level="5">, <kernel target-level="5"/>
debugfs -R 'cat /etc/vintf/compatibility_matrix.xml' vendor.img  # <vendor-ndk><version>30
debugfs -R 'cat /default.prop' vendor.img                        # ro.vndk.version=30
```

The GSI was checked the same way: `LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img`, Android 15 (sdk 35):

- `/system/etc/vintf/` has framework matrices for levels 5, 6, 7, 8 and 202404, so there **is** a level 5 one
- That level 5 matrix takes a 4.14 kernel from `4.14.180` up, and the tablet's is `4.14.199`
- `/system/system_ext/apex/` has `com.android.vndk.v30.apex`, the VNDK the vendor asks for

```
debugfs -R 'ls -l /system/etc/vintf' GSI.img
debugfs -R 'cat /system/etc/vintf/compatibility_matrix.5.xml' GSI.img | grep -o '<kernel version="[^"]*" level="5">' | sort | uniq -c
debugfs -R 'ls -l /system/system_ext/apex' GSI.img
```

So all three line up. This is a read of the files, not a run of Android's own `checkvintf` tool, and the per-HAL rows inside the matrix weren't compared one by one.

Samsung's own stock system (Android 14) ships matrices for levels 4 to 8, so it leans on the same level 5 match. An Android 11 vendor under a newer system is how this tablet ships.

## The secure world

![The secure world and the fence around it: lk makes an smc into an sml stage (a BL31 monitor by its strings) and on to the Trusty TOS, with that hop and the hardware-key box marked as not read; on the Android side 23 domains can open the Trusty IPC node and no app domain is among them, keys reach it only through keystore and the keymaster HAL, and an app can find the Widevine HAL but not the key ones](figures/secure-world.png)

The A10e ran Samsung's TEEGRIS. This tablet runs **Trusty**, Google's little-kernel TEE, in Unisoc's port. Three reads settle it: the firmware's own files, what Trusty does with the two commands `lk` sends it, and what the running OS lets near it.

### Which TEE, from the files

- The kernel's `gta8wifi_eur_open_defconfig` has `CONFIG_TRUSTY=y`, `CONFIG_TRUSTY_LOG=y`, `CONFIG_TRUSTY_VIRTIO=y` and `CONFIG_DRM_SPRD_GSP_IPC_TRUSTY=y`, and `# CONFIG_TEE is not set` (so no OP-TEE). There's no `CONFIG_TZDEV`, which is what TEEGRIS needs. `lk` has 49 lines with `trusty` in any case (`strings -n 8`) and none with `teegris`.
- `tos-sign.bin`'s body is the Trusty TOS: a little-kernel image (`welcome to lk/MP`, `lk/trusty/lib/trusty/smcall.c`, `Initializing Trusted OS SMC handler`) built `sharkl5pro, Built: 01:24:05 Oct 24 2023`, with nine packed 32-bit ELF blobs behind the kernel. Their `com.android.trusty.*` strings name keymaster(.secure), gatekeeper, the storage clients and proxy, rpmb.bl, storage_auth.rpmb, hwkey, hwrng, kernelbootcp and oemcrypto(.secure)/Widevine. That's more names than blobs, and a name in a string isn't proof of a running app.
- `sml-sign.bin` is ARM Trusted Firmware's BL31 with the Trusty dispatcher (`NOTICE:  BL31: %s`, `trusty_fast`). So the stack is lk (normal world) → BL31 monitor at EL3 (sml) → Trusty TOS (tos), the usual Trusty layout.

```
grep -E 'TRUSTY|CONFIG_TEE|TZDEV' arch/arm64/configs/gta8wifi_eur_open_defconfig   # in Samsung's published kernel source for this build
python3 tools/pin_base.py tos-sign.bin --skip 0x200 --end 0xbc000 --high   # base 0xffffffffe0000000, 101 votes to 38
strings -n 8 tos.body | grep -E 'com\.android\.trusty\.|welcome to lk|Built:'
```

The TOS body splits like `lk` did: the Trusty kernel is the first ~752 KiB (AArch64), then nine packed 32-bit ARM ELF trusted apps start at body offset `0xbc000`. Only the kernel part was carved out and read (`head -c 770048 tos.body > tos-kernel.body`; that's `0xbc000` bytes). It loads at `0xffffffffe0000000`, pinned the same two ways as `lk`.

### What Trusty does with lk's two commands

`lk` reaches the secure world with an `smc #0` whose function id is `0xb4000020` and whose second argument word is the command: the "command `0x33`" and "command `0x20`" of the `lk` sections above. In the TOS, one handler takes those, `sprdsec`'s `process_sip_call` at `0xffffffffe004256c`, and switches on that command word. It checks the id is `0xb4000020` first, then:

- **Command `0x33` - the unlock record (`FUNCTYPE_CHECK_LOCK_STATUS`).** It maps the 64-byte record `lk` read out of `miscdata`, computes its own expected 64 bytes, compares the two, and writes `1` into the buffer at offset `0x40` on a match (`unlock status is matched, return unlock.`) or `0` on a miss. The expected bytes come from `0xffffffffe0041d74`: derive a key with the label `VerifiedBoot-HUK-DERIVE` (through `0xffffffffe0053b00`, which wasn't read), then AES-CBC the label `VerifiedBoot-UNLOCK` under it. So the unlock record isn't a flag `lk` trusts. It's a token the secure world computes for itself and compares. Going by that label, the key comes from the chip's hardware key, which would tie the token to this one tablet and mean planting bytes in `miscdata` can't forge it. That last step is the label's word, not the code's: the routine that derives the key wasn't read.
- **Command `0x20` - vbmeta (`avb_slot_verify`).** The handler at `0xffffffffe0072a5c` runs libavb inside the TEE: its callees are the AVB slot-verify path (`### enter avb_slot_verify. ###`, `avb_slot_verify result is %d`, `external/lk/platform/sprd/secureboot/sprd/avb/tos_avb_api.c`). So the vbmeta check `lk` was seen handing to the secure world really does run there, as a full `avb_slot_verify`, and the result comes back. This is the secure world's half, not proof `lk` trusts only it: `lk` checks vbmeta's signature with its own libavb as well (see [what lk does about verified boot](#what-lk-does-about-verified-boot)), and the boot state is set from this command's answer, in `0x9f120b00`; `lk`'s own check feeds the kernel command line, with the caveat given there that Ghidra may have cut that function's tail.
- The same switch carries the rest of the secure plumbing: `0x31` runs a caller's buffer through the same keyed step, `0x30` only logs and returns an error in this build, `0x32` checks a password through a different routine (`0xffffffffe0041f20`), `0x40` takes the chip id handed over by the bootloader (its log line starts `from uboot smc(set chip uid)`), and a spread of `0x21`-`0x26` and `0x34`-`0x36` handlers for RPMB and efuse.

```
python3 tools/a64_refs.py tos-kernel.body 0xffffffffe0000000 \
    "FUNCTYPE_CHECK_LOCK_STATUS" "VerifiedBoot-UNLOCK" "VerifiedBoot-HUK-DERIVE" "enter avb_slot_verify"
```

This answers the question the `lk` read left open, "what does Trusty do with `0x20` and `0x33`": `0x33` checks an unlock token it computes for itself, tied to the chip if its key label means what it says, and `0x20` is libavb. It was read with Ghidra through REA, named by address, for a handful of functions, not the whole TOS.

*Not read:* The key-derivation primitive itself (which hardware key, which KDF), the nine trusted apps packed behind the kernel, and what BL31 in `sml` does between the `smc` and the TOS.

### What the running OS lets near it

The secure world's Android side was read from the stock `vendor` and `system` images (`debugfs`, no mount) and the compiled SELinux policy (`seinfo`/`sesearch` on `vendor/etc/selinux/precompiled_sepolicy`, v30 MLS, 2900 types, 52,742 `allow` rules, **0 permissive domains**, a proper `user`-build lockdown).

What talks to Trusty: the IPC node `/dev/trusty-ipc-dev0` and the shared-memory node `/dev/tshm`, both labelled `teetz_device` and both mode `0660 system:system`. The userspace that reaches them, each in its own SELinux domain: `keystore`, the `keymaster` HALs (`@4.0` and a `@4.1-unisoc`), `gatekeeper@1.0-service.trusty`, Unisoc's `trusty@1.0` client, Widevine DRM, `mediacodec`, `vold`, `vaultkeeperd`, Samsung's `sem`/`proca`/`fkey`/`kgta`/`hdcp`/`iccc`/`face` HALs, and a few system domains like `vendor_shell`, `engpc` and `gatekeeperd`. That's 23 in all with read or write on it, going by `sesearch -A -t teetz_device -c chr_file` (`init` and `vendor_init` also show up there, but only with `setattr`, so they aren't counted). `drk`, despite the name, isn't one of them: it holds no `teetz_device` rule. Secure storage rides a second path: `sprdstorageproxyd` and `rpmbserver` run in the `tee` domain and are the only things with `chr_file` to the RPMB node.

The fence around it holds, read the same way the A10e's was:

- **No app domain reaches the TEE at all.** Across `untrusted_app` and its variants (`_25`/`_27`/`_29`, `sec_`, `filtered_`, `vzwfiltered_`), `isolated_app`, `ephemeral_app`, `priv_app` and `platform_app`, there is **not one `allow` rule** on `teetz_device`, on the RPMB node, or on the `rpmbserver` socket. And here the Unix modes back SELinux up: the nodes are `0660 system:system`, so an app (not in `system`) is already shut out even before the policy, unlike the A10e, where most of the TrustZone nodes were mode `0666` and SELinux was the main fence.
- **Of the HALs that touch the TEE, an app can discover only the media ones.** In all `untrusted_app` can `find` 15 hwservice types (`sesearch -A -s untrusted_app -c hwservice_manager -p find`); this point is about the ones behind the TEE nodes. `untrusted_app` has no `hwservice_manager find` on keymaster, gatekeeper, the Unisoc trusty client, or any of Samsung's `drk`/`sem`/`wvkprov`/`engmode`/`vaultkeeper` services, all denied. The TEE-touching HALs it *can* find are for protected media: Widevine DRM (`hal_drm`) and the codec HAL (`mediacodec`) both hold `teetz_device` access, and CAS reaches a `tee_device` type that no node here carries. So an app's one path toward the secure world is content protection, never keys or the lock state.
- **The one sanctioned route to keys** is the normal Android one: an app makes a binder call to `keystore` (allowed) and finds `keystore_service` (allowed); `keystore` calls the `keymaster` HAL (`keystore → hal_keymaster_server:binder`) and also holds its own `teetz_device` access. There's no `keystore2` domain on this build; it's the older `keystore`.
- The `rpmbserver` socket is mode `0666`, but only `init`/`vendor_init` have `sock_file` rules on it and nothing in `appdomain` can `connectto` the `tee` domain, so the open mode is unreachable in practice.
- The Trustonic hwservice types (`vendor.trustonic.tee`, `.teeregistry`) exist in the policy but no Trustonic binary ships. It's leftover template, the same thing the A10e showed.

```
mkdir -p vendor/etc && debugfs -R 'rdump /etc/selinux vendor/etc' vendor.img   # pull the compiled policy out of vendor.img first (it grumbles about ownership when not root, and still extracts)
seinfo vendor/etc/selinux/precompiled_sepolicy | grep -E 'Allow|Types|Permissive'
sesearch -A -t teetz_device -c chr_file vendor/etc/selinux/precompiled_sepolicy
sesearch -A -s untrusted_app -t teetz_device -c chr_file vendor/etc/selinux/precompiled_sepolicy   # no rules
sesearch -A -s untrusted_app -t hal_keymaster_hwservice -c hwservice_manager vendor/etc/selinux/precompiled_sepolicy   # no rules
```

One caveat on the policy read: `vendor/etc/selinux/precompiled_sepolicy` carries a `plat_sepolicy_and_mapping.sha256` that doesn't match `system`'s, so Android `init` likely recompiles the policy at boot from the CIL sources against the system's plat policy rather than loading this exact blob. So these are the stock Samsung **vendor** rules; the tablet as it runs is LineageOS, whose own policy wasn't pulled off the device. This is the stock fence, not a read of what the running GSI enforces.

## The kernel

`boot.img` is a header v2 image: os version `11.0.0`, patch level `2025-08`, 2048-byte pages, cmdline `console=ttyS1,115200n8`. The kernel inside is a raw ARM64 `Image` and says:

```
Linux version 4.14.199-29056031-abX200XXS6DYG6 ... clang version 11.0.1 ... #2 SMP PREEMPT Mon Jul 28 15:32:23 KST 2025
```

```
unpack_bootimg --boot_img boot.img --out boot/unpacked
strings -n 8 boot/unpacked/kernel | grep -m1 '^Linux version'
```

Samsung's published source for this build is the same `4.14.199` (its `Makefile`: `VERSION = 4`, `PATCHLEVEL = 14`, `SUBLEVEL = 199`) and has a `gta8wifi_eur_open_defconfig`. The `-29056031-abX200XXS6DYG6` part of the version isn't in that defconfig (`CONFIG_LOCALVERSION=""`). Where it comes from isn't traced.

*Not read yet:* Whether that source builds into this exact kernel.

## What didn't work, and mistakes

Kept on purpose, same as the A10e one.

- **The md5 check that failed for the wrong reason.** The first try at checking the bundles cut the md5 line off at the last newline before it, and the BL and AP bundles came out as mismatches. The last bytes show why (`tail -c 176 <bundle> | xxd`): in the CSC bundle the hash follows a text line ending in a newline (`original_tar_file_size:67543040`), so that cut works. In the BL bundle zero bytes run right up to the hash with no newline, so the cut lands somewhere earlier. Cutting at the hash itself fixed it, and all four match. The AP bundle's tail wasn't looked at; it just passes the same fix. `tools/md5_check.py` does it the right way.
