# Capstone MIPS — examples

## MIPS32R5 big-endian

```c
csh handle;
cs_mode mode = CS_MODE_MIPS32R5 | CS_MODE_BIG_ENDIAN;
if (cs_open(CS_ARCH_MIPS, mode, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);
```

## MIPS64 little-endian

```c
cs_open(CS_ARCH_MIPS, CS_MODE_MIPS64 | CS_MODE_LITTLE_ENDIAN, &handle);
```

## microMIPS32R6

```c
cs_open(CS_ARCH_MIPS, CS_MODE_MICRO32R6 | CS_MODE_BIG_ENDIAN, &handle);
```

## Syntax without `$`

```c
cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_NO_DOLLAR);
```

## Replace mode at runtime (full mask)

```c
/* Wrong: drops endian/ISA */
cs_option(handle, CS_OPT_MODE, CS_MODE_MICRO);

/* Right: full combination */
cs_option(handle, CS_OPT_MODE,
	CS_MODE_MICRO | CS_MODE_MIPS32R6 | CS_MODE_BIG_ENDIAN);
```

## Operand unsigned immediate

```c
cs_mips_op *op = &insn->detail->mips.operands[i];
if (op->type == MIPS_OP_IMM) {
	if (op->is_unsigned)
		use(op->uimm);
	else
		use(op->imm);
}
```

## cstool

```text
cstool mips 0x...
cstool mipsbe 0x...
```
