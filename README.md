# tab-a8-firmware

a static read of the stock firmware on a **Samsung Galaxy Tab A8 (SM-X200)** - the tablet that took [LineageOS](https://lineageos.org), next to the phone that wouldn't.

**the read is in**: the firmware's layout, verified boot, why a GSI fits, the bootloader's signing chain and its first two stages, and the secure world. there's a LineageOS how-to from two real flashes too. what's still open is listed at the end of each section of the [teardown](Tab-A8-teardown.md).

the short of it: on this tablet the bootloader doesn't decide alone. it asks a **secure world** (Trusty) whether the unlock is genuine and whether the boot image passes, and sets the boot colour from the answers. the A10e kept those decisions in `sboot`, the part you can read.

new to this? [the plain version](Tab-A8-teardown.md#the-plain-version) is six short points with no addresses.

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
