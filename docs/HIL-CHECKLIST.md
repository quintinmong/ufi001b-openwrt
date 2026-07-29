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
