# Capstone HPPA reference

## Modes

Static config in `cs.c` (under `CAPSTONE_HAS_HPPA`):

```
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_BIG_ENDIAN | CS_MODE_HPPA_11 |
  CS_MODE_HPPA_20 | CS_MODE_HPPA_20W)
```

| Flag | Meaning |
| --- | --- |
| `CS_MODE_HPPA_11` | PA-RISC 1.1 |
| `CS_MODE_HPPA_20` | PA-RISC 2.0 |
| `CS_MODE_HPPA_20W` | PA-RISC 2.0 wide (`HPPA_20 | (1<<3)`) |
| `CS_MODE_LITTLE_ENDIAN` (`0`) | LE |
| `CS_MODE_BIG_ENDIAN` | BE |

Combine **one** version with an endian. Tests and MC files cover
`HPPA_11`/`HPPA_20` × LE/BE. Wide mode affects displacement extraction
(`MODE_IS_HPPA_20W`).

Instruction alignment / default skip size is **4**.

## Runtime options

`HPPA_option` (**replace**, not OR):

- `CS_OPT_MODE` → `handle->mode = value`
- Other types → `CS_ERR_OK` without changes (including syntax)

Core options (`CS_OPT_DETAIL`, skipdata, …) work normally.

## Detail / operands

`cs_hppa`: `op_count`, `operands[NUM_HPPA_OPS]` (`5`).

`hppa_op_type`:

| Type | Use |
| --- | --- |
| `HPPA_OP_REG` | General / FP / space / control regs |
| `HPPA_OP_IMM` | Immediate |
| `HPPA_OP_MEM` | `hppa_mem` (`base`, `space`) |
| `HPPA_OP_IDX_REG` | Index register (special) |
| `HPPA_OP_DISP` | Displacement (special) |
| `HPPA_OP_TARGET` | Branch target (special) |

Each `cs_hppa_op` has `access` (`CS_AC_READ` / `WRITE` / `READ_WRITE`).

Asm completers (`,w`, cache hints, …) are applied via internal `MI->hppa_ext`
modifiers during print. That structure is **not** part of public `cs_detail`.

Groups include computation, mem_ref, branch, sysctrl, float, etc.

## Alias and regs_access

| Feature | Support |
| --- | --- |
| Capstone `is_alias` | No |
| Print modifiers | Yes (internal `hppa_ext`) |
| Operand `access` | Yes |
| `HPPA_reg_access` | Yes — REG/IDX_REG/MEM (space + base) |

## Workflows

1. Open with ISA version + endian matching the binary (HP-UX BE is common).
2. Enable detail; decode space registers on MEM ops (`mem.space`).
3. Prefer printed mnemonic/op_str for completers; do not expect modifiers in
   `cs_hppa`.
4. Use `cs_regs_access` for aggregated register sets.
5. Switch `HPPA_11` ↔ `HPPA_20` / wide with `CS_OPT_MODE` when needed.

## Pitfalls

- Opening without a version bit may accept the mask but miss 1.1/2.0-gated
  encodings (`MODE_IS_HPPA_20` checks).
- LE vs BE: same logical insn bytes differ; fixtures cover both orders.
- `HPPA_OP_MEM` uses space+base, not base+disp; displacements are separate op
  types when present.
- DIET builds omit access / regs_access.

## Troubleshooting

### Missing public arch registration (HPPA and Xtensa)

With `CAPSTONE_USE_ARCH_REGISTRATION`, Capstone exports `cs_arch_register_*`
for other arches (including `wasm`, `sh`, `tricore`, `alpha`, `arc`) but
**does not** declare or define `cs_arch_register_hppa` or
`cs_arch_register_xtensa` in `capstone.h` / `cs.c`.

Effects:

- HPPA/Xtensa stay in the static `all_arch` bitmask when built without
  selective registration.
- Selective-registration builds cannot enable either arch through the public
  register API until matching `cs_arch_register_*` entry points are added.

Workaround: build with HPPA (or Xtensa) on the default arch table
(non-selective registration), or patch in a register helper mirroring
`CS_ARCH_REGISTER(HPPA)` / `CS_ARCH_REGISTER(XTENSA)`.

Do not confuse this with mode errors — failed selective init surfaces as
`CS_ERR_ARCH` from `cs_open` when the arch slot is empty.

## Source map

- Config / missing register export: `cs.c`, `include/capstone/capstone.h`
- Init/options: `arch/HPPA/HPPAModule.c`
- Decode / modifiers: `arch/HPPA/HPPADisassembler.c`, `HPPAInstPrinter.c`
- regs_access: `arch/HPPA/HPPAMapping.c`
- Public types: `include/capstone/hppa.h`
- Fixtures: `tests/details/hppa.yaml`, `tests/MC/HPPA/`
- cstool: `hppa11`, `hppa11be`, `hppa20`, `hppa20be`, `hppa20w`, `hppa20wbe`
