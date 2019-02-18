/*
  A fast poisson PRNG converter.
*/

#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"
#include "random.h"


/*
   Custom seed version of above - need to create & validate 128 bit seed
   before use
*/
uint32_t mars_kiss64_seed(mars_kiss64_seed_t seed)
{
#define x seed[0]
#define y seed[1]
#define z seed[2]
#define c seed[3]

    uint64_t t;

    x = 314527869 * x + 1234567;
    y ^= y << 5;
    y ^= y >> 7;
    y ^= y << 22;
    t = 4294584393ULL * z + c;
    c = t >> 32;
    z = t;

    return (uint32_t) x + y + z;

#undef x
#undef y
#undef z
#undef c
}

uint32_t seed[] = {123456789, 987654321, 43219876, 6543217};

typedef unsigned long fract ulf_t;      // DKF type introduced to make Eclipse moan less



/*
   Implementation of Marsaglia JKISS RNG uses 64-bit value and 2x multiplies

   219.9 nanosecs (i.e. 44 ticks) per call
*/
uint32_t mars_kiss64_simp(void)
{
    static uint32_t
        x = 123456789,
        y = 987654321,
        z = 43219876,
        c = 6543217; /* Seed variables */
    uint64_t t;

    x = 314527869 * x + 1234567;
    y ^= y << 5;
    y ^= y >> 7;
    y ^= y << 22;
    t = 4294584393ULL * z + c;
    c = t >> 32;
    z = t;

    return (uint32_t) x + y + z;
}

//! \brief A poisson distributed random variable, given exp (-lambda).
//! \param[in] uni_rng A uniformly distributed random number generator.
//! \param[in] seed_arg The seed state for the random number sequence.
//! \param[in] exp_minus_lambda \f$\exp(-\lambda)\f$.
//! \return An unsigned integer which is poisson-distributed.

uint32_t poisson_dist_variate_exp_minus_lambda(
        uniform_rng uni_rng,
        uint32_t* seed_arg,
        ulf_t exp_minus_lambda)
{
    ulf_t p = 1.0ulr;
    uint32_t k = 0;

    //! \remark DRL thinks this can be simplified to the following code:

    //!     while (p > exp_minus_lambda) {
    //!         p *= ulrbits(uni_rng(seed_arg));
    //!         k++;
    //!     }
    //!
    //!     return k;

    do {
        k++;
        p = p * ulrbits(uni_rng(seed_arg));
    } while (p > exp_minus_lambda);
    return k - 1;
}

uint32_t poisson_nibble[] = { 12,   7,  3,  1, 0};


//! \brief This array holds a value n at position i, such that whenever
//! a uniformly distributed 32-bit unsigned input x satisfies:
//!
//!        table[i] <= x < table[i-1]  {with table[-1] notionally being MAXUINT}
//!
//! With the given table entries, then the varible i will be a Poisson PRNG,
//! with lambda = 1.6.

uint32_t fast_poisson_table[]
    = { 3427828354,  // p = 0; 3427828354.0287867
	2040406047,  // p = 1; 2040406046.8874736
	930468201,   // p = 2; 930468201.1744232
	338501350,   // p = 3; 338501350.1274629
	101714610,   // p = 4; 101714609.7086788
	25942853,    // p = 5; 25942852.77466787
	5737051,     // p = 6; 5737050.925598297
	1118582,     // p = 7; 1118581.931525252
	194888,      // p = 8; 194888.1327106422
	30676,       // p = 9; 30675.90181026706
	4402,        // p = 10; 4401.944866207042
	580,         // p = 11; 580.2784016164973
	71,          // p = 12; 70.72287300442295
	8,           // p = 13; 8.008346406013947
	1,           // p = 14; 0.8409719376243779
	0            // p = 15, 0.0
       };

uint32_t old_fast_poisson (uint32_t* base, uint32_t key)
{
    uint32_t offset = - ((((uint32_t)base) >> 2) + 2);

    while (*base++ > key);

    return (((uint32_t)base >> 2) + offset);
}

static inline uint32_t fast_poisson (uint32_t* __base, uint32_t __key)
{
    __label__ L0, L1;

    register uint32_t* base   asm ("r0") = __base;
    register uint32_t  key    asm ("r1") = __key;
    register uint32_t  offset asm ("r2");
    register uint32_t  tmp1   asm ("r3");
    register uint32_t  tmp2   asm ("ip");

    offset = - ((((uint32_t)base) >> 2) + 2);

    asm volatile ("ldr %[tmp1], [%[base]], #4\n\t"
		  : [base] "+r" (base), [tmp1] "=r" (tmp1) : : "memory");

L0:
    asm volatile ("ldr %[tmp2], [%[base]], #4\n\t"
		  "cmp %[tmp1], %[key]\n\t"
		  : [base] "+r" (base), [tmp2] "=r" (tmp2)
		  : [tmp1]  "r" (tmp1), [key]   "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp1], [%[base]], #4\n\t"
		  "cmp %[tmp2], %[key]\n\t"
		  : [base] "+r" (base), [tmp1] "=r" (tmp1)
		  : [tmp2]  "r" (tmp2), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp2], [%[base]], #4\n\t"
		  "cmp %[tmp1], %[key]\n\t"
		  : [base] "+r" (base), [tmp2] "=r" (tmp2)
		  : [tmp1]  "r" (tmp1), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp1], [%[base]], #4\n\t"
		  "cmp %[tmp2], %[key]\n\t"
		  : [base] "+r" (base), [tmp1] "=r" (tmp1)
		  : [tmp2]  "r" (tmp2), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);
    
    asm volatile ("ldr %[tmp2], [%[base]], #4\n\t"
		  "cmp %[tmp1], %[key]\n\t"
		  : [base] "+r" (base), [tmp2] "=r" (tmp2)
		  : [tmp1]  "r" (tmp1), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp1], [%[base]], #4\n\t"
		  "cmp %[tmp2], %[key]\n\t"
		  : [base] "+r" (base), [tmp1] "=r" (tmp1)
		  : [tmp2]  "r" (tmp2), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp2], [%[base]], #4\n\t"
		  "cmp %[tmp1], %[key]\n\t"
		  : [base] "+r" (base), [tmp2] "=r" (tmp2)
		  : [tmp1]  "r" (tmp1), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp1], [%[base]], #4\n\t"
		  "cmp %[tmp2], %[key]\n\t"
		  : [base] "+r" (base), [tmp1] "=r" (tmp1)
		  : [tmp2]  "r" (tmp2), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp2], [%[base]], #4\n\t"
		  "cmp %[tmp1], %[key]\n\t"
		  : [base] "+r" (base), [tmp2] "=r" (tmp2)
		  : [tmp1]  "r" (tmp1), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp1], [%[base]], #4\n\t"
		  "cmp %[tmp2], %[key]\n\t"
		  : [base] "+r" (base), [tmp1] "=r" (tmp1)
		  : [tmp2]  "r" (tmp2), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp2], [%[base]], #4\n\t"
		  "cmp %[tmp1], %[key]\n\t"
		  : [base] "+r" (base), [tmp2] "=r" (tmp2)
		  : [tmp1]  "r" (tmp1), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp1], [%[base]], #4\n\t"
		  "cmp %[tmp2], %[key]\n\t"
		  : [base] "+r" (base), [tmp1] "=r" (tmp1)
		  : [tmp2]  "r" (tmp2), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);
    
    asm volatile ("ldr %[tmp2], [%[base]], #4\n\t"
		  "cmp %[tmp1], %[key]\n\t"
		  : [base] "+r" (base), [tmp2] "=r" (tmp2)
		  : [tmp1]  "r" (tmp1), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp1], [%[base]], #4\n\t"
		  "cmp %[tmp2], %[key]\n\t"
		  : [base] "+r" (base), [tmp1] "=r" (tmp1)
		  : [tmp2]  "r" (tmp2), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp2], [%[base]], #4\n\t"
		  "cmp %[tmp1], %[key]\n\t"
		  : [base] "+r" (base), [tmp2] "=r" (tmp2)
		  : [tmp1]  "r" (tmp1), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bls %l[L1]\n\t"
		  : : : "cc", "memory" : L1);

    asm volatile ("ldr %[tmp1], [%[base]], #4\n\t"
		  "cmp %[tmp2], %[key]\n\t"
		  : [base] "+r" (base), [tmp1] "=r" (tmp1)
		  : [tmp2]  "r" (tmp2), [key] "r" (key) : "cc", "memory");

    asm goto (	  "bhi %l[L0]\n\t"
		  : : : "cc", "memory" : L0);
L1:
    return (((uint32_t)base >> 2) + offset);

  /* WAS:::

  uint32_t result = - ((((uint32_t)base) >> 2) + 1);

    //asm volatile ("lsr r3, %[key]\n\t"
    //		  "rsb	r2, r3, #1\n\t"
    //		  : : [key] "r" (key) : "cc", "memory");

    while (*base++ > key)
    ;*/

}

uint32_t poisson_byte  [] = {204, 121, 55, 20, 6, 1, 0};

uint32_t extend_fast_poisson (uint32_t index, uint32_t prn, uint32_t* prng)
{
    uint32_t key = (prn << 24) & (*prng++ >> 8);

    if (fast_poisson_table[index] < key)
        index += 1;

    return (index);
}

uint32_t tail_fast_poisson (uint32_t prn)
{
    return (fast_poisson (fast_poisson_table, prn >> 8));
}

uint32_t __fast_poisson_byte_table[]
   = {6, 5, 5, 5, 5, 5, 4, 4,
      4, 4, 4, 4, 4, 4, 4, 4,
      4, 4, 4, 4, 3, 3, 3, 3,
      3, 3, 3, 3, 3, 3, 3, 3,
      3, 3, 3, 3, 3, 3, 3, 3,
      3, 3, 3, 3, 3, 3, 3, 3,
      3, 3, 3, 3, 3, 3, 3, 2,
      2, 2, 2, 2, 2, 2, 2, 2,
      
      2, 2, 2, 2, 2, 2, 2, 2,
      2, 2, 2, 2, 2, 2, 2, 2,
      2, 2, 2, 2, 2, 2, 2, 2,
      2, 2, 2, 2, 2, 2, 2, 2,
      2, 2, 2, 2, 2, 2, 2, 2,
      2, 2, 2, 2, 2, 2, 2, 2,
      2, 2, 2, 2, 2, 2, 2, 2,
      2, 1, 1, 1, 1, 1, 1, 1,

      1, 1, 1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1, 1, 1,

      1, 1, 1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0};

//! \brief Generate a poisson random value for the random byte "key"
//! using the random number stream "prng", returning the result in
//! "result", and using two tables. The returned value is the new
//! random number stream, less any values consumed by this routine.

uint32_t* __fast_poisson_byte (uint32_t* prng,
			      uint32_t key, uint32_t* result,
			      uint32_t* table_8, uint32_t* table_32)
{
    if (key == 0) {
        *result = fast_poisson (table_32, *prng++ >> 8);
	return (prng);
    }

    *result = table_8[key];

    return (prng);
}

//! \brief Calculates four Poisson Distributed Random Numbers from a single
//! 32-bit uniform random number (though it might use more random bits in
//! rare cases).
//!
//! \param[out] result The result vector
//! \param[in]  prn    A 32-bit random number

uint32_t* fast_poisson_bytes (uint32_t* prng, uint32_t keys, uint32_t* result,
			      uint32_t* table_8, uint32_t* table_32)
{
    prng = __fast_poisson_byte (prng,  keys        & 0xff, result++, table_8, table_32);
    prng = __fast_poisson_byte (prng, (keys >>  8) & 0xff, result++, table_8, table_32);
    prng = __fast_poisson_byte (prng, (keys >> 16) & 0xff, result++, table_8, table_32);
    prng = __fast_poisson_byte (prng, (keys >> 24),        result,   table_8, table_32);

    return (prng);
    
    /*    prn = prn << 8;
    prn = prn >> 24;

    if      (key >= 204) tmp = 0;
    else if (key >= 121) tmp = 1;
    else if (key >=  55) tmp = 2;
    else if (key >=  20) tmp = 3;
    else if (key >=   6) tmp = 4;
    else if (key >=   1) tmp = 5;
    else {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
    }

    *result++ = tmp;
    prn = prn << 8;
    key = prn >> 24;

    if      (key >= 204) tmp = 0;
    else if (key >= 121) tmp = 1;
    else if (key >=  55) tmp = 2;
    else if (key >=  20) tmp = 3;
    else if (key >=   6) tmp = 4;
    else if (key >=   1) tmp = 5;
    else {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
    }

    *result++ = tmp;
    prn = prn << 8;
    key = prn >> 24;

    if      (key >= 204) tmp = 0;
    else if (key >= 121) tmp = 1;
    else if (key >=  55) tmp = 2;
    else if (key >=  20) tmp = 3;
    else if (key >=   6) tmp = 4;
    else if (key >=   1) tmp = 5;
    else {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
    }

    *result   = tmp;
    */
    //return (prns_used);
    /*
    asm volatile ("mov %[tmp], #0\n\t"
		  "cmp %[key], #204\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #121\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #55\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #20\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #6\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");
		  L1:
    *result++ = tmp;
    prn = prn << 8;
    key = prn >> 24;
    
    if (key == 0) {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
	goto L2;
	}

    asm volatile ("mov %[tmp], #0\n\t"
		  "cmp %[key], #204\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #121\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #55\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #20\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #6\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");
L2:
    *result++ = tmp;
    prn = prn << 8;
    key = prn >> 24;
    
    if (key == 0) {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
	goto L3;
	}

    asm volatile ("mov %[tmp], #0\n\t"
		  "cmp %[key], #204\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #121\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #55\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #20\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #6\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");
L3:
    *result++ = tmp;
    prn = prn << 8;
    key = prn >> 24;
    
    if (key == 0) {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
	goto L4;
	}

    asm volatile ("mov %[tmp], #0\n\t"
		  "cmp %[key], #204\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #121\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #55\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #20\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  "cmp %[key], #6\n\t"
		  "addlo %[tmp], %[tmp], #1\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");
L4:
*result   = tmp;

return (prns_used);*/
}

/*
uint32_t fast_poisson_bytes (uint32_t* result, uint32_t* prng)
{
    __label__ L1, L2, L3, L4;
    register uint32_t prn = *prng++;
    register uint32_t tmp;
    register uint32_t key = prn >> 24;
    uint32_t prns_used = 1;

    if (key == 0) {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
	goto L1;
    }
      
    asm volatile ("mov %[tmp], #0\n\t"
		  "cmp %[key], #204\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L1]\n\t": : : "cc" : L1);

    asm volatile ("mov %[tmp], #1\n\t"
		  "cmp %[key], #121\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L1]\n\t": : : "cc" : L1);

    asm volatile ("mov %[tmp], #2\n\t"
		  "cmp %[key], #55\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");
    
    asm goto (    "bcs %l[L1]\n\t": : : "cc" : L1);

    asm volatile ("mov %[tmp], #3\n\t"
		  "cmp %[key], #20\n\t"
		      : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L1]\n\t": : : "cc" : L1);

    asm volatile ("mov %[tmp], #4\n\t"
		  "cmp %[key], #6\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L1]\n\t": : : "cc" : L1);

    asm volatile ("mov %[tmp], #5\n\t"
		  "cmp %[key], #1\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");
    
L1:
    *result++ = tmp;
    prn = prn << 8;
    key = prn >> 24;

    if (key == 0) {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
	goto L2;
    }

    asm volatile ("mov %[tmp], #0\n\t"
		  "cmp %[key], #204\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L2]\n\t": : : "cc" : L2);

    asm volatile ("mov %[tmp], #1\n\t"
		  "cmp %[key], #121\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L2]\n\t": : : "cc" : L2);

    asm volatile ("mov %[tmp], #2\n\t"
		  "cmp %[key], #55\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");
    
    asm goto (    "bcs %l[L2]\n\t": : : "cc" : L2);

    asm volatile ("mov %[tmp], #3\n\t"
		  "cmp %[key], #20\n\t"
		      : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L2]\n\t": : : "cc" : L2);

    asm volatile ("mov %[tmp], #4\n\t"
		  "cmp %[key], #6\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L2]\n\t": : : "cc" : L2);

    asm volatile ("mov %[tmp], #5\n\t"
		  "cmp %[key], #1\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

L2:
    *result++ = tmp;
    prn = prn << 8;
    key = prn >> 24;

    if (key == 0) {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
	goto L3;
    }

    asm volatile ("mov %[tmp], #0\n\t"
		  "cmp %[key], #204\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L3]\n\t": : : "cc" : L3);

    asm volatile ("mov %[tmp], #1\n\t"
		  "cmp %[key], #121\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L3]\n\t": : : "cc" : L3);

    asm volatile ("mov %[tmp], #2\n\t"
		  "cmp %[key], #55\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");
    
    asm goto (    "bcs %l[L3]\n\t": : : "cc" : L3);

    asm volatile ("mov %[tmp], #3\n\t"
		  "cmp %[key], #20\n\t"
		      : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L3]\n\t": : : "cc" : L3);

    asm volatile ("mov %[tmp], #4\n\t"
		  "cmp %[key], #6\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L3]\n\t": : : "cc" : L3);

    asm volatile ("mov %[tmp], #5\n\t"
		  "cmp %[key], #1\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

L3:
    *result++ = tmp;
    prn = prn << 8;
    key = prn >> 24;

    if (key == 0) {
        tmp = fast_poisson (fast_poisson_table, *prng++ >> 8);
	prns_used++;
	goto L4;
    }

    asm volatile ("mov %[tmp], #0\n\t"
		  "cmp %[key], #204\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L4]\n\t": : : "cc" : L4);

    asm volatile ("mov %[tmp], #1\n\t"
		  "cmp %[key], #121\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L4]\n\t": : : "cc" : L4);

    asm volatile ("mov %[tmp], #2\n\t"
		  "cmp %[key], #55\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");
    
    asm goto (    "bcs %l[L4]\n\t": : : "cc" : L4);

    asm volatile ("mov %[tmp], #3\n\t"
		  "cmp %[key], #20\n\t"
		      : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L4]\n\t": : : "cc" : L4);

    asm volatile ("mov %[tmp], #4\n\t"
		  "cmp %[key], #6\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

    asm goto (    "bcs %l[L4]\n\t": : : "cc" : L4);

    asm volatile ("mov %[tmp], #5\n\t"
		  "cmp %[key], #1\n\t"
		  : [tmp] "=r" (tmp) : [key] "r" (key) : "cc");

L4:
    *result   = tmp;

    return (prns_used);
    }*/


void test (uint32_t* result)
{
    uint32_t time, tmp, i, j, used, total = 0;
    uint32_t* timer_addr = (uint32_t*)(0x21000004);
    uint32_t min = 3000, max = 0;
    uint32_t randoms[1100];
    uint32_t *rp = randoms;

    for (i = 0; i < 1100; i++)
        randoms [i] = mars_kiss64_seed (seed);

    for (i = 0; i < 1024; i++) {
        asm volatile ("ldr %[time], [%[timer_addr]]\n\t"
		      : [time] "=r" (time)
		      : [timer_addr] "r" (timer_addr)
		      : "memory");
	
	rp = fast_poisson_bytes (rp+1, rp[0], result,
				 __fast_poisson_byte_table, fast_poisson_table);

	//for (j = 0; j < used; j++)	    randoms [j] = mars_kiss64_seed (seed);

	//(void)fast_poisson (fast_poisson_table, n);
	//n = poisson_dist_variate_exp_minus_lambda
	//         (mars_kiss64_seed, seed, 0.20189651799465540848);

	asm volatile ("ldr %[tmp], [%[timer_addr]]\n\t"
		      "sub %[time], %[time], %[tmp]\n\t"
		      : [tmp] "=r" (tmp), [time] "+r" (time)
		      : [timer_addr] "r" (timer_addr)
		      : "memory");
	time -= 4;
	total += time;
	if (time > max) max = time;
	if (time < min) min = time;
    }

    used = ((uint32_t)rp - (uint32_t)randoms) >> 2;

    asm volatile ("ldr %[time], [%[timer_addr]]\n\t"
		      : [time] "=r" (time)
		      : [timer_addr] "r" (timer_addr)
		      : "memory");
    
    for (j = 0; j < used; j++)
        randoms [j] = mars_kiss64_seed (seed);

    asm volatile ("ldr %[tmp], [%[timer_addr]]\n\t"
		      "sub %[time], %[time], %[tmp]\n\t"
		      : [tmp] "=r" (tmp), [time] "+r" (time)
		      : [timer_addr] "r" (timer_addr)
		      : "memory");
    time -= 4;
    total += time;
	
    io_printf (IO_BUF,
	       "fast_poisson x 1024 takes %u clock ticks"
	       "min/max = (%u, %u)\n"
	       "     including time for %u JKISS-64 PRNs used\n",
	       total, min, max, used);
}

void c_main (void)
{
    uint32_t* timer_addr = (uint32_t*)(0x21000000);
    uint32_t i, j;
    uint32_t result[4];
    uint32_t randoms[50];
    uint32_t* rp = randoms;

    timer_addr[0] = (uint32_t)(-1);
    timer_addr[2] = 0xC2;

    for (j = 0; j < 10; j++) {
      for (i = 0; i < 50; i++)
        randoms[i] = mars_kiss64_seed (seed);

      io_printf (IO_BUF, "prn = %x: {", randoms[0]);

      rp = fast_poisson_bytes (rp+1, *rp, result,
				 __fast_poisson_byte_table, fast_poisson_table);

      for (i = 0; i < 4; i++) {
	io_printf (IO_BUF, "%u", result[i]);
	if (i != 3) io_printf (IO_BUF, ", ");
      }
      io_printf (IO_BUF, "}\n");
    }
    
    test (result);

    io_printf (IO_BUF, "--\nPRN = %x\n--\n{", 0);

    for (i = 0; i < 4; i++) {
        io_printf (IO_BUF, "%u", result[i]);
	if (i != 3)
	    io_printf (IO_BUF, ", ");
    }
    io_printf (IO_BUF, "}\n--\n");


    /*
    test(3427828355);
 
    test (3427828354);
    test (3427828353);

    io_printf (IO_BUF, "--\n");
    test ((1 << 31));

    io_printf (IO_BUF, "--\n");
    test (2040406048);
    test (2040406047);
    test (2040406046);

    io_printf (IO_BUF, "--\n");
    test ((1 << 30));

    io_printf (IO_BUF, "--\n");
    test (930468202);
    test (930468201);
    test (930468200);

    io_printf (IO_BUF, "--\n");
    test ((1 << 29));

    io_printf (IO_BUF, "--\n");
    test (338501351);
    test (338501350);
    test (338501349);

    io_printf (IO_BUF, "--\n");
    test ((1 << 28));
    test ((1 << 27));

    io_printf (IO_BUF, "--\n");
    test (101714611);
    test (101714610);
    test (101714609);

    io_printf (IO_BUF, "--\n");
    test ((1 << 25));

    io_printf (IO_BUF, "--\n");
    test (25942854);
    test (25942853);
    test (25942852);

    io_printf (IO_BUF, "--\n");
    test ((1 << 24));
    test ((1 << 23));

    io_printf (IO_BUF, "--\n");
    test (5737052);
    test (5737051);
    test (5737050);

    io_printf (IO_BUF, "--\n");
    test ((1 << 21));

    io_printf (IO_BUF, "--\n");
    test (1118583);
    test (1118582);
    test (1118581);

    io_printf (IO_BUF, "--\n");
    test ((1 << 19));
    test ((1 << 18));

    io_printf (IO_BUF, "--\n");
    test (194889);
    test (194888);
    test (194887);

    io_printf (IO_BUF, "--\n");
    test ((1 << 17));
    test ((1 << 16));
    test ((1 << 15));

    io_printf (IO_BUF, "--\n");
    test (30677);
    test (30676);
    test (30675);

    io_printf (IO_BUF, "--\n");
    test ((1 << 14));
    test ((1 << 13));

    io_printf (IO_BUF, "--\n");
    test (4403);
    test (4402);
    test (4401);

    io_printf (IO_BUF, "--\n");
    test ((1 << 12));
    test ((1 << 11));
    test ((1 << 10));

    io_printf (IO_BUF, "--\n");
    test (581);
    test (580);
    test (579);

    io_printf (IO_BUF, "--\n");
    test ((1 << 9));
    test ((1 << 8));
    test ((1 << 7));

    io_printf (IO_BUF, "--\n");
    test (72);
    test (71);
    test (70);

    io_printf (IO_BUF, "--\n");
    test ((1 << 6));
    test ((1 << 5));
    test ((1 << 4));

    io_printf (IO_BUF, "--\n");
    test (9);
    test (8);
    test (7);

    io_printf (IO_BUF, "--\n");
    test (1);
    test (0);

    io_printf (IO_BUF, "--\n");

    
    io_printf (IO_BUF, "--\n");*/

}
