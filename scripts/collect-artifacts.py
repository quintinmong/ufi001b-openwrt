#!/usr/bin/env python3
"""Copy a small allow-listed artifact set and generate hashes/SBOM."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    profile = "stable-squashfs"

    source = args.tree / "bin/targets/msm89xx/msm8916"
    if not source.is_dir():
        raise SystemExit(f"build output directory does not exist: {source}")
    if args.out.exists() and any(args.out.iterdir()):
        raise SystemExit(
            f"refusing to mix a new build with existing artifacts: {args.out}"
        )
    args.out.mkdir(parents=True, exist_ok=True)
    fs_token = "squashfs"
    selected: list[Path] = []
    for image_kind in ("boot", "rootfs"):
        matches = list(source.glob(f"*{fs_token}*{image_kind}.img"))
        if len(matches) != 1:
            raise SystemExit(
                f"expected one {fs_token} {image_kind}.img, found {len(matches)}"
            )
        selected.extend(matches)

    for pattern in ("*.manifest", "*.buildinfo", "profiles.json"):
        selected.extend(path for path in source.glob(pattern) if path.is_file())

    copied = []
    for path in selected:
        destination = args.out / path.name
        shutil.copy2(path, destination)
        copied.append(destination)

    public_key = args.tree / "public-key.pem"
    if not public_key.is_file():
        raise SystemExit("OpenWrt APK signing public key is missing")
    public_key_artifact = args.out / "apk-signing-public-key.pem"
    shutil.copy2(public_key, public_key_artifact)
    copied.append(public_key_artifact)

    package_roots = list((args.tree / "bin/packages").glob("aarch64_cortex-a53*"))
    for prefix in ("luci-app-openclash-", "mihomo-openclash-"):
        matches = [
            path
            for package_root in package_roots
            for path in package_root.rglob(f"{prefix}*.apk")
        ]
        if len(matches) != 1:
            raise SystemExit(f"expected one {prefix} APK, found {len(matches)}")
        destination = args.out / matches[0].name
        shutil.copy2(matches[0], destination)
        copied.append(destination)

    packages = []
    for manifest in args.out.glob("*.manifest"):
        for line in manifest.read_text(encoding="utf-8", errors="replace").splitlines():
            if " - " in line:
                name, version = line.split(" - ", 1)
                packages.append({
                    "SPDXID": f"SPDXRef-Package-{len(packages)}",
                    "name": name,
                    "versionInfo": version,
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                })
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0"))
    created = dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest_fingerprint = hashlib.sha256(
        json.dumps(packages, sort_keys=True).encode("utf-8")
    ).hexdigest()
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"ufi001b-openwrt-{profile}",
        "documentNamespace": f"https://spdx.org/spdxdocs/ufi001b-{profile}-{manifest_fingerprint}",
        "creationInfo": {"created": created, "creators": ["Tool: ufi001b collect-artifacts.py"]},
        "packages": packages,
    }
    sbom_path = args.out / "sbom.spdx.json"
    sbom_path.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    copied.append(sbom_path)

    checksums = "".join(f"{sha256(path)}  {path.name}\n" for path in sorted(copied))
    (args.out / "SHA256SUMS").write_text(checksums, encoding="utf-8")
    print(f"collected {len(copied)} artifacts in {args.out}")


if __name__ == "__main__":
    main()
