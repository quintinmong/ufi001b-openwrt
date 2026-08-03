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
- stable run `30759026223`（commit `20b4b667`）成功，artifact `8839178394`
  已下载并通过离线验证；GitHub Actions 使用 Node 24，build annotations 为 0；
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
  SIM 已注册 LTE 家庭网络并附着分组业务；配置 `ctnet` IPv4 bearer 后，
  modem 跨重启自动恢复 connected；
- `UFI001B-OpenWrt` 2.4 GHz WPA2 AP 已启动并被 Windows 扫描到，地址为
  `192.168.2.1/24`；东八区、IPv6 禁用和 overlay 标记均跨软件重启保留。
- Wi-Fi 客户端已实际关联并取得 `192.168.2.0/24` DHCP 租约；客户端可访问
  LuCI 和公网。`ctnet` IPv4 bearer 开机自动建立，modem 为 LTE connected、
  SIM 注册 home、packet service attached，dnsmasq 解析和 WAN NAT 均通过；
- 运行时发现自定义 `aarch64_cortex-a53_neon` feed 名称在官方 25.12 软件源
  不存在；设备 overlay 已备份原配置，将六条官方通用 feed 修正为
  `aarch64_cortex-a53`，禁用不存在的自定义 target/OpenClash feed。索引验签
  后安装 LuCI base、防火墙和包管理器简体中文翻译，默认语言 `zh_cn` 已跨
  软件重启保留；USB DHCP 暂不下发网关/DNS，避免未选择棒子上网的电脑被
  RNDIS 抢走默认路由。
- 实物确认为红、蓝两颗可见 LED；内核另暴露 `green:wan`，但外壳没有可见的
  独立绿灯。WCNSS/WWAN 驱动不提供可用 netdev 字节计数或 LED 活动事件，
  因而流量 trigger 只能常亮；运行时改为红灯和不可见绿通道关闭、蓝灯由
  内核 timer 按 1.5 秒亮/0.3 秒灭显示系统心跳，实物闪烁验收通过，无后台
  轮询进程；
- 候选已完成多次软件重启、断电冷启动和 9008 后正常启动复验；F2FS overlay
  标记、UCI、私有固件、中文包、软件源修正、LTE、Wi-Fi 和 LED 设置均保留；
- ROM 默认配置候选 run `30759026223`（commit `20b4b667`，artifact
  `8839178394`）已完成授权写入、p14/p12 回读和增量 HIL；首次默认中文、官方
  `aarch64_cortex-a53` feed、私有 firmware 禁入以及 heartbeat/phy0tx LED
  策略均通过；
- 冷启动实测确认 netifd 早于 ModemManager 发现 modem，失败后不会自动恢复。
  设备 overlay 已安装 `ufi001b-wan-retry`：最多 180 秒，仅在接口非 pending
  时补发 `ifup wan`，WAN 在线后退出。修正前的 5 秒重复触发会重置注册流程；
  修正后软件重启只触发一次，8 秒完成 LTE、DNS 和公网恢复，无常驻进程；
- 最终 `AuditProtected` 只读审计通过：GPT 与 `fsc`、`fsg`、`modemst1`、
  `modemst2` 全部匹配备份基线和设备唯一前缀，审计未写入 eMMC；
- 设备上的 `firstboot`/`jffs2reset` 均调用 fstools `factoryreset`；当前
  `rootfs_data` 明确为挂载于 `/overlay` 的 `/dev/loop0` F2FS。官方
  [fstools factoryreset 源码](https://git.openwrt.org/project/fstools/plain/jffs2reset.c)
  固定查找 `rootfs_data` 并在已挂载时仅删除 overlay 文件，因此恢复出厂
  语义不会触及 GPT、modem/NV/EFS；为保留已验收配置未实际执行清理。

## 已解决的构建失败

stable run `30554242007`（commit `61beb7f`）在 Rust 1.94 host LLVM 的
`3752/3795` 链接阶段失败。runner 仅余 5 MiB，`ld.bfd` 报告
`No space left on device`；没有生成或上传可刷写 artifact。

## 后续改进（不阻塞本 Goal）

1. WAN/APN、私有 Qualcomm firmware 与冷启动拨号补偿继续保持为设备 overlay
   配置，不进入公开 ROM；
2. 按独立的 [OPENCLASH.md](OPENCLASH.md) 计划继续透明代理运行测试。

新候选已完成 Actions 构建、离线验证、授权写入、回读、运行时 HIL 和重启
持久化；写后受保护分区最终只读审计仍需再次进入 9008。OpenClash 运行测试
不属于当前 Goal。

历史 run `30541982297` / artifact `8762389406` 的 ext4 镜像仅保留为设备恢复
依据，不再属于源码构建、CI、Release 或正常刷写流程。
