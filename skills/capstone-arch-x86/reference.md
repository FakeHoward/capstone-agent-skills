# Capstone x86 — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_X86` in `cs.c`:

```
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_32 | CS_MODE_64 | CS_MODE_16)
```

No `CS_MODE_BIG_ENDIAN`.

## Runtime option behavior (`X86_option`)

### `CS_OPT_MODE`

```
handle->mode = (cs_mode)value;
regsize_map = (value == CS_MODE_64) ? regsize_map_64 : regsize_map_32;
```

### `CS_OPT_SYNTAX`

| value | result |
|-------|--------|
| `DEFAULT` / `INTEL` | Intel printer, Intel syntax |
| `MASM` | Intel printer, MASM syntax |
| `ATT` | ATT printer if built; else `CS_ERR_X86_ATT` or `CS_ERR_DIET` |
| other | `CS_ERR_OPTION` |

## `cs_x86` summary

Header: `include/capstone/x86.h`.

Notable fields:

- `prefix[4]` — LOCK/REP*, segment, OPSIZE, ADDRSIZE (`x86_prefix`)
- `opcode[4]`, `rex`, `addr_size`, `modrm`, `sib`, `disp`
- `sib_index` / `sib_scale` / `sib_base`
- `xop_cc`, `sse_cc`, `avx_cc`, `avx_rm`, `avx_sae`
- `eflags` / FPU flag macros
- `encoding` — `modrm_offset`, `disp_offset`/`disp_size`, `imm_offset`/`imm_size`
- `op_count` / `operands[8]` — each with `size`, `access`, AVX bcast / zero-opmask

Memory operand: `segment`, `base`, `index`, `scale`, `disp`.

## Alias support

X86 is not an Auto-Sync GenCS backend. Do not rely on `cs_insn.is_alias` / `alias_id` for x86. Mnemonics come from the X86 printer tables.

## Register access

Installed in `X86_global_init` unless `CAPSTONE_DIET`. Detail tests in `tests/details/x86.yaml` show `regs_read` / `regs_write` and eflags.

## Build-time variants

| Macro | Effect |
|-------|--------|
| `CAPSTONE_X86_ATT_DISABLE` | ATT option returns `CS_ERR_X86_ATT` |
| `CAPSTONE_X86_REDUCE` | reduced insn/table set; query `CS_SUPPORT_X86_REDUCE` |
| `CAPSTONE_DIET` | empty mnemonic/op_str paths; ATT → `CS_ERR_DIET`; no `reg_access` |

## Skipdata

1 byte.

## Evidence pointers

- `tests/details/x86.yaml` — 16/32/64 detail, encoding offsets
- `tests/issues/x86-prefixes.yaml`, `x86-mandatory-prefixes.yaml`, `x86-xacquire-xrelease.yaml`
- `arch/X86/X86Disassembler.c`, `X86IntelInstPrinter.c`, `X86ATTInstPrinter.c`, `X86Mapping.c`
