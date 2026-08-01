# 当前 stable 候选

构建与下载时间：2026-07-31。

| 字段 | 值 |
| --- | --- |
| Actions run | `30697722579` |
| Commit | `e6af8aba986ca96eef85ecf8dcf20311c02df3c9` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8819870142` |
| Artifact bytes | `61,061,521` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `a8daf147af8683d1906b7ab5f8bcc315c1b555ca3b48502d10e57209da435545` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `dc1626226331e2cedaa615ab5a66fadec4f2547705e9e7774ab9b503cd0ceb9b` |
| SquashFS bytes_used | `30,963,378` |
| rootfs_data offset | `30,998,528` |
| p14 overlay capacity | `3,506,880,000` bytes |
| APK public-key SHA-256 | `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb` |

Artifact 已通过 `fetch-verify-actions-artifact.ps1`、`verify-stable-artifact.py`
和 `flash-stable-hil.ps1 -Mode LocalCheck`。验证覆盖 11 项 artifact 哈希、boot
metadata/DTB/IKCONFIG、p12/p14 边界、SquashFS、F2FS preinit、RNDIS、
OpenClash/Mihomo、`deadc0de` 和 overlay 容量。

该候选把 RNDIS 服务移至 `S90`，确保 netifd 已注册 LAN。现有 Overlay 若保留
旧 `S25` 链接，早期调用只记录 deferred 并退出；`S90` 再显式加载
`usb_f_rndis`，首次绑定创建 `usb0`，重启 LAN、创建 `br-lan`、入桥并最终
重绑 UDC。启动阶段会立即及延迟 15/60 秒记录 master、IPv4、carrier 和 RX/TX。
artifact 只含 `S90` 链接，GitHub build job 成功且没有 annotation。

上一候选已完成 p14/p12 写入和回读哈希。只读诊断显示即使重启 LAN，S25 时
ubus 仍返回 `Interface lan not found`，证明根因是 netifd 异步启动时序，不是
bridge 命令本身。当前候选将实际配置延后至 S90，并兼容旧 Overlay 的 S25
链接。用户已授权仅写本表候选的 p14/p12，待写前审计。
