# 当前 stable 候选

构建与下载时间：2026-07-31。

| 字段 | 值 |
| --- | --- |
| Actions run | `30609684589` |
| Commit | `31a65bfd3cc24f96541798302e8a67b574568eec` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8788269575` |
| Artifact bytes | `61,061,016` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `f251eee4574e331992b083869e812ae64f0b29b9051b7d7b0a6fba827d721171` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `3cbd9b9742b647321a0b2f84975b933a0d1eff40be4103bc9c41b9078be1f173` |
| SquashFS bytes_used | `30,962,690` |
| rootfs_data offset | `30,998,528` |
| p14 overlay capacity | `3,506,880,000` bytes |
| APK public-key SHA-256 | `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb` |

Artifact 已通过 `fetch-verify-actions-artifact.ps1`、`verify-stable-artifact.py`
和 `flash-stable-hil.ps1 -Mode LocalCheck`。验证覆盖 11 项 artifact 哈希、boot
metadata/DTB/IKCONFIG、p12/p14 边界、SquashFS、F2FS preinit、RNDIS、
OpenClash/Mihomo、`deadc0de` 和 overlay 容量。

该候选将 RNDIS gadget 调整到 netifd 启动后运行，并在 UDC 绑定后等待并拉起
`usb0`，再执行 `ifup lan`。GitHub build job 成功且 annotations 为 0；所有
GitHub Actions 依赖及 attestation 下游已使用 Node 24。

旧候选已完成 p14/p12 写入、回读哈希、GPT 与受保护分区不变验证，并确认首次
启动成功创建约 3.27 GiB F2FS overlay；但 RNDIS 枚举后链路未接通。当前候选
针对该问题重新构建，尚未获得写入授权，也未完成设备功能验收。
