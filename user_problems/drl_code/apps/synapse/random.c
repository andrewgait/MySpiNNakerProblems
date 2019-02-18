//!
//! random.c
//!
//! A generic OO-like mechanism for efficient random number generation.

//!============================================================================
//!
//! The data structure is an array of unsigned 32-bit integers laid out as shown
//! in the following diagram. Note that the centre (0) element is an address.
//!
//!                      +--------+----------------+---------------+
//!                index |  name  | description    | default value |
//!                      +--------+----------------+---------------+
//!
//!                      +--------+----------------+---------------+
//!                -80:  | b[-80] | buffer element |               |
//!                      +--------+----------------+---------------+
//!                -79:  | b[-79] | buffer element |               |
//!                      +--------+----------------+---------------+
//!
//!                        ...          ....             ....
//!
//!                      +--------+----------------+---------------+         +---------------------------+
//!                 -3:  | b[-3]  | buffer element |               |         | constant k2 4294584393ULL |
//!                      +--------+----------------+---------------+         +---------------------------+
//!                 -2:  | b[-2]  | buffer element |               |         | constant k1   1234567     |
//!   pointer            +--------+----------------+---------------+         +---------------------------+
//!     to          -1:  | b[-1]  | buffer element |               |         | constant k0    314527869  |
//! structure            +--------+----------------+---------------+         +---------------------------+
//!       ------->   0:  | pointer to method/constant table  *-----+-------> | next_random()  method     |
//!                      +--------+----------------+---------------+         +---------------------------+
//!                  1:  | index  |                |      0        |         | randoms(n)     method     |
//!                      +--------+----------------+---------------+         +---------------------------+
//!                  2:  |  size  | buffer size    |     80        |         | refill()       method     |
//!                      +--------+----------------+---------------+         +---------------------------+
//!                  3:  |   x    | state variable |   123456789   |         | free()         method     |
//!                      +--------+----------------+---------------+         +---------------------------+
//!                  4:  |   y    | state variable |   987654321   |         | save()         method     |
//!                      +--------+----------------+---------------+         +---------------------------+
//!                  5:  |   z    | state variable |   43219876    |         | restore()      method     |
//!                      +--------+----------------+---------------+         +---------------------------+
//!                  6:  |   c    | state variable |    6543217    |
//!                      +--------+----------------+---------------+
//!                  7:  |   x    | saved variable |   123456789   |
//!                      +--------+----------------+---------------+
//!                  8:  |   y    | saved variable |   987654321   |
//!                      +--------+----------------+---------------+
//!                  9:  |   z    | saved variable |   43219876    |
//!                      +--------+----------------+---------------+
//!                 10:  |   c    | saved variable |    6543217    |
//!                      +--------+----------------+---------------+
//!
//! The reason for having the pointer point into the middle of the structures is
//! that the ARM instruction set permits negative array access just as easily as
//! positive array access.

#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"
#include <debug.h>

#define JKISS_BUFFER_SIZE   80
#define JKISS_VARIABLE_SIZE  4
#define JKISS_CONSTANT_SIZE  3
#define JKISS_STATE_SIZE     3

#define RANDOM_FREE     0
#define RANDOM_SAVE     1
#define RANDOM_RESTORE  2
#define RANDOM_NEXT     3
#define RANDOM_BLOCK    4
#define RANDOM_REFILL   5


typedef uint32_t* random_buffer_t;
typedef void (*random_method_t)(const random_buffer_t);
typedef uint32_t (*random_uint32_method_t)(const random_buffer_t);
typedef void (*random_method_uint32s_t)(const random_buffer_t, uint32_t*);


#define buffer_constants(buffer)  ((uint32_t*)(buffer[0]))
#define buffer_index(buffer)      buffer[1]
#define buffer_size(buffer)       buffer[2]
#define buffer_method(buffer,n)   (((random_method_t*)(buffer[0]))[n])
#define buffer_value(buffer,n)    (((uint32_t*)(buffer[0]))[-n])

//! \brief Generic free operation for any random buffer.
//!
//! \param[in] buffer The data structure holding data on a particular PRNG.

void random_free (const random_buffer_t buffer)
{   ((random_method_t)(buffer_constants(buffer)[RANDOM_FREE]))(buffer); }


//! \brief Generic save operation for any random buffer.
//!
//! \param[in] buffer The data structure holding data on a particular PRNG.
//! \param[in] dest   The data structure to hold the saved state.

void random_save (const random_buffer_t buffer, uint32_t* dest)
{   ((random_method_uint32s_t)(buffer_constants(buffer)[RANDOM_SAVE]))(buffer, dest); }


//! \brief Generic restore operation for any random buffer.
//!
//! \param[in] buffer The data structure holding data on a particular PRNG.
//! \param[in] src    The data structure from which to restore the saved state.

void random_restore (const random_buffer_t buffer, uint32_t* src)
{   ((random_method_uint32s_t)(buffer_constants(buffer)[RANDOM_RESTORE]))(buffer, src); }


//! \brief Generic next operation for any random buffer.
//!
//! \param[in] buffer The data structure holding data on a particular PRNG.
//! \return           The next random number.

uint32_t random_next (const random_buffer_t buffer)
{
    register uint32_t prn;
    register uint32_t index = buffer_index (buffer);

    // The following asm statement implements the C statement:
    //
    //           prn = buffer [-(index >> 2)];
    
    asm volatile ("ldr %[prn], [%[buffer], -%[index]]  @ Single-cycle negative indexing  \n\t"
		  : [prn] "=r" (prn) : [buffer] "r" (buffer), [index] "r" (index) : "memory");

    index -= 4;
    buffer_index (buffer) = index;

    if (index == 0)
        random_refill (buffer);

    return (prn);
}
//! \brief Generic refill operation for any random buffer.
//!
//! \param[in] buffer The data structure holding data on a particular PRNG.

void random_refill (const random_buffer_t buffer)
{   ((random_method_t)(buffer_constants (buffer) [RANDOM_REFILL])) (buffer); }


//{   return (((random_uint32_method_t)(buffer_constants(buffer)[RANDOM_NEXT]))(buffer)); }



//! \brief Frees the memory space taken by a JKISS-64 buffer and state.

void jkiss_free (const random_buffer_t buffer)
{   sark_free (buffer - buffer_size (buffer)); }

//! \brief Returns a pointer to the values to be saved if the state needs saving

uint32_t* jkiss_save (const random_buffer_t buffer)
{   return ((uint32_t*)(buffer)); }




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
//!                   This odd, lop-sided use of pointers makes for faster access
//!                   to the PRNGs in the buffer than if we always had to offset
//!                   to get to element 0.

random_buffer_t new_jkiss_buffer (uint32_t size, uint32_t* state)
{
    uint32_t* r;
    uint32_t* s;
    int n;

    static const random_method_t jkiss_methods []
      = {(random_method_t)123456789,     // default x
	 (random_method_t)987654321,     // default y
	 (random_method_t)43219876,      // default z
	 (random_method_t)6543217,       // default c
	 (random_method_t)4294584393ULL, // constant
	 (random_method_t)1234567,       // constant
	 (random_method_t)314527869,     // constant
	 *jkiss_free,
	 (random_method_t)jkiss_save     // save method
    };

    if (size == 0)
	size = JKISS_BUFFER_SIZE;

    //    assert ((size & 0x7) == 0);     // HACK!!! Need to check that size is a multiple of EIGHT!

    r = (uint32_t*) sark_alloc (size + JKISS_STATE_SIZE + 2*JKISS_VARIABLE_SIZE, sizeof(uint32_t));

    //    assert (r != NULL);            // HACK!!! Handling of NULL returned by alloc???

    r += size; // Skip over the actual buffer area.

    r[0] = (uint32_t)(jkiss_methods + 7);
    r[1] = size << 2;
    r[2] = size << 2;

    if (state != NULL)   // If the state is non-empty, use it to initialise the JKISS seed values
        s = state;       // HACK!!! Handling of state check.
    else
        s = (uint32_t*)jkiss_methods; // Otherwise the values in the jkiss_parameters are used.

    // Copy the four state variables from jkiss_methods or state, to state variables and saved state
    for (n = 0; n < 4; n++) {
        r[n+3] = *s;
        r[n+7] = *s++;
    }

    return (r);   // Offset the pointer to point at the start of the actual buffer.
			 // This happens because we have been auto-incrementing r.
}



uint32_t next_random (random_buffer_t buffer)
{
    register uint32_t n asm ("r2");

    asm volatile ("ldr  r1, [r0]          @ Load method table                            \n\t"
		  "ldr  %[n], [r0, #4]    @ Load the index into register n               \n\t"
		  "ldr  r1, [r1]          @ Load method table[0]                         \n\t"
		  "                       @ ... This is refill, and uses up a delay slot \n\t"
		  "subs %[n], %[n], #4    @ Adjust the index, setting flags              \n\t"
		  "bxeq r1                @ Jump to the refill routine, if index is zero \n\t"
		  "str  %[n], [r0, #4]    @ Store back the index from register n         \n\t"
		  "ldr  r0, [r0, -%[n]]   @ Load the next buffer element                 \n\t"
		  : [n] "+r" (n), "+r" (buffer) : : "cc", "memory");
    return ((uint32_t)buffer);
}

/*
uint32_t next_random1 (random_buffer_t buffer)
{
    register uint32_t* p asm ("r2");
    register uint32_t  r asm ("r3");

    asm volatile ("ldr  %[p], [r0, #4]    @ Load the pointer into register p             \n\t"
		  "ldr  r1, [r0]          @ Load method table                            \n\t"
		  "ldr  %[r], [%[p]], #4  @ Adjust the index, setting flags              \n\t"
		  "ldr  r1, [r1]          @ Load method table[0]                         \n\t"
		  "                       @ ... This is refill, and uses up a delay slot \n\t"
		  "cmp  r0, %[p]          @ Test for end of buffer                       \n\t"
		  "bxeq r1                @ Jump to the refill routine, if index is zero \n\t"
		  "str  %[p], [r0, #4]    @ Store back the index from register n         \n\t"
		  : [n] "+r" (n), "+r" (buffer) : : "cc", "memory");
    return ((uint32_t)buffer);
}
*/

void foo (const random_buffer_t buffer)
{
  io_printf (IO_STD, "%x \n\t", next_random (buffer));
}
