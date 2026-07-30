# 刷写与恢复

> 本页是人工操作规程，不是自动刷机脚本。未经用户当次明确批准，不执行
> 任何真实写入。

## 刷写前门禁

必须全部满足：

1. PCB 丝印是 `UFI001B`，不是 UFI003/UFI001C；
2. 已离线保存本机完整 eMMC 备份，并复核大小和 SHA-256；
3. 9008 端口能稳定识别为 MSM8916，且可以只读扫描分区；
4. 新产物通过 `verify-developer-artifact.py`，包括 `SHA256SUMS`、boot
   metadata、内嵌 IKCONFIG、分区大小和 ext4 `e2fsck -fn`；
5. 第一次只使用 `developer-ext4`；
6. 有串口日志条件时优先接串口；否则至少保留 9008 恢复路径；
7. 用户再次明确批准本次 p12/p14 写入。

## 唯一允许写入的对象

| 产物 | 目标 | 上限 |
|---|---|---:|
| `*boot.img` | p12 `boot` | 64 MiB |
| `*rootfs.img` | p14 `rootfs` | 现有 p14 边界 |

在刷写工具中按分区名选择时，只勾选 `boot` 与 `rootfs`。不得选择
`Backup All`、`format eMMC`、GPT、Block 0、全盘写入或任何其他分区；
不得使用 UFI003 的 XML、loader、DTB 或整包。

推荐顺序是先写 p14 rootfs，再写 p12 boot。每写一个分区都等待工具明确
报告成功并保存日志，中途不拔线。完成后正常断开并冷启动，禁止让工具
自动执行格式化或修复 NV。

## Developer HIL 专用脚本

本仓库的 `scripts/flash-developer-hil.ps1` 只接受四类设备操作：只读 GPT
检查、只读设备唯一分区审计、写 p14 rootfs、写 p12 boot。它把当前候选、
MSM8916 loader、3.61 GiB 全盘备份及 p12/p14 精确 LBA/SHA-256 固定为门禁，
写后按镜像实际长度回读并重新校验 SHA-256。rootfs 还执行只读
`e2fsck -fn`。脚本不含 GPT、全盘、erase 或其他分区写命令。

已确认缺少 `DEVTMPFS/MMC_BLOCK` 的旧 Actions boot/rootfs 哈希被永久列入
脚本撤销名单，即使文件仍位于 `out/developer-ext4`，`LocalCheck` 也会在
打开 USB 前失败。新构建只有先通过离线门禁、更新脚本绑定的精确尺寸/哈希，
再取得用户针对该构建的明确批准，才能进入设备检查或写入模式。

顺序如下；只有 `LocalCheck` 不打开 USB：

```powershell
pwsh scripts/flash-developer-hil.ps1 -Mode LocalCheck
pwsh scripts/flash-developer-hil.ps1 -Mode Check
pwsh scripts/flash-developer-hil.ps1 -Mode AuditProtected
pwsh scripts/flash-developer-hil.ps1 -Mode FlashRootfs `
  -Confirmation FLASH-UFI001B-DEVELOPER-ROOTFS
# rootfs 写入和回读完全通过后，重新进入干净 9008：
pwsh scripts/flash-developer-hil.ps1 -Mode FlashBoot `
  -Confirmation FLASH-UFI001B-DEVELOPER-BOOT
```

不得跳过顺序或把两个确认字符串用于其他镜像。任何 loader/GPT/哈希、回读
或 ext4 检查失败都会终止；失败后不得继续写 boot。运行时必须关闭 Miko、
Premium Tool、QFIL、QPST 等会占用同一端口的工具。

## 首次失败时

若 3 分钟内没有 USB 网络、DHCP 或串口登录：

- 不反复写 GPT、不格式化 eMMC；
- 按 reset 重新进入 9008，仅做只读分区扫描，确认 eMMC 与表仍可读；
- 保存串口或工具日志；
- 优先把已验证的旧 UFI001B p12 boot 与 p14 rootfs 写回相同分区。

只有 p12/p14 回滚无效且经过单独分析、人工确认后，才考虑全盘恢复。
全盘恢复会覆盖设备唯一数据，必须使用这根 UFI001B 自己的备份，绝不能
使用昨天 UFI003 或另一根棒子的备份。

## 恢复验收

恢复后确认：设备正常启动、USB 网络出现、192.168.1.1 可达、IMEI 和
SIM 注册状态仍属本机、Wi-Fi MAC/校准正常。任何唯一标识变化都立即停止。
