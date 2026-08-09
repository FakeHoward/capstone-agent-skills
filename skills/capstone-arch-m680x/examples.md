# Capstone M680X — examples

## Open one chip (preferred)

```c
csh h;
if (cs_open(CS_ARCH_M680X, CS_MODE_M680X_6301, &h) != CS_ERR_OK)
	return -1;
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);
```

## At least one chip required

```c
/* CS_ERR_MODE — no default CPU */
cs_open(CS_ARCH_M680X, 0, &h);
```

## Multiple chip bits: priority, not an error

```c
/* Open succeeds; decode uses 6800 (higher priority than 6809) */
cs_open(CS_ARCH_M680X,
	CS_MODE_M680X_6800 | CS_MODE_M680X_6809, &h);
```

Prefer a single flag so priority never surprises you.

## Walk indexed / direct operands

```c
cs_m680x *m = &insn->detail->m680x;
for (int i = 0; i < m->op_count; i++) {
	cs_m680x_op *op = &m->operands[i];
	switch (op->type) {
	case M680X_OP_INDEXED:
		/* op->idx.base_reg, op->idx.offset, op->access */
		break;
	case M680X_OP_DIRECT:
		/* op->direct_addr */
		break;
	default:
		break;
	}
}
```

## cstool

```text
cstool -d hd6301 "6b1000"
cstool -d m6809 "..."
```
