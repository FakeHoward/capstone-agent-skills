# Cross-platform reference

## Shipped CMake toolchain examples (`cross_configs/`)

| File | Intent (from name + comments) |
|------|-------------------------------|
| `linux_arm_ubuntu24.cmake` | arm-linux-gnueabihf + qemu-arm-static |
| `linux_arm_fedora42_musl.cmake` | Fedora musl ARM |
| `linux_mips_ubuntu24.cmake` | MIPS |
| `linux_mips64_ubuntu24.cmake` | MIPS64 |
| `linux_ppc64_ubuntu24.cmake` | PPC64 |
| `linux_s390x_ubuntu24.cmake` | s390x on Ubuntu |
| `linux_s390x_fedora42.cmake` | s390x on Fedora |
| `linux_x86.cmake` | Linux x86 |
| `windows_i686_ubuntu24.cmake` | MinGW-style Windows from Ubuntu |

Each file sets `CMAKE_SYSTEM_*`, compilers, find-root modes, and often
`CMAKE_CROSSCOMPILING_EMULATOR`. Host package install lines are comments in
the files; install those packages on the host before configuring.

## Windows tree

`windows/` holds `winkernel_mm.c` / `winkernel_mm.h` for kernel-mode alloc
wrappers used when Capstone is built/linked for Windows drivers. Core user-mode
Windows builds go through normal CMake/MSVC as in `BUILDING.md`. Sample driver
integration is under `contrib/cs_driver/` (VS solution), not under `windows/`.

## MSVC runtime

`CAPSTONE_BUILD_STATIC_MSVC_RUNTIME` embeds static MSVC runtime on Windows.
Its default tracks `CAPSTONE_BUILD_SHARED_LIBS` (ON when shared is ON).

## Deprecated Make cross paths (`COMPILE_MAKE.TXT`)

Only for legacy maintenance:

- `./make.sh cross-win32` / `cross-win64`
- `./make.sh ios_*` / `ios`
- `NDK=... ./make.sh cross-android arm|arm64`
- `./make.sh cygwin-mingw32|cygwin-mingw64`
- `./make.sh nix32`

Prefer CMake + toolchain / NDK for new work.

## Xcode / Windows CE

Separate trees exist (`xcode/`, `windowsce/`). Mention them only if the user
targets those environments; they are not the primary CMake path.
