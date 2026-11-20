# Tab A8 vs A10e

**in progress.** the A10e column points at what's already written up in [a10e-firmware](https://github.com/CassieFox23/a10e-firmware). a Tab A8 cell only gets filled once it's been read from the tablet's own files - the how is in the [teardown](Tab-A8-teardown.md).

| question | A10e (SM-A102U) | Tab A8 (SM-X200) |
|---|---|---|
| chip family | Exynos | Unisoc UMS512 (`ro.soc.model=T618`) |
| can the bootloader be unlocked? | no - OEM unlocking isn't allowed on that unit | yes - done on two units from Download Mode, and `ro.boot.flash.locked` read back `0` after ([how-to](docs/lineageos-howto.md), step 5). where that state is stored: not read yet |
| what verified boot accepts | one Samsung key while locked | `vbmeta.img` is signed with one RSA-4096 key (a different one from the A10e's) and covers 11 partitions. what the bootloader does with another key: not read yet |
| Treble level vs a current GSI | vendor level 3, below what the GSI ships | vendor level 5, VNDK 30, kernel 4.14.199 - the LineageOS 22.2 GSI ships a level 5 matrix and VNDK 30, so it fits |
| secure world | TEEGRIS | not read yet |
| extra flash gates | Knox Guard | not read yet |
| ends up running | stock Android 9 | LineageOS 22.2 (Android 15) as a GSI on the stock 4.14.199 kernel - both read back right after the flash, Oct 2026. the Android 11 vendor is still stock going by what was flashed (only `system` and `recovery`) |

the A10e answers are short on purpose - the real ones, with addresses, are in its [teardown](https://github.com/CassieFox23/a10e-firmware/blob/master/A10e-teardown.md).
