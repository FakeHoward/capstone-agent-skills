# Capstone TriCore examples

## TC1.6.2 with detail

```c
#include <capstone/capstone.h>

csh h;
cs_insn *insn;
size_t n;
uint8_t code[] = { 0x12, 0x00 }; /* add d0, d15, d0 */

cs_open(CS_ARCH_TRICORE, CS_MODE_TRICORE_162, &h);
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(h, code, sizeof(code), 0, 0, &insn);
cs_tricore *tc = &insn[0].detail->tricore;
for (uint8_t i = 0; i < tc->op_count; i++) {
    cs_tricore_op *op = &tc->operands[i];
    if (op->type == TRICORE_OP_REG)
        printf("reg %s access=%u\n", cs_reg_name(h, op->reg), op->access);
    else if (op->type == TRICORE_OP_MEM)
        printf("mem base=%s disp=%lld\n",
               cs_reg_name(h, op->mem.base), (long long)op->mem.disp);
}
if (tc->update_flags)
    puts("updates flags");
cs_free(insn, n);
cs_close(&h);
```

## Runtime version switch

```c
csh h;
cs_open(CS_ARCH_TRICORE, CS_MODE_TRICORE_160, &h);
cs_option(h, CS_OPT_MODE, CS_MODE_TRICORE_162); /* applied */
/* big endian rejected: CS_ERR_OPTION from core mask check */
cs_option(h, CS_OPT_MODE, CS_MODE_TRICORE_162 | CS_MODE_BIG_ENDIAN);
cs_close(&h);
```

## regs_access

```c
cs_regs r, w;
uint8_t nr, nw;
cs_regs_access(h, &insn[0], r, &nr, w, &nw);
```

## cstool

```bash
cstool -d tc162 "09 cf bc f5"
cstool -d tc180 "12 00"
```
