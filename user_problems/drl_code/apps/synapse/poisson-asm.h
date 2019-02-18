/* poisson-asm.h


Hi,
 
Just thinking about this a bit...
 
I think the best option for this for now at least is to have this in a separate module.  This can then do what it wants internally, and can be used in code separately when appropriate (noting that it might not always be appropriate ;).  The API can still be similar to make the change easy enough if a user decides it is appropriate for their function.
 
On the issue of alignment, we could create a call to the spin1_malloc that allows things to be aligned.  This would mean that although a hole was created, it would at least be a reusable hole.  An alternative is to allow a variable in the linker script which controls the start position of the heap, the space before which would be usable as generic space by the user program.
 
For the Poisson with tables, I think the API would need to have an “initialise_poisson_table” and then a “generate_from_poisson_table” function (names don’t need to be these, they are just to give an idea of what the functions would do).  Ideally, the initialise function would return a pointer to a struct containing appropriate data, which is then passed in to the generate function for use; this then allows us to use multiple poisson tables.  Would that work?
 
Note that on the subject of the seed, I guess you might still want to include this in the argument list even in the buffered call.  The seed is the current RNG generating state, so this would still need to be used when the RNG is generating its next buffer.  It might remain at the same value for a number of calls of course.  An alternative is similar to above – have an initialise function for the RNG that returns a struct pointer that is then passed around as needed.

 */

//=============================================================================
// We define the register allocation suitable for the random number processing.
//=============================================================================

//! The key idea is to have a resevoir of pre-computed random numbers in a
//! buffer, from which we draw, and into which we periodically top-up.
//!
//! This buffer is the "random_buffer" which is allocated to an address that's
//! aligned on a 1K byte boundary. Doing this makes testing whether the buffer
//! is empty very efficient, as we shall see later.
//!
//! The buffer is consumed from the bottom upwards, and filling the buffer works
//! in the opposite direction -- on the same pointer -- by decrementing as new
//! random numbers are added.
//!
//! In assembly code this buffer pointer is "rp", and if the RANDOM_REGISTER_MAP
//! register assignment is in use, then "rp" is register r11. To ensure proper
//! interworking with "C", the register "rp" is saved into the control
//! structure, and can be operated on in "C" once the prointer is loaded. Don't
//! forget to save it back to the control structure!
//!
//! The critical advantage of taking this approach to random number allocation
//! is that once we have loaded the JKISS-64 state, and it's constants -- and
//! when we account for saving the state afterwards -- it makes a lot of sense
//! to create multiple random numbers at a time. The difference is stark: with
//! pre-loaded registers, JKISS-64 takes just 12 cycles to deliver the result
//! into register "r0" (the usual place for return values to be placed,
//! according to the ARM procedure call standard). This compares with 44 cycles
//! if we load and save these registers -- as we must, to preseve the PRNG's
//! state -- for the generation of a random number each time we call the
//! function to create a new random number.
//!
//! The C-level API is as follows:
//!
//!     uint32_t* load_random_pointer  (void)
//!     void      save_random_pointer  (uint32_t* rp)
//!     uint32_t  random_buffer_size   (uint32_t* rp)
//!     uint32_t* refill_random_buffer (uint32_t* rp)
//!     uint32_t  next_random          (void)
//!           [Actually a macro, since it has the side-effect of incrementing rp.]
//!
//! Within an assembler setting, we have the following similar, but not
//! identical, API:
//!
//!     __load_random_pointer   [Loads r11 (rp) to the random-pointer, saving previous contents of r11.]
//!     __save_random_pointer   [Saves r11 (rp), the random-pointer, restoring previous contents of r11.]
//!     __load_random_state     [Loads all variables and constants required to calculate a random number.
//!                              IMPORTANT: does not save previous values of registers.]
//!     __save_random_state     [Saves all variables required to calculate a random number.
//!                              IMPORTANT: does not restore previous values of registers.]
//!     __random_buffer_size    [returns size in r0, assuming register rp is set.]
//!     __refill_random_buffer  [Actually used underneath the C function. Affects register rp.]
//!     __next_random_unchecked [If we know that the buffer cannot be empty -- probably through the use of random_buffer_size --
//!                              we can short-cut the delivery of the next random number.]
//!     __next_random_checked   [Checks that the buffer is not empty. If it is, then it fills in a few values to keep us going.]

//! \brief This pseudo-instruction pretends to use the registers declared in
//! RANDOM_REGISTER_MAP. This alerts gcc to the fact that the register and flags
//! may change, and thus it should not rearrange code blocks.

#define USE_RANDOM_REGISTERS()						               \
  do {asm volatile ("@ spoof register use\n\t"\
		    : : "r" (n), "r" (x), "r" (y), "r" (z), "r" (c), "r" (k0), "r" (k1), "r" (k2), "r" (rp), "r" (ctrl) : "cc"); \
  } while (false)

//! \brief The following macro allows us to define _in_one_place_ the register
//! names and locations used by the various pieces of random manipulation code.
//!
//! It also hides a piece of non-code-generating code that "uses" all of these
//! registers, as most code fragments don't use _all_ the registers.
//!
//! It may be that omitting this "asm" statement becomes necessary later.

#define RANDOM_REGISTER_MAP                                                                   \
  register uint32_t* ctrl      asm ("r12"); /* control and constant access                 */ \
  register uint32_t* rp        asm ("r11"); /* Pointer to next random number               */ \
  register uint32_t  c         asm ("r10"); /* JKISS-64 state variable                     */ \
  register uint32_t  z         asm ("r9");  /* JKISS-64 state variable                     */ \
  register uint32_t  y         asm ("r8");  /* JKISS-64 state variable                     */ \
  register uint32_t  x         asm ("r7");  /* JKISS-64 state variable                     */ \
  register uint32_t  k2        asm ("r6");  /* Constant 4294584393ULL                      */ \
  register uint32_t  k1        asm ("r5");  /* Constant 1234567                            */ \
  register uint32_t  k0        asm ("r4");  /* Constant 314527869                          */ \
  register uint32_t  n         asm ("r2");  /* Register used to count the number of buffer entries, etc. */ \
                                                                                              \
  USE_RANDOM_REGISTERS()

//! \brief BUFFER_SIZE_MASK indicates the index bits used to index into the
//!random buffer. It is used to determine the size, and to test whether the
//! random buffer is empty.

#define BUFFER_SIZE_MASK 0x3fc

void __refill_random_buffer (void) asm ("__refill_random_buffer") __attribute__ ((noinline, naked));

//! \brief The __load_random_state routine, loads the registers needed by the
//! jkiss64 routine.
//!
//! \param[in] ctrl A pointer to the State Variables
//! \param     rp   A pointer to the next Random Number
//! \param     x    State variable x
//! \param     y    State variable y
//! \param     z    State variable z
//! \param     c    State variable c
//! \param     k0   Constant 314527869
//! \param     k1   Constant 1234567
//! \param     k2   Constant 4294584393ULL

#define __load_random_state()                                                                                         \
    do {asm volatile ("ldr r11, [%[ctrl], %[kiss_rp]]                 @ Load rp register from kiss rp location  \n\t" \
		      "ldr r10, [%[ctrl], %[kiss_c]]                  @ Load c  register from kiss c location   \n\t" \
		      "ldr r9,  [%[ctrl], %[kiss_z]]                  @ Load z  register from kiss z location   \n\t" \
		      "ldr r8,  [%[ctrl], %[kiss_y]]                  @ Load y  register from kiss y location   \n\t" \
		      "ldr r7,  [%[ctrl], %[kiss_x]]                  @ Load x  register from kiss x location   \n\t" \
		      "ldr r6,  [%[ctrl], %[kiss_k2]]                 @ Load k2 register from kiss k2 location  \n\t" \
		      "ldr r5,  [%[ctrl], %[kiss_k1]]                 @ Load k1 register from kiss k1 location  \n\t" \
		      "ldr r4,  [%[ctrl], %[kiss_k0]]                 @ Load k0 register from kiss k0 location  \n\t" \
		      :  : [ctrl] "r" (ctrl), [kiss_x] "J" (KISS_STATE_X), [kiss_y] "J" (KISS_STATE_Y),               \
			[kiss_z] "J" (KISS_STATE_Z), [kiss_c] "J" (KISS_STATE_C), [kiss_k0] "J" (KISS_STATE_K0),      \
			 [kiss_k1] "J" (KISS_STATE_K1), [kiss_k2] "J" (KISS_STATE_K2), [kiss_rp] "J" (KISS_STATE_RP)  \
		      : "memory");					                                              \
    } while (false)

//! \brief The __save_random_state routine, flushes the registers needed by
//! the JKISS-64 routine back to memory. Note there is no need to flush the
//! constants. Also note that we do not restore the previous values of the
//! registers used by the JKISS-64 routine.
//!
//! \param[in] ctrl A pointer to the State Variables
//! \param     rp   A pointer to the next Random Number
//! \param     x     State variable x
//! \param     y     State variable y
//! \param     z     State variable z
//! \param     c     State variable c

#define __save_random_state()                                                                                         \
    do {asm volatile ("str %[rp], [%[ctrl], %[kiss_rp]]                @ Save rp register in kiss rp location   \n\t" \
		      "str %[c],  [%[ctrl], %[kiss_c]]                 @ Save c register in kiss c location     \n\t" \
		      "str %[z],  [%[ctrl], %[kiss_z]]                 @ Save z register in kiss z location     \n\t" \
		      "str %[y],  [%[ctrl], %[kiss_y]]                 @ Save y register in kiss y location     \n\t" \
		      "str %[x],  [%[ctrl], %[kiss_x]]                 @ Save x register in kiss x location     \n\t" \
		      :                                                                                               \
		      : [ctrl] "r" (ctrl), [rp] "r" (rp), [x] "r" (x), [y] "r" (y), [z] "r" (z), [c] "r" (c),         \
			[kiss_x] "J" (KISS_STATE_X), [kiss_y] "J" (KISS_STATE_Y), [kiss_z] "J" (KISS_STATE_Z),        \
			[kiss_c] "J" (KISS_STATE_C), [kiss_rp] "J" (KISS_STATE_RP)			              \
		      : "memory"); 					                                              \
    } while (false)


//! \brief The __random_buffer_size routine, returns the current size of the
//! random buffer in register n.
//!
//! \param[in] rp  The random pointer
//! \param     n   The "number" register; returns a value in the range 0-256.

#define __random_buffer_size()                                                                                               \
    do {asm volatile ("ands  r0, %[rp], #0x3fc                      @ Mask out the current pointer index bits          \n\t" \
		      "addeq r0, r0, #4                             @ Adjust for zero -- equivalent to 256             \n\t" \
		      "lsrs  r0, #2                                 @ Index is in words, so right-shift 2              \n\t" \
		      "                                             @ Notice we set the Z flag if the buffer is empty  \n\t" \
		      "                                             @  .. (both addresses are the same)                \n\t" \
		      : [n] "=r" (n) : [rp] "r" (rp) : "memory"); 					                     \
    } while (false)

//! \brief The algorithm implemented is Marsaglia's JKISS-64.
//!
//! The __jkiss64_asm routine assumes that the seed/state and constants are
//! all pre-loaded, and that it can maintain the state in registers between
//! calls. If this is the case, then the following 9 instructions takes just
//! 11 cycles to calculate the next 32-bit PRNG in r0.
//!
//! \param[in] %[rp] Pointer for the random number array
//! \param     %[x]  State variable x
//! \param     %[y]  State variable y
//! \param     %[z]  State variable z
//! \param     %[c]  State variable c
//! \param[in] %[k0] Constant 314527869
//! \param[in] %[k1] Constant 1234567
//! \param[in] %[k2] Constant 4294584393ULL

#define __jkiss64_asm()                                                                                           \
    do {asm volatile ("mla   %[x], %[k0], %[x], %[k1]  @ x = 314527869*x + 1234567  (32-bit MLA)            \n\t" \
                      "eor   %[y], %[y], %[y], lsl #5  @ shifted x-or                                       \n\t" \
                      "eor   %[y], %[y], %[y], lsr #7  @ shifted x-or                                       \n\t" \
                      "eor   %[y], %[y], %[y], lsl #22 @ shifted x-or                                       \n\t" \
                      "umull %[z], r0, %[k2], %[z]     @ [z;r0] = 4294584393 * z    (64-bit unsigned mul)   \n\t" \
                      "adds  %[z], %[z], %[c]          @ 64-bit addition ...                                \n\t" \
                      "adc   %[c], r0, #0              @  ...                                               \n\t" \
                      "add   r0, %[x], %[y]            @ Accumulate output ...                              \n\t" \
                      "add   r0, r0, %[z]              @     ...                                            \n\t" \
                      : [x] "+r" (x), [y] "+r" (y), [z] "+r" (z), [c] "+r" (c), [rp] "+r" (rp)                    \
		      : [k0] "r" (k0), [k1] "r" (k1), [k2] "r" (k2) : "cc", "memory"); 	                          \
    } while (false)

//! \brief Loads a random number from the buffer, _and_ it is known that the
//! buffer is not empty.

#define __next_random_unchecked()							        \
    do {									                \
        asm volatile ("                                @ spoof      \n\t" : : "r" (rp) : "cc"); \
        asm volatile ("ldr   r0, [%[rp]], #4           @ load random number               \n\t"	\
		      : [rp] "+r" (rp) : : "memory");			                        \
    } while (false)

//! \brief Loads a random number from the buffer, _and_ it is not known whether
//! the buffer is empty or not. If the buffer _is_ empty, then a new random
//! number is created.

#define __next_random_checked()					                                                                    \
    do {									                                                    \
        asm volatile ("                                @ spoof                                          \n\t" : : "r" (rp) : "cc"); \
        asm volatile ("tst   %[rp], %[size_mask]       @ test for buffer overflow                                             \n\t" \
		      "ldrne r0, [%[rp]], #4           @ load random number, if available                                     \n\t" \
		      "blxeq __refill_random_buffer    @ A refill is required if the index bits are 0x00                      \n\t" \
		      : [rp] "+r" (rp) : [size_mask] "I" (BUFFER_SIZE_MASK) : "cc", "memory");                                      \
    } while (false)


#define __jkiss64_and_store()                                                                   \
    do {									                \
        __jkiss64_asm ();                                                                       \
	asm volatile ("str r0, [%[rp], #-4]!           @ Store new number into buffer     \n\t" \
		      : [rp] "+r" (rp) : : "memory");			                        \
    } while (false)

#define __jkiss64_loop_decrement_and_test()					                              \
  do {asm volatile ("subs %[n], %[n], #8     @ decrement and test the 'loop counter'                    \n\t" \
		    "                        @   (actually the number of synapses to be processed -1)   \n\t" \
		    "bpl  __jkiss64_loop     @ If the number is still positive then loop again          \n\t" \
		    : [n] "+r" (n) : : "cc");				                                      \
  } while (false)

#define __jkiss64_dispatch()				                                                      \
    do {asm volatile ("@---------------------------------------------------------------------------------------------\n\t" \
		      "@ At this point n contains: .... .... .... .... .... ...N NNNN NNNN         (. is 0)          \n\t" \
		      "@---------------------------------------------------------------------------------------------\n\t" \
		      "and   r0, %[n], #0x7                 @ mask out odd elements                                  \n\t" \
		      "add   r0, %[ctrl], r0, lsl #2        @ add the odd elements to the control register           \n\t" \
		      "ldr   r0, [r0, %[random_jump]]       @ Load the base address of the random loop               \n\t" \
		      "sub   %[n], %[n], #1                 @ adjust loop count                                      \n\t" \
		      "bx    r0                             @ If the number is still positive then loop again        \n\t" \
		      : [n] "+r" (n) : [ctrl] "r" (ctrl), [random_jump] "J" (RANDOM_LOOP_ADDRESS) : "cc", "memory");       \
  } while (false)


//! \brief This is the function that reloads the random buffer when it is empty.
//! It also has the effect of leaving the next random number in r0, and setting
//! the rp register correctly.
//!
//! Note it should not be called from 'C' as it does not save all the registers
//! it uses.
//!
//! The conditional "call" for feeding the DMA requires us to preserve the link
//! register in some way.

void __refill_random_buffer (void)
{
    __label__ Loop;
    RANDOM_REGISTER_MAP;

    asm volatile ("push  {lr}        @ Save the return address (we will be using the link register to store register 'n'  \n\t"
		  "mov   %[n], #255  @ Load the loop counter to one less than the number of random numbers required       \n\t"
		  : [n] "=r" (n) : : "memory");

    __load_random_state (); // Load all of the registers needed to calculate JKISS-64

 Loop:                      // Do eight JKISS-64 iterations...
    __jkiss64_and_store (); __jkiss64_and_store (); __jkiss64_and_store (); __jkiss64_and_store ();
    __jkiss64_and_store (); __jkiss64_and_store (); __jkiss64_and_store (); __jkiss64_and_store ();

    feed_dma_if_needed ();  // Poll the DMA engine

    asm volatile ("subs %[n], %[n], #8     @ decrement and test the 'loop counter'                    \n\t"
		  "                        @   (actually the number of synapses to be processed -1)   \n\t"
		  : [n] "+r" (n) : : "cc", "memory");

    asm goto     ("bpl  %l[Loop]           @ If the number is still positive then loop again          \n\t"
		  : : : "cc" : Loop);

    __save_random_state (); // Save the JKISS-64 registers

    asm volatile ("ldr  %[rp], [%[ctrl], %[kiss_rp]]  @ Reset the random pointer                      \n\t"
		  "ldr  r0, [%[rp]], #4               @ load random number, and advance pointer       \n\t"
		  "pop  {pc}                          @ Return                                        \n\t"
		  : [ctrl] "=r" (ctrl), [rp] "+r" (rp) : [kiss_rp] "J" (RANDOM_BASE_OFFSET) : "memory");
}

uint32_t refill_random_buffer (void)  __attribute__ ((noinline, naked));
uint32_t refill_random_buffer (void)
{
    register uint32_t* ctrl asm ("r12"); /* control and constant access                 */

    asm volatile ("push  {r1-r12,lr}                 @ Save all 'C' registers and return address \n\t"
		  : : "r" (ctrl) : "memory");
    ctrl = __control;                               // Load control register
    asm volatile ("ldr   r11, [%[ctrl], %[kiss_rp]]  @ Load the random pointer                   \n\t"
		  "bl    __refill_random_buffer      @ Do actual buffer refill                   \n\t"
		  "pop   {r1-r12,pc}                 @ Restore all 'C' registers and return      \n\t"
		  : [ctrl] "=r" (ctrl) : [kiss_rp] "J" (KISS_STATE_RP) : "cc", "memory");
}


//! \brief Loads the random pointer from the control structure. Register r12
//! must point to this structure.

#define __load_random_pointer()                                                                    \
    do {asm volatile ("push {r11}                        @ Save the previous value of r11    \n\t" \
		      "ldr  r11, [%[ctrl], %[kiss_rp]]   @ Load the random pointer           \n\t" \
		      : : [ctrl] "r" (ctrl), [kiss_rp] "J" (KISS_STATE_RP) : "memory");            \
    } while (false)

//! \brief Saves the random pointer from the control structure. Register r12
//! must point to this structure.

#define __save_random_pointer()                                                                    \
    do {asm volatile ("str  r11, [%[ctrl], %[kiss_rp]]   @ Save the random pointer           \n\t" \
		      "pop  {r11}                        @ Restore the previous value of r11 \n\t" \
		      : : [ctrl] "r" (ctrl), [kiss_rp] "J" (KISS_STATE_RP) : "memory");            \
    } while (false)









/* 

  growing upwards from zero, pre-indexing:         ldr r0, [rp, #4]!    // loads from 1 to 256   START rp = -1;  END rp = 254
  growing upwards from zero, post-indexing:        ldr r0, [rp], #4     // loads from 0 to 255   START rp = 0;   END rp = 255
  growing downwards from 255, pre-indexing:        ldr r0, [rp, #-4]!   // loads from 255 to 0   START rp = 256; END rp = 1
  growing downwards from 255, post-indexing:       ldr r0, [rp], #-4    // loads from 255 to 0   START rp = 255; END rp = 0


 */












uint32_t old_fast_poisson (uint32_t* base, uint32_t key)
{
    uint32_t offset = - ((((uint32_t)base) >> 2) + 2);

    while (*base++ > key);

    return (((uint32_t)base >> 2) + offset);
}

/*
00001bd4 <old_fast_poisson>:
    1bd4:       e1a03120        lsr     r3, r0, #2
    1bd8:       e3e02001        mvn     r2, #1
    1bdc:       e0632002        rsb     r2, r3, r2
    1be0:       e4903004        ldr     r3, [r0], #4
    1be4:       e1530001        cmp     r3, r1
    1be8:       8afffffc        bhi     1be0 <old_fast_poisson+0xc>
    1bec:       e0820120        add     r0, r2, r0, lsr #2
    1bf0:       e12fff1e        bx      lr
*/
/*
byte = 1 then

     ldr   r1, [%[rp]], #4           @ load random number 

     if r0 & 0xff000000 == 80

     ldr   r2, [%[table], #-4]       @ load constant 1350730249
     and   r0, r0, #0x00ffffff       @ clear high bits of r0
     cmp   r1, r2                    @ set flags
     addle r0, r0, #0x01000000       @ increment if prn < 1350730249

     if r0 & 0xff000000 == 81

     ldr   r2, [%[table], #-8]       @ load constant 2652905189
     and   r0, r0, #0x01ffffff       @ clear high bits of r0
     cmp   r1, r2                    @ set flags
     ldr   r2, [%[table], #-8]       @ load constant 1976658223
     addle r0, r0, #0x01000000       @ increment if prn < 2652905189
     cmp   r1, r2                    @ set flags
     ldr   r2, [%[table], #-12]      @ load constant 756999715
     addle r0, r0, #0x01000000       @ increment if prn < 1976658223
     cmp   r1, r2                    @ set flags
     ldr   r2, [%[table], #-16]      @ load constant 269136311
     addle r0, r0, #0x01000000       @ increment if prn < 756999715
     cmp   r1, r2                    @ set flags
     addle r0, r0, #0x01000000       @ increment if prn < 269136311



>>> poisson.pmf(0,1.6) * 256
51.685508606631785
>>> poisson.pmf(1,1.6) * 256
82.69681377061086
>>> poisson.pmf(2,1.6) * 256
66.1574510164887
>>> poisson.pmf(3,1.6) * 256
35.28397387546064
>>> poisson.pmf(4,1.6) * 256
14.113589550184257
>>> poisson.pmf(5,1.6) * 256
4.5163486560589625
>>> poisson.pmf(6,1.6) * 256
1.204359641615723
>>> poisson.pmf(7,1.6) * 256
0.27528220379787954


{2944237047, // 2944237046.6100454 = 0.68550... * 2^32
==========
    1642062107,  //  1642062106.7861347 = (0.68550+0.69681377061086 - 1) * 2^32 = 0.38232237724264495 * 2^32
    //0.5397733937313449

    */

//! \brief The combined tables for a Poisson Distribution with lambda = 1.6
//! This includes (first part): the 8-bit values needed for the fast case;
//! (second part): the 32-bit comparison values to more accurately determine
//! small (< 6) return values; and (third part) an extended table for the tail.
//!
//! This will generate poisson values as if it had been fed with 40-bit PRNs.
//!
//! Arrgghh!! Note LSB is lowest in following table!!

/*



1350730249.3899546
*/

static const uint32_t __poisson_tables[]
   = {0x83828106, 0x05050505,  //B, C, D, 6, 5, 5, 5, 5,
      0x04040404, 0x04040404,  //4, 4, 4, 4, 4, 4, 4, 4,
      0x04040404, 0x03030404,  //4, 4, 4, 4, 4, 4, 3, 3,
      0x03030303, 0x03030303,  //3, 3, 3, 3, 3, 3, 3, 3,
      0x03030303, 0x03030303,  //3, 3, 3, 3, 3, 3, 3, 3,
      0x03030303, 0x03030303,  //3, 3, 3, 3, 3, 3, 3, 3,
      0x03030303, 0x03030303,  //3, 3, 3, 3, 3, 3, 3, 3,
      0x03020202, 0x02020202,  //3, 2, 2, 2, 2, 2, 2, 2,

      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020202, 0x02020202,  //2, 2, 2, 2, 2, 2, 2, 2,
      0x02020201, 0x01010101,  //2, 2, 2, 1, 1, 1, 1, 1,

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


//=============================================================================
// We define the register allocation suitable for the poisson processing.
//=============================================================================

#define USE_POISSON_REGISTERS()						                          \
  do {asm volatile ("@ spoof register use\n\t"				                          \
		    : : "r" (n), "r" (mask), "r" (table), "r" (pp), "r" (rp), "r" (ctrl) : "cc"); \
  } while (false)

//! \brief The following macro allows us to define _in_one_place_ the register
//! names and locations used by the various pieces of poisson manipulation code.
//!
//! It also hides a piece of non-code-generating code that "uses" all of these
//! registers, as most code fragments don't use _all_ the registers.
//!
//! It may be that omitting this "asm" statement becomes necessary later.

#define POISSON_REGISTER_MAP                                                                   \
  register uint32_t* ctrl      asm ("r12"); /* control and constant access                 */ \
  register uint32_t* rp        asm ("r11"); /* Pointer to next random number               */ \
  register uint32_t* pp        asm ("r10"); /* Pointer to next poisson random number       */ \
  register uint32_t* table     asm ("r9");  /* Table of look-up values                     */ \
  register uint32_t  mask      asm ("r8");  /* mask used in processing                     */ \
  register uint32_t  n         asm ("r7");  /* counter for loop                            */ \
                                                                                              \
  USE_POISSON_REGISTERS()

void fast_poisson_hex      (void) asm ("fast_poisson_hex")      __attribute__ ((noinline, naked));
void __fast_poisson_fixup  (void) asm ("__fast_poisson_fixup")  __attribute__ ((noinline, naked));

//! \brief The following code fills in four poisson values from one random word
//! "most of the time"; to be precise, we get the right answer 253 times out of
//! 256 attempts. As usual, we accumulate failures in the flags (using the Z
//! flag to indicate that we have been successful so far), and post-process any
//! failed attempts -- which are indicated by having byte values with the first
//! nibble being non-zero -- using an extended poisson transformation.
//!
//! The code provided is 12 instructions long and takes 12 cycles to execute.

#define __fast_poisson_quad()                                                                                          \
    do {asm volatile ("ldrb   r0, [%[rp]], #1          @ load random byte                                        \n\t" \
		      "ldrb   r1, [%[rp]], #1          @ load random byte                                        \n\t" \
		      "ldrb   r2, [%[rp]], #1          @ load random byte                                        \n\t" \
		      "ldrb   r3, [%[rp]], #1          @ load random byte                                        \n\t" \
		      "ldrb   r0, [%[table], r0]       @ look-up 8-bit poisson                                   \n\t" \
		      "ldrb   r1, [%[table], r1]       @ look-up 8-bit poisson                                   \n\t" \
		      "ldrb   r2, [%[table], r2]       @ look-up 8-bit poisson                                   \n\t" \
		      "ldrb   r3, [%[table], r3]       @ look-up 8-bit poisson                                   \n\t" \
		      "orr    r0, r1, r0, lsl #8       @ accumulate result                                       \n\t" \
		      "orr    r0, r2, r0, lsl #8       @ accumulate result                                       \n\t" \
		      "orr    r0, r3, r0, lsl #8       @ accumulate result                                       \n\t" \
		      "str    r0, [%[pp]], #4          @ store poisson values in buffer                          \n\t" \
		      : [rp] "+r" (rp), [pp] "+r" (pp) : [table] "r" (table) : "cc", "memory");		               \
    } while (false)

//! \brief Tests the result of four poisson random numbers to see if further
//! processing is required. The mask used is 0x07070707, and we use the bit-
//! clear instruction to zero bytes that are OK. 

#define __fast_poisson_quad_first_test()				                                               \
    do {asm volatile ("tst   r0, %[mask]               @ 'And' the write-back word with the mask 0x07070707      \n\t" \
		      : : [mask] "r" (mask) : "cc");		                                                       \
    } while (false)

//! \brief Tests the result of four poisson random numbers to see if further
//! processing is required. The mask used is 0x07070707, and we use the bit-
//! clear instruction to zero bytes that are OK. 

#define __fast_poisson_quad_remaining_test()				                                               \
    do {asm volatile ("tsteq r0, %[mask]               @ 'And' the write-back word with the mask 0x07070707      \n\t" \
		      "                                @ This is conditional on previous tests having proved to  \n\t" \
		      "                                @ be 'OK so far'                                          \n\t" \
		      : : [mask] "r" (mask) : "cc");		                                                       \
    } while (false)

//! \brief This organises a call to the fix-up routine if needed, derements the
//! loop counter and tests for completion. It ought to check the DMA as well.

#define __fast_poisson_loop()				                                                               \
    do {asm volatile ("subs %[n], %[n], #1          @ decrement and test the 'loop counter'                      \n\t" \
		      "                             @   (actually the number of poissons to be processed -1)     \n\t" \
		      "bpl  fast_poisson_hex        @ If the number is still non-negative then loop again        \n\t" \
		      : [n] "=r" (n) : : "cc");				                                               \
    } while (false)

//! \brief This organises a call to the fix-up routine if needed, derements the
//! loop counter and tests for completion. It ought to check the DMA as well.

#define __fast_poisson_fixup_loop()				                                                       \
    do {asm volatile ("bleq __fast_poisson_fixup    @ fix up poisson numbers if needed  \n\t" : : : "cc");             \
        __fast_poisson_loop (); 						                                       \
    } while (false)

//! \brief The following code generates 16 poisson random variables, and has
//! a 17.2% chance of requiring at least one extended poisson calculation. Or,
//! it has an 82.8% of succeeding. If the branch is not taken, it executes in
//! 53 cycles.

#define __fast_poisson_hexadecatuple()					\
    do {								\
        __fast_poisson_quad (); __fast_poisson_quad_first_test ();	\
	__fast_poisson_quad (); __fast_poisson_quad_remaining_test ();	\
	__fast_poisson_quad (); __fast_poisson_quad_remaining_test ();	\
	__fast_poisson_quad (); __fast_poisson_quad_remaining_test ();	\
     } while (false)

//! \brief Although it appears that we only need _some_ of the poisson registers
//! set up -- in fact with probability > 50% we will call the fixup routine.
//! This requires all of them, so rather than do this repeatedly, we make the
//! assumption that they are always set u
void fast_poisson_hex (void)
{
    POISSON_REGISTER_MAP;

    __fast_poisson_hexadecatuple ();  // Fill in 16 bytes with poisson values

    feed_dma_if_needed ();            // Poll the DMA engine

    __fast_poisson_fixup_loop ();     // Fix up bytes requiring an extended value

    /* HACK!!!! need to exit this function!!! */
}

//! \brief This function replaces a poisson number by a corrected one.
//!
//! On entry, the value to be replace is in the top byte of the word held in
//! register r0.


//! \brief Replaces the top byte with a "fixed up" version.

uint32_t __poisson_fixup_value (uint32_t p) asm ("__poisson_fixup_value") __attribute__ ((noinline));
uint32_t __poisson_fixup_value (uint32_t p)
{
    POISSON_REGISTER_MAP;

    p = p & 0x00ffffff;

    return (0| p);
}

//! \brief This is the poisson fix-up routine. Note how we have structured the
//! tests: we branch-and-link to the actual fix-up only when the word is
//! negative (i.e. the top bit is set).

void __poisson_fixup (void) asm ("__poisson_fixup") __attribute__ ((noinline,naked));
void __poisson_fixup (void)
{
    POISSON_REGISTER_MAP;

    asm volatile ("push   {lr}                        @ Save the return address (this is not a leaf routine)          \n\t"
		  "blmi   __poisson_fixup_value       @ If the leading bit of r0 is set, then we need a new           \n\t"
		  "                                   @ value here so jump to a routine to amend the value            \n\t"
		  "rors   r0, r0, #8                  @ rotate r0 to align the next byte at the top of the word       \n\t"
		  "blmi   __poisson_fixup_value       @ If the leading bit of r0 is set, then we need a new           \n\t"
		  "                                   @ value here so jump to a routine to amend the value            \n\t"
		  "rors   r0, r0, #8                  @ rotate r0 to align the next byte at the top of the word       \n\t"
		  "blmi   __poisson_fixup_value       @ If the leading bit of r0 is set, then we need a new           \n\t"
		  "                                   @ value here so jump to a routine to amend the value            \n\t"
		  "rors   r0, r0, #8                  @ rotate r0 to align the next byte at the top of the word       \n\t"
		  "blmi   __poisson_fixup_value       @ If the leading bit of r0 is set, then we need a new           \n\t"
		  "                                   @ value here so jump to a routine to amend the value            \n\t"
		  "ror    r0, r0, #8                  @ rotate r0 to align the next byte at the top of the word       \n\t"
		  "pop    {pc}                        @ return                                                        \n\t"
	      : : : "cc");
}

//! mask = 0x80808080. Then r & mask == 0 when no fixup is required.
void __fast_poisson_fixup (void)
{
    __label__ L0, L1, L2, L3;
    POISSON_REGISTER_MAP;

    asm goto ("ldr    r0, [%[pp], #-16]          @ load first quad of poisson values                          \n\t"
	      "ldr    r1, [%[pp], #-12]          @ load second quad of poisson values                         \n\t"
	      "bics   lr, r0, %[mask]            @ Does the first quad need fix-up?                           \n\t"
	      "blne   %l[L0]                      \n\t"
	      "bics   lr, r1, %[mask]            @ Does the second quad need fix-up?                           \n\t"
	      "blne   %l[L1]                      \n\t"
	      "ldr    r0, [%[pp], #-8]           @ load third quad of poisson values                          \n\t"
	      "ldr    r1, [%[pp], #-4]           @ load fourth quad of poisson values                         \n\t"
	      "bics   lr, r0, %[mask]            @ Does the third quad need fix-up?                           \n\t"
	      "blne   %l[L2]                      \n\t"
	      "bics   lr, r1, %[mask]            @ Does the fourth quad need fix-up?                           \n\t"
	      "bne    %l[L3]                      \n\t"
	      : : [pp] "r" (pp), [mask] "r" (mask) : "cc", "memory" : L0, L1, L2, L3);

    __fast_poisson_loop ();
    
 L0:
    asm volatile
             ("push   {lr}                       @ save return address                                        \n\t"
	      "bl     __poisson_fixup            @ Do fix up                                                  \n\t"
	      "str    r0, [%[pp], #-16]          @ write-back first quad of poisson values                    \n\t"
	      "pop    {pc}                       @ return                                                     \n\t"
	      : : [pp] "r" (pp) : "cc", "memory");
 L1:
    asm volatile
             ("push   {lr}                       @ save return address                                        \n\t"
	      "mov    r0, r1                     @ move word to r0                                            \n\t"
	      "bl     __poisson_fixup            @ Do fix up                                                  \n\t"
	      "str    r0, [%[pp], #-12]          @ write-back second quad of poisson values                   \n\t"
	      "pop    {pc}                       @ return                                                     \n\t"
	      : : [pp] "r" (pp) : "cc", "memory");
 L2:
    asm volatile
             ("push   {lr}                       @ save return address                                        \n\t"
	      "bl     __poisson_fixup            @ Do fix up                                                  \n\t"
	      "str    r0, [%[pp], #-8]           @ write-back third quad of poisson values                    \n\t"
	      "pop    {pc}                       @ return                                                     \n\t"
	      : : [pp] "r" (pp) : "cc", "memory");
 L3:
    asm volatile
             ("mov    r0, r1                     @ move word to r0                                            \n\t"
	      "bl     __poisson_fixup            @ Do fix up                                                  \n\t"
	      "str    r0, [%[pp], #-4]           @ write-back fourth quad of poisson values                   \n\t"
	      : : [pp] "r" (pp) : "cc", "memory");

    __fast_poisson_loop ();
}
