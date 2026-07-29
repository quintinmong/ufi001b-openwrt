#!/usr/bin/env python3
"""Inspect an Android boot image v0 and optionally extract its appended DTB."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


FDT_MAGIC = b"\xd0\x0d\xfe\xed"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cstring(data: bytes) -> str:
    return data.split(b"\0", 1)[0].decode("ascii", errors="strict")


def inspect(path: Path) -> tuple[dict[str, object], bytes]:
    image = path.read_bytes()
    if len(image) < 608 or image[:8] != b"ANDROID!":
        raise ValueError("not an Android boot image v0")

    kernel_size, kernel_addr = struct.unpack_from("<II", image, 8)
    ramdisk_size, ramdisk_addr = struct.unpack_from("<II", image, 16)
    second_size, second_addr = struct.unpack_from("<II", image, 24)
    tags_addr, page_size, dt_size = struct.unpack_from("<III", image, 32)
    if page_size < 512 or page_size & (page_size - 1):
        raise ValueError(f"invalid page size: {page_size}")

    kernel = image[page_size : page_size + kernel_size]
    if len(kernel) != kernel_size:
        raise ValueError("truncated kernel")

    candidates: list[tuple[int, int, bytes]] = []
    offset = 0
    while True:
        offset = kernel.find(FDT_MAGIC, offset)
        if offset < 0:
            break
        if offset + 8 <= len(kernel):
            total_size = struct.unpack_from(">I", kernel, offset + 4)[0]
            if 40 <= total_size <= len(kernel) - offset:
                candidates.append((offset, total_size, kernel[offset : offset + total_size]))
        offset += 1
    if len(candidates) != 1:
        raise ValueError(f"expected one appended DTB, found {len(candidates)}")

    dtb_offset, dtb_size, dtb = candidates[0]
    name = cstring(image[48:64])
    cmdline = cstring(image[64:576])
    extra_cmdline = cstring(image[608:1632]) if len(image) >= 1632 else ""
    cmdline = (cmdline + extra_cmdline).strip()

    metadata: dict[str, object] = {
        "format": "Android boot image v0",
        "image_size_bytes": len(image),
        "image_sha256": sha256(image),
        "board_name": name,
        "page_size": page_size,
        "kernel_address": f"0x{kernel_addr:08x}",
        "ramdisk_address": f"0x{ramdisk_addr:08x}",
        "second_address": f"0x{second_addr:08x}",
        "tags_address": f"0x{tags_addr:08x}",
        "cmdline": cmdline,
        "kernel_size_bytes": kernel_size,
        "kernel_sha256": sha256(kernel),
        "ramdisk_size_bytes": ramdisk_size,
        "second_size_bytes": second_size,
        "header_dt_size_bytes": dt_size,
        "appended_dtb_offset_in_kernel": dtb_offset,
        "appended_dtb_size_bytes": dtb_size,
        "appended_dtb_sha256": sha256(dtb),
    }
    return metadata, dtb


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("boot_image", type=Path)
    parser.add_argument("--extract-dtb", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    metadata, dtb = inspect(args.boot_image)
    encoded = json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    print(encoded, end="")
    if args.extract_dtb:
        args.extract_dtb.parent.mkdir(parents=True, exist_ok=True)
        args.extract_dtb.write_bytes(dtb)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded, encoding="utf-8")


if __name__ == "__main__":
    main()
