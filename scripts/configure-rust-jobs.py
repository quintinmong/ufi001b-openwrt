#!/usr/bin/env python3
"""Constrain Rust bootstrap resources after OpenWrt creates bootstrap.toml."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


LLVM_TARGETS = "AArch64;X86"


def set_section_setting(
    lines: list[str], section: str, key: str, value: str
) -> None:
    try:
        section_start = lines.index(f"[{section}]")
    except ValueError as error:
        raise SystemExit(f"Rust bootstrap.toml has no [{section}] section") from error
    section_end = next(
        (
            index
            for index in range(section_start + 1, len(lines))
            if re.fullmatch(r"\[.+]", lines[index])
        ),
        len(lines),
    )
    setting_lines = [
        index
        for index in range(section_start + 1, section_end)
        if re.fullmatch(rf"{re.escape(key)}\s*=.*", lines[index])
    ]
    setting = f"{key} = {value}"
    if len(setting_lines) > 1:
        raise SystemExit(
            f"Rust [{section}] section contains multiple {key} settings"
        )
    if setting_lines:
        lines[setting_lines[0]] = setting
    else:
        lines.insert(section_start + 1, setting)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", required=True, type=Path)
    parser.add_argument("--jobs", required=True, type=int)
    args = parser.parse_args()
    if args.jobs < 1:
        raise SystemExit("Rust jobs must be positive")

    matches = list(
        (args.tree / "build_dir").glob(
            "target-*/host/rustc-*-src/bootstrap.toml"
        )
    )
    if len(matches) != 1:
        raise SystemExit(f"expected one Rust bootstrap.toml, found {len(matches)}")

    path = matches[0]
    lines = path.read_text(encoding="utf-8").splitlines()
    set_section_setting(lines, "build", "jobs", str(args.jobs))
    set_section_setting(lines, "llvm", "targets", f'"{LLVM_TARGETS}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"configured Rust bootstrap jobs={args.jobs} "
        f"llvm-targets={LLVM_TARGETS}: {path}"
    )


if __name__ == "__main__":
    main()
