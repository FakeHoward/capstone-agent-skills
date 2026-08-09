# cstool reference

## Sources

- CLI and arch tables: `cstool/cstool.c`
- Short user doc: `cstool/README.md`
- CMake target: root `CMakeLists.txt` (`add_executable(cstool ...)`)
- Optional invalid-input smoke script for developers: `suite/run_invalid_cstool.sh`

## Output layout (basic mode)

Per instruction: offset, opcodes, then mnemonic/operands
(`cstool/README.md`). Detail mode (`-d`) prints arch-specific fields via the
`cstool_*.c` printers.

## Arch-specific syntax options

`cstool` supports extra syntax tokens after arch (ATT, Intel, MASM, Motorola,
noregname, percent, etc.) when those options apply to the selected arch. The
runtime help lists only options whose arches are present in the linked library
(`cs_support`).

## Relation to tests

YAML regression tests are run with `cstest` / `cstest_py`, not cstool.
`cstool` remains the practical manual disassembler and fuzz reproducer front
end.

## Deprecated Make

`cstool/Makefile` may exist for legacy builds; prefer the CMake `cstool` target.
