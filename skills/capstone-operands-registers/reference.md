# Operands / registers reference

## Access enum

Operand access uses `cs_ac_type` (`CS_AC_INVALID`, `CS_AC_READ`, `CS_AC_WRITE`,
combinations) inside arch-specific operand structs (v6 typed field).

## Detail caps (`capstone.h`)

- `MAX_IMPL_R_REGS` 20
- `MAX_IMPL_W_REGS` 47
- `MAX_NUM_GROUPS` 16
- `cs_regs` is `uint16_t[64]` for `cs_regs_access` outputs

## How to verify arch support in code

`cs_regs_access` path:

```c
if (handle->reg_access) {
    handle->reg_access(...);
} else {
    return CS_ERR_ARCH;
}
```

`reg_access` is set only in arch `*Module.c` init. Absence = unsupported.

## Groups

`cs_insn_group` checks `detail->groups[]` against `cs_group_type` /
arch-specific group ids. Common groups: `CS_GRP_JUMP`, `CALL`, `RET`, `INT`,
`IRET`, `PRIVILEGE`, `BRANCH_RELATIVE`.

## Tests

- `tests/unit/riscv_reg_access.c`
- `tests/integration/test_poc.c` (regs_access usage)
- `tests/unit/riscv_op_count_iter.c`
