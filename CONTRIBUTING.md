# Contributing

感谢你改进 UFI001B OpenWrt 固件工程。项目优先接受可复现、可审计且不触碰受
保护分区的贡献。

## 提交问题

请先搜索现有 Issue。新问题应说明：

- 设备 PCB/硬件版本和当前固件版本；
- 可复现步骤、预期行为和实际行为；
- 相关 Actions run、commit SHA 或构建日志；
- 已执行的只读诊断和 HIL 检查。

不要上传 IMEI、SIM/APN、Wi-Fi 密码、代理订阅、设备完整备份、Qualcomm 私有
firmware、NV/EFS 或校准数据。

## 提交更改

1. 从 `main` 创建分支，并保持改动范围单一。
2. 运行 `python3 scripts/verify-locks.py`。
3. 运行 `python3 scripts/validate-layout.py`。
4. 对固件相关改动记录构建产物哈希；涉及硬件行为时按
   `docs/HIL-CHECKLIST.md` 验证。
5. 在 PR 中说明风险、验证范围以及是否影响 boot/rootfs 布局。

任何生成或写入 GPT、SBL、aboot、modem、modemst、fsc、fsg、NV、IMEI、EFS
或 Wi-Fi 校准分区的改动都不会被接受。

## 维护流程

主要维护者负责 Issue 分类、PR 评审、依赖更新、Release 和 HIL 结果核对。
小型文档修正可直接评审；构建、分区或运行时行为的变更必须通过自动检查，
并在适用时提供实机验证证据。
