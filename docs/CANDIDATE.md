# 当前 stable 候选

构建与下载时间：2026-08-03。当前设备运行的是 ROM 默认配置候选。

| 字段 | 值 |
| --- | --- |
| Actions run | `30759026223` |
| Commit | `20b4b667a5bb5a5c403f3744a286ec33bab6f0c5` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8839178394` |
| Artifact bytes | `61,238,677` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `8c6f10f66eefe4a38a50f5bc9258354bdd5aa845a42a945cd59f6fe8737dc85f` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `e760e2b325ef6df2e4ea8b2fc3d4b589a51626d8b0a816168b2eb9dd21b73b09` |
| SquashFS bytes_used | `31,140,468` |
| rootfs_data offset | `31,195,136` |
| p14 overlay capacity | `3,506,683,392` bytes |
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
设置 `network.lan.netmask='255.255.255.0'`；Wi-Fi 作为独立网络验证。

本候选已完成写前审计、p14/p12 写入和逐镜像回读，OverlayFS、RNDIS、DHCP、
LuCI 与 SSH 均通过。rmtfs 分区链接、`rpmsg_wwan_ctrl.ko` 自动加载和 rpmsg
hotplug fallback 已在实机生效；恢复仅本地持有的私有运行时固件后，MPSS、
WCNSS、QMI、ModemManager Modem3gpp 和 SIM LTE 注册均通过。Wi-Fi AP 已被
Windows 扫描到并完成客户端关联、DHCP、LuCI 和公网验证；`ctnet` IPv4
bearer、DNS 与 NAT 均已通过。断电持久化、9008 后正常启动和最终受保护分区
只读审计全部通过。
