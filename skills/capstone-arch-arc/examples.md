# Capstone ARC — examples

## LE with detail

```c
csh handle;
cs_insn *insn;
size_t n;

if (cs_open(CS_ARCH_ARC, CS_MODE_LITTLE_ENDIAN, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(handle, code, code_size, address, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_arc *a = &insn[i].detail->arc;
	for (uint8_t o = 0; o < a->op_count; o++) {
		if (a->operands[o].type == ARC_OP_REG)
			/* reg + access */;
		else if (a->operands[o].type == ARC_OP_IMM)
			/* imm — may be CC, offset, or branch target */;
	}
}
cs_free(insn, n);
cs_close(&handle);
```

## regs_access

```c
cs_regs regs_read, regs_write;
uint8_t read_count, write_count;
if (cs_regs_access(handle, &insn[i],
		regs_read, &read_count,
		regs_write, &write_count) == CS_ERR_OK) {
	/* may include status32 for predicated ops */
}
```

## Big-endian rejected

```c
/* CS_ERR_MODE */
cs_open(CS_ARCH_ARC, CS_MODE_BIG_ENDIAN, &handle);
```

## Reconstruct memory from flat ops

```c
/* ld ... prints [rA, off] but detail is REG then IMM */
cs_arc_op *base = &a->operands[j];
cs_arc_op *off  = &a->operands[j + 1];
/* base->type == ARC_OP_REG, off->type == ARC_OP_IMM */
```

## cstool

```text
cstool arc 0x...
```
