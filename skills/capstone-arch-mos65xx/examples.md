# Capstone MOS65XX — examples

## 6502 with Motorola syntax

```c
csh h;
cs_open(CS_ARCH_MOS65XX, CS_MODE_MOS65XX_6502, &h);
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);
cs_option(h, CS_OPT_SYNTAX, CS_OPT_SYNTAX_MOTOROLA);
```

## 65816 via LONG_MX (preferred)

```c
cs_open(CS_ARCH_MOS65XX, CS_MODE_MOS65XX_65816_LONG_MX, &h);
/* long_m = 1, long_x = 1, cpu = 65816 */
```

## 65816 with only 16-bit M

```c
cs_open(CS_ARCH_MOS65XX, CS_MODE_MOS65XX_65816_LONG_M, &h);
```

## Runtime width change (replace mode)

```c
cs_option(h, CS_OPT_MODE, CS_MODE_MOS65XX_65816_LONG_X);
```

## Do not open with bare 65816 flag

```c
/* Fails mask check: CS_ERR_MODE */
cs_open(CS_ARCH_MOS65XX, CS_MODE_MOS65XX_65816, &h);
```

## Read address mode + operands

```c
cs_mos65xx *m = &insn->detail->mos65xx;
/* m->am, m->modifies_flags */
for (int i = 0; i < m->op_count; i++) {
	if (m->operands[i].type == MOS65XX_OP_IMM)
		/* m->operands[i].imm */;
	else if (m->operands[i].type == MOS65XX_OP_MEM)
		/* m->operands[i].mem */;
}
```

## cstool

```text
cstool -d 6502 "a112"
cstool -d 65816 "..."
```
