# Capstone LoongArch — examples

## LA64 with detail

```c
csh handle;
cs_insn *insn;
size_t n;

if (cs_open(CS_ARCH_LOONGARCH, CS_MODE_LOONGARCH64, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(handle, code, code_size, address, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_loongarch *la = &insn[i].detail->loongarch;
	/* la->format, MEM rewrite: base/index/disp */
}
cs_free(insn, n);
cs_close(&handle);
```

## LA32

```c
cs_open(CS_ARCH_LOONGARCH, CS_MODE_LOONGARCH32, &handle);
```

## Alias real operands (partial aliases)

```c
cs_option(handle, CS_OPT_DETAIL, CS_OPT_DETAIL_REAL | CS_OPT_ON);
/* ret/jr/nop/move: inspect real JIRL/OR/ANDI operands */
```

## Syntax

```c
cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_NO_DOLLAR);
cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_NOREGNAME);
```

## regs_access (index gap)

```c
cs_regs regs_read, regs_write;
uint8_t read_count, write_count;
cs_regs_access(handle, &insn[i],
	regs_read, &read_count, regs_write, &write_count);
/* For indexed MEM, also inspect operands[].mem.index manually */
```

## cstool

```text
cstool loongarch64 0x...
cstool loongarch32 0x...
cstool loongarch64+nodollar 0x...
```
