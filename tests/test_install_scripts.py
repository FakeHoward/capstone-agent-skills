#!/usr/bin/env python3
"""Install script tests runnable on the current host (PowerShell + Git Bash)."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PS1 = ROOT / "scripts" / "install.ps1"
SH = ROOT / "scripts" / "install.sh"

GIT_BASH_CANDIDATES = [
    Path(r"C:\Program Files\Git\bin\bash.exe"),
    Path(r"C:\Program Files\Git\usr\bin\bash.exe"),
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Git" / "bin" / "bash.exe",
]


def _find_git_bash() -> Path | None:
    for cand in GIT_BASH_CANDIDATES:
        if cand.is_file():
            return cand
    which = shutil.which("bash")
    if not which:
        return None
    path = Path(which)
    # Windows WSL stub is not a real POSIX shell for this script.
    if path.name.lower() == "bash.exe" and "system32" in str(path).lower():
        return None
    return path


def _find_powershell() -> str | None:
    for name in ("pwsh", "powershell"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _run_ps(*args: str) -> subprocess.CompletedProcess[str]:
    shell = _find_powershell()
    if shell is None:
        raise FileNotFoundError("powershell/pwsh not on PATH")
    cmd = [
        shell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(PS1),
        *args,
    ]
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _to_bash_path(path: Path | str) -> str:
    s = str(path).replace("\\", "/")
    if len(s) >= 2 and s[1] == ":":
        return f"/{s[0].lower()}{s[2:]}"
    return s


def _run_sh(bash: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = _to_bash_path(SH)
    converted: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        converted.append(arg)
        if arg in {"--target", "--repo-root", "--project-root"} and i + 1 < len(args):
            converted.append(_to_bash_path(args[i + 1]))
            i += 2
            continue
        i += 1
    cmd = [str(bash), script, *converted]
    env = os.environ.copy()
    env.setdefault("MSYS_NO_PATHCONV", "1")
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


class PowerShellInstallTests(unittest.TestCase):
    def test_dry_run_copy_skip_force_backup_refuse_unicode(self) -> None:
        if _find_powershell() is None:
            self.skipTest(
                "PowerShell install.ps1 unexecuted: neither pwsh nor "
                "powershell on PATH (expected on Linux CI runners)"
            )
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            safe = base / "safe-skills"
            uni = base / "Документы-тест"
            reserved = base / "skills-cursor"

            dry = _run_ps(
                "-Scope",
                "personal",
                "-Target",
                str(safe),
                "-DryRun",
            )
            self.assertEqual(dry.returncode, 0, dry.stderr + dry.stdout)
            self.assertIn("WOULD_COPY", dry.stdout)
            self.assertIn("dry_run=True", dry.stdout)

            copy = _run_ps("-Scope", "personal", "-Target", str(safe))
            self.assertEqual(copy.returncode, 0, copy.stderr + copy.stdout)
            self.assertTrue((safe / "capstone-core-api" / "SKILL.md").is_file())

            marker = safe / "capstone-core-api" / "USER_EDIT.md"
            marker.write_text("keep-me\n", encoding="utf-8")

            skip = _run_ps("-Scope", "personal", "-Target", str(safe))
            self.assertEqual(skip.returncode, 0, skip.stderr + skip.stdout)
            self.assertIn("SKIP  exists:", skip.stdout)
            self.assertTrue(marker.is_file())

            force = _run_ps(
                "-Scope",
                "personal",
                "-Target",
                str(safe),
                "-Force",
            )
            self.assertEqual(force.returncode, 0, force.stderr + force.stdout)
            self.assertIn("REPLACE", force.stdout)
            self.assertIn("backup:", force.stdout)
            backups = list(safe.glob("capstone-core-api.bak.*"))
            self.assertTrue(backups, "expected .bak.* directory after -Force")
            self.assertTrue((backups[0] / "USER_EDIT.md").is_file())
            self.assertFalse(marker.is_file())
            self.assertTrue((safe / "capstone-core-api" / "SKILL.md").is_file())

            refuse = _run_ps(
                "-Scope",
                "personal",
                "-Target",
                str(reserved),
                "-DryRun",
            )
            self.assertNotEqual(refuse.returncode, 0)
            combined = refuse.stdout + refuse.stderr
            self.assertIn("skills-cursor", combined.lower())

            uni.mkdir()
            uni_run = _run_ps(
                "-Scope",
                "personal",
                "-Target",
                str(uni),
                "-DryRun",
            )
            self.assertEqual(uni_run.returncode, 0, uni_run.stderr + uni_run.stdout)
            self.assertIn("WOULD_COPY", uni_run.stdout)


class PosixInstallTests(unittest.TestCase):
    def test_posix_install_or_mark_unexecuted(self) -> None:
        bash = _find_git_bash()
        if bash is None:
            self.skipTest(
                "POSIX install.sh unexecuted: no Git Bash/WSL shell available "
                "(system32 bash stub ignored)"
            )

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            safe = base / "sh-safe"
            reserved = base / "skills-cursor"

            dry = _run_sh(
                bash,
                "--scope",
                "personal",
                "--target",
                str(safe),
                "--dry-run",
            )
            self.assertEqual(dry.returncode, 0, dry.stderr + dry.stdout)
            self.assertIn("WOULD_COPY", dry.stdout)

            copy = _run_sh(bash, "--scope", "personal", "--target", str(safe))
            self.assertEqual(copy.returncode, 0, copy.stderr + copy.stdout)
            self.assertTrue((safe / "capstone-core-api" / "SKILL.md").is_file())

            marker = safe / "capstone-core-api" / "USER_EDIT.md"
            marker.write_text("keep-me\n", encoding="utf-8")

            skip = _run_sh(bash, "--scope", "personal", "--target", str(safe))
            self.assertEqual(skip.returncode, 0, skip.stderr + skip.stdout)
            self.assertIn("SKIP  exists:", skip.stdout)
            self.assertTrue(marker.is_file())

            force = _run_sh(
                bash,
                "--scope",
                "personal",
                "--target",
                str(safe),
                "--force",
            )
            self.assertEqual(force.returncode, 0, force.stderr + force.stdout)
            self.assertIn("REPLACE", force.stdout)
            backups = list(safe.glob("capstone-core-api.bak.*"))
            self.assertTrue(backups)
            self.assertTrue((backups[0] / "USER_EDIT.md").is_file())

            refuse = _run_sh(
                bash,
                "--scope",
                "personal",
                "--target",
                str(reserved),
                "--dry-run",
            )
            self.assertNotEqual(refuse.returncode, 0)
            self.assertIn("skills-cursor", (refuse.stdout + refuse.stderr).lower())


if __name__ == "__main__":
    unittest.main()
