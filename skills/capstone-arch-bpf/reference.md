# Capstone BPF — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_BPF` in `cs.c`:

```
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_BPF_CLASSIC |
  CS_MODE_BPF_EXTENDED | CS_MODE_BIG_ENDIAN)
```

Helper: `EBPF_MODE(mode)` → `mode & CS_MODE_BPF_EXTENDED`.

Both classic and extended require **8-byte** alignment in core.

## Classic vs extended

### Wire format

| | cBPF | eBPF |
|--|------|------|
| Size | 8 | 8; `lddw` = 16 |
| Layout | `op:u16`, `jt`, `jf`, `k:u32` | `op:u8`, reg nibble, `offset:u16`, `k:u32` (+ next imm for lddw) |

### Feature split

**cBPF:** `A`/`X`, `RET`, `TAX`/`TXA`, `M[k]` (`MMEM`), `MSH`, `#len` (`EXT`),
jt/jf jumps, ALU through XOR, word stores to `M[]`, mnemonics `ld`/`ldx`/`st`/`stx`.

**eBPF:** `r0`–`r10`, ALU64, MOV/ARSH/endian/bswap, wide load/store, atomics,
JMP32, CALL/CALLX/EXIT, signed jumps, packet ABS/IND, writable regs R0–R9 only.

Shared class encodings differ: class `0x06` = RET vs JMP32; `0x07` = MISC vs ALU64.

## Runtime options (`BPF_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | `handle->mode = value` (replace) |

No BPF-specific syntax options. Generic `CS_OPT_DETAIL`, skipdata, etc. apply.

## `cs_bpf` summary

Header: `include/capstone/bpf.h`.

| Field | Role |
|-------|------|
| `op_count` | operand count (max 3 in practice; array size 4) |
| `operands[]` | `cs_bpf_op` |

### Operand types

`BPF_OP_REG`, `IMM`, `OFF`, `MEM`, `MMEM`, `MSH`, `EXT`.

`bpf_op_mem`: `base`, `disp`. Extension enum: `BPF_EXT_LEN`.

Per-op: `is_signed`, `is_pkt`, `access`.

### Groups

`BPF_GRP_LOAD`, `STORE`, `ALU`, `JUMP`, `CALL`, `RETURN`, `MISC`.

## Alias support (limited)

Not Capstone Auto-Sync aliases. Present:

1. Enum synonyms after `BPF_INS_ENDING`: `BPF_INS_LD = LDW`, `LDX = LDXW`,
   `ST = STW`, `STX = STXW`.
2. `BPF_insn_name` prints `"ld"`/`"ldx"`/`"st"`/`"stx"` when not eBPF.

No `CS_OPT_SYNTAX` alias toggles. `is_alias` / `alias_id` unused by BPF.

## Register access

- `BPF_global_init` sets `ud->reg_access = BPF_reg_access` (non-DIET).
- Merges implicit regs + explicit `REG` access + `MEM` base reads.
- Requires detail ON. Unavailable in DIET.

## Evidence pointers

- Details: `tests/details/bpf.yaml`
- MC: `tests/MC/BPF/classic-all.yaml`, `classic-be.yaml`, `extended-all.yaml`,
  `extended-be.yaml`
- Disasm/constants: `arch/BPF/BPFDisassembler.c`, `BPFConstants.h`
- Harness: `suite/cstest/src/test_detail_bpf.c`
