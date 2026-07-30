# 构建与 GitHub Actions

## 本地环境

推荐 Ubuntu 24.04。WSL2 下仓库可在 `D:`，但 OpenWrt 构建树必须放在
例如 `/home/runtian/ufi001b-openwrt-build`；OpenWrt 会拒绝大小写不敏感的
`/mnt/d` 构建目录。

构建必须使用普通 Linux 用户，不能使用 root，也不能设置
`FORCE_UNSAFE_CONFIGURE=1` 绕过上游检查。WSL 示例应使用当前用户 home，
例如 `/home/runtian/ufi001b-openwrt-build`。

Ubuntu 依赖与 `.github/workflows/build.yml` 保持一致。首次构建：

```sh
cd /mnt/d/project/410wifi/ufi001b-openwrt
python3 scripts/verify-locks.py
python3 scripts/validate-layout.py
BUILD_ROOT=/home/runtian/ufi001b-openwrt-build JOBS=3 \
  scripts/build.sh developer-ext4
```

默认产物写入仓库的 `out/<profile>`。需要做独立 CI 复现时可设置
`OUTPUT_ROOT` 指向另一个空目录；它只改变收集位置，不改变构建输入或镜像。

`scripts/prepare-source.py` 会把 OpenWrt 和全部 feed 固定在
`locks/sources.lock.json` 的完整 commit；只允许覆盖本项目管理的 target、
tool 和 package 路径，发现其他脏改动便终止。

更新自定义 Git 源的 commit 时，必须在 Linux/WSL 用 OpenWrt 相同的规范归档
规则重新计算 `PKG_MIRROR_HASH`，例如：

```sh
scripts/compute-mirror-hash.sh qrtr 0.2 \
  https://github.com/andersson/qrtr.git FULL_40_HEX_COMMIT
```

把结果同时写入对应 Makefile 与 `locks/sources.lock.json`；
`verify-locks.py` 会拒绝两处不一致。

开发镜像完成并通过实机硬件检查后，才构建：

```sh
BUILD_ROOT=/home/runtian/ufi001b-openwrt-build JOBS=3 \
  scripts/build.sh stable-squashfs
```

发布候选必须使用长期保存的 EC APK 签名密钥：

```sh
openssl ecparam -name prime256v1 -genkey -noout \
  -out /安全且不在仓库内的路径/ufi001b-apk-private-key.pem
chmod 600 /安全且不在仓库内的路径/ufi001b-apk-private-key.pem
APK_SIGNING_KEY_FILE=/安全且不在仓库内的路径/ufi001b-apk-private-key.pem \
  BUILD_ROOT=/home/runtian/ufi001b-openwrt-build JOBS=3 \
  scripts/build.sh stable-squashfs
```

未设置 `APK_SIGNING_KEY_FILE` 时，OpenWrt 会生成一次性密钥；这种构建只适合
本地试验或 PR，不能成为 Release。收集器只复制由私钥推导的
`apk-signing-public-key.pem`，并明确排除私钥。

## 输出校验

`validate-build.py` 强制检查：

- boot image v0 的地址、页尺寸和命令行与参考镜像相同；
- boot 解压内核不得含会随链接变化的 GNU SHA-1 build-id note；
- p12 镜像不超过 64 MiB，rootfs 不越过 p14；
- 内核具备 devtmpfs、内建 eMMC block/GPT/ext4 根挂载链、USB gadget、
  remoteproc、WCN36xx、TUN、NFT TPROXY、NFT socket 和 OverlayFS；
- 输出名称不含 GPT、bootloader、modemst、fsc/fsg 等危险对象；
- 公开配置的 manifest 不含私有 Qualcomm 固件包。
- developer ext4 必须通过只读 `e2fsck -fn`；
- stable SquashFS 必须能由构建树的 `unsquashfs4` 读取，按 64 KiB 计算的
  `rootfs_data` 起点必须位于 p14 内并至少留下 2 GiB；
- stable 镜像内必须实际存在 OpenClash、AArch64 Mihomo、zram 与
  `mkfs.f2fs`，并校验对应 manifest 和 F2FS/ZRAM/loop 内核符号；
- stable 镜像内的 libelf 不得含非确定性 GNU SHA-1 build-id note。

下载 artifact 后使用独立离线门禁（在 Linux/WSL 中运行，以获得只读
`e2fsck`）：

```sh
python3 scripts/verify-developer-artifact.py out/developer-ext4
```

它重新计算 `SHA256SUMS`、boot metadata、p12/p14 尺寸和 ext4 超级块，执行
`e2fsck -fn`，并从 boot 内核的 IKCONFIG 载荷读取最终配置，验证完整根挂载
与 USB/网络依赖；不会信任构建树中已经消失的临时 `.config`。

仅在 target `config-6.12` 中写入 `DEVTMPFS` 或 `MMC_BLOCK` 不足以保证最终
内核仍启用它们：OpenWrt 顶层 `CONFIG_KERNEL_*` 与内核包元数据会在
`Kernel/Configure` 阶段再次覆盖配置。因此两个 profile 都显式选择
`CONFIG_KERNEL_DEVTMPFS`/`CONFIG_KERNEL_DEVTMPFS_MOUNT`，UFI001B 的
`DEVICE_PACKAGES` 也必须包含 `kmod-mmc`；最终门禁读取实际构建内核的
`.config`，不以源片段代替产物证据。

收集器按 profile 只复制对应的 ext4 或 SquashFS 镜像和 APK 公钥，stable
另收集唯一的 OpenClash/Mihomo APK；生成 SPDX 2.3 SBOM 与
`SHA256SUMS`，并拒绝向非空输出目录混入新文件。

OpenClash 依赖会首次构建 Rust/LLVM host 工具链。`build.sh` 先执行 Rust
host configure，再把 bootstrap 内层并发限制为 `min(JOBS, 4)`；这是为了
避免 16 GiB 左右主机在 LLVM `-j8` 时严重换页，不改变源码或目标产物版本。

## Actions

- `static.yml`：锁、分区策略、Python、Shell、workflow YAML 和禁入二进制检查；
- `build.yml`：main push 只构建 developer，手动运行可选择 developer 或
  stable，PR 才运行双 profile 矩阵；artifact 保留 3 天。GitHub 只对公开的
  用户仓库开放 artifact attestation，因此私有仓库跳过该步；
- `dependency-update.yml`：每周只提交版本锁更新 PR，不直接发布；
- `release.yml`：只接受人工 `workflow_dispatch`，要求签名 tag、同一 commit
  的成功 Build firmware run、artifact profile/哈希复核、布尔确认和受保护
  的 `release` environment。

首次使用前必须完成以下 GitHub 设置：

1. 在 Actions Secret `APK_SIGNING_KEY_PEM` 中保存完整 EC 私钥 PEM；
2. 从该私钥推导公钥并计算 `sha256sum`，把 64 位十六进制值保存为仓库
   Variable `APK_SIGNING_PUBLIC_KEY_SHA256`；
3. 给 `release` environment 添加人工审核人，并保持 Actions 默认 token
   最小权限。

`build.yml` 的 PR 步骤从不注入 Secret，只使用一次性密钥；push 和手工构建
缺少 Secret 会失败。`release.yml` 同时要求两个 profile 的公钥相同且等于仓库
Variable；build 会在上传 artifact 前检查指纹，release 会再次检查两个 profile
的公钥身份，防止错误密钥的包进入 Release。公开 CI 永远不注入私有固件。

## 可复现边界

版本、commit、Git 规范归档哈希以及 Mihomo ARM64 资产哈希全部锁定；浅克隆
会先补全历史，保证 `base-files` 的 commit count 稳定。内核、arm64 vDSO 和
libelf 中已关闭非确定性 GNU build-id，并由镜像内容校验门禁验证。

APK 使用 EC/ECDSA 签名；当前工具链签名 nonce 具有随机性，所以即使源码、
公钥与内容相同，APK 及包含 APK 数据库的 rootfs 也不承诺逐字节相同。发布
保证是“锁定输入 + 固定公钥指纹 + 每次构建的 SHA-256/SBOM”，不是预先
承诺某个整镜像哈希。公开仓库额外生成 GitHub provenance；用户所有的私有
仓库受 GitHub 平台限制无法保存 attestation。每个 Release 必须保存
buildinfo、manifest、公钥、SBOM 和哈希，不能仅以版本字符串判断两个镜像相同。
