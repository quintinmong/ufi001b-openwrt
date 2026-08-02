# Goal 完成性审计

## 交付定义

唯一交付是配套的 p12 boot 与 p14 SquashFS rootfs。运行时必须满足：

- `/rom` 为只读 SquashFS；
- `/overlay` 为 p14 剩余空间上的持久化 F2FS；
- `/` 为 OverlayFS 合并挂载；
- GPT、bootloader、modem、NV、IMEI、EFS 和校准分区不变。

## 证据状态

| 项目 | 状态 |
| --- | --- |
| 固定源码、签名身份和分区策略 | 已建立 |
| stable 构建与离线验证脚本 | run `30744657848` 通过 |
| stable artifact 与精确哈希 | artifact `8834512936` 已固定 |
| p14/p12 专用 HIL 工具 | 已固定，LocalCheck 通过 |
| 写入回读、GPT 与受保护分区 | p14/p12 回读、写前和最终只读审计全部通过 |
| OverlayFS/F2FS | 冷启动、软件重启、断电和 9008 后正常启动复验全部通过 |
| RNDIS、DHCP、LuCI、SSH | 新候选已通过 |
| Wi-Fi、SIM、基带 | 客户端关联/DHCP/公网、LTE bearer、DNS/NAT 均已通过 |
| 恢复出厂语义 | 设备映射与 fstools 源码静态审计确认仅清理 `rootfs_data` overlay |

因此本 Goal 已完成。运行时发现的软件源架构、中文和 LED 默认配置可在后续
构建中固化，但不改变当前 p12/p14 镜像及设备 HIL 结论。OpenClash 运行测试
已明确移出本 Goal。
