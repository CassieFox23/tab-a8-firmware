# Roadmap

Where this is going, in the order it'll happen. Phases 0 to 7 are done: the read is written up and the repo is public. Phases 8 on are what's still missing, cheapest first. Every item in them comes from a *not read* or *not tested* line somewhere in the write-up.

A phase is done when its finish line is met, not when it feels done.

Anything that's easier to see than read gets drawn: a diagram or a chart in each phase, not saved up for the end.

## Phase 0 - the outline

- [x] README, licence, stub pages

## Phase 1 - the easy rows

The things that can be read straight off the stock firmware without a disassembler.

- [x] Which build is being read, and what's in each bundle
- [x] The chip, from the device tree
- [x] The partition map, from the PIT
- [x] What `vbmeta.img` says: the key, the flags, which partitions it covers
- [x] The vendor's Treble level, and why a current GSI fits it
- [x] The kernel in `boot.img` against Samsung's published source
- [x] Picture: the partition map
- [x] Pictures: what vbmeta covers, and the Treble fit next to the A10e's miss

Finish line: those rows of [`A8-vs-A10e.md`](A8-vs-A10e.md) are filled, each with the command that shows it.

## Phase 2 - the LineageOS how-to

- [x] The steps, written from the commands that were actually run
- [x] Every step checked against the logs before it goes in, not run again
- [x] What the tablet ends up running
- [x] What broke along the way
- [x] Picture: the whole flash as one flow, with the way back to stock

Finish line: [`docs/lineageos-howto.md`](docs/lineageos-howto.md) has no step that wasn't run on a real SM-X200.

Not tested: the full way back to stock. Only the recovery partition has been written back, and the how-to lists the rest under [not tested](docs/lineageos-howto.md#not-tested).

## Phase 3 - sizing the bootloader

The BL bundle has seven files. Before reading any of them properly: what format is each one, which are signed, which are encrypted, which are readable at all.

- [x] A short table of the seven files: size, header, entropy, readable or not
- [x] A call on which ones are worth a full read: `lk-sign.bin` and the SPL. The other five stay at sizing level
- [x] Picture: the seven files by size and entropy, and the signing chain the hashes gave away

Finish line: phase 4's scope is written down, or phase 4 is dropped with the reason.

## Phase 4 - the bootloader read

Scope: `lk-sign.bin` (the main bootloader) and `u-boot-spl-16k-sign.bin` (the first stage).

- [x] The load address of each, pinned before anything else
- [x] What trusts key A, if the SPL shows it: it doesn't. The SPL is the stage being checked, so the answer is below it

- [x] Where the unlock state lives and who reads it
- [x] What the bootloader checks before it boots an image, locked and unlocked: a failed check while locked ends in Download Mode
- [x] Any extra gate on flashing, like the A10e's Knox Guard
- [x] How that differs from the A10e's `sboot`
- [x] Picture: the boot chain, who checks whom

Finish line: the boot chain section of [`Tab-A8-teardown.md`](Tab-A8-teardown.md) is written, with addresses.

## Phase 5 - the secure world

- [x] Which TEE this chip runs, from the firmware's own files: Trusty, three ways
- [x] What Trusty does with the bootloader's two commands: `0x33` an unlock token Trusty vouches for (device-bound if its key label holds), `0x20` libavb
- [x] What the SELinux policy lets a normal app reach: of the HALs that touch the TEE, only the media ones (Widevine, codec), never the key ones
- [x] Picture: the secure world and the fence around it

Finish line: the secure world row of the comparison is filled.

## Phase 6 - putting the two side by side

- [x] The comparison page finished: every cell read, no "not read yet"
- [x] Diagrams: the tablet's boot chain (refreshed for the secure-world read), and the two devices next to each other
- [x] The README rewritten around what was found

## Phase 7 - review, then public

- [x] A blind read of the whole thing by a reviewer who wasn't in the room, three of them: one on the whole repo, two on the fixes and the new diagrams
- [x] Fixes from that read
- [x] Repo goes public, Discussions on, the how-to gets its thread

Finish line: met on 20 Nov 2026.

## Phase 8 - a third tablet, still on stock

One more SM-X200 hasn't been unlocked yet. It can show things the first two can't any more, and settle what the how-to only has from memory.

While it's still locked, read-only:

- [x] The locked boot state off a real tablet: `ro.boot.verifiedbootstate` and `ro.boot.flash.locked`. The repo has only seen orange. Read 21 Nov: `green`, `1`, vbmeta `locked`, in the teardown's verified-boot section
- [ ] The Download Mode screen's lines, letter for letter. The how-to isn't sure of `KG STATE` against `KG STATUS`
- [x] The Widevine level on stock, so the `L3` after the flash has something to compare to. Read 21 Nov with `tools/widevine_probe`: `L1`, not provisioned. The old `L3` came from a browser log, so the probe has to run after the flash too before it's a comparison

Also read off it while locked (21 Nov): `ro.boot.vbmeta.digest` matches the stock images (Phase 9's baseline), `ro.boot.dtbo_idx` `4` (Phase 11), the running kernel config against Samsung's defconfig (Phase 13), and a stock bugreport with the previous boot's kernel log, kept off the repo. Its own PIT, dumped in Download Mode, matches the CSC bundle's entries byte for byte (`recovery` is id `38`); its signature block names `X200XXU1AVG1`

During its flash:

- [ ] Which key confirms the unlock
- [ ] samloader-rs run in a normal terminal window, the one way it wasn't run
- [ ] The how-to followed as written, a third time
- [ ] What the first two tablets run today, read again. Their rows rest on October's logs

Finish line: the how-to has no "wasn't written down" or "may not be letter for letter" left in it.

## Phase 9 - the way back to stock

The how-to's biggest gap. Only the recovery partition has ever been written back.

- [ ] The `vbmeta` partition read back off an unlocked tablet, to show it's still the stock one. The stock side is read: a locked tablet's `ro.boot.vbmeta.digest` matches `avbtool calculate_vbmeta_digest` over the stock images (21 Nov). The same property off an unlocked tablet would answer this box
- [ ] A full restore: the BL, AP and HOME_CSC bundles flashed onto a tablet running the GSI
- [ ] Relocking the bootloader after it, and what the boot state, the Knox Guard line and `ro.boot.warranty_bit` read then
- [ ] Picture: the flash flow redrawn with the way back as a tested lane

Finish line: "going back to stock" in the how-to is a set of steps that were run, or it says which step failed. This one risks a tablet, so it waits until one can be spared.

## Phase 10 - the gaps in lk

The boot path was read. These are the pieces beside it.

- [ ] The unlock itself: what runs between the long press and the wipe, and what writes the record in `miscdata` and the switch byte in `persistent`
- [ ] `0x9f01082c`, the small function that sets the unlocked flag on the boot path
- [ ] What lets a different `system` through once unlocked. The skipped check is on `boot`, and the code that deals with the hashtree wasn't read. Lead (21 Nov): the stock ramdisk's `init` is AOSP's `libfs_avb` with `Allow signature verification error when the device is unlocked`. An unlocked tablet's boot log would show if that's the line that runs
- [ ] The key-trust slot at `0x9f9ae060` + `0x30`, which only exists while `lk` runs
- [ ] The second Knox Guard check, `0x9f038880`, and the second user of the flash-block message, `0x9f0179a0`
- [ ] The other callers of command `0x20`: `0x9f1208b0` on `pm_sys`, `0x9f123d88`, and which images come through the loader `0x9f00ef18`
- [ ] The three calls on the unlocked path that most likely draw the startup warning
- [ ] The second `smc` at `0x9f143d40`, the 18 branches into `0x9f010c48`, what `grdm` is, and the warranty bit. Leads, not answers: `lk` adds `androidboot.grdm_status=%s` (a stock tablet's command line has `NORMAL`) and has the line `GRDM BL Auth key derived from SHK on UNISOC LK`. A separate property, `ro.security.grdm_status`, reads `FW_VER:0502`; what sets that one wasn't read. `warranty_bit` read `0` both locked and unlocked
- [ ] The 74 pictures packed in the file
- [x] What `lk` hands the kernel on a locked, stock boot, from a bugreport's copy of the command line (21 Nov). In the teardown's "What lk hands the kernel", each key against its format string in `lk`
- [ ] The same command line off an unlocked tablet: `flash.locked`, `ulcnt`, `warranty_bit`, `kg` and the vbmeta digest after an unlock
- [ ] Picture: the unlock diagram with its grey boxes filled

Finish line: the *not read* list under "What lk does about verified boot" is empty, or each line left says why it can't be read from the file.

## Phase 11 - below and beside lk

- [ ] What trusts key A. Nothing in the bundle names it, so this may not be answerable from files at all
- [ ] Inside the SPL's check: `0x10bd8`, `0x107b4` and `0x10940`, where the hashing actually runs, and what picks the mode that skips the TEE files
- [ ] What BL31 in `sml` does between the `smc` and Trusty, and how control gets from `sml` to `lk`
- [ ] The unparsed part of the `SignerVer02` block
- [x] Which of the two `25c10` overlays in `dtbo.img` the tablet picks. The second one, entry 4 (`ro.boot.dtbo_idx`, zero-based). How `lk` chooses it wasn't read: entries 0, 2 and 4 share id and rev
- [ ] Picture: the boot chain with the `sml` hop drawn from code, not from strings

Finish line: the power-on diagram has no grey box between the SPL and `lk`.

## Phase 12 - deeper into Trusty

- [ ] The key derivation behind the unlock token (`0xffffffffe0053b00`): which hardware key, which KDF. Until then "tied to the chip" is the label's word
- [ ] The nine trusted apps behind the kernel: which blob is which
- [ ] The rest of the command switch: the RPMB and efuse handlers, and the password check on `0x32`
- [ ] Picture: the secure-world diagram with the hardware-key box filled

Finish line: the secure world's *not read* line is down to things that need the hardware.

## Phase 13 - loose ends

Small, separate, and none blocks another.

- [ ] `grd_fw.img`: what it is, and whether it's encrypted or only compressed
- [ ] The `teecfg` table and the Cortex-M4 image, both still at sizing level
- [ ] Whether Samsung's published kernel source builds into this exact kernel, and where the `-29056031-abX200XXS6DYG6` part of its version comes from. So far: the running config matches the defconfig on all 4,083 entries, and the suffix can only come from a build-time `LOCALVERSION`. No build has been run
- [ ] Android's own `checkvintf` run on the vendor and the GSI, and the per-HAL rows compared
- [ ] The SELinux policy as the tablet runs it under LineageOS, pulled off the device. The read so far is the stock vendor's
- [x] Why `vbmeta_system` has no chain entry in the main vbmeta, and what the `vbmeta_vendor` partition is for, since no bundle ships an image for it. The boot ramdisk's fstab names them: `system` is checked against `vbmeta_system`, `vendor` against `vbmeta_vendor` (21 Nov). What's on a real tablet's `vbmeta_vendor` wasn't read

Finish line: each one is answered in the teardown or moved to its "what didn't work" section with what was tried.
