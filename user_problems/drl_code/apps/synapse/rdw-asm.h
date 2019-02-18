/*
rdw-asm.h
*/

uint32_t rdw_buffer[256];

//! \brief Translates each rowlet in tmp into a Rowlet Descriptor Word (RDW).
//! This is a 32-bit word, split into three parts: an "address" part, a "delay"
//! part, and a "size" part. These ae of sizes: 21, 4, and 7 bits each as
//! follows.
//!
//!      31....................................0
//!      AAAA AAAA AAAA AAAA AAAA ADDD DSSS SSSS
//!
//! The information in this word is to be interpreted as follows. The address
//! data in the A-bits is added to SDRAM base register for this processor to
//! give word-aligned addressing to 8M Byte of SDRAM reserved for _this_
//! processor. The delay of 0-15 'ticks' as indicated by the D-bits sends the
//! current RDW to a delayed RDW buffer. Eventually this buffer comes to the
//! front of the queue, and the RDWs are decoded and then DMA-ed into a DMA-
//! buffer from which they ae eventually processed into the ring-buffer.
//! Finally the seven S-bits encode the number of _words_ involved to be
//! transferred by the DMA. Because a DMA transfer of 0 words is pointless,
//! we add  to get the actual size of a transfer, giving possible values
//! of 1-128 words.
//!
//! To recap: the RDW has three pieces of information: an address in SDRAM,
//! a delay before any action is taken to transfer a rowlet's contents to the
//! ring-buffers, and the size of the DMA to be requested.
//!
//! Possible Usages
//! ---------------
//!
//! (1) Long (axonal) delays before any synapses activate can be modelled by using
//!     indirections.
//!
//!     +---+---+     +---+---+
//!     | H | R-+---> | H | R-+---> ....
//!     +---+---+     +---+---+
//!
//!     The required header H word is 0x00202000
//!                                       ^ ^
//!                                       | +-- Indicates the presence of an extension.
//!                                       +---- Indicates the secondary dispatch tag of 2.
//!
//!     The RDW R might be of the following form 0x0000f781
//!                                                    ^ ^^
//!                                                    | |+--- 1  indicates size 2 words (= 1+1)
//!                                                    | +---- 78 indicates a delay of 15.
//!                                                    +------ f  indicates an SDRAM address of sdram_base + 0x3c
//!                                                               (f indicates 15th _word_ thus add 60 to the base address).
//!
//! (2) If there are more than 169 synapses, then they will not all fit into a
//!     single rowlet. So long as not all of the synapses have the same delay,
//!     we can chain two rowlets together, ordering the synapses so that the
//!     earlier ones (i.e. those with a shorter delay) occur in the first
//!     rowlet, and the later ones (with a longer delay) occur in the second
//!     rowlet.
     

uint32_t tmp_to_rdw (void) __attribute__ ((noinline));
uint32_t tmp_to_rdw (void) 
{
  uint32_t* wp  = dma_buffer0;
  uint32_t* out = rdw_buffer;
  uint32_t  w;
  uint32_t  n = 0;
  uint32_t  addr = 0;
  uint32_t  byte, ssex, quads, odds, ext, size;
  

  w = *wp;

  while (w != 0) {
      byte  = middle_byte (w);
      ssex  = byte & 0xf;
      ext   = ssex & 1;
      odds  = (ssex >> 2) & 3;
      quads = (byte >> 4) & 0xf;

      if ((byte & 0xfc) == 0) { //secondary
	  odds  = w & 3;
	  quads = (w >> 2) & 0x3f;
	  size  = odds + 3*quads + ext + 1; // extra 1 for header
      }
      else {// primary
	  size   = odds + 3 * quads + ext;
	  if (odds == 0)
	      size++; // exta word for stand-alone header
      }
      io_printf (IO_BUF, "  n = %2u; w = %08x; size = %3u; addr = %04x; RDW = %08x\n",
		 n+1, w, size, addr,
		 (addr << 11) | (size - 1));
      
      *out++ =  (addr << 11) | (size - 1);
      addr  += size;
      wp    += size;
      w      = *wp;
      n++;
  }
  
  return (n);
}


#define advance_rdw_buffers()					                 \
    do {									 \
        __label__ Loop;							         \
									         \
	asm volatile ("ldr r3, [%[ctrl]]     @ Load lo delay pointer       \n\t" \
		      "ldr r1, [%[ctrl], #4] @ Load lo delay pointer       \n\t" \
		      "add r2, %[ctrl], #4   @ Initialise pointer          \n\t" \
		      "str r1, [%[ctrl]]     @ Store lo delay pointer      \n\t" \
		      : : [ctrl] "r" (ctrl) : "cc", "memory");		         \
    Loop:								         \
	asm goto     ("ldr r0, [r2, #4]      @ Load lo delay pointer       \n\t" \
		      "ldr r1, [r2, #8]      @ Load hi delay pointer       \n\t" \
		      "str r0, [r2], #8      @ Store lo delay pointer      \n\t" \
		      "str r1, [r2, #-4]     @ Store hi delay pointer      \n\t" \
		      "sub r0, r0, #60       @ Test for loop completion    \n\t" \
		      "cmp r0, %[ctrl]       @ Test for loop completion    \n\t" \
	asm goto     ("bmi %l[Loop]          @ Loop back                   \n\t" \
		      "bic r3, r3, 0x3fc     @ reset buffer pointer        \n\t" \
		      "str r3, [%[ctrl], #64] @ Store last delay pointer   \n\t" \
		      : : [ctrl] "r" (ctrl) : "cc", "memory" : Loop);            \
    } while (false)

//! \brief A Code fragment to place a extension description word -- placed
//! immediately after the current word w -- into the correct delay buffer.
//!
//! It uses regsiters r0, r1, r2 as scratch, increments the synaptic word
//! pointer wp, and uses the constants in ctrl and time_base.
//!
//! This code has 5 instructions, and takes 7 cycles to execute.
//!
//! Note that we can improve the performance by combining this code with other
//! subsequent code in order to hide the pipeline interlocks shown. This will
//! have the effect of _increasing_ the number of code fragments, since we can
//! no longer just jump into the code using a fixed 20 byte offset.

#define rowlet_extension()						                                                   \
    do {asm volatile ("ldr   r2, [%[wp]], #4               @ Load the rowlet descriptor                              \n\t" \
		      "and   r3, %[mask_0x3c], r3, lsr #26 @ Mask out all but bits 2-5                               \n\t" \
		      "ldr   r1, [%[ctrl], r3]	           @ Load rowlet buffer pointer                              \n\t" \
		      "@ ----------------->                @ pipeline interlock here                                 \n\t" \
		      "str   r2, [r1], #4                  @ Store rowlet in buffer                                  \n\t" \
		      "str   r1, [%[ctrl], r3]	           @ Write-back the rowlet buffer pointer                    \n\t" \
		      : [wp] "+r" (wp) : [mask_0x3c] "r" (mask_0x3c), [ctrl] "r" (ctrl) : "memory");                       \
    } while (false)
