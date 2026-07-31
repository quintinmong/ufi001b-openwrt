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
