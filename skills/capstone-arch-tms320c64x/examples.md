# Capstone TMS320C64x — examples

## Big-endian open with detail

```c
csh h;
cs_open(CS_ARCH_TMS320C64X, CS_MODE_BIG_ENDIAN, &h);
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);

cs_insn *insn;
size_t n = cs_disasm(h, code, len, 0x1000, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_tms320c64x *t = &insn[i].detail->tms320c64x;
	/* t->funit.unit / .side / .crosspath */
	/* t->condition.reg / .zero */
	/* t->parallel */
	for (int j = 0; j < t->op_count; j++) {
		if (t->operands[j].type == TMS320C64X_OP_MEM) {
			/* t->operands[j].mem.* */
		}
	}
}
cs_free(insn, n);
cs_close(&h);
```

## Reset endian: reopen

```c
/* mode |= will not clear CS_MODE_BIG_ENDIAN */
cs_close(&h);
cs_open(CS_ARCH_TMS320C64X, CS_MODE_LITTLE_ENDIAN, &h);
```

## regs_access unsupported

```c
/* CS_ERR_ARCH */
cs_regs_access(h, insn, ...);
```

## cstool

```text
cstool -d tms320c64x "01ac8840"
cstool -d tms320c64xle "..."
```
