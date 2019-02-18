
#include <stdint.h>
#include <stdbool.h>
#include <arm_acle.h>
#include <sark.h>
#include "stdfix-full-iso.h"
#include "random.h"

uint32_t time;

void     initialise_timer (void)      __attribute__ ((noinline));
void     start_timer      (void)      __attribute__ ((noinline));
void     stop_timer       (void)      __attribute__ ((noinline));

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

    time -= t+20;

    asm volatile ("pop {r1, r2, r3}\n\t" : : : "memory");
}

//! \brief A non-disturbing hex printer. Has no _overall_ effect on any
//! registers apart from r0 (used to pass argument, and even that is restored),
//! since any that are affected by the print, are stacked and then unstacked at
//! the end.
//!
//! \param[in] x The unsigned integer to be printed

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


//  [dma, #4]  SDRAM address        (ADRS)
//  [dma, #8]  TCM   address        (ADRT)
//  [dma, #12] transfer description (DESC)
//  [dma, #16] control transfer     (CTRL)
//  [dma, #20] status               (STAT) (read-only)
//  [dma, #24] device control       (GCTL)

//  [dma, #40] Stats control        (StatsCtl)




//! \brief This function loads a pointer to the base register of the DMA
//! engine into the register ip.
//!
//! Note: it affects no other registers.

void dma_register_load (void) __attribute__ ((noinline, naked));
void dma_register_load (void) 
{   asm volatile ("mov ip, #0x40000000\n\t" : : : "memory"); }

//! \brief This function writes a DMA request into the DMA engine. Can be
//! in-lined.
//!
//! Notes:
//!
//!     (0) Assumes ip register loaded with DMA base address.

void dma_request (uint32_t* addr_s, uint32_t* addr_t, uint32_t desc)
{
    uint32_t* base = (uint32_t*)0x40000000;

    base[1] = (uint32_t)addr_s;
    base[2] = (uint32_t)addr_t;
    base[3] = desc;
    
  /*    asm volatile ("mov ip, #0x40000000\n\t"
		  "str %[addr_s], [ip, #4]\n\t"
		  "str %[addr_t], [ip, #8]\n\t"
		  "str %[desc],   [ip, #12]\n\t"
		  : : [addr_s] "r" (addr_s), [addr_t] "r" (addr_t),
		  [desc]   "r" (desc) : "memory");*/
}


void dma_error_registers (void)
{
    uint32_t* base    = (uint32_t*)0x40000000;

    io_printf (IO_BUF, "AD2S = %08x\n", base[65]);
    io_printf (IO_BUF, "AD2T = %08x\n", base[66]);
    io_printf (IO_BUF, "DES2 = %08x\n", base[67]);

}

//! \brief Returns the status word of the DMA in registe r0. Can be in-lined.
//!
//! Notes:
//!
//!     (0) Assumes ip register loaded with DMA base address.
//!
//! \return The status register of the DMA engine.

uint32_t dma_status (void) __attribute__ ((noinline));
uint32_t dma_status (void)
{
    uint32_t* base    = (uint32_t*)0x40000000;
    uint32_t  status;

    status = base [5];
    
    /*asm volatile ("mov %[status], #0x40000000\n\t"
		  "ldr %[status], [%[status], #20]\n\t"
		  : [status] "=r" (status) : : "memory");*/

    return (status);
}


void poll_dma_pre_loaded (void)
{
    register uint32_t status;

    status = dma_status () << 8;

    if (status == 0) // Masks out Processor Id bits.
        return;

    // ... other actions here. including stacking of registers.
}


void poll_dma (void)
{
    asm volatile ("push {ip}\n\t"
		  "mov ip, #0x40000000\n\t" : : : "memory");

    poll_dma_pre_loaded ();
    
    asm volatile ("pop {ip}\n\t"            : : : "memory");
}

//! \brief Initialises the DMA engine.
//!
//! Notes:
//!
//!     (0) Corrupts registers r0 and r1.
//!     (1) Resets the DMA engine CTRL word
//!     (2) GCTL set up
//!     (3) StatsCtl set up to record.

void dma_initialise (void) __attribute__ ((noinline));
void dma_initialise (void)
{
    asm volatile ("mov r1, #0x40000000\n\t"
		  "mov r0, #0x3f\n\t"
		  "str r0, [r1, #16]\n\t"
		  "mov r0, #0x0d\n\t"
		  "str r0, [r1, #16]\n\t"
		  "mov r0, #0\n\t"
		  "str r0, [r1, #24]\n\t"
		  "mov r0, #3\n\t"
		  "str r0, [r1, #40]\n\t"
		  "bx  lr\n\t"		    : : : "memory");
}

//! \brief Prints out the DMA Description Register
//!
//! \param[in] desc

void print_desc (uint32_t desc) __attribute__ ((noinline));
void print_desc (uint32_t desc)
{
    uint32_t length   = desc & 0x3ffff;
    uint32_t top_byte = desc >> 24;
    uint32_t control  = (desc >> 19) & 0x3f;
    uint32_t burst    = (control >> 2) & 0x7;

    io_printf (IO_BUF, "DMA DESC register: %08x\n    [ID = %u, ",
	       desc, top_byte >> 2);
    io_printf (IO_BUF, (top_byte & 0x2) == 0 ? "user,  ": "priviledged, ");
    io_printf (IO_BUF, (top_byte & 0x1) == 0 ? "words]; ": "dbl words]; ");
    io_printf (IO_BUF, "[Burst size = %u ", 1 << burst);
    io_printf (IO_BUF, (top_byte & 0x1) == 0 ? "words, ": "dbl words, ");
    io_printf (IO_BUF, (control & 0x2) ? "crc = on,  ": "crc = off, ");
    io_printf (IO_BUF, (control & 0x1) ? "Read];  ": "Write]; ");
    io_printf (IO_BUF, "length = %u bytes\n", length);
}
 


//! \brief Prints out lowest byte of DMA status register

void print_low_byte (void) __attribute__ ((noinline));
void print_low_byte (void)
{
    uint32_t* base = (uint32_t*)0x40000000;
    uint32_t  r    = base[5] & 0x1f;
    char      buffer[6];

    buffer [5] = '\0';
    buffer [4] = (r & 1) ? 'T': ' ';
    buffer [3] = (r & 2) ? 'P': ' ';
    buffer [2] = (r & 4) ? 'Q': ' ';
    buffer [1] = (r & 8) ? 'F': ' ';
    buffer [0] = (r & 16) ? 'A': ' ';

    io_printf (IO_BUF, buffer);
}
 

//! \brief Prints out the DMA statistics.

void print_and_reset_dma_statistics (void) __attribute__ ((noinline));
void print_and_reset_dma_statistics (void)
{
    uint32_t  i;
    uint32_t* base = (uint32_t*)0x40000000;
  
    io_printf (IO_BUF, "DMA statistics\n--------------\n");

    for (i = 0; i < 7; i++)
        io_printf (IO_BUF, "  %10u DMAs completed in %3u-%3u cycles\n",
		   base[i+16], i << 7, ((i+1) << 7) - 1);

    io_printf (IO_BUF, "  %10u DMAs completed in %3u+    cycles\n",
		   base[i+16], i << 7);

    base[10] = 3;
}

void c_main ()
{
    uint32_t  buffer0[256];
    uint32_t  buffer1[256];
    uint32_t  i;
    uint32_t* addr_s;
    uint32_t* addr_t;
    uint32_t  desc;
    uint32_t  status;

    initialise_timer ();

    for (i = 0; i < 256; i++) {
        buffer1 [i] = 0;
	buffer0 [i] = i;
    }

    dma_initialise ();

    
    addr_s = (uint32_t*)0x60000000;
    addr_t = buffer1;
    //    desc   = (1 << 24) | (0x88 << 16) | (0x100 << 2);
    desc   = (1 << 24) | (0x11 << 19) | (0x400 << 2);

    print_desc (desc);

    status = dma_status ();
    io_printf (IO_BUF, "DMA status: %08x [", status);
    print_low_byte ();
    io_printf (IO_BUF, "]\n");
    if (status != 0)
        dma_error_registers ();

    start_timer ();
    dma_request (addr_s, addr_t, desc);

    i = 0;
    do {
        i++;
	status = dma_status ();
	asm volatile ("" : : : "memory");
	//io_printf (IO_BUF, "Iteration %u, DMA status %08x\n", i++, status);
    } while (((status >> 10) & 0x3) == 0);

    stop_timer ();

    status = dma_status ();

    io_printf (IO_BUF, "DMA status %08x [", status);
    print_low_byte ();
    io_printf (IO_BUF, "], loops = %u\n", i);

    /*i = 0;
    do {
        dma_register_load ();
	status = dma_status ();
	io_printf (IO_BUF, "Iteration %u, DMA status %08x [", i++, status);
	print_low_byte ();
	io_printf (IO_BUF, "]\n");

    } while (i < 2);

    stop_timer ();
    */


    io_printf (IO_BUF, "DMA write took %u cycles to complete\n\n", time);

    print_and_reset_dma_statistics ();

}
