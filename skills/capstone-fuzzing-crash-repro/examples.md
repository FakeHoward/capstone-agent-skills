# Fuzz crash repro examples

## From OSS-Fuzz byte dump

Report footer:

```text
0x7,0xe8,0x3,0x4e,0xc0,0xf8,
```

Steps:

```bash
# Map 0x7 via suite/fuzz/platform.c or fuzz_decode_platform (Makefile target)
./fuzz_decode_platform 0x7
# cstool arch+mode = aarch64

cstool -d aarch64 0xe8,0x03,0x4e,0xc0,0xf8,
```

## CMake onefile target

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --target fuzz_disasm
# feed a raw file; behavior follows onefile.c + fuzz_disasm.c
./build/fuzz_disasm /path/to/crash-input
```

Exact binary path depends on generator (`build/fuzz_disasm`,
`build/Debug/fuzz_disasm`, …).

## Platform byte spot checks

```bash
./fuzz_decode_platform 0x0   # x32
./fuzz_decode_platform 0x1   # x64
./fuzz_decode_platform 0x7   # aarch64
```

Names come from `platforms[]` in `suite/fuzz/platform.c`.
