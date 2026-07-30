# Goal 完成性审计

更新日期：2026-07-30。

## 已由离线证据证明

| 目标 | 证据 | 状态 |
| --- | --- | --- |
| OpenWrt 25.12 / Linux 6.12 | 固定 OpenWrt 25.12.5 commit；产物 buildinfo 与 kernel 6.12.94 | 通过 |
| MSM8916/UFI001B 目标 | msm89xx/msm8916 target、DTS、Android boot v0、eMMC p12/p14 规则 | 通过 |
| developer-ext4 | 历史 boot/rootfs 的尺寸、metadata、`e2fsck -fn`、SHA-256 通过，但嵌入 IKCONFIG 缺少 `DEVTMPFS/MMC_BLOCK`；修复版正在重建 | 未通过 |
| stable-squashfs | 独立干净构建；SquashFS 解包、rootfs_data 对齐与约 3.27 GiB overlay | 通过 |
| OpenClash/Mihomo | 0.47.133 / 1.19.29；独立 APK；AArch64 ELF；manifest 与根文件系统内容 | 通过 |
| 透明代理依赖 | dnsmasq-full、TUN、nft socket/TPROXY、策略路由相关包/配置 | 离线通过 |
| F2FS/zram | 内核模块、用户态工具、init/defaults 与 manifest | 离线通过 |
| 可维护更新 | lock 更新脚本、OpenClash/Mihomo 拆包、静态门禁 | 通过 |
| Actions | 修复 commit `2d388cf` 的 Static checks 已通过；developer Build firmware 正在运行 | 进行中 |
| APK 签名身份 | 外部 EC 私钥输入；artifact 只含公钥；双 profile/仓库 Variable 指纹门禁 | 通过 |
| 供应链材料 | buildinfo、manifest、APK 公钥、SPDX 2.3 SBOM、SHA256SUMS | 通过 |
| 安全边界 | 只允许 p12 boot 与 p14 rootfs；禁止 GPT、bootloader、modem/NV/校准进入写入或公开产物 | 通过 |

两套干净构建使用完全独立的源码树、toolchain、`staging_dir` 和 `build_dir`，
只共享经过 OpenWrt 哈希校验的 `dl` 下载缓存。developer 构建耗时约 44 分
53 秒；stable 在 `JOBS=3` 下耗时约 2 小时 44 分 25 秒。两套收集目录的
`SHA256SUMS` 均已重新执行并通过。

随后完成了差异归因和加固：源码准备强制补全 Git 历史，boot 中 vmlinux/
arm64 vDSO 及 stable libelf 的非确定性 GNU build-id 被关闭并加入最终镜像
检查。另在第三个全新构建根，以 stable 使用的同一外部 EC 密钥完成约 56 分
18 秒的 developer 全量构建；9 项哈希、ext4、公钥一致性和私钥禁入均通过。
EC/ECDSA 签名 nonce 具有随机性，因此这里不宣称 APK/rootfs 跨构建逐字节
相同；Release 身份由固定公钥指纹锁定，每次实际产物由 SHA-256 和 SBOM
描述；公开仓库额外生成 provenance，用户所有的私有仓库受 GitHub 平台限制。

本地交付目录保留历史产物用于审计：`out/developer-ext4` 已因缺少最终
root-mount 内核链而撤销，`out/stable-squashfs` 未进入本 Goal。复制到
Windows 文件系统后曾分别重新验证 9/11 项
`SHA256SUMS`。早期和中间候选被可恢复地归档到
`out/archive/20260729-before-reprofix`，避免实机阶段误选旧镜像。

本次独立干净构建的主要产物指纹：

| profile | 产物 | SHA-256 |
| --- | --- | --- |
| developer（历史，已撤销） | ext4 boot | `b7a23d0930e912b9f6373705e73f72f81344d08cbd35f6a8efe9d4f848025963` |
| developer（历史，已撤销） | ext4 rootfs | `a217323b2b8c3c3237b9a4caad12dd025126ca3c37000d31e0c13ecb79da2ae0` |
| stable | SquashFS boot | `8788b747eacdbbc5740d9a9e38748afa8745d6279eddbb4e294029d6bdc2742c` |
| stable | SquashFS rootfs | `cf039facb9edfacd9c1f49a867fe823cd8c42ffac40bf21a8253608a2393d774` |
| stable | OpenClash APK | `821a7e323b6ab183fadb5682e103bdb36f5743ab312e8a6d19c28de4c5081786` |
| stable | Mihomo APK | `d3d51ccd8c882457418b73e61ed51cf0c9acda48cf6f66f2d630bfba24c1894a` |
| both（历史，已撤销） | APK signing public key | `d9f66c0bb4bab16a28c2bb7019e0bb4c981775c0f76921e8074db58e25b486f4` |
| current developer Actions | APK signing public key | `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb` |

## 尚不能由离线构建证明

以下项目必须刷入真实 UFI001B 后验证，不能由编译成功替代：

1. aboot 实际启动 6.12 boot image、串口与冷启动；
2. eMMC p14 挂载、developer ext4 首启和 stable rootfs_data/F2FS overlay；
3. USB gadget（RNDIS/ECM/ADB 或维护串口）枚举；
4. WCNSS firmware、WCN36xx、Wi-Fi AP 和校准数据；
5. modem remoteproc、SIM 检测、运营商注册与 4G 数据；
6. LuCI、DNS、firewall4 和 IPv4 路由；
7. OpenClash TCP、UDP、DNS、QUIC 与 TUN/TPROXY 透明代理；
8. 重启、模拟断电、配置保留、恢复与回滚；
9. 30 分钟以上内存压力及 `dmesg` 无 remoteproc crash、eMMC I/O error、OOM kill。

## 当前结论

源码和配置覆盖根因已经修复，但当前修复版 Actions 仍在构建，尚无通过
嵌入 IKCONFIG 与 ext4 离线门禁的新 artifact；Goal 尚未完成，后续还必须
完成真实硬件 HIL。任何刷写都必须获得用户对新候选哈希的明确批准，并先从
developer-ext4 开始。不得写 GPT、bootloader、baseband、NV、IMEI、
modemst、fsc、fsg 或校准分区。
