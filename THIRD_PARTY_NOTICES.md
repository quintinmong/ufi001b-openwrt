# Third-party notices

The repository-level GPL-2.0-only default applies only to original project
code for which the project maintainer has the right to grant that license. It
does not replace a license or copyright notice attached to third-party code.

| Component or path | License | Copyright / source |
| --- | --- | --- |
| `openwrt-overlay/target/linux/msm89xx/**` | GPL-2.0-only | Copyright HandsomeMod Project and other applicable contributors; derived from the pinned HandsomeMod and Linux sources in `locks/sources.lock.json` |
| `openwrt-overlay/tools/mkbootimg/**` | GPL-2.0-only | osm0sis/mkbootimg at the pinned commit |
| `package/qrtr/**` | GPL-2.0-or-later | Bjorn Andersson and applicable contributors |
| `package/rmtfs/**` | GPL-2.0-or-later | Bjorn Andersson and applicable contributors |
| `package/rpmsgexport/**` | GPL-2.0-or-later | Bjorn Andersson and applicable contributors |
| `package/mihomo-openclash/**` and the Mihomo executable | GPL-3.0-only | MetaCubeX/mihomo at tag `v1.19.29`, commit `e26714a181ac0e2fa803453c0a8e9a9ce94e31cb` |
| OpenClash feed and `luci-app-openclash` | MIT | Copyright (c) vernesong; pinned commit `a9e5d98cd664917724dbfb0a31440e512ab45a1b` |
| Qualcomm firmware fetched only by an explicitly private build | Proprietary QTI license; not redistributed | HandsomeMod/qcom-firmware at the pinned commit |
| OpenWrt, Linux, packages, LuCI, routing, telephony and video feed content | Their file-level upstream licenses | Exact repositories and commits are recorded in `locks/sources.lock.json` |

## OpenClash MIT notice

Copyright (c) 2016-2023 vernesong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This notice is informational and is not a complete inventory of every package
inside an OpenWrt image. The corresponding-source archive shipped with each
public binary release preserves upstream source files and their notices.
