# Size optimization examples

## Only ARM + AArch64 + X86

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DCAPSTONE_ARCHITECTURE_DEFAULT=OFF \
  -DCAPSTONE_ARM_SUPPORT=ON \
  -DCAPSTONE_AARCH64_SUPPORT=ON \
  -DCAPSTONE_X86_SUPPORT=ON \
  -DCAPSTONE_BUILD_CSTOOL=OFF
cmake --build build
```

## Compact X86-focused engine

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DCAPSTONE_ARCHITECTURE_DEFAULT=OFF \
  -DCAPSTONE_X86_SUPPORT=ON \
  -DCAPSTONE_BUILD_DIET=ON \
  -DCAPSTONE_X86_REDUCE=ON \
  -DCAPSTONE_X86_ATT_DISABLE=ON
cmake --build build
```

## One static lib, register arches per consumer

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DCAPSTONE_USE_ARCH_REGISTRATION=ON
cmake --build build
```

In each consumer, call the needed `cs_arch_register_*()` before `cs_open`.
No public register helpers exist for **HPPA** or **Xtensa** — keep those arches
on the default compile-time table (`CAPSTONE_HPPA_SUPPORT` /
`CAPSTONE_XTENSA_SUPPORT`) instead of selective registration.

## Windows diet preset

```bash
cmake --preset windows-x64-diet
cmake --build --preset build-windows-diet-release
```
