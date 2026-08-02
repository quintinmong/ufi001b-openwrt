#!/usr/bin/env python3
"""Offline verification for a downloaded UFI001B stable-squashfs artifact."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMMON = load_module(
    "artifact_common", ROOT / "scripts/verify-artifact-common.py"
)
BUILD_VALIDATOR = load_module("build_validator", ROOT / "scripts/validate-build.py")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_dir", type=Path)
    parser.add_argument("--unsquashfs", default=shutil.which("unsquashfs"))
    args = parser.parse_args()

    directory = args.artifact_dir.resolve()
    if not directory.is_dir():
        raise SystemExit(f"artifact directory does not exist: {directory}")
    if not args.unsquashfs:
        raise SystemExit("unsquashfs is required; pass --unsquashfs PATH")

    hash_count = COMMON.verify_hashes(directory)
    boot, rootfs, boot_meta = COMMON.validate_common(directory, "squashfs")
    manifest = COMMON.find_one(directory, "*.manifest").read_text(encoding="utf-8")
    if re.search(r"^kmod-mmc - \S+$", manifest, flags=re.MULTILINE) is None:
        raise SystemExit("package manifest missing kmod-mmc")

    config = BUILD_VALIDATOR.extract_embedded_kernel_config(boot, boot_meta)
    missing = BUILD_VALIDATOR.missing_kernel_config(config)
    stable_required = (
        "CONFIG_BLK_DEV_LOOP=y",
        "CONFIG_F2FS_FS=m",
        "CONFIG_ZRAM=m",
        "CONFIG_ZSMALLOC=m",
    )
    missing.extend(symbol for symbol in stable_required if symbol not in config)
    if missing:
        raise SystemExit("embedded stable kernel config missing:\n- " + "\n- ".join(missing))

    buildinfo = (directory / "config.buildinfo").read_text(encoding="utf-8")
    for symbol in (
        "CONFIG_KERNEL_DEVTMPFS=y",
        "CONFIG_KERNEL_DEVTMPFS_MOUNT=y",
        "CONFIG_PACKAGE_kmod-fs-f2fs=y",
        "CONFIG_PACKAGE_kmod-ipt-led=y",
        "CONFIG_PACKAGE_iptables-mod-led=y",
        "CONFIG_PACKAGE_iptables-nft=y",
        "CONFIG_PACKAGE_luci-i18n-base-zh-cn=y",
        "CONFIG_PACKAGE_luci-i18n-firewall-zh-cn=y",
        "CONFIG_PACKAGE_luci-i18n-package-manager-zh-cn=y",
        "CONFIG_PACKAGE_mkf2fs=y",
    ):
        if symbol not in buildinfo:
            raise SystemExit(f"config.buildinfo missing {symbol}")

    partition_bytes = next(
        partition["size_bytes"]
        for partition in COMMON.LAYOUT["partitions"]
        if partition["name"] == "rootfs"
    )
    offset, overlay_bytes = BUILD_VALIDATOR.validate_stable_rootfs(
        Path(args.unsquashfs), rootfs, partition_bytes, manifest
    )
    print(
        "verified stable artifact: "
        f"hashes={hash_count} boot={boot.stat().st_size} rootfs={rootfs.stat().st_size} "
        f"rootfs_data_offset={offset} overlay={overlay_bytes} "
        "embedded-root-chain=ok squashfs=ok fstools-marker=ok"
    )


if __name__ == "__main__":
    main()
