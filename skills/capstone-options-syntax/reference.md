# Options / syntax reference

## `cs_opt_type` list

`CS_OPT_SYNTAX`, `CS_OPT_DETAIL`, `CS_OPT_MODE`, `CS_OPT_MEM`,
`CS_OPT_SKIPDATA`, `CS_OPT_SKIPDATA_SETUP`, `CS_OPT_MNEMONIC`,
`CS_OPT_UNSIGNED`, `CS_OPT_ONLY_OFFSET_BRANCH`, `CS_OPT_LITBASE`.

## Compile-time syntax opt-outs

Errors if built without a syntax:

- `CS_ERR_X86_ATT`
- `CS_ERR_X86_INTEL`
- `CS_ERR_X86_MASM`

## Mnemonic customization

```c
cs_opt_mnem m = { .id = X86_INS_JNE, .mnemonic = "jnz" };
cs_option(h, CS_OPT_MNEMONIC, (uintptr_t)&m);
/* restore default */
cs_opt_mnem r = { .id = X86_INS_JNE, .mnemonic = NULL };
cs_option(h, CS_OPT_MNEMONIC, (uintptr_t)&r);
```

Stored in a per-handle linked list (`mnem_list` in `cs_priv.h`).

## Mode changes

`CS_OPT_MODE` rejects bits in `arch_disallowed_mode_mask` with
`CS_ERR_OPTION`. Prefer opening with the right mode when possible; runtime
mode changes are for known-safe switches (e.g. ARM Thumb).

## LITBASE

Xtensa literal base (`cs_struct.LITBASE`, default 0 until `CS_OPT_LITBASE`):

- LSB (`value & 1`) enables Extended L32R resolution
- Base address is `value & 0xfffff000` (bits `[31:12]`), matching
  `Xtensa_L32R_Value` in `XtensaMapping.c`

Do not use the stale `cs_priv.h` comment that says bits `[23:8]`.
Pass `base | 1` (see arch-xtensa skill).
