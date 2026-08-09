#!/usr/bin/env python3
"""Unit tests for scripts/runtime_smoke.py."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import runtime_smoke as rs  # noqa: E402


class HexAndMatchTests(unittest.TestCase):
    def test_parse_hex_and_cstool_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.hex"
            path.write_text(
                "8d 4c 32 08 01 d8 81 c6 34 12 00 00 00 91 92  # skipdata\n",
                encoding="utf-8",
            )
            blob = rs.parse_hex_file(path)
            self.assertEqual(
                blob,
                bytes.fromhex("8d4c320801d881c634120000009192"),
            )
            self.assertTrue(rs.bytes_to_cstool_hex(blob).startswith("8d 4c 32"))

    def test_match_asm_texts(self) -> None:
        ok, msg = rs.match_asm_texts(
            "0x1000: push rbp\n0x1001: mov rax, qword ptr [rip + 0x13b8]\n",
            ["push rbp", "mov rax, qword ptr [rip + 0x13b8]"],
        )
        self.assertTrue(ok)
        self.assertIn("matched 2", msg)
        bad, detail = rs.match_asm_texts("push rbp\n", ["push rbp", "lea ecx"])
        self.assertFalse(bad)
        self.assertIn("lea ecx", detail)
        # cstool uses TAB between mnemonic and operands.
        tab_ok, _ = rs.match_asm_texts(
            "1000  55                                               push\trbp\n"
            "1000  09 00 38 d5  mrs\tx9, MIDR_EL1\n",
            ["push rbp", "mrs x9, MIDR_EL1"],
        )
        self.assertTrue(tab_ok)

    def test_load_expected_asm_texts_nested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "e.json"
            path.write_text(
                json.dumps(
                    {
                        "insns": [{"asm_text": "push rbp"}],
                        "cases": [
                            {"insns": [{"asm_text": "ret"}]},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                rs.load_expected_asm_texts(path), ["push rbp", "ret"]
            )


class ProbeAndCliTests(unittest.TestCase):
    def test_probe_only_skips_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cap = Path(tmp) / "cap"
            cap.mkdir()
            (cap / "CMakeLists.txt").write_text("project(x)\n", encoding="utf-8")
            code = rs.main(
                [
                    "--capstone",
                    str(cap),
                    "--skills-root",
                    str(ROOT),
                    "--probe-only",
                ]
            )
            self.assertEqual(code, 0)

    def test_missing_cmake_skips_without_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cap = Path(tmp) / "cap"
            cap.mkdir()
            (cap / "CMakeLists.txt").write_text("project(x)\n", encoding="utf-8")
            with mock.patch.object(rs, "which", return_value=None):
                code = rs.main(
                    [
                        "--capstone",
                        str(cap),
                        "--skills-root",
                        str(ROOT),
                    ]
                )
            self.assertEqual(code, 0)

    def test_bad_capstone_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code = rs.main(
                [
                    "--capstone",
                    str(Path(tmp) / "missing"),
                    "--skills-root",
                    str(ROOT),
                    "--probe-only",
                ]
            )
            self.assertEqual(code, 2)

    def test_dry_run_with_fake_cmake(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cap = Path(tmp) / "cap"
            cap.mkdir()
            (cap / "CMakeLists.txt").write_text("project(x)\n", encoding="utf-8")
            fake_cmake = Path(tmp) / "cmake.exe"
            fake_cmake.write_text("", encoding="utf-8")
            with mock.patch.object(rs, "which", return_value=fake_cmake):
                code = rs.main(
                    [
                        "--capstone",
                        str(cap),
                        "--skills-root",
                        str(ROOT),
                        "--dry-run",
                    ]
                )
            self.assertEqual(code, 0)

    def test_find_executable_multiconfig(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            build = Path(tmp)
            exe = build / "Release" / "cstool.exe"
            exe.parent.mkdir(parents=True)
            exe.write_text("", encoding="utf-8")
            found = rs.find_executable(build, ("cstool.exe", "cstool"))
            self.assertEqual(found, exe)


if __name__ == "__main__":
    unittest.main()
