#!/usr/bin/env python3
"""Create the corresponding-source asset required for public binary releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = ROOT / "locks" / "sources.lock.json"
ARCHIVE_NAME = "ufi001b-openwrt-corresponding-source.tar.zst"
MIHOMO_SOURCE_PREFIX = "mihomo-source-"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_mihomo_source(tree: Path) -> Path:
    lock = json.loads(LOCK_FILE.read_text(encoding="utf-8"))["sources"]["mihomo"]
    commit = lock["commit"]
    destination = tree / "dl" / f"{MIHOMO_SOURCE_PREFIX}{commit}.tar.gz"
    expected = lock["source_sha256"]
    if destination.is_file() and sha256(destination) == expected:
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    try:
        request = urllib.request.Request(
            lock["source_url"],
            headers={"User-Agent": "ufi001b-openwrt-source-compliance"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            with temporary.open("wb") as output:
                shutil.copyfileobj(response, output)
        if sha256(temporary) != expected:
            raise SystemExit("Mihomo corresponding-source archive hash mismatch")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def reject_forbidden_inputs(tree: Path) -> None:
    forbidden_names = (
        "private-key.pem",
        "qcom-firmware-ufi001b",
        "openstick-ufi001b-modem",
        "openstick-ufi001b-nv",
    )
    for path in (tree / "dl").glob("*"):
        lowered = path.name.lower()
        if any(token in lowered for token in forbidden_names):
            raise SystemExit(f"refusing proprietary or private source input: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    tree = args.tree.resolve()
    if not (tree / ".config").is_file() or not (tree / "dl").is_dir():
        raise SystemExit("prepared OpenWrt source tree and download directory required")
    if shutil.which("tar") is None or shutil.which("zstd") is None:
        raise SystemExit("tar and zstd are required")

    ensure_mihomo_source(tree)
    reject_forbidden_inputs(tree)

    args.out.mkdir(parents=True, exist_ok=True)
    archive = args.out / ARCHIVE_NAME
    if archive.exists():
        raise SystemExit(f"refusing to overwrite existing source archive: {archive}")

    excludes = (
        "./.git",
        "./build_dir",
        "./staging_dir",
        "./tmp",
        "./logs",
        "./bin",
        "./private-key.pem",
        "./public-key.pem",
        "./key-build*",
        "./dl/mihomo-linux-arm64-*.gz",
    )
    command = ["tar", "--zstd", "-cf", str(archive)]
    command.extend(f"--exclude={pattern}" for pattern in excludes)
    command.extend(("-C", str(tree), "."))
    subprocess.run(command, check=True)

    checksum = args.out / "corresponding-source-SHA256SUMS"
    checksum.write_text(f"{sha256(archive)}  {archive.name}\n", encoding="utf-8")
    print(f"created corresponding source: {archive}")


if __name__ == "__main__":
    main()
