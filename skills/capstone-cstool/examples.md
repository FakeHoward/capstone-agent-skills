# cstool examples

## Basic x86-32

```bash
cstool x32 "90 91"
# also: "0x90 0x91" / "\x90\x91" / "90,91"
```

## Detail

```bash
cstool -d x32 "01 d8"
```

## AArch64 with start address

```bash
cstool aarch64 "01421bd501423bd5" 0x1000
```

## Inspect linked features

```bash
cstool -v
```

## SKIPDATA over mixed bytes (x86-32 fixture)

Matches `fixtures/hex/x86_skipdata.hex` / `tests/features/skipdata.yaml`
(`CS_MODE_32`, not x64):

```bash
cstool -s x32 "8d 4c 32 08 01 d8 81 c6 34 12 00 00 00 91 92" 0x1000
```
