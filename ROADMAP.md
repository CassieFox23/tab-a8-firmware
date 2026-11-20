# roadmap

where this is going, in the order it'll happen. cheapest reads first, the bootloader last, since nobody knows yet how big that one is.

a phase is done when its finish line is met, not when it feels done.

## phase 0 - the outline

- [x] README, licence, stub pages

## phase 1 - the easy rows

the things that can be read straight off the stock firmware without a disassembler.

- [ ] which build is being read, and what's in each bundle
- [ ] the chip, from the device tree
- [ ] the partition map, from the PIT
- [ ] what `vbmeta.img` says - the key, the flags, which partitions it covers
- [ ] the vendor's Treble level, and why a current GSI fits it
- [ ] the kernel in `boot.img` against Samsung's published source

finish line: those rows of [`A8-vs-A10e.md`](A8-vs-A10e.md) are filled, each with the command that shows it.

## phase 2 - the LineageOS how-to

- [ ] the steps, written from the commands that were actually run
- [ ] every step checked a second time before it goes in
- [ ] what the tablet ends up running
- [ ] how to go back to stock
- [ ] what broke along the way

finish line: [`docs/lineageos-howto.md`](docs/lineageos-howto.md) has no step that wasn't run on a real SM-X200.

## phase 3 - sizing the bootloader

the BL bundle has seven files. before reading any of them properly: what format is each one, which are signed, which are encrypted, which are readable at all.

- [ ] a short table of the seven files - size, header, entropy, readable or not
- [ ] a call on which ones are worth a full read

finish line: phase 4's scope is written down, or phase 4 is dropped with the reason.

## phase 4 - the bootloader read

- [ ] where the unlock state lives and who reads it
- [ ] what the bootloader checks before it boots an image, locked and unlocked
- [ ] any extra gate on flashing, like the A10e's Knox Guard
- [ ] how that differs from the A10e's `sboot`

finish line: the boot chain section of [`Tab-A8-teardown.md`](Tab-A8-teardown.md) is written, with addresses.

## phase 5 - the secure world

- [ ] which TEE this chip runs, from the firmware's own files
- [ ] what the SELinux policy lets a normal app reach

finish line: the secure world row of the comparison is filled.

## phase 6 - putting the two side by side

- [ ] the comparison page finished
- [ ] diagrams - the tablet's boot chain, and the two devices next to each other
- [ ] the README rewritten around what was found

## phase 7 - review, then public

- [ ] a blind read of the whole thing by a reviewer who wasn't in the room
- [ ] fixes from that read
- [ ] repo goes public, Discussions on, the how-to gets its thread
