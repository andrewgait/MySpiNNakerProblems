/*
  A fast LIF neuron with exponential PSP shaping
*/

#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"

uint32_t time;

void     initialise_timer (void)  __attribute__ ((noinline));
void     start_timer      (void)  __attribute__ ((noinline));
void     stop_timer       (void)  __attribute__ ((noinline));

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

    time -= t+21;

    asm volatile ("pop {r1, r2, r3}\n\t" : : : "memory");

}

void print_voltage (uint32_t v)
{
    union {uint32_t u; int32_t i;} tmp;
    int v_i, v_f;
    int64_t long_temp;

    tmp.u = v;

    if (tmp.i >= 0)
        io_printf (IO_BUF, "t = %d", tmp.i);
    else {
        long_temp = ((int64_t)(-tmp.i) * 100000) / (int64_t)1686367527;
	v_i = (int)(long_temp / 10000);
	v_f = (int)(long_temp - v_i * 10000);
	v_i += 55;
	io_printf (IO_BUF, "-%2d.", v_i);
	if (v_f == 0)
	    io_printf (IO_BUF, "0000");
	else if (v_f < 10)
	    io_printf (IO_BUF, "000%d", v_f);
	else if (v_f < 100)
	    io_printf (IO_BUF, "00%d", v_f);
	else if (v_f < 1000)
	    io_printf (IO_BUF, "0%d", v_f);
	else
	    io_printf (IO_BUF, "%d", v_f);
    }
}

//! \brief The LIF dynamics for a single neuron update are coded here. This
//! includes the shaping of the PSP or synapse current as well. It is coded
//! in assembler for performance, both execution speed and code density.
//!
//! The resultant assembler has three parts: a header, a body with unfolded,
//! and a tail.
//!
//! The header is as follows, and stacks the used registers, as per the EABI
//! protocol. It also loads the constants from the kp argument.
//!
//!  4e4:       push    {r7, r8, r9, sl, fp, lr} ; stack used registers
//!  4e8:       ldr     r9, [r3]                 ; load k0
//!  4ec:       ldr     sl, [r3, #4]             ; load k1
//!  4f0:       ldr     fp, [r3, #8]             ; load k2
//!
//! The body consists of as many copies of the following twelve instructions
//! as it is deemed sensible to have.
//!
//!   4f4:       ldr     r3, [r1], #4            ; load input to temporary register r3
//!   4f8:       ldr     r8, [r2]                ; load psp current
//!   4fc:       ldr     r7, [r2, #4]            ; load voltage
//!   500:       add     r8, r3, r8              ; combine psp and input
//!   504:       cmp     r7, #0                  ; test original voltage, is refractory if r7 >= 0
//!   508:       smlawb  r8, r8, sl, r8          ; decay combined psp and input
//!   50c:       smlawb  r3, r7, r9, r7          ; decay voltage (due to voltage value)
//!   510:       smlawt  r3, r8, r9, r3          ; decay voltage (due to psp value)
//!   514:       str     r8, [r2], #4            ; store psp back now, post-incrementing
//!   518:       subslt  r3, r3, #16777216       ; if non-refractory subtract drift term from voltage
//!                                              ;    and also setting flags
//!   51c:       blge    678 <L_special>         ; branch-and-link to special handling sub-routine
//!                                              ;    if either the original voltage >= 0; or
//!                                              ;    the new voltage is >= 0.
//!   520:       str     r3, [r2], #4            ; store back the newly calculated voltage into
//!                                              ;    the neuron; post-incrementing
//!
//! Finally we have the tail part, which consists of the return (including unstacking
//! all the clobbered registers), and the special handling sub-routine.
//!
//!   674:       pop     {r7, r8, r9, sl, fp, pc}; unstack and return.
//!
//! <L_special>:
//!   678:       cmp     r7, #0                  ; re-test for refractory period
//!                                              ;     i.e. (original voltage >= 0)
//!   67c:       moveq   r3, fp                  ; if precisely zero, then assign reset voltage
//!                                              ;     from k2
//!   680:       subgt   r3, r7, #1              ; if original voltage > 0, then decrement
//!                                              ;     refractory counter
//!   684:       bxge    lr                      ; if original voltage >= 0, then return
//!                                              ; if we get to here the newly calculated voltage
//!                                              ;     must be >= 0, and thus we generate a spike
//!   68c:       mov     r3, #20                 ; Set refractory counter to 20
//!   690:       str     r2, [r0], #4            ; Store neuron pointer value in spike buffer
//!                                              ;     for later post-processing
//!   694:       bx      lr                      ; return to main neuron processing routine.

//! We assume that:
//!
//!    r0 holds the spike buffer pointer.
//!    r2 holds the neuron pointer
//!    r3 holds the input pointer
//!    r9 holds the 16-bit signed multiplier for PSP shaping
//!    r8 holds the two 16-bit signed multipliers for voltage adjustments
//!    sl holds the rest voltage
//!
//! Voltage/refractory representation
//! ----------------------------------
//!
//! During a refractory period the timer is decremented (or theoretically
//! incremented). During normal execution we begin by subtracting phi.b from
//! the voltage. If we treat positive voltages as if they were a refractory
//! counter, and negative ones as if they represent voltages and zero
//! represents either a spiking neuron or the end of a refractory period. Then
//! we can kill two birds with the one stone.
//!
//! If the voltage was already positive we are decrementing the timer. If the
//! voltage was negative, then we are subtracting phi.b.
//!
//!  2c:   ldm	r2, {fp, ip}
//!                          ;   load neuron variables (fp = psp, ip = voltage)
//!  30:   ldr	lr, [r3], #4
//!                          ;   load input
//!  34:   smlawb	fp, fp, r9, fp
//!                          ;   decay psp, (r9_lo = coefficient)
//!  38:   subs	ip, ip, #0x4000000
//!                          ;  subtract phi.b from voltage OR
//!                          ;     subtract refractory tick, set flags
//!  3c:   add	fp, lr, fp              ;   add input to psp
//!  40:   smlawbmi	ip, ip, r8, ip
//!                          ;   add voltage correction, if voltage is negative
//!  44:   smlawtmi	ip, fp, r8, ip
//!                          ;   add psp correction, if voltage is negative
//!  48:   moveqs	ip, sl
//!                          ;   if initial voltage == 0
//!                          ;     (refractory period over),
//!                          ;           load reset voltage, and set flags.
//!  4c:   cmpne	ip, #0;   compare current voltage to zero.
//!  50:   movpl	ip, #0x50000000
//!                          ; if voltage >= 0 (threshold), set refract period
//!  54:   strpl	r2, [r0], #4
//!                          ;   if voltage >= 0, store neuron pointer
//!                          ;         in spike buffer
//!  58:   stmia	r2!, {fp, ip}
//!                          ;   store neuron variables
//!
//! With an assumed spike rate of 10Hz and 0.1ms time-steps, we expect an
//! individual neuron to spike just once in every 1,000 iterations. Similarly,
//! we'd expect a neuron to be refractory just once every 1,000/20 = 50
//! iterations. Thus the chance of at least one or more neurons spiking is just
//! over 3%; detecting that no neurons spiked is simply testing that the spike
//! recorder word is 0. The chance that all 32 neurons are not refractory is
//! 47.6%.
//!
//! It is these probablities that dictate the policy of fixing-up the rare
//! cases (refractory, firing) afterwards.
//!
//! Obviously the code is just 12 instructions long; I _think_ it takes 14
//! cycles to execute. This is because ldm and stmia both take two cycles to
//! load/store their two arguments (making 14 cycles).
//!
//! Note 1: The explicit mention of r11 (elsewhere referred to as "%[p]"),
//!         and r12 (elsewhere referred to as "%[v]") prevents asm error
//!         messages about incorrect register ordering. Note also that we load
//!         p first and then modify its value; this avoids a delay slot.
//!
//!         As to why asm complains (even if p and v are forced into the
//!         correct order): who knows!
//!
//! Note 2: To make this work, the register variables p, and v have to be
//!         in registers r11 and r12 respectively.
//!
//! Note 3: This is declared as a macro, rather than as an inline function
//!         because a lot of variables are modified as a consequence of this
//!         code being executed. An inline function would attempt to
//!         preserve values between calls, thereby re-using old values.
//!
//! Note 4: Both the flags (cc) and memory are "clobbered" or changed by this
//!         code. The flags by the threshold detection, and memory by the
//!         write-back of the modified neuron values
//!
//! \param     ip  Input pointer (auto-incremented by instruction "ldr").
//! \param     np  Neuron Pointer (auto-incremented by instruction "stmia").
//! \param     tmp Input this time-step.
//! \param     p   PSP (shaped) current for this neuron (must be in r11)
//! \param     v   Voltage for this neuron (must be in r12)
//! \param     sp  The spike recording buffer
//! \param[in] k0  Multiplication constants for small multiplies
//! \param[in] k1  Multiplication constants for small multiplies
//! \param[in] k2  Reset Voltage
//!                instruction count.

#define __lif_dynamics()						\
  do {									\
      asm volatile ("ldr r3, [r1], #4\n\t"				\
                    "ldr r8, [r2]\n\t"					\
                    "ldr r7, [r2, #4]\n\t"				\
		    "add r8, r3, r8\n\t"				\
		    "cmp r7, #0\n\t"					\
		    "smlawb r8, r8, r10, r8\n\t"			\
		    "smlawb r3, r7, r9, r7\n\t"				\
		    "smlawt r3, r8, r9, r3\n\t"				\
		    "str r8, [r2], #4\n\t"				\
		    "sublts r3, r3, #0x1000000\n\t"			\
		    : : : "memory");					\
      asm goto     ("blge %l[L_special]\n\t" : : : "cc" : L_special);	\
      asm volatile ("str r3, [r2], #4\n\t"				\
		    : : : "memory");					\
    } while (false)


//! \brief The LIF dynamics are replicated 32 times. This exhausts the capacity
//! of the spike recording register s, and so is a convenient point to
//! re-introduce the loop overhead.

typedef struct {uint32_t psp; uint32_t v;} neuron_t, *neuron_ptr;

typedef struct {
      neuron_ptr* sp; // Out-going spike buffer
      uint32_t*   ip; // Pointer to a vector of input values to each neuron
      neuron_ptr  np; // Pointer to the neuronds still to be processed
      uint32_t*   kp; // Pointer to the constants required to process the neurons
} neuron_processing_state, *neuron_processing_state_ptr;



//! \brief This "function" is really two combined mini-branches for the
//! neuron_dynamics function. Note the "naked" attribute: this prevents the
//! standard function template being output.
//!
//! \param     r0  Spike Buffer
//! \param[in] r2  Neuron Pointer
//! \param     r3  Modified Voltage
//! \param[in] r7  Original Voltage
//! \param[in] r11 Constant: reset Voltage
//!
//!				        @ In a non-standard state
//!
//!	cmp     r7, #0			@ if original voltage >= 0: Refractory
//!     moveq   r3, r11			@ Reset voltage if previous test was 0
//!     subgt   r3, r7, #1		@ Alternatively decrement refractory
//!	bxge	lr  			@ Return if r7 >= 0,
//!					@     ... otherwise dropthrough
//!
//!	 			        @ To get here the modified voltage >= 0
//!                                     @    i.e we have a spike
//!	mov     r3, #20			@ Set refractory counter
//!     str     r2, [r0], #4		@ Store neuron address in spike counter
//!     bx      lr  	  		@ return to main processing


void neuron_dynamics (neuron_ptr* sp, uint32_t* ip, neuron_ptr  np, uint32_t* kp)
  __attribute__ ((noinline, naked));

void neuron_dynamics (neuron_ptr* sp, uint32_t* ip, neuron_ptr  np, uint32_t* kp)
{
    __label__ L_special;

    asm volatile ("push {r7, r8, r9, r10, r11, lr}\n\t"
		  "ldr  r9,  [r3]\n\t"
		  "ldr  r10, [r3, #4]\n\t"
		  "ldr  r11, [r3, #8]\n\t"
		  : : "r" (sp), "r" (ip), "r" (np), "r" (kp) : "memory");

    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    /*__lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();

    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();
    __lif_dynamics();  __lif_dynamics();  __lif_dynamics();  __lif_dynamics();*/

    asm volatile ("pop {r7, r8, r9, r10, r11, pc}\n\t" : : : "memory");

L_special:

    asm volatile ("cmp   r7, #0\n\t"
		  "moveq r3, r11\n\t"
		  "subgt r3, r7, #1\n\t"
		  "bxge	 lr\n\t"
		  "mov   r3, #20\n\t"
		  "str   r2, [r0], #4\n\t"
		  "bx    lr\n\t"
		  : : : "memory");
}

    //  4 loops gives
    //          74 cycles for normal       (18.5)
    //         118 cycles for spiking      (29.5)
    //         106 cycles for refractory   (26.5)
    //                                    -------
    //                                   =  18.671 at 10 Hz
    //  8 loops gives
    //         122 cycles for normal       (15.25)
    //         210 cycles for spiking      (26.25)
    //         186 cycles for refractory   (23.25)
    //                                    -------
    //                                   =  15.421 at 10 Hz
    // 16 loops gives
    //          218 cycles for normal       (13.625)
    //          394 cycles for spiking      (24.625)
    //          346 cycles for refractory   (21.625)
    //                                    -------
    //                                   =   13.796 at 10 Hz
    // 32 loops gives
    //         410 cycles for normal       (12.8125)
    //         794 cycles for spiking      (23.8125)
    //         666 cycles for refractory   (20.8125)
    //                                    ----------
    //                                  =   12.9835  at 10 Hz


uint32_t neuron_parameter[]
    = {0x4000FD74, // representing +25 hi; -652 low
       0x0000F384, // representing -3196 lo
       (uint32_t)(-1686367527)};     // representing the reset voltage -65mV


void c_main (void)
{
    register uint32_t i, j;
    neuron_t   n[32];         // neuron
    uint32_t   in[32];    // input buffer
    neuron_ptr s[32];    // spike buffer
    //neuron_ptr* new_sp;
    neuron_ptr  np = n;
    neuron_ptr* sp = s;
    uint32_t*   ip = in;
    uint32_t*   kp = in;

    initialise_timer ();

    for (i = 0; i < 32; i++) {
        ip[i]     = 0x70000000;
	sp[i]     = 0;
	n[i].psp = 0;
	n[i].v   = (uint32_t)(-1);//20; // start of refractory period
    }
	kp = neuron_parameter;

    uint32_t runtime = 1000; // 30;
    for (i = 0; i < runtime; i++) {
      if (i > 0)
	  for (j = 0; j < 32; j++)
	      ip[j] = 0;

      /*if (i % 10 == 0)*/ {
		io_printf (IO_BUF, "  t = %3d.%d: v = ", i/10, i%10);
		print_voltage (n[0].v);
		//io_printf (IO_BUF, "\n");
		io_printf (IO_BUF, " [%x], psp = %u\n", n[0].v, n[0].psp);
      }

      start_timer ();
      neuron_dynamics (sp, ip, np, kp);
      stop_timer ();

      io_printf (IO_BUF, "  time = %d\n", time);


      /*if (s != state.sp)
	io_printf (IO_BUF, "*** Neuron %u Spikes at t = %3d.%d\n",
	((uint32_t)(s[0]) - (uint32_t)(n))/8, i/10, i%10);*/
    }

    io_printf (IO_BUF, " end t = %3d.%d: v = ", i/10, i%10);
    print_voltage (n[0].v);
    io_printf (IO_BUF, " [%x], psp = %u\n", n[0].v, n[0].psp);

}
