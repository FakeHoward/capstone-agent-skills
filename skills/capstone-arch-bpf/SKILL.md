---
name: capstone-arch-bpf
description: >-
  Guides Capstone BPF disassembly: classic vs extended modes, endian,
  cs_bpf operands, cBPF mnemonic synonyms, and cs_regs_access. Use when the
  task involves CS_ARCH_BPF, CS_MODE_BPF_CLASSIC/EXTENDED, bpf.h, eBPF, or
  BPFModule.
---

# Capstone BPF

Load only this skill for BPF work. Do not pull other architecture skills.

## Source of truth

Sibling Capstone tree (`capstone/`):

- `include/capstone/bpf.h` — `cs_bpf`, operand types
- `arch/BPF/BPFModule.c` — init, `CS_OPT_MODE`, `reg_access`
- `cs.c` — `CS_ARCH_CONFIG_BPF`
- `tests/details/bpf.yaml`, `tests/MC/BPF/`

## Valid modes

Allowed: `CS_MODE_LITTLE_ENDIAN` (0), `CS_MODE_BIG_ENDIAN`,
`CS_MODE_BPF_CLASSIC` (0), `CS_MODE_BPF_EXTENDED`.

| Target | Mode |
|--------|------|
| cBPF LE (default) | `0` or `CS_MODE_BPF_CLASSIC` |
| cBPF BE | `CS_MODE_BIG_ENDIAN \| CS_MODE_BPF_CLASSIC` |
| eBPF LE | `CS_MODE_BPF_EXTENDED` |
| eBPF BE | `CS_MODE_BIG_ENDIAN \| CS_MODE_BPF_EXTENDED` |

Always set classic vs extended explicitly. Wrong mode reinterprets class 6/7
and the register model. `BPF_option` **assigns** `handle->mode` (replace).

## Options and detail

- Detail: `CS_OPT_DETAIL` → `insn->detail->bpf`
- Ops: `REG`, `IMM`, `OFF`, `MEM`, plus cBPF-only `MMEM`, `MSH`, `EXT`
- Extra op flags: `is_signed`, `is_pkt`, `access`
- Groups: `LOAD`, `STORE`, `ALU`, `JUMP`, `CALL`, `RETURN`, `MISC`
- “Aliases”: enum synonyms `BPF_INS_LD/LDX/ST/STX` + cBPF mnemonic override only
  — **not** Capstone `is_alias` / `alias_id` framework
- `cs_regs_access`: **supported** (non-DIET)

## Workflow

1. Open with classic or extended (+ endian).
2. Enable detail for operands/groups/`cs_regs_access`.
3. Expect 8-byte instructions; eBPF `lddw` is **16** bytes.
4. Prefer `tests/MC/BPF` YAML over legacy `suite/MC` for current mnemonics.

## Traps

- Default open is classic; eBPF bytes mis-decode without `CS_MODE_BPF_EXTENDED`.
- Class `0x06`/`0x07` mean RET/MISC (cBPF) vs JMP32/ALU64 (eBPF).
- R10 is not a writable destination.
- Atomics: type selected by `imm` (+ fetch bit), not only opcode.
- Older `xaddw` strings are outdated; current decode uses `aadd*` / `axchg*`.

## More

- Modes, structs, traps: [reference.md](reference.md)
- Open/disasm snippets: [examples.md](examples.md)
