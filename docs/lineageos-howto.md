# LineageOS on the Tab A8 (SM-X200)

how a [LineageOS](https://lineageos.org) GSI went onto two Galaxy Tab A8s from a Linux PC, written from the logs of doing it.

**read this bit first.**

- this is what was done, twice, on two **SM-X200** (wifi) tablets, both on stock build `X200XXS6DYG6` / CSC `X200XAR6DYG6`, in October 2026. it's a record, not a promise. a different build, region or model (the X205 has a modem) might not behave the same.
- unlocking the bootloader **wipes the tablet**. back up first.
- every step below was either run on the PC with its output saved, or done by hand on the tablet and seen to work. the few that were only followed and never checked one by one are marked *(followed, not checked on its own)*.
- the full way back to stock was **not** tested. only a smaller piece of it was - see [going back to stock](#going-back-to-stock).
- the tablet side was my hands. the PC side was run by [Claude Code](https://github.com/anthropics/claude-code).

the order of the flash itself (TWRP, format data, fastbootd, system, then stock recovery back) comes from [yashjawale's notes](https://github.com/yashjawale/wiki/blob/main/docs/guides/flash-gsi-a8.md), which use Odin on Windows. this is the same route with Linux tools.

## what you need

| thing | what was used | where from |
|---|---|---|
| a Linux PC and a USB cable | Fedora-based | |
| `adb` and `fastboot` | android-tools 37.0.0 | the distro's package |
| a Samsung flasher | [samloader-rs](https://github.com/topjohnwu/samloader-rs) 2.2.0 (Apache-2.0) | its [GitHub release](https://github.com/topjohnwu/samloader-rs/releases/tag/2.2.0) |
| the stock firmware for *your* build | `X200XXS6DYG6`, region XAR | Samsung's servers, through samloader-rs |
| a TWRP recovery for the SM-X200 | `3.7.1_12-support x200-205 stable A14` (the version string inside the image), as `twrp.tar` | an XDA thread (`xdaforums.com/t/4763633/`) |
| the GSI | `LineageOS-22.2-20260105-VANILLA-EXT4-GSI` (Android 15) | MisterZtr's [SourceForge builds](https://sourceforge.net/projects/misterztr-gsi/files/LineageOS/) |

[Heimdall](https://git.sr.ht/~grimler/Heimdall) 2.2.2 was also used once, only to read the partition table. you can skip it.

samloader-rs's linux x86_64 zip should have the sha256 GitHub lists for it:

```
f6029dcce75b8a66acc1975529085c53903f7cdb35505e0ac0a973f2652480ff  samloader-v2.2.0-linux-x86_64.zip
```

### about the TWRP file

this is the part to think about. it's an unofficial build from a forum thread, and the thread posts no hash, so there's nothing to check it against. it gets flashed, used once to format data and reach fastbootd, and then the stock recovery goes back over it.

these are the hashes of the file that was used - they tell you if yours is the same file, not whether to trust it:

```
31f2838e943a86c6d60ed7336177565bbfd122897129e2706f4c671b13aead2c  twrp.tar
54464609773a8b0fc1616e5bc700d6da1f70bea167e0f8f0c6980dcaa2faef79  recovery.img   (the one file inside it, 67108864 bytes)
```

### the GSI file

```
ca2b46488ac0deace0a9fa4770998a97                                  LineageOS-22.2-20260105-VANILLA-EXT4-GSI.7z   (md5)
ad4d00d5b865c35964033c7ac8aafe74c67a1921b7fcd3f9491df643ac17fd8f  LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img  (sha256, 2623557632 bytes)
```

why this GSI fits this tablet at all is in the [teardown](../Tab-A8-teardown.md#why-a-gsi-fits).

## 1. back up

the unlock erases everything on the tablet. copy off anything you want before step 5.

## 2. get the stock firmware and pull out its recovery

you need the stock `recovery.img` twice: once for a test before unlocking, and once at the very end.

the firmware came down with samloader-rs. the exact command line wasn't kept in the log, this is its shape:

```
samloader download -m SM-X200 -r XAR -v '<your full version string>' -d firmware/
```

what it gave: `SM-X200_4_20250807222311_nm95ejh13u_fac.zip`, 4870006933 bytes, and `unzip -tq` on it said `No errors detected`.

unzip it, then take five images out of the AP bundle:

```
unzip SM-X200_4_20250807222311_nm95ejh13u_fac.zip
mkdir ap
tar -xf AP_X200XXS6DYG6_*.tar.md5 -C ap recovery.img super.img vbmeta.img vbmeta_system.img boot.img
```

only `recovery.img` is needed for the flash. for this build it's 67108864 bytes:

```
c8cfcb64a7330ae215a536e3dad9a982030e01e77f55faa4b6facefc97157589  recovery.img
```

[`tools/md5_check.py`](../tools/md5_check.py) checks each bundle against its own md5 line.

## 3. turn on OEM unlocking

on the tablet: Settings → Developer options → **OEM unlocking**, switch it on. (Developer options shows up after tapping the build number - that part is standard Android and wasn't logged.)

the switch only gives permission. nothing is unlocked or wiped yet. with USB debugging on, the PC can read it back:

```
adb shell getprop sys.oem_unlock_allowed
```

`1` means allowed.

## 4. meet Download Mode, and test a write while still locked

power the tablet off. hold **both volume keys** and plug the cable into the PC while holding them. you get a warning screen with three choices:

- **short press Volume Up** - continue into Download Mode. writes nothing.
- **long press Volume Up** - device unlock mode. this is the wipe. not yet.
- **Volume Down** - cancel.

short press. before unlocking, the Download Mode screen read `OEM LOCK` on and `KG STATE` completed. on the PC, `lsusb` shows the tablet as `04e8:685d`.

once Android is running with USB debugging on, you don't need the key combo any more:

```
adb reboot download
```

now the test: write the **stock** recovery back over itself. it changes nothing, and it proves the PC can write to this tablet before anything is wiped.

```
samloader flash -p 38 ap/recovery.img
```

it ends with `recovery flash successful` and the tablet reboots. the first time round the tablet was then booted into recovery (`adb reboot recovery`), the stock recovery menu showed, and it booted to Android fine.

`38` is the recovery partition's id in this tablet's partition table - it's in the [partition map](partition-map.md). check yours matches before using the number.

## 5. unlock the bootloader

**this wipes the tablet.**

1. power off.
2. hold both volume keys and plug in, same as before.
3. on the warning screen, **long press Volume Up**.
4. confirm on the next screen. the screen says which key - it wasn't written down.
5. the tablet wipes itself and restarts.

it sits on the Samsung logo long enough to look like a boot loop. it wasn't one, either time. from then on there's a warning at startup about the unlocked bootloader.

go through setup, turn USB debugging back on, and read the state:

```
adb shell 'getprop ro.boot.flash.locked; getprop ro.boot.verifiedbootstate; getprop ro.boot.warranty_bit; getprop sys.oem_unlock_allowed'
```

both tablets answered:

```
0
orange
0
1
```

`flash.locked` `0` and `orange` are the unlocked bootloader.

## 6. flash TWRP

```
adb reboot download
samloader flash --no-reboot -p 38 twrp/recovery.img
```

it ends with `recovery flash successful`. `--no-reboot` matters: the tablet stays in Download Mode, so stock Android doesn't get a chance to start first.

## 7. boot into TWRP

this one is about timing.

1. hold **Volume Down + Power** until the screen goes black.
2. the moment it does, switch to holding **Power + Volume Up**. keep holding through the warning screen until TWRP shows.
3. if TWRP asks about keeping system read-only, swipe to allow changes *(followed, not checked on its own)*.

## 8. format data, then go to fastbootd

in TWRP:

1. **Wipe** → **Format Data** → type `yes` *(followed, not checked on its own)*
2. **Reboot** → **Recovery**, and let it come back into TWRP *(followed, not checked on its own)*
3. **Reboot** → **Fastboot**

what was checked is where it ends up. on the PC:

```
fastboot devices
fastboot getvar is-userspace
fastboot getvar is-logical:system
```

`fastboot devices` should say `fastbootd`, `is-userspace` should be `yes` and `is-logical:system` should be `yes`. `product` reads `gta8wifi`.

## 9. flash the GSI, put the stock recovery back, reboot

```
fastboot flash system LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img
fastboot flash recovery ap/recovery.img
fastboot reboot
```

- the system image goes over in 10 sparse chunks and took about 99 seconds both times (`Finished. Total time: 99.590s` and `98.523s`).
- the second line puts the **stock** recovery back over TWRP. don't skip it - the notes this route comes from say the tablet won't boot the GSI with TWRP still there. that claim wasn't tested here, the stock recovery just went back both times.
- **no vbmeta image was flashed**, and nothing about verified boot was disabled. those three commands are all that got written in fastbootd.

## 10. first boot

both tablets booted LineageOS on the first try. the second one took about 2 minutes 20 seconds from `fastboot reboot` to boot-complete.

```
adb shell 'getprop ro.lineage.version; getprop ro.build.version.release; uname -r'
```

```
22.2-20260105-VANILLA-EXT4-GSI
15
4.14.199-29056031-abX200XXS6DYG6
```

so it's Android 15 on top of the stock kernel. the vendor partition is the stock one too, going by what was flashed - only `system` and `recovery` were written.

## after it boots

- **the launcher stutters at the native 1200x1920.** frame stats (`dumpsys gfxinfo`) put about 80% of app-drawer frames as janky on one tablet and 76% on the other. dropping the resolution to 98% took that to about 2%:

  ```
  adb shell wm size 1175x1880
  adb shell wm density 235
  ```

  density is taste - one tablet got `235`, the other `274`. the setting survived a reboot. to undo: `adb shell 'wm size reset; wm density reset'`. why native is slow isn't known.

- **the time zone** came up as Pacific/Midway on the first tablet. set it by hand in Settings → Date & time.
- **Widevine** read as `L3` in a browser. what it was on stock wasn't recorded, so that may or may not be a change.
- wifi, touch, sound, rotation and sleep got an "everything works" by hand, not a test each.

## going back to stock

what was shown to work:

- writing the stock `recovery.img` back with `samloader flash -p 38` while the bootloader was still locked (step 4)
- writing it back from fastbootd after the GSI (step 9)

what was **not** done: putting the whole stock firmware back. no stock `super`, `boot` or bootloader files were ever flashed back onto either tablet, and neither was relocked. so there's a tool that can write to this tablet, and the stock files are intact on disk, but the full restore itself is untested.

## what broke along the way

- **the older python `samloader` can't download any more.** version 0.4 answered `Model or region not found (403)` for every model tried, and its download step crashed. samloader-rs is the one that worked.
- **`samloader flash -p recovery` fails on this tablet:**

  ```
  ERROR: File "RECOVERY" does not match any partition in the specified PIT.
  ```

  it looks for the name in capitals and the tablet's is lowercase. using the partition's number (`-p 38`) gets round it.
- **after a failed flash, the next try can't connect:**

  ```
  ERROR: Unexpected handshake response!
  ```

  the Download Mode session is left half open. hold Volume Down + Power for about 7 seconds to restart the tablet, then go back into Download Mode.
- **a flash that says nothing.** run from a script with no real terminal behind it, samloader-rs exited `0` more than once without printing any progress, only `Ending session... Rebooting device...`, so there was no telling whether it wrote. run again with `TERM=xterm-256color` and a terminal that has a size, it printed the progress bar and `recovery flash successful`. in a normal terminal window you'd expect to just see it, but that's the one way it wasn't run.

## not tested

- a full restore to stock, and relocking the bootloader
- any firmware build other than `X200XXS6DYG6`, and any region other than XAR
- the SM-X205
- any other GSI
- booting the GSI with TWRP left in place
- flashing or disabling vbmeta
- camera, MTP and encryption, each on its own
