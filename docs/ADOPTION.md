# 实机部署与采用证据

本页只记录能够追溯到具体构建和验证记录的部署，不把 Star、浏览量或未经核实的
口头反馈当作安装量。

## 当前快照

更新时间：2026-08-17。

| 指标 | 数量 | 说明 |
| --- | ---: | --- |
| 已核验实机部署 | 1 | 主要维护者持有的 UFI001B |
| 独立外部用户报告 | 0 | 尚未收到可公开核验的第三方报告 |
| 覆盖硬件 | 1 类 | Qualcomm MSM8916 / PCB UFI001B |

## 首台实机部署

主要维护者已将本仓库 stable 流水线生成的固件刷入一台 UFI001B 随身 Wi-Fi，
并将设备投入实际使用；维护者反馈当前体验良好。

可追溯构建为 Actions run `30759026223`、commit `20b4b667`、artifact
`8839178394`。该候选已完成授权写入、p14/p12 逐镜像回读、SHA-256 核对和
运行时 HIL。已验证的公开功能包括：

- SquashFS/F2FS OverlayFS 与跨重启持久化；
- RNDIS、DHCP、LuCI、SSH 和 USB 上网；
- 2.4 GHz Wi-Fi AP、客户端 DHCP、DNS/NAT 和公网访问；
- LTE 注册、分组业务附着和冷启动 WAN 恢复；
- 多次软件重启、断电冷启动和写后受保护分区只读审计；
- 红/蓝 LED 的实物行为。

详细命令、故障定位和验收记录见 [STATUS.md](STATUS.md) 与
[HIL-CHECKLIST.md](HIL-CHECKLIST.md)。

## 证据边界

这 1 台设备属于主要维护者，不能作为独立第三方采用量。仓库不会公开 IMEI、
SIM/APN、Wi-Fi 密码、设备备份、Qualcomm 私有 firmware、NV/EFS 或校准数据。
后续计数只接受包含硬件版本和 commit、Release 或 Actions run 的公开部署报告。

使用本项目刷机的用户可以通过
[Field deployment report](../.github/ISSUE_TEMPLATE/deployment_report.yml)
模板提交结果；失败和部分成功的报告同样有价值。
