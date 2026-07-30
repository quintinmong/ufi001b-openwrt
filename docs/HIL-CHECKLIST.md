# UFI001B 实机 HIL 验收清单

每一项记录镜像 SHA-256、日期、测试人、串口/系统日志和结论。任何关键项
失败都停止进入 stable 阶段。

## 阶段 A：developer-ext4 最小启动

- [x] 用户核对 UFI001B、私有全盘备份和 p12/p14 产物后批准刷写；
- [x] Android boot header、DTB compatible 和 cmdline 与预期一致；
- [ ] 3 分钟内进入系统，无 kernel panic、watchdog loop；
- [ ] `/` 来自 `/dev/mmcblk0p14` 且为 ext4；
- [ ] guarded resize 只扩 p14，重启不重复执行；
- [x] eMMC 分区起止 LBA 与刷前完全相同；
- [ ] USB gadget 出现，PC 获得地址，SSH/LuCI 可达；
- [ ] reset、三色 LED、时区和冷启动正常。

首轮结果（2026-07-29）：p12/p14 回读、GPT 和受保护分区审计通过；正常
重插超过 3 分钟无 USB 枚举或网络，阶段 A 停止。已定位并修正 GPIO110
USB-ID extcon，等待新 developer boot 进行第二轮 HIL。

第二轮写入结果（2026-07-30）：只写 p12 `boot`，写入范围为 LBA
526336–538767；完整读取 64 MiB p12 后，候选长度内 SHA-256 为
`a1265330c1f8ad892dcd830b0f68689f255d3c3884bb2fc275dbf3581188507e`，
与 Actions 候选一致。p14 及受保护分区未作为写入目标；等待正常重插后的
启动、USB gadget 和网络验证。正常重插超过 3 分钟仍无枚举或网络；随后
确认旧 p14 rootfs 的内核 vermagic `144c65224430cca527a5de559fa687e2`
与新 boot 配套 rootfs 的 `f81efc174e450d3050da454e58dd5749` 不同。
因此本次“新 boot + 旧 rootfs”不是有效配对，阶段 A 结论保持未定，等待
获得明确批准后写入同一 Actions 构建的 developer rootfs。

成对写入结果（2026-07-30）：用户另行批准后仅写 p14 `rootfs`，设备报告
从 LBA 659456 写入 1,048,576 个扇区完成。相同起点的回读数据前 512 MiB
SHA-256 为 `8874bde7229c5076fe5c00fa27fdaf57a32abec4629e0bb7139781db33687b54`；
`e2fsck -f -n` 退出码为 0。刷后 GPT 不变，四个受保护分区与首轮全分区
快照及原始专属备份有效前缀一致。当前 p12/p14 已是同一 Actions 构建，
正常重插超过 3 分钟后设备退出 9008，但无 USB 枚举或管理地址响应；阶段 A
保持失败。通过 EDL 只读 p14 超级块后，block count 仍为 131072、mount
count 为 0、last mount time 为 `never`，证明 rootfs 从未挂载。最终内核
包含 `sdhci_msm` 但不含 `mmcblk`，并确认源配置缺少 `CONFIG_MMC_BLOCK=y`；
内核因而无法创建 `/dev/mmcblk0p14`，在 `rootwait` 等待。源码与构建门禁已
补齐 block/GPT/MMC block/ext4 根挂载链，等待 Actions 重建后再申请 HIL。

Actions 第 6 次重建（commit `57c3401`）已完成内核、boot 和 512 MiB ext4
rootfs，但最终产物校验拒绝上传：实际构建配置仍缺少 `DEVTMPFS`。进一步
复现 OpenWrt 的 `.config.target` + `.config.override` 合并后确认，target
内核片段会被顶层 `CONFIG_KERNEL_DEVTMPFS` 和未选择的 `kmod-mmc` 包元数据
覆盖。现已在两个 profile 启用 devtmpfs 顶层开关，并把 `kmod-mmc` 加入
UFI001B 设备包；本地以相同合并命令验证最终 config-set 中
`DEVTMPFS/MMC_BLOCK/GPT/EXT4/SDHCI_MSM` 全部为内建。等待新 Actions 产物，
此前镜像不得再次刷写。

## 阶段 B：无线和 modem

- [ ] WCNSS remoteproc 启动，WCN36xx 加载；
- [ ] Wi-Fi MAC、校准、2.4 GHz 扫描/AP、WPA2 和断电恢复正常；
- [ ] MPSS remoteproc、QRTR、rmtfs、rpmsgexport、BAM-DMUX/rmnet 正常；
- [ ] ModemManager 出现 3GPP 接口，不再报告 `No such interface`；
- [ ] SIM、IMEI、运营商注册、APN、IPv4 上网和重拨正常；
- [ ] modemst/fsc/fsg/NV/校准分区哈希或只读抽查未变化。

## 阶段 C：stable-squashfs / overlay

- [ ] `/rom` 为只读 SquashFS；
- [ ] `/overlay` 为 p14 剩余空间上的可写 rootfs_data；
- [ ] `/` 类型为 overlay，容量符合 p14 剩余空间；
- [ ] UCI、Wi-Fi 和测试文件跨正常重启/断电保持；
- [ ] 恢复出厂只清 overlay，不影响其他分区；
- [ ] 上一对 boot/rootfs 可回滚。

## 阶段 D：OpenClash

- [ ] 不开 OpenClash时 LAN/Wi-Fi/4G/DNS 基线正常；
- [ ] 棒子自身 DNS 和 TCP curl 经代理成功；
- [ ] LAN 客户端 TCP 透明代理成功；
- [ ] UDP TPROXY 和 QUIC 成功，nft 计数器与日志可证明；
- [ ] TUN 开关、停用恢复、防火墙重载和 4G 重拨后规则正常；
- [ ] PC 端 Clash 关闭后重复关键测试；
- [ ] 24 小时压力、OOM、温度、日志/tmpfs 空间和断电恢复通过。

## 放行条件

developer 的 A/B 全通过后才开始 stable；A–D 与升级/回滚均通过，才允许
给 commit 标记“候选稳定”。公开 Release 还需要许可证审查、受保护环境
人工批准和不含私有固件的 manifest 检查。
