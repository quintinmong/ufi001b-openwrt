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
| stable 构建与离线验证脚本 | 已建立，待新 run |
| stable artifact 与精确哈希 | 未产出 |
| p14/p12 专用 HIL 工具 | 待固定 |
| 回读、冷启动、OverlayFS/F2FS | 待设备 HIL |
| RNDIS、DHCP、LuCI、SSH、Wi-Fi、SIM、基带 | 待设备 HIL |

因此 Goal 尚未完成，也不存在当前可授权刷写的 stable 候选。OpenClash 运行
测试已明确移出本 Goal。
