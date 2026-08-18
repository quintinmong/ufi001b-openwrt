import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicRomPolicyTests(unittest.TestCase):
    def test_license_policy_has_explicit_boundaries(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        notice = (ROOT / "NOTICE.md").read_text(encoding="utf-8")
        third_party = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("GPL-2.0-only", readme)
        self.assertNotIn("本项目沿用 OpenStick README 的使用声明", readme)
        self.assertIn("不会给 GPL 代码附加", readme)
        self.assertIn("does not relicense", notice)
        self.assertIn("GPL-3.0-only", third_party)
        self.assertIn("OpenClash MIT notice", third_party)
        self.assertIn("Proprietary QTI license", third_party)

    def test_release_requires_corresponding_source_and_notices(self):
        build = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
        release = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        collector = (ROOT / "scripts/collect-artifacts.py").read_text(encoding="utf-8")
        self.assertIn("collect-corresponding-source.py", build)
        self.assertIn("ufi001b-corresponding-source", release)
        self.assertIn("corresponding-source-SHA256SUMS", release)
        for name in (
            "LICENSE",
            "NOTICE.md",
            "THIRD_PARTY_NOTICES.md",
            "SOURCE-COMPLIANCE.md",
            "sources.lock.json",
            "LICENSE.GPL-3.0-only-Mihomo",
        ):
            self.assertIn(name, collector)

    def test_public_profile_contains_language_and_led_capability(self):
        config = (ROOT / "configs/stable-squashfs.config").read_text(encoding="utf-8")
        for symbol in (
            "CONFIG_LUCI_LANG_zh_Hans=y",
            "CONFIG_PACKAGE_luci-i18n-base-zh-cn=y",
            "CONFIG_PACKAGE_luci-i18n-firewall-zh-cn=y",
            "CONFIG_PACKAGE_luci-i18n-package-manager-zh-cn=y",
            "CONFIG_PACKAGE_kmod-ipt-led=y",
            "CONFIG_PACKAGE_iptables-mod-led=y",
            "CONFIG_PACKAGE_iptables-nft=y",
            "CONFIG_FEED_openclash=m",
        ):
            self.assertIn(symbol, config)

    def test_shared_feed_architecture_is_official_cortex_a53(self):
        target = (
            ROOT / "openwrt-overlay/target/linux/msm89xx/msm8916/target.mk"
        ).read_text(encoding="utf-8")
        self.assertIn("CPU_TYPE:=cortex-a53", target)
        self.assertNotIn("CPU_SUBTYPE:=neon", target)

        patch = (
            ROOT
            / "patches/openwrt/020-msm89xx-disable-unpublished-core-repository.patch"
        ).read_text(encoding="utf-8")
        self.assertIn('"$(BOARD)" = "msm89xx"', patch)
        self.assertIn("'1s,^,# ,'", patch)

    def test_rom_defaults_have_chinese_leds_and_no_connection_profile(self):
        defaults = (
            ROOT / "package/ufi001b-base/files/etc/uci-defaults/90-ufi001b-system"
        ).read_text(encoding="utf-8")
        for token in (
            "luci.main.lang='zh_cn'",
            "system.ufi001b_red_system.trigger='heartbeat'",
            "system.ufi001b_blue_wifi.trigger='phy0tx'",
            "system.ufi001b_green_unused.trigger='none'",
        ):
            self.assertIn(token, defaults)
        forbidden = re.compile(
            r"(?:network\.wan|\bctnet\b|\bapn\b|\bsim_pin\b|"
            r"\boperator(?:_id)?\b|\.proto=['\"]modemmanager['\"])",
            re.IGNORECASE,
        )
        self.assertIsNone(forbidden.search(defaults))

        board = (
            ROOT / "package/ufi001b-base/files/etc/board.d/02_network"
        ).read_text(encoding="utf-8")
        self.assertIsNone(forbidden.search(board))

    def test_private_firmware_recipe_remains_non_redistributable(self):
        recipe = (ROOT / "package/qcom-firmware-ufi001b/Makefile").read_text(
            encoding="utf-8"
        )
        self.assertIn("PKG_LICENSE:=Proprietary", recipe)
        self.assertIn("PKG_REDISTRIBUTE:=0", recipe)
        public_config = (ROOT / "configs/stable-squashfs.config").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("CONFIG_PACKAGE_qcom-ufi001b-", public_config)


if __name__ == "__main__":
    unittest.main()
