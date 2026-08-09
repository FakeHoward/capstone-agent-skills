# Troubleshooting reference

## `cs_err` map (caller-focused)

| Code | Typical trigger |
| --- | --- |
| `CS_ERR_OK` | Success |
| `CS_ERR_MEM` | OOM in open/disasm/malloc |
| `CS_ERR_ARCH` | Bad arch to open, or `regs_access` unsupported |
| `CS_ERR_HANDLE` / `CS_ERR_CSH` | Invalid handle arguments |
| `CS_ERR_MODE` | Illegal mode bits at open |
| `CS_ERR_OPTION` | Illegal option/mode change |
| `CS_ERR_DETAIL` | Detail-required API without detail/pointer |
| `CS_ERR_MEMSETUP` | Memory hooks unset in no-sys-dyn-mem builds |
| `CS_ERR_VERSION` | Binding/engine mismatch |
| `CS_ERR_DIET` | Unavailable in diet build |
| `CS_ERR_SKIPDATA` | Detail-like API on data insn |
| `CS_ERR_X86_*` | Syntax built out |

## Arches without `reg_access` (CS_ERR_ARCH)

PPC, Sparc, SystemZ, XCore, TMS320C64x, EVM, MOS65XX, WASM.

## Skipdata default gap

Present in `skipdata_size`: ARM, AArch64, Mips, PPC, Sparc, SystemZ, X86,
XCore, M68K, TMS320C64x, M680X, EVM, WASM, MOS65XX, BPF, RISCV, SH, TriCore,
Alpha, HPPA, LoongArch, ARC.

Absent (falls through to 255): **Xtensa** (and any future arch not added).

## Useful integration tests

- `tests/integration/test_iter.c`
- `tests/integration/test_skipdata.c`
- `tests/integration/test_poc.c`
- `tests/unit/riscv_op_count_iter.c`
