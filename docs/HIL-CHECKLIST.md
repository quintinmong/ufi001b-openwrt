# UFI001B stable HIL 清单

候选固定为 run `30759026223`、commit `20b4b667`、artifact `8839178394`；完整
哈希见 [CANDIDATE.md](CANDIDATE.md)。`LocalCheck`、候选实机写入、回读、
冷启动、运行时功能、断电持久化和写后受保护分区最终只读审计均已通过。

当前候选保留 `/24`、rmtfs EFS 分区映射、RPMSG WWAN QMI/AT 与 hotplug
fallback，并固化中文、官方 feed 和内核事件 LED 默认策略。

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
- [x] GPT 和所有受保护分区在写前、写后完全一致。

## C. 文件系统与持久化

- [x] 冷启动成功；首次启动后 `rootfs_data` 已格式化为 F2FS；
- [x] `/rom` 为只读 SquashFS；
- [x] `/overlay` 为 p14 剩余空间上的可写 F2FS；
- [x] `/` 的类型为 overlay，容量符合离线计算；
- [x] UCI 修改、测试文件和软件安装跨正常重启及断电保持；
- [x] 恢复出厂语义经设备映射和 fstools 源码静态审计确认只清理
  `rootfs_data`/overlay，不影响其他分区；为保留当前配置未实际执行清理。

## D. 设备基本功能

- [x] Windows RNDIS 枚举稳定；
- [x] DHCP、`192.168.1.1`、LuCI 和 SSH 可用；
- [x] Wi-Fi 可设置密码、关联、获取地址并访问网络；
- [x] SIM 可识别，modem/QRTR/BAM-DMUX 正常，移动数据可建立；
- [x] 时区为 `Asia/Shanghai`，IPv6 默认禁用；
- [x] 实物可见的红、蓝两颗 LED 中，运行阶段红灯关闭，蓝灯以 1.5 秒亮、
  0.3 秒灭的内核 timer 心跳显示，实物观察通过且不使用后台轮询；内核暴露
  但外壳无可见独立灯的 `green:wan` 保持关闭；
- [x] 多次冷启动后功能一致；
- [x] 再次进入 9008；GPT 与 `fsc/fsg/modemst1/modemst2` 均匹配备份基线，
  审计未写入 eMMC。

OpenClash 安装和透明代理运行测试不属于当前 Goal，不阻塞 A-D 验收。

## ROM 默认配置增量 HIL

- [x] `/rom` manifest 含三个 LuCI `zh-cn` 包，首次启动语言为 `zh_cn`；
- [x] `apk update` 只访问六个有效的官方 `aarch64_cortex-a53` 共享源；
- [x] 干净系统不存在 WAN、ctnet、APN、运营商或 SIM PIN 默认配置；
- [x] 未恢复设备自有私有 firmware 时 MPSS/WCNSS blob 不在 `/rom`；
- [x] 恢复设备自有 34 个 firmware 后，红灯 heartbeat、蓝灯 `phy0tx` 生效；
- [x] 蓝灯空闲采样无误闪；xt_LED 对 FORWARD 的限时测试通过且规则无残留；
- [x] overlay-only WAN 冷启动补偿任务只请求一次拨号，pending 期间不重启，
  LTE、DNS 和公网在软件重启后自动恢复，任务随后退出。
