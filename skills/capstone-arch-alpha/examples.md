# Capstone Alpha examples

## Little-endian detail

```c
#include <capstone/capstone.h>

csh h;
cs_insn *insn;
size_t n;
uint8_t code[] = { 0x02, 0x00, 0xbb, 0x27 }; /* ldah $29,2($27) LE */

cs_open(CS_ARCH_ALPHA, CS_MODE_LITTLE_ENDIAN, &h);
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(h, code, sizeof(code), 0, 0, &insn);
cs_alpha *a = &insn[0].detail->alpha;
for (uint8_t i = 0; i < a->op_count; i++) {
    cs_alpha_op *op = &a->operands[i];
    if (op->type == ALPHA_OP_REG)
        printf("reg %s\n", cs_reg_name(h, op->reg));
    else if (op->type == ALPHA_OP_IMM)
        printf("imm 0x%llx\n", (unsigned long long)op->imm);
}

cs_regs r, w;
uint8_t nr, nw;
cs_regs_access(h, &insn[0], r, &nr, w, &nw);
cs_free(insn, n);
cs_close(&h);
```

## Big-endian same instruction

```c
uint8_t be[] = { 0x27, 0xbb, 0x00, 0x02 };
cs_open(CS_ARCH_ALPHA, CS_MODE_BIG_ENDIAN, &h);
```

## Runtime endian switch

```c
cs_open(CS_ARCH_ALPHA, CS_MODE_LITTLE_ENDIAN, &h);
cs_option(h, CS_OPT_MODE, CS_MODE_BIG_ENDIAN); /* applied */
```

## cstool

```bash
cstool -d alpha "02 00 bb 27 50 7a bd 23"
cstool -d alphabe "27 bb 00 02 23 bd 7a 50"
```
