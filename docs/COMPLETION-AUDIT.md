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
| 写入回读、GPT 与受保护分区 | p14/p12 回读通过，写前审计通过，最终审计待执行 |
| OverlayFS/F2FS | 新候选已通过冷启动和软件重启持久化复验 |
| RNDIS、DHCP、LuCI、SSH | 新候选已通过 |
| Wi-Fi、SIM、基带 | AP/扫描和 SIM LTE 注册已通过；客户端关联与移动数据待验收 |

因此 Goal 尚未完成；剩余项为 Wi-Fi 客户端关联/获址、移动数据、断电复验和
最终受保护分区审计。OpenClash 运行测试已明确移出本 Goal。
