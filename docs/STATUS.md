# 当前状态

更新时间：2026-08-03。

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
- stable run `30744657848`（commit `5285456`）成功，artifact `8834512936`
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
- run `30728461724` 已仅写 p14/p12 并完成回读；`192.168.1.1/24`、RNDIS
  426 Mbps、DHCP、LuCI、SSH 均通过，Windows 已恢复 DHCP；`/rom` 为只读
  SquashFS，`/overlay` 为约 3.3 GiB F2FS，`/` 为 OverlayFS，持久化标记跨
  正常重启保留；
- 从本地 HandsomeMod UFI001B 镜像提取私有固件到设备 overlay 后，WCNSS
  `phy0` 和 2.4 GHz AP 能力已出现；私有文件未进入 Git 或公开 artifact；
- 实机发现 rmtfs 缺少 `/dev/disk/by-partlabel` 导致 MPSS EFS 崩溃；创建与
  GPT PARTNAME 一致的 p7-p10 映射后 remoteproc0 稳定运行并生成
  `wwan0`-`wwan7`。同时发现 `CONFIG_RPMSG_WWAN_CTRL=m` 的模块未被打包，
  导致 ModemManager 缺少 QMI 控制口。源码已补齐 EFS 映射、
  `rpmsg_wwan_ctrl.ko` 打包/自动加载和 rpmsg hotplug 的 DEVNAME fallback，
  并加入构建期强制验证。
- 当前 stable 候选已仅写 p14/p12，rootfs/boot 均完成逐镜像回读和 SHA-256
  验证；写前 GPT 与 `fsc`、`fsg`、`modemst1`、`modemst2` 审计通过；
- 候选冷启动后 RNDIS 以 426 Mbps 枚举，Windows DHCP 获得
  `192.168.1.154/24`，`192.168.1.1`、LuCI 和 SSH 均可用；`/rom`、
  `/overlay`、`/` 分别为只读 SquashFS、约 3.3 GiB F2FS 和 OverlayFS；
- 本地私有运行时固件 34 个文件已恢复到 overlay，并逐文件 SHA-256 核对；
  重启后 MPSS/WCNSS remoteproc 均保持运行，RPMSG WWAN 模块自动加载，QMI
  与 AT 端口存在，ModemManager 的 Modem3gpp 接口可用。手动启用 modem 后
  SIM 已注册 LTE 家庭网络并附着分组业务；重启后因尚未建立蜂窝 bearer，
  modem 按 ModemManager 默认行为回到 disabled；
- `UFI001B-OpenWrt` 2.4 GHz WPA2 AP 已启动并被 Windows 扫描到，地址为
  `192.168.2.1/24`；东八区、IPv6 禁用和 overlay 标记均跨软件重启保留。

## 已解决的构建失败

stable run `30554242007`（commit `61beb7f`）在 Rust 1.94 host LLVM 的
`3752/3795` 链接阶段失败。runner 仅余 5 MiB，`ld.bfd` 报告
`No space left on device`；没有生成或上传可刷写 artifact。

## 待完成

1. 完成 Wi-Fi 客户端关联、DHCP 获址和管理页访问；
2. 配置蜂窝 bearer/APN 后完成移动数据 HIL；
3. 完成断电持久化复验，并再次审计 GPT 与受保护分区。

新候选已完成 Actions 构建、离线验证、授权写入、回读和首轮实机 HIL。
OpenClash 运行测试不属于当前 Goal。

历史 run `30541982297` / artifact `8762389406` 的 ext4 镜像仅保留为设备恢复
依据，不再属于源码构建、CI、Release 或正常刷写流程。
