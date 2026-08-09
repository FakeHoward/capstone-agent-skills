# v6 migration reference

## Compat header mechanics

- `CAPSTONE_AARCH64_COMPAT_HEADER`: exposes ARM64 names mapped to AArch64;
  `cs_arch_register_aarch64` macro-aliased to `cs_arch_register_arm64`.
- `CAPSTONE_SYSTEMZ_COMPAT_HEADER`: SYSZ names; `cs_arch_register_sysz` →
  `cs_arch_register_systemz`.
- Keep defining macros **before** including `capstone.h`.

## sed-oriented rename (from release guide)

Typical replacements:

- `CS_ARCH_ARM64` → `CS_ARCH_AARCH64`
- `ARM64_INS_` / `ARM64_REG_` / `ARM64_OP_` → `AArch64_*`
- `cs_arm64` → `cs_aarch64`
- `CS_ARCH_SYSZ` → `CS_ARCH_SYSTEMZ`
- SYSZ insn/reg prefixes → SystemZ spellings in headers

Always review CC enum value changes; mechanical rename is insufficient when
numeric values changed.

## Tests

- `tests/integration/compat_header/src/test_arm64_compatibility_header.c`
- `tests/integration/compat_header/src/test_sysz_compatibility_header.c`

## API version

`CS_API_MAJOR 6` / `CS_API_MINOR 0` with alpha pre-release markers on next.
Bindings may return `CS_ERR_VERSION` if mismatched.
