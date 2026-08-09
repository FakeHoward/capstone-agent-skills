# Capstone M68K — examples

## Open 68020 big-endian with detail

```c
csh h;
cs_open(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020, &h);
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);

cs_insn *insn;
size_t n = cs_disasm(h, code, len, 0, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_m68k *m = &insn[i].detail->m68k;
	/* m->op_size, m->operands[j].address_mode, .type, .mem, … */
}
cs_free(insn, n);
cs_close(&h);
```

## Change CPU: reopen (MODE option is a no-op)

```c
/* WRONG expectation: this does not switch the ISA */
cs_option(h, CS_OPT_MODE, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_040);

/* CORRECT */
cs_close(&h);
cs_open(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_040, &h);
```

## regs_access

```c
cs_regs regs_read, regs_write;
uint8_t read_count, write_count;
if (cs_regs_access(h, &insn[0], regs_read, &read_count,
		   regs_write, &write_count) == CS_ERR_OK) {
	/* use counts */
}
```

## cstool

```text
cstool -d m68k40 "f6209000"
cstool -d m68kcf "..."
```
