/*
  A fast LIF synapse processing

  end: 1160
start: 036c
-----------
        ef4   = 3828 bytes.
*/

#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"
#include <debug.h>



//=============================================================================
// DMA Processing
//=============================================================================


//#define DMA_ADRS 0x4   /* SDRAM Address        */
//#define DMA_ADRT 0x8   /* TCM Address          */
//#define DMA_DESC 0xc   /* Transfer description */
//#define DMA_CTRL 0x10  /* Control Register     */
//#define DMA_STAT 0x14  /* Status Register      */


//----------------------------+-----------------------------------------------+
//                            |                 Components                    |
//        Descriptor Name     +------------+-----------+-----------+----------+
//                            |   Double   |   Burst   |   Write   |   Size   |
//----------------------------+------------+-----------+-----------+----------+

#define WORD_READ_DESCRIPTOR    ((0 << 24) | (0 << 21) | (0 << 19) | (1 << 2))  /* = 0x00000004 */
#define DWORD_READ_DESCRIPTOR   ((1 << 24) | (0 << 21) | (0 << 19) | (1 << 3))  /* = 0x01000008 */
#define LARGE_READ_DESCRIPTOR   ((1 << 24) | (4 << 21) | (0 << 19) | (0 << 2))  /* = 0x01800000 */
#define WORD_WRITE_DESCRIPTOR   ((0 << 24) | (0 << 21) | (1 << 19) | (1 << 2))  /* = 0x00080004 */
#define DWORD_WRITE_DESCRIPTOR  ((1 << 24) | (0 << 21) | (1 << 19) | (1 << 3))  /* = 0x01080008 */
#define LARGE_WRITE_DESCRIPTOR  ((1 << 24) | (4 << 21) | (1 << 19) | (0 << 2))  /* = 0x01880000 */

#define QSSX_DISPATCH 2
#define QUAD_DISPATCH 2
#define PRIMARY_DISPATCH 2
#define SECONDARY_DISPATCH 2

//=============================================================================
// We define the register allocation suitable for the rowlet processing.
//
//=============================================================================

#define USE_ROWLET_REGISTERS()						                      \
  do {asm volatile ("@ spoof register use\n\t" : : "r" (ctrl), "r" (wp), "r" (w), "r" (n),    \
		    "r" (time_base), "r" (jump), "r" (mask),"r" (mask_0x3c) : "cc");          \
  } while (false)

//! \brief The following macro allows us to define _in_one_place_ the register
//! names and locations used by the various pieces of rowlet manipulation code.
//!
//! It also hides a piece of non-code-generating code that "uses" all of these
//! registers, as most code fragments don't use _all_ the registers.
//!
//! It may be that omitting this "asm" statement becomes necessary later.

#define ROWLET_REGISTER_MAP                                                                   \
  register uint32_t* ctrl      asm ("r12"); /* control and constant access                 */ \
  register uint32_t* wp        asm ("r11"); /* Pointer to next synaptic word               */ \
  register uint32_t  w         asm ("r10"); /* Current synaptic word                       */ \
  register uint32_t  n         asm ("r9");  /* Number of synapses in this rowlet.          */ \
  register uint32_t  time_base asm ("r8");  /* Bottom 4 bits of global timer in bits 31-28 */ \
  register uint32_t* jump      asm ("r7");  /* The base of the dispatch jump table         */ \
  register uint32_t  mask      asm ("r6");  /* Mask 0x1fe                                  */ \
  register uint32_t  mask_0x3c asm ("r5");  /* Mask 0x3c, easily reconstructed with mov    */ \
                                                                                              \
  USE_ROWLET_REGISTERS()

//=============================================================================
// Large uninitialised data structures requiring careful alignment
//
// (or those smaller ones that can be squeezed in!)
//=============================================================================

// 0x0040 0000 DMA buffer 0                       Yes
// 0x0040 1800 Circular Buffer for FIQ
// 0x0040 1c00 Random Number Buffer
// 0x0040 2000 DMA buffer 1                       Yes
// 0x0040 3800 Current Buffer 0
// 0x0040 3c00 Current Buffer 1
// 0x0040 4000 Ring buffer 0                      Yes
// 0x0040 6000 Ring buffer 1                      Yes
// 0x0040 8000 Start of available DTCM


#define RING_ADDRESS_BITS 7
#define RING_TIME_BITS 2
#define SHIFT_LEFT  (32 - (RING_TIME_BITS+RING_ADDRESS_BITS))
#define SHIFT_RIGHT (SHIFT_LEFT - 1)
#define PLASTICITY_REQUIRED false

#define NEURONS          256
#define DELAYS           16
#define TIME_CONSTANTS   2
#define RING_BUFFER_SIZE (NEURONS*DELAYS)
#define DMA_BUFFER_SIZE  (1024+512)

//=============================================================================
// DMA Buffer Section
//=============================================================================

//! It __does__ make sense to align these buffers in the lower part of the DTCM! (OH NO IT DOESN'T!!!)
//! This then ensures that when we mask out the effects of the time/delay
//! calculation, we still obtain a correct address for the ring-buffer.
//!
//! This is of importance with fast accessing of the ring-buffer when the
//! offsets are auto-incremented in lock-step with the processing of the DMA
//! buffer. c.f. Dense rowlets.
//!
//! It seems __likely__ that 1536 entries is the most we are ever likely to
//! require for a 0.1ms simulation. This is a due to one or other of the
//! following observations:
//!
//!   (*) Transferring more than 4K bytes -- or 1,000 words -- will saturate
//!       the available SDRAM bandwith, if all cores are DMA-ing.
//!
//!   (*) If we are transferring 16-bit synapses, and each synapse takes six
//!       cycles to compute, then if the DMA buffer is full we have of the
//!       order of 3,000 synapses to process. This will take at least 18,000
//!       cycles of the available 20,000 in a 0.1ms "tick".
//!
//!       Note that if the buffer is full, this core must have grabbed more
//!       than its fair share of the SDRAM bandwidth.
//!
//!   (*) Thus, 1536 (= 1.5 * 1024) words seems likely to be enough space.
//!
//!       This leaves TWO 512 word spaces above each of the actual DMA buffers.

#define __dma_buffer0_address 0x00400000
#define __dma_buffer1_address 0x00402000

#define dma_buffer0 ((uint32_t*)__dma_buffer0_address)
#define dma_buffer1 ((uint32_t*)__dma_buffer1_address)

void zero_dma_buffers (void)
{
    uint32_t i = 0;

    for (i = 0; i < 1536; i++) {
        dma_buffer0[i] = 0xaaaaaaaa;
        dma_buffer1[i] = 0xbbbbbbbb;
    }
}

void print_dma_buffer0 (void)
{
    uint32_t i = 0;

    for (i = 0; i < 200; i++)
        io_printf (IO_BUF, "  *(%08x) = %08x\n", (uint32_t)(dma_buffer0 + i), dma_buffer0[i]);
}


void print_dma_buffer1 (void)
{
    uint32_t i = 0;

    for (i = 0; i < 40; i++)
        io_printf (IO_BUF, "  *(%08x) = %08x\n", (uint32_t)(dma_buffer1 + i), dma_buffer1[i]);
}



void print_dma_buffers (void)
{
    io_printf (IO_BUF, "DMA 0\n=====\n");
    print_dma_buffer0 ();
    io_printf (IO_BUF, "DMA 1\n=====\n");
    print_dma_buffer1 ();
}

//=============================================================================
// Ring Buffer Buffer Section
//=============================================================================

//! The ring buffers, are aligned on 8192-byte boundaries and -- considered as
//! uint16_t -- are pre-initialised with 0xffff. I've chosen to declare them
//! as int, so that counting the array entries is easier.
//!
//! VERY IMPORTANT (DRL)!!! The declaration of these buffers has to be on an
//! 8192-byte boundary alignment, otherwise we take an extra instruction for
//! each synaptic event.
//!
//! ALSO IMPORTANT (DRL)!!! CHECK THAT gcc _actually_ acts on the above.
//!                         It might not!!!
//!
//! IMPORTANT NOTE: gcc seems unhappy with anything bigger than 8192 bytes
//!
//! VERY VERY IMPORTANT (DRL)!!! The real problem is that the linker script and
//! or loaded has trouble placing these buffers using the "aligned" attribute.
//!
//! For this reason I've taken the liberty of modifying the linker script to
//! make DTCM "seem" smaller, and to thereby free-up the lowest 16K of memory
//! for ring-buffers.
//!
//! Another factor in the decision was that pre-loading the ring-buffers with
//! "0x0" is easy; pre-loading with 0xffffffff causes the size of the APLX to
//! expand massively (basically all 16k needs representation in the APLX file).

#define __ring_buffer0_address 0x00404000
#define __ring_buffer1_address 0x00406000

#define __ring_buffer0 ((int*)__ring_buffer0_address)
#define __ring_buffer1 ((int*)__ring_buffer1_address)

#define ring_buffer0 ((uint16_t*)__ring_buffer0_address)
#define ring_buffer1 ((uint16_t*)__ring_buffer1_address)

//=============================================================================
// Debug Printer Routine
//
// Doesn't affect r0-r12, or flags, except for r0, which is the input register
//=============================================================================

void printx (uint32_t x)  __attribute__ ((noinline, naked));
void printx (uint32_t x)
{
    register uint32_t tmp asm ("r2");
  
    asm volatile ("push {r0-r3,ip,lr}\n\t"
                  "mrs  r3, cpsr\n\t"
                  "push {r3}\n\t"
                  "mov  %[tmp], r0\n\t"
                  : [tmp] "=r" (tmp) : "r" (x) : "memory");

    io_printf (IO_BUF, " DEBUG: %08x\n", tmp);

    asm volatile ("pop {r3}\n\t"
                  "msr cpsr_fs, r3\n\t"
                  "pop {r0-r3,ip,pc}\n\t" : [tmp] "=r" (tmp) : : "memory");

}

//=============================================================================
// Timer Buffer Section
//=============================================================================

static uint32_t time; // Timer 1 time stashed by our accountancy routines

void     initialise_timer (void)  __attribute__ ((noinline));
void     start_timer      (void)  __attribute__ ((noinline));
void     stop_timer       (void)  __attribute__ ((noinline));

void initialise_timer (void)
{
    register uint32_t* timer_addr = (uint32_t*)(0x21000000);

    timer_addr[0] = (uint32_t)(-1);
    timer_addr[2] = 0xc2;
}

void start_timer (void)
{
    register uint32_t* timer_addr = (uint32_t*)(0x21000000);
    register uint32_t  t;

    asm volatile ("push {r2, r3}\n\t"
                  "ldr %[t], [%[timer_addr], #4]\n\t"
                  : [t] "=r" (t) : [timer_addr] "r" (timer_addr) : "memory");

    time = t;

    asm volatile ("pop {r2, r3}\n\t" : : : "memory");
}

void stop_timer (void)
{
    register uint32_t* timer_addr = (uint32_t*)(0x21000000);
    register uint32_t t;

    asm volatile ("push {r1, r2, r3}\n\t"
                  "ldr %[t], [%[timer_addr], #4]\n\t"
                  : [t] "=r" (t) : [timer_addr] "r" (timer_addr) : "memory");

    time -= t+20;

    asm volatile ("pop {r1, r2, r3}\n\t" : : : "memory");
}

//! \brief The following routine resets to ring-buffer entries corresponding to
//! a delay of "delay" to "zero" (actually represented by 0xffff). It does so
//! using 32-bit operations to reset a pair of ring-buffer elements in one
//! assignment.
//!
//! We also take the opportunity to indulge in a little bit of our favourite
//! recreational pastime: loop-unrolling.
//!
//! The hand crafted assembler executes -- with call and return -- in 331 cycles;
//! the C code executes in 773 cycles.
//!
//! Thoughts: is it worth coding this up in THUMB? (Probably.) Is it worth reducing the
//! code size, but increasing the register footprint, by using "stm r3, {r4,r5,r6,r7}"?
//! Probably, but it __will__ lose some execution efficiency.
//!
//! \param[in] delay The delay slot requiring zero-ing.

//#define C_CODE

#ifndef C_CODE
void reset_ring_buffer_row (uint32_t delay) asm ("reset_ring_buffer_row") __attribute__ ((noinline, naked));
void reset_ring_buffer_row (uint32_t delay)
{
    __label__ Loop;
    register uint16_t* rp1    asm ("r1");
    register uint16_t* rp2    asm ("r2");
    register int       minus1 asm ("r3");

    asm volatile ("mov  r1, #0x00400000           @ Load base address of DTCM           \n\t"
                  "add  r2, r1, #0x6000           @ Base address of ring_buffer1        \n\t"
                  "add  r1, r1, #0x4000           @ Base address of ring_buffer1        \n\t"
                  "add  r1, r1, %[delay], lsl #9  @ Offset for specific delay           \n\t"
                  "add  r2, r2, %[delay], lsl #9  @ Offset for specific delay           \n\t"
                  "mvn  %[minus1], #0             @ Value to be stored in ring buffers  \n\t"
                  "mov  %[delay], #15             @ Recycle r0 (=delay) as counter      \n\t"
                  : [minus1] "=r" (minus1), [rp1] "=r" (rp1), [rp2] "=r" (rp2), [delay] "+r" (delay)
                  : : "memory");

Loop:
    asm volatile ("str r3, [%[rp1]], #4                                             \n\t"
                  "str r3, [%[rp1]], #4                                             \n\t"
                  "str r3, [%[rp1]], #4                                             \n\t"
                  "str r3, [%[rp1]], #4                                             \n\t"
                  "str r3, [%[rp1]], #4                                             \n\t"
                  "str r3, [%[rp1]], #4                                             \n\t"
                  "str r3, [%[rp1]], #4                                             \n\t"
                  "str r3, [%[rp1]], #4                                             \n\t"
                  "str r3, [%[rp2]], #4                                             \n\t"
                  "str r3, [%[rp2]], #4                                             \n\t"
                  "str r3, [%[rp2]], #4                                             \n\t"
                  "str r3, [%[rp2]], #4                                             \n\t"
                  "str r3, [%[rp2]], #4                                             \n\t"
                  "str r3, [%[rp2]], #4                                             \n\t"
                  "str r3, [%[rp2]], #4                                             \n\t"
                  "str r3, [%[rp2]], #4                                             \n\t"
                  "subs r0, r0, #1                @ Decrement loop counter, and ... \n\t"
                  : [rp1] "+r" (rp1), [rp2] "+r" (rp2) : "r" (minus1) : "memory");

    asm goto     ("bpl %l[Loop]                   @   ... loop back if needed       \n\t"
                  "mov pc, lr                     @ Return                          \n\t"
                  : : : "cc", "memory" : Loop);
}
#else /*C_CODE*/
void reset_ring_buffer_row (uint32_t delay)
{
  int i;

  for (i = 0; i < 128; i++) {
      __ring_buffer0 [(delay << 7) + i] = 0xffffffff;
      __ring_buffer1 [(delay << 7) + i] = 0xffffffff;
  }
  /*// If gcc didn't generate such appallingly inefficient ARM code, I might
    // have left this "as is". But it doesn't, so I don't!

    // Recall that this routine is called at (or near) the start of each time-step.

    int i;

    for (i = RING_BUFFER_SIZE >> 4; i >= 0; i--) {
        __ring_buffer0 [(delay << 6) + (i << 3)     ] = -1;
        __ring_buffer0 [(delay << 6) + (i << 3) +  1] = -1;
        __ring_buffer0 [(delay << 6) + (i << 3) +  2] = -1;
        __ring_buffer0 [(delay << 6) + (i << 3) +  3] = -1; 
        __ring_buffer0 [(delay << 6) + (i << 3) +  4] = -1;
        __ring_buffer0 [(delay << 6) + (i << 3) +  5] = -1;
        __ring_buffer0 [(delay << 6) + (i << 3) +  6] = -1;
        __ring_buffer0 [(delay << 6) + (i << 3) +  7] = -1;

        __ring_buffer1 [(delay << 6) + (i << 3)     ] = -1;
        __ring_buffer1 [(delay << 6) + (i << 3) +  1] = -1;
        __ring_buffer1 [(delay << 6) + (i << 3) +  2] = -1;
        __ring_buffer1 [(delay << 6) + (i << 3) +  3] = -1; 
        __ring_buffer1 [(delay << 6) + (i << 3) +  4] = -1;
        __ring_buffer1 [(delay << 6) + (i << 3) +  5] = -1;
        __ring_buffer1 [(delay << 6) + (i << 3) +  6] = -1;
        __ring_buffer1 [(delay << 6) + (i << 3) +  7] = -1;
        }*/
}

/* For comparison here's the code gcc generates:

(Each store takes 2 cycles = 16 additional cycles;
 the push/pop sequence takes an additional 16 cycles;
 Also saved eight instructions setting registers each loop)

0000051c <reset_ring_buffer_row>:
     51c:       e59fc080        ldr     ip, [pc, #128]  ; 5a4 <SPARE_SIZE+0x4>
     520:       e59f1080        ldr     r1, [pc, #128]  ; 5a8 <SPARE_SIZE+0x8>
     524:       e92d47f0        push    {r4, r5, r6, r7, r8, r9, sl, lr}
     528:       e1a00400        lsl     r0, r0, #8
     52c:       e3a0ec01        mov     lr, #256        ; 0x100
     530:       e3e03000        mvn     r3, #0
     534:       e080218e        add     r2, r0, lr, lsl #3
     538:       e24ee001        sub     lr, lr, #1
     53c:       e282a001        add     sl, r2, #1
     540:       e2829002        add     r9, r2, #2
     544:       e2828003        add     r8, r2, #3
     548:       e2827004        add     r7, r2, #4
     54c:       e2826005        add     r6, r2, #5
     550:       e2825006        add     r5, r2, #6
     554:       e2824007        add     r4, r2, #7
     558:       e37e0001        cmn     lr, #1
     55c:       e78c3102        str     r3, [ip, r2, lsl #2]
     560:       e7813102        str     r3, [r1, r2, lsl #2]
     564:       e78c310a        str     r3, [ip, sl, lsl #2]
     568:       e781310a        str     r3, [r1, sl, lsl #2]
     56c:       e78c3109        str     r3, [ip, r9, lsl #2]
     570:       e7813109        str     r3, [r1, r9, lsl #2]
     574:       e78c3108        str     r3, [ip, r8, lsl #2]
     578:       e7813108        str     r3, [r1, r8, lsl #2]
     57c:       e78c3107        str     r3, [ip, r7, lsl #2]
     580:       e7813107        str     r3, [r1, r7, lsl #2]
     584:       e78c3106        str     r3, [ip, r6, lsl #2]
     588:       e7813106        str     r3, [r1, r6, lsl #2]
     58c:       e78c3105        str     r3, [ip, r5, lsl #2]
     590:       e7813105        str     r3, [r1, r5, lsl #2]
     594:       e78c3104        str     r3, [ip, r4, lsl #2]
     598:       e7813104        str     r3, [r1, r4, lsl #2]
     59c:       1affffe4        bne     534 <reset_ring_buffer_row+0x18>
     5a0:       e8bd87f0        pop     {r4, r5, r6, r7, r8, r9, sl, pc}
     5a4:       00406000        .word   0x00406000
     5a8:       0040c000        .word   0x0040c000
*/
#endif /*C_CODE*/

//! \brief This routine sets up the ring-buffers on start-up. Pre-assigning the
//! buffers to 0xffffffff takes up too much space in the .aplx!
//!
//! Using the efficient assembler row function, this takes 5375 cycles to
//! execute.

void initialise_ring_buffers (void)
{
    int i;

    for (i = DELAYS-1; i >= 0; i--)
        reset_ring_buffer_row ((uint32_t)i);
}

//! \brief For debugging purposes, we define a printing routine, that prints
//! out only non-"zero" elements of the indicated buffer.
//!
//! \param[in] buffer_number 0 for ring_buffer0; 1 for ring_buffer1

void print_ring_buffer (int buffer_number)
{
    int       i, j;
    uint16_t* buffer;

    buffer = (buffer_number == 0)? ring_buffer0: ring_buffer1;

    for (i = 0; i < 256; i++)
        for (j = 0; j < 16; j++)
            if (buffer[256*j + i] != 0xffff)
                io_printf (IO_BUF, "ring_buffer%1u [%d, %u] = %u\n",
                           buffer_number, j, i, 0xffff - (uint32_t)buffer[256*j + i]);
}

//! \brief For debugging purposes, we define a printing routine, that prints
//! out only non-"zero" elements of all buffers.
//!
//! \param[in] buffer_number 0 for ring_buffer0; 1 for ring_buffer1

void print_ring_buffers (void)
{
    print_ring_buffer (0);
    print_ring_buffer (1);
}

uint32_t get_index (uint32_t w)
{   return (w & 0xff); }

uint32_t get_delay (uint32_t w)
{   return ((w >> 8) & 0xf); }

uint32_t get_index_delay (uint32_t w)
{   return (w & 0xfff); }

uint32_t get_weight (uint32_t w)
{   return ((w >> 12) & 0xfff); }

uint32_t odd_word (uint32_t w)
{   return ((get_weight (w) << 20) | (get_index_delay (w))); }

static uint32_t* __op__;
static uint32_t* __ip__;
static uint32_t __rowlets  = 0;
static uint32_t __synapses = 0;

void compress_quad (void)
{
    uint32_t w, w0, w1, w2, w3;

    w0 = *__ip__++;
    w1 = *__ip__++;
    w2 = *__ip__++;
    w3 = *__ip__++;
	
    w = odd_word(w0) | (get_index (w2) << 12);
    *__op__++ = w;
    io_printf (IO_BUF, "    {%08x, ", w);

    w = odd_word(w1) | (get_index (w3) << 12);
    *__op__++ = w;
    io_printf (IO_BUF, "%08x, ", w);

    w = (get_weight (w3) << 20) | (get_delay (w3) <<16) | ( get_weight (w2) << 4) | (get_delay (w2));
    *__op__++ = w;
    io_printf (IO_BUF, "%08x}\n", w);

}

static inline uint32_t compress_excitatory (uint32_t w)
{   return (w >= 256); }

static inline uint32_t compress_odds (uint32_t w)
{   return (w & 3); }

static inline uint32_t compress_quads (uint32_t w)
{   return ((w & 0xfc) >> 2); }

static inline uint32_t compress_extension_word (void)
{   return ((*__ip__++)); }

static inline uint32_t compress_short_header (uint32_t odds, uint32_t quads, uint32_t exc, uint32_t ext)
{   return ((quads << 16) | (odds << 14) | ((exc? 1: 0) << 13) | ((ext? 1: 0) << 12)); }

static inline uint32_t compress_long_header (uint32_t odds, uint32_t quads, uint32_t exc, uint32_t ext)
{   return ((0x1 << 20) | ((exc? 1: 0) << 13) | ((ext? 1: 0) << 12) | (quads << 2) | (odds << 0)); }

static inline void emit_header_extension (uint32_t h, uint32_t x)
{
    if (x == 0) {
        *__op__++ = h; // Header Information
	io_printf (IO_BUF, "%08x:\n---------\n", h);
    }
    else {
        *__op__++ = h; // Header Information
        *__op__++ = x; // Descriptor Word
	io_printf (IO_BUF, "%08x: (extension descriptor: %08x)\n------------------------------------------\n", h, x);
    }
}

static /*inline*/ void process_odds (uint32_t odds)
{
    uint32_t w;
    uint32_t i;

    for (i = 0; i < odds; i++) {
        w = odd_word (*__ip__++);
	*__op__++ = w;
	io_printf (IO_BUF, "    %08x\n", w);
    }

}

static /*inline*/ void process_quads (uint32_t quads)
{
    uint32_t i;

    for (i = 0; i < quads; i++)
        compress_quad ();
}


void compress_rowlet (void)
{
    uint32_t odds;
    uint32_t quads;
    uint32_t exc;
    uint32_t ext;
    uint32_t x;
    uint32_t w;
    uint32_t h;

    w     = *__ip__++;
    exc   = compress_excitatory (w);
    odds  = compress_odds (w);
    quads = compress_quads (w);
    x     = compress_extension_word ();
    ext   = (x != 0);

    __rowlets++;
    __synapses += 4*quads + odds;
    
    if (quads >= 16) {
        h = compress_long_header (odds, quads, exc, ext);
        emit_header_extension (h, x);
	process_odds  (odds);
	process_quads (quads);
    }
    else {
        h = compress_short_header (odds, quads, exc, ext);
        if (odds == 0) {
	    emit_header_extension (h, x);
	    process_odds  (odds);
	    process_quads (quads);
	}
	else {
	    w = *__ip__++;
	    emit_header_extension (odd_word (w) | h, x);
	    process_odds  (odds-1);
	    process_quads (quads);
	}
    }
}

void translate_rowlets (void)
{
    uint32_t  w;
    uint32_t  ip = (uint32_t)__ip__;
    uint32_t  op = (uint32_t)__op__;
    uint32_t  n, f;

    w = *__ip__;

    while (w != 0) {
        compress_rowlet ();
	w = *__ip__;
    }

    *__op__++ = 0; // end marker

    ip = (((uint32_t)__ip__) - ip) >> 2;
    op = (((uint32_t)__op__) - op) >> 2;

    f = (1000*(ip-op)+50) / ip;
    n = f / 10;
    f = f - 10*n;
    
    io_printf (IO_BUF, "At the end of synapse compression we have:\n"
	       "     input = %4u words: output = %4u words, compression = %2u.%1u%%\n"
	       "-----------------------------------------------------------------\n",
	       ip, op, n, f);
}

// we expect spikes as follows
//
//             L2/3e    L2/3i   L4e      L4i     L5e    L5i      L6e        L6i  
//            20.683    5.834   21.915  5.479   4.850   1.065   14.395     2.948
//              4        1        4       1       1       1        3       not connected

uint32_t tmp[] =  // DRAM max = 4kB per 0.1 time-step
  {
    //dma_buffer1 set up with inputs to a chunk of L5e

    24, 0, // L2/3e
    0x00dc938d, 0x00dc0332, 0x00dc04ac, 0x00db7507,
    0x00dba68a, 0x00d886b4, 0x00db27f8, 0x00dbf74a,
    0x00dceb69, 0x00db7bdb, 0x00d67e3b, 0x00d6df84,
    0x00dd4f16, 0x00d8b059, 0x00de2105, 0x00df91fb,
    0x00dc72dc, 0x00d8c2d6, 0x00ddc382, 0x00dc93f2,
    0x00d783cc, 0x00d9b55b, 0x00de570b, 0x00daf721,

    30, 0, // L2/3e
    0x00dd212a, 0x00d683e6, 0x00d91313, 0x00db068e,
    0x00da57d4, 0x00e197c3, 0x00d5c7f1, 0x00d9c8ce,
    0x00d9eb00, 0x00db3b22, 0x00dc1b7f, 0x00de4cee,
    0x00da0d08, 0x00dc5ff7, 0x00dc70f5, 0x00dcf065,
    0x00dc11a4, 0x00d962a6, 0x00dc32dc, 0x00da33d5,
    0x00dc75c7, 0x00dc252f, 0x00dc7677, 0x00da9630,
    0x00dca75e, 0x00d859b7, 0x00db1a48, 0x00d86a10,
    0x00dc3a86, 0x00dc7037,

    21, 0, // L2/3e
    0x00de42b7, 0x00daf593, 0x00d79b8a, 0x00d83d15,
    0x00de2e95, 0x00daa05d, 0x00dc7054, 0x00de2190,
    0x00dae1ab, 0x00d9e2c0, 0x00d9d2ce, 0x00d95243,
    0x00db0399, 0x00dc73ca, 0x00dd34ac, 0x00dc4508,
    0x00dae789, 0x00e01716, 0x00dc2881, 0x00ddbc9c,
    0x00dfc6ee,
    
    25, 0, // L2/3e
    0x00ddd8aa, 0x00dbb9c5, 0x00d9c9e2, 0x00da2b21,
    0x00d98c53, 0x00dc3d0d, 0x00dcff31, 0x00e360d6,
    0x00d8807f, 0x00dbf070, 0x00da51a8, 0x00dbe10a,
    0x00df01ab, 0x00daa408, 0x00ddd536, 0x00dd151e,
    0x00dda62e, 0x00db664d, 0x00dd165a, 0x00dd9648,
    0x00da67fb, 0x00d9b816, 0x00da68da, 0x00d919a5,
    0x00dc1795,


    256+14, 0, //L2/3i
    0xfc97cc64, 0xfc86ca52, 0xfc8569d9, 0xfc9b2718,
    0xfc98f800, 0xfc8d8634, 0xfc9dd602, 0xfc9126c9,
    0xfc8d7524, 0xfc8b85bb, 0xfc8e3451, 0xfc8b24f2,
    0xfc88a490, 0xfc8d7399,


    13, 0, //L4e
    0x00dd233f, 0x00e069ca, 0x00d9cc7e, 0x00dc60a2,
    0x00d910bd, 0x00d990b2, 0x00d9b12e, 0x00dd7275,
    0x00dae288, 0x00da44f9, 0x00db179b, 0x00d90b13,
    0x00dbaf15,


    9, 0, //L4e
    0x00da42b7, 0x00db638d, 0x00dd059b, 0x00d579c5,
    0x00dd8b07, 0x00dd4c5f, 0x00da3618, 0x00da660d,
    0x00d93b74,

    19, 0, //L4e
    0x00dc260a, 0x00dce924, 0x00dc9a90, 0x00d55de8,
    0x00de6d29, 0x00db5d53, 0x00d93e5a, 0x00db5ebc,
    0x00db1e1d, 0x00dfafb9, 0x00de2fd4, 0x00de20a2,
    0x00d8a073, 0x00d921c7, 0x00db3140, 0x00dd141e,
    0x00d8c606, 0x00dc06e9, 0x00de1c1a,


    13, 0, //L4e
    0x00db5233, 0x00dd6223, 0x00d9536f, 0x00dc0692,
    0x00d9d966, 0x00d9ca8e, 0x00dd3ccf, 0x00dedeb0,
    0x00da833e, 0x00d7a462, 0x00da45e3, 0x00de1627,
    0x00da53f3,


    
    256+1, 0, 0x1fc00450, // An L4i rowlet


    23, 0, // L5e
    0x00d937c2, 0x00dc98ae, 0x00df4abb, 0x00dbebe2,
    0x00df1c50, 0x00dd6c0a, 0x00e07d76, 0x00dd7e38,
    0x00dd1f18, 0x00d8f093, 0x00d9b073, 0x00d950be,
    0x00d9d1f2, 0x00d6c3bf, 0x00ddc4d0, 0x00dc44ac,
    0x00dea54f, 0x00dd0627, 0x00de961d, 0x00e1f8fa,
    0x00dcba4a, 0x00dbeb6e, 0x00de43b1,
    
    9, 0, // L6e
    0x00daa5a3, 0x00d8791b, 0x00d8caca, 0x00dc1f8f,
    0x00e0509a, 0x00dac264, 0x00dd2236, 0x00db84b6,
    0x00d66afc,
    6, 0, // L6e
    0x00d8a95a, 0x00d92a36, 0x00d7d582, 0x00d8c60a,
    0x00da9610, 0x00dd4378,
    7, 0, // L6e
    0x00dbb2b6, 0x00d92b85, 0x00d9bb9b, 0x00dd5f23,
    0x00df50f6, 0x00db45f5, 0x00d8a972,

    24, 0, // L2/3e
    0x00dc938d, 0x00dc0332, 0x00dc04ac, 0x00db7507,
    0x00dba68a, 0x00d886b4, 0x00db27f8, 0x00dbf74a,
    0x00dceb69, 0x00db7bdb, 0x00d67e3b, 0x00d6df84,
    0x00dd4f16, 0x00d8b059, 0x00de2105, 0x00df91fb,
    0x00dc72dc, 0x00d8c2d6, 0x00ddc382, 0x00dc93f2,
    0x00d783cc, 0x00d9b55b, 0x00de570b, 0x00daf721,

    30, 0, // L2/3e
    0x00dd212a, 0x00d683e6, 0x00d91313, 0x00db068e,
    0x00da57d4, 0x00e197c3, 0x00d5c7f1, 0x00d9c8ce,
    0x00d9eb00, 0x00db3b22, 0x00dc1b7f, 0x00de4cee,
    0x00da0d08, 0x00dc5ff7, 0x00dc70f5, 0x00dcf065,
    0x00dc11a4, 0x00d962a6, 0x00dc32dc, 0x00da33d5,
    0x00dc75c7, 0x00dc252f, 0x00dc7677, 0x00da9630,
    0x00dca75e, 0x00d859b7, 0x00db1a48, 0x00d86a10,
    0x00dc3a86, 0x00dc7037,

    21, 0, // L2/3e
    0x00de42b7, 0x00daf593, 0x00d79b8a, 0x00d83d15,
    0x00de2e95, 0x00daa05d, 0x00dc7054, 0x00de2190,
    0x00dae1ab, 0x00d9e2c0, 0x00d9d2ce, 0x00d95243,
    0x00db0399, 0x00dc73ca, 0x00dd34ac, 0x00dc4508,
    0x00dae789, 0x00e01716, 0x00dc2881, 0x00ddbc9c,
    0x00dfc6ee,
    
    25, 0, // L2/3e
    0x00ddd8aa, 0x00dbb9c5, 0x00d9c9e2, 0x00da2b21,
    0x00d98c53, 0x00dc3d0d, 0x00dcff31, 0x00e360d6,
    0x00d8807f, 0x00dbf070, 0x00da51a8, 0x00dbe10a,
    0x00df01ab, 0x00daa408, 0x00ddd536, 0x00dd151e,
    0x00dda62e, 0x00db664d, 0x00dd165a, 0x00dd9648,
    0x00da67fb, 0x00d9b816, 0x00da68da, 0x00d919a5,
    0x00dc1795,

    256+14, 0, //L2/3i
    0xfc97cc64, 0xfc86ca52, 0xfc8569d9, 0xfc9b2718,
    0xfc98f800, 0xfc8d8634, 0xfc9dd602, 0xfc9126c9,
    0xfc8d7524, 0xfc8b85bb, 0xfc8e3451, 0xfc8b24f2,
    0xfc88a490, 0xfc8d7399,

    13, 0, //L4e
    0x00dd233f, 0x00e069ca, 0x00d9cc7e, 0x00dc60a2,
    0x00d910bd, 0x00d990b2, 0x00d9b12e, 0x00dd7275,
    0x00dae288, 0x00da44f9, 0x00db179b, 0x00d90b13,
    0x00dbaf15,
    9, 0, //L4e
    0x00da42b7, 0x00db638d, 0x00dd059b, 0x00d579c5,
    0x00dd8b07, 0x00dd4c5f, 0x00da3618, 0x00da660d,
    0x00d93b74,
    19, 0, //L4e
    0x00dc260a, 0x00dce924, 0x00dc9a90, 0x00d55de8,
    0x00de6d29, 0x00db5d53, 0x00d93e5a, 0x00db5ebc,
    0x00db1e1d, 0x00dfafb9, 0x00de2fd4, 0x00de20a2,
    0x00d8a073, 0x00d921c7, 0x00db3140, 0x00dd141e,
    0x00d8c606, 0x00dc06e9, 0x00de1c1a,
    13, 0, //L4e
    0x00db5233, 0x00dd6223, 0x00d9536f, 0x00dc0692,
    0x00d9d966, 0x00d9ca8e, 0x00dd3ccf, 0x00dedeb0,
    0x00da833e, 0x00d7a462, 0x00da45e3, 0x00de1627,
    0x00da53f3,
    
    256+1, 0, 0x1fc00450, // An L4i rowlet

    23, 0, // L5e
    0x00d937c2, 0x00dc98ae, 0x00df4abb, 0x00dbebe2,
    0x00df1c50, 0x00dd6c0a, 0x00e07d76, 0x00dd7e38,
    0x00dd1f18, 0x00d8f093, 0x00d9b073, 0x00d950be,
    0x00d9d1f2, 0x00d6c3bf, 0x00ddc4d0, 0x00dc44ac,
    0x00dea54f, 0x00dd0627, 0x00de961d, 0x00e1f8fa,
    0x00dcba4a, 0x00dbeb6e, 0x00de43b1,
    
    9, 0, // L6e
    0x00daa5a3, 0x00d8791b, 0x00d8caca, 0x00dc1f8f,
    0x00e0509a, 0x00dac264, 0x00dd2236, 0x00db84b6,
    0x00d66afc,
    6, 0, // L6e
    0x00d8a95a, 0x00d92a36, 0x00d7d582, 0x00d8c60a,
    0x00da9610, 0x00dd4378,
    7, 0, // L6e
    0x00dbb2b6, 0x00d92b85, 0x00d9bb9b, 0x00dd5f23,
    0x00df50f6, 0x00db45f5, 0x00d8a972,

    24, 0, // L2/3e
    0x00dc938d, 0x00dc0332, 0x00dc04ac, 0x00db7507,
    0x00dba68a, 0x00d886b4, 0x00db27f8, 0x00dbf74a,
    0x00dceb69, 0x00db7bdb, 0x00d67e3b, 0x00d6df84,
    0x00dd4f16, 0x00d8b059, 0x00de2105, 0x00df91fb,
    0x00dc72dc, 0x00d8c2d6, 0x00ddc382, 0x00dc93f2,
    0x00d783cc, 0x00d9b55b, 0x00de570b, 0x00daf721,

    30, 0, // L2/3e
    0x00dd212a, 0x00d683e6, 0x00d91313, 0x00db068e,
    0x00da57d4, 0x00e197c3, 0x00d5c7f1, 0x00d9c8ce,
    0x00d9eb00, 0x00db3b22, 0x00dc1b7f, 0x00de4cee,
    0x00da0d08, 0x00dc5ff7, 0x00dc70f5, 0x00dcf065,
    0x00dc11a4, 0x00d962a6, 0x00dc32dc, 0x00da33d5,
    0x00dc75c7, 0x00dc252f, 0x00dc7677, 0x00da9630,
    0x00dca75e, 0x00d859b7, 0x00db1a48, 0x00d86a10,
    0x00dc3a86, 0x00dc7037,

    21, 0, // L2/3e
    0x00de42b7, 0x00daf593, 0x00d79b8a, 0x00d83d15,
    0x00de2e95, 0x00daa05d, 0x00dc7054, 0x00de2190,
    0x00dae1ab, 0x00d9e2c0, 0x00d9d2ce, 0x00d95243,
    0x00db0399, 0x00dc73ca, 0x00dd34ac, 0x00dc4508,
    0x00dae789, 0x00e01716, 0x00dc2881, 0x00ddbc9c,
    0x00dfc6ee,
    
    25, 0, // L2/3e
    0x00ddd8aa, 0x00dbb9c5, 0x00d9c9e2, 0x00da2b21,
    0x00d98c53, 0x00dc3d0d, 0x00dcff31, 0x00e360d6,
    0x00d8807f, 0x00dbf070, 0x00da51a8, 0x00dbe10a,
    0x00df01ab, 0x00daa408, 0x00ddd536, 0x00dd151e,
    0x00dda62e, 0x00db664d, 0x00dd165a, 0x00dd9648,
    0x00da67fb, 0x00d9b816, 0x00da68da, 0x00d919a5,
    0x00dc1795,

    256+14, 0, //L2/3i
    0xfc97cc64, 0xfc86ca52, 0xfc8569d9, 0xfc9b2718,
    0xfc98f800, 0xfc8d8634, 0xfc9dd602, 0xfc9126c9,
    0xfc8d7524, 0xfc8b85bb, 0xfc8e3451, 0xfc8b24f2,
    0xfc88a490, 0xfc8d7399,

    13, 0, //L4e
    0x00dd233f, 0x00e069ca, 0x00d9cc7e, 0x00dc60a2,
    0x00d910bd, 0x00d990b2, 0x00d9b12e, 0x00dd7275,
    0x00dae288, 0x00da44f9, 0x00db179b, 0x00d90b13,
    0x00dbaf15,
    9, 0, //L4e
    0x00da42b7, 0x00db638d, 0x00dd059b, 0x00d579c5,
    0x00dd8b07, 0x00dd4c5f, 0x00da3618, 0x00da660d,
    0x00d93b74,
    19, 0, //L4e
    0x00dc260a, 0x00dce924, 0x00dc9a90, 0x00d55de8,
    0x00de6d29, 0x00db5d53, 0x00d93e5a, 0x00db5ebc,
    0x00db1e1d, 0x00dfafb9, 0x00de2fd4, 0x00de20a2,
    0x00d8a073, 0x00d921c7, 0x00db3140, 0x00dd141e,
    0x00d8c606, 0x00dc06e9, 0x00de1c1a,
    13, 0, //L4e
    0x00db5233, 0x00dd6223, 0x00d9536f, 0x00dc0692,
    0x00d9d966, 0x00d9ca8e, 0x00dd3ccf, 0x00dedeb0,
    0x00da833e, 0x00d7a462, 0x00da45e3, 0x00de1627,
    0x00da53f3,
    
    256+1, 0, 0x1fc00450, // An L4i rowlet

    23, 0, // L5e
    0x00d937c2, 0x00dc98ae, 0x00df4abb, 0x00dbebe2,
    0x00df1c50, 0x00dd6c0a, 0x00e07d76, 0x00dd7e38,
    0x00dd1f18, 0x00d8f093, 0x00d9b073, 0x00d950be,
    0x00d9d1f2, 0x00d6c3bf, 0x00ddc4d0, 0x00dc44ac,
    0x00dea54f, 0x00dd0627, 0x00de961d, 0x00e1f8fa,
    0x00dcba4a, 0x00dbeb6e, 0x00de43b1,
    
    9, 0, // L6e
    0x00daa5a3, 0x00d8791b, 0x00d8caca, 0x00dc1f8f,
    0x00e0509a, 0x00dac264, 0x00dd2236, 0x00db84b6,
    0x00d66afc,
    6, 0, // L6e
    0x00d8a95a, 0x00d92a36, 0x00d7d582, 0x00d8c60a,
    0x00da9610, 0x00dd4378,
    7, 0, // L6e
    0x00dbb2b6, 0x00d92b85, 0x00d9bb9b, 0x00dd5f23,
    0x00df50f6, 0x00db45f5, 0x00d8a972,

    24, 0, // L2/3e
    0x00dc938d, 0x00dc0332, 0x00dc04ac, 0x00db7507,
    0x00dba68a, 0x00d886b4, 0x00db27f8, 0x00dbf74a,
    0x00dceb69, 0x00db7bdb, 0x00d67e3b, 0x00d6df84,
    0x00dd4f16, 0x00d8b059, 0x00de2105, 0x00df91fb,
    0x00dc72dc, 0x00d8c2d6, 0x00ddc382, 0x00dc93f2,
    0x00d783cc, 0x00d9b55b, 0x00de570b, 0x00daf721,

    30, 0, // L2/3e
    0x00dd212a, 0x00d683e6, 0x00d91313, 0x00db068e,
    0x00da57d4, 0x00e197c3, 0x00d5c7f1, 0x00d9c8ce,
    0x00d9eb00, 0x00db3b22, 0x00dc1b7f, 0x00de4cee,
    0x00da0d08, 0x00dc5ff7, 0x00dc70f5, 0x00dcf065,
    0x00dc11a4, 0x00d962a6, 0x00dc32dc, 0x00da33d5,
    0x00dc75c7, 0x00dc252f, 0x00dc7677, 0x00da9630,
    0x00dca75e, 0x00d859b7, 0x00db1a48, 0x00d86a10,
    0x00dc3a86, 0x00dc7037,

    21, 0, // L2/3e
    0x00de42b7, 0x00daf593, 0x00d79b8a, 0x00d83d15,
    0x00de2e95, 0x00daa05d, 0x00dc7054, 0x00de2190,
    0x00dae1ab, 0x00d9e2c0, 0x00d9d2ce, 0x00d95243,
    0x00db0399, 0x00dc73ca, 0x00dd34ac, 0x00dc4508,
    0x00dae789, 0x00e01716, 0x00dc2881, 0x00ddbc9c,
    0x00dfc6ee,
    
    25, 0, // L2/3e
    0x00ddd8aa, 0x00dbb9c5, 0x00d9c9e2, 0x00da2b21,
    0x00d98c53, 0x00dc3d0d, 0x00dcff31, 0x00e360d6,
    0x00d8807f, 0x00dbf070, 0x00da51a8, 0x00dbe10a,
    0x00df01ab, 0x00daa408, 0x00ddd536, 0x00dd151e,
    0x00dda62e, 0x00db664d, 0x00dd165a, 0x00dd9648,
    0x00da67fb, 0x00d9b816, 0x00da68da, 0x00d919a5,
    0x00dc1795,

    256+14, 0, //L2/3i
    0xfc97cc64, 0xfc86ca52, 0xfc8569d9, 0xfc9b2718,
    0xfc98f800, 0xfc8d8634, 0xfc9dd602, 0xfc9126c9,
    0xfc8d7524, 0xfc8b85bb, 0xfc8e3451, 0xfc8b24f2,
    0xfc88a490, 0xfc8d7399,

    13, 0, //L4e
    0x00dd233f, 0x00e069ca, 0x00d9cc7e, 0x00dc60a2,
    0x00d910bd, 0x00d990b2, 0x00d9b12e, 0x00dd7275,
    0x00dae288, 0x00da44f9, 0x00db179b, 0x00d90b13,
    0x00dbaf15,
    9, 0, //L4e
    0x00da42b7, 0x00db638d, 0x00dd059b, 0x00d579c5,
    0x00dd8b07, 0x00dd4c5f, 0x00da3618, 0x00da660d,
    0x00d93b74,
    19, 0, //L4e
    0x00dc260a, 0x00dce924, 0x00dc9a90, 0x00d55de8,
    0x00de6d29, 0x00db5d53, 0x00d93e5a, 0x00db5ebc,
    0x00db1e1d, 0x00dfafb9, 0x00de2fd4, 0x00de20a2,
    0x00d8a073, 0x00d921c7, 0x00db3140, 0x00dd141e,
    0x00d8c606, 0x00dc06e9, 0x00de1c1a,
    13, 0, //L4e
    0x00db5233, 0x00dd6223, 0x00d9536f, 0x00dc0692,
    0x00d9d966, 0x00d9ca8e, 0x00dd3ccf, 0x00dedeb0,
    0x00da833e, 0x00d7a462, 0x00da45e3, 0x00de1627,
    0x00da53f3,
    
    256+1, 0, 0x1fc00450, // An L4i rowlet

    23, 0, // L5e
    0x00d937c2, 0x00dc98ae, 0x00df4abb, 0x00dbebe2,
    0x00df1c50, 0x00dd6c0a, 0x00e07d76, 0x00dd7e38,
    0x00dd1f18, 0x00d8f093, 0x00d9b073, 0x00d950be,
    0x00d9d1f2, 0x00d6c3bf, 0x00ddc4d0, 0x00dc44ac,
    0x00dea54f, 0x00dd0627, 0x00de961d, 0x00e1f8fa,
    0x00dcba4a, 0x00dbeb6e, 0x00de43b1,
    
    9, 0, // L6e
    0x00daa5a3, 0x00d8791b, 0x00d8caca, 0x00dc1f8f,
    0x00e0509a, 0x00dac264, 0x00dd2236, 0x00db84b6,
    0x00d66afc,
    6, 0, // L6e
    0x00d8a95a, 0x00d92a36, 0x00d7d582, 0x00d8c60a,
    0x00da9610, 0x00dd4378,
    7, 0, // L6e
    0x00dbb2b6, 0x00d92b85, 0x00d9bb9b, 0x00dd5f23,
    0x00df50f6, 0x00db45f5, 0x00d8a972,

    24, 0, // L2/3e
    0x00dc938d, 0x00dc0332, 0x00dc04ac, 0x00db7507,
    0x00dba68a, 0x00d886b4, 0x00db27f8, 0x00dbf74a,
    0x00dceb69, 0x00db7bdb, 0x00d67e3b, 0x00d6df84,
    0x00dd4f16, 0x00d8b059, 0x00de2105, 0x00df91fb,
    0x00dc72dc, 0x00d8c2d6, 0x00ddc382, 0x00dc93f2,
    0x00d783cc, 0x00d9b55b, 0x00de570b, 0x00daf721,

    30, 0, // L2/3e
    0x00dd212a, 0x00d683e6, 0x00d91313, 0x00db068e,
    0x00da57d4, 0x00e197c3, 0x00d5c7f1, 0x00d9c8ce,
    0x00d9eb00, 0x00db3b22, 0x00dc1b7f, 0x00de4cee,
    0x00da0d08, 0x00dc5ff7, 0x00dc70f5, 0x00dcf065,
    0x00dc11a4, 0x00d962a6, 0x00dc32dc, 0x00da33d5,
    0x00dc75c7, 0x00dc252f, 0x00dc7677, 0x00da9630,
    0x00dca75e, 0x00d859b7, 0x00db1a48, 0x00d86a10,
    0x00dc3a86, 0x00dc7037,

    21, 0, // L2/3e
    0x00de42b7, 0x00daf593, 0x00d79b8a, 0x00d83d15,
    0x00de2e95, 0x00daa05d, 0x00dc7054, 0x00de2190,
    0x00dae1ab, 0x00d9e2c0, 0x00d9d2ce, 0x00d95243,
    0x00db0399, 0x00dc73ca, 0x00dd34ac, 0x00dc4508,
    0x00dae789, 0x00e01716, 0x00dc2881, 0x00ddbc9c,
    0x00dfc6ee,
    
    25, 0, // L2/3e
    0x00ddd8aa, 0x00dbb9c5, 0x00d9c9e2, 0x00da2b21,
    0x00d98c53, 0x00dc3d0d, 0x00dcff31, 0x00e360d6,
    0x00d8807f, 0x00dbf070, 0x00da51a8, 0x00dbe10a,
    0x00df01ab, 0x00daa408, 0x00ddd536, 0x00dd151e,
    0x00dda62e, 0x00db664d, 0x00dd165a, 0x00dd9648,
    0x00da67fb, 0x00d9b816, 0x00da68da, 0x00d919a5,
    0x00dc1795,

    256+14, 0, //L2/3i
    0xfc97cc64, 0xfc86ca52, 0xfc8569d9, 0xfc9b2718,
    0xfc98f800, 0xfc8d8634, 0xfc9dd602, 0xfc9126c9,
    0xfc8d7524, 0xfc8b85bb, 0xfc8e3451, 0xfc8b24f2,
    0xfc88a490, 0xfc8d7399,

    13, 0, //L4e
    0x00dd233f, 0x00e069ca, 0x00d9cc7e, 0x00dc60a2,
    0x00d910bd, 0x00d990b2, 0x00d9b12e, 0x00dd7275,
    0x00dae288, 0x00da44f9, 0x00db179b, 0x00d90b13,
    0x00dbaf15,
    9, 0, //L4e
    0x00da42b7, 0x00db638d, 0x00dd059b, 0x00d579c5,
    0x00dd8b07, 0x00dd4c5f, 0x00da3618, 0x00da660d,
    0x00d93b74,
    19, 0, //L4e
    0x00dc260a, 0x00dce924, 0x00dc9a90, 0x00d55de8,
    0x00de6d29, 0x00db5d53, 0x00d93e5a, 0x00db5ebc,
    0x00db1e1d, 0x00dfafb9, 0x00de2fd4, 0x00de20a2,
    0x00d8a073, 0x00d921c7, 0x00db3140, 0x00dd141e,
    0x00d8c606, 0x00dc06e9, 0x00de1c1a,
    13, 0, //L4e
    0x00db5233, 0x00dd6223, 0x00d9536f, 0x00dc0692,
    0x00d9d966, 0x00d9ca8e, 0x00dd3ccf, 0x00dedeb0,
    0x00da833e, 0x00d7a462, 0x00da45e3, 0x00de1627,
    0x00da53f3,
    
    256+1, 0, 0x1fc00450, // An L4i rowlet

    23, 0, // L5e
    0x00d937c2, 0x00dc98ae, 0x00df4abb, 0x00dbebe2,
    0x00df1c50, 0x00dd6c0a, 0x00e07d76, 0x00dd7e38,
    0x00dd1f18, 0x00d8f093, 0x00d9b073, 0x00d950be,
    0x00d9d1f2, 0x00d6c3bf, 0x00ddc4d0, 0x00dc44ac,
    0x00dea54f, 0x00dd0627, 0x00de961d, 0x00e1f8fa,
    0x00dcba4a, 0x00dbeb6e, 0x00de43b1,
    
    9, 0, // L6e
    0x00daa5a3, 0x00d8791b, 0x00d8caca, 0x00dc1f8f,
    0x00e0509a, 0x00dac264, 0x00dd2236, 0x00db84b6,
    0x00d66afc,
    6, 0, // L6e
    0x00d8a95a, 0x00d92a36, 0x00d7d582, 0x00d8c60a,
    0x00da9610, 0x00dd4378,
    7, 0, // L6e
    0x00dbb2b6, 0x00d92b85, 0x00d9bb9b, 0x00dd5f23,
    0x00df50f6, 0x00db45f5, 0x00d8a972,

    /*
    256+60, 0, // L5i
    0xfca0ce1d, 0xfc94be05, 0xfc950ec4, 0xfc90cec1,
    0xfc8c2e36, 0xfc981efd, 0xfc8a0ef6, 0xfc8bbdcf,
    0xfc9dad15, 0xfc8eddee, 0xfc8e4de4, 0xfc807d09,
    0xfc950df9, 0xfca18cfc, 0xfc9aacac, 0xfc852cc2,
    0xfc939caf, 0xfc8b0b54, 0xfc9eab29, 0xfc953b3c,
    0xfca6bbb2, 0xfc992b8f, 0xfc9f4c00, 0xfca27b4f,
    0xfc99ea08, 0xfc8ffa4c, 0xfca39a42, 0xfc913a62,
    0xfc8bda7d, 0xfc99ca78, 0xfc98e9f7, 0xfc85a994,
    0xfc8eb90f, 0xfc891957, 0xfc9fa96d, 0xfc9c495f,
    0xfc94d902, 0xfc94f916, 0xfc87d8ad, 0xfc94d8da,
    0xfc9cc834, 0xfc925880, 0xfc813823, 0xfc9728f3,
    0xfc8988aa, 0xfc8dc8e6, 0xfc8f68d7, 0xfc926897,
    0xfc8db860, 0xfca19724, 0xfc91173e, 0xfc922781,
    0xfc91d747, 0xfc8b07a2, 0xfc97e799, 0xfc936770,
    0xfc93770c, 0xfc90a767, 0xfc966784, 0xfc9f1711,

    256+41, 0, // L5i
    0xfc917619, 0xfc8b4632, 0xfc8a561c, 0xfc8f3693,
    0xfc904696, 0xfc8c76df, 0xfc938601, 0xfca4c6f1,
    0xfc95a540, 0xfc9225b0, 0xfc8f0589, 0xfc942585,
    0xfc8d7553, 0xfc8f059e, 0xfc8a55dd, 0xfc8a146f,
    0xfc9334cc, 0xfc8bb483, 0xfc9514de, 0xfc9224ae,
    0xfc9f13d8, 0xfc954375, 0xfc98a3cd, 0xfc8e3322,
    0xfc952331, 0xfc8d335b, 0xfc9173ef, 0xfca0b341,
    0xfc94327b, 0xfca4d2db, 0xfc828292, 0xfc935235,
    0xfc86d249, 0xfc8d7137, 0xfc8f9120, 0xfc9a514b,
    0xfc98907a, 0xfc845003, 0xfc9c4ee5, 0xfc945dbf,
    0xfc76bb52,
    */

    
    256+101, 0, // L5i
    0xfca0ce1d, 0xfc94be05, 0xfc950ec4, 0xfc90cec1,
    0xfc8c2e36, 0xfc981efd, 0xfc8a0ef6, 0xfc8bbdcf,
    0xfc9dad15, 0xfc8eddee, 0xfc8e4de4, 0xfc807d09,
    0xfc950df9, 0xfca18cfc, 0xfc9aacac, 0xfc852cc2,
    0xfc939caf, 0xfc8b0b54, 0xfc9eab29, 0xfc953b3c,
    0xfca6bbb2, 0xfc992b8f, 0xfc9f4c00, 0xfca27b4f,
    0xfc99ea08, 0xfc8ffa4c, 0xfca39a42, 0xfc913a62,
    0xfc8bda7d, 0xfc99ca78, 0xfc98e9f7, 0xfc85a994,
    0xfc8eb90f, 0xfc891957, 0xfc9fa96d, 0xfc9c495f,
    0xfc94d902, 0xfc94f916, 0xfc87d8ad, 0xfc94d8da,
    0xfc9cc834, 0xfc925880, 0xfc813823, 0xfc9728f3,
    0xfc8988aa, 0xfc8dc8e6, 0xfc8f68d7, 0xfc926897,
    0xfc8db860, 0xfca19724, 0xfc91173e, 0xfc922781,
    0xfc91d747, 0xfc8b07a2, 0xfc97e799, 0xfc936770,
    0xfc93770c, 0xfc90a767, 0xfc966784, 0xfc9f1711,
    0xfc917619, 0xfc8b4632, 0xfc8a561c, 0xfc8f3693,
    0xfc904696, 0xfc8c76df, 0xfc938601, 0xfca4c6f1,
    0xfc95a540, 0xfc9225b0, 0xfc8f0589, 0xfc942585,
    0xfc8d7553, 0xfc8f059e, 0xfc8a55dd, 0xfc8a146f,
    0xfc9334cc, 0xfc8bb483, 0xfc9514de, 0xfc9224ae,
    0xfc9f13d8, 0xfc954375, 0xfc98a3cd, 0xfc8e3322,
    0xfc952331, 0xfc8d335b, 0xfc9173ef, 0xfca0b341,
    0xfc94327b, 0xfca4d2db, 0xfc828292, 0xfc935235,
    0xfc86d249, 0xfc8d7137, 0xfc8f9120, 0xfc9a514b,
    0xfc98907a, 0xfc845003, 0xfc9c4ee5, 0xfc945dbf,
    0xfc76bb52,
    
    0,0,0,0,0,0 //end marker

    /*
   29, 0, // An L2/3e rowlet
   0x0dc80321,   0x0da8046d,   0x0da80491,   0x0df806de,
   0x0da00750,   0x0dd40837,   0x0db40958,   0x0dc409c7,
   0x0da80a9a,   0x0df00a9b,   0x0dd00c74,   0x0d680d10,
   0x0db40eff,   0x0db81192,   0x0df011f9,   0x0db0117f,
   0x0d9c11a6,   0x0dc41223,   0x0d9c12bc,   0x0d941462,
   0x0dc41697,   0x0e0417fc,   0x0d7018c1,   0x0de0182a,
   0x0d9418c4,   0x0ddc193a,   0x0dd019c2,   0x0df81947,
   0x0dac1959,
   34, 0, // An L2/3e rowlet
   0x0dc40275,   0x0da40262,   0x0df808fd,   0x0d8408e3,
   0x0db0082b,   0x0db808d1,   0x0da80af2,   0x0de40a59,
   0x0d800ae6,   0x0d980ac6,   0x0dd40b43,   0x0d5c0c5b,
   0x0dd40c6f,   0x0db40cb1,   0x0dac0cd0,   0x0db40c09,
   0x0d980f08,   0x0da00ff9,   0x0df410fa,   0x0d941023,
   0x0d981140,   0x0dc81197,   0x0dc01139,   0x0de41295,
   0x0dbc12fc,   0x0dc81200,   0x0d9014ed,   0x0d941488,
   0x0da015de,   0x0e00170e,   0x0da01990,   0x0db01cb6,
   0x0db41cd8,   0x0dcc1e7c
    
   3, 0, 0x2620026c, 0x24900e64, 0x25c01096, // An L4i rowlet
    
   1, 0, 0x22800d77, // An L4i rowlet
   4, 0, // An L4i rowlet
   0x27f00434, 0x2160053d, 0x282007ea, 0x25300e3f
   // And one L4i rowlet which is empty!!*/
   
  };

void translate_tmp (void)
{
  __ip__ = tmp;
  __op__ = dma_buffer0;
  
  translate_rowlets();
}

//=============================================================================
// (ASYNC) Circular Buffer Section
//=============================================================================

//! \brief A pretty typical Buffer structure.
//!
//! BUT, IMPORTANT, NOTE ...
//!
//!   ... the index representation. The index is incremented by 2^24 each time,
//!       which means it wraps after 256 increments.
//!
//!       Obviously we use the "free shifts" when adding the base register to
//!       get at the values in the buffer.
//!
//! VERY, VERY IMPORTANT: For this to work, the buffer size must be a power of two.

#define CIRCULAR_BUFFER_INDEX_BITS  8
#define CIRCULAR_BUFFER_SIZE        (1 << CIRCULAR_BUFFER_INDEX_BITS)
#define CIRCULAR_BUFFER_INCREMENT   (1 << (32 - CIRCULAR_BUFFER_INDEX_BITS))
#define CIRCULAR_BUFFER_INDEX_SHIFT (30 - CIRCULAR_BUFFER_INDEX_BITS)

//! \brief Calculates the address in the circular buffer, where the item may
//! be accessed.
//!
//! \param[in] base  The base address of the "actual" circular buffer
//! \param[in] index The "index" of the item being referenced.

#define circular_buffer_address(base,index)                             \
  (uint32_t*)((base) + ((index) >> CIRCULAR_BUFFER_INDEX_SHIFT))

#define circular_buffer ((uint32_t*)0x00401800)

typedef struct {
    uint32_t  output;
    uint32_t  base;
    uint32_t  input;
    uint32_t  overflows;
} circular_buffer_t, *circular_buffer_ptr;

circular_buffer_t circular_buffer_state asm ("circular_buffer_state");

//! \brief Returns a pointer to the next item to the current item.
//!
//! \param[in] current The index under consideration.
//! \return The next index

static inline uint32_t circular_buffer_next (uint32_t current)
{   return (current + CIRCULAR_BUFFER_INCREMENT); }

//! \brief Determines whether a circular buffer can input a new item.
//!
//! \param[in] buffer The circular buffer state
//! \return The truth value (in an integer): true for nonempty; i.e. has at least one element;
//!                                          false means "might be empty".

static inline int circular_buffer_nonempty (circular_buffer_ptr buffer)
{   return (buffer->input != buffer->output); }

//! \brief Determines whether a circular buffer can output an item.
//!
//! \param[in] buffer The circular buffer state
//! \return The truth value (in an integer): true for nonfull; i.e. has at least one spare space.
//!                                          false means "might be full".

static inline int circular_buffer_nonfull (circular_buffer_ptr buffer)
{   return (circular_buffer_next (buffer->input) != buffer->output); }

//! \brief Initialises the circular buffer structure.

void circular_buffer_initialize (void)
{
    circular_buffer_state.output    = 0;
    circular_buffer_state.base      = 0x00401800;
    circular_buffer_state.input     = 0;
    circular_buffer_state.overflows = 0;
}

//! \brief Assuming that the buffer is nonfull -- i.e. that there's space for
//! at least one more element -- this routine writes a new element into the
//! buffer structure. Otherwise it updates its overflow counter.
//!
//! Recall that this routine is called only from within the FIQ to place items
//! into the inspike buffer.
//!
//! The assembler code is eight instructions and executes in eight cycles.
//!
//! VERY VERY IMPORTANT: A naked C functions will __not__ static inline!!!
//!                      So we use a #define-ed version.
//!
//!                      On the assumption that we are working in FIQ-mode,
//!                      we have r8-r12, at our disposal, which will not
//!                      interfere with user-mode registers (plus registers
//!                      lr and sp, if you are reckless beyond peradventure!)

//!                      Will need scratch registers (r8, r9)
//!                      defining, along with where the result and buffer registers are
//!
//!                      I don't __think__ you can overlap [result] and [buffer], but
//!                      look at gcc's "late result" register specifier.

#ifndef C_CODE

//! \brief A piece of helper code to handle the (hopefully) rare case of buffer
//! overflows. We will be __branching__ to this code, from precisely one place:
//! the FIQ handler code. Thus we can return to user-mode at the end of this
//! code fragment, using the special "return-from-FIQ" code.
//!
//! ... And the buffer pointer is already in place in r12.

void __circular_buffer_overflow (void) asm ("__circular_buffer_overflow") __attribute__ ((noinline, naked));
void __circular_buffer_overflow (void)
{
    register uint32_t r8     asm ("r8");
    register uint32_t buffer asm ("r12");

    asm volatile ("ldr  %[r8], [%[buffer], #12] @ Load overflow value  ..           \n\t"
                  "add  %[r8], %[r8], #1        @   .. increment it, and ..         \n\t"
                  "ldr  %[r8], [%[buffer], #12] @ Write-back                        \n\t"
                  "mov  pc, lr                  @ Standard return                   \n\t"
                  "@subs pc, lr, #4              @ return from FIQ.                  \n\t"
                  : [r8] "=r" (r8) : [buffer] "r" (buffer) : "memory");
}

#define circular_buffer_input()                                                          \
    do {                                                                                 \
        asm volatile ("ldr  r8, [%[buffer], #8]   @ Load input index               \n\t" \
                      "ldr  r9, [%[buffer]]       @ Load output address            \n\t" \
                      "add  r8, r8, #0x1000000    @ Increment input index          \n\t" \
                      "cmp  r9, r8                @ Test for nonfull-ness, and ..  \n\t" \
                      "ldr  r9, [%[buffer], #4]   @ .. pre-load base, and hope not \n\t" \
                      "beq  __circular_buffer_overflow   @ .. to branch            \n\t" \
                      "str  r8, [%[buffer], #8]   @ Write back input index         \n\t" \
                      "str  %[input], [r9, r8, lsr #22]                            \n\t" \
                      "                           @ Store input value              \n\t" \
                      : [input] "=r" (input), "=r" (r8), "=r" (r9)                       \
                      : [buffer] "r" (buffer) : "memory");                               \
    } while (false)
#else /*C_CODE*/
void circular_buffer_input (circular_buffer_ptr buffer, uint32_t item)
{
    uint32_t last    = buffer -> output;
    uint32_t current = buffer -> input;
    uint32_t next    = circular_buffer_next (current);
  
    if (next != last) {
        *circular_buffer_address(buffer->base, next) = item;
        buffer->input  = next;
    } else 
        buffer->overflows++;
    
    // generated code:
    // 0000069c <circular_buffer_input>:
    //     69c:       e5903008        ldr     r3, [r0, #8]
    //     6a0:       e5902000        ldr     r2, [r0]
    //     6a4:       e2833401        add     r3, r3, #16777216       ; 0x1000000
    //     6a8:       e1520003        cmp     r2, r3
    //     6ac:       0590300c        ldreq   r3, [r0, #12]
    //     6b0:       15902004        ldrne   r2, [r0, #4]
    //     6b4:       02833001        addeq   r3, r3, #1
    //     6b8:       17821b23        strne   r1, [r2, r3, lsr #22]
    //     6bc:       0580300c        streq   r3, [r0, #12]
    //     6c0:       15803008        strne   r3, [r0, #8]
    //     6c4:       e12fff1e        bx      lr
}
#endif /*C_CODE*/

//! \brief Assuming that the buffer is nonempty -- i.e. that there's at least
//! one element -- this routine returns the next element, and updates the
//! buffer structure.
//!
//! The assembler code is six instructions and executes in 12 cycles with the
//! call and return. Given six of those cycles __are__ the call and return,
//! consider static inline-ing instead.
//!
//! VERY VERY IMPORTANT: A naked C functions will __not__ static inline!!!
//!                      So use a #define-ed version. Will need scratch registers
//!                      defining, along with where the result and buffer registers are
//!
//!                      I don't __think__ you can overlap [result] and [buffer], but
//!                      look at gcc's "late result" register specifier.

uint32_t circular_buffer_output (circular_buffer_ptr buffer)
{
    uint32_t item = *circular_buffer_address(buffer->base, buffer->output);
  
    // assert (circular_buffer_not_empty (buffer));

    buffer->output = circular_buffer_next (buffer->output);

    return (item);
    
    // Generates:
    // 000006c8 <circular_buffer_output>:
    // 6c8:       e5902000        ldr     r2, [r0]
    // 6cc:       e1a03000        mov     r3, r0
    // 6d0:       e5900004        ldr     r0, [r0, #4]
    // 6d4:       e2821401        add     r1, r2, #16777216       ; 0x1000000
    // 6d8:       e7900b22        ldr     r0, [r0, r2, lsr #22]
    // 6dc:       e5831000        str     r1, [r3]
    // 6e0:       e12fff1e        bx      lr
}
//#endif /*C_CODE*/

//! \brief The following code transfers the items in the buffer to a simple
//! array structure, that does not need to interact with the FIQ process.
//!
//! This has a two-fold benefit: (1) access to the spikes is made much more
//! efficient, and (2) the extraction process is much more efficient, also.
//!
//! The assembler code is ??? instructions and executes in ??? cycles with the
//! call and return.
//!
//! \param[in] buffer A pointer to the Circular Buffer structure
//! \param[in] output The buffer area to which we are transferring spikes.
//! \return The number of extracted spikes.


// HACK!!! UNTESTED!!!
/*
uint32_t circular_buffer_outputs (circular_buffer_ptr buffer, uint32_t* ptr)
{
    register uint32_t   input;
    register uint32_t*  base;
    register uint32_t   output;
    register uint32_t   n;
    register uint32_t*  bp;

    input  = buffer->input;
    base   = (uint32_t*)(buffer->base);
    output = buffer->output;

    if (input == output)
        return (0);

    n  = (input - output) >> CIRCULAR_BUFFER_INDEX_SHIFT;

    bp = circular_buffer_address (base, output);
    if (input < output) { // transfer _all_ spikes from output to 255
        while (bp < circular_buffer_address (base, CIRCULAR_BUFFER_SIZE))
            *ptr++ = *bp++;
    }

    bp = (uint32_t*)base;
    while (bp < circular_buffer_address (base, input))
        *ptr++ = *bp++;

    buffer->output = output + (n << CIRCULAR_BUFFER_INDEX_SHIFT);

    return (n);
}
*/
//=============================================================================
// Rowlet Formats
//=============================================================================

// A single word format makes the initial rowlet in the "master pop table" easier and smaller.
//
// Elsewhere we might need a full format, otherwise we could run out of memory addressing, delays, or sizes.
// Or do we?
//
// In a single word we get: 4-bits delay (what does 0 represent?)
// 7-bits of "size" (representing sizes 1-128 words) and thus 21-bits of address.
// (which addresses 2 million words = 8MBytes, which is enough for core.)
//
// What we do need is a pre-transformed set of DMA commands.

// Inspike            --dma--> New Rowlet     (compressed form __with__    delay)
// New Rowlet         --exp--> Rowlet Buffers (compressed form; delay to be ignored)
// Next Rowlet Buffer --exp--> DMA commands   (r0, r1, r2 ready for DMA extraction; r3 preset)

//! Forward declaration of the synapse loop is required for the definition of
//! the synapse jump table.

void packed_quad_loop             (void)  asm ("packed_quad_loop")            __attribute__ ((noinline, naked));
void primary_dispatch             (void)  asm ("primary_dispatch")            __attribute__ ((noinline, naked));
void secondary_dispatch_big_fixed (void)  asm ("secondary_dispatch_big_quad") __attribute__ ((noinline, naked));

void __reserved_dispatch (void)  asm ("__reserved_dispatch") __attribute__ ((noinline, naked));
void __reserved_dispatch (void)
{
    printx (0xbad0add0);

    asm volatile ("pop {pc}\n\t" : : : "cc");
}

void primary_dispatch_0I  (void)  asm ("primary_dispatch_0I")  __attribute__ ((noinline, naked));
void primary_dispatch_1I  (void)  asm ("primary_dispatch_1I")  __attribute__ ((noinline, naked));
void primary_dispatch_2I  (void)  asm ("primary_dispatch_2I")  __attribute__ ((noinline, naked));
void primary_dispatch_3I  (void)  asm ("primary_dispatch_3I")  __attribute__ ((noinline, naked));
void primary_dispatch_0E  (void)  asm ("primary_dispatch_0E")  __attribute__ ((noinline, naked));
void primary_dispatch_1E  (void)  asm ("primary_dispatch_1E")  __attribute__ ((noinline, naked));
void primary_dispatch_2E  (void)  asm ("primary_dispatch_2E")  __attribute__ ((noinline, naked));
void primary_dispatch_3E  (void)  asm ("primary_dispatch_3E")  __attribute__ ((noinline, naked));

//! \brief This is a dual jump table for rowlet header processing. Indexed in
//! the usual way -- with a positive register offset -- it gives the address
//! to which we've been dispatched, accoring to the bits ZSSX of the header.
//! Indexed with a _negative_ register offset we get the address to which a
//! secondary dispatch jumps.
//!
//! Speeding up secondary dispatch could involve selecting this secondary jump
//! as part of the primary dispatch code, but that's not how it works at the
//! moment.

//!jumping into the synapse processing loop. It is quadrupled up,
//! so that if there are two extraneous bits set in bits 5 and 6 of the index, then they are ignored.
//! (see code in rowlet dispatch).

#define SYNAPSE_CODE_SIZE          (27*4)
#define ROWLET_EXTENSION_CODE_SIZE (6*4)

static const uint32_t __jump_table[]
         = { (uint32_t)__reserved_dispatch,  // ?? Reserved
	     (uint32_t)__reserved_dispatch,  // -15 Reserved
	     (uint32_t)__reserved_dispatch,  // -14 Reserved
	     (uint32_t)__reserved_dispatch,  // -13 Reserved
	     (uint32_t)__reserved_dispatch,  // -12 Reserved
	     (uint32_t)__reserved_dispatch,  // -11 Reserved
	     (uint32_t)__reserved_dispatch,  // -10 Reserved
	     (uint32_t)__reserved_dispatch,  // -9 Reserved
	     (uint32_t)__reserved_dispatch,  // -8 Reserved
	     (uint32_t)__reserved_dispatch,  // -7 Reserved
	     (uint32_t)__reserved_dispatch,  // -6 Reserved
	     (uint32_t)__reserved_dispatch,  // -5 Reserved
	     (uint32_t)__reserved_dispatch,  // -4 Reserved
	     (uint32_t)__reserved_dispatch,  // -3 Reserved
	     (uint32_t)__reserved_dispatch,  // -2 Reserved
	     (uint32_t)secondary_dispatch_big_fixed,  // -1 A "large" block of fixed synapses.
//----------------------------------------------------------------------------------------------------------
             (uint32_t)primary_dispatch_0I + ROWLET_EXTENSION_CODE_SIZE,  // Skips over extension code
	     (uint32_t)primary_dispatch_0I,                               // Needs secondary dispatch   QQQQQ=0,  and SS=00
	     (uint32_t)primary_dispatch_0E + ROWLET_EXTENSION_CODE_SIZE,  // Skips over extension code
	     (uint32_t)primary_dispatch_0E,                               // Packed Quads only          QQQQQ!=0, and SS=00
	     (uint32_t)primary_dispatch_1I + ROWLET_EXTENSION_CODE_SIZE,  // Skips over extension code
	     (uint32_t)primary_dispatch_1I,                               // Single synpase             QQQQQ=0,  and SS=01
	     (uint32_t)primary_dispatch_1E + ROWLET_EXTENSION_CODE_SIZE,  // Skips over extension code
	     (uint32_t)primary_dispatch_1E,                               // Single synpase + quads     QQQQQ!=0, and SS=01
	     (uint32_t)primary_dispatch_2I + ROWLET_EXTENSION_CODE_SIZE,  // Skips over extension code
	     (uint32_t)primary_dispatch_2I,                               // Twin synpases              QQQQQ=0,  and SS=10
	     (uint32_t)primary_dispatch_2E + ROWLET_EXTENSION_CODE_SIZE,  // Skips over extension code
	     (uint32_t)primary_dispatch_2E,                               // Twin synpases + quads      QQQQQ!=0, and SS=10
	     (uint32_t)primary_dispatch_3I + ROWLET_EXTENSION_CODE_SIZE,  // Skips over extension code
	     (uint32_t)primary_dispatch_3I,                               // Triple synpases            QQQQQ=0,  and SS=11
	     (uint32_t)primary_dispatch_3E + ROWLET_EXTENSION_CODE_SIZE,  // Skips over extension code
	     (uint32_t)primary_dispatch_3E};                              // Triple synpases + quads    QQQQQ!=0, and SS=11

#define dispatch_table         ((uint32_t*)__jump_table + 16)
#define secondary_jump_table   ((uint32_t*)__jump_table)

void print_primary (void)
{
    uint32_t* table = dispatch_table;
    uint32_t i, j, k;
    
    io_printf (IO_BUF, "Primary Dispatch Table\n======================\n\n");

    for (i = 0; i < 2; i++) {
        for (j = 0; j < 4; j++) {
	    for (k = 0; k < 2; k++) {
	        io_printf (IO_BUF, "[%08x] Q %c 0; S %u; %c\n",
			   table [8*i+2*j+k],
			   (i==0)? '=': '>',
			   j,
			   (k==0)? ' ': 'X');

	    }
	}
    }

    io_printf (IO_BUF, "\n");
}

void print_secondary (void)
{
    uint32_t* table = secondary_jump_table;

    io_printf (IO_BUF, "Secondary Dispatch Table\n========================\n\n");
    io_printf (IO_BUF, "[%08x] Big Fixed\n", table[15]);
}

void print_jump_tables (void)
{
    print_primary ();
    print_secondary ();
}


static const uint32_t rowlet_subheader_table[8]
         = { (uint32_t)__reserved_dispatch,  // Never used (code drops through!)
	     (uint32_t)__reserved_dispatch,  // Reserved
	     (uint32_t)__reserved_dispatch,  // Reserved
	     (uint32_t)__reserved_dispatch,  // Reserved
	     (uint32_t)__reserved_dispatch,  // Reserved
	     (uint32_t)__reserved_dispatch,  // Reserved
	     (uint32_t)__reserved_dispatch,  // Reserved
	     (uint32_t)__reserved_dispatch}; // Reserved

/* Following code shows how to get 16 bit jump tables into ITCM if needed!

// Like all jump tables for SpiNNaker, this table could be 16-bits:
// all ITCM addresses are less than 0x7ffc. But the linker insists
// relocatable items must be placed in 32-bit storage. Following sketch
// shows how to reassign static const. (V dangerous!!)

static const uint16_t rowlet_dispatch_table [4]
    = { 0xaaaa, 0xbbbb, 0xcccc, 0xdddd}; // Values provided to ensure ITCM location

static const uint16_t rowlet_dispatch2_table [4]
    = { 0xaabb, 0xbbcc, 0xccdd, 0xddee}; // Values provided to ensure ITCM location

void __rowlet_dispatch_table (uint16_t* hp)
{
  int i = 4;
  for ( ; i > 0; i--)
    *hp++ = (uint16_t)(dispatch_table[i] & 0xffff);
}

void initialise_rowlet_dispatch_table (void)
{
    uint16_t* hp = (uint16_t*)rowlet_dispatch_table;

    __rowlet_dispatch_table (hp);
}
*/


//! \brief The following array, gives rapid access to addresses (which might
//! change on a timer-tick), constants that can't be represented by an
//! immediate constant, and anything else that could be of use!
//!
//! NOTE The point here is that:
//!           (1) access to relocatable values from within gcc's asm
//!               inline-assembler is tricky;
//!           (2) our code is then relocatable; and
//!           (3) constants only appear once!

static uint32_t __control_synapse[]
         = { (uint32_t)packed_quad_loop +     SYNAPSE_CODE_SIZE,  // QQQQQ = 11111 Does 3 packed-quad synapses
	     (uint32_t)packed_quad_loop + 2 * SYNAPSE_CODE_SIZE,  // QQQQQ = 11110 Does 2 packed-quad synapses
   	     (uint32_t)packed_quad_loop + 3 * SYNAPSE_CODE_SIZE,  // QQQQQ = 11101 Does 1 packed-quad synapses
	     (uint32_t)packed_quad_loop,                          // QQQQQ = 11100 Does 4 packed-quad synapses
	     (uint32_t)packed_quad_loop +     SYNAPSE_CODE_SIZE,  // QQQQQ = 11011 Does 3 packed-quad synapses
	     (uint32_t)packed_quad_loop + 2 * SYNAPSE_CODE_SIZE,  // QQQQQ = 11010 Does 2 packed-quad synapses
   	     (uint32_t)packed_quad_loop + 3 * SYNAPSE_CODE_SIZE,  // QQQQQ = 11001 Does 1 packed-quad synapses
	     (uint32_t)packed_quad_loop,                          // QQQQQ = 11000 Does 4 packed-quad synapses
	     (uint32_t)packed_quad_loop +     SYNAPSE_CODE_SIZE,  // QQQQQ = 10111 Does 3 packed-quad synapses
	     (uint32_t)packed_quad_loop + 2 * SYNAPSE_CODE_SIZE,  // QQQQQ = 10110 Does 2 packed-quad synapses
   	     (uint32_t)packed_quad_loop + 3 * SYNAPSE_CODE_SIZE,  // QQQQQ = 10101 Does 1 packed-quad synapses
	     (uint32_t)packed_quad_loop,                          // QQQQQ = 10100 Does 4 packed-quad synapses
	     (uint32_t)packed_quad_loop +     SYNAPSE_CODE_SIZE,  // QQQQQ = 10011 Does 3 packed-quad synapses
	     (uint32_t)packed_quad_loop + 2 * SYNAPSE_CODE_SIZE,  // QQQQQ = 10010 Does 2 packed-quad synapses
   	     (uint32_t)packed_quad_loop + 3 * SYNAPSE_CODE_SIZE,  // QQQQQ = 10001 Does 1 packed-quad synapses
             (uint32_t)packed_quad_loop,                          // QQQQQ = 10000 Does 4 packed-quad synapses
	     (uint32_t)packed_quad_loop +     SYNAPSE_CODE_SIZE,  // QQQQQ = 01111 Does 3 packed-quad synapses
	     (uint32_t)packed_quad_loop + 2 * SYNAPSE_CODE_SIZE,  // QQQQQ = 01110 Does 2 packed-quad synapses
   	     (uint32_t)packed_quad_loop + 3 * SYNAPSE_CODE_SIZE,  // QQQQQ = 01101 Does 1 packed-quad synapses
	     (uint32_t)packed_quad_loop,                          // QQQQQ = 01100 Does 4 packed-quad synapses
	     (uint32_t)packed_quad_loop +     SYNAPSE_CODE_SIZE,  // QQQQQ = 01011 Does 3 packed-quad synapses
	     (uint32_t)packed_quad_loop + 2 * SYNAPSE_CODE_SIZE,  // QQQQQ = 01010 Does 2 packed-quad synapses
   	     (uint32_t)packed_quad_loop + 3 * SYNAPSE_CODE_SIZE,  // QQQQQ = 01001 Does 1 packed-quad synapses
	     (uint32_t)packed_quad_loop,                          // QQQQQ = 01000 Does 4 packed-quad synapses
	     (uint32_t)packed_quad_loop +     SYNAPSE_CODE_SIZE,  // QQQQQ = 00111 Does 3 packed-quad synapses
	     (uint32_t)packed_quad_loop + 2 * SYNAPSE_CODE_SIZE,  // QQQQQ = 00110 Does 2 packed-quad synapses
   	     (uint32_t)packed_quad_loop + 3 * SYNAPSE_CODE_SIZE,  // QQQQQ = 00101 Does 1 packed-quad synapses
	     (uint32_t)packed_quad_loop,                          // QQQQQ = 00100 Does 4 packed-quad synapses
	     (uint32_t)packed_quad_loop +     SYNAPSE_CODE_SIZE,  // QQQQQ = 00011 Does 3 packed-quad synapses
	     (uint32_t)packed_quad_loop + 2 * SYNAPSE_CODE_SIZE,  // QQQQQ = 00010 Does 2 packed-quad synapses
   	     (uint32_t)packed_quad_loop + 3 * SYNAPSE_CODE_SIZE,  // QQQQQ = 00001 Does 1 packed-quad synapses
//----------------------------------------------------------------------------------------------------------
	     0,0,0,0,0,0,0,0,               // Base of Rowlet Processing Buffers
	     0,0,0,0,0,0,0,0,
	     0,0,                             //  64 global timer (64 bit)
	     0,                             //  72 circular buffer output "index
	     0x00401800,                    //  76 circular buffer array
	     0,                             //  80 circular buffer input  "index"
	     0,                             //  84 circular buffer overflows
	     WORD_WRITE_DESCRIPTOR,         //  88 A descriptor word for a "small" single word write
	     LARGE_READ_DESCRIPTOR,         //  92 A descriptor word for a "large" read  using double word
	     (uint32_t)dma_buffer0,         //  96 DMA Read buffer for Rowlets
	     (uint32_t)dma_buffer1,         // 100 DMA Write Buffer for the next tick's Rowlets
	     0x18181818, 0x10121416, 0x0,   // 104 log_size_to_burst table.
	     0x0,                           // 116 Unused
	     (uint32_t)dispatch_table,      // 120 Rowlet Dispatch Tables
	     ((uint32_t)ring_buffer0 >> 13),// 124 Time-base: rotated base address of ring-buffer with 4 bits of timer
	     0,                             // 128 DMA Processing Address
	     0x60800000,                    // 132 SDRAM base address for this processor (p) is 0x60000000 + p * 0x800000
	     0                              // 136 Saturation Counter
};

#define __control              ((uint32_t*)(__control_synapse + 31))
#define delayed_rowlet_buffer  (__control)


#define GLOBAL_TIMER                  64
#define DMA_BUFFER_READ               96
#define DMA_BUFFER_WRITE             100
#define LOG_SIZE_BURST_OFFSET        (104-21)

#define DISPATCH_TABLE               120
#define TIME_BASE                    124
#define DMA_PROCESSING               128
#define PROCESSOR_SDRAM_BASE         132
#define SATURATION_COUNTER           136

void print_synapse_jump_table (void)
{
    int i;

    io_printf (IO_BUF, "\nquad jump table\n===============\n");

    for (i = 0; i < 8; i++) {
        io_printf (IO_BUF, "[%08x] n = %d\n", __control_synapse[31 - i], i);
    }
    io_printf (IO_BUF, "\n\n");
}

//! \brief This "routine" saves all the 'C' registers requiring saving under
//! the ARM Procedure Call standard, i.e. registers 4-12, and the link
//! register (lr).
//!
//! This instruction will take 10 cycles to execute.

#define save_C_registers()						                                 \
  do { asm volatile ("push  {r4-r12,lr}  @ Save all 'C' registers    \n\t" ::: "memory"); } while (false)

//! \brief This "routine" restores all the 'C' registers that were previously
//! saved using the ARM Procedure Call standard -- i.e. registers 4-12, and
//! restores the program counter (pc) from the saved link register value.
//!
//! This instruction will take 15 (10 to recover the registers from memory,
//! and five to set the pc) cycles to execute.

#define restore_C_registers_and_return()                                                                 \
  do { asm volatile ("pop   {r4-r12,pc}  @ Restore all 'C' registers \n\t" ::: "memory"); } while (false)

#define set_rowlet_registers_from_control()					                                         \
  do {									                                                 \
      asm volatile ("ldr   %[time_base], [%[ctrl], %[BASE]]         @ Get time base                               \n\t"	 \
		    "ldr   %[jump],      [%[ctrl], %[JUMP]]         @ Set up dispatch tables' base address        \n\t"	 \
		    "mov   %[mask_0x3c], #0x3c                      @ Initialse mask with 0x3c                    \n\t"	 \
		    "lsr   %[mask], %[mask_0x3c], #1                @  .. and with 0x1fe                          \n\t"	 \
		    "ldr   %[w], [%[wp]], #4                        @ Pre-load first word of rowlets              \n\t"	 \
		    : [time_base] "=r" (time_base), [jump] "=r" (jump), [mask_0x3c] "=r" (mask_0x3c),                    \
		      [wp] "+r" (wp), [w] "=r" (w), [mask] "=r" (mask)  				                 \
		    : [BASE] "J" (TIME_BASE), [JUMP] "J" (DISPATCH_TABLE), [ctrl] "r" (ctrl) : "memory");                \
  } while (false)

#define initialise_control()					                                           \
  do {									                                   \
      ((uint64_t*)__control)[GLOBAL_TIMER >> 2] = 0;                              /* Set 64-bit timer   */ \
      __control[DMA_BUFFER_READ >> 2]           = (uint32_t)dma_buffer0;          /* Set up DMA buffers */ \
      __control[DMA_BUFFER_WRITE >> 2]          = (uint32_t)dma_buffer1;		                   \
      __control[TIME_BASE >> 2]                 = ((uint32_t)ring_buffer0 >> 13); /* Set up time_base   */ \
  } while (false)

//=============================================================================
// Global Timer Routines (the SpiNNaker simulation clock)
//=============================================================================

//! \brief We use the following union type to allow us to address the global
//! clock words in the control array.

#define __global_timer_address ((uint64_t*)((uint32_t)__control + GLOBAL_TIMER))

//! \brief Increment the global timer.

void global_timer_tick (void)      {   *(__global_timer_address) += 1;     }

//! \brief Returns the current global clock value.

uint64_t global_timer_value (void) {   return (*(__global_timer_address)); }

//! \brief Sets the current global clock value.

void set_global_timer (uint64_t t) {   *(__global_timer_address) = t;      }

//=============================================================================

    // Is there anything in the write-back queue?
    // (Not at the moment: we have no plasticity!)


//! \param[in] r0 SDRAM address of row_header
//! \param     r1 rowlet_header buffer pointer

#define spike_to_dma()							          \
  do {									          \
      asm volatile ("stmib ip, {r0-r3}         @ Do DMA transfer ..         \n\t" \
		    "add   %[rp], %[rp], #8    @ Increment header ptr       \n\t" \
		    : [rp] "+r" (rowlet_ptr)				          \
		    : "r" (dma), "r" (descriptor), "r" (clear_ctrl)	          \
		    : "cc", "memory");					          \
  } while (false)

//! \brief Transfers Rowlet Descriptor Words to the DMA Command Buffer
//!
//! The Rowlet Descriptor word consists of three blocks:
//!
//!      AAAA AAAA AAAA AAAA AAAA ADDD DSSS SSSS
//!
//! with 21-bit address offset in SDRAM, 4-bit delay, and 7-bit size.
//!
//! Each of these words is translated into a three word DMA command in the Command Buffer;
//! The first word is the actual, SDRAM address, the second is the DTCM address for delivery,
//! and the third word is the DMA control word, with a suitable burst size.
//!
//! NOTE!!! Does not write to dma[4] to reset completed dma counter in bits 10-11 of dma[3]
//!
//! In use, we need only use the code:
//!
//!      mov   r3, #0x8          @ Cancel one of the DMA-completed flags.
//!             .......
//!      ldmia %[cp]!, {r0-r2}   @ Load the Command words, from cp, auto-incrementing
//!      stmib %[dma], {r0-r3}   @ Do DMA transfer ..
//!
//! Alternatively, set the cp to be the memory-mapped DMA address 0x40000000, and have the
//! commands directly transferred to the DMA engine.
//!
//! \param rp Rowlet Pointer (auto-incremented).
//! \param cp DMA Command Pointer NOTE: This register is NOT auto-incremented
//! \param dp DTCM Buffer Pointer (auto-incremented).

//! This takes 12 cycles per DMA command processed (with 3 cycles being extra for burst calculation)

#define __rowlet_to_dma_command()							        \
  do {									                        \
    asm volatile ("ldr   r0, [%[rp]], #4              @ Get next rowlet                   \n\t" \
		  "str   %[dp], [%[cp], #8]           @ Store DTCM address                \n\t" \
		  "and   r0, r0, #0xfffff87f          @ mask out delay                    \n\t" \
		  "and   r1, %[mask], r0, lsl #2      @ mask off size to bits 8-2         \n\t" \
		  "add   r1, r1, #4                   @ Add 1: DMA-ing 0 words is silly   \n\t" \
		  "add   r2, %[sdram], r0, lsr #9     @ SDRAM address                     \n\t" \
		  "clz   r3, r1                       @ Take log_2(size)                  \n\t" \
		  "ldrb  r0, [%[table], r3]           @ Load the burst/control byte       \n\t"	\
		  "add   %[dp], %[dp], r1             @ increment the DTCM pointer        \n\t" \
		  "str   r2, [%[cp], #4]              @ Store SDRAM address               \n\t" \
		  "add   r0, r1, r0, lsl #20          @ Add size to shifted control word  \n\t" \
		  "str   r0, [%[cp], #12]             @ Store Control Word                \n\t" \
		  : [rp] "+r" (rp), [dp] "+r" (dp)				                \
		  : [cp] "r" (cp), [sdram] "r" (sdram), [table] "r" (table),  [mask] "r" (mask)	\
		  : "cc", "memory");					                        \
  } while (false)

//! transfer to rowlet delay buffers

/*
     and r0, %[mask_0x3c], %[rdw], lsr #5     @ r0 = ..DD DD..
     ldr r1, [%[ctrl], r0]                    @ load up corect buffer pointer
                                              @---> interlock
     str %[rdw], [r1], #4                     @ store rowlet descriptor word in buffer
 */

//! Used to unpack a rowlet descriptor word, and place it into the DMA engine.

/*void read_a_rowlet (void) asm ("read_a_rowlet") __attribute__ ((noinline, naked));
void read_a_rowlet (void)
{
    register uint32_t* cp          asm ("ip");
    register uint32_t* rp          asm ("r11");
    register uint32_t* dp          asm ("r10");
    register uint32_t  sdram       asm ("r9");
    register uint32_t  mask        asm ("r4");
    register uint8_t*  table       asm ("r5");

    table = log_size_to_burst;
    mask  = 0x1fc;
    cp    = dma_buffer0;
    sdram = 0x60000000;

    dp    = dma_buffer1;

    __rowlet_to_dma_command ();

    asm volatile ("mov   r3, #0x8            @ cancel one outstanding DMA \n\t"
		  "str   r3, [%[cp], #16]    @ Cancel one outstanding DMA \n\t"
		  "bx lr                                                  \n\t"
		  : : [cp] "r" (cp) : "memory");
}

#define try_to_read_a_rowlet()						         \
  do {									         \
      asm volatile ("ldr    r6, [r5, #16]    @ load rowlet pointer         \n\t" \
		    "ldr    r7, [r5, #20]    @ load rowlet base            \n\t" \
		    "cmp    r6, r7           @ test for no more rows       \n\t" \
		    "poplo  {r4,r5,r6,r7,pc} @ return (from dma scheduler) \n\t" \
		    "ldr    r3, [r6]         @ load rowlet from pointer    \n\t" \
		    "bl     read_a_rowlet    @ transfer rowlet from DMA    \n\t" \
		    "cmp    r6, r7           @ test again for more rows    \n\t" \
		    "lsrhss r4, r4, #1       @ test for a further DMA slot \n\t" \
		    "popeq  {r4,r5,r6,r7,pc} @ return (from dma scheduler) \n\t" \
		    "ldr    r3, [r6]         @ load rowlet from pointer    \n\t" \
		    "bl     read_a_rowlet    @ transfer rowlet from DMA    \n\t" \
		    "pop    {r4,r5,r6,r7,pc} @ return (from dma scheduler) \n\t" \
		    : "+r" (done), "=r" (inp), "=r" (outp)                       \
		    : "r" (ctrl)  : "cc", "memory");			         \
  } while (false)
*/
#define get_inspike()						                                  \
    do {									                  \
        asm volatile ("ldr   r1,      [%[ctrl], #12]   @ Get base address                \n\t" \
		      "add   %[outp], %[outp], #0x1000000 @ Increment output pointer        \n\t" \
		      "ldr   r0, [r1, %[outp], lsr #22]   @ Load spike                      \n\t" \
		      "ldr   r2,      [%[ctrl], #24]   @ Get small write descriptor      \n\t" \
		      "ldr   r1,      [%[ctrl], #32]   @ Get rowlet buffer pointer       \n\t" \
		      "str   %[outp], [%[ctrl], #8]    @ Write-back output pointer       \n\t" \
		      "@--------------------------------------------------------------------\n\t" \
		      "@ INSERT DMA TRANSFER CODE HERE!!!!                                  \n\t" \
		      "@--------------------------------------------------------------------\n\t" \
		      "stmib %[dma], {r0-r3}              @ Do DMA transfer                 \n\t" \
		      "add   r1, r1, #4                   @ Increment rowlet buffer ptr     \n\t" \
		      "ldr   r1,      [%[ctrl], #32]   @ Write-back rowlet buffer pointer\n\t" \
		      "lsrs  %[done], %[done], #1         @ Test again for another DMA done \n\t" \
		      "popeq {r4-r7,pc}                   @ Return if all done DMAs sorted  \n\t" \
		      "cmp %[inp], %[outp]                @ Test nonempty (again)           \n\t" \
		      : [done] "+r" (done), [outp] "+r" (outp)		                          \
		      : [ctrl] "r" (ctrl), [inp] "r" (inp), [dma] "r" (dma): "memory");     \
    } while (false)

//! \brief The following code conditionally calls the spike-to-DMA rountine if
//! there are some incoming spikes to process. It assumes that the DMA has at
//! least one free outstanding req#uest. (Note: if this is not the highest
//! priority task for the DMA scheduler, this assumption will need to be
//! checked.)
//!
//!



//! \brief The following sets the flags according to whether the circular
//! buffer is nonempty (i.e. has at least one element) or not, (i.e. might be
//! empty). The nonempty case is indicated when the Z flag is clear; "<inst>ne"

#define test_for_inspike()						                \
  do {									                \
       asm volatile ("ldr %[inp],  [%[ctrl], #16] @ Get input pointer          \n\t" \
		     "ldr %[outp], [%[ctrl], #8]  @ Get output pointer         \n\t" \
		     "mov  r3, #0x8                  @ Set up clear_control       \n\t" \
		     "cmp %[inp], %[outp]            @ Test nonempty              \n\t" \
		      : [inp] "=r" (inp), [outp] "=r" (outp)		                \
		      : [ctrl] "r" (ctrl) : "memory");                            \
  } while (false)


#define load_for_rowlet()						                  \
  do {									                  \
       asm volatile ("ldr   %[inp], [%[ctrl], #16]  @ Get input pointer          \n\t" \
		     "ldr   r1, [%[ctrl], #32]      @ Get output pointer         \n\t" \
		     "ldr   r2, [%[ctrl], #20]      @ Get small write descriptor \n\t" \
		     : [outp] "+r" (outp)		                                  \
		     : [ctrl] "r" (ctrl), [inp] "r" (inp) : "memory");	          \
  } while (false)

//! \brief The following sets the tests whether there is a rowlet transfer required. If there
//! is, it organises that transfer and then tests if more are needed.

#define test_and_process_rowlet()						                 \
  do {									                         \
       asm volatile ("cmp   %[inp], %[outp]              @ Test nonempty                   \n\t" \
		     "popeq {r4-r7,pc}                   @ Return if all done DMAs sorted  \n\t" \
		     "ldr   r1,     [%[ctrl], #12]       @ Get base address                \n\t" \
		     "add   %[outp], %[outp], #0x1000000 @ Increment output pointer        \n\t" \
		     "str   %[outp], [%[ctrl], #8]       @ Write-back output pointer       \n\t" \
		     "ldr   r0, [r1, %[outp], lsr #22]   @ Load spike                      \n\t" \
		     "@--------------------------------------------------------------------\n\t" \
		     "@ INSERT DMA TRANSFER CODE HERE!!!!                                  \n\t" \
		     "@--------------------------------------------------------------------\n\t" \
		     "lsrs  %[done], %[done], #1         @ Test again for another DMA done \n\t" \
		      : [done] "+r" (done), [inp] "=r" (inp), [outp] "=r" (outp)	         \
		      : [ctrl] "r" (ctrl) : "memory");                                     \
    } while (false)

//! \brief This routine is the "scheduler" for the DMA engine. It is callable
//! from C.
//!
//! We are passing in the "number" of oustanding transactions in r4.





/*

On entry 
//! Registers: r0  Done       The two bits of status indicating DMA-completion .... SS.. .... ....
//!            r2  DMA-status The entirity of the DMA status word
//!            r3  DMA-queues Four 8-bit counters for different DMA input queue lengths
//!            r4  DMA-base   The Base Address of the DMA engine memory-mapped registers

mov    %[mask], 0xff       @ load up byte mask
ands   r1, r3, %[mask]     @ and out highest priority DMA requests

 */

void dma_scheduler (void) asm ("dma_scheduler") __attribute__ ((noinline, naked));
void dma_scheduler (void)
{
    __label__ L0, L1, /*L2,*/ L3;

    register uint32_t*   ctrl        asm ("r12");
    register uint32_t*   dma         asm ("r11");
    register uint32_t    done        asm ("r0");
    register uint32_t    inp         asm ("r6");
    register uint32_t    outp        asm ("r7");

    //assert (outstanding != 0);
    asm volatile ("mov pc, lr\n\t"); // DRL Hack!! In case DMA register is signalling something!!!

    // To be on the safe side, and because we are going to call _something_, we stash r4/r5.
    // Note these are effectively scratch registers in the synazpse code.

    asm volatile ("push {r4,r5,r6,r7,lr} @ Save registers                 \n\t"
		  : : "r" (ctrl), "r" (dma), "r" (done) : "memory");

    //----------------------------------
    // Try to transfer a spike from
    // the inspike circular buffer
    //----------------------------------

    test_for_inspike (); // Test whether the buffer is empty
                         // Set circular buffer in and out registers
    
    asm goto ("beq %l[L1] @ Skip if there are no spikes \n\t" : : : "cc": L1);
L0:
    get_inspike ();      // Transfer the spike to the DMA engine.

    asm goto ("bne %l[L0] @ Transfer another spike, if there's still    \n\t"
	      "           @ a completed outstanding transaction         \n\t"
	      : : : "cc": L0);
L1:
    //----------------------------------
    // Try to perform a write-back
    //----------------------------------

    //try_to_write_back_a_rowlet ();
//L2:
    //----------------------------------
    // Try to perform a rowlet transfer
    //----------------------------------
    load_for_rowlet ();
L3:
    test_and_process_rowlet ();  // Test whether there's a rowlet transfer required.

    asm goto ("bne %l[L3]        @ Transfer another rowlet, if there's still    \n\t"
	      "                  @    a completed outstanding transaction       \n\t"
	      "pop {r4-r7,pc}    @ Return if all done DMAs sorted               \n\t"
	      : : : "cc": L3);
}


/*
Following code is 27 cycles, including return, provided there's no 
Can use r2, r3. 

      push  {lr}
      ldr   r0, [%[ctrl], OFF_RP]              @ load 'number' of rdw's
      ldr   r2, [%[ctrl], OFF_R_BASE]
      ldr   r1, [%[ctrl], OFF_BP]              @ load buffer pointer
      ldr   %[rdw], [r2, r0]                   @ load next rdw
      subs  r0, r0, #4
      str   r0, [%[ctrl], OFF_RP]              @ write-back 'number' of rdw's
      bleq  dma_scheduler
      str   r1, [%[dma], %[adrt]]              @ Store DTCM address
      add   r0, %[rdw], #1                     @ Add 1: DMA-ing 0 words is silly
      and   r0, %[mask], r0, lsl #2            @ Shift to position and mask (0x1fe)
      add   r1, r1, r0                         @ increment the DMA buffer pointer
      str   r1, [%[ctrl], OFF_BP]              @ write-back buffer pointer
      ldr   r2, [%[ctrl], OFF_BURST]           @ load the burst table address
      clz   r1, r0                             @ Take log_2(size)
      ldrb  r1, [r2, r1]                       @ Load the burst/control byte
      ldr   r2, [%[ctrl], OFF_SDRAM]
      bic   %[rdw], %[rdw], #0x600             @ Mask out delay bits
      add   %[rdw], r2, %[rdw], lsr #9         @ SDRAM address                                        \n\t" \
      str   %[rdw], [%[dma], %[adrs]]          @ Store SDRAM address                                  \n\t" \
      orr   r0, r0, r1, lsl #20                @ Add size to shifted descriptor word
      str   r0, [%[dma], %[desc]]              @ Store DMA Descriptor Word
      mov   r0, #0x8                           @ clear Done bit
      str   r0, [%[dma], %[d_ctrl]]            @ write CTRL
      pop   {pc}                                 @ return

[dma] = r4 (pre-set)
[mask]     (pre-set)

need to set up rdw, rp, bp, (need ld/st) burst, sdram (just need loading). 

Loop takes 13 cycles to complete (return not taken). Suggests doing them in blocks of eight, then checking for inspikes.

      ldr   %[rdw], [%[rp]], #4                @ pre-load next rdw
      str   %[dp], [%[dma], #8]                @ Store DTCM address
      bics  %[rdw], %[rdw], #0x780             @ Mask out delay bits
      bxeq  lr                                 @ Return if RDW is zero
      and   r0, %[mask], %[rdw], lsl #2        @ mask the size bits of rdw as ...S SSSS SS.. 
     	                                       @    (assuming mask is 0x1fe, as it is for rowlet processing)
      add   r0, r0, #4                         @ Add 1: DMA-ing 0 words is silly
      clz   r1, r0                             @ Take log_2(size)
      ldrb  r1, [%[burst], r1]                 @ Load the burst/control byte
      add   %[rdw], %[sdram], %[rdw], lsr #9   @ SDRAM address                                        \n\t" \
      str   %[rdw], [%[dma]], #8               @ Store SDRAM address                                  \n\t" \
      add   %[dp], %[dp], r0                   @ increment the DTCM pointer
      orr   r0, r0, r1, lsl #20                @ Add size to shifted control word
      str   r0, [%[dma]], #4                   @ Store DMA Descriptor Word

		  : [rdw] "+r" (rdw), [dp] "+r" (dp)				                                           \
		  : [dma] "r" (dma), [sdram] "r" (sdram), [mask] "r" (mask),                                               \
		    [adrs] "J" (DMA_ADRS), [adrt] "J" (DMA_ADRT), [desc] "J" (DMA_DESC), [d_ctrl] "J" (DMA_CTRL)           \
		  : "memory");			  

   thus processing a DMA is now the 8 cycle code:

    ldr  r0, [%[cp]], #4         @ load first word (SDRAM address)
    ldr  r1, [%[cp]], #4         @ load second word (DTCM address)
    str  r0, [%[dma], %[adrs]]   @ write SDRAM address
    ldr  r0, [%[cp]], #4         @ load third word (DESC)
    str  r1, [%[dma], %[adrt]]   @ write DTCM address
    str  r0, [%[dma], %[desc]]   @ write DESC
    mov  r0, #0x8                @ clear Done bit
    str  r0, [%[dma], %[d_ctrl]] @ write CTRL


 */

//! \brief translates a rwolet descriptor word into a sequence of three words
//! that can be directly copied to the DMA registers.
//! \param     w     The rowlet descriptor word
//! \param     wp    A pointer to the rowlet descriptor words
//! \param[in] mask  The mask bit pattern 0x1fe
//! \param     bp    A pointer to the eventual DTCM memory address for the DMA transfer.
//! \param     dp    A pointer to the DMA Command buffer
//! \param[in] burst A pointer to the table used to calculate the required burst size.
//! \param[in] sdram Base address for this processors allocation of SDRAM.

#define rdw_to_dma_register_sequence()					                                                   \
  do {asm volatile ("ldr   %[w], [%[wp]], #4             @ Load next rowlet descriptor word w                        \n\t" \
		    "str   %[bp], [%[dp], #4]            @ Store DTCM address                                        \n\t" \
		    "bic   %[w], %[w], #0x780            @ Mask out delay bits                                       \n\t" \
		    "and   r0, %[mask], %[w], lsl #2     @ mask the size bits of w as ...S SSSS SS..                 \n\t" \
		    "add   r0, r0, #4                    @ Add 1: DMA-ing 0 words is silly                           \n\t" \
		    "clz   r1, r0                        @ Take log_2(size)                                          \n\t" \
		    "ldrb  r1, [%[burst], r1]            @ Load the burst/control byte                               \n\t" \
		    "add   %[w], %[sdram], %[w], lsr #9  @ SDRAM address                                             \n\t" \
		    "str   %[w], [%[dp]], #8             @ Store SDRAM address                                       \n\t" \
		    "add   %[bp], %[bp], r0              @ increment the DTCM pointer                                \n\t" \
		    "orr   r0, r0, r1, lsl #20           @ Add size to shifted control word                          \n\t" \
		    "str   r0, [%[dp]], #4               @ Store DMA Descriptor Word                                 \n\t" \
		    : [w] "=r" (w), [dp] "+r" (dp), [wp] "+r" (wp), [bp] "+r" (bp)                                         \
		    : [burst] "r" (burst), [sdram] "r" (sdram), [mask] "r" (mask)                                          \
		    : "memory");		                                                                           \
  } while (false)

//! \brief Translates a sequence Rowlet Description Words (RDW's) into a
//! sequence of DMA transfer words. The end of the RDW sequence is indicated by
//! a zero.

void translate_rdws (void)  asm ("translate_rdw") __attribute__ ((noinline, naked));
void translate_rdws (void)
{

}


//! \brief Transfers Rowlet Descriptor Words to the DMA Command Buffer
//!
//! The Rowlet Descriptor word consists of three blocks:
//!
//!      AAAA AAAA AAAA AAAA AAAA ADDD DSSS SSSS
//!
//! with 21-bit address offset in SDRAM, 4-bit delay, and 7-bit size.
//!
//! Each of these words is translated into a three word DMA command in the Command Buffer;
//! The first word is the actual, SDRAM address, the second is the DTCM address for delivery,
//! and the third word is the DMA control word, with a suitable burst size.
//!
//! NOTE!!! Does not write to dma[4] to reset completed dma counter in bits 10-11 of dma[3]
//!
//! In use, we need only use the code:
//!
//!      mov   r3, #0x8          @ Cancel one of the DMA-completed flags.
//!             .......
//!      ldmia %[cp]!, {r0-r2}   @ Load the Command words, from cp, auto-incrementing
//!      stmib %[dma], {r0-r3}   @ Do DMA transfer ..
//!
//! Alternatively, set the cp to be the memory-mapped DMA address 0x40000000, and have the
//! commands directly transferred to the DMA engine.
//!
//! \param[in] rdw Rowlet Descriptor Word
//! \param[in] dma DMA Base Address
//! \param     dp  DTCM Buffer Pointer, DTCM address for DMA (auto-incremented).

//! This takes 12 cycles per DMA command processed (with 3 cycles being extra for burst calculation)

#define size_of_rowlet_descriptor_word()				                                                  \
  do {									                                                  \
    asm volatile ("and   r0, %[mask], %[rdw], lsl #2  @ mask the size bits of rdw as ...S SSSS SS..                 \n\t" \
		  "                                   @    (assuming mask is 0x1fe, as it is for rowlet processing) \n\t" \
		  "add   r0, r0, #4                   @ Add 1: DMA-ing 0 words is silly                             \n\t" \
		  : : [rdw] "r" (rdw), [mask] "r" (mask) : "cc", "memory");                                               \
  } while (false)

#define burst_size_of_rowlet_descriptor_word()							                          \
  do {									                                                  \
    asm volatile ("add   r1, %[ctrl], %[burst]        @ Add offset to ctrl for burst table                          \n\t" \
		  "clz   r2, r0                       @ Take log_2(size)                                            \n\t" \
		  "ldrb  r1, [r1, r2]                 @ Load the burst/control byte                                 \n\t" \
		  : : [ctrl] "r" (ctrl), [burst] "J" (LOG_SIZE_BURST_OFFSET) : "memory");	                          \
  } while (false)

//! \brief Transfers Rowlet Descriptor Words to the DMA Command Buffer
//!
//! The Rowlet Descriptor word consists of three blocks:
//!
//!      AAAA AAAA AAAA AAAA AAAA ADDD DSSS SSSS
//!
//! with 21-bit address offset in SDRAM, 4-bit delay, and 7-bit size.
//!
//! Each of these words is translated into a three word DMA command in the Command Buffer;
//! The first word is the actual, SDRAM address, the second is the DTCM address for delivery,
//! and the third word is the DMA control word, with a suitable burst size.
//!
//! NOTE!!! Does not write to dma[4] to reset completed dma counter in bits 10-11 of dma[3]
//!
//! In use, we need only use the code:
//!
//!      mov   r3, #0x8          @ Cancel one of the DMA-completed flags.
//!             .......
//!      ldmia %[cp]!, {r0-r2}   @ Load the Command words, from cp, auto-incrementing
//!      stmib %[dma], {r0-r3}   @ Do DMA transfer ..
//!
//! Alternatively, set the cp to be the memory-mapped DMA address 0x40000000, and have the
//! commands directly transferred to the DMA engine.
//!
//! \param[in] rdw Rowlet Descriptor Word
//! \param[in] dma DMA Base Address
//! \param     dp  DTCM Buffer Pointer, DTCM address for DMA (auto-incremented).

//! This takes 12 cycles per DMA command processed (with 3 cycles being extra for burst calculation)

#define translate_rowlet_descriptor_word_to_dma()							                   \
  do {									                                                   \
      size_of_rowlet_descriptor_word();                       /* Places size in r0                                      */ \
      burst_size_of_rowlet_descriptor_word ();                /* Places burst bits in r1 (clobbers r2)                  */ \
      asm volatile ("str   %[dp], [%[dma], %[adrt]]           @ Store DTCM address                                   \n\t" \
		    "add   %[dp], %[dp], r0                   @ increment the DTCM pointer                           \n\t" \
		    "add   %[rdw], %[sdram], %[rdw], lsr #9   @ SDRAM address                                        \n\t" \
		    "and   %[rdw], %[rdw], #-3                @ mask out delay bits from SDRAM address               \n\t" \
		    "str   %[rdw], [%[dma], %[adrs]]          @ Store SDRAM address                                  \n\t" \
		    "orr   r0, r0, r1, lsl #20                @ Add size to shifted control word                     \n\t" \
		    "str   r0, [%[dma], %[desc]]              @ Store Control Word                                   \n\t" \
		  : [rdw] "+r" (rdw), [dp] "+r" (dp)				                                           \
		  : [dma] "r" (dma), [sdram] "r" (sdram), [mask] "r" (mask),                                               \
		    [adrs] "J" (DMA_ADRS), [adrt] "J" (DMA_ADRT), [desc] "J" (DMA_DESC), [d_ctrl] "J" (DMA_CTRL)           \
		  : "memory");					                                                           \
  } while (false)

void dma_fill_rowlet_buffer (void) asm ("dma_fill_rowlet_buffer") __attribute__ ((noinline, naked));
void dma_fill_rowlet_buffer (void)
{
    register uint32_t* ctrl      asm ("r12"); /* control and constant access                 */

    register uint32_t* jump      asm ("r7");  /* The base of the dispatch jump table         */
    register uint32_t  mask      asm ("r6");  /* Mask 0x1fe                                  */
    register uint32_t  dma       asm ("r4");
    register uint32_t  done      asm ("r3");

    translate_rowlet_descriptor_word_to_dma();
    asm volatile ("bx lr        @ return immediately\n\t" : : : "memory");
}

//! \brief This is the default out-going dma processing routine, and is
//! called when we have _no_ out-going DMA requests to perform. This
//! happens -- if at all -- near the end of a clock tick when all DMA queues
//! are empty.

void dma_empty (void) asm ("dma_empty") __attribute__ ((noinline, naked));
void dma_empty (void)
{   asm volatile ("bx lr        @ return immediately\n\t" : : : "memory"); }

//! \brief The following C wrapper function calls the DMA feeding routine
//! if one or more DMAs have completed.
//!
//! We assume that the "ip" register is set to 0x40000000, the start of the
//! DMA engine's memory-mapped control registers.
//!
//! Done as a macro to prevent registers moving.
//!
//! Five cycles to check for any DMA-requests, and to poll the DMA status
//! register to see if any submitted requests have completed. If the
//! branch-and-link is then this code takes seven cycles to execute (plus at
//! least three to return).
//!
//! Registers: r0  Address of a DMA set-up routine
//!            r3  DMA-status The two done bits of the DMA status word
//!            r4  DMA-base   The Base Address of the DMA engine's memory-mapped registers

#define feed_dma_if_needed()						                                                   \
    do {asm volatile ("mov    r4, #0x40000000           @ Load base-address of DMA register base                     \n\t" \
		      "ldr    r3, [r4, %[status]]       @ Check DMA status                                           \n\t" \
		      "ldr    r0, [%[ctrl], %[addr]]    @ Load address of an outgoing DMA processing routine         \n\t" \
		      "ands   r3, r3, #0xc00            @ Test whether there are any spare DMA slots, this occurs .. \n\t" \
		      "                                 @   .. if either of the DMA-completed flags are set          \n\t" \
		      "blxne  r0                        @ Set up new DMA(s), if needed                               \n\t" \
		      : : [ctrl] "r" (ctrl), [addr] "J" (DMA_PROCESSING), [status] "J" (DMA_STAT): "cc", "memory");        \
    } while (false)

//! Rowlet Structure.
//!
//! The header word has 4-bytes.
//!
//! Lowest byte is number of standard/packed synapses. If this is 0, then we have a special case.
//! Top byte gives the delay to the continuation rowlet, which is in the next word. If this delay
//! is 0, then there is no follow-up rowlet.
//!
//! Thus a header of 0x00000000 is a rowlet that has no successor, and "no" synapses -- which would
//! be useless. So use it instead as a header for a "Full" synaptic rowlet. These are rowlets where
//! each neuron is assumed to be connected, so there's no need for the index component. Obviously,
//! we'd need to permit weights of 0, and in such cases the delay is irrelevant, so again a 16-bit
//! synapse all of which is 0, indicates -- quickly -- that there's nothing to do.
//!
//! Tags are in bits 12-19.
//! The assumed commonest tag is a fixed rowlet. These come in two sorts small and standard
//!
//! The approach is to use bits 12-15 as a jump tag; and bits 16-19 as further data.
//!
//! If bits 12-15 are all 0, then we have a "standard packed synapse". There is an extension
//! if bit 16 is set, and bits 17-19 encode the number of synapses. The values 1-7 are
//! represented in the obvious way, and the value 0 indicates that this is a larger row,
//! with size indicated elsewhere.
//!
//! One type to think about is the "sparse set of rows", in which a spike is matched to a number
//! of possible synapses.



//! Full synapses are:
//!
//!    (*) 16-bit half-word
//!    (*) And an unsigned 16-bit ring-buffer
//!
//! The format of the 16-bit synapse half-word is:
//!
//!      wwww wwww wwww dddd
//!
//! Where "w" represents a weight bit (12 off), "d" represents a delay bit (4 off)
//! and we no longer need to represent the neuron index, since that is implicit
//! from the position in the rowlet.
//!

/*

Assign timer_base := timer_base - rotated (wp_initial)

Then each

    ldrh w0, [wp], #2

increments wp by 2, _and_

    ldrh r0, [a0, wp]

will correctly align on the indexed ring-buffer element

Total time taken for a "full synapse row" is 256*6 = 1500: could be almost _double_ the time taken with
standad processing.

addressing of ring-buffer: 1-bit tcs + 4 bits delay + 8 index bits + 1 bit lo/hi byte = 14
   address offset   0x00000000-
                    0x000001fe
timer-bits          0x00001c00

          ZI =      0x00402000
dma_buffer1  = ZI + 0x00001000
ring_buffer0 = ZI + 0x00002000

Thought: use the auto-incrementing of wp as a "base", then the delay+(timer+offset)

So timer-base must be: (000t ttt0 0000 0000 + (ring_base - wp_base)) ror #13

     ldrh w, [wp], #2
     add  a, timer_base, w, lsl #28    @ add timer_base to delay
     ror  a, a, #19                    @ rotate around until delay bits are in 13-9
                                       @      000d ddd0 0000 0000
     ldrh r, [wp, a]                   @ load ring-buffer element (offset from wp)
     add  r, r, w, lsr #4              @ add weight
     strh r, [wp, a]                   @ write-back ring-buffer element

 */
 
//! Standard synapses are:
//!
//!    (*) A 32-bit word.
//!    (*) And an unsigned 16-bit ring-buffer
//!
//! The format of the 32-bit synapse word is:
//!
//!      wwww wwww wwww 0000 0000 dddd nnnn nnnn
//!
//! Where "w" represents a weight bit (12 off), "d" represents a delay bit (4 off)
//! and "n" represents a neural index (8 off).
//!
//! The weight is at the top because we can simply add a shifted weight using the
//! ARM add -- or in this case sub -- instruction.
//!
//! The delay and index are treated as a single unit, and is added to the combined
//! time_base register again, after shifting. But in this case we shift left, so
//! that the carry bit in the addition is ignored. After this, we rotate the answer
//! into the correct location. This works provided the ring-buffer is aligned on
//! a 8192-byte boundry!
//!
//! To support saturation, the ring-buffer elements count down from 0xffff
//! (representing 0) to 0x0000 (representing 65535). Thus _adding_ a weight
//! to the ring-buffer becomes a subtraction, and detecting a saturation is
//! merely the detection that the result -- in a 32-bit register -- has gone
//! negative.
//!
//! Finally, to improve the execution speed in what is hopefully the common
//! case, we process synaptic events _four_ at a time, _and_ only check for
//! saturation at the end of this block of code. If no saturation occurs the
//! code will have correctly updated the ring-buffer. If a saturation occurs
//! the ring-buffer write-backs (half-word conditional stores, "strplh", in
//! the following code) do not take place, and a saturation_fix_up routine
//! is called to repeat the synaptic event processing, only this time paying
//! more attention to writing back the saturated value, and counting the
//! number of saturations that have occured.
//!
//! It may seem extravagent to repeat an evaluation, but remember we are
//! expecting the user to repeat a saturated simulation with a smaller scale
//! factor on the weights, until saturation no longer occurs.
//!
//! Thus we pay one cycle in correct code for a branch not taken:
//! "bmi __saturation_fix_up", to avoid an eight cycle penalty for fixing up
//! erroneous code immediately.
//!
//! The head-line performance of this code is: 25 cycles for processing four
//! non-saturating synaptic events, using one state register ("wp"), one
//! constant register ("time_base"), and nine scratch registers. Along with
//! another state register counting out the synaptic events processed ("n"),
//! which is not touched by this code, but which ideally needs to be preserved
//! between calls, we use all TWELVE easily available registers.
//!
//! Note it is also possible to perform the __saturation_fix_up only once per
//! sixteen synapses processed, i.e. 1 additional cycle per 96, or just a 1.04%
//! performance penalty.
//!
//! The basic six instruction sequence is then:
//!
//!   ldr    w0, [wp], #4                ; load synapse, auto-incrementing pointer
//!   add    a0, time_base, w0, lsl #20  ; add in time and base to address
//!   ror    a0, a0, #19                 ; rotate around to the correct position
//!   ldrh   r0, [a0]                    ; load ring buffer element
//!   subs   r0, r0, w0, lsr #20         ; "add" 12-bit weight to ring-buffer value, setting flags
//!   strplh r0, [a0]                    ; store back modified result, if correct
//!
//! Then if a saturation occurs, we conditionally branch-and-link to it as
//! follows:
//!
//!   blmi   __saturation_fix_up
//!
//! The fix-up code is:
//!
//!   ldr    w0, [wp, #-4]               ; load synapse, auto-incrementing pointer
//!   ldr    sat, [sp, #4]               ; load saturation counter
//!   add    a0, time_base, w0, lsl #20  ; add in time and base to address
//!   ror    a0, a0, #19                 ; rotate around to the correct position
//!   ldrh   r0, [a0]                    ; load ring buffer element
//!   subs   r0, r0, w0, lsr #20         ; "add" weight to ring-buffer value, setting flags
//!   movmi  r0, #0                      ; saturate
//!   addmi  r0, r0, #1                  ; increment the saturation counter
//!   strh   r0, [a0]                    ; store back modified result.
//!   str    sat, [sp, #4]               ; store saturation counter
//!   bx     lr                          ; return
//!
//! We can interleave this fix-up code.
//!
//! Note the minimal number of cycles to process a synapse _must_ be at least:
//!
//!    ldr{T1} w, [wp], #4     ; Load a new synapse from the auto-incremented pointer
//!                            ;   T1: type of synapses
//!    "add"   index(w), time  ; index(w) is some sort of index-delay extraction function
//!                            ;  which needs to be combined with adding and masking the current time
//!    ldr{T2} r, [f(a)]       ; T2: type of ring-buffer elements
//!                            ;    f(a) is an optional base + shifted address function.
//!                            ;    note: indexing with [r1, r2, <shft> #n] takes TWO cycles
//!    "add"   r, weight(w)    ; weight(w): a weight extraction function, probably a shift
//!    str{T2} r, [f(a)]       ; write back result to ring-buffer
//!
//!
//! Internal Register usage.
//!
//! +---------+----------------------------+------------------------------+
//! |  dir    |          names             |         ARM registers        |
//! +---------+----------------------------+------------------------------+
//! |  i/o    |          wp, n             |           %[wp], %[n]        |
//! |  in     |        time_base           |         %[time_base]         |
//! | scratch |   r0, r1, a0, a1, w0, w1   |    r0, r1, r2, r3, r4, %[w]  |
//! +---------+----------------------------+------------------------------+
//!
//! The i/o registers hold the state of the computation; the "in" register
//! holds a constant (or, more correctly a constant during _this_ clock tick);
//! and the scratch registers get trampled on, but are not set to any
//! particular value on entry to the routine.
//!
//! One other value is needed, and that's the saturation counter which we store
//! on the top of the stack.


//! Generic stuff about synapse processing
//! ======================================
//!
//! (1) The code is optimised to perform as fast as possible when there is _no_
//!     saturation. When saturation occurs, there is a price to be paid.
//!
//! (2) Control over how the processing of synapses proceeds lies primarily
//!     with the "synaptic word pointer" -- abbreviated wp (sp might be
//!     confused with the stack pointer!) -- in addition to the position in the
//!     code, which encodes previously taken decisions.
//!
//! (3) On entry to a synaptic processing routine, we expect the wp register to
//!     be pointing to the __next__ synaptic word, and the current synaptic
//!     word to be held in register "w". This will have been previously loaded.
//!
//!     The reason for this design decision is that we will use the first word
//!     of a rolwet to decide on the structure, type or tag of the rowlet. For
//!     example, some small rowlets might combine the tag information with a
//!     synaptic word.
//!
//!     In addition, if there is an extension rowlet (representing delays
//!     greater than 15 or 16 (value to be decided later!!)), this word sits
//!     immediately after the tag word w. After processing the extensi<on, we
//!     will come across the remainder of the synapses in the rowlet. It is for
//!     this reason that we must preserve w until the current bunch of synapses
//!     are processed: we cannot go back, as we do not know how far back to
//!     rewind the synaptic word pointer wp! (Though there is an important
//!     exception to this "rule": if we are processing a block of four synapses
//!     then there cannot be a rowlet extension word as there are not enough
//!     bits in 3 words to store a rowlet extension word _and_ four synapses!)
//!
//!     Another important reason is that if the word w is precisely 0, we will
//!     use this to indicate that synaptic processing has come to an end.
//!
//! (4) When saturation occurs in a ring buffer element, we will make a
//!     sub-routine call to "fix-up" or repair the missing updates to the ring-
//!     buffer. This is because in the main rountine, we only write-back the
//!     modified ring-buffer value when we have not had a saturation detected
//!     so far.
//!
//!     This has two important consequences.
//!
//!     (a) We must store the link register somewhere (see later why this might
//!         not be on the stack), since the call to the fix-up routine would
//!         otherwise trash it's value.
//!
//!     (b) In order to detect which synapses have saturated we preseve the
//!         modified write-back values as full 32-bit values in registers.
//!         If we rely on the values stored in the ring-buffer (as an unsigned
//!         16-bit value) we cannot then distinguish between a negative value
//!         -- which would indicate saturation -- and a positive value -- which
//!         indicates saturation did not take place.
//!
//!         There is thus a limit on the number of synapses that can share a
//!         fix-up routine, which is imposed by the number of registers that
//!         can be set aside to hold these values between each possible call to
//!         a fix-up routine. I've arbitrarily chosen to preserve the updated
//!         ring buffer elements in registers r0-r3 (depending on the number of
//!         synapses to be processed).
//!
//!         In addition, in the case of processing three or fewer synapses, we
//!         must preserve the first word of the rowlet in w. For four synapses
//!         we will be using a packed representation, so there is no confusion
//!         possible: there is no tag information in w (there's not enough
//!         space, as all bits are used!); additionally, any extension rowlet
//!         will already have been handled, again, as there are no bits left
//!         over to indicate whether there is an extension or not!
//!
//!         We thus reach the following position on entry to the relevant fix-
//!         up routines.
//!
//!         +----------+------------------------------------------------------+
//!         | Synapses | saturated value(s) | valid address(es) | w preserved?|
//!         +----------+------------------------------------------------------+
//!         |     1    |        r0          |        r4         |  un-needed  |
//!         |     2    |       r0, r1       |      r3, r4       |  un-needed  |
//!         |     3    |    r0, r1, r2      |    r3, r4, r5?     |     no      |
//!         |     4    |   r0, r1, r2, r3   |      r4, r5?       |     no      |
//!         +----------+------------------------------------------------------+
//!
//!         Notice that this is strongly hinting that we should use register r5
//!         for %[w].
//!
//! (5) To make it more convenient for the fix-up routines to access their
//!     synapses, we postpone any auto-incrementing of the %[wp] register until
//!     after any fix-up has occurred.
//!
//! (6) Access to constants and global variables is via the control register in
//!     %[ctrl].


#define synapse_0()							                                                \
  do {									                                                \
      asm volatile ("                                       @ A synaptic word has already been pre-loaded into w, \n\t" \
		    "                                       @   but it had no left-over synapses; so prepare to   \n\t"	\
		    "                                       @   process quads. But quads must have 3 full words   \n\t" \
                    "ldr  %[w], [%[wp]], #4                 @ Get next word                                       \n\t" \
                    : [w] "=r" (w), [wp] "+r" (wp) : : "memory");	                                                \
    } while (false)

//! \brief Transfers the weight for one synaptic event -- held in register %[w] --
//! to the ring buffer "pointed" to by time_base (which actually combines the time
//! offset and a rotated base pointer). It uses registers r0, and r4 as scratch --
//! holding saturated weight, and ring_buffer address respectively -- and will also
//! update the wp pointer and load the next synaptic word into %[w].
//!
//! If no saturation occurs this code has 7 instructions, and depending on when
//! exactly %[w] was loaded, executes in 9 or 10 cycles. In the case of
//! saturation occuring, it takes ?? cycles.

#define synapse_1()							                                                \
  do {									                                                \
      asm volatile ("                                       @ The synaptic word is already pre-loaded into w      \n\t" \
		    "add    r4, %[time_base], %[w], lsl #20 @ Add to rotated time_base                            \n\t"	\
                    "ror    r4, r4, #19                     @ Rotate back again                                   \n\t"	\
                    "ldrh   r0, [r4]                        @ Load the ring-buffer element                        \n\t"	\
		    "subs   r0, r0, %[w], lsr #20           @ 'add' weight to ring buffer, testing for saturation \n\t"	\
		    "strplh r0, [r4]                        @ write back ring buffer, if no saturation            \n\t"	\
		    "ldr    %[w], [%[wp]], #4               @ Pre-load next synaptic word, incrementing wp        \n\t"	\
		    "blmi   __saturation_detected_1         @ if saturated, repair                                \n\t"	\
                    : [w] "+r" (w), [wp] "+r" (wp) : [time_base] "r" (time_base): "cc", "memory");                      \
    } while (false)

//! \brief This routine fixes up one saturation in a single synapse.
//! Consequently, we know exactly where the saturation must have occurred, and
//! how many there were (one, duh!). Furthermore the address of the ring buffer
//! element is still in r4. All we need to do is move the saturated value (0)
//! to r4, and increment the saturation counter.

void __saturation_detected_1 (void) asm ("__saturation_detected_1") __attribute__ ((noinline, naked));
void __saturation_detected_1 (void)
{
    ROWLET_REGISTER_MAP;

    asm volatile ("ldr    r1, [%[ctrl], %[off]]          @ Load saturation counter          \n\t"
		  "mov    r0, #0                         @ Saturate ring buffer             \n\t"
		  "strh   r0, [r4]                       @ Write back ring buffer           \n\t"
		  "adds   r1, r1, #1                     @ Increment the saturation counter \n\t"
		  "moveq  r1, #-1                        @ Saturate the saturation counter  \n\t"
		  "str    r1, [%[ctrl], %[off]]          @ Write back saturation counter    \n\t"
		  "bx     lr                             @ Return                           \n\t"
		  : : [ctrl] "r" (ctrl), [off] "J" (SATURATION_COUNTER) : "cc", "memory");
}

//! \brief Transfers the weights for two synaptic events -- one in %w] and one
//! pointed to by wp -- to the ring buffer "pointed" to by time_base (actually
//! combines the time offset and a rotated base pointer). It uses registers
//! r0-r4 as scratch, and will also update the wp pointer to and load the next
//! synaptic word, into %[w].
//!
//! If no saturation occurs this code has 13 instructions, and executes in 13 cycles. In the case of
//! saturation occuring in either synaptic event, it takes ?? cycles.

#define synapse_2()							                                 \
  do {									                                 \
      asm volatile ("                                       @ S0 word pre-loaded into w            \n\t" \
		    "ldr    r2, [%[wp]], #4                 @ S1 Load the synaptic word            \n\t" \
                    "add    r3, %[time_base], %[w], lsl #20 @ S0 Add to rotated time_base          \n\t" \
                    "ror    r3, r3, #19                     @ S0 Rotate back again                 \n\t" \
                    "ldrh   r0, [r3]                        @ S0 Load the ring-buffer element      \n\t" \
		    "add    r4, %[time_base], r2, lsl #20   @ S1 Add to rotated time_base          \n\t" \
                    "ror    r4, r4, #19                     @ S1 Rotate back again                 \n\t" \
                    "ldrh   r1, [r4]                        @ S1 Load the ring-buffer element      \n\t" \
		    "subs   r0, r0, %[w], lsr #20           @ S0 'add' weight to ring buffer       \n\t" \
		    "strplh r0, [r3]                        @ S0 write back ring buffer, if OK     \n\t" \
		    "subpls r1, r1, r2, lsr #20             @ S1 'add' weight to ring buffer       \n\t" \
		    "strplh r1, [r4]                        @ S1 write back ring buffer, if OK     \n\t" \
		    "ldr    %[w], [%[wp]], #4               @ Pre-load next synaptic word          \n\t" \
		    "blmi   __saturation_detected_2         @ if saturated, repair                 \n\t" \
                    : [w] "+r" (w), [wp] "+r" (wp) : [time_base] "r" (time_base) : "cc", "memory");      \
    } while (false)

//! \brief This routine fixes up one or two saturations that have occurred
//! while processing a pair of synapses. We still have the values of the
//! ring-buffer addresses in r3, r4, and the (possibly) saturated values of the
//! modified ring-buffer elements in registers r0, r1.

void __saturation_detected_2 (void) asm ("__saturation_detected_2") __attribute__ ((noinline, naked));
void __saturation_detected_2 (void)
{
    ROWLET_REGISTER_MAP;

    asm volatile ("cmp    r0, #0                @ Did the first synapse saturate?                          \n\t"
		  "movmi  r0, #0                @ Saturated value in r0                                    \n\t"
		  "strh   r0, [r3]              @ Store back modified result in all cases                  \n\t"
		  "movpl  r2, #-1               @ Local saturation counter (r2) holds sat count - 1        \n\t"
		  "cmp    r1, #0                @ Did the second synapse saturate?                         \n\t"
		  "movmi  r1, #0                @ Saturated value in r1                                    \n\t"
		  "strh   r1, [r4]              @ Store back modified result in all cases                  \n\t"
		  "ldr    r1, [%[ctrl], %[off]] @ Load global saturation counter                           \n\t"
		  "addpl  r2, r2, #-1           @ Local saturation counter holds sat count - 2             \n\t"
		  "add    r2, r2, #2            @ local saturation counter now holds the count             \n\t"
		  "adds   r1, r1, r2            @ 'Add' the local counter to the global one                \n\t"
		  "movcs  r1, #-1               @ Saturate the saturation counter                          \n\t"
		  "str    r1, [%[ctrl], %[off]] @ Write back global saturation counter                     \n\t"
		  "bx     lr                    @ Return                                                   \n\t"
		  : : [ctrl] "r" (ctrl), [off] "J" (SATURATION_COUNTER) : "cc", "memory");
}

//! \brief Transfers the weights for three synaptic event -- pointed to by wp --
//! to the ring buffer "pointed" to by time_base (actually combines the time
//! offset and a rotated base pointer). It uses registers r0, r1, r3, r4, r6
//! and r7 as scratch, and will also update the wp pointer to point to the next
//! synaptic word.
//!
//! If no saturation occurs this code has 19 instructions, and executes in 19 cycles. In the case of
//! saturation occuring in either synaptic event, it takes ?? cycles.
//!
//! Register usage
//! --------------
//!
//! ctrl         r12  Constants Pointer
//! wp           r11  Pointer to the next synaptic word
//! w            r10  The current synaptic word at the beginning and end of the code.
//! n            r9   Number of "items" to be processed
//! time_base    r8   Mask and base register combined
//! mask         r7   Mask 0x1fe
//! ----------------------------------------------------------
//! r0, r1, r2        Weights
//! r3, r4            Addresses of ring-buffer elements
//! lr                Used as a temporary variable to hold a synapse word

#define synapse_3()							                                       \
  do {									                                       \
      asm volatile ("                                        @ S0 word pre-loaded into w                 \n\t" \
                    "ldr    r0, [%[wp]], #4                  @ S1 Load the synaptic word                 \n\t" \
		    "ldr    lr, [%[wp]], #4                  @ S2 Load the synaptic word                 \n\t" \
                    "add    r3, %[time_base], r0, lsl #20    @ S1 Add to rotated time_base               \n\t" \
                    "ror    r3, r3, #19                      @ S1 Rotate back again                      \n\t" \
                    "ldrh   r1, [r3]                         @ S1 Load the ring-buffer element           \n\t" \
		    "add    r4, %[time_base], lr, lsl #20    @ S2 Add to rotated time_base               \n\t" \
                    "add    r2, %[time_base], %[w], lsl #20  @ S0 Add to rotated time_base               \n\t" \
		    "subs   r1, r1, r0, lsr #20              @ S1 'add' weight to ring buffer            \n\t" \
		    "strplh r1, [r3]                         @ S1 write back ring buffer, if OK          \n\t" \
                    "ror    r3, r2, #19                      @ S0 Rotate back again                      \n\t" \
                    "ldrh   r0, [r3]                         @ S0 Load the ring-buffer element           \n\t" \
                    "ror    r4, r4, #19                      @ S2 Rotate back again                      \n\t" \
                    "ldrh   r2, [r4]                         @ S2 Load the ring-buffer element           \n\t" \
		    "subpls r0, r0, %[w], lsr #20            @ S0 'add' weight to ring buffer            \n\t" \
		    "strplh r0, [r3]                         @ S0 write back ring buffer, if OK          \n\t" \
		    "subpls r2, r2, lr, lsr #20              @ S2 'add' weight to ring buffer            \n\t" \
		    "strplh r2, [r4]                         @ S2 write back ring buffer, if OK          \n\t" \
		    "ldr    %[w], [%[wp]], #4                @ Pre-load next synaptic word, increment wp \n\t" \
		    "blmi   __saturation_detected_3          @ if saturated, repair                      \n\t" \
                    : [w] "+r" (w), [wp] "+r" (wp) : [time_base] "r" (time_base) : "cc", "memory");            \
    } while (false)

//! \brief This routine fixes up one, two or three saturations that have occurred
//! while processing a pair of synapses. Though we don't know where the
//! saturations will have occurred, we do still have the values of the
//! addresses in r4, r5, and the calculated values of the modified ring-buffer
//! elements in r0, r1.

void __saturation_detected_3 (void) asm ("__saturation_detected_3") __attribute__ ((noinline, naked));
void __saturation_detected_3 (void)
{
    ROWLET_REGISTER_MAP;

    // needs checking
      
    asm volatile ("cmp    r0, #0                           @ Did the first synapse (S0) saturate?                     \n\t"
		  "movmi  r0, #0                           @ Saturate the result for S0 if needed                     \n\t"
		  "strh   r0, [r3]                         @ Store back modified result, in all cases                 \n\t"
		  "movpl  r0, #-1                          @ Local saturation counter (r0) holds sat count - 1        \n\t"
		  "cmp    r2, #0                           @ Did the second synapse (S2) saturate?                    \n\t"
		  "movmi  r2, #0                           @ Saturate the result for S2 if needed                     \n\t"
		  "strh   r2, [r4]                         @ Store back modified result in all cases                  \n\t"
		  "addpl  r0, r0, #-1                      @ Local saturation counter (r0) holds sat count - 2        \n\t"
		  "ldr    r2, [%[wp]], #-16                @ Start re-calculating address of S1                       \n\t"
		  "cmp    r1, #0                           @ Did the third synapse (S1) saturate?                     \n\t"
		  "movmi  r1, #0                           @ Saturate the result for S1 if needed                     \n\t"
		  "add    r2, %[time_base], r2, lsl #20    @ S1 Add to rotated time_base                              \n\t"
		  "ror    r2, r2, #19                      @ S1 Rotate back again                                     \n\t"
		  "strh   r1, [r2]                         @ Store back modified result in all cases                  \n\t"
		  "addpl  r0, r0, #-1                      @ Local saturation counter (r0) holds sat count - 3        \n\t"
		  "ldr    r1, [%[ctrl], %[off]]            @ Load global saturation counter                           \n\t"
		  "add    r0, r0, #3                       @ Local saturation counter now holds sat-count             \n\t"
		  "adds   r1, r1, r0                       @ Add the local counter to the global one                  \n\t"
		  "movcs  r1, #-1                          @ Saturate the saturation counter                          \n\t"
		  "str    r1, [%[ctrl], %[off]]            @ Write back global saturation counter                     \n\t"
		  "bx     lr                               @ Return                                                   \n\t"
		  : : [ctrl] "r" (ctrl), [wp] "r" (wp), [time_base] "r" (time_base),
		      [off] "J" (SATURATION_COUNTER) : "cc", "memory");
}

//! PACKED SYNAPSES
//!================
//!
//! The format of the standard 32-bit synapse word is:
//!
//!      wwww wwww wwww 0000 0000 dddd nnnn nnnn
//!
//! Where "w" represents a weight bit (12 off), "d" represents a delay bit (4 off)
//! and "n" represents a neural index (8 off).
//!
//! This is still the way we represent any synapses in excess of multiplies of four.
//! The "packed" synapse representation holds FOUR synapses in just THREE words.
//!
//! The layout is:
//!
//! WORD  1   wwww wwww wwww NNNN NNNN dddd nnnn nnnn    w's, d's, and n's for synapse S0;
//!                                                      N's index for S2
//! WORD  2   wwww wwww wwww NNNN NNNN dddd nnnn nnnn    w's, d's, and n's for synapse S1;
//!                                                      N's index for S3
//! HWORD 1                       wwww wwww wwww dddd    w's, d's for synapse S2
//! HWORD 2                       wwww wwww wwww dddd    w's, d's for synapse S3
//!
//! Processing a standard form synapse (S0, S1) is now as before; because the
//! presence or absence of anything in the middle byte doesn't affect the way
//! things are processed.
//!
//! The new packed synapses (S2, S3) require one extra instruction.

//!    ldr    %[w], [%[wp]], #4               @ S0 Pre-load next synaptic word for S0
//!    ldrh   lr, [%[wp], #2]                 @ S2 Pre-load synaptic half-word for S2 with 0x wwwd
//! ...
//!    @ w  = .... .... .... iiii iiii .... .... ....  (. = don't care)
//!    @ lr = .... .... .... .... wwww wwww wwww dddd  (. = 0)
//!
//!    and    r2, %[mask], %[w], lsr #11      @ S2 mask out middle 8-bits from w into bits 8-1
//!                                           @ r2 = .... .... .... .... .... ...i iiii iii. (. = 0)
//!
//!    add    r4, %[time_base], lr, lsl #28   @ S2 add delay to timer_base (= 4 bits time + base)
//!                                           @ r4 = tttt .... .... .... .... ..10 0000 000E
//!                                           @ where tttt = (bottom 4-bits of time + dddd), ignoring carry;
//!                                           @       . = 0; and
//!                                           @       E-bit indicates excitatory (0 = inhibitory)
//!
//!    orr    r4, r2, r4, ror #19             @ S2 rotate to position and 'or' in index bits
//!                                           @ r4 = 0000 0000 0100 0000 00Et ttti iiii iii0
//!
//!    ldrh   r2, [r4]                        @ S2 load ring-element
//!    subs   r2, r2, lr, lsr #4              @ S2 'add' weight
//!    strplh r2, [r4]                        @ S2 conditionally modify the ring-buffer, if OK


//! \brief The following certainly works, but can we do anything to reduce the
//! register-footprint? Using the link register as the "mask" (holding a
//! non-immediately representable constant of 0x1fe) is 'tricky, very tricky'.
//!
//! NOTE!! Use registers r2, r3 to hold possibly saturated results from S2/S3
//! calculations. This permits easy detection of saturation. The following
//! looks a bit better..
//!
//! scratch: r0, r1: temps for ring buffer values and other bits'n'bobs
//!          r2, r3: "weights" or words.
//!          r4, r5: address calculations
//!
//! constant registers: time_base, holds rotated time and base
//!                     mask       holds 0x1fe
//!
//! changing registers: wp         rowlet pointer
//!
//! Reference is made to the Synapse being processed: S0, S1, S2, S3.


//! HACK!!! HACK!!! HACK!!! DRL!!! Need to retain initial word, because we may not be able to rewind to the correct wp
//!                                (Think Rowlet extension!!)
//! Answer: All packed_4 synapses occur __after__ we've dealt with the rowlet extension. So only have to consider this
//! case in synapse_3, where we __may__ get an intervening rowlet extension.

#define packed_quad()							                                              \
  do {							       	                                                      \
    asm volatile ("                                       @ S0 word pre-loaded into w                           \n\t" \
		  "ldr    r1, [%[wp]], #4                 @ S1 Pre-load next synaptic word for S1               \n\t" \
		  "ldrh   lr, [%[wp]], #2                 @ S2 Pre-load synaptic half-word for S2 with 0x wwwd  \n\t" \
		  "and    r2, %[mask], %[w], lsr #11      @ S2 mask out middle 8-bits from w into bits 8-1      \n\t" \
		  "add    r3, %[time_base], %[w], lsl #20 @ S0 add delay|index to timer_base                    \n\t" \
		  "add    r4, %[time_base], lr, lsl #28   @ S2 add delay to timer_base (= 4 bits time + base)   \n\t" \
		  "orr    r4, r2, r4, ror #19             @ S2 rotate to position and 'or' in index bits        \n\t" \
		  "ldrh   r2, [r4]                        @ S2 load ring-element                                \n\t" \
		  "ror    r3, r3, #19                     @ S0 rotate to position                               \n\t" \
		  "ldrh   r0, [r3]                        @ S0 load ring-element                                \n\t" \
		  "subs   r2, r2, lr, lsr #4              @ S2 'add' weight                                     \n\t" \
		  "strplh r2, [r4]                        @ S2 conditionally store ring-element                 \n\t" \
		  "subpls r0, r0, %[w], lsr #20           @ S0 conditionally 'add' weight, if OK so far         \n\t" \
		  "ldrh   lr, [%[wp]], #2                 @ S3 Pre-load synaptic half-word for S3 with 0x wwwd  \n\t" \
		  "strplh r0, [r3]                        @ S0 conditionally store ring-element                 \n\t" \
		  "@============================================================================================\n\t" \
		  "@  At this point we have done synapses S0 and S2, and only r0, and r2 need to be preserved.  \n\t" \
		  "@  We have also pre-loaded the synapses S1 and S3.                                           \n\t" \
		  "@                                                                                            \n\t" \
		  "@ To process S1 and S3, whilst preserving r0 and r2 and using only the remaining registers:  \n\t" \
		  "@ r1, r3, r4, w, and lr; we have had to make some very peculiar register assignments for the \n\t" \
		  "@ the next block of code.                                                                    \n\t" \
		  "@============================================================================================\n\t" \
		  "and    r3, %[mask], r1, lsr #11        @ S3 mask out middle 8-bits from w into bits 8-1      \n\t" \
		  "add    %[w], %[time_base], lr, lsl #28 @ S3 add delay to timer_base (= 4 bits time + base)   \n\t" \
		  "orr    %[w], r3, %[w], ror #19         @ S3 rotate to position and 'or' in index bits        \n\t" \
		  "ldrh   r3, [%[w]]                      @ S3 load ring-element                                \n\t" \
		  "add    r4, %[time_base], r1, lsl #20   @ S1 add delay|index to timer_base                    \n\t" \
		  "ror    r4, r4, #19                     @ S1 rotate to position                               \n\t" \
		  "subpls r3, r3, lr, lsr #4              @ S3 conditionally 'add' weight, if OK so far         \n\t" \
		  "ldrh   lr, [r4]                        @ S1 load ring-element                                \n\t" \
		  "strplh r3, [%[w]]                      @ S3 conditionally store ring-element                 \n\t" \
		  "ldr    %[w], [%[wp]], #4               @ S4 Pre-load next synaptic word                      \n\t" \
		  "subpls r1, lr, r1, lsr #20             @ S1 conditionally 'add' weight, if OK so far         \n\t" \
		  "strplh r1, [r4]                        @ S1 conditionally store ring-element                 \n\t" \
		  "blmi   __packed_fix_up_4               @ Perform fix-up, if saturation occurred              \n\t" \
		  : [w] "+r" (w), [wp] "+r" (wp) : [time_base] "r" (time_base), [mask] "r" (mask) : "cc", "memory");  \
  } while (false)


/*

w2 = lr
i2 = r2
a0 = r3
a2 = r4
======================================================================================
"ldrh   lr, [%[wp], #2]                     @ S2
"and    r2, %[mask], %[w], lsr #11          @ S2
"add    r3, %[time_base], %[w], lsl #20     @ S0
"add    r4, %[time_base], lr, lsl #28       @ S2
"add    r4, r2, r4, ror #19                 @ S2 i2 = r2 now free
"ldrh   r2, [r4]                            @ S2
"ror    r3, r3, #19                         @ S0
"ldrh   r0, [r3]                            @ S0
"subs   r2, r2, lr, lsr #4                  @ S2
"strplh r2, [r4]                            @ S2
"subpls r0, r0, %[w], lsr #20               @ S0
"ldrh   w3, [%[wp]], #4                     @ S3 Load up third  synapse containing 0x wwwd       \n\t" \
"strplh r0, [r3]                            @ S0
		  "@============================================================================================\n\t" \
		  "@  At this point only r0, and r2 need to be preserved.                          \n\t" \
		  "@============================================================================================\n\t" \
========================================================================================
available are r1, r3, r4, lr, w

r0, r2 now need preserving

available are r1, r3, r4, lr, w
                                                                                =r1  =r1  =r3  =r3?
                                                     +------+    +----+----+----+----+----+----+----+----+----+----+
                                                     | out  |    | w1 | w3 | a1 | a3 | r1 | r3 | i3 |    |    |    |
                                                     +------+    +----+----+----+----+----+----+----+----+----+----+
(1)  ldr    w1, [%[wp]]                       @ S1   |  w1  |    |_w1_|    |    |    |    |    |    |    |    |    | 
(A)  ldrh   w3, [%[wp]], #4                   @ S3   |  w3  |    | .. |_w3_|    |    |    |    |    |    |    |    |
(2)  add    a1, %[time_base], w1, lsl #28     @ S1   |  a1  |    | w1 | .. |_a1_|    |    |    |    |    |    |    | 
(B2) and    i3, %[mask], w1, lsr #11          @ S3   |  i3  |    | w1 | .. | .. |    |    |    |_i3_|    |    |    |
(B1) add    a3, %[time_base], w3, lsl #28     @ S3   |  a3  |    | .. | w3 | .. |_a3_|    |    | .. |    |    |    | 
(D)  add    a3, i3, a3, ror #19               @ S3   |  a3  |    | .. | .. | .. |*a3 |    |    | i3 |    |    |    |
(E)  ldrh   r3, [a3]                          @ S3   |  r3  |    | .. | .. | .. | a3 |    |_r3_|    |    |    |    |
(3)  ror    a1, a1, #19                       @ S1   |  a1  |    | .. | .. |*a1 | .. |    | .. |    |    |    |    |
(4)  ldrh   r1, [a1]                          @ S1   |  r1  |    | .. | .. | a1 | .. |_r1_| .. |    |    |    |    |
(F)  subpls r3, r3, w3, lsr #4                @ S3   |  r3  |    | .. | w3 | .. | .. | .. |*r3 |    |    |    |    |
(G)  strplh r3, [a3]                          @ S3   |  --  |    | .. |    | .. | a3 | .. | r3 |    |    |    |    |
(5)  subpls r1, r1, w1, lsr #20               @ S1   |  r1  |    | w1 |    | .. |    |*r1 |    |    |    |    |    |
(6)  strplh r1, [a1]                          @ S1   |  --  |    |    |    | a1 |    | r1 |    |    |    |    |    |

(H)  ldr    %[w], [%[wp]], #8                 @ S++  |  w+  |    |    |    | .. |    | .. |    |    |    |    |    |

                                                  +------+    +----+----+----+----+----+----+----+----+----+----+----+
                                                  |      |    | w  |    | lr | r4 |=r1 |=r3 |    |    |    |    |    |
                                                  +------+    +----+----+----+----+----+----+----+----+----+----+----+
                                                  | out  |    | w1 | w3 | a1 | a3 | r1 | r3 | i3 |    |    |    |    |
                                                  +------+    +----+----+----+----+----+----+----+----+----+----+----+
(3)  ror    a1, a1, #19                    @ S1   |  a1  |    | .. | .. |*a1 | .. |    |    | .. |    |    |    | 5
(4)  ldrh   r1, [a1]                       @ S1   |  r1  |    | .. | .. | a1 | .. |_r1_|    | .. |    |    |    | 6*
(D)  add    a3, i3, a3, ror #19            @ S3   |  a3  |    | .. | .. | .. |*a3 | .. |    | i3 |    |    |    | 6*
(E)  ldrh   r3, [a3]                       @ S3   |  r3  |    | .. | .. | .. | a3 | .. |_r3_|    |    |    |    | 6*
(5)  subpls r1, r1, w1, lsr #20            @ S1   |  r1  |    | w1 | .. | .. | .. |*r1 | .. |    |    |    |    | 6*
(6)  strplh r1, [a1]                       @ S1   |  --  |    |    | .. | a1 | .. | r1 | .. |    |    |    |    | 5
(F)  subpls r3, r3, w3, lsr #4             @ S3   |  r3  |    |    | w3 |    | .. | .. |*r3 |    |    |    |    | 4
(G)  strplh r3, [a3]                       @ S3   |  --  |    |    |    |    | a3 | .. | r3 |    |    |    |    | 3
                                                  +------+    +----+----+----+----+----+----+----+----+----+----+----+

(H) ldr    w1, [%[wp]], #8                 @ S++  |  w+  |    |    |    | .. |    | .. | .. |    |    |    |    |

                                                  +------+    +----+----+----+----+----+----+----+----+----+----+----+
                                                  |      |    |    |    |    |    |=r1 |=r3 |    |    |    |    |    |
                                                  +------+    +----+----+----+----+----+----+----+----+----+----+----+
                                                  | out  |    | w1 | w3 | a1 | a3 | r1 | r3 | i3 |    |    |    |    |
                                                  +------+    +----+----+----+----+----+----+----+----+----+----+----+
(D)  add    a3, i3, a3, ror #19            @ S3   |  a3  |    | .. | .. |    |*a3 |    |    | i3 |    |    |    | 4
(E)  ldrh   r3, [a3]                       @ S3   |  r3  |    | .. | .. |    | a3 |    |_r3_|    |    |    |    | 4
(2)  add    a1, %[time_base], w1, lsl #28  @ S1   |  a1  |    | w1 | .. |_a1_| .. |    | .. |    |    |    |    | 5
(3)  ror    a1, a1, #19                    @ S1   |  a1  |    | .. | .. |*a1 | .. |    | .. |    |    |    |    | 5
(F)  subpls r3, r3, w3, lsr #4             @ S3   |  r3  |    | .. | w3 | .. | .. |    |*r3 |    |    |    |    | 5
(4)  ldrh   r1, [a1]                       @ S1   |  r1  |    | .. |    | a1 | .. |_r1_| .. |    |    |    |    | 5
(G)  strplh r3, [a3]                       @ S3   |  --  |    | .. |    | .. | a3 | .. | r3 |    |    |    |    | 5
(H)  ldr    w3, [%[wp]], #8                @ S++  |  w+  |    | .. |_w4_| .. |    | .. | .. |    |    |    |    | 5
(5)  subpls r1, r1, w1, lsr #20            @ S1   |  r1  |    | w1 | .. | .. |    |*r1 | .. |    |    |    |    | 5
(6)  strplh r1, [a1]                       @ S1   |  --  |    |    | .. | a1 |    | r1 | .. |    |    |    |    | 4
                                                  +------+    +----+----+----+----+----+----+----+----+----+----+----+


available are r1, r3, r4, lr, w

a1  = r4
a3  = w
w3  = lr
RR3 = r3
RR1 = w3
w1  = r1
w4  = w
i3  = r3
====================================================================================
(A)  ldrh   lr, [%[wp]], #4                 @ S3
(1)  ldr    r1, [%[wp]]                     @ S1
--------------------------------------------------
(2)  add    r4, %[time_base], r1, lsl #28   @ S1
(B2) and    r3, %[mask], r1, lsr #11        @ S3
(B1) add    %[w], %[time_base], lr, lsl #28 @ S3
(D)  add    %[w], r3, %[w], ror #19         @ S3
(E)  ldrh   r3, [%[w]]                      @ S3    r3 starts here!
(2)  add    r4, %[time_base], r1, lsl #28   @ S1    a1 starts here!
(3)  ror    r4, r4, #19                     @ S1
(F)  subpls r3, r3, lr, lsr #4              @ S3    r3 assignment             w3 = w4 = w --- can use r1 to here
(4)  ldrh   lr, [r4]                        @ S1    r1 needed?
(G)  strplh r3, [%[w]]                      @ S3    a3 = w4 = w?
(H)  ldr    %[w], [%[wp]], #8               @ S++
(5)  subpls r1, lr, r1, lsr #20             @ S1    r1 assignment w1 in lr/r4
(6)  strplh r1, [r4]                        @ S1    a1 in r4/lr
=====================================================================================

1 << 2 < 3 < 4 <<< 5 < 6
A <<< B1/B2 < D < E <<< F < G
1 << B2


(1)  ldr    w1, [%[wp]]                       @ S1
(2)  add    a1, %[time_base], w1, lsl #28     @ S1
(3)  ror    a1, a1, #19                       @ S1
(4)  ldrh   r1, [a1]                          @ S1
(5)  subpls r1, r1, w1, lsr #20               @ S1
(6)  strplh r1, [a1]                          @ S1

(A)  ldrh   w3, [%[wp]], #4                   @ S3
(B1) add    a3, %[time_base], w3, lsl #28     @ S3
(B2) and    i3, %[mask], w1, lsr #11          @ S3
(D)  add    a3, i3, a3, ror #19               @ S3
(E)  ldrh   r3, [a3]                          @ S3
(F)  subpls r3, r3, w3, lsr #4                @ S3
(G)  strplh r3, [a3]                          @ S3

(H) ldr    %[w], [%[wp]], #8                 @ S++

Put (1) or (7) (or both??) back into previous part

*/

void __packed_fix_up_4 (void) asm ("__packed_fix_up_4") __attribute__ ((noinline, naked));
void __packed_fix_up_4 (void)
{
    ROWLET_REGISTER_MAP;

    // Start by re-doing the synapse (S1).
    
    asm volatile ("cmp    r1, #0                            @ Did the third synapse (S1) saturate?                     \n\t"
		  "movmi  r1, #0                            @ Saturated value in r1                                    \n\t"
		  "strh   r1, [r4]                          @ Store back modified result, in all cases                 \n\t"
		  "movpl  r1, #-1                           @ local saturation counter r1 holds sat-count - 1          \n\t"
		  "@---------------------------------------------------------------------------------------------------\n\t"
		  "@  At this point, we now recalculate ring-buffer addresses for synapses S0, S2, and S3.             \n\t"
		  "@---------------------------------------------------------------------------------------------------\n\t"
		  "ldr    %[w], [%[wp], #-12]               @ recalculate address for (S0) ring-buffer                 \n\t"
		  "and    r4, %[mask], %[w], lsr #11        @ S2 mask out middle 8-bits from w into bits 8-1           \n\t"
		  "add    %[w], %[time_base], %[w], lsl #20 @ S0 add delay to timer_base and mask with shift           \n\t"
		  "ror    %[w], %[w], #19                   @ S0 rotate to position                                    \n\t"
		  "cmp    r0, #0                            @ Did the fourth synapse (S0) saturate?                    \n\t"
		  "movmi  r0, #0                            @ Saturated value in r0, if required (otherwise old value) \n\t"
		  "strh   r0, [%[w]]                        @ Store back modified result in all cases                  \n\t"
		  "addpl  r1, r1, #-1                       @ local saturation counter r1 holds sat-count - 2          \n\t"
		  "ldrh   %[w], [%[wp], #-6]                @ S2 Pre-load synaptic half-word for S2 with 0x wwwd       \n\t"
		  "add    %[w], %[time_base], %[w], lsl #28 @ S2 add delay to timer_base (= 4 bits time + base)        \n\t"
		  "orr    %[w], r4, %[w], ror #19           @ S2 rotate to position and 'or' in index bits             \n\t"
		  "cmp    r2, #0                            @ Did the fourth synapse (S0) saturate?                    \n\t"
		  "movmi  r2, #0                            @ Saturated value in r2, if required (otherwise old value) \n\t"
		  "strh   r2, [%[w]]                        @ Store back modified result in all cases                  \n\t"
		  "addpl  r1, r1, #-1                       @ local saturation counter r1 holds sat-count - 3          \n\t"
		  "ldr    %[w], [%[wp], #-8]                @ recalculate address for (S3) ring-buffer                 \n\t"
		  "and    r4, %[mask], %[w], lsr #11        @ S3 mask out middle 8-bits from w into bits 8-1           \n\t"
		  "ldrh   %[w], [%[wp], #-4]                @ S3 Pre-load synaptic half-word for S3 with 0x wwwd       \n\t"
		  "add    %[w], %[time_base], %[w], lsl #28 @ S3 add delay to timer_base (= 4 bits time + base)        \n\t"
		  "orr    %[w], r4, %[w], ror #19           @ S3 rotate to position and 'or' in index bits             \n\t"
		  "cmp    r3, #0                            @ Did the fourth synapse (S3) saturate?                    \n\t"
		  "movmi  r3, #0                            @ Saturated value in r3, if required (otherwise old value) \n\t"
		  "strh   r3, [%[w]]                        @ Store back modified result in all cases                  \n\t"
		  "addpl  r1, r1, #-1                       @ local saturation counter r1 holds sat-count - 4          \n\t"
		  "ldr    r2, [%[ctrl], %[off]]             @ Load global saturation counter                           \n\t"
		  "add    r1, r1, #4                                                                                   \n\t"
		  "adds   r1, r2, r1                        @ Add the local counter to the global one                  \n\t"
		  "movcs  r1, #-1                           @ Saturate the saturation counter                          \n\t"
		  "str    r1, [%[ctrl], %[off]]             @ Write back global saturation counter                     \n\t"
		  "bx     lr                                                                                           \n\t"
		  : [w] "=r" (w)
		  : [time_base] "r" (time_base), [wp] "r" (wp), [ctrl] "r" (ctrl), [mask] "r" (mask),
		    [off] "J" (SATURATION_COUNTER)
		  : "cc", "memory");
}

//! \brief Process a dense rowlet of 256 16-bit synapses. These have a 4-bit
//! delay in the bottom four bits, and a 12-bit weight in the top 12 bits of a
//! half-word.

//We need to add the time/delay pair, mask,
//  then add/sub offset involving wp
//
// calculate base address of wp, and of delay 0 row of ring buffer (which is fixed, and is either 0x404000 or 0x406000)

// Idea: start processing mid-way through 256 synapses.
//
//       Process first chunk. Then change time-base. Then process second chunk.
//
//       This change to time-base occurs just as we are about to wrap-over.
//       Note there is a problem at "wrap-over": it is not a single event!!
//       I think wrap-over occurs when wp "hits" 0x... 200
//
//

//! The basic sequence is:
//!
//!     "ldrh   %[h0], [%[wp]], #2                @ S0 Load a new half word synapse                    \n\t"
//!     "add    r4, %[time_base], %[h0], lsl #28  @ S0 Add delay to time-base                          \n\t"
//!	"add    r4, %[wp], r4, ror #19            @ S0 Add in the index, via wp                        \n\t"
//!	"ldrh   r0, [r4]                          @ S0 Load ring-buffer weight	                       \n\t"
//!     "subs   r0, r0, %[h0], lsr #4             @ S0 'add' weight                                    \n\t"
//!	"strplh r0, [r4]                          @ S0 Conditionally store ring-element                \n\t"
		      		      		      

//!
//! Register Usage
//!
//! Synaptic Row pointer: wp
//! Input half words h0, h1
//! Addresses a0, a1  (= r4, r5)
//! New weights r0-r3


#define __dense_4_head()       						                                                   \
    do {							       	                                                   \
        asm volatile ("                                         @ Assume that both synapse half-words are pre-loaded \n\t" \
		      "add    r4, %[time_base], %[h0], lsl #28  @ S0 Add delay to time-base                          \n\t" \
		      "add    r4, %[wp], r4, ror #19            @ S0 Add in the index, via wp                        \n\t" \
		      "ldrh   r0, [r4, #-4]                     @ S0 Load ring-buffer weight	                     \n\t" \
		      "add    r5, %[time_base], %[h1], lsl #28  @ S1 Add delay to time-base                          \n\t" \
		      "add    r5, %[wp], r5, ror #19            @ S1 Add in the index, via wp                        \n\t" \
		      "ldrh   r1, [r5, #-2]                     @ S1 Load ring-buffer weight                         \n\t" \
		      "subs   r0, r0, %[h0], lsr #4             @ S0 'add' weight                                    \n\t" \
		      "strplh r0, [r4, #-4]                     @ S0 Conditionally store ring-element                \n\t" \
		      "ldrh   %[h0], [%[wp]], #2                @ S2 Load a new half word synapse                    \n\t" \
		      "subpls r1, r1, %[h1], lsr #4             @ S1 'add' weight                                    \n\t" \
		      "strplh r1, [r5, #-2]                     @ S1 Conditionally store ring-element                \n\t" \
		      "ldrh   %[h1], [%[wp]], #2                @ S3 Load a new half word synapse and auto-increment \n\t" \
		      "@=============================================================================================\n\t" \
		      "@  At this point we have handled two of the four synapses                                     \n\t" \
		      "@=============================================================================================\n\t" \
		      "add    r4, %[time_base], %[h0], lsl #28  @ S2 Add delay to time-base                          \n\t" \
		      "add    r4, %[wp], r4, ror #19            @ S2 Add in the index, via wp                        \n\t" \
		      "ldrh   r2, [r4, #-4]                     @ S2 Load ring-buffer weight	                     \n\t" \
		      "add    r5, %[time_base], %[h1], lsl #28  @ S3 Add delay to time-base                          \n\t" \
		      "add    r5, %[wp], r5, ror #19            @ S3 Add in the index, via wp                        \n\t" \
		      "ldrh   r3, [r5, #-2]                     @ S3 Load ring-buffer weight                         \n\t" \
		      "subpls r2, r2, %[h0], lsr #4             @ S2 'add' weight                                    \n\t" \
		      "strplh r2, [r4, #-4]                     @ S2 Conditionally store ring-element                \n\t" \
		      : [wp] "+r" (wp), [h0] "+r" (h0), [h1] "+r" (h1) : [time_base] "r" (time_base) : "cc", "memory");    \
    } while (false)

#define __dense_4_tail()       						                                                   \
    do {							       	                                                   \
        asm volatile ("ldrh   %[h0], [%[wp]]                    @ S0 Load a new half word synapse                    \n\t" \
		      "subpls r3, r3, %[h1], lsr #4             @ S3 'add' weight                                    \n\t" \
		      "strplh r3, [r5, #-2]                     @ S3 Conditionally store ring-element                \n\t" \
		      "ldrh   %[h1], [%[wp]], #4                @ S1 Load a new half word synapse and increment      \n\t" \
		      "blmi   __dense_fix_up_4                  @ Perform fix-up, if saturation occurred             \n\t" \
		      : [wp] "+r" (wp), [h0] "=r" (h0), [h1] "+r" (h1) : : "cc", "memory");                                \
    } while (false)

#define __dense_4()  do { __dense_4_head (); __dense_4_tail (); } while (false)

//! On entry the new weights (one of which must be negative) are in r0-r3.
//! We have two "near-addresses" in r4, r5.
//! Register wp now points at the next pair of synapses, and thus needs to be wound back 8 bytes.
//!
//! So we fix up the last two synapses first, freeing up r2, r3.

void __dense_fix_up_4 (void) asm ("__dense_fix_up_4") __attribute__ ((noinline, naked));
void __dense_fix_up_4 (void)
{
    register uint32_t* ctrl      asm ("r12"); // control and constant access
    register uint32_t* wp        asm ("r11"); // Pointer to next synaptic word
    register uint32_t  w         asm ("r10"); // Current synaptic word
    register uint32_t  n         asm ("r9");  // Number of synapses in this rowlet.
    register uint32_t  time_base asm ("r8");  // Bottom 4 bits of global timer in bits 31-28
    register uint32_t  mask      asm ("r7");  // Mask 0x1fe

    asm volatile ("cmp    r2, #0                            @ Did S2 saturate?                                   \n\t"
		  "movmi  r2, #0                            @ Saturate if needed.                                \n\t"
		  "strh   r2, [r4, #-2]                     @ S2 Write-back ring-element                         \n\t" 
		  "movpl  r2, #-1                           @ r2 is local sat-counter.                           \n\t"
		  "cmp    r3, #0                            @ Did S3 saturate?                                   \n\t"
		  "movmi  r3, #0                            @ Saturate if needed.                                \n\t"
		  "strh   r3, [r5, #-4]                     @ S3 Write-back ring-element                         \n\t" 
		  "ldrh   r4, [%[wp], #-12]                 @ reload S0                                          \n\t"
		  "addpl  r2, r2, #-1                       @ r2 is local sat-counter.                           \n\t"
		  "ldrh   r5, [%[wp], #-10]                 @ reload S1                                          \n\t"
		  "add    r4, %[time_base], r4, lsl #28     @ S0 Add delay to time-base                          \n\t"
		  "add    r4, %[wp], r4, ror #19            @ S0 Add in the index, via wp                        \n\t"
		  "cmp    r0, #0                            @ Did S0 saturate?                                   \n\t"
		  "movmi  r0, #0                            @ Saturate if needed.                                \n\t"
		  "strh   r0, [r4, #-16]                    @ S0 Load ring-buffer weight	                 \n\t"
		  "addpl  r2, r2, #-1                       @ r2 is local sat-counter.                           \n\t"
		  "add    r5, %[time_base], r5, lsl #28     @ S1 Add delay to time-base                          \n\t"
		  "add    r5, %[wp], r5, ror #19            @ S1 Add in the index, via wp                        \n\t"
		  "cmp    r1, #0                            @ Did S1 saturate?                                   \n\t"
		  "movmi  r1, #0                            @ Saturate if needed.                                \n\t"
		  "strh   r1, [r5, #-14]                    @ S1 Load ring-buffer weight	                 \n\t"
		  "addpl  r2, r2, #-1                       @ r2 is local sat-counter.                           \n\t"
		  "ldr    r1, [%[ctrl], %[off]]             @ Load global saturation counter                     \n\t"
		  "add    r2, r2, #4                        @ Compensate for sat-counter being sc-4              \n\t"
		  "adds   r1, r2, r1                        @ Add the local counter to the global one            \n\t"
		  "movcs  r2, #-1                           @ Saturate the saturation counter                    \n\t"
		  "str    r2, [%[ctrl], %[off]]             @ Write back global saturation counter               \n\t"
		  "bx     lr                                                                                     \n\t"
		  : : [time_base] "r" (time_base), [wp] "r" (wp), [ctrl] "r" (ctrl),
		    [off] "J" (SATURATION_COUNTER), "r" (mask), "r" (n), "r" (w) : "cc", "memory");
}



void synapse_head (void) asm ("synapse_head") __attribute__ ((noinline, naked));
void synapse_head (void)
{
    __label__ L0, L1;

    register uint32_t* ctrl      asm ("r12"); // control and constant access
    register uint32_t* wp        asm ("r11"); // Pointer to next synaptic word
    register uint32_t  w         asm ("r10"); // Current synaptic word
    register uint32_t  n         asm ("r9");  // Number of synapses in this rowlet.
    register uint32_t  time_base asm ("r8");  // Bottom 4 bits of global timer in bits 31-28
    register uint32_t  mask      asm ("r7");  // Mask 0x1fe

    asm goto ("cmp  %[n], #0     @ Test whether the rolwet is empty (SHOULD NOT HAPPEN) \n\t"
	      "bxeq lr           @ Return if there are no synapses  (SHOULD NOT HAPPEN) \n\t"
	      "push {lr}         @ Otherwise, push link register: we might need to ..   \n\t"
	      "                  @  .. call saturation fix-up or dma feeding routines.  \n\t"
	      "tst  %[n], #1     @ Test to see if there's an odd synapse                \n\t"
	      "beq  %l[L0]       @ If not skip over synapse_1                         \n\t"
	      : : [n] "r" (n), "r" (mask) : "cc" : L0);

    synapse_1 ();

L0:
    asm goto ("tst  %[n], #2     @ Test to see if there's two odd synapses              \n\t"
	      "beq  %l[L1]       @ If not skip over synapse_2                         \n\t"
	      : : [n] "r" (n) : "cc" : L1);

    synapse_2 ();

L1:

    // BUG IN FOLLOWING refers to synapse jump table at 116.
    asm volatile ("ands  %[n], %[n], #0xfffffffc @ mask out the bottom 2 bits treated as small cases   \n\t"
		  "popeq {pc}                    @ If result is 0, we are done.                        \n\t"
		  "ldr   r1, [%[ctrl], #116]     @ Load the Synapse Jump Table                         \n\t"
		  "ands  r0, %[n], #0xc          @ Mask out bottom two bits of remaining n             \n\t"
		  "lsr   %[n], %[n], #4          @ n now indicates number of whole loops to do         \n\t"
		  "beq   packed_quad_loop          @ If no odds & ends need to be processed: jump        \n\t"
		  "ldr   pc, [r1, r0]            @  .. otherwise use jump table entry point            \n\t"
		  : [n] "+r" (n) : [ctrl] "r" (ctrl) : "cc", "memory");

    // Note: the jump -- either via the jump table or the conditional branch --
    // ensures we do not need sequentiality of code placement here.

    // Note: If we _do_ have sequential placement, then we can omit the "beq",
    //       and change the "ldr pc, .." to "ldrne pc, ..".

    // At the point that we jump into the loop body (start address:
    // "packed_quad_loop"), n will have the number of remaining, whole, loops
    // needed to complete the execution.
}

//! \brief Dispatch Function 3 performs a secondary dispatch. And a default
//! dense synapse, if bits JJJ of r0 are all 0.

void dense_256 (void) asm ("dense_256") __attribute__ ((noinline, naked));
void dense_256 (void)
{
    __label__ Loop;

    register uint32_t* ctrl      asm ("r12"); // control and constant access
    register uint32_t* wp        asm ("r11"); // Pointer to next synaptic word
    register uint32_t  w         asm ("r10"); // Current synaptic word
    register uint32_t  n         asm ("r9");  // Number of synapses in this rowlet.
    register uint32_t  time_base asm ("r8");  // Bottom 4 bits of global timer in bits 31-28
    register uint32_t  mask      asm ("r7");  // Mask 0x1fe

    register uint32_t  h0        asm ("r7");
    register uint32_t  h1        asm ("r6");
    register uint32_t  r5        asm ("r5");
    register uint32_t  r4        asm ("r4");

    asm volatile ("push   {lr}                              @ Return                                             \n\t"
		  "ldr    %[h1], [%[wp]], #4                @ Load synapses (Has this aleady been done?)         \n\t"
		  "mov    %[n], #15                         @ Number of loops to execute                         \n\t"
		  : [n] "=r" (n), [h1] "=r" (h1) : [wp] "r" (wp), "r" (mask), "r" (w), "r" (time_base), "r" (ctrl)
		  : "cc", "memory");

    h0 = 0xffff; // set up mask for one synpase


    asm volatile ("and    %[h0], %[h1], %[h0]               @ Initialise S0                                      \n\t"
		  "lsr    %[h1], %[h1], #16                 @ Initialise S1; Assumes little-endianness           \n\t"
		  : [h0] "+r" (h0), [h1] "+r" (h1) : : "cc", "memory");

    printx ((uint32_t)wp);
    printx (h0);
    printx (h1);

    //               wp = 00402004
    // time_base ror 19 = 00004000
    // ---------------------------
    //
   
    asm volatile ("add    r4, %[time_base], %[h0], lsl #28  @ S0 Add delay to time-base                          \n\t"
		  "add    r4, %[wp], r4, ror #19            @ S0 Add in the index, via wp                        \n\t"
		  "ldrh   r0, [r4, #-4]                     @ S0 Load ring-buffer weight	                 \n\t"
		  "add    r5, %[time_base], %[h1], lsl #28  @ S1 Add delay to time-base                          \n\t"
		  "add    r5, %[wp], r5, ror #19            @ S1 Add in the index, via wp                        \n\t"
		  "ldrh   r1, [r5, #-2]                     @ S1 Load ring-buffer weight                         \n\t"
		  "subs   r0, r0, %[h0], lsr #4             @ S0 'add' weight                                    \n\t"
		  "strplh r0, [r4, #-4]                     @ S0 Conditionally store ring-element                \n\t"
		  "subpls r1, r1, %[h1], lsr #4             @ S1 'add' weight                                    \n\t"
		  "strplh r1, [r5, #-2]                     @ S1 Conditionally store ring-element                \n\t"
		  : : [h0] "r" (h0), [h1] "r" (h1), [wp] "r" (wp), [time_base] "r" (time_base) : "cc", "memory");

    printx (r4);
    printx (r5);
    
    asm goto     ("@bpl    %l[Loop]                          @\n\t"
		  "pop    {pc}                              @\n\t" : : : "cc" : Loop);
    
Loop:
    //__dense_4();
    //__dense_4();
    //__dense_4();
    __dense_4_head ();

    asm volatile ("subpls r3, r3, %[h1], lsr #4             @ S3 'add' weight                                    \n\t"
		  "strplh r3, [r5, #-2]                     @ S3 Conditionally store ring-element                \n\t"
		  "blmi   __dense_fix_up_4                  @ Perform fix-up, if saturation occurred             \n\t"
		  : [wp] "+r" (wp), [h0] "+r" (h0), [h1] "+r" (h1) : : "cc", "memory");

    feed_dma_if_needed ();

    asm volatile ("subs   %[n], %[n], #1                    @ Test to see if the rowlet is completed             \n\t"
		  "ldrplh %[h0], [%[wp]]                    @ S0 Conditionally load a new half word synapse      \n\t"
		  "ldrplh %[h1], [%[wp]], #4                @ S1 Conditionally load a new half word synapse      \n\t"
		  : [n] "+r" (n), [h0] "=r" (h0), [h1] "=r" (h1), [wp] "+r" (wp) : : "cc", "memory");
    asm goto     ("@bpl    %l[Loop]                          @\n\t"
		  "pop    {pc}                              @\n\t" : : : "cc" : Loop);
}
  
/*
"add    r4, %[time_base], r2, lsl #20  @ S0 add delay to timer_base and mask with shift     \n\t" \
		      "ror    r4, r4, #19                    @ S0 rotate to position                              \n\t"	\
		      "ldrh   r0, [r4]                       @ S0 load ring-element                               \n\t"	\
		      "add    r5, %[time_base], r3, lsl #20  @ S1 add delay to timer_base and mask with shift     \n\t"	\
		      "ror    r5, r5, #19                    @ S1 rotate to position                              \n\t"	\
		      "ldrh   r1, [r5]                       @ S0 load ring-element                               \n\t"	\
		      "subs   r0, r0, r2, lsr #20            @ S0 'add' weight                                    \n\t"	\
		      "strplh r0, [r4]                       @ S0 conditionally store ring-element                \n\t"	\
		      "subpls r1, r1, r3, lsr #20            @ S1 conditionally 'add' weight, if OK so far        \n\t"	\
		      "strplh r1, [r5]                       @ S1 conditionally store ring-element                \n\t"	\
		      "@==========================================================================================\n\t" \
		      "@  At this point only the middle 8-bits of r2, r3 are still in use.                        \n\t" \
		      "@==========================================================================================\n\t" \
		      "and    r0, %[mask], r2, lsr #11       @ S2 mask out middle 8-bits from r2 into bits 8-1    \n\t" \
		      "ldrh   r2, [%[wp]], #2                @ S2 Load up third  synapse containing 0x wwwd       \n\t" \
		      "and    r1, %[mask], r3, lsr #11       @ S3 mask out middle 8-bits from r3 into bits 8-1    \n\t" \
		      "ldrh   r3, [%[wp]], #2                @ S3 Load up fourth synapse containing 0x wwwd       \n\t"	\
		      "add    r4, %[time_base], r2, lsl #28  @ S2 add delay to timer_base and mask with shift     \n\t"	\
		      "add    r4, r0, r4, ror #19            @ S2 add neuron id and rotate                        \n\t"	\
		      "add    r5, %[time_base], r3, lsl #28  @ S3 add delay to timer_base and mask with shift     \n\t"	\
		      "ldrh   r0, [r4]                       @ S2 load ring-element                               \n\t"	\
		      "add    r5, r1, r5, ror #19            @ S3 add neuron id and rotate                        \n\t"	\
		      "ldrh   r1, [r5]                       @ S3 load ring-element                               \n\t"	\
		      "subpls r2, r0, r2, lsr #4             @ S2 conditionally 'add' weight, if OK so far        \n\t"	\
		      "strplh r2, [r4]                       @ S2 conditionally store ring-element, if OK so far  \n\t"	\
		      "subpls r3, r1, r3, lsr #4             @ S3 conditionally 'add' weight, if OK so far        \n\t"	\
		      "strplh r3, [r5]                       @ S3 conditionally store ring-element, if OK so far  \n\t"	\
		      "blmi   __packed_fix_up_4              @ Perform fix-up, if saturation occurred             \n\t"	\
		      "ldr    r5, [%[wp]], #4                @ Pre-load next synaptic word                        \n\t"	\
                    : [wp] "+r" (wp) : [time_base] "r" (time_base), [mask] "r" (mask) : "cc", "memory");		\
    } while (false)


Trial 5 This might just work!!!! Needs topping and tailing!!

h0, h1 pre-loaded. wp pointing at next h0,h1 pair

     add    a0, %[time_base], h0, lsl #28     @ S0 Add delay to time-base
     add    a0, wp, a0, ror #19               @ S0
     ldrh   w0, [a0, #-4]                     @ S0 Load ring-buffer weight
>       add    a1, %[time_base], h1, lsl #28     @ S1 Add delay to time-base
>       add    a1, wp, a1, ror #19               @ S1
>       ldrh   w1, [a1, #-2]                     @ S1 Load ring-buffer weight
     subs   w0, w0, h0, lsr #4                @ S0 'add' weight
     strplh w0, [a0, #-4]                     @ S0 Conditionally store ring-element
     ldrh   h0, %[wp]                         @ S0 Load a half word synapse
>       subpls w1, w1, h1, lsr #4                @ S1 'add' weight
>       strplh w1, [a1, #-2]                     @ S1 Conditionally store ring-element
>       ldrh   h1, %[wp], #4                     @ S1 Load a half word synapse, with auto-increment

*/

/*
Trial 1: Problem three pipeline stalls -- might be fixable.

  wp, h0, h1, a0, a1, w1, w0

     ldrh   h0, %[wp], #2                     @ Load a half word synapse
>>
     add    a0, %[time_base], h0, lsl #28     @ Add delay to time-base
     add    a0, wp, a0, ror #19
     ldrh   h1, %[wp], #2                     @ Load a half word synapse
     ldrh   w0, [a0]                          @ Load ring-buffer weight
>
     add    a1, %[time_base], h1, lsl #28     @ Add delay to time-base
     add    a1, wp, a1, ror #19
     ldrh   w1, [a1]                          @ Load ring-buffer weight
     subs   w0, w0, h0, lsr #4                @ 'add' weight
     strplh w0, [a0]                          @ Conditionally store ring-element
     subs   w1, w1, h1, lsr #4                @ 'add' weight
     strplh w1, [a1]                          @ Conditionally store ring-element

Trial 2: Problem and/or one pipeline stall. Fixable using extra time-base register

Needs checking, but solution to auto-incrementing?
Needs checking, but rotates and shifts __may__ be OK (check extraneous bits don't intefere)

Move s1 load into previous 

     ldr    s1, %[wp], #4                     @ Load two synapses
>
     lsl    s0, s1, #16                       @ Place synapse 0 in top bits of s0

     add    a0, %[time_base], s0, lsl #12     @ Add delay to time-base
     add    a0, wp, a0, ror #19
     add    a1, %[time_base], s1, lsl #12     @ Add delay to time-base (extraneous bits in lower part of s1)
     add    a1, wp, a1, ror #19

     ldrh   w0, [a0]                          @ Load ring-buffer weight
     ldrh   w1, [a1, #2]                      @ Load ring-buffer weight
     subs   w0, w0, s1, lsr #20               @ 'add' weight
     strplh w0, [a0]                          @ Conditionally store ring-element
     subs   w1, w1, s2, lsr #20               @ 'add' weight
     strplh w1, [a1, #2]                      @ Conditionally store ring-element

Trial 3 Problem Still got pipeline stalls

  wp, h0, h1, a0, a1, w1, w0

     suppose we start with one preloaded half-words In h0.

     add    a0, %[time_base], h0, lsl #28     @ Add delay to time-base
     add    a0, wp, a0, ror #19
     ldrh   h1, %[wp], #2                     @ Load a half word synapse
     ldrh   w0, [a0]                          @ Load ring-buffer weight
>
     add    a1, %[time_base], h1, lsl #28     @ Add delay to time-base
     add    a1, wp, a1, ror #19
     ldrh   HH, %[wp], #2                     @ Load a half word synapse
     ldrh   w1, [a1]                          @ Load ring-buffer weight
     subs   w0, w0, h0, lsr #4                @ 'add' weight
     strplh w0, [a0]                          @ Conditionally store ring-element
     subs   w1, w1, h1, lsr #4                @ 'add' weight
     strplh w1, [a1]                          @ Conditionally store ring-element

Trial 4

     @ Assume h0 pre-loaded
     @----------------------   

     add    a0, %[time_base], h0, lsl #28     @ S0 Add delay to time-base
     add    a0, wp, a0, ror #19               @ S0
     ldrh   h1, %[wp], #2                     @ S1 Load a half word synapse
>
     ldrh   w0, [a0]                          @ S0 Load ring-buffer weight
     add    a1, %[time_base], h1, lsl #28     @ S1 Add delay to time-base
     add    a1, wp, a1, ror #19               @ S1
     ldrh   w1, [a1]                          @ S1 Load ring-buffer weight
     subs   w0, w0, h0, lsr #4                @ S0 'add' weight
     strplh w0, [a0]                          @ S0 Conditionally store ring-element
     ldrh   h0, %[wp], #2                     @ S0 Load a half word synapse

     subpls w1, w1, h1, lsr #4                @ S1 'add' weight
     strplh w1, [a1]                          @ S1 Conditionally store ring-element


Trial 5 This might just work!!!! Needs topping and tailing!!

h0, h1 pre-loaded. wp pointing at next h0,h1 pair

     add    a0, %[time_base], h0, lsl #28     @ S0 Add delay to time-base
     add    a0, wp, a0, ror #19               @ S0
     ldrh   w0, [a0, #-4]                     @ S0 Load ring-buffer weight
>       add    a1, %[time_base], h1, lsl #28     @ S1 Add delay to time-base
>       add    a1, wp, a1, ror #19               @ S1
>       ldrh   w1, [a1, #-2]                     @ S1 Load ring-buffer weight
     subs   w0, w0, h0, lsr #4                @ S0 'add' weight
     strplh w0, [a0, #-4]                     @ S0 Conditionally store ring-element
     ldrh   h0, %[wp]                         @ S0 Load a half word synapse
>       subpls w1, w1, h1, lsr #4                @ S1 'add' weight
>       strplh w1, [a1, #-2]                     @ S1 Conditionally store ring-element
>       ldrh   h1, %[wp], #4                     @ S1 Load a half word synapse, with auto-increment



 */

/*


Obvious "fast" dispatch code is:

   // optional quad code
   //-----------------------
   subs    %[n], %[n], #0x8000                  @ subtract '1' from n
                                                @ N flag indicates QQQQQ = 0 (and n now = -0x8000)
   ldr     %[w], [%[wp]], #4                    @ Load next synapse
   bpl     __quad_loop                          @ Do any quad processing required.

   // primary dispatch code
   //-----------------------
   and     r0, %[mask_0x1c], %[w], lsr #10      @ Put dispatch offset into r0
   ldr     r0, [%[jump], r0]                    @ Calculate dispatch address
   and     %[n], %[w], #0xf8000                 @ Take opportunity to mask-out bits of n
   bx      r0                                   @ Dispatch

// suspect code is 15 cycles???

*/



//=============================================================================
//
// Dispatch is determined by the values in the "middle" byte of the synapse
// word w; i.e. bit 12-19. These are encoded as follows:
//
//                    w = .... .... .... QQQQ QSSX .... .... ....
// where:
//   .   represents "don't care";
//   Q   represents the number of "quads" or blocks of four synapses packed
//       into three words;
//   S   represents the number of additional unpacked synapses, that need to be
//       pocessed as well as the quads; and
//   X   represents the presence of an extension rowlet, who's descriptor is
//       in the word currently pointed to by wp.
//
// The dispatch routine jumps to the address in the jump table: jump [SSXZ];
// in addition the number of quads required has been masked off during the
// calculation of the Z bit, and stored in n, though they are at location 15-19.
//
//                    n = .... .... .... QQQQ Q... .... ....
//
// The Z bit (in bit 5) is 0 if n = 0, and is 1 otherwise.
//
// This dispatch routine ensures that we only make one jump for small rowlets
// with 1-3 synapses. For 4-127 synapses, we need to loop though the
// synapse_loop code.
//
// In the special case where ZSSX = 000. we will do a second stage look-up for
// other sorts of rowlets, after processing the extension.
//
// On jumping to the dispatch handler routines, we have the following register
// set.
//
//   r0     Holds the jump offset "ZS SX.." in bits 0-5.
//   r1     Holds the target address jumped to.
//   flags  Will be set according to the comparison "cmp w, #0", with w != 0.
//   n      Holds just the bits QQQQQ in their oiginal locations in w.
//
//=============================================================================

//! \brief A Code fragment to place a extension description word -- placed
//! immediately after the current word w -- into the correct delay buffer.
//!
//! It uses regsiters r0, r1, r2 as scratch, increments the synaptic word
//! pointer wp, and uses the constants in ctrl and time_base.
//!
//! This code has 7 instructions, and takes 9 cycles to execute.

#define rowlet_extension()						                                                   \
    do {asm volatile ("ldr   r2, [%[wp]], #4               @ Load the rowlet descriptor                              \n\t" \
		      "@ ----------------->                @ pipeline interlock here                                 \n\t" \
		      "add   r3, %[time_base], r2, lsl #21 @ Add current time to rowlet descriptor word              \n\t" \
		      "and   r3, %[mask_0x3c], r3, lsr #26 @ Mask out all but bits 2-5                               \n\t" \
		      "ldr   r1, [%[ctrl], r3]	           @ Load rowlet buffer pointer                              \n\t" \
		      "@ ----------------->                @ pipeline interlock here                                 \n\t" \
		      "str   r2, [r1], #4                  @ Store rowlet in buffer                                  \n\t" \
		      "str   r1, [%[ctrl], r3]	           @ Write-back the rowlet buffer pointer                    \n\t" \
		      : [wp] "+r" (wp)					                                                   \
		      : [time_base] "r" (time_base), [mask_0x3c] "r" (mask_0x3c), [ctrl] "r" (ctrl)                        \
		      : "memory");					                                                   \
    } while (false)

//! \brief This code fragment selects a jump destination after the original,
//! primary, dispatch drops through. Note it is still possible that the whole
//! word w is 0, or that the "middle byte" is indicating an extension row.
//!
//! For simplicity of explication, we'll use the 3 bits in locations [22:20]
//! of w for secondary dispatch. This also has the advantage that we know that
//! the seven bits below these bits are all 0, and therefore don't need masking
//! out (though the bits above _do_). When we enter this code the registers
//! will be in the following state:
//!
//!      r0 contains: .... .... .... .... .... .... ..00 0X..
//!	 w  contains: .... .... .222 0000 000X .... .... ....
//!
//! And, if the word w is non-zero -- and thus we haven't yet finished synapse
//! processing -- we can shift this into position.

#define secondary_dispatch()						                                                   \
    do {asm volatile ("@---------------------------------------------------------------------------------------------\n\t" \
		      "@ At this point w contains: .... .... 2222 0000 00EX .... .... ....         (. is don't care) \n\t" \
		      "@ and r1 contains:          .... .... .... .... .... .... ..00 EX..         (. is 0)          \n\t" \
		      "@---------------------------------------------------------------------------------------------\n\t" \
		      "ands   r2, %[mask_0x3c], %[w], lsr #18 @ Shift the bits '2222' into position, and masks       \n\t" \
		      "ldr    r0, [%[jump], -r2]              @ Use the four bits to offset for secondary dispatch   \n\t" \
		      "popeq  {pc}                            @ Return: end of rowlet processing if '2222' = 0       \n\t" \
		      "                                       @ We need to ensure only one of +/- register occurs    \n\t" \
		      "bx     r0                              @ If '2222' != 0, then jump                            \n\t" \
		      : [w] "+r" (w), [wp] "+r" (wp) : [jump] "r" (jump), [mask_0x3c] "r" (mask_0x3c) : "cc", "memory");   \
    } while (false)

//! \brief This is the primary dispatch code. It splits the "middle byte" into
//! three parts: a five bit QQQQQ part, representing the number of packed
//! quadruples of synapses ("quads" for short); a two bit SS part, representing
//! the number of singleton synapses; and a one bit X part indicating whether
//! an extension rowlet is present or not.
//!
//! If QQQQQ = 00000 _and_ SS = 00, then we have a special case (a rowlet with
//! no synapses is fairly useless), and we then do a secondary dispatch using
//! other bits within the header to select the secondary destination address.

//! \brief The following version of primary dispatch incorporates the "E" bit to indicate whether the row is excitatory
//! or (if the E-bit is 0, inhibitory). As before, the X-bit indicates that an extension is present. The two S bits
//! indicate 0-3 synapses; and the four Q-bits indicate 0-15 packed quadruple synapses -- with one exception: if the bits
//! QQQQSS are _all_ 0, then this indicates an secondary dispatch is required. The secondary dispatch can be used for
//! other sorts of synaptic row (plasticity, different packing schemes, etc, etc.) I suggest using bits 23-20 as the
//! dispatch offsets for secondary dispatch as this permits the use of a full byte at the top of w to hold some sort of
//! count.

#define primary_dispatch()						                                                 \
    do {asm volatile ("and    r1, %[mask_0x3c], %[w], lsr #10   @ Set r1 = ..SS EX..                               \n\t" \
		      "@-------------------------------------------------------------------------------------------\n\t" \
		      "@ At this point r0 contains: .... .... .... .... .... .... ..SS EX..                        \n\t" \
		      "@-------------------------------------------------------------------------------------------\n\t" \
		      "ldr    r0, [%[jump], r1]                 @ Set up 16-way primary dispatch jump address      \n\t" \
		      "and    %[n], %[mask_0x3c], %[w], lsr #14 @ Take opportunity to mask out n ..                \n\t" \
		      "bx     r0                                @ Take the primary jump unconditionally            \n\t" \
		      "@-------------------------------------------------------------------------------------------\n\t" \
		      "@ At this point   r1 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)         \n\t" \
		      "@                 n  contains: .... .... .... .... .... .... ..QQ QQ..     (. is 0)         \n\t" \
		      "@-------------------------------------------------------------------------------------------\n\t" \
		      : [n] "+r" (n) : [mask_0x3c] "r" (mask_0x3c), [jump] "r" (jump), [w] "r" (w) : "cc", "memory");    \
    } while (false)    

#define PRIMARY_DISPATCH_SIZE 4
#define FIRST_DISPATCH_OFFSET (PRIMARY_DISPATCH_SIZE*4)

#define first_dispatch_and_return()						                                        \
    do {asm volatile ("add  r0, pc, %[OFF]             @ Push a return address pointing to the next instruction ..\n\t" \
		      "                                @   .. after the branch in primary_dispatch                \n\t" \
		      "push {r0}                       @ The link register (lr) can now be re-purposed during     \n\t" \
		      "                                @   .. rowlet processing, as needed.                       \n\t" \
		      : "+r" (wp), "+r" (w), "+r" (n) : [OFF] "J" (FIRST_DISPATCH_OFFSET) : "cc", "memory");            \
        primary_dispatch ();						                                                \
    } while (false)    

//! \brief This code fragment sets the value of n to control the packed
//! quadruple synapse processing loop. Since we also need to use this value to
//! offset into the synaptic processing loop, we chose to align QQQQQ as a word
//! offset (bottom two bits being 00).
//!
//! As on entry n has the value   .... .... .... QQQQ Q... .... .... ....
//! (with all . values being 0)
//! a left shift of 13 gives:     0000 0000 0000 0... .... .... .QQQ QQ00
//!
//! We then subtract "1" from QQQQQ (actually a 4, because of the location
//! within the word.
//!
//! Note we are using the double-entry table approach, and also that QQQQQ !=0.

#define quad_setup_and_dispatch()                                                                                          \
    do {asm volatile ("ldr  r0, [%[ctrl], -%[n]]              @ Need to ensure a negative index never collides with  \n\t" \
		      "                                       @   a positive one. Calculate the jump address         \n\t" \
		      "subs %[n], %[n], #4                    @ subtract '1' from n for loop counter, and only       \n\t" \
		      "bxpl r0                                @   __branch__ to the looping process if Q>0           \n\t" \
		      "                                       @   or fall through, if there are no quads to process  \n\t" \
		      : [n] "+r" (n) : [ctrl] "r" (ctrl) : "memory");	                                                   \
    } while (false)

#define quad_or_secondary_dispatch()                                                                                       \
    do {asm volatile ("@---------------------------------------------------------------------------------------------\n\t" \
		      "@ At this point w contains: .... .... 2222 QQQQ 00EX .... .... ....         (. is don't care) \n\t" \
		      "@     r0 contains:          .... .... .... .... .... .... ..00 EX..         (. is 0)          \n\t" \
		      "@ and n  contains:          .... .... .... .... .... .... ..QQ QQ..         (. is 0)          \n\t" \
		      "@---------------------------------------------------------------------------------------------\n\t" \
		      "ldr   r0, [%[ctrl], -%[n]]             @ Need to ensure a negative index never collides with  \n\t" \
		      "                                       @   a positive one. Calculate the jump address         \n\t" \
		      "subs  %[n], %[n], #4                   @ subtract '1' from n for loop counter, and test       \n\t" \
		      "ldrpl %[w], [%[wp]], #4                @ pre-load next synaptic word, for quad-processing     \n\t" \
		      "bxpl  r0                               @ __branch__ to the looping process if Q > 0           \n\t" \
		      "                                       @   or fall through, if there are no quads to process  \n\t" \
		      : [w] "+r" (w), [wp] "+r" (wp), [n] "+r" (n) : [ctrl] "r" (ctrl) : "memory");                        \
    } while (false)

#define big_fixed_redispatch()						                                                   \
    do {asm volatile ("@---------------------------------------------------------------------------------------------\n\t" \
		      "@ At this point w contains: .... .... 0001 0000 00EX .... .QQQ QQSS         (. is don't care) \n\t" \
		      "@---------------------------------------------------------------------------------------------\n\t" \
		      "and   r0, %[mask_0x3c], %[w], lsl #4   @ r0 now holds .... ..SS 00..                          \n\t" \
		      "orr   r1, r1, r0                       @ r1 now holds .... ..SS EX..                          \n\t" \
		      "ldr   r0, [%[jump], r1]                @ Set up 16-way primary dispatch jump address          \n\t" \
		      "and   %[n], %[w], #0x7c                @ And out value of n                                   \n\t" \
		      "ldr   %[w], [%[wp]], #4                @ Pre-load next synaptic word                          \n\t" \
		      "bx    r0                               @ Take the primary jump unconditionally                \n\t" \
		      : [n] "=r" (n), [w] "+r" (w), [wp] "+r" (wp)	                                                   \
		      :  [mask_0x3c] "r" (mask_0x3c), [jump] "r" (jump)	                                                   \
		      : "memory");					                                                   \
        } while (false)

#define set_excitatory_time_base()					                                                   \
    do {asm volatile ("orr %[time_base], %[time_base], #0x1   @ Set bit 0 of time-base                               \n\t" \
		    : [time_base] "+r" (time_base)); } while (false)

#define set_inhibitory_time_base()					                                                   \
    do {asm volatile ("bic %[time_base], %[time_base], #0x1   @ Clear bit 0 of time-base                             \n\t" \
		    : [time_base] "+r" (time_base)); } while (false)

#define excitatory_bit_orr_time_base()					                                      \
  do {asm volatile ("and r0, %[w], #0x2000                          @ Get excitatory bit from word 'w'  \n\t" \
		    "orr %[time_base], %[time_base], r0, lsr #13    @  .. and or it in                  \n\t" \
		    : [time_base] "+r" (time_base) : [w] "r" (w));	                                      \
  } while (false)

#define loop_decrement_and_test()					                                      \
  do {asm volatile ("subs %[n], %[n], #16    @ decrement and test the 'loop counter'                    \n\t" \
		    "                        @   (actually the number of synapses to be processed -1)   \n\t" \
		    "bpl  packed_quad_loop   @ If the number is still positive then loop again          \n\t" \
		    : [n] "+r" (n) : : "cc");				                                      \
  } while (false)

//! \brief Pre-process the value of n, the number of packed-quads to be processed.
//!
//! Initially, 

//! \brief The following code fragment consists of the loop body -- with four copies of
//! the packed-quad synapse processing macros, giving a total of 16 synaptic events
//! if the entire loop is executed.
//!
//! It is entered via the synapse jump table at the start of one of the four
//! packed_quad () macros. The number of iterations performed depends on the
//! value of register n. The number of loops performed is then:
//!
//!       $\lfloor (n/16) \rfloor$.
//!
//! Thus, if on entry $n = 31$, one additional loop is executed in addition to
//! the number of quads determined by the entry point. This allows us to
//! enter the code with n set to the full number of synapses to be processed,
//! and we don't need to mask off the low-order bits of n to get the right
//! answer.

//! It checks whether a DMA is required, and it decides whether there is a next
//! rowlet or not, either jumping to primary_dispatch for the next rowlet, or
//! returning otherwise.

void packed_quad_loop (void)
{
    ROWLET_REGISTER_MAP;

    packed_quad (); packed_quad (); packed_quad (); packed_quad ();

    feed_dma_if_needed ();
    loop_decrement_and_test ();
    primary_dispatch ();
}

void primary_dispatch_0I (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_inhibitory_time_base ();
    quad_or_secondary_dispatch (); 
    secondary_dispatch ();
}

void primary_dispatch_1I (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_inhibitory_time_base ();
    synapse_1 ();
    quad_setup_and_dispatch ();
    primary_dispatch ();
}

void primary_dispatch_2I (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_inhibitory_time_base ();
    synapse_2 ();
    quad_setup_and_dispatch ();
    primary_dispatch ();
}

void primary_dispatch_3I (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_inhibitory_time_base ();
    synapse_3 ();
    quad_setup_and_dispatch ();
    primary_dispatch ();
}
void primary_dispatch_0E (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_excitatory_time_base ();
    quad_or_secondary_dispatch ();
    secondary_dispatch ();
}

void primary_dispatch_1E (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_excitatory_time_base();
    synapse_1 ();
    quad_setup_and_dispatch();
    primary_dispatch ();
}

void primary_dispatch_2E (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_excitatory_time_base ();
    synapse_2 ();
    quad_setup_and_dispatch ();
    primary_dispatch ();
}

void primary_dispatch_3E (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_excitatory_time_base ();
    synapse_3 ();
    quad_setup_and_dispatch ();
    primary_dispatch ();
}

//! \brief Since the current small fixed rowlets can only handle up to 1-63
//! synapses, we use one of the fifteen secondary dispatches to handle the
//! case of a fixed rowlet with more than 63 synapses. The upper limit is
//! determined by the fact that a rowlet descriptor word can only handle up to
//! 128 words. So we need to leave one word for the header, and an optional one
//! for an extension.
//!
//! On entry to this routine we have the following situation:
//!
//!   w  contains: .... .... 0001 0000 00EX .... .... ....  (. is don't care)
//!   r1 contains: .... .... .... .... .... .... ..00 EX..  (. is 0)
//!   r2 contains: .... .... .... .... .... .... ..00 01..  (. is 0)
//!
//! So we are going to use the bottom seven bits of w to hold the number of synapses.

void secondary_dispatch_big_fixed (void)
{
    ROWLET_REGISTER_MAP;

    big_fixed_redispatch ();
}

//! \brief Plastic Synapse

//! Notice that we have to manually perform the extension check and the
//! excitatory/inhibitory check, since they are no longer part of the jump
//! table. Nevertheless, it should be a minimal part of what will inevitably
//! be quite a large chunk computation.

void secondary_dispatch_plastic1 (void)
{
    ROWLET_REGISTER_MAP;

    if (w & 0x1000)
        rowlet_extension ();

    excitatory_bit_orr_time_base ();


}

//==============================================================================
//! We also assume that we __branch__ into this code fragment, we do __not__
//! come here via a branch-and-link!
//!
//! We assume on entry that there is a "synaptic word", w, in the w register,
//! and that this register is non-zero. Furthermore wp points to the next word
//! in the synaptic buffer after w.
//!
//! The bits of w of interest at this level of dispatch are:
//!
//!         .... .... .... QQQQ QSSX .... .... ....
//!
//! If T is 0, then we have a standard "small" rowlet. The singletons (0-3) are coded by SS;
//! X is the extension bit; and QQQQ codes for (0-15) packed quad synapses. One other feature:
//! if all the bits QQQQSS.T are 0, then this indicates a "long" rowlet.
//!
//! If T is 1, then we have one of the other sort of rowlets, though X is still treated as
//! the extension bit.

//! If all of these eight bits are 0, then this is a standard long rowlet without extension.
//! If bit 16 of w is set, then there is an extension word immediately following w, which is in
//! the standard rowlet descriptor format (21 bits SDRAM address, 4 bits delay, 7 bits size-1).
//!
//! If at least one bit is non-zero, this code fragment will jump to the address in dispatch_table[JJ],
//! either after processing the extension, or immediately if there is no extension.
//!
//! But it also looks for a rowlet extension if bit 12 is set. In this case
//! we still dispatch using the current word, but we advance the pointer to
//! the next synapse by one word, to account for the space used by the
//! extension.
//!
//! We do the extension-check here, since this hides the table lookup cost.
//!
//! Expected execution time: 8 cycles with no extension to get to jump destination, 17 cycles to process extention.

void rowlet_dispatch (void) __attribute__ ((noinline, naked));
void rowlet_dispatch (void)
{  
    ROWLET_REGISTER_MAP;

    primary_dispatch ();
}

//! \brief This function is the primary one to be used within the overall
//! assembly program. It assumes that any registers required afterwards are
//! stacked; i.e. that we have a callee-saves protocol. It furthermore assumes
//! that the rowlet word pointer (wp) is correctly assigned to the beginning of
//! the area of rowlets that need processing. At the end, it will leave the
//! register wp pointing (just after???) the end of the processed rowlets.
//!
//! For the moment, we'll also assume that the control pointer is also
//! correctly set.

void process_rowlets (void) __attribute__ ((noinline, naked));
void process_rowlets (void)
{
    ROWLET_REGISTER_MAP;

    set_rowlet_registers_from_control ();
    start_timer ();
    first_dispatch_and_return ();
    stop_timer ();

}

//! \brief A C wrapper for testing the lower-level routines. It performs the register set-up required.
//!
//! When processing the rowlet buffer in anger it is expected that a full restoration of the registers
//! will not be needed. Thus don't use this routine, which takes 25+ cycles to stack and unstack __all__
//! potentially used registers, and to transfer control.

uint32_t* process_rowlets_from_C (uint32_t* __wp) __attribute__ ((noinline, naked));
uint32_t* process_rowlets_from_C (uint32_t* __wp)
{
    ROWLET_REGISTER_MAP;

    save_C_registers ();

    asm volatile ("mov   %[wp], r0                     @ Copy the start pointer into the correct register: wp     \n\t"
		  "ldr   %[w], [%[wp]], #4             @ Load first word into w, increment pointer wp             \n\t"
		  : [wp] "+r" (wp), [w] "=r" (w) : "r" (__wp));

    ctrl      = __control;
    jump      = (uint32_t*)(__control[DISPATCH_TABLE >> 2]);
    time_base = __control[TIME_BASE >> 2];
    mask_0x3c = 0x3c;
    mask      = mask_0x3c >> 1;
    //initialise_control ();
    
    //set_rowlet_registers_from_control ();

    USE_ROWLET_REGISTERS ();

    start_timer ();
    first_dispatch_and_return ();
    stop_timer ();

    // From here, the dispatch and return via pop {pc} takes 18 cycles.
    // Dispatch and return via another rowlet_dispatch takes 28 cycles.
    // A single synapse takes                                36 cycles (might be improvable)
    // Two single synapses                                   56 cycles

    asm volatile ("mov  r0, %[wp]                      @ Set up return value (current value of wp)                \n\t"
		  : : [wp] "r" (wp));

    restore_C_registers_and_return ();
}

// Data management plan required.
// Austria: Vienna 4-6 December. Whole HBP.

//! spike to master-pop lookup.
//!
//! needed only when [r0] != [r0, #8]

void c_main (void)
{
    uint32_t  w, w1, w2, w3, h, q1, q2 ,q3;
    uint32_t* wp;
    uint32_t* initial_wp;

    initialise_timer ();
    initialise_ring_buffers ();

    print_jump_tables ();
    print_synapse_jump_table ();
    print_ring_buffers ();
    zero_dma_buffers ();

    //h  = (0x08 << 12); // indicates a single quad
    h  = (0x1 << 20) | 0x4; // indicates 1 quads
    q1 = (11 << 20) | (0x3 << 12) | (0x1);
    q2 = (22 << 20) | (0x4 << 12) | (0x2);
    q3 = (44 << 20) | (33 << 4);

    w    =  (11 << 20) | (0x2 << 12) | (0x1 << 8);
    w1   =  (11 << 20) | (0x3 << 12) | (0x1 << 8);
    w2   =  (22 << 20) | (0x4 << 12) | (0x2 << 8);
    w3   =  (44 << 20) | (33 << 4);

    dma_buffer1[0] = h ;
    dma_buffer1[1] = q1;
    dma_buffer1[2] = q2;
    dma_buffer1[3] = q3;
    dma_buffer1[4] = 0; //(55 << 20) | (0x16 << 12) | (5); // excitatory
    dma_buffer1[5] = q1;
    dma_buffer1[6] = q2;
    dma_buffer1[7] = q3;
    dma_buffer1[8] = (66 << 20) | (0x06 << 12) | (6);
    dma_buffer1[9] = 0;
    dma_buffer1[10] = q1;
    dma_buffer1[11] = q2;
    dma_buffer1[12] = w;
    
    dma_buffer1[13] = 0;
    dma_buffer1[14] = w2;
    dma_buffer1[15] = w3;
    dma_buffer1[16] = w1;

    translate_tmp ();
    //printx (dma_buffer0[0]);
    //printx (dma_buffer0[1]);
    
    //print_dma_buffers ();

    initial_wp = dma_buffer0;
    wp = initial_wp;
    
    //start_timer ();
    //dense_256 ();
    //stop_timer ();
    asm volatile ("@\n\t" : "+r" (wp) : : "cc");
    wp = process_rowlets_from_C (wp);
    asm volatile ("@\n\t" : "+r" (wp) : : "cc");
    //stop_timer ();

    print_ring_buffers ();

    io_printf (IO_BUF, "Total time taken to process rowlet buffer is: = %u cycles\n", time);
    io_printf (IO_BUF, "The number of words processed is: %u (initial %08x, final: %08x)\n",
	       ((uint32_t)wp - (uint32_t)initial_wp) >> 2, (uint32_t)initial_wp, (uint32_t)wp);
    io_printf (IO_BUF, "The number of synapses is %u, the number of rowlets is: %u\n", __synapses, __rowlets);

    
    
    //  23 cycles for a dispatch that just pops the return address
    //  43 cycles for a dispatch that handles a single neuron.      (+20 cycles)
    //  63 cycles for 2 singletons                                  (+20 cycles)
    //  83 cycles for 3 singletons                                  (+20 cycles)
    // 103 cycles for 4 singletons                                  (+20 cycles)

    //  47 cycles for 1 doubleton                                   (+24 cycles)
    //  71 cycles for 2 doubletons                                  (+24 cycles)

    //  55 cycles for 1 tripleton                                   (+32 cycles)
    //  87 cycles for 2 tripletons                                  (+32 cycles)

    //  79 cycles for a quad                                        (+54 cycles)
    // 131 cycles for 2 quads                                       (+52 cycles)
    
    // 100 cycles for extended quad. Thus +21 cycles for extra jumps
    
    //print_ring_buffers ();

}
