/* Independently invoke the unchanged upstream C routines on fixed inputs. */
#include <stdio.h>
#include <inttypes.h>
#ifdef HARNESS_SHR3
#include "generators/shr3.c"
#else
#include "generators/xorrot32.c"
#endif

static void emit(uint32_t input)
{
#ifdef HARNESS_SHR3
    SHR3State state = {.x = input};
    (void) get_bits_raw(&state);
    printf("shr3,%08" PRIx32 ",%08" PRIx32 "\n", input, state.x);
#else
    Xorrot32State state = {.x = input};
    (void) get_bits_good_raw(&state);
    printf("xorrot32_default,%08" PRIx32 ",%08" PRIx32 "\n", input, state.x);
    state.x = input;
    (void) get_bits_bad1_raw(&state);
    printf("xorrot32_bad1,%08" PRIx32 ",%08" PRIx32 "\n", input, state.x);
    state.x = input;
    (void) get_bits_bad2_raw(&state);
    printf("xorrot32_bad2,%08" PRIx32 ",%08" PRIx32 "\n", input, state.x);
#endif
}

int main(void)
{
    static const uint32_t samples[] = {
        0, UINT32_C(0xffffffff), UINT32_C(0x12345678), UINT32_C(0xdeadbeef),
        UINT32_C(0xa5a5a5a5), UINT32_C(0x5a5a5a5a), UINT32_C(0x80000001),
        UINT32_C(0x01010101)
    };
    for (unsigned i = 0; i < 32; i++) emit(UINT32_C(1) << i);
    for (unsigned i = 0; i < sizeof(samples) / sizeof(samples[0]); i++) emit(samples[i]);
    return 0;
}
