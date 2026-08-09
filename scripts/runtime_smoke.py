#!/usr/bin/env python3
"""Narrow Capstone runtime smoke against package fixtures.

Stdlib only. Probes cmake, optionally configures/builds an isolated dir
(`build-skill-smoke` by default) with cstool + CSTEST, then runs a short
cstool / unit / skipdata checklist. Missing toolchain or targets → SKIP
with a reason (exit 0). A failed command or fixture mismatch → FAIL
(exit 1). Bad CLI → exit 2.

Does not install toolchains, mutate Capstone sources, or run full
corpus/fuzz suites.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_SKIP = "SKIP"


@dataclass
class ScenarioResult:
    name: str
    status: str
    command: str = ""
    exit_code: Optional[int] = None
    reason: str = ""
    detail: str = ""


@dataclass
class SmokeReport:
    results: List[ScenarioResult] = field(default_factory=list)

    def add(self, result: ScenarioResult) -> None:
        self.results.append(result)

    @property
    def failed(self) -> bool:
        return any(r.status == STATUS_FAIL for r in self.results)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_hex_file(path: Path) -> bytes:
    raw = path.read_text(encoding="utf-8")
    cleaned_lines = []
    for line in raw.splitlines():
        if "#" in line:
            line = line.split("#", 1)[0]
        cleaned_lines.append(line)
    cleaned = "".join(cleaned_lines)
    cleaned = re.sub(r"0x", "", cleaned, flags=re.I)
    cleaned = re.sub(r"[^0-9a-fA-F]", "", cleaned)
    if len(cleaned) % 2 != 0:
        raise ValueError(f"odd number of hex digits in {path}")
    return bytes.fromhex(cleaned)


def bytes_to_cstool_hex(blob: bytes) -> str:
    return " ".join(f"{b:02x}" for b in blob)


def load_expected_asm_texts(expected_path: Path) -> List[str]:
    data = json.loads(expected_path.read_text(encoding="utf-8"))
    texts: List[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("asm_text"), str):
                texts.append(node["asm_text"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return texts


def which(name: str) -> Optional[Path]:
    found = shutil.which(name)
    return Path(found) if found else None


def find_executable(build_dir: Path, names: Sequence[str]) -> Optional[Path]:
    """Locate a built binary under build_dir (single- or multi-config)."""
    candidates: List[Path] = []
    for name in names:
        candidates.extend(
            [
                build_dir / name,
                build_dir / "Release" / name,
                build_dir / "Debug" / name,
                build_dir / "RelWithDebInfo" / name,
            ]
        )
        # CMake may nest test targets under tests/...
        for sub in ("tests/unit", "tests/integration", "suite/cstest"):
            base = build_dir / Path(sub)
            candidates.extend(
                [
                    base / name,
                    base / "Release" / name,
                    base / "Debug" / name,
                ]
            )
    for path in candidates:
        if path.is_file():
            return path
    # Last resort: shallow name walk (depth-capped).
    wanted = {n.lower() for n in names}
    if not build_dir.is_dir():
        return None
    for root, dirnames, filenames in os.walk(build_dir):
        depth = Path(root).relative_to(build_dir).parts
        if len(depth) > 4:
            dirnames[:] = []
            continue
        for fname in filenames:
            if fname.lower() in wanted:
                return Path(root) / fname
    return None


def run_cmd(
    argv: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    timeout: int = 180,
) -> Tuple[int, str, str]:
    proc = subprocess.run(
        list(argv),
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def normalize_asm_whitespace(text: str) -> str:
    """Collapse runs of spaces/tabs so cstool tab-separated asm matches fixtures."""
    return re.sub(r"[ \t]+", " ", text)


def match_asm_texts(stdout: str, expected: Sequence[str]) -> Tuple[bool, str]:
    # cstool prints mnemonic TAB op_str; YAML fixtures usually use a space.
    haystack = normalize_asm_whitespace(stdout)
    missing = [
        text
        for text in expected
        if normalize_asm_whitespace(text) not in haystack
    ]
    if missing:
        return False, "missing asm_text: " + ", ".join(missing[:5])
    return True, f"matched {len(expected)} asm_text item(s)"


def probe_toolchain() -> ScenarioResult:
    cmake = which("cmake")
    compilers = [
        name
        for name in ("cl", "gcc", "g++", "clang", "clang++", "cc")
        if which(name)
    ]
    if cmake is None:
        return ScenarioResult(
            name="toolchain-probe",
            status=STATUS_SKIP,
            command="cmake --version",
            reason="cmake not found on PATH",
        )
    # cmake alone is enough to attempt configure; compiler absence will
    # surface as configure/build FAIL or SKIP later.
    detail = f"cmake={cmake}"
    if compilers:
        detail += "; compilers=" + ",".join(compilers)
    else:
        detail += "; no cl/gcc/clang on PATH (configure may still find a toolchain)"
    return ScenarioResult(
        name="toolchain-probe",
        status=STATUS_PASS,
        command="cmake --version",
        exit_code=0,
        detail=detail,
    )


def ensure_configured(
    capstone: Path,
    build_dir: Path,
    cmake: Path,
    *,
    dry_run: bool,
) -> ScenarioResult:
    cache = build_dir / "CMakeCache.txt"
    cmd = [
        str(cmake),
        "-S",
        str(capstone),
        "-B",
        str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCAPSTONE_BUILD_CSTOOL=ON",
        "-DCAPSTONE_BUILD_CSTEST=ON",
    ]
    command = " ".join(cmd)
    if dry_run:
        return ScenarioResult(
            name="configure",
            status=STATUS_SKIP,
            command=command,
            reason="dry-run",
        )
    if cache.is_file():
        return ScenarioResult(
            name="configure",
            status=STATUS_PASS,
            command=command,
            exit_code=0,
            detail=f"reuse existing cache {cache}",
        )
    code, out, err = run_cmd(cmd, timeout=300)
    if code == 0:
        return ScenarioResult(
            name="configure",
            status=STATUS_PASS,
            command=command,
            exit_code=code,
            detail="configured with CSTOOL+CSTEST",
        )
    return ScenarioResult(
        name="configure",
        status=STATUS_FAIL,
        command=command,
        exit_code=code,
        reason="cmake configure failed",
        detail=(err or out)[-800:],
    )


def ensure_built(
    build_dir: Path,
    cmake: Path,
    *,
    dry_run: bool,
) -> ScenarioResult:
    cmd = [
        str(cmake),
        "--build",
        str(build_dir),
        "--config",
        "Release",
        "--target",
        "cstool",
    ]
    command = " ".join(cmd)
    if dry_run:
        return ScenarioResult(
            name="build",
            status=STATUS_SKIP,
            command=command,
            reason="dry-run",
        )
    code, out, err = run_cmd(cmd, timeout=900)
    if code != 0:
        return ScenarioResult(
            name="build",
            status=STATUS_FAIL,
            command=command,
            exit_code=code,
            reason="cmake --build cstool failed",
            detail=(err or out)[-800:],
        )
    # Best-effort: also build narrow test targets when present.
    extra_targets = ("riscv_reg_access", "test_skipdata", "cstest")
    extras_ok: List[str] = []
    extras_skip: List[str] = []
    for target in extra_targets:
        ecmd = [
            str(cmake),
            "--build",
            str(build_dir),
            "--config",
            "Release",
            "--target",
            target,
        ]
        ecode, _, eerr = run_cmd(ecmd, timeout=600)
        if ecode == 0:
            extras_ok.append(target)
        else:
            extras_skip.append(f"{target} unavailable")
    detail = "built cstool"
    if extras_ok:
        detail += "; also " + ", ".join(extras_ok)
    if extras_skip:
        detail += "; " + "; ".join(extras_skip)
    return ScenarioResult(
        name="build",
        status=STATUS_PASS,
        command=command,
        exit_code=0,
        detail=detail,
    )


def run_cstool_scenario(
    name: str,
    cstool: Path,
    arch: str,
    hex_path: Path,
    expected_path: Path,
    *,
    flags: Sequence[str] = (),
    address: str = "0x1000",
    dry_run: bool = False,
) -> ScenarioResult:
    blob = parse_hex_file(hex_path)
    hex_str = bytes_to_cstool_hex(blob)
    argv = [str(cstool), *flags, arch, hex_str, address]
    command = " ".join(argv)
    if dry_run:
        return ScenarioResult(
            name=name,
            status=STATUS_SKIP,
            command=command,
            reason="dry-run",
        )
    code, out, err = run_cmd(argv, timeout=60)
    if code != 0:
        return ScenarioResult(
            name=name,
            status=STATUS_FAIL,
            command=command,
            exit_code=code,
            reason="cstool non-zero exit",
            detail=(err or out)[-500:],
        )
    expected = load_expected_asm_texts(expected_path)
    if not expected:
        return ScenarioResult(
            name=name,
            status=STATUS_PASS,
            command=command,
            exit_code=code,
            detail="no asm_text expectations; exit 0",
        )
    ok, msg = match_asm_texts(out, expected)
    return ScenarioResult(
        name=name,
        status=STATUS_PASS if ok else STATUS_FAIL,
        command=command,
        exit_code=code,
        reason="" if ok else msg,
        detail=msg if ok else (out[:500] or msg),
    )


def run_binary_scenario(
    name: str,
    binary: Optional[Path],
    *,
    args: Sequence[str] = (),
    dry_run: bool = False,
    skip_reason: str = "binary not found in build dir",
) -> ScenarioResult:
    if binary is None:
        return ScenarioResult(
            name=name,
            status=STATUS_SKIP,
            reason=skip_reason,
        )
    argv = [str(binary), *args]
    command = " ".join(argv)
    if dry_run:
        return ScenarioResult(
            name=name,
            status=STATUS_SKIP,
            command=command,
            reason="dry-run",
        )
    code, out, err = run_cmd(argv, timeout=120)
    if code == 0:
        return ScenarioResult(
            name=name,
            status=STATUS_PASS,
            command=command,
            exit_code=code,
            detail=(out or "ok")[:300],
        )
    return ScenarioResult(
        name=name,
        status=STATUS_FAIL,
        command=command,
        exit_code=code,
        reason="non-zero exit",
        detail=(err or out)[-500:],
    )


def print_report(report: SmokeReport) -> None:
    for item in report.results:
        line = f"[{item.status}] {item.name}"
        if item.command:
            line += f" :: {item.command}"
        if item.exit_code is not None:
            line += f" (exit={item.exit_code})"
        if item.reason:
            line += f" — {item.reason}"
        if item.detail and item.status != STATUS_FAIL:
            line += f" [{item.detail}]"
        print(line)
        if item.status == STATUS_FAIL and item.detail:
            print(item.detail)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Capstone runtime smoke for capstone-agent-skills fixtures. "
            "Missing toolchain yields SKIP (exit 0), not FAIL."
        )
    )
    p.add_argument(
        "--capstone",
        type=Path,
        required=True,
        help="Path to Capstone checkout (must contain CMakeLists.txt)",
    )
    p.add_argument(
        "--build-dir",
        type=Path,
        default=None,
        help="Build directory (default: <capstone>/build-skill-smoke)",
    )
    p.add_argument(
        "--skills-root",
        type=Path,
        default=None,
        help="capstone-agent-skills root (default: parent of scripts/)",
    )
    p.add_argument(
        "--probe-only",
        action="store_true",
        help="Only probe toolchain; skip configure/build/run",
    )
    p.add_argument(
        "--no-configure",
        action="store_true",
        help="Do not run cmake configure (use existing build dir)",
    )
    p.add_argument(
        "--no-build",
        action="store_true",
        help="Do not run cmake --build",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions as SKIP without executing builds/runs",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    skills_root = (args.skills_root or repo_root_from_script()).resolve()
    capstone = args.capstone.resolve()
    build_dir = (
        args.build_dir.resolve()
        if args.build_dir
        else (capstone / "build-skill-smoke")
    )

    if not (capstone / "CMakeLists.txt").is_file():
        print(
            f"error: --capstone does not look like Capstone: {capstone}",
            file=sys.stderr,
        )
        return 2
    fixtures = skills_root / "fixtures"
    if not (fixtures / "pointers.json").is_file():
        print(
            f"error: --skills-root missing fixtures/: {skills_root}",
            file=sys.stderr,
        )
        return 2

    report = SmokeReport()
    probe = probe_toolchain()
    report.add(probe)
    cmake = which("cmake")
    can_build = probe.status == STATUS_PASS and cmake is not None

    if args.probe_only:
        for name in (
            "configure",
            "build",
            "cstool-version",
            "x86-batch",
            "x86-detail",
            "x86-skipdata",
            "aarch64-smoke",
            "riscv_reg_access",
            "skipdata-integration",
        ):
            report.add(
                ScenarioResult(
                    name=name,
                    status=STATUS_SKIP,
                    reason="--probe-only",
                )
            )
        print_report(report)
        return 1 if report.failed else 0

    if not can_build:
        skip_reason = probe.reason or "toolchain unavailable"
        for name in (
            "configure",
            "build",
            "cstool-version",
            "x86-batch",
            "x86-detail",
            "x86-skipdata",
            "aarch64-smoke",
            "riscv_reg_access",
            "skipdata-integration",
        ):
            report.add(
                ScenarioResult(
                    name=name,
                    status=STATUS_SKIP,
                    reason=skip_reason,
                )
            )
        print_report(report)
        print(
            "NOTE: runtime smoke SKIPPED (no cmake/toolchain). "
            "Install a CMake + C compiler toolchain to execute scenarios."
        )
        return 0

    assert cmake is not None

    if args.no_configure:
        report.add(
            ScenarioResult(
                name="configure",
                status=STATUS_SKIP,
                reason="--no-configure",
                detail=str(build_dir),
            )
        )
    else:
        conf = ensure_configured(
            capstone, build_dir, cmake, dry_run=args.dry_run
        )
        report.add(conf)
        if conf.status == STATUS_FAIL:
            print_report(report)
            return 1

    if args.no_build:
        report.add(
            ScenarioResult(
                name="build",
                status=STATUS_SKIP,
                reason="--no-build",
            )
        )
    else:
        built = ensure_built(build_dir, cmake, dry_run=args.dry_run)
        report.add(built)
        if built.status == STATUS_FAIL:
            print_report(report)
            return 1

    cstool = find_executable(build_dir, ("cstool.exe", "cstool"))
    hex_root = fixtures / "hex"
    exp_root = fixtures / "expected"
    cstool_scenarios = (
        (
            "x86-batch",
            "x64",
            (),
            hex_root / "x86_batch.hex",
            exp_root / "x86_batch.json",
        ),
        (
            "x86-detail",
            "x64",
            ("-d",),
            hex_root / "x86_batch.hex",
            exp_root / "x86_batch.json",
        ),
        (
            "x86-skipdata",
            "x32",
            ("-s",),
            hex_root / "x86_skipdata.hex",
            exp_root / "x86_skipdata.json",
        ),
        (
            "aarch64-smoke",
            "aarch64",
            (),
            hex_root / "aarch64_smoke.hex",
            exp_root / "aarch64_smoke.json",
        ),
    )

    if args.dry_run:
        report.add(
            ScenarioResult(
                name="cstool-version",
                status=STATUS_SKIP,
                command="cstool -v",
                reason="dry-run",
            )
        )
        for name, arch, flags, hex_path, exp_path in cstool_scenarios:
            report.add(
                run_cstool_scenario(
                    name,
                    cstool or Path("cstool"),
                    arch,
                    hex_path,
                    exp_path,
                    flags=flags,
                    dry_run=True,
                )
            )
        report.add(
            ScenarioResult(
                name="riscv_reg_access",
                status=STATUS_SKIP,
                command="riscv_reg_access",
                reason="dry-run",
            )
        )
        report.add(
            ScenarioResult(
                name="skipdata-integration",
                status=STATUS_SKIP,
                command="test_skipdata",
                reason="dry-run",
            )
        )
    elif cstool is None:
        for name in (
            "cstool-version",
            "x86-batch",
            "x86-detail",
            "x86-skipdata",
            "aarch64-smoke",
        ):
            report.add(
                ScenarioResult(
                    name=name,
                    status=STATUS_SKIP,
                    reason="cstool binary not found under build dir",
                )
            )
        riscv_bin = find_executable(
            build_dir, ("riscv_reg_access.exe", "riscv_reg_access")
        )
        report.add(
            run_binary_scenario(
                "riscv_reg_access",
                riscv_bin,
                skip_reason=(
                    "riscv_reg_access not built "
                    "(needs CAPSTONE_BUILD_CSTEST=ON and successful build)"
                ),
            )
        )
        skip_bin = find_executable(
            build_dir, ("test_skipdata.exe", "test_skipdata")
        )
        if skip_bin is not None:
            report.add(run_binary_scenario("skipdata-integration", skip_bin))
        else:
            cstest = find_executable(build_dir, ("cstest.exe", "cstest"))
            yaml_case = capstone / "tests" / "features" / "skipdata.yaml"
            if cstest is None or not yaml_case.is_file():
                report.add(
                    ScenarioResult(
                        name="skipdata-integration",
                        status=STATUS_SKIP,
                        reason=(
                            "neither test_skipdata nor "
                            "cstest+skipdata.yaml available"
                        ),
                    )
                )
            else:
                report.add(
                    run_binary_scenario(
                        "skipdata-integration",
                        cstest,
                        args=(str(yaml_case),),
                    )
                )
    else:
        code, out, err = run_cmd([str(cstool), "-v"], timeout=30)
        report.add(
            ScenarioResult(
                name="cstool-version",
                status=STATUS_PASS if code == 0 else STATUS_FAIL,
                command=f"{cstool} -v",
                exit_code=code,
                reason="" if code == 0 else "cstool -v failed",
                detail=(out or err)[:400],
            )
        )
        for name, arch, flags, hex_path, exp_path in cstool_scenarios:
            if not hex_path.is_file() or not exp_path.is_file():
                report.add(
                    ScenarioResult(
                        name=name,
                        status=STATUS_SKIP,
                        reason="fixture files missing",
                    )
                )
                continue
            report.add(
                run_cstool_scenario(
                    name,
                    cstool,
                    arch,
                    hex_path,
                    exp_path,
                    flags=flags,
                )
            )
        riscv_bin = find_executable(
            build_dir, ("riscv_reg_access.exe", "riscv_reg_access")
        )
        report.add(
            run_binary_scenario(
                "riscv_reg_access",
                riscv_bin,
                skip_reason=(
                    "riscv_reg_access not built "
                    "(needs CAPSTONE_BUILD_CSTEST=ON and successful build)"
                ),
            )
        )
        skip_bin = find_executable(
            build_dir, ("test_skipdata.exe", "test_skipdata")
        )
        if skip_bin is not None:
            report.add(run_binary_scenario("skipdata-integration", skip_bin))
        else:
            cstest = find_executable(build_dir, ("cstest.exe", "cstest"))
            yaml_case = capstone / "tests" / "features" / "skipdata.yaml"
            if cstest is None or not yaml_case.is_file():
                report.add(
                    ScenarioResult(
                        name="skipdata-integration",
                        status=STATUS_SKIP,
                        reason=(
                            "neither test_skipdata nor "
                            "cstest+skipdata.yaml available"
                        ),
                    )
                )
            else:
                report.add(
                    run_binary_scenario(
                        "skipdata-integration",
                        cstest,
                        args=(str(yaml_case),),
                    )
                )

    print_report(report)
    counts = {STATUS_PASS: 0, STATUS_FAIL: 0, STATUS_SKIP: 0}
    for item in report.results:
        counts[item.status] = counts.get(item.status, 0) + 1
    print(
        f"SUMMARY pass={counts[STATUS_PASS]} "
        f"fail={counts[STATUS_FAIL]} skip={counts[STATUS_SKIP]}"
    )
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
