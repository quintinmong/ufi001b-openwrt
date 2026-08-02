# UFI001B OpenWrt firmware

面向 Qualcomm MSM8916 / PCB `UFI001B` 随身 Wi-Fi 的可复现 OpenWrt 固件工程。
基线锁定为 OpenWrt `v25.12.5` 与 Linux `6.12`，唯一固件形态是标准
`SquashFS + OverlayFS`：只读 `/rom` 位于 p14 前部，持久化 F2FS
`rootfs_data` 使用 p14 剩余空间，`/` 为两者的 OverlayFS 合并视图。

## 安全边界

工程只生成 p12 `boot.img` 和 p14 `rootfs.img`。构建、升级、Release 与 HIL
不得生成或写入 GPT、SBL、aboot、modem、`modemst1/2`、`fsc`、`fsg`、NV、
IMEI、EFS 或 Wi-Fi 校准分区。

全盘备份、Qualcomm 固件、校准数据、SIM 信息、代理订阅和密钥均由
`.gitignore` 排除，不得进入 Git、Actions artifact 或公开 Release。

## 授权与使用声明

本项目沿用 OpenStick README 的使用声明：项目公开可见，但禁止商用。商用
行为包括售卖原本免费开放下载的系统镜像及衍生品、收费发布相关构建产物，
以及大规模批量售卖搭载 OpenStick Linux 的设备。涉及 Qualcomm firmware 的
二进制另受 QTI 原许可证约束；本仓库不保存或公开分发这些二进制。完整来源
和固定上游版本见 [NOTICE.md](NOTICE.md)。

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

stable Actions run `30597258946` 已成功，artifact `8783573556` 通过完整离线
验证和 HIL `LocalCheck`。精确尺寸、哈希与 OverlayFS 布局见
[当前候选](docs/CANDIDATE.md)。设备目前不在手边，因此候选尚未获得当次刷写
授权，也没有完成 HIL。

详见[构建](docs/BUILD.md)、[架构](docs/ARCHITECTURE.md)、
[刷写与恢复](docs/FLASH-AND-RECOVERY.md)、[HIL 清单](docs/HIL-CHECKLIST.md)和
[状态](docs/STATUS.md)。中文/软件源/LED 新构建的精确来源与哈希见
[ROM 默认配置候选](docs/ROM-DEFAULTS-CANDIDATE.md)；该候选尚未获准刷写。
