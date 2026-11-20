# Tab A8 teardown

**stub.** nothing below has been read yet - these are the questions, the same kind the [A10e teardown](https://github.com/CassieFox23/a10e-firmware/blob/master/A10e-teardown.md) answered for the phone.

## the device

- model, build and Android version of the stock firmware being read
- the chip, from the device tree
- the partition layout

## the boot chain

- what the bootloader files are on this chip and how they're packed
- who verifies whom, stage by stage
- where the OEM-unlock state is stored and read

## verified boot

- the AVB key and where it lives
- what the bootloader does with an image signed by another key, locked and unlocked

## why a GSI fits

- the vendor's Treble level against what the GSI ships
- the kernel version against that level's floor

## the secure world

- which TEE this chip runs and what talks to it
- what the SELinux policy lets a normal app reach

## the kernel

- Samsung's published source against the kernel in the stock boot image

## what didn't work, and mistakes

- kept on purpose, same as the A10e one
