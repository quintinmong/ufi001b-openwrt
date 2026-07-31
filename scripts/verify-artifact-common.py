#!/usr/bin/env python3
"""Common offline checks for downloaded UFI001B firmware artifacts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = json.loads(
    (ROOT / "board/ufi001b/partition-layout.json").read_text(encoding="utf-8")
)
REFERENCE = json.loads(
    (ROOT / "board/ufi001b/reference/handsomemod-bootimg.json").read_text(
        encoding="utf-8"
    )
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BOOT_INSPECTOR = load_module(
    "boot_inspector", ROOT / "scripts/extract-reference-boot.py"
)


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


def validate_common(
    directory: Path, fs_token: str
) -> tuple[Path, Path, dict[str, object]]:
    boot = find_one(directory, f"*-{fs_token}-boot.img")
    rootfs = find_one(directory, f"*-{fs_token}-rootfs.img")

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

    sizes = {
        partition["name"]: partition["size_bytes"]
        for partition in LAYOUT["partitions"]
    }
    if boot.stat().st_size > sizes["boot"]:
        raise SystemExit("boot image exceeds p12")
    if rootfs.stat().st_size > sizes["rootfs"]:
        raise SystemExit("rootfs image exceeds p14")
    return boot, rootfs, boot_meta
