# 当前 stable 候选

构建与下载时间：2026-07-31。

| 字段 | 值 |
| --- | --- |
| Actions run | `30650713990` |
| Commit | `c6490f91b248e37f72cd4e818b239445890f98e1` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8805527163` |
| Artifact bytes | `61,061,467` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `a8daf147af8683d1906b7ab5f8bcc315c1b555ca3b48502d10e57209da435545` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `63f5ce6f479ed62b1875fdfa8ab8e6ba9c85539550ae1cc262957cbe5a03ddae` |
| SquashFS bytes_used | `30,963,186` |
| rootfs_data offset | `30,998,528` |
| p14 overlay capacity | `3,506,880,000` bytes |
| APK public-key SHA-256 | `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb` |

Artifact 已通过 `fetch-verify-actions-artifact.ps1`、`verify-stable-artifact.py`
和 `flash-stable-hil.ps1 -Mode LocalCheck`。验证覆盖 11 项 artifact 哈希、boot
metadata/DTB/IKCONFIG、p12/p14 边界、SquashFS、F2FS preinit、RNDIS、
OpenClash/Mihomo、`deadc0de` 和 overlay 容量。

该候选显式加载 `usb_f_rndis`，首次绑定 UDC 使 MSM8916 内核实例化 `usb0`，
随后显式把动态创建的接口加入 `br-lan`，再解绑/重绑 UDC，让 Windows 最终
枚举已准备且已入桥的 RNDIS netdev。启动阶段会立即及延迟 15/60 秒把 master、
IPv4、carrier、RX/TX 和失败步骤写入本机 overlay。GitHub build job 成功且没有
annotation。

上一候选已完成 p14/p12 写入、回读哈希和写前受保护分区审计，并确认首次启动
成功创建约 3.27 GiB F2FS overlay。两阶段 UDC 绑定已让 Windows 稳定得到
426 Mbps carrier，但 DHCP、ARP 和静态 IPv4 仍不通；只读 overlay 分析确认
LAN 配置仍指向单端口 `br-lan`，而旧诊断没有记录 `usb0` 的 master。当前候选
据此在接口创建后显式入桥。用户已针对本表精确 run 授权，仅待写前审计。
