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

#define NUMBER_OF_NEURONS 256

int neuron [NUMBER_OF_NEURONS * 2];

// The following are not made explicit, since we do not wish to import all the
// floating point library functions, just to set up integer constants!
//
// #define FLOAT_TIME_STEP    0.1  ms
// #define FLOAT_TIME_CONST_V 10.0 ms
// #define FLOAT_TIME_CONST_S 0.5  ms
// #define FLOAT_MEMBRANE_R   40.0 M Ohm

#define MEMBRANE_R   40 /* M \Ohm */

#define VOLTAGE_SCALE 1048576         /* (= 2^20) integer representing 10\mu V */
#define WEIGHT_PSC_CONVERSIONSHIFT 18 /* _left_ shift needed to convert a weight to a PSC */
#define WEIGHT_SCALE  16              /* integer representing 1pA  */
#define PSC_SCALE     (WEIGHT_SCALE << WEIGHT_PSC_CONVERSIONSHIFT)  /* =2^22 integer representing 1pA  */


// 4594-3181-QKW9AW


// MEMBRANE_R * PSC_SCALE = 4 * VOLTAGE_SCALE

// If a weight of 1 translates as 0.0625pA, then a value of 16 translates as 1pA.
// This has to cause a 0.04mV = 40\mu V rise in membrane potential which is 4 * 2^20.
// Now we have head-room for just 512 of these 40\mu V, which corresponds to a range of 20.48 mV
/*

The technique I'm using is to subtract the drift term first -- then decay.

Thus       (v + d) * (P_11) = v         (if v = v_rest)
     |=|   d = v/P_11 - v
     |=|   d  = v (P_11 -1)/ P_11


suppose weight 16 = 1pA
  suggest 40\mu V = 2^22 or 10 \mu V = 2^20
  range of voltage is then 15*100 = 1500 < 2048

thus weight 16 = 2^4 => 4 * 2^20 = 2^22 i.e psc shift = 18. no scaling needed



0.10000000000000000555111512312578270  -65.000000000000000000000000000000000  0.087800000000000003042011087472928921

0.20000000000000001110223024625156540  -64.968333020455061995544365461043755  0.15968456011933140208317831589936344

0.30000000000000001665334536937734811  -64.911054402611745579588211249527201  0.21853866016008921189057736026773978

0.40000000000000002220446049250313081  -64.833118705355481837163272392381396  0.26672432180892294974211847453963714

0.50000000000000002775557561562891351  -64.738579274377587047020344574645683  0.30617540485199683830302880834348414

0.60000000000000003330669073875469621  -64.630751635308315684558934285616773  0.33847521976525538820267823369475074

0.70000000000000003885780586188047891  -64.512347268440139035683561145294615  0.36492007155156823514977927236302376

0.80000000000000004440892098500626162  -64.385583133782895761637701266386888  0.38657128497711972661568635918308248

0.90000000000000004996003610813204432  -64.252271342348485321359841339059698  0.40429779925852127938412612643345275

1.0000000000000000555111512312578270  -64.113892572508860943914569372033465  0.41881104165151350159943282583128263

1.1000000000000000610622663543836097  -63.971656177926264639533621913319198  0.43069347952833751385067825560036671

1.2000000000000000666133814775093924  -63.826549399468302227333347301261372  0.44042199683984055761913855395350443

1.3000000000000000721644966006351751  -63.679377656225692563084483216089974  0.44838703314336738427622068228507700

1.4000000000000000777156117237609578  -63.530797532719450112992666580194499  0.45490825331272745935469496250014244

1.5000000000000000832667268468867405  -63.381343786257318585436896231881801  0.46024737681123005303344191384962276

1.6000000000000000888178419700125232  -63.231451458406774531449906861026383  0.46461868141234158460860117293617596

1.7000000000000000943689570931383059  -63.081473978060209282649233317563482  0.46819760291895629355419010693229172

1.8000000000000000999200722162640886  -62.931697982695955950298938573923405  0.47112777601809826156320042655060948

1.9000000000000001054711873393898713  -62.782355452727992448513996106045710  0.47352679884522506460424752206094394

2.0000000000000001110223024625156540  -62.633633646001389480255116103639035  0.47549095261031562072439400245426054

2.1000000000000001165734175856414367  -62.485683231202096034386669009862447  0.47709906570089776953684942349677723

2.2000000000000001221245327087672194  -62.338624946665154536080580997047606  0.47841567734203268947676501538865193

2.3000000000000001276756478318930021  -62.192555051883890017566498969830188  0.47949362778203733594616537104529940

2.4000000000000001332267629550187849  -62.047549790568862589630759186827715  0.48037617895719169487978766905707290

2.5000000000000001387778780781445676  -61.903669044434792317899777913103166  0.48109875074515134721583537402883898

2.6000000000000001443289932012703503  -61.760959324414141373792671922214932  0.48169034248901112037412925910021185

2.7000000000000001498801083243961330  -61.619456219404053000057075661090375  0.48217469684277186999255033862841920

2.8000000000000001554312234475219157  -61.479186400881670786582178089399855  0.48257125264741562002797317226510232

2.9000000000000001609823385706476984  -61.340169263897721220150698237755015  0.48289592507985184937858844877270589

3.0000000000000001665334536937734811  -61.202418270364251960547656673021205  0.48316174438485153994751866595826448

3.1000000000000001720845688168992638  -61.065942048603869687061173799929737  0.48337937882452433845961306469994436

3.2000000000000001776356839400250465  -60.930745293345177397499250395572960  0.48355756283313763551178391346364705

3.3000000000000001831867990631508292  -60.796829502339759823393593336894035  0.48370344756063387628440445257554071

3.4000000000000001887379141862766119  -60.664193579218563709081720652286546  0.48382288787338835353309613763723868

3.5000000000000001942890293094023946  -60.532834326836691457388408982136505  0.48392067733055566990621201731672033

3.6000000000000001998401444325281773  -60.402746850960002087284939633134473  0.48400074056643075112226505392946605

3.7000000000000002053912595556539600  -60.273924890548080677243908582242946  0.48406629079980409060519837318830029

3.8000000000000002109423746787797427  -60.146361087941662632638039525471488  0.48411995879171473128979894457611694

3.9000000000000002164934898019055254  -60.020047209850229782174030264542717  0.48416389842712843512917201259263166

4.0000000000000002220446049250313081  -59.894974328060414572465379732766940  0.48419987315790452564158142190653479

4.1000000000000002275957200481570908  -59.771132967168789514305397386928479  0.48422932677631119942871146139863043

4.2000000000000002331468351712828735  -59.648513225318683227169359943905265  0.48425344135947899079949794118059391

4.3000000000000002386979502944086562  -59.527104872836717686273696213316288  0.48427318471030677363506956509505427

4.4000000000000002442490654175344389  -59.406897432777300959847811177948876  0.48428934919879044270267904687236697

4.5000000000000002498001805406602216  -59.287880246656718884530557011007398  0.48430258356261318212556501711535830

4.6000000000000002553512956637860043  -59.170042528063587072872734053419179  0.48431341894326667330295633769471929





*/

// Matrix propogators
//
// { P_11 P_21 }
// { P_12 P_22 }
//
// P_12 is always 0
// P_11 = exp (-TIME_STEP/TIME_CONST_V) = exp (-0.1/10.0)  ~= 64884/65536
// P_22 = exp (-TIME_STEP/TIME_CONST_S) = exp (-0.1/0.5)   ~= 53656/65536
//
// The above propgators only depend on time, but P_21 depends on the units by
// which voltage and current are measured, but P_21 depends on the
// representations of both voltage and psc.
//
// These matrix propogators are reasonably close to 1.0, and to use the
// special DSP multiplication instructions, we need our multipliers to be
// in the range [-1/2, 1/2)

// 1 - exp (-0.1/0.5)   ~= 11880/65536 = 0.1812692469220181413300644913809605756414 = P_22
// 1 - exp (-0.1/10.0)  ~=  652/65536  = 0.0099501662508319464260940228199634422279 = P_11
// P_12 =

// phi B = -65 * ((1::CR)-exp (-(1::CR)/100)) = -0.6467608063040765176961114832976237448149


//#define signed_16bit(x) (((x < 0)? (0x10000 -(x)): (x)))
// tau = RC
// 10ms = tau; C = 250pF; R = tau/C = 4T \Ohm?
//
// Therefore a 1nA impulse generates a 40mV increase in voltage.
// The multiplier is then 7202 (not 7202/65536, note!)

/*
Hmm, how about these:
-        Synaptic expander now in master – microcortical column runs in ~10 minutes end-to-end
-        Log changes to avoid large log messages filling up ITCM – logs are stored in encoded form and messages are then reconstructed on host
-        Neuron implementation updated to allow “complete” neuron models rather than the current “compartmentalised” version.
-        Working on improvements to code to allow column to run in real-time at 0.1ms (you have the details of this!)
-        Working on Java implementation of parts of the software to allow parallel reading / writing of data – read from a single chip anywhere on the machine now 40Mb/s.
-        Working on various learning rules and models.
-        Astrocytes proposal for HBP voucher programme submitted.  Another “memristor” proposal in the works.
 
Is that enough?  Let me know if you want more info...
 
Andrew :)
*/

// so an 87.8pA impulse results in a 351.2 \mu V, represented by 37710 unit increment in v.
// An 87.8pA current is 512 in the ring-buffer, and becomes 512*65536 in me

#define PSC_COEFFICIENTS     ((0 << 16) | (0x10000 - 11880))
#define VOLTAGE_COEFFICIENTS ((0 << 16) | (0x10000 -   652))
#define PHI_B_COEFFICIENT    15805242 /*16184567  phi =   (V_RESET_VOLTAGE-phi) * (1 -  163 / 32768) */
#define V_RESET_VOLTAGE      (-15* (VOLTAGE_SCALE * 100))
#define REFRACTORY 20
// phi = 0 

void neuron_loop (void) asm ("neuron_loop") __attribute__ ((noinline, naked));

#define NEURON_DYNAMICS_CODE_SIZE (17*4)

#define NEURON_ODD_NEURONS        (NUMBER_OF_NEURONS & 0x3) 
#define NEURON_LOOPS              ((NUMBER_OF_NEURONS >> 2) + ((NEURON_ODD_NEURONS == 0)? 1: 0))
#define NEURON_LOOP_START_ADDRESS					          \
	       ((uint32_t)neuron_loop + NEURON_DYNAMICS_CODE_SIZE*                \
		((NEURON_ODD_NEURONS == 0)? 0: (4-NEURON_ODD_NEURONS)))

#define __neuron_processing (void*)(NEURON_LOOP_START_ADDRESS)

//=============================================================================
// DMA Processing
//=============================================================================


//#define DMA_ADRS 0x4   /* SDRAM Address        */
//#define DMA_ADRT 0x8   /* TCM Address          */
//#define DMA_DESC 0xc   /* Transfer description */
//#define DMA_CTRL 0x10  /* Control Register     */
//#define DMA_STAT 0x14  /* Status Register      */


//=============================================================================
// Master Pop Table Look-up
//=============================================================================

//! \brief The first RDW word is in the "master pop table". We index this using
//! the lowest 17 bits of the spike's ID. This corresponds to 8 bits of internal
//! selection for a particular neuron, and 9 bits to select the particular sub-
//! population or population. I'm assuming that we place the sub-populations
//! into contiguous blocks of 256 RDW words, and that each full population
//! starts on a 512-word boundary. (Not sure I need this but hey-ho!)

#define spike_to_master_pop_dma()					                                                 \
    do {asm volatile ("ldr  %[w], [%[wp]], #4         @ Load spike into w, incrementing spike pointer wp           \n\t" \
		      "str  r1, [r3, %[adrt]]         @ Store DMA destination (TCM) address                        \n\t" \
		      "and  r0, %[mask], %[w], lsr #6 @ Mask out the table offset bits into their correct places   \n\t" \
		      "add  r0, %[sdram], r0          @ Calculate the SDRAM address                                \n\t" \
		      "str  r0, [r3, %[adrs]]         @ Store DMA source (SDRAM) address                           \n\t" \
		      "mov  r0, #4                    @ Load descriptor word                                       \n\t" \
		      "str  r0, [r3, %[desc]]         @ Store DMA Descriptor word, 0x4, and thereby start DMA      \n\t" \
		      "mov  r0, #8                    @ Load the control word                                      \n\t" \
		      "str  r0, [r3, %[d_ctrl]]       @ Store DMA Control word, 0x8, and thereby clear a Done flag \n\t" \
		      "add  r1, r1, #4                @ Increment the TCM address                                  \n\t" \
		      : [w] "=r" (w), [wp] "+r" (wp)					                                 \
		      : [adrs] "J" ((DMA_ADRS) << 2), [adrt] "J" ((DMA_ADRT) << 2),\
			[desc] "J" ((DMA_DESC) << 2), [d_ctrl] "J" ((DMA_CTRL) << 2), \
			[mask] "r" (mask), [sdram] "r" (sdram)		                                                 \
		      : "memory");					                                                 \
    } while (false)


//! \brief The following code executes in eight cycles (9?), and transfers the DMA commands to the DMA engine.
//!
//! It clobbers all four scratch registers: r0, r1, r2, and r3.

#ifdef SMALL_CODE
#define command_to_dma()                                                                                                 \
  do {asm volatile ("mov   r3, #0x8          @ Cancel one of the DMA-completed flags.                              \n\t" \
		    "ldmia %[cp]!, {r0-r2}   @ Load the Command words, from cp, auto-incrementing                  \n\t" \
		    "stmib %[dma], {r0-r3}   @ Do DMA transfer                                                     \n\t" \
		    : [cp] "=r" (cp) : [dma] "r" (dma) : "memory");	                                                 \
    } while (false)
#else
//! Following version only clobbers r0 and r1, and only takes 8 cycles
#define command_to_dma()                                                                                                 \
  do {asm volatile ("ldr   r0, [%[cp]], #4         @ Load the Source word, from cp, auto-incrementing              \n\t" \
		    "ldr   r1, [%[cp]], #4         @ Load the Destination word, from cp, auto-incrementing         \n\t" \
		    "str   r0, [%[dma], %[adrs]]   @ Store Source word                                             \n\t" \
		    "ldr   r0, [%[cp]], #4         @ Load the Description word, from cp, auto-incrementing         \n\t" \
		    "str   r1, [%[dma], %[adrt]]   @ Store Destination word                                        \n\t" \
		    "str   r0, [%[dma], %[desc]]   @ Store Description word                                        \n\t" \
		    "mov   r0, #0x8                @ Cancel one of the DMA-completed flags.                        \n\t" \
		    "str   r0, [%[dma], %[d_ctrl]] @ Store Control word                                            \n\t" \
		    : [cp] "=r" (cp) : [dma] "r" (dma), [adrs] "J" ((DMA_ADRS) << 2), [adrt] "J" ((DMA_ADRT) << 2),      \
		      [desc] "J" ((DMA_DESC) << 2), [d_ctrl] "J" ((DMA_CTRL) << 2),	                                 \
		    : "memory");					                                                 \
    } while (false)
#endif

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
//=============================================================================

#define USE_ROWLET_REGISTERS()						                      \
  do {asm volatile ("@ spoof register use\n\t" : : "r" (ctrl), "r" (wp), "r" (w), "r" (n),    \
		    "r" (time_base), "r" (jump), "r" (mask_0x3fc),"r" (mask_0x3c) : "cc");          \
  } while (false)

//! \brief The following macro allows us to define _in_one_place_ the register
//! names and locations used by the various pieces of rowlet manipulation code.
//!
//! It also hides a piece of non-code-generating code that "uses" all of these
//! registers, as most code fragments don't use _all_ the registers.
//!
//! It may be that omitting this "asm" statement becomes necessary later.

#define ROWLET_REGISTER_MAP                                                                   \
  register uint32_t* ctrl       asm ("r12"); /* control and constant access                 */ \
  register uint32_t* wp         asm ("r11"); /* Pointer to next synaptic word               */ \
  register uint32_t  w          asm ("r10"); /* Current synaptic word                       */ \
  register uint32_t  n          asm ("r9");  /* Number of synapses in this rowlet.          */ \
  register uint32_t  time_base  asm ("r8");  /* Bottom 4 bits of global timer in bits 31-28 */ \
  register uint32_t* jump       asm ("r7");  /* The base of the dispatch jump table         */ \
  register uint32_t  mask_0x3fc asm ("r6");  /* Mask 0x3fc                                  */ \
  register uint32_t  mask_0x3c  asm ("r5");  /* Mask 0x3c, easily reconstructed with mov    */ \
                                                                                              \
  USE_ROWLET_REGISTERS()

#define USE_RDW_REGISTERS()						                      \
  do {asm volatile ("@ spoof register use\n\t" : : "r" (ctrl), "r" (wp), "r" (w), "r" (n),    \
		    "r" (sdram), "r" (bp), "r" (dp), "r" (mask_0x3fc),"r" (burst) : "cc");    \
  } while (false)

#define RDW_REGISTER_MAP                                                                         \
  register uint32_t* ctrl       asm ("r12"); /* control and constant access                    */ \
  register uint32_t* wp         asm ("r11"); /* Pointer to next RDW word                       */ \
  register uint32_t  w          asm ("r10"); /* Current RDW word                               */ \
  register uint32_t  n          asm ("r9");  /* Number of RDWs in this buffer.                 */ \
  register uint32_t  sdram      asm ("r8");  /* Base address of this processor's area in SDRAM */ \
  register uint32_t* burst      asm ("r7");  /* The base of the burst table                    */ \
  register uint32_t  mask_0x3fc asm ("r6");  /* Mask 0x3fc                                     */ \
  register uint32_t* bp         asm ("r5");  /* The eventual DMA Buffer addresses              */ \
  register uint32_t* dp         asm ("r4");  /* The pointer to the DMA Command buffer          */ \
                                                                                                 \
  USE_RDW_REGISTERS()

//=============================================================================
// Large uninitialised data structures requiring careful alignment
//
// (or those smaller ones that can be squeezed in!)
//=============================================================================

// 0x0040 0000 Ring Buffers            (size 16,384 bytes; 16 KB; 8K weights)
// 0x0040 4000 DMA buffer 0            (size  6,144 bytes;  6 KB; 1.5K synapses)
// 0x0040 5800 Outspike Buffer         (size  1,024 bytes;  1 KB; 256 spikes)
// 0x0040 5c00 Random Number Buffer    (size  2,048 bytes;  2 KB; 512 random numbers)
// 0x0040 6000 DMA buffer 1            (size  6,144 bytes;  6 KB; 1.5K synapses)
// 0x0040 7800 Circular Buffer for FIQ (size  1,024 bytes;  1 KB; 256 in spikes)


#define __ring_buffer_address      0x00400000
#define __dma_buffer0_address      0x00404000
#define __dma_buffer1_address      0x00406000
#define __outspike_buffer_address  0x00405800
#define random_buffer              0x00405c00

#define outspike_buffer  ((uint32_t*)__outspike_buffer_address)

//#define __ring_buffer0_address 0x00404000
//#define __ring_buffer1_address 0x00406000

// 0x0040 8000 Start of available DTCM


#define RING_ADDRESS_BITS 7
#define RING_TIME_BITS 2
#define SHIFT_LEFT  (32 - (RING_TIME_BITS+RING_ADDRESS_BITS))
#define SHIFT_RIGHT (SHIFT_LEFT - 1)
#define PLASTICITY_REQUIRED false

#define DELAYS           16
#define TIME_CONSTANTS   2
#define RING_BUFFER_SIZE (NUMBER_OF_NEURONS*DELAYS)
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

#define __ring_buffer ((int*)__ring_buffer_address)
#define ring_buffer   ((uint16_t*)__ring_buffer_address)

//#define __ring_buffer0 ((int*)__ring_buffer0_address)
//#define __ring_buffer1 ((int*)__ring_buffer1_address)

//#define ring_buffer0 ((uint16_t*)__ring_buffer0_address)
//#define ring_buffer1 ((uint16_t*)__ring_buffer1_address)

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
// Timer Section
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

#define C_CODE

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

    for (i = 0; i < 256; i++) {
        __ring_buffer [(delay << 8) + i] = 0xffffffff;
    }
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
    int i, j;

    for (i = 0; i < 256; i++)
        for (j = 0; j < 16; j++)
	    if (ring_buffer[(256*j + i) * 2 + buffer_number] != 0xffff)
                io_printf (IO_BUF, "%s [%d, %u] = %u\n",
                           (buffer_number == 0)? "excitatory\0": "inhibitory\0",
			   j, i, 0xffff - (uint32_t)ring_buffer[(256*j + i)*2+buffer_number]);
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

uint32_t middle_byte (uint32_t w)
{   return ((w >> 12) & 0xff); }

uint32_t secondary_nibble (uint32_t w)
{   return ((w >> 20) & 0xf); }

uint32_t big_fixed_synapse (uint32_t w)
{   return (w & 0xff); }

uint32_t tmp[];

static uint32_t* __op__ = dma_buffer0;
static uint32_t* __ip__ = tmp;
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

void dma_empty                     (void)  asm ("dma_empty")                     __attribute__ ((noinline, naked));
void convert_rdws                  (void)  asm ("convert_rdws")                  __attribute__ ((noinline, naked));
void time_step_start               (void)  asm ("time_step_start")               __attribute__ ((noinline, naked));
void rdw_loop                      (void)  asm ("rdw_loop")                      __attribute__ ((noinline, naked));
void packed_quad_loop              (void)  asm ("packed_quad_loop")              __attribute__ ((noinline, naked));
void primary_dispatch              (void)  asm ("primary_dispatch")              __attribute__ ((noinline, naked));
void secondary_dispatch_big_fixed  (void)  asm ("secondary_dispatch_big_fixed")  __attribute__ ((noinline, naked));
void secondary_dispatch_delay_only (void)  asm ("secondary_dispatch_delay_only") __attribute__ ((noinline, naked));

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
#define RDW_CODE_SIZE              (12*4)
#define ROWLET_EXTENSION_CODE_SIZE (6*4)
#define JKISS_CODE_SIZE            (10*4)

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
	     (uint32_t)secondary_dispatch_delay_only, // -2 A delay rowlet consisting solely of another RDW
	     (uint32_t)secondary_dispatch_big_fixed,  // -1 A "large" block of fixed synapses, with a seperate header word
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
    io_printf (IO_BUF, "[%08x] Big Fixed      \n", table[15]);
    io_printf (IO_BUF, "[%08x] Delay Extension\n", table[14]);
}

void print_jump_tables (void)
{
    print_primary ();
    print_secondary ();
}

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

//! \brief Pocessor SDRAM layout. The 8M Bytes allocated to a processor are split as follows
//!
//!
//! Next processor's matser pop base
//!------------------------------------------
//!                     RDW buffer 16
//!
//!                     RDW buffer 2
//! RDW_BASE:           RDW buffer 1
//!------------------------------------------
//!                     FREE SPACE
//!------------------------------------------
//!                     rowlet m
//!
//! ROWLET_BASE    :    rowlet 1
//!------------------------------------------
//!                     master pop table n
//!
//!                     master pop table 2
//! MASTER_POP_BASE:    master pop table 1
//!------------------------------------------

#define PROCESS_SDRAM_BASE   0x60800000
#define PROCESS_SDRAM_SIZE     0x800000 /* = 8M Byte */

#define MASTER_POP_BASE      PROCESS_SDRAM_BASE
#define MASTER_POP_SIZE      0x4000
#define ROWLET_BASE          (MASTER_POP_BASE + MASTER_POP_SIZE)

#define RDW_BUFFER_SIZE      (256*4)
#define RDW_BASE             (PROCESS_SDRAM_BASE + PROCESS_SDRAM_SIZE - 16 * RDW_BUFFER_SIZE)

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
	     RDW_BASE +  0 * RDW_BUFFER_SIZE,  // Base of 16 Rowlet Processing Buffers, each holding a sequence of RDWs
	     RDW_BASE +  1 * RDW_BUFFER_SIZE,
	     RDW_BASE +  2 * RDW_BUFFER_SIZE,
	     RDW_BASE +  3 * RDW_BUFFER_SIZE,
	     RDW_BASE +  4 * RDW_BUFFER_SIZE,
	     RDW_BASE +  5 * RDW_BUFFER_SIZE,
	     RDW_BASE +  6 * RDW_BUFFER_SIZE,
	     RDW_BASE +  7 * RDW_BUFFER_SIZE,
	     RDW_BASE +  8 * RDW_BUFFER_SIZE,
	     RDW_BASE +  9 * RDW_BUFFER_SIZE,
	     RDW_BASE + 10 * RDW_BUFFER_SIZE,
	     RDW_BASE + 11 * RDW_BUFFER_SIZE,
	     RDW_BASE + 12 * RDW_BUFFER_SIZE,
	     RDW_BASE + 13 * RDW_BUFFER_SIZE,
	     RDW_BASE + 14 * RDW_BUFFER_SIZE,
	     RDW_BASE + 15 * RDW_BUFFER_SIZE,
	     0,0,                           //  64 global timer (64 bit)
	     0,                             //  72 circular buffer output "index
	     0x00401800,                    //  76 circular buffer array
	     0,                             //  80 circular buffer input  "index"
	     0,                             //  84 circular buffer overflows
	     WORD_WRITE_DESCRIPTOR,         //  88 A descriptor word for a "small" single word write
	     LARGE_READ_DESCRIPTOR,         //  92 A descriptor word for a "large" read  using double word
	     (uint32_t)dma_buffer0,         //  96 DMA Read buffer for Rowlets
	     (uint32_t)dma_buffer1,         // 100 DMA Write Buffer for the next tick's Rowlets
	     0x18181818, 0x10121416, 0x0,   // 104 log_size_to_burst table.
	     0,                             // 116 unused
	     (uint32_t)dispatch_table,      // 120 Rowlet Dispatch Tables
	     ((uint32_t)ring_buffer >> 14), // 124 Time-base: rotated base address of ring-buffer with 4 bits of timer
	     0,                             // 128 DMA Processing Address
	     SDRAM_BASE,                    // 132 SDRAM base address for this processor (p) is 0x60000000 + p * 0x800000
	     0,                             // 136 Saturation Counter
	     V_RESET_VOLTAGE,               // 140 V_reset value
	     PHI_B_COEFFICIENT * REFRACTORY,  // 144 Refractory counter initial value
	     (uint32_t)outspike_buffer,     // 148 Outspike buffer pointer
	     (uint32_t)neuron,              // 152 Neuron variables address
	     PSC_COEFFICIENTS,              // 156 PSC Coefficients
	     VOLTAGE_COEFFICIENTS,          // 160 Voltage Coefficients
	     PHI_B_COEFFICIENT,             // 164 phi.b Coefficient
	     NEURON_LOOPS,                  // 168 number of loops
	     NEURON_LOOP_START_ADDRESS,	    // 172 start point
	     123456789, //KISS_STATE_X
	     987654321, //KISS_STATE_Y
	     43219876, //KISS_STATE_Z
	     6543217, //KISS_STATE_C
	     314527869, //KISS_STATE_K0
	     1234567, //KISS_STATE_K1
	     4294584393ULL, //KISS_STATE_K2
	     ((uint32_t)random_buffer) + 1024, //KISS_STATE_RP = empty OR delete +1024 and initialise
	     (uint32_t)random_buffer //RANDOM_BASE_OFFSET
};

#define __control              ((uint32_t*)(__control_synapse + 31))
#define delayed_rowlet_buffer  (__control)


#define GLOBAL_TIMER                  64
#define GLOBAL_TIMER_LO               64
#define GLOBAL_TIMER_HI               68
#define DMA_BUFFER_READ               96
#define DMA_BUFFER_WRITE             100
#define LOG_SIZE_BURST_OFFSET        (104-21)
#define RDW_RESET_OFFSET             116
#define DISPATCH_TABLE               120
#define TIME_BASE                    124
#define DMA_PROCESSING               128
#define PROCESSOR_SDRAM_BASE_OFFSET  132
#define SATURATION_COUNTER           136
#define V_RESET_OFFSET               140
#define REFRACTORY_OFFSET            144
#define OUTSPIKE_OFFSET              148
#define NEURON_VARIABLES_OFFSET      152
#define NEURON_PSC_COEFFICIENTS_1    156
#define NEURON_PSC_COEFFICIENTS_2    160
#define NEURON_PHI_OFFSET            164
#define NEURON_NUMBER_LOOPS_OFFSET   168
#define NEURON_LOOP_START_OFFSET     172
#define KISS_STATE_X                 176
#define KISS_STATE_Y                 180
#define KISS_STATE_Z                 184
#define KISS_STATE_C                 188
#define KISS_STATE_K0                192
#define KISS_STATE_K1                196
#define KISS_STATE_K2                200
#define KISS_STATE_RP                204
#define RANDOM_BASE_OFFSET           208
#define RANDOM_LOOP_ADDRESS          212

void print_synapse_jump_table (void)
{
    int i;

    io_printf (IO_BUF, "\nquad jump table\n===============\n");

    for (i = 0; i < 8; i++) {
        io_printf (IO_BUF, "[%08x] n = %d\n", __control_synapse[31 - i], i);
    }
    io_printf (IO_BUF, "\n\n");
}

//! \brief The following double entry table is used during Rowlet Descriptor
//! Word (RDW) Processing. It resides in ITCM as its contents do not change.
//!
//! To use access the table we use the address burst_table, defined below.
//!
//! The negatively-indexed (by words) values point into the rdw_loop code, at
//! the correct point to  process a certain number of RDWs. The positively-
//! indexed (by bytes) values give a burst-size/double/single-word byte for
//! use in a DMA descriptor word at bits 20-27. The first nibble is 1 if it
//! is a double word transfer, with 0 representing a single word transfer.
//! The second nibble represents the number of "units" (either single or
//! double words) in a burst, with 0x8 representing 2^4 = 16 , 0x6 representing
//! 2^3 = 8, 0x4 representing 2^2 = 4, 0x2 representing 2^1 = 2, and 0x0
//! representing 2^0 = 1.

static const uint32_t __burst_size[]
          = {(uint32_t)rdw_loop +   RDW_CODE_SIZE,  // First process 7 odd RDWs
	     (uint32_t)rdw_loop + 2*RDW_CODE_SIZE,  // First process 6 odd RDWs
	     (uint32_t)rdw_loop + 3*RDW_CODE_SIZE,  // First process 5 odd RDWs
	     (uint32_t)rdw_loop + 4*RDW_CODE_SIZE,  // First process 4 odd RDWs
	     (uint32_t)rdw_loop + 5*RDW_CODE_SIZE,  // First process 3 odd RDWs
	     (uint32_t)rdw_loop + 6*RDW_CODE_SIZE,  // First process 2 odd RDWs
	     (uint32_t)rdw_loop + 7*RDW_CODE_SIZE,  // First process 1 odd RDW
	     (uint32_t)rdw_loop,                    // No odd RDWs to process
 //----------------------------------------------------------------------------------------------------------
	     0,
	     0,
	     0,
	     0,
	     0x18181800,                            // Byte-indexed burst sizes
	     0x12141618,                            // Byte-indexed burst sizes
	     0x10};                                 // Byte-indexed burst sizes

#define rdw_jump_table   ((uint32_t*)__burst_size + 7)
#define burst_table      ((uint8_t*)rdw_jump_table)

void print_rdw_table (void)
{
    uint32_t i;

    io_printf (IO_BUF, "\nRDW Jump Table (at base address: %08x)\n==============\n", (uint32_t)burst_table);

    for (i = 0; i < 8; i++) {
        io_printf (IO_BUF, "[%08x] n = %u\n", __burst_size[i], 7-i);
    }

    io_printf (IO_BUF, "\nBurst Table\n===========\n");

    for (i = 0; i < 10; i++) {
        io_printf (IO_BUF, "[%02x] bytes <= %u\n", (uint32_t)(burst_table[__clz (1 << i)]), (1 << i));
    }
    io_printf (IO_BUF, "\n");
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
		    "mov   %[mask_0x3fc], #0x3fc                    @  .. and with 0x3fc                          \n\t"	 \
		    "ldr   %[w], [%[wp]], #4                        @ Pre-load first word of rowlets              \n\t"	 \
		    : [time_base] "=r" (time_base), [jump] "=r" (jump), [mask_0x3c] "=r" (mask_0x3c),                    \
		      [wp] "+r" (wp), [w] "=r" (w), [mask_0x3fc] "=r" (mask_0x3fc)  				                 \
		    : [BASE] "J" (TIME_BASE), [JUMP] "J" (DISPATCH_TABLE), [ctrl] "r" (ctrl) : "memory");                \
  } while (false)

#define initialise_control()					                                           \
  do {									                                   \
      ((uint64_t*)__control)[GLOBAL_TIMER >> 2] = 0;                              /* Set 64-bit timer   */ \
      __control[DMA_BUFFER_READ >> 2]           = (uint32_t)dma_buffer0;          /* Set up DMA buffers */ \
      __control[DMA_BUFFER_WRITE >> 2]          = (uint32_t)dma_buffer1;		                   \
      __control[TIME_BASE >> 2]                 = ((uint32_t)ring_buffer0 >> 14); /* Set up time_base   */ \
  } while (false)

//=============================================================================
// Global Timer Routines (the SpiNNaker simulation clock)
//=============================================================================

//! \brief We use the following union type to allow us to address the global
//! clock words in the control array.

#define __global_timer_address ((uint64_t*)((uint32_t)__control + GLOBAL_TIMER))

//! \brief Increment the global timer.

#define global_timer_tick()						                                                \
  do {asm volatile ("ldr  r0, [%[ctrl], %[lo]]  @ Load the low word of the timer                                  \n\t"	\
		    "ldr  r1, [%[ctrl], %[hi]]  @ Load the high word of the timer                                 \n\t"	\
		    "adds r0, r0, #1            @ increment low word (setting carry flag if necessary)            \n\t" \
		    "adc  r1, r1, #0            @ increment high word (absorbing carry flag if necessary)         \n\t" \
		    "str  r0, [%[ctrl], %[lo]]  @ Store the low word of the timer                                 \n\t"	\
		    "ldr  r1, [%[ctrl], %[hi]]  @ Store the high word of the timer                                \n\t"	\
		    : : [ctrl] "r" (ctrl), [lo] "J" (GLOBAL_TIMER_LO), [hi] "J" (GLOBAL_TIMER_HI) : "memory");          \
  } while (false)


//! \brief Returns the current global clock value.

uint64_t global_timer_value (void) {   return (*(__global_timer_address)); }

//! \brief Sets the current global clock value.

void set_global_timer (uint64_t t) {   *(__global_timer_address) = t;      }

//=============================================================================

#define time_base_tick()						                                                  \
  do {asm volatile ("ldr  r0, [%[ctrl], %[time]]  @ Load the time_base word                                         \n\t" \
		    "add  r0, r0, #0x10000000     @ increment time_base word                                        \n\t" \
		    "str  r0, [%[ctrl], %[time]]  @ Store the time_base word                                        \n\t" \
		    : : [ctrl] "r" (ctrl), [time] "J" (TIME_BASE) : "memory");                                            \
  } while (false)

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
    register uint32_t  mask_0x3fc        asm ("r4");
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



//!


/*

On entry 
//! Registers: r0  Done       The two bits of status indicating DMA-completion .... SS.. .... ....
//!            r2  DMA-status The entirity of the DMA status word
//!            r3  DMA-queues Four 8-bit counters for different DMA input queue lengths
//!            r4  DMA-base   The Base Address of the DMA engine memory-mapped registers

mov    %[mask_0x3fc], 0x3fc      @ load up byte mask_0x3fc
ands   r1, r3, %[mask_0x3fc]     @ and out highest priority DMA requests

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


//! \brief This is the default out-going dma processing routine, and is
//! called when we have _no_ out-going DMA requests to perform. This
//! happens -- if at all -- near the end of a clock tick when all DMA queues
//! are empty.

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
//! branch-and-link is taken then this code takes seven cycles to execute (plus at
//! least three to return).
//!
//! Registers: r0  Address of a DMA set-up routine
//!            r2  DMA-status The two done bits of the DMA status word
//!            r3  DMA-base   The Base Address of the DMA engine's memory-mapped registers

#define feed_dma_if_needed()						                                                   \
    do {asm volatile ("ldr    r1, [%[ctrl], %[addr]]    @ Load address of an outgoing DMA processing routine         \n\t" \
		      "mov    r3, #0x40000000           @ Load base-address of DMA register base                     \n\t" \
		      "ldr    r2, [r3, %[status]]       @ Check DMA status                                           \n\t" \
		      "cmp    r1, #0                    @ Test dma_processing address; if 0 then DMA requests empty  \n\t" \
		      "andnes r2, r2, #0xc00            @ Test whether there are any spare DMA slots, this occurs .. \n\t" \
		      "                                 @   .. if either of the DMA-completed flags are set          \n\t" \
		      "blxne  r1                        @ Set up new DMA(s), provided there are slots and requests   \n\t" \
		      : : [ctrl] "r" (ctrl), [addr] "J" (DMA_PROCESSING), [status] "J" ((DMA_STAT) << 2): "cc", "memory"); \
    } while (false)


//! \brief Translates a rowlet descriptor word (RDW) into a sequence of three
//! words that can be directly copied to the DMA registers.
//!
//! A Rowlet Descriptor word consists of three blocks of bits:
//!
//!      AAAA AAAA AAAA AAAA AAAA ADDD DSSS SSSS
//!
//! with a 21-bit address offset (from this processor's base SDRAM address) in
//! SDRAM, a 4-bit delay before this rolwet is acted upon, and a 7-bit size.
//!
//! Each of these words is translated into a three word DMA command in the DMA
//! Command Buffer; The first word is the actual SDRAM address, the second is
//! the DTCM address for delivery, and the third word is the DMA control word,
//! with a suitable burst size.
//!
//! NOTE: Does not write to dma[4] to reset completed dma counter in bits 10-11 of dma[3]
//!
//! In use, we need only use the code:
//!
//!      mov   r3, #0x8          @ Cancel one of the DMA-completed flags.
//!             .......
//!      ldmia %[dp]!, {r0-r2}   @ Load the DMA Command words, from cp, auto-incrementing
//!      stmib %[dma], {r0-r3}   @ Do DMA transfer ..
//!
//! The translation code takes 12 cycles to complete. If we are lucky the copy-to-DMA
//! code above takes 8 cycles.
//!
//! \param     w     The rowlet descriptor word
//! \param     wp    A pointer to the rowlet descriptor words
//! \param[in] mask_0x3fc  The mask_0x3fc bit pattern 0x3fc
//! \param     bp    A pointer to the eventual DTCM memory address for the DMA transfer.
//! \param     dp    A pointer to the DMA Command buffer
//! \param[in] burst A pointer to the table used to calculate the required burst size.
//! \param[in] sdram Base address for this processor's allocation of SDRAM.

#define rdw_to_dma_register_sequence()					                                                   \
  do {asm volatile ("ldr   %[w], [%[wp]], #4             @ Load next rowlet descriptor word w                        \n\t" \
		    "str   %[bp], [%[dp], #4]            @ Store DTCM address (no dp increment)                      \n\t" \
		    "bic   %[w], %[w], #0x780            @ Mask out delay bits                                       \n\t" \
		    "and   r0, %[mask_0x3fc], %[w], lsl #2  @ mask the size bits of w as ..0S SSSS SS..              \n\t" \
		    "add   r0, r0, #4                    @ Add 1: DMA-ing 0 words is silly                           \n\t" \
		    "clz   r1, r0                        @ Take log_2(size)                                          \n\t" \
		    "ldrb  r1, [%[burst], r1]            @ Load the burst/control byte                               \n\t" \
		    "add   %[w], %[sdram], %[w], lsr #9  @ SDRAM address                                             \n\t" \
		    "str   %[w], [%[dp]], #8             @ Store SDRAM address (double increment for dp)             \n\t" \
		    "add   %[bp], %[bp], r0              @ increment the DTCM pointer                                \n\t" \
		    "orr   r0, r0, r1, lsl #20           @ Add size to shifted control word                          \n\t" \
		    "str   r0, [%[dp]], #4               @ Store DMA Descriptor Word (incrementing dp)               \n\t" \
		    : [w] "=r" (w), [dp] "+r" (dp), [wp] "+r" (wp), [bp] "+r" (bp)                                         \
		    : [burst] "r" (burst), [sdram] "r" (sdram), [mask_0x3fc] "r" (mask_0x3fc)                              \
		    : "memory");		                                                                           \
  } while (false)

#define rdw_loop_decrement_and_test()					                                                   \
  do {asm volatile ("subs %[n], %[n], #8                 @ decrement and test the 'loop counter'                     \n\t" \
		    "                                    @   (actually the number of synapses to be processed -1)    \n\t" \
		    "bpl  rdw_loop                       @ If the number is still positive then loop again           \n\t" \
		    : [n] "=r" (n) : : "cc", "memory");				                                           \
  } while (false)

#define rdw_setup_and_dispatch()                                                                                           \
    do {asm volatile ("ands  r0, %[n], #7                @ Get the remainder mod 8                                   \n\t" \
		      "lsl   r0, r0, #2                  @ line up for table jump \n\t"\
		      "ldr   r0, [%[burst], -r0]         @ Need to ensure a negative index never collides with a     \n\t" \
		      "                                  @   positive one. This is true because of the burst offset. \n\t" \
		      "subeq %[n], %[n], #8              @ subtract '1' from n for loop counter, and                 \n\t" \
		      "bx    r0                          @   __branch__ to the looping process                       \n\t" \
		      : [n] "=r" (n) : [burst] "r" (burst) : "cc", "memory");                                              \
    } while (false)

//! \brief Translates a sequence of 8 Rowlet Description Words (RDW's) into a
//! sequence of DMA transfer words.


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
//!   ror    a0, a0, #18                 ; rotate around to the correct position
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
//!   ror    a0, a0, #18                 ; rotate around to the correct position
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
//!                            ;  which needs to be combined with adding and mask_0x3fcing the current time
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
                    "ror    r4, r4, #18                     @ Rotate back again                                   \n\t"	\
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
                    "ror    r3, r3, #18                     @ S0 Rotate back again                 \n\t" \
                    "ldrh   r0, [r3]                        @ S0 Load the ring-buffer element      \n\t" \
		    "add    r4, %[time_base], r2, lsl #20   @ S1 Add to rotated time_base          \n\t" \
                    "ror    r4, r4, #18                     @ S1 Rotate back again                 \n\t" \
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
//! mask_0x3fc   r7   Mask 0x3fc
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
                    "ror    r3, r3, #18                      @ S1 Rotate back again                      \n\t" \
                    "ldrh   r1, [r3]                         @ S1 Load the ring-buffer element           \n\t" \
		    "add    r4, %[time_base], lr, lsl #20    @ S2 Add to rotated time_base               \n\t" \
                    "add    r2, %[time_base], %[w], lsl #20  @ S0 Add to rotated time_base               \n\t" \
		    "subs   r1, r1, r0, lsr #20              @ S1 'add' weight to ring buffer            \n\t" \
		    "strplh r1, [r3]                         @ S1 write back ring buffer, if OK          \n\t" \
                    "ror    r3, r2, #18                      @ S0 Rotate back again                      \n\t" \
                    "ldrh   r0, [r3]                         @ S0 Load the ring-buffer element           \n\t" \
                    "ror    r4, r4, #18                      @ S2 Rotate back again                      \n\t" \
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
		  "ror    r2, r2, #18                      @ S1 Rotate back again                                     \n\t"
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
//!    and    r2, %[mask_0x3fc], %[w], lsr #10      @ S2 mask out middle 8-bits from w into bits 8-1
//!                                           @ r2 = .... .... .... .... .... ...i iiii iii. (. = 0)
//!
//!    add    r4, %[time_base], lr, lsl #28   @ S2 add delay to timer_base (= 4 bits time + base)
//!                                           @ r4 = tttt .... .... E... .... ..10 0000 0000
//!                                           @ where tttt = (bottom 4-bits of time + dddd), ignoring carry;
//!                                           @       . = 0; and
//!                                           @       E-bit indicates excitatory (0 = inhibitory)
//!
//!    orr    r4, r2, r4, ror #18             @ S2 rotate to position and 'or' in index bits
//!                                           @ r4 = 0000 0000 0100 0000 00tt ttii iiii iiE0
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
//!                     mask_0x3fc       holds 0x1fe
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
		  "and    r2, %[mask_0x3fc], %[w], lsr #10  @ S2 mask out middle 8-bits from w into bits 9-2      \n\t" \
		  "add    r3, %[time_base], %[w], lsl #20 @ S0 add delay|index to timer_base                    \n\t" \
		  "add    r4, %[time_base], lr, lsl #28   @ S2 add delay to timer_base (= 4 bits time + base)   \n\t" \
		  "orr    r4, r2, r4, ror #18             @ S2 rotate to position and 'or' in index bits        \n\t" \
		  "ldrh   r2, [r4]                        @ S2 load ring-element                                \n\t" \
		  "ror    r3, r3, #18                     @ S0 rotate to position                               \n\t" \
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
		  "and    r3, %[mask_0x3fc], r1, lsr #10    @ S3 mask out middle 8-bits from w into bits 9-2   \n\t" \
		  "add    %[w], %[time_base], lr, lsl #28 @ S3 add delay to timer_base (= 4 bits time + base)   \n\t" \
		  "orr    %[w], r3, %[w], ror #18         @ S3 rotate to position and 'or' in index bits        \n\t" \
		  "ldrh   r3, [%[w]]                      @ S3 load ring-element                                \n\t" \
		  "add    r4, %[time_base], r1, lsl #20   @ S1 add delay|index to timer_base                    \n\t" \
		  "ror    r4, r4, #18                     @ S1 rotate to position                               \n\t" \
		  "subpls r3, r3, lr, lsr #4              @ S3 conditionally 'add' weight, if OK so far         \n\t" \
		  "ldrh   lr, [r4]                        @ S1 load ring-element                                \n\t" \
		  "strplh r3, [%[w]]                      @ S3 conditionally store ring-element                 \n\t" \
		  "ldr    %[w], [%[wp]], #4               @ S4 Pre-load next synaptic word                      \n\t" \
		  "subpls r1, lr, r1, lsr #20             @ S1 conditionally 'add' weight, if OK so far         \n\t" \
		  "strplh r1, [r4]                        @ S1 conditionally store ring-element                 \n\t" \
		  "blmi   __packed_fix_up_4               @ Perform fix-up, if saturation occurred              \n\t" \
		  : [w] "+r" (w), [wp] "+r" (wp) : [time_base] "r" (time_base), [mask_0x3fc] "r" (mask_0x3fc) : "cc", "memory");  \
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
"add    r4, r2, r4, ror #18                 @ S2 i2 = r2 now free
"ldrh   r2, [r4]                            @ S2
"ror    r3, r3, #18                         @ S0
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
(B2) and    i3, %[mask_0x3fc], w1, lsr #10    @ S3   |  i3  |    | w1 | .. | .. |    |    |    |_i3_|    |    |    |
(B1) add    a3, %[time_base], w3, lsl #28     @ S3   |  a3  |    | .. | w3 | .. |_a3_|    |    | .. |    |    |    | 
(D)  add    a3, i3, a3, ror #18               @ S3   |  a3  |    | .. | .. | .. |*a3 |    |    | i3 |    |    |    |
(E)  ldrh   r3, [a3]                          @ S3   |  r3  |    | .. | .. | .. | a3 |    |_r3_|    |    |    |    |
(3)  ror    a1, a1, #18                       @ S1   |  a1  |    | .. | .. |*a1 | .. |    | .. |    |    |    |    |
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
(3)  ror    a1, a1, #18                    @ S1   |  a1  |    | .. | .. |*a1 | .. |    |    | .. |    |    |    | 5
(4)  ldrh   r1, [a1]                       @ S1   |  r1  |    | .. | .. | a1 | .. |_r1_|    | .. |    |    |    | 6*
(D)  add    a3, i3, a3, ror #18            @ S3   |  a3  |    | .. | .. | .. |*a3 | .. |    | i3 |    |    |    | 6*
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
(D)  add    a3, i3, a3, ror #18            @ S3   |  a3  |    | .. | .. |    |*a3 |    |    | i3 |    |    |    | 4
(E)  ldrh   r3, [a3]                       @ S3   |  r3  |    | .. | .. |    | a3 |    |_r3_|    |    |    |    | 4
(2)  add    a1, %[time_base], w1, lsl #28  @ S1   |  a1  |    | w1 | .. |_a1_| .. |    | .. |    |    |    |    | 5
(3)  ror    a1, a1, #18                    @ S1   |  a1  |    | .. | .. |*a1 | .. |    | .. |    |    |    |    | 5
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
(B2) and    r3, %[mask_0x3fc], r1, lsr #10  @ S3
(B1) add    %[w], %[time_base], lr, lsl #28 @ S3
(D)  add    %[w], r3, %[w], ror #18         @ S3
(E)  ldrh   r3, [%[w]]                      @ S3    r3 starts here!
(2)  add    r4, %[time_base], r1, lsl #28   @ S1    a1 starts here!
(3)  ror    r4, r4, #18                     @ S1
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
(3)  ror    a1, a1, #18                       @ S1
(4)  ldrh   r1, [a1]                          @ S1
(5)  subpls r1, r1, w1, lsr #20               @ S1
(6)  strplh r1, [a1]                          @ S1

(A)  ldrh   w3, [%[wp]], #4                   @ S3
(B1) add    a3, %[time_base], w3, lsl #28     @ S3
(B2) and    i3, %[mask_0x3fc], w1, lsr #10    @ S3
(D)  add    a3, i3, a3, ror #18               @ S3
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
		  "and    r4, %[mask_0x3fc], %[w], lsr #10  @ S2 mask out middle 8-bits from w into bits 9-2           \n\t"
		  "add    %[w], %[time_base], %[w], lsl #20 @ S0 add delay to timer_base and mask with shift           \n\t"
		  "ror    %[w], %[w], #18                   @ S0 rotate to position                                    \n\t"
		  "cmp    r0, #0                            @ Did the fourth synapse (S0) saturate?                    \n\t"
		  "movmi  r0, #0                            @ Saturated value in r0, if required (otherwise old value) \n\t"
		  "strh   r0, [%[w]]                        @ Store back modified result in all cases                  \n\t"
		  "addpl  r1, r1, #-1                       @ local saturation counter r1 holds sat-count - 2          \n\t"
		  "ldrh   %[w], [%[wp], #-6]                @ S2 Pre-load synaptic half-word for S2 with 0x wwwd       \n\t"
		  "add    %[w], %[time_base], %[w], lsl #28 @ S2 add delay to timer_base (= 4 bits time + base)        \n\t"
		  "orr    %[w], r4, %[w], ror #18           @ S2 rotate to position and 'or' in index bits             \n\t"
		  "cmp    r2, #0                            @ Did the fourth synapse (S0) saturate?                    \n\t"
		  "movmi  r2, #0                            @ Saturated value in r2, if required (otherwise old value) \n\t"
		  "strh   r2, [%[w]]                        @ Store back modified result in all cases                  \n\t"
		  "addpl  r1, r1, #-1                       @ local saturation counter r1 holds sat-count - 3          \n\t"
		  "ldr    %[w], [%[wp], #-8]                @ recalculate address for (S3) ring-buffer                 \n\t"
		  "and    r4, %[mask_0x3fc], %[w], lsr #10  @ S3 mask out middle 8-bits from w into bits 9-2           \n\t"
		  "ldrh   %[w], [%[wp], #-4]                @ S3 Pre-load synaptic half-word for S3 with 0x wwwd       \n\t"
		  "add    %[w], %[time_base], %[w], lsl #28 @ S3 add delay to timer_base (= 4 bits time + base)        \n\t"
		  "orr    %[w], r4, %[w], ror #18           @ S3 rotate to position and 'or' in index bits             \n\t"
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
		  : [time_base] "r" (time_base), [wp] "r" (wp), [ctrl] "r" (ctrl), [mask_0x3fc] "r" (mask_0x3fc),
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
//!	"add    r4, %[wp], r4, ror #18            @ S0 Add in the index, via wp                        \n\t"
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
		      "add    r4, %[wp], r4, ror #18            @ S0 Add in the index, via wp                        \n\t" \
		      "ldrh   r0, [r4, #-4]                     @ S0 Load ring-buffer weight	                     \n\t" \
		      "add    r5, %[time_base], %[h1], lsl #28  @ S1 Add delay to time-base                          \n\t" \
		      "add    r5, %[wp], r5, ror #18            @ S1 Add in the index, via wp                        \n\t" \
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
		      "add    r4, %[wp], r4, ror #18            @ S2 Add in the index, via wp                        \n\t" \
		      "ldrh   r2, [r4, #-4]                     @ S2 Load ring-buffer weight	                     \n\t" \
		      "add    r5, %[time_base], %[h1], lsl #28  @ S3 Add delay to time-base                          \n\t" \
		      "add    r5, %[wp], r5, ror #18            @ S3 Add in the index, via wp                        \n\t" \
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
    register uint32_t  mask_0x3fc      asm ("r7");  // Mask 0x1fe

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
		  "add    r4, %[wp], r4, ror #18            @ S0 Add in the index, via wp                        \n\t"
		  "cmp    r0, #0                            @ Did S0 saturate?                                   \n\t"
		  "movmi  r0, #0                            @ Saturate if needed.                                \n\t"
		  "strh   r0, [r4, #-16]                    @ S0 Load ring-buffer weight	                 \n\t"
		  "addpl  r2, r2, #-1                       @ r2 is local sat-counter.                           \n\t"
		  "add    r5, %[time_base], r5, lsl #28     @ S1 Add delay to time-base                          \n\t"
		  "add    r5, %[wp], r5, ror #18            @ S1 Add in the index, via wp                        \n\t"
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
		    [off] "J" (SATURATION_COUNTER), "r" (mask_0x3fc), "r" (n), "r" (w) : "cc", "memory");
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
    register uint32_t  mask_0x3fc      asm ("r7");  // Mask 0x1fe

    asm goto ("cmp  %[n], #0     @ Test whether the rolwet is empty (SHOULD NOT HAPPEN) \n\t"
	      "bxeq lr           @ Return if there are no synapses  (SHOULD NOT HAPPEN) \n\t"
	      "push {lr}         @ Otherwise, push link register: we might need to ..   \n\t"
	      "                  @  .. call saturation fix-up or dma feeding routines.  \n\t"
	      "tst  %[n], #1     @ Test to see if there's an odd synapse                \n\t"
	      "beq  %l[L0]       @ If not skip over synapse_1                         \n\t"
	      : : [n] "r" (n), "r" (mask_0x3fc) : "cc" : L0);

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
    register uint32_t  mask_0x3fc      asm ("r7");  // Mask 0x1fe

    register uint32_t  h0        asm ("r7");
    register uint32_t  h1        asm ("r6");
    register uint32_t  r5        asm ("r5");
    register uint32_t  r4        asm ("r4");

    asm volatile ("push   {lr}                              @ Return                                             \n\t"
		  "ldr    %[h1], [%[wp]], #4                @ Load synapses (Has this aleady been done?)         \n\t"
		  "mov    %[n], #15                         @ Number of loops to execute                         \n\t"
		  : [n] "=r" (n), [h1] "=r" (h1) : [wp] "r" (wp), "r" (mask_0x3fc), "r" (w), "r" (time_base), "r" (ctrl)
		  : "cc", "memory");

    h0 = 0xffff; // set up mask for one synpase


    asm volatile ("and    %[h0], %[h1], %[h0]               @ Initialise S0                                      \n\t"
		  "lsr    %[h1], %[h1], #16                 @ Initialise S1; Assumes little-endianness           \n\t"
		  : [h0] "+r" (h0), [h1] "+r" (h1) : : "cc", "memory");

    printx ((uint32_t)wp);
    printx (h0);
    printx (h1);

    //               wp = 00402004
    // time_base ror 18 = 00004000
    // ---------------------------
    //
   
    asm volatile ("add    r4, %[time_base], %[h0], lsl #28  @ S0 Add delay to time-base                          \n\t"
		  "add    r4, %[wp], r4, ror #18            @ S0 Add in the index, via wp                        \n\t"
		  "ldrh   r0, [r4, #-4]                     @ S0 Load ring-buffer weight	                 \n\t"
		  "add    r5, %[time_base], %[h1], lsl #28  @ S1 Add delay to time-base                          \n\t"
		  "add    r5, %[wp], r5, ror #18            @ S1 Add in the index, via wp                        \n\t"
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
		      "ror    r4, r4, #18                    @ S0 rotate to position                              \n\t"	\
		      "ldrh   r0, [r4]                       @ S0 load ring-element                               \n\t"	\
		      "add    r5, %[time_base], r3, lsl #20  @ S1 add delay to timer_base and mask with shift     \n\t"	\
		      "ror    r5, r5, #18                    @ S1 rotate to position                              \n\t"	\
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
		      "add    r4, r0, r4, ror #18            @ S2 add neuron id and rotate                        \n\t"	\
		      "add    r5, %[time_base], r3, lsl #28  @ S3 add delay to timer_base and mask with shift     \n\t"	\
		      "ldrh   r0, [r4]                       @ S2 load ring-element                               \n\t"	\
		      "add    r5, r1, r5, ror #18            @ S3 add neuron id and rotate                        \n\t"	\
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
     add    a0, wp, a0, ror #18               @ S0
     ldrh   w0, [a0, #-4]                     @ S0 Load ring-buffer weight
>       add    a1, %[time_base], h1, lsl #28     @ S1 Add delay to time-base
>       add    a1, wp, a1, ror #18               @ S1
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
     add    a0, wp, a0, ror #18
     ldrh   h1, %[wp], #2                     @ Load a half word synapse
     ldrh   w0, [a0]                          @ Load ring-buffer weight
>
     add    a1, %[time_base], h1, lsl #28     @ Add delay to time-base
     add    a1, wp, a1, ror #18
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
     add    a0, wp, a0, ror #18
     add    a1, %[time_base], s1, lsl #12     @ Add delay to time-base (extraneous bits in lower part of s1)
     add    a1, wp, a1, ror #18

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
     add    a0, wp, a0, ror #18
     ldrh   h1, %[wp], #2                     @ Load a half word synapse
     ldrh   w0, [a0]                          @ Load ring-buffer weight
>
     add    a1, %[time_base], h1, lsl #28     @ Add delay to time-base
     add    a1, wp, a1, ror #18
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
     add    a0, wp, a0, ror #18               @ S0
     ldrh   h1, %[wp], #2                     @ S1 Load a half word synapse
>
     ldrh   w0, [a0]                          @ S0 Load ring-buffer weight
     add    a1, %[time_base], h1, lsl #28     @ S1 Add delay to time-base
     add    a1, wp, a1, ror #18               @ S1
     ldrh   w1, [a1]                          @ S1 Load ring-buffer weight
     subs   w0, w0, h0, lsr #4                @ S0 'add' weight
     strplh w0, [a0]                          @ S0 Conditionally store ring-element
     ldrh   h0, %[wp], #2                     @ S0 Load a half word synapse

     subpls w1, w1, h1, lsr #4                @ S1 'add' weight
     strplh w1, [a1]                          @ S1 Conditionally store ring-element


Trial 5 This might just work!!!! Needs topping and tailing!!

h0, h1 pre-loaded. wp pointing at next h0,h1 pair

     add    a0, %[time_base], h0, lsl #28     @ S0 Add delay to time-base
     add    a0, wp, a0, ror #18               @ S0
     ldrh   w0, [a0, #-4]                     @ S0 Load ring-buffer weight
>       add    a1, %[time_base], h1, lsl #28     @ S1 Add delay to time-base
>       add    a1, wp, a1, ror #18               @ S1
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
// word w; i.e. bit 12-18. These are encoded as follows:
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
		      "@ Because we have reached this point via a primary dispatch, certain registers already have   \n\t" \
		      "@ their contents determined.                                                                  \n\t" \
		      "@                                                                                             \n\t" \
		      "@ At this point w  contains: .... .... 0001 0000 00EX .... .QQQ QQSS     (. is don't care)    \n\t" \
		      "@ At this point r1 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)             \n\t" \
		      "@---------------------------------------------------------------------------------------------\n\t" \
		      "ldr   r0, [%[jump], r1]                @ Set up 16-way primary dispatch jump address          \n\t" \
		      "and   %[n], %[w], #0x7c                @ Mask out to leave just the bits in n                 \n\t" \
		      "ldr   %[w], [%[wp]], #4                @ Pre-load next synaptic word                          \n\t" \
		      "bx    r0                               @ Take the primary jump unconditionally                \n\t" \
		      : [n] "=r" (n), [w] "+r" (w), [wp] "+r" (wp) : [mask_0x3c] "r" (mask_0x3c), [jump] "r" (jump)        \
		      : "memory");					                                                   \
        } while (false)

#define set_excitatory_time_base()					                                                   \
    do {asm volatile ("orr %[time_base], %[time_base], #0x00080000   @ Set bit 19 of time-base                       \n\t" \
		    : [time_base] "+r" (time_base)); } while (false)

#define set_inhibitory_time_base()					                                                   \
    do {asm volatile ("bic %[time_base], %[time_base], #0x00080000   @ Clear bit 19 of time-base                     \n\t" \
		    : [time_base] "+r" (time_base)); } while (false)

#define excitatory_bit_orr_time_base()					                                             \
  do {asm volatile ("and r0, %[w], #0x2000                                 @ Get excitatory bit from word 'w'  \n\t" \
		    "orr %[time_base], %[time_base], r0, lsl #6            @  .. and or it in                  \n\t" \
		    : [time_base] "+r" (time_base) : [w] "r" (w)); \
  } while (false)

#define synapse_loop_decrement_and_test()					                              \
  do {asm volatile ("subs %[n], %[n], #16    @ decrement and test the 'loop counter'                    \n\t" \
		    "                        @   (actually the number of synapses to be processed -1)   \n\t" \
		    "bpl  packed_quad_loop   @ If the number is still positive then loop again          \n\t" \
		    : [n] "+r" (n) : : "cc");				                                      \
  } while (false)

#include "neuron_asm.h"
#include "rdw-asm.h"
#include "poisson-asm.h"
