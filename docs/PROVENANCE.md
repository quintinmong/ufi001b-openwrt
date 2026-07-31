# 来源、版本锁与私有输入

## 公共输入

`locks/sources.lock.json` 是唯一事实源。OpenWrt、feeds、OpenClash、Mihomo、
msm8916 参考和构建工具均固定为完整 commit 或资产 SHA-256。

## 私有输入

以下内容不得提交、上传 artifact 或发布：完整 eMMC 备份、Qualcomm firmware、
modemst/EFS/NV/IMEI、Wi-Fi 校准、SIM 信息、代理订阅和任何密钥。

`qcom-firmware-ufi001b` 只是一份本地配方；提取的 firmware 仍为 proprietary，
`PKG_REDISTRIBUTE:=0`。`PRIVATE_FIRMWARE=1` 只允许本地 HIL 构建，公开 Actions
和 Release 必须拒绝对应包名及二进制。

## APK 签名

本地正式候选通过 `APK_SIGNING_KEY_FILE` 引用仓库外 EC 私钥；Actions 使用
Secret `APK_SIGNING_KEY_PEM` 在临时目录生成权限 0600 的文件。artifact 仅含
公钥，仓库 Variable `APK_SIGNING_PUBLIC_KEY_SHA256` 固定其指纹。PR 不注入
Secret，只能生成不可发布的临时签名。

## 公开仓库检查

公开前必须检查当前工作树和完整 Git 历史不存在密钥、订阅、设备标识、备份
或 proprietary blob；检查未过期 Actions artifacts 和日志；确认提交作者邮箱
可公开；并添加明确的顶层开源许可证。公开源码不等于允许重新分发 Qualcomm
firmware 或第三方构建资产，各文件和依赖仍遵循其自身许可证。
