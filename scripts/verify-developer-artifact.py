#!/usr/bin/env python3
"""Offline verification for a downloaded UFI001B developer-ext4 artifact."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = json.loads((ROOT / "board/ufi001b/partition-layout.json").read_text(encoding="utf-8"))
REFERENCE = json.loads(
    (ROOT / "board/ufi001b/reference/handsomemod-bootimg.json").read_text(encoding="utf-8")
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BOOT_INSPECTOR = load_module("boot_inspector", ROOT / "scripts/extract-reference-boot.py")
BUILD_VALIDATOR = load_module("build_validator", ROOT / "scripts/validate-build.py")


def find_one(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    if len(matches) != 1:
        raise SystemExit(f"expected one {pattern}, found {len(matches)}")
    return matches[0]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hashes(directory: Path) -> int:
    sums = directory / "SHA256SUMS"
    if not sums.is_file():
        raise SystemExit("SHA256SUMS is missing")
    entries: dict[str, str] = {}
    for line in sums.read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\]+)", line)
        if match is None:
            raise SystemExit(f"invalid SHA256SUMS line: {line!r}")
        expected, name = match.groups()
        if name in entries:
            raise SystemExit(f"duplicate SHA256SUMS entry: {name}")
        path = directory / name
        if not path.is_file():
            raise SystemExit(f"SHA256SUMS entry is missing: {name}")
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"SHA-256 mismatch for {name}: {actual}")
        entries[name] = expected
    return len(entries)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_dir", type=Path)
    parser.add_argument("--e2fsck", default=shutil.which("e2fsck"))
    args = parser.parse_args()

    directory = args.artifact_dir.resolve()
    if not directory.is_dir():
        raise SystemExit(f"artifact directory does not exist: {directory}")
    hash_count = verify_hashes(directory)
    boot = find_one(directory, "*-ext4-boot.img")
    rootfs = find_one(directory, "*-ext4-rootfs.img")

    boot_meta, dtb = BOOT_INSPECTOR.inspect(boot)
    recorded_meta_path = directory / "boot-metadata.json"
    if recorded_meta_path.is_file():
        recorded_meta = json.loads(recorded_meta_path.read_text(encoding="utf-8"))
        if recorded_meta != boot_meta:
            raise SystemExit("boot-metadata.json does not match the boot image")
    for token in (
        b"handsome,openstick-ufi001b\0",
        b"linux,extcon-usb-gpio\0",
        b"usb-id-default-state\0",
        b"gpio110\0",
    ):
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

    sizes = {partition["name"]: partition["size_bytes"] for partition in LAYOUT["partitions"]}
    if boot.stat().st_size > sizes["boot"]:
        raise SystemExit("boot image exceeds p12")
    if rootfs.stat().st_size > sizes["rootfs"]:
        raise SystemExit("rootfs image exceeds p14")
    with rootfs.open("rb") as handle:
        handle.seek(1024 + 56)
        if handle.read(2) != b"\x53\xef":
            raise SystemExit("rootfs does not contain an ext4 superblock")

    if not args.e2fsck:
        raise SystemExit("e2fsck is required; pass --e2fsck PATH")
    fsck = subprocess.run(
        (args.e2fsck, "-fn", str(rootfs)),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if fsck.returncode != 0:
        raise SystemExit(f"ext4 consistency check failed:\n{fsck.stdout}")

    config = BUILD_VALIDATOR.extract_embedded_kernel_config(boot, boot_meta)
    missing = BUILD_VALIDATOR.missing_kernel_config(config)
    if missing:
        raise SystemExit("embedded kernel config missing:\n- " + "\n- ".join(missing))
    buildinfo = (directory / "config.buildinfo").read_text(encoding="utf-8")
    for symbol in (
        "CONFIG_KERNEL_DEVTMPFS=y",
        "CONFIG_KERNEL_DEVTMPFS_MOUNT=y",
    ):
        if symbol not in buildinfo:
            raise SystemExit(f"config.buildinfo missing {symbol}")
    manifest = find_one(directory, "*.manifest").read_text(encoding="utf-8")
    if re.search(r"^kmod-mmc - \S+$", manifest, flags=re.MULTILINE) is None:
        raise SystemExit("package manifest missing kmod-mmc")

    print(
        "verified developer artifact: "
        f"hashes={hash_count} boot={boot.stat().st_size} rootfs={rootfs.stat().st_size} "
        "embedded-root-chain=ok manifest-mmc=ok ext4=ok"
    )


if __name__ == "__main__":
    main()
