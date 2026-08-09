# Capstone HPPA examples

## HPPA 2.0 big-endian with detail

```c
#include <capstone/capstone.h>

csh h;
cs_insn *insn;
size_t n;
uint8_t code[] = { 0x00, 0x20, 0x50, 0xa2 }; /* ldsid (sr1,r1), rp BE */

cs_open(CS_ARCH_HPPA, CS_MODE_HPPA_20 | CS_MODE_BIG_ENDIAN, &h);
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(h, code, sizeof(code), 0, 0, &insn);
cs_hppa *hp = &insn[0].detail->hppa;
for (uint8_t i = 0; i < hp->op_count; i++) {
    cs_hppa_op *op = &hp->operands[i];
    switch (op->type) {
    case HPPA_OP_REG:
        printf("reg %s access=%u\n", cs_reg_name(h, op->reg), op->access);
        break;
    case HPPA_OP_MEM:
        printf("mem space=%s base=%s access=%u\n",
               cs_reg_name(h, op->mem.space),
               cs_reg_name(h, op->mem.base),
               op->access);
        break;
    case HPPA_OP_IMM:
        printf("imm 0x%llx\n", (unsigned long long)op->imm);
        break;
    default:
        printf("op type=%u\n", op->type);
        break;
    }
}
cs_free(insn, n);
cs_close(&h);
```

## Little-endian HPPA 2.0

```c
cs_open(CS_ARCH_HPPA, CS_MODE_HPPA_20 | CS_MODE_LITTLE_ENDIAN, &h);
/* same as CS_MODE_HPPA_20 alone */
```

## Runtime mode change

```c
cs_open(CS_ARCH_HPPA, CS_MODE_HPPA_11 | CS_MODE_BIG_ENDIAN, &h);
cs_option(h, CS_OPT_MODE, CS_MODE_HPPA_20 | CS_MODE_BIG_ENDIAN);
```

## Wide 2.0

```c
cs_open(CS_ARCH_HPPA, CS_MODE_HPPA_20W | CS_MODE_BIG_ENDIAN, &h);
```

## regs_access

```c
cs_regs r, w;
uint8_t nr, nw;
cs_regs_access(h, &insn[0], r, &nr, w, &nw);
```

## cstool

```bash
cstool -d hppa20be "00 20 50 a2 00 01 58 20"
cstool -d hppa11be "00 20 50 a2"
cstool -d hppa20 "a2 50 20 00"
```
