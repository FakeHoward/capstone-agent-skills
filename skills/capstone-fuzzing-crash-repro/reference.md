# Fuzzing / crash repro reference

## Suite layout (`suite/fuzz/`)

| File | Role |
|------|------|
| `platform.c` / `platform.h` | Platform index ↔ arch/mode ↔ cstool name |
| `fuzz_disasm.c` | Core fuzz target logic |
| `onefile.c` | Simple single-file driver (wired into CMake `fuzz_disasm`) |
| `fuzz_decode_platform.c` | Print cstool arch+mode for one hex byte |
| `driverbin.c` | Directory of binary inputs; prints cstool arch hint |
| `drivermc.c` | MC-line oriented driver |
| `fuzz_harness.c` | Additional harness bits |
| `Makefile` | Builds reproducers / libFuzzer binary names |

`suite/README.md` notes MC corpus material under `suite/MC/` generated from
`tests/MC/`.

## CMake note

Root `CMakeLists.txt` comments that moving the fuzzer into its own
CMakeLists breaks OSS-Fuzz’s hard-coded paths; keep the in-tree target where it
is unless that external build is updated.

## Reading an AddressSanitizer / OSS-Fuzz footer

Typical report ends with a byte list and escaped string. Use the numeric list:

- Index 0 → `fuzz_decode_platform`
- Index 1..n → comma-separated hex for cstool, each value width 2

`driverbin.c` also prints `command cstool <name>` from `Data[0]` when replaying
a directory of raw inputs.

## Sanitizer build sketch (legacy Make)

`suite/fuzz/README.md` shows ASAN/`fuzzer-no-link` flags with `make`, and notes
clang if `-fsanitize=fuzzer` is unrecognized. That path depends on a static
Make-built `libcapstone` (`Makefile` errors if `CAPSTONE_STATIC` is not yes).
Prefer documenting it as optional; CMake-first for the core library itself.
