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
| stable 构建与离线验证脚本 | run `30636412439` 通过 |
| stable artifact 与精确哈希 | artifact `8800636377` 已固定 |
| p14/p12 专用 HIL 工具 | 已固定，LocalCheck 通过 |
| 写入回读、GPT 与受保护分区 | 旧候选通过，新候选待授权 |
| OverlayFS/F2FS | 旧候选已确认创建 F2FS，新候选待 HIL |
| RNDIS、DHCP、LuCI、SSH、Wi-Fi、SIM、基带 | 两阶段 UDC 绑定待复测，其余待 HIL |

因此 Goal 尚未完成；新 stable 候选已通过 CI 和离线验证，但需要对其精确哈希
重新授权并完成设备 HIL。OpenClash 运行测试已明确移出本 Goal。
