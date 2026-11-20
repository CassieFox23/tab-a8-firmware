# tab-a8-firmware

a static read of the stock firmware on a **Samsung Galaxy Tab A8 (SM-X200)** - the tablet that took [LineageOS](https://lineageos.org), next to the phone that wouldn't.

**the read is in.** the build, the chip, the partition map and verified boot's metadata; why a current GSI fits; the whole bootloader signing chain worked out from the hashes; the two main bootloader stages read for how they check each other, where the unlock state lives and what Knox Guard gates; and the secure world - which TEE this chip runs, what the bootloader asks it, and what keeps apps away from it. there's a LineageOS how-to too, from two real flashes. [`ROADMAP.md`](ROADMAP.md) has the phases; what's still open is listed at the foot of each section of the [teardown](Tab-A8-teardown.md).

the short of it: on this tablet the decisions that matter sit in the **secure world**, not in the bootloader you can read. a little-kernel TEE (Trusty) judges a device-bound unlock token and runs the vbmeta check that sets the boot state, and the bootloader goes by its answers. that's the opposite of the A10e, where those decisions were in `sboot` - and it's why this one unlocks and runs a GSI where the phone couldn't.

new to this? [the plain version](Tab-A8-teardown.md#the-plain-version) is six short points with no addresses.

## what this is for

this is the sibling to [a10e-firmware](https://github.com/CassieFox23/a10e-firmware). that one is about a Galaxy A10e that's locked down and stays on stock - so it ended up being a read of how a phone decides what it's allowed to boot.

the Tab A8 went the other way, it's running a LineageOS GSI. so the plan here is to ask the same questions of the tablet and put the two answers side by side:

- what does the bootloader check before it boots something, and what changes once it's unlocked?
- what does verified boot ([AVB](https://android.googlesource.com/platform/external/avb/)) do on this one?
- why does a GSI fit here when it couldn't on the A10e?
- what's the secure world on this chip, and what keeps apps away from it?

the tablet is a different chip family too - Samsung's kernel source for it is a Unisoc (Spreadtrum) tree, where the A10e is Exynos. so the bootloader won't look the same, and the A10e scripts won't just carry over.

there's also a [how-to](docs/lineageos-howto.md) for putting LineageOS on the tablet, since that part actually worked.

## what's in here

| path | what it is |
|---|---|
| [`Tab-A8-teardown.md`](Tab-A8-teardown.md) | the writeup - the full read, each section ending with what's still open |
| [`A8-vs-A10e.md`](A8-vs-A10e.md) | the tablet next to the phone - every cell filled, the A10e side links to its teardown |
| [`docs/partition-map.md`](docs/partition-map.md) | all 58 partitions from the PIT |
| [`docs/lineageos-howto.md`](docs/lineageos-howto.md) | the LineageOS how-to - what was done on two tablets, and what wasn't tested |
| [`docs/how-the-code-was-read.md`](docs/how-the-code-was-read.md) | the REA + Ghidra tools that read the bootloader and secure world, and what each is for |
| `figures/` | pictures - the charts are made by scripts in `tools/`, the diagrams are screenshots of the archify pages |
| `.archify/workflow-tab-a8-flash-20261120-144800/` | the whole flash as one flow diagram - standalone HTML + its source |
| `.archify/tree-tab-a8-vbmeta-20261120-145200/` | what vbmeta covers, as a tree - standalone HTML + its source |
| `.archify/tree-tab-a8-signing-chain-20261120-151500/` | who signs what in the bootloader files - standalone HTML + its source |
| `.archify/workflow-tab-a8-boot-chain-20261120-154500/` | the boot chain, who checks whom - standalone HTML + its source |
| `.archify/arch-tab-a8-secure-world-20261120-162600/` | the secure world and the fence around it - standalone HTML + its source |
| `.archify/arch-tab-a8-vs-a10e-20261120-163500/` | the two devices side by side - standalone HTML + its source |
| [`tools/`](tools/README.md) | ten small scripts |
| [`ROADMAP.md`](ROADMAP.md) | the phases, and what's still open |

## get the files

no firmware is in here and none will be - the stock bundles are big. the build read is `X200XXS6DYG6` (CSC `X200XAR6DYG6`), and how to fetch your own is [step 2 of the how-to](docs/lineageos-howto.md#2-get-the-stock-firmware-and-pull-out-its-recovery).

## samsung

i'm not affiliated with Samsung at all. nobody there asked for this, helped with it or looked it over. it's just me and a tablet i own.

Samsung and Galaxy are Samsung's trademarks. the names are only here because that's what this is about.

there's no Samsung firmware or code in this repo.

## help

got a question, or spotted something wrong? open an issue: [github.com/CassieFox23/tab-a8-firmware/issues](https://github.com/CassieFox23/tab-a8-firmware/issues)

## contributing

this is a personal project. issues are welcome; pull requests aren't expected.

## license

the scripts and the write-up are [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html) - see [`LICENSE`](LICENSE). holder: Cassie_Fox. the `.archify/` diagrams were made with [archify](https://github.com/tt-a1i/archify), and the generated pages carry its runtime and the [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) font ([OFL-1.1](https://openfontlicense.org)) under their own licenses.
