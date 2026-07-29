# 架构与文件系统

## 启动链

UFI001B 沿用现有 Android 启动链。p12 的 Android boot image v0 包含压缩
内核、紧随其后的 UFI001B DTB 和空 ramdisk；命令行保持：

```text
earlycon console=tty0 console=ttyMSM0,115200 root=/dev/mmcblk0p14 rw rootwait
```

base、kernel/ramdisk/second/tags offset、2048 字节页尺寸均来自已能启动的
HandsomeMod UFI001B `boot.img`。构建后的镜像必须再次与
`board/ufi001b/reference/handsomemod-bootimg.json` 对照。

## 目标层

`target/linux/msm89xx/msm8916` 是本工程自己的 OpenWrt 目标。DTS 的首个
compatible 是 `handsome,openstick-ufi001b`，同时保留旧
`handsome,openstick` 兼容项。GPIO 37 低有效复位、GPIO 20/21/22 LED、
GPIO 1/2 SIM 控制来自 UFI001B 的工作 DTB，不能用 UFI003 或 UFI001C
参数替换。

内核保留 eMMC、ChipIdea USB gadget、remoteproc/Q6V5 MSS、QRTR/SMD、
BAM-DMUX/rmnet、WCNSS/WCN36xx。modem 与 WCNSS 驱动必须以模块交付，
保证根文件系统中的私有固件可用后再启动 remoteproc。

## rootfs 的职责

`rootfs` 是启动后看到的 `/`，包含 `/etc`、`/usr`、LuCI、OpenClash 和
软件包。它不包含 p12 的内核/DTB，也不包含基带、NV、IMEI、EFS 或
Wi-Fi 校准分区。

### developer-ext4

p14 起始位置写入 512 MiB ext4。首次启动服务只有同时满足以下条件才会
调用 `resize2fs /dev/mmcblk0p14`：

- compatible 明确为 UFI001B；
- 根文件系统是 ext4；
- 根设备是 `/dev/mmcblk0p14` 或 `/dev/root`；
- sysfs 报告该块设备确为第 14 分区。

扩容只改变 p14 内的文件系统，不改 GPT 和分区边界。

### stable-squashfs

p14 前部是只读 SquashFS。OpenWrt `fstools/rootdisk` 读取 SquashFS 的
`bytes_used`，按 64 KiB 对齐后把 p14 的剩余区域映射为 loop block；首次
使用时建立 `rootfs_data`，挂载为 `/overlay`。最终 `/` 是 `/rom` 与
`/overlay` 的 OverlayFS 合并视图。

因此系统文件有只读基线，UCI、OpenClash、Mihomo 和用户文件仍能持久
更新。无需新增 p15，也不修改 GPT。

2026-07-29 的本地构建在可复现性修正后，SquashFS 文件为 31,303,378 bytes；其
`bytes_used` 按 64 KiB 对齐后的 `rootfs_data` 起点是 31,326,208 bytes，
p14 仍留下 3,506,552,320 bytes（约 3.27 GiB）。这是按备份 GPT 精确 LBA
计算的离线布局证明；旧整数 KiB 表示会保守少算 512 bytes。loop、
F2FS、`/overlay` 和断电恢复仍须 HIL 才能确认运行时行为。

## 网络数据面

固件使用 firewall4/nftables，提供 TUN、NFT socket、NFT TPROXY、策略
路由和完整 `ip` 工具。预期路径为：TCP REDIRECT、UDP TPROXY、DNS 经
dnsmasq-full 转交 Mihomo；UDP 443/QUIC 可透明代理。IPv6 内核能力保留，
UCI 默认关闭，待单独验收后再开启。
