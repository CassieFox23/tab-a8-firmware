# roadmap

where this is going, in the order it'll happen. cheapest reads first, the bootloader last, since nobody knows yet how big that one is.

a phase is done when its finish line is met, not when it feels done.

anything that's easier to see than read gets drawn - a diagram or a chart in each phase, not saved up for the end.

## phase 0 - the outline

- [x] README, licence, stub pages

## phase 1 - the easy rows

the things that can be read straight off the stock firmware without a disassembler.

- [x] which build is being read, and what's in each bundle
- [x] the chip, from the device tree
- [x] the partition map, from the PIT
- [x] what `vbmeta.img` says - the key, the flags, which partitions it covers
- [x] the vendor's Treble level, and why a current GSI fits it
- [x] the kernel in `boot.img` against Samsung's published source
- [x] picture: the partition map
- [x] pictures: what vbmeta covers, and the Treble fit next to the A10e's miss

finish line: those rows of [`A8-vs-A10e.md`](A8-vs-A10e.md) are filled, each with the command that shows it.

## phase 2 - the LineageOS how-to

- [x] the steps, written from the commands that were actually run
- [x] every step checked against the logs before it goes in - not run again
- [x] what the tablet ends up running
- [ ] how to go back to stock - only the recovery partition has been written back so far, the full restore is untested
- [x] what broke along the way
- [x] picture: the whole flash as one flow, with the way back to stock

finish line: [`docs/lineageos-howto.md`](docs/lineageos-howto.md) has no step that wasn't run on a real SM-X200.

## phase 3 - sizing the bootloader

the BL bundle has seven files. before reading any of them properly: what format is each one, which are signed, which are encrypted, which are readable at all.

- [x] a short table of the seven files - size, header, entropy, readable or not
- [x] a call on which ones are worth a full read: `lk-sign.bin` and the SPL. the other five stay at sizing level
- [x] picture: the seven files by size and entropy, and the signing chain the hashes gave away

finish line: phase 4's scope is written down, or phase 4 is dropped with the reason.

## phase 4 - the bootloader read

scope: `lk-sign.bin` (the main bootloader) and `u-boot-spl-16k-sign.bin` (the first stage).

- [x] the load address of each, pinned before anything else
- [x] what trusts key A, if the SPL shows it - it doesn't. the SPL is the stage being checked, so the answer is below it

- [x] where the unlock state lives and who reads it
- [x] what the bootloader checks before it boots an image, locked and unlocked - except what it does next with a failed check while locked
- [x] any extra gate on flashing, like the A10e's Knox Guard
- [x] how that differs from the A10e's `sboot`
- [x] picture: the boot chain, who checks whom

finish line: the boot chain section of [`Tab-A8-teardown.md`](Tab-A8-teardown.md) is written, with addresses.

## phase 5 - the secure world

- [ ] which TEE this chip runs, from the firmware's own files
- [ ] what the SELinux policy lets a normal app reach
- [ ] picture: the secure world and the fence around it

finish line: the secure world row of the comparison is filled.

## phase 6 - putting the two side by side

- [ ] the comparison page finished
- [ ] diagrams - the tablet's boot chain, and the two devices next to each other
- [ ] the README rewritten around what was found

## phase 7 - review, then public

- [ ] a blind read of the whole thing by a reviewer who wasn't in the room
- [ ] fixes from that read
- [ ] repo goes public, Discussions on, the how-to gets its thread
