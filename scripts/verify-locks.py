#!/usr/bin/env python3
"""Validate immutable source locks without downloading build inputs."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "locks" / "sources.lock.json"
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    print(f"lock validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if data.get("schema") != 1:
        fail("unsupported schema")

    sources = data.get("sources")
    if not isinstance(sources, dict) or not sources:
        fail("sources must be a non-empty object")

    for name, source in sources.items():
        if not isinstance(source, dict):
            fail(f"{name} must be an object")
        url = source.get("url", "")
        if not isinstance(url, str) or not url.startswith("https://github.com/"):
            fail(f"{name}.url is not an HTTPS GitHub URL")
        commit = source.get("commit")
        if commit is not None and not SHA1_RE.fullmatch(commit):
            fail(f"{name}.commit is not a full 40-character SHA-1")
        source_digest = source.get("source_sha256")
        if source_digest is not None and not SHA256_RE.fullmatch(source_digest):
            fail(f"{name}.source_sha256 is not a SHA-256 digest")

    qcom_firmware = sources.get("qcom_firmware_reference", {})
    if qcom_firmware.get("redistribution") != "private-review-required":
        fail("qcom_firmware_reference must remain private-review-required")

    mihomo = sources.get("mihomo", {})
    digest = mihomo.get("asset_sha256", "")
    if not SHA256_RE.fullmatch(digest):
        fail("mihomo.asset_sha256 is not a SHA-256 digest")
    if mihomo.get("asset_size", 0) <= 0:
        fail("mihomo.asset_size must be positive")

    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
    print(f"locks OK: {len(sources)} sources")
    print(f"lockset sha256: {hashlib.sha256(canonical).hexdigest()}")


if __name__ == "__main__":
    main()
