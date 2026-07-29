#!/usr/bin/env python3
"""Cap Rust bootstrap parallelism after OpenWrt creates bootstrap.toml."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


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
    try:
        section_start = lines.index("[build]")
    except ValueError as error:
        raise SystemExit("Rust bootstrap.toml has no [build] section") from error
    section_end = next(
        (index for index in range(section_start + 1, len(lines)) if re.fullmatch(r"\[.+]", lines[index])),
        len(lines),
    )
    job_lines = [
        index
        for index in range(section_start + 1, section_end)
        if re.fullmatch(r"jobs\s*=.*", lines[index])
    ]
    setting = f"jobs = {args.jobs}"
    if len(job_lines) > 1:
        raise SystemExit("Rust [build] section contains multiple jobs settings")
    if job_lines:
        lines[job_lines[0]] = setting
    else:
        lines.insert(section_start + 1, setting)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"configured Rust bootstrap jobs={args.jobs}: {path}")


if __name__ == "__main__":
    main()
