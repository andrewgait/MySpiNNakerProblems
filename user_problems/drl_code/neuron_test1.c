/*
  An LIF neuron with 32x16 DSP multiplication for accuracy comparison.
*/

#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"

//! This routine performs an unsigned 32x32 -> 32 decay with rounding.
//! It corrupts register r1.

static inline uint32_t __umlal (uint32_t x, uint32_t m)
{
  register uint32_t result;
  register uint32_t tmp;

  asm volatile ("mov   %[tmp], #1               @ Set up the required rounding \n"
		"umlal %[x], %[tmp], %[x], %[m] @ \n");

  return (result);
}

//! following code executes in 7 cycles.

#define lif_dc_accurate() asm volatile					    \
  ("cmp    %[v], #0                    @ Test whether refractive        \n" \
   "umull  r0, r1, %[v], %[e0]         @ calculate the decay term       \n" \
   "addpl  r1, %[current], r1, lsr #31 @ add current to rounding        \n" \
   "addpls r0, r0, r1                  @ add the decay term             \n" \
  )

//! This routine prints the synaptic weight in pA according to our chosen
//! scaling factor; in this case 0.1. In other words an integer of 10
//! represents a current of 1pA.
//!
//! \param[in] w The weight to be printed.

void print_synapse_weight (int w)
{
  w = (w << 15) + 5;
  w = w / 10;

  io_printf (IO_BUF, "%k", kbits (w));
}

//! This routine prints the synaptic current in nA according to our chosen
//! scaling factor; in this case 0.0004. In other words an integer of 81,920
//! represents a current of 0.001nA (or 1 pA).
//!
//! \param[in] p The synaptic current gsyn to be printed

void print_gsyn (int p)
{
  p = (p << 2);
  p = p / 10;

  io_printf (IO_BUF, "%k", kbits (p));
}

//! This routine prints the voltage in mV according to our chosen scaling
//! factor and threshold; in this case 0.0004. In other words an integer of 81,920
//! represents a current of 0.001nA (or 1 pA).
//!
//! \param[in] p The synaptic current gsyn to be printed

void print_volt (int v)
{
  int64_t tmp = ((int64_t)v) << 2;

  tmp = tmp / 13863;
  v = (int)tmp;
  

  io_printf (IO_BUF, "%k", kbits (v - (50 << 15)));
}

//void fixup (){}


int t_ref   = 30;

#define v_reset (-1703488011)

//! Implements an LIF neuron with _one_ exponentially decayed synapse type.
//!
//! \param[in] np Neuron Pointer
//! \param[in] ip Input Pointer

void neuron (int* np, int* ip, int t)
{
  int v = np[0];
  int p = np[1];
  int r = np[2];
  int i = ip[0];

  if (r == 0) { // non-refractory
    v  = __smlawb (v, -652, v);
    //v += 33562215; // = 0.4*7449*2^13 WAS: 7449 << 12;
    //v += 33669458; // = (7449 << 12) * 40 * (1 - exp (-0.01))/b10
    v += 33670998; // = (7449.3408203125 << 12) * 40 * (1 - exp (-0.01))/b10
    //v += p >> 1;
    v -= 16947543;

    //p  = __smlawb (p, -11880, p);
    //p += i << 13;

    if (v >= 0) { // spiked
      io_printf (IO_BUF, "%3d", t / 10);
      io_printf (IO_BUF, ".%1d voltage is ", t % 10);
      print_volt (v);
      io_printf (IO_BUF, "\n");

      v = v_reset;
      r = t_ref-1;
    }
    np[0] = v;
    np[1] = p;
    np[2] = r;
  }
  else { // refractory
    p  = __smlawb (p, -11880, p);
    p += i << 13;

    //np[1] = p;
    np[2] = r-1;

  }
}

int ip[1] = {878};
int np[3] = {v_reset, 0, 0};

void c_main (void)
{

  int t;

  for (t = 0; t <= 301; t++) {
    io_printf (IO_BUF, "%3d", t / 10);
    io_printf (IO_BUF, ".%1d [", t % 10);
    print_volt (np[0]);
    io_printf (IO_BUF, ", ");
    print_gsyn (np[1]);
    io_printf (IO_BUF, "]\n");

    neuron (np, ip, t);
  }
}

/*{
  int w = 878;         // = 87.8 pA
  int p = 39723020;    // = 0.484900146484375 nA
  int v = -1703488011; // = -65mV

  io_printf
    (IO_BUF,
     "A synaptic weight of 87.8pA is represented by %d, and prints as: ",
     w);
  print_synapse_weight (w);
  io_printf (IO_BUF, "\n");

  io_printf
    (IO_BUF,
     "A synaptic current of 484.900146 pA is represented by %d, and prints as: ",
     p);
  print_gsyn (p);
  io_printf (IO_BUF, "\n");
  
  io_printf
    (IO_BUF,
     "A voltage of -65mV is represented by %d, and prints as: ",
     v);
  print_volt (v);
  io_printf (IO_BUF, "\n");
  }*/
