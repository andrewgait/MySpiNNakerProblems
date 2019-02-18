
/*
 A generic lif neuron with current-based synapses 
*/
#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"
#include <debug.h>

//! The neuron data structure mirrors that provided by the current tool chain.
//!
//!

/*
#define __input_2_ring_buffer_elements()\

    ldr      %[i0], [%[np]]            @ Load 'input' variable i1
    ldr      %[i1], [%[np], #4]        @ Load 'input' variable i1
    ldrh     r0, [%[rp]]               @ Load ring buffer entry R0
    ldr      %[k], [%[np], #8]         @ Load input decay constants
    ldrh     r1, [%[rp], #2]           @ Load ring buffer entry R1
    smlawb   %[i0], %[i0], %[k], %[i0] @ decay input (small decay; for large use smulwb instead)
    smlawt   %[i1], %[i1], %[k], %[i1] @ decay input (small decay; for large use smulwt instead)
    add      %[i0], r0, %[i0]          @ add ring-buffer input to input
    add      %[i1], r1, %[i1]          @ add ring-buffer input to input
    str      %[minus1], [%[rp]], #4    @ reset ring-buffer elements
    ldr      %[i0], [%[np]], #4        @ Write-back 'input' variable i0
    ldr      %[i1], [%[np]], #8        @ Write-back 'input' variable i1

...

#define __accumulate_same_sign_inputs()\

    add      %[input], %[input], %[i0] @ Accumulate input 0
    add      %[input], %[input], %[i1] @ Accumulate input 1

#define __accumulate_different_sign_inputs()\

    add      %[input], %[input], %[i0] @ Accumulate input 0
    rsb      %[input], %[input], %[i1] @ Accumulate input 1

#define __accumulate_same_sign_inputs_and negate()\
    add      %[input], %[input], %[i0] @ Accumulate input 0
    add      %[input], %[input], %[i1] @ Accumulate input 1
    rsb      %[input], %[input], #0    @ Invert accumulator


//--------------------------------------------------
    ldr      r2, [%[np]]                    @ Load neuron's membrane voltage                      \n\t" \
    ldr      %[prop], [??]
    subs     %[v], r2, %[phi]               @ Subtract phi.b from voltage OR ..                   \n\t" \
                                            @  .. subtract refractory tick, set flags             \n\t" \
    smlawbmi r0, %[inputs], %[prop], %[v]   @ combined input with voltage using propogators       \n\t" \
    smlawtmi %[v], %[v], %[prop], r0        @ decay voltage and combine                           \n\t" \
----------->
    cmpmi    %[v], #0                       @ if initial voltage was negative (subs instruction): \n\t" \
                                            @ then compare voltage now to zero                    \n\t" \
    blpl     refractory_or_spiking_neuron   @ if initial or final voltage >= 0, then jump to      \n\t" \
                                            @    special case code to emit spike and reset or     \n\t" \
                                            @    decrement refractory counter                     \n\t" \
    str      %[v],   [%[np]], #4            @ write-back voltage                                  \n\t" \
		   


*/

#define __get_two_ring_buffer_inputs(ex,in)				\
  do {asm volatile (\
		    \
		    "ldr      %[psp], [%[np], #4]            @ Load neuron's PSP                                   \n\t" \
		    "ldrh     r0, [%[in]]                    @ Load inhibitory ring-buffer values to r0.           \n\t" \
		    "smlawb   %[psp], %[psp], %[k2], %[psp]  @ decay the psp.                                      \n\t" \
		    "ldr      r2, [%[np]]                    @ Load neuron's membrane voltage                      \n\t" \
		    "ldrh     r1, [%[in], #2]                @ Load excitatory ring-buffer values to r1.           \n\t" \
		    "subs     %[v], r2, %[phi]               @ Subtract phi.b from voltage OR ..                   \n\t" \
		    "                                        @  .. subtract refractory tick, set flags             \n\t" \
		    "smlawb   r0, r0, %[k1], %[psp]          @ scale the inhibitory current, and combined with psp \n\t" \
		    "smlawt   %[psp], r1, %[k1], r0          @ scale the excitatory, and combine with inhibitory   \n\t" \
		    "smlawbmi r0, %[psp], %[k0], %[v]        @ decay psp, and combined with voltage                \n\t" \
		    "smlawtmi %[v], %[v], %[k0], r0          @ decay voltage and combine                           \n\t" \
		    "str      %[psp], [%[np], #4]            @ write-back psp                                      \n\t" \
		    "cmpmi    %[v], #0                       @ if initial voltage was negative (subs instruction): \n\t" \
		    "                                        @ then compare voltage now to zero                    \n\t" \
		    "blpl     refractory_or_spiking_neuron   @ if initial or final voltage >= 0, then jump to      \n\t" \
		    "                                        @    special case code to emit spike and reset or     \n\t" \
		    "                                        @    decrement refractory counter                     \n\t" \
		    "str      %[v],   [%[np]], #8            @ write-back voltage                                  \n\t" \
		    "str      %[minus1], [%[in]], #4         @ write-back reset value (-1) of ring buffer          \n\t" \
		    : [v] "=r" (v), [psp] "=r" (psp), [np] "+r" (np), [in] "+r" (in)                                     \
		    : [k0] "r" (k0), [k1] "r" (k1), [k2] "r" (k2), [phi] "r" (phi), [minus1] "r" (minus1)	         \
		    : "cc", "memory");	                                                                                 \
    } while (false)
