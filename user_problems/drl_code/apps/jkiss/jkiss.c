/*
  A fast poisson PRNG.
*/

#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"
#include "random.h"

uint32_t time;

void     initialise_timer (void)      __attribute__ ((noinline));
void     start_timer      (void)      __attribute__ ((noinline));
void     stop_timer       (void)      __attribute__ ((noinline));

void initialise_timer (void)
{
    register uint32_t* timer_addr = (uint32_t*)(0x21000000);

    timer_addr[0] = (uint32_t)(-1);
    timer_addr[2] = 0xC2;

}

void start_timer (void)
{
    register uint32_t* timer_addr = (uint32_t*)(0x21000000);
    register uint32_t t;

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

//! \brief A non-disturbing hex printer. Has no _overall_ effect on any
//! registers apart from r0 (used to pass argument, and even that is restored),
//! since any that are affected by the print, are stacked and then unstacked at
//! the end.
//!
//! \param[in] x The unsigned integer to be printed

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


//! \brief Marsaglia's JKISS-64 in a ready-to-pick-up/ready-to-put-down form.
//!
//! \param sp  A pointer to the state variables, including constants.
//! \param hp  A pointer to the head of the random number (circular) buffer.
//! \param tp  A pointer to the tail of the random number (circular) buffer.

#define RANDOM_BUFFER_SIZE 256

static uint32_t random[RANDOM_BUFFER_SIZE]; // Random Number Buffer
static uint32_t state[] = {123456789, 987654321, 43219876,     6543217,
			   314527869,   1234567, 4294584393ULL};

uint32_t* random_head = random;
uint32_t* random_tail = random;

//! \brief The __load_jkiss64_state routine, loads the registers needed by the
//! jkiss64 routine.
//!
//! \param[in] sp  A pointer to the Random Number State
//! \param     r4  State variable x
//! \param     r5  State variable y
//! \param     r6  State variable z
//! \param     r7  State variable c
//! \param[in] r8  Constant 314527869
//! \param[in] r9  Constant 1234567
//! \param[in] r10 Constant 4294584393ULL

void __load_jkiss64_state (uint32_t* sp)
{   asm volatile ("ldm %[sp], {r4-r10}\n\t" : : [sp] "r" (sp) : "memory"); }

//! \brief The __flush_jkiss64_state routine, flushes the registers needed by
//! the jkiss64 routine, back to memory. Note there is no need to flush the
//! constants.
//!
//! \param[in] sp  A pointer to the Random Number State
//! \param     r4  State variable x
//! \param     r5  State variable y
//! \param     r6  State variable z
//! \param     r7  State variable c

void __flush_jkiss64_state (uint32_t* sp)
{   asm volatile ("stm %[sp], {r4-r7}\n\t" : : [sp] "r" (sp) : "memory"); }

//! \brief The __fast_jkiss64 routine, assumes that the seed/state and
//! constants are all pre-loaded, and that it can maintain the state in
//! registers between calls. If this is the case, then the following code takes
//! just 13 cycles to store the next 32-bit PRNG into memory.
//!
//! \param[in] n   Number of random numbers required
//! \param[in] rp  Pointer for the random number array
//! \param     r4  State variable x
//! \param     r5  State variable y
//! \param     r6  State variable z
//! \param     r7  State variable c
//! \param[in] r8  Constant 314527869
//! \param[in] r9  Constant 1234567
//! \param[in] r10 Constant 4294584393ULL

#define __jkiss64_asm()						\
    do {asm volatile ("mla   r4, r8, r4, r9\n\t"		\
		      "eor   r5, r5, r5, lsl #5\n\t"		\
		      "eor   r5, r5, r5, lsr #7\n\t"		\
		      "eor   r5, r5, r5, lsl #22\n\t"		\
		      "umull r6, ip, r10, r6\n\t"		\
		      "adds  r6, r6, r7\n\t"			\
		      "adc   r7, ip, #0\n\t"			\
		      "add   ip, r4, r5\n\t"			\
		      "add   ip, ip, r6\n\t"			\
		      "str   ip, [r0], #4\n\t"			\
		      : "+r" (rp):  : "cc", "memory");		\
    } while (false)

uint32_t* __fast_jkiss64 (uint32_t* rp, uint32_t* sp)
{
    __load_jkiss64_state (sp);  // Load registers with Seed State and Constants

    // Do a number of PRNG iterations...
    __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm ();
    __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm ();
    __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm ();
    __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm ();

    __flush_jkiss64_state (sp); // Flush Seed State back to State

    return (rp);                // Permits calculation of number of PRNGs
                                // created.
}

//! \brief The combined tables for a Poisson Distribution with lambda = 1.6
//! This includes (first part): the 8-bit values needed for the fast case;
//! (second part): the 32-bit comparison values to more accurately determine
//! small (< 6) return values; and (third part) an extended table for the tail.
//!
//! This will generate poisson values as if it had been fed with 40-bit PRNs.
//!
//! Arrgghh!! Note LSB is lowest in following table!!

uint32_t __fast_poisson_tables[]
   = {0x0A090807, 0x020D0C0B,  //7, 8, 9, A, B, C, D, 2,
      0x05050505, 0x04040404,  //5, 5, 5, 5, 4, 4, 4, 4,
      0x04040404, 0x04040404,  //4, 4, 4, 4, 4, 4, 4, 4,
      0x03030303, 0x03030303,  //3, 3, 3, 3, 3, 3, 3, 3,
      0x03030303, 0x03030303,  //3, 3, 3, 3, 3, 3, 3, 3,
      0x03030303, 0x03030303,  //3, 3, 3, 3, 3, 3, 3, 3,
      0x03030303, 0x03030303,  //3, 3, 3, 3, 3, 3, 3, 3,
      0x03030301, 0x01010101,  //3, 3, 3, 1, 1, 1, 1, 1,

      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,

      0x01010101, 0x01010101,  //1, 1, 1, 1, 1, 1, 1, 1,
      0x01010101, 0x01010101,  //1, 1, 1, 1, 1, 1, 1, 1,
      0x01010101, 0x01010101,  //1, 1, 1, 1, 1, 1, 1, 1,
      0x01010101, 0x01010101,  //1, 1, 1, 1, 1, 1, 1, 1,
      0x01010101, 0x01010101,  //1, 1, 1, 1, 1, 1, 1, 1,
      0x01010101, 0x01010101,  //1, 1, 1, 1, 1, 1, 1, 1,
      0x01010101, 0x01010101,  //1, 1, 1, 1, 1, 1, 1, 1,
      0x01010101, 0x01010101,  //1, 1, 1, 1, 1, 1, 1, 1,

      0x01010101, 0x01010101,  //1, 1, 1, 1, 1, 1, 1, 1,
      0x01010101, 0x00000001,  //1, 1, 1, 1, 1, 0, 0, 0,
      0x00000000, 0x00000000,  //0, 0, 0, 0, 0, 0, 0, 0,
      0x00000000, 0x00000000,  //0, 0, 0, 0, 0, 0, 0, 0,
      0x00000000, 0x00000000,  //0, 0, 0, 0, 0, 0, 0, 0,
      0x00000000, 0x00000000,  //0, 0, 0, 0, 0, 0, 0, 0,
      0x00000000, 0x00000000,  //0, 0, 0, 0, 0, 0, 0, 0,
      0x00000000, 0x00000000,  //0, 0, 0, 0, 0, 0, 0, 0

          // Special edge-case decisions:
      3427828353, //  0,1  test value; higher value selected if prn <= table no.
      2040406046, //  1,2  test value
      930468200,  //  2,3  test value
      338501349,  //  3,4  test value
      101714609,  //  4,5  test value
      25942852,   //  5,6  test value

          // First entry in extended table
      1468685039, //  6,7 test value
      286356976,  //  7,8 test value
      49891364,   //  8,9 test value
      7853033,    //  9,10 test value
      1126900,    // 10,11 test value
      148553,     // 11,12 test value
      18107,      // 12,13 test value
      2052,       // 13,14 test value
      217,        // 14,15 test value
      22,         // 15,16 test value
      2,          // 16,17 test value
      0};         //   ... Must be 17!

/*
-----------------------------------------
  register | name  | purpose
-----------------------------------------
   r0, r3  |       | scratch registers
    r4-r7  | v0-v3 | poisson values
     r8    | seven | constant 0x07000000
     r9    | prng  | random number stream
    r10    |  tab  | poisson table bases
    r11    |  out  | poisson output pointer
-----------------------------------------

    ldr    r3, [prng], #4            ; load scratch register r3 with random bits
    adds   r0, seven, r3             ; add 6 to top byte
    ldrccb v0, [tab, r0, lsr #24]    ; fill-in v0 in standard case
    blcs   <L_poisson>               ; sub-routine if value in r0 < 7 * 2^24
    adds   r0, seven, r3, ror #8
    ldrccb v1, [tab, r0, lsr #24]
    blcs   <L_poisson>
    adds   r0, seven, r3, ror #16
    ldrccb v2, [tab, r0, lsr #24]
    blcs   <L_poisson>
    adds   r0, seven, r3, ror #24
    ldrccb v3, [tab, r0, lsr #24]
    blcs   <L_poisson>
    orr    v0, v1, v0, lsl #16
    str    v0, [out], #4
    orr    v2, v3, v2, lsl #16
    str    v2, [out], #4

   Corrections needed above: total = still 17 instructions,
   but 22 cycles. Reason: each ldrb is a shift-offset, thus 2 cycles,
   and initial prng load is adjacent to adds. Thus average = 5.5 cycles per
   poisson (+ rare case [p = (7 / 256)] for sub-routines, not encountered
   so far)

New 4-byte version:

   ldrb   r0, [%[prng]], #1        @ load random byte
   ldrb   r1, [%[prng]], #1        @ load random byte
   ldrb   r2, [%[prng]], #1        @ load random byte
   ldrb   r3, [%[prng]], #1        @ load random byte
   subs   r0, r0, #7               @ subtract 7, to deal with special cases
   ldrb   r0, [%[table], r0]       @ look-up 8-bit poisson
   ldrmib r0, [%[poisson]], #1     @ alternatively use 40-bit version.
   subs   r1, r1, #7               @ subtract 7, to deal with special cases
   ldrb   r1, [%[table], r1]       @ look-up 8-bit poisson
   ldrmib r1, [%[poisson]], #1     @ alternatively use 40-bit version.
   subs   r2, r2, #7               @ subtract 7, to deal with special cases
   ldrb   r2, [%[table], r0]       @ look-up 8-bit poisson
   ldrmib r2, [%[poisson]], #1     @ alternatively use 40-bit version.
   subs   r3, r3, #7               @ subtract 7, to deal with special cases
   ldrb   r3, [%[table], r3]       @ look-up 8-bit poisson
   ldrmib r3, [%[poisson]], #1     @ alternatively use 40-bit version.
   strb   r0, [%[p_out]], #1       @ store poisson value in buffer
   strb   r1, [%[p_out]], #1       @ store poisson value in buffer
   strb   r2, [%[p_out]], #1       @ store poisson value in buffer
   strb   r3, [%[p_out]], #1       @ store poisson value in buffer

Takes 5 cycles per poisson (+ a few more for rare cases)
Can get it down to 4.25 if needed (which it is), by using same trick as synapse

Even newer 4-byte version:

   ldrb   r0, [%[prng]], #1        @ load random byte
   ldrb   r1, [%[prng]], #1        @ load random byte
   ldrb   r2, [%[prng]], #1        @ load random byte
   ldrb   r3, [%[prng]], #1        @ load random byte
   subs   r0, r0, #7               @ subtract 7, to deal with special cases
   ldrplb r4, [%[table], r0]       @ look-up 8-bit poisson
   subpls r1, r1, #7               @ subtract 7, to deal with special cases
   ldrplb r5, [%[table], r1]       @ look-up 8-bit poisson
   strb   r4, [%[p_out]], #1       @ store poisson value in buffer
   subpls r2, r2, #7               @ subtract 7, to deal with special cases
   ldrplb r4, [%[table], r2]       @ look-up 8-bit poisson
   subpls r3, r3, #7               @ subtract 7, to deal with special cases
   ldrplb r6, [%[table], r3]       @ look-up 8-bit poisson
   strb   r4, [%[p_out]], #1       @ store poisson value in buffer
   strb   r5, [%[p_out]], #1       @ store poisson value in buffer
   strb   r6, [%[p_out]], #1       @ store poisson value in buffer
   bmi    poisson_40_bit_fixup     @ Any problem so far: redo..

 */

#define __fast_poisson()						\
  do {									\
    asm volatile ("ldr    r3, [%[prng]], #4\n\t"	       		\
		  "adds   r0, %[seven], r3\n\t"				\
		  : "=r" (v0) : [prng] "r" (prng),			\
		    [seven] "r" (seven)	 : "cc", "memory");		\
    asm goto     ("blcs %l[L0]\n\t" : : : "memory" : L0);		\
    asm volatile ("ldrb   %[v0], [%[tab], r0, lsr #24]\n\t"		\
                  "adds   r0, %[seven], r3, ror #8\n\t"			\
		  : [v0] "=r" (v0) : [tab] "r" (tab),			\
		    [seven] "r" (seven)	 : "cc", "memory");		\
    asm goto     ("blcs %l[L1]\n\t" : : : "memory" : L1);		\
    asm volatile ("ldrb %[v1], [%[tab], r0, lsr #24]\n\t"		\
                  "adds   r0, %[seven], r3, ror #16\n\t"		\
		  : [v1] "=r" (v1) : [tab] "r" (tab),			\
		    [seven] "r" (seven) : "cc", "memory");		\
    asm goto     ("blcs %l[L2]\n\t" : : : "memory" : L2);		\
    asm volatile ("ldrb   %[v2], [%[tab], r0, lsr #24]\n\t"		\
                  "adds   r0, %[seven], r3, ror #24\n\t"		\
		  : [v2] "=r" (v2) : [tab] "r" (tab),			\
		    [seven] "r" (seven) : "cc", "memory");		\
    asm goto     ("blcs %l[L3]\n\t" : : : "memory" : L3);		\
    asm volatile ("ldrb %[v3], [%[tab], r0, lsr #24]\n\t"		\
		  "orr  %[v0], %[v1], %[v0], lsl #16\n\t"		\
		  "str  %[v0], [%[out]], #4\n\t"			\
		  "orr  %[v2], %[v3], %[v2], lsl #16\n\t"		\
		  "str  %[v2], [%[out]], #4\n\t"			\
		  : [v0] "+r" (v0), [v2] "+r" (v2), [out] "+r" (out)	\
		  : [v1]  "r" (v1), [v3]  "r" (v3), [tab]  "r" (tab)	\
		  : "memory");						\
  } while (false)

#define __fast_poisson_branch(rr)					\
  do {asm volatile ("add   lr, lr, #4\n\t"				\
		    "push  {lr}\n\t"					\
		    "ldr   r1, [%[prng]], #4\n\t"			\
		    "movs  r0, r0, lsr #24\n\t"				\
		    : [prng] "+r" (prng) : : "cc", "memory");		\
      asm goto     ("bleq  %l[L_zero]\n\t": : : "memory" : L_zero);	\
      asm volatile ("add   r2, %[tab], #252\n\t"			\
		    "ldr   r2, [r2, r0, lsl #2]\n\t"			\
		    "cmp   r2, r1\n\t"					\
		    "adc   "/**/rr/**/", r0, #-1\n\t"			\
		    "pop    {pc}\n\t"					\
		    : : [tab] "r" (tab) : "cc", "memory");		\
  } while (false)


    // 1 Paris doc workshop
// 2 book work to be checked in 2 weeks
    // 3 Open invitations to "outsiders"

typedef struct {uint32_t** prng; // pointer to the prng buffer
                uint32_t*  tab;  // pointer to the poisson table
                uint32_t** out;  // pointer to the output buffer
               } poisson_state_t, *poisson_state_ptr;

poisson_state_t poisson_state;

//! \brief The __load_poisson_state routine, loads the registers needed by the
//! poisson routine.
//!
//! \param[in] sp  A pointer to the Random Number State
//! \param     r4  State variable x
//! \param     r5  State variable y
//! \param     r6  State variable z
//! \param     r7  State variable c
//! \param[in] r8  Constant 314527869
//! \param[in] r9  Constant 1234567
//! \param[in] r10 Constant 4294584393ULL

//void __load_poisson_state (poisson_state_ptr) __attribute__ ((noinline, naked));
void __load_poisson_state (void)
{
    asm volatile ("mov  r9,  r0\n\t"
		  "mov r11,  r1\n\t"
		  "mov r10,  r2\n\t"
		  "mov  r8,  #0x07000000\n\t"
		  : :  : "memory");
}
//! \brief The __flush_poisson_state routine, flushes the registers needed by
//! the poisson routine, back to memory. Note there is no need to flush the
//! constants.
//!
//! \param[in] sp  A pointer to the Random Number State
//! \param     r4  State variable x
//! \param     r5  State variable y
//! \param     r6  State variable z
//! \param     r7  State variable c

void __flush_poisson_state (void)
{
    asm volatile ("mov  r0, r9\n\t"
		  "mov  r1, r11\n\t"
		  : : : "memory");
}

void fast_poisson (uint32_t* __prng, uint32_t* __out, uint32_t* __tab)
                                  __attribute__ ((noinline, naked));
void fast_poisson (uint32_t* __prng, uint32_t* __out, uint32_t* __tab)
{
    __label__ L0, L1, L2, L3, L_zero, Loop;
    /*register uint32_t  r0    asm ("r0");
    register uint32_t  r1    asm ("r1");
    register uint32_t  r2    asm ("r2");
    register uint32_t  r3    asm ("r3");*/
    register uint32_t  v0    asm ("r4");
    register uint32_t  v1    asm ("r5");
    register uint32_t  v2    asm ("r6");
    register uint32_t  v3    asm ("r7");
    register uint32_t  seven asm ("r8");
    register uint32_t* prng  asm ("r9");
    register uint32_t* tab   asm ("r10");
    register uint32_t* out   asm ("r11");
    //register uint32_t  ip    asm ("ip");

    asm volatile ("push {r4-r12, lr}\n\t"
		  : [prng] "=r" (prng)
		  : "r" (__prng), "r" (__out), "r" (__tab)
		  : "memory");

    __load_poisson_state ();

    start_timer ();
    __fast_poisson (); __fast_poisson (); __fast_poisson (); __fast_poisson ();
    stop_timer ();

    __flush_poisson_state ();
    printx ((uint32_t)prng);

    asm volatile ("pop {r4-r12, pc}\n\t" : : : "memory");

L0:
    __fast_poisson_branch ("r4");
L1:
    __fast_poisson_branch ("r5");
L2:
    __fast_poisson_branch ("r6");
L3:
    __fast_poisson_branch ("r7");

L_zero:
    // On entry new random number is in r1.
    asm volatile ("add lr, lr, #12\n\t"
		  "add r2, %[tab], #256\n\t"
		  "mov r0, #6\n\t" : : [tab] "r" (tab) : "memory");
Loop:
    asm volatile ("ldr   ip, [r2, r0, lsl #2]\n\t"
		  "cmp   r1, ip\n\t"
		  "bxhs  lr\n\t"
		  "add   r0, r0, #1\n\t"
		  "ldr   ip, [r2, r0, lsl #2]\n\t"
		  "cmp   r1, ip\n\t"
		  "bxhs  lr\n\t"
		  "add   r0, r0, #1\n\t"
		  "ldr   ip, [r2, r0, lsl #2]\n\t"
		  "cmp   r1, ip\n\t"
		  "bxhs  lr\n\t"
		  "add   r0, r0, #1\n\t"
		  "ldr   ip, [r2, r0, lsl #2]\n\t"
		  "cmp   r1, ip\n\t"
		  "bxhs  lr\n\t"
		  "add   r0, r0, #1\n\t"
		  : : : "cc", "memory");

    asm goto     ("b %l[Loop]\n\t" : : : : Loop);
}

void c_main (void)
{
    uint32_t  randoms [12];
    uint32_t  poissons[8];
    uint32_t* prng = randoms;
    register uint32_t* out  = poissons;
    register uint32_t i;

    initialise_timer();

    start_timer ();
    (void)__fast_jkiss64 (prng,   state);
    /*(void)__fast_jkiss64 (prng+4, state);
      (void)__fast_jkiss64 (prng+8, state);*/
    stop_timer ();

    io_printf (IO_BUF, "16 32-bit random numbers generated in %u cycles\n",
    	       time);



    io_printf (IO_BUF, " randoms = {");
    for (i = 0; i < 8; i++) {
        io_printf (IO_BUF, "%x", randoms [i]);
	if (i == 3)
	    io_printf (IO_BUF, ",\n");
	else if (i == 7)
	    io_printf (IO_BUF, "}\n");
	else
	    io_printf (IO_BUF, ", ");
    }
    /*
    printx ((uint32_t)prng);
    prng = randoms;
    fast_poisson (prng, out, __fast_poisson_tables);

    //io_printf (IO_BUF, "\n randoms used = %u\n",
    //	       ((uint32_t)(random_head) - (uint32_t)(randoms)) >> 2);

    io_printf (IO_BUF, " out[0] = {%u, %u}\n",
	       poissons[0] & 0xffff, poissons[0] >> 16);
    io_printf (IO_BUF, " out[1] = {%u, %u}\n",
	       poissons[1] & 0xffff, poissons[1] >> 16);
    io_printf (IO_BUF, " out[2] = {%u, %u}\n",
	       poissons[2] & 0xffff, poissons[2] >> 16);
    io_printf (IO_BUF, " out[3] = {%u, %u}\n",
	       poissons[3] & 0xffff, poissons[3] >> 16);
    io_printf (IO_BUF, " out[4] = {%u, %u}\n",
	       poissons[4] & 0xffff, poissons[4] >> 16);
    io_printf (IO_BUF, " out[5] = {%u, %u}\n",
	       poissons[5] & 0xffff, poissons[5] >> 16);
    io_printf (IO_BUF, " out[6] = {%u, %u}\n",
	       poissons[6] & 0xffff, poissons[6] >> 16);
    io_printf (IO_BUF, " out[7] = {%u, %u}\n",
	       poissons[7] & 0xffff, poissons[7] >> 16);
	       io_printf (IO_BUF, "\n 16 poisson variables generated in %u cycles\n", time);*/
}
