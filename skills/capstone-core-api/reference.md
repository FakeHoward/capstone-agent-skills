# Core API reference

## Version macros (`capstone.h`)

- `CS_API_MAJOR` / `CS_API_MINOR` = 6 / 0 on current next tip.
- `CS_NEXT_VERSION` tracks bleeding-edge next-branch bumps.
- `CS_VERSION_PRE_RELEASE` is an alpha identifier on this tree
  (`CS_VERSION_ALPHA11` at verification time). Prefer `cs_version()` at runtime
  over hard-coding package extras.

## `cs_support`

- Pass `cs_arch` (including `CS_ARCH_ALL`) to query compiled-in engines.
- `CS_SUPPORT_DIET` and `CS_SUPPORT_X86_REDUCE` are special query values
  (`CS_ARCH_ALL + 1/2`).

## Handle ownership

- `csh` is an opaque `uintptr_t` wrapping `cs_struct *`.
- One logical engine instance per successful `cs_open`.
- `cs_close` frees engine state and sets `*handle = 0`.

## Memory hooks

```c
cs_opt_mem mem = { my_malloc, my_calloc, my_realloc, my_free, my_vsnprintf };
cs_option(0, CS_OPT_MEM, (uintptr_t)&mem);
```

Hooks are global statics in `cs.c` (`cs_mem_malloc`, …). Changing them races
with any concurrent Capstone use. See performance-concurrency skill.

## What this skill does not cover

- Detail/`DETAIL_REAL` latching (`|=`) → detail-aliases
- Batch vs iter → disasm-iteration
- Arch rename migration → v6-migration
