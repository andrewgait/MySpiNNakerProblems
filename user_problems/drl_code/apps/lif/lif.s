       .text
       .global neuron_dynamics

@-------------------------------------------------------------------------------
@
@ neuron_dynamics (neuron_ptr* sp, uint32_t* ip, neuron_ptr  np, uint32_t* kp)
@
@ r0 holds sp: spike buffer
@ r1 holds ip: input pointer
@ r2 holds np: neuron pointer
@ r3 holds kp: constant/parameter pointer
@
@ Standard alternate names for r12-15: ip, sp, lr, pc
@-------------------------------------------------------------------------------
neuron_dynamics:

        push    {r7, r8, r9, r10, r11, lr}
		     	     	     	@ Save registers


	ldr     r9,  [r3]		@ Load constant parameters
	ldr	r10, [r3, #4]
	ldr	r11, [r3, #8]
		    	     		@       (frees up r3)

	ldr     r8, [r2]  		@ Load psp
        ldr     r3, [r1], #4		@ Load inputs
	ldr     r7, [r2, #4]    	@ Load v
        add     r8, r3, r8              @ add input to psp
	smlawb  r3, r7,  r9, r7		@ Decay voltage
	smlawb  r8, r8, r10, r8		@ Decay PSP+input (in tmp = ip)
        smlawt  r3, r8,  r9, r3		@ Add PSP+input effects to voltage

	cmp     r7, #0			@ if voltage >= 0
	sublts  r3, r3, #16777216	@ Subtract drift term and test voltage
        blge    neuron_nonstd		@    ... Branch on voltage >= 0

	str     r8, [r2], #4 		@ write-back psp value
	str     r3, [r2], #4 		@ write-back v value

	pop     {r7, r8, r9, r10, r11, pc}
		     	     	        @ Restore registers

neuron_nonstd:				@ In a non-standard state

	cmp     r7, #0			@ if original voltage >= 0: Refractory
        moveq   r3, r11			@ Reset voltage if previous test was 0
        subge   r3, r7, #1		@ Alternatively decrement refractory
	bxge	lr  			@ Return if r7 >= 0,
					@     ... otherwise dropthrough

	cmp	r3, #0			@ if modified voltage >= 0: A spike
	movge   r3, #20			@ Set refractory counter
        strge   r2, [r0], #4		@ Store neuron address in spike counter
        bx      lr  	  		@ return to main processing

	.end
