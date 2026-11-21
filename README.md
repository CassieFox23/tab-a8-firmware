# tab-a8-firmware

a static read of the stock firmware on a **Samsung Galaxy Tab A8 (SM-X200)** - the tablet that took [LineageOS](https://lineageos.org), next to the phone that wouldn't.

![an animated blueprint sheet of what happens when you press power on a Galaxy Tab A8: the first loader checks the next pieces against a key fingerprint and jumps to sml, which starts with Trusty in the secure world; the bootloader lk reads an unlock record and asks the secure world if it is genuine; a locked tablet's boot image goes to Trusty to be checked, an unlocked one skips the check and the lamp reads orange; a failed check drops to Download Mode; Android gets the colour, and two unlocked tablets read orange and booted LineageOS](figures/blueprint-power-on.gif)

**the read is in**: the firmware's layout, verified boot, why a GSI fits, the bootloader's signing chain and its first two stages, and the secure world. there's a LineageOS how-to from two real flashes too. what's still open is listed at the end of each section of the [teardown](Tab-A8-teardown.md).

the short of it: on this tablet the bootloader doesn't decide alone. it asks a **secure world** (Trusty) whether the unlock is genuine and whether the boot image passes, and sets the boot colour from the answers. the A10e kept those decisions in `sboot`, the part you can read.

new to this? [the plain version](Tab-A8-teardown.md#the-plain-version) is six short points with no addresses.

## what it found (short version)

- **the files sign each other, and you can see it without a disassembler.** one key signs the first loader, which names the key for the next four files, and the bootloader names the key for the Android images.

![the signing chain: key A signs the SPL, whose certificate names key B; key B signs sml, tos, teecfg and lk; lk's certificate names the AVB key, which signs vbmeta.img](figures/signing-chain.png)

- **unlocking isn't a flag the bootloader just believes.** the switch in Developer options is one byte, but the unlock itself is a record the secure world recomputes and compares whenever the bootloader asks.

![the unlock step by step in four lanes: by hand (OEM unlocking on, both volume keys, long-press Volume Up, the tablet wipes itself), the bootloader (is an unlock possible, reading the record on every boot after), the secure world (Trusty recomputes the expected 64 bytes) and storage (the last byte of persistent, the record at miscdata + 0x2000); what runs the unlock between the long press and the wipe, what writes the switch byte and the record, the extra Knox Guard check and the key derivation are marked not read](figures/unlock-steps.png)

- **the secure world is Trusty, and apps are fenced away from it.** the hop into it and its key derivation weren't read, and the pictures say so.

![the secure world and the fence around it: lk makes an smc into an sml stage (a BL31 monitor by its strings) and on to the Trusty TOS, with that hop and the hardware-key box marked as not read; on the Android side 23 domains can open the Trusty IPC node and no app domain is among them, keys reach it only through keystore and the keymaster HAL, and an app can find the Widevine HAL but not the key ones](figures/secure-world.png)

- **a current GSI fits because the vendor's Treble level is one the GSI still ships.** the A10e's wasn't.

![Treble levels side by side: the A10e's vendor declares level 3 and its LineageOS 21 GSI ships levels 4 to 8, so nothing matches; the Tab A8's vendor declares level 5 and its LineageOS 22.2 GSI ships 5, 6, 7, 8 and 202404, so level 5 matches](figures/treble-fit.png)

the full read, with addresses and the command behind each claim, is the [teardown](Tab-A8-teardown.md).

## what this is for

the sibling to [a10e-firmware](https://github.com/CassieFox23/a10e-firmware), a phone that's locked down and stays on stock. the Tab A8 went the other way and runs a LineageOS GSI, so this asks the same questions of the tablet and puts the answers [side by side](A8-vs-A10e.md):

- what does the bootloader check before it boots something, and what changes once it's unlocked?
- what does verified boot ([AVB](https://android.googlesource.com/platform/external/avb/)) do on this one?
- why does a GSI fit here when it couldn't on the A10e?
- what's the secure world on this chip, and what keeps apps away from it?

## what's in here

| path | what it is |
|---|---|
| [`Tab-A8-teardown.md`](Tab-A8-teardown.md) | the write-up |
| [`A8-vs-A10e.md`](A8-vs-A10e.md) | the tablet next to the phone |
| [`docs/lineageos-howto.md`](docs/lineageos-howto.md) | LineageOS on the tablet: what was done, and what wasn't tested |
| [`docs/partition-map.md`](docs/partition-map.md) | all 58 partitions from the PIT |
| [`docs/how-the-code-was-read.md`](docs/how-the-code-was-read.md) | the tools that read the bootloader and the secure world |
| [`docs/what-it-took.md`](docs/what-it-took.md) | tool calls, tokens and an API-price cost estimate for building the repo |
| [`tools/`](tools/README.md) | eleven small scripts |
| `figures/` | the pictures: charts drawn by `tools/`, diagrams from the pages below |
| `.archify/` | eight diagrams as standalone pages with their sources: the flash, vbmeta, the signing chain, the boot chain, the secure world, the two devices, power on, the unlock |
| `.blueprint/` | the source of the animated power-on sheet |
| [`ROADMAP.md`](ROADMAP.md) | the phases |

## get the files

no firmware is in here and none will be - the stock bundles are big. the build read is `X200XXS6DYG6` (CSC `X200XAR6DYG6`), and how to fetch your own is [step 2 of the how-to](docs/lineageos-howto.md#2-get-the-stock-firmware-and-pull-out-its-recovery).

## samsung

i'm not affiliated with Samsung at all. nobody there asked for this, helped with it or looked it over. it's just me and a tablet i own.

Samsung and Galaxy are Samsung's trademarks. the names are only here because that's what this is about.

there's no Samsung firmware or code in this repo.

## help

got a question, or spotted something wrong? open an issue: [github.com/CassieFox23/tab-a8-firmware/issues](https://github.com/CassieFox23/tab-a8-firmware/issues)

## contributing

this is a personal project. issues are welcome, pull requests aren't expected - see [CONTRIBUTING.md](CONTRIBUTING.md).

## license

the scripts and the write-up are [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html) - see [`LICENSE`](LICENSE). holder: Cassie_Fox. the `.archify/` diagrams were made with [archify](https://github.com/tt-a1i/archify), and the generated pages carry its runtime and the [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) font ([OFL-1.1](https://openfontlicense.org)) under their own licenses. the animated power-on sheet was drawn with [blueprint](https://github.com/intincrab/blueprint) (MIT); only its pictures are here, not its code.
