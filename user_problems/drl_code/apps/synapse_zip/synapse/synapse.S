
#define ctrl        r12
#define wp          r11
#define w           r10
#define n           r9
#define time_base   r8
#define jump        r7
#define mask        r6
#define mask_0x3c   r5


#define save_C_registers()\
push  {r4-r12,lr}  @ Save all 'C' registers

        .arch armv5te
        .fpu softvfp
        .eabi_attribute 23, 1
        .eabi_attribute 24, 1
        .eabi_attribute 25, 1
        .eabi_attribute 26, 1
        .eabi_attribute 30, 2
        .eabi_attribute 34, 0
        .eabi_attribute 18, 4
        .arm
        .syntax divided
        .file   "std_synapse.c"
        .text
.Ltext0:
        .cfi_sections   .debug_frame
        .align  2
        .global __synapse_loop
        .type   __synapse_loop, %function
__synapse_loop:
