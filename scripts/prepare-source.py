#!/usr/bin/env python3
"""Prepare a pinned OpenWrt tree and apply the UFI001B source overlay."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = ROOT / "locks" / "sources.lock.json"
OVERLAY = ROOT / "openwrt-overlay"
OPENWRT_PATCHES = ROOT / "patches" / "openwrt"
LOCAL_PACKAGES = (
    "ufi001b-base",
    "mihomo-openclash",
    "qrtr",
    "rmtfs",
    "rpmsgexport",
    "qcom-firmware-ufi001b",
)
ALLOWED_DIRTY_PREFIXES = (
    "target/linux/msm89xx/",
    "tools/mkbootimg/",
    "package/ufi001b-base/",
    "package/mihomo-openclash/",
    "package/qrtr/",
    "package/rmtfs/",
    "package/rpmsgexport/",
    "package/qcom-firmware-ufi001b/",
)
ALLOWED_DIRTY_FILES = {
    "tools/Makefile",
    "feeds.conf",
    ".ufi001b-overlay-state.json",
    "package/libs/elfutils/Makefile",
}
TOOLS_MARKER = "tools-$(CONFIG_TARGET_msm89xx) += mkbootimg"


def run(*args: str, cwd: Path, capture: bool = False) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout.rstrip("\r\n") if capture else ""


def dirty_paths(tree: Path) -> list[str]:
    output = run("git", "status", "--porcelain", "--untracked-files=all", cwd=tree, capture=True)
    paths = []
    for line in output.splitlines():
        path = line[3:].replace("\\", "/")
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return paths


def is_managed(path: str) -> bool:
    return path in ALLOWED_DIRTY_FILES or path.startswith(ALLOWED_DIRTY_PREFIXES)


def copy_tree(source: Path, destination: Path) -> None:
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def apply_openwrt_patches(tree: Path) -> None:
    for patch in sorted(OPENWRT_PATCHES.glob("*.patch")):
        reversed_check = subprocess.run(
            ("git", "apply", "--reverse", "--check", str(patch)),
            cwd=tree,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if reversed_check.returncode == 0:
            continue
        run("git", "apply", "--check", str(patch), cwd=tree)
        run("git", "apply", str(patch), cwd=tree)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", type=Path, default=ROOT / "work" / "openwrt")
    parser.add_argument("--update-feeds", action="store_true")
    parser.add_argument("--install-feeds", action="store_true")
    args = parser.parse_args()
    if args.install_feeds:
        args.update_feeds = True

    locks = json.loads(LOCK_FILE.read_text(encoding="utf-8"))["sources"]
    tree = args.tree.resolve()
    if not (tree / ".git").is_dir():
        tree.parent.mkdir(parents=True, exist_ok=True)
        run(
            "git", "clone", "--filter=blob:none",
            locks["openwrt"]["url"], str(tree), cwd=tree.parent,
        )

    shallow = run(
        "git", "rev-parse", "--is-shallow-repository", cwd=tree, capture=True
    )
    if shallow == "true":
        run("git", "fetch", "--unshallow", "--filter=blob:none", "origin", cwd=tree)

    unexpected = [path for path in dirty_paths(tree) if not is_managed(path)]
    if unexpected:
        print("refusing to overwrite an OpenWrt tree with unrelated changes:", file=sys.stderr)
        for path in unexpected:
            print(f"- {path}", file=sys.stderr)
        raise SystemExit(1)

    expected_commit = locks["openwrt"]["commit"]
    head = run("git", "rev-parse", "HEAD", cwd=tree, capture=True)
    if head != expected_commit:
        if dirty_paths(tree):
            raise SystemExit("OpenWrt HEAD differs from lock and managed overlay changes exist")
        run("git", "fetch", "origin", expected_commit, cwd=tree)
        run("git", "checkout", "--detach", expected_commit, cwd=tree)

    copy_tree(OVERLAY, tree)
    for package_name in LOCAL_PACKAGES:
        copy_tree(ROOT / "package" / package_name, tree / "package" / package_name)
    apply_openwrt_patches(tree)

    tools_makefile = tree / "tools" / "Makefile"
    tools_text = tools_makefile.read_text(encoding="utf-8")
    if TOOLS_MARKER not in tools_text:
        anchor = "tools-y += zlib\n"
        if anchor not in tools_text:
            raise SystemExit("tools/Makefile anchor not found")
        tools_makefile.write_text(
            tools_text.replace(anchor, anchor + TOOLS_MARKER + "\n", 1), encoding="utf-8"
        )

    feed_names = ("packages", "luci", "routing", "telephony", "video", "openclash")
    feed_text = "".join(
        f"src-git {name} {locks[name]['url']}^{locks[name]['commit']}\n"
        for name in feed_names
    )
    (tree / "feeds.conf").write_text(feed_text, encoding="utf-8")

    state = {
        "schema": 1,
        "openwrt_commit": expected_commit,
        "base_files_commit_count": int(
            run(
                "git",
                "rev-list",
                "--count",
                "HEAD",
                "--",
                "package/base-files",
                cwd=tree,
                capture=True,
            )
        ),
        "feeds": {name: locks[name]["commit"] for name in feed_names},
    }
    (tree / ".ufi001b-overlay-state.json").write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if args.update_feeds:
        run("./scripts/feeds", "update", "-a", cwd=tree)
    if args.install_feeds:
        run("./scripts/feeds", "install", "-a", cwd=tree)

    print(f"prepared {tree}")
    print(f"OpenWrt {expected_commit}")
    print("no firmware, backup, partition table, or device was modified")


if __name__ == "__main__":
    main()
