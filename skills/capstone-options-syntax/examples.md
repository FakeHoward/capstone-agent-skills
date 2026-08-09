# Options / syntax examples

## X86 ATT

```c
cs_option(h, CS_OPT_SYNTAX, CS_OPT_SYNTAX_ATT);
```

## RISC-V exact text (no aliases)

```c
cs_option(h, CS_OPT_SYNTAX, CS_OPT_SYNTAX_NO_ALIAS_TEXT);
```

## AArch64 explicit wide immediates

```c
cs_option(h, CS_OPT_SYNTAX, CS_OPT_SYNTAX_AARCH64_EXPLICIT_WIDE_IMM);
```

## Unsigned immediates + offset branches

```c
cs_option(h, CS_OPT_UNSIGNED, CS_OPT_ON);
cs_option(h, CS_OPT_ONLY_OFFSET_BRANCH, CS_OPT_ON);
```
