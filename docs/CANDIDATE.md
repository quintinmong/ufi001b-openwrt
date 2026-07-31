# 当前 stable 候选

构建与下载时间：2026-07-31。

| 字段 | 值 |
| --- | --- |
| Actions run | `30636412439` |
| Commit | `0acd0d80594cc04ffab6821d835bb7515457469f` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8800636377` |
| Artifact bytes | `61,061,179` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `a8daf147af8683d1906b7ab5f8bcc315c1b555ca3b48502d10e57209da435545` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `b775bb87cd9beeb0e829f2ccb1143ee968b62cdd479eaac0d75312ae98ed83dd` |
| SquashFS bytes_used | `30,962,966` |
| rootfs_data offset | `30,998,528` |
| p14 overlay capacity | `3,506,880,000` bytes |
| APK public-key SHA-256 | `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb` |

Artifact 已通过 `fetch-verify-actions-artifact.ps1`、`verify-stable-artifact.py`
和 `flash-stable-hil.ps1 -Mode LocalCheck`。验证覆盖 11 项 artifact 哈希、boot
metadata/DTB/IKCONFIG、p12/p14 边界、SquashFS、F2FS preinit、RNDIS、
OpenClash/Mihomo、`deadc0de` 和 overlay 容量。

该候选显式加载 `usb_f_rndis`，首次绑定 UDC 使 MSM8916 内核实例化 `usb0`，
随后拉起接口并协调 LAN，再解绑/重绑 UDC，让 Windows 最终枚举已准备好的
RNDIS netdev。启动阶段会把 `operstate`、`carrier` 和失败步骤写入本机 overlay
的诊断文件。GitHub build job 成功且 annotations 为 0。

上一候选已完成 p14/p12 写入、回读哈希和写前受保护分区审计，并确认首次启动
成功创建约 3.27 GiB F2FS overlay；但 RNDIS 枚举后链路仍未接通。只读 overlay
分析确认 F2FS ready、S25 服务启用、br-lan/usb0 和 DHCP 配置正确。pre-bind
候选的持久诊断进一步证明该内核只在 UDC 绑定后创建 `usb0`。当前候选据此
改为两阶段绑定，用户已针对该 run 授权，待写前审计。
