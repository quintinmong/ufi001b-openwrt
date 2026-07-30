# 实现状态与已知风险

更新日期：2026-07-29。

## 已完成

- 核对 UFI001B 3.61 GiB eMMC、p12/p14 边界和受保护分区；
- 保存已工作 boot image v0 的完整地址、页尺寸、cmdline 和哈希；
- 建立 OpenWrt 25.12.5 / Linux 6.12 msm89xx/msm8916 目标骨架；
- 移入 UFI001B 专用 DTS、Android boot image 构建规则；
- 建立 ext4 与 SquashFS 配置、p14 ext4 安全扩容服务；
- 建立 remoteproc/WCN36xx、QRTR/rmtfs/rpmsgexport、OpenClash/Mihomo 包；
- 建立不可变锁、分区策略、构建校验、SBOM/哈希和 Actions 门禁；
- 锁、布局、Python、Shell 语法及 OpenWrt `defconfig` 已通过本地检查；
- QRTR、rmtfs、rpmsgexport 和 mkbootimg 规范源码归档哈希已由 OpenWrt
  下载/校验逻辑验证；
- OpenWrt 全部 developer-ext4 构建输入已下载并校验；
- 非 root WSL 构建环境的 binutils、GCC 14.3、Linux headers 与 musl
  交叉工具链已从零构建成功；
- Linux 6.12.94 目标配置已由 OpenWrt `kernel_oldconfig` 刷新并固定为
  ARM64 小端，移除了 UFI001B 不需要的 KVM/虚拟化配置；
- Linux 6.12.94 已在全新 target clean 后以非 root WSL 环境完整编译成功；
- `Image.gz`（6,311,614 bytes）和 UFI001B DTB（49,694 bytes）已生成，
  DTB 的 model/compatible 已核对为 Handsome OpenStick UFI001B；
- ChipIdea UDC、WCN36xx、MSM8916 MPSS/WCNSS remoteproc、BAM-DMUX 等
  关键驱动均已生成预期 `.ko`，QRTR 核心已编入内核。
- developer-ext4 全量构建成功：boot 6,365,184 bytes，rootfs
  536,870,912 bytes；Android boot metadata、p12/p14 上限和 `e2fsck -fn`
  全部通过；
- stable-squashfs 全量构建及可复现性修正后的受影响目标重建成功：boot
  6,363,136 bytes，SquashFS rootfs 31,303,378 bytes；
- 稳定镜像的 SquashFS `bytes_used` 经 64 KiB 对齐后，`rootfs_data`
  起点为 31,326,208 bytes，p14 精确剩余 3,506,552,320 bytes（约 3.27 GiB）；
- 已解包验证 OpenClash 0.47.133、Mihomo 1.19.29 AArch64 ELF、F2FS
  工具、zram 服务和 UFI001B 默认配置；manifest 同时验证 nft TPROXY、
  TUN、dnsmasq-full、fstools/rootdisk 依赖；
- stable kernel config 已验证 `F2FS_FS=m`、`ZRAM=m`、`ZSMALLOC=m` 和
  `BLK_DEV_LOOP=y`；
- 两个正式输出目录均含 buildinfo、manifest、APK 签名公钥、SPDX 2.3 SBOM
  和 `SHA256SUMS`；稳定输出另含独立 OpenClash/Mihomo APK；全部哈希复核
  通过，且白名单确认没有私钥；
- Actions 的 build/static/update/release 工作流已经实现；第三方 Action 固定
  到完整 commit。非 PR 构建必须取得 `APK_SIGNING_KEY_PEM`，Release 要求
  两个 profile 的公钥一致且匹配 `APK_SIGNING_PUBLIC_KEY_SHA256`，并继续要求
  签名 tag、同 commit 的成功构建、人工环境审批和 artifact 哈希复核；
- 从零构建暴露的 Rust 1.94/LLVM 内存压力已转成仓库级门禁：稳定构建先
  生成 bootstrap 配置，再把 Rust 内层并发限制为最多 4。
- 已按 GitHub Actions 矩阵语义完成两套互不复用 toolchain、`staging_dir`
  或 `build_dir` 的独立干净构建；两者只复用了经校验的 `dl` 下载缓存：
  - `developer-ext4`：约 44 分 53 秒，boot 6,365,184 bytes，rootfs
    536,870,912 bytes，8 项 SHA-256 全部通过，`e2fsck -fn` 通过；
  - `stable-squashfs`：约 2 小时 44 分 25 秒（`JOBS=3`），boot
    6,363,136 bytes，rootfs 31,303,466 bytes，10 项 SHA-256 全部通过，
    内容级校验再次确认 `rootfs_data` 偏移 31,326,208 bytes、overlay 余量
    3,506,552,320 bytes，以及 OpenClash/Mihomo/F2FS/zram/TPROXY/TUN；
- 对镜像差异做了逐层定位：boot 的 DTB 完全相同，差异只来自 vmlinux 与
  arm64 vDSO 的 GNU build-id；rootfs 的额外差异来自浅克隆导致的
  `base-files` commit count、libelf build-id，以及 APK EC/ECDSA 随机签名。
  源码准备现会补全 Git 历史（`base-files=1711~f5dae5ece4`），并以仓库补丁
  关闭 boot/libelf 非确定性 build-id；校验器会直接检查最终镜像内容；
- 另以全新源码/toolchain/build/staging 根、同一外部 EC 密钥完成一次
  developer-ext4 全量构建，耗时约 56 分 18 秒：boot 6,365,184 bytes、rootfs
  536,870,912 bytes，9 项 `SHA256SUMS`、`e2fsck -fn`、boot build-id、公钥
  一致性和私钥禁入全部通过；公钥 SHA-256 为
  `d9f66c0bb4bab16a28c2bb7019e0bb4c981775c0f76921e8074db58e25b486f4`；
  这是历史构建身份，相关私钥现已撤销并删除；
- EC/ECDSA 的随机 nonce 意味着 APK 及包含 APK 数据库的 rootfs 不承诺跨构建
  逐字节相同。当前已证明并自动执行的是锁定输入、固定公钥身份、镜像内容
  约束，以及对每次实际产物生成哈希和 SBOM；公开仓库额外生成 provenance。
- 已把上述最新 developer/stable 产物复制到规范的 `out/<profile>`，复制后
  再次逐项执行 `SHA256SUMS` 并全部通过；四个早期/中间目录完整移动到
  `out/archive/20260729-before-reprofix/`，未删除。`out/CANDIDATE.md` 明确
  标记 developer 为唯一第一阶段候选、stable 尚不可刷，并记录候选哈希和
  p12/p14 安全边界。

## 2026-07-29 首轮 developer HIL

- 用户明确批准后，仅写入 p14 `rootfs` 和 p12 `boot`；两者均完整回读，
  大小和 SHA-256 与候选产物逐字节一致，ext4 `e2fsck -fn` 通过；
- 刷写前后主/备 GPT 完全一致；`fsc`、`fsg`、`modemst1`、`modemst2`
  的刷前/刷后快照逐字节一致；
- 正常重插并等待超过 3 分钟后，Windows 未枚举 USB gadget、ADB、串口或
  未知设备，`192.168.1.1`/`192.168.68.1` 均不可达，因此阶段 A 未通过；
- 与已知可启动 HandsomeMod UFI001B DTB 对比后，发现旧候选错误使用
  PM8916 VBUS role switch；板级实际连接是 GPIO110 USB-ID extcon。源码现已
  改回该拓扑并启用 `CONFIG_EXTCON_USB_GPIO=y`，同时加入最终 DTB 自动门禁；
- 失败候选已完整归档。GPIO110 修复版已由私有 GitHub Actions 干净构建，
  artifact 内全部哈希、公钥、boot metadata、DTB token 和 ext4 `e2fsck -fn`
  已在本地复核；尚待第二轮仅 p12 boot HIL，p14 rootfs 暂不重复写入。

## 2026-07-30 私有 Actions 修复候选

- 私有仓库 `quintinmong/ufi001b-openwrt` 已创建并推送；Static checks 通过；
- developer 构建、签名指纹复核和 artifact 上传成功。boot SHA-256 为
  `a1265330c1f8ad892dcd830b0f68689f255d3c3884bb2fc275dbf3581188507e`，
  rootfs SHA-256 为
  `8874bde7229c5076fe5c00fa27fdaf57a32abec4629e0bb7139781db33687b54`；
- 活动 APK 公钥 SHA-256 为
  `cdca512810c06a6136ca81998d9d2ce1416b72d30fec67dee81fbb34c9447ecb`；
  两把可能暴露的旧私钥已删除，不再作为可信签名身份；
- GitHub 对用户所有的私有仓库不提供 artifact attestation，导致该次 job
  仅在最终 provenance 步骤失败；固件和 artifact 已成功。工作流现仅在
  公开仓库运行 attestation，私有仓库继续强制 SHA-256、SBOM、buildinfo 和
  固定 APK 公钥指纹。

## 2026-07-30 第二轮 developer boot HIL

- 当前设备通过 `emmcdl` 读取的 GPT 与批准的 14 分区 UFI001B 布局一致；
- 仅向 p12 `boot` 的 LBA 526336–538767 写入 GPIO110 USB-ID 修复版，
  共 12,432 个扇区；p14 `rootfs` 未重复写入；
- 随后完整读取 64 MiB `boot` 分区，前 6,365,184 字节 SHA-256 为
  `a1265330c1f8ad892dcd830b0f68689f255d3c3884bb2fc275dbf3581188507e`，
  与 Actions 候选完全一致；
- 本轮命令未以 GPT、rootfs、基带、NV 或校准分区为写入目标；正常启动、
  USB gadget 和网络枚举仍待重插验证；
- 正常重插超过 3 分钟后仍无 USB gadget、RNDIS、未知设备或管理地址响应。
  离线复核发现设备上的首轮 rootfs 内核 vermagic 为
  `144c65224430cca527a5de559fa687e2`，修复版 boot 对应 rootfs 的 vermagic 为
  `f81efc174e450d3050da454e58dd5749`。两者不兼容，旧 rootfs 的 USB/Wi-Fi
  内核模块无法作为修复版 boot 的有效配套模块；在写入成对 rootfs 前，
  本轮不能用于判断 GPIO110 修复本身是否有效。

## 2026-07-30 成对 developer rootfs HIL

- 用户另行明确批准后，仅向 p14 `rootfs` 的 LBA 659456 起写入同一次
  Actions 构建的 512 MiB ext4 镜像；设备报告写入 1,048,576 个扇区完成；
- 从相同起点回读的数据前 536,870,912 字节 SHA-256 为
  `8874bde7229c5076fe5c00fa27fdaf57a32abec4629e0bb7139781db33687b54`，
  与候选完全一致；回读镜像的 `e2fsck -f -n` 五阶段检查退出码为 0；
- 刷后 GPT 的 p12/p14 起止和容量未变化；`fsc`、`fsg`、`modemst1`、
  `modemst2` 与首轮刷后全分区快照及原始设备专属备份有效前缀均一致；
- p12 boot 与 p14 rootfs 现为同一次 Actions 构建、相同 vermagic 的有效配对；
  正常重插超过 3 分钟后，设备退出 9008，但 Windows 未观察到原 USB 端口
  的任何设备枚举，`192.168.1.1`/`192.168.68.1` 均不可达。阶段 A 仍未通过；
- 当前已排除 p12/p14 写入不一致、GPT 改动、ext4 元数据损坏和内核模块
  vermagic 不匹配。重新进入 9008 只读 p14 超级块后，block count 仍为
  131072、mount count 为 0、last mount time 为 `never`，证明 rootfs 从未挂载；
- 最终 developer 内核的解压内容包含 `sdhci_msm`，但不包含工作参考内核中
  存在的 `mmcblk` 字符串；目标配置也确实缺少 `CONFIG_MMC_BLOCK=y`。因此
  控制器驱动存在，但内核不能创建 `/dev/mmcblk0p14`，会在 cmdline 的
  `rootwait` 永久等待。这与全部 HIL 现象一致；
- 源配置现已明确加入 `CONFIG_BLOCK=y`、`CONFIG_EFI_PARTITION=y` 和
  `CONFIG_MMC_BLOCK=y`；构建校验及静态工作流新增完整 root-mount 内建链
  门禁，避免再次产出无 mmc block 根设备的镜像；
- Actions 第 6 次构建实际完成了内核和两张镜像，但产物校验发现最终配置中
  `DEVTMPFS` 仍被关闭，因此没有上传 artifact。根因是 OpenWrt 顶层
  `CONFIG_KERNEL_*` 与内核包元数据晚于 target 配置覆盖；两个 profile 已
  启用 `CONFIG_KERNEL_DEVTMPFS`/`CONFIG_KERNEL_DEVTMPFS_MOUNT`，设备包已
  选择 `kmod-mmc`。本地按 Actions 相同的 kconfig 合并流程确认最终
  `DEVTMPFS`、`MMC_BLOCK`、GPT、ext4 和 SDHCI_MSM 均为 `y`。

## 当前门禁

- 本地源码、锁、布局、Python、Shell、YAML、危险文件、APK 公钥和两类镜像
  内容检查已通过；
- 两个 profile 的原始源码版本已完成本地独立干净构建；远端 GitHub-hosted
  runner 已完成 GPIO110 修复版 developer 构建和 artifact 上传；
- 首轮和 GPIO110 修复版 HIL 已完成安全写入与回读，但因缺少内建
  `MMC_BLOCK` 未通过根挂载门禁；stable 继续禁止刷写；
- 下一阶段由 GitHub Actions 重建 developer，必须先证明最终解压内核含
  `mmcblk` 且最终 kernel config 含完整 root-mount 链，再申请下一轮 HIL。

## 尚未完成

- `MMC_BLOCK` 修复版 developer 尚待 Actions 构建和离线验证；
- Wi-Fi、modem、USB 和 ext4 首启尚未在修复后的 6.12 镜像上实机验证；
- stable-squashfs、rootfs_data 与 OpenClash 尚未进行 HIL；
- 私有 GitHub 仓库与远端 Actions 已建立；未创建 Release；
- 私有 Qualcomm firmware 的本地 HIL 注入和许可证审查未放行。

## 主要技术风险

1. MSM8916 6.12 remoteproc/WCNSS 的编译、kmod 打包与 rootfs 安装已证明，
   但固件加载、SIM/4G 注册、Wi-Fi AP 和 USB gadget 仍必须实机证明；
2. 上游 msm8916-mainline defconfig 仍较宽，完成点亮后需裁剪无关显示、
   音频、摄像头驱动，重新验证 boot 大小与内存；
3. WCN36xx 使用内核内置 mac80211/cfg80211 与 OpenWrt 用户态组合，需
   编译和 AP 模式实测；
4. modem 固件和设备唯一 NV/校准的许可证与注入方式必须保持私有；
5. 394 MiB RAM 下 OpenClash/Geo 数据/zram 预算需要 24 小时压力测试。
