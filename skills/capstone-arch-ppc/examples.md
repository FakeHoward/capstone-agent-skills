# Capstone PowerPC — examples

## 32-bit big-endian with detail

```c
csh handle;
cs_mode mode = CS_MODE_32 | CS_MODE_BIG_ENDIAN;
if (cs_open(CS_ARCH_PPC, mode, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);
```

## Enable Book-E via MSYNC

```c
cs_option(handle, CS_OPT_MODE, CS_MODE_MSYNC);
/* mode now also has CS_MODE_BOOKE */
```

## Switch to little-endian (clears BE)

```c
cs_option(handle, CS_OPT_MODE, CS_MODE_LITTLE_ENDIAN);
```

## Alias vs real detail

```c
/* alias operands (default when detail on) */
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

/* force real instruction operands */
cs_option(handle, CS_OPT_DETAIL, CS_OPT_DETAIL_REAL | CS_OPT_ON);
```

## Syntax: numeric regs / percent prefix

```c
cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_NOREGNAME);
cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_PERCENT);
```

Note: PPC assigns `syntax` (replace). Combine flags in one value if both are required:

```c
cs_option(handle, CS_OPT_SYNTAX,
	CS_OPT_SYNTAX_NOREGNAME | CS_OPT_SYNTAX_PERCENT);
```

## regs_access — expect failure

```c
cs_err e = cs_regs_access(handle, insn, r_regs, &rc, w_regs, &wc);
/* e == CS_ERR_ARCH on current PPC backend */
```

## cstool

```text
cstool ppc32 0x...
cstool ppc64 0x...
cstool ppc32+noregname 0x...
```
