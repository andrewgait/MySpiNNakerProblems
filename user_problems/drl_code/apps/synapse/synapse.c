/*
  A fast LIF synapse processing

*/

#include "asm.h"

//! Standard sequencing for a time-step:
//!
//! (1)  Update various global parameters (including DMA-ing an RDW buffer, if it's not already present)
//! (2)  DMA in the RDW buffer.
//! (3)  Ensure enough PRNGs are present
//! (4)  Create Poisson sources
//! (5)  Process RDW into DMA control bursts
//! (6)  Set up DMA scheduler to RDW buffer (if present), or incoming spikes (if present) or null.
//! (7)  Update neurons (emitting spikes)
//! (8)  Process synapses
//! (9)

// once in steady state:
// tick - [rdw-done] => neurons - rdw - synapses - prng - poisson
//        [~rdw]     => rdw 
//        dma is set to spike traffic at start - then extension traffic (RDW)

// initial sequence
// tick - neurons - next rdw
//        dma is set to empty until spike traffic becomes present

// Data management plan required.
// Austria: Vienna 4-6 December. Whole HBP.

void time_step_start (void) asm ("time_step_start") __attribute__ ((noinline, naked));
void neuron_loop     (void) asm ("neuron_loop")     __attribute__ ((noinline, naked));
void convert_rdws    (void) asm ("convert_rdws")    __attribute__ ((noinline, naked));

//! \brief This routine is called first when a timer interrupt occurs.
//! It has the following effects:
//!
//!  (1) Advance the 64-bit clock
//!  (2) Advance the time-base register
//!  (3) Swap the pointers to dma buffers (if not already done)
//!  (4) Adjust the RDW buffer pointers (if not already done)

void time_step_start (void)
{
    register uint32_t* ctrl      asm ("r12"); /* control and constant access                 */


    global_timer_tick ();
    time_base_tick ();

    set_neuron_registers_and_branch ();
}

void neuron_loop (void)
{
    NEURON_REGISTER_MAP;

    neuron_dynamics (); neuron_dynamics (); neuron_dynamics (); neuron_dynamics ();

    USE_NEURON_REGISTERS ();

    printx((uint32_t)in);
    printx(*in);
    //feed_dma_if_needed ();
    //neuron_loop_decrement_and_test ();

    asm volatile ("pop {pc}\n\t" : : "r" (ctrl) : "memory");
    //dispatch_from_neuron_loop ();
}

//! \brief Spike Handling (post interrupt buffer).
//!
//! We assume that each time a check is made by the consumer process on the
//! in-spike buffer, we fill up a contiguous buffer of these spikes; these are
//! then used to access the array of initial rowlet descriptor words. Each
//! spike is transformed to a RDW, which is then fed into the correct RDW delay
//! buffer.
//!
//! We also need to do a "master pop table" filtering.




uint32_t dma_buffer [256];

void convert_rdws (void)
{
    RDW_REGISTER_MAP;
    
    asm volatile ("push {r4-r12,lr}\n\t" : : : "memory");

    ctrl = __control;
    wp = rdw_buffer;
    n = 71;
    dp = dma_buffer;
    mask_0x3fc = 0x3fc;
    bp = dma_buffer1;
    sdram = 0x60800000;
    burst = (uint32_t*)burst_table;

    USE_RDW_REGISTERS ();

    rdw_setup_and_dispatch ();
}
//! \brief This code stub transforms eight Rowlet Descriptor Words (RDW) to DMA
//! command triples: SDRAM address, DTCM address, and DMA Descriptor word. We do
//! this as a seperate operation, since the expense of loading up the registers
//! to do just one translation at a time exceeds the costs of doing so in bulk,
//! and then copying the commands into the actual DMA registers as needed.
//!
//! \param     w       The rowlet descriptor word
//! \param     wp      A pointer to the rowlet descriptor words
//! \param[in] mask    The mask bit pattern 0x1fe
//! \param     bp      A pointer to the eventual DTCM memory address for the DMA transfer.
//! \param     dp      A pointer to the DMA Command buffer
//! \param[in] burst   A pointer to the table used to calculate the required burst size.
//! \param[in] sdram   Base address for this processor's allocation of SDRAM.

void rdw_loop (void)  asm ("rdw_loop") __attribute__ ((noinline, naked));
void rdw_loop (void)
{
    RDW_REGISTER_MAP;

    rdw_to_dma_register_sequence (); rdw_to_dma_register_sequence ();
    rdw_to_dma_register_sequence (); rdw_to_dma_register_sequence ();
    rdw_to_dma_register_sequence (); rdw_to_dma_register_sequence ();
    rdw_to_dma_register_sequence (); rdw_to_dma_register_sequence ();

    USE_RDW_REGISTERS ();

    feed_dma_if_needed ();

    rdw_loop_decrement_and_test ();

    asm volatile ("pop {r4-r12,pc}\n\t" : : : "memory");
}

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
    synapse_loop_decrement_and_test ();
    primary_dispatch ();
}

//! \brief A code sequence that handles an inhibitory rowlet with no odd
//! synapses. If entered at the start it also handles a rowlet extension word,
//! otherwise it goes immediately to the quad processing.
//!
//! If there are no quads, then this is a rowlet header indicating the need for
//! secondary dispatch.

void primary_dispatch_0I (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_inhibitory_time_base ();
    quad_or_secondary_dispatch (); 
    secondary_dispatch ();
}

//! \brief A code sequence that handles an inhibitory rowlet with just one odd
//! synapse. If entered at the start it also handles a rowlet extension word,
//! otherwise it goes immediately to processing the synapse.
//!
//! If there are no quads, then we immediately dispatch on the next rowlet.

void primary_dispatch_1I (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_inhibitory_time_base ();
    synapse_1 ();
    quad_setup_and_dispatch ();
    primary_dispatch ();
}

//! \brief A code sequence that handles an inhibitory rowlet with two odd
//! synapses. If entered at the start it also handles a rowlet extension word,
//! otherwise it goes immediately to processing the synapses.
//!
//! If there are no quads, then we immediately dispatch on the next rowlet.

void primary_dispatch_2I (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_inhibitory_time_base ();
    synapse_2 ();
    quad_setup_and_dispatch ();
    primary_dispatch ();
}

//! \brief A code sequence that handles an inhibitory rowlet with three odd
//! synapses. If entered at the start it also handles a rowlet extension word,
//! otherwise it goes immediately to processing the synapses.
//!
//! If there are no quads, then we immediately dispatch on the next rowlet.

void primary_dispatch_3I (void)
{
    ROWLET_REGISTER_MAP;
    rowlet_extension ();
    set_inhibitory_time_base ();
    synapse_3 ();
    quad_setup_and_dispatch ();
    primary_dispatch ();
}

//! \brief A code sequence that handles an excitatory rowlet with no odd
//! synapses. If entered at the start it also handles a rowlet extension word,
//! otherwise it goes immediately to the quad processing.
//!
//! If there are no quads, then this is a rowlet header indicating the need for
//! secondary dispatch.

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

//! \brief Since the current small fixed rowlets can only handle delays of upto
//! 15 or 16 time steps, we include the possibility of deferring synaptic
//! processing for a further 1-15 time steps. Recall that we've chosen to treat
//! a rowlet with no odd synapses and no quads to process as a secondary
//! dispatch.
//!
//! On entry to this routine we have the following situation:
//!
//!   w  contains: .... .... 0010 0000 00.. .... .... ....  (. is don't care)
//!   r1 contains: .... .... .... .... .... .... ..00 EX..  (. is 0)
//!   r2 contains: .... .... .... .... .... .... ..00 10..  (. is 0)
//!
//! All we have to do is a rowlet extension.

void secondary_dispatch_delay_only (void)
{
    ROWLET_REGISTER_MAP;

    rowlet_extension ();
    primary_dispatch ();
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

//! \brief A C wrapper for gaining access to the assembler routines in such a
//! way that we can return to 'C' and resume prcessing in 'C' if needed. It also
//! sets up the control register used to access variables in different parts of
//! the assembly code.
//!
//! The starting address for the assembler code is "__entry_point".


uint32_t* C_wrapper (uint32_t* in) __attribute__ ((noinline, naked));
uint32_t* C_wrapper (uint32_t* in)
{
    register uint32_t* ctrl asm ("r12"); /* control and constant access  */

    asm volatile ("push  {r0-r12,lr}      @ Save all 'C' registers                        \n\t" :: "r" (in) : "memory");
    ctrl  = __control;
    asm volatile ("push  {pc}             @  set up return address and save on stack      \n\t"
		  "nop                    @ nop instruction is as cheap as adjusting pc   \n\t"\
		  "b     time_step_start  @ Now just __branch__ to the starting address   \n\t"
		  "pop   {r0-r12,pc}      @ Restore all 'C' registers                     \n\t" :: "r" (ctrl) : "memory");
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

    ctrl       = __control;
    jump       = (uint32_t*)(__control[DISPATCH_TABLE >> 2]);
    time_base  = __control[TIME_BASE >> 2];
    mask_0x3fc = 0x3fc;
    mask_0x3c  = 0x3c;
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

//! spike to master-pop lookup.
//!
//! needed only when [r0] != [r0, #8]

void c_main (void)
{
    uint32_t  w, w1, w2, w3, h, q1, q2 ,q3;
    uint32_t* wp;
    uint32_t* initial_wp;
    uint32_t i, n;
    
    initialise_timer ();
    initialise_ring_buffers ();
    initialise_neurons ();

    print_jump_tables ();
    print_synapse_jump_table ();
    print_ring_buffers ();
    zero_dma_buffers ();

    /*
    io_printf (IO_BUF, "Voltages: -65mV = "); print_voltage ((-VOLTAGE_SCALE*100));
    io_printf (IO_BUF, "\n-50mV = "); print_voltage (-1); io_printf (IO_BUF, "\n");
*/
    wp = dma_buffer1;
    initial_wp = dma_buffer1;
    //print_neurons ();
    //translate_rowlets ();

    h  = (0x1 << 16) | (0x2 << 12); // indicates 1 quad of excitatory
    q1 = (16 << 20) | (0x3 << 12) | (0x1);
    q2 = (32 << 20) | (0x4 << 12) | (0x2);
    q3 = (64 << 20) | (48 << 4);

    w    =  (11 << 20) | (0x2 << 12) | (0x1 << 8);
    w1   =  (11 << 20) | (0x3 << 12) | (0x1 << 8);
    w2   =  (22 << 20) | (0x4 << 12) | (0x2 << 8);
    w3   =  (44 << 20) | (33 << 4);

    dma_buffer1[0] = h;
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

    //neuron_loop ();

    //start_timer ();
    asm volatile ("@\n\t" : "+r" (wp)   : : "cc");
    wp = process_rowlets_from_C (dma_buffer1);
    asm volatile ("@\n\t" : "+r" (wp) : : "cc");
    //stop_timer ();
    
    print_ring_buffers ();
    print_neurons ();

    io_printf (IO_BUF, "Total time taken to process rowlet buffer is: = %u cycles\n", time);
    io_printf (IO_BUF, "The number of words processed is: %u (initial %08x, final: %08x)\n",
	       ((uint32_t)wp - (uint32_t)initial_wp) >> 2, (uint32_t)initial_wp, (uint32_t)wp);
    io_printf (IO_BUF, "The number of synapses is %u, the number of rowlets is: %u\n", __synapses, __rowlets);

    asm volatile ("@\n\t" : "+r" (wp) : : "cc");
    wp = C_wrapper (dma_buffer1);
    asm volatile ("@\n\t" : "+r" (wp) : : "cc");
    io_printf (IO_BUF, "Current time is now: %u\n",        __control [ 64 >> 2]);
    io_printf (IO_BUF, "Current time_base is now: %08x\n", __control [124 >> 2]);
        print_ring_buffers ();

    print_neurons ();
    
    asm volatile ("@\n\t" : "+r" (wp) : : "cc");
    wp = C_wrapper (dma_buffer1);
    asm volatile ("@\n\t" : "+r" (wp) : : "cc");
    io_printf (IO_BUF, "Current time is now: %u\n",        __control [ 64 >> 2]);
    io_printf (IO_BUF, "Current time_base is now: %08x\n", __control [124 >> 2]);
        print_ring_buffers ();

    print_neurons ();
    
    /*    io_printf (IO_BUF, "NUMBER_OF_NEURONS         %u\n", NUMBER_OF_NEURONS);
    io_printf (IO_BUF, "NEURON_ODD_NEURONS        %u\n", NEURON_ODD_NEURONS);
    io_printf (IO_BUF, "NEURON_LOOPS              %u\n", NEURON_LOOPS);
    io_printf (IO_BUF, "PHI_B_COEFFICIENT         %u\n", PHI_B_COEFFICIENT);
    io_printf (IO_BUF, "NEURON_PSC_COEFFICIENTS_2 %u\n", NEURON_PSC_COEFFICIENTS_2);
    io_printf (IO_BUF, "control k2                %u\n", (uint32_t)__control[NEURON_PSC_COEFFICIENTS_2>>2]);
    io_printf (IO_BUF, "NEURON_PHI_OFFSET         %u\n", NEURON_PHI_OFFSET);
    io_printf (IO_BUF, "control phi               %u\n", (uint32_t)__control[NEURON_PHI_OFFSET>>2]);
    io_printf (IO_BUF, "neuron base address       %08x\n", (uint32_t)neuron);
    io_printf (IO_BUF, "neuron loop start address %08x\n", (uint32_t)neuron_loop);
    io_printf (IO_BUF, "control neuron loop addy  %08x\n", (uint32_t)__control[NEURON_LOOP_START_OFFSET >> 2]);
    io_printf (IO_BUF, "number of neuron loops    %08x\n", (uint32_t)__control[NEURON_NUMBER_LOOPS_OFFSET >> 2]);
   
    return;
        print_rdw_table ();

    translate_tmp ();
    initial_wp = dma_buffer0;
    wp = initial_wp;

    n = tmp_to_rdw ();
    io_printf (IO_BUF, "Number of RDWs processed is %u\n", n);

    asm volatile ("@\n\t" : "=r" (wp) : : "cc");
    start_timer ();
    asm volatile ("@\n\t" : "=r" (wp) : : "cc");
    convert_rdws ();
    asm volatile ("@\n\t" : "=r" (wp) : : "cc");
    stop_timer ();
    asm volatile ("@\n\t" : "=r" (wp) : : "cc");

    io_printf (IO_BUF, "rdw_buffer = %08x; dma_buffer = %08x\n\n", rdw_buffer, dma_buffer);
    io_printf (IO_BUF, "Total time taken to process RDW buffer is: = %u cycles\n", time);

    for (i = 0; i < n; i++) {
        io_printf (IO_BUF, "%2u:   RDW = %08x {%08x, %08x, %08x}\n",
		   i+1,
		   rdw_buffer[i],
		   dma_buffer[3*i],
		   dma_buffer[3*i+1],
		   dma_buffer[3*i+2]);
    }
   
    io_printf (IO_BUF, "\nRDW = %08x; (A << 2) = %06x; D = %01x; S = %u [S << 2 = %03x], size is %u words\n",
	       tmp_rdw, (tmp_rdw >> 11) << 2, (tmp_rdw >> 7) & 0xf, tmp_rdw & 0x7f, (tmp_rdw & 0x7f) << 2,
	       (tmp_rdw & 0x7f)+1);
    io_printf (IO_BUF, "Commands are: {%08x, %08x, %08x}\n", dma_buffer[0], dma_buffer[1], dma_buffer[2]);


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

    //translate_tmp ();
      //printx (dma_buffer0[0]);
    //printx (dma_buffer0[1]);
    
    //print_dma_buffers ();

    initial_wp = dma_buffer0;
    wp = initial_wp;
    
    //start_timer ();
    //dense_256 ();
    //stop_timer ();
    asm volatile ("@\n\t" : "+r" (wp) : : "cc");
    //wp = process_rowlets_from_C (wp);
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
    
    //print_ring_buffers ();*/

}
