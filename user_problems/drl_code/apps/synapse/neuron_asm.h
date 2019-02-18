/*

The ODE solver needed for the LIF-current neuron can be implemented as a matrix exponential.

If we have a single time-constant for synapses -- and it is different to the membrane time-constant --
then for the following ODE:

    x' = A(t) x + b

the evolution is described by:

    x (t+dt) = exp (dt A) (x(t) - b)


Note also that

    exp [ a  b ]  = [ e^a  b (e^a - e^c)/ (a-c) ]        provided a /= c
        [ 0  c ]    [  0          e^c           ]

                  = [ e^a  b e^a ]                       if a = c
                    [  0    e^a  ] 






  A fast LIF synapse processing

  end: 1160
start: 036c
-----------
        ef4   = 3828 bytes.


These are coefficients

Vreset = -65.0 mV
Vthresh = -50.0 mV
Vrest = -65.0 mV
R = 40.0,  MOhm
I0 = 0.0878    = 87.8 pA
\[Tau]I = 0.5,  mS
v0 = -65.0,  mV
Tref = 2.0,  mS
\[Tau]RC = 10.0  mS


firing every 0.1ms after the start

With[{Vreset = -65.0, Vthresh = -50.0, Vrest = -65.0, R = 40.0, 
  I0 = 0.0878, \[Tau]I = 0.5, v0 = -65.0, 
  Tref = 2.0, \[Tau]RC = 10.0, tmax = 100.0},
 lif = NDSolve[{v'[t] == 
     If[ t >= trest[t], ((Vrest - v[t]) + i[t] R )/ \[Tau]RC , 0], 
    i'[t] == -i[t]/\[Tau]I, v[0] == v0, i[0] == 0.0, trest'[t] == 0, 
    trest[0] == 0, 
    WhenEvent[
     v[t] >= Vthresh, {v[t] -> Vreset, 
      trest[t] -> Evaluate[ t + Tref], Print[t]} ], 
    WhenEvent[Mod[ t, 0.1 ] == 0, {i[t] -> i[t] + I0 }]}, {v[t], 
    i[t]}, {t, 0, tmax}, AccuracyGoal -> 20, PrecisionGoal -> 20, 
   WorkingPrecision -> 35, MaxSteps -> Infinity]; 
 Plot[{(*Evaluate[i[t]/.lif],*)Evaluate[v[t] /. lif]}, {t, 0, tmax}, 
  ImageSize -> Large, PlotRange -> Full, PlotLegends -> {"V"}]]



On 23 Oct 2018, at 11:38, David Lester <david.r.lester@manchester.ac.uk> wrote:

Of course for one extra instruction I can give you a decay multiplier of: 20867/(2*1024*1024), with a right shift of 5.



*/

#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"
#include <debug.h>

void refractory_or_spiking_neuron (void) asm ("refractory_or_spiking_neuron") __attribute__ ((noinline, naked));
void __spiking_neuron             (void) asm ("__spiking_neuron")             __attribute__ ((noinline, naked));


//! \brief This code fragment performs a neuron update.



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
//!  2c:   ldm  r2, {fp, ip}
//!                          ;   load neuron variables (fp = psp, ip = voltage)
//!  30:   ldr  lr, [r3], #4
//!                          ;   load input
//!  34:   smlawb       fp, fp, r9, fp
//!                          ;   decay psp, (r9_lo = coefficient)
//!  38:   subs ip, ip, #0x4000000
//!                          ;  subtract phi.b from voltage OR
//!                          ;     subtract refractory tick, set flags
//!  3c:   add  fp, lr, fp              ;   add input to psp
//!  40:   smlawbmi     ip, ip, r8, ip
//!                          ;   add voltage correction, if voltage is negative
//!  44:   smlawtmi     ip, fp, r8, ip
//!                          ;   add psp correction, if voltage is negative
//!  48:   moveqs       ip, sl
//!                          ;   if initial voltage == 0
//!                          ;     (refractory period over),
//!                          ;           load reset voltage, and set flags.
//!  4c:   cmpne        ip, #0;   compare current voltage to zero.
//!  50:   movpl        ip, #0x50000000
//!                          ; if voltage >= 0 (threshold), set refract period
//!  54:   strpl        r2, [r0], #4
//!                          ;   if voltage >= 0, store neuron pointer
//!                          ;         in spike buffer
//!  58:   stmia        r2!, {fp, ip}
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

/*
asm volatile ("ldm       r2, {fp, ip}       @  load neuron variables (fp = psp, ip = voltage)\n\t"\
	      "ldr       lr, [r3], #4       @   load input\n\t"			\
	      "smlawb    fp, fp, r9, fp     @   decay psp, (r9_lo = coefficient)\n\t"	\
	      "subs      ip, ip, #0x4000000 @ subtract phi.b from voltage OR\n\t" \
	      "                             @     subtract refractory tick, set flags\n\t"	\
	      "add       fp, lr, fp         @   add input to psp\n\t"	\
	      "smlawbmi  ip, ip, r8, ip     @   add voltage correction, if voltage is negative" \
	      "smlawtmi  ip, fp, r8, ip     @   add psp correction, if voltage is negative" \
	      "moveqs    ip, sl             @   if initial voltage == 0\n\t" \
	      "                             @     (refractory period over),\n\t" \
	      "                             @           load reset voltage, and set flags.\n\t" \
	      "cmpne     ip, #0             @   compare current voltage to zero.\n\t" \
	      "movpl     ip, #0x50000000    @ if voltage >= 0 (threshold), set refract period\n\t"	\
	      "strpl     r2, [r0], #4       @   if voltage >= 0, store neuron pointer\n\t"	\
	      "                             @         in spike buffer\n\t"	\
	      "stmia     r2!, {fp, ip}      @   store neuron variables\n\t"	\
	      );
*/

// r3 = kp = constant pointer
// r2 = np
// r1 = input p
// r0 = sp = spike i.e. output pointer

//=============================================================================
// We define the register allocation suitable for the neuron processing.
//=============================================================================

#define USE_NEURON_REGISTERS()						                     \
  do {asm volatile ("@ spoof register use\n\t" : : "r" (ctrl), "r" (np), "r" (in), "r" (v),  \
		    "r" (c), "r" (k2), "r" (k1), "r" (phi), "r" (n), "r" (minus1) : "cc");   \
  } while (false)

//! \brief The following macro allows us to define _in_one_place_ the register
//! names and locations used by the various pieces of neuron manipulation code.
//!
//! It also hides a piece of non-code-generating code that "uses" all of these
//! registers, as most code fragments don't use _all_ the registers.
//!
//! It may be that omitting this "asm" statement becomes necessary later.

#define NEURON_REGISTER_MAP                                                                   \
  register uint32_t* ctrl      asm ("r12"); /* control and constant access                 */ \
  register uint32_t* np        asm ("r11"); /* Pointer to next neuron structure            */ \
  register uint32_t* in        asm ("r10"); /* Pointer to input ring-buffer elements       */ \
  register uint32_t  v         asm ("r9");  /* Current neuron voltage                      */ \
  register uint32_t  c         asm ("r8");  /* Current neuron post-synaptic-current (PSC). */ \
  register uint32_t  k2        asm ("r7");  /* Coefficients                                */ \
  register uint32_t  k1        asm ("r6");  /* Coefficients                                */ \
  register uint32_t  phi       asm ("r5");  /* Value of phi.b                              */ \
  register uint32_t  n         asm ("r4");  /* number of neurons still to be processed     */ \
  register uint32_t  minus1    asm ("r2");  /* minus one, easily reconstructed with mov    */ \
                                                                                              \
  USE_NEURON_REGISTERS()

//! \brief We assume that the control register has already been set, and that
//! any registers used in the preceeding code that need preservation have been.
//!
//! Note, in order that this macro can be used anywhere, we will not use the
//! register names defined above in NEURON_REGISTER_MAP.

#define set_neuron_registers_and_branch()				                                                   \
    do {asm volatile ("ldr r11, [%[ctrl], %[np_off]]         @ np: Load up the np register                           \n\t" \
		      "ldr r10, [%[ctrl], %[tb_off]]         @ in: Load up the time_base  - suitably rotated it      \n\t" \
		      "ror r10, r10, #18                     @ .. becomes the base address for the current ring-     \n\t" \
		      "                                      @    buffer elements to be used as inputs.              \n\t" \
		      "ldr r7,  [%[ctrl], %[k2_off]]         @ k2: Load up coefficients                              \n\t" \
		      "ldr r6,  [%[ctrl], %[k1_off]]         @ k1: Load up coefficients                              \n\t" \
		      "ldr r5,  [%[ctrl], %[phi_off]]        @ phi: Load up phi.b                                    \n\t" \
		      "ldr r4,  [%[ctrl], %[nl_off]]         @ nn: Load up number of neuron loops                    \n\t" \
		      "ldr r0,  [%[ctrl], %[neuron_start]]   @ Load up neuron processing start address               \n\t" \
		      "mov r2, #-1                           @ minus one                                             \n\t" \
		      "bx  r0                                @ Jump to correct start address                         \n\t" \
		      "@---------------------------------------------------------------------------------------------\n\t" \
		      "@ Note that this can be made more efficient if we can directly branch to the start address.   \n\t" \
		      "@ This should be possible in assembler since it is an address in text memory formed by an     \n\t" \
		      "@ compile-time constant offset from a constant -- but relocatable -- label.                   \n\t" \
		      "@---------------------------------------------------------------------------------------------\n\t" \
		    : : [ctrl] "r" (ctrl),                                                                                 \
		      [np_off] "J" (NEURON_VARIABLES_OFFSET), [tb_off] "J" (TIME_BASE), [phi_off] "J" (NEURON_PHI_OFFSET), \
		      [k2_off] "J" (NEURON_PSC_COEFFICIENTS_2), [k1_off] "J" (NEURON_PSC_COEFFICIENTS_1),                  \
		      [nl_off] "J" (NEURON_NUMBER_LOOPS_OFFSET), [neuron_start] "J" (NEURON_LOOP_START_OFFSET));           \
      } while (false)

//! \brief At the end of the neuron processing loop we might need to save neuron
//! registers; in fact we don't, but we reserve a way to save things if needed.

#define save_neuron_registers() do { } while (false)

//! \brief This is the decrement and loop if non-negative code used inside the
//! neuron loop code.

#define neuron_loop_decrement_and_test()					                              \
  do {asm volatile ("subs %[n], %[n], #1     @ decrement and test the 'loop counter'                    \n\t" \
		    "                        @   (actually the number of neurons to be processed -1)    \n\t" \
		    "bpl  neuron_loop        @ If the number is still non-negative then loop again      \n\t" \
		    : [n] "=r" (n) : : "cc");				                                      \
  } while (false)


//! \brief A support function that handles the special cases occuring when a
//! neuron is not evolving according to the ODE, but instead is either in a
//! refactory period (most common, by a factor of twenty) or has just spiked.
//!
//! \param[in] ctrl Provides access to the reset value for voltage
//! \param[in] r0   Temporary register holding the initial value of the voltage.
//!                   If this is negative, then the neuron has just spiked.
//! \param     v    The current value of the voltage. If we have not just
//!                   spiked, then we are using this as a refractory count-
//!                   down timer. When it reaches 0, we reset the voltage.

void __refractory_or_spiking_neuron (void)
{
    NEURON_REGISTER_MAP;

    asm volatile ("cmp  r0, #0                       @ If the initial voltage (which is still held in r0) is ..  \n\t"
		  "bmi  __spiking_neuron             @  .. negative, then we have just spiked. Branch forward.   \n\t"
		  "cmp  %[v], #0                     @ If the current voltage is also positive, then the ..      \n\t"
		  "                                  @  .. refractory period is still in progress                \n\t"
		  "bxgt lr                           @  .. so just return                                        \n\t"
		  "                                  @  .. otherwise, the refractory period is finished          \n\t"
		  "ldr  %[v], [%[ctrl], %[v_reset]]  @ Load reset voltage                                        \n\t"
		  "bx   lr                           @ Return                                                    \n\t"
		  : [v] "=r" (v) : [ctrl] "r" (ctrl), [v_reset] "J" (V_RESET_OFFSET) : "cc", "memory");
}

//! A support function that handles the special case occuring when a neuron has
//! just spiked. We need to record this fact in the outspike buffer, and set
//! the voltage to act as a refractory counter.

void __spiking_neuron (void)
{
    NEURON_REGISTER_MAP;

    asm volatile ("ldr    r0,   [%[ctrl], %[outspike]]    @ Load outspike pointer                    \n\t"
		  "ldr    r1,   [%[ctrl], %[neuron]]      @ neuron base address                      \n\t"
		  "ldr    %[v], [%[ctrl], %[refractory]]  @ Reset refractory timer                   \n\t"
		  "rsb    r1, %[np], r1                   @ subtract the base address from np        \n\t"
		  "lsr    r1, r1, #3                      @ divide by size of neuron (8 = 2^3)       \n\t"
		  "strb   r1, [r0], #1                    @ Add neuron index byte to outspike buffer \n\t"
		  "str    r0,   [%[ctrl], %[outspike]]    @ Save updated outspike pointer            \n\t"
		  "bx     lr                              @ Return                                   \n\t"
		  : [v] "=r" (v) : [ctrl] "r" (ctrl), [np] "r" (np), [neuron] "J" (NEURON_VARIABLES_OFFSET),
		    [refractory] "J" (REFRACTORY_OFFSET), [outspike] "J" (OUTSPIKE_OFFSET)  : "memory");
}


//! \brief This is the neuron dynamics of an LIF neuron with exponentially
//! decaying current-based synapse PSCs. This code implements a 2x2 matrix
//! ODE propogation on the two variables v (voltage) and c (post-synaptic
//! current). In NEST the 2x2 matrix is labelled as [[P_22, P_21],[0, P_11]];
//! we use the bottom of k1 to hold P_11, and k2 holds {P_22, P_21}, all as
//! signed 16-bit half-words. The evolution is:
//!
//!    [v_t+1; c_t+1] = P [v_t; c_t] + phi . [b_0; b_1]
//!
//! The vector b = [b_0; b_1] represents the drift term; with currents
//! both having the same time-constnat and tending to zero: b_1 = 0.
//!
//! Options
//! -------
//!
//! If LIF_BIG_CURRENTS is defined, then we scale the input currents in a four-
//! to-one ratio of inhibitory to excitatory currents, and leave the precise
//! scaling to the most-signficant 16-bit halfword in k0, when the PSC is
//! combined into the voltage.
//!
//! Otherwise we can utilise a per-neuron scaling, but the limitation is that
//! the scaling factor must lie between -1/2 and +1/2, which may not be ideal.
//!
//! Performance
//! -----------
//!
//! The main body consists of 17 instructions, and takes 17 cycles to execute.
//!
//! Register Usage
//! --------------
//!
//! \param[in] k1     A pair of signed 16-bit half words for use in 32x16
//!                     multiplications.
//! \param[in] k2     A pair of signed 16-bit half words for use in 32x16
//!                     multiplications.
//! \param[in] phi    Represents phi.b.
//! \param[in] minus1 Is: -1. Used to reset ring-buffer elements after
//!                     processing.
//! \param     np     Points to the neuron parameters v and c
//! \param     in     Points to the ring-buffer elements
//! \param     v      A neuron's voltage
//! \param     c      A neuron's post-synaptic current


#define neuron_dynamics()                                                                                                \
  do {asm volatile ("ldr      %[c], [%[np], #4]              @ Load neuron's PSC                                   \n\t" \
		    "ldrh     r0, [%[in]]                    @ Load inhibitory ring-buffer value to r0.            \n\t" \
		    "smlawb   %[c], %[c], %[k1], %[c]        @ decay the c.                                        \n\t" \
		    "ldrh     r1, [%[in], #2]                @ Load excitatory ring-buffer value to r1.            \n\t" \
		    "rsb      r0, r0, %[minus1], lsr #16     @ correct value of ring-buffer element in r0          \n\t" \
		    "add      %[c], %[c], r0, lsl #8         @ accumulate excitatory input                         \n\t" \
		    "ldr      r0, [%[np]]                    @ Load neuron's membrane voltage                      \n\t" \
		    "rsb      r1, r1, %[minus1], lsr #16     @ correct value of ring-buffer element in r1          \n\t" \
		    "sub      %[c], %[c], r1, lsl #10        @ accumulate inhibitory input (4x)                    \n\t" \
		    "subs     %[v], r0, %[phi]               @ Subtract phi.b from voltage OR ..                   \n\t" \
		    "                                        @  .. subtract refractory tick, set flags             \n\t" \
		    "smlawbmi %[v], %[v], %[k2], %[v]        @ decay voltage                                       \n\t" \
		    "addmi    %[v], %[v], %[c]               @ combine input into voltage                          \n\t" \
		    "str      %[minus1], [%[in]], #4         @ write-back reset value (-1) of ring buffer          \n\t" \
		    "cmpmi    %[v], #0                       @ if initial voltage was negative (subs instruction): \n\t" \
		    "                                        @ then compare voltage now to zero                    \n\t" \
		    "blpl     __refractory_or_spiking_neuron @ if initial or final voltage >= 0, then jump to      \n\t" \
		    "                                        @    special case code to emit spike and reset or     \n\t" \
		    "                                        @    decrement refractory counter                     \n\t" \
		    "str      %[c], [%[np], #4]              @ write-back psp                                      \n\t" \
		    "str      %[v],   [%[np]], #8            @ write-back voltage                                  \n\t" \
		    : [v] "=r" (v), [c] "=r" (c), [np] "+r" (np), [in] "+r" (in)                                         \
		    : [k1] "r" (k1), [k2] "r" (k2), [phi] "r" (phi), [minus1] "r" (minus1)	                         \
		    : "cc", "memory");	                                                                                 \
    } while (false)

/*#else
  #define neuron_dynamics()                                                                                                \
  do {asm volatile ("ldr      %[c], [%[np], #4]              @ Load neuron's PSC (c)                               \n\t" \
		    "ldrh     r0, [%[in]]                    @ Load inhibitory ring-buffer values to r0.           \n\t" \
		    "smlawb   %[c], %[c], %[k2], %[c]        @ decay the PSC.                                      \n\t" \
		    "ldr      r2, [%[np]]                    @ Load neuron's membrane voltage                      \n\t" \
		    "ldrh     r1, [%[in], #2]                @ Load excitatory ring-buffer values to r1.           \n\t" \
		    "subs     %[v], r2, %[phi]               @ Subtract phi.b from voltage OR ..                   \n\t" \
		    "                                        @  .. subtract refractory tick, set flags             \n\t" \
		    "smlawb   r0, r0, %[k2], %[c]            @ scale the inhibitory current, and combined with PSC \n\t" \
		    "smlawt   %[c], r1, %[k2], r0            @ scale the excitatory, and combine with inhibitory   \n\t" \
		    "smlawbmi r0, %[c], %[k0], %[v]          @ decay PSC, and combined with voltage                \n\t" \
		    "smlawtmi %[v], %[v], %[k0], r0          @ decay voltage and combine                           \n\t" \
		    "str      %[c], [%[np], #4]              @ write-back c                                        \n\t" \
		    "cmpmi    %[v], #0                       @ if initial voltage was negative (subs instruction): \n\t" \
		    "                                        @ then compare voltage now to zero                    \n\t" \
		    "blpl     __refractory_or_spiking_neuron @ if initial or final voltage >= 0, then jump to      \n\t" \
		    "                                        @    special case code to emit spike and reset or     \n\t" \
		    "                                        @    decrement refractory counter                     \n\t" \
		    "str      %[v],   [%[np]], #8            @ write-back voltage                                  \n\t" \
		    "str      %[minus1], [%[in]], #4         @ write-back reset value (-1) of ring buffer          \n\t" \
		    : [v] "=r" (v), [c] "=r" (c), [np] "+r" (np), [in] "+r" (in)                                         \
		    : [k1] "r" (k1), [k2] "r" (k2), [phi] "r" (phi), [minus1] "r" (minus1)	                         \
		    : "cc", "memory");	                                                                                 \
    } while (false)
    #endif*/

/* 16 cycles -- and includes random input as well.
"ldrh     r0, [%[rn]], #2                @ Load random input                                   \n\t" \
"ldrh     r2, [%[in]]                    @ Load ring-buffer value to r1.                       \n\t" \
"ldrh     r1, [%[in], #2]                @ Load ring-buffer value to r2.                       \n\t" \
"ldr      %[c], [%[np], #4]              @ Load neuron's PSC (c)                               \n\t" \
"add      r0, r0, r2                     @ add excitatory and random values ...                \n\t" \
"smlawb   %[c], %[c], %[k], %[c]         @ decay the PSC.                                      \n\t" \
"ldr      r2, [%[np]]                    @ Load neuron's membrane voltage                      \n\t" \
"sub      r0, r0, r1                     @  ... subtract inhibitory values                     \n\t" \
"add      %[c], %[c], r0, asl #18        @ combine with decayed PSC value in c                 \n\t" \
"subs     %[v], r2, %[phi]               @ Subtract phi.b from voltage OR ..                   \n\t" \
"                                        @  .. subtract refractory tick, set flags             \n\t" \
"smlawtmi %[v], %[v], %[k], %[v]         @ decay voltage and combine                           \n\t" \
"str      %[c], [%[np], #4]              @ write-back c                                        \n\t" \
"addsmi   %[v], %[c], %[v]               @ combine PSC and voltage   .. and ..                 \n\t" \
"                                        @ if initial voltage was negative (subs instruction): \n\t" \
"                                        @ then compare voltage now to zero                    \n\t" \
"blpl     __refractory_or_spiking_neuron @ if initial or final voltage >= 0, then jump to      \n\t" \
"                                        @    special case code to emit spike and reset or     \n\t" \
"                                        @    decrement refractory counter                     \n\t" \
"str      %[v],   [%[np]], #8            @ write-back voltage                                  \n\t" \
"str      %[minus1], [%[in]], #4         @ write-back reset value (-1) of ring buffer          \n\t" \
: [v] "=r" (v), [c] "=r" (c), [np] "+r" (np), [in] "+r" (in)		\
: [k] "r" (k), [phi] "r" (phi), [minus1] "r" (minus1)	\
: "cc", "memory");

 */

/*

//#define NEURON_REGISTER_MAP                                                                   \
//  register uint32_t* ctrl      asm ("r12");  control and constant access                 *
//  register uint32_t* np        asm ("r11");  Pointer to next neuron structure            *
//  register uint32_t* in        asm ("r10");  Pointer to input ring-buffer elements       *
//  register uint16_t* rp        asm ("r9");   Pointer to random numbers                   *
//  register uint32_t  n         asm ("r8");   number of neurons still to be processed     *
//  register uint32_t  c         asm ("r7");   Current neuron current                      *
//  register uint32_t  k         asm ("r6");   Coefficients                                *
//  register uint32_t  phi       asm ("r5");   Value of phi.b                              *
                                                                                              \
// single 32-bit input
//=====================
// 10 cycles  plus branch & link (if needed) every four loops = 41 cycles per quad -- with random number
// input (but not reset)

"ldr      %[c], [%[np], #4]              @ Load neuron's PSC (c)                               \n\t" \
"ldr      lr, [%[in], #4]                @ Load ring-buffer value to link register.            \n\t" \
"smlawb   %[c], %[c], %[k], %[c]         @ decay the PSC.                                      \n\t" \
"ldr      r0, [%[np]]                    @ Load neuron's membrane voltage                      \n\t" \
"add      %[c], %[c], lr, asl #18        @ combine input with decayed PSC value in c           \n\t" \
"subs     r0, r0, %[phi]                 @ Subtract phi.b from voltage OR ..                   \n\t" \
"                                        @  .. subtract refractory tick, and set flags         \n\t" \
"smlawtmi r0, r0, %[k], r0               @ decay voltage                                       \n\t" \
"str      %[c], [%[np], #4]              @ write-back c                                        \n\t" \
"addsmi   r0, r0, %[c]                   @ combine PSC and voltage   .. and ..                 \n\t" \
"                                        @ if initial voltage was negative (subs instruction): \n\t" \
"                                        @ then compare voltage now to zero                    \n\t" \
"strmi    r0, [%[np]], #8                @ write-back voltage                                  \n\t" \

"blpl     __refractory_or_spiking_neuron @ if initial or final voltage >= 0, then jump to      \n\t" \
"                                        @    special case code to emit spike and reset or     \n\t" \
"                                        @    decrement refractory counter                     \n\t" \

: [c] "=r" (c), [np] "+r" (np), [in] "+r" (in) : [k] "r" (k), [phi] "r" (phi) : "cc", "memory");



// 14 cycles  plus branch & link (if needed) every four loops = 57 cycles per quad -- with random number
// input, but no reset (so needed immediately afterwards).

"ldr      %[c], [%[np], #4]              @ Load neuron's PSC (c)                               \n\t" \
"ldr      lr, [%[in]], #4                @ Load ring-buffer value to link register.            \n\t" \
"smlal    half, %[c], %[k_p], %[c]       @ super-accurate takes 3 cycles; has interlock        \n\t" \

=================== 3cycles

"ldr      r0, [%[np]]                    @ Load neuron's membrane voltage                      \n\t" \
"add      %[c], %[c], lr, asl #18        @ combine with decayed PSC value in c                 \n\t" \
"subs     r0, r0, %[phi]                 @ Subtract phi from voltage, setting flags.           \n\t"
"                                        @  .. phi is a pun for:  phi.b OR refractory tick     \n\t" \
"smlalmi  half, r0, %[k_v], r0           @ decay voltage                                       \n\t" \

=================== 3cycles

"str      %[c], [%[np], #4]              @ write-back c                                        \n\t" \
"addsmi   r0, r0, %[c], lsr? ??          @ combine PSC and voltage   .. and ..                 \n\t" \
"                                        @ if initial voltage was negative (subs instruction): \n\t" \
"                                        @ then compare voltage now to zero                    \n\t" \
"strmi    r0, [%[np]], #8                @ write-back voltage                                  \n\t" \

"blpl     __refractory_or_spiking_neuron @ if initial or final voltage >= 0, then jump to      \n\t" \
"                                        @    special case code to emit spike and reset or     \n\t" \
"                                        @    decrement refractory counter                     \n\t" \

: [c] "=r" (c), [np] "+r" (np), [in] "+r" (in) : [k] "r" (k), [phi] "r" (phi) : "cc", "memory");

Generic signed 16-bit inputs
============================

per neuron cost = 22 cycles + fix-up + loads of parameters (4)

"ldrh     r0, [%[in]], #2                @ Load ring-buffer value to register.            \n\t" \
"ldrh     r1, [%[in]], #2                @ Load ring-buffer value to register.            \n\t" \
"ldr      %[c0], [%[np], #4]             @ Load neuron's PSC (c0)                              \n\t" \
"ldr      %[c1], [%[np], #8]             @ Load neuron's PSC (c1)                              \n\t" \
"smlal    half, %[c0], %[k_p0], %[c0]    @ super-accurate takes 3 cycles; has interlock        \n\t" \
=================== 3cycles
"smlal    half, %[c1], %[k_p1], %[c1]    @ super-accurate takes 3 cycles; has interlock        \n\t" \
=================== 3cycles
"add      %[c0], %[c0], r0, asl #18      @ combine with decayed PSC value in c0                 \n\t" \
"add      %[c1], %[c1], r1, asl #18      @ combine with decayed PSC value in c1                 \n\t" \
"str      %[c0], [%[np], #4]             @ write-back c0                                        \n\t" \
"ldr      r0, [%[np]]                    @ Load neuron's membrane voltage                      \n\t" \
"str      %[c1], [%[np], #8]             @ write-back c1                                        \n\t" \
"subs     r0, r0, %[phi]                 @ Subtract phi from voltage, setting flags.           \n\t"
"                                        @  .. phi is a pun for:  phi.b OR refractory tick     \n\t" \
"smlalmi  half, r0, %[k_v], r0           @ decay voltage                                       \n\t" \
=================== 3cycles
"addmi    r0, r0, %[c0], lsr? ??         @ combine PSC and voltage                             \n\t" \
"subsmi   r0, r0, %[c1], lsr? ??         @ combine PSC and voltage                             \n\t" \
"                                        @ if initial voltage was negative (subs instruction): \n\t" \
"                                        @ then compare voltage now to zero                    \n\t" \
"strmi    r0, [%[np]], #12                @ write-back voltage                                  \n\t" \



"blpl     __refractory_or_spiking_neuron @ if initial or final voltage >= 0, then jump to      \n\t" \
"                                        @    special case code to emit spike and reset or     \n\t" \
"                                        @    decrement refractory counter                     \n\t" \




 */


void initialise_neurons (void)
{
    uint32_t i;

    for (i = 0; i < NUMBER_OF_NEURONS; i++)
        neuron [2*i] = V_RESET_VOLTAGE;
}

void print_voltage (int v)
{

    if (v >= 0) { // In a refractory period
        io_printf (IO_BUF, "**R %3d", v);

    }
    else {
      io_printf (IO_BUF, "%3.5kmV {%10d}", kbits ((v >> 7)/25) - kbits (50 << 15), v);
    }
}

void print_psc (int p)
{
    //512 = 87.8pA
  io_printf (IO_BUF, "%4.5kpA {%10d}", kbits (p << 3), p);
}

void print_neuron_variables (uint32_t n)
{
    io_printf (IO_BUF, "%3u, ", n);
    print_voltage (neuron [2*n]);
    io_printf (IO_BUF, ", ");
    print_psc (neuron [2*n+1]);
    io_printf (IO_BUF, "\n");
}

void print_neurons (void)
{
    uint32_t i;

    for (i = 0; i < 3; i++)
        print_neuron_variables (i);
}
