# 当前 stable 候选

构建与下载时间：2026-08-02。

| 字段 | 值 |
| --- | --- |
| Actions run | `30728461724` |
| Commit | `c69ca33b20ab87fbe0b0efaa09d2c6d6df96d013` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8828953097` |
| Artifact bytes | `61,061,630` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `a8daf147af8683d1906b7ab5f8bcc315c1b555ca3b48502d10e57209da435545` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `3e1db1860c4e4fe0078b59b2575d41c4f3bc0e26196931e2ef9f00f9bf2ffae7` |
| SquashFS bytes_used | `30,963,414` |
| rootfs_data offset | `30,998,528` |
| p14 overlay capacity | `3,506,880,000` bytes |
| APK public-key SHA-256 | `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb` |

Artifact 已通过 `fetch-verify-actions-artifact.ps1`、`verify-stable-artifact.py`
和 `flash-stable-hil.ps1 -Mode LocalCheck`。验证覆盖 11 项 artifact 哈希、boot
metadata/DTB/IKCONFIG、p12/p14 边界、SquashFS、F2FS preinit、RNDIS、
OpenClash/Mihomo、`deadc0de` 和 overlay 容量。

该候选把 RNDIS 服务移至 `S90`，确保 netifd 已注册 LAN。现有 Overlay 若保留
旧 `S25` 链接，早期调用只记录 deferred 并退出；`S90` 再显式加载
`usb_f_rndis`，首次绑定创建 `usb0`，将 LAN 直接迁移到 `usb0`，执行 network
reload 后最终重绑 UDC。启动阶段会立即及延迟 15/60 秒记录 IPv4、carrier 和
RX/TX。artifact 只含 `S90` 链接，GitHub build job 成功且没有 annotation。

上一候选已完成 p14/p12 写入和回读哈希。管理 LAN 直接绑定 `usb0` 后，RNDIS
carrier 与 RX 已恢复，但运行时地址被配置成 `192.168.1.1/32`，导致没有到
Windows 端的直连返回路由。本候选在运行时迁移和首次启动默认配置中都显式
设置 `network.lan.netmask='255.255.255.0'`；Wi-Fi 将作为独立网络验证。尚待
本候选已完成写前审计、p14/p12 写入和逐镜像回读。OverlayFS、RNDIS、DHCP、
LuCI 与 SSH 已通过；HIL 进一步发现 rmtfs 分区链接和 RPMSG WWAN 模块打包
缺口，源码已修复，待下一次 Actions 产物取代本候选。
