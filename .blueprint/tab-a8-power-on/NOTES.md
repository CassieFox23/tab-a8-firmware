# tab-a8-power-on: blueprint sheet source

Scene file: `tab-a8-power-on.js` (scene id `tab-a8-power-on`, 860x460 (wider and taller than the 800x400 the craft guide names for complex scenes, to give the labels air; `size` accepts any width and height), 10 steps, 12 numbered parts plus a zone and a junction dot, 13 lines).
Facts come from `Tab-A8-teardown.md` ("the plain version", "what lk does about verified boot"). Nothing here has been linted, built or looked at: the blueprint project was only read, never run. While writing I used cat, sed, grep, find, ls, wc, awk, cut and head on the blueprint folder (read-only), `git check-ignore` once in the firmware repo (read-only, it matched nothing for `.blueprint`), and `python3` on scratch text files in `/tmp` (`caps*.txt`) only to count caption characters, plus a `python3` string edit of my own scene file. No blueprint file was executed or imported.

## Blueprint files read to learn the format

All in a clone of intincrab/blueprint, read statically (see above):
`SKILL.md`, `README.md`, `package.json`, `references/craft.md`, `templates/scene.js`, `examples/small/cache.js`, `examples/complex/url.js`, `examples/complex/circuit-breaker.js`, `examples/complex/oauth.js`, `scripts/check.mjs` (to know what the lint warns about), parts of `runtime/blueprint.js` (layout, port, leader, label and compile code, to hand-check geometry), the head of `scripts/build.mjs` and `scripts/export.mjs` (option names).

## Commands to run later, inside a VM (not run here)

`<skill-dir>` is the blueprint clone. Run from this folder or give full paths.

Lint (Node 18+ only, no browser; prints `clean` when there are no warnings):

    node <skill-dir>/scripts/check.mjs tab-a8-power-on.js

Optional contact sheet to look at before shipping (needs `npm i && npx playwright install chromium` in the skill folder, once):

    node <skill-dir>/scripts/frames.mjs tab-a8-power-on.js --out /tmp/tab-a8-power-on-frames.png

Standalone HTML page (runtime inlined; `--no-font` stops the page fetching IBM Plex Mono from Google Fonts):

    node <skill-dir>/scripts/build.mjs tab-a8-power-on.js --out tab-a8-power-on.html --no-font

GIF and PNG (Playwright; GIF should stay under about 5 MB, add `--width 960` if the script warns):

    node <skill-dir>/scripts/export.mjs tab-a8-power-on.js --format gif --out tab-a8-power-on.gif --no-font
    node <skill-dir>/scripts/export.mjs tab-a8-power-on.js --format png --out tab-a8-power-on.png --no-font

If Chromium comes from the distro, prefix with `BLUEPRINT_CHROMIUM=/usr/bin/chromium-browser` (README). The scene has no `sources` (no http links in the brief), so exports lose nothing there.

## Authoring rules I could not fully satisfy

- **Never linted or looked at.** The workflow says lint until `clean` and read a contact sheet. I could do neither. I hand-checked every part box, numeral, label, note and line segment against the lint's rules and the runtime's geometry, but expect the real lint to find something (most likely: notes or numerals touching, tight margins). Fix those in the VM.
- **Part count.** Complex scenes allow 6-14 parts. I use 14 ids counting the zone and the junction dot. At the limit.
- **Edge margin.** After the loosening pass every part is at least 28 units from each edge of the 860x460 drawing area, and the notes and numerals are all inside it. (An earlier 800x400 layout had the zone and the key at y 30 and some notes near the bottom edge.)
- **"Problem ends the caption, next starts with So".** Steps 6-9 do not follow it cleanly. Step 5 ends on the problem ("it must learn if the owner unlocked the tablet") and step 6 starts "So". Steps 7, 8 and 9 each open with "But ... so ..." inside one caption instead, because the brief's chain has the problem and its fix as one link and there are only 10 steps. All captions are one sentence under 100 characters (longest 98).
- **Every part named in a caption by number.** Not met: the sieve (10) and the junction are not in any caption, the colour (9) is only in step 8's caption, the record's answer and the key are explained by notes. They are all in the key list via `name` and `note`.
- **Real numbers.** The facts give no measured units, so there are no `~120 MS`-style notes. The numbers on the sheet are the command codes 0x33 and 0x20 and counts (four pieces, two tablets).
- **Concrete first.** The starting case is "you press power". The facts name no specific tablet state or file beyond that.
- **Step 7 shows a green pass as the example.** The brief says a pass with Samsung's key is green, but not that it was seen on the tablets. The green chip is an illustration of the locked path, and the note beside it states the three colour rules. Only step 10 states what was actually seen (two tablets, unlocked, orange, LineageOS).
- **Lamp colour.** The kit's lamp only lights (yellow ink). It cannot be green, orange or red. The colour is shown by replacing its label text (`GREEN`, `ORANGE`, `RED`), and step 9 adds the red failure badge. Step 7 does not use a green badge because it would sit on the colour note.
- **Last frame as a summary.** Only notes marked `keep` survive on the finished still, and most of the rules are in step-bound notes. The finished sheet shows the parts, the lamp reading ORANGE, Android reading LINEAGEOS, the VERIFIEDBOOTSTATE string, SEEN ON 2 TABLETS, the NOT READ marks and lk's own-check note, but not the 0x33 / 0x20 command names, the green/yellow/red rule, or the red path's note. Download Mode (12) is on the sheet but not marked as the red path. Check this in the VM and consider `keep: true` on a note or two.
- **Leaders the lint cannot see.** Hand-checked only: the lamp (9) has its numeral on a custom `lead: [34, -14]` so its leader clears the three-line notes; Android (11) and Download Mode (12) lead east and south-west so their leaders do not cross a label or a note; the sieve (10) leads south so its numeral is clear of its label.
- **Camera.** Moves in step 4 (zoom to the SPL, sml and the secure-world zone), back to `all` in step 5, zoom to the lower right in step 8 (held through 9), `all` again in step 10. Not tried against the real runtime.

## Where I chose a kit part to stand for something

| Thing | Kit part | Why / caveat |
|---|---|---|
| The power key press | `box` "POWER ON" | No kit part for a key press; a plain labelled box |
| SPL, sml, lk | `box` | Named services in a chain |
| The key fingerprint the SPL carries | `key` | The kit's secret/credential part; it is a fingerprint, not the key itself, so the label says KEY FINGERPRINT |
| The four loaded pieces (teecfg, sml, trustos, lk) | One `queue` with 4 slots, filled one by one | A rack of slots; stands for "the four pieces", not a real queue. The same names also appear as separate boxes (sml, lk) later; the rack only shows they were loaded |
| The secure world | `zone` labelled SECURE WORLD, holding `box` TRUSTY | The catalogue uses zones for boundaries. sml is drawn outside the zone on purpose: the facts say the SPL jumps to sml, the secure-world monitor, which starts with Trusty. They do not say sml sits inside Trusty. The line from sml to Trusty is labelled THEN, not STARTS, to avoid saying more than that |
| The unlock record in miscdata | `book` labelled MISCDATA | A ledger/record part; the partition name is the label |
| The two asks (0x33, 0x20) | One `track` line `ask` from lk to Trusty, used twice, with notes naming the command | One channel drawn once; the command is in the note |
| Not-read hand-off from sml to lk | `wire` (dashed) with a kept yellow note HAND-OFF: NOT READ beside it | Dashed means "talks to / control signal"; the note says it was not read and sits 24 units from the line so it does not hug it. No chip travels on it |
| What checks the SPL | A kept note under POWER ON: "WHAT CHECKS THE SPL: NOT READ" | No part drawn, because nothing was read |
| The boot state colour | `lamp` | The status part; shows colour only through its label text (see above) |
| lk's own check | `sieve` on a `wire` from lk | A validation/filter part; the note says it is logged, feeds the kernel command line, and does not set the colour |
| Android | `screen` | The OS that gets the colour; its text changes to LINEAGEOS in step 10 to show what booted on the tablets |
| Download Mode | `box` | A destination, drawn below the junction |
| Where the colour goes | `dot` junction `junc` with `track`s to Android and to Download Mode | The kit's way to branch a line |
| Red / failure | `fail` badge on the lamp, red `chip` and `ball` runs | Red only for failure, as the style rules say |

## Facts left out

- The unlocked-bootloader warning shown at startup on real tablets: the code behind it was not read, and the brief allows leaving it out. No part or note for it.
- Nothing from the nine facts is left out except the warning screen above. Fact 7 (green or yellow logs a line and boots) is a note in step 8, beside Android, not a caption.
- Not in the brief's nine facts, so not drawn even though `candidate.json` has them: the `tos return error!` loop, `vbmeta_system` check, the `flash.locked` value, state numbers, the 10000 tick wait.

## What was run afterwards (20 Nov 2026)

The sheet was linted and exported inside an offline virtual machine, never on the host: blueprint at commit `f34e950`, Node 24, the guest's own Chromium 157 through `BLUEPRINT_CHROMIUM`, and `playwright-core` 1.64.1 in place of the pinned `playwright` 1.56.1.

- `check.mjs`: `clean` (10 steps, 54.8 s, 14 parts, 13 lines), exit 0.
- `export.mjs --format png,gif --no-font`: exit 0. The GIF is 1280 x 797 and 4.58 MB; the PNG is 2560 x 1594.

That is the second run. The first, on the 800 x 400 layout, also linted clean; the sheet was then re-laid at 860 x 460 because its text sat too close together, and run again the same way.

Only those two image files left the machine; they are `figures/blueprint-power-on.gif` and `figures/blueprint-power-on.png`. The standalone HTML page was not built or kept.
