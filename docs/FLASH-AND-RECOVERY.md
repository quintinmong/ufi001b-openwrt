# 刷写与恢复

## 写入前提

每次写入必须同时满足：

1. PCB 丝印确认是 `UFI001B`；
2. 本机完整 eMMC 备份的大小和 SHA-256 已复核；
3. 9008 端口可稳定识别 MSM8916，并完成只读 GPT 扫描；
4. stable artifact 已通过 `verify-stable-artifact.py`；
5. 候选的 run、commit、artifact ID、boot/rootfs 尺寸和 SHA-256 已固定；
6. 用户针对这对精确镜像明确授权写入 p14 和 p12。

不存在通用的“同型号可直接刷”假设。任何板型、GPT、loader、镜像哈希或
分区边界不一致都必须在打开写操作前终止。

## 唯一允许的写入顺序

1. 只读审计 GPT 与所有受保护分区摘要；
2. 写 p14 `rootfs`，按实际镜像长度回读并逐字节 SHA-256；
3. 从回读内容验证 SquashFS 和 `rootfs_data` 的 `deadc0de` 标记；
4. 只有 p14 完全通过后才写 p12 `boot`，随后回读并逐字节 SHA-256；
5. 正常重插、冷启动并执行 HIL；
6. HIL 后再次审计 GPT 与受保护分区，确认没有变化。

不得使用会重建 GPT 的 rawprogram，不得写入 bootloader、modem、NV、IMEI、
EFS 或校准分区。当前候选固定在 [CANDIDATE.md](CANDIDATE.md)，只能使用
`scripts/flash-stable-hil.ps1`，不得手工替代门禁执行刷写。

设备不在手边时只运行本地检查：

```powershell
pwsh scripts/flash-stable-hil.ps1 -Mode LocalCheck
```

设备进入 9008 后依次执行只读检查、受保护分区审计、p14 和 p12。每个写入
命令都需要精确确认文本；每次仍须重新取得用户授权：

```powershell
pwsh scripts/flash-stable-hil.ps1 -Mode Check
pwsh scripts/flash-stable-hil.ps1 -Mode AuditProtected
pwsh scripts/flash-stable-hil.ps1 -Mode FlashRootfs `
  -Confirmation FLASH-UFI001B-STABLE-ROOTFS
pwsh scripts/flash-stable-hil.ps1 -Mode FlashBoot `
  -Confirmation FLASH-UFI001B-STABLE-BOOT
```

`FlashRootfs` 会先自动执行受保护分区审计；`FlashBoot` 会先从设备回读并确认
配套 rootfs 的 SHA-256、SquashFS magic 与 `deadc0de`，因此不能绕过 p14 成对
约束。

## 恢复

若 stable 无法启动，保持设备断电并优先返回 9008。先只读确认 GPT 和 p12/p14
状态，再使用本机归档的、已验证的恢复候选或完整备份。历史 developer 恢复
候选 run `30541982297` / artifact `8762389406` 仅作为设备救援依据，不属于
当前构建、发布或交付路径。
