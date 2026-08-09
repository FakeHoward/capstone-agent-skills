---
name: capstone-arch-riscv
description: >-
  Guides Capstone RISC-V disassembly: RV32/RV64 modes, working extension flags
  (C/FD/V/A/Z* and vendor groups), cs_riscv detail/CSR ops, alias text options,
  and regs_access. Use when the task involves CS_ARCH_RISCV, include/capstone/
  riscv.h, RISCVModule, compressed decode, or CS_OPT_SYNTAX_NO_ALIAS_TEXT.
---

# Capstone RISC-V

Load only this skill for RISC-V. Do not pull other architecture skills.

## Source of truth

Sibling Capstone tree (`capstone/`):

- `include/capstone/riscv.h` — `cs_riscv`, CSR/`rounding_mode`
- `arch/RISCV/RISCVModule.c`
- `cs.c` — `CS_ARCH_CONFIG_RISCV` allowed mask
- `tests/details/riscv.yaml`, `tests/MC/RISCV/`, and unit tests under
  `tests/unit/` matching glob `riscv_*.c` (not a single literal path)

## Valid modes

Base (pick one width): `CS_MODE_RISCV32` or `CS_MODE_RISCV64`.

Working extension flags (in the allowed mask):

| Flag | Role |
|------|------|
| `CS_MODE_RISCV_C` | compressed (RVC) |
| `CS_MODE_RISCV_FD` | F/D float (YAML may say `RISCV_F`/`RISCV_D`; both map to `FD`) |
| `CS_MODE_RISCV_V` | vector |
| `CS_MODE_RISCV_A` | atomics |
| `CS_MODE_RISCV_E` | RV32E |
| `CS_MODE_RISCV_ZFINX` | Zfinx |
| `CS_MODE_RISCV_ZCMP_ZCMT_ZCE` | Zc* / Zce group |
| `CS_MODE_RISCV_ZICFISS` | Zicfiss |
| `CS_MODE_RISCV_ZBA` / `ZBB` / `ZBC` / `ZBKB` / `ZBKC` / `ZBKX` / `ZBS` | bit-manip subsets |
| `CS_MODE_RISCV_COREV` / `THEAD` / `SIFIVE` / `VENTANA` | vendor groups |

**Do not use `CS_MODE_RISCV_BITMANIP`.** It appears in `cs_mode` and cstool `+bitmanip` but is absent from the allowed mask (open/option → `CS_ERR_MODE` / `CS_ERR_OPTION`). Use the `ZBA`…`ZBS` flags (and vendor `COREV` for XCVbitmanip tests). Defect note: [reference.md](reference.md#defect-cs_mode_riscv_bitmanip).

Runtime `CS_OPT_MODE` **replaces** the mode word. Pass the full combination every time.

## Options and syntax

- Detail / `CS_OPT_DETAIL_REAL`
- `CS_OPT_SYNTAX_NO_ALIAS_TEXT` — suppress all asm aliases (`ret`→`jalr`, …)
- `CS_OPT_SYNTAX_NO_ALIAS_TEXT_COMPRESSED` — suppress aliases only for compressed insns
- Module ORs syntax flags; replaces mode
- Skipdata: 2 if `CS_MODE_RISCV_C`, else 4
- Compat: `CAPSTONE_RISCV_COMPAT_HEADER` exposes legacy `CS_MODE_RISCVC` = `CS_MODE_RISCV_C`

## Detail, alias, regs_access

- Detail: `insn->detail->riscv` — up to 8 ops: `REG`/`IMM`/`MEM`/`FP`/`CSR`; `need_effective_addr`; `rounding_mode`
- Auto-Sync alias fields supported
- `cs_regs_access`: supported (`RISCV_reg_access`); covered by `tests/unit/riscv_reg_access.c`

## Workflow

1. `cs_open(CS_ARCH_RISCV, CS_MODE_RISCV64 | CS_MODE_RISCV_C | …, &handle)`.
2. Enable detail for CSR ops and rounding mode.
3. Choose alias printing via `NO_ALIAS_TEXT` / `_COMPRESSED` as needed.
4. On extension changes, set the complete mode mask with `CS_OPT_MODE`.
5. For bit-manip, OR the specific `Z*` flags — never `CS_MODE_RISCV_BITMANIP`.

## Traps

- Mode replace drops unspecified extension bits.
- Compressed vs non-compressed mix needs `CS_MODE_RISCV_C` (and affects skipdata).
- Dead `BITMANIP` flag / cstool `+bitmanip` rejects at validation.
- Alias text options interact: `NO_ALIAS_TEXT` overrides compressed-only behavior.

## More

- Mask, defect, operand tables: [reference.md](reference.md)
- Snippets: [examples.md](examples.md)
