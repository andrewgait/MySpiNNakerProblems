
#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"

#define __lif_dynamics()						\
  do {									\
      asm volatile ("ldr r8, [%[ip]], #4\n\t"				\
                    "ldr r7, [%[np]]\n\t"				\
                    "ldr r6, [%[np], #4]\n\t"				\
		    "add r7, r8, r7\n\t"				\
		    "smlawb r8, r6,  r9, r6\n\t"			\
		    "smlawb r7, r7, r10, r7\n\t"			\
		    "smlawt r8, r7,  r9, r8\n\t"			\
		    "cmp r6, #0\n\t"					\
		    "sublts r8, r8, #0x1000000\n\t"			\
		    "nop\n\t"						\
		    "str r7, [%[np]], #4\n\t"				\
		    "str r8, [%[np]], #4\n\t"				\
		    : [np] "+r" (np), [ip] "+r" (ip),			\
		      [v] "=r" (v), [p] "=r" (p), [in] "=r" (in)	\
		    : [k0] "r" (k0), [k1] "r" (k1), [k2] "r" (k2)	\
		    : "memory");					\
    } while (false)


#define __lif_load_constants()						\
  do {									\
      asm volatile ("ldr %[k0], [%[kp]]\n\t"				\
                    "ldr %[k1], [%[kp], #4]\n\t"			\
                    "ldr %[k2], [%[kp], #8]\n\t"			\
		    : [k0] "=r" (k0), [k1] "=r" (k1), [k2] "=r" (k2)	\
		    : [kp] "r" (kp) : "memory");			\
    } while (false)



neuron_ptr* neuron_dynamics (neuron_ptr* sp, uint32_t* ip,
			     neuron_ptr  np, uint32_t* kp)
{
    __label__ L_start, L1_1, L1_2, L1_3;
    register uint32_t   k0 asm ("r9");
    register uint32_t   k1 asm ("r10");
    register uint32_t   k2 asm ("r11");
    register uint32_t   p  asm ("r7");
    register uint32_t   v  asm ("r6");
    register uint32_t   in asm ("r8");

    // Load up constants from kp.
    __lif_load_constants();

    goto L_start;
    //    asm goto     ("b %l[L_start]\n\t" : : : "cc" : L_start);

L1_2: //Non-standard// Refractory handling

    asm volatile ("cmp r6, #0\n\t" : : [v] "r" (v) : "cc");
    asm goto     ("b %l[L1_3]\n\t" : : : "cc" : L1_3);
    asm volatile ("moveq r8, r11\n\t"
		  "subne r8, r6, #1\n\t"
		  : [in] "=r" (in)
		  : [k2] "r" (k2), [v] "r" (v) : "memory");
    asm goto     ("b %l[L1_1]\n\t" : : : "cc" : L1_1); // continue 

L1_3: // Spike send.
    
    asm volatile ("cmp r8, #0\n\t"
		  "movge r8, #20\n\t"
		  "strge  %[np], [%[sp]], #4\n\t"
		  : [in] "=r" (in), [sp] "+r" (sp)
		  : [np] "r" (np) : "memory");
    asm goto     ("b %l[L1_1]\n\t" : : : "cc" : L1_1); // continue

L_start:

    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    
  
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    
    
    //  4 loops gives  80 cycles time.(20.0)        TICK!!
    //  8 loops gives 134 cycles time (16.75)       TICK!!
    // 16 loops gives 212 cycles time (13.25)       238 (14.875)
    // 32 loops gives 394 cycles time (12.3125)     446 (13.9375)
    
    //asm goto     ("bge %l[L1_2]\n\t" : : : "cc" : L1_2);

L1_1: // continue main processing

    return (sp);
}
