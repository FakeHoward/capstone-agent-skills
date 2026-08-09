# Detail / alias examples

## Default alias details

```c
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);
/* decode ... */
if (insn->is_alias) {
    printf("real=%s alias=%s details=%s\n",
           cs_insn_name(h, insn->id),
           cs_insn_name(h, (unsigned)insn->alias_id),
           insn->usesAliasDetails ? "alias" : "real");
}
```

## Force real details

```c
cs_option(h, CS_OPT_DETAIL, CS_OPT_DETAIL_REAL | CS_OPT_ON);
```

## Incorrect disable attempt

```c
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);
cs_option(h, CS_OPT_DETAIL, CS_OPT_OFF); /* no effect: |= 0 */
/* detail_opt still has CS_OPT_ON */
```

## New handle when detail must be off

```c
cs_close(&h);
cs_open(arch, mode, &h); /* detail_opt starts CS_OPT_OFF */
```
