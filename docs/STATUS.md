# 当前状态

更新时间：2026-07-31。

## 已完成

- 固定 UFI001B p12/p14 布局、参考 boot metadata 和受保护分区策略；
- 建立 Linux 6.12、RNDIS、Wi-Fi/modem、F2FS、OverlayFS、zram 与 OpenClash
  构建配置；
- stable rootfs 使用 `append-rootfs | pad-rootfs | pad-to 512`，验证
  `deadc0de`、512 字节对齐和至少 2 GiB overlay；
- stable 验证覆盖 boot/DTB/IKCONFIG、SquashFS、F2FS preinit、RNDIS、manifest、
  Mihomo 架构、私有固件禁入、哈希和分区边界；
- Rust bootstrap 限制并发，并将 LLVM target 裁剪为 `AArch64;X86`；
- GitHub Actions stable runner 清理无关 SDK，并要求至少 30 GiB 可用；
- 删除与最终 Goal 无关的 ext4 开发版构建、发布、验证和刷写入口。
- 仓库已转为 public；完整 Git 历史未发现密钥、设备标识、备份或 proprietary
  blob，4 个旧开发版 artifact 已从 GitHub 删除；
- stable run `30622797978`（commit `ba90239`）成功，artifact `8794844117`
  已下载并通过离线验证；GitHub Actions 已升级到 Node 24，build annotations 为 0；
- stable HIL 脚本已固定候选，`LocalCheck` 验证 provenance、备份、GPT、loader、
  boot、SquashFS、F2FS preinit、RNDIS、marker 与哈希后通过；
- 旧候选已仅写 p14/p12 并完成回读；写前后 GPT、`fsc`、`fsg`、`modemst1`、
  `modemst2` 一致，首次启动已创建可读且容量正确的 F2FS overlay；
- 两轮网络 HIL 均能枚举 RNDIS，但 Windows 报告 media disconnected；只读
  overlay 分析确认 F2FS ready、S25 服务和 LAN/DHCP 配置正确；新候选在绑定
  UDC 前拉起 `usb0` 并记录持久链路诊断，等待设备复测。

## 已解决的构建失败

stable run `30554242007`（commit `61beb7f`）在 Rust 1.94 host LLVM 的
`3752/3795` 链接阶段失败。runner 仅余 5 MiB，`ld.bfd` 报告
`No space left on device`；没有生成或上传可刷写 artifact。

## 待完成

1. 用户针对 [CANDIDATE.md](CANDIDATE.md) 的新 rootfs 精确哈希明确授权；
2. 重新确认设备处于 9008、GPT 和受保护分区仍匹配基线；
3. 仅写 p14、回读验证，再写配套 p12、回读验证；
4. 正常重插、冷启动并完成 OverlayFS、网络、Wi-Fi、SIM 和基带 HIL；
5. 再次审计 GPT 与受保护分区，更新最终状态。

新候选尚未获得写入授权，禁止写入。OpenClash 运行测试不属于当前 Goal。

历史 run `30541982297` / artifact `8762389406` 的 ext4 镜像仅保留为设备恢复
依据，不再属于源码构建、CI、Release 或正常刷写流程。
