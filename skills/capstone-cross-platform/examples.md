# Cross-platform examples

## ARM Linux (Ubuntu 24 host packages per toolchain comments)

```bash
# sudo apt install gcc-arm-linux-gnueabihf ... qemu-user-static  # see file header
cmake -DCMAKE_TOOLCHAIN_FILE=cross_configs/linux_arm_ubuntu24.cmake \
  -DCAPSTONE_BUILD_STATIC_LIBS=ON -S . -B build
cmake --build build
```

## s390x + QEMU smoke (pattern from BUILDING.md)

```bash
cmake -DCMAKE_TOOLCHAIN_FILE=cross_configs/linux_s390x_fedora42.cmake \
  -DCAPSTONE_BUILD_STATIC_LIBS=ON -S . -B build
cmake --build build
QEMU_LD_PREFIX=/usr/s390x-redhat-linux/sys-root/fc40/usr/ \
  qemu-s390x-static ./build/cstool -d aarch64 01421bd501423bd5
```

Adjust sysroot/QEMU binary to match the host distro used for the toolchain.

## Android arm64-v8a

```bash
export NDK_PATH=/path/to/android-ndk
cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=$NDK_PATH/build/cmake/android.toolchain.cmake \
  -DANDROID_NDK=$NDK_PATH \
  -DANDROID_ABI=arm64-v8a
cmake --build build
```

## Native Windows Release

```bash
cmake.exe -B build
cmake.exe --build build --config Release
```

## macOS thin (host arch only)

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCAPSTONE_BUILD_MACOS_THIN=ON
cmake --build build
```
