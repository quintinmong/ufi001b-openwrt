# UFI001B OpenWrt firmware

[![Build](https://github.com/quintinmong/ufi001b-openwrt/actions/workflows/build.yml/badge.svg)](https://github.com/quintinmong/ufi001b-openwrt/actions/workflows/build.yml)
[![Static checks](https://github.com/quintinmong/ufi001b-openwrt/actions/workflows/static.yml/badge.svg)](https://github.com/quintinmong/ufi001b-openwrt/actions/workflows/static.yml)
[![Latest release](https://img.shields.io/github/v/release/quintinmong/ufi001b-openwrt)](https://github.com/quintinmong/ufi001b-openwrt/releases/latest)

## English overview

This repository builds a reproducible OpenWrt firmware for Qualcomm MSM8916
portable Wi-Fi devices using the UFI001B PCB. It pins all public inputs, checks
the p12/p14 write boundary, excludes device-unique and proprietary firmware,
and publishes manifests, build metadata, SHA-256 checksums, and an SPDX SBOM.

One maintainer-owned device is running the hardware-validated baseline in daily
use. This is real field evidence, but it is not presented as independent user
adoption. Start with the [latest release](https://github.com/quintinmong/ufi001b-openwrt/releases/latest),
[maintainer and ecosystem case](docs/OSS-MAINTAINER.md),
[governance](GOVERNANCE.md), [deployment evidence](docs/ADOPTION.md), and the
[flashing and recovery guide](docs/FLASH-AND-RECOVERY.md).

面向 Qualcomm MSM8916 / PCB `UFI001B` 随身 Wi-Fi 的可复现 OpenWrt 固件工程。
基线锁定为 OpenWrt `v25.12.5` 与 Linux `6.12`，唯一固件形态是标准
`SquashFS + OverlayFS`：只读 `/rom` 位于 p14 前部，持久化 F2FS
`rootfs_data` 使用 p14 剩余空间，`/` 为两者的 OverlayFS 合并视图。

## 项目价值

UFI001B 是一类资源受限、资料分散且刷写风险较高的 Qualcomm MSM8916 随身
Wi-Fi 设备。本项目把上游版本、补丁、构建输入和验证步骤固定下来，提供可审计、
可复现的固件流水线，减少依赖来历不明的预编译镜像。构建输出包含 manifest、
buildinfo、SHA-256 与 SPDX SBOM，并以实机 HIL 验证覆盖 RNDIS、Wi-Fi、LTE、
DNS/NAT、OverlayFS 和 LED。

项目由 [@quintinmong](https://github.com/quintinmong) 作为主要维护者持续维护。
问题、硬件兼容性反馈和改进建议请通过
[GitHub Issues](https://github.com/quintinmong/ufi001b-openwrt/issues) 提交；
贡献流程见 [CONTRIBUTING.md](CONTRIBUTING.md)，安全问题见
[SECURITY.md](SECURITY.md)，项目决策与发布职责见 [GOVERNANCE.md](GOVERNANCE.md)。

## 实机部署与采用情况

截至 2026-08-17，已有 1 台由主要维护者持有的 UFI001B 刷入本仓库 stable
构建并投入实际使用，维护者反馈当前体验良好。该设备已验证 RNDIS、Wi-Fi AP、
LTE、DHCP、DNS/NAT、OverlayFS 持久化、重启恢复和 LED 等关键功能。

这台设备属于维护者，不能代替独立第三方采用量；当前独立用户报告为 0。可追溯
构建、HIL 结果和计数口径见 [实机部署与采用证据](docs/ADOPTION.md)。使用本项目
刷机的用户可以通过 Field deployment report Issue 模板提交可公开核验的结果。

## 安全边界

工程只生成 p12 `boot.img` 和 p14 `rootfs.img`。构建、升级、Release 与 HIL
不得生成或写入 GPT、SBL、aboot、modem、`modemst1/2`、`fsc`、`fsg`、NV、
IMEI、EFS 或 Wi-Fi 校准分区。

全盘备份、Qualcomm 固件、校准数据、SIM 信息、代理订阅和密钥均由
`.gitignore` 排除，不得进入 Git、Actions artifact 或公开 Release。

## 许可证与再分发

除文件中另有标注外，本仓库由项目维护者原创的代码以
[`GPL-2.0-only`](LICENSE) 提供。仓库和固件包含采用其他许可证的独立上游
组件；顶层许可证不会重新许可这些组件，也不会给 GPL 代码附加“禁止商用”
等额外限制。逐项范围、版权和许可证见
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

Qualcomm firmware 二进制属于专有材料，不属于本项目 GPL 授权范围，也不得
进入公开 Git、Actions artifact 或 Release。公开二进制的对应源码提供方式见
[SOURCE-COMPLIANCE.md](SOURCE-COMPLIANCE.md)，完整固定来源见
[NOTICE.md](NOTICE.md)。

## 构建

构建必须在 Ubuntu/WSL2 的大小写敏感 Linux 文件系统中执行，`BUILD_ROOT`
不能位于 `/mnt/*`：

```sh
python3 scripts/verify-locks.py
python3 scripts/validate-layout.py
BUILD_ROOT="$HOME/ufi001b-openwrt-build" scripts/build.sh
```

产物位于 `out/stable-squashfs/`，包括配套的 Android boot v0 镜像、SquashFS
rootfs、manifest、buildinfo、SPDX SBOM、SHA-256、APK 签名公钥以及独立的
OpenClash/Mihomo APK。私钥永不进入产物。

公开 ROM 内置 LuCI 简体中文、有效的 OpenWrt
`aarch64_cortex-a53` 软件源以及 ModemManager/QMI/WWAN 能力，但不预设移动
WAN、APN、SIM 或运营商参数，也不分发 Qualcomm modem/WCNSS/NV blob。
LED 默认由内核事件驱动：红灯显示系统 heartbeat、蓝灯响应 Wi-Fi TX；固件
另含 xt_LED 能力，便于实机验证更精确的转发流量指示。

## 当前状态

stable Actions run `30759026223`（commit `20b4b667`，artifact
`8839178394`）已通过完整离线验证、授权写入、逐镜像回读和运行时 HIL。
SquashFS/F2FS OverlayFS、RNDIS、LuCI/SSH、中文、Wi-Fi、LTE、DNS/NAT 和 LED
均已验证。设备自己的 34 个私有运行时 firmware 文件、WAN/APN 与 Wi-Fi 密码
只恢复到设备 overlay，没有进入 ROM、Git、artifact 或 Release。

UFI001B 冷启动时 ModemManager 发现 modem 晚于 netifd；设备 overlay 因而安装
了一个最多运行 180 秒、WAN 在线即退出的补偿任务。它只在连接未处于 pending
状态时执行 `ifup wan`，已通过软件重启验证，不是常驻监控进程。
本候选写后 GPT 与受保护分区的最终 9008 只读审计也已通过。

详见[构建](docs/BUILD.md)、[架构](docs/ARCHITECTURE.md)、
[刷写与恢复](docs/FLASH-AND-RECOVERY.md)、[HIL 清单](docs/HIL-CHECKLIST.md)和
[状态](docs/STATUS.md)。中文/软件源/LED 构建的精确来源、哈希与 HIL 结果见
[ROM 默认配置候选](docs/ROM-DEFAULTS-CANDIDATE.md)。
