#!/usr/bin/env python3
"""Propose safe updates for public, independently versioned inputs."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "locks/sources.lock.json"
API = "https://api.github.com"


def request_json(url: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ufi001b-lock-updater"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def request_text(url: str) -> str:
    headers = {"User-Agent": "ufi001b-lock-updater"}
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return response.read().decode("utf-8")


def peel_tag(owner: str, repo: str, tag: str) -> str:
    ref = request_json(f"{API}/repos/{owner}/{repo}/git/ref/tags/{tag}")["object"]
    while ref["type"] == "tag":
        ref = request_json(ref["url"])["object"]
    if ref["type"] != "commit" or not re.fullmatch(r"[0-9a-f]{40}", ref["sha"]):
        raise RuntimeError(f"cannot peel {owner}/{repo} {tag}")
    return ref["sha"]


def latest_openwrt_25_12() -> str:
    tags = request_json(f"{API}/repos/openwrt/openwrt/tags?per_page=100")
    candidates = []
    for item in tags:
        match = re.fullmatch(r"v25\.12\.(\d+)", item["name"])
        if match:
            candidates.append((int(match.group(1)), item["name"]))
    if not candidates:
        raise RuntimeError("no OpenWrt 25.12 patch tag found")
    return max(candidates)[1]


def latest_release(owner: str, repo: str):
    return request_json(f"{API}/repos/{owner}/{repo}/releases/latest")


def replace_make_value(path: Path, key: str, value: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        rf"^{re.escape(key)}:=.*$", f"{key}:={value}", text, count=1, flags=re.MULTILINE
    )
    if count != 1:
        raise RuntimeError(f"could not update {key} in {path}")
    path.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    sources = data["sources"]
    changes = []

    openwrt_tag = latest_openwrt_25_12()
    if openwrt_tag != sources["openwrt"]["version"]:
        commit = peel_tag("openwrt", "openwrt", openwrt_tag)
        changes.append(f"OpenWrt {sources['openwrt']['version']} -> {openwrt_tag}")
        sources["openwrt"].update(version=openwrt_tag, commit=commit)
        feeds = request_text(
            f"https://raw.githubusercontent.com/openwrt/openwrt/{commit}/feeds.conf.default"
        )
        feed_commits = dict(
            re.findall(r"^src-git\s+(packages|luci|routing|telephony|video)\s+\S+\^([0-9a-f]{40})$", feeds, re.MULTILINE)
        )
        if len(feed_commits) != 5:
            raise RuntimeError("new OpenWrt release does not contain five pinned feeds")
        for name, feed_commit in feed_commits.items():
            sources[name]["commit"] = feed_commit

    openclash = latest_release("vernesong", "OpenClash")
    openclash_tag = openclash["tag_name"]
    if openclash_tag != sources["openclash"]["version"]:
        changes.append(f"OpenClash {sources['openclash']['version']} -> {openclash_tag}")
        sources["openclash"].update(
            version=openclash_tag,
            commit=peel_tag("vernesong", "OpenClash", openclash_tag),
        )

    mihomo = latest_release("MetaCubeX", "mihomo")
    mihomo_tag = mihomo["tag_name"]
    asset_name = f"mihomo-linux-arm64-{mihomo_tag}.gz"
    assets = {asset["name"]: asset for asset in mihomo["assets"]}
    if asset_name not in assets:
        raise RuntimeError(f"Mihomo release lacks {asset_name}")
    asset = assets[asset_name]
    digest = asset.get("digest", "")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise RuntimeError("GitHub did not provide a trusted SHA-256 for the Mihomo asset")
    if mihomo_tag != sources["mihomo"]["version"]:
        changes.append(f"Mihomo {sources['mihomo']['version']} -> {mihomo_tag}")
        sources["mihomo"].update(
            version=mihomo_tag,
            commit=peel_tag("MetaCubeX", "mihomo", mihomo_tag),
            asset=asset_name,
            asset_url=asset["browser_download_url"],
            asset_size=asset["size"],
            asset_sha256=digest.removeprefix("sha256:"),
        )
        if args.write:
            makefile = ROOT / "package/mihomo-openclash/Makefile"
            replace_make_value(makefile, "PKG_VERSION", mihomo_tag.removeprefix("v"))
            replace_make_value(makefile, "PKG_HASH", digest.removeprefix("sha256:"))

    if not changes:
        print("all automatically tracked dependencies are current")
        return
    print("\n".join(changes))
    if args.write:
        LOCK_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
