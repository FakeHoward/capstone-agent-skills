#!/usr/bin/env python3
"""Unit tests for scripts/validate_skills.py."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_skills as vs  # noqa: E402

DEMO_DESC = (
    "Guides Capstone demo handle open/close flows for API checks. "
    "Use when opening cs_open handles in unit tests."
)


class FrontmatterTests(unittest.TestCase):
    def test_folded_description_crlf(self) -> None:
        text = (
            "---\r\n"
            "name: demo-skill\r\n"
            "description: >-\r\n"
            "  Guides Capstone demo flows with clear steps.\r\n"
            "  Use when testing the validator frontmatter parser.\r\n"
            "---\r\n"
            "# Body\r\n"
        )
        fm, body = vs.parse_frontmatter(text)
        assert fm is not None
        self.assertEqual(fm["name"], "demo-skill")
        self.assertIn("Use when", fm["description"])
        self.assertIn("Guides Capstone demo", fm["description"])
        self.assertTrue(body.startswith("# Body"))

    def test_one_level_links(self) -> None:
        self.assertTrue(vs.link_is_one_level("reference.md"))
        self.assertTrue(vs.link_is_one_level("../capstone-core-api/SKILL.md"))
        self.assertFalse(vs.link_is_one_level("../../escape.md"))
        self.assertFalse(vs.link_is_one_level("a/b/c.md"))


class HexParseTests(unittest.TestCase):
    def test_hex_comments_and_separators(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.hex"
            path.write_text("55 48 # push/mov\n8b 05\n", encoding="utf-8")
            self.assertEqual(vs.parse_hex_file(path), bytes.fromhex("55488b05"))


class SchemaHelperTests(unittest.TestCase):
    def test_schema_const_and_required(self) -> None:
        rep = vs.Reporter()
        schema = {
            "type": "object",
            "required": ["version"],
            "properties": {"version": {"type": "integer", "const": 1}},
        }
        vs.validate_against_schema({"version": 2}, schema, "doc", rep)
        self.assertTrue(any("const" in e for e in rep.errors))


class ValidatorIntegrationTests(unittest.TestCase):
    def _write_skill(
        self,
        skills_root: Path,
        name: str,
        description: str,
        body: str = "# Skill\n\nSee [reference.md](reference.md).\n",
        extra_files=None,
    ):
        d = skills_root / name
        d.mkdir(parents=True)
        text = (
            "---\n"
            f"name: {name}\n"
            "description: >-\n"
            f"  {description}\n"
            "---\n"
            f"{body}"
        )
        (d / "SKILL.md").write_text(text, encoding="utf-8")
        (d / "reference.md").write_text("# ref\n", encoding="utf-8")
        if extra_files:
            for fname, content in extra_files.items():
                (d / fname).write_text(content, encoding="utf-8")

    def _write_required_fixtures(
        self, root: Path, skill: str = "capstone-demo", bad_expected=None
    ) -> None:
        hex_dir = root / "fixtures" / "hex"
        exp_dir = root / "fixtures" / "expected"
        hex_dir.mkdir(parents=True, exist_ok=True)
        exp_dir.mkdir(parents=True, exist_ok=True)
        names = (
            ("x86-batch", "x86_batch"),
            ("x86-skipdata", "x86_skipdata"),
            ("aarch64-smoke", "aarch64_smoke"),
            ("alias-detail", "alias_detail"),
            ("riscv-regs", "riscv_regs"),
        )
        pointers = []
        for pid, stem in names:
            (hex_dir / f"{stem}.hex").write_text("55 48\n", encoding="utf-8")
            payload = (
                bad_expected
                if bad_expected is not None
                else {"insns": [{"asm_text": "nop"}]}
            )
            (exp_dir / f"{stem}.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            pointers.append(
                {
                    "id": pid,
                    "skill": skill,
                    "hex": f"fixtures/hex/{stem}.hex",
                    "expected": f"fixtures/expected/{stem}.json",
                    "upstream": "tests/example.yaml",
                }
            )
        (root / "fixtures" / "pointers.json").write_text(
            json.dumps({"version": 1, "pointers": pointers}), encoding="utf-8"
        )

    def _base_manifest(self, skill: str = "capstone-demo", **overrides):
        entry = {
            "id": skill,
            "path": f"skills/{skill}",
            "category": "api",
            "files": ["SKILL.md", "reference.md"],
            "auto_invoke": True,
        }
        entry.update(overrides)
        return {
            "version": 1,
            "source": {
                "upstream_url": "https://github.com/capstone-engine/capstone",
                "branch": "next",
                "commit": "1c1f6f4e",
                "api": "6 alpha",
            },
            "auto_invoke_policy": {
                "default": True,
                "forbid_disable_model_invocation": True,
            },
            "skills": [entry],
        }

    def test_minimal_package_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            skills.mkdir()
            self._write_skill(skills, "capstone-demo", DEMO_DESC)
            (root / "skills.manifest.json").write_text(
                json.dumps(self._base_manifest()), encoding="utf-8"
            )
            triggers = {
                "version": 1,
                "triggers": [
                    {
                        "skill": "capstone-demo",
                        "required_terms": ["cs_open", "Capstone demo"],
                        "blind_prompts": ["Open a Capstone demo handle with cs_open."],
                    }
                ],
            }
            (root / "triggers.json").write_text(json.dumps(triggers), encoding="utf-8")
            cap = root / "capstone"
            cap.mkdir()
            (cap / "cs.c").write_text(
                "case CS_OPT_DETAIL:\n\thandle->detail_opt |= (cs_opt_value)value;\n",
                encoding="utf-8",
            )
            claims = {
                "version": 1,
                "claims": [
                    {
                        "id": "detail-or",
                        "source_path": "cs.c",
                        "regex": r"detail_opt\s*\|=",
                    }
                ],
            }
            (root / "claims.json").write_text(json.dumps(claims), encoding="utf-8")
            self._write_required_fixtures(root)
            code = vs.run_validation(root, cap)
            self.assertEqual(code, 0)

    def test_detects_missing_use_when(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "skills" / "capstone-bad"
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(
                "---\nname: capstone-bad\ndescription: Only explains WHAT without trigger.\n---\n# x\n",
                encoding="utf-8",
            )
            rep = vs.Reporter()
            vs.validate_skill_dir(d, rep)
            self.assertTrue(any("Use when" in e for e in rep.errors))

    def test_forbidden_thread_safe_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "skills" / "capstone-bad"
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(
                "---\n"
                "name: capstone-bad\n"
                "description: >-\n"
                "  Guides Capstone concurrency. Use when sharing handles.\n"
                "---\n"
                "# x\n\nCapstone is thread-safe for shared handles.\n",
                encoding="utf-8",
            )
            rep = vs.Reporter()
            vs.validate_skill_dir(d, rep)
            self.assertTrue(any("thread-safe" in e for e in rep.errors))

    def test_manifest_wrong_path_and_incomplete_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            skills.mkdir()
            self._write_skill(skills, "capstone-demo", DEMO_DESC)
            infos = {
                "capstone-demo": vs.validate_skill_dir(
                    skills / "capstone-demo", vs.Reporter()
                )
            }
            manifest = self._base_manifest(
                path="skills/WRONG", files=["SKILL.md"]
            )
            (root / "skills.manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            rep = vs.Reporter()
            vs.validate_manifest(root, infos, rep)
            self.assertTrue(any("path" in e and "WRONG" in e for e in rep.errors))
            self.assertTrue(
                any("files incomplete" in e and "reference.md" in e for e in rep.errors)
            )

    def test_manifest_bad_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            skills.mkdir()
            self._write_skill(skills, "capstone-demo", DEMO_DESC)
            infos = {
                "capstone-demo": vs.validate_skill_dir(
                    skills / "capstone-demo", vs.Reporter()
                )
            }
            (root / "skills.manifest.json").write_text(
                json.dumps(self._base_manifest(category="tooling")),
                encoding="utf-8",
            )
            rep = vs.Reporter()
            vs.validate_manifest(root, infos, rep)
            self.assertTrue(any("category" in e for e in rep.errors))

    def test_manifest_incomplete_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            skills.mkdir()
            self._write_skill(skills, "capstone-demo", DEMO_DESC)
            self._write_skill(
                skills,
                "capstone-extra",
                "Guides Capstone extra flows for inventory checks. "
                "Use when testing incomplete manifests.",
            )
            infos = {
                name: vs.validate_skill_dir(skills / name, vs.Reporter())
                for name in ("capstone-demo", "capstone-extra")
            }
            (root / "skills.manifest.json").write_text(
                json.dumps(self._base_manifest()), encoding="utf-8"
            )
            rep = vs.Reporter()
            vs.validate_manifest(root, infos, rep)
            self.assertTrue(
                any("incomplete inventory" in e and "capstone-extra" in e for e in rep.errors)
            )

    def test_trigger_missing_term_and_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            skills.mkdir()
            self._write_skill(skills, "capstone-a", DEMO_DESC)
            self._write_skill(
                skills,
                "capstone-b",
                "Guides Capstone batch flows for collision checks. "
                "Use when opening cs_open handles in unit tests.",
            )
            infos = {
                "capstone-a": {
                    "fm": {"description": DEMO_DESC},
                },
                "capstone-b": {
                    "fm": {
                        "description": (
                            "Guides Capstone batch flows for collision checks. "
                            "Use when opening cs_open handles in unit tests."
                        )
                    },
                },
            }
            (root / "triggers.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "triggers": [
                            {
                                "skill": "capstone-a",
                                "required_terms": ["NOT_IN_DESC"],
                                "blind_prompts": ["x"],
                            },
                            {
                                "skill": "capstone-b",
                                "required_terms": ["cs_open"],
                                "blind_prompts": ["y"],
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            # First check missing term
            rep = vs.Reporter()
            vs.validate_triggers(root, {"capstone-a": infos["capstone-a"]}, rep)
            self.assertTrue(any("NOT_IN_DESC" in e for e in rep.errors))

            # Collision: identical term sets
            (root / "triggers.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "triggers": [
                            {
                                "skill": "capstone-a",
                                "required_terms": ["cs_open"],
                                "blind_prompts": ["x"],
                            },
                            {
                                "skill": "capstone-b",
                                "required_terms": ["CS_OPEN"],
                                "blind_prompts": ["y"],
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rep2 = vs.Reporter()
            vs.validate_triggers(root, infos, rep2)
            self.assertTrue(any("colliding required_terms" in e for e in rep2.errors))

    def test_claim_mismatch_and_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cap = root / "cap"
            cap.mkdir()
            (cap / "cs.c").write_text("nope\n", encoding="utf-8")
            (root / "secret.txt").write_text("secret\n", encoding="utf-8")
            (root / "claims.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "claims": [
                            {
                                "id": "bad",
                                "source_path": "cs.c",
                                "regex": r"detail_opt\s*\|=",
                            },
                            {
                                "id": "escape",
                                "source_path": "../secret.txt",
                                "regex": r"secret",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rep = vs.Reporter()
            vs.validate_claims(root, cap, rep)
            self.assertTrue(any("regex did not match" in e for e in rep.errors))
            self.assertTrue(any("escapes capstone tree" in e for e in rep.errors))

    def test_broken_and_deep_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "skills" / "capstone-x"
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(
                "---\n"
                "name: capstone-x\n"
                "description: Guides Capstone link checks carefully. "
                "Use when validating markdown links.\n"
                "---\n"
                "See [missing](missing.md) and [deep](../../secret.md).\n",
                encoding="utf-8",
            )
            rep = vs.Reporter()
            vs.validate_skill_dir(d, rep)
            self.assertTrue(any("broken local link" in e for e in rep.errors))
            self.assertTrue(any("deeper than one level" in e for e in rep.errors))

    def test_missing_and_escaped_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills").mkdir()
            infos = {"capstone-demo": {"fm": {}}}
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (outside / "leak.hex").write_text("55", encoding="utf-8")
            (outside / "leak.json").write_text(
                json.dumps({"insns": [{"asm_text": "x"}]}), encoding="utf-8"
            )
            fix = root / "fixtures"
            fix.mkdir()
            (fix / "pointers.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "pointers": [
                            {
                                "id": "x86-batch",
                                "skill": "capstone-demo",
                                "hex": "fixtures/missing.hex",
                                "expected": "fixtures/missing.json",
                                "upstream": "u",
                            },
                            {
                                "id": "x86-skipdata",
                                "skill": "capstone-demo",
                                "hex": "../outside/leak.hex",
                                "expected": "../outside/leak.json",
                                "upstream": "u",
                            },
                            {
                                "id": "aarch64-smoke",
                                "skill": "capstone-demo",
                                "hex": "fixtures/missing.hex",
                                "expected": "fixtures/missing.json",
                                "upstream": "u",
                            },
                            {
                                "id": "alias-detail",
                                "skill": "capstone-demo",
                                "hex": "fixtures/missing.hex",
                                "expected": "fixtures/missing.json",
                                "upstream": "u",
                            },
                            {
                                "id": "riscv-regs",
                                "skill": "capstone-demo",
                                "hex": "fixtures/missing.hex",
                                "expected": "fixtures/missing.json",
                                "upstream": "u",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rep = vs.Reporter()
            vs.validate_fixtures(root, infos, rep)
            self.assertTrue(any("missing hex file" in e for e in rep.errors))
            self.assertTrue(any("path escapes package root" in e for e in rep.errors))

    def test_expected_shape_and_pointer_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            infos = {"capstone-demo": {"fm": {}}}
            self._write_required_fixtures(
                root, skill="unknown-skill", bad_expected={"insns": "not-a-list"}
            )
            rep = vs.Reporter()
            vs.validate_fixtures(root, infos, rep)
            self.assertTrue(any("unknown skill" in e for e in rep.errors))
            self.assertTrue(any("insns must be a list" in e for e in rep.errors))

    def test_repo_schemas_validate_package_json(self) -> None:
        rep = vs.Reporter()
        for rel, schema_rel in (
            ("skills.manifest.json", "schemas/skills.manifest.schema.json"),
            ("triggers.json", "schemas/triggers.schema.json"),
            ("claims.json", "schemas/claims.schema.json"),
            ("fixtures/pointers.json", "schemas/pointers.schema.json"),
        ):
            data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
            schema = vs.load_schema(ROOT, schema_rel, rep)
            self.assertIsNotNone(schema)
            vs.validate_against_schema(data, schema, rel, rep)
        self.assertEqual(rep.errors, [])

    def test_repo_validator_against_capstone(self) -> None:
        capstone = ROOT.parent / "capstone"
        if not capstone.is_dir():
            self.skipTest("sibling capstone checkout missing")
        code = vs.run_validation(ROOT, capstone)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
