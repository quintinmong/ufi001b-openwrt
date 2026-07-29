# OpenClash 配置、验证与更新

## 固件能力

`stable-squashfs` 固定包含 OpenClash LuCI 包、ARM64 Mihomo Meta 核心、
firewall4/nftables、TUN、NFT socket、NFT TPROXY、策略路由工具和
dnsmasq-full 所需依赖。固件不包含订阅、节点或用户规则。

推荐首次配置：

- 先确认不开 OpenClash时 USB、Wi-Fi、4G 与 DNS 正常；
- 导入配置后先启动 TCP，再启用 UDP TPROXY；
- DNS 由 dnsmasq-full 转交 Mihomo，避免两个 DHCP/DNS 服务争用 53 端口；
- QUIC 是基于 UDP/443 的 HTTP/3。UDP TPROXY 工作时可代理 QUIC，无需
  为了“能打开网页”永久关闭 UDP；
- TUN 能力保留，但不是默认模式，只有特殊流量无法被 TPROXY 捕获时开启；
- IPv6 当前默认关闭，避免未验收的 IPv6 路径绕过代理。

## 在棒子自身验证

电脑上的 Clash 会干扰浏览器测试，因此必须通过 SSH 在棒子上测试：

```sh
ip rule show
nft list ruleset
logread -e openclash
nslookup www.google.com 127.0.0.1
curl -4 --connect-timeout 10 https://www.google.com/generate_204
```

`ping` 只验证 ICMP/IP 可达，不足以证明 HTTP 透明代理。应结合 nft 计数器、
OpenClash 日志、DNS 结果和棒子自身的 `curl`。UDP/QUIC 需另看 Mihomo
连接日志或使用明确支持 HTTP/3 的测试工具。

## 失联处置

开启后网页全断时，从 USB 管理口执行：

```sh
/etc/init.d/openclash stop
/etc/init.d/firewall restart
/etc/init.d/dnsmasq restart
```

随后检查配置语法、核心架构、时间、DNS 端口、默认路由、订阅有效性和
nft 规则。不要把 PC 端代理成功误判为棒子端成功。

## 独立更新

OpenClash 和 Mihomo 分成两个 APK。依赖更新 workflow 只创建 PR；通过
构建和安全审核后再发布到自建签名软件源。出现 OpenClash 漏洞时可只
更新对应 APK；涉及 nft/kmod/kernel ABI 时必须重建并刷完整固件。

394 MiB 内存下只保留一个 Mihomo 核心，控制 Geo 数据和日志大小，不与
Docker、AdGuard Home 等大服务并用。zram 是否启用及大小须经 HIL 内存
压力测试决定。
