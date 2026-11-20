# what it took

building this repo - reading the firmware, writing it up, drawing the diagrams - ran across three Claude Code sessions and several helper agents. this page is the tool calls, the tokens, and what the same work would cost at API prices. how the reading itself was done is in [how the code was read](how-the-code-was-read.md).

the three sessions, with their helpers: **the build** (phases 0 to 4 - the bundles, the images, the signing chain, the first bootloader read), **the secure world** (phases 5 and 6 - the Trusty TEE, the comparison, the diagrams) and **the review** (a third session, the deep `lk` boot-path read plus two blind reads of the finished repo). the git history is authored under two models (Fable 5.2 and Opus 4.8); the finer five-model split below is from the transcripts, not the commit log.

![tool calls per session, split into shell commands, REA, file tools and everything else: the build 269, the secure world 246, the review 459](../figures/tool-calls.png)

![the API-price estimate per model split into model output, cache reads and cache writes, about $115 to $123 in all, and the tokens per session: written, new input, and the far larger re-read total](../figures/cost-and-tokens.png)

**tool calls, per session** (helper agents included):

| session | shell | REA | file tools | everything else | total |
|---|---|---|---|---|---|
| the build | 224 | 21 | 14 | 10 | 269 |
| the secure world | 142 | 15 | 76 | 13 | 246 |
| the review | 329 | 49 | 42 | 39 | 459 |
| **all three** | **695** | **85** | **132** | **62** | **974** |

so **85 REA calls** read the bootloader and the secure world. REA is the small slice that does the actual decompiling; shell is the bulk, and most of that is little scripts that scan the whole image for "who jumps here" and "who reads this value" to find which functions are worth decompiling - the decompiler reads a function, the scripts pick which one. "file tools" is Read, Edit, Write, Grep and Glob; "everything else" is the diagram builds, coordination between the sessions, and the like.

the review session's 49 REA calls cover its own deep `lk` read (18 distinct functions decompiled) and the two blind reads its helpers ran over the finished repo. opens and closes are a big share of any such count: REA runs one Ghidra at a time, so each read opens the image and closes it after.

**tokens, per session** (helper agents included):

| session | written | new input | re-read from cache |
|---|---|---|---|
| the build | 239,885 | 774,808 | 71,435,720 |
| the secure world | 382,457 | 702,368 | 80,852,380 |
| the review | 398,137 | 1,413,576 | 100,928,501 |
| **all three** | **1,020,479** | **2,890,752** | **253,216,601** |

"written" is model output; "new input" is input plus cache-creation tokens; "re-read" is cache reads - the whole conversation read again every turn, which is why it dwarfs the rest.

**what it would cost at API prices.** the work ran on a Claude subscription, so this is an *estimate* - what the same tokens would run billed per-token on the pay-as-you-go API, not a bill:

| model | where it ran | estimated cost |
|---|---|---|
| Fable 5.2 | the build and the review sessions | $54.91 - $61.44 |
| Opus 4.8 | most of the secure-world session | $49.24 - $51.02 |
| Sonnet 5.5 | four helper agents | $8.45 |
| Opus 5.5 | the start of the secure-world session | $1.97 - $2.41 |
| Haiku 5.5 | one helper agent | $0.03 |
| **all** | | **$114.61 - $123.35** |

so **about $115 to $123** for the whole repo so far. almost all of it is the cache, not the thinking: at the high end, re-reading the conversation every turn is $70.03 and writing it to cache $26.08, against $27.23 of model output and under a cent of fresh input.

the prices, USD per million tokens, from [models.dev](https://models.dev) (`models show`, read 20 Nov 2026):

| model | input | output | cache read | cache write |
|---|---|---|---|---|
| Fable 5.2 | 8 | 40 | 0.2 | 10 |
| Opus 4.8 | 5 | 25 | 0.5 | 6.25 |
| Opus 5.5 | 4 | 20 | 0.2 | 5 |
| Sonnet 5.5 | 2 | 10 | 0.1 | 2.5 |
| Haiku 5.5 | 0.1 | 0.5 | 0.01 | 0.125 |

and the tokens behind it, per model (uncached input / output / cache read / cache write):

| model | uncached in | output | cache read | cache write |
|---|---|---|---|---|
| Fable 5.2 | 902 | 410,031 | 138,119,018 | 1,087,840 |
| Opus 4.8 | 400 | 321,312 | 76,446,581 | 476,338 |
| Opus 5.5 | 74 | 24,871 | 3,768,173 | 144,437 |
| Sonnet 5.5 | 526 | 227,991 | 34,245,203 | 1,099,116 |
| Haiku 5.5 | 30 | 36,274 | 637,626 | 81,089 |

*source and limits:* the calls and tokens were counted by a script (`tools/tool_calls_chart.py` draws the tool-call chart, `tools/cost_chart.py` the cost one) from the three sessions' transcripts and every helper agent's - API-reported usage per message, de-duplicated by message id; tool-use blocks de-duplicated by id - at about 5:56 PM on 20 Nov 2026, as one consistent run. two sessions were still going then, so it's a snapshot and the real totals are a little higher. two short pre-fork stubs were left out so nothing is double-counted. the cost is an estimate at list prices, not a bill. its range is the cache-write price: models.dev lists one rate, so the low end prices every cache write at it, and the high end prices the three main sessions' writes at the one-hour-cache rate (twice the input price) - that doubling is Anthropic's rule as best i understand it, but it wasn't verified on the day. all the arithmetic was done by a script, not by hand.
