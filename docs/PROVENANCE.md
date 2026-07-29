# 来源、版本锁与私有固件

## 公共输入

唯一事实源是 `locks/sources.lock.json`。OpenWrt、五个官方 feed、
OpenClash、msm8916-mainline 参考、HandsomeMod 参考、mkbootimg、QRTR、
rmtfs、rpmsgexport 和 Mihomo 都固定到完整 commit 或发布资产 SHA-256。

对 `PKG_SOURCE_PROTO:=git` 的包，`source_sha256` 指 OpenWrt 生成的规范
`.tar.zst`，不是 GitHub codeload 文件的哈希。更新脚本必须同时更新包
Makefile 和锁文件，并由干净构建验证。

## 私有输入

以下内容不得提交、上传 artifact 或发布：

- `backup_manual.bin` 等全 eMMC 备份；
- modem、WCNSS 和 Wi-Fi NV/校准二进制；
- modemst、fsc、fsg、EFS/NV、IMEI 数据；
- SIM 信息、代理订阅、密钥和真实用户配置。

`qcom-firmware-ufi001b` 只是受保护的本地 HIL 配方，公开 profile 不选择
它。它仍受原上游许可证约束，`PRIVATE_FIRMWARE=1` 只能配合
`developer-ext4` 在本机测试；产物不得进入公开 Release。未完成许可证和
再分发审查前，不把含这些 blob 的完整 rootfs 交付给第三方。

## APK 签名密钥

APK 私钥不是源码输入，不得提交仓库、写入日志、上传 artifact 或放入固件。
本地发布候选通过 `APK_SIGNING_KEY_FILE` 指向仓库外的 PEM；GitHub Actions
通过 Secret `APK_SIGNING_KEY_PEM` 在 runner 临时目录创建权限为 0600 的
文件，用后随 runner 销毁。公开产物只包含推导出的
`apk-signing-public-key.pem`。

仓库 Variable `APK_SIGNING_PUBLIC_KEY_SHA256` 保存预期公钥文件的 SHA-256。
Release 会比较 developer/stable 两份公钥，并要求它们与该 Variable 完全
一致。所有 `pull_request` 步骤都不注入 Secret，只使用一次性密钥，这类产物
不可发布。

生成和登记密钥：

```sh
openssl ecparam -name prime256v1 -genkey -noout -out private-key.pem
openssl ec -in private-key.pem -pubout -out public-key.pem
sha256sum public-key.pem
```

私钥应另有离线加密备份；轮换密钥必须经人工审核，更新仓库 Variable，并在
Release 说明中同时公布旧、新公钥指纹和生效版本。

EC/ECDSA 签名含随机 nonce。因此本工程不把 APK 或整 rootfs 的逐字节相同
作为供应链承诺；承诺的是固定源码、固定公钥身份，以及对每次实际产物生成
并证明其 SHA-256、manifest、SBOM 和 provenance。

## 更新原则

自动任务只能创建 PR。审核人应确认上游账号、tag/commit、资产名称、
SHA-256、许可证变化和安全公告；随后运行静态检查与两种完整构建。内核
或 kmod ABI 变化必须重新走 developer-ext4 与 HIL，不可仅更新 APK。
