# Roadmap

Where this is going, in the order it'll happen. Cheapest reads first, the bootloader last, since nobody knows yet how big that one is.

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

- [x] A blind read of the whole thing by a reviewer who wasn't in the room, two of them: one on the whole repo, one on the fixes and the new diagrams
- [x] Fixes from that read
- [ ] Repo goes public, Discussions on, the how-to gets its thread
