# UFI001B OpenWrt firmware

面向 Qualcomm MSM8916 / PCB `UFI001B` 随身 Wi-Fi 的可复现 OpenWrt
固件工程。基线锁定为 OpenWrt `v25.12.5` 与 Linux `6.12`，目标是保留
USB、WCN36xx Wi-Fi 和 MSM8916 modem 的同时，提供完整的 OpenClash
nftables/TPROXY/TUN 能力。

设计依据见
[`../UFI001B-OpenWrt25.12-OpenClash固件与GitHub-Actions设计.md`](../UFI001B-OpenWrt25.12-OpenClash固件与GitHub-Actions设计.md)。

## 安全边界

本工程只生成 `boot.img` 和 `rootfs.img`，对应现有 GPT 中的 p12 与 p14。
构建、升级及 Release 流程均不得生成或写入 GPT、SBL、aboot、modem、
`modemst1/2`、`fsc`、`fsg`、NV、IMEI 或 Wi-Fi 校准分区。

全盘备份、Qualcomm 固件、校准数据、订阅和密钥都是私有输入，已被
`.gitignore` 排除，禁止进入 Actions artifact 或公开 Release。

## 构建产物

- `developer-ext4`：512 MiB 可写 ext4，首启只在确认根设备为 p14 后执行
  `resize2fs`，用于第一阶段硬件点亮和调试；
- `stable-squashfs`：只读 SquashFS；OpenWrt `fstools/rootdisk` 使用 p14
  剩余区域建立 `rootfs_data`，最终根目录为 OverlayFS；
- 每种配置都有 Android boot image v0、rootfs、包清单、构建信息、SPDX
  SBOM、SHA-256 和 APK 签名公钥；私钥永不进入产物；
- 正式配置额外包含独立的 `luci-app-openclash` 与 `mihomo-openclash` APK。

## 快速开始

构建必须在 Ubuntu 24.04 或 WSL2 的大小写敏感 Linux 文件系统中进行；
仓库可以位于 Windows 盘，但 `BUILD_ROOT` 不能位于 `/mnt/*`。

```sh
python3 scripts/verify-locks.py
python3 scripts/validate-layout.py
BUILD_ROOT="$HOME/ufi001b-openwrt-build" scripts/build.sh developer-ext4
BUILD_ROOT="$HOME/ufi001b-openwrt-build" scripts/build.sh stable-squashfs
```

PR 可使用构建时生成的一次性 APK 密钥；分支构建和 Release 必须通过
`APK_SIGNING_KEY_FILE=/安全路径/private-key.pem` 使用持久 EC 密钥。GitHub
配置方法与公钥指纹门禁见[构建与流水线](docs/BUILD.md)。

任何已有的 `out/<profile>` 会令收集阶段失败，避免旧产物混入新构建。
请把旧目录另行归档后再运行，而不要覆盖或混用。

## 文档

- [架构与文件系统](docs/ARCHITECTURE.md)
- [构建与流水线](docs/BUILD.md)
- [来源、锁定与私有固件](docs/PROVENANCE.md)
- [刷写与恢复](docs/FLASH-AND-RECOVERY.md)
- [升级与回滚](docs/UPGRADE.md)
- [OpenClash 配置与独立更新](docs/OPENCLASH.md)
- [实机验收清单](docs/HIL-CHECKLIST.md)
- [实现状态和已知风险](docs/STATUS.md)
- [Goal 完成性审计](docs/COMPLETION-AUDIT.md)

## 当前门禁

developer-ext4 与 stable-squashfs 已在两个相互独立的干净构建根完成本地
全量构建、文件系统/内容校验、签名公钥、SBOM 和哈希校验；boot 与稳定版
libelf 中的非确定性 GNU build-id 也已移除并纳入自动门禁；详见
[实现状态](docs/STATUS.md)和[完成性审计](docs/COMPLETION-AUDIT.md)。这些仍是未做 HIL 的
候选产物，没有任何生成镜像被批准刷入实机。首次刷写必须是
`developer-ext4`，且必须由用户核对板型、备份和哈希后当次明确批准。
Actions 不接触真实设备，也不会自动创建 Release。

本机最新离线验收产物与哈希见 [`out/CANDIDATE.md`](out/CANDIDATE.md)；其中
只有 `developer-ext4` 可在获得当次明确批准后进入第一阶段 HIL，归档候选和
`stable-squashfs` 当前均不得刷写。
