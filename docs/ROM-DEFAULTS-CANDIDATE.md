# ROM 默认配置候选

构建与下载验证时间：2026-08-03。该候选用于固化中文、软件源和 LED 策略，
用户已于 2026-08-03 针对该精确候选授权刷写。p14 rootfs 与 p12 boot 已按
顺序写入并逐镜像回读验证；正常启动和运行时增量 HIL 尚待完成。

| 字段 | 值 |
| --- | --- |
| Static run | `30758993145`（success） |
| Build run | `30759026223`（success，3h 26m 9s） |
| Commit | `20b4b667a5bb5a5c403f3744a286ec33bab6f0c5` |
| Artifact | `ufi001b-stable-squashfs` |
| Artifact ID | `8839178394` |
| Artifact bytes | `61,238,677` |
| Build job | `91526146951`，annotations `0` |
| boot bytes | `6,113,280` |
| boot SHA-256 | `8c6f10f66eefe4a38a50f5bc9258354bdd5aa845a42a945cd59f6fe8737dc85f` |
| rootfs bytes | `31,195,648` |
| rootfs SHA-256 | `e760e2b325ef6df2e4ea8b2fc3d4b589a51626d8b0a816168b2eb9dd21b73b09` |
| SquashFS bytes_used | `31,140,468` |
| rootfs_data offset | `31,195,136` |
| p14 overlay capacity | `3,506,683,392` bytes |
| APK public-key SHA-256 | `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb` |

下载目录：
`out/actions/30759026223-rom-defaults/ufi001b-stable-squashfs`。
`fetch-verify-actions-artifact.ps1` 和 `verify-stable-artifact.py` 已完整通过，
验证 11 项文件哈希、签名公钥身份、boot/DTB/IKCONFIG、SquashFS、F2FS
preinit、`deadc0de`、p12/p14 边界和 OverlayFS 容量。

ROM 产物复核确认：

- manifest 包含 LuCI base、防火墙、包管理器三个简体中文包，默认语言脚本
  写入 `zh_cn`；
- 六个启用源均为官方 `aarch64_cortex-a53`，msm89xx target 与 OpenClash
  无效源保留为注释；
- ROM board/UCI 默认没有 WAN、ctnet、APN、SIM PIN 或运营商连接参数；
- manifest 与 SquashFS 均不含 `qcom-ufi001b-*`、`mba.mbn`、`modem.*`、
  `wcnss.*` 或 `WCNSS_qcom_wlan_nv.bin`；
- 红灯默认 `heartbeat`，蓝灯默认 `phy0tx`，不可见绿通道为 `none`；内核与
  用户态包含 `xt_LED`、`iptables-nft`、`iptables-mod-led` 供后续 HIL；
- ModemManager 与 LuCI ModemManager 协议能力仍在 ROM，但没有自动移动 WAN。

HIL 工具已固定到本候选。写前 GPT 与 `fsc/fsg/modemst1/modemst2` 审计通过；
p14 回读 SHA-256、SquashFS 与 `deadc0de` 通过，写 p12 前再次回读确认配套
rootfs，p12 回读 SHA-256 通过。除 p14/p12 外未写入其他分区。
