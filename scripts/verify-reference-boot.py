#!/usr/bin/env python3
"""Check the private reference boot image against committed public metadata."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "board" / "ufi001b" / "reference" / "handsomemod-bootimg.json"


def load_inspector():
    module_path = Path(__file__).with_name("extract-reference-boot.py")
    spec = importlib.util.spec_from_file_location("extract_reference_boot", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.inspect


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("boot_image", type=Path)
    args = parser.parse_args()

    expected = json.loads(REFERENCE.read_text(encoding="utf-8"))
    actual, _ = load_inspector()(args.boot_image)
    mapping = {
        "source_sha256": "image_sha256",
        "page_size": "page_size",
        "cmdline": "cmdline",
        "header_kernel_address": "kernel_address",
        "header_ramdisk_address": "ramdisk_address",
        "header_second_address": "second_address",
        "header_tags_address": "tags_address",
        "kernel_size_bytes": "kernel_size_bytes",
        "kernel_sha256": "kernel_sha256",
        "ramdisk_size_bytes": "ramdisk_size_bytes",
        "appended_dtb_offset_in_kernel": "appended_dtb_offset_in_kernel",
        "appended_dtb_size_bytes": "appended_dtb_size_bytes",
        "appended_dtb_sha256": "appended_dtb_sha256",
    }
    failures = []
    for expected_key, actual_key in mapping.items():
        if expected[expected_key] != actual[actual_key]:
            failures.append(
                f"{expected_key}: expected {expected[expected_key]!r}, got {actual[actual_key]!r}"
            )

    base = int(expected["base"], 16)
    address_checks = {
        "header_kernel_address": "kernel_offset",
        "header_ramdisk_address": "ramdisk_offset",
        "header_second_address": "second_offset",
        "header_tags_address": "tags_offset",
    }
    for address_key, offset_key in address_checks.items():
        calculated = base + int(expected[offset_key], 16)
        observed = int(expected[address_key], 16)
        if calculated != observed:
            failures.append(
                f"{address_key} != base + {offset_key}: 0x{observed:08x} != 0x{calculated:08x}"
            )

    if failures:
        print("reference boot verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)
    print("reference boot image and mkbootimg offsets OK")


if __name__ == "__main__":
    main()
