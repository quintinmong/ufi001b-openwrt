# UFI001B stable HIL 清单

候选固定为 run `30744657848`、commit `5285456`、artifact `8834512936`；完整
哈希见 [CANDIDATE.md](CANDIDATE.md)。`LocalCheck` 和候选实机写入/启动已通过，
以下未勾选项仍待执行。

上一候选的 p14/p12 写入、回读、OverlayFS、RNDIS、DHCP、LuCI 和 SSH 均已
通过。当前候选保留 `/24` 修复，并补齐 rmtfs EFS 分区映射、RPMSG WWAN
QMI/AT 模块与 rpmsg hotplug fallback。

## A. 离线与写前审计

- [x] 固定 run、commit、artifact ID、镜像尺寸和 SHA-256；
- [x] boot、DTB、IKCONFIG、SquashFS、`deadc0de`、F2FS 模块链全部通过；
- [x] loader、备份 GPT 和完整备份摘要与基线一致；
- [x] 实机 PCB、当前 GPT 和受保护分区摘要与基线一致；
- [x] 用户针对精确候选明确授权仅写 p14/p12。

## B. 写入与回读

- [x] p14 写入后按实际长度回读，SHA-256 与候选一致；
- [x] 回读 rootfs 可解析为 SquashFS，准确偏移处为 `deadc0de`；
- [x] p12 写入后按实际长度回读，SHA-256 与候选一致；
- [ ] GPT 和所有受保护分区在写前、写后完全一致。

## C. 文件系统与持久化

- [x] 冷启动成功；首次启动后 `rootfs_data` 已格式化为 F2FS；
- [x] `/rom` 为只读 SquashFS；
- [x] `/overlay` 为 p14 剩余空间上的可写 F2FS；
- [x] `/` 的类型为 overlay，容量符合离线计算；
- [ ] UCI 修改、测试文件和软件安装跨正常重启及断电保持；
- [ ] 恢复出厂只清理 overlay，不影响其他分区。

## D. 设备基本功能

- [x] Windows RNDIS 枚举稳定；
- [x] DHCP、`192.168.1.1`、LuCI 和 SSH 可用；
- [ ] Wi-Fi 可设置密码、关联、获取地址并访问网络；
- [ ] SIM 可识别，modem/QRTR/BAM-DMUX 正常，移动数据可建立；
- [x] 时区为 `Asia/Shanghai`，IPv6 默认禁用；
- [ ] 多次冷启动后功能一致，受保护分区最终审计无变化。

OpenClash 安装和透明代理运行测试不属于当前 Goal，不阻塞 A-D 验收。
