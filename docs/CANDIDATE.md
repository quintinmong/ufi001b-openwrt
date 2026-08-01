# 当前 stable 候选

构建与下载时间：2026-07-31。

| 字段 | 值 |
| --- | --- |
| Actions run | `30673711516` |
| Commit | `065d884b722591ebb92695160fe7f27b0ed2abb6` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8812103488` |
| Artifact bytes | `61,061,290` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `a8daf147af8683d1906b7ab5f8bcc315c1b555ca3b48502d10e57209da435545` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `4ce132c8d8d8c4b35932140324e6127ada897b51c2b4e218d0ef000697e78922` |
| SquashFS bytes_used | `30,963,166` |
| rootfs_data offset | `30,998,528` |
| p14 overlay capacity | `3,506,880,000` bytes |
| APK public-key SHA-256 | `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb` |

Artifact 已通过 `fetch-verify-actions-artifact.ps1`、`verify-stable-artifact.py`
和 `flash-stable-hil.ps1 -Mode LocalCheck`。验证覆盖 11 项 artifact 哈希、boot
metadata/DTB/IKCONFIG、p12/p14 边界、SquashFS、F2FS preinit、RNDIS、
OpenClash/Mihomo、`deadc0de` 和 overlay 容量。

该候选显式加载 `usb_f_rndis`，首次绑定 UDC 使 MSM8916 内核实例化 `usb0`，
随后重启 LAN，使 netifd 在 `usb0` 已存在时创建 `br-lan`，再显式入桥并解绑/
重绑 UDC，让 Windows 最终枚举已准备且已入桥的 RNDIS netdev。启动阶段会立即
及延迟 15/60 秒把 master、IPv4、carrier、RX/TX 和失败步骤写入本机 overlay。
GitHub build job 成功且没有 annotation。

上一候选已完成 p14/p12 写入和回读哈希。只读诊断精确停在
`initial-bind br-lan unavailable`：`ifup lan` 对已标记为 up、但启动时缺少
`usb0` 的 LAN 没有重建 bridge，脚本因此未执行最终 UDC 重绑。当前候选在
首次临时绑定创建 `usb0` 后明确执行 `ifdown lan`/`ifup lan`，再等待并加入
`br-lan`。本候选尚未获得写入授权。
