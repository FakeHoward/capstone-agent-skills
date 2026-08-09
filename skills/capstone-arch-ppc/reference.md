# Capstone PowerPC — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_PPC` in `cs.c`:

```
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_32 | CS_MODE_64 |
  CS_MODE_BIG_ENDIAN | CS_MODE_QPX | CS_MODE_PS |
  CS_MODE_BOOKE | CS_MODE_SPE | CS_MODE_AIX_OS |
  CS_MODE_PWR7 | CS_MODE_PWR8 | CS_MODE_PWR9 | CS_MODE_PWR10 |
  CS_MODE_PPC_ISA_FUTURE | CS_MODE_MSYNC |
  CS_MODE_MODERN_AIX_AS)
```

## Runtime option behavior (`PPC_option`)

```c
if (type == CS_OPT_SYNTAX)
	handle->syntax = (int)value;

if (type == CS_OPT_MODE) {
	if (value == CS_MODE_LITTLE_ENDIAN) {
		handle->mode = handle->mode & ~CS_MODE_BIG_ENDIAN;
		return CS_ERR_OK;
	}
	handle->mode |= (cs_mode)value;
	if (value & CS_MODE_MSYNC)
		handle->mode |= (cs_mode)CS_MODE_BOOKE;
}
```

Implications:

1. OR is the default for feature/endian/width bits.
2. Passing exactly `CS_MODE_LITTLE_ENDIAN` is the only path that clears BE.
3. Passing `CS_MODE_BIG_ENDIAN` ORs BE back on.
4. `MSYNC` ⇒ `BOOKE`.

## `cs_ppc` summary

`#define NUM_PPC_OPS 8`.

| Field | Role |
|-------|------|
| `bc` | branch condition block (`bo`/`bi`, CR bit, predicates, hints) |
| `update_cr0` | dotted insn updates CR0 |
| `format` | `ppc_insn_form` encoding shape |
| `op_count` / `operands[8]` | `REG` / `IMM` / `MEM` |

`ppc_op_mem`: `base`, `disp`, `offset`.

Helpers in `ppc.h`: `cs_ppc_bc_decr_ctr`, predicate helpers around `ppc_bc`.

## Alias support

Auto-Sync. Examples in `tests/details/ppc.yaml`: `lis`, `li` with `is_alias: 1`.

Release guide also documents rotate aliases (`rotldi` vs real `rldicl`) with `-r` / `CS_OPT_DETAIL_REAL`.

## Register access — unsupported

`PPC_global_init` sets printer/disasm/name callbacks only. It does **not** assign `ud->reg_access`.

`cs_regs_access` then takes the unsupported path (`CS_ERR_ARCH`).

Do not document workarounds that invent a PPC `regs_access` implementation unless the tree gains one.

## Skipdata

4 bytes.

## Evidence pointers

- `arch/PowerPC/PPCModule.c` — LE/MSYNC behavior
- `arch/PowerPC/PPCInstPrinter.c` — `NOREGNAME` / `PERCENT`
- `tests/details/ppc.yaml`
- `docs/cs_v6_release_guide.md` — PPC breaking changes / alias section
