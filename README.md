# tab-a8-firmware

poking at the stock firmware on a **Samsung Galaxy Tab A8 (SM-X200)** - the tablet that took [LineageOS](https://lineageos.org), next to the phone that wouldn't.

**just started.** right now this is the outline and nothing else - the pages below are stubs, and nothing in here is a finding yet.

## what this is for

this is the sibling to [a10e-firmware](https://github.com/CassieFox23/a10e-firmware). that one is about a Galaxy A10e that's locked down and stays on stock - so it ended up being a read of how a phone decides what it's allowed to boot.

the Tab A8 went the other way, it's running a LineageOS GSI. so the plan here is to ask the same questions of the tablet and put the two answers side by side:

- what does the bootloader check before it boots something, and what changes once it's unlocked?
- what does verified boot ([AVB](https://android.googlesource.com/platform/external/avb/)) do on this one?
- why does a GSI fit here when it couldn't on the A10e?
- what's the secure world on this chip, and what keeps apps away from it?

the tablet is a different chip family too - Samsung's kernel source for it is a Unisoc (Spreadtrum) tree, where the A10e is Exynos. so the bootloader won't look the same, and the A10e scripts won't just carry over.

there's also going to be a how-to for putting LineageOS on the tablet, since that part actually worked.

## what's in here

| path | what it is |
|---|---|
| [`Tab-A8-teardown.md`](Tab-A8-teardown.md) | the writeup - a stub for now, just the questions |
| [`A8-vs-A10e.md`](A8-vs-A10e.md) | the tablet next to the phone - the A10e side links to its teardown, the tablet side is empty |
| [`docs/lineageos-howto.md`](docs/lineageos-howto.md) | the LineageOS how-to - not written yet |
| [`tools/`](tools/README.md) | scripts, once there are any |

## get the files

no firmware is in here and none will be - the stock bundles are big. which build it is and how to fetch your own goes here once the read starts.

## samsung

i'm not affiliated with Samsung at all. nobody there asked for this, helped with it or looked it over. it's just me and a tablet i own.

Samsung and Galaxy are Samsung's trademarks. the names are only here because that's what this is about.

there's no Samsung firmware or code in this repo.

## help

got a question, or spotted something wrong? open an issue: [github.com/CassieFox23/tab-a8-firmware/issues](https://github.com/CassieFox23/tab-a8-firmware/issues)

## contributing

this is a personal project. issues are welcome; pull requests aren't expected.

## license

the scripts and the write-up are [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html) - see [`LICENSE`](LICENSE). holder: Cassie_Fox.
