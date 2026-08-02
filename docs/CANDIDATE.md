# 当前 stable 候选

构建与下载时间：2026-07-31。

| 字段 | 值 |
| --- | --- |
| Actions run | `30705979030` |
| Commit | `3953aeac23605e7d11bd82027465ef47aca92f58` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8822507318` |
| Artifact bytes | `61,061,677` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `a8daf147af8683d1906b7ab5f8bcc315c1b555ca3b48502d10e57209da435545` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `43fd868e772cabeffe99381841d6caf922a3326c7312a10ffa060cf550aee93f` |
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

上一候选已完成 p14/p12 写入和回读哈希。S90 诊断证明 netifd 已注册 LAN，
但仍不会为运行时才出现的 USB port 实例化 `br-lan`。当前候选因此让管理 LAN
直接绑定 `usb0`，不再依赖单端口 bridge；Wi-Fi 将作为独立网络验证。用户已
授权仅写本表候选的 p14/p12，待写前审计。
