# Custom memory examples

## User-mode custom heap

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DCAPSTONE_USE_DEFAULT_ALLOC=OFF \
  -DCAPSTONE_BUILD_DIET=ON
cmake --build build
```

```c
#include <capstone/capstone.h>

static cs_opt_mem mem = {
	.malloc = my_malloc,
	.calloc = my_calloc,
	.realloc = my_realloc,
	.free = my_free,
	.vsnprintf = vsnprintf,
};

int init_cs(void)
{
	csh handle;
	if (cs_option(0, CS_OPT_MEM, (size_t)&mem) != CS_ERR_OK)
		return -1;
	return cs_open(CS_ARCH_X86, CS_MODE_64, &handle) == CS_ERR_OK ? 0 : -1;
}
```

## OS X kext-oriented configure

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DCAPSTONE_OSXKERNEL_SUPPORT=ON \
  -DCAPSTONE_BUILD_DIET=ON
cmake --build build
```

## Windows kernel sample

1. Build Capstone for kernel use with the winkernel memory sources as required
   by your driver project.
2. Open `contrib/cs_driver/cs_driver.sln` in Visual Studio (2013+ per README).
3. Follow include/lib path comments in `cs_driver.c`.
