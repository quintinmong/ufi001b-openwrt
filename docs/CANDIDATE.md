# 当前 stable 候选

构建与下载时间：2026-07-31。

| 字段 | 值 |
| --- | --- |
| Actions run | `30597258946` |
| Commit | `cd67dfe7f04516c94a9a451f8c47d4217fe8b55b` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8783573556` |
| Artifact ZIP bytes | `61,060,559` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `f251eee4574e331992b083869e812ae64f0b29b9051b7d7b0a6fba827d721171` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `2179a9464f6b45d7f20dab58be7b4eff64eaaf7300f8285896ccd8d85748d2b9` |
| SquashFS bytes_used | `30,962,562` |
| rootfs_data offset | `30,998,528` |
| p14 overlay capacity | `3,506,880,000` bytes |
| APK public-key SHA-256 | `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb` |

Artifact 已通过 `fetch-verify-actions-artifact.ps1`、`verify-stable-artifact.py`
和 `flash-stable-hil.ps1 -Mode LocalCheck`。验证覆盖 11 项 artifact 哈希、boot
metadata/DTB/IKCONFIG、p12/p14 边界、SquashFS、F2FS preinit、RNDIS、
OpenClash/Mihomo、`deadc0de` 和 overlay 容量。

这只是离线验证通过的 HIL 候选。设备不在手边，尚未授权或执行写入，也没有
完成冷启动和设备功能验收。
