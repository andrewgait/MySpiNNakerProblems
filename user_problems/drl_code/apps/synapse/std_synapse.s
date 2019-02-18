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
	.file	"std_synapse.c"
	.text
.Ltext0:
	.cfi_sections	.debug_frame
	.align	2
	.global	__synapse_loop
	.type	__synapse_loop, %function
__synapse_loop:
.LFB236:
	.file 1 "std_synapse.c"
	.loc 1 3429 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3430 0
	.syntax divided
@ 3430 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3432 0
@ 3432 "std_synapse.c" 1
	                                       @ S0 word pre-loaded into w                           
	ldr    r1, [fp], #4                 @ S1 Pre-load next synaptic word for S1               
	ldrh   lr, [fp], #2                 @ S2 Pre-load synaptic half-word for S2 with 0x wwwd  
	and    r2, r6, r10, lsr #11      @ S2 mask out middle 8-bits from w into bits 8-1      
	add    r3, r8, r10, lsl #20 @ S0 add delay|index to timer_base                    
	add    r4, r8, lr, lsl #28   @ S2 add delay to timer_base (= 4 bits time + base)   
	orr    r4, r2, r4, ror #19             @ S2 rotate to position and 'or' in index bits        
	ldrh   r2, [r4]                        @ S2 load ring-element                                
	ror    r3, r3, #19                     @ S0 rotate to position                               
	ldrh   r0, [r3]                        @ S0 load ring-element                                
	subs   r2, r2, lr, lsr #4              @ S2 'add' weight                                     
	strplh r2, [r4]                        @ S2 conditionally store ring-element                 
	subpls r0, r0, r10, lsr #20           @ S0 conditionally 'add' weight, if OK so far         
	ldrh   lr, [fp], #2                 @ S3 Pre-load synaptic half-word for S3 with 0x wwwd  
	strplh r0, [r3]                        @ S0 conditionally store ring-element                 
	@============================================================================================
	@  At this point we have done synapses S0 and S2, and only r0, and r2 need to be preserved.  
	@  We have also pre-loaded the synapses S1 and S3.                                           
	@                                                                                            
	@ To process S1 and S3, whilst preserving r0 and r2 and using only the remaining registers:  
	@ r1, r3, r4, w, and lr; we have had to make some very peculiar register assignments for the 
	@ the next block of code.                                                                    
	@============================================================================================
	and    r3, r6, r1, lsr #11        @ S3 mask out middle 8-bits from w into bits 8-1      
	add    r10, r8, lr, lsl #28 @ S3 add delay to timer_base (= 4 bits time + base)   
	orr    r10, r3, r10, ror #19         @ S3 rotate to position and 'or' in index bits        
	ldrh   r3, [r10]                      @ S3 load ring-element                                
	add    r4, r8, r1, lsl #20   @ S1 add delay|index to timer_base                    
	ror    r4, r4, #19                     @ S1 rotate to position                               
	subpls r3, r3, lr, lsr #4              @ S3 conditionally 'add' weight, if OK so far         
	ldrh   lr, [r4]                        @ S1 load ring-element                                
	strplh r3, [r10]                      @ S3 conditionally store ring-element                 
	ldr    r10, [fp], #4               @ S4 Pre-load next synaptic word                      
	subpls r1, lr, r1, lsr #20             @ S1 conditionally 'add' weight, if OK so far         
	strplh r1, [r4]                        @ S1 conditionally store ring-element                 
	blmi   __packed_fix_up_4               @ Perform fix-up, if saturation occurred              
	
@ 0 "" 2
@ 3432 "std_synapse.c" 1
	                                       @ S0 word pre-loaded into w                           
	ldr    r1, [fp], #4                 @ S1 Pre-load next synaptic word for S1               
	ldrh   lr, [fp], #2                 @ S2 Pre-load synaptic half-word for S2 with 0x wwwd  
	and    r2, r6, r10, lsr #11      @ S2 mask out middle 8-bits from w into bits 8-1      
	add    r3, r8, r10, lsl #20 @ S0 add delay|index to timer_base                    
	add    r4, r8, lr, lsl #28   @ S2 add delay to timer_base (= 4 bits time + base)   
	orr    r4, r2, r4, ror #19             @ S2 rotate to position and 'or' in index bits        
	ldrh   r2, [r4]                        @ S2 load ring-element                                
	ror    r3, r3, #19                     @ S0 rotate to position                               
	ldrh   r0, [r3]                        @ S0 load ring-element                                
	subs   r2, r2, lr, lsr #4              @ S2 'add' weight                                     
	strplh r2, [r4]                        @ S2 conditionally store ring-element                 
	subpls r0, r0, r10, lsr #20           @ S0 conditionally 'add' weight, if OK so far         
	ldrh   lr, [fp], #2                 @ S3 Pre-load synaptic half-word for S3 with 0x wwwd  
	strplh r0, [r3]                        @ S0 conditionally store ring-element                 
	@============================================================================================
	@  At this point we have done synapses S0 and S2, and only r0, and r2 need to be preserved.  
	@  We have also pre-loaded the synapses S1 and S3.                                           
	@                                                                                            
	@ To process S1 and S3, whilst preserving r0 and r2 and using only the remaining registers:  
	@ r1, r3, r4, w, and lr; we have had to make some very peculiar register assignments for the 
	@ the next block of code.                                                                    
	@============================================================================================
	and    r3, r6, r1, lsr #11        @ S3 mask out middle 8-bits from w into bits 8-1      
	add    r10, r8, lr, lsl #28 @ S3 add delay to timer_base (= 4 bits time + base)   
	orr    r10, r3, r10, ror #19         @ S3 rotate to position and 'or' in index bits        
	ldrh   r3, [r10]                      @ S3 load ring-element                                
	add    r4, r8, r1, lsl #20   @ S1 add delay|index to timer_base                    
	ror    r4, r4, #19                     @ S1 rotate to position                               
	subpls r3, r3, lr, lsr #4              @ S3 conditionally 'add' weight, if OK so far         
	ldrh   lr, [r4]                        @ S1 load ring-element                                
	strplh r3, [r10]                      @ S3 conditionally store ring-element                 
	ldr    r10, [fp], #4               @ S4 Pre-load next synaptic word                      
	subpls r1, lr, r1, lsr #20             @ S1 conditionally 'add' weight, if OK so far         
	strplh r1, [r4]                        @ S1 conditionally store ring-element                 
	blmi   __packed_fix_up_4               @ Perform fix-up, if saturation occurred              
	
@ 0 "" 2
@ 3432 "std_synapse.c" 1
	                                       @ S0 word pre-loaded into w                           
	ldr    r1, [fp], #4                 @ S1 Pre-load next synaptic word for S1               
	ldrh   lr, [fp], #2                 @ S2 Pre-load synaptic half-word for S2 with 0x wwwd  
	and    r2, r6, r10, lsr #11      @ S2 mask out middle 8-bits from w into bits 8-1      
	add    r3, r8, r10, lsl #20 @ S0 add delay|index to timer_base                    
	add    r4, r8, lr, lsl #28   @ S2 add delay to timer_base (= 4 bits time + base)   
	orr    r4, r2, r4, ror #19             @ S2 rotate to position and 'or' in index bits        
	ldrh   r2, [r4]                        @ S2 load ring-element                                
	ror    r3, r3, #19                     @ S0 rotate to position                               
	ldrh   r0, [r3]                        @ S0 load ring-element                                
	subs   r2, r2, lr, lsr #4              @ S2 'add' weight                                     
	strplh r2, [r4]                        @ S2 conditionally store ring-element                 
	subpls r0, r0, r10, lsr #20           @ S0 conditionally 'add' weight, if OK so far         
	ldrh   lr, [fp], #2                 @ S3 Pre-load synaptic half-word for S3 with 0x wwwd  
	strplh r0, [r3]                        @ S0 conditionally store ring-element                 
	@============================================================================================
	@  At this point we have done synapses S0 and S2, and only r0, and r2 need to be preserved.  
	@  We have also pre-loaded the synapses S1 and S3.                                           
	@                                                                                            
	@ To process S1 and S3, whilst preserving r0 and r2 and using only the remaining registers:  
	@ r1, r3, r4, w, and lr; we have had to make some very peculiar register assignments for the 
	@ the next block of code.                                                                    
	@============================================================================================
	and    r3, r6, r1, lsr #11        @ S3 mask out middle 8-bits from w into bits 8-1      
	add    r10, r8, lr, lsl #28 @ S3 add delay to timer_base (= 4 bits time + base)   
	orr    r10, r3, r10, ror #19         @ S3 rotate to position and 'or' in index bits        
	ldrh   r3, [r10]                      @ S3 load ring-element                                
	add    r4, r8, r1, lsl #20   @ S1 add delay|index to timer_base                    
	ror    r4, r4, #19                     @ S1 rotate to position                               
	subpls r3, r3, lr, lsr #4              @ S3 conditionally 'add' weight, if OK so far         
	ldrh   lr, [r4]                        @ S1 load ring-element                                
	strplh r3, [r10]                      @ S3 conditionally store ring-element                 
	ldr    r10, [fp], #4               @ S4 Pre-load next synaptic word                      
	subpls r1, lr, r1, lsr #20             @ S1 conditionally 'add' weight, if OK so far         
	strplh r1, [r4]                        @ S1 conditionally store ring-element                 
	blmi   __packed_fix_up_4               @ Perform fix-up, if saturation occurred              
	
@ 0 "" 2
@ 3432 "std_synapse.c" 1
	                                       @ S0 word pre-loaded into w                           
	ldr    r1, [fp], #4                 @ S1 Pre-load next synaptic word for S1               
	ldrh   lr, [fp], #2                 @ S2 Pre-load synaptic half-word for S2 with 0x wwwd  
	and    r2, r6, r10, lsr #11      @ S2 mask out middle 8-bits from w into bits 8-1      
	add    r3, r8, r10, lsl #20 @ S0 add delay|index to timer_base                    
	add    r4, r8, lr, lsl #28   @ S2 add delay to timer_base (= 4 bits time + base)   
	orr    r4, r2, r4, ror #19             @ S2 rotate to position and 'or' in index bits        
	ldrh   r2, [r4]                        @ S2 load ring-element                                
	ror    r3, r3, #19                     @ S0 rotate to position                               
	ldrh   r0, [r3]                        @ S0 load ring-element                                
	subs   r2, r2, lr, lsr #4              @ S2 'add' weight                                     
	strplh r2, [r4]                        @ S2 conditionally store ring-element                 
	subpls r0, r0, r10, lsr #20           @ S0 conditionally 'add' weight, if OK so far         
	ldrh   lr, [fp], #2                 @ S3 Pre-load synaptic half-word for S3 with 0x wwwd  
	strplh r0, [r3]                        @ S0 conditionally store ring-element                 
	@============================================================================================
	@  At this point we have done synapses S0 and S2, and only r0, and r2 need to be preserved.  
	@  We have also pre-loaded the synapses S1 and S3.                                           
	@                                                                                            
	@ To process S1 and S3, whilst preserving r0 and r2 and using only the remaining registers:  
	@ r1, r3, r4, w, and lr; we have had to make some very peculiar register assignments for the 
	@ the next block of code.                                                                    
	@============================================================================================
	and    r3, r6, r1, lsr #11        @ S3 mask out middle 8-bits from w into bits 8-1      
	add    r10, r8, lr, lsl #28 @ S3 add delay to timer_base (= 4 bits time + base)   
	orr    r10, r3, r10, ror #19         @ S3 rotate to position and 'or' in index bits        
	ldrh   r3, [r10]                      @ S3 load ring-element                                
	add    r4, r8, r1, lsl #20   @ S1 add delay|index to timer_base                    
	ror    r4, r4, #19                     @ S1 rotate to position                               
	subpls r3, r3, lr, lsr #4              @ S3 conditionally 'add' weight, if OK so far         
	ldrh   lr, [r4]                        @ S1 load ring-element                                
	strplh r3, [r10]                      @ S3 conditionally store ring-element                 
	ldr    r10, [fp], #4               @ S4 Pre-load next synaptic word                      
	subpls r1, lr, r1, lsr #20             @ S1 conditionally 'add' weight, if OK so far         
	strplh r1, [r4]                        @ S1 conditionally store ring-element                 
	blmi   __packed_fix_up_4               @ Perform fix-up, if saturation occurred              
	
@ 0 "" 2
	.loc 1 3434 0
@ 3434 "std_synapse.c" 1
	mov  r1, #0x40000000        @ Load base address of DMA    
	ldr  r0, [r1, #20]          @ Check DMA status            
	ands r0, r0, #0xc00         @ Extract DMA completed flags 
	blne dma_scheduler          @ Set up new DMAs if needed   
	
@ 0 "" 2
	.loc 1 3436 0
@ 3436 "std_synapse.c" 1
	subs r9, r9, #16    @ decrement and test the 'loop counter'                     
	                        @   (actually the number of synapses to be processed -1)    
	bpl  __synapse_loop     @ If the number is still positive then loop again           
	
@ 0 "" 2
	.loc 1 3441 0
@ 3441 "std_synapse.c" 1
	and    r0, r5, r10, lsr #10   @ Set r0 = ..SS EX..                               
	@-------------------------------------------------------------------------------------------
	@ At this point r0 contains: .... .... .... .... .... .... ..SS EX..                        
	@-------------------------------------------------------------------------------------------
	ldr    r1, [r7, r0]                 @ Set up 16-way primary dispatch jump address      
	and    r9, r5, r10, lsr #14 @ Take opportunity to mask out n ..                
	bx     r1                                @ Take the primary jump unconditionally            
	@-------------------------------------------------------------------------------------------
	@ At this point   r0 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)         
	@                 n  contains: .... .... .... .... .... .... ..QQ QQ..     (. is 0)         
	@-------------------------------------------------------------------------------------------
	
@ 0 "" 2
	.loc 1 3442 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE236:
	.size	__synapse_loop, .-__synapse_loop
	.align	2
	.global	primary_dispatch_0I
	.type	primary_dispatch_0I, %function
primary_dispatch_0I:
.LFB237:
	.loc 1 3510 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3511 0
	.syntax divided
@ 3511 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3512 0
@ 3512 "std_synapse.c" 1
	ldr   r2, [fp], #4               @ Load the rowlet descriptor                              
	@ ----------------->                @ pipeline interlock here                                 
	add   r1, r8, r2, lsl #21 @ Add current time to rowlet descriptor word              
	lsr   r1, r1, #26                   @ Mask out all but bits 2-5                               
	and   r0, r1, #0x3c                 @ Mask out all but bits 2-5                               
	ldr   r1, [ip, r0]	           @ Load rowlet buffer pointer                              
	@ ----------------->                @ pipeline interlock here                                 
	str   r2, [r1], #4                  @ Store rowlet in buffer                                  
	str   r1, [ip, r0]	           @ Write-back the rowlet buffer pointer                    
	
@ 0 "" 2
	.loc 1 3513 0
@ 3513 "std_synapse.c" 1
	and r8, r8, #0xfffffffd    @ Clear bit 1 of time-base 
	
@ 0 "" 2
	.loc 1 3514 0
@ 3514 "std_synapse.c" 1
	                                       @ A synaptic word has already been pre-loaded into w, 
	                                       @   but it had no left-over synapses; so prepare to   
	                                       @   process quads. But quads must have 3 full words   
	ldr  r10, [fp], #4                 @ Get next word                                       
	
@ 0 "" 2
	.loc 1 3515 0
@ 3515 "std_synapse.c" 1
	ldr  r0, [ip, -r9]              @ Need to ensure a negative index never collides with  
	                                       @   a positive one. Calculate the jump address         
	subs r9, r9, #4                    @ subtract '1' from n for loop counter, and only       
	bxpl r0                                @   __branch__ to the looping process if Q>0           
	                                       @   or fall through, if there are no quads to process  
	
@ 0 "" 2
	.loc 1 3516 0
@ 3516 "std_synapse.c" 1
	@---------------------------------------------------------------------------------------------
	@ At this point w contains: .... .... 2222 0000 00EX .... .... ....         (. is don't care) 
	@ and r0 contains:          .... .... .... .... .... .... ..00 EX..         (. is 0)          
	@---------------------------------------------------------------------------------------------
	ands   r1, r5, r10, lsr #18 @ Shift the bits '2222' into position, and masks       
	ldr    r1, [r7, -r1]              @ Use the four bits to offset for secondary dispatch   
	popeq  {pc}                            @ Return: end of rowlet processing if '2222' = 0       
	                                       @ We need to ensure only one of +/- register occurs    
	bx     r1                              @ If  != 0, then jump                                  
	
@ 0 "" 2
	.loc 1 3517 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE237:
	.size	primary_dispatch_0I, .-primary_dispatch_0I
	.align	2
	.global	primary_dispatch_1I
	.type	primary_dispatch_1I, %function
primary_dispatch_1I:
.LFB238:
	.loc 1 3520 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3521 0
	.syntax divided
@ 3521 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3522 0
@ 3522 "std_synapse.c" 1
	ldr   r2, [fp], #4               @ Load the rowlet descriptor                              
	@ ----------------->                @ pipeline interlock here                                 
	add   r1, r8, r2, lsl #21 @ Add current time to rowlet descriptor word              
	lsr   r1, r1, #26                   @ Mask out all but bits 2-5                               
	and   r0, r1, #0x3c                 @ Mask out all but bits 2-5                               
	ldr   r1, [ip, r0]	           @ Load rowlet buffer pointer                              
	@ ----------------->                @ pipeline interlock here                                 
	str   r2, [r1], #4                  @ Store rowlet in buffer                                  
	str   r1, [ip, r0]	           @ Write-back the rowlet buffer pointer                    
	
@ 0 "" 2
	.loc 1 3523 0
@ 3523 "std_synapse.c" 1
	and r8, r8, #0xfffffffd    @ Clear bit 1 of time-base 
	
@ 0 "" 2
	.loc 1 3524 0
@ 3524 "std_synapse.c" 1
	                                       @ The synaptic word is already pre-loaded into w      
	add    r4, r8, r10, lsl #20 @ Add to rotated time_base                            
	ror    r4, r4, #19                     @ Rotate back again                                   
	ldrh   r0, [r4]                        @ Load the ring-buffer element                        
	subs   r0, r0, r10, lsr #20           @ 'add' weight to ring buffer, testing for saturation 
	strplh r0, [r4]                        @ write back ring buffer, if no saturation            
	ldr    r10, [fp], #4               @ Pre-load next synaptic word, incrementing wp        
	blmi   __saturation_detected_1         @ if saturated, repair                                
	
@ 0 "" 2
	.loc 1 3525 0
@ 3525 "std_synapse.c" 1
	ldr  r0, [ip, -r9]              @ Need to ensure a negative index never collides with  
	                                       @   a positive one. Calculate the jump address         
	subs r9, r9, #4                    @ subtract '1' from n for loop counter, and only       
	bxpl r0                                @   __branch__ to the looping process if Q>0           
	                                       @   or fall through, if there are no quads to process  
	
@ 0 "" 2
	.loc 1 3526 0
@ 3526 "std_synapse.c" 1
	and    r0, r5, r10, lsr #10   @ Set r0 = ..SS EX..                               
	@-------------------------------------------------------------------------------------------
	@ At this point r0 contains: .... .... .... .... .... .... ..SS EX..                        
	@-------------------------------------------------------------------------------------------
	ldr    r1, [r7, r0]                 @ Set up 16-way primary dispatch jump address      
	and    r9, r5, r10, lsr #14 @ Take opportunity to mask out n ..                
	bx     r1                                @ Take the primary jump unconditionally            
	@-------------------------------------------------------------------------------------------
	@ At this point   r0 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)         
	@                 n  contains: .... .... .... .... .... .... ..QQ QQ..     (. is 0)         
	@-------------------------------------------------------------------------------------------
	
@ 0 "" 2
	.loc 1 3527 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE238:
	.size	primary_dispatch_1I, .-primary_dispatch_1I
	.align	2
	.global	primary_dispatch_2I
	.type	primary_dispatch_2I, %function
primary_dispatch_2I:
.LFB239:
	.loc 1 3530 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3531 0
	.syntax divided
@ 3531 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3532 0
@ 3532 "std_synapse.c" 1
	ldr   r2, [fp], #4               @ Load the rowlet descriptor                              
	@ ----------------->                @ pipeline interlock here                                 
	add   r1, r8, r2, lsl #21 @ Add current time to rowlet descriptor word              
	lsr   r1, r1, #26                   @ Mask out all but bits 2-5                               
	and   r0, r1, #0x3c                 @ Mask out all but bits 2-5                               
	ldr   r1, [ip, r0]	           @ Load rowlet buffer pointer                              
	@ ----------------->                @ pipeline interlock here                                 
	str   r2, [r1], #4                  @ Store rowlet in buffer                                  
	str   r1, [ip, r0]	           @ Write-back the rowlet buffer pointer                    
	
@ 0 "" 2
	.loc 1 3533 0
@ 3533 "std_synapse.c" 1
	and r8, r8, #0xfffffffd    @ Clear bit 1 of time-base 
	
@ 0 "" 2
	.loc 1 3534 0
@ 3534 "std_synapse.c" 1
	                                       @ S0 word pre-loaded into w            
	ldr    r2, [fp], #4                 @ S1 Load the synaptic word            
	add    r3, r8, r10, lsl #20 @ S0 Add to rotated time_base          
	ror    r3, r3, #19                     @ S0 Rotate back again                 
	ldrh   r0, [r3]                        @ S0 Load the ring-buffer element      
	add    r4, r8, r2, lsl #20   @ S1 Add to rotated time_base          
	ror    r4, r4, #19                     @ S1 Rotate back again                 
	ldrh   r1, [r4]                        @ S1 Load the ring-buffer element      
	subs   r0, r0, r10, lsr #20           @ S0 'add' weight to ring buffer       
	strplh r0, [r3]                        @ S0 write back ring buffer, if OK     
	subpls r1, r1, r2, lsr #20             @ S1 'add' weight to ring buffer       
	strplh r1, [r4]                        @ S1 write back ring buffer, if OK     
	ldr    r10, [fp], #4               @ Pre-load next synaptic word          
	blmi   __saturation_detected_2         @ if saturated, repair                 
	
@ 0 "" 2
	.loc 1 3535 0
@ 3535 "std_synapse.c" 1
	ldr  r0, [ip, -r9]              @ Need to ensure a negative index never collides with  
	                                       @   a positive one. Calculate the jump address         
	subs r9, r9, #4                    @ subtract '1' from n for loop counter, and only       
	bxpl r0                                @   __branch__ to the looping process if Q>0           
	                                       @   or fall through, if there are no quads to process  
	
@ 0 "" 2
	.loc 1 3536 0
@ 3536 "std_synapse.c" 1
	and    r0, r5, r10, lsr #10   @ Set r0 = ..SS EX..                               
	@-------------------------------------------------------------------------------------------
	@ At this point r0 contains: .... .... .... .... .... .... ..SS EX..                        
	@-------------------------------------------------------------------------------------------
	ldr    r1, [r7, r0]                 @ Set up 16-way primary dispatch jump address      
	and    r9, r5, r10, lsr #14 @ Take opportunity to mask out n ..                
	bx     r1                                @ Take the primary jump unconditionally            
	@-------------------------------------------------------------------------------------------
	@ At this point   r0 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)         
	@                 n  contains: .... .... .... .... .... .... ..QQ QQ..     (. is 0)         
	@-------------------------------------------------------------------------------------------
	
@ 0 "" 2
	.loc 1 3537 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE239:
	.size	primary_dispatch_2I, .-primary_dispatch_2I
	.align	2
	.global	primary_dispatch_3I
	.type	primary_dispatch_3I, %function
primary_dispatch_3I:
.LFB240:
	.loc 1 3540 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3541 0
	.syntax divided
@ 3541 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3542 0
@ 3542 "std_synapse.c" 1
	ldr   r2, [fp], #4               @ Load the rowlet descriptor                              
	@ ----------------->                @ pipeline interlock here                                 
	add   r1, r8, r2, lsl #21 @ Add current time to rowlet descriptor word              
	lsr   r1, r1, #26                   @ Mask out all but bits 2-5                               
	and   r0, r1, #0x3c                 @ Mask out all but bits 2-5                               
	ldr   r1, [ip, r0]	           @ Load rowlet buffer pointer                              
	@ ----------------->                @ pipeline interlock here                                 
	str   r2, [r1], #4                  @ Store rowlet in buffer                                  
	str   r1, [ip, r0]	           @ Write-back the rowlet buffer pointer                    
	
@ 0 "" 2
	.loc 1 3543 0
@ 3543 "std_synapse.c" 1
	and r8, r8, #0xfffffffd    @ Clear bit 1 of time-base 
	
@ 0 "" 2
	.loc 1 3544 0
@ 3544 "std_synapse.c" 1
	                                        @ S0 word pre-loaded into w                 
	ldr    r0, [fp], #4                  @ S1 Load the synaptic word                 
	ldr    lr, [fp], #4                  @ S2 Load the synaptic word                 
	add    r3, r8, r0, lsl #20    @ S1 Add to rotated time_base               
	ror    r3, r3, #19                      @ S1 Rotate back again                      
	ldrh   r1, [r3]                         @ S1 Load the ring-buffer element           
	add    r4, r8, lr, lsl #20    @ S2 Add to rotated time_base               
	add    r2, r8, r10, lsl #20  @ S0 Add to rotated time_base               
	subs   r1, r1, r0, lsr #20              @ S1 'add' weight to ring buffer            
	strplh r1, [r3]                         @ S1 write back ring buffer, if OK          
	ror    r3, r2, #19                      @ S0 Rotate back again                      
	ldrh   r0, [r3]                         @ S0 Load the ring-buffer element           
	ror    r4, r4, #19                      @ S2 Rotate back again                      
	ldrh   r2, [r4]                         @ S2 Load the ring-buffer element           
	subpls r0, r0, r10, lsr #20            @ S0 'add' weight to ring buffer            
	strplh r0, [r3]                         @ S0 write back ring buffer, if OK          
	subpls r2, r2, lr, lsr #20              @ S2 'add' weight to ring buffer            
	strplh r2, [r4]                         @ S2 write back ring buffer, if OK          
	ldr    r10, [fp], #4                @ Pre-load next synaptic word, increment wp 
	blmi   __saturation_detected_3          @ if saturated, repair                      
	
@ 0 "" 2
	.loc 1 3545 0
@ 3545 "std_synapse.c" 1
	ldr  r0, [ip, -r9]              @ Need to ensure a negative index never collides with  
	                                       @   a positive one. Calculate the jump address         
	subs r9, r9, #4                    @ subtract '1' from n for loop counter, and only       
	bxpl r0                                @   __branch__ to the looping process if Q>0           
	                                       @   or fall through, if there are no quads to process  
	
@ 0 "" 2
	.loc 1 3546 0
@ 3546 "std_synapse.c" 1
	and    r0, r5, r10, lsr #10   @ Set r0 = ..SS EX..                               
	@-------------------------------------------------------------------------------------------
	@ At this point r0 contains: .... .... .... .... .... .... ..SS EX..                        
	@-------------------------------------------------------------------------------------------
	ldr    r1, [r7, r0]                 @ Set up 16-way primary dispatch jump address      
	and    r9, r5, r10, lsr #14 @ Take opportunity to mask out n ..                
	bx     r1                                @ Take the primary jump unconditionally            
	@-------------------------------------------------------------------------------------------
	@ At this point   r0 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)         
	@                 n  contains: .... .... .... .... .... .... ..QQ QQ..     (. is 0)         
	@-------------------------------------------------------------------------------------------
	
@ 0 "" 2
	.loc 1 3547 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE240:
	.size	primary_dispatch_3I, .-primary_dispatch_3I
	.align	2
	.global	primary_dispatch_0E
	.type	primary_dispatch_0E, %function
primary_dispatch_0E:
.LFB241:
	.loc 1 3549 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3550 0
	.syntax divided
@ 3550 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3551 0
@ 3551 "std_synapse.c" 1
	ldr   r2, [fp], #4               @ Load the rowlet descriptor                              
	@ ----------------->                @ pipeline interlock here                                 
	add   r1, r8, r2, lsl #21 @ Add current time to rowlet descriptor word              
	lsr   r1, r1, #26                   @ Mask out all but bits 2-5                               
	and   r0, r1, #0x3c                 @ Mask out all but bits 2-5                               
	ldr   r1, [ip, r0]	           @ Load rowlet buffer pointer                              
	@ ----------------->                @ pipeline interlock here                                 
	str   r2, [r1], #4                  @ Store rowlet in buffer                                  
	str   r1, [ip, r0]	           @ Write-back the rowlet buffer pointer                    
	
@ 0 "" 2
	.loc 1 3552 0
@ 3552 "std_synapse.c" 1
	orr r8, r8, #0x2           @ Set bit 1 of time-base   
	
@ 0 "" 2
	.loc 1 3553 0
@ 3553 "std_synapse.c" 1
	                                       @ A synaptic word has already been pre-loaded into w, 
	                                       @   but it had no left-over synapses; so prepare to   
	                                       @   process quads. But quads must have 3 full words   
	ldr  r10, [fp], #4                 @ Get next word                                       
	
@ 0 "" 2
	.loc 1 3554 0
@ 3554 "std_synapse.c" 1
	ldr  r0, [ip, -r9]              @ Need to ensure a negative index never collides with  
	                                       @   a positive one. Calculate the jump address         
	subs r9, r9, #4                    @ subtract '1' from n for loop counter, and only       
	bxpl r0                                @   __branch__ to the looping process if Q>0           
	                                       @   or fall through, if there are no quads to process  
	
@ 0 "" 2
	.loc 1 3555 0
@ 3555 "std_synapse.c" 1
	@---------------------------------------------------------------------------------------------
	@ At this point w contains: .... .... 2222 0000 00EX .... .... ....         (. is don't care) 
	@ and r0 contains:          .... .... .... .... .... .... ..00 EX..         (. is 0)          
	@---------------------------------------------------------------------------------------------
	ands   r1, r5, r10, lsr #18 @ Shift the bits '2222' into position, and masks       
	ldr    r1, [r7, -r1]              @ Use the four bits to offset for secondary dispatch   
	popeq  {pc}                            @ Return: end of rowlet processing if '2222' = 0       
	                                       @ We need to ensure only one of +/- register occurs    
	bx     r1                              @ If  != 0, then jump                                  
	
@ 0 "" 2
	.loc 1 3556 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE241:
	.size	primary_dispatch_0E, .-primary_dispatch_0E
	.align	2
	.global	primary_dispatch_1E
	.type	primary_dispatch_1E, %function
primary_dispatch_1E:
.LFB242:
	.loc 1 3559 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3560 0
	.syntax divided
@ 3560 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3561 0
@ 3561 "std_synapse.c" 1
	ldr   r2, [fp], #4               @ Load the rowlet descriptor                              
	@ ----------------->                @ pipeline interlock here                                 
	add   r1, r8, r2, lsl #21 @ Add current time to rowlet descriptor word              
	lsr   r1, r1, #26                   @ Mask out all but bits 2-5                               
	and   r0, r1, #0x3c                 @ Mask out all but bits 2-5                               
	ldr   r1, [ip, r0]	           @ Load rowlet buffer pointer                              
	@ ----------------->                @ pipeline interlock here                                 
	str   r2, [r1], #4                  @ Store rowlet in buffer                                  
	str   r1, [ip, r0]	           @ Write-back the rowlet buffer pointer                    
	
@ 0 "" 2
	.loc 1 3562 0
@ 3562 "std_synapse.c" 1
	orr r8, r8, #0x2           @ Set bit 1 of time-base   
	
@ 0 "" 2
	.loc 1 3563 0
@ 3563 "std_synapse.c" 1
	                                       @ The synaptic word is already pre-loaded into w      
	add    r4, r8, r10, lsl #20 @ Add to rotated time_base                            
	ror    r4, r4, #19                     @ Rotate back again                                   
	ldrh   r0, [r4]                        @ Load the ring-buffer element                        
	subs   r0, r0, r10, lsr #20           @ 'add' weight to ring buffer, testing for saturation 
	strplh r0, [r4]                        @ write back ring buffer, if no saturation            
	ldr    r10, [fp], #4               @ Pre-load next synaptic word, incrementing wp        
	blmi   __saturation_detected_1         @ if saturated, repair                                
	
@ 0 "" 2
	.loc 1 3564 0
@ 3564 "std_synapse.c" 1
	ldr  r0, [ip, -r9]              @ Need to ensure a negative index never collides with  
	                                       @   a positive one. Calculate the jump address         
	subs r9, r9, #4                    @ subtract '1' from n for loop counter, and only       
	bxpl r0                                @   __branch__ to the looping process if Q>0           
	                                       @   or fall through, if there are no quads to process  
	
@ 0 "" 2
	.loc 1 3565 0
@ 3565 "std_synapse.c" 1
	and    r0, r5, r10, lsr #10   @ Set r0 = ..SS EX..                               
	@-------------------------------------------------------------------------------------------
	@ At this point r0 contains: .... .... .... .... .... .... ..SS EX..                        
	@-------------------------------------------------------------------------------------------
	ldr    r1, [r7, r0]                 @ Set up 16-way primary dispatch jump address      
	and    r9, r5, r10, lsr #14 @ Take opportunity to mask out n ..                
	bx     r1                                @ Take the primary jump unconditionally            
	@-------------------------------------------------------------------------------------------
	@ At this point   r0 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)         
	@                 n  contains: .... .... .... .... .... .... ..QQ QQ..     (. is 0)         
	@-------------------------------------------------------------------------------------------
	
@ 0 "" 2
	.loc 1 3566 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE242:
	.size	primary_dispatch_1E, .-primary_dispatch_1E
	.align	2
	.global	primary_dispatch_2E
	.type	primary_dispatch_2E, %function
primary_dispatch_2E:
.LFB243:
	.loc 1 3569 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3570 0
	.syntax divided
@ 3570 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3571 0
@ 3571 "std_synapse.c" 1
	ldr   r2, [fp], #4               @ Load the rowlet descriptor                              
	@ ----------------->                @ pipeline interlock here                                 
	add   r1, r8, r2, lsl #21 @ Add current time to rowlet descriptor word              
	lsr   r1, r1, #26                   @ Mask out all but bits 2-5                               
	and   r0, r1, #0x3c                 @ Mask out all but bits 2-5                               
	ldr   r1, [ip, r0]	           @ Load rowlet buffer pointer                              
	@ ----------------->                @ pipeline interlock here                                 
	str   r2, [r1], #4                  @ Store rowlet in buffer                                  
	str   r1, [ip, r0]	           @ Write-back the rowlet buffer pointer                    
	
@ 0 "" 2
	.loc 1 3572 0
@ 3572 "std_synapse.c" 1
	orr r8, r8, #0x2           @ Set bit 1 of time-base   
	
@ 0 "" 2
	.loc 1 3573 0
@ 3573 "std_synapse.c" 1
	                                       @ S0 word pre-loaded into w            
	ldr    r2, [fp], #4                 @ S1 Load the synaptic word            
	add    r3, r8, r10, lsl #20 @ S0 Add to rotated time_base          
	ror    r3, r3, #19                     @ S0 Rotate back again                 
	ldrh   r0, [r3]                        @ S0 Load the ring-buffer element      
	add    r4, r8, r2, lsl #20   @ S1 Add to rotated time_base          
	ror    r4, r4, #19                     @ S1 Rotate back again                 
	ldrh   r1, [r4]                        @ S1 Load the ring-buffer element      
	subs   r0, r0, r10, lsr #20           @ S0 'add' weight to ring buffer       
	strplh r0, [r3]                        @ S0 write back ring buffer, if OK     
	subpls r1, r1, r2, lsr #20             @ S1 'add' weight to ring buffer       
	strplh r1, [r4]                        @ S1 write back ring buffer, if OK     
	ldr    r10, [fp], #4               @ Pre-load next synaptic word          
	blmi   __saturation_detected_2         @ if saturated, repair                 
	
@ 0 "" 2
	.loc 1 3574 0
@ 3574 "std_synapse.c" 1
	ldr  r0, [ip, -r9]              @ Need to ensure a negative index never collides with  
	                                       @   a positive one. Calculate the jump address         
	subs r9, r9, #4                    @ subtract '1' from n for loop counter, and only       
	bxpl r0                                @   __branch__ to the looping process if Q>0           
	                                       @   or fall through, if there are no quads to process  
	
@ 0 "" 2
	.loc 1 3575 0
@ 3575 "std_synapse.c" 1
	and    r0, r5, r10, lsr #10   @ Set r0 = ..SS EX..                               
	@-------------------------------------------------------------------------------------------
	@ At this point r0 contains: .... .... .... .... .... .... ..SS EX..                        
	@-------------------------------------------------------------------------------------------
	ldr    r1, [r7, r0]                 @ Set up 16-way primary dispatch jump address      
	and    r9, r5, r10, lsr #14 @ Take opportunity to mask out n ..                
	bx     r1                                @ Take the primary jump unconditionally            
	@-------------------------------------------------------------------------------------------
	@ At this point   r0 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)         
	@                 n  contains: .... .... .... .... .... .... ..QQ QQ..     (. is 0)         
	@-------------------------------------------------------------------------------------------
	
@ 0 "" 2
	.loc 1 3576 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE243:
	.size	primary_dispatch_2E, .-primary_dispatch_2E
	.align	2
	.global	primary_dispatch_3E
	.type	primary_dispatch_3E, %function
primary_dispatch_3E:
.LFB244:
	.loc 1 3579 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3580 0
	.syntax divided
@ 3580 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3581 0
@ 3581 "std_synapse.c" 1
	ldr   r2, [fp], #4               @ Load the rowlet descriptor                              
	@ ----------------->                @ pipeline interlock here                                 
	add   r1, r8, r2, lsl #21 @ Add current time to rowlet descriptor word              
	lsr   r1, r1, #26                   @ Mask out all but bits 2-5                               
	and   r0, r1, #0x3c                 @ Mask out all but bits 2-5                               
	ldr   r1, [ip, r0]	           @ Load rowlet buffer pointer                              
	@ ----------------->                @ pipeline interlock here                                 
	str   r2, [r1], #4                  @ Store rowlet in buffer                                  
	str   r1, [ip, r0]	           @ Write-back the rowlet buffer pointer                    
	
@ 0 "" 2
	.loc 1 3582 0
@ 3582 "std_synapse.c" 1
	orr r8, r8, #0x2           @ Set bit 1 of time-base   
	
@ 0 "" 2
	.loc 1 3583 0
@ 3583 "std_synapse.c" 1
	                                        @ S0 word pre-loaded into w                 
	ldr    r0, [fp], #4                  @ S1 Load the synaptic word                 
	ldr    lr, [fp], #4                  @ S2 Load the synaptic word                 
	add    r3, r8, r0, lsl #20    @ S1 Add to rotated time_base               
	ror    r3, r3, #19                      @ S1 Rotate back again                      
	ldrh   r1, [r3]                         @ S1 Load the ring-buffer element           
	add    r4, r8, lr, lsl #20    @ S2 Add to rotated time_base               
	add    r2, r8, r10, lsl #20  @ S0 Add to rotated time_base               
	subs   r1, r1, r0, lsr #20              @ S1 'add' weight to ring buffer            
	strplh r1, [r3]                         @ S1 write back ring buffer, if OK          
	ror    r3, r2, #19                      @ S0 Rotate back again                      
	ldrh   r0, [r3]                         @ S0 Load the ring-buffer element           
	ror    r4, r4, #19                      @ S2 Rotate back again                      
	ldrh   r2, [r4]                         @ S2 Load the ring-buffer element           
	subpls r0, r0, r10, lsr #20            @ S0 'add' weight to ring buffer            
	strplh r0, [r3]                         @ S0 write back ring buffer, if OK          
	subpls r2, r2, lr, lsr #20              @ S2 'add' weight to ring buffer            
	strplh r2, [r4]                         @ S2 write back ring buffer, if OK          
	ldr    r10, [fp], #4                @ Pre-load next synaptic word, increment wp 
	blmi   __saturation_detected_3          @ if saturated, repair                      
	
@ 0 "" 2
	.loc 1 3584 0
@ 3584 "std_synapse.c" 1
	ldr  r0, [ip, -r9]              @ Need to ensure a negative index never collides with  
	                                       @   a positive one. Calculate the jump address         
	subs r9, r9, #4                    @ subtract '1' from n for loop counter, and only       
	bxpl r0                                @   __branch__ to the looping process if Q>0           
	                                       @   or fall through, if there are no quads to process  
	
@ 0 "" 2
	.loc 1 3585 0
@ 3585 "std_synapse.c" 1
	and    r0, r5, r10, lsr #10   @ Set r0 = ..SS EX..                               
	@-------------------------------------------------------------------------------------------
	@ At this point r0 contains: .... .... .... .... .... .... ..SS EX..                        
	@-------------------------------------------------------------------------------------------
	ldr    r1, [r7, r0]                 @ Set up 16-way primary dispatch jump address      
	and    r9, r5, r10, lsr #14 @ Take opportunity to mask out n ..                
	bx     r1                                @ Take the primary jump unconditionally            
	@-------------------------------------------------------------------------------------------
	@ At this point   r0 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)         
	@                 n  contains: .... .... .... .... .... .... ..QQ QQ..     (. is 0)         
	@-------------------------------------------------------------------------------------------
	
@ 0 "" 2
	.loc 1 3586 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE244:
	.size	primary_dispatch_3E, .-primary_dispatch_3E
	.align	2
	.global	printx
	.type	printx, %function
printx:
.LFB193:
	.loc 1 202 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
.LVL0:
	.loc 1 205 0
	.syntax divided
@ 205 "std_synapse.c" 1
	push {r0-r3,ip,lr}
	mrs  r3, cpsr
	push {r3}
	mov  r2, r0
	
@ 0 "" 2
	.loc 1 211 0
	.arm
	.syntax divided
	ldr	r1, .L11
	mov	r0, #2
.LVL1:
	bl	io_printf
.LVL2:
	.loc 1 213 0
	.syntax divided
@ 213 "std_synapse.c" 1
	pop {r3}
	msr cpsr_fs, r3
	pop {r0-r3,ip,pc}
	
@ 0 "" 2
	.loc 1 217 0
	.arm
	.syntax divided
.L12:
	.align	2
.L11:
	.word	.LC0
	.cfi_endproc
.LFE193:
	.size	printx, .-printx
	.align	2
	.global	__reserved_dispatch
	.type	__reserved_dispatch, %function
__reserved_dispatch:
.LFB215:
	.loc 1 1358 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 1359 0
	ldr	r0, .L14
	bl	printx
.LVL3:
	.loc 1 1361 0
	.syntax divided
@ 1361 "std_synapse.c" 1
	bx lr
	
@ 0 "" 2
	.loc 1 1362 0
	.arm
	.syntax divided
.L15:
	.align	2
.L14:
	.word	-1160729136
	.cfi_endproc
.LFE215:
	.size	__reserved_dispatch, .-__reserved_dispatch
	.align	2
	.global	initialise_timer
	.type	initialise_timer, %function
initialise_timer:
.LFB194:
	.loc 1 230 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL4:
	.loc 1 233 0
	mov	r3, #553648128
	mvn	r1, #0
	.loc 1 234 0
	mov	r2, #194
	.loc 1 233 0
	str	r1, [r3]
	.loc 1 234 0
	str	r2, [r3, #8]
	bx	lr
	.cfi_endproc
.LFE194:
	.size	initialise_timer, .-initialise_timer
	.align	2
	.global	start_timer
	.type	start_timer, %function
start_timer:
.LFB195:
	.loc 1 238 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL5:
	.loc 1 242 0
	mov	r3, #553648128
	.syntax divided
@ 242 "std_synapse.c" 1
	push {r2, r3}
	ldr r3, [r3, #4]
	
@ 0 "" 2
.LVL6:
	.loc 1 246 0
	.arm
	.syntax divided
	ldr	r2, .L18
	str	r3, [r2]
	.loc 1 248 0
	.syntax divided
@ 248 "std_synapse.c" 1
	pop {r2, r3}
	
@ 0 "" 2
	.arm
	.syntax divided
	bx	lr
.L19:
	.align	2
.L18:
	.word	.LANCHOR0
	.cfi_endproc
.LFE195:
	.size	start_timer, .-start_timer
	.align	2
	.global	stop_timer
	.type	stop_timer, %function
stop_timer:
.LFB196:
	.loc 1 252 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL7:
	.loc 1 256 0
	mov	r3, #553648128
	.syntax divided
@ 256 "std_synapse.c" 1
	push {r1, r2, r3}
	ldr r2, [r3, #4]
	
@ 0 "" 2
.LVL8:
	.loc 1 260 0
	.arm
	.syntax divided
	ldr	r1, .L21
	ldr	r3, [r1]
	sub	r3, r3, #20
	rsb	r3, r2, r3
	str	r3, [r1]
	.loc 1 262 0
	.syntax divided
@ 262 "std_synapse.c" 1
	pop {r1, r2, r3}
	
@ 0 "" 2
	.arm
	.syntax divided
	bx	lr
.L22:
	.align	2
.L21:
	.word	.LANCHOR0
	.cfi_endproc
.LFE196:
	.size	stop_timer, .-stop_timer
	.align	2
	.global	reset_ring_buffer_row
	.type	reset_ring_buffer_row, %function
reset_ring_buffer_row:
.LFB197:
	.loc 1 287 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
.LVL9:
	.loc 1 293 0
	.syntax divided
@ 293 "std_synapse.c" 1
	mov  r1, #0x00400000           @ Load base address of DTCM           
	add  r2, r1, #0x6000           @ Base address of ring_buffer1        
	add  r1, r1, #0x4000           @ Base address of ring_buffer1        
	add  r1, r1, r0, lsl #9  @ Offset for specific delay           
	add  r2, r2, r0, lsl #9  @ Offset for specific delay           
	mvn  r3, #0             @ Value to be stored in ring buffers  
	mov  r0, #15             @ Recycle r0 (=delay) as counter      
	
@ 0 "" 2
.LVL10:
	.arm
	.syntax divided
.L24:
	.loc 1 304 0 discriminator 1
	.syntax divided
@ 304 "std_synapse.c" 1
	str r3, [r1], #4                                             
	str r3, [r1], #4                                             
	str r3, [r1], #4                                             
	str r3, [r1], #4                                             
	str r3, [r1], #4                                             
	str r3, [r1], #4                                             
	str r3, [r1], #4                                             
	str r3, [r1], #4                                             
	str r3, [r2], #4                                             
	str r3, [r2], #4                                             
	str r3, [r2], #4                                             
	str r3, [r2], #4                                             
	str r3, [r2], #4                                             
	str r3, [r2], #4                                             
	str r3, [r2], #4                                             
	str r3, [r2], #4                                             
	subs r0, r0, #1                @ Decrement loop counter, and ... 
	
@ 0 "" 2
	.loc 1 323 0 discriminator 1
@ 323 "std_synapse.c" 1
	bpl .L24                   @   ... loop back if needed       
	mov pc, lr                     @ Return                          
	
@ 0 "" 2
	.loc 1 326 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE197:
	.size	reset_ring_buffer_row, .-reset_ring_buffer_row
	.align	2
	.global	initialise_ring_buffers
	.type	initialise_ring_buffers, %function
initialise_ring_buffers:
.LFB198:
	.loc 1 417 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
.LVL11:
	stmfd	sp!, {r4, lr}
	.cfi_def_cfa_offset 8
	.cfi_offset 4, -8
	.cfi_offset 14, -4
	.loc 1 420 0
	mov	r4, #15
.LVL12:
.L28:
	.loc 1 421 0 discriminator 3
	mov	r0, r4
	.loc 1 420 0 discriminator 3
	sub	r4, r4, #1
.LVL13:
	.loc 1 421 0 discriminator 3
	bl	reset_ring_buffer_row
.LVL14:
	.loc 1 420 0 discriminator 3
	cmn	r4, #1
	bne	.L28
	.loc 1 422 0
	ldmfd	sp!, {r4, pc}
	.cfi_endproc
.LFE198:
	.size	initialise_ring_buffers, .-initialise_ring_buffers
	.align	2
	.global	print_ring_buffer
	.type	print_ring_buffer, %function
print_ring_buffer:
.LFB199:
	.loc 1 430 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
.LVL15:
	.loc 1 434 0
	ldr	r3, .L40
	.loc 1 430 0
	stmfd	sp!, {r4, r5, r6, r7, r8, lr}
	.cfi_def_cfa_offset 24
	.cfi_offset 4, -24
	.cfi_offset 5, -20
	.cfi_offset 6, -16
	.cfi_offset 7, -12
	.cfi_offset 8, -8
	.cfi_offset 14, -4
	.loc 1 434 0
	subs	r6, r0, #0
	.loc 1 438 0
	ldr	r7, .L40+4
	.loc 1 434 0
	ldr	r5, .L40+8
	.loc 1 430 0
	sub	sp, sp, #8
	.cfi_def_cfa_offset 32
	.loc 1 434 0
	movne	r5, r3
.LVL16:
	.loc 1 436 0
	mov	r8, #0
.LVL17:
.L33:
	.loc 1 434 0
	mov	r4, #0
.LVL18:
.L35:
	.loc 1 438 0
	mov	ip, r4, asl #9
	ldrh	lr, [r5, ip]
	.loc 1 439 0
	mov	r3, r4
	rsb	ip, lr, #65280
	.loc 1 438 0
	cmp	lr, r7
	.loc 1 439 0
	mov	r2, r6
	ldr	r1, .L40+12
	mov	r0, #2
	.loc 1 437 0
	add	r4, r4, #1
.LVL19:
	.loc 1 439 0
	add	ip, ip, #255
	.loc 1 438 0
	beq	.L34
.LVL20:
	.loc 1 439 0
	stmia	sp, {r8, ip}
	bl	io_printf
.LVL21:
.L34:
	.loc 1 437 0 discriminator 2
	cmp	r4, #16
	bne	.L35
	.loc 1 436 0 discriminator 2
	add	r8, r8, #1
.LVL22:
	cmp	r8, #256
	add	r5, r5, #2
	bne	.L33
	.loc 1 441 0
	add	sp, sp, #8
	.cfi_def_cfa_offset 24
	@ sp needed
	ldmfd	sp!, {r4, r5, r6, r7, r8, pc}
.LVL23:
.L41:
	.align	2
.L40:
	.word	4218880
	.word	65535
	.word	4210688
	.word	.LC1
	.cfi_endproc
.LFE199:
	.size	print_ring_buffer, .-print_ring_buffer
	.align	2
	.global	print_ring_buffers
	.type	print_ring_buffers, %function
print_ring_buffers:
.LFB200:
	.loc 1 449 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	stmfd	sp!, {r4, lr}
	.cfi_def_cfa_offset 8
	.cfi_offset 4, -8
	.cfi_offset 14, -4
	.loc 1 450 0
	mov	r0, #0
	bl	print_ring_buffer
.LVL24:
	.loc 1 451 0
	mov	r0, #1
	.loc 1 452 0
	ldmfd	sp!, {r4, lr}
	.cfi_restore 14
	.cfi_restore 4
	.cfi_def_cfa_offset 0
	.loc 1 451 0
	b	print_ring_buffer
.LVL25:
	.cfi_endproc
.LFE200:
	.size	print_ring_buffers, .-print_ring_buffers
	.align	2
	.global	get_index
	.type	get_index, %function
get_index:
.LFB201:
	.loc 1 457 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL26:
	.loc 1 457 0
	and	r0, r0, #255
.LVL27:
	bx	lr
	.cfi_endproc
.LFE201:
	.size	get_index, .-get_index
	.align	2
	.global	get_delay
	.type	get_delay, %function
get_delay:
.LFB202:
	.loc 1 460 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL28:
	.loc 1 460 0
	mov	r0, r0, lsr #8
.LVL29:
	and	r0, r0, #15
	bx	lr
	.cfi_endproc
.LFE202:
	.size	get_delay, .-get_delay
	.align	2
	.global	get_index_delay
	.type	get_index_delay, %function
get_index_delay:
.LFB203:
	.loc 1 463 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL30:
	.loc 1 463 0
	mov	r0, r0, asl #20
.LVL31:
	mov	r0, r0, lsr #20
	bx	lr
	.cfi_endproc
.LFE203:
	.size	get_index_delay, .-get_index_delay
	.align	2
	.global	get_weight
	.type	get_weight, %function
get_weight:
.LFB204:
	.loc 1 466 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL32:
	.loc 1 466 0
	mov	r0, r0, asl #8
.LVL33:
	mov	r0, r0, lsr #20
	bx	lr
	.cfi_endproc
.LFE204:
	.size	get_weight, .-get_weight
	.align	2
	.global	odd_word
	.type	odd_word, %function
odd_word:
.LFB205:
	.loc 1 469 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL34:
	.loc 1 469 0
	mov	r3, r0, asl #20
	mov	r3, r3, lsr #20
	mov	r0, r0, lsr #12
.LVL35:
	orr	r0, r3, r0, asl #20
	bx	lr
	.cfi_endproc
.LFE205:
	.size	odd_word, .-odd_word
	.align	2
	.global	process_quad
	.type	process_quad, %function
process_quad:
.LFB206:
	.loc 1 477 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	stmfd	sp!, {r4, r5, r6, r7, r8, lr}
	.cfi_def_cfa_offset 24
	.cfi_offset 4, -24
	.cfi_offset 5, -20
	.cfi_offset 6, -16
	.cfi_offset 7, -12
	.cfi_offset 8, -8
	.cfi_offset 14, -4
	.loc 1 480 0
	ldr	r6, .L51
	.loc 1 485 0
	ldr	r5, .L51+4
	.loc 1 480 0
	ldr	r3, [r6, #4]
	.loc 1 486 0
	ldr	r0, [r6, #8]
	.loc 1 482 0
	ldr	r7, [r3, #8]
	.loc 1 480 0
	ldr	ip, [r3]
.LVL36:
	.loc 1 485 0
	and	r1, r5, r7, asl #12
	mov	r2, ip, lsr #12
	orr	r2, r1, r2, asl #20
	mov	ip, ip, asl #20
.LVL37:
	.loc 1 481 0
	ldr	r8, [r3, #4]
.LVL38:
	.loc 1 483 0
	ldr	r4, [r3, #12]
.LVL39:
	.loc 1 485 0
	orr	r2, r2, ip, lsr #20
.LVL40:
	.loc 1 483 0
	add	r3, r3, #16
.LVL41:
	.loc 1 486 0
	add	ip, r0, #4
	str	r2, [r0]
.LVL42:
	.loc 1 487 0
	ldr	r1, .L51+8
	mov	r0, #2
	.loc 1 483 0
	str	r3, [r6, #4]
	.loc 1 486 0
	str	ip, [r6, #8]
	.loc 1 489 0
	and	r5, r5, r4, asl #12
	.loc 1 487 0
	bl	io_printf
.LVL43:
	.loc 1 489 0
	mov	r2, r8, lsr #12
	.loc 1 490 0
	ldr	r3, [r6, #8]
	.loc 1 489 0
	orr	r5, r5, r2, asl #20
	mov	r2, r8, asl #20
	orr	r2, r5, r2, lsr #20
.LVL44:
	.loc 1 490 0
	str	r2, [r3]
	.loc 1 491 0
	ldr	r1, .L51+12
	.loc 1 490 0
	add	r3, r3, #4
	.loc 1 491 0
	mov	r0, #2
	.loc 1 490 0
	str	r3, [r6, #8]
	.loc 1 491 0
	bl	io_printf
.LVL45:
	.loc 1 493 0
	mov	r3, r7, lsr #8
	mov	r1, r4, lsr #12
	and	r3, r3, #15
	mov	r4, r4, asl #8
.LVL46:
	ldr	r2, .L51+16
	orr	r3, r3, r1, asl #20
	and	r4, r4, #983040
	.loc 1 494 0
	ldr	r1, [r6, #8]
	.loc 1 493 0
	orr	r4, r3, r4
	and	r2, r2, r7, lsr #8
	orr	r2, r4, r2
.LVL47:
	.loc 1 494 0
	add	r3, r1, #4
	str	r2, [r1]
	str	r3, [r6, #8]
	.loc 1 495 0
	ldr	r1, .L51+20
	mov	r0, #2
	.loc 1 497 0
	ldmfd	sp!, {r4, r5, r6, r7, r8, lr}
	.cfi_restore 14
	.cfi_restore 8
	.cfi_restore 7
	.cfi_restore 6
	.cfi_restore 5
	.cfi_restore 4
	.cfi_def_cfa_offset 0
.LVL48:
	.loc 1 495 0
	b	io_printf
.LVL49:
.L52:
	.align	2
.L51:
	.word	.LANCHOR0
	.word	16773120
	.word	.LC2
	.word	.LC3
	.word	65520
	.word	.LC4
	.cfi_endproc
.LFE206:
	.size	process_quad, .-process_quad
	.align	2
	.global	translate_rowlets
	.type	translate_rowlets, %function
translate_rowlets:
.LFB207:
	.loc 1 501 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	stmfd	sp!, {r4, r5, r6, r7, r8, lr}
	.cfi_def_cfa_offset 24
	.cfi_offset 4, -24
	.cfi_offset 5, -20
	.cfi_offset 6, -16
	.cfi_offset 7, -12
	.cfi_offset 8, -8
	.cfi_offset 14, -4
	.loc 1 507 0
	ldr	r5, .L70
	ldr	r3, [r5, #4]
	ldr	r6, [r3]
.LVL50:
	add	r3, r3, #4
	.loc 1 508 0
	cmp	r6, #0
	.loc 1 507 0
	str	r3, [r5, #4]
	.loc 1 516 0
	movne	r7, r5
	.loc 1 508 0
	beq	.L58
.L57:
	.loc 1 516 0
	ldr	r2, [r5, #12]
	.loc 1 513 0
	and	r4, r6, #3
.LVL51:
	.loc 1 517 0
	ldr	r1, [r5, #16]
	.loc 1 516 0
	add	r2, r4, r2
	.loc 1 514 0
	mov	r6, r6, lsr #2
.LVL52:
	.loc 1 516 0
	add	r2, r2, r6, lsl #2
	.loc 1 517 0
	add	r1, r1, #1
	.loc 1 519 0
	cmp	r4, #0
	.loc 1 516 0
	str	r2, [r5, #12]
	.loc 1 517 0
	str	r1, [r5, #16]
	.loc 1 519 0
	bne	.L55
	.loc 1 520 0
	ldr	r1, [r7, #8]
	mov	r2, r6, asl #15
	add	ip, r1, #4
	.loc 1 521 0
	add	r3, r3, #4
	.loc 1 520 0
	str	r2, [r1]
	.loc 1 523 0
	mov	r0, #2
	ldr	r1, .L70+4
	.loc 1 520 0
	stmib	r7, {r3, ip}
	.loc 1 523 0
	bl	io_printf
.LVL53:
.L60:
	.loc 1 540 0 discriminator 1
	cmp	r6, #0
	movne	r4, #0
.LVL54:
	beq	.L64
.LVL55:
.L63:
	.loc 1 540 0 is_stmt 0 discriminator 3
	add	r4, r4, #1
.LVL56:
	.loc 1 541 0 is_stmt 1 discriminator 3
	bl	process_quad
.LVL57:
	.loc 1 540 0 discriminator 3
	cmp	r6, r4
	bne	.L63
.LVL58:
.L64:
	.loc 1 543 0
	ldr	r3, [r5, #4]
	ldr	r6, [r3]
.LVL59:
	add	r3, r3, #4
	.loc 1 508 0
	cmp	r6, #0
	.loc 1 543 0
	str	r3, [r5, #4]
	.loc 1 508 0
	bne	.L57
.L58:
	.loc 1 546 0
	ldr	r3, [r5, #8]
	mov	r1, #0
	add	r2, r3, #4
	str	r1, [r3]
	str	r2, [r5, #8]
	.loc 1 547 0
	ldmfd	sp!, {r4, r5, r6, r7, r8, pc}
.LVL60:
.L55:
	.loc 1 527 0
	ldr	ip, [r3, #4]
.LVL61:
	.loc 1 530 0
	ldr	r0, [r7, #8]
	mov	r2, ip, asl #20
	mov	r2, r2, lsr #20
	orr	r2, r2, r6, asl #15
	orr	r1, r2, r4, asl #13
	mov	r2, ip, lsr #12
	.loc 1 529 0
	orr	r2, r1, r2, asl #20
.LVL62:
	.loc 1 530 0
	add	ip, r0, #4
	.loc 1 527 0
	add	r3, r3, #8
	.loc 1 530 0
	str	r2, [r0]
	.loc 1 531 0
	ldr	r1, .L70+4
	mov	r0, #2
	.loc 1 530 0
	stmib	r7, {r3, ip}
	.loc 1 531 0
	bl	io_printf
.LVL63:
	.loc 1 532 0
	subs	r4, r4, #1
.LVL64:
	beq	.L60
.L61:
	.loc 1 533 0
	ldr	ip, [r5, #4]
	.loc 1 534 0
	ldr	r1, [r5, #8]
	.loc 1 533 0
	ldr	r0, [ip]
.LVL65:
	add	ip, ip, #4
.LBB60:
.LBB61:
	.loc 1 469 0
	mov	r2, r0, asl #20
	mov	r3, r2, lsr #20
	mov	r2, r0, lsr #12
	orr	r2, r3, r2, asl #20
.LVL66:
.LBE61:
.LBE60:
	.loc 1 534 0
	str	r2, [r1]
	add	r3, r1, #4
	.loc 1 535 0
	mov	r0, #2
	ldr	r1, .L70+8
	.loc 1 533 0
	str	ip, [r5, #4]
	.loc 1 534 0
	str	r3, [r5, #8]
	.loc 1 535 0
	bl	io_printf
.LVL67:
	.loc 1 532 0
	subs	r4, r4, #1
.LVL68:
	bne	.L61
	b	.L60
.L71:
	.align	2
.L70:
	.word	.LANCHOR0
	.word	.LC5
	.word	.LC6
	.cfi_endproc
.LFE207:
	.size	translate_rowlets, .-translate_rowlets
	.align	2
	.global	translate_tmp
	.type	translate_tmp, %function
translate_tmp:
.LFB208:
	.loc 1 1035 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
	.loc 1 1036 0
	ldr	r3, .L73
	ldr	r1, .L73+4
	.loc 1 1037 0
	mov	r2, #4194304
	stmib	r3, {r1, r2}
	.loc 1 1039 0
	b	translate_rowlets
.LVL69:
.L74:
	.align	2
.L73:
	.word	.LANCHOR0
	.word	.LANCHOR1
	.cfi_endproc
.LFE208:
	.size	translate_tmp, .-translate_tmp
	.align	2
	.global	circular_buffer_initialize
	.type	circular_buffer_initialize, %function
circular_buffer_initialize:
.LFB212:
	.loc 1 1112 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
	.loc 1 1113 0
	ldr	r3, .L76
	mov	r2, #0
	.loc 1 1114 0
	ldr	r1, .L76+4
	str	r1, [r3, #4]
	.loc 1 1113 0
	str	r2, [r3]
	.loc 1 1115 0
	str	r2, [r3, #8]
	.loc 1 1116 0
	str	r2, [r3, #12]
	bx	lr
.L77:
	.align	2
.L76:
	.word	circular_buffer_state
	.word	4200448
	.cfi_endproc
.LFE212:
	.size	circular_buffer_initialize, .-circular_buffer_initialize
	.align	2
	.global	__circular_buffer_overflow
	.type	__circular_buffer_overflow, %function
__circular_buffer_overflow:
.LFB213:
	.loc 1 1153 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 1157 0
	.syntax divided
@ 1157 "std_synapse.c" 1
	ldr  r8, [ip, #12] @ Load overflow value  ..           
	add  r8, r8, #1        @   .. increment it, and ..         
	ldr  r8, [ip, #12] @ Write-back                        
	mov  pc, lr                  @ Standard return                   
	@subs pc, lr, #4              @ return from FIQ.                  
	
@ 0 "" 2
	.loc 1 1163 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE213:
	.size	__circular_buffer_overflow, .-__circular_buffer_overflow
	.align	2
	.global	circular_buffer_output
	.type	circular_buffer_output, %function
circular_buffer_output:
.LFB214:
	.loc 1 1224 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL70:
	.loc 1 1225 0
	ldr	r2, [r0]
	.loc 1 1224 0
	mov	r3, r0
	.loc 1 1225 0
	ldr	r0, [r0, #4]
.LVL71:
	.loc 1 1229 0
	add	r1, r2, #16777216
	.loc 1 1225 0
	ldr	r0, [r0, r2, lsr #22]
.LVL72:
	.loc 1 1229 0
	str	r1, [r3]
	.loc 1 1242 0
	bx	lr
	.cfi_endproc
.LFE214:
	.size	circular_buffer_output, .-circular_buffer_output
	.align	2
	.global	print_primary
	.type	print_primary, %function
print_primary:
.LFB216:
	.loc 1 1476 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
.LVL73:
	stmfd	sp!, {r4, r5, r6, r7, r8, r9, r10, fp, lr}
	.cfi_def_cfa_offset 36
	.cfi_offset 4, -36
	.cfi_offset 5, -32
	.cfi_offset 6, -28
	.cfi_offset 7, -24
	.cfi_offset 8, -20
	.cfi_offset 9, -16
	.cfi_offset 10, -12
	.cfi_offset 11, -8
	.cfi_offset 14, -4
	.loc 1 1480 0
	ldr	r1, .L89
	.loc 1 1476 0
	sub	sp, sp, #12
	.cfi_def_cfa_offset 48
	.loc 1 1480 0
	mov	r0, #2
	bl	io_printf
.LVL74:
	ldr	fp, .L89+4
	.loc 1 1482 0
	mov	r10, #0
	.loc 1 1485 0
	mov	r9, #88
.LVL75:
.L81:
	cmp	r10, #0
	add	r7, fp, r10, lsl #5
	add	r7, r7, #60
	moveq	r8, #61
	movne	r8, #62
	.loc 1 1476 0
	mov	r5, #0
.LVL76:
.L87:
	mov	r6, r7
	mov	r4, #1
.LVL77:
.L85:
	.loc 1 1485 0
	cmp	r4, #1
	mov	r3, r8
	ldr	r1, .L89+8
	mov	r0, #2
	ldr	r2, [r6, #4]!
	beq	.L82
	.loc 1 1485 0 is_stmt 0 discriminator 8
	stmia	sp, {r5, r9}
	bl	io_printf
.LVL78:
	.loc 1 1484 0 is_stmt 1 discriminator 8
	cmp	r4, #2
	bne	.L83
	.loc 1 1483 0 discriminator 2
	add	r5, r5, #1
.LVL79:
	cmp	r5, #4
	add	r7, r7, #8
	bne	.L87
	.loc 1 1482 0 discriminator 2
	add	r10, r10, #1
.LVL80:
	cmp	r10, #2
	bne	.L81
	.loc 1 1494 0
	add	sp, sp, #12
	.cfi_remember_state
	.cfi_def_cfa_offset 36
	@ sp needed
	ldmfd	sp!, {r4, r5, r6, r7, r8, r9, r10, fp, pc}
.LVL81:
.L82:
	.cfi_restore_state
	.loc 1 1485 0
	mov	r3, #32
	str	r3, [sp, #4]
	str	r5, [sp]
	mov	r3, r8
	ldr	r1, .L89+8
	mov	r0, #2
	bl	io_printf
.LVL82:
.L83:
	add	r4, r4, #1
.LVL83:
	b	.L85
.L90:
	.align	2
.L89:
	.word	.LC7
	.word	.LANCHOR2
	.word	.LC8
	.cfi_endproc
.LFE216:
	.size	print_primary, .-print_primary
	.align	2
	.global	print_secondary
	.type	print_secondary, %function
print_secondary:
.LFB217:
	.loc 1 1497 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
	.loc 1 1498 0
	ldr	r1, .L92
	mov	r0, #2
	b	io_printf
.LVL84:
.L93:
	.align	2
.L92:
	.word	.LC9
	.cfi_endproc
.LFE217:
	.size	print_secondary, .-print_secondary
	.align	2
	.global	print_jump_tables
	.type	print_jump_tables, %function
print_jump_tables:
.LFB218:
	.loc 1 1502 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	stmfd	sp!, {r4, lr}
	.cfi_def_cfa_offset 8
	.cfi_offset 4, -8
	.cfi_offset 14, -4
	.loc 1 1503 0
	bl	print_primary
.LVL85:
.LBB62:
.LBB63:
	.loc 1 1498 0
	ldr	r1, .L96
	mov	r0, #2
.LBE63:
.LBE62:
	.loc 1 1505 0
	ldmfd	sp!, {r4, lr}
	.cfi_restore 14
	.cfi_restore 4
	.cfi_def_cfa_offset 0
.LBB65:
.LBB64:
	.loc 1 1498 0
	b	io_printf
.LVL86:
.L97:
	.align	2
.L96:
	.word	.LC9
.LBE64:
.LBE65:
	.cfi_endproc
.LFE218:
	.size	print_jump_tables, .-print_jump_tables
	.align	2
	.global	print_synapse_jump_table
	.type	print_synapse_jump_table, %function
print_synapse_jump_table:
.LFB219:
	.loc 1 1618 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	stmfd	sp!, {r4, r5, r6, lr}
	.cfi_def_cfa_offset 16
	.cfi_offset 4, -16
	.cfi_offset 5, -12
	.cfi_offset 6, -8
	.cfi_offset 14, -4
	.loc 1 1621 0
	ldr	r1, .L102
	mov	r0, #2
	bl	io_printf
.LVL87:
	ldr	r5, .L102+4
	.loc 1 1623 0
	mov	r4, #0
.LVL88:
.L99:
	.loc 1 1624 0 discriminator 3
	mov	r3, r4
	ldr	r2, [r5, #-4]!
	.loc 1 1623 0 discriminator 3
	add	r4, r4, #1
.LVL89:
	.loc 1 1624 0 discriminator 3
	ldr	r1, .L102+8
	mov	r0, #2
	bl	io_printf
.LVL90:
	.loc 1 1623 0 discriminator 3
	cmp	r4, #8
	bne	.L99
	.loc 1 1626 0
	ldr	r1, .L102+12
	mov	r0, #2
	.loc 1 1627 0
	ldmfd	sp!, {r4, r5, r6, lr}
	.cfi_restore 14
	.cfi_restore 6
	.cfi_restore 5
	.cfi_restore 4
	.cfi_def_cfa_offset 0
.LVL91:
	.loc 1 1626 0
	b	io_printf
.LVL92:
.L103:
	.align	2
.L102:
	.word	.LC10
	.word	.LANCHOR3-2800
	.word	.LC11
	.word	.LC12
	.cfi_endproc
.LFE219:
	.size	print_synapse_jump_table, .-print_synapse_jump_table
	.align	2
	.global	global_timer_tick
	.type	global_timer_tick, %function
global_timer_tick:
.LFB220:
	.loc 1 1639 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
	.loc 1 1639 0
	ldr	r1, .L105
	ldrd	r2, [r1, #188]
	adds	r2, r2, #1
	adc	r3, r3, #0
	strd	r2, [r1, #188]
	bx	lr
.L106:
	.align	2
.L105:
	.word	.LANCHOR3-2928
	.cfi_endproc
.LFE220:
	.size	global_timer_tick, .-global_timer_tick
	.align	2
	.global	global_timer_value
	.type	global_timer_value, %function
global_timer_value:
.LFB221:
	.loc 1 1643 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
	.loc 1 1643 0
	ldr	r3, .L108
	ldrd	r0, [r3, #-4]
	bx	lr
.L109:
	.align	2
.L108:
	.word	.LANCHOR3-2736
	.cfi_endproc
.LFE221:
	.size	global_timer_value, .-global_timer_value
	.align	2
	.global	set_global_timer
	.type	set_global_timer, %function
set_global_timer:
.LFB222:
	.loc 1 1647 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
.LVL93:
	.loc 1 1647 0
	ldr	r3, .L111
	strd	r0, [r3, #-4]
	bx	lr
.L112:
	.align	2
.L111:
	.word	.LANCHOR3-2736
	.cfi_endproc
.LFE222:
	.size	set_global_timer, .-set_global_timer
	.align	2
	.global	read_a_rowlet
	.type	read_a_rowlet, %function
read_a_rowlet:
.LFB223:
	.loc 1 1720 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 1728 0
	ldr	r5, .L114
	.loc 1 1729 0
	mov	r4, #508
	.loc 1 1730 0
	mov	ip, #4194304
	.loc 1 1731 0
	mov	r9, #1610612736
	.loc 1 1733 0
	ldr	r10, .L114+4
	.loc 1 1735 0
	.syntax divided
@ 1735 "std_synapse.c" 1
	ldr   r0, [fp], #4              @ Get next rowlet                   
	str   r10, [ip, #8]           @ Store DTCM address                
	and   r0, r0, #0xfffff87f          @ mask out delay                    
	and   r1, r4, r0, lsl #2      @ mask off size to bits 8-2         
	add   r1, r1, #4                   @ Add 1: DMA-ing 0 words is silly   
	add   r2, r9, r0, lsr #9     @ SDRAM address                     
	clz   r3, r1                       @ Take log_2(size)                  
	ldrb  r0, [r5, r3]           @ Load the burst/control byte       
	add   r10, r10, r1             @ increment the DTCM pointer        
	str   r2, [ip, #4]              @ Store SDRAM address               
	add   r0, r1, r0, lsl #20          @ Add size to shifted control word  
	str   r0, [ip, #12]             @ Store Control Word                
	
@ 0 "" 2
	.loc 1 1737 0
@ 1737 "std_synapse.c" 1
	mov   r3, #0x8            @ cancel one outstanding DMA 
	str   r3, [ip, #16]    @ Cancel one outstanding DMA 
	bx lr                                                  
	
@ 0 "" 2
	.loc 1 1741 0
	.arm
	.syntax divided
.L115:
	.align	2
.L114:
	.word	.LANCHOR2+107
	.word	4202496
	.cfi_endproc
.LFE223:
	.size	read_a_rowlet, .-read_a_rowlet
	.align	2
	.global	dma_scheduler
	.type	dma_scheduler, %function
dma_scheduler:
.LFB224:
	.loc 1 1843 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 1853 0
	.syntax divided
@ 1853 "std_synapse.c" 1
	mov pc, lr
	
@ 0 "" 2
	.loc 1 1858 0
@ 1858 "std_synapse.c" 1
	push {r4,r5,r6,r7,lr} @ Save registers                 
	
@ 0 "" 2
	.loc 1 1866 0
@ 1866 "std_synapse.c" 1
	ldr r6,  [ip, #16] @ Get input pointer          
	ldr r7, [ip, #8]  @ Get output pointer         
	mov  r3, #0x8                  @ Set up clear_control       
	cmp r6, r7            @ Test nonempty              
	
@ 0 "" 2
	.loc 1 1869 0
@ 1869 "std_synapse.c" 1
	beq .L117 @ Skip if there are no spikes 
	
@ 0 "" 2
	.arm
	.syntax divided
.L120:
	.loc 1 1871 0 discriminator 1
	.syntax divided
@ 1871 "std_synapse.c" 1
	ldr   r1,      [ip, #12]   @ Get base address                
	add   r7, r7, #0x1000000 @ Increment output pointer        
	ldr   r0, [r1, r7, lsr #22]   @ Load spike                      
	ldr   r2,      [ip, #24]   @ Get small write descriptor      
	ldr   r1,      [ip, #32]   @ Get rowlet buffer pointer       
	str   r7, [ip, #8]    @ Write-back output pointer       
	@--------------------------------------------------------------------
	@ INSERT DMA TRANSFER CODE HERE!!!!                                  
	@--------------------------------------------------------------------
	stmib fp, {r0-r3}              @ Do DMA transfer                 
	add   r1, r1, #4                   @ Increment rowlet buffer ptr     
	ldr   r1,      [ip, #32]   @ Write-back rowlet buffer pointer
	lsrs  r0, r0, #1         @ Test again for another DMA done 
	popeq {r4-r7,pc}                   @ Return if all done DMAs sorted  
	cmp r6, r7                @ Test nonempty (again)           
	
@ 0 "" 2
	.loc 1 1873 0 discriminator 1
@ 1873 "std_synapse.c" 1
	bne .L120 @ Transfer another spike, if there's still    
	           @ a completed outstanding transaction         
	
@ 0 "" 2
	.arm
	.syntax divided
.L117:
	.loc 1 1886 0
	.syntax divided
@ 1886 "std_synapse.c" 1
	ldr   r6, [ip, #16]  @ Get input pointer          
	ldr   r1, [ip, #32]      @ Get output pointer         
	ldr   r2, [ip, #20]      @ Get small write descriptor 
	
@ 0 "" 2
	.arm
	.syntax divided
.L119:
	.loc 1 1888 0 discriminator 1
	.syntax divided
@ 1888 "std_synapse.c" 1
	cmp   r6, r7              @ Test nonempty                   
	popeq {r4-r7,pc}                   @ Return if all done DMAs sorted  
	ldr   r1,     [ip, #12]       @ Get base address                
	add   r7, r7, #0x1000000 @ Increment output pointer        
	str   r7, [ip, #8]       @ Write-back output pointer       
	ldr   r0, [r1, r7, lsr #22]   @ Load spike                      
	@--------------------------------------------------------------------
	@ INSERT DMA TRANSFER CODE HERE!!!!                                  
	@--------------------------------------------------------------------
	lsrs  r0, r0, #1         @ Test again for another DMA done 
	
@ 0 "" 2
	.loc 1 1890 0 discriminator 1
@ 1890 "std_synapse.c" 1
	bne .L119        @ Transfer another rowlet, if there's still    
	                  @    a completed outstanding transaction       
	pop {r4-r7,pc}    @ Return if all done DMAs sorted               
	
@ 0 "" 2
	.loc 1 1894 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE224:
	.size	dma_scheduler, .-dma_scheduler
	.align	2
	.global	__saturation_detected_1
	.type	__saturation_detected_1, %function
__saturation_detected_1:
.LFB225:
	.loc 1 2250 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 2251 0
	.syntax divided
@ 2251 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 2253 0
@ 2253 "std_synapse.c" 1
	ldr    r1, [ip, #112]          @ Load saturation counter          
	mov    r0, #0                         @ Saturate ring buffer             
	strh   r0, [r4]                       @ Write back ring buffer           
	adds   r1, r1, #1                     @ Increment the saturation counter 
	moveq  r1, #-1                        @ Saturate the saturation counter  
	str    r1, [ip, #112]          @ Write back saturation counter    
	bx     lr                             @ Return                           
	
@ 0 "" 2
	.loc 1 2261 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE225:
	.size	__saturation_detected_1, .-__saturation_detected_1
	.align	2
	.global	__saturation_detected_2
	.type	__saturation_detected_2, %function
__saturation_detected_2:
.LFB226:
	.loc 1 2298 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 2299 0
	.syntax divided
@ 2299 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 2301 0
@ 2301 "std_synapse.c" 1
	cmp    r0, #0                @ Did the first synapse saturate?                          
	movmi  r0, #0                @ Saturated value in r0                                    
	strh   r0, [r3]              @ Store back modified result in all cases                  
	movpl  r2, #-1               @ Local saturation counter (r2) holds sat count - 1        
	cmp    r1, #0                @ Did the second synapse saturate?                         
	movmi  r1, #0                @ Saturated value in r1                                    
	strh   r1, [r4]              @ Store back modified result in all cases                  
	ldr    r1, [ip, #112] @ Load global saturation counter                           
	addpl  r2, r2, #-1           @ Local saturation counter holds sat count - 2             
	add    r2, r2, #2            @ local saturation counter now holds the count             
	adds   r1, r1, r2            @ 'Add' the local counter to the global one                
	movcs  r1, #-1               @ Saturate the saturation counter                          
	str    r1, [ip, #112] @ Write back global saturation counter                     
	bx     lr                    @ Return                                                   
	
@ 0 "" 2
	.loc 1 2316 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE226:
	.size	__saturation_detected_2, .-__saturation_detected_2
	.align	2
	.global	__saturation_detected_3
	.type	__saturation_detected_3, %function
__saturation_detected_3:
.LFB227:
	.loc 1 2374 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 2375 0
	.syntax divided
@ 2375 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 2379 0
@ 2379 "std_synapse.c" 1
	cmp    r0, #0                           @ Did the first synapse (S0) saturate?                     
	movmi  r0, #0                           @ Saturate the result for S0 if needed                     
	strh   r0, [r3]                         @ Store back modified result, in all cases                 
	movpl  r0, #-1                          @ Local saturation counter (r0) holds sat count - 1        
	cmp    r2, #0                           @ Did the second synapse (S2) saturate?                    
	movmi  r2, #0                           @ Saturate the result for S2 if needed                     
	strh   r2, [r4]                         @ Store back modified result in all cases                  
	addpl  r0, r0, #-1                      @ Local saturation counter (r0) holds sat count - 2        
	ldr    r2, [fp], #-16                @ Start re-calculating address of S1                       
	cmp    r1, #0                           @ Did the third synapse (S1) saturate?                     
	movmi  r1, #0                           @ Saturate the result for S1 if needed                     
	add    r2, r8, r2, lsl #20    @ S1 Add to rotated time_base                              
	ror    r2, r2, #19                      @ S1 Rotate back again                                     
	strh   r1, [r2]                         @ Store back modified result in all cases                  
	addpl  r0, r0, #-1                      @ Local saturation counter (r0) holds sat count - 3        
	ldr    r1, [ip, #112]            @ Load global saturation counter                           
	add    r0, r0, #3                       @ Local saturation counter now holds sat-count             
	adds   r1, r1, r0                       @ Add the local counter to the global one                  
	movcs  r1, #-1                          @ Saturate the saturation counter                          
	str    r1, [ip, #112]            @ Write back global saturation counter                     
	bx     lr                               @ Return                                                   
	
@ 0 "" 2
	.loc 1 2402 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE227:
	.size	__saturation_detected_3, .-__saturation_detected_3
	.align	2
	.global	__packed_fix_up_4
	.type	__packed_fix_up_4, %function
__packed_fix_up_4:
.LFB228:
	.loc 1 2673 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 2674 0
	.syntax divided
@ 2674 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 2678 0
@ 2678 "std_synapse.c" 1
	cmp    r1, #0                            @ Did the third synapse (S1) saturate?                     
	movmi  r1, #0                            @ Saturated value in r1                                    
	strh   r1, [r4]                          @ Store back modified result, in all cases                 
	movpl  r1, #-1                           @ local saturation counter r1 holds sat-count - 1          
	@---------------------------------------------------------------------------------------------------
	@  At this point, we now recalculate ring-buffer addresses for synapses S0, S2, and S3.             
	@---------------------------------------------------------------------------------------------------
	ldr    r10, [fp, #-12]               @ recalculate address for (S0) ring-buffer                 
	and    r4, r6, r10, lsr #11        @ S2 mask out middle 8-bits from w into bits 8-1           
	add    r10, r8, r10, lsl #20 @ S0 add delay to timer_base and mask with shift           
	ror    r10, r10, #19                   @ S0 rotate to position                                    
	cmp    r0, #0                            @ Did the fourth synapse (S0) saturate?                    
	movmi  r0, #0                            @ Saturated value in r0, if required (otherwise old value) 
	strh   r0, [r10]                        @ Store back modified result in all cases                  
	addpl  r1, r1, #-1                       @ local saturation counter r1 holds sat-count - 2          
	ldrh   r10, [fp, #-6]                @ S2 Pre-load synaptic half-word for S2 with 0x wwwd       
	add    r10, r8, r10, lsl #28 @ S2 add delay to timer_base (= 4 bits time + base)        
	orr    r10, r4, r10, ror #19           @ S2 rotate to position and 'or' in index bits             
	cmp    r2, #0                            @ Did the fourth synapse (S0) saturate?                    
	movmi  r2, #0                            @ Saturated value in r2, if required (otherwise old value) 
	strh   r2, [r10]                        @ Store back modified result in all cases                  
	addpl  r1, r1, #-1                       @ local saturation counter r1 holds sat-count - 3          
	ldr    r10, [fp, #-8]                @ recalculate address for (S3) ring-buffer                 
	and    r4, r6, r10, lsr #11        @ S3 mask out middle 8-bits from w into bits 8-1           
	ldrh   r10, [fp, #-4]                @ S3 Pre-load synaptic half-word for S3 with 0x wwwd       
	add    r10, r8, r10, lsl #28 @ S3 add delay to timer_base (= 4 bits time + base)        
	orr    r10, r4, r10, ror #19           @ S3 rotate to position and 'or' in index bits             
	cmp    r3, #0                            @ Did the fourth synapse (S3) saturate?                    
	movmi  r3, #0                            @ Saturated value in r3, if required (otherwise old value) 
	strh   r3, [r10]                        @ Store back modified result in all cases                  
	addpl  r1, r1, #-1                       @ local saturation counter r1 holds sat-count - 4          
	ldr    r2, [ip, #112]             @ Load global saturation counter                           
	add    r1, r1, #4                                                                                   
	adds   r1, r2, r1                        @ Add the local counter to the global one                  
	movcs  r1, #-1                           @ Saturate the saturation counter                          
	str    r1, [ip, #112]             @ Write back global saturation counter                     
	bx     lr                                                                                           
	
@ 0 "" 2
	.loc 1 2719 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE228:
	.size	__packed_fix_up_4, .-__packed_fix_up_4
	.align	2
	.global	__dense_fix_up_4
	.type	__dense_fix_up_4, %function
__dense_fix_up_4:
.LFB229:
	.loc 1 2808 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 2816 0
	.syntax divided
@ 2816 "std_synapse.c" 1
	cmp    r2, #0                            @ Did S2 saturate?                                   
	movmi  r2, #0                            @ Saturate if needed.                                
	strh   r2, [r4, #-2]                     @ S2 Write-back ring-element                         
	movpl  r2, #-1                           @ r2 is local sat-counter.                           
	cmp    r3, #0                            @ Did S3 saturate?                                   
	movmi  r3, #0                            @ Saturate if needed.                                
	strh   r3, [r5, #-4]                     @ S3 Write-back ring-element                         
	ldrh   r4, [fp, #-12]                 @ reload S0                                          
	addpl  r2, r2, #-1                       @ r2 is local sat-counter.                           
	ldrh   r5, [fp, #-10]                 @ reload S1                                          
	add    r4, r8, r4, lsl #28     @ S0 Add delay to time-base                          
	add    r4, fp, r4, ror #19            @ S0 Add in the index, via wp                        
	cmp    r0, #0                            @ Did S0 saturate?                                   
	movmi  r0, #0                            @ Saturate if needed.                                
	strh   r0, [r4, #-16]                    @ S0 Load ring-buffer weight	                 
	addpl  r2, r2, #-1                       @ r2 is local sat-counter.                           
	add    r5, r8, r5, lsl #28     @ S1 Add delay to time-base                          
	add    r5, fp, r5, ror #19            @ S1 Add in the index, via wp                        
	cmp    r1, #0                            @ Did S1 saturate?                                   
	movmi  r1, #0                            @ Saturate if needed.                                
	strh   r1, [r5, #-14]                    @ S1 Load ring-buffer weight	                 
	addpl  r2, r2, #-1                       @ r2 is local sat-counter.                           
	ldr    r1, [ip, #112]             @ Load global saturation counter                     
	add    r2, r2, #4                        @ Compensate for sat-counter being sc-4              
	adds   r1, r2, r1                        @ Add the local counter to the global one            
	movcs  r2, #-1                           @ Saturate the saturation counter                    
	str    r2, [ip, #112]             @ Write back global saturation counter               
	bx     lr                                                                                     
	
@ 0 "" 2
	.loc 1 2846 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE229:
	.size	__dense_fix_up_4, .-__dense_fix_up_4
	.align	2
	.global	__synapse_head
	.type	__synapse_head, %function
__synapse_head:
.LFB230:
	.loc 1 2852 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 2862 0
	.syntax divided
@ 2862 "std_synapse.c" 1
	cmp  r9, #0     @ Test whether the rolwet is empty (SHOULD NOT HAPPEN) 
	bxeq lr           @ Return if there are no synapses  (SHOULD NOT HAPPEN) 
	push {lr}         @ Otherwise, push link register: we might need to ..   
	                  @  .. call saturation fix-up or dma feeding routines.  
	tst  r9, #1     @ Test to see if there's an odd synapse                
	beq  .L129       @ If not skip over __synapse_1                         
	
@ 0 "" 2
	.loc 1 2870 0
@ 2870 "std_synapse.c" 1
	                                       @ The synaptic word is already pre-loaded into w      
	add    r4, r8, r10, lsl #20 @ Add to rotated time_base                            
	ror    r4, r4, #19                     @ Rotate back again                                   
	ldrh   r0, [r4]                        @ Load the ring-buffer element                        
	subs   r0, r0, r10, lsr #20           @ 'add' weight to ring buffer, testing for saturation 
	strplh r0, [r4]                        @ write back ring buffer, if no saturation            
	ldr    r10, [fp], #4               @ Pre-load next synaptic word, incrementing wp        
	blmi   __saturation_detected_1         @ if saturated, repair                                
	
@ 0 "" 2
	.arm
	.syntax divided
.L129:
	.loc 1 2873 0
	.syntax divided
@ 2873 "std_synapse.c" 1
	tst  r9, #2     @ Test to see if there's two odd synapses              
	beq  .L130       @ If not skip over __synapse_2                         
	
@ 0 "" 2
	.loc 1 2877 0
@ 2877 "std_synapse.c" 1
	                                       @ S0 word pre-loaded into w            
	ldr    r2, [fp], #4                 @ S1 Load the synaptic word            
	add    r3, r8, r10, lsl #20 @ S0 Add to rotated time_base          
	ror    r3, r3, #19                     @ S0 Rotate back again                 
	ldrh   r0, [r3]                        @ S0 Load the ring-buffer element      
	add    r4, r8, r2, lsl #20   @ S1 Add to rotated time_base          
	ror    r4, r4, #19                     @ S1 Rotate back again                 
	ldrh   r1, [r4]                        @ S1 Load the ring-buffer element      
	subs   r0, r0, r10, lsr #20           @ S0 'add' weight to ring buffer       
	strplh r0, [r3]                        @ S0 write back ring buffer, if OK     
	subpls r1, r1, r2, lsr #20             @ S1 'add' weight to ring buffer       
	strplh r1, [r4]                        @ S1 write back ring buffer, if OK     
	ldr    r10, [fp], #4               @ Pre-load next synaptic word          
	blmi   __saturation_detected_2         @ if saturated, repair                 
	
@ 0 "" 2
	.arm
	.syntax divided
.L130:
	.loc 1 2882 0
	.syntax divided
@ 2882 "std_synapse.c" 1
	ands  r9, r9, #0xfffffffc @ mask out the bottom 2 bits treated as small cases   
	popeq {pc}                    @ If result is 0, we are done.                        
	ldr   r1, [ip, #116]     @ Load the Synapse Jump Table                         
	ands  r0, r9, #0xc          @ Mask out bottom two bits of remaining n             
	lsr   r9, r9, #4          @ n now indicates number of whole loops to do         
	beq   __synapse_loop          @ If no odds & ends need to be processed: jump        
	ldr   pc, [r1, r0]            @  .. otherwise use jump table entry point            
	
@ 0 "" 2
	.loc 1 2900 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE230:
	.size	__synapse_head, .-__synapse_head
	.align	2
	.global	__rowlet_dispatch2_0
	.type	__rowlet_dispatch2_0, %function
__rowlet_dispatch2_0:
.LFB249:
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
	.syntax divided
@ 2909 "std_synapse.c" 1
	bx lr
	
@ 0 "" 2
	.arm
	.syntax divided
	bx	lr
	.cfi_endproc
.LFE249:
	.size	__rowlet_dispatch2_0, .-__rowlet_dispatch2_0
	.align	2
	.global	__rowlet_dispatch2_3
	.type	__rowlet_dispatch2_3, %function
__rowlet_dispatch2_3:
.LFB232:
	.loc 1 2909 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	@ link register save eliminated.
	.loc 1 2909 0
	.syntax divided
@ 2909 "std_synapse.c" 1
	bx lr
	
@ 0 "" 2
	.arm
	.syntax divided
	bx	lr
	.cfi_endproc
.LFE232:
	.size	__rowlet_dispatch2_3, .-__rowlet_dispatch2_3
	.align	2
	.global	dense_256
	.type	dense_256, %function
dense_256:
.LFB233:
	.loc 1 2917 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 2932 0
	.syntax divided
@ 2932 "std_synapse.c" 1
	push   {lr}                              @ Return                                             
	ldr    r6, [fp], #4                @ Load synapses (Has this aleady been done?)         
	mov    r9, #15                         @ Number of loops to execute                         
	
@ 0 "" 2
	.loc 1 2938 0
	.arm
	.syntax divided
	ldr	r7, .L137
	.loc 1 2941 0
	.syntax divided
@ 2941 "std_synapse.c" 1
	and    r7, r6, r7               @ Initialise S0                                      
	lsr    r6, r6, #16                 @ Initialise S1; Assumes little-endianness           
	
@ 0 "" 2
	.loc 1 2945 0
	.arm
	.syntax divided
	mov	r0, fp
	bl	printx
.LVL94:
	.loc 1 2946 0
	mov	r0, r7
	bl	printx
.LVL95:
	.loc 1 2947 0
	mov	r0, r6
	bl	printx
.LVL96:
	.loc 1 2954 0
	.syntax divided
@ 2954 "std_synapse.c" 1
	add    r4, r8, r7, lsl #28  @ S0 Add delay to time-base                          
	add    r4, fp, r4, ror #19            @ S0 Add in the index, via wp                        
	ldrh   r0, [r4, #-4]                     @ S0 Load ring-buffer weight	                 
	add    r5, r8, r6, lsl #28  @ S1 Add delay to time-base                          
	add    r5, fp, r5, ror #19            @ S1 Add in the index, via wp                        
	ldrh   r1, [r5, #-2]                     @ S1 Load ring-buffer weight                         
	subs   r0, r0, r7, lsr #4             @ S0 'add' weight                                    
	strplh r0, [r4, #-4]                     @ S0 Conditionally store ring-element                
	subpls r1, r1, r6, lsr #4             @ S1 'add' weight                                    
	strplh r1, [r5, #-2]                     @ S1 Conditionally store ring-element                
	
@ 0 "" 2
	.loc 1 2966 0
	.arm
	.syntax divided
	mov	r0, r4
	bl	printx
.LVL97:
	.loc 1 2967 0
	mov	r0, r5
	bl	printx
.LVL98:
	.loc 1 2969 0
	.syntax divided
@ 2969 "std_synapse.c" 1
	@bpl    .L135                          @
	pop    {pc}                              @
	
@ 0 "" 2
	.arm
	.syntax divided
.L135:
	.loc 1 2976 0 discriminator 1
	.syntax divided
@ 2976 "std_synapse.c" 1
	                                         @ Assume that both synapse half-words are pre-loaded 
	add    r4, r8, r7, lsl #28  @ S0 Add delay to time-base                          
	add    r4, fp, r4, ror #19            @ S0 Add in the index, via wp                        
	ldrh   r0, [r4, #-4]                     @ S0 Load ring-buffer weight	                     
	add    r5, r8, r6, lsl #28  @ S1 Add delay to time-base                          
	add    r5, fp, r5, ror #19            @ S1 Add in the index, via wp                        
	ldrh   r1, [r5, #-2]                     @ S1 Load ring-buffer weight                         
	subs   r0, r0, r7, lsr #4             @ S0 'add' weight                                    
	strplh r0, [r4, #-4]                     @ S0 Conditionally store ring-element                
	ldrh   r7, [fp], #2                @ S2 Load a new half word synapse                    
	subpls r1, r1, r6, lsr #4             @ S1 'add' weight                                    
	strplh r1, [r5, #-2]                     @ S1 Conditionally store ring-element                
	ldrh   r6, [fp], #2                @ S3 Load a new half word synapse and auto-increment 
	@=============================================================================================
	@  At this point we have handled two of the four synapses                                     
	@=============================================================================================
	add    r4, r8, r7, lsl #28  @ S2 Add delay to time-base                          
	add    r4, fp, r4, ror #19            @ S2 Add in the index, via wp                        
	ldrh   r2, [r4, #-4]                     @ S2 Load ring-buffer weight	                     
	add    r5, r8, r6, lsl #28  @ S3 Add delay to time-base                          
	add    r5, fp, r5, ror #19            @ S3 Add in the index, via wp                        
	ldrh   r3, [r5, #-2]                     @ S3 Load ring-buffer weight                         
	subpls r2, r2, r7, lsr #4             @ S2 'add' weight                                    
	strplh r2, [r4, #-4]                     @ S2 Conditionally store ring-element                
	
@ 0 "" 2
	.loc 1 2978 0 discriminator 1
@ 2978 "std_synapse.c" 1
	subpls r3, r3, r6, lsr #4             @ S3 'add' weight                                    
	strplh r3, [r5, #-2]                     @ S3 Conditionally store ring-element                
	blmi   __dense_fix_up_4                  @ Perform fix-up, if saturation occurred             
	
@ 0 "" 2
	.loc 1 2983 0 discriminator 1
@ 2983 "std_synapse.c" 1
	mov  r1, #0x40000000        @ Load base address of DMA    
	ldr  r0, [r1, #20]          @ Check DMA status            
	ands r0, r0, #0xc00         @ Extract DMA completed flags 
	blne dma_scheduler          @ Set up new DMAs if needed   
	
@ 0 "" 2
	.loc 1 2985 0 discriminator 1
@ 2985 "std_synapse.c" 1
	subs   r9, r9, #1                    @ Test to see if the rowlet is completed             
	ldrplh r7, [fp]                    @ S0 Conditionally load a new half word synapse      
	ldrplh r6, [fp], #4                @ S1 Conditionally load a new half word synapse      
	
@ 0 "" 2
	.loc 1 2989 0 discriminator 1
@ 2989 "std_synapse.c" 1
	@bpl    .L135                          @
	pop    {pc}                              @
	
@ 0 "" 2
	.loc 1 2991 0
	.arm
	.syntax divided
.L138:
	.align	2
.L137:
	.word	65535
	.cfi_endproc
.LFE233:
	.size	dense_256, .-dense_256
	.align	2
	.global	__long_fixed_rowlet
	.type	__long_fixed_rowlet, %function
__long_fixed_rowlet:
.LFB234:
	.loc 1 3176 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3178 0
	.cfi_endproc
.LFE234:
	.size	__long_fixed_rowlet, .-__long_fixed_rowlet
	.align	2
	.global	__standard_rowlet
	.type	__standard_rowlet, %function
__standard_rowlet:
.LFB235:
	.loc 1 3182 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3184 0
	.cfi_endproc
.LFE235:
	.size	__standard_rowlet, .-__standard_rowlet
	.align	2
	.global	rowlet_dispatch
	.type	rowlet_dispatch, %function
rowlet_dispatch:
.LFB245:
	.loc 1 3625 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	.loc 1 3626 0
	.syntax divided
@ 3626 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3628 0
@ 3628 "std_synapse.c" 1
	and    r0, r5, r10, lsr #10   @ Set r0 = ..SS EX..                               
	@-------------------------------------------------------------------------------------------
	@ At this point r0 contains: .... .... .... .... .... .... ..SS EX..                        
	@-------------------------------------------------------------------------------------------
	ldr    r1, [r7, r0]                 @ Set up 16-way primary dispatch jump address      
	and    r9, r5, r10, lsr #14 @ Take opportunity to mask out n ..                
	bx     r1                                @ Take the primary jump unconditionally            
	@-------------------------------------------------------------------------------------------
	@ At this point   r0 contains: .... .... .... .... .... .... ..SS EX..     (. is 0)         
	@                 n  contains: .... .... .... .... .... .... ..QQ QQ..     (. is 0)         
	@-------------------------------------------------------------------------------------------
	
@ 0 "" 2
	.loc 1 3663 0
	.arm
	.syntax divided
	.cfi_endproc
.LFE245:
	.size	rowlet_dispatch, .-rowlet_dispatch
	.align	2
	.global	process_rowlets
	.type	process_rowlets, %function
process_rowlets:
.LFB246:
	.loc 1 3673 0
	.cfi_startproc
	@ Naked Function: prologue and epilogue provided by programmer.
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
.LVL99:
	.loc 1 3674 0
	.syntax divided
@ 3674 "std_synapse.c" 1
	@ spoof register use
	
@ 0 "" 2
	.loc 1 3676 0
@ 3676 "std_synapse.c" 1
	push  {r4-r12,lr}  @ Save all 'C' registers    
	
@ 0 "" 2
	.loc 1 3679 0
@ 3679 "std_synapse.c" 1
	mov   fp, r0                     @ Copy the start pointer into the correct register: wp     
	ldr   r10, [fp], #4             @ Load first word into w, increment pointer wp             
	
@ 0 "" 2
	.loc 1 3683 0
	.arm
	.syntax divided
	ldr	ip, .L143
	.loc 1 3685 0
	ldr	r6, .L143+4
	.loc 1 3684 0
	ldr	r8, [ip, #-2740]
	.loc 1 3683 0
	sub	ip, ip, #2928
	.loc 1 3684 0
	mov	r8, r8, asl #28
	orr	r8, r8, #512
	orr	r8, r8, #2
	.loc 1 3683 0
	add	ip, ip, #124
	.loc 1 3686 0
	mov	r5, #60
	.loc 1 3687 0
	ldr	r7, .L143+8
	.loc 1 3689 0
	.syntax divided
@ 3689 "std_synapse.c" 1
	@
	
@ 0 "" 2
	.loc 1 3693 0
	.arm
	.syntax divided
	bl	start_timer
.LVL100:
	.loc 1 3695 0
	.syntax divided
@ 3695 "std_synapse.c" 1
	add  r0, pc, #4                     @ Push a return address pointing to the next instruction ..
	                                    @   .. after the branch to rowlet_dispatch                 
	push {r0}                           @ The link register (lr) can now be re-purposed during     
	                                    @   .. rowlet processing, as needed.                       
	b    rowlet_dispatch                @ Now just __branch__ to the dispatch code                 
	
@ 0 "" 2
	.loc 1 3702 0
	.arm
	.syntax divided
	bl	stop_timer
.LVL101:
	.loc 1 3710 0
	.syntax divided
@ 3710 "std_synapse.c" 1
	mov  r0, fp                      @ Set up return value (current value of wp)                
	
@ 0 "" 2
	.loc 1 3713 0
@ 3713 "std_synapse.c" 1
	pop   {r4-r12,pc}  @ Restore all 'C' registers 
	
@ 0 "" 2
	.loc 1 3714 0
	.arm
	.syntax divided
.L144:
	.align	2
.L143:
	.word	.LANCHOR3
	.word	510
	.word	.LANCHOR2+64
	.cfi_endproc
.LFE246:
	.size	process_rowlets, .-process_rowlets
	.align	2
	.global	c_main
	.type	c_main, %function
c_main:
.LFB247:
	.loc 1 3724 0
	.cfi_startproc
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 0, uses_anonymous_args = 0
	stmfd	sp!, {r4, r5, r6, r7, lr}
	.cfi_def_cfa_offset 20
	.cfi_offset 4, -20
	.cfi_offset 5, -16
	.cfi_offset 6, -12
	.cfi_offset 7, -8
	.cfi_offset 14, -4
	sub	sp, sp, #12
	.cfi_def_cfa_offset 32
	.loc 1 3729 0
	bl	initialise_timer
.LVL102:
.LBB66:
.LBB67:
	.loc 1 420 0
	mov	r4, #15
.LVL103:
.L146:
	.loc 1 421 0
	mov	r0, r4
	.loc 1 420 0
	sub	r4, r4, #1
.LVL104:
	.loc 1 421 0
	bl	reset_ring_buffer_row
.LVL105:
	.loc 1 420 0
	cmn	r4, #1
	bne	.L146
.LVL106:
.LBE67:
.LBE66:
.LBB68:
.LBB69:
	.loc 1 1503 0
	bl	print_primary
.LVL107:
.LBB70:
.LBB71:
	.loc 1 1498 0
	ldr	r1, .L149
	mov	r0, #2
	bl	io_printf
.LVL108:
.LBE71:
.LBE70:
.LBE69:
.LBE68:
	.loc 1 3733 0
	bl	print_synapse_jump_table
.LVL109:
.LBB72:
.LBB73:
	.loc 1 450 0
	mov	r0, #0
	bl	print_ring_buffer
.LVL110:
	.loc 1 451 0
	mov	r0, #1
	bl	print_ring_buffer
.LVL111:
.LBE73:
.LBE72:
	.loc 1 3766 0
	ldr	r3, .L149+4
	.loc 1 3769 0
	ldr	r2, .L149+8
	.loc 1 3768 0
	ldr	r1, .L149+12
	.loc 1 3767 0
	ldr	r0, .L149+16
	.loc 1 3766 0
	mov	ip, #32768
	.loc 1 3774 0
	mov	r6, #0
	.loc 1 3766 0
	str	ip, [r3]
	.loc 1 3770 0
	str	ip, [r3, #16]
	.loc 1 3767 0
	str	r0, [r3, #4]
	.loc 1 3771 0
	str	r0, [r3, #20]
	.loc 1 3776 0
	str	r0, [r3, #40]
	.loc 1 3768 0
	str	r1, [r3, #8]
	.loc 1 3772 0
	str	r1, [r3, #24]
	.loc 1 3777 0
	str	r1, [r3, #44]
	.loc 1 3781 0
	str	r1, [r3, #56]
	.loc 1 3769 0
	str	r2, [r3, #12]
	.loc 1 3773 0
	str	r2, [r3, #28]
	.loc 1 3775 0
	str	r2, [r3, #36]
	.loc 1 3778 0
	str	r2, [r3, #48]
	.loc 1 3782 0
	str	r2, [r3, #60]
	.loc 1 3774 0
	str	r6, [r3, #32]
	.loc 1 3780 0
	str	r6, [r3, #52]
	.loc 1 3783 0
	str	r6, [r3, #64]
.LBB74:
.LBB75:
	.loc 1 1036 0
	ldr	r4, .L149+20
	ldr	r3, .L149+24
	.loc 1 1037 0
	mov	r7, #4194304
	stmib	r4, {r3, r7}
	.loc 1 1039 0
	bl	translate_rowlets
.LVL112:
.LBE75:
.LBE74:
	.loc 1 3796 0
	mov	r0, r7
	.syntax divided
@ 3796 "std_synapse.c" 1
	@
	
@ 0 "" 2
.LVL113:
	.loc 1 3797 0
	.arm
	.syntax divided
	bl	process_rowlets
.LVL114:
	.loc 1 3798 0
	mov	r5, r0
	.syntax divided
@ 3798 "std_synapse.c" 1
	@
	
@ 0 "" 2
.LVL115:
	.arm
	.syntax divided
.LBB76:
.LBB77:
	.loc 1 450 0
	mov	r0, r6
	bl	print_ring_buffer
.LVL116:
	.loc 1 451 0
	mov	r0, #1
	bl	print_ring_buffer
.LVL117:
.LBE77:
.LBE76:
	.loc 1 3803 0
	ldr	r2, [r4]
	ldr	r1, .L149+28
	mov	r0, #2
	bl	io_printf
.LVL118:
	.loc 1 3804 0
	sub	r2, r5, #4194304
	mov	r3, r7
	str	r5, [sp]
	mov	r2, r2, lsr #2
	ldr	r1, .L149+32
	mov	r0, #2
	bl	io_printf
.LVL119:
	.loc 1 3806 0
	mov	r0, #2
	ldr	r3, [r4, #16]
	ldr	r2, [r4, #12]
	ldr	r1, .L149+36
	.loc 1 3976 0
	add	sp, sp, #12
	.cfi_def_cfa_offset 20
	@ sp needed
	ldmfd	sp!, {r4, r5, r6, r7, lr}
	.cfi_restore 14
	.cfi_restore 7
	.cfi_restore 6
	.cfi_restore 5
	.cfi_restore 4
	.cfi_def_cfa_offset 0
.LVL120:
	.loc 1 3806 0
	b	io_printf
.LVL121:
.L150:
	.align	2
.L149:
	.word	.LC9
	.word	4202496
	.word	46137872
	.word	23085058
	.word	11546625
	.word	.LANCHOR0
	.word	.LANCHOR1
	.word	.LC13
	.word	.LC14
	.word	.LC15
	.cfi_endproc
.LFE247:
	.size	c_main, .-c_main
	.comm	circular_buffer_state,16,4
	.global	tmp
	.section	.rodata
	.align	2
	.set	.LANCHOR2,. + 0
	.type	__jump_table, %object
	.size	__jump_table, 128
__jump_table:
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	__reserved_dispatch
	.word	primary_dispatch_0I+28
	.word	primary_dispatch_0I
	.word	primary_dispatch_0E+28
	.word	primary_dispatch_0E
	.word	primary_dispatch_1I+28
	.word	primary_dispatch_1I
	.word	primary_dispatch_1E+28
	.word	primary_dispatch_1E
	.word	primary_dispatch_2I+28
	.word	primary_dispatch_2I
	.word	primary_dispatch_2E+28
	.word	primary_dispatch_2E
	.word	primary_dispatch_3I+28
	.word	primary_dispatch_3I
	.word	primary_dispatch_3E+28
	.word	primary_dispatch_3E
	.type	__log_size_to_burst, %object
	.size	__log_size_to_burst, 9
__log_size_to_burst:
	.byte	24
	.byte	24
	.byte	24
	.byte	24
	.byte	22
	.byte	20
	.byte	18
	.byte	16
	.byte	0
	.data
	.align	2
	.set	.LANCHOR1,. + 0
	.set	.LANCHOR3,. + 8184
	.type	tmp, %object
	.size	tmp, 5256
tmp:
	.word	24
	.word	0
	.word	14455693
	.word	14418738
	.word	14419116
	.word	14382343
	.word	14395018
	.word	14190260
	.word	14362616
	.word	14415690
	.word	14478185
	.word	14384091
	.word	14057019
	.word	14081924
	.word	14503702
	.word	14200921
	.word	14557445
	.word	14651899
	.word	14447324
	.word	14205654
	.word	14533506
	.word	14455794
	.word	14123980
	.word	14267739
	.word	14571275
	.word	14350113
	.word	30
	.word	0
	.word	14491946
	.word	14058470
	.word	14226195
	.word	14354062
	.word	14309332
	.word	14784451
	.word	14010353
	.word	14272718
	.word	14281472
	.word	14367522
	.word	14424959
	.word	14568686
	.word	14290184
	.word	14442487
	.word	14446837
	.word	14479461
	.word	14422436
	.word	14246566
	.word	14430940
	.word	14300117
	.word	14448071
	.word	14427439
	.word	14448247
	.word	14325296
	.word	14460766
	.word	14178743
	.word	14359112
	.word	14182928
	.word	14432902
	.word	14446647
	.word	21
	.word	0
	.word	14566071
	.word	14349715
	.word	14130058
	.word	14171413
	.word	14560917
	.word	14327901
	.word	14446676
	.word	14557584
	.word	14344619
	.word	14279360
	.word	14275278
	.word	14242371
	.word	14353305
	.word	14447562
	.word	14496940
	.word	14435592
	.word	14346121
	.word	14685974
	.word	14428289
	.word	14531740
	.word	14665454
	.word	25
	.word	0
	.word	14538922
	.word	14399941
	.word	14272994
	.word	14297889
	.word	14257235
	.word	14433549
	.word	14483249
	.word	14901462
	.word	14188671
	.word	14413936
	.word	14307752
	.word	14409994
	.word	14614955
	.word	14328840
	.word	14538038
	.word	14488862
	.word	14525998
	.word	14378573
	.word	14489178
	.word	14521928
	.word	14313467
	.word	14268438
	.word	14313690
	.word	14227877
	.word	14423957
	.word	14
	.word	0
	.word	-57160604
	.word	-58275246
	.word	-58365479
	.word	-56940776
	.word	-57083904
	.word	-57833932
	.word	-56764926
	.word	-57596215
	.word	-57838300
	.word	-57965125
	.word	-57789359
	.word	-57989902
	.word	-58153840
	.word	-57838695
	.word	13
	.word	0
	.word	14492479
	.word	14707146
	.word	14273662
	.word	14442658
	.word	14225597
	.word	14258354
	.word	14266670
	.word	14512757
	.word	14344840
	.word	14304505
	.word	14358427
	.word	14224147
	.word	14397205
	.word	9
	.word	0
	.word	14303927
	.word	14377869
	.word	14484891
	.word	13990341
	.word	14519047
	.word	14503007
	.word	14300696
	.word	14312973
	.word	14236532
	.word	19
	.word	0
	.word	14427658
	.word	14477604
	.word	14457488
	.word	13983208
	.word	14576937
	.word	14376275
	.word	14237274
	.word	14376636
	.word	14360093
	.word	14659513
	.word	14561236
	.word	14557346
	.word	14196851
	.word	14229959
	.word	14364992
	.word	14488606
	.word	14206470
	.word	14419689
	.word	14556186
	.word	13
	.word	0
	.word	14373427
	.word	14508579
	.word	14242671
	.word	14419602
	.word	14276966
	.word	14273166
	.word	14499023
	.word	14606000
	.word	14320446
	.word	14132322
	.word	14304739
	.word	14554663
	.word	14308339
	.word	1
	.word	0
	.word	532677712
	.word	23
	.word	0
	.word	14235586
	.word	14457006
	.word	14633659
	.word	14412770
	.word	14621776
	.word	14511114
	.word	14712182
	.word	14515768
	.word	14491416
	.word	14217363
	.word	14266483
	.word	14241982
	.word	14275058
	.word	14074815
	.word	14533840
	.word	14435500
	.word	14591311
	.word	14485031
	.word	14587421
	.word	14809338
	.word	14465610
	.word	14412654
	.word	14566321
	.word	9
	.word	0
	.word	14329251
	.word	14186779
	.word	14207690
	.word	14425999
	.word	14700698
	.word	14336612
	.word	14492214
	.word	14386358
	.word	14052092
	.word	6
	.word	0
	.word	14199130
	.word	14232118
	.word	14144898
	.word	14206474
	.word	14325264
	.word	14500728
	.word	7
	.word	0
	.word	14398134
	.word	14232453
	.word	14269339
	.word	14507811
	.word	14635254
	.word	14370293
	.word	14199154
	.word	24
	.word	0
	.word	14455693
	.word	14418738
	.word	14419116
	.word	14382343
	.word	14395018
	.word	14190260
	.word	14362616
	.word	14415690
	.word	14478185
	.word	14384091
	.word	14057019
	.word	14081924
	.word	14503702
	.word	14200921
	.word	14557445
	.word	14651899
	.word	14447324
	.word	14205654
	.word	14533506
	.word	14455794
	.word	14123980
	.word	14267739
	.word	14571275
	.word	14350113
	.word	30
	.word	0
	.word	14491946
	.word	14058470
	.word	14226195
	.word	14354062
	.word	14309332
	.word	14784451
	.word	14010353
	.word	14272718
	.word	14281472
	.word	14367522
	.word	14424959
	.word	14568686
	.word	14290184
	.word	14442487
	.word	14446837
	.word	14479461
	.word	14422436
	.word	14246566
	.word	14430940
	.word	14300117
	.word	14448071
	.word	14427439
	.word	14448247
	.word	14325296
	.word	14460766
	.word	14178743
	.word	14359112
	.word	14182928
	.word	14432902
	.word	14446647
	.word	21
	.word	0
	.word	14566071
	.word	14349715
	.word	14130058
	.word	14171413
	.word	14560917
	.word	14327901
	.word	14446676
	.word	14557584
	.word	14344619
	.word	14279360
	.word	14275278
	.word	14242371
	.word	14353305
	.word	14447562
	.word	14496940
	.word	14435592
	.word	14346121
	.word	14685974
	.word	14428289
	.word	14531740
	.word	14665454
	.word	25
	.word	0
	.word	14538922
	.word	14399941
	.word	14272994
	.word	14297889
	.word	14257235
	.word	14433549
	.word	14483249
	.word	14901462
	.word	14188671
	.word	14413936
	.word	14307752
	.word	14409994
	.word	14614955
	.word	14328840
	.word	14538038
	.word	14488862
	.word	14525998
	.word	14378573
	.word	14489178
	.word	14521928
	.word	14313467
	.word	14268438
	.word	14313690
	.word	14227877
	.word	14423957
	.word	14
	.word	0
	.word	-57160604
	.word	-58275246
	.word	-58365479
	.word	-56940776
	.word	-57083904
	.word	-57833932
	.word	-56764926
	.word	-57596215
	.word	-57838300
	.word	-57965125
	.word	-57789359
	.word	-57989902
	.word	-58153840
	.word	-57838695
	.word	13
	.word	0
	.word	14492479
	.word	14707146
	.word	14273662
	.word	14442658
	.word	14225597
	.word	14258354
	.word	14266670
	.word	14512757
	.word	14344840
	.word	14304505
	.word	14358427
	.word	14224147
	.word	14397205
	.word	9
	.word	0
	.word	14303927
	.word	14377869
	.word	14484891
	.word	13990341
	.word	14519047
	.word	14503007
	.word	14300696
	.word	14312973
	.word	14236532
	.word	19
	.word	0
	.word	14427658
	.word	14477604
	.word	14457488
	.word	13983208
	.word	14576937
	.word	14376275
	.word	14237274
	.word	14376636
	.word	14360093
	.word	14659513
	.word	14561236
	.word	14557346
	.word	14196851
	.word	14229959
	.word	14364992
	.word	14488606
	.word	14206470
	.word	14419689
	.word	14556186
	.word	13
	.word	0
	.word	14373427
	.word	14508579
	.word	14242671
	.word	14419602
	.word	14276966
	.word	14273166
	.word	14499023
	.word	14606000
	.word	14320446
	.word	14132322
	.word	14304739
	.word	14554663
	.word	14308339
	.word	1
	.word	0
	.word	532677712
	.word	23
	.word	0
	.word	14235586
	.word	14457006
	.word	14633659
	.word	14412770
	.word	14621776
	.word	14511114
	.word	14712182
	.word	14515768
	.word	14491416
	.word	14217363
	.word	14266483
	.word	14241982
	.word	14275058
	.word	14074815
	.word	14533840
	.word	14435500
	.word	14591311
	.word	14485031
	.word	14587421
	.word	14809338
	.word	14465610
	.word	14412654
	.word	14566321
	.word	9
	.word	0
	.word	14329251
	.word	14186779
	.word	14207690
	.word	14425999
	.word	14700698
	.word	14336612
	.word	14492214
	.word	14386358
	.word	14052092
	.word	6
	.word	0
	.word	14199130
	.word	14232118
	.word	14144898
	.word	14206474
	.word	14325264
	.word	14500728
	.word	7
	.word	0
	.word	14398134
	.word	14232453
	.word	14269339
	.word	14507811
	.word	14635254
	.word	14370293
	.word	14199154
	.word	24
	.word	0
	.word	14455693
	.word	14418738
	.word	14419116
	.word	14382343
	.word	14395018
	.word	14190260
	.word	14362616
	.word	14415690
	.word	14478185
	.word	14384091
	.word	14057019
	.word	14081924
	.word	14503702
	.word	14200921
	.word	14557445
	.word	14651899
	.word	14447324
	.word	14205654
	.word	14533506
	.word	14455794
	.word	14123980
	.word	14267739
	.word	14571275
	.word	14350113
	.word	30
	.word	0
	.word	14491946
	.word	14058470
	.word	14226195
	.word	14354062
	.word	14309332
	.word	14784451
	.word	14010353
	.word	14272718
	.word	14281472
	.word	14367522
	.word	14424959
	.word	14568686
	.word	14290184
	.word	14442487
	.word	14446837
	.word	14479461
	.word	14422436
	.word	14246566
	.word	14430940
	.word	14300117
	.word	14448071
	.word	14427439
	.word	14448247
	.word	14325296
	.word	14460766
	.word	14178743
	.word	14359112
	.word	14182928
	.word	14432902
	.word	14446647
	.word	21
	.word	0
	.word	14566071
	.word	14349715
	.word	14130058
	.word	14171413
	.word	14560917
	.word	14327901
	.word	14446676
	.word	14557584
	.word	14344619
	.word	14279360
	.word	14275278
	.word	14242371
	.word	14353305
	.word	14447562
	.word	14496940
	.word	14435592
	.word	14346121
	.word	14685974
	.word	14428289
	.word	14531740
	.word	14665454
	.word	25
	.word	0
	.word	14538922
	.word	14399941
	.word	14272994
	.word	14297889
	.word	14257235
	.word	14433549
	.word	14483249
	.word	14901462
	.word	14188671
	.word	14413936
	.word	14307752
	.word	14409994
	.word	14614955
	.word	14328840
	.word	14538038
	.word	14488862
	.word	14525998
	.word	14378573
	.word	14489178
	.word	14521928
	.word	14313467
	.word	14268438
	.word	14313690
	.word	14227877
	.word	14423957
	.word	14
	.word	0
	.word	-57160604
	.word	-58275246
	.word	-58365479
	.word	-56940776
	.word	-57083904
	.word	-57833932
	.word	-56764926
	.word	-57596215
	.word	-57838300
	.word	-57965125
	.word	-57789359
	.word	-57989902
	.word	-58153840
	.word	-57838695
	.word	13
	.word	0
	.word	14492479
	.word	14707146
	.word	14273662
	.word	14442658
	.word	14225597
	.word	14258354
	.word	14266670
	.word	14512757
	.word	14344840
	.word	14304505
	.word	14358427
	.word	14224147
	.word	14397205
	.word	9
	.word	0
	.word	14303927
	.word	14377869
	.word	14484891
	.word	13990341
	.word	14519047
	.word	14503007
	.word	14300696
	.word	14312973
	.word	14236532
	.word	19
	.word	0
	.word	14427658
	.word	14477604
	.word	14457488
	.word	13983208
	.word	14576937
	.word	14376275
	.word	14237274
	.word	14376636
	.word	14360093
	.word	14659513
	.word	14561236
	.word	14557346
	.word	14196851
	.word	14229959
	.word	14364992
	.word	14488606
	.word	14206470
	.word	14419689
	.word	14556186
	.word	13
	.word	0
	.word	14373427
	.word	14508579
	.word	14242671
	.word	14419602
	.word	14276966
	.word	14273166
	.word	14499023
	.word	14606000
	.word	14320446
	.word	14132322
	.word	14304739
	.word	14554663
	.word	14308339
	.word	1
	.word	0
	.word	532677712
	.word	23
	.word	0
	.word	14235586
	.word	14457006
	.word	14633659
	.word	14412770
	.word	14621776
	.word	14511114
	.word	14712182
	.word	14515768
	.word	14491416
	.word	14217363
	.word	14266483
	.word	14241982
	.word	14275058
	.word	14074815
	.word	14533840
	.word	14435500
	.word	14591311
	.word	14485031
	.word	14587421
	.word	14809338
	.word	14465610
	.word	14412654
	.word	14566321
	.word	9
	.word	0
	.word	14329251
	.word	14186779
	.word	14207690
	.word	14425999
	.word	14700698
	.word	14336612
	.word	14492214
	.word	14386358
	.word	14052092
	.word	6
	.word	0
	.word	14199130
	.word	14232118
	.word	14144898
	.word	14206474
	.word	14325264
	.word	14500728
	.word	7
	.word	0
	.word	14398134
	.word	14232453
	.word	14269339
	.word	14507811
	.word	14635254
	.word	14370293
	.word	14199154
	.word	24
	.word	0
	.word	14455693
	.word	14418738
	.word	14419116
	.word	14382343
	.word	14395018
	.word	14190260
	.word	14362616
	.word	14415690
	.word	14478185
	.word	14384091
	.word	14057019
	.word	14081924
	.word	14503702
	.word	14200921
	.word	14557445
	.word	14651899
	.word	14447324
	.word	14205654
	.word	14533506
	.word	14455794
	.word	14123980
	.word	14267739
	.word	14571275
	.word	14350113
	.word	30
	.word	0
	.word	14491946
	.word	14058470
	.word	14226195
	.word	14354062
	.word	14309332
	.word	14784451
	.word	14010353
	.word	14272718
	.word	14281472
	.word	14367522
	.word	14424959
	.word	14568686
	.word	14290184
	.word	14442487
	.word	14446837
	.word	14479461
	.word	14422436
	.word	14246566
	.word	14430940
	.word	14300117
	.word	14448071
	.word	14427439
	.word	14448247
	.word	14325296
	.word	14460766
	.word	14178743
	.word	14359112
	.word	14182928
	.word	14432902
	.word	14446647
	.word	21
	.word	0
	.word	14566071
	.word	14349715
	.word	14130058
	.word	14171413
	.word	14560917
	.word	14327901
	.word	14446676
	.word	14557584
	.word	14344619
	.word	14279360
	.word	14275278
	.word	14242371
	.word	14353305
	.word	14447562
	.word	14496940
	.word	14435592
	.word	14346121
	.word	14685974
	.word	14428289
	.word	14531740
	.word	14665454
	.word	25
	.word	0
	.word	14538922
	.word	14399941
	.word	14272994
	.word	14297889
	.word	14257235
	.word	14433549
	.word	14483249
	.word	14901462
	.word	14188671
	.word	14413936
	.word	14307752
	.word	14409994
	.word	14614955
	.word	14328840
	.word	14538038
	.word	14488862
	.word	14525998
	.word	14378573
	.word	14489178
	.word	14521928
	.word	14313467
	.word	14268438
	.word	14313690
	.word	14227877
	.word	14423957
	.word	14
	.word	0
	.word	-57160604
	.word	-58275246
	.word	-58365479
	.word	-56940776
	.word	-57083904
	.word	-57833932
	.word	-56764926
	.word	-57596215
	.word	-57838300
	.word	-57965125
	.word	-57789359
	.word	-57989902
	.word	-58153840
	.word	-57838695
	.word	13
	.word	0
	.word	14492479
	.word	14707146
	.word	14273662
	.word	14442658
	.word	14225597
	.word	14258354
	.word	14266670
	.word	14512757
	.word	14344840
	.word	14304505
	.word	14358427
	.word	14224147
	.word	14397205
	.word	9
	.word	0
	.word	14303927
	.word	14377869
	.word	14484891
	.word	13990341
	.word	14519047
	.word	14503007
	.word	14300696
	.word	14312973
	.word	14236532
	.word	19
	.word	0
	.word	14427658
	.word	14477604
	.word	14457488
	.word	13983208
	.word	14576937
	.word	14376275
	.word	14237274
	.word	14376636
	.word	14360093
	.word	14659513
	.word	14561236
	.word	14557346
	.word	14196851
	.word	14229959
	.word	14364992
	.word	14488606
	.word	14206470
	.word	14419689
	.word	14556186
	.word	13
	.word	0
	.word	14373427
	.word	14508579
	.word	14242671
	.word	14419602
	.word	14276966
	.word	14273166
	.word	14499023
	.word	14606000
	.word	14320446
	.word	14132322
	.word	14304739
	.word	14554663
	.word	14308339
	.word	1
	.word	0
	.word	532677712
	.word	23
	.word	0
	.word	14235586
	.word	14457006
	.word	14633659
	.word	14412770
	.word	14621776
	.word	14511114
	.word	14712182
	.word	14515768
	.word	14491416
	.word	14217363
	.word	14266483
	.word	14241982
	.word	14275058
	.word	14074815
	.word	14533840
	.word	14435500
	.word	14591311
	.word	14485031
	.word	14587421
	.word	14809338
	.word	14465610
	.word	14412654
	.word	14566321
	.word	9
	.word	0
	.word	14329251
	.word	14186779
	.word	14207690
	.word	14425999
	.word	14700698
	.word	14336612
	.word	14492214
	.word	14386358
	.word	14052092
	.word	6
	.word	0
	.word	14199130
	.word	14232118
	.word	14144898
	.word	14206474
	.word	14325264
	.word	14500728
	.word	7
	.word	0
	.word	14398134
	.word	14232453
	.word	14269339
	.word	14507811
	.word	14635254
	.word	14370293
	.word	14199154
	.word	24
	.word	0
	.word	14455693
	.word	14418738
	.word	14419116
	.word	14382343
	.word	14395018
	.word	14190260
	.word	14362616
	.word	14415690
	.word	14478185
	.word	14384091
	.word	14057019
	.word	14081924
	.word	14503702
	.word	14200921
	.word	14557445
	.word	14651899
	.word	14447324
	.word	14205654
	.word	14533506
	.word	14455794
	.word	14123980
	.word	14267739
	.word	14571275
	.word	14350113
	.word	30
	.word	0
	.word	14491946
	.word	14058470
	.word	14226195
	.word	14354062
	.word	14309332
	.word	14784451
	.word	14010353
	.word	14272718
	.word	14281472
	.word	14367522
	.word	14424959
	.word	14568686
	.word	14290184
	.word	14442487
	.word	14446837
	.word	14479461
	.word	14422436
	.word	14246566
	.word	14430940
	.word	14300117
	.word	14448071
	.word	14427439
	.word	14448247
	.word	14325296
	.word	14460766
	.word	14178743
	.word	14359112
	.word	14182928
	.word	14432902
	.word	14446647
	.word	21
	.word	0
	.word	14566071
	.word	14349715
	.word	14130058
	.word	14171413
	.word	14560917
	.word	14327901
	.word	14446676
	.word	14557584
	.word	14344619
	.word	14279360
	.word	14275278
	.word	14242371
	.word	14353305
	.word	14447562
	.word	14496940
	.word	14435592
	.word	14346121
	.word	14685974
	.word	14428289
	.word	14531740
	.word	14665454
	.word	25
	.word	0
	.word	14538922
	.word	14399941
	.word	14272994
	.word	14297889
	.word	14257235
	.word	14433549
	.word	14483249
	.word	14901462
	.word	14188671
	.word	14413936
	.word	14307752
	.word	14409994
	.word	14614955
	.word	14328840
	.word	14538038
	.word	14488862
	.word	14525998
	.word	14378573
	.word	14489178
	.word	14521928
	.word	14313467
	.word	14268438
	.word	14313690
	.word	14227877
	.word	14423957
	.word	14
	.word	0
	.word	-57160604
	.word	-58275246
	.word	-58365479
	.word	-56940776
	.word	-57083904
	.word	-57833932
	.word	-56764926
	.word	-57596215
	.word	-57838300
	.word	-57965125
	.word	-57789359
	.word	-57989902
	.word	-58153840
	.word	-57838695
	.word	13
	.word	0
	.word	14492479
	.word	14707146
	.word	14273662
	.word	14442658
	.word	14225597
	.word	14258354
	.word	14266670
	.word	14512757
	.word	14344840
	.word	14304505
	.word	14358427
	.word	14224147
	.word	14397205
	.word	9
	.word	0
	.word	14303927
	.word	14377869
	.word	14484891
	.word	13990341
	.word	14519047
	.word	14503007
	.word	14300696
	.word	14312973
	.word	14236532
	.word	19
	.word	0
	.word	14427658
	.word	14477604
	.word	14457488
	.word	13983208
	.word	14576937
	.word	14376275
	.word	14237274
	.word	14376636
	.word	14360093
	.word	14659513
	.word	14561236
	.word	14557346
	.word	14196851
	.word	14229959
	.word	14364992
	.word	14488606
	.word	14206470
	.word	14419689
	.word	14556186
	.word	13
	.word	0
	.word	14373427
	.word	14508579
	.word	14242671
	.word	14419602
	.word	14276966
	.word	14273166
	.word	14499023
	.word	14606000
	.word	14320446
	.word	14132322
	.word	14304739
	.word	14554663
	.word	14308339
	.word	1
	.word	0
	.word	532677712
	.word	23
	.word	0
	.word	14235586
	.word	14457006
	.word	14633659
	.word	14412770
	.word	14621776
	.word	14511114
	.word	14712182
	.word	14515768
	.word	14491416
	.word	14217363
	.word	14266483
	.word	14241982
	.word	14275058
	.word	14074815
	.word	14533840
	.word	14435500
	.word	14591311
	.word	14485031
	.word	14587421
	.word	14809338
	.word	14465610
	.word	14412654
	.word	14566321
	.word	9
	.word	0
	.word	14329251
	.word	14186779
	.word	14207690
	.word	14425999
	.word	14700698
	.word	14336612
	.word	14492214
	.word	14386358
	.word	14052092
	.word	6
	.word	0
	.word	14199130
	.word	14232118
	.word	14144898
	.word	14206474
	.word	14325264
	.word	14500728
	.word	7
	.word	0
	.word	14398134
	.word	14232453
	.word	14269339
	.word	14507811
	.word	14635254
	.word	14370293
	.word	14199154
	.word	101
	.word	0
	.word	-56570339
	.word	-57360891
	.word	-57340220
	.word	-57618751
	.word	-57921994
	.word	-57139459
	.word	-58061066
	.word	-57950769
	.word	-56775403
	.word	-57745938
	.word	-57782812
	.word	-58688247
	.word	-57340423
	.word	-56521476
	.word	-56972116
	.word	-58381118
	.word	-57434961
	.word	-57996460
	.word	-56710359
	.word	-57328836
	.word	-56181838
	.word	-57070705
	.word	-56669184
	.word	-56460465
	.word	-57021944
	.word	-57673140
	.word	-56387006
	.word	-57591198
	.word	-57943427
	.word	-57030024
	.word	-57087497
	.word	-58349164
	.word	-57755377
	.word	-58123945
	.word	-56645267
	.word	-56866465
	.word	-57353982
	.word	-57345770
	.word	-58206035
	.word	-57354022
	.word	-56833996
	.word	-57517952
	.word	-58640349
	.word	-57202445
	.word	-58095446
	.word	-57816858
	.word	-57710377
	.word	-57513833
	.word	-57821088
	.word	-56518876
	.word	-57600194
	.word	-57530495
	.word	-57551033
	.word	-57997406
	.word	-57153639
	.word	-57448592
	.word	-57444596
	.word	-57628825
	.word	-57251964
	.word	-56682735
	.word	-57575911
	.word	-57981390
	.word	-58042852
	.word	-57723245
	.word	-57653610
	.word	-57903393
	.word	-57440767
	.word	-56310031
	.word	-57301696
	.word	-57530960
	.word	-57735799
	.word	-57399931
	.word	-57838253
	.word	-57735778
	.word	-58042915
	.word	-58059665
	.word	-57461556
	.word	-57953149
	.word	-57338658
	.word	-57531218
	.word	-56683560
	.word	-57326731
	.word	-57105459
	.word	-57789662
	.word	-57334991
	.word	-57855141
	.word	-57576465
	.word	-56577215
	.word	-57396613
	.word	-56306981
	.word	-58555758
	.word	-57454027
	.word	-58273207
	.word	-57839305
	.word	-57700064
	.word	-56995509
	.word	-57110406
	.word	-58437629
	.word	-56865051
	.word	-57385537
	.word	-59327662
	.word	0
	.type	__control_synapse, %object
	.size	__control_synapse, 252
__control_synapse:
	.word	__synapse_loop+108
	.word	__synapse_loop+216
	.word	__synapse_loop+324
	.word	__synapse_loop
	.word	__synapse_loop+108
	.word	__synapse_loop+216
	.word	__synapse_loop+324
	.word	__synapse_loop
	.word	__synapse_loop+108
	.word	__synapse_loop+216
	.word	__synapse_loop+324
	.word	__synapse_loop
	.word	__synapse_loop+108
	.word	__synapse_loop+216
	.word	__synapse_loop+324
	.word	__synapse_loop
	.word	__synapse_loop+108
	.word	__synapse_loop+216
	.word	__synapse_loop+324
	.word	__synapse_loop
	.word	__synapse_loop+108
	.word	__synapse_loop+216
	.word	__synapse_loop+324
	.word	__synapse_loop
	.word	__synapse_loop+108
	.word	__synapse_loop+216
	.word	__synapse_loop+324
	.word	__synapse_loop
	.word	__synapse_loop+108
	.word	__synapse_loop+216
	.word	__synapse_loop+324
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	4200448
	.word	0
	.word	0
	.word	524292
	.word	25165824
	.word	4194304
	.word	4202496
	.word	__log_size_to_burst-21
	.word	1619001344
	.word	0
	.word	0
	.word	__jump_table+64
	.word	510
	.section	.rodata.str1.4,"aMS",%progbits,1
	.align	2
.LC0:
	.ascii	" DEBUG: %08x\012\000"
	.space	2
.LC1:
	.ascii	"ring_buffer%1u [%d, %u] = %u\012\000"
	.space	2
.LC2:
	.ascii	"    {%08x, \000"
.LC3:
	.ascii	"%08x, \000"
	.space	1
.LC4:
	.ascii	"%08x}\012\000"
	.space	1
.LC5:
	.ascii	"%08x:\012---------\012\000"
	.space	3
.LC6:
	.ascii	"    %08x\012\000"
	.space	2
.LC7:
	.ascii	"Primary Dispatch Table\012======================\012"
	.ascii	"\012\000"
.LC8:
	.ascii	"[%08x] Q %c 0; S %u; %c\012\000"
	.space	3
.LC9:
	.ascii	"Secondry Dispatch Table\012=======================\012"
	.ascii	"\012\000"
	.space	2
.LC10:
	.ascii	"\012quad jump table\012===============\012\000"
	.space	2
.LC11:
	.ascii	"[%08x] n = %d\012\000"
	.space	1
.LC12:
	.ascii	"\012\012\000"
	.space	1
.LC13:
	.ascii	"Total time taken to process rowlet buffer is: = %u "
	.ascii	"cycles\012\000"
	.space	1
.LC14:
	.ascii	"The number of words processed is: %u (initial %08x,"
	.ascii	" final: %08x)\012\000"
	.space	2
.LC15:
	.ascii	"The number of synapses is %u, the number of rowlets"
	.ascii	" is: %u\012\000"
	.bss
	.align	2
	.set	.LANCHOR0,. + 0
	.type	time, %object
	.size	time, 4
time:
	.space	4
	.type	__ip__, %object
	.size	__ip__, 4
__ip__:
	.space	4
	.type	__op__, %object
	.size	__op__, 4
__op__:
	.space	4
	.type	__synapses, %object
	.size	__synapses, 4
__synapses:
	.space	4
	.type	__rowlets, %object
	.size	__rowlets, 4
__rowlets:
	.space	4
	.text
.Letext0:
	.file 2 "/Users/mbassdrl/opt/gcc-arm-none-eabi-5_4-2016q3/lib/gcc/arm-none-eabi/5.4.1/include/stdint-gcc.h"
	.file 3 "/Users/mbassdrl/Github/SpiNNaker/spinnaker_tools/include/spinnaker.h"
	.file 4 "/Users/mbassdrl/Github/SpiNNaker/spinnaker_tools/include/sark.h"
	.section	.debug_info,"",%progbits
.Ldebug_info0:
	.4byte	0x2453
	.2byte	0x4
	.4byte	.Ldebug_abbrev0
	.byte	0x4
	.uleb128 0x1
	.4byte	.LASF290
	.byte	0xc
	.4byte	.LASF291
	.4byte	.LASF292
	.4byte	.Ltext0
	.4byte	.Letext0-.Ltext0
	.4byte	.Ldebug_line0
	.uleb128 0x2
	.byte	0x1
	.byte	0x6
	.4byte	.LASF0
	.uleb128 0x2
	.byte	0x2
	.byte	0x5
	.4byte	.LASF1
	.uleb128 0x2
	.byte	0x4
	.byte	0x5
	.4byte	.LASF2
	.uleb128 0x2
	.byte	0x8
	.byte	0x5
	.4byte	.LASF3
	.uleb128 0x3
	.4byte	.LASF5
	.byte	0x2
	.byte	0x2e
	.4byte	0x4c
	.uleb128 0x2
	.byte	0x1
	.byte	0x8
	.4byte	.LASF4
	.uleb128 0x3
	.4byte	.LASF6
	.byte	0x2
	.byte	0x31
	.4byte	0x5e
	.uleb128 0x2
	.byte	0x2
	.byte	0x7
	.4byte	.LASF7
	.uleb128 0x3
	.4byte	.LASF8
	.byte	0x2
	.byte	0x34
	.4byte	0x70
	.uleb128 0x2
	.byte	0x4
	.byte	0x7
	.4byte	.LASF9
	.uleb128 0x3
	.4byte	.LASF10
	.byte	0x2
	.byte	0x37
	.4byte	0x82
	.uleb128 0x2
	.byte	0x8
	.byte	0x7
	.4byte	.LASF11
	.uleb128 0x4
	.byte	0x4
	.byte	0x5
	.ascii	"int\000"
	.uleb128 0x2
	.byte	0x4
	.byte	0x7
	.4byte	.LASF12
	.uleb128 0x3
	.4byte	.LASF13
	.byte	0x3
	.byte	0x13
	.4byte	0x4c
	.uleb128 0x3
	.4byte	.LASF14
	.byte	0x3
	.byte	0x14
	.4byte	0x5e
	.uleb128 0x3
	.4byte	.LASF15
	.byte	0x3
	.byte	0x15
	.4byte	0x90
	.uleb128 0x3
	.4byte	.LASF16
	.byte	0x3
	.byte	0x16
	.4byte	0x82
	.uleb128 0x3
	.4byte	.LASF17
	.byte	0x4
	.byte	0x3a
	.4byte	0xce
	.uleb128 0x5
	.byte	0x4
	.4byte	0xd4
	.uleb128 0x6
	.uleb128 0x7
	.4byte	.LASF19
	.byte	0x4
	.byte	0x4
	.2byte	0x1e0
	.4byte	0xf0
	.uleb128 0x8
	.4byte	.LASF21
	.byte	0x4
	.2byte	0x1e1
	.4byte	0xf0
	.byte	0
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0xd5
	.uleb128 0x9
	.4byte	.LASF18
	.byte	0x4
	.2byte	0x1e2
	.4byte	0xd5
	.uleb128 0x7
	.4byte	.LASF20
	.byte	0x8
	.byte	0x4
	.2byte	0x1e8
	.4byte	0x137
	.uleb128 0x8
	.4byte	.LASF22
	.byte	0x4
	.2byte	0x1e9
	.4byte	0x137
	.byte	0
	.uleb128 0x8
	.4byte	.LASF23
	.byte	0x4
	.2byte	0x1ea
	.4byte	0xa2
	.byte	0x4
	.uleb128 0xa
	.ascii	"max\000"
	.byte	0x4
	.2byte	0x1eb
	.4byte	0xa2
	.byte	0x6
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0xf6
	.uleb128 0x9
	.4byte	.LASF24
	.byte	0x4
	.2byte	0x1ec
	.4byte	0x102
	.uleb128 0x2
	.byte	0x4
	.byte	0x7
	.4byte	.LASF25
	.uleb128 0xb
	.4byte	0x97
	.4byte	0x160
	.uleb128 0xc
	.4byte	0x149
	.byte	0x3
	.byte	0
	.uleb128 0x7
	.4byte	.LASF26
	.byte	0x10
	.byte	0x4
	.2byte	0x203
	.4byte	0x1af
	.uleb128 0x8
	.4byte	.LASF21
	.byte	0x4
	.2byte	0x204
	.4byte	0xa2
	.byte	0
	.uleb128 0x8
	.4byte	.LASF22
	.byte	0x4
	.2byte	0x205
	.4byte	0xa2
	.byte	0x2
	.uleb128 0x8
	.4byte	.LASF27
	.byte	0x4
	.2byte	0x206
	.4byte	0xad
	.byte	0x4
	.uleb128 0xa
	.ascii	"key\000"
	.byte	0x4
	.2byte	0x207
	.4byte	0xad
	.byte	0x8
	.uleb128 0x8
	.4byte	.LASF28
	.byte	0x4
	.2byte	0x208
	.4byte	0xad
	.byte	0xc
	.byte	0
	.uleb128 0x9
	.4byte	.LASF29
	.byte	0x4
	.2byte	0x209
	.4byte	0x160
	.uleb128 0x7
	.4byte	.LASF30
	.byte	0x8
	.byte	0x4
	.2byte	0x210
	.4byte	0x20a
	.uleb128 0x8
	.4byte	.LASF31
	.byte	0x4
	.2byte	0x211
	.4byte	0x97
	.byte	0
	.uleb128 0x8
	.4byte	.LASF32
	.byte	0x4
	.2byte	0x212
	.4byte	0x97
	.byte	0x1
	.uleb128 0x8
	.4byte	.LASF33
	.byte	0x4
	.2byte	0x213
	.4byte	0x97
	.byte	0x2
	.uleb128 0x8
	.4byte	.LASF34
	.byte	0x4
	.2byte	0x214
	.4byte	0x97
	.byte	0x3
	.uleb128 0x8
	.4byte	.LASF28
	.byte	0x4
	.2byte	0x215
	.4byte	0xad
	.byte	0x4
	.byte	0
	.uleb128 0x9
	.4byte	.LASF35
	.byte	0x4
	.2byte	0x216
	.4byte	0x1bb
	.uleb128 0xd
	.4byte	.LASF36
	.2byte	0x124
	.byte	0x4
	.2byte	0x22d
	.4byte	0x2f6
	.uleb128 0x8
	.4byte	.LASF21
	.byte	0x4
	.2byte	0x22e
	.4byte	0x2f6
	.byte	0
	.uleb128 0x8
	.4byte	.LASF37
	.byte	0x4
	.2byte	0x22f
	.4byte	0xa2
	.byte	0x4
	.uleb128 0x8
	.4byte	.LASF38
	.byte	0x4
	.2byte	0x230
	.4byte	0xa2
	.byte	0x6
	.uleb128 0x8
	.4byte	.LASF39
	.byte	0x4
	.2byte	0x234
	.4byte	0x97
	.byte	0x8
	.uleb128 0xa
	.ascii	"tag\000"
	.byte	0x4
	.2byte	0x235
	.4byte	0x97
	.byte	0x9
	.uleb128 0x8
	.4byte	.LASF40
	.byte	0x4
	.2byte	0x236
	.4byte	0x97
	.byte	0xa
	.uleb128 0x8
	.4byte	.LASF41
	.byte	0x4
	.2byte	0x237
	.4byte	0x97
	.byte	0xb
	.uleb128 0x8
	.4byte	.LASF42
	.byte	0x4
	.2byte	0x238
	.4byte	0xa2
	.byte	0xc
	.uleb128 0x8
	.4byte	.LASF43
	.byte	0x4
	.2byte	0x239
	.4byte	0xa2
	.byte	0xe
	.uleb128 0x8
	.4byte	.LASF44
	.byte	0x4
	.2byte	0x23d
	.4byte	0xa2
	.byte	0x10
	.uleb128 0xa
	.ascii	"seq\000"
	.byte	0x4
	.2byte	0x23e
	.4byte	0xa2
	.byte	0x12
	.uleb128 0x8
	.4byte	.LASF45
	.byte	0x4
	.2byte	0x23f
	.4byte	0xad
	.byte	0x14
	.uleb128 0x8
	.4byte	.LASF46
	.byte	0x4
	.2byte	0x240
	.4byte	0xad
	.byte	0x18
	.uleb128 0x8
	.4byte	.LASF47
	.byte	0x4
	.2byte	0x241
	.4byte	0xad
	.byte	0x1c
	.uleb128 0x8
	.4byte	.LASF48
	.byte	0x4
	.2byte	0x245
	.4byte	0x2fc
	.byte	0x20
	.uleb128 0xe
	.4byte	.LASF49
	.byte	0x4
	.2byte	0x247
	.4byte	0xad
	.2byte	0x120
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0x216
	.uleb128 0xb
	.4byte	0x97
	.4byte	0x30c
	.uleb128 0xc
	.4byte	0x149
	.byte	0xff
	.byte	0
	.uleb128 0x9
	.4byte	.LASF50
	.byte	0x4
	.2byte	0x248
	.4byte	0x216
	.uleb128 0x7
	.4byte	.LASF51
	.byte	0x8
	.byte	0x4
	.2byte	0x268
	.4byte	0x340
	.uleb128 0x8
	.4byte	.LASF21
	.byte	0x4
	.2byte	0x269
	.4byte	0x340
	.byte	0
	.uleb128 0x8
	.4byte	.LASF22
	.byte	0x4
	.2byte	0x26a
	.4byte	0x340
	.byte	0x4
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0x318
	.uleb128 0x9
	.4byte	.LASF52
	.byte	0x4
	.2byte	0x26b
	.4byte	0x318
	.uleb128 0xf
	.byte	0x10
	.byte	0x4
	.2byte	0x275
	.4byte	0x39d
	.uleb128 0x8
	.4byte	.LASF22
	.byte	0x4
	.2byte	0x276
	.4byte	0x39d
	.byte	0
	.uleb128 0x8
	.4byte	.LASF53
	.byte	0x4
	.2byte	0x277
	.4byte	0x39d
	.byte	0x4
	.uleb128 0x8
	.4byte	.LASF54
	.byte	0x4
	.2byte	0x278
	.4byte	0x39d
	.byte	0x8
	.uleb128 0x8
	.4byte	.LASF55
	.byte	0x4
	.2byte	0x279
	.4byte	0xad
	.byte	0xc
	.uleb128 0x8
	.4byte	.LASF56
	.byte	0x4
	.2byte	0x27a
	.4byte	0x3a3
	.byte	0x10
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0x346
	.uleb128 0xb
	.4byte	0x97
	.4byte	0x3b2
	.uleb128 0x10
	.4byte	0x149
	.byte	0
	.uleb128 0x9
	.4byte	.LASF57
	.byte	0x4
	.2byte	0x27b
	.4byte	0x352
	.uleb128 0x7
	.4byte	.LASF58
	.byte	0x4
	.byte	0x4
	.2byte	0x289
	.4byte	0x3f3
	.uleb128 0x8
	.4byte	.LASF59
	.byte	0x4
	.2byte	0x28a
	.4byte	0xa2
	.byte	0
	.uleb128 0x8
	.4byte	.LASF60
	.byte	0x4
	.2byte	0x28b
	.4byte	0x97
	.byte	0x2
	.uleb128 0x8
	.4byte	.LASF61
	.byte	0x4
	.2byte	0x28c
	.4byte	0x97
	.byte	0x3
	.byte	0
	.uleb128 0x9
	.4byte	.LASF62
	.byte	0x4
	.2byte	0x28d
	.4byte	0x3be
	.uleb128 0x7
	.4byte	.LASF63
	.byte	0x58
	.byte	0x4
	.2byte	0x296
	.4byte	0x545
	.uleb128 0x8
	.4byte	.LASF64
	.byte	0x4
	.2byte	0x297
	.4byte	0xc3
	.byte	0
	.uleb128 0x8
	.4byte	.LASF65
	.byte	0x4
	.2byte	0x298
	.4byte	0xc3
	.byte	0x4
	.uleb128 0x8
	.4byte	.LASF66
	.byte	0x4
	.2byte	0x299
	.4byte	0xc3
	.byte	0x8
	.uleb128 0x8
	.4byte	.LASF67
	.byte	0x4
	.2byte	0x29a
	.4byte	0xc3
	.byte	0xc
	.uleb128 0x8
	.4byte	.LASF68
	.byte	0x4
	.2byte	0x29b
	.4byte	0xc3
	.byte	0x10
	.uleb128 0x8
	.4byte	.LASF69
	.byte	0x4
	.2byte	0x29c
	.4byte	0xc3
	.byte	0x14
	.uleb128 0x8
	.4byte	.LASF70
	.byte	0x4
	.2byte	0x29d
	.4byte	0xc3
	.byte	0x18
	.uleb128 0x8
	.4byte	.LASF71
	.byte	0x4
	.2byte	0x29e
	.4byte	0xc3
	.byte	0x1c
	.uleb128 0x8
	.4byte	.LASF72
	.byte	0x4
	.2byte	0x2a0
	.4byte	0xa2
	.byte	0x20
	.uleb128 0x8
	.4byte	.LASF73
	.byte	0x4
	.2byte	0x2a1
	.4byte	0xa2
	.byte	0x22
	.uleb128 0x8
	.4byte	.LASF74
	.byte	0x4
	.2byte	0x2a2
	.4byte	0xa2
	.byte	0x24
	.uleb128 0x8
	.4byte	.LASF75
	.byte	0x4
	.2byte	0x2a3
	.4byte	0xa2
	.byte	0x26
	.uleb128 0x8
	.4byte	.LASF76
	.byte	0x4
	.2byte	0x2a5
	.4byte	0x545
	.byte	0x28
	.uleb128 0x8
	.4byte	.LASF77
	.byte	0x4
	.2byte	0x2a6
	.4byte	0x545
	.byte	0x2c
	.uleb128 0x8
	.4byte	.LASF78
	.byte	0x4
	.2byte	0x2a7
	.4byte	0x545
	.byte	0x30
	.uleb128 0x8
	.4byte	.LASF79
	.byte	0x4
	.2byte	0x2a9
	.4byte	0xad
	.byte	0x34
	.uleb128 0x8
	.4byte	.LASF80
	.byte	0x4
	.2byte	0x2ab
	.4byte	0x97
	.byte	0x38
	.uleb128 0x8
	.4byte	.LASF81
	.byte	0x4
	.2byte	0x2ac
	.4byte	0x97
	.byte	0x39
	.uleb128 0x8
	.4byte	.LASF82
	.byte	0x4
	.2byte	0x2ae
	.4byte	0x97
	.byte	0x3a
	.uleb128 0xa
	.ascii	"api\000"
	.byte	0x4
	.2byte	0x2af
	.4byte	0x97
	.byte	0x3b
	.uleb128 0x8
	.4byte	.LASF83
	.byte	0x4
	.2byte	0x2b0
	.4byte	0x97
	.byte	0x3c
	.uleb128 0x8
	.4byte	.LASF84
	.byte	0x4
	.2byte	0x2b1
	.4byte	0x54b
	.byte	0x3d
	.uleb128 0x8
	.4byte	.LASF85
	.byte	0x4
	.2byte	0x2b2
	.4byte	0xa2
	.byte	0x3e
	.uleb128 0x8
	.4byte	.LASF86
	.byte	0x4
	.2byte	0x2b4
	.4byte	0x550
	.byte	0x40
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0xad
	.uleb128 0x11
	.4byte	0x97
	.uleb128 0xb
	.4byte	0x3f3
	.4byte	0x560
	.uleb128 0xc
	.4byte	0x149
	.byte	0x5
	.byte	0
	.uleb128 0x9
	.4byte	.LASF87
	.byte	0x4
	.2byte	0x2b5
	.4byte	0x3ff
	.uleb128 0x7
	.4byte	.LASF88
	.byte	0x80
	.byte	0x4
	.2byte	0x2c5
	.4byte	0x6ae
	.uleb128 0xa
	.ascii	"r\000"
	.byte	0x4
	.2byte	0x2c6
	.4byte	0x6ae
	.byte	0
	.uleb128 0xa
	.ascii	"psr\000"
	.byte	0x4
	.2byte	0x2c7
	.4byte	0xad
	.byte	0x20
	.uleb128 0xa
	.ascii	"sp\000"
	.byte	0x4
	.2byte	0x2c8
	.4byte	0xad
	.byte	0x24
	.uleb128 0xa
	.ascii	"lr\000"
	.byte	0x4
	.2byte	0x2c9
	.4byte	0xad
	.byte	0x28
	.uleb128 0x8
	.4byte	.LASF89
	.byte	0x4
	.2byte	0x2ca
	.4byte	0x97
	.byte	0x2c
	.uleb128 0x8
	.4byte	.LASF90
	.byte	0x4
	.2byte	0x2cb
	.4byte	0x97
	.byte	0x2d
	.uleb128 0x8
	.4byte	.LASF91
	.byte	0x4
	.2byte	0x2cc
	.4byte	0x97
	.byte	0x2e
	.uleb128 0x8
	.4byte	.LASF83
	.byte	0x4
	.2byte	0x2cd
	.4byte	0x97
	.byte	0x2f
	.uleb128 0x8
	.4byte	.LASF92
	.byte	0x4
	.2byte	0x2ce
	.4byte	0x6be
	.byte	0x30
	.uleb128 0x8
	.4byte	.LASF93
	.byte	0x4
	.2byte	0x2cf
	.4byte	0x6be
	.byte	0x34
	.uleb128 0x8
	.4byte	.LASF94
	.byte	0x4
	.2byte	0x2d0
	.4byte	0x54b
	.byte	0x38
	.uleb128 0x8
	.4byte	.LASF95
	.byte	0x4
	.2byte	0x2d1
	.4byte	0x54b
	.byte	0x39
	.uleb128 0x8
	.4byte	.LASF96
	.byte	0x4
	.2byte	0x2d2
	.4byte	0xa2
	.byte	0x3a
	.uleb128 0x8
	.4byte	.LASF97
	.byte	0x4
	.2byte	0x2d3
	.4byte	0x6c0
	.byte	0x3c
	.uleb128 0x8
	.4byte	.LASF98
	.byte	0x4
	.2byte	0x2d4
	.4byte	0xad
	.byte	0x40
	.uleb128 0x8
	.4byte	.LASF99
	.byte	0x4
	.2byte	0x2d5
	.4byte	0xad
	.byte	0x44
	.uleb128 0x8
	.4byte	.LASF100
	.byte	0x4
	.2byte	0x2d6
	.4byte	0x6cd
	.byte	0x48
	.uleb128 0x8
	.4byte	.LASF101
	.byte	0x4
	.2byte	0x2d7
	.4byte	0x6be
	.byte	0x58
	.uleb128 0x8
	.4byte	.LASF102
	.byte	0x4
	.2byte	0x2d8
	.4byte	0xad
	.byte	0x5c
	.uleb128 0x8
	.4byte	.LASF85
	.byte	0x4
	.2byte	0x2d9
	.4byte	0x6dd
	.byte	0x60
	.uleb128 0x8
	.4byte	.LASF103
	.byte	0x4
	.2byte	0x2da
	.4byte	0xad
	.byte	0x70
	.uleb128 0x8
	.4byte	.LASF104
	.byte	0x4
	.2byte	0x2db
	.4byte	0xad
	.byte	0x74
	.uleb128 0x8
	.4byte	.LASF105
	.byte	0x4
	.2byte	0x2dc
	.4byte	0xad
	.byte	0x78
	.uleb128 0x8
	.4byte	.LASF106
	.byte	0x4
	.2byte	0x2dd
	.4byte	0xad
	.byte	0x7c
	.byte	0
	.uleb128 0xb
	.4byte	0xad
	.4byte	0x6be
	.uleb128 0xc
	.4byte	0x149
	.byte	0x7
	.byte	0
	.uleb128 0x12
	.byte	0x4
	.uleb128 0x5
	.byte	0x4
	.4byte	0x6c6
	.uleb128 0x2
	.byte	0x1
	.byte	0x8
	.4byte	.LASF107
	.uleb128 0xb
	.4byte	0x6c6
	.4byte	0x6dd
	.uleb128 0xc
	.4byte	0x149
	.byte	0xf
	.byte	0
	.uleb128 0xb
	.4byte	0xad
	.4byte	0x6ed
	.uleb128 0xc
	.4byte	0x149
	.byte	0x3
	.byte	0
	.uleb128 0x9
	.4byte	.LASF108
	.byte	0x4
	.2byte	0x2de
	.4byte	0x56c
	.uleb128 0x5
	.byte	0x4
	.4byte	0x30c
	.uleb128 0x5
	.byte	0x4
	.4byte	0x3b2
	.uleb128 0x5
	.byte	0x4
	.4byte	0x6ed
	.uleb128 0x13
	.ascii	"sv\000"
	.2byte	0x100
	.byte	0x4
	.2byte	0x3b9
	.4byte	0xadb
	.uleb128 0x8
	.4byte	.LASF109
	.byte	0x4
	.2byte	0x3ba
	.4byte	0xa2
	.byte	0
	.uleb128 0x8
	.4byte	.LASF110
	.byte	0x4
	.2byte	0x3bb
	.4byte	0xa2
	.byte	0x2
	.uleb128 0x8
	.4byte	.LASF111
	.byte	0x4
	.2byte	0x3bd
	.4byte	0xa2
	.byte	0x4
	.uleb128 0x8
	.4byte	.LASF112
	.byte	0x4
	.2byte	0x3be
	.4byte	0x97
	.byte	0x6
	.uleb128 0x8
	.4byte	.LASF113
	.byte	0x4
	.2byte	0x3bf
	.4byte	0x97
	.byte	0x7
	.uleb128 0x8
	.4byte	.LASF114
	.byte	0x4
	.2byte	0x3c1
	.4byte	0xa2
	.byte	0x8
	.uleb128 0x8
	.4byte	.LASF115
	.byte	0x4
	.2byte	0x3c2
	.4byte	0x97
	.byte	0xa
	.uleb128 0x8
	.4byte	.LASF116
	.byte	0x4
	.2byte	0x3c3
	.4byte	0x97
	.byte	0xb
	.uleb128 0x8
	.4byte	.LASF117
	.byte	0x4
	.2byte	0x3c5
	.4byte	0x97
	.byte	0xc
	.uleb128 0x8
	.4byte	.LASF118
	.byte	0x4
	.2byte	0x3c6
	.4byte	0x97
	.byte	0xd
	.uleb128 0x8
	.4byte	.LASF119
	.byte	0x4
	.2byte	0x3c7
	.4byte	0x97
	.byte	0xe
	.uleb128 0x8
	.4byte	.LASF120
	.byte	0x4
	.2byte	0x3c8
	.4byte	0x97
	.byte	0xf
	.uleb128 0x8
	.4byte	.LASF121
	.byte	0x4
	.2byte	0x3ca
	.4byte	0xadb
	.byte	0x10
	.uleb128 0x8
	.4byte	.LASF122
	.byte	0x4
	.2byte	0x3cb
	.4byte	0xae0
	.byte	0x18
	.uleb128 0x8
	.4byte	.LASF123
	.byte	0x4
	.2byte	0x3cc
	.4byte	0xa2
	.byte	0x1a
	.uleb128 0x8
	.4byte	.LASF124
	.byte	0x4
	.2byte	0x3ce
	.4byte	0xae5
	.byte	0x1c
	.uleb128 0x8
	.4byte	.LASF125
	.byte	0x4
	.2byte	0x3cf
	.4byte	0xad
	.byte	0x20
	.uleb128 0x8
	.4byte	.LASF126
	.byte	0x4
	.2byte	0x3d1
	.4byte	0xa2
	.byte	0x24
	.uleb128 0x8
	.4byte	.LASF127
	.byte	0x4
	.2byte	0x3d2
	.4byte	0xa2
	.byte	0x26
	.uleb128 0x8
	.4byte	.LASF128
	.byte	0x4
	.2byte	0x3d4
	.4byte	0x97
	.byte	0x28
	.uleb128 0x8
	.4byte	.LASF129
	.byte	0x4
	.2byte	0x3d5
	.4byte	0x97
	.byte	0x29
	.uleb128 0x8
	.4byte	.LASF130
	.byte	0x4
	.2byte	0x3d6
	.4byte	0x97
	.byte	0x2a
	.uleb128 0x8
	.4byte	.LASF131
	.byte	0x4
	.2byte	0x3d7
	.4byte	0x97
	.byte	0x2b
	.uleb128 0x8
	.4byte	.LASF132
	.byte	0x4
	.2byte	0x3d9
	.4byte	0x97
	.byte	0x2c
	.uleb128 0x8
	.4byte	.LASF133
	.byte	0x4
	.2byte	0x3da
	.4byte	0x97
	.byte	0x2d
	.uleb128 0x8
	.4byte	.LASF134
	.byte	0x4
	.2byte	0x3db
	.4byte	0xa2
	.byte	0x2e
	.uleb128 0x8
	.4byte	.LASF135
	.byte	0x4
	.2byte	0x3dd
	.4byte	0xad
	.byte	0x30
	.uleb128 0x8
	.4byte	.LASF136
	.byte	0x4
	.2byte	0x3de
	.4byte	0xad
	.byte	0x34
	.uleb128 0x8
	.4byte	.LASF137
	.byte	0x4
	.2byte	0x3df
	.4byte	0xad
	.byte	0x38
	.uleb128 0x8
	.4byte	.LASF138
	.byte	0x4
	.2byte	0x3e0
	.4byte	0xad
	.byte	0x3c
	.uleb128 0x8
	.4byte	.LASF139
	.byte	0x4
	.2byte	0x3e2
	.4byte	0x97
	.byte	0x40
	.uleb128 0x8
	.4byte	.LASF140
	.byte	0x4
	.2byte	0x3e3
	.4byte	0x97
	.byte	0x41
	.uleb128 0x8
	.4byte	.LASF141
	.byte	0x4
	.2byte	0x3e4
	.4byte	0x97
	.byte	0x42
	.uleb128 0x8
	.4byte	.LASF142
	.byte	0x4
	.2byte	0x3e5
	.4byte	0x97
	.byte	0x43
	.uleb128 0x8
	.4byte	.LASF143
	.byte	0x4
	.2byte	0x3e7
	.4byte	0xad
	.byte	0x44
	.uleb128 0x8
	.4byte	.LASF144
	.byte	0x4
	.2byte	0x3e9
	.4byte	0x6ff
	.byte	0x48
	.uleb128 0x8
	.4byte	.LASF145
	.byte	0x4
	.2byte	0x3ea
	.4byte	0x6ff
	.byte	0x4c
	.uleb128 0x8
	.4byte	.LASF146
	.byte	0x4
	.2byte	0x3ec
	.4byte	0xad
	.byte	0x50
	.uleb128 0x8
	.4byte	.LASF147
	.byte	0x4
	.2byte	0x3ed
	.4byte	0x545
	.byte	0x54
	.uleb128 0x8
	.4byte	.LASF148
	.byte	0x4
	.2byte	0x3ee
	.4byte	0xad
	.byte	0x58
	.uleb128 0x8
	.4byte	.LASF149
	.byte	0x4
	.2byte	0x3ef
	.4byte	0xad
	.byte	0x5c
	.uleb128 0x8
	.4byte	.LASF150
	.byte	0x4
	.2byte	0x3f1
	.4byte	0xad
	.byte	0x60
	.uleb128 0x8
	.4byte	.LASF151
	.byte	0x4
	.2byte	0x3f3
	.4byte	0x54b
	.byte	0x64
	.uleb128 0x8
	.4byte	.LASF152
	.byte	0x4
	.2byte	0x3f4
	.4byte	0x97
	.byte	0x65
	.uleb128 0x8
	.4byte	.LASF153
	.byte	0x4
	.2byte	0x3f5
	.4byte	0x97
	.byte	0x66
	.uleb128 0x8
	.4byte	.LASF154
	.byte	0x4
	.2byte	0x3f6
	.4byte	0x97
	.byte	0x67
	.uleb128 0x8
	.4byte	.LASF155
	.byte	0x4
	.2byte	0x3f8
	.4byte	0x13d
	.byte	0x68
	.uleb128 0x8
	.4byte	.LASF156
	.byte	0x4
	.2byte	0x3fa
	.4byte	0xad
	.byte	0x70
	.uleb128 0x8
	.4byte	.LASF157
	.byte	0x4
	.2byte	0x3fb
	.4byte	0xad
	.byte	0x74
	.uleb128 0x8
	.4byte	.LASF158
	.byte	0x4
	.2byte	0x3fc
	.4byte	0xad
	.byte	0x78
	.uleb128 0x8
	.4byte	.LASF159
	.byte	0x4
	.2byte	0x3fd
	.4byte	0xad
	.byte	0x7c
	.uleb128 0x8
	.4byte	.LASF160
	.byte	0x4
	.2byte	0x3ff
	.4byte	0xaea
	.byte	0x80
	.uleb128 0x8
	.4byte	.LASF161
	.byte	0x4
	.2byte	0x400
	.4byte	0xaea
	.byte	0x94
	.uleb128 0x8
	.4byte	.LASF162
	.byte	0x4
	.2byte	0x401
	.4byte	0xaea
	.byte	0xa8
	.uleb128 0x8
	.4byte	.LASF163
	.byte	0x4
	.2byte	0x403
	.4byte	0x97
	.byte	0xbc
	.uleb128 0x8
	.4byte	.LASF164
	.byte	0x4
	.2byte	0x404
	.4byte	0x97
	.byte	0xbd
	.uleb128 0x8
	.4byte	.LASF165
	.byte	0x4
	.2byte	0x405
	.4byte	0xa2
	.byte	0xbe
	.uleb128 0x8
	.4byte	.LASF166
	.byte	0x4
	.2byte	0x407
	.4byte	0x545
	.byte	0xc0
	.uleb128 0x8
	.4byte	.LASF167
	.byte	0x4
	.2byte	0x408
	.4byte	0x545
	.byte	0xc4
	.uleb128 0x8
	.4byte	.LASF168
	.byte	0x4
	.2byte	0x409
	.4byte	0x545
	.byte	0xc8
	.uleb128 0x8
	.4byte	.LASF169
	.byte	0x4
	.2byte	0x40a
	.4byte	0x705
	.byte	0xcc
	.uleb128 0x8
	.4byte	.LASF170
	.byte	0x4
	.2byte	0x40c
	.4byte	0x6ff
	.byte	0xd0
	.uleb128 0x8
	.4byte	.LASF171
	.byte	0x4
	.2byte	0x40d
	.4byte	0xafa
	.byte	0xd4
	.uleb128 0x8
	.4byte	.LASF172
	.byte	0x4
	.2byte	0x40e
	.4byte	0x545
	.byte	0xd8
	.uleb128 0x8
	.4byte	.LASF173
	.byte	0x4
	.2byte	0x40f
	.4byte	0xb00
	.byte	0xdc
	.uleb128 0x8
	.4byte	.LASF174
	.byte	0x4
	.2byte	0x410
	.4byte	0xa2
	.byte	0xe0
	.uleb128 0x8
	.4byte	.LASF175
	.byte	0x4
	.2byte	0x411
	.4byte	0xa2
	.byte	0xe2
	.uleb128 0x8
	.4byte	.LASF30
	.byte	0x4
	.2byte	0x412
	.4byte	0xb06
	.byte	0xe4
	.uleb128 0x8
	.4byte	.LASF176
	.byte	0x4
	.2byte	0x413
	.4byte	0x6f9
	.byte	0xe8
	.uleb128 0x8
	.4byte	.LASF177
	.byte	0x4
	.2byte	0x414
	.4byte	0xad
	.byte	0xec
	.uleb128 0x8
	.4byte	.LASF178
	.byte	0x4
	.2byte	0x416
	.4byte	0x150
	.byte	0xf0
	.uleb128 0x8
	.4byte	.LASF179
	.byte	0x4
	.2byte	0x417
	.4byte	0xad
	.byte	0xf4
	.uleb128 0x8
	.4byte	.LASF180
	.byte	0x4
	.2byte	0x418
	.4byte	0x545
	.byte	0xf8
	.uleb128 0x8
	.4byte	.LASF102
	.byte	0x4
	.2byte	0x419
	.4byte	0xad
	.byte	0xfc
	.byte	0
	.uleb128 0x11
	.4byte	0xb8
	.uleb128 0x11
	.4byte	0xa2
	.uleb128 0x11
	.4byte	0xad
	.uleb128 0xb
	.4byte	0x97
	.4byte	0xafa
	.uleb128 0xc
	.4byte	0x149
	.byte	0x13
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0x1af
	.uleb128 0x5
	.byte	0x4
	.4byte	0x39d
	.uleb128 0x5
	.byte	0x4
	.4byte	0x20a
	.uleb128 0x9
	.4byte	.LASF181
	.byte	0x4
	.2byte	0x41a
	.4byte	0x70b
	.uleb128 0x2
	.byte	0x1
	.byte	0xd
	.4byte	.LASF182
	.uleb128 0x2
	.byte	0x2
	.byte	0xd
	.4byte	.LASF183
	.uleb128 0x2
	.byte	0x4
	.byte	0xd
	.4byte	.LASF184
	.uleb128 0x2
	.byte	0x2
	.byte	0xd
	.4byte	.LASF185
	.uleb128 0x2
	.byte	0x4
	.byte	0xd
	.4byte	.LASF186
	.uleb128 0x2
	.byte	0x8
	.byte	0xd
	.4byte	.LASF187
	.uleb128 0x2
	.byte	0x1
	.byte	0xe
	.4byte	.LASF188
	.uleb128 0x2
	.byte	0x2
	.byte	0xe
	.4byte	.LASF189
	.uleb128 0x2
	.byte	0x4
	.byte	0xe
	.4byte	.LASF190
	.uleb128 0x2
	.byte	0x2
	.byte	0xe
	.4byte	.LASF191
	.uleb128 0x2
	.byte	0x4
	.byte	0xe
	.4byte	.LASF192
	.uleb128 0x2
	.byte	0x8
	.byte	0xe
	.4byte	.LASF193
	.uleb128 0xf
	.byte	0x10
	.byte	0x1
	.2byte	0x432
	.4byte	0xbaa
	.uleb128 0x8
	.4byte	.LASF194
	.byte	0x1
	.2byte	0x433
	.4byte	0x65
	.byte	0
	.uleb128 0x8
	.4byte	.LASF195
	.byte	0x1
	.2byte	0x434
	.4byte	0x65
	.byte	0x4
	.uleb128 0x8
	.4byte	.LASF196
	.byte	0x1
	.2byte	0x435
	.4byte	0x65
	.byte	0x8
	.uleb128 0x8
	.4byte	.LASF197
	.byte	0x1
	.2byte	0x436
	.4byte	0x65
	.byte	0xc
	.byte	0
	.uleb128 0x9
	.4byte	.LASF198
	.byte	0x1
	.2byte	0x437
	.4byte	0xb6c
	.uleb128 0x9
	.4byte	.LASF199
	.byte	0x1
	.2byte	0x437
	.4byte	0xbc2
	.uleb128 0x5
	.byte	0x4
	.4byte	0xb6c
	.uleb128 0x14
	.4byte	.LASF200
	.byte	0x1
	.2byte	0x1ce
	.4byte	0x65
	.byte	0x1
	.4byte	0xbe4
	.uleb128 0x15
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x1ce
	.4byte	0x65
	.byte	0
	.uleb128 0x14
	.4byte	.LASF201
	.byte	0x1
	.2byte	0x1d1
	.4byte	0x65
	.byte	0x1
	.4byte	0xc00
	.uleb128 0x15
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x1d1
	.4byte	0x65
	.byte	0
	.uleb128 0x14
	.4byte	.LASF202
	.byte	0x1
	.2byte	0x1cb
	.4byte	0x65
	.byte	0x1
	.4byte	0xc1c
	.uleb128 0x15
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x1cb
	.4byte	0x65
	.byte	0
	.uleb128 0x14
	.4byte	.LASF203
	.byte	0x1
	.2byte	0x1d4
	.4byte	0x65
	.byte	0x1
	.4byte	0xc38
	.uleb128 0x15
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x1d4
	.4byte	0x65
	.byte	0
	.uleb128 0x16
	.4byte	.LASF293
	.byte	0x1
	.2byte	0x440
	.4byte	0x65
	.byte	0x3
	.4byte	0xc56
	.uleb128 0x17
	.4byte	.LASF204
	.byte	0x1
	.2byte	0x440
	.4byte	0x65
	.byte	0
	.uleb128 0x18
	.4byte	.LASF205
	.byte	0x1
	.2byte	0x5d8
	.byte	0x1
	.uleb128 0x19
	.4byte	.LASF294
	.byte	0x1
	.2byte	0x66b
	.4byte	0x77
	.byte	0x1
	.uleb128 0x18
	.4byte	.LASF206
	.byte	0x1
	.2byte	0x1c0
	.byte	0x1
	.uleb128 0x18
	.4byte	.LASF207
	.byte	0x1
	.2byte	0x40a
	.byte	0x1
	.uleb128 0x18
	.4byte	.LASF208
	.byte	0x1
	.2byte	0x5dd
	.byte	0x1
	.uleb128 0x1a
	.4byte	.LASF295
	.byte	0x1
	.2byte	0x1a0
	.byte	0x1
	.4byte	0xc9f
	.uleb128 0x1b
	.ascii	"i\000"
	.byte	0x1
	.2byte	0x1a2
	.4byte	0x89
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF213
	.byte	0x1
	.2byte	0xd64
	.4byte	.LASF213
	.4byte	.LFB236
	.4byte	.LFE236-.LFB236
	.uleb128 0x1
	.byte	0x9c
	.4byte	0xd25
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xd66
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xd66
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xd66
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xd66
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xd66
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xd66
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xd66
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xd66
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0x65
	.uleb128 0x1c
	.4byte	.LASF214
	.byte	0x1
	.2byte	0xdb5
	.4byte	.LASF214
	.4byte	.LFB237
	.4byte	.LFE237-.LFB237
	.uleb128 0x1
	.byte	0x9c
	.4byte	0xdb1
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xdb7
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xdb7
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xdb7
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xdb7
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xdb7
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xdb7
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xdb7
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xdb7
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF215
	.byte	0x1
	.2byte	0xdbf
	.4byte	.LASF215
	.4byte	.LFB238
	.4byte	.LFE238-.LFB238
	.uleb128 0x1
	.byte	0x9c
	.4byte	0xe37
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xdc1
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xdc1
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xdc1
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xdc1
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xdc1
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xdc1
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xdc1
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xdc1
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF216
	.byte	0x1
	.2byte	0xdc9
	.4byte	.LASF216
	.4byte	.LFB239
	.4byte	.LFE239-.LFB239
	.uleb128 0x1
	.byte	0x9c
	.4byte	0xebd
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xdcb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xdcb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xdcb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xdcb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xdcb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xdcb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xdcb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xdcb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF217
	.byte	0x1
	.2byte	0xdd3
	.4byte	.LASF217
	.4byte	.LFB240
	.4byte	.LFE240-.LFB240
	.uleb128 0x1
	.byte	0x9c
	.4byte	0xf43
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xdd5
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xdd5
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xdd5
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xdd5
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xdd5
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xdd5
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xdd5
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xdd5
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF218
	.byte	0x1
	.2byte	0xddc
	.4byte	.LASF218
	.4byte	.LFB241
	.4byte	.LFE241-.LFB241
	.uleb128 0x1
	.byte	0x9c
	.4byte	0xfc9
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xdde
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xdde
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xdde
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xdde
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xdde
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xdde
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xdde
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xdde
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF219
	.byte	0x1
	.2byte	0xde6
	.4byte	.LASF219
	.4byte	.LFB242
	.4byte	.LFE242-.LFB242
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x104f
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xde8
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xde8
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xde8
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xde8
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xde8
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xde8
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xde8
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xde8
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF220
	.byte	0x1
	.2byte	0xdf0
	.4byte	.LASF220
	.4byte	.LFB243
	.4byte	.LFE243-.LFB243
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x10d5
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xdf2
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xdf2
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xdf2
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xdf2
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xdf2
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xdf2
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xdf2
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xdf2
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF221
	.byte	0x1
	.2byte	0xdfa
	.4byte	.LASF221
	.4byte	.LFB244
	.4byte	.LFE244-.LFB244
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x115b
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xdfc
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xdfc
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xdfc
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xdfc
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xdfc
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xdfc
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xdfc
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xdfc
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1f
	.4byte	.LASF223
	.byte	0x1
	.byte	0xc9
	.4byte	.LFB193
	.4byte	.LFE193-.LFB193
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x11a3
	.uleb128 0x20
	.ascii	"x\000"
	.byte	0x1
	.byte	0xc9
	.4byte	0x65
	.4byte	.LLST0
	.uleb128 0x21
	.ascii	"tmp\000"
	.byte	0x1
	.byte	0xcb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x22
	.4byte	.LVL2
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC0
	.byte	0
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF222
	.byte	0x1
	.2byte	0x54d
	.4byte	.LASF222
	.4byte	.LFB215
	.4byte	.LFE215-.LFB215
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x11d2
	.uleb128 0x22
	.4byte	.LVL3
	.4byte	0x115b
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x6
	.byte	0x11
	.sleb128 -1160729136
	.byte	0
	.byte	0
	.uleb128 0x1f
	.4byte	.LASF224
	.byte	0x1
	.byte	0xe5
	.4byte	.LFB194
	.4byte	.LFE194-.LFB194
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x11f7
	.uleb128 0x24
	.4byte	.LASF225
	.byte	0x1
	.byte	0xe7
	.4byte	0xd25
	.4byte	0x21000000
	.byte	0
	.uleb128 0x1f
	.4byte	.LASF226
	.byte	0x1
	.byte	0xed
	.4byte	.LFB195
	.4byte	.LFE195-.LFB195
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1227
	.uleb128 0x24
	.4byte	.LASF225
	.byte	0x1
	.byte	0xef
	.4byte	0xd25
	.4byte	0x21000000
	.uleb128 0x21
	.ascii	"t\000"
	.byte	0x1
	.byte	0xf0
	.4byte	0x65
	.uleb128 0x1
	.byte	0x53
	.byte	0
	.uleb128 0x1f
	.4byte	.LASF227
	.byte	0x1
	.byte	0xfb
	.4byte	.LFB196
	.4byte	.LFE196-.LFB196
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1257
	.uleb128 0x24
	.4byte	.LASF225
	.byte	0x1
	.byte	0xfd
	.4byte	0xd25
	.4byte	0x21000000
	.uleb128 0x21
	.ascii	"t\000"
	.byte	0x1
	.byte	0xfe
	.4byte	0x65
	.uleb128 0x1
	.byte	0x52
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF228
	.byte	0x1
	.2byte	0x11e
	.4byte	.LASF228
	.4byte	.LFB197
	.4byte	.LFE197-.LFB197
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x12b8
	.uleb128 0x25
	.4byte	.LASF229
	.byte	0x1
	.2byte	0x11e
	.4byte	0x65
	.4byte	.LLST1
	.uleb128 0x26
	.4byte	.LASF250
	.byte	0x1
	.2byte	0x12f
	.4byte	.L24
	.uleb128 0x1e
	.ascii	"rp1\000"
	.byte	0x1
	.2byte	0x121
	.4byte	0x12b8
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x1e
	.ascii	"rp2\000"
	.byte	0x1
	.2byte	0x122
	.4byte	0x12b8
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x1d
	.4byte	.LASF230
	.byte	0x1
	.2byte	0x123
	.4byte	0x89
	.uleb128 0x1
	.byte	0x53
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0x53
	.uleb128 0x27
	.4byte	0xc87
	.4byte	.LFB198
	.4byte	.LFE198-.LFB198
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x12eb
	.uleb128 0x28
	.4byte	0xc94
	.4byte	.LLST2
	.uleb128 0x22
	.4byte	.LVL14
	.4byte	0x1257
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x2
	.byte	0x74
	.sleb128 1
	.byte	0
	.byte	0
	.uleb128 0x29
	.4byte	.LASF231
	.byte	0x1
	.2byte	0x1ad
	.4byte	.LFB199
	.4byte	.LFE199-.LFB199
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1369
	.uleb128 0x25
	.4byte	.LASF232
	.byte	0x1
	.2byte	0x1ad
	.4byte	0x89
	.4byte	.LLST3
	.uleb128 0x2a
	.ascii	"i\000"
	.byte	0x1
	.2byte	0x1af
	.4byte	0x89
	.4byte	.LLST4
	.uleb128 0x2a
	.ascii	"j\000"
	.byte	0x1
	.2byte	0x1af
	.4byte	0x89
	.4byte	.LLST5
	.uleb128 0x2b
	.4byte	.LASF56
	.byte	0x1
	.2byte	0x1b0
	.4byte	0x12b8
	.4byte	.LLST6
	.uleb128 0x22
	.4byte	.LVL21
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC1
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x2
	.byte	0x76
	.sleb128 0
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x53
	.uleb128 0x2
	.byte	0x74
	.sleb128 -1
	.uleb128 0x23
	.uleb128 0x2
	.byte	0x7d
	.sleb128 0
	.uleb128 0x2
	.byte	0x78
	.sleb128 0
	.byte	0
	.byte	0
	.uleb128 0x27
	.4byte	0xc6c
	.4byte	.LFB200
	.4byte	.LFE200-.LFB200
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x139f
	.uleb128 0x2c
	.4byte	.LVL24
	.4byte	0x12eb
	.4byte	0x138f
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x30
	.byte	0
	.uleb128 0x2d
	.4byte	.LVL25
	.4byte	0x12eb
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x31
	.byte	0
	.byte	0
	.uleb128 0x2e
	.4byte	.LASF233
	.byte	0x1
	.2byte	0x1c8
	.4byte	0x65
	.4byte	.LFB201
	.4byte	.LFE201-.LFB201
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x13c8
	.uleb128 0x2f
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x1c8
	.4byte	0x65
	.4byte	.LLST7
	.byte	0
	.uleb128 0x27
	.4byte	0xc00
	.4byte	.LFB202
	.4byte	.LFE202-.LFB202
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x13e5
	.uleb128 0x30
	.4byte	0xc11
	.4byte	.LLST8
	.byte	0
	.uleb128 0x27
	.4byte	0xbc8
	.4byte	.LFB203
	.4byte	.LFE203-.LFB203
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1402
	.uleb128 0x30
	.4byte	0xbd9
	.4byte	.LLST9
	.byte	0
	.uleb128 0x27
	.4byte	0xbe4
	.4byte	.LFB204
	.4byte	.LFE204-.LFB204
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x141f
	.uleb128 0x30
	.4byte	0xbf5
	.4byte	.LLST10
	.byte	0
	.uleb128 0x27
	.4byte	0xc1c
	.4byte	.LFB205
	.4byte	.LFE205-.LFB205
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x143c
	.uleb128 0x30
	.4byte	0xc2d
	.4byte	.LLST11
	.byte	0
	.uleb128 0x29
	.4byte	.LASF234
	.byte	0x1
	.2byte	0x1dc
	.4byte	.LFB206
	.4byte	.LFE206-.LFB206
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x14fa
	.uleb128 0x2a
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x1de
	.4byte	0x65
	.4byte	.LLST12
	.uleb128 0x2a
	.ascii	"w0\000"
	.byte	0x1
	.2byte	0x1de
	.4byte	0x65
	.4byte	.LLST13
	.uleb128 0x2a
	.ascii	"w1\000"
	.byte	0x1
	.2byte	0x1de
	.4byte	0x65
	.4byte	.LLST14
	.uleb128 0x2a
	.ascii	"w2\000"
	.byte	0x1
	.2byte	0x1de
	.4byte	0x65
	.4byte	.LLST15
	.uleb128 0x2a
	.ascii	"w3\000"
	.byte	0x1
	.2byte	0x1de
	.4byte	0x65
	.4byte	.LLST16
	.uleb128 0x2c
	.4byte	.LVL43
	.4byte	0x244a
	.4byte	0x14b8
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC2
	.byte	0
	.uleb128 0x2c
	.4byte	.LVL45
	.4byte	0x244a
	.4byte	0x14e1
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC3
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x9
	.byte	0x78
	.sleb128 0
	.byte	0x44
	.byte	0x24
	.byte	0x44
	.byte	0x25
	.byte	0x75
	.sleb128 0
	.byte	0x21
	.byte	0
	.uleb128 0x2d
	.4byte	.LVL49
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC4
	.byte	0
	.byte	0
	.uleb128 0x29
	.4byte	.LASF235
	.byte	0x1
	.2byte	0x1f4
	.4byte	.LFB207
	.4byte	.LFE207-.LFB207
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x15cc
	.uleb128 0x2b
	.4byte	.LASF236
	.byte	0x1
	.2byte	0x1f6
	.4byte	0x65
	.4byte	.LLST17
	.uleb128 0x2b
	.4byte	.LASF237
	.byte	0x1
	.2byte	0x1f7
	.4byte	0x65
	.4byte	.LLST18
	.uleb128 0x2a
	.ascii	"i\000"
	.byte	0x1
	.2byte	0x1f8
	.4byte	0x65
	.4byte	.LLST19
	.uleb128 0x2a
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x1f9
	.4byte	0x65
	.4byte	.LLST20
	.uleb128 0x31
	.4byte	0xc1c
	.4byte	.LBB60
	.4byte	.LBE60-.LBB60
	.byte	0x1
	.2byte	0x215
	.4byte	0x156a
	.uleb128 0x30
	.4byte	0xc2d
	.4byte	.LLST21
	.byte	0
	.uleb128 0x2c
	.4byte	.LVL53
	.4byte	0x244a
	.4byte	0x158e
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC5
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x4
	.byte	0x76
	.sleb128 0
	.byte	0x3f
	.byte	0x24
	.byte	0
	.uleb128 0x32
	.4byte	.LVL57
	.4byte	0x143c
	.uleb128 0x2c
	.4byte	.LVL63
	.4byte	0x244a
	.4byte	0x15b3
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC5
	.byte	0
	.uleb128 0x22
	.4byte	.LVL67
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC6
	.byte	0
	.byte	0
	.uleb128 0x27
	.4byte	0xc75
	.4byte	.LFB208
	.4byte	.LFE208-.LFB208
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x15e9
	.uleb128 0x33
	.4byte	.LVL69
	.4byte	0x14fa
	.byte	0
	.uleb128 0x34
	.4byte	.LASF244
	.byte	0x1
	.2byte	0x457
	.4byte	.LFB212
	.4byte	.LFE212-.LFB212
	.uleb128 0x1
	.byte	0x9c
	.uleb128 0x1c
	.4byte	.LASF238
	.byte	0x1
	.2byte	0x480
	.4byte	.LASF238
	.4byte	.LFB213
	.4byte	.LFE213-.LFB213
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1631
	.uleb128 0x1e
	.ascii	"r8\000"
	.byte	0x1
	.2byte	0x482
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF56
	.byte	0x1
	.2byte	0x483
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5c
	.byte	0
	.uleb128 0x2e
	.4byte	.LASF239
	.byte	0x1
	.2byte	0x4c7
	.4byte	0x65
	.4byte	.LFB214
	.4byte	.LFE214-.LFB214
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x166a
	.uleb128 0x25
	.4byte	.LASF56
	.byte	0x1
	.2byte	0x4c7
	.4byte	0xbb6
	.4byte	.LLST22
	.uleb128 0x1d
	.4byte	.LASF240
	.byte	0x1
	.2byte	0x4c9
	.4byte	0x65
	.uleb128 0x1
	.byte	0x50
	.byte	0
	.uleb128 0x29
	.4byte	.LASF241
	.byte	0x1
	.2byte	0x5c3
	.4byte	.LFB216
	.4byte	.LFE216-.LFB216
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1736
	.uleb128 0x1d
	.4byte	.LASF242
	.byte	0x1
	.2byte	0x5c5
	.4byte	0xd25
	.uleb128 0x6
	.byte	0x3
	.4byte	__jump_table+64
	.byte	0x9f
	.uleb128 0x2a
	.ascii	"i\000"
	.byte	0x1
	.2byte	0x5c6
	.4byte	0x65
	.4byte	.LLST23
	.uleb128 0x2a
	.ascii	"j\000"
	.byte	0x1
	.2byte	0x5c6
	.4byte	0x65
	.4byte	.LLST24
	.uleb128 0x2a
	.ascii	"k\000"
	.byte	0x1
	.2byte	0x5c6
	.4byte	0x65
	.4byte	.LLST25
	.uleb128 0x2c
	.4byte	.LVL74
	.4byte	0x244a
	.4byte	0x16d9
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC7
	.byte	0
	.uleb128 0x2c
	.4byte	.LVL78
	.4byte	0x244a
	.4byte	0x1709
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC8
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x53
	.uleb128 0x2
	.byte	0x78
	.sleb128 0
	.uleb128 0x23
	.uleb128 0x2
	.byte	0x7d
	.sleb128 0
	.uleb128 0x2
	.byte	0x75
	.sleb128 0
	.uleb128 0x23
	.uleb128 0x2
	.byte	0x7d
	.sleb128 4
	.uleb128 0x2
	.byte	0x79
	.sleb128 0
	.byte	0
	.uleb128 0x22
	.4byte	.LVL82
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC8
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x53
	.uleb128 0x2
	.byte	0x78
	.sleb128 0
	.uleb128 0x23
	.uleb128 0x2
	.byte	0x7d
	.sleb128 0
	.uleb128 0x2
	.byte	0x75
	.sleb128 0
	.uleb128 0x23
	.uleb128 0x2
	.byte	0x7d
	.sleb128 4
	.uleb128 0x2
	.byte	0x8
	.byte	0x20
	.byte	0
	.byte	0
	.uleb128 0x27
	.4byte	0xc56
	.4byte	.LFB217
	.4byte	.LFE217-.LFB217
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1762
	.uleb128 0x2d
	.4byte	.LVL84
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC9
	.byte	0
	.byte	0
	.uleb128 0x27
	.4byte	0xc7e
	.4byte	.LFB218
	.4byte	.LFE218-.LFB218
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x17ac
	.uleb128 0x35
	.4byte	0xc56
	.4byte	.LBB62
	.4byte	.Ldebug_ranges0+0
	.byte	0x1
	.2byte	0x5e0
	.4byte	0x17a2
	.uleb128 0x2d
	.4byte	.LVL86
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC9
	.byte	0
	.byte	0
	.uleb128 0x32
	.4byte	.LVL85
	.4byte	0x166a
	.byte	0
	.uleb128 0x29
	.4byte	.LASF243
	.byte	0x1
	.2byte	0x651
	.4byte	.LFB219
	.4byte	.LFE219-.LFB219
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1827
	.uleb128 0x2a
	.ascii	"i\000"
	.byte	0x1
	.2byte	0x653
	.4byte	0x89
	.4byte	.LLST26
	.uleb128 0x2c
	.4byte	.LVL87
	.4byte	0x244a
	.4byte	0x17ec
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC10
	.byte	0
	.uleb128 0x2c
	.4byte	.LVL90
	.4byte	0x244a
	.4byte	0x180e
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC11
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x53
	.uleb128 0x2
	.byte	0x74
	.sleb128 -1
	.byte	0
	.uleb128 0x2d
	.4byte	.LVL92
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC12
	.byte	0
	.byte	0
	.uleb128 0x34
	.4byte	.LASF245
	.byte	0x1
	.2byte	0x667
	.4byte	.LFB220
	.4byte	.LFE220-.LFB220
	.uleb128 0x1
	.byte	0x9c
	.uleb128 0x36
	.4byte	0xc5f
	.4byte	.LFB221
	.4byte	.LFE221-.LFB221
	.uleb128 0x1
	.byte	0x9c
	.uleb128 0x29
	.4byte	.LASF246
	.byte	0x1
	.2byte	0x66f
	.4byte	.LFB222
	.4byte	.LFE222-.LFB222
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1870
	.uleb128 0x37
	.ascii	"t\000"
	.byte	0x1
	.2byte	0x66f
	.4byte	0x77
	.uleb128 0x6
	.byte	0x50
	.byte	0x93
	.uleb128 0x4
	.byte	0x51
	.byte	0x93
	.uleb128 0x4
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF247
	.byte	0x1
	.2byte	0x6b7
	.4byte	.LASF247
	.4byte	.LFB223
	.4byte	.LFE223-.LFB223
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x18dc
	.uleb128 0x1e
	.ascii	"cp\000"
	.byte	0x1
	.2byte	0x6b9
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"rp\000"
	.byte	0x1
	.2byte	0x6ba
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"dp\000"
	.byte	0x1
	.2byte	0x6bb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1d
	.4byte	.LASF248
	.byte	0x1
	.2byte	0x6bc
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0x6bd
	.4byte	0x65
	.uleb128 0x1
	.byte	0x54
	.uleb128 0x1d
	.4byte	.LASF242
	.byte	0x1
	.2byte	0x6be
	.4byte	0x18dc
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x5
	.byte	0x4
	.4byte	0x41
	.uleb128 0x1c
	.4byte	.LASF249
	.byte	0x1
	.2byte	0x732
	.4byte	.LASF249
	.4byte	.LFB224
	.4byte	.LFE224-.LFB224
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1960
	.uleb128 0x38
	.ascii	"L0\000"
	.byte	0x1
	.2byte	0x74e
	.uleb128 0x39
	.ascii	"L1\000"
	.byte	0x1
	.2byte	0x754
	.4byte	.L117
	.uleb128 0x39
	.ascii	"L3\000"
	.byte	0x1
	.2byte	0x75f
	.4byte	.L119
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0x736
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"dma\000"
	.byte	0x1
	.2byte	0x737
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1d
	.4byte	.LASF251
	.byte	0x1
	.2byte	0x738
	.4byte	0x65
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1e
	.ascii	"inp\000"
	.byte	0x1
	.2byte	0x739
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF252
	.byte	0x1
	.2byte	0x73a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x57
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF253
	.byte	0x1
	.2byte	0x8c9
	.4byte	.LASF253
	.4byte	.LFB225
	.4byte	.LFE225-.LFB225
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x19e6
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0x8cb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0x8cb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x8cb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0x8cb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0x8cb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0x8cb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0x8cb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0x8cb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF254
	.byte	0x1
	.2byte	0x8f9
	.4byte	.LASF254
	.4byte	.LFB226
	.4byte	.LFE226-.LFB226
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1a6c
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0x8fb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0x8fb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x8fb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0x8fb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0x8fb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0x8fb
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0x8fb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0x8fb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF255
	.byte	0x1
	.2byte	0x945
	.4byte	.LASF255
	.4byte	.LFB227
	.4byte	.LFE227-.LFB227
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1af2
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0x947
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0x947
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0x947
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0x947
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0x947
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0x947
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0x947
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0x947
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF256
	.byte	0x1
	.2byte	0xa70
	.4byte	.LASF256
	.4byte	.LFB228
	.4byte	.LFE228-.LFB228
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1b78
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xa72
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xa72
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xa72
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xa72
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xa72
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xa72
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xa72
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xa72
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF257
	.byte	0x1
	.2byte	0xaf7
	.4byte	.LASF257
	.4byte	.LFB229
	.4byte	.LFE229-.LFB229
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1be2
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xaf9
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xafa
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xafb
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xafc
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xafd
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xafe
	.4byte	0x65
	.uleb128 0x1
	.byte	0x57
	.byte	0
	.uleb128 0x1c
	.4byte	.LASF258
	.byte	0x1
	.2byte	0xb23
	.4byte	.LASF258
	.4byte	.LFB230
	.4byte	.LFE230-.LFB230
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1c62
	.uleb128 0x39
	.ascii	"L0\000"
	.byte	0x1
	.2byte	0xb38
	.4byte	.L129
	.uleb128 0x39
	.ascii	"L1\000"
	.byte	0x1
	.2byte	0xb3f
	.4byte	.L130
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xb27
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xb28
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xb29
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xb2a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xb2b
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xb2c
	.4byte	0x65
	.uleb128 0x1
	.byte	0x57
	.byte	0
	.uleb128 0x18
	.4byte	.LASF259
	.byte	0x1
	.2byte	0xb5c
	.byte	0x1
	.uleb128 0x36
	.4byte	0x1c62
	.4byte	.LFB232
	.4byte	.LFE232-.LFB232
	.uleb128 0x1
	.byte	0x9c
	.uleb128 0x1c
	.4byte	.LASF260
	.byte	0x1
	.2byte	0xb64
	.4byte	.LASF260
	.4byte	.LFB233
	.4byte	.LFE233-.LFB233
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1d84
	.uleb128 0x26
	.4byte	.LASF250
	.byte	0x1
	.2byte	0xb9c
	.4byte	.L135
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xb68
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xb69
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xb6a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xb6b
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xb6c
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xb6d
	.4byte	0x65
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1e
	.ascii	"h0\000"
	.byte	0x1
	.2byte	0xb6f
	.4byte	0x65
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1e
	.ascii	"h1\000"
	.byte	0x1
	.2byte	0xb70
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1e
	.ascii	"r5\000"
	.byte	0x1
	.2byte	0xb71
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.uleb128 0x1e
	.ascii	"r4\000"
	.byte	0x1
	.2byte	0xb72
	.4byte	0x65
	.uleb128 0x1
	.byte	0x54
	.uleb128 0x2c
	.4byte	.LVL94
	.4byte	0x115b
	.4byte	0x1d37
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x2
	.byte	0x7b
	.sleb128 0
	.byte	0
	.uleb128 0x2c
	.4byte	.LVL95
	.4byte	0x115b
	.4byte	0x1d4b
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x2
	.byte	0x77
	.sleb128 0
	.byte	0
	.uleb128 0x2c
	.4byte	.LVL96
	.4byte	0x115b
	.4byte	0x1d5f
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x2
	.byte	0x76
	.sleb128 0
	.byte	0
	.uleb128 0x2c
	.4byte	.LVL97
	.4byte	0x115b
	.4byte	0x1d73
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x2
	.byte	0x74
	.sleb128 0
	.byte	0
	.uleb128 0x22
	.4byte	.LVL98
	.4byte	0x115b
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x2
	.byte	0x75
	.sleb128 0
	.byte	0
	.byte	0
	.uleb128 0x3a
	.4byte	.LASF261
	.byte	0x1
	.2byte	0xc67
	.4byte	.LASF261
	.4byte	.LFB234
	.4byte	.LFE234-.LFB234
	.uleb128 0x1
	.byte	0x9c
	.uleb128 0x3a
	.4byte	.LASF262
	.byte	0x1
	.2byte	0xc6d
	.4byte	.LASF262
	.4byte	.LFB235
	.4byte	.LFE235-.LFB235
	.uleb128 0x1
	.byte	0x9c
	.uleb128 0x29
	.4byte	.LASF263
	.byte	0x1
	.2byte	0xe28
	.4byte	.LFB245
	.4byte	.LFE245-.LFB245
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1e32
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xe2a
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xe2a
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xe2a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xe2a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xe2a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xe2a
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xe2a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xe2a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.byte	0
	.uleb128 0x2e
	.4byte	.LASF264
	.byte	0x1
	.2byte	0xe58
	.4byte	0xd25
	.4byte	.LFB246
	.4byte	.LFE246-.LFB246
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x1eda
	.uleb128 0x25
	.4byte	.LASF265
	.byte	0x1
	.2byte	0xe58
	.4byte	0xd25
	.4byte	.LLST27
	.uleb128 0x1d
	.4byte	.LASF209
	.byte	0x1
	.2byte	0xe5a
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x1e
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xe5a
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1e
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xe5a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x1e
	.ascii	"n\000"
	.byte	0x1
	.2byte	0xe5a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x59
	.uleb128 0x1d
	.4byte	.LASF210
	.byte	0x1
	.2byte	0xe5a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1d
	.4byte	.LASF211
	.byte	0x1
	.2byte	0xe5a
	.4byte	0xd25
	.uleb128 0x1
	.byte	0x57
	.uleb128 0x1d
	.4byte	.LASF28
	.byte	0x1
	.2byte	0xe5a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x56
	.uleb128 0x1d
	.4byte	.LASF212
	.byte	0x1
	.2byte	0xe5a
	.4byte	0x65
	.uleb128 0x1
	.byte	0x55
	.uleb128 0x32
	.4byte	.LVL100
	.4byte	0x11f7
	.uleb128 0x32
	.4byte	.LVL101
	.4byte	0x1227
	.byte	0
	.uleb128 0x29
	.4byte	.LASF266
	.byte	0x1
	.2byte	0xe8b
	.4byte	.LFB247
	.4byte	.LFE247-.LFB247
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x2117
	.uleb128 0x3b
	.ascii	"w\000"
	.byte	0x1
	.2byte	0xe8d
	.4byte	0x65
	.4byte	0xb02100
	.uleb128 0x3b
	.ascii	"w1\000"
	.byte	0x1
	.2byte	0xe8d
	.4byte	0x65
	.4byte	0xb03100
	.uleb128 0x3b
	.ascii	"w2\000"
	.byte	0x1
	.2byte	0xe8d
	.4byte	0x65
	.4byte	0x1604200
	.uleb128 0x3b
	.ascii	"w3\000"
	.byte	0x1
	.2byte	0xe8d
	.4byte	0x65
	.4byte	0x2c00210
	.uleb128 0x3c
	.ascii	"h\000"
	.byte	0x1
	.2byte	0xe8d
	.4byte	0x65
	.2byte	0x8000
	.uleb128 0x3b
	.ascii	"q1\000"
	.byte	0x1
	.2byte	0xe8d
	.4byte	0x65
	.4byte	0xb03001
	.uleb128 0x3b
	.ascii	"q2\000"
	.byte	0x1
	.2byte	0xe8d
	.4byte	0x65
	.4byte	0x1604002
	.uleb128 0x3b
	.ascii	"q3\000"
	.byte	0x1
	.2byte	0xe8d
	.4byte	0x65
	.4byte	0x2c00210
	.uleb128 0x2a
	.ascii	"wp\000"
	.byte	0x1
	.2byte	0xe8e
	.4byte	0xd25
	.4byte	.LLST28
	.uleb128 0x3d
	.4byte	.LASF267
	.byte	0x1
	.2byte	0xe8f
	.4byte	0xd25
	.4byte	0x400000
	.uleb128 0x31
	.4byte	0xc87
	.4byte	.LBB66
	.4byte	.LBE66-.LBB66
	.byte	0x1
	.2byte	0xe92
	.4byte	0x1fbb
	.uleb128 0x3e
	.4byte	.LBB67
	.4byte	.LBE67-.LBB67
	.uleb128 0x28
	.4byte	0xc94
	.4byte	.LLST29
	.uleb128 0x22
	.4byte	.LVL105
	.4byte	0x1257
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x2
	.byte	0x74
	.sleb128 1
	.byte	0
	.byte	0
	.byte	0
	.uleb128 0x31
	.4byte	0xc7e
	.4byte	.LBB68
	.4byte	.LBE68-.LBB68
	.byte	0x1
	.2byte	0xe94
	.4byte	0x2006
	.uleb128 0x31
	.4byte	0xc56
	.4byte	.LBB70
	.4byte	.LBE70-.LBB70
	.byte	0x1
	.2byte	0x5e0
	.4byte	0x1ffc
	.uleb128 0x22
	.4byte	.LVL108
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC9
	.byte	0
	.byte	0
	.uleb128 0x32
	.4byte	.LVL107
	.4byte	0x166a
	.byte	0
	.uleb128 0x31
	.4byte	0xc6c
	.4byte	.LBB72
	.4byte	.LBE72-.LBB72
	.byte	0x1
	.2byte	0xe96
	.4byte	0x203d
	.uleb128 0x2c
	.4byte	.LVL110
	.4byte	0x12eb
	.4byte	0x202d
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x30
	.byte	0
	.uleb128 0x22
	.4byte	.LVL111
	.4byte	0x12eb
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x31
	.byte	0
	.byte	0
	.uleb128 0x31
	.4byte	0xc75
	.4byte	.LBB74
	.4byte	.LBE74-.LBB74
	.byte	0x1
	.2byte	0xec9
	.4byte	0x205b
	.uleb128 0x32
	.4byte	.LVL112
	.4byte	0x14fa
	.byte	0
	.uleb128 0x31
	.4byte	0xc6c
	.4byte	.LBB76
	.4byte	.LBE76-.LBB76
	.byte	0x1
	.2byte	0xed9
	.4byte	0x2093
	.uleb128 0x2c
	.4byte	.LVL116
	.4byte	0x12eb
	.4byte	0x2083
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x2
	.byte	0x76
	.sleb128 0
	.byte	0
	.uleb128 0x22
	.4byte	.LVL117
	.4byte	0x12eb
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x31
	.byte	0
	.byte	0
	.uleb128 0x32
	.4byte	.LVL102
	.4byte	0x11d2
	.uleb128 0x32
	.4byte	.LVL109
	.4byte	0x17ac
	.uleb128 0x32
	.4byte	.LVL114
	.4byte	0x1e32
	.uleb128 0x2c
	.4byte	.LVL118
	.4byte	0x244a
	.4byte	0x20ca
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC13
	.byte	0
	.uleb128 0x2c
	.4byte	.LVL119
	.4byte	0x244a
	.4byte	0x20fe
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC14
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x7
	.byte	0x75
	.sleb128 -4194304
	.byte	0x32
	.byte	0x25
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x53
	.uleb128 0x2
	.byte	0x77
	.sleb128 0
	.uleb128 0x23
	.uleb128 0x2
	.byte	0x7d
	.sleb128 0
	.uleb128 0x2
	.byte	0x75
	.sleb128 0
	.byte	0
	.uleb128 0x2d
	.4byte	.LVL121
	.4byte	0x244a
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x50
	.uleb128 0x1
	.byte	0x32
	.uleb128 0x23
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x5
	.byte	0x3
	.4byte	.LC15
	.byte	0
	.byte	0
	.uleb128 0x3b
	.ascii	"cc\000"
	.byte	0x3
	.2byte	0x254
	.4byte	0x212c
	.4byte	0x20000000
	.uleb128 0x5
	.byte	0x4
	.4byte	0xae5
	.uleb128 0x3f
	.4byte	0x2126
	.uleb128 0x3b
	.ascii	"tc\000"
	.byte	0x3
	.2byte	0x255
	.4byte	0x212c
	.4byte	0x21000000
	.uleb128 0x3b
	.ascii	"tc1\000"
	.byte	0x3
	.2byte	0x256
	.4byte	0x212c
	.4byte	0x21000000
	.uleb128 0x3b
	.ascii	"tc2\000"
	.byte	0x3
	.2byte	0x257
	.4byte	0x212c
	.4byte	0x21000020
	.uleb128 0x3b
	.ascii	"vic\000"
	.byte	0x3
	.2byte	0x258
	.4byte	0x212c
	.4byte	0x1f000000
	.uleb128 0x3b
	.ascii	"dma\000"
	.byte	0x3
	.2byte	0x259
	.4byte	0x212c
	.4byte	0x40000000
	.uleb128 0x40
	.ascii	"sc\000"
	.byte	0x3
	.2byte	0x25b
	.4byte	0x212c
	.sleb128 -503316480
	.uleb128 0x40
	.ascii	"rtr\000"
	.byte	0x3
	.2byte	0x25c
	.4byte	0x212c
	.sleb128 -520093696
	.uleb128 0x40
	.ascii	"er\000"
	.byte	0x3
	.2byte	0x25d
	.4byte	0x212c
	.sleb128 -469712896
	.uleb128 0x40
	.ascii	"mc\000"
	.byte	0x3
	.2byte	0x25e
	.4byte	0x212c
	.sleb128 -536870912
	.uleb128 0x40
	.ascii	"wd\000"
	.byte	0x3
	.2byte	0x25f
	.4byte	0x212c
	.sleb128 -486539264
	.uleb128 0x3d
	.4byte	.LASF248
	.byte	0x3
	.2byte	0x261
	.4byte	0x21e1
	.4byte	0x60000000
	.uleb128 0x3f
	.4byte	0x545
	.uleb128 0x41
	.4byte	.LASF268
	.byte	0x3
	.2byte	0x262
	.4byte	0x21e1
	.sleb128 -452984832
	.uleb128 0x41
	.4byte	.LASF269
	.byte	0x3
	.2byte	0x264
	.4byte	0x21e1
	.sleb128 -520077312
	.uleb128 0x41
	.4byte	.LASF270
	.byte	0x3
	.2byte	0x265
	.4byte	0x21e1
	.sleb128 -520060928
	.uleb128 0x41
	.4byte	.LASF271
	.byte	0x3
	.2byte	0x266
	.4byte	0x21e1
	.sleb128 -520044544
	.uleb128 0x41
	.4byte	.LASF272
	.byte	0x3
	.2byte	0x267
	.4byte	0x21e1
	.sleb128 -520028160
	.uleb128 0x41
	.4byte	.LASF273
	.byte	0x3
	.2byte	0x269
	.4byte	0x2252
	.sleb128 -469762048
	.uleb128 0x5
	.byte	0x4
	.4byte	0x97
	.uleb128 0x3f
	.4byte	0x224c
	.uleb128 0x41
	.4byte	.LASF274
	.byte	0x3
	.2byte	0x26a
	.4byte	0x2252
	.sleb128 -469745664
	.uleb128 0x41
	.4byte	.LASF275
	.byte	0x3
	.2byte	0x26b
	.4byte	0x21e1
	.sleb128 -469729280
	.uleb128 0x42
	.4byte	.LASF63
	.byte	0x4
	.2byte	0x2bb
	.4byte	0x228c
	.byte	0x20
	.uleb128 0x5
	.byte	0x4
	.4byte	0x560
	.uleb128 0x3f
	.4byte	0x2286
	.uleb128 0x40
	.ascii	"sv\000"
	.byte	0x4
	.2byte	0x423
	.4byte	0x22a7
	.sleb128 -452952320
	.uleb128 0x5
	.byte	0x4
	.4byte	0xb0c
	.uleb128 0x3f
	.4byte	0x22a1
	.uleb128 0x41
	.4byte	.LASF276
	.byte	0x4
	.2byte	0x427
	.4byte	0x22bd
	.sleb128 -452956160
	.uleb128 0x3f
	.4byte	0x705
	.uleb128 0x41
	.4byte	.LASF277
	.byte	0x4
	.2byte	0x429
	.4byte	0x21e1
	.sleb128 -452952096
	.uleb128 0x41
	.4byte	.LASF278
	.byte	0x4
	.2byte	0x42a
	.4byte	0x21e1
	.sleb128 -452952416
	.uleb128 0x41
	.4byte	.LASF279
	.byte	0x4
	.2byte	0x42b
	.4byte	0x21e1
	.sleb128 -452952352
	.uleb128 0x41
	.4byte	.LASF280
	.byte	0x4
	.2byte	0x42e
	.4byte	0x21e1
	.sleb128 -452953856
	.uleb128 0x43
	.4byte	.LASF99
	.byte	0x1
	.byte	0xdf
	.4byte	0x65
	.uleb128 0x5
	.byte	0x3
	.4byte	time
	.uleb128 0x1d
	.4byte	.LASF281
	.byte	0x1
	.2byte	0x1d7
	.4byte	0xd25
	.uleb128 0x5
	.byte	0x3
	.4byte	__op__
	.uleb128 0x1d
	.4byte	.LASF282
	.byte	0x1
	.2byte	0x1d8
	.4byte	0xd25
	.uleb128 0x5
	.byte	0x3
	.4byte	__ip__
	.uleb128 0x1d
	.4byte	.LASF283
	.byte	0x1
	.2byte	0x1d9
	.4byte	0x65
	.uleb128 0x5
	.byte	0x3
	.4byte	__rowlets
	.uleb128 0x1d
	.4byte	.LASF284
	.byte	0x1
	.2byte	0x1da
	.4byte	0x65
	.uleb128 0x5
	.byte	0x3
	.4byte	__synapses
	.uleb128 0xb
	.4byte	0x236f
	.4byte	0x236f
	.uleb128 0xc
	.4byte	0x149
	.byte	0x8
	.byte	0
	.uleb128 0x3f
	.4byte	0x41
	.uleb128 0x1d
	.4byte	.LASF285
	.byte	0x1
	.2byte	0x538
	.4byte	0x2386
	.uleb128 0x5
	.byte	0x3
	.4byte	__log_size_to_burst
	.uleb128 0x3f
	.4byte	0x235f
	.uleb128 0xb
	.4byte	0x239b
	.4byte	0x239b
	.uleb128 0xc
	.4byte	0x149
	.byte	0x1f
	.byte	0
	.uleb128 0x3f
	.4byte	0x65
	.uleb128 0x1d
	.4byte	.LASF286
	.byte	0x1
	.2byte	0x59d
	.4byte	0x23b2
	.uleb128 0x5
	.byte	0x3
	.4byte	__jump_table
	.uleb128 0x3f
	.4byte	0x238b
	.uleb128 0xb
	.4byte	0x239b
	.4byte	0x23c7
	.uleb128 0xc
	.4byte	0x149
	.byte	0x7
	.byte	0
	.uleb128 0x44
	.4byte	.LASF287
	.byte	0x1
	.2byte	0x5e4
	.4byte	0x23d3
	.uleb128 0x3f
	.4byte	0x23b7
	.uleb128 0xb
	.4byte	0x65
	.4byte	0x23e8
	.uleb128 0xc
	.4byte	0x149
	.byte	0x3e
	.byte	0
	.uleb128 0x1d
	.4byte	.LASF288
	.byte	0x1
	.2byte	0x615
	.4byte	0x23d8
	.uleb128 0x5
	.byte	0x3
	.4byte	__control_synapse
	.uleb128 0xb
	.4byte	0x6c6
	.4byte	0x2405
	.uleb128 0x45
	.byte	0
	.uleb128 0x46
	.4byte	.LASF289
	.byte	0x4
	.2byte	0x43f
	.4byte	0x23fa
	.uleb128 0xb
	.4byte	0x65
	.4byte	0x2422
	.uleb128 0x47
	.4byte	0x149
	.2byte	0x521
	.byte	0
	.uleb128 0x48
	.ascii	"tmp\000"
	.byte	0x1
	.2byte	0x22b
	.4byte	0x2411
	.uleb128 0x5
	.byte	0x3
	.4byte	tmp
	.uleb128 0x49
	.4byte	.LASF296
	.byte	0x1
	.2byte	0x439
	.4byte	.LASF296
	.4byte	0xbaa
	.uleb128 0x5
	.byte	0x3
	.4byte	circular_buffer_state
	.uleb128 0x4a
	.4byte	.LASF297
	.4byte	.LASF297
	.byte	0x4
	.2byte	0x704
	.byte	0
	.section	.debug_abbrev,"",%progbits
.Ldebug_abbrev0:
	.uleb128 0x1
	.uleb128 0x11
	.byte	0x1
	.uleb128 0x25
	.uleb128 0xe
	.uleb128 0x13
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x1b
	.uleb128 0xe
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x10
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x2
	.uleb128 0x24
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x3e
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0xe
	.byte	0
	.byte	0
	.uleb128 0x3
	.uleb128 0x16
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x4
	.uleb128 0x24
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x3e
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0x8
	.byte	0
	.byte	0
	.uleb128 0x5
	.uleb128 0xf
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x6
	.uleb128 0x15
	.byte	0
	.uleb128 0x27
	.uleb128 0x19
	.byte	0
	.byte	0
	.uleb128 0x7
	.uleb128 0x13
	.byte	0x1
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x8
	.uleb128 0xd
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x38
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x9
	.uleb128 0x16
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xa
	.uleb128 0xd
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x38
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0xb
	.uleb128 0x1
	.byte	0x1
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xc
	.uleb128 0x21
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2f
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0xd
	.uleb128 0x13
	.byte	0x1
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0xb
	.uleb128 0x5
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xe
	.uleb128 0xd
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x38
	.uleb128 0x5
	.byte	0
	.byte	0
	.uleb128 0xf
	.uleb128 0x13
	.byte	0x1
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x10
	.uleb128 0x21
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x11
	.uleb128 0x35
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x12
	.uleb128 0xf
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x13
	.uleb128 0x13
	.byte	0x1
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0xb
	.uleb128 0x5
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x14
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x20
	.uleb128 0xb
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x15
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x16
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x20
	.uleb128 0xb
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x17
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x18
	.uleb128 0x2e
	.byte	0
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x20
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x19
	.uleb128 0x2e
	.byte	0
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x20
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x1a
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x20
	.uleb128 0xb
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x1b
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x1c
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x6e
	.uleb128 0xe
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2117
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x1d
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x1e
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x1f
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2117
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x20
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x21
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x22
	.uleb128 0x4109
	.byte	0x1
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x31
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x23
	.uleb128 0x410a
	.byte	0
	.uleb128 0x2
	.uleb128 0x18
	.uleb128 0x2111
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x24
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0x6
	.byte	0
	.byte	0
	.uleb128 0x25
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x26
	.uleb128 0xa
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x11
	.uleb128 0x1
	.byte	0
	.byte	0
	.uleb128 0x27
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x31
	.uleb128 0x13
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2117
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x28
	.uleb128 0x34
	.byte	0
	.uleb128 0x31
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x29
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2117
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x2a
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x2b
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x2c
	.uleb128 0x4109
	.byte	0x1
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x31
	.uleb128 0x13
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x2d
	.uleb128 0x4109
	.byte	0x1
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x2115
	.uleb128 0x19
	.uleb128 0x31
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x2e
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2117
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x2f
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x30
	.uleb128 0x5
	.byte	0
	.uleb128 0x31
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x31
	.uleb128 0x1d
	.byte	0x1
	.uleb128 0x31
	.uleb128 0x13
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x58
	.uleb128 0xb
	.uleb128 0x59
	.uleb128 0x5
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x32
	.uleb128 0x4109
	.byte	0
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x31
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x33
	.uleb128 0x4109
	.byte	0
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x2115
	.uleb128 0x19
	.uleb128 0x31
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x34
	.uleb128 0x2e
	.byte	0
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2117
	.uleb128 0x19
	.byte	0
	.byte	0
	.uleb128 0x35
	.uleb128 0x1d
	.byte	0x1
	.uleb128 0x31
	.uleb128 0x13
	.uleb128 0x52
	.uleb128 0x1
	.uleb128 0x55
	.uleb128 0x17
	.uleb128 0x58
	.uleb128 0xb
	.uleb128 0x59
	.uleb128 0x5
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x36
	.uleb128 0x2e
	.byte	0
	.uleb128 0x31
	.uleb128 0x13
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2117
	.uleb128 0x19
	.byte	0
	.byte	0
	.uleb128 0x37
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x38
	.uleb128 0xa
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.byte	0
	.byte	0
	.uleb128 0x39
	.uleb128 0xa
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x11
	.uleb128 0x1
	.byte	0
	.byte	0
	.uleb128 0x3a
	.uleb128 0x2e
	.byte	0
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x6e
	.uleb128 0xe
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2117
	.uleb128 0x19
	.byte	0
	.byte	0
	.uleb128 0x3b
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0x6
	.byte	0
	.byte	0
	.uleb128 0x3c
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0x5
	.byte	0
	.byte	0
	.uleb128 0x3d
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0x6
	.byte	0
	.byte	0
	.uleb128 0x3e
	.uleb128 0xb
	.byte	0x1
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.byte	0
	.byte	0
	.uleb128 0x3f
	.uleb128 0x26
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x40
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0xd
	.byte	0
	.byte	0
	.uleb128 0x41
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0xd
	.byte	0
	.byte	0
	.uleb128 0x42
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x43
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x44
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x45
	.uleb128 0x21
	.byte	0
	.byte	0
	.byte	0
	.uleb128 0x46
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3c
	.uleb128 0x19
	.byte	0
	.byte	0
	.uleb128 0x47
	.uleb128 0x21
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2f
	.uleb128 0x5
	.byte	0
	.byte	0
	.uleb128 0x48
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x49
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x6e
	.uleb128 0xe
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x4a
	.uleb128 0x2e
	.byte	0
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3c
	.uleb128 0x19
	.uleb128 0x6e
	.uleb128 0xe
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.byte	0
	.byte	0
	.byte	0
	.section	.debug_loc,"",%progbits
.Ldebug_loc0:
.LLST0:
	.4byte	.LVL0-.Ltext0
	.4byte	.LVL1-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL1-.Ltext0
	.4byte	.LFE193-.Ltext0
	.2byte	0x4
	.byte	0xf3
	.uleb128 0x1
	.byte	0x50
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST1:
	.4byte	.LVL9-.Ltext0
	.4byte	.LVL10-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	0
	.4byte	0
.LLST2:
	.4byte	.LVL11-.Ltext0
	.4byte	.LVL12-.Ltext0
	.2byte	0x2
	.byte	0x3f
	.byte	0x9f
	.4byte	.LVL12-.Ltext0
	.4byte	.LVL13-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL13-.Ltext0
	.4byte	.LVL14-1-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL14-1-.Ltext0
	.4byte	.LVL14-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 1
	.byte	0x9f
	.4byte	.LVL14-.Ltext0
	.4byte	.LFE198-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	0
	.4byte	0
.LLST3:
	.4byte	.LVL15-.Ltext0
	.4byte	.LVL17-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL17-.Ltext0
	.4byte	.LVL20-.Ltext0
	.2byte	0x1
	.byte	0x56
	.4byte	.LVL20-.Ltext0
	.4byte	.LVL21-1-.Ltext0
	.2byte	0x1
	.byte	0x52
	.4byte	.LVL21-1-.Ltext0
	.4byte	.LVL23-.Ltext0
	.2byte	0x1
	.byte	0x56
	.4byte	.LVL23-.Ltext0
	.4byte	.LFE199-.Ltext0
	.2byte	0x4
	.byte	0xf3
	.uleb128 0x1
	.byte	0x50
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST4:
	.4byte	.LVL16-.Ltext0
	.4byte	.LVL17-.Ltext0
	.2byte	0x2
	.byte	0x30
	.byte	0x9f
	.4byte	.LVL17-.Ltext0
	.4byte	.LVL23-.Ltext0
	.2byte	0x1
	.byte	0x58
	.4byte	0
	.4byte	0
.LLST5:
	.4byte	.LVL17-.Ltext0
	.4byte	.LVL18-.Ltext0
	.2byte	0x2
	.byte	0x30
	.byte	0x9f
	.4byte	.LVL18-.Ltext0
	.4byte	.LVL19-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL19-.Ltext0
	.4byte	.LVL21-1-.Ltext0
	.2byte	0x1
	.byte	0x53
	.4byte	.LVL21-1-.Ltext0
	.4byte	.LVL21-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 -1
	.byte	0x9f
	.4byte	.LVL21-.Ltext0
	.4byte	.LVL23-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	0
	.4byte	0
.LLST6:
	.4byte	.LVL16-.Ltext0
	.4byte	.LVL17-.Ltext0
	.2byte	0x1
	.byte	0x55
	.4byte	.LVL17-.Ltext0
	.4byte	.LVL20-.Ltext0
	.2byte	0x14
	.byte	0xc
	.4byte	0x406000
	.byte	0xc
	.4byte	0x404000
	.byte	0x76
	.sleb128 0
	.byte	0x30
	.byte	0x2e
	.byte	0x28
	.2byte	0x1
	.byte	0x16
	.byte	0x13
	.byte	0x9f
	.4byte	.LVL20-.Ltext0
	.4byte	.LVL21-1-.Ltext0
	.2byte	0x14
	.byte	0xc
	.4byte	0x406000
	.byte	0xc
	.4byte	0x404000
	.byte	0x72
	.sleb128 0
	.byte	0x30
	.byte	0x2e
	.byte	0x28
	.2byte	0x1
	.byte	0x16
	.byte	0x13
	.byte	0x9f
	.4byte	.LVL21-1-.Ltext0
	.4byte	.LVL23-.Ltext0
	.2byte	0x14
	.byte	0xc
	.4byte	0x406000
	.byte	0xc
	.4byte	0x404000
	.byte	0x76
	.sleb128 0
	.byte	0x30
	.byte	0x2e
	.byte	0x28
	.2byte	0x1
	.byte	0x16
	.byte	0x13
	.byte	0x9f
	.4byte	.LVL23-.Ltext0
	.4byte	.LFE199-.Ltext0
	.2byte	0x15
	.byte	0xc
	.4byte	0x406000
	.byte	0xc
	.4byte	0x404000
	.byte	0xf3
	.uleb128 0x1
	.byte	0x50
	.byte	0x30
	.byte	0x2e
	.byte	0x28
	.2byte	0x1
	.byte	0x16
	.byte	0x13
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST7:
	.4byte	.LVL26-.Ltext0
	.4byte	.LVL27-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL27-.Ltext0
	.4byte	.LFE201-.Ltext0
	.2byte	0x4
	.byte	0xf3
	.uleb128 0x1
	.byte	0x50
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST8:
	.4byte	.LVL28-.Ltext0
	.4byte	.LVL29-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL29-.Ltext0
	.4byte	.LFE202-.Ltext0
	.2byte	0x4
	.byte	0xf3
	.uleb128 0x1
	.byte	0x50
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST9:
	.4byte	.LVL30-.Ltext0
	.4byte	.LVL31-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL31-.Ltext0
	.4byte	.LFE203-.Ltext0
	.2byte	0x4
	.byte	0xf3
	.uleb128 0x1
	.byte	0x50
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST10:
	.4byte	.LVL32-.Ltext0
	.4byte	.LVL33-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL33-.Ltext0
	.4byte	.LFE204-.Ltext0
	.2byte	0x4
	.byte	0xf3
	.uleb128 0x1
	.byte	0x50
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST11:
	.4byte	.LVL34-.Ltext0
	.4byte	.LVL35-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL35-.Ltext0
	.4byte	.LFE205-.Ltext0
	.2byte	0x4
	.byte	0xf3
	.uleb128 0x1
	.byte	0x50
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST12:
	.4byte	.LVL40-.Ltext0
	.4byte	.LVL43-1-.Ltext0
	.2byte	0x1
	.byte	0x52
	.4byte	.LVL44-.Ltext0
	.4byte	.LVL45-1-.Ltext0
	.2byte	0x1
	.byte	0x52
	.4byte	.LVL45-1-.Ltext0
	.4byte	.LVL47-.Ltext0
	.2byte	0xa
	.byte	0x78
	.sleb128 0
	.byte	0x44
	.byte	0x24
	.byte	0x44
	.byte	0x25
	.byte	0x75
	.sleb128 0
	.byte	0x21
	.byte	0x9f
	.4byte	.LVL47-.Ltext0
	.4byte	.LVL49-1-.Ltext0
	.2byte	0x1
	.byte	0x52
	.4byte	0
	.4byte	0
.LLST13:
	.4byte	.LVL36-.Ltext0
	.4byte	.LVL37-.Ltext0
	.2byte	0x1
	.byte	0x5c
	.4byte	.LVL37-.Ltext0
	.4byte	.LVL41-.Ltext0
	.2byte	0x2
	.byte	0x73
	.sleb128 0
	.4byte	.LVL41-.Ltext0
	.4byte	.LVL42-.Ltext0
	.2byte	0x6
	.byte	0x3
	.4byte	__ip__
	.byte	0x6
	.4byte	0
	.4byte	0
.LLST14:
	.4byte	.LVL38-.Ltext0
	.4byte	.LVL48-.Ltext0
	.2byte	0x1
	.byte	0x58
	.4byte	0
	.4byte	0
.LLST15:
	.4byte	.LVL38-.Ltext0
	.4byte	.LVL48-.Ltext0
	.2byte	0x1
	.byte	0x57
	.4byte	0
	.4byte	0
.LLST16:
	.4byte	.LVL39-.Ltext0
	.4byte	.LVL46-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	0
	.4byte	0
.LLST17:
	.4byte	.LVL51-.Ltext0
	.4byte	.LVL54-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL60-.Ltext0
	.4byte	.LVL63-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL63-.Ltext0
	.4byte	.LVL64-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 -1
	.byte	0x9f
	.4byte	.LVL64-.Ltext0
	.4byte	.LVL67-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL67-.Ltext0
	.4byte	.LVL68-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 -1
	.byte	0x9f
	.4byte	.LVL68-.Ltext0
	.4byte	.LFE207-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	0
	.4byte	0
.LLST18:
	.4byte	.LVL52-.Ltext0
	.4byte	.LVL59-.Ltext0
	.2byte	0x1
	.byte	0x56
	.4byte	.LVL60-.Ltext0
	.4byte	.LFE207-.Ltext0
	.2byte	0x1
	.byte	0x56
	.4byte	0
	.4byte	0
.LLST19:
	.4byte	.LVL53-.Ltext0
	.4byte	.LVL55-.Ltext0
	.2byte	0x2
	.byte	0x30
	.byte	0x9f
	.4byte	.LVL55-.Ltext0
	.4byte	.LVL56-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL56-.Ltext0
	.4byte	.LVL57-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 -1
	.byte	0x9f
	.4byte	.LVL57-.Ltext0
	.4byte	.LVL58-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	0
	.4byte	0
.LLST20:
	.4byte	.LVL50-.Ltext0
	.4byte	.LVL52-.Ltext0
	.2byte	0x1
	.byte	0x56
	.4byte	.LVL59-.Ltext0
	.4byte	.LVL60-.Ltext0
	.2byte	0x1
	.byte	0x56
	.4byte	.LVL61-.Ltext0
	.4byte	.LVL62-.Ltext0
	.2byte	0x1
	.byte	0x5c
	.4byte	.LVL62-.Ltext0
	.4byte	.LVL63-1-.Ltext0
	.2byte	0x1
	.byte	0x52
	.4byte	0
	.4byte	0
.LLST21:
	.4byte	.LVL65-.Ltext0
	.4byte	.LVL66-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	0
	.4byte	0
.LLST22:
	.4byte	.LVL70-.Ltext0
	.4byte	.LVL71-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL71-.Ltext0
	.4byte	.LFE214-.Ltext0
	.2byte	0x1
	.byte	0x53
	.4byte	0
	.4byte	0
.LLST23:
	.4byte	.LVL74-.Ltext0
	.4byte	.LVL75-.Ltext0
	.2byte	0x2
	.byte	0x30
	.byte	0x9f
	.4byte	.LVL75-.Ltext0
	.4byte	.LFE216-.Ltext0
	.2byte	0x1
	.byte	0x5a
	.4byte	0
	.4byte	0
.LLST24:
	.4byte	.LVL75-.Ltext0
	.4byte	.LVL76-.Ltext0
	.2byte	0x2
	.byte	0x30
	.byte	0x9f
	.4byte	.LVL76-.Ltext0
	.4byte	.LFE216-.Ltext0
	.2byte	0x1
	.byte	0x55
	.4byte	0
	.4byte	0
.LLST25:
	.4byte	.LVL76-.Ltext0
	.4byte	.LVL77-.Ltext0
	.2byte	0x2
	.byte	0x30
	.byte	0x9f
	.4byte	.LVL77-.Ltext0
	.4byte	.LVL78-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 -1
	.byte	0x9f
	.4byte	.LVL78-.Ltext0
	.4byte	.LVL81-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL81-.Ltext0
	.4byte	.LVL82-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 -1
	.byte	0x9f
	.4byte	.LVL82-.Ltext0
	.4byte	.LVL83-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL83-.Ltext0
	.4byte	.LFE216-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 -1
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST26:
	.4byte	.LVL87-.Ltext0
	.4byte	.LVL88-.Ltext0
	.2byte	0x2
	.byte	0x30
	.byte	0x9f
	.4byte	.LVL88-.Ltext0
	.4byte	.LVL89-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL89-.Ltext0
	.4byte	.LVL90-1-.Ltext0
	.2byte	0x1
	.byte	0x53
	.4byte	.LVL90-1-.Ltext0
	.4byte	.LVL90-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 -1
	.byte	0x9f
	.4byte	.LVL90-.Ltext0
	.4byte	.LVL91-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	0
	.4byte	0
.LLST27:
	.4byte	.LVL99-.Ltext0
	.4byte	.LVL100-1-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL100-1-.Ltext0
	.4byte	.LFE246-.Ltext0
	.2byte	0x4
	.byte	0xf3
	.uleb128 0x1
	.byte	0x50
	.byte	0x9f
	.4byte	0
	.4byte	0
.LLST28:
	.4byte	.LVL112-.Ltext0
	.4byte	.LVL113-.Ltext0
	.2byte	0x4
	.byte	0x40
	.byte	0x42
	.byte	0x24
	.byte	0x9f
	.4byte	.LVL113-.Ltext0
	.4byte	.LVL114-1-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL114-.Ltext0
	.4byte	.LVL115-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL115-.Ltext0
	.4byte	.LVL120-.Ltext0
	.2byte	0x1
	.byte	0x55
	.4byte	0
	.4byte	0
.LLST29:
	.4byte	.LVL102-.Ltext0
	.4byte	.LVL103-.Ltext0
	.2byte	0x2
	.byte	0x3f
	.byte	0x9f
	.4byte	.LVL103-.Ltext0
	.4byte	.LVL104-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	.LVL104-.Ltext0
	.4byte	.LVL105-1-.Ltext0
	.2byte	0x1
	.byte	0x50
	.4byte	.LVL105-1-.Ltext0
	.4byte	.LVL105-.Ltext0
	.2byte	0x3
	.byte	0x74
	.sleb128 1
	.byte	0x9f
	.4byte	.LVL105-.Ltext0
	.4byte	.LVL106-.Ltext0
	.2byte	0x1
	.byte	0x54
	.4byte	0
	.4byte	0
	.section	.debug_aranges,"",%progbits
	.4byte	0x1c
	.2byte	0x2
	.4byte	.Ldebug_info0
	.byte	0x4
	.byte	0
	.2byte	0
	.2byte	0
	.4byte	.Ltext0
	.4byte	.Letext0-.Ltext0
	.4byte	0
	.4byte	0
	.section	.debug_ranges,"",%progbits
.Ldebug_ranges0:
	.4byte	.LBB62-.Ltext0
	.4byte	.LBE62-.Ltext0
	.4byte	.LBB65-.Ltext0
	.4byte	.LBE65-.Ltext0
	.4byte	0
	.4byte	0
	.section	.debug_line,"",%progbits
.Ldebug_line0:
	.section	.debug_str,"MS",%progbits,1
.LASF104:
	.ascii	"user1\000"
.LASF105:
	.ascii	"user2\000"
.LASF106:
	.ascii	"user3\000"
.LASF103:
	.ascii	"user0\000"
.LASF54:
	.ascii	"last\000"
.LASF114:
	.ascii	"eth_addr\000"
.LASF109:
	.ascii	"p2p_addr\000"
.LASF55:
	.ascii	"free_bytes\000"
.LASF247:
	.ascii	"read_a_rowlet\000"
.LASF89:
	.ascii	"rt_code\000"
.LASF216:
	.ascii	"primary_dispatch_2I\000"
.LASF123:
	.ascii	"ltpc_period\000"
.LASF281:
	.ascii	"__op__\000"
.LASF70:
	.ascii	"irq_vec\000"
.LASF162:
	.ascii	"v2p_map\000"
.LASF194:
	.ascii	"output\000"
.LASF100:
	.ascii	"app_name\000"
.LASF60:
	.ascii	"slot\000"
.LASF101:
	.ascii	"iobuf\000"
.LASF132:
	.ascii	"netinit_bc_wait\000"
.LASF81:
	.ascii	"sark_slot\000"
.LASF171:
	.ascii	"rtr_copy\000"
.LASF39:
	.ascii	"flags\000"
.LASF168:
	.ascii	"sdram_sys\000"
.LASF56:
	.ascii	"buffer\000"
.LASF152:
	.ascii	"link_en\000"
.LASF256:
	.ascii	"__packed_fix_up_4\000"
.LASF140:
	.ascii	"num_buf\000"
.LASF289:
	.ascii	"build_name\000"
.LASF20:
	.ascii	"mem_block\000"
.LASF12:
	.ascii	"unsigned int\000"
.LASF21:
	.ascii	"next\000"
.LASF142:
	.ascii	"soft_wdog\000"
.LASF17:
	.ascii	"int_handler\000"
.LASF145:
	.ascii	"sdram_heap\000"
.LASF237:
	.ascii	"quads\000"
.LASF149:
	.ascii	"boot_sig\000"
.LASF33:
	.ascii	"sema\000"
.LASF68:
	.ascii	"dabt_vec\000"
.LASF62:
	.ascii	"event_vec_t\000"
.LASF222:
	.ascii	"__reserved_dispatch\000"
.LASF226:
	.ascii	"start_timer\000"
.LASF262:
	.ascii	"__standard_rowlet\000"
.LASF82:
	.ascii	"num_events\000"
.LASF200:
	.ascii	"get_index_delay\000"
.LASF78:
	.ascii	"stack_top\000"
.LASF273:
	.ascii	"eth_tx_ram\000"
.LASF248:
	.ascii	"sdram\000"
.LASF283:
	.ascii	"__rowlets\000"
.LASF249:
	.ascii	"dma_scheduler\000"
.LASF202:
	.ascii	"get_delay\000"
.LASF271:
	.ascii	"rtr_mask\000"
.LASF296:
	.ascii	"circular_buffer_state\000"
.LASF191:
	.ascii	"unsigned short _Accum\000"
.LASF159:
	.ascii	"utmp3\000"
.LASF267:
	.ascii	"initial_wp\000"
.LASF189:
	.ascii	"unsigned _Fract\000"
.LASF253:
	.ascii	"__saturation_detected_1\000"
.LASF254:
	.ascii	"__saturation_detected_2\000"
.LASF255:
	.ascii	"__saturation_detected_3\000"
.LASF148:
	.ascii	"sysbuf_size\000"
.LASF65:
	.ascii	"undef_vec\000"
.LASF138:
	.ascii	"random\000"
.LASF8:
	.ascii	"uint32_t\000"
.LASF244:
	.ascii	"circular_buffer_initialize\000"
.LASF117:
	.ascii	"p2pb_repeats\000"
.LASF295:
	.ascii	"initialise_ring_buffers\000"
.LASF282:
	.ascii	"__ip__\000"
.LASF93:
	.ascii	"mbox_mp_msg\000"
.LASF221:
	.ascii	"primary_dispatch_3E\000"
.LASF227:
	.ascii	"stop_timer\000"
.LASF38:
	.ascii	"checksum\000"
.LASF290:
	.ascii	"GNU C99 5.4.1 20160919 (release) [ARM/embedded-5-br"
	.ascii	"anch revision 240496] -mthumb-interwork -march=armv"
	.ascii	"5te -g -Ofast -std=gnu99 -ffreestanding -finline-li"
	.ascii	"mit=4\000"
.LASF195:
	.ascii	"base\000"
.LASF23:
	.ascii	"count\000"
.LASF166:
	.ascii	"sdram_base\000"
.LASF84:
	.ascii	"app_flags\000"
.LASF174:
	.ascii	"rtr_free\000"
.LASF184:
	.ascii	"long _Fract\000"
.LASF120:
	.ascii	"tp_scale\000"
.LASF11:
	.ascii	"long long unsigned int\000"
.LASF203:
	.ascii	"odd_word\000"
.LASF208:
	.ascii	"print_jump_tables\000"
.LASF160:
	.ascii	"status_map\000"
.LASF119:
	.ascii	"clk_div\000"
.LASF199:
	.ascii	"circular_buffer_ptr\000"
.LASF27:
	.ascii	"route\000"
.LASF97:
	.ascii	"sw_file\000"
.LASF173:
	.ascii	"alloc_tag\000"
.LASF209:
	.ascii	"ctrl\000"
.LASF99:
	.ascii	"time\000"
.LASF263:
	.ascii	"rowlet_dispatch\000"
.LASF32:
	.ascii	"clean\000"
.LASF115:
	.ascii	"hw_ver\000"
.LASF187:
	.ascii	"long _Accum\000"
.LASF161:
	.ascii	"p2v_map\000"
.LASF218:
	.ascii	"primary_dispatch_0E\000"
.LASF88:
	.ascii	"vcpu\000"
.LASF214:
	.ascii	"primary_dispatch_0I\000"
.LASF280:
	.ascii	"sv_board_info\000"
.LASF110:
	.ascii	"p2p_dims\000"
.LASF257:
	.ascii	"__dense_fix_up_4\000"
.LASF49:
	.ascii	"__PAD1\000"
.LASF137:
	.ascii	"__PAD2\000"
.LASF143:
	.ascii	"__PAD3\000"
.LASF207:
	.ascii	"translate_tmp\000"
.LASF29:
	.ascii	"rtr_entry_t\000"
.LASF22:
	.ascii	"free\000"
.LASF63:
	.ascii	"sark_vec\000"
.LASF206:
	.ascii	"print_ring_buffers\000"
.LASF176:
	.ascii	"shm_buf\000"
.LASF154:
	.ascii	"bt_flags\000"
.LASF230:
	.ascii	"minus1\000"
.LASF219:
	.ascii	"primary_dispatch_1E\000"
.LASF215:
	.ascii	"primary_dispatch_1I\000"
.LASF260:
	.ascii	"dense_256\000"
.LASF232:
	.ascii	"buffer_number\000"
.LASF246:
	.ascii	"set_global_timer\000"
.LASF211:
	.ascii	"jump\000"
.LASF190:
	.ascii	"unsigned long _Fract\000"
.LASF44:
	.ascii	"cmd_rc\000"
.LASF34:
	.ascii	"lead\000"
.LASF287:
	.ascii	"rowlet_subheader_table\000"
.LASF297:
	.ascii	"io_printf\000"
.LASF67:
	.ascii	"pabt_vec\000"
.LASF107:
	.ascii	"char\000"
.LASF150:
	.ascii	"mem_ptr\000"
.LASF139:
	.ascii	"root_chip\000"
.LASF124:
	.ascii	"unix_time\000"
.LASF242:
	.ascii	"table\000"
.LASF220:
	.ascii	"primary_dispatch_2E\000"
.LASF48:
	.ascii	"data\000"
.LASF175:
	.ascii	"p2p_active\000"
.LASF31:
	.ascii	"cores\000"
.LASF183:
	.ascii	"_Fract\000"
.LASF188:
	.ascii	"unsigned short _Fract\000"
.LASF5:
	.ascii	"uint8_t\000"
.LASF245:
	.ascii	"global_timer_tick\000"
.LASF131:
	.ascii	"led_period\000"
.LASF288:
	.ascii	"__control_synapse\000"
.LASF153:
	.ascii	"last_biff_id\000"
.LASF213:
	.ascii	"__synapse_loop\000"
.LASF270:
	.ascii	"rtr_key\000"
.LASF182:
	.ascii	"short _Fract\000"
.LASF3:
	.ascii	"long long int\000"
.LASF144:
	.ascii	"sysram_heap\000"
.LASF151:
	.ascii	"lock\000"
.LASF186:
	.ascii	"_Accum\000"
.LASF217:
	.ascii	"primary_dispatch_3I\000"
.LASF19:
	.ascii	"mem_link\000"
.LASF83:
	.ascii	"app_id\000"
.LASF180:
	.ascii	"board_info\000"
.LASF223:
	.ascii	"printx\000"
.LASF235:
	.ascii	"translate_rowlets\000"
.LASF291:
	.ascii	"std_synapse.c\000"
.LASF79:
	.ascii	"stack_fill\000"
.LASF192:
	.ascii	"unsigned _Accum\000"
.LASF185:
	.ascii	"short _Accum\000"
.LASF135:
	.ascii	"led0\000"
.LASF136:
	.ascii	"led1\000"
.LASF128:
	.ascii	"forward\000"
.LASF45:
	.ascii	"arg1\000"
.LASF46:
	.ascii	"arg2\000"
.LASF47:
	.ascii	"arg3\000"
.LASF35:
	.ascii	"app_data_t\000"
.LASF277:
	.ascii	"sv_srom\000"
.LASF28:
	.ascii	"mask\000"
.LASF146:
	.ascii	"iobuf_size\000"
.LASF141:
	.ascii	"boot_delay\000"
.LASF259:
	.ascii	"__rowlet_dispatch2_3\000"
.LASF225:
	.ascii	"timer_addr\000"
.LASF13:
	.ascii	"uchar\000"
.LASF278:
	.ascii	"sv_random\000"
.LASF197:
	.ascii	"overflows\000"
.LASF241:
	.ascii	"print_primary\000"
.LASF251:
	.ascii	"done\000"
.LASF94:
	.ascii	"mbox_ap_cmd\000"
.LASF69:
	.ascii	"aplx_proc\000"
.LASF18:
	.ascii	"mem_link_t\000"
.LASF156:
	.ascii	"utmp0\000"
.LASF157:
	.ascii	"utmp1\000"
.LASF158:
	.ascii	"utmp2\000"
.LASF96:
	.ascii	"sw_count\000"
.LASF294:
	.ascii	"global_timer_value\000"
.LASF6:
	.ascii	"uint16_t\000"
.LASF275:
	.ascii	"eth_rx_desc\000"
.LASF64:
	.ascii	"reset_vec\000"
.LASF116:
	.ascii	"eth_up\000"
.LASF238:
	.ascii	"__circular_buffer_overflow\000"
.LASF212:
	.ascii	"mask_0x3c\000"
.LASF264:
	.ascii	"process_rowlets\000"
.LASF125:
	.ascii	"tp_timer\000"
.LASF1:
	.ascii	"short int\000"
.LASF177:
	.ascii	"mbox_flags\000"
.LASF169:
	.ascii	"vcpu_base\000"
.LASF172:
	.ascii	"hop_table\000"
.LASF155:
	.ascii	"shm_root\000"
.LASF147:
	.ascii	"sdram_bufs\000"
.LASF266:
	.ascii	"c_main\000"
.LASF2:
	.ascii	"long int\000"
.LASF233:
	.ascii	"get_index\000"
.LASF229:
	.ascii	"delay\000"
.LASF37:
	.ascii	"length\000"
.LASF130:
	.ascii	"peek_time\000"
.LASF87:
	.ascii	"sark_vec_t\000"
.LASF61:
	.ascii	"priority\000"
.LASF170:
	.ascii	"sys_heap\000"
.LASF58:
	.ascii	"event_vec\000"
.LASF85:
	.ascii	"__PAD\000"
.LASF10:
	.ascii	"uint64_t\000"
.LASF30:
	.ascii	"app_data\000"
.LASF52:
	.ascii	"block_t\000"
.LASF252:
	.ascii	"outp\000"
.LASF127:
	.ascii	"mem_clk\000"
.LASF51:
	.ascii	"block\000"
.LASF269:
	.ascii	"rtr_ram\000"
.LASF36:
	.ascii	"sdp_msg\000"
.LASF276:
	.ascii	"sv_vcpu\000"
.LASF72:
	.ascii	"svc_stack\000"
.LASF86:
	.ascii	"event\000"
.LASF16:
	.ascii	"uint64\000"
.LASF293:
	.ascii	"circular_buffer_next\000"
.LASF285:
	.ascii	"__log_size_to_burst\000"
.LASF59:
	.ascii	"proc\000"
.LASF224:
	.ascii	"initialise_timer\000"
.LASF25:
	.ascii	"sizetype\000"
.LASF9:
	.ascii	"long unsigned int\000"
.LASF292:
	.ascii	"/Users/mbassdrl/Github/SpiNNaker/spinnaker_tools/ap"
	.ascii	"ps/synapse\000"
.LASF108:
	.ascii	"vcpu_t\000"
.LASF167:
	.ascii	"sysram_base\000"
.LASF196:
	.ascii	"input\000"
.LASF76:
	.ascii	"code_top\000"
.LASF279:
	.ascii	"sv_vectors\000"
.LASF198:
	.ascii	"circular_buffer_t\000"
.LASF205:
	.ascii	"print_secondary\000"
.LASF4:
	.ascii	"unsigned char\000"
.LASF26:
	.ascii	"rtr_entry\000"
.LASF14:
	.ascii	"ushort\000"
.LASF250:
	.ascii	"Loop\000"
.LASF165:
	.ascii	"board_addr\000"
.LASF95:
	.ascii	"mbox_mp_cmd\000"
.LASF74:
	.ascii	"fiq_stack\000"
.LASF90:
	.ascii	"phys_cpu\000"
.LASF261:
	.ascii	"__long_fixed_rowlet\000"
.LASF163:
	.ascii	"num_cpus\000"
.LASF53:
	.ascii	"first\000"
.LASF98:
	.ascii	"sw_line\000"
.LASF274:
	.ascii	"eth_rx_ram\000"
.LASF234:
	.ascii	"process_quad\000"
.LASF193:
	.ascii	"unsigned long _Accum\000"
.LASF24:
	.ascii	"mem_block_t\000"
.LASF91:
	.ascii	"cpu_state\000"
.LASF179:
	.ascii	"fr_copy\000"
.LASF50:
	.ascii	"sdp_msg_t\000"
.LASF240:
	.ascii	"item\000"
.LASF41:
	.ascii	"srce_port\000"
.LASF40:
	.ascii	"dest_port\000"
.LASF286:
	.ascii	"__jump_table\000"
.LASF228:
	.ascii	"reset_ring_buffer_row\000"
.LASF66:
	.ascii	"svc_vec\000"
.LASF80:
	.ascii	"num_msgs\000"
.LASF239:
	.ascii	"circular_buffer_output\000"
.LASF134:
	.ascii	"p2p_root\000"
.LASF71:
	.ascii	"fiq_vec\000"
.LASF133:
	.ascii	"netinit_phase\000"
.LASF0:
	.ascii	"signed char\000"
.LASF7:
	.ascii	"short unsigned int\000"
.LASF204:
	.ascii	"current\000"
.LASF15:
	.ascii	"uint\000"
.LASF236:
	.ascii	"odds\000"
.LASF111:
	.ascii	"dbg_addr\000"
.LASF75:
	.ascii	"stack_size\000"
.LASF57:
	.ascii	"heap_t\000"
.LASF113:
	.ascii	"last_id\000"
.LASF43:
	.ascii	"srce_addr\000"
.LASF42:
	.ascii	"dest_addr\000"
.LASF243:
	.ascii	"print_synapse_jump_table\000"
.LASF181:
	.ascii	"sv_t\000"
.LASF77:
	.ascii	"heap_base\000"
.LASF118:
	.ascii	"p2p_sql\000"
.LASF92:
	.ascii	"mbox_ap_msg\000"
.LASF210:
	.ascii	"time_base\000"
.LASF164:
	.ascii	"rom_cpus\000"
.LASF122:
	.ascii	"time_ms\000"
.LASF272:
	.ascii	"rtr_p2p\000"
.LASF265:
	.ascii	"__wp\000"
.LASF112:
	.ascii	"p2p_up\000"
.LASF73:
	.ascii	"irq_stack\000"
.LASF268:
	.ascii	"sysram\000"
.LASF126:
	.ascii	"cpu_clk\000"
.LASF121:
	.ascii	"clock_ms\000"
.LASF231:
	.ascii	"print_ring_buffer\000"
.LASF178:
	.ascii	"ip_addr\000"
.LASF129:
	.ascii	"retry\000"
.LASF201:
	.ascii	"get_weight\000"
.LASF284:
	.ascii	"__synapses\000"
.LASF258:
	.ascii	"__synapse_head\000"
.LASF102:
	.ascii	"sw_ver\000"
	.ident	"GCC: (GNU Tools for ARM Embedded Processors) 5.4.1 20160919 (release) [ARM/embedded-5-branch revision 240496]"
