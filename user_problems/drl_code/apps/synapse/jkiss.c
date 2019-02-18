//! JKISS-64 implementation
//!
//! The array is laid out as follows. The reason for having the pointer point
//! into the middle of the structure is that the ARM instruction set permits
//! negative array access just as easily as positive array access (although C
//! is less comfortable).
//!
//!           +-------+----------------+---------------+
//!     index | name  | description    | default value |
//!           +-------+----------------+---------------+
//!
//!           +-------+----------------+---------------+
//!      -9:  |   k0  | Constant       |  314527869    |
//!           +-------+----------------+---------------+
//!      -8:  |   k1  | Constant       |    1234567    |
//!           +-------+----------------+---------------+
//!      -7:  |   k2  | Constant       | 4294584393ULL |
//!           +-------+----------------+---------------+
//!      -6:  |   x   | state variable |  123456789    |
//!           +-------+----------------+---------------+
//!      -5:  |   y   | state variable |  987654321    |
//!           +-------+----------------+---------------+
//!      -4:  |   z   | state variable |   43219876    |
//!           +-------+----------------+---------------+
//!      -3:  |   c   | state variable |    6543217    |
//!           +-------+----------------+---------------+
//!      -2:  | size  | buffer size    |     80        |
//!           +-------+----------------+---------------+
//!      -1:  | index |                |      0        |
//!           +-------+----------------+---------------+
//!       0:  | b[0]  | buffer element |               |    <------------- buffer pointer, points here.
//!           +-------+----------------+---------------+
//!       1:  | b[1]  | buffer element |               |
//!           +-------+----------------+---------------+
//!
//!             ...         ....             ....
//!
//!           +-------+----------------+---------------+
//!      79:  | b[79] | buffer element |               |
//!           +-------+----------------+---------------+

#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"
#include <debug.h>

//! \brief This pseudo-instruction pretends to use the registers declared in
//! RANDOM_REGISTER_MAP. This alerts gcc to the fact that the register and flags
//! may change, and thus it should not rearrange code blocks.

#define USE_RANDOM_REGISTERS()						       \
    do {asm volatile ("@ pretend to use registers                        \n\t" \
		      :							       \
		      : "r" (x), "r" (y), "r" (z), "r" (c), "r" (k0), "r" (t), \
			"r" (k1), "r" (k2)	                               \
		      : "cc");						       \
  } while (false)

//! \brief The following macro allows us to define _in_one_place_ the register
//! names and locations used by the various pieces of random manipulation code.
//!
//! It also hides a piece of non-code-generating code that "uses" all of these
//! registers, as most code fragments don't use _all_ the registers.
//!
//! It may be that omitting this "asm" statement becomes necessary later.

#define RANDOM_REGISTER_MAP                                                                   \
  register uint32_t  c         asm ("r10"); /* JKISS-64 state variable                     */ \
  register uint32_t  z         asm ("r9");  /* JKISS-64 state variable                     */ \
  register uint32_t  y         asm ("r8");  /* JKISS-64 state variable                     */ \
  register uint32_t  x         asm ("r7");  /* JKISS-64 state variable                     */ \
  register uint32_t  k2        asm ("r6");  /* Constant 4294584393ULL                      */ \
  register uint32_t  k1        asm ("r5");  /* Constant 1234567                            */ \
  register uint32_t  k0        asm ("r4");  /* Constant 314527869                          */ \
                                                                                              \
  USE_RANDOM_REGISTERS()

//! \brief The algorithm implemented is Marsaglia's JKISS-64.
//!
//! The __jkiss64_asm routine assumes that the seed/state and constants are
//! all pre-loaded, and that it can maintain the state in registers between
//! calls. If this is the case, then the following 9 instructions takes just
//! 11 cycles to calculate the next 32-bit PRNG in r0.
//!
//! Note: we use assemble, because gcc tries to use a umlal instruction, and
//! this uses an additional cycle, because of the swapping of the location of Z.
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
                      "umull %[z], %[t], %[k2], %[z]   @ [z;t] = 4294584393 * z     (64-bit unsigned mul)   \n\t" \
                      "adds  %[z], %[z], %[c]          @ 64-bit addition ...                                \n\t" \
                      "adc   %[c], %[t], #0            @  ...                                               \n\t" \
                      "add   %[t], %[x], %[y]          @ Accumulate output ...                              \n\t" \
                      "add   %[t], %[t], %[z]          @     ...                                            \n\t" \
		      "str   %[t], [%[rp], #-4]!       @ Store the result and auto-decrement the rp pointer \n\t" \
                      : [x] "+r" (x), [y] "+r" (y), [z] "+r" (z), [c] "+r" (c), [rp] "+r" (rp), [t] "+r" (t)      \
		      : [k0] "r" (k0), [k1] "r" (k1), [k2] "r" (k2) : "cc", "memory"); 	                          \
    } while (false)


//! \brief

typedef uint32_t* jkiss_state_t;

uint32_t __jkiss64_block (const jkiss_state_t state) asm ("__jkiss64_block") __attribute__ ((noinline));


static inline int jkiss_index (jkiss_state_t state)
{
    return ((int)(state [-1]));
}

//! \brief This is the _internal_ pointer access for a pointer to the random
//! number buffer.

static inline uint32_t* jkiss_pointer (const jkiss_state_t state)
{
    return ((uint32_t*)((uint32_t)state + state [-1]));
}

//! \brief This is the publically-facing API interface to the index.
//! It returns the number of random numbers available in the buffer.

uint32_t jkiss_available (const jkiss_state_t state)
{
    return ((uint32_t)jkiss_index (state));
}

//! \brief This _allocates_ n random numbers from the buffer, if they are
//! available. It does this by returning a pointer which is guaranteed to have
//! enough elements when auto-decremented. Otherwise it returns NULL.

uint32_t* jkiss_allocate (const jkiss_state_t state, const uint32_t n)
{
    uint32_t* rp;

    if (n > jkiss_available (state))
	return (NULL);

    rp = jkiss_pointer (state);

    state[-1] -= n;

    if (state[-1] == 0)
	__jkiss64_block (state);

    return (rp);
}



//! \brief The unsigned integers required to implement the JKISS-64 algorithm.
//!
//! The last four numbers are the initial values of x, y, z, and c respectively.
//! The other three are the constants.

static const uint32_t jkiss_parameters[]
    = {314527869, 1234567, 4294584393ULL, 123456789, 987654321, 43219876, 6543217};

#define JKISS_VARIABLE_SIZE 4
#define JKISS_CONSTANT_SIZE 3
#define JKISS_BUFFER_SIZE   80

//! \brief Initialises the JKISS-64 state, so that different initial states can
//! be supported.
//!
//! \param[in] size   Defines the number of random numbers held in the buffer.
//!                   If size == 0, then the default size of 80 is used instead.
//!                   Note, size should be a multiple of EIGHT.
//!
//! \param[in] state  The initial values of the JKISS state. These are copied
//!                   into the buffer, where they are updated as the JKISS-64
//!                   algorithm runs.
//!
//! \return           A pointer to a new malloc-ed PRNG buffer. Below the
//!                   pointer are the NINE varaibles/constants that control the
//!                   behaviour of the PNG algorithm.
//!
//!                   This odd, lop-sided use of pointers makes fo faster access
//!                   to the PRNGs in the buffer than if we always had to offset
//!                   to get to element 0.

jkiss_state_t initialise_jkiss_state (uint32_t size, uint32_t* state)
{
    uint32_t* r;
    uint32_t* s = (uint32_t*)jkiss_parameters;

    if (size == 0)
	size = JKISS_BUFFER_SIZE;

    assert ((size & 0x7) == 0);     // HACK!!! Need to check that size is a multiple of EIGHT!

    r = (uint32_t*) sark_alloc (2 + size + JKISS_VARIABLE_SIZE + JKISS_CONSTANT_SIZE, sizeof(uint32_t));

    assert (r != NULL);            // HACK!!! Handling of NULL returned by alloc???


    // Copy the three constants from jkiss_parameters.
    *r++ = *s++;
    *r++ = *s++;
    *r++ = *s++;

    if (state != NULL) { // If the state is non-empty, use it to initialise the JKISS seed values
        s = state;
    }                    // Othewise the values in the jkiss_parameters are used.

    // Copy the four state variables from jkiss_parameters or state.
    *r++ = *s++;
    *r++ = *s++;
    *r++ = *s++;
    *r++ = *s++;

    *r++ = size << 2;    // initial index value, multiplied by 4
    *r++ = size << 2;    // the size of the actual buffer
			 // The multiplication by fou permits faster access to the PRNGs

    return (r);          // Offset the pointer to point at the start of the actual buffer.
			 // This happens because we have been auto-incrementing r.
}

//! \brief Frees the memory space taken by a JKISS-64 buffer and state.

void free_jkiss_state (const jkiss_state_t buffer)
{
    sark_free (buffer - 9);
}


//! \brief
//!

uint32_t __jkiss64_block (const jkiss_state_t state)
{
    register uint32_t* rp asm ("r0");
    register uint32_t  t  asm ("r1");
    register int       n;

    RANDOM_REGISTER_MAP;

    rp = state - 9;

    // Read the JKISS constants and state variables

    k0 = *rp++;
    k1 = *rp++;
    k2 = *rp++;
    x  = *rp++;
    y  = *rp++;
    z  = *rp++;
    c  = *rp++;
    n  = *rp++;  // pick up size
    *rp++ = n;   // reset index
    rp += n;     // set rp to point at the top of the buffer

    // Do the buffer filling in blocks of eight random numbers
    for ( ; n > 0; n -= 8) {
        __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm ();
	__jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm (); __jkiss64_asm ();
    }

    // Write back JKISS state variables
    rp -= 6;
    *rp++ = x;
    *rp++ = y;
    *rp++ = z;
    *rp++ = c;

    // reset rp to top;
    rp += *rp + 2; 

    return (*rp);
}


//! \brief This is the function call
//=====================
//(which can be inlined) Not so sure. Single entry/exit needed?
//=====================
//! that returns a new
//! pseudo-random number. It does so by calling the __jkiss64_block to refill
//! the buffer whenever the index reaches zero; i.e. once every eighty function
//! calls.

uint32_t stateful_jkiss64 (const jkiss_state_t buffer)
{
    register uint32_t rand  asm ("r0");
    register int      index asm ("r1");

    index = ((int)(*(buffer - 1)));                // index = buffer [-1];

    asm volatile ("subs %[index], %[index], #4     @ subtract 'one' from index value and test for 0 \n\t"
		  "bmi  __jkiss64_block            @ _branch_ to jkiss block fill routine           \n\t"
		  "                                @   ... and return from there with new random    \n\t"
		  : [index] "+r" (index) : : "cc", "memory");

    *(buffer - 1) = (uint32_t)index;               // buffer [-1] = index;
    rand = *((uint32_t*) ((int)buffer + index));   // rand = buffer [index >> 2];

    return (rand);
}

void foo (const jkiss_state_t buffer)
{
    io_printf (IO_BUF, "%08x\n", stateful_jkiss64 (buffer));
}

