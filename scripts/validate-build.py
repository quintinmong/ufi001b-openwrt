#!/usr/bin/env python3
"""Validate UFI001B build outputs before they can become artifacts."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import tempfile
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = json.loads((ROOT / "board/ufi001b/partition-layout.json").read_text(encoding="utf-8"))
REFERENCE = json.loads(
    (ROOT / "board/ufi001b/reference/handsomemod-bootimg.json").read_text(encoding="utf-8")
)
GNU_SHA1_BUILD_ID_NOTE = b"\x04\x00\x00\x00\x14\x00\x00\x00\x03\x00\x00\x00GNU\x00"
REQUIRED_KERNEL_CONFIG = (
    "CONFIG_ARCH_QCOM=y",
    "CONFIG_BLOCK=y",
    "CONFIG_DEVTMPFS=y",
    "CONFIG_EFI_PARTITION=y",
    "CONFIG_MMC=y",
    "CONFIG_MMC_BLOCK=y",
    "CONFIG_MMC_SDHCI=y",
    "CONFIG_MMC_SDHCI_MSM=y",
    "CONFIG_USB_SUPPORT=y",
    "CONFIG_USB_CONFIGFS=m",
    "CONFIG_USB_CONFIGFS_RNDIS=y",
    "CONFIG_USB_F_RNDIS=m",
    "CONFIG_EXTCON_USB_GPIO=y",
    "CONFIG_QRTR=y",
    "CONFIG_QRTR_SMD=y",
    "CONFIG_QCOM_BAM_DMUX=m",
    "CONFIG_QCOM_Q6V5_MSS=m",
    "CONFIG_QCOM_WCNSS_PIL=m",
    "CONFIG_RPMSG_WWAN_CTRL=m",
    "CONFIG_WCN36XX=m",
    "CONFIG_TUN=m",
    "CONFIG_NFT_TPROXY=m",
    "CONFIG_NFT_SOCKET=m",
    "CONFIG_NETFILTER_XT_TARGET_LED=m",
    "CONFIG_OVERLAY_FS=y",
)


def load_inspector():
    path = ROOT / "scripts/extract-reference-boot.py"
    spec = importlib.util.spec_from_file_location("boot_inspector", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.inspect


def find_one(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    if len(matches) != 1:
        raise SystemExit(f"expected one {pattern}, found {len(matches)}")
    return matches[0]


def read_kernel_config(tree: Path) -> str:
    matches = list(
        (tree / "build_dir").glob(
            "target-aarch64_cortex-a53*_musl/linux-msm89xx_msm8916/linux-6.12.*/.config"
        )
    )
    if len(matches) != 1:
        raise SystemExit(f"expected one built kernel config, found {len(matches)}")
    return matches[0].read_text(encoding="utf-8")


def run_text(command: tuple[str, ...]) -> str:
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}")
    return result.stdout


def extract_embedded_kernel_config(boot: Path, metadata: dict[str, object]) -> str:
    """Extract CONFIG_IKCONFIG data from the gzip-compressed boot kernel."""
    image = boot.read_bytes()
    page_size = int(metadata["page_size"])
    dtb_offset = int(metadata["appended_dtb_offset_in_kernel"])
    compressed_kernel = image[page_size : page_size + dtb_offset]
    try:
        kernel = zlib.decompress(compressed_kernel, 16 + zlib.MAX_WBITS)
    except zlib.error as error:
        raise SystemExit(f"cannot decompress boot kernel: {error}") from error

    start_marker = b"IKCFG_ST"
    end_marker = b"IKCFG_ED"
    start = kernel.find(start_marker)
    end = kernel.find(end_marker, start + len(start_marker))
    if start < 0 or end < 0:
        raise SystemExit("boot kernel does not contain an embedded IKCONFIG payload")
    payload = kernel[start + len(start_marker) : end]
    try:
        config = zlib.decompress(payload, 16 + zlib.MAX_WBITS)
    except zlib.error as error:
        raise SystemExit(f"cannot decompress embedded kernel config: {error}") from error
    return config.decode("utf-8", errors="strict")


def missing_kernel_config(config: str) -> list[str]:
    missing = [symbol for symbol in REQUIRED_KERNEL_CONFIG if symbol not in config]
    for symbol in ("CONFIG_USB_CHIPIDEA", "CONFIG_USB_GADGET"):
        if not any(f"{symbol}={value}" in config for value in ("y", "m")):
            missing.append(f"{symbol}=(y|m)")
    if not any(symbol in config for symbol in ("CONFIG_NF_TABLES=y", "CONFIG_NF_TABLES=m")):
        missing.append("CONFIG_NF_TABLES=(y|m)")
    return missing


def validate_boot_build_ids(boot: Path, metadata: dict[str, object]) -> None:
    """Reject the two known non-deterministic GNU build-id notes in the boot kernel."""
    image = boot.read_bytes()
    page_size = int(metadata["page_size"])
    dtb_offset = int(metadata["appended_dtb_offset_in_kernel"])
    compressed_kernel = image[page_size : page_size + dtb_offset]
    try:
        kernel = zlib.decompress(compressed_kernel, 16 + zlib.MAX_WBITS)
    except zlib.error as error:
        raise SystemExit(f"cannot decompress boot kernel: {error}") from error
    if GNU_SHA1_BUILD_ID_NOTE in kernel:
        raise SystemExit("boot kernel contains a non-deterministic GNU SHA-1 build-id note")


def validate_stable_rootfs(
    unsquashfs: Path,
    rootfs: Path,
    partition_bytes: int,
    manifest: str,
    allow_private_firmware: bool = False,
) -> tuple[int, int]:
    if not unsquashfs.is_file():
        raise SystemExit("host unsquashfs4 is missing")
    with rootfs.open("rb") as handle:
        if handle.read(4) != b"hsqs":
            raise SystemExit("stable rootfs does not start with a SquashFS superblock")

    summary = run_text((str(unsquashfs), "-s", str(rootfs)))
    size_match = re.search(r"^Filesystem size (\d+) bytes", summary, re.MULTILINE)
    if size_match is None:
        raise SystemExit("cannot read SquashFS filesystem size")
    squashfs_bytes = int(size_match.group(1))
    rootfs_data_offset = (squashfs_bytes + 65535) & ~65535
    overlay_bytes = partition_bytes - rootfs_data_offset
    image_bytes = rootfs.stat().st_size
    if image_bytes % 512:
        raise SystemExit("stable rootfs image is not eMMC-sector aligned")
    if image_bytes < rootfs_data_offset + 4:
        raise SystemExit("stable rootfs does not initialize the rootfs_data boundary")
    if image_bytes > rootfs_data_offset + 256 * 1024 + 512:
        raise SystemExit("stable rootfs padding extends unexpectedly far into rootfs_data")
    with rootfs.open("rb") as handle:
        handle.seek(rootfs_data_offset)
        if handle.read(4) != b"\xde\xad\xc0\xde":
            raise SystemExit("stable rootfs lacks the fstools deadc0de marker at rootfs_data")
    if rootfs_data_offset >= partition_bytes:
        raise SystemExit("aligned rootfs_data offset falls outside p14")
    if overlay_bytes < 2 * 1024 * 1024 * 1024:
        raise SystemExit("stable p14 leaves less than 2 GiB for rootfs_data")

    listing = run_text((str(unsquashfs), "-ll", str(rootfs)))
    required_paths = (
        "squashfs-root/etc/apk/repositories.d/distfeeds.list",
        "squashfs-root/etc/init.d/openclash",
        "squashfs-root/etc/init.d/rmtfs",
        "squashfs-root/etc/hotplug.d/rpmsg/55-rpmsgexport",
        "squashfs-root/etc/init.d/ufi001b-usb-gadget",
        "squashfs-root/etc/rc.d/S90ufi001b-usb-gadget",
        "squashfs-root/etc/init.d/zram",
        "squashfs-root/etc/modules-boot.d/30-fs-f2fs",
        "squashfs-root/etc/openclash/core/clash_meta",
        "squashfs-root/etc/uci-defaults/90-ufi001b-system",
        "squashfs-root/sbin/mount_root",
        "squashfs-root/usr/sbin/mkfs.f2fs",
    )
    missing_paths = [path for path in required_paths if path not in listing]
    if missing_paths:
        raise SystemExit("SquashFS missing:\n- " + "\n- ".join(missing_paths))

    if not re.search(
        r"squashfs-root/etc/modules-boot\.d/30-fs-f2fs"
        r" -> \.\./modules\.d/30-fs-f2fs$",
        listing,
        re.MULTILINE,
    ):
        raise SystemExit("SquashFS F2FS boot-module symlink has an unexpected target")
    if not re.search(
        r"squashfs-root/lib/modules/[^/\s]+/f2fs\.ko$", listing, re.MULTILINE
    ):
        raise SystemExit("SquashFS is missing the F2FS kernel module")
    if not re.search(
        r"squashfs-root/lib/modules/[^/\s]+/rpmsg_wwan_ctrl\.ko$",
        listing,
        re.MULTILINE,
    ):
        raise SystemExit("SquashFS is missing the RPMSG WWAN control module")
    if not re.search(
        r"squashfs-root/lib/modules/[^/\s]+/xt_LED\.ko$", listing, re.MULTILINE
    ):
        raise SystemExit("SquashFS is missing the Netfilter xt_LED module")

    private_firmware_paths = (
        r"squashfs-root/lib/firmware/mba\.mbn$",
        r"squashfs-root/lib/firmware/modem\.[^/\s]+$",
        r"squashfs-root/lib/firmware/wcnss\.[^/\s]+$",
        r"squashfs-root/lib/firmware/wlan/prima/WCNSS_qcom_wlan_nv\.bin$",
    )
    leaked_paths = [
        pattern
        for pattern in private_firmware_paths
        if re.search(pattern, listing, re.IGNORECASE | re.MULTILINE)
    ]
    if leaked_paths and not allow_private_firmware:
        raise SystemExit(
            "private Qualcomm firmware leaked into public SquashFS:\n- "
            + "\n- ".join(leaked_paths)
        )

    boot_modules = run_text(
        (
            str(unsquashfs),
            "-cat",
            str(rootfs),
            "etc/modules.d/30-fs-f2fs",
        )
    )
    if boot_modules.splitlines() != ["f2fs"]:
        raise SystemExit("SquashFS F2FS boot-module list is unexpected")

    gadget = run_text(
        (
            str(unsquashfs),
            "-cat",
            str(rootfs),
            "etc/init.d/ufi001b-usb-gadget",
        )
    )
    for token in (
        "START=90",
        "functions/rndis.usb0",
        "os_desc/use",
        "os_desc/b_vendor_code",
        "MSFT100",
        "compatible_id",
        "5162001",
        "lan interface unavailable; deferred to late rc link",
        "network.lan.device='usb0'",
        "network.lan.netmask='255.255.255.0'",
        "ubus call network reload",
        "delayed-15s",
        "delayed-60s",
    ):
        if token not in gadget:
            raise SystemExit(f"stable USB gadget script missing {token}")
    if "modprobe g_ether" in gadget:
        raise SystemExit("stable rootfs retained the legacy g_ether startup path")
    if "ip link set dev usb0 master br-lan" in gadget:
        raise SystemExit("stable rootfs retained the failed br-lan dependency")
    if "squashfs-root/etc/rc.d/S25ufi001b-usb-gadget" in listing:
        raise SystemExit("stable rootfs retained the early S25 USB gadget link")

    rmtfs = run_text(
        (
            str(unsquashfs),
            "-cat",
            str(rootfs),
            "etc/init.d/rmtfs",
        )
    )
    for token in (
        "PARTNAME=",
        "/dev/disk/by-partlabel",
        "modemst1|modemst2|fsc|fsg",
        "required modem EFS partition links are unavailable",
    ):
        if token not in rmtfs:
            raise SystemExit(f"stable rmtfs init missing {token}")

    rpmsg_hotplug = run_text(
        (
            str(unsquashfs),
            "-cat",
            str(rootfs),
            "etc/hotplug.d/rpmsg/55-rpmsgexport",
        )
    )
    for token in ('devname="${DEVNAME:-${DEVPATH##*/}}"', "/dev/$devname"):
        if token not in rpmsg_hotplug:
            raise SystemExit(f"stable rpmsg hotplug script missing {token}")

    defaults = run_text(
        (
            str(unsquashfs),
            "-cat",
            str(rootfs),
            "etc/uci-defaults/90-ufi001b-system",
        )
    )
    for expected in (
        "luci.main.lang='zh_cn'",
        "system.ufi001b_red_system.trigger='heartbeat'",
        "system.ufi001b_blue_wifi.trigger='phy0tx'",
        "system.ufi001b_green_unused.trigger='none'",
        "zram_size_mb='96'",
        "zram_comp_algo='lzo-rle'",
        "network.lan.netmask='255.255.255.0'",
        "/etc/init.d/zram enable",
    ):
        if expected not in defaults:
            raise SystemExit(f"stable UCI defaults missing {expected}")
    forbidden_connection_defaults = re.compile(
        r"(?:network\.wan|\bctnet\b|\bapn\b|\bsim_pin\b|\boperator(?:_id)?\b|"
        r"\.proto=['\"]modemmanager['\"])",
        re.IGNORECASE,
    )
    if forbidden_connection_defaults.search(defaults):
        raise SystemExit("stable ROM must not preconfigure WAN, APN, SIM, or operator data")

    board_network = run_text(
        (
            str(unsquashfs),
            "-cat",
            str(rootfs),
            "etc/board.d/02_network",
        )
    )
    if forbidden_connection_defaults.search(board_network):
        raise SystemExit("stable board defaults must not create a WAN connection profile")

    repositories = run_text(
        (
            str(unsquashfs),
            "-cat",
            str(rootfs),
            "etc/apk/repositories.d/distfeeds.list",
        )
    )
    if "aarch64_cortex-a53_neon" in repositories:
        raise SystemExit("stable ROM retained the nonexistent neon package feed")
    expected_feeds = ("base", "luci", "packages", "routing", "telephony", "video")
    for feed in expected_feeds:
        pattern = (
            r"^https://downloads\.openwrt\.org/releases/25\.12\.5/packages/"
            rf"aarch64_cortex-a53/{feed}/packages\.adb$"
        )
        if re.search(pattern, repositories, re.MULTILINE) is None:
            raise SystemExit(f"stable ROM missing active official {feed} feed")
    if re.search(
        r"^# https://downloads\.openwrt\.org/releases/25\.12\.5/targets/"
        r"msm89xx/msm8916/packages/packages\.adb$",
        repositories,
        re.MULTILINE,
    ) is None:
        raise SystemExit("stable ROM must disable the unpublished msm89xx target feed")
    if re.search(r"^https?://.*?/openclash/packages\.adb$", repositories, re.MULTILINE):
        raise SystemExit("stable ROM must not enable the nonexistent official OpenClash feed")
    if re.search(r"^# https?://.*?/openclash/packages\.adb$", repositories, re.MULTILINE) is None:
        raise SystemExit("stable ROM should retain the disabled OpenClash feed for provenance")

    with tempfile.TemporaryDirectory(prefix="ufi001b-mihomo-") as temp_dir:
        mihomo = Path(temp_dir) / "clash_meta"
        with mihomo.open("wb") as output:
            result = subprocess.run(
                (
                    str(unsquashfs),
                    "-cat",
                    str(rootfs),
                    "etc/openclash/core/clash_meta",
                ),
                stdout=output,
                stderr=subprocess.PIPE,
                check=False,
            )
        if result.returncode != 0:
            raise SystemExit(
                "cannot extract Mihomo from SquashFS: "
                + result.stderr.decode("utf-8", errors="replace")
            )
        with mihomo.open("rb") as handle:
            header = handle.read(20)
        if len(header) < 20 or header[:4] != b"\x7fELF":
            raise SystemExit("Mihomo core is not ELF")
        if header[4:6] != b"\x02\x01" or int.from_bytes(header[18:20], "little") != 183:
            raise SystemExit("Mihomo core is not a 64-bit little-endian AArch64 ELF")

    with tempfile.TemporaryDirectory(prefix="ufi001b-libelf-") as temp_dir:
        libelf = Path(temp_dir) / "libelf-0.192.so"
        with libelf.open("wb") as output:
            result = subprocess.run(
                (
                    str(unsquashfs),
                    "-cat",
                    str(rootfs),
                    "usr/lib/libelf-0.192.so",
                ),
                stdout=output,
                stderr=subprocess.PIPE,
                check=False,
            )
        if result.returncode != 0:
            raise SystemExit(
                "cannot extract libelf from SquashFS: "
                + result.stderr.decode("utf-8", errors="replace")
            )
        if GNU_SHA1_BUILD_ID_NOTE in libelf.read_bytes():
            raise SystemExit("stable libelf contains a non-deterministic GNU SHA-1 build-id note")

    packages = {line.split(" - ", 1)[0] for line in manifest.splitlines() if " - " in line}
    required_packages = {
        "block-mount",
        "dnsmasq-full",
        "fstools",
        "kmod-fs-f2fs",
        "kmod-ipt-led",
        "kmod-nft-socket",
        "kmod-nft-tproxy",
        "kmod-tun",
        "kmod-usb-gadget-eth",
        "kmod-zram",
        "iptables-mod-led",
        "iptables-nft",
        "luci-i18n-base-zh-cn",
        "luci-i18n-firewall-zh-cn",
        "luci-i18n-package-manager-zh-cn",
        "luci-proto-modemmanager",
        "luci-app-openclash",
        "mihomo-openclash",
        "mkf2fs",
        "modemmanager",
        "zram-swap",
    }
    missing_packages = sorted(required_packages - packages)
    if missing_packages:
        raise SystemExit("stable manifest missing:\n- " + "\n- ".join(missing_packages))
    return rootfs_data_offset, overlay_bytes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", required=True, type=Path)
    parser.add_argument("--allow-private-firmware", action="store_true")
    args = parser.parse_args()

    bin_dir = args.tree / "bin/targets/msm89xx/msm8916"
    fs_token = "squashfs"
    boot = find_one(bin_dir, f"*{fs_token}*boot.img")
    rootfs = find_one(bin_dir, f"*{fs_token}*rootfs.img")

    inspect = load_inspector()
    boot_meta, dtb = inspect(boot)
    validate_boot_build_ids(boot, boot_meta)
    required_dtb_tokens = (
        b"handsome,openstick-ufi001b\0",
        b"linux,extcon-usb-gpio\0",
        b"usb-id-default-state\0",
        b"gpio110\0",
    )
    for token in required_dtb_tokens:
        if token not in dtb:
            raise SystemExit(f"boot DTB missing UFI001B token: {token!r}")
    if b"usb-role-switch\0" in dtb:
        raise SystemExit("boot DTB retained the incompatible PM8916 USB role switch")
    expected_addresses = {
        "kernel_address": "header_kernel_address",
        "ramdisk_address": "header_ramdisk_address",
        "second_address": "header_second_address",
        "tags_address": "header_tags_address",
    }
    for actual_key, reference_key in expected_addresses.items():
        if boot_meta[actual_key] != REFERENCE[reference_key]:
            raise SystemExit(f"boot {actual_key} differs from reference profile")
    if boot_meta["page_size"] != REFERENCE["page_size"]:
        raise SystemExit("boot page size differs from reference profile")
    if boot_meta["cmdline"] != REFERENCE["cmdline"]:
        raise SystemExit("boot cmdline differs from approved p14 profile")

    sizes = {p["name"]: p["size_bytes"] for p in LAYOUT["partitions"]}
    if boot.stat().st_size > sizes["boot"]:
        raise SystemExit("boot image exceeds p12")
    if rootfs.stat().st_size > sizes["rootfs"]:
        raise SystemExit("rootfs image exceeds p14")

    manifest_path = find_one(bin_dir, "*.manifest")
    manifest = manifest_path.read_text(encoding="utf-8", errors="replace")

    rootfs_data_offset, overlay_bytes = validate_stable_rootfs(
        args.tree / "staging_dir/host/bin/unsquashfs4",
        rootfs,
        sizes["rootfs"],
        manifest,
        args.allow_private_firmware,
    )

    config = read_kernel_config(args.tree)
    missing = missing_kernel_config(config)
    if missing:
        raise SystemExit("built kernel config missing:\n- " + "\n- ".join(missing))
    embedded_config = extract_embedded_kernel_config(boot, boot_meta)
    embedded_missing = missing_kernel_config(embedded_config)
    if embedded_missing:
        raise SystemExit("embedded kernel config missing:\n- " + "\n- ".join(embedded_missing))

    stable_required = (
        "CONFIG_BLK_DEV_LOOP=y",
        "CONFIG_F2FS_FS=m",
        "CONFIG_ZRAM=m",
        "CONFIG_ZSMALLOC=m",
    )
    stable_missing = [symbol for symbol in stable_required if symbol not in config]
    if stable_missing:
        raise SystemExit("stable kernel config missing:\n- " + "\n- ".join(stable_missing))
    embedded_stable_missing = [
        symbol for symbol in stable_required if symbol not in embedded_config
    ]
    if embedded_stable_missing:
        raise SystemExit(
            "embedded stable kernel config missing:\n- "
            + "\n- ".join(embedded_stable_missing)
        )

    names = [path.name.lower() for path in bin_dir.iterdir() if path.is_file()]
    forbidden = re.compile(r"(gpt|partition-table|rawprogram|patch\d.*xml|modemst|fsc|fsg|sbl|aboot)")
    offenders = [name for name in names if forbidden.search(name)]
    if offenders:
        raise SystemExit(f"forbidden artifact names: {offenders}")

    private_names = ("qcom-ufi001b-modem", "qcom-ufi001b-wcnss")
    if not args.allow_private_firmware:
        if any(name in manifest for name in private_names):
            raise SystemExit("private Qualcomm firmware leaked into public build")

    message = (
        "validated stable-squashfs: "
        f"boot={boot.stat().st_size} rootfs={rootfs.stat().st_size} "
        f"rootfs_data_offset={rootfs_data_offset} overlay={overlay_bytes}"
    )
    print(message)


if __name__ == "__main__":
    main()
