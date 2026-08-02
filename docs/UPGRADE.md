# 升级与回滚

## 软件包更新

OpenClash LuCI/脚本和 Mihomo 核心可独立安装同一仓库生成并签名的 APK，
不需要重刷 p12/p14。更新前导出配置，核对架构为 AArch64，并确认新包
来自通过静态检查的构建。内核模块不能跨不同 kernel ABI 混装。

## 完整固件升级

在 HIL 完成前不提供设备内自动写盘。人工升级流程为：

1. 导出 UCI、OpenClash 配置及用户明确选择的文件；
2. 保存当前稳定 boot/rootfs 的版本和 SHA-256；
3. 校验新 boot/rootfs、manifest、SBOM 和哈希；
4. 进入 9008，只写 p14 rootfs 和 p12 boot；
5. 首启后检查 rootfs/overlay，再恢复兼容配置；
6. 完成 USB、Wi-Fi、4G、DNS、TCP/UDP 透明代理和断电重启测试。

SquashFS 长度改变时，`rootfs_data` loop 的起点也会改变，旧 overlay 不应
被假定为可复用。正式升级默认按“备份配置、建立干净 overlay、选择性
恢复”处理。stable rootfs 镜像在新偏移处自带 `deadc0de` 初始化标记，完整
刷入后 `fstools` 会建立干净 F2FS overlay；不要把系统级旧文件整包覆盖到
新 `/overlay`。

## 回滚

回滚使用同一 UFI001B 已经通过 HIL 的上一对 p12/p14 镜像。boot 与
rootfs 作为一组回退，避免 kernel/kmod ABI 不匹配。仍然只写 p12/p14；
分区表、基带、NV 和校准数据保持原样。

OpenClash 单包回滚则安装上一版 APK，并恢复与之兼容的配置。若代理导致
失联，先通过有线 USB 管理口停用 OpenClash，不要立刻重刷整机。

公开固件不会携带 Qualcomm modem/WCNSS/NV 文件，也不会预设移动 WAN。
全新 overlay 或完整刷入后，应从设备自己的合规备份恢复所需私有 firmware，
再由用户为当前 SIM 配置 APN/连接；不要从其他棒子复制校准或身份数据。
