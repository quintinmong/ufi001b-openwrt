#!/usr/bin/env python3
"""Validate that build metadata cannot address protected UFI001B partitions."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "board" / "ufi001b" / "partition-layout.json"


def main() -> None:
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    sector_bytes = layout["logical_sector_bytes"]
    emmc_bytes = layout["emmc_size_bytes"]
    if sector_bytes != 512 or emmc_bytes != 3_875_536_896:
        raise SystemExit("unexpected UFI001B eMMC geometry")
    if emmc_bytes % sector_bytes:
        raise SystemExit("eMMC size is not sector aligned")

    partitions = layout["partitions"]
    if [partition["number"] for partition in partitions] != list(range(1, 15)):
        raise SystemExit("partition numbering must be exactly 1 through 14")
    names = [partition["name"] for partition in partitions]
    if len(set(names)) != len(names):
        raise SystemExit("partition names must be unique")
    previous_last = -1
    for partition in sorted(partitions, key=lambda item: item["first_lba"]):
        first_lba = partition["first_lba"]
        last_lba = partition["last_lba"]
        expected_bytes = (last_lba - first_lba + 1) * sector_bytes
        if first_lba <= previous_last:
            raise SystemExit(f"overlapping partition geometry: {partition['name']}")
        if partition["size_bytes"] != expected_bytes:
            raise SystemExit(f"partition size mismatch: {partition['name']}")
        if last_lba >= emmc_bytes // sector_bytes:
            raise SystemExit(f"partition outside eMMC: {partition['name']}")
        previous_last = last_lba

    allowed = set(layout["allowed_build_targets"])
    if allowed != {"boot", "rootfs"}:
        raise SystemExit(f"unexpected writable set: {sorted(allowed)}")
    if layout["gpt_mutation_allowed"] is not False:
        raise SystemExit("GPT mutation must remain disabled")
    for partition in partitions:
        if partition["name"] in allowed:
            continue
        if "write" not in partition["policy"] and partition["policy"] != "protected":
            raise SystemExit(f"ambiguous protected policy: {partition}")
    by_name = {partition["name"]: partition for partition in partitions}
    expected_writable_geometry = {
        "boot": (12, 526_336, 657_407, 67_108_864),
        "rootfs": (14, 659_456, 7_569_374, 3_537_878_528),
    }
    for name, expected in expected_writable_geometry.items():
        actual = by_name[name]
        observed = (
            actual["number"],
            actual["first_lba"],
            actual["last_lba"],
            actual["size_bytes"],
        )
        if observed != expected:
            raise SystemExit(f"unexpected writable geometry for {name}: {observed}")
    if by_name["rootfs"]["last_lba"] != emmc_bytes // sector_bytes - 34:
        raise SystemExit("rootfs must end immediately before the 33-sector backup GPT")
    print("partition policy OK: only p12 boot and p14 rootfs are build outputs")


if __name__ == "__main__":
    main()
