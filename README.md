![skills.sh](https://skills.sh/b/FakeHoward/capstone-agent-skills)

# capstone-agent-skills

Agent skills for [Capstone Engine](https://github.com/capstone-engine/capstone) on branch `next`, API 6 alpha, pinned commit `1c1f6f4e`. One `skills/` tree works with Cursor, Claude Code, and Codex (Agent Skills `SKILL.md` format). Each skill covers one slice of the C API, a build/tooling path, or a single architecture.

The package has 41 skills, plus `skills.manifest.json`, `triggers.json`, `claims.json`, fixtures, schemas, a Python validator, and a Node installer.

## Install with npx

Primary install (open skills CLI; installs into the agent dirs you choose):

```bash
# List skills in this repo
npx skills add FakeHoward/capstone-agent-skills --list

# Global install for Cursor, Claude Code, and Codex
npx skills add FakeHoward/capstone-agent-skills \
  --skill '*' \
  -a cursor -a claude-code -a codex \
  -g -y --copy

# Project install (from your app repo)
npx skills add FakeHoward/capstone-agent-skills \
  --skill '*' \
  -a cursor -a claude-code -a codex \
  -y --copy
```

Package installer (same skill files; agent roots below):

```bash
# All agents, personal scope
npx github:FakeHoward/capstone-agent-skills --agent all --scope personal

# One agent, project scope
npx github:FakeHoward/capstone-agent-skills --agent claude --scope project
npx github:FakeHoward/capstone-agent-skills --agent codex --scope project
npx github:FakeHoward/capstone-agent-skills --agent cursor --scope project

# Dry-run / force replace (keeps <name>.bak.<timestamp>)
npx github:FakeHoward/capstone-agent-skills --agent all --dry-run
npx github:FakeHoward/capstone-agent-skills --agent cursor --force
```

| Agent | Personal | Project |
| --- | --- | --- |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.agents/skills/` | `.agents/skills/` |

Do not install Cursor skills into `~/.cursor/skills-cursor/` (reserved). The package installer refuses that path.

Local checkout (without npx):

```bash
node bin/capstone-agent-skills.js --agent all --scope personal
# Cursor-only shells still work:
./scripts/install.sh --scope personal
.\scripts\install.ps1 -Scope personal
```

## Why the skills are small

Agents match skills from each `SKILL.md` description (WHAT + WHEN) and from `triggers.json`. One Capstone mega-skill burns context and makes trigger terms collide. Smaller units stay under the 500-line `SKILL.md` check, keep required terms unique, and let auto-invoke load one primary skill (a second only when the task spans domains).

Do not set `disable-model-invocation: true` on these skills.

## Skill groups (41)

### Core / API (10)

`capstone-skill-router`, `capstone-core-api`, `capstone-disasm-iteration`, `capstone-detail-aliases`, `capstone-operands-registers`, `capstone-options-syntax`, `capstone-skipdata`, `capstone-performance-concurrency`, `capstone-troubleshooting`, `capstone-v6-migration`

### Build / tooling (8)

Build: `capstone-cmake-build`, `capstone-cross-platform`, `capstone-size-optimized-builds`, `capstone-custom-memory-embedding`

Tooling: `capstone-cstool`, `capstone-cstest-yaml`, `capstone-language-bindings`, `capstone-fuzzing-crash-repro`

### Architectures (23)

`capstone-arch-<name>` for: `aarch64`, `alpha`, `arc`, `arm`, `bpf`, `evm`, `hppa`, `loongarch`, `m680x`, `m68k`, `mips`, `mos65xx`, `ppc`, `riscv`, `sh`, `sparc`, `systemz`, `tms320c64x`, `tricore`, `wasm`, `x86`, `xcore`, `xtensa`

## How to choose a skill

1. If the topic is unclear, start with `capstone-skill-router`.
2. Put the API symbol or arch in the prompt (`cs_open`, `CS_OPT_DETAIL_REAL`, `CS_ARCH_RISCV`, `cstool`).
3. Prefer one primary skill. Add a second only when the work crosses domains.

## Prompt examples

- "Open a Capstone API 6 alpha handle for x86-64, check `cs_errno`, then close it cleanly."
- "Why doesn't `CS_OPT_DETAIL` + `CS_OPT_OFF` turn detail off?"
- "Port Capstone 5 code that still uses `CS_ARCH_ARM64` and `CS_ARCH_SYSZ` to API 6."
- "Disassemble Thumb-2 with `CS_ARCH_ARM` and list valid MCLASS/V8 mode combos."
- "Enable skipdata with a custom callback; explain batch vs iter `offset`."
- "Configure a diet + `CAPSTONE_X86_REDUCE` CMake build and say what diet removes."
- "Author a `cstest` YAML case with `is_alias` expectations for RISC-V."
- "Xtensa skipdata jumps 255 bytes. Is that intended?"

## Validation and tests

Stdlib Python validator (no PyYAML / `jsonschema` packages required):

```bash
python scripts/validate_skills.py --capstone /path/to/capstone
python -m unittest discover -s tests -v
node --test tests/node/*.test.js
```

Optional Capstone runtime smoke (needs CMake + a C compiler):

```bash
python scripts/runtime_smoke.py --capstone /path/to/capstone
```

Without a toolchain, runtime scenarios SKIP and exit 0. FAIL means a real command or fixture mismatch after a build exists.

## Version boundaries and current-tree defects

These skills describe Capstone `next` at `1c1f6f4e` (API 6 alpha), not Capstone 4/5 releases. Re-run claims after you change the pin.

- `CS_OPT_DETAIL` latches with `|=`; `CS_OPT_OFF` does not clear detail. Open a new handle instead.
- Skipdata callback `offset`: batch is buffer-relative; iter passes `0` and a remaining slice.
- Do not promise shared-`csh` thread safety. Use one handle per thread. `CS_OPT_MEM` hooks are process-global.
- Xtensa: `skipdata_size` has no `CS_ARCH_XTENSA` case; default `(uint8_t)-1` skips 255 bytes. Treat as a probable defect.
- RISC-V: `CS_MODE_RISCV_BITMANIP` sits outside the allowed mask. Prefer `ZBA` through `ZBS`.
- `cs_regs_access` returns `CS_ERR_ARCH` on PowerPC, Sparc, SystemZ, XCore, TMS320C64x, EVM, MOS65XX, and WASM.

## Contribution

1. Edit `skills/<id>/` (`SKILL.md`, plus `reference.md` / `examples.md` when needed).
2. Keep `name` equal to the directory name. Keep WHAT + `Use when` WHEN. Stay under validator limits.
3. Update `skills.manifest.json` and `triggers.json`.
4. Adjust `claims.json` for source-backed facts.
5. Run validator, Python unit tests, and Node installer tests.
6. Change `skills.manifest.json` `source.commit` only when retargeting another Capstone revision.

## License

MIT. See [LICENSE](LICENSE). Skill text is drawn from Capstone Engine sources and docs; Capstone remains under its upstream license. Pin and provenance are in `skills.manifest.json`.
