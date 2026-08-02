# 架构与文件系统

## 分区边界

UFI001B 现有 GPT 保持不变。唯一允许更新的分区是：

- p12 `boot`：Android boot image v0，包含 Linux 6.12 内核和 UFI001B DTB；
- p14 `rootfs`：SquashFS 与同分区尾部的 F2FS `rootfs_data`。

bootloader、modem、NV、IMEI、EFS 和校准分区均属于受保护范围。

## SquashFS 与 OverlayFS

p14 前部是只读 SquashFS，运行时挂载为 `/rom`。`fstools/rootdisk` 从
SquashFS `bytes_used` 计算 64 KiB 对齐的 `rootfs_data` 起点，在剩余空间
建立 F2FS 并挂载为 `/overlay`。最终 `/` 是 `/rom` 与 `/overlay` 的
OverlayFS 合并视图。

`rootfs.img` 通过 `append-rootfs | pad-rootfs | pad-to 512` 在准确的对齐点
写入大端 `deadc0de`，并补齐到 512 字节 eMMC 扇区。该标记要求 `fstools`
初始化新的持久层，避免误用旧 rootfs 尾部数据。F2FS 驱动通过
`/etc/modules-boot.d` 在 preinit 阶段加载。

构建和下载门禁都会重新验证 SquashFS、标记、扇区对齐、p14 边界以及至少
2 GiB 的 overlay 可用空间，不能复用旧构建的固定偏移。

## 网络与服务

USB 使用 configfs RNDIS，LAN 默认地址为 `192.168.1.1`，IPv6 默认禁用，
时区为 `Asia/Shanghai`。内核保留 MSM8916 modem、QRTR、BAM-DMUX、WCN36xx、
nftables TPROXY、TUN 和 zram 支撑。OpenClash 包随镜像构建，但其代理功能
测试不属于当前 Goal。

ROM 只提供 ModemManager、QMI/RPMSG WWAN 和 LuCI 协议能力，不创建 WAN
接口，不保存 `ctnet`、运营商、APN、SIM PIN 或自动拨号参数。具体移动网络
配置属于每台设备和 SIM 的 OverlayFS 数据，不能成为公开固件默认值。

## ROM 默认与 LED

LuCI 基础界面、防火墙、包管理器的简体中文翻译随 SquashFS 提供，首次启动
默认使用 `zh_cn`。共享软件源架构固定为 OpenWrt 官方发布的
`aarch64_cortex-a53`；本项目没有公开 target 包仓，因此 msm89xx target 源和
不存在的官方 OpenClash 源在 `/rom` 中保留为注释，仅启用六个官方共享源。

LED 不使用轮询守护进程。默认采用 OpenStick 社区习惯：红灯由内核
`heartbeat` 表示系统存活，蓝灯由 mac80211 `phy0tx` 表示 Wi-Fi 发包，外壳
不可见的 `green:wan` 通道关闭。固件同时包含 Netfilter `xt_LED` 与
iptables-nft 扩展，供 HIL 在确认转发路径后测试“匹配到真实转发包才闪”的
备选规则；ROM 默认不写入未经实机验证的防火墙 LED 规则。
