from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "configure_rust_jobs", ROOT / "scripts/configure-rust-jobs.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RustBootstrapConfigurationTests(unittest.TestCase):
    def test_inserts_bounded_jobs_and_required_llvm_targets(self) -> None:
        lines = [
            "profile = 'dist'",
            "[build]",
            "extended = true",
            "[llvm]",
            "download-ci-llvm = false",
        ]

        MODULE.set_section_setting(lines, "build", "jobs", "3")
        MODULE.set_section_setting(
            lines, "llvm", "targets", f'"{MODULE.LLVM_TARGETS}"'
        )

        self.assertIn("jobs = 3", lines)
        self.assertIn('targets = "AArch64;X86"', lines)
        self.assertEqual(lines.count("jobs = 3"), 1)

    def test_replaces_existing_values(self) -> None:
        lines = [
            "[build]",
            "jobs = 99",
            "[llvm]",
            'targets = "all"',
        ]

        MODULE.set_section_setting(lines, "build", "jobs", "2")
        MODULE.set_section_setting(
            lines, "llvm", "targets", f'"{MODULE.LLVM_TARGETS}"'
        )

        self.assertEqual(lines[1], "jobs = 2")
        self.assertEqual(lines[3], 'targets = "AArch64;X86"')

    def test_rejects_duplicate_setting(self) -> None:
        lines = ["[build]", "jobs = 2", "jobs=3", "[llvm]"]

        with self.assertRaisesRegex(SystemExit, "multiple jobs settings"):
            MODULE.set_section_setting(lines, "build", "jobs", "1")


if __name__ == "__main__":
    unittest.main()
