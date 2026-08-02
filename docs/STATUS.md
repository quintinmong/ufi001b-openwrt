# 当前状态

更新时间：2026-08-02。

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
- stable run `30728461724`（commit `c69ca33`）成功，artifact `8828953097`
  已下载并通过离线验证；GitHub Actions 已升级到 Node 24，build annotations 为 0；
- stable HIL 脚本已固定候选，`LocalCheck` 验证 provenance、备份、GPT、loader、
  boot、SquashFS、F2FS preinit、RNDIS、marker 与哈希后通过；
- 旧候选已仅写 p14/p12 并完成回读；写前后 GPT、`fsc`、`fsg`、`modemst1`、
  `modemst2` 一致，首次启动已创建可读且容量正确的 F2FS overlay；
- pre-bind 诊断证明内核只在首次 UDC 绑定后创建 `usb0`；S25 诊断证明 netifd
  尚未注册 LAN，S90 诊断进一步证明动态 USB port 仍不能实例化 `br-lan`。
  上一候选让管理 LAN 直接绑定 `usb0`，执行 network reload 后最终重绑；旧
  Overlay 的 S25 调用仍会自动 defer。RNDIS carrier 与 RX 已恢复，但 LAN
  地址为错误的 `192.168.1.1/32`；当前候选在两个配置入口显式补齐 `/24`。

## 已解决的构建失败

stable run `30554242007`（commit `61beb7f`）在 Rust 1.94 host LLVM 的
`3752/3795` 链接阶段失败。runner 仅余 5 MiB，`ld.bfd` 报告
`No space left on device`；没有生成或上传可刷写 artifact。

## 待完成

1. 重新确认设备处于 9008、GPT 和受保护分区仍匹配基线；
2. 仅写 p14、回读验证，再写配套 p12、回读验证；
3. 正常重插、冷启动并完成 OverlayFS、网络、Wi-Fi、SIM 和基带 HIL；
4. 再次审计 GPT 与受保护分区，更新最终状态。

新候选尚待针对精确 run 的仅写 p14/p12 授权。OpenClash 运行测试不属于当前
Goal。

历史 run `30541982297` / artifact `8762389406` 的 ext4 镜像仅保留为设备恢复
依据，不再属于源码构建、CI、Release 或正常刷写流程。
