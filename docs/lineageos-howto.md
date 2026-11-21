# LineageOS on the Tab A8 (SM-X200)

How a [LineageOS](https://lineageos.org) GSI (a generic system image: one Android build made to run on many devices) went onto two Galaxy Tab A8s from a Linux PC. It's written from the logs of doing it.

**Read this bit first.**

- This is what was done, twice, on two **SM-X200** (wifi) tablets, both on stock build `X200XXS6DYG6` / CSC `X200XAR6DYG6`, in October 2026. It's a record, not a promise. A different build, region or model (the X205 has a modem) might not behave the same.
- Unlocking the bootloader **wipes the tablet**. Back up first.
- Every step below was either run on the PC with its output saved, or done by hand on the tablet and seen to work. The few that were only followed and never checked one by one are marked *(followed, not checked on its own)*.
- The full way back to stock was **not** tested. Only a smaller piece of it was. See [going back to stock](#going-back-to-stock).
- I did the tablet side by hand. The PC side was run by [Claude Code](https://github.com/anthropics/claude-code).

The whole thing in one picture. Teal is by hand, green is a PC command, red wipes the tablet:

![The flash as one flow in three lanes: by hand on the tablet (OEM unlocking, Download Mode, long-press Volume Up which wipes it, boot into TWRP, Format Data, LineageOS 22.2 boots), on the PC (get stock firmware, write test of the stock recovery while still locked, flash.locked reads 0, flash TWRP with -p 38 --no-reboot, fastboot flash system, fastboot flash recovery with the stock one), and the way back to stock (the stock recovery menu shows after the write test; a full stock restore was never run)](../figures/flash-flow.png)

The same diagram as an interactive page is [`tab-a8-flash.html`](../.archify/workflow-tab-a8-flash-20261120-144800/tab-a8-flash.html). GitHub shows it as source, so download it and open it in a browser.

The order of the flash itself (TWRP, format data, fastbootd, system, then stock recovery back) comes from [yashjawale's notes](https://github.com/yashjawale/wiki/blob/main/docs/guides/flash-gsi-a8.md), which use Odin on Windows. This is the same route with Linux tools.

## What you need

| Thing | What was used | Where from |
|---|---|---|
| A Linux PC and a USB cable | Fedora-based | |
| `adb` and `fastboot` | android-tools 37.0.0 | The distro's package |
| A Samsung flasher | [samloader-rs](https://github.com/topjohnwu/samloader-rs) 2.2.0 (Apache-2.0) | Its [GitHub release](https://github.com/topjohnwu/samloader-rs/releases/tag/2.2.0) |
| The stock firmware for *your* build | `X200XXS6DYG6`, region XAR | Samsung's servers, through samloader-rs |
| A TWRP recovery (a custom recovery with a touch menu) for the SM-X200 | `3.7.1_12-support x200-205 stable A14` (the version string inside the image), as `twrp.tar` | An XDA thread, id 4763633 |
| The GSI | `LineageOS-22.2-20260105-VANILLA-EXT4-GSI` (Android 15) | MisterZtr's [SourceForge builds](https://sourceforge.net/projects/misterztr-gsi/files/LineageOS/) |

[Heimdall](https://git.sr.ht/~grimler/Heimdall) 2.2.2 was also used once, only to read the partition table. You can skip it.

samloader-rs's Linux x86_64 zip should have the sha256 GitHub lists for it:

```
f6029dcce75b8a66acc1975529085c53903f7cdb35505e0ac0a973f2652480ff  samloader-v2.2.0-linux-x86_64.zip
```

### About the TWRP file

This is the part to think about. It's an unofficial build from a forum thread, and the thread posts no hash, so there's nothing to check it against. It gets flashed, used once to format data and reach fastbootd, and then the stock recovery goes back over it.

These are the hashes of the file that was used. They tell you if yours is the same file, not whether to trust it:

```
31f2838e943a86c6d60ed7336177565bbfd122897129e2706f4c671b13aead2c  twrp.tar
54464609773a8b0fc1616e5bc700d6da1f70bea167e0f8f0c6980dcaa2faef79  recovery.img   (the one file inside it, 67108864 bytes)
```

### The GSI file

```
ca2b46488ac0deace0a9fa4770998a97                                  LineageOS-22.2-20260105-VANILLA-EXT4-GSI.7z   (md5)
ad4d00d5b865c35964033c7ac8aafe74c67a1921b7fcd3f9491df643ac17fd8f  LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img  (sha256, 2623557632 bytes)
```

Why this GSI fits this tablet at all is in the [teardown](../Tab-A8-teardown.md#why-a-gsi-fits).

## 1. Back up

The unlock erases everything on the tablet. Copy off anything you want before step 5.

## 2. Get the stock firmware and pull out its recovery

You need the stock `recovery.img` twice: once for a test before unlocking, and once at the very end.

The firmware came down with samloader-rs. The exact command line wasn't kept in the log. This is its shape:

```
samloader download -m SM-X200 -r XAR -v '<your full version string>' -d firmware/
```

What it gave: `SM-X200_4_20250807222311_nm95ejh13u_fac.zip`, 4870006933 bytes, and `unzip -tq` on it said `No errors detected`.

Unzip it, then take five images out of the AP bundle:

```
unzip SM-X200_4_20250807222311_nm95ejh13u_fac.zip
mkdir ap
tar -xf AP_X200XXS6DYG6_*.tar.md5 -C ap recovery.img super.img vbmeta.img vbmeta_system.img boot.img
```

Only `recovery.img` is needed for the flash; the other four aren't used in any step below. For this build `recovery.img` is 67108864 bytes:

```
c8cfcb64a7330ae215a536e3dad9a982030e01e77f55faa4b6facefc97157589  recovery.img
```

[`tools/md5_check.py`](../tools/md5_check.py) checks each bundle against its own md5 line.

## 3. Turn on OEM unlocking

On the tablet: Settings → Developer options → **OEM unlocking**, switch it on. (Developer options shows up after tapping the build number. That part is standard Android and wasn't logged.)

The switch only gives permission. Nothing is unlocked or wiped yet. With USB debugging on, the PC can read it back:

```
adb shell getprop sys.oem_unlock_allowed
```

`1` means allowed.

## 4. Meet Download Mode, and test a write while still locked

Power the tablet off. Hold **both volume keys** and plug the cable into the PC while holding them. You get a warning screen with three choices:

- **Short press Volume Up** - continue into Download Mode. Writes nothing.
- **Long press Volume Up** - device unlock mode. This is the wipe. Not yet.
- **Volume Down** - cancel.

Short press. Before unlocking, the Download Mode screen read `OEM LOCK` on and `KG STATE` completed (the label in the bootloader's own strings is `KG STATUS`, so that wording may not be letter for letter). On the PC, `lsusb` shows the tablet as `04e8:685d`.

Once Android is running with USB debugging on, you don't need the key combo any more:

```
adb reboot download
```

Now the test: write the **stock** recovery back over itself. It changes nothing, and it proves the PC can write to this tablet before anything is wiped.

```
samloader flash -p 38 ap/recovery.img
```

It ends with `recovery flash successful` and the tablet reboots. The first time round the tablet was then booted into recovery (`adb reboot recovery`), the stock recovery menu showed, and it booted to Android fine.

`38` is the recovery partition's id in this tablet's partition table. It's in the [partition map](partition-map.md), in the second column next to the name, not the row number in the first. A wrong number writes to a different partition, so check yours before using it (`samloader print-pit -f <your .pit file>` prints the table; the `.pit` file is in the CSC bundle).

You can also read the table off the tablet itself, in Download Mode. By samloader's own description it only dumps the table, and it reboots the tablet when it's done:

```
samloader dump-pit --output device.pit
samloader print-pit -f device.pit
```

On a third tablet, still on stock, the header and all 58 entries matched the CSC bundle's `.pit` byte for byte, with `recovery` at id `38`. Only the signature block after the entries differs: the tablet's names an older build, `X200XXU1AVG1`, signed in 2022.

## 5. Unlock the bootloader

**This wipes the tablet.**

1. Power off.
2. Hold both volume keys and plug in, same as before.
3. On the warning screen, **long press Volume Up**.
4. Confirm on the next screen. The screen says which key. It was pressed by hand and the key wasn't written down. The "Unlock bootloader?" picture packed in the bootloader says `Volume up : Yes` and `Volume down : No`, but that's read from the file, not off the tablet.
5. The tablet wipes itself and restarts.

It sits on the Samsung logo long enough to look like a boot loop. It wasn't one, either time. From then on there's a warning at startup about the unlocked bootloader.

Go through setup, turn USB debugging back on, and read the state:

```
adb shell 'getprop ro.boot.flash.locked; getprop ro.boot.verifiedbootstate; getprop ro.boot.warranty_bit; getprop sys.oem_unlock_allowed'
```

Both tablets answered:

```
0
orange
0
1
```

`flash.locked` `0` and `orange` are the unlocked bootloader. The third line is `ro.boot.warranty_bit` as the tablet reported it. What sets it wasn't read, so don't take that `0` as proof of anything.

For comparison, a third tablet still locked on stock `X200XXS6DYG6` answered `1`, `green`, `0` and `1` to the same line. So `warranty_bit` read `0` before an unlock as well as right after it. One of the first two tablets, a month into LineageOS, reads `1` (21 Nov 2026), so something after the unlock set it. What, wasn't read.

## 6. Flash TWRP

```
mkdir twrp && tar -xf twrp.tar -C twrp      # twrp.tar holds one file, recovery.img; this unpack line is written for the guide, not copied from a log
adb reboot download
samloader flash --no-reboot -p 38 twrp/recovery.img
```

It ends with `recovery flash successful`. `--no-reboot` matters: the tablet stays in Download Mode, so stock Android doesn't get a chance to start first.

## 7. Boot into TWRP

This one is about timing.

1. Hold **Volume Down + Power** until the screen goes black.
2. The moment it does, switch to holding **Power + Volume Up**. Keep holding through the warning screen until TWRP shows.
3. If TWRP asks about keeping system read-only, swipe to allow changes *(followed, not checked on its own)*.

## 8. Format data, then go to fastbootd

In TWRP:

1. **Wipe** → **Format Data** → type `yes` *(followed, not checked on its own)*
2. **Reboot** → **Recovery**, and let it come back into TWRP *(followed, not checked on its own)*
3. **Reboot** → **Fastboot**. This is fastbootd, the fastboot that runs inside recovery. It's the one that can write to `system`, which lives inside `super`.

What was checked is where it ends up. On the PC:

```
fastboot devices
fastboot getvar is-userspace
fastboot getvar is-logical:system
```

`fastboot devices` should say `fastbootd`, `is-userspace` should be `yes` and `is-logical:system` should be `yes`. `product` reads `gta8wifi`.

## 9. Flash the GSI, put the stock recovery back, reboot

```
fastboot flash system LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img
fastboot flash recovery ap/recovery.img
fastboot reboot
```

- The system image goes over in 10 sparse chunks and took about 99 seconds both times (`Finished. Total time: 99.590s` and `98.523s`).
- The second line puts the **stock** recovery back over TWRP. Don't skip it. The notes this route comes from say the tablet won't boot the GSI with TWRP still there. That claim wasn't tested here; the stock recovery just went back both times.
- **No vbmeta image was flashed**, and nothing about verified boot was disabled. Those three commands are all that got written in fastbootd.

## 10. First boot

Both tablets booted LineageOS on the first try. The second one took about 2 minutes 20 seconds from `fastboot reboot` to boot-complete.

```
adb shell 'getprop ro.lineage.version; getprop ro.build.version.release; uname -r'
```

```
22.2-20260105-VANILLA-EXT4-GSI
15
4.14.199-29056031-abX200XXS6DYG6
```

So it's Android 15 on top of the stock kernel. The vendor partition is the stock one too, going by what was flashed: only `system` and `recovery` were written.

## After it boots

- **The launcher stutters at the native 1200x1920.** Frame stats (`dumpsys gfxinfo`) put about 80% of app-drawer frames as janky on one tablet and 76% on the other. Dropping the resolution to 98% took that to about 2%:

  ```
  adb shell wm size 1175x1880
  adb shell wm density 235
  ```

  Density is taste: one tablet got `235`, the other `274`. The setting survived a reboot. To undo: `adb shell 'wm size reset; wm density reset'`. Why native is slow isn't known.

- **The time zone** came up as Pacific/Midway on the first tablet. Set it by hand in Settings → Date & time.
- **Widevine** read as `L3` in a browser's log. On stock, a third tablet reports `L1` through Android's own `MediaDrm` ([`tools/widevine_probe`](../tools/widevine_probe/)), with OEMCrypto API 16, but it isn't provisioned, so it couldn't open a session. That's two different instruments, so it isn't a before and after: the probe hasn't been run on a flashed tablet.
- Wifi, touch, sound, rotation and sleep got an "everything works" by hand, not a test each.

## Going back to stock

What was shown to work:

- Writing the stock `recovery.img` back with `samloader flash -p 38` while the bootloader was still locked (step 4)
- Writing it back from fastbootd after the GSI (step 9)

What was **not** done: putting the whole stock firmware back. No stock `super`, `boot` or bootloader files were ever flashed back onto either tablet, and neither was relocked. So there's a tool that can write to this tablet, and the stock files are intact on disk, but the full restore itself is untested.

## What broke along the way

- **The older Python `samloader` can't download any more.** Version 0.4 answered `Model or region not found (403)` for every model tried, and its download step crashed. samloader-rs is the one that worked.
- **`samloader flash -p recovery` fails on this tablet:**

  ```
  ERROR: File "RECOVERY" does not match any partition in the specified PIT.
  ```

  It looks for the name in capitals and the tablet's is lowercase. Using the partition's number (`-p 38`) gets round it.
- **After a failed flash, the next try can't connect:**

  ```
  ERROR: Unexpected handshake response!
  ```

  The Download Mode session is left half open. Hold Volume Down + Power for about 7 seconds to restart the tablet, then go back into Download Mode.
- **A flash that says nothing.** Run from a script with no real terminal behind it, samloader-rs exited `0` more than once without printing any progress, only `Ending session... Rebooting device...`, so there was no telling whether it wrote. Run again with `TERM=xterm-256color` and a terminal that has a size, it printed the progress bar and `recovery flash successful`. In a normal terminal window you'd expect to just see it, but that's the one way it wasn't run.

## Not tested

- A full restore to stock, and relocking the bootloader
- Any firmware build other than `X200XXS6DYG6`, and any region other than XAR
- The SM-X205
- Any other GSI
- Booting the GSI with TWRP left in place
- Flashing or disabling vbmeta
- Camera, MTP and encryption, each on its own
