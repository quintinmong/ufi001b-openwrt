# 构建与流水线

## 固定输入

`locks/sources.lock.json` 固定 OpenWrt、feeds、OpenClash、Mihomo 和板级参考
源码的完整 commit 或资产 SHA-256。`scripts/verify-locks.py` 与
`scripts/prepare-source.py` 拒绝漂移输入。

## 本地构建

```sh
BUILD_ROOT="$HOME/ufi001b-openwrt-build" JOBS=3 scripts/build.sh
```

`BUILD_ROOT` 必须是大小写敏感的 Linux 文件系统。正式候选通过
`APK_SIGNING_KEY_FILE` 指向仓库外的 EC 私钥；未提供时只生成不可发布的临时
签名身份。`PRIVATE_FIRMWARE=1` 仅供本地 HIL 构建，任何包含 Qualcomm 私有
固件的产物都不得上传或发布。

OpenClash 依赖会构建 Rust host 工具链。脚本把 Rust bootstrap 并发限制为
`min(JOBS, 4)`，并将 LLVM 后端限制为 `AArch64;X86`，分别服务目标固件和
runner host，减少无关后端造成的磁盘与链接开销。

## 自动门禁

构建必须验证：

- boot metadata、DTB token、内嵌 IKCONFIG 及 p12 边界；
- rootfs 为可读取的 SquashFS，镜像按 512 字节对齐；
- `rootfs_data` 对齐点包含大端 `deadc0de`，p14 至少留下 2 GiB；
- F2FS preinit 模块链、`mount_root`、RNDIS 脚本和必需包实际存在；
- LuCI 简体中文包、默认 `zh_cn`、官方 `aarch64_cortex-a53` 六个共享源、
  禁用的 msm89xx/OpenClash 无效源和 LED/xt_LED 能力实际位于 ROM；
- board/UCI 默认不创建 WAN，不含 APN、运营商、SIM PIN 或自动拨号配置；
- Mihomo 是 AArch64 ELF，OpenClash/Mihomo APK、manifest、SBOM 和公钥齐全；
- manifest 与 SquashFS 路径均不含私有 Qualcomm 固件、危险分区文件或
  非确定性 build-id。

下载后的离线复核：

```sh
python3 scripts/verify-stable-artifact.py out/stable-squashfs
```

Windows 可按成功 run ID 下载并立即复核：

```powershell
pwsh -File scripts/fetch-verify-actions-artifact.ps1 -RunId 123456789
```

脚本拒绝失败 run、过期/重名 artifact、ZIP 路径穿越和已有目标目录。下载验证
通过仍不代表获准刷写，必须记录该候选的精确 commit、artifact ID、尺寸和
SHA-256，并重新取得用户授权。

## GitHub Actions

- `static.yml`：锁文件、分区策略、Python/PowerShell/shell、workflow YAML、
  内核与镜像配置及禁入二进制检查；
- `build.yml`：PR 或人工 dispatch 才构建 `stable-squashfs`；runner 先清理
  无关 SDK 并要求至少 30 GiB 可用；artifact 保留 3 天；
- `dependency-update.yml`：每周只创建更新 PR；
- `release.yml`：只接受人工 dispatch、签名 tag、同 commit 成功 run 和受保护
  environment 批准，并只发布 stable artifact。
