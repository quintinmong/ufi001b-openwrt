# Security Policy

## Supported version

当前只维护 `main` 分支以及最新公开 Release。旧构建仅用于历史复现，不保证
获得安全更新。

## Reporting a vulnerability

请不要为可能泄露设备凭据、私有固件、分区数据或可被利用的刷写问题创建公开
Issue。请使用仓库的 **Security → Report a vulnerability** 私下提交报告。

报告应包含受影响的 commit/Release、复现条件、潜在影响和建议缓解措施，但不
应包含 IMEI、SIM/APN、Wi-Fi 密码、代理订阅、设备完整备份、NV/EFS、校准
数据或其他个人/设备秘密。

主要维护者会先确认收到报告，再评估修复、HIL 验证和披露计划。普通兼容性或
构建问题请使用公开 GitHub Issues。
