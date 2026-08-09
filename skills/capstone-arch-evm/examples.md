# Capstone EVM — examples

## Open mode 0 with detail

```c
csh h;
if (cs_open(CS_ARCH_EVM, 0, &h) != CS_ERR_OK)
	return -1;
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);

cs_insn *insn;
size_t n = cs_disasm(h, code, len, 0, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_evm *e = &insn[i].detail->evm;
	/* e->pop, e->push, e->fee */
	/* insn[i].mnemonic / insn[i].op_str / insn[i].bytes */
}
cs_free(insn, n);
cs_close(&h);
```

## Nonzero mode fails

```c
cs_open(CS_ARCH_EVM, CS_MODE_BIG_ENDIAN, &h);  /* CS_ERR_MODE */
```

## No regs_access

```c
cs_regs_access(h, &insn[0], ...);  /* CS_ERR_ARCH */
```

## cstool

```text
cstool -d evm "606150"
```

Expect `push1` / `pop` with `push`/`pop`/`fee` in detail (see
`tests/details/evm.yaml`).
