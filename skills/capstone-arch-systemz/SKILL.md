---
name: capstone-arch-systemz
description: >-
  Guides Capstone SystemZ disassembly: CS_ARCH_SYSTEMZ, Arch/Z CPU modes,
  CAPSTONE_SYSTEMZ_COMPAT_HEADER, cs_systemz detail, aliases, and missing
  cs_regs_access. Use when working with systemz.h, SystemZModule, SYSZ compat
  names, or s390x Capstone modes.
---

# Capstone SystemZ

Load only this skill for SystemZ work. Do not pull other architecture skills.

## Source of truth

Sibling Capstone tree (`capstone/`):

- `include/capstone/systemz.h` — canonical `cs_systemz`
- `include/capstone/systemz_compatibility.h` — legacy `SYSZ_*` / `cs_sysz`
- `arch/SystemZ/SystemZModule.c`
- `cs.c` — `CS_ARCH_CONFIG_SYSTEMZ`
- `tests/details/systemz.yaml`, `tests/MC/SystemZ/`,
  `tests/integration/compat_header/`

## Valid modes

Allowed: `CS_MODE_BIG_ENDIAN` plus one CPU/ISA level:

| Level | Modes |
|-------|--------|
| Arch8 | `CS_MODE_SYSTEMZ_ARCH8`, `Z10`, `GENERIC` |
| Arch9 | `ARCH9`, `Z196` |
| Arch10 | `ARCH10`, `ZEC12` |
| Arch11 | `ARCH11`, `Z13` |
| Arch12 | `ARCH12`, `Z14` |
| Arch13 | `ARCH13`, `Z15` |
| Arch14 | `ARCH14`, `Z16` |

No CPU bit (e.g. only BE or `0`): feature gate allows **all** features (legacy).

`CS_OPT_MODE` **ORs** bits — stacking CPU modes can fall through to “allow all”.

## Compat header

```c
#define CAPSTONE_SYSTEMZ_COMPAT_HEADER
#include <capstone/capstone.h>
/* CS_ARCH_SYSZ, detail->sysz, SYSZ_* */
```

There is no standalone `sysz.h`. Prefer `CS_ARCH_SYSTEMZ` / `SYSTEMZ_*`.

## Options and detail

- Detail: `CS_OPT_DETAIL` → `insn->detail->systemz` (or `sysz` in compat)
- Ops: `REG`, `IMM`, `MEM` with `SYSTEMZ_AM_BD/BDX/BDL/BDR/BDV`
- Fields: `cc`, `format`, `op_count`, per-op `access`, `imm_width`
- Aliases: yes (`SYSTEMZ_INS_ALIAS_*`, mainly vector)
- `cs_regs_access`: **not supported** (`CS_ERR_ARCH`)

## Workflow

1. Open `CS_ARCH_SYSTEMZ` with `CS_MODE_BIG_ENDIAN | CS_MODE_SYSTEMZ_Z*` (or ARCH*).
2. Enable detail for AM / imm_width / access.
3. Restrict CPU level when testing feature gating; default open allows all.
4. Do not call `cs_regs_access`.

## Traps

- Default (no CPU mode) = allow all features.
- Compat requires `CAPSTONE_SYSTEMZ_COMPAT_HEADER` before include.
- Skipdata advances by **2** (insn size 2/4/6).
- MC strings like `"zEC12"` / `"s390x-linux-gnu"` are not Capstone mode constants.

## More

- Modes, structs, traps: [reference.md](reference.md)
- Open/disasm snippets: [examples.md](examples.md)
