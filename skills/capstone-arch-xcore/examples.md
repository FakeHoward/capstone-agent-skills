# Capstone XCore — examples

## Open and disassemble with detail

```c
csh handle;
cs_insn *insn;
size_t count;

if (cs_open(CS_ARCH_XCORE, CS_MODE_BIG_ENDIAN, &handle) != CS_ERR_OK)
	return -1;

cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

count = cs_disasm(handle, code, code_size, address, 0, &insn);
for (size_t i = 0; i < count; i++) {
	cs_xcore *x = &insn[i].detail->xcore;
	for (int j = 0; j < x->op_count; j++) {
		cs_xcore_op *op = &x->operands[j];
		if (op->type == XCORE_OP_REG)
			/* op->reg */;
		else if (op->type == XCORE_OP_MEM)
			/* op->mem.base, op->mem.disp, op->mem.direct */;
	}
}
cs_free(insn, count);
cs_close(&handle);
```

## Do not call regs_access

```c
/* Always CS_ERR_ARCH for XCore */
cs_regs_access(handle, &insn[0], r_read, &n_read, r_write, &n_write);
```

## cstool

```text
cstool xcore "fe0ffe17"
```

Matches `tests/details/xcore.yaml` style detail checks (`get r11, ed`,
`ldw et, sp[4]`, …).
