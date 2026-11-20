# partition map

from `GTA8WIFI_EUR_OPEN.pit` in the CSC bundle of `X200XXS6DYG6`, printed with `samloader print-pit -f` and tabled by [`tools/pit_table.py`](../tools/pit_table.py). sizes assume 512-byte blocks, which is what makes `recovery` come out at the 64 MiB its image is.

Entry Count: 58 | Project Name: COM_TAR2 | CPU/bootloader tag: SPRD8735

| # | id | partition | start block | blocks | MiB (512 B blocks) | flash file |
|---|---|---|---|---|---|---|
| 0 | 69 | splloader | 0 | 1024 | 0.5 | u-boot-spl-16k-sign.bin |
| 1 | 70 | PGPT | 0 | 34 | 0.0 | pgpt.img |
| 2 | 71 | pit | 34 | 24 | 0.0 | gta8.pit |
| 3 | 72 | MD5 | 58 | 1990 | 1.0 | md5.img |
| 4 | 1 | prodnv | 2048 | 20480 | 10.0 | - |
| 5 | 2 | miscdata | 22528 | 2048 | 1.0 | - |
| 6 | 3 | l_fixnv1 | 24576 | 4096 | 2.0 | - |
| 7 | 4 | l_fixnv2 | 28672 | 4096 | 2.0 | nvitem.bin |
| 8 | 5 | l_deltanv | 32768 | 2048 | 1.0 | deltanv.bin |
| 9 | 6 | l_runtimenv1 | 34816 | 4096 | 2.0 | - |
| 10 | 7 | l_runtimenv2 | 38912 | 4096 | 2.0 | - |
| 11 | 8 | misc | 43008 | 2048 | 1.0 | - |
| 12 | 9 | param | 45056 | 20480 | 10.0 | - |
| 13 | 10 | vendor_efs | 65536 | 32768 | 16.0 | vendor_efs.img |
| 14 | 11 | sec_efs | 98304 | 32768 | 16.0 | sec_efs.img |
| 15 | 12 | persist | 131072 | 16384 | 8.0 | persist.img |
| 16 | 13 | steady | 147456 | 8192 | 4.0 | steady.bin |
| 17 | 14 | persistent | 155648 | 2048 | 1.0 | - |
| 18 | 15 | pad | 157696 | 6144 | 3.0 | - |
| 19 | 16 | trustos | 163840 | 12288 | 6.0 | tos-sign.bin |
| 20 | 17 | trustos_bak | 176128 | 12288 | 6.0 | - |
| 21 | 18 | sml | 188416 | 2048 | 1.0 | sml-sign.bin |
| 22 | 19 | sml_bak | 190464 | 2048 | 1.0 | - |
| 23 | 20 | pm_sys | 192512 | 4096 | 2.0 | sharkl5pro_cm4.bin |
| 24 | 21 | teecfg | 196608 | 2048 | 1.0 | teecfg-sign.bin |
| 25 | 22 | teecfg_bak | 198656 | 2048 | 1.0 | - |
| 26 | 23 | tzar | 200704 | 8192 | 4.0 | - |
| 27 | 24 | uboot | 208896 | 10240 | 5.0 | lk-sign.bin |
| 28 | 25 | uboot_bak | 219136 | 2048 | 1.0 | - |
| 29 | 26 | vbmeta | 221184 | 2048 | 1.0 | vbmeta.img |
| 30 | 27 | vbmeta_bak | 223232 | 2048 | 1.0 | - |
| 31 | 28 | grd_fw | 225280 | 2048 | 1.0 | grd_fw.img |
| 32 | 29 | btd | 227328 | 2048 | 1.0 | - |
| 33 | 30 | uboot_log | 229376 | 32768 | 16.0 | - |
| 34 | 31 | logo | 262144 | 12288 | 6.0 | - |
| 35 | 32 | fbootlogo | 274432 | 8192 | 4.0 | - |
| 36 | 33 | bota | 282624 | 34816 | 17.0 | - |
| 37 | 34 | debug | 317440 | 20480 | 10.0 | - |
| 38 | 35 | gnssmodem | 337920 | 2048 | 1.0 | gnssmodem.bin |
| 39 | 36 | wcnmodem | 339968 | 20480 | 10.0 | EXEC_KERNEL_IMAGE.bin |
| 40 | 37 | boot | 360448 | 131072 | 64.0 | boot.img |
| 41 | 38 | recovery | 491520 | 131072 | 64.0 | recovery.img |
| 42 | 39 | dtbo | 622592 | 16384 | 8.0 | dtbo.img |
| 43 | 40 | socko | 638976 | 153600 | 75.0 | socko.img |
| 44 | 41 | odmko | 792576 | 49152 | 24.0 | odmko.img |
| 45 | 42 | metadata | 841728 | 32768 | 16.0 | - |
| 46 | 43 | vbmeta_system | 874496 | 2048 | 1.0 | vbmeta_system.img |
| 47 | 44 | vbmeta_vendor | 876544 | 2048 | 1.0 | vbmeta_vendor.img |
| 48 | 45 | pad2 | 878592 | 12288 | 6.0 | - |
| 49 | 46 | super | 890880 | 13164544 | 6428.0 | super.img |
| 50 | 47 | prism | 14055424 | 851968 | 416.0 | prism.img |
| 51 | 48 | optics | 14907392 | 40960 | 20.0 | optics.img |
| 52 | 49 | cache | 14948352 | 409600 | 200.0 | cache.img |
| 53 | 50 | omr | 15357952 | 49152 | 24.0 | omr.img |
| 54 | 51 | sysdumpdb | 15407104 | 20480 | 10.0 | - |
| 55 | 52 | l_agdsp | 15427584 | 12288 | 6.0 | AGCP_DSP.bin |
| 56 | 53 | userdata | 15439872 | 0 | 0.0 | userdata.img |
| 57 | 73 | SGPT | 61071327 | 33 | 0.0 | sgpt.img |
