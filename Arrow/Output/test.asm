.global _start
.section .text.BSP__boot_segment_1296
.global BSP__boot_segment_1296
BSP__boot_segment_1296:
_start:
     label_4844_BSP__boot_segment_code_segment: // starting label for BSP__boot_segment code Segment                        // ( From memlayout/segment_manager.py, line 105)
     // ========================= BSP BOOT CODE - start =====================                                               // ( From test_stage/test_boot.py, line 203)
     // Load the stack pointer (address of 2305329248)                                                                      // ( From test_stage/test_boot.py, line 214)
     ldr x10, =0x89688860                                                                                                   // ( From test_stage/test_boot.py, line 215)
     mov sp, x10                                                                                                            // ( From test_stage/test_boot.py, line 217)
     // switch according to thread                                                                                          // ( From test_stage/test_boot.py, line 223)
     mrs x10, mpidr_el1                                                                                                     // ( From test_stage/test_boot.py, line 224)
     and w22, w10, #0xff // Extract Aff0 (core within cluster)                                                              // ( From test_stage/test_boot.py, line 228)
     lsr x12, x10, #16 // Shift right by 16 to get Aff2 in lower bits                                                       // ( From test_stage/test_boot.py, line 231)
     and w12, w12, #0xff // Extract Aff2 (cluster ID)                                                                       // ( From test_stage/test_boot.py, line 232)
     lsl w12, w12, #1 // cluster_id * 2                                                                                     // ( From test_stage/test_boot.py, line 235)
     add w22, w22, w12 // sequential_core_id = core_in_cluster + (cluster_id * 2)                                           // ( From test_stage/test_boot.py, line 236)
     cmp x22, #0                                                                                                            // ( From test_stage/test_boot.py, line 254)
     bne label_4899_skip_label_0 // Skip if NOT equal (inverse of beq)                                                      // ( From test_stage/test_boot.py, line 257)
     ldr x10, =label_4845_core_0_el3_root__boot_segment_code_segment // Load far address into temp register                 // ( From test_stage/test_boot.py, line 258)
     br x10 // Branch to register (unlimited range)                                                                         // ( From test_stage/test_boot.py, line 259)
     label_4899_skip_label_0: // Local label for the fall-through code                                                      // ( From test_stage/test_boot.py, line 260)
     cmp x22, #1                                                                                                            // ( From test_stage/test_boot.py, line 254)
     bne label_4900_skip_label_0 // Skip if NOT equal (inverse of beq)                                                      // ( From test_stage/test_boot.py, line 257)
     ldr x10, =label_4858_core_1_el3_root__boot_segment_code_segment // Load far address into temp register                 // ( From test_stage/test_boot.py, line 258)
     br x10 // Branch to register (unlimited range)                                                                         // ( From test_stage/test_boot.py, line 259)
     label_4900_skip_label_0: // Local label for the fall-through code                                                      // ( From test_stage/test_boot.py, line 260)

.section .text.core_0_el3_root__boot_segment_1301
.global core_0_el3_root__boot_segment_1301
core_0_el3_root__boot_segment_1301:
     label_4845_core_0_el3_root__boot_segment_code_segment: // starting label for core_0_el3_root__boot_segment code Segment// ( From memlayout/segment_manager.py, line 105)
     // ========================= CORE_0 BOOT CODE - start =====================                                            // ( From test_stage/test_boot.py, line 42)
     // First disable the MMU                                                                                               // ( From test_stage/test_boot.py, line 87)
     mrs x21, sctlr_el3                                                                                                     // ( From test_stage/test_boot.py, line 88)
     bic x21, x21, #1 // Clear bit 0 (MMU enable)                                                                           // ( From test_stage/test_boot.py, line 89)
     msr sctlr_el3, x21                                                                                                     // ( From test_stage/test_boot.py, line 90)
     // Load translation table base register with the address of our L0 table                                               // ( From test_stage/test_boot.py, line 92)
     ldr x21, =LABEL_TTBR0_EL3_core_0 // read value of LABEL_TTBR0_EL3 from memory                                          // ( From test_stage/test_boot.py, line 93)
     ldr x21, [x21] // load the value of LABEL_TTBR0_EL3                                                                    // ( From test_stage/test_boot.py, line 94)
     msr ttbr0_el3, x21                                                                                                     // ( From test_stage/test_boot.py, line 95)
     // Set up TCR_EL3 (Translation Control Register)                                                                       // ( From test_stage/test_boot.py, line 97)
     ldr x21, =LABEL_TCR_EL3_core_0 // read value of LABEL_TCR_EL3 from memory                                              // ( From test_stage/test_boot.py, line 98)
     ldr x21, [x21] // load the value of LABEL_TCR_EL3                                                                      // ( From test_stage/test_boot.py, line 99)
     msr tcr_el3, x21                                                                                                       // ( From test_stage/test_boot.py, line 100)
     // Set up MAIR_EL1 (Memory Attribute Indirection Register)                                                             // ( From test_stage/test_boot.py, line 102)
     ldr x21, =LABEL_MAIR_EL3_core_0 // read value of LABEL_MAIR_EL3 from memory                                            // ( From test_stage/test_boot.py, line 103)
     ldr x21, [x21] // load the value of LABEL_MAIR_EL3                                                                     // ( From test_stage/test_boot.py, line 104)
     msr mair_el3, x21                                                                                                      // ( From test_stage/test_boot.py, line 105)
     // Enable MMU                                                                                                          // ( From test_stage/test_boot.py, line 107)
     mrs x21, sctlr_el3                                                                                                     // ( From test_stage/test_boot.py, line 108)
     orr x21, x21, #1 // Set bit 0 (MMU enable)                                                                             // ( From test_stage/test_boot.py, line 109)
     orr x21, x21, #(1 << 2) // Set bit 2 (Data cache enable)                                                               // ( From test_stage/test_boot.py, line 110)
     bic x21, x21, #(1 << 20) // Clear bit 20 (WXN)                                                                         // ( From test_stage/test_boot.py, line 111)
     msr sctlr_el3, x21                                                                                                     // ( From test_stage/test_boot.py, line 112)
     isb // Instruction Synchronization Barrier, must to ensure context-syncronization after enabling MMU                   // ( From test_stage/test_boot.py, line 113)
     // Now the MMU is enabled with your page tables                                                                        // ( From test_stage/test_boot.py, line 115)
     // Code can now access virtual addresses defined in your page tables                                                   // ( From test_stage/test_boot.py, line 116)
     // Set up EL1 Non-Secure Translation Tables                                                                            // ( From test_stage/test_boot.py, line 126)
     // First disable the EL1 MMU                                                                                           // ( From test_stage/test_boot.py, line 129)
     mrs x20, sctlr_el1                                                                                                     // ( From test_stage/test_boot.py, line 130)
     bic x20, x20, #1 // Clear bit 0 (MMU enable)                                                                           // ( From test_stage/test_boot.py, line 131)
     msr sctlr_el1, x20                                                                                                     // ( From test_stage/test_boot.py, line 132)
     // Set up TTBR0_EL1 (EL1 Translation Table Base Register 0)                                                            // ( From test_stage/test_boot.py, line 134)
     ldr x20, =LABEL_TTBR0_EL1NS_core_0 // read value of LABEL_TTBR0_EL1NS from memory                                      // ( From test_stage/test_boot.py, line 135)
     ldr x20, [x20] // load the value of LABEL_TTBR0_EL1NS                                                                  // ( From test_stage/test_boot.py, line 136)
     msr ttbr0_el1, x20                                                                                                     // ( From test_stage/test_boot.py, line 137)
     // Set up TTBR1_EL1 (EL1 Translation Table Base Register 1)                                                            // ( From test_stage/test_boot.py, line 139)
     ldr x20, =LABEL_TTBR1_EL1NS_core_0 // read value of LABEL_TTBR1_EL1NS from memory                                      // ( From test_stage/test_boot.py, line 140)
     ldr x20, [x20] // load the value of LABEL_TTBR1_EL1NS                                                                  // ( From test_stage/test_boot.py, line 141)
     msr ttbr1_el1, x20                                                                                                     // ( From test_stage/test_boot.py, line 142)
     // Set up TCR_EL1 (EL1 Translation Control Register)                                                                   // ( From test_stage/test_boot.py, line 144)
     ldr x20, =LABEL_TCR_EL1NS_core_0 // read value of LABEL_TCR_EL1NS from memory                                          // ( From test_stage/test_boot.py, line 145)
     ldr x20, [x20] // load the value of LABEL_TCR_EL1NS                                                                    // ( From test_stage/test_boot.py, line 146)
     msr tcr_el1, x20                                                                                                       // ( From test_stage/test_boot.py, line 147)
     // Set up MAIR_EL1 (EL1 Memory Attribute Indirection Register)                                                         // ( From test_stage/test_boot.py, line 149)
     ldr x20, =LABEL_MAIR_EL1NS_core_0 // read value of LABEL_MAIR_EL1NS from memory                                        // ( From test_stage/test_boot.py, line 150)
     ldr x20, [x20] // load the value of LABEL_MAIR_EL1NS                                                                   // ( From test_stage/test_boot.py, line 151)
     msr mair_el1, x20                                                                                                      // ( From test_stage/test_boot.py, line 152)
     // Enable EL1 MMU                                                                                                      // ( From test_stage/test_boot.py, line 155)
     mrs x20, sctlr_el1 // read EL1 system control register                                                                 // ( From test_stage/test_boot.py, line 156)
     orr x20, x20, #1 // set MMU enable bit (M bit)                                                                         // ( From test_stage/test_boot.py, line 157)
     orr x20, x20, #(1 << 2) // Set bit 2 (Data cache enable)                                                               // ( From test_stage/test_boot.py, line 158)
     bic x20, x20, #(1 << 20) // Clear bit 20 (WXN)                                                                         // ( From test_stage/test_boot.py, line 159)
     msr sctlr_el1, x20 // enable EL1 MMU                                                                                   // ( From test_stage/test_boot.py, line 160)
     isb // Instruction Synchronization Barrier, ensure MMU changes take effect                                             // ( From test_stage/test_boot.py, line 161)
     // EL1 MMU configuration complete                                                                                      // ( From test_stage/test_boot.py, line 163)
     // Now both EL3 and EL1 page tables are configured                                                                     // ( From test_stage/test_boot.py, line 164)
     ldr x7, =label_4873_exception_table_core_0_el3_root_code_segment // load the address of the vbar label                 // ( From test_stage/test_boot.py, line 182)
     msr vbar_el3, x7 // set the vbar_el3 address                                                                           // ( From test_stage/test_boot.py, line 183)
     ldr x6, =label_4880_exception_table_core_0_el1_ns_code_segment // load the address of the vbar label                   // ( From test_stage/test_boot.py, line 182)
     msr vbar_el1, x6 // set the vbar_el1 address                                                                           // ( From test_stage/test_boot.py, line 183)
     // ==== starting barrier sequence - label_4901_end_boot_barrier ====                                                   // ( From test_stage/test_boot.py, line 59)
     mrs x21, mpidr_el1                                                                                                     // ( From test_stage/test_boot.py, line 59)
     and w26, w21, #0xff // Extract Aff0 (core within cluster)                                                              // ( From test_stage/test_boot.py, line 59)
     lsr x20, x21, #16 // Shift right by 16 to get Aff2 in lower bits                                                       // ( From test_stage/test_boot.py, line 59)
     and w20, w20, #0xff // Extract Aff2 (cluster ID)                                                                       // ( From test_stage/test_boot.py, line 59)
     lsl w20, w20, #1 // cluster_id * 2 (2 cores per cluster)                                                               // ( From test_stage/test_boot.py, line 59)
     add w21, w26, w20 // sequential_core_id = core_in_cluster + (cluster_id * 2)                                           // ( From test_stage/test_boot.py, line 59)
     // Calculate the bit position for this core                                                                            // ( From test_stage/test_boot.py, line 59)
     mov w26, #1                                                                                                            // ( From test_stage/test_boot.py, line 59)
     lsl w26, w26, w21 // w1 = 1 << unique_core_id                                                                          // ( From test_stage/test_boot.py, line 59)
     // Set this core's bit in the barrier vector (active low)                                                              // ( From test_stage/test_boot.py, line 59)
     ldr x21, =label_4901_end_boot_barrier_barrier_vector_mem1985                                                           // ( From test_stage/test_boot.py, line 59)
     stclr w26, [x21]                                                                                                       // ( From test_stage/test_boot.py, line 59)
     // Spin until all bits are clear (active low)                                                                          // ( From test_stage/test_boot.py, line 59)
     label_4902_spin_label:                                                                                                 // ( From test_stage/test_boot.py, line 59)
     ldr w20, [x21]                                                                                                         // ( From test_stage/test_boot.py, line 59)
     cbnz w20, label_4902_spin_label // Continue spinning if any bit is set                                                 // ( From test_stage/test_boot.py, line 59)
     // Barrier reached - all cores have arrived                                                                            // ( From test_stage/test_boot.py, line 59)
     // ==== finished barrier sequence - label_4901_end_boot_barrier ====                                                   // ( From test_stage/test_boot.py, line 59)
     // using 'B' (branch) for unconditional 'one-way' branch (similar to jmp) to code segment core_0_el3_root__code_segment_3_1305// ( From test_stage/test_boot.py, line 64)
     B label_4903_core_0_el3_root__code_segment_3_1305_branchToSegment_target // Jump to code_label                         // ( From test_stage/test_boot.py, line 64)
     // ========================= CORE_0 BOOT CODE - end =====================                                              // ( From test_stage/test_boot.py, line 68)

.section .text.core_0_el3_root__code_segment_0_1302
.global core_0_el3_root__code_segment_0_1302
core_0_el3_root__code_segment_0_1302:
     label_4846_core_0_el3_root__code_segment_0_code_segment: // starting label for core_0_el3_root__code_segment_0 code Segment// ( From memlayout/segment_manager.py, line 105)
     label_4906_core_0_el3_root__code_segment_0_1302_branchToSegment_target:                                                // ( From test_stage/test_body.py, line 64)
     // ========================== Start scenario random_instructions ====================                                  // ( From test_stage/test_body.py, line 14)
     // inside random_instructions                                                                                          // ( From templates/direct_template.py, line 18)
     subr z23.D, p5/M, z23.D, z22.D                                                                                         // ( From templates/direct_template.py, line 21)
     ucvtf z1.H, p6/M, z30.S                                                                                                // ( From templates/direct_template.py, line 21)
     ldr x4, =mem1986+16 // dynamic init: loading x4 for next instruction (0x819a0a8c:0xa86f6a8c)                           // ( From templates/direct_template.py, line 21)
     ldp s12, s2, [x4, #0]                                                                                                  // ( From templates/direct_template.py, line 21)
     ldr x11, =mem1987+8 // dynamic init: loading x11 for next instruction (0x819a0a48:0xa86f6a48)                          // ( From templates/direct_template.py, line 21)
     ldlarh w26, [x11, #0]                                                                                                  // ( From templates/direct_template.py, line 21)
     cnt z29.D, p0/M, z11.D                                                                                                 // ( From templates/direct_template.py, line 21)
     brkpb p9.B, p9/Z, p3.B, p1.B                                                                                           // ( From templates/direct_template.py, line 21)
     shadd z22.H, p0/M, z22.H, z16.H                                                                                        // ( From templates/direct_template.py, line 21)
     sunpkhi z26.S, z9.H                                                                                                    // ( From templates/direct_template.py, line 21)
     // Starting loop with 50 iterations. using a x20 operand and a label_4907_loop_label label                             // ( From templates/direct_template.py, line 24)
     mov x20, #0                                                                                                            // ( From templates/direct_template.py, line 24)
     label_4907_loop_label:                                                                                                 // ( From templates/direct_template.py, line 24)
     adc w23, w19, w22                                                                                                      // ( From templates/direct_template.py, line 26)
     fmov w18, s10                                                                                                          // ( From templates/direct_template.py, line 27)
     adc w3, w3, w0                                                                                                         // ( From templates/direct_template.py, line 26)
     decp x18, p9.S                                                                                                         // ( From templates/direct_template.py, line 27)
     sqdecp x23, p10.D                                                                                                      // ( From templates/direct_template.py, line 27)
     adcs w27, w0, w13                                                                                                      // ( From templates/direct_template.py, line 26)
     nor p1.B, p3/Z, p1.B, p5.B                                                                                             // ( From templates/direct_template.py, line 27)
     fmov w12, h12                                                                                                          // ( From templates/direct_template.py, line 27)
     add x20, x20, #1 // Increment the loop counter (x20 += 1)                                                              // ( From templates/direct_template.py, line 24)
     cmp x20, #50 //  Compare x20 with 50                                                                                   // ( From templates/direct_template.py, line 24)
     bne label_4907_loop_label                                                                                              // ( From templates/direct_template.py, line 24)
     // Ending loop                                                                                                         // ( From templates/direct_template.py, line 24)
     add x12, x12, x24 // adding x12 = x12 + x24                                                                            // ( From templates/direct_template.py, line 32)
     ldr x16, =mem1986+4 // dynamic init: loading x16 with reused memory mem1988 (0x819a0a80:0xa86f6a80) for next instruction// ( From templates/direct_template.py, line 33)
     casa x12, x26, [x16, #0] // store reg                                                                                  // ( From templates/direct_template.py, line 33)
     ldr x6, =mem1989+0 // dynamic init: loading x6 for next instruction (0x8a3c5420:0x1f8bc5420)                           // ( From templates/direct_template.py, line 42)
     stlurb w21, [x6, #0] // load mem                                                                                       // ( From templates/direct_template.py, line 42)
     ldr x18, =mem1989+0 // dynamic init: loading x18 for next instruction (0x8a3c5420:0x1f8bc5420)                         // ( From templates/direct_template.py, line 43)
     ldrsb x21, [x18, #0]! // store mem                                                                                     // ( From templates/direct_template.py, line 43)
     // Starting loop with 100 iterations. using a x21 operand and a label_4908_loop_label label                            // ( From templates/direct_template.py, line 50)
     mov x21, #0                                                                                                            // ( From templates/direct_template.py, line 50)
     label_4908_loop_label:                                                                                                 // ( From templates/direct_template.py, line 50)
     ldr x7, =3841842585                                                                                                    // ( From templates/direct_template.py, line 51)
     // EventTrigger:: Setting event trigger flow with Frequency.LOW frequency                                              // ( From templates/direct_template.py, line 53)
     // EventTrigger:: Using mem at 0xe4fde0ea with the following 64bit pattern: 0000000000000000000000000000000000000000000000000000000000100000// ( From templates/direct_template.py, line 53)
     ldr x10, =0xe4fde0ea                                                                                                   // ( From templates/direct_template.py, line 53)
     ldr x22, [x10] // load the vector from mem 0xe4fde0ea                                                                  // ( From templates/direct_template.py, line 53)
     ror x22, x22, #1 // rotate the vector                                                                                  // ( From templates/direct_template.py, line 53)
     str x22, [x10] // store back the vector into the memory location                                                       // ( From templates/direct_template.py, line 53)
     tbz x22, #63, label_4909_skip_label // test bit 63 and branch if 0 (zero)                                              // ( From templates/direct_template.py, line 53)
     ldr x7, =2319212364                                                                                                    // ( From templates/direct_template.py, line 54)
     label_4909_skip_label:                                                                                                 // ( From templates/direct_template.py, line 53)
     ldr x9, [x7]                                                                                                           // ( From templates/direct_template.py, line 57)
     add x21, x21, #1 // Increment the loop counter (x21 += 1)                                                              // ( From templates/direct_template.py, line 50)
     cmp x21, #100 //  Compare x21 with 100                                                                                 // ( From templates/direct_template.py, line 50)
     bne label_4908_loop_label                                                                                              // ( From templates/direct_template.py, line 50)
     // Ending loop                                                                                                         // ( From templates/direct_template.py, line 50)
     // ========================== End scenario random_instructions ====================                                    // ( From test_stage/test_body.py, line 40)
     // Return to the previous code segment core_0_el3_root__code_segment_3_1305 using the address in `LR` (similar to `ret stack` in x86)// ( From test_stage/test_body.py, line 64)
     RET // Returns from a function using the LR (x30) register.                                                            // ( From test_stage/test_body.py, line 64)

// No code on core_0_el3_root__code_segment_1_1303 segment. skipping .text section

// No code on core_0_el3_root__code_segment_2_1304 segment. skipping .text section

.section .text.core_0_el3_root__code_segment_3_1305
.global core_0_el3_root__code_segment_3_1305
core_0_el3_root__code_segment_3_1305:
     label_4849_core_0_el3_root__code_segment_3_code_segment: // starting label for core_0_el3_root__code_segment_3 code Segment// ( From memlayout/segment_manager.py, line 105)
     label_4903_core_0_el3_root__code_segment_3_1305_branchToSegment_target:                                                // ( From test_stage/test_boot.py, line 64)
     // ========================= core core_0 - TEST BODY - start =====================                                     // ( From test_stage/test_body.py, line 83)
     // BODY:: Running core_0, scenario 1(:2), scenario random_instructions                                                 // ( From test_stage/test_body.py, line 60)
     // branch with link `label` by jumping to code segment core_0_el3_root__code_segment_0_1302 and storing the return address in `LR` (Link Register) register// ( From test_stage/test_body.py, line 64)
     bl label_4906_core_0_el3_root__code_segment_0_1302_branchToSegment_target // Branch with Link to target address        // ( From test_stage/test_body.py, line 64)
     // BODY:: Running core_0, scenario 2(:2), scenario random_instructions                                                 // ( From test_stage/test_body.py, line 60)
     // using 'B' (branch) for unconditional 'one-way' branch (similar to jmp) to code segment exception_table_core_0_el3_root_1347// ( From test_stage/test_body.py, line 67)
     B label_4914_exception_table_core_0_el3_root_1347_branchToSegment_target // Jump to code_label                         // ( From test_stage/test_body.py, line 67)

// No code on core_0_el3_root__code_segment_4_1306 segment. skipping .text section

// No code on core_0_el3_root__code_segment_5_1307 segment. skipping .text section

.section .text.exception_table_core_0_el3_root_1347
.global exception_table_core_0_el3_root_1347
exception_table_core_0_el3_root_1347:
     label_4873_exception_table_core_0_el3_root_code_segment: // starting label for exception_table_core_0_el3_root code Segment// ( From memlayout/segment_manager.py, line 105)
     // ================ exception table for core_0 core_0_el3_root =====================                                   // ( From exception_management/__init__.py, line 110)
     .org 0x0                                                                                                               // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_SYNCHRONOUS - target label label_4871_halting_label                   // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x80                                                                                                              // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_IRQ - target label label_4871_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x100                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_FIQ - target label label_4871_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x180                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_SERROR - target label label_4871_halting_label                        // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x200                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_SYNCHRONOUS - target label label_4871_halting_label                   // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x280                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_IRQ - target label label_4871_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x300                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_FIQ - target label label_4871_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x380                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_SERROR - target label label_4871_halting_label                        // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x400                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_SYNCHRONOUS - target label label_4872_callback_label                    // ( From exception_management/__init__.py, line 114)
     b label_4872_callback_label                                                                                            // ( From exception_management/__init__.py, line 115)
     .org 0x480                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_IRQ - target label label_4871_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x500                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_FIQ - target label label_4871_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x580                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_SERROR - target label label_4871_halting_label                          // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x600                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_SYNCHRONOUS - target label label_4871_halting_label                     // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x680                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_IRQ - target label label_4871_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x700                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_FIQ - target label label_4871_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x780                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_SERROR - target label label_4871_halting_label                          // ( From exception_management/__init__.py, line 114)
     b label_4871_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     label_4871_halting_label:                                                                                              // ( From exception_management/__init__.py, line 118)
     // default halting hander                                                                                              // ( From exception_management/__init__.py, line 119)
     nop                                                                                                                    // ( From exception_management/__init__.py, line 120)
     mrs x0, esr_el1 // Read cause of exception                                                                             // ( From exception_management/__init__.py, line 136)
     ubfx x1, x0, #26, #6 // Extract EC (bits[31:26])                                                                       // ( From exception_management/__init__.py, line 137)
     cmp x1, #0x00 // EC = 0b000000 = undefined instruction                                                                 // ( From exception_management/__init__.py, line 138)
     b.ne label_4874_halting_handler_test_fail_label // handle undefined instruction                                        // ( From exception_management/__init__.py, line 139)
     ldr x0, =core_0_el3_root__exception_callback_LOWER_A64_SYNC_mem1977                                                    // ( From exception_management/__init__.py, line 141)
     ldr x1, [x0]                                                                                                           // ( From exception_management/__init__.py, line 142)
     br x1                                                                                                                  // ( From exception_management/__init__.py, line 143)
     label_4874_halting_handler_test_fail_label:                                                                            // ( From exception_management/__init__.py, line 145)
     // Test failed with error code of 0x0                                                                                  // ( From exception_management/__init__.py, line 147)
     // End test logic:                                                                                                     // ( From exception_management/__init__.py, line 147)
     // Core0 reached end of test, write '** TEST FAILED **' to Trickbox                                                    // ( From exception_management/__init__.py, line 147)
     // Load the stack pointer                                                                                              // ( From exception_management/__init__.py, line 147)
     ldr x14, =0x89688860                                                                                                   // ( From exception_management/__init__.py, line 147)
     mov sp, x14                                                                                                            // ( From exception_management/__init__.py, line 147)
     // Print a string to the trickbox tube                                                                                 // ( From exception_management/__init__.py, line 147)
     ldr x14, =2319212384 // Load the address of the test_end string                                                        // ( From exception_management/__init__.py, line 147)
     stp x6, x7, [sp, #-16]! // Push x6, x7 to stack to get some temps                                                      // ( From exception_management/__init__.py, line 147)
     ldr x6, =0x13000000 // Load the address of the trickbox tube                                                           // ( From exception_management/__init__.py, line 147)
     label_4876_core_0_print_str_loop: // Start of the loop                                                                 // ( From exception_management/__init__.py, line 147)
     ldrb w7, [x14], #1 // Load the next character from the string                                                          // ( From exception_management/__init__.py, line 147)
     cbz w7, label_4877_core_0_print_str_end // If the character is the null terminator, end the loop                       // ( From exception_management/__init__.py, line 147)
     strb w7, [x6] // Store the character to the Tbox tube                                                                  // ( From exception_management/__init__.py, line 147)
     b label_4876_core_0_print_str_loop // Jump back to the start of the loop                                               // ( From exception_management/__init__.py, line 147)
     label_4877_core_0_print_str_end: // End of the loop                                                                    // ( From exception_management/__init__.py, line 147)
     ldp x6, x7, [sp], #16 // Pop x6, x7 from stack                                                                         // ( From exception_management/__init__.py, line 147)
     // Close the trickbox tube (end the test)                                                                              // ( From exception_management/__init__.py, line 147)
     ldr x14, =0x13000000 // Load the address of the trickbox tube                                                          // ( From exception_management/__init__.py, line 147)
     mov x6, #0x4 // Load the EOT character                                                                                 // ( From exception_management/__init__.py, line 147)
     strb w6, [x14] // Store the EOT character to the trickbox tube                                                         // ( From exception_management/__init__.py, line 147)
     dsb sy // Flush the data cache                                                                                         // ( From exception_management/__init__.py, line 147)
     label_4875_core_0_end_of_test:                                                                                         // ( From exception_management/__init__.py, line 147)
     wfi // End of test convention. not expecting to be waked                                                               // ( From exception_management/__init__.py, line 147)
     b label_4875_core_0_end_of_test                                                                                        // ( From exception_management/__init__.py, line 147)
     label_4872_callback_label:                                                                                             // ( From exception_management/__init__.py, line 150)
     // default callback handler                                                                                            // ( From exception_management/__init__.py, line 151)
     nop                                                                                                                    // ( From exception_management/__init__.py, line 152)
     ldr x0, =core_0_el3_root__exception_callback_LOWER_A64_SYNC_mem1978                                                    // ( From exception_management/__init__.py, line 166)
     ldr x1, [x0]                                                                                                           // ( From exception_management/__init__.py, line 167)
     br x1                                                                                                                  // ( From exception_management/__init__.py, line 168)
     // ================ end of exception table for core_0 core_0_el3_root ===============                                  // ( From exception_management/__init__.py, line 171)
     label_4914_exception_table_core_0_el3_root_1347_branchToSegment_target:                                                // ( From test_stage/test_body.py, line 67)
     // ========================== Start scenario random_instructions ====================                                  // ( From test_stage/test_body.py, line 14)
     // inside random_instructions                                                                                          // ( From templates/direct_template.py, line 18)
     ldr x12, =mem1998+0 // dynamic init: loading x12 for next instruction (0x17cce1df0:0x14e4e1df0)                        // ( From templates/direct_template.py, line 21)
     fcvtzs z5.D, p1/M, z8.S                                                                                                // ( From templates/direct_template.py, line 21)
     ldr x16, =mem1999+0 // dynamic init: loading x16 for next instruction (0x17cce0fa8:0x14e4e0fa8)                        // ( From templates/direct_template.py, line 21)
     ldapursb x26, [x16, #0]                                                                                                // ( From templates/direct_template.py, line 21)
     ldr x7, =mem2000+0 // dynamic init: loading x7 for next instruction (0x819a03f0:0xa86f63f0)                            // ( From templates/direct_template.py, line 21)
     ldnp d2, d3, [x7, #0]                                                                                                  // ( From templates/direct_template.py, line 21)
     orns p12.B, p5/Z, p11.B, p5.B                                                                                          // ( From templates/direct_template.py, line 21)
     fcvtzs w26, s28                                                                                                        // ( From templates/direct_template.py, line 21)
     xpacd x12                                                                                                              // ( From templates/direct_template.py, line 21)
     ldr x16, =mem1999+8 // dynamic init: loading x16 with reused memory mem2001 (0x17cce0fb0:0x14e4e0fb0) for next instruction// ( From templates/direct_template.py, line 21)
     ldtrsh w2, [x16, #8]                                                                                                   // ( From templates/direct_template.py, line 21)
     ldr x9, =mem2002+0 // dynamic init: loading x9 for next instruction (0x17cce1400:0x14e4e1400)                          // ( From templates/direct_template.py, line 21)
     casl x18, x24, [x9, #0]                                                                                                // ( From templates/direct_template.py, line 21)
     // Starting loop with 50 iterations. using a x20 operand and a label_4915_loop_label label                             // ( From templates/direct_template.py, line 24)
     mov x20, #0                                                                                                            // ( From templates/direct_template.py, line 24)
     label_4915_loop_label:                                                                                                 // ( From templates/direct_template.py, line 24)
     adc x10, x16, x27                                                                                                      // ( From templates/direct_template.py, line 26)
     punpkhi p13.H, p1.B                                                                                                    // ( From templates/direct_template.py, line 27)
     uqdecp z6.S, p7.S                                                                                                      // ( From templates/direct_template.py, line 27)
     adc w15, w19, w4                                                                                                       // ( From templates/direct_template.py, line 26)
     ptest p10, p7.B                                                                                                        // ( From templates/direct_template.py, line 27)
     zip1 p12.S, p4.S, p1.S                                                                                                 // ( From templates/direct_template.py, line 27)
     adclt z30.S, z1.S, z16.S                                                                                               // ( From templates/direct_template.py, line 26)
     scvtf d16, w10                                                                                                         // ( From templates/direct_template.py, line 27)
     uzp1 p12.H, p7.H, p4.H                                                                                                 // ( From templates/direct_template.py, line 27)
     add x20, x20, #1 // Increment the loop counter (x20 += 1)                                                              // ( From templates/direct_template.py, line 24)
     cmp x20, #50 //  Compare x20 with 50                                                                                   // ( From templates/direct_template.py, line 24)
     bne label_4915_loop_label                                                                                              // ( From templates/direct_template.py, line 24)
     // Ending loop                                                                                                         // ( From templates/direct_template.py, line 24)
     add x16, x16, x24 // adding x16 = x16 + x24                                                                            // ( From templates/direct_template.py, line 32)
     uqincp w16, p3.H // store reg                                                                                          // ( From templates/direct_template.py, line 33)
     ldr x26, =mem2003+0 // dynamic init: loading x26 for next instruction (0x8a3c5f38:0x1f8bc5f38)                         // ( From templates/direct_template.py, line 42)
     ld1rqh z1.H, p6/Z, [x26, #0] // load mem                                                                               // ( From templates/direct_template.py, line 42)
     ldr x8, =mem2003+0 // dynamic init: loading x8 for next instruction (0x8a3c5f38:0x1f8bc5f38)                           // ( From templates/direct_template.py, line 43)
     ldrh w27, [x8], #0 // store mem                                                                                        // ( From templates/direct_template.py, line 43)
     // Starting loop with 100 iterations. using a x17 operand and a label_4916_loop_label label                            // ( From templates/direct_template.py, line 50)
     mov x17, #0                                                                                                            // ( From templates/direct_template.py, line 50)
     label_4916_loop_label:                                                                                                 // ( From templates/direct_template.py, line 50)
     ldr x26, =2319209648                                                                                                   // ( From templates/direct_template.py, line 51)
     // EventTrigger:: Setting event trigger flow with Frequency.LOW frequency                                              // ( From templates/direct_template.py, line 53)
     // EventTrigger:: Using mem at 0x8a3c5480 with the following 64bit pattern: 0000000000000000000000000010000000000000000000000000000000000000// ( From templates/direct_template.py, line 53)
     ldr x6, =0x8a3c5480                                                                                                    // ( From templates/direct_template.py, line 53)
     ldr x12, [x6] // load the vector from mem 0x8a3c5480                                                                   // ( From templates/direct_template.py, line 53)
     ror x12, x12, #1 // rotate the vector                                                                                  // ( From templates/direct_template.py, line 53)
     str x12, [x6] // store back the vector into the memory location                                                        // ( From templates/direct_template.py, line 53)
     tbz x12, #63, label_4917_skip_label // test bit 63 and branch if 0 (zero)                                              // ( From templates/direct_template.py, line 53)
     ldr x26, =2319212372                                                                                                   // ( From templates/direct_template.py, line 54)
     label_4917_skip_label:                                                                                                 // ( From templates/direct_template.py, line 53)
     ldr x0, [x26]                                                                                                          // ( From templates/direct_template.py, line 57)
     add x17, x17, #1 // Increment the loop counter (x17 += 1)                                                              // ( From templates/direct_template.py, line 50)
     cmp x17, #100 //  Compare x17 with 100                                                                                 // ( From templates/direct_template.py, line 50)
     bne label_4916_loop_label                                                                                              // ( From templates/direct_template.py, line 50)
     // Ending loop                                                                                                         // ( From templates/direct_template.py, line 50)
     // ========================== End scenario random_instructions ====================                                    // ( From test_stage/test_body.py, line 40)
     // ========================= core core_0 - TEST BODY - end =====================                                       // ( From test_stage/test_body.py, line 103)
     // in do_final, ending test body                                                                                       // ( From test_stage/test_final.py, line 13)
     // ==== starting barrier sequence - label_4922_end_test_barrier ====                                                   // ( From test_stage/test_final.py, line 22)
     mrs x7, mpidr_el1                                                                                                      // ( From test_stage/test_final.py, line 22)
     and w15, w7, #0xff // Extract Aff0 (core within cluster)                                                               // ( From test_stage/test_final.py, line 22)
     lsr x22, x7, #16 // Shift right by 16 to get Aff2 in lower bits                                                        // ( From test_stage/test_final.py, line 22)
     and w22, w22, #0xff // Extract Aff2 (cluster ID)                                                                       // ( From test_stage/test_final.py, line 22)
     lsl w22, w22, #1 // cluster_id * 2 (2 cores per cluster)                                                               // ( From test_stage/test_final.py, line 22)
     add w7, w15, w22 // sequential_core_id = core_in_cluster + (cluster_id * 2)                                            // ( From test_stage/test_final.py, line 22)
     // Calculate the bit position for this core                                                                            // ( From test_stage/test_final.py, line 22)
     mov w15, #1                                                                                                            // ( From test_stage/test_final.py, line 22)
     lsl w15, w15, w7 // w1 = 1 << unique_core_id                                                                           // ( From test_stage/test_final.py, line 22)
     // Set this core's bit in the barrier vector (active low)                                                              // ( From test_stage/test_final.py, line 22)
     ldr x7, =label_4922_end_test_barrier_barrier_vector_mem2017                                                            // ( From test_stage/test_final.py, line 22)
     stclr w15, [x7]                                                                                                        // ( From test_stage/test_final.py, line 22)
     // Spin until all bits are clear (active low)                                                                          // ( From test_stage/test_final.py, line 22)
     label_4923_spin_label:                                                                                                 // ( From test_stage/test_final.py, line 22)
     ldr w22, [x7]                                                                                                          // ( From test_stage/test_final.py, line 22)
     cbnz w22, label_4923_spin_label // Continue spinning if any bit is set                                                 // ( From test_stage/test_final.py, line 22)
     // Barrier reached - all cores have arrived                                                                            // ( From test_stage/test_final.py, line 22)
     // ==== finished barrier sequence - label_4922_end_test_barrier ====                                                   // ( From test_stage/test_final.py, line 22)
     // Test ended successfully                                                                                             // ( From test_stage/test_final.py, line 25)
     // End test logic:                                                                                                     // ( From test_stage/test_final.py, line 25)
     // Core0 reached end of test, write '** TEST PASSED OK **' to Trickbox                                                 // ( From test_stage/test_final.py, line 25)
     // Load the stack pointer                                                                                              // ( From test_stage/test_final.py, line 25)
     ldr x16, =0x89688860                                                                                                   // ( From test_stage/test_final.py, line 25)
     mov sp, x16                                                                                                            // ( From test_stage/test_final.py, line 25)
     // Print a string to the trickbox tube                                                                                 // ( From test_stage/test_final.py, line 25)
     ldr x16, =3841843200 // Load the address of the test_end string                                                        // ( From test_stage/test_final.py, line 25)
     stp x9, x2, [sp, #-16]! // Push x9, x2 to stack to get some temps                                                      // ( From test_stage/test_final.py, line 25)
     ldr x9, =0x13000000 // Load the address of the trickbox tube                                                           // ( From test_stage/test_final.py, line 25)
     label_4925_core_0_print_str_loop: // Start of the loop                                                                 // ( From test_stage/test_final.py, line 25)
     ldrb w2, [x16], #1 // Load the next character from the string                                                          // ( From test_stage/test_final.py, line 25)
     cbz w2, label_4926_core_0_print_str_end // If the character is the null terminator, end the loop                       // ( From test_stage/test_final.py, line 25)
     strb w2, [x9] // Store the character to the Tbox tube                                                                  // ( From test_stage/test_final.py, line 25)
     b label_4925_core_0_print_str_loop // Jump back to the start of the loop                                               // ( From test_stage/test_final.py, line 25)
     label_4926_core_0_print_str_end: // End of the loop                                                                    // ( From test_stage/test_final.py, line 25)
     ldp x9, x2, [sp], #16 // Pop x9, x2 from stack                                                                         // ( From test_stage/test_final.py, line 25)
     // Close the trickbox tube (end the test)                                                                              // ( From test_stage/test_final.py, line 25)
     ldr x16, =0x13000000 // Load the address of the trickbox tube                                                          // ( From test_stage/test_final.py, line 25)
     mov x9, #0x4 // Load the EOT character                                                                                 // ( From test_stage/test_final.py, line 25)
     strb w9, [x16] // Store the EOT character to the trickbox tube                                                         // ( From test_stage/test_final.py, line 25)
     dsb sy // Flush the data cache                                                                                         // ( From test_stage/test_final.py, line 25)
     label_4924_core_0_end_of_test:                                                                                         // ( From test_stage/test_final.py, line 25)
     wfi // End of test convention. not expecting to be waked                                                               // ( From test_stage/test_final.py, line 25)
     b label_4924_core_0_end_of_test                                                                                        // ( From test_stage/test_final.py, line 25)

// No code on core_0_el1_ns__code_segment_0_1313 segment. skipping .text section

// No code on core_0_el1_ns__code_segment_1_1314 segment. skipping .text section

// No code on core_0_el1_ns__code_segment_2_1315 segment. skipping .text section

// No code on core_0_el1_ns__code_segment_3_1316 segment. skipping .text section

// No code on core_0_el1_ns__code_segment_4_1317 segment. skipping .text section

// No code on core_0_el1_ns__code_segment_5_1318 segment. skipping .text section

.section .text.exception_table_core_0_el1_ns_1348
.global exception_table_core_0_el1_ns_1348
exception_table_core_0_el1_ns_1348:
     label_4880_exception_table_core_0_el1_ns_code_segment: // starting label for exception_table_core_0_el1_ns code Segment// ( From memlayout/segment_manager.py, line 105)
     // ================ exception table for core_0 core_0_el1_ns =====================                                     // ( From exception_management/__init__.py, line 110)
     .org 0x0                                                                                                               // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_SYNCHRONOUS - target label label_4878_halting_label                   // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x80                                                                                                              // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_IRQ - target label label_4878_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x100                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_FIQ - target label label_4878_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x180                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_SERROR - target label label_4878_halting_label                        // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x200                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_SYNCHRONOUS - target label label_4878_halting_label                   // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x280                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_IRQ - target label label_4878_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x300                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_FIQ - target label label_4878_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x380                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_SERROR - target label label_4878_halting_label                        // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x400                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_SYNCHRONOUS - target label label_4879_callback_label                    // ( From exception_management/__init__.py, line 114)
     b label_4879_callback_label                                                                                            // ( From exception_management/__init__.py, line 115)
     .org 0x480                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_IRQ - target label label_4878_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x500                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_FIQ - target label label_4878_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x580                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_SERROR - target label label_4878_halting_label                          // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x600                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_SYNCHRONOUS - target label label_4878_halting_label                     // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x680                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_IRQ - target label label_4878_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x700                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_FIQ - target label label_4878_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x780                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_SERROR - target label label_4878_halting_label                          // ( From exception_management/__init__.py, line 114)
     b label_4878_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     label_4878_halting_label:                                                                                              // ( From exception_management/__init__.py, line 118)
     // default halting hander                                                                                              // ( From exception_management/__init__.py, line 119)
     nop                                                                                                                    // ( From exception_management/__init__.py, line 120)
     mrs x0, esr_el1 // Read cause of exception                                                                             // ( From exception_management/__init__.py, line 136)
     ubfx x1, x0, #26, #6 // Extract EC (bits[31:26])                                                                       // ( From exception_management/__init__.py, line 137)
     cmp x1, #0x00 // EC = 0b000000 = undefined instruction                                                                 // ( From exception_management/__init__.py, line 138)
     b.ne label_4881_halting_handler_test_fail_label // handle undefined instruction                                        // ( From exception_management/__init__.py, line 139)
     ldr x0, =core_0_el1_ns__exception_callback_LOWER_A64_SYNC_mem1979                                                      // ( From exception_management/__init__.py, line 141)
     ldr x1, [x0]                                                                                                           // ( From exception_management/__init__.py, line 142)
     br x1                                                                                                                  // ( From exception_management/__init__.py, line 143)
     label_4881_halting_handler_test_fail_label:                                                                            // ( From exception_management/__init__.py, line 145)
     // Test failed with error code of 0x0                                                                                  // ( From exception_management/__init__.py, line 147)
     // End test logic:                                                                                                     // ( From exception_management/__init__.py, line 147)
     // Core0 reached end of test, write '** TEST FAILED **' to Trickbox                                                    // ( From exception_management/__init__.py, line 147)
     // Load the stack pointer                                                                                              // ( From exception_management/__init__.py, line 147)
     ldr x17, =0x2322d38a0                                                                                                  // ( From exception_management/__init__.py, line 147)
     mov sp, x17                                                                                                            // ( From exception_management/__init__.py, line 147)
     // Print a string to the trickbox tube                                                                                 // ( From exception_management/__init__.py, line 147)
     ldr x17, =8243700656 // Load the address of the test_end string                                                        // ( From exception_management/__init__.py, line 147)
     stp x2, x10, [sp, #-16]! // Push x2, x10 to stack to get some temps                                                    // ( From exception_management/__init__.py, line 147)
     ldr x2, =0x13000000 // Load the address of the trickbox tube                                                           // ( From exception_management/__init__.py, line 147)
     label_4883_core_0_print_str_loop: // Start of the loop                                                                 // ( From exception_management/__init__.py, line 147)
     ldrb w10, [x17], #1 // Load the next character from the string                                                         // ( From exception_management/__init__.py, line 147)
     cbz w10, label_4884_core_0_print_str_end // If the character is the null terminator, end the loop                      // ( From exception_management/__init__.py, line 147)
     strb w10, [x2] // Store the character to the Tbox tube                                                                 // ( From exception_management/__init__.py, line 147)
     b label_4883_core_0_print_str_loop // Jump back to the start of the loop                                               // ( From exception_management/__init__.py, line 147)
     label_4884_core_0_print_str_end: // End of the loop                                                                    // ( From exception_management/__init__.py, line 147)
     ldp x2, x10, [sp], #16 // Pop x2, x10 from stack                                                                       // ( From exception_management/__init__.py, line 147)
     // Close the trickbox tube (end the test)                                                                              // ( From exception_management/__init__.py, line 147)
     ldr x17, =0x13000000 // Load the address of the trickbox tube                                                          // ( From exception_management/__init__.py, line 147)
     mov x2, #0x4 // Load the EOT character                                                                                 // ( From exception_management/__init__.py, line 147)
     strb w2, [x17] // Store the EOT character to the trickbox tube                                                         // ( From exception_management/__init__.py, line 147)
     dsb sy // Flush the data cache                                                                                         // ( From exception_management/__init__.py, line 147)
     label_4882_core_0_end_of_test:                                                                                         // ( From exception_management/__init__.py, line 147)
     wfi // End of test convention. not expecting to be waked                                                               // ( From exception_management/__init__.py, line 147)
     b label_4882_core_0_end_of_test                                                                                        // ( From exception_management/__init__.py, line 147)
     label_4879_callback_label:                                                                                             // ( From exception_management/__init__.py, line 150)
     // default callback handler                                                                                            // ( From exception_management/__init__.py, line 151)
     nop                                                                                                                    // ( From exception_management/__init__.py, line 152)
     ldr x0, =core_0_el1_ns__exception_callback_LOWER_A64_SYNC_mem1980                                                      // ( From exception_management/__init__.py, line 166)
     ldr x1, [x0]                                                                                                           // ( From exception_management/__init__.py, line 167)
     br x1                                                                                                                  // ( From exception_management/__init__.py, line 168)
     // ================ end of exception table for core_0 core_0_el1_ns ===============                                    // ( From exception_management/__init__.py, line 171)

.section .text.core_1_el3_root__boot_segment_1324
.global core_1_el3_root__boot_segment_1324
core_1_el3_root__boot_segment_1324:
     label_4858_core_1_el3_root__boot_segment_code_segment: // starting label for core_1_el3_root__boot_segment code Segment// ( From memlayout/segment_manager.py, line 105)
     // ========================= CORE_1 BOOT CODE - start =====================                                            // ( From test_stage/test_boot.py, line 42)
     // First disable the MMU                                                                                               // ( From test_stage/test_boot.py, line 87)
     mrs x0, sctlr_el3                                                                                                      // ( From test_stage/test_boot.py, line 88)
     bic x0, x0, #1 // Clear bit 0 (MMU enable)                                                                             // ( From test_stage/test_boot.py, line 89)
     msr sctlr_el3, x0                                                                                                      // ( From test_stage/test_boot.py, line 90)
     // Load translation table base register with the address of our L0 table                                               // ( From test_stage/test_boot.py, line 92)
     ldr x0, =LABEL_TTBR0_EL3_core_1 // read value of LABEL_TTBR0_EL3 from memory                                           // ( From test_stage/test_boot.py, line 93)
     ldr x0, [x0] // load the value of LABEL_TTBR0_EL3                                                                      // ( From test_stage/test_boot.py, line 94)
     msr ttbr0_el3, x0                                                                                                      // ( From test_stage/test_boot.py, line 95)
     // Set up TCR_EL3 (Translation Control Register)                                                                       // ( From test_stage/test_boot.py, line 97)
     ldr x0, =LABEL_TCR_EL3_core_1 // read value of LABEL_TCR_EL3 from memory                                               // ( From test_stage/test_boot.py, line 98)
     ldr x0, [x0] // load the value of LABEL_TCR_EL3                                                                        // ( From test_stage/test_boot.py, line 99)
     msr tcr_el3, x0                                                                                                        // ( From test_stage/test_boot.py, line 100)
     // Set up MAIR_EL1 (Memory Attribute Indirection Register)                                                             // ( From test_stage/test_boot.py, line 102)
     ldr x0, =LABEL_MAIR_EL3_core_1 // read value of LABEL_MAIR_EL3 from memory                                             // ( From test_stage/test_boot.py, line 103)
     ldr x0, [x0] // load the value of LABEL_MAIR_EL3                                                                       // ( From test_stage/test_boot.py, line 104)
     msr mair_el3, x0                                                                                                       // ( From test_stage/test_boot.py, line 105)
     // Enable MMU                                                                                                          // ( From test_stage/test_boot.py, line 107)
     mrs x0, sctlr_el3                                                                                                      // ( From test_stage/test_boot.py, line 108)
     orr x0, x0, #1 // Set bit 0 (MMU enable)                                                                               // ( From test_stage/test_boot.py, line 109)
     orr x0, x0, #(1 << 2) // Set bit 2 (Data cache enable)                                                                 // ( From test_stage/test_boot.py, line 110)
     bic x0, x0, #(1 << 20) // Clear bit 20 (WXN)                                                                           // ( From test_stage/test_boot.py, line 111)
     msr sctlr_el3, x0                                                                                                      // ( From test_stage/test_boot.py, line 112)
     isb // Instruction Synchronization Barrier, must to ensure context-syncronization after enabling MMU                   // ( From test_stage/test_boot.py, line 113)
     // Now the MMU is enabled with your page tables                                                                        // ( From test_stage/test_boot.py, line 115)
     // Code can now access virtual addresses defined in your page tables                                                   // ( From test_stage/test_boot.py, line 116)
     // Set up EL1 Non-Secure Translation Tables                                                                            // ( From test_stage/test_boot.py, line 126)
     // First disable the EL1 MMU                                                                                           // ( From test_stage/test_boot.py, line 129)
     mrs x13, sctlr_el1                                                                                                     // ( From test_stage/test_boot.py, line 130)
     bic x13, x13, #1 // Clear bit 0 (MMU enable)                                                                           // ( From test_stage/test_boot.py, line 131)
     msr sctlr_el1, x13                                                                                                     // ( From test_stage/test_boot.py, line 132)
     // Set up TTBR0_EL1 (EL1 Translation Table Base Register 0)                                                            // ( From test_stage/test_boot.py, line 134)
     ldr x13, =LABEL_TTBR0_EL1NS_core_1 // read value of LABEL_TTBR0_EL1NS from memory                                      // ( From test_stage/test_boot.py, line 135)
     ldr x13, [x13] // load the value of LABEL_TTBR0_EL1NS                                                                  // ( From test_stage/test_boot.py, line 136)
     msr ttbr0_el1, x13                                                                                                     // ( From test_stage/test_boot.py, line 137)
     // Set up TTBR1_EL1 (EL1 Translation Table Base Register 1)                                                            // ( From test_stage/test_boot.py, line 139)
     ldr x13, =LABEL_TTBR1_EL1NS_core_1 // read value of LABEL_TTBR1_EL1NS from memory                                      // ( From test_stage/test_boot.py, line 140)
     ldr x13, [x13] // load the value of LABEL_TTBR1_EL1NS                                                                  // ( From test_stage/test_boot.py, line 141)
     msr ttbr1_el1, x13                                                                                                     // ( From test_stage/test_boot.py, line 142)
     // Set up TCR_EL1 (EL1 Translation Control Register)                                                                   // ( From test_stage/test_boot.py, line 144)
     ldr x13, =LABEL_TCR_EL1NS_core_1 // read value of LABEL_TCR_EL1NS from memory                                          // ( From test_stage/test_boot.py, line 145)
     ldr x13, [x13] // load the value of LABEL_TCR_EL1NS                                                                    // ( From test_stage/test_boot.py, line 146)
     msr tcr_el1, x13                                                                                                       // ( From test_stage/test_boot.py, line 147)
     // Set up MAIR_EL1 (EL1 Memory Attribute Indirection Register)                                                         // ( From test_stage/test_boot.py, line 149)
     ldr x13, =LABEL_MAIR_EL1NS_core_1 // read value of LABEL_MAIR_EL1NS from memory                                        // ( From test_stage/test_boot.py, line 150)
     ldr x13, [x13] // load the value of LABEL_MAIR_EL1NS                                                                   // ( From test_stage/test_boot.py, line 151)
     msr mair_el1, x13                                                                                                      // ( From test_stage/test_boot.py, line 152)
     // Enable EL1 MMU                                                                                                      // ( From test_stage/test_boot.py, line 155)
     mrs x13, sctlr_el1 // read EL1 system control register                                                                 // ( From test_stage/test_boot.py, line 156)
     orr x13, x13, #1 // set MMU enable bit (M bit)                                                                         // ( From test_stage/test_boot.py, line 157)
     orr x13, x13, #(1 << 2) // Set bit 2 (Data cache enable)                                                               // ( From test_stage/test_boot.py, line 158)
     bic x13, x13, #(1 << 20) // Clear bit 20 (WXN)                                                                         // ( From test_stage/test_boot.py, line 159)
     msr sctlr_el1, x13 // enable EL1 MMU                                                                                   // ( From test_stage/test_boot.py, line 160)
     isb // Instruction Synchronization Barrier, ensure MMU changes take effect                                             // ( From test_stage/test_boot.py, line 161)
     // EL1 MMU configuration complete                                                                                      // ( From test_stage/test_boot.py, line 163)
     // Now both EL3 and EL1 page tables are configured                                                                     // ( From test_stage/test_boot.py, line 164)
     ldr x5, =label_4887_exception_table_core_1_el3_root_code_segment // load the address of the vbar label                 // ( From test_stage/test_boot.py, line 182)
     msr vbar_el3, x5 // set the vbar_el3 address                                                                           // ( From test_stage/test_boot.py, line 183)
     ldr x13, =label_4894_exception_table_core_1_el1_ns_code_segment // load the address of the vbar label                  // ( From test_stage/test_boot.py, line 182)
     msr vbar_el1, x13 // set the vbar_el1 address                                                                          // ( From test_stage/test_boot.py, line 183)
     // ==== starting barrier sequence - label_4901_end_boot_barrier ====                                                   // ( From test_stage/test_boot.py, line 59)
     mrs x21, mpidr_el1                                                                                                     // ( From test_stage/test_boot.py, line 59)
     and w10, w21, #0xff // Extract Aff0 (core within cluster)                                                              // ( From test_stage/test_boot.py, line 59)
     lsr x23, x21, #16 // Shift right by 16 to get Aff2 in lower bits                                                       // ( From test_stage/test_boot.py, line 59)
     and w23, w23, #0xff // Extract Aff2 (cluster ID)                                                                       // ( From test_stage/test_boot.py, line 59)
     lsl w23, w23, #1 // cluster_id * 2 (2 cores per cluster)                                                               // ( From test_stage/test_boot.py, line 59)
     add w21, w10, w23 // sequential_core_id = core_in_cluster + (cluster_id * 2)                                           // ( From test_stage/test_boot.py, line 59)
     // Calculate the bit position for this core                                                                            // ( From test_stage/test_boot.py, line 59)
     mov w10, #1                                                                                                            // ( From test_stage/test_boot.py, line 59)
     lsl w10, w10, w21 // w1 = 1 << unique_core_id                                                                          // ( From test_stage/test_boot.py, line 59)
     // Set this core's bit in the barrier vector (active low)                                                              // ( From test_stage/test_boot.py, line 59)
     ldr x21, =label_4901_end_boot_barrier_barrier_vector_mem1985__core_1_el3_root                                          // ( From test_stage/test_boot.py, line 59)
     stclr w10, [x21]                                                                                                       // ( From test_stage/test_boot.py, line 59)
     // Spin until all bits are clear (active low)                                                                          // ( From test_stage/test_boot.py, line 59)
     label_4904_spin_label:                                                                                                 // ( From test_stage/test_boot.py, line 59)
     ldr w23, [x21]                                                                                                         // ( From test_stage/test_boot.py, line 59)
     cbnz w23, label_4904_spin_label // Continue spinning if any bit is set                                                 // ( From test_stage/test_boot.py, line 59)
     // Barrier reached - all cores have arrived                                                                            // ( From test_stage/test_boot.py, line 59)
     // ==== finished barrier sequence - label_4901_end_boot_barrier ====                                                   // ( From test_stage/test_boot.py, line 59)
     // using 'B' (branch) for unconditional 'one-way' branch (similar to jmp) to code segment core_1_el3_root__code_segment_2_1327// ( From test_stage/test_boot.py, line 64)
     B label_4905_core_1_el3_root__code_segment_2_1327_branchToSegment_target // Jump to code_label                         // ( From test_stage/test_boot.py, line 64)
     // ========================= CORE_1 BOOT CODE - end =====================                                              // ( From test_stage/test_boot.py, line 68)

// No code on core_1_el3_root__code_segment_0_1325 segment. skipping .text section

.section .text.core_1_el3_root__code_segment_1_1326
.global core_1_el3_root__code_segment_1_1326
core_1_el3_root__code_segment_1_1326:
     label_4860_core_1_el3_root__code_segment_1_code_segment: // starting label for core_1_el3_root__code_segment_1 code Segment// ( From memlayout/segment_manager.py, line 105)
     label_4918_core_1_el3_root__code_segment_1_1326_branchToSegment_target:                                                // ( From test_stage/test_body.py, line 64)
     // ========================== Start scenario random_instructions ====================                                  // ( From test_stage/test_body.py, line 14)
     // inside random_instructions                                                                                          // ( From templates/direct_template.py, line 18)
     frintp d25, d24                                                                                                        // ( From templates/direct_template.py, line 21)
     esb                                                                                                                    // ( From templates/direct_template.py, line 21)
     ldr x2, =mem1993+4 // dynamic init: loading x2 with reused memory mem2007 (0xaf557c68:0x1c0412c68) for next instruction// ( From templates/direct_template.py, line 21)
     ldsmaxl x1, x8, [x2]                                                                                                   // ( From templates/direct_template.py, line 21)
     ldr x16, =mem2008+0 // dynamic init: loading x16 for next instruction (0xaf557ef0:0x1c0412ef0)                         // ( From templates/direct_template.py, line 21)
     ld1rh z22.H, p5/Z, [x16, #0]                                                                                           // ( From templates/direct_template.py, line 21)
     ldr x23, =mem2009+0 // dynamic init: loading x23 for next instruction (0xaf557fd9:0x1c0412fd9)                         // ( From templates/direct_template.py, line 21)
     ldr b19, [x23, #0]!                                                                                                    // ( From templates/direct_template.py, line 21)
     ldr x20, =mem1993+4 // dynamic init: loading x20 with reused memory mem2010 (0xaf557c68:0x1c0412c68) for next instruction// ( From templates/direct_template.py, line 21)
     swpah w14, w2, [x20]                                                                                                   // ( From templates/direct_template.py, line 21)
     fcvtas h25, h16                                                                                                        // ( From templates/direct_template.py, line 21)
     frintp v12.8H, v19.8H                                                                                                  // ( From templates/direct_template.py, line 21)
     ldr x28, =mem2008+0 // dynamic init: loading x28 with reused memory mem2011 (0xaf557ef0:0x1c0412ef0) for next instruction// ( From templates/direct_template.py, line 21)
     // Starting loop with 50 iterations. using a x3 operand and a label_4919_loop_label label                              // ( From templates/direct_template.py, line 24)
     mov x3, #0                                                                                                             // ( From templates/direct_template.py, line 24)
     label_4919_loop_label:                                                                                                 // ( From templates/direct_template.py, line 24)
     adclb z28.D, z11.D, z28.D                                                                                              // ( From templates/direct_template.py, line 26)
     decp z26.D, p1.D                                                                                                       // ( From templates/direct_template.py, line 27)
     nand p11.B, p1/Z, p9.B, p4.B                                                                                           // ( From templates/direct_template.py, line 27)
     adcs w23, w24, w21                                                                                                     // ( From templates/direct_template.py, line 26)
     fmov h15, w6                                                                                                           // ( From templates/direct_template.py, line 27)
     ucvtf s26, w7                                                                                                          // ( From templates/direct_template.py, line 27)
     adcs w19, w1, w13                                                                                                      // ( From templates/direct_template.py, line 26)
     fmov d27, x11                                                                                                          // ( From templates/direct_template.py, line 27)
     fmov d27, x20                                                                                                          // ( From templates/direct_template.py, line 27)
     add x3, x3, #1 // Increment the loop counter (x3 += 1)                                                                 // ( From templates/direct_template.py, line 24)
     cmp x3, #50 //  Compare x3 with 50                                                                                     // ( From templates/direct_template.py, line 24)
     bne label_4919_loop_label                                                                                              // ( From templates/direct_template.py, line 24)
     // Ending loop                                                                                                         // ( From templates/direct_template.py, line 24)
     add x25, x25, x8 // adding x25 = x25 + x8                                                                              // ( From templates/direct_template.py, line 32)
     ldr x15, =mem2012+0 // dynamic init: loading x15 for next instruction (0x14455d810:0x1d0d5d810)                        // ( From templates/direct_template.py, line 33)
     lduminal x20, x25, [x15] // store reg                                                                                  // ( From templates/direct_template.py, line 33)
     ldr x13, =mem2013+0 // dynamic init: loading x13 for next instruction (0x233ed8d94:0x1d7ed8d94)                        // ( From templates/direct_template.py, line 42)
     stllr w1, [x13, #0] // load mem                                                                                        // ( From templates/direct_template.py, line 42)
     ldr x17, =mem2013+0 // dynamic init: loading x17 for next instruction (0x233ed8d94:0x1d7ed8d94)                        // ( From templates/direct_template.py, line 43)
     strb w26, [x17], #0 // store mem                                                                                       // ( From templates/direct_template.py, line 43)
     // Starting loop with 100 iterations. using a x28 operand and a label_4920_loop_label label                            // ( From templates/direct_template.py, line 50)
     mov x28, #100                                                                                                          // ( From templates/direct_template.py, line 50)
     label_4920_loop_label:                                                                                                 // ( From templates/direct_template.py, line 50)
     ldr x5, =10711041904                                                                                                   // ( From templates/direct_template.py, line 51)
     // EventTrigger:: Setting event trigger flow with Frequency.LOW frequency                                              // ( From templates/direct_template.py, line 53)
     // EventTrigger:: Using mem at 0x27e6d8423 with the following 64bit pattern: 0000000000000000000000000000000000000000000100000000000000000000// ( From templates/direct_template.py, line 53)
     ldr x21, =0x27e6d8423                                                                                                  // ( From templates/direct_template.py, line 53)
     ldr x13, [x21] // load the vector from mem 0x27e6d8423                                                                 // ( From templates/direct_template.py, line 53)
     ror x13, x13, #1 // rotate the vector                                                                                  // ( From templates/direct_template.py, line 53)
     str x13, [x21] // store back the vector into the memory location                                                       // ( From templates/direct_template.py, line 53)
     tbz x13, #63, label_4921_skip_label // test bit 63 and branch if 0 (zero)                                              // ( From templates/direct_template.py, line 53)
     ldr x5, =10711041620                                                                                                   // ( From templates/direct_template.py, line 54)
     label_4921_skip_label:                                                                                                 // ( From templates/direct_template.py, line 53)
     ldr x17, [x5]                                                                                                          // ( From templates/direct_template.py, line 57)
     sub x28, x28, #1 // Decrement the loop counter (x28 -= 1)                                                              // ( From templates/direct_template.py, line 50)
     cmp x28, #0 //  Compare x28 with 0                                                                                     // ( From templates/direct_template.py, line 50)
     bne label_4920_loop_label                                                                                              // ( From templates/direct_template.py, line 50)
     // Ending loop                                                                                                         // ( From templates/direct_template.py, line 50)
     // ========================== End scenario random_instructions ====================                                    // ( From test_stage/test_body.py, line 40)
     // Return to the previous code segment core_1_el3_root__code_segment_3_1328 using the address in `LR` (similar to `ret stack` in x86)// ( From test_stage/test_body.py, line 64)
     RET // Returns from a function using the LR (x30) register.                                                            // ( From test_stage/test_body.py, line 64)

.section .text.core_1_el3_root__code_segment_2_1327
.global core_1_el3_root__code_segment_2_1327
core_1_el3_root__code_segment_2_1327:
     label_4861_core_1_el3_root__code_segment_2_code_segment: // starting label for core_1_el3_root__code_segment_2 code Segment// ( From memlayout/segment_manager.py, line 105)
     label_4905_core_1_el3_root__code_segment_2_1327_branchToSegment_target:                                                // ( From test_stage/test_boot.py, line 64)
     // ========================= core core_1 - TEST BODY - start =====================                                     // ( From test_stage/test_body.py, line 83)
     // BODY:: Running core_1, scenario 1(:2), scenario random_instructions                                                 // ( From test_stage/test_body.py, line 60)
     // using 'B' (branch) for unconditional 'one-way' branch (similar to jmp) to code segment core_1_el3_root__code_segment_3_1328// ( From test_stage/test_body.py, line 67)
     B label_4910_core_1_el3_root__code_segment_3_1328_branchToSegment_target // Jump to code_label                         // ( From test_stage/test_body.py, line 67)

.section .text.core_1_el3_root__code_segment_3_1328
.global core_1_el3_root__code_segment_3_1328
core_1_el3_root__code_segment_3_1328:
     label_4862_core_1_el3_root__code_segment_3_code_segment: // starting label for core_1_el3_root__code_segment_3 code Segment// ( From memlayout/segment_manager.py, line 105)
     label_4910_core_1_el3_root__code_segment_3_1328_branchToSegment_target:                                                // ( From test_stage/test_body.py, line 67)
     // ========================== Start scenario random_instructions ====================                                  // ( From test_stage/test_body.py, line 14)
     // inside random_instructions                                                                                          // ( From templates/direct_template.py, line 18)
     fcvtmu w21, s23                                                                                                        // ( From templates/direct_template.py, line 21)
     fminnm v23.8H, v5.8H, v12.8H                                                                                           // ( From templates/direct_template.py, line 21)
     fadd z5.D, p7/M, z5.D, z15.D                                                                                           // ( From templates/direct_template.py, line 21)
     clasta z1.S, p3, z1.S, z4.S                                                                                            // ( From templates/direct_template.py, line 21)
     ldr x1, =mem1993+4 // dynamic init: loading x1 for next instruction (0xaf557c68:0x1c0412c68)                           // ( From templates/direct_template.py, line 21)
     ldaprh w8, [x1, #0]                                                                                                    // ( From templates/direct_template.py, line 21)
     fmaxnm d19, d27, d1                                                                                                    // ( From templates/direct_template.py, line 21)
     fcvt z3.D, p2/M, z4.S                                                                                                  // ( From templates/direct_template.py, line 21)
     fcvtmu x15, d11                                                                                                        // ( From templates/direct_template.py, line 21)
     // Starting loop with 50 iterations. using a x17 operand and a label_4911_loop_label label                             // ( From templates/direct_template.py, line 24)
     mov x17, #50                                                                                                           // ( From templates/direct_template.py, line 24)
     label_4911_loop_label:                                                                                                 // ( From templates/direct_template.py, line 24)
     adc w2, w27, w6                                                                                                        // ( From templates/direct_template.py, line 26)
     fmov h14, x7                                                                                                           // ( From templates/direct_template.py, line 27)
     adc w10, w1, w6                                                                                                        // ( From templates/direct_template.py, line 26)
     decp x23, p11.D                                                                                                        // ( From templates/direct_template.py, line 27)
     sqincp z16.S, p11.S                                                                                                    // ( From templates/direct_template.py, line 27)
     adclb z8.S, z5.S, z10.S                                                                                                // ( From templates/direct_template.py, line 26)
     fmov x27, d16                                                                                                          // ( From templates/direct_template.py, line 27)
     fmov h14, x27                                                                                                          // ( From templates/direct_template.py, line 27)
     sub x17, x17, #1 // Decrement the loop counter (x17 -= 1)                                                              // ( From templates/direct_template.py, line 24)
     cmp x17, #0 //  Compare x17 with 0                                                                                     // ( From templates/direct_template.py, line 24)
     bne label_4911_loop_label                                                                                              // ( From templates/direct_template.py, line 24)
     // Ending loop                                                                                                         // ( From templates/direct_template.py, line 24)
     add x3, x3, x14 // adding x3 = x3 + x14                                                                                // ( From templates/direct_template.py, line 32)
     sbc x3, x23, x14 // store reg                                                                                          // ( From templates/direct_template.py, line 33)
     ldr x4, =mem1994+0 // dynamic init: loading x4 for next instruction (0x233ed8f3c:0x1d7ed8f3c)                          // ( From templates/direct_template.py, line 42)
     ldp s8, s15, [x4, #0]! // load mem                                                                                     // ( From templates/direct_template.py, line 42)
     ldr x12, =mem1994+0 // dynamic init: loading x12 for next instruction (0x233ed8f3c:0x1d7ed8f3c)                        // ( From templates/direct_template.py, line 43)
     // Starting loop with 100 iterations. using a x0 operand and a label_4912_loop_label label                             // ( From templates/direct_template.py, line 50)
     mov x0, #0                                                                                                             // ( From templates/direct_template.py, line 50)
     label_4912_loop_label:                                                                                                 // ( From templates/direct_template.py, line 50)
     ldr x1, =9461140524                                                                                                    // ( From templates/direct_template.py, line 51)
     // EventTrigger:: Setting event trigger flow with Frequency.LOW frequency                                              // ( From templates/direct_template.py, line 53)
     // EventTrigger:: Using mem at 0x27e6d8d38 with the following 64bit pattern: 0000000000000000000000010000000000000000000000100000000100000000// ( From templates/direct_template.py, line 53)
     ldr x17, =0x27e6d8d38                                                                                                  // ( From templates/direct_template.py, line 53)
     ldr x9, [x17] // load the vector from mem 0x27e6d8d38                                                                  // ( From templates/direct_template.py, line 53)
     ror x9, x9, #1 // rotate the vector                                                                                    // ( From templates/direct_template.py, line 53)
     str x9, [x17] // store back the vector into the memory location                                                        // ( From templates/direct_template.py, line 53)
     tbz x9, #63, label_4913_skip_label // test bit 63 and branch if 0 (zero)                                               // ( From templates/direct_template.py, line 53)
     ldr x1, =10711040992                                                                                                   // ( From templates/direct_template.py, line 54)
     label_4913_skip_label:                                                                                                 // ( From templates/direct_template.py, line 53)
     ldr x21, [x1]                                                                                                          // ( From templates/direct_template.py, line 57)
     add x0, x0, #1 // Increment the loop counter (x0 += 1)                                                                 // ( From templates/direct_template.py, line 50)
     cmp x0, #100 //  Compare x0 with 100                                                                                   // ( From templates/direct_template.py, line 50)
     bne label_4912_loop_label                                                                                              // ( From templates/direct_template.py, line 50)
     // Ending loop                                                                                                         // ( From templates/direct_template.py, line 50)
     // ========================== End scenario random_instructions ====================                                    // ( From test_stage/test_body.py, line 40)
     // BODY:: Running core_1, scenario 2(:2), scenario random_instructions                                                 // ( From test_stage/test_body.py, line 60)
     // branch with link `label` by jumping to code segment core_1_el3_root__code_segment_1_1326 and storing the return address in `LR` (Link Register) register// ( From test_stage/test_body.py, line 64)
     bl label_4918_core_1_el3_root__code_segment_1_1326_branchToSegment_target // Branch with Link to target address        // ( From test_stage/test_body.py, line 64)
     // ========================= core core_1 - TEST BODY - end =====================                                       // ( From test_stage/test_body.py, line 103)
     // ==== starting barrier sequence - label_4922_end_test_barrier ====                                                   // ( From test_stage/test_final.py, line 22)
     mrs x5, mpidr_el1                                                                                                      // ( From test_stage/test_final.py, line 22)
     and w1, w5, #0xff // Extract Aff0 (core within cluster)                                                                // ( From test_stage/test_final.py, line 22)
     lsr x14, x5, #16 // Shift right by 16 to get Aff2 in lower bits                                                        // ( From test_stage/test_final.py, line 22)
     and w14, w14, #0xff // Extract Aff2 (cluster ID)                                                                       // ( From test_stage/test_final.py, line 22)
     lsl w14, w14, #1 // cluster_id * 2 (2 cores per cluster)                                                               // ( From test_stage/test_final.py, line 22)
     add w5, w1, w14 // sequential_core_id = core_in_cluster + (cluster_id * 2)                                             // ( From test_stage/test_final.py, line 22)
     // Calculate the bit position for this core                                                                            // ( From test_stage/test_final.py, line 22)
     mov w1, #1                                                                                                             // ( From test_stage/test_final.py, line 22)
     lsl w1, w1, w5 // w1 = 1 << unique_core_id                                                                             // ( From test_stage/test_final.py, line 22)
     // Set this core's bit in the barrier vector (active low)                                                              // ( From test_stage/test_final.py, line 22)
     ldr x5, =label_4922_end_test_barrier_barrier_vector_mem2017__core_1_el3_root                                           // ( From test_stage/test_final.py, line 22)
     stclr w1, [x5]                                                                                                         // ( From test_stage/test_final.py, line 22)
     // Spin until all bits are clear (active low)                                                                          // ( From test_stage/test_final.py, line 22)
     label_4927_spin_label:                                                                                                 // ( From test_stage/test_final.py, line 22)
     ldr w14, [x5]                                                                                                          // ( From test_stage/test_final.py, line 22)
     cbnz w14, label_4927_spin_label // Continue spinning if any bit is set                                                 // ( From test_stage/test_final.py, line 22)
     // Barrier reached - all cores have arrived                                                                            // ( From test_stage/test_final.py, line 22)
     // ==== finished barrier sequence - label_4922_end_test_barrier ====                                                   // ( From test_stage/test_final.py, line 22)
     // Test ended successfully                                                                                             // ( From test_stage/test_final.py, line 25)
     // End test logic:                                                                                                     // ( From test_stage/test_final.py, line 25)
     // core_1 reached end of test, waiting for Trickbox to be closed                                                       // ( From test_stage/test_final.py, line 25)
     label_4928_core_1_end_of_test:                                                                                         // ( From test_stage/test_final.py, line 25)
     wfi                                                                                                                    // ( From test_stage/test_final.py, line 25)
     b label_4928_core_1_end_of_test                                                                                        // ( From test_stage/test_final.py, line 25)

// No code on core_1_el3_root__code_segment_4_1329 segment. skipping .text section

// No code on core_1_el3_root__code_segment_5_1330 segment. skipping .text section

.section .text.exception_table_core_1_el3_root_1349
.global exception_table_core_1_el3_root_1349
exception_table_core_1_el3_root_1349:
     label_4887_exception_table_core_1_el3_root_code_segment: // starting label for exception_table_core_1_el3_root code Segment// ( From memlayout/segment_manager.py, line 105)
     // ================ exception table for core_1 core_1_el3_root =====================                                   // ( From exception_management/__init__.py, line 110)
     .org 0x0                                                                                                               // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_SYNCHRONOUS - target label label_4885_halting_label                   // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x80                                                                                                              // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_IRQ - target label label_4885_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x100                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_FIQ - target label label_4885_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x180                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_SERROR - target label label_4885_halting_label                        // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x200                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_SYNCHRONOUS - target label label_4885_halting_label                   // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x280                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_IRQ - target label label_4885_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x300                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_FIQ - target label label_4885_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x380                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_SERROR - target label label_4885_halting_label                        // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x400                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_SYNCHRONOUS - target label label_4886_callback_label                    // ( From exception_management/__init__.py, line 114)
     b label_4886_callback_label                                                                                            // ( From exception_management/__init__.py, line 115)
     .org 0x480                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_IRQ - target label label_4885_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x500                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_FIQ - target label label_4885_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x580                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_SERROR - target label label_4885_halting_label                          // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x600                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_SYNCHRONOUS - target label label_4885_halting_label                     // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x680                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_IRQ - target label label_4885_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x700                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_FIQ - target label label_4885_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x780                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_SERROR - target label label_4885_halting_label                          // ( From exception_management/__init__.py, line 114)
     b label_4885_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     label_4885_halting_label:                                                                                              // ( From exception_management/__init__.py, line 118)
     // default halting hander                                                                                              // ( From exception_management/__init__.py, line 119)
     nop                                                                                                                    // ( From exception_management/__init__.py, line 120)
     mrs x0, esr_el1 // Read cause of exception                                                                             // ( From exception_management/__init__.py, line 136)
     ubfx x1, x0, #26, #6 // Extract EC (bits[31:26])                                                                       // ( From exception_management/__init__.py, line 137)
     cmp x1, #0x00 // EC = 0b000000 = undefined instruction                                                                 // ( From exception_management/__init__.py, line 138)
     b.ne label_4888_halting_handler_test_fail_label // handle undefined instruction                                        // ( From exception_management/__init__.py, line 139)
     ldr x0, =core_1_el3_root__exception_callback_LOWER_A64_SYNC_mem1981                                                    // ( From exception_management/__init__.py, line 141)
     ldr x1, [x0]                                                                                                           // ( From exception_management/__init__.py, line 142)
     br x1                                                                                                                  // ( From exception_management/__init__.py, line 143)
     label_4888_halting_handler_test_fail_label:                                                                            // ( From exception_management/__init__.py, line 145)
     // Test failed with error code of 0x0                                                                                  // ( From exception_management/__init__.py, line 147)
     // End test logic:                                                                                                     // ( From exception_management/__init__.py, line 147)
     // core_1 reached end of test, waiting for Trickbox to be closed                                                       // ( From exception_management/__init__.py, line 147)
     label_4889_core_1_end_of_test:                                                                                         // ( From exception_management/__init__.py, line 147)
     wfi                                                                                                                    // ( From exception_management/__init__.py, line 147)
     b label_4889_core_1_end_of_test                                                                                        // ( From exception_management/__init__.py, line 147)
     label_4886_callback_label:                                                                                             // ( From exception_management/__init__.py, line 150)
     // default callback handler                                                                                            // ( From exception_management/__init__.py, line 151)
     nop                                                                                                                    // ( From exception_management/__init__.py, line 152)
     ldr x0, =core_1_el3_root__exception_callback_LOWER_A64_SYNC_mem1982                                                    // ( From exception_management/__init__.py, line 166)
     ldr x1, [x0]                                                                                                           // ( From exception_management/__init__.py, line 167)
     br x1                                                                                                                  // ( From exception_management/__init__.py, line 168)
     // ================ end of exception table for core_1 core_1_el3_root ===============                                  // ( From exception_management/__init__.py, line 171)

// No code on core_1_el1_ns__code_segment_0_1336 segment. skipping .text section

// No code on core_1_el1_ns__code_segment_1_1337 segment. skipping .text section

// No code on core_1_el1_ns__code_segment_2_1338 segment. skipping .text section

// No code on core_1_el1_ns__code_segment_3_1339 segment. skipping .text section

// No code on core_1_el1_ns__code_segment_4_1340 segment. skipping .text section

// No code on core_1_el1_ns__code_segment_5_1341 segment. skipping .text section

.section .text.exception_table_core_1_el1_ns_1350
.global exception_table_core_1_el1_ns_1350
exception_table_core_1_el1_ns_1350:
     label_4894_exception_table_core_1_el1_ns_code_segment: // starting label for exception_table_core_1_el1_ns code Segment// ( From memlayout/segment_manager.py, line 105)
     // ================ exception table for core_1 core_1_el1_ns =====================                                     // ( From exception_management/__init__.py, line 110)
     .org 0x0                                                                                                               // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_SYNCHRONOUS - target label label_4892_halting_label                   // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x80                                                                                                              // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_IRQ - target label label_4892_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x100                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_FIQ - target label label_4892_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x180                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SP0_SERROR - target label label_4892_halting_label                        // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x200                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_SYNCHRONOUS - target label label_4892_halting_label                   // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x280                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_IRQ - target label label_4892_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x300                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_FIQ - target label label_4892_halting_label                           // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x380                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.CURRENT_SPX_SERROR - target label label_4892_halting_label                        // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x400                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_SYNCHRONOUS - target label label_4893_callback_label                    // ( From exception_management/__init__.py, line 114)
     b label_4893_callback_label                                                                                            // ( From exception_management/__init__.py, line 115)
     .org 0x480                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_IRQ - target label label_4892_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x500                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_FIQ - target label label_4892_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x580                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A64_SERROR - target label label_4892_halting_label                          // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x600                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_SYNCHRONOUS - target label label_4892_halting_label                     // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x680                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_IRQ - target label label_4892_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x700                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_FIQ - target label label_4892_halting_label                             // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     .org 0x780                                                                                                             // ( From exception_management/__init__.py, line 113)
     //  exception AArch64ExceptionVector.LOWER_A32_SERROR - target label label_4892_halting_label                          // ( From exception_management/__init__.py, line 114)
     b label_4892_halting_label                                                                                             // ( From exception_management/__init__.py, line 115)
     label_4892_halting_label:                                                                                              // ( From exception_management/__init__.py, line 118)
     // default halting hander                                                                                              // ( From exception_management/__init__.py, line 119)
     nop                                                                                                                    // ( From exception_management/__init__.py, line 120)
     mrs x0, esr_el1 // Read cause of exception                                                                             // ( From exception_management/__init__.py, line 136)
     ubfx x1, x0, #26, #6 // Extract EC (bits[31:26])                                                                       // ( From exception_management/__init__.py, line 137)
     cmp x1, #0x00 // EC = 0b000000 = undefined instruction                                                                 // ( From exception_management/__init__.py, line 138)
     b.ne label_4895_halting_handler_test_fail_label // handle undefined instruction                                        // ( From exception_management/__init__.py, line 139)
     ldr x0, =core_1_el1_ns__exception_callback_LOWER_A64_SYNC_mem1983                                                      // ( From exception_management/__init__.py, line 141)
     ldr x1, [x0]                                                                                                           // ( From exception_management/__init__.py, line 142)
     br x1                                                                                                                  // ( From exception_management/__init__.py, line 143)
     label_4895_halting_handler_test_fail_label:                                                                            // ( From exception_management/__init__.py, line 145)
     // Test failed with error code of 0x0                                                                                  // ( From exception_management/__init__.py, line 147)
     // End test logic:                                                                                                     // ( From exception_management/__init__.py, line 147)
     // core_1 reached end of test, waiting for Trickbox to be closed                                                       // ( From exception_management/__init__.py, line 147)
     label_4896_core_1_end_of_test:                                                                                         // ( From exception_management/__init__.py, line 147)
     wfi                                                                                                                    // ( From exception_management/__init__.py, line 147)
     b label_4896_core_1_end_of_test                                                                                        // ( From exception_management/__init__.py, line 147)
     label_4893_callback_label:                                                                                             // ( From exception_management/__init__.py, line 150)
     // default callback handler                                                                                            // ( From exception_management/__init__.py, line 151)
     nop                                                                                                                    // ( From exception_management/__init__.py, line 152)
     ldr x0, =core_1_el1_ns__exception_callback_LOWER_A64_SYNC_mem1984                                                      // ( From exception_management/__init__.py, line 166)
     ldr x1, [x0]                                                                                                           // ( From exception_management/__init__.py, line 167)
     br x1                                                                                                                  // ( From exception_management/__init__.py, line 168)
     // ================ end of exception table for core_1 core_1_el1_ns ===============                                    // ( From exception_management/__init__.py, line 171)



.section .data.core_0_el3_root__data_shared_segment_0_1308
.global core_0_el3_root__data_shared_segment_0_1308
core_0_el3_root__data_shared_segment_0_1308:
    .quad 0xd8bdd8dacf618f0a
    .quad 0x255d0c13f5f149db
    .quad 0x41a673eca8ccf555
    .quad 0xe0a99e9a95eae527
    .quad 0x52dae8b56fc43eda
    .quad 0x8a181a45fa5d339b
    .quad 0x2152a841c57a0f2a
    .quad 0xa9e14c9658dcca0f
    .quad 0x53a08182cc18ba45
    .quad 0x23dca56ce18e73b8
    .quad 0x0bdad27c07b634e2
    .quad 0x2348364939f6ee8a
    .quad 0x7db3406cad62c9fe
    .quad 0x585fcab3a69dab58
    .quad 0x7e5f300fd25e6d5f
    .quad 0x76955a21b02aa1d7
    .quad 0x89fb8aae594cca6f
    .quad 0x477ab3cec80f2f27
    .quad 0xfaeafa35443ee9d5
    .quad 0xfcb063b783cd234a
    .quad 0xf5f7d74743d9963e
    .quad 0xc69ecc0d82c6ec3e
    .quad 0xb7fdaba30ab47295
    .quad 0x436e30f358d7300f
    .quad 0xefa09ee441b7776f
    .quad 0xd48ce9a6d5f5bfdb
    .quad 0x6bcff78ab648fe63
    .quad 0xa23923f4aaf08185
    .quad 0x587090a2734a4211
    .quad 0x33e64ee68916023a
    .quad 0x42176b52ecb6dcc8
    .quad 0x230e5995283b1aae
    .quad 0xb24f1cc86ee8c0b6
    .quad 0x6c72653d405866d7
    .quad 0x84e344a31277dfa4
    .quad 0x27b7c52b88474261
    .quad 0x85ce87e3176e45d0
    .quad 0x32cb5c346dddd037
    .quad 0xc80c2c7e61378777
    .quad 0xd52a79d29cdcd68c
    .quad 0x7f4bdabd39473991
    .quad 0x1af21ea56b95241d
    .quad 0x87248d23c4865857
    .quad 0xaae0548f63d335bd
    .quad 0x320e78e38349a41c
    .quad 0x6ffaa2f5630319ce
    .quad 0xea33af646b5be783
    .quad 0x947daf7ec7bba147
    .quad 0x296df3882d8fd917
    .quad 0xd95ecfa84f9d9db2
    .quad 0xc77445b9c6a47db8
    .quad 0x57d3c95a9cb6f849
    .quad 0x936426881cfe9adf
    .quad 0xdca7cc3b76576ca7
    .quad 0x4e127e1465080827
    .quad 0x4378b2fcc7f5d715
    .quad 0x580bc0b3442f2cca
    .quad 0x41e67daa2fa2e2f7
    .quad 0x524e572d72d2f65c
    .quad 0xac28eb269c0c99ff
    .quad 0x22330a73ffddc15d
    .quad 0xdcefc799802288a5
    .quad 0x353861a5f4095042
    .quad 0xcc4addffa7181762
    .quad 0xa408e4da6f3b1d6f
    .quad 0xf95ba58a69ed494a
    .quad 0xc4ca6d4778791e1f
    .quad 0xa1ba29c0f02b63b9
    .quad 0xde0b477711315c11
    .quad 0xd1051f58068baf44
    .quad 0x0b3d341a10b76de8
    .quad 0x0adba750260b1fa3
    .quad 0x1ffd097d3a4977ed
    .quad 0xcefdaad22b1b3731
    .quad 0x04d3dccc04aa6c15
    .quad 0x20f77b1e1214338d
    .quad 0x12204a2fb0ffd3d1
    .quad 0xda121745c38857a6
    .quad 0x768c2b93a79e2888
    .quad 0xa57ddacbbbd3ee0f
    .quad 0xa8e1a1d1325cf8f1
    .quad 0xa47f20b39559f417
    .quad 0x7950d2335b203f8d
    .quad 0x4c8802e885ede09c
    .quad 0x65fd6d89f55c0700
    .quad 0x69162788f0405a2f
    .quad 0x360e60b99558d927
    .quad 0x574b967f86a5b248
    .quad 0xf4008881adf67ea6
    .quad 0x5656acdd26160097
    .quad 0x80d379ae325d718d
    .quad 0xd0f4f0f27d9bc7e4
    .quad 0x3f48f4e9db77c779
    .quad 0x514eab749b8092c2
    .quad 0xbf94ea38ae217da2
    .quad 0x0ddccc775df1ff2a
    .quad 0xcd990ebe924d8b01
    .quad 0xf261e7f6528a798e
    .quad 0xb0437742371a7968
    .quad 0x7538dbf45f7affd8
    .quad 0x0cbba1acb7b76bdc
    .quad 0x1b0d437bc368ceeb
    .quad 0x70464cc8b21de353
    .quad 0x85e79aeb04a7717b
    .quad 0xb413337e83a5ba2c
    .quad 0x723719ae466a96da
    .quad 0xa3018e9981308dd6
    .quad 0x3108a5a2fda98701
    .quad 0x64552e168ec71325
    .quad 0x0d3431bcf2929398
    .quad 0x81f4921d71a89c94
    .quad 0x964549c633fb43ca
    .quad 0x6b66792f3bca8549
    .quad 0xbf042cebd7aad652
    .quad 0x872c28d330f55ae7
    .quad 0x9807d44d8a4c443a
    .quad 0xc6634769b3d60890
    .quad 0x1abce4ca227df253
    .quad 0x26b3d56845974f9d
    .quad 0x9078b13761629785
    .quad 0x3d6d41d2fbe1392d
    .quad 0xa3d7691338048314
    .quad 0x97dc47997463db8d
    .quad 0xc69172d2af1f6d3c
    .quad 0xf399c4989d9d7ee6
    .quad 0x44db27b9d6d11bbf
mem2000:
    .quad 0xc5918edb91b92e01
    .quad 0xddcd7811f9dcb9f1
    .quad 0xc24c21236ea8bbe8
    .quad 0xa3d47d84991221fd
    .quad 0x73ad0382892d547f
    .quad 0xd3839c5fcafbc104
    .quad 0x5435c83054d23251
    .quad 0xe73eec29b15c2656
    .quad 0x344874674bc2d2f0
    .quad 0x89dd36a9b0d0ba06
    .quad 0xc3843472002bc653
    .quad 0x986920935c833186
    .quad 0x79fa5f83c74a6f36
    .quad 0x02b0b56832adae9c
    .quad 0xb96891d1142700d4
    .quad 0x22dd01f08b1b7ee7
    .quad 0x16a5d48b87f51d7f
    .quad 0xa304a19b0cdd2a90
    .quad 0xcaae2afbb13edbf8
    .quad 0x6fd3160e713e5bbb
    .quad 0x2a8656bcb197063f
    .quad 0xcafdf9b1176be6a5
    .quad 0x60903d16a94eac0e
    .quad 0x5044ca3bf248f96d
    .quad 0xb386dbb47c68ba34
    .quad 0xfdd63e67aff951cd
    .quad 0xa4e4d1f78b2398fa
    .quad 0xfc13a320a45322fe
    .quad 0x1bcd28bbc7f57a32
    .quad 0x5e1eb1dd2da37bbc
    .quad 0x5ca3a615a6740b88
    .quad 0x80762e4b558a2912
    .quad 0x0c51e8214ecc378a
    .quad 0x96357254fa28044b
    .quad 0xe3abd30205f3aa24
    .quad 0x22bf715378bd7360
    .quad 0xe93759d1a17ecee7
    .quad 0xb2371c7d19df7429
    .quad 0x21820608056179fe
    .quad 0x2289295117d4e160
    .quad 0x6749227d62110e1c
    .quad 0xbe793715bd9cc491
    .quad 0x907fbb56deea593b
    .quad 0xba5585a9183fbe82
    .quad 0x0ab50976c23216d5
    .quad 0x27263452ca44ceb0
    .quad 0x10663a83fbb267b6
    .quad 0x0f6b5317aa80e037
    .quad 0xf14692640ac32c39
    .quad 0x1354a057980afa65
    .quad 0x54cd5d219825ee61
    .quad 0xe4e78efe5183700e
    .quad 0xacbdeb11682fb1ba
    .quad 0x2056ee3e97cc04ab
    .quad 0x0de2f4a760cd98de
    .quad 0x5e98ef8481c4c03c
    .quad 0x1e7f441f41587984
    .quad 0xdbfd349a16f2363d
    .quad 0x6d0fbbc93e65845c
    .quad 0x797d723ad6919156
    .quad 0xe7c3d7d13f383908
    .quad 0xa917490d68625ef9
    .quad 0x83e074a153d9a20b
    .quad 0x11ac7103687e2091
    .quad 0x490b5af0b9c1bac9
    .quad 0x546f4508a50abefc
    .quad 0x9f8e47cfc7699235
    .quad 0xeada2167121ebc2a
    .quad 0xe483738890183d1b
    .quad 0x3cdd81baadb3dd80
    .quad 0xb4f5b33c7070b766
    .quad 0x93900b2a81fca0f9
    .quad 0x26fe9bd72e7b865d
    .quad 0xed26338e19c5b993
    .quad 0xc727991b859c085f
    .quad 0x2e5591f8d45d0cd1
    .quad 0x223699a7600eb938
    .quad 0x704904db80339660
    .quad 0x5102834a08847474
    .quad 0xe448b1ff6b68aa73
    .quad 0x3fa5c80850bdf691
    .quad 0x889537148249ff3e
    .quad 0xdca704e063d3dc47
    .quad 0x5160b442bc4d23ac
    .quad 0x0f9f265390ed03d3
    .quad 0xadbab13a58f52eb3
    .quad 0x0d86a7d6f312293f
    .quad 0x25ffe50ba59da511
    .quad 0xdf383d9ae18fff71
    .quad 0x1b4491bd03f5332c
    .quad 0x268a2a32f60f159b
    .quad 0xcf76179a261d1fae
    .quad 0x7e97199ef0324593
    .quad 0x2b07ebe06e076e3b
    .quad 0xebd032c4e59ce391
    .quad 0x9e49b81f93fbc07a
    .quad 0x370e9d6a1a378a14
    .quad 0x6b702a224f930ba3
    .quad 0x4fead257cf64755c
    .quad 0x2d8809c8a9a3c7c4
    .quad 0x5fb4c4e061f00b73
    .quad 0x8e52416f8bbf956c
    .quad 0x2ab435a6d47501d6
    .quad 0x5367c220d1f09ef0
    .quad 0x9d5f80d071d8841c
    .quad 0x428c52b0960f655a
    .quad 0x69de9f2da61b5005
    .quad 0xf3910afcfae527e5
    .quad 0x2e3ce23e50f9b40e
    .quad 0x2f13cf1104d152a2
    .quad 0x89d2dbe00cb3af98
    .quad 0x9e6b3565b79c9ce7
    .quad 0x88e0e850e5ae278c
    .quad 0xc95c2f70db1d53b3
    .quad 0xcb5474e9c5c896ab
    .quad 0x91f90e5c7f69d375
    .quad 0x118421b7180d8e00
    .quad 0xab1dad99b697df3f
    .quad 0x4c7b0938f4d2d2c3
    .quad 0x067406937f60c84d
    .quad 0x09a459bfd58acfcc
    .quad 0x96c0c084a54548d7
    .quad 0x1d2564f3f3406984
    .quad 0xf6a59316bcd464dd
    .quad 0x97ed731abe87cb9a
    .quad 0xb48ebe9176f0af22
    .quad 0x71842631291e62b9
    .quad 0x19216621e11c8140
    .quad 0x808239c2496f5d5b
    .quad 0xb7bb86909653accc
    .quad 0x5f7ff326294e19a2
    .quad 0x143ad3acf00b3958
    .quad 0x1796aa5bdd70f408
    .quad 0xd4d44e7e843fb143
    .quad 0x497ce2a9622e1ab6
    .quad 0x575368f08eb167a6
    .quad 0x3a145c850ee2d499
    .quad 0x27510581aad9f978
    .quad 0x5b4adb4942013b82
    .quad 0x44d03ff45659f3ad
    .quad 0x64a36e75e947c4ad
    .quad 0xa6733f9b69d8ab5e
    .quad 0xdab437a28b321740
    .quad 0x8f0193b7e3738180
    .quad 0x23e16fa761349951
    .quad 0x6d71baaa3229890f
    .quad 0x023a8da85033f65d
    .quad 0x92f100315cc7c09d
    .quad 0xc1773a9bf0c27fba
    .quad 0xccb8e4e8a8b949d6
    .quad 0x88fb29b7fec94ef4
    .quad 0x7dd3161875ac59cc
    .quad 0x2b33725f1bbfd7cb
    .quad 0x25240ad8d68c70d7
    .quad 0x46c77a9b6e8d9d58
    .quad 0x47b1cd7d8e45f34f
    .quad 0x31a98ecadf7b298c
    .quad 0xc5f0a6f3d85af9a1
    .quad 0x36b3ad436a209fb3
    .quad 0x6db9faa8d6b9d425
    .quad 0xa514ac324a40e396
    .quad 0x84b75b302a5aedeb
    .quad 0x95a4931fad78d988
    .quad 0xe78fc556d97c4fc1
    .quad 0xf1fd05801317328e
    .quad 0x4515061313c1ef92
    .quad 0x27f519a729a0d498
    .quad 0x80ea45d6b6f898e1
    .quad 0x463830cdb53e805c
    .quad 0x780f8df17f20b868
    .quad 0x9687d703f3241821
    .quad 0xf0a9d83795a7a792
    .quad 0xed56c8bd6de41a70
    .quad 0x12ec4dc48ce46fbd
    .quad 0xe8258e1b12ecbb92
    .quad 0x40bde354ae4e540d
    .quad 0x4b06b1a57cadbcc1
    .quad 0xe9078a21c77d0341
    .quad 0x4781f30310b4d75b
    .quad 0xdca2500ee1f82aa3
    .quad 0xc51776835d73d8f9
    .quad 0xb7c7dffc57d56480
    .quad 0x7ea0e0815eb9efda
    .quad 0x1660707b2132ecf0
    .quad 0xec0f3c3ff63b01d3
    .quad 0x4d1184890e1c2361
    .quad 0xa586923831f2a3b5
    .quad 0x9073e655a11de77e
    .quad 0xb39af5ca651e86d0
    .quad 0xfa0af688c7636c31
    .quad 0xef6aa3cb3bb4ee16
    .quad 0xeb28a88ad186d3ac
    .quad 0x6b1ff98166d995d8
    .quad 0xc4146d35c49de8f5
    .quad 0xf294ce6c2850f046
    .quad 0x533c0e826b743508
    .quad 0x9b8e3ab585282b63
    .quad 0xf458a2d6aafc694a
    .quad 0xa435425a78b2ddff
    .quad 0xb833f54e686aa2d9
    .quad 0xeccff4728e503bf0
    .quad 0xe2261576475a35f2
mem1987:
    .quad 0x6fccf3394d9efcc0
    .quad 0x67b28507c6f6e3a0
    .quad 0x2d7c6a6e02a3a956
    .quad 0x866c5704e0ad1fbe
    .quad 0xa8dbfb460b88abd2
    .quad 0xc40a2d1c8f944f62
    .quad 0x39316c54cc5edda7
    .word 0x0c68f90f
mem1986:
    .quad 0x61253ddc26ceaedb
    .quad 0xcf8073f6af1b98e2
    .quad 0xcdff447e61d9013d
    .quad 0xb53266dd21bfe4b5
    .quad 0x15e0b28b9e753847
    .quad 0x425ee34e1350d730
    .quad 0x05da70793a0e2211
    .quad 0x8d01f51f82ec1d2e
    .quad 0x616ba8e4dd2584f3
    .quad 0x88deb3f40cbadbf8
    .quad 0x155fd74c67d7cc31
    .quad 0x9ce14b2bb6e88e11
    .quad 0xfb7f3cea6aa1f796
    .quad 0x89967e933a217362
    .quad 0xd3c2a1767b9aafb6
    .quad 0x5af157e6ea8fdb67
    .quad 0xcb1e91ac6b65b524
    .quad 0x3ae5b1dbf6904742
    .quad 0x522420dfd7e11526
    .quad 0x4eb5efaa657ca3d8
    .quad 0x021947a37bd2dd88
    .quad 0x160ce10abeee72ed
    .quad 0x1da1cd2f7d3b1be4
    .quad 0x0b02eed3a1c59ff5
    .quad 0x4cdb0a7da86e859f
    .quad 0xd07f1e6d1ca8c728
    .quad 0x898002a557a0db84
    .quad 0x385e48297e0fdceb
    .quad 0xbe3d151f6eda6c4c
    .quad 0x9f6be7d98fb03d1d
    .quad 0x58f7e00985c98b7b
    .quad 0xb3c1b8d2371d1f58
    .quad 0x5166fe6a9265fbae
    .quad 0xd147b8e24f88a874
    .quad 0x5b10a80d77076206
    .quad 0xd1bb4c8867050792
    .quad 0x1f578095fb2906cc
    .quad 0x4ee0e56d22d521ca
    .quad 0xb87b961c97958b62
    .quad 0x2a5c65c208887153
    .quad 0x09cfbffafe9d4814
    .quad 0xee8c3f3a574578f2
    .quad 0x2bf4501a47c53dfc
    .quad 0xb4d862e400f96882
    .quad 0xc96587d3816ba3b2
    .quad 0x095fa7980b1a1a90
    .quad 0x4ab4a81b6854f515
    .quad 0x6474234929586abd
    .quad 0x66dab3729495aa4a
    .quad 0xbfb93f297a64b6d9
    .quad 0x472fe448012b292c
    .quad 0x2cd2c1536d9247d9
    .quad 0x986a317bf4b370da
    .quad 0x3eed322bf115d8b7
    .quad 0xd9bab2eb2b76d4e5
    .quad 0xf1a5595a66b7d528
    .quad 0x16a4d6767b60f680
    .quad 0x124549599eb90825
    .quad 0x591541d2c51e12e4
    .quad 0x5112cc3807bfea21
    .quad 0x01634598c2f99abf
    .quad 0x75335d81d1967157
    .quad 0x45e033cb91c61989
    .quad 0x510dc7b966b17713
    .quad 0x1ddaadd54367130b
    .quad 0xd5d9f9265ad97047
    .quad 0x4fde953bf4fd6a74
    .quad 0xed4db16a5afca8ba
    .quad 0x6a4239725f213a63
    .quad 0x2c39fe9ad012c847
    .quad 0xfaf37c7b126c8ded
    .quad 0x98d3172e01b3cd9e
    .quad 0x8850c9d6cb816c28
    .quad 0xed6263ef463bd6ae
    .quad 0xa2fc6193d220f88b
    .quad 0x88363f653ded9f7a
    .quad 0xdf3e733d7168800a
    .quad 0xe2890e5190037faf
    .quad 0xfa6b8fc6bbbba6cb
    .quad 0x7a7b146927d68e46
    .quad 0xb455abb2bef2dc67
    .quad 0x1db8667b33081af0
    .quad 0xeff603f3233c2b99
    .quad 0xed638dda4e20db0b
    .quad 0xdf3fdbb428d64a13
    .quad 0xb7434728688a1e60
    .quad 0x00b4930c8e414b02
    .quad 0xd6428e6fd42fe619
    .quad 0x9af0ca8107eab16c
    .quad 0xf1a960dfa3247379
    .quad 0x58fc3e0433363be5
    .quad 0xedd3c44670a2a969
    .quad 0xfab2b1532fe913ee
    .quad 0xa9b09a8407d95c99
    .quad 0x554ad8bcd54b207f
    .quad 0xf2ede0445df28d3e
    .quad 0xb60b33608d0e983c
    .quad 0xe27816dbf9c292c1
    .quad 0x50d7dbd180ac7707
    .quad 0x180a122c8d48ca89
    .quad 0xf13ca6ccf1b4dda6
    .quad 0xd25eef751e171e0f
    .quad 0xaf1f5c2ae61bf03e
    .quad 0x6a301f700af5e89d
    .quad 0xfce034e6ef8c1a27
    .quad 0x282e60197807af5b
    .quad 0x789bce3202351e1f
    .quad 0xa0a9a5b9e9f7dc2d
    .quad 0x903188ff7477dc51
    .quad 0x9a75a10e27343807
    .quad 0x3425a62923699118
    .quad 0xadab236341744bb4
    .quad 0x6227c465ccbeca5f
    .quad 0x324500cad7e3f00e
    .quad 0x7822973d2874c18d
    .quad 0x1f6476731bc5901e
    .quad 0x4c96160387a4231a
    .quad 0x884295220815a525
    .quad 0x3d91bb09eee89476
    .quad 0x2af2052bcc69f8ab
    .quad 0x8157b688f5bda589
    .quad 0x4efe38be5e609a72
    .quad 0x533f9450e80e9788
    .quad 0x0ebaf272bbfc4b55
    .quad 0x1f605b05fb522979
    .quad 0xf0759a7e8a4cee64
    .quad 0xc5537b57402478f6
    .quad 0x3acff9a48ce00c31
    .quad 0x11db9dacdc3cdd18
    .quad 0x1708ca12063ea524
    .quad 0xf2534c214f188afa
    .quad 0xe0a5addd26cf0490
    .quad 0x273493d40ab0a692
    .quad 0xe34ada5d310946aa
    .quad 0xe100441262d31a10
    .quad 0xcdf551a5869b3442
    .quad 0x51f2ec209547cff6
    .quad 0x0f2b0f71ef59b631
    .quad 0xabafb920bf023caa
    .quad 0x9951f698f35c8480
    .quad 0x8caa7bc4f99ad95d
    .quad 0x0ca60f9ce0e5ea73
    .quad 0xe7c1a25edf1337af
    .quad 0x0f7eaf75eb80c8f5
    .quad 0xe213685f51f0bb31
    .quad 0x70c10ba442803277
    .quad 0xfa3b053223d18d03
    .quad 0x1297c08332459b9d
    .quad 0x1e109f9c55f65bed
    .quad 0xf270d3397fa3ecfd
    .quad 0x3c6a34a1d9b8ae2e
    .quad 0x41d4c1757a619487
    .quad 0xcb650358e0e8cdd2
    .quad 0x582ec233f036b224
    .quad 0xdc66d88e918eef8c
    .quad 0x5d547753c9648c14
    .quad 0x3227a570e3dfbbcb
    .quad 0xd0a4bba928b2b178
    .quad 0x925a1a8c14cec786
    .quad 0xda89e6914f103f18
    .quad 0x672ee550e9e398c3
    .quad 0xeba3b9eb2b71e7ef
    .quad 0x0f11c9c3660ea4fd
    .quad 0x67ab025109763d9e
    .quad 0x1a7bb5bd6b8062f2
    .quad 0x9b1728f18048685e
    .quad 0x5fcbc4423f458984
    .quad 0xc2087d4224ada6d7
    .quad 0xec871773003bc86e
    .quad 0x565a3aeed58a15a8
    .quad 0xb1aadc6c30f9ffe9
    .quad 0xfa8a0db86f5d55da
    .quad 0xb30ff2d05900d3f4
    .quad 0x96ce18db208b3de8
    .quad 0xe3f7b99ed46a66b3
    .quad 0x1b6effeecb64140b
    .word 0xf3bb2845

.section .data.core_0_el3_root__data_shared_segment_1_1309
.global core_0_el3_root__data_shared_segment_1_1309
core_0_el3_root__data_shared_segment_1_1309:
    .quad 0xf545db52afbf9cdc
    .quad 0x769bdf80d2a6e205
    .quad 0x979571b82bca5c58
    .quad 0xad2e9eda8f7b9b49
    .quad 0x831a95c52f949cae
    .quad 0x44ede87274c07b0a
    .quad 0x2e1bea2ab96dd9dc
    .quad 0x23fc96511612ef97
    .quad 0xd1a5b44ad1c2ae8a
    .quad 0x19824d9dd285c734
    .quad 0x1ea91fe59faeddaa
    .quad 0xa82b2b545897d15e
    .quad 0x91860e80739d41bd
    .quad 0x23fdf0b8d661cc6b
    .quad 0xc4972b039028743b
    .quad 0x188823b4b6dacca8
    .quad 0x94be15a19410ddba
    .quad 0x5485891780f2db92
    .quad 0xeaef93a718c09a88
    .quad 0x38ab391f89f3c901
    .quad 0x0d040836ec48b46f
    .quad 0xeb31c4fc5eea3d58
    .quad 0xb5593b0be007000b
    .quad 0xfcac522f442ed40d
    .quad 0x8b6d8013140854d4
    .quad 0x2fe31a055967ea05
    .quad 0xf6b4a669dd06327e
    .quad 0x246665c66e4ca501
    .quad 0xa1499baef6960b16
    .quad 0x09c3c5609b88eed4
    .quad 0xcfcdb3d16001ce74
    .quad 0xe7c57bad99b182b2
    .quad 0x0603d27a5fad05ca
    .quad 0x11eafa5690691041
    .quad 0x78ff8241d2228607
    .quad 0x38091bedf8c5857f
    .quad 0xec9b84cae8422c95
    .quad 0x90fe1201443816aa
    .quad 0x0024dbcbd9ca3b9a
    .quad 0x4dc95d15ffe7fea5
    .quad 0x95d07cfc52f9988e
    .quad 0xbab9f11a14891fe8
    .quad 0x0ce3ec917d36d514
    .quad 0x5d28316c88d40558
    .quad 0x8cbad96f1a412236
mem1999:
    .quad 0x7979978ec23abb62
    .quad 0xeb27feabeb6f6878
    .quad 0x70393b9be61f42e2
    .quad 0x32724ff3cd4e1ca2
    .quad 0x2702a9da536c0f1e
    .quad 0x7c27e6a461d02f26
    .quad 0x642d402d81f936be
    .quad 0xf3bf75629e59c6b4
    .quad 0x2fae968354ff7fca
    .quad 0xb929f5e1dafa5019
    .quad 0xa37d9134cbb68717
    .quad 0x9573c597a5599633
    .quad 0xad6739d97318ce05
    .quad 0xe67d0cc503259d53
    .quad 0x7c8ac91c4bdd77cb
    .quad 0xc609dcc2acd46029
    .quad 0x988269e9fb4ebce0
    .quad 0x3a816125b2ef7781
    .quad 0xa0b6b0286593a0ab
    .quad 0x22fa8d30116a7d3a
    .quad 0x1690784c35c91ce7
    .quad 0xcc06ede74f5d0de5
    .quad 0x42a95278be7a8bd7
    .quad 0xe957d7955687f477
    .quad 0x3a0bf522f3860e25
    .quad 0x4a7834453d830c27
    .quad 0x7bc96633291e0eed
    .quad 0xce17d2bcdab18098
    .quad 0xef817fa25d7e84f1
    .quad 0x078d8ddb9b58a0dc
    .quad 0x88e548fc72beffc7
    .quad 0x976ae5e98d221907
    .quad 0x86a0d312fd6b4073
    .quad 0x9a21fa62cb465a27
    .quad 0xa5857a0941ce733e
    .quad 0xdbc2a221170b5987
    .quad 0x509eaf583c130a39
    .quad 0x3f5e0b51fe7dc58e
    .quad 0xbb232fa1abca1ce3
    .quad 0x3a920eddbdeff758
    .quad 0xa092e3761a7fa112
    .quad 0xf64a0a8f038d5723
    .quad 0xb637dc22a24270af
    .quad 0x1b5529ebbd7cafeb
    .quad 0x4ceacb4393275202
    .quad 0xf6c3c99ac038b90e
    .quad 0x15a39e8e3553e36a
    .quad 0xde19bdb11e3328f9
    .quad 0xc1bdee75a89b11a1
    .quad 0x6d2b5f82b264a016
    .quad 0xf2c4c2a7eee125f5
    .quad 0x73852667a5f4c313
    .quad 0xe32a0e4ae4186c6b
    .quad 0x6e9ef6e8a71dbffa
    .quad 0xaa7b86d723092667
    .quad 0xcf1e947db9a4ac64
    .quad 0xefcb55086c7da1d1
    .quad 0x5d20a72d0c1d611b
    .quad 0x80e0155c54ae4139
    .quad 0x8dfbcccba11de829
    .quad 0xd84fd0501143a98a
    .quad 0x0bd00d64149cb14a
    .quad 0x08fec84ed8297aab
    .quad 0xac71c764bd9496e7
    .quad 0xc977b58ff449af04
    .quad 0x9c191d0c92c48cbf
    .quad 0x48c0036660e2c93f
    .quad 0x78f53615d61c9658
    .quad 0x32a18cab4b530482
    .quad 0x45855244e81b88ba
    .quad 0xb26e09e4c3a54795
    .quad 0x1b31e5d30b788a70
    .quad 0x4d2e491c7044e12b
    .quad 0xf945ccc96eece778
    .quad 0x35ceda439a7a7dfe
    .quad 0xd006251c6b2a4316
    .quad 0x9479668e3a821d00
    .quad 0xe11061121750a0c7
    .quad 0x01092fbeab6f080c
    .quad 0x71f206f1099cf5af
    .quad 0xaedd2e82423b13d8
    .quad 0x013bda6cc04892a0
    .quad 0x97979587d5970aa9
    .quad 0x69a19f6275eccb02
    .quad 0x824c92b413609fc9
    .quad 0xdec1a51ac4fcd3c7
    .quad 0xb9e45d5aa8ef4d5c
    .quad 0xe199145ea3aeb536
    .quad 0xaf58bc4bc9e10b0c
    .quad 0xedba23289a3281b7
    .quad 0x6f712a6201e698db
    .quad 0x8c18af27a149a320
    .quad 0xf6f0832116c62c97
    .quad 0x15613d74c5d72289
    .quad 0xd2ad29f1c05e5f88
    .quad 0x3b4c6a8b59ea785b
    .quad 0x55d3502fbb5c25cf
    .quad 0x543263ba0be2508a
    .quad 0xbb679cfba73e3d7b
    .quad 0x922726afe6d273f9
    .quad 0xdc2b555af38bb1a8
    .quad 0x3756e5c3a2b7b8b0
    .quad 0x853b1973f42dab93
    .quad 0x84bdc8173bec4ca2
    .quad 0xf23f5848ed6ffd1a
    .quad 0x4bb6e590e3fd4c08
    .quad 0x25a0386932905a2d
    .quad 0x7736ad1833792e88
    .quad 0xcf000da2ec105a51
    .quad 0xba55da9de8943dc8
    .quad 0xabdbcbe291e8434a
    .quad 0x8f6ca0815ca2c0e8
    .quad 0x3beb1ef6cf6e6da2
    .quad 0x8cdc9ec4040d7e36
    .quad 0x12ebe75a7928e240
    .quad 0x1e9f69c25c1f6822
    .quad 0xd687c8386be03ecd
    .quad 0xef0703fc02144d1e
    .quad 0x5020e88a8300d623
    .quad 0x77f9dbdace1599e9
    .quad 0x074bebcabfe53d0b
    .quad 0xbc0252ccf1a4ea47
    .quad 0x96ced0cb2fda8be0
    .quad 0x8998d3feec6d8af6
    .quad 0x6022eb69d8685113
    .quad 0xbbafbf05d91094de
    .quad 0x15d7d5f27914c984
    .quad 0x680e4bbc6489a0fd
    .quad 0xaf6c3d94c47f1a52
    .quad 0x916721fa8fa6c921
    .quad 0x8d474c47c62bc9cc
    .quad 0xf08b22e4a4dbf568
    .quad 0xba57be3468e0ebed
    .quad 0x45036a34d2628ad2
    .quad 0x9001a25c0af7c0fa
    .quad 0x89f314ef9c753277
    .quad 0x4208d6e03ef6c6ff
    .quad 0xad2cd5e150f871d2
    .quad 0xa73f9c619cedb248
mem2002:
    .quad 0xb7a9795909acf04a
    .quad 0x4232f24493ec0dc5
    .quad 0xdaafa18702b832ef
    .quad 0xb551697be60bee49
    .quad 0x4cffa8c5b2b9f9b0
    .quad 0x68926b4afe46c83d
    .quad 0x49097d9efc6094c4
    .quad 0xbe86296cdc29eeb3
    .quad 0xa1abeead8f06e9d2
    .quad 0xa7d3f2b8c72a7284
    .quad 0x865863de2b88f73c
    .quad 0x91900c08a7feb094
    .quad 0xe604a8a66ece0749
    .quad 0x5fb8261f5e0bf0c6
    .quad 0x4c4771231913b358
    .quad 0xdbedc1e9f401797d
    .quad 0xc71b4ef71d6969c0
    .quad 0x3eceaadb861006a3
    .quad 0x2bf69281dd0676d1
    .quad 0x796fe3fb2043203d
    .quad 0xc178185d1b6c892f
    .quad 0x3db70469811a6ea7
    .quad 0xff0e7d3b8d2b41e4
    .quad 0x85290ff0c1c73eec
    .quad 0xa8d1555a1e550232
    .quad 0xa1a24ae9237d0c9e
    .quad 0x6a2e674b619944d0
    .quad 0xcc687c36da00844a
    .quad 0x6760be39ee0b4c17
    .quad 0xc207eb446a38f35b
    .quad 0x1b1935b122b44651
    .quad 0xa37abbac68bfe508
    .quad 0xff472f32a33218e4
    .quad 0xf5963696be45ca0b
    .quad 0x26f6b1c62fdb4d15
    .quad 0xf2ca39b5e637cf2f
    .quad 0x1762d78e2ce80741
    .quad 0xb7168218de6d0736
    .quad 0xa2d266aabf5df192
    .quad 0x3b1ab71d679789c0
    .quad 0xf53b43ef290f9298
    .quad 0x3673ea03c3ea9e2b
    .quad 0xb97fce8fce2e84f4
    .quad 0xa9818ce1a88c7e03
    .quad 0x4a65aa4cda3c8d3b
    .quad 0x11501201bd22dc23
    .quad 0x4f04ef50311a4b8a
    .quad 0x981f8d3caf0c2e8a
    .quad 0x0aa607689773dfa3
    .quad 0xbb64b83a82052d9c
    .quad 0xeaeb2305ee10eb4e
    .quad 0xf429799e6e231638
    .quad 0xc6f1163cd28479a4
    .quad 0x92fd4a9b740e1a9d
    .quad 0x5d12ea6556659404
    .quad 0x20aa2370da683b21
    .quad 0x61a40003e788e734
    .quad 0x7cb187a48130242c
    .quad 0xdc0cff60b607733b
    .quad 0x71dcf6eb301a2176
    .quad 0x059b8f824b955cf2
    .quad 0xdf4337222604d45e
    .quad 0x881a4e74f0b2d97e
    .quad 0xf37f343799346cce
    .quad 0x67f76dcad91c8162
    .quad 0xf5ad30186ec9d839
    .quad 0xd19712125f2bd063
    .quad 0x6d28b0971a228052
    .quad 0xda017cc248df36bc
    .quad 0x03f2b36fb4c23dbc
    .quad 0xb06689edd3891fa9
    .quad 0x66394cf9c17e4e50
    .quad 0x311bbf0d4f785d81
    .quad 0xc77f04252caf8a00
    .quad 0x08d909ad9d46b9af
    .quad 0x321cb29312662545
    .quad 0x3ba423010c42dc56
    .quad 0x91bf1c635acc3c98
    .quad 0xce8edc79a6472573
    .quad 0x33057eeb3cb34ca4
    .quad 0x2b18b2b721d9ac73
    .quad 0x7001ad9c609211e3
    .quad 0x2256bb491415e131
    .quad 0x58f087e3a89c12a0
    .quad 0x863ffd89c34c0686
    .quad 0xed88cefd17013f8f
    .quad 0x924e782b9d27f4b6
    .quad 0xa551efef46999abf
    .quad 0x04f3a3ea7282fa4f
    .quad 0x946d8495d7e2ff42
    .quad 0xba5a9b24659b4fef
    .quad 0x1bba3dfb9afd0e8d
    .quad 0xbd58ff09da0bb31d
    .quad 0x697de0b5a809bbcc
    .quad 0xf043f9a09ff9ebba
    .quad 0x1ee13d3a4cfd3bc6
    .quad 0x62587e1d4e35eb7b
    .quad 0x88bf7d0635505fba
    .quad 0x45900d7dd7647e54
    .quad 0xc7bbb457ccd6ea64
    .quad 0x5e57323d9a8dab72
    .quad 0xc3eeba3cd37b84d4
    .quad 0x1913b36274a74be8
    .quad 0xfd93357022d08416
    .quad 0xa01e82efa07eee01
    .quad 0xa880792012865212
    .quad 0x332d1b53a6855064
    .quad 0x39e911fde48dec40
    .quad 0x9299752d84a6f8b9
    .quad 0x0ecba3bf37fcddb2
    .quad 0xdf8e1bef7d63100c
    .quad 0x0115819e92d7bb03
    .quad 0x3fb6c2cc39ea32f8
    .quad 0x53f7c13bb8021d18
    .quad 0xc803261332951fb8
    .quad 0xe94b4bd577e3be42
    .quad 0xfa144a718e2a3481
    .quad 0xc52c008a997d12ba
    .quad 0xdee7f011f2865005
    .quad 0x773a9b1701c1d13a
    .quad 0x20db3946885244cf
    .quad 0xbcb69421464fce61
    .quad 0x0c90066f5eb4cc07
    .quad 0x82edf621d155c6e2
    .quad 0x402b725692d6a850
    .quad 0xce3200cfeb66d3eb
    .quad 0x60b2adb1126b8426
    .quad 0xdc70d057eb05ea29
    .quad 0xbad2c129035dd0fe
    .quad 0xabd4e48707cf4641
    .quad 0x1104484c5d020689
    .quad 0x079701fb19c1f0e9
    .quad 0x0247a4d34cbdacc3
    .quad 0x3e10651af9108f0d
    .quad 0x89e25b0731099f1e
    .quad 0x71792718f765ca1d
    .quad 0x32451067cadd47e1
    .quad 0xd1a3bfd4b9e79fca
    .quad 0xd356fc766aeec183
    .quad 0xd0fcd586d950dffe
    .quad 0x14fb7b0273181529
    .quad 0xf5ce798bf3da2897
    .quad 0xccd775cc47e673f3
    .quad 0x957d1c0f655f91e5
    .quad 0xf94056ae40c8fe64
    .quad 0x856b3f9bcdc4c6c8
    .quad 0xb2d0cccb72c2005c
    .quad 0x9e392054dcb61d54
    .quad 0x03c3fbd6af51acd5
    .quad 0x524b123203914b7a
    .quad 0xd22d4121310935da
    .quad 0x1198cfbc51d48bb6
    .quad 0x59adcb088daeaea6
    .quad 0xf6f7a07be2a07f6e
    .quad 0x9274a72ecece9e61
    .quad 0xeefde9375eae7984
    .quad 0xb7a4408e6c536c30
    .quad 0xfa83060ec7780722
    .quad 0xcba7fe419d9b74fb
    .quad 0xc26f0c819b7dbaf1
    .quad 0x7debffcdd64692fc
    .quad 0x5d9a0d98b8559bd5
    .quad 0x945559d3095a62a0
    .quad 0xda935b2495e5497b
    .quad 0x9d0c5775c483a93b
    .quad 0x2fed631a625f68e1
    .quad 0x283beaff412a6762
    .quad 0xea7467fcc5acf4b4
    .quad 0x54aa79e9517bee15
    .quad 0x59260019ffb8b1ed
    .quad 0x110b6ac4b4cf9732
    .quad 0xae61661260c49c32
    .quad 0x77c22391d0e92cf4
    .quad 0x52c682e00111eb80
    .quad 0xfac744bfe3f922a9
    .quad 0xdb92e76f5852f428
    .quad 0x425c0ca7acf42bf8
    .quad 0x5923cea17d87c412
    .quad 0xa57cb84bec5f40e0
    .quad 0xf897e018aec1ba5c
    .quad 0xa94a3f44af5e2401
    .quad 0x630d726b1d27def0
    .quad 0x4769626933212fa9
    .quad 0xf0d687f9414dae90
    .quad 0x0937b88d879f03c7
    .quad 0x3da4f840dea0dc32
    .quad 0x8e3746ef39094dea
    .quad 0xb13f752105caad84
    .quad 0xdd2d259142bf75d0
    .quad 0x0770cfa2ac5de6d2
    .quad 0x18fcf842b5d80869
    .quad 0x7c87e378e6f451d7
    .quad 0xd0e9f45902f3f494
    .quad 0xa48de519f1b5745a
    .quad 0xa48e222a037c4e43
    .quad 0x756c0fe4a2a1f6f2
    .quad 0x59cc9475f8c00d2c
    .quad 0x1b573edb2568bac1
    .quad 0x77f01b0d0b9deeec
    .quad 0x9d063cc7d6b8ff0b
    .quad 0x0082df459e4065bd
    .quad 0xbbe234c6b5a6df92
    .quad 0x4cdd66bba148151f
    .quad 0xc7f6e908c995fb1e
    .quad 0x38d63e6fb13e86e1
    .quad 0x1569003a3dfa3988
    .quad 0x883120106a6ce275
    .quad 0x157ca292400b78f9
    .quad 0x43c7802e514edc37
    .quad 0x377cea694699371d
    .quad 0x0eb693dc8fa09fb4
    .quad 0x2a2470c961f0bd7e
    .quad 0x66e69b19bc1380a0
    .quad 0xc7fdd7324c044545
    .quad 0xd3f24d2123a4bf95
    .quad 0x0a003610ba74942e
    .quad 0x20eacc18599b1cbc
    .quad 0x4122bcfcecd78c21
    .quad 0xf0742917656c4cb2
    .quad 0xbb2c6846767aa7d1
    .quad 0x64978a3990e126a9
    .quad 0xf886fac51c4fa790
    .quad 0xc87df705dee78bf5
    .quad 0x5e06847ccd350f20
    .quad 0xec01e0fe948e61b0
    .quad 0x75c183deb1d7a03d
    .quad 0x1efc7463c8d815d9
    .quad 0x886720fb46bb5147
    .quad 0x080f726d6e4980b0
    .quad 0xf068288cccf02f65
    .quad 0x36f615be84bfdc6f
    .quad 0x478383d8cc28fe11
    .quad 0xa321fa23b621bb29
    .quad 0xb8ee87b699ea4996
    .quad 0xa94644805965d714
    .quad 0x5009b241e6fd989b
    .quad 0x8304ac7bd4337b29
    .quad 0x0dcc35fd44db4ccf
    .quad 0x0426a7cf9fcd05c0
    .quad 0x3fe1987837a0383b
    .quad 0x0a60d10a3505156b
    .quad 0x7d23367599a26588
    .quad 0x26d48eeb5cc4608a
    .quad 0x7440719a24c7b0d1
    .quad 0x0d34b6c35c953903
    .quad 0xf07e1f1c2b728ef7
    .quad 0x2de2054a0c4572b3
    .quad 0x1db8579ea267b6af
    .quad 0x50f74f2348c17048
    .quad 0xc73243e54be62188
    .quad 0x9a9b83cc241acb40
    .quad 0xe1a2914e1197480c
    .quad 0x81d05a007863668e
    .quad 0xca71ce9b36213a37
    .quad 0xb2094d51ae198b02
    .quad 0x97fa219ddb379159
    .quad 0x95809daa2701503e
    .quad 0xff3f0fbaa8bf2dcb
    .quad 0x31507ae3e12c4701
    .quad 0x0935faaa8e0fd978
    .quad 0x7b2639a402c54120
    .quad 0x823d3c704d00ad20
    .quad 0x38455c1d9a943bef
    .quad 0x65647ed86b3cf7a1
    .quad 0x7cda5701459085e9
    .quad 0x1e81f42966543067
    .quad 0x8712942f0e1a1313
    .quad 0x92363f0e5c766cf8
    .quad 0x2bf254f60fa1afd8
    .quad 0xd080bf469841109e
    .quad 0x441ae7a11ecd5ced
    .quad 0x07165542ee8ff4e5
    .quad 0xc4484c411239de4c
    .quad 0x2f04a6dae90cdb48
    .quad 0x8a2a47db828bf2f8
    .quad 0xe83cf9433d9ef55e
    .quad 0x7dea5b98686952e0
    .quad 0x4e0fdc1b074e58c8
    .quad 0xaf858d5083d4cb56
    .quad 0x37c7a2ba6b3586db
    .quad 0x3bb2e86f7e0fc202
    .quad 0xdf56e3dc0ee9eed2
    .quad 0x9e21df546d146b2b
    .quad 0xa5c90db450346b5f
    .quad 0x9f69161c68db3390
    .quad 0x304705535ade2300
    .quad 0xaab24879e6737eae
    .quad 0xff736335c58ea6b9
    .quad 0x8c3137e66dcfc077
    .quad 0x9e9a06a4694e39ef
    .quad 0x34146818d31204ca
    .quad 0x34c1cce1123869c3
    .quad 0x983380e65b92f7b9
    .quad 0xf2474d933bdcc0a3
    .quad 0xec946bc0f04d36f7
    .quad 0x6481ba0e011e83aa
    .quad 0xe42eebc15d0e2331
    .quad 0x0884fda06b1e1f6f
    .quad 0xb59d64979a1b3ab5
    .quad 0xbad2daf58366633f
    .quad 0xd56dce0ce47c4e2c
    .quad 0x5aad23e60ad9a043
    .quad 0xb2681f2b95c79a8b
    .quad 0xd2f1c7edb9f63cab
    .quad 0xd1dd86dca44202b7
    .quad 0x7d1ef5814b73aa24
    .quad 0x4c8ac61afef2a272
    .quad 0x029a605af6380726
    .quad 0xd329971caaab3794
    .quad 0x96d2d8097a2d8364
    .quad 0xf06994903446802c
    .quad 0x3bbe968cbcb5a512
    .quad 0xa8bbd90fed48aadd
    .quad 0x3123a76c6e32d75e
    .quad 0xfd6497322155e6f7
    .quad 0x185c1d0c816f41de
    .quad 0x9b001f4d07528485
    .quad 0x2c0115d8c9bf7c76
mem1998:
    .quad 0x25ec61ab54ebcfcc
    .quad 0x428eb59475456620
    .quad 0x55d30fe35c4aefc4
    .quad 0xaa1d7e8942d26624
    .quad 0x33b52da6944c8a1c
    .quad 0xa7aa46f65440014e
    .quad 0x06610e2a3faa58de
    .quad 0x7aeaf30d54edd34d
    .quad 0x2117d8d09602d2a5
    .quad 0xbb1966fb26dca97f

.section .data.cross_core_data_segment_1297
.global cross_core_data_segment_1297
cross_core_data_segment_1297:
.org 0x4e8
.align 3
label_4901_end_boot_barrier_barrier_vector_mem1985:
    .word 0x00000003  // 4 bytes

.org 0x780
.align 3
label_4922_end_test_barrier_barrier_vector_mem2017:
    .word 0x00000003  // 4 bytes



.section .data.core_0_el3_root__data_preserve_segment_0_1310
.global core_0_el3_root__data_preserve_segment_0_1310
core_0_el3_root__data_preserve_segment_0_1310:
.org 0x440
.align 2
mem1989:
    .word 0x00000456  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0x4a0
.align 2
mem2006:
    .word 0x00000000  // 4 bytes
    .word 0x00000020  // 4 bytes

.org 0x4d0
.align 2
mem2004:
    .word 0x00001234  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0x830
.align 2
core_0_el3_root__exception_callback_LOWER_A64_SYNC_mem1978:
    .word 0x00000000  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0xf50
.align 2
core_0_el3_root__exception_callback_LOWER_A64_SYNC_mem1977:
    .word 0x00000000  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0xf58
.align 2
mem2003:
    .word 0x00000456  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0xf6c
.align 1
mem1991:
    .word 0x00005678  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0xf74
.align 1
mem2005:
    .word 0x00005678  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0xf80
.align 4
test_end_str_block_mem2193:
    .word 0x54202a2a  // 4 bytes
    .word 0x20545345  // 4 bytes
    .word 0x4c494146  // 4 bytes
    .word 0x2a204445  // 4 bytes
    .byte 0xa2a  // 1 byte



.section .data.core_0_el3_root__data_preserve_segment_1_1311
.global core_0_el3_root__data_preserve_segment_1_1311
core_0_el3_root__data_preserve_segment_1_1311:
.org 0xac9
.align 0
mem1990:
    .word 0x00001234  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0xd30
.align 4
test_end_str_block_mem2230:
    .word 0x54202a2a  // 4 bytes
    .word 0x20545345  // 4 bytes
    .word 0x53534150  // 4 bytes
    .word 0x4f204445  // 4 bytes
    .word 0x2a2a204b  // 4 bytes
    .byte 0x0a  // 1 byte

.org 0xe1a
.align 1
mem1992:
    .word 0x00000020  // 4 bytes
    .word 0x00000000  // 4 bytes


// No uninitialized data on core_0_el3_root__stack_segment_1312 data segment. skipping .data section


.section .data.core_0_el1_ns__data_shared_segment_0_1319
.global core_0_el1_ns__data_shared_segment_0_1319
core_0_el1_ns__data_shared_segment_0_1319:
    .quad 0xbb3afdf85f6202b9
    .quad 0x8b6106575f885550
    .quad 0xa64ba5b44b77d372
    .quad 0x2879bac69222739d
    .quad 0x03caec60c91a2c01
    .quad 0x2bc0d5f24ac8d676
    .quad 0xc1f8c450acde1291
    .quad 0x64329b386fe284c1
    .quad 0x3ccb1431f10f8bd3
    .quad 0xa538471cbc04f045
    .quad 0x17097833c389884d
    .quad 0x0b6c31d086b1ea5b
    .quad 0x462e9b3bbc937cea
    .quad 0xc9529d0d004756e3
    .quad 0x45f6b980e4beab29
    .quad 0x563cc27693e64f33
    .quad 0x76a77c172d878d00
    .quad 0x3fe916c00ffa16ae
    .quad 0x99a5e1ed46dfaf15
    .quad 0x749c8a127e2d323d
    .quad 0x6b16ca4d778be115
    .quad 0x030c28525a492ea1
    .quad 0x39f665292ba758d4
    .quad 0x19b161d43136e3ec
    .quad 0xef4da1717cdd6b32
    .quad 0x4e8841d42f7b59c9
    .quad 0x2cde092f2bdb186b
    .quad 0xa1ba82212f63bc79
    .quad 0x16d94f9b9865186b
    .quad 0x6ce2de91f10862f4
    .quad 0xe84b71bcfcb63c94
    .quad 0xf9a96c2d6220c384
    .quad 0x94ced8d2f2b59c9f
    .quad 0x4b3e56a93fb418c6
    .quad 0x64041edaef58dfc5
    .quad 0x131381d7dc6155b5
    .quad 0xe217a678950971b3
    .quad 0x6909e6297a7718d4
    .quad 0x5205c39493a343a5
    .quad 0x324a812f475f8d76
    .quad 0xc0b6f53293821830
    .quad 0xb35d46f7fba6fa3d
    .quad 0x7996b7e12e3ccf27
    .quad 0x25ecee37ec9f13ea
    .quad 0xce6cc0d047d7fa12
    .quad 0xadf3ee7a1dd06ffb
    .quad 0x03d019a8112f20b6
    .quad 0x5df5e42228137522
    .quad 0xe1031c49cb6962de
    .quad 0x5a81ea79b9ed9748
    .quad 0xf6aa32648e0288c3
    .quad 0xfa64308c0174c6ec
    .quad 0x88f44bda8928a690
    .quad 0x2bf396953f5717cf
    .quad 0x7622b4a110134d9c
    .quad 0x8e0c45332028e07c
    .quad 0x529652ad24e2a9d7
    .quad 0x2469f5a7312fca69
    .quad 0xdf61d0f99f1b8ef3
    .quad 0x17644342fa1f9d8e
    .quad 0x3c73b11a09a587fb
    .quad 0x185275a96fca4d62
    .quad 0x8f21e51ada88d30a
    .quad 0xadcaf503124f9e95
    .quad 0xe961f083d86fcf2e
    .quad 0x7030e0fb51d214fd
    .quad 0x6c6aeb555f6896da
    .quad 0xd8e9ac91bc400034
    .quad 0xbaadf23115c57a7e
    .quad 0x4263f32cb9a3b8b1
    .quad 0xc686b4be38197bc4
    .quad 0x45af78a44cce7ef3
    .quad 0xf6b5c53647d47e2f
    .quad 0x85b4592314167563
    .quad 0x840d137625d5e0cf
    .quad 0xa5db7729a0cca3e1
    .quad 0xac9d839d3a09e94a
    .quad 0xe529371fe1a79531
    .quad 0xed0d93fda086405f
    .quad 0xc25995444233a8c0
    .quad 0xba807dc528ff120c
    .quad 0xb78b87b2ac768192
    .quad 0xe46019981920e8d3
    .quad 0xda1205a6be892165
    .quad 0xc8a8caaa496c5203
    .quad 0x7e748ba0c2a4f54d
    .quad 0xf20f79c752c0d2b5
    .quad 0x964e44dc4f5bdee1
    .quad 0x1da451f7016a287b
    .quad 0x718cb5d53203ef7a
    .quad 0xa24b2f2d3a26034c
    .quad 0xf588eb630c2a74cf
    .quad 0xea60f4acfa8df10f
    .quad 0x4cf01521871ed87d
    .quad 0x76a98dde99c3fa4a
    .quad 0x377d1c051e707d45
    .quad 0xb750eddc564da18d
    .quad 0x3d14ba88119c4d5e
    .quad 0xdcbb59be881b5cd8
    .quad 0xe9d98917afa72ea1
    .quad 0x62f05274f4b026ce
    .quad 0x52690de40e1d1df6
    .quad 0xdf7cb068bd8a807d
    .quad 0x1f6e3ec4846c80d1
    .quad 0x2742e783efb4e0f2
    .quad 0xc22de7a80594feca
    .quad 0x96c966de73783a49
    .quad 0x6ae8e92d059025e4
    .quad 0x624a0bd846822dcc
    .quad 0x7b826fcea7571444
    .quad 0x1356d79d18202148
    .quad 0x7198e30ff0c7e036
    .quad 0x15ba2df33ba830ad
    .quad 0xb1c6ed4e45aa7ed8
    .quad 0xccdf91264bec3503
    .quad 0xddf8b84dd630a683
    .quad 0x3e1c42fe81c88693
    .quad 0x4e2ad84a370b4813
    .quad 0x72abf570f71677a5
    .quad 0xd4948844505301c4
    .quad 0xedc5e880821b9074
    .quad 0xea99798a6b9d5887
    .quad 0xb3e9ca3464b28b1a
    .quad 0xa92101145c397d43
    .quad 0xac1e8c67058cd270
    .quad 0x2af596a4138eaacc
    .quad 0x2607373def970624
    .quad 0xdd411de707357f23
    .quad 0xcbaa98fccf86bc0a
    .quad 0x9a86e83f10ac26ee
    .quad 0xdfb455b90064b1cd
    .quad 0x47d8c3229f5e83c8
    .quad 0xd86bf76e0087ddfa
    .quad 0x57877124fa2b37f4
    .quad 0x5dc23d6d0f9421c4
    .quad 0x57cb85e65b08a526
    .quad 0x1445035be3a68a0f
    .quad 0xdbb6ceb516de1dbb
    .quad 0xee0c38a088f8ab54
    .quad 0x01ecfe2968d467b9
    .quad 0x8f5ac1778b16d97e
    .quad 0x1f1907b60c9a754c
    .quad 0x6db9ef66e3dd2ee0
    .quad 0xd21efd09c31cd442
    .quad 0x9d624a0e65b7fd21
    .quad 0x6de2eaf0dc520bb6
    .quad 0xfd9acb5f3a145083
    .quad 0xdba2d89140e323df
    .quad 0x659eaf8b7e970432
    .quad 0xa948c8573dc705a4
    .quad 0xe4f2ec75c6732664
    .quad 0x2daf5dac3d8258fa
    .quad 0x033a25d7f971a338
    .quad 0xae854946c8ca0768
    .quad 0x269102f9761c6aac
    .quad 0x0e52d6a781b79bcd
    .quad 0xcd2cd22e0bb1a0fd
    .quad 0x1c0ba41a4bc91b89
    .quad 0xea50457ab1492348
    .quad 0xac613f2692fc8af2
    .quad 0x337e2d9566216ef8
    .quad 0xfeb8efe9a90eab81
    .quad 0xeccbd479cda45db4
    .quad 0x66d7f0cf4a4628e9
    .quad 0x132f432bc7cb663d
    .quad 0xb3d669d391d45201
    .quad 0xcfeff10152b7d72e
    .quad 0x8f0f9951edf288d5
    .quad 0xff89e9d6293e2936
    .quad 0xaf0651ebdeb9ac6c
    .quad 0x434755c274622f09
    .quad 0xb55d99eeeb64c673
    .quad 0x0ffe6b4bac09ca77
    .quad 0x342888d25c90e8bf
    .quad 0xd8d9e6831681f408
    .quad 0x119ae875625e184f
    .quad 0xa48d0da84eb9f463
    .quad 0x7665494b54ee8786
    .quad 0x1558333d20696005
    .quad 0x5fbfe71c8e776cdb
    .quad 0x70e8246e07b48375
    .quad 0xdef4dab8fd1f9e98
    .quad 0xd4c4cc2672612bf4
    .quad 0x49ea0f74cd82465d
    .quad 0x4e7cc7f860005170
    .quad 0xf178f1ef1f625153
    .quad 0xb5a275378c66cff6
    .quad 0xf942082b3d3a1a17
    .quad 0xb9af4425c0510de4
    .quad 0xeebda65eb785c039
    .quad 0xa2cf302070bb6bf4
    .quad 0xa24ad597e128e599
    .quad 0xa9a8b67f9e98478b
    .quad 0xb0947999d931b8aa
    .quad 0x26d13b40f0a896b9
    .quad 0x87173a4987f68fa4
    .quad 0xf28b120fea2bc165
    .quad 0x63a0f6c44ab7a8f0
    .quad 0x4776c83e540be7f1
    .quad 0x658f6b9736c45b3e
    .quad 0x884be54d49e5155e
    .quad 0x0030498e877d57f8
    .quad 0x70f34d0aed904ac6
    .quad 0x0f5873cfba9ef00f
    .quad 0x97b746fd94c9f4d0
    .quad 0x269b161bbfa23757
    .quad 0xc0819d32461bb7b3
    .quad 0x68fd584d88797260
    .quad 0xf6035506d314718e
    .quad 0x45a09d216ffd741b
    .quad 0xcd81f460a149f06b
    .quad 0xec9597c9209d5dbb
    .quad 0x1d7a1c32aa1c0d35
    .quad 0xe378544542c6c3bc
    .quad 0x8e6fb0389584982c
    .quad 0xd1255b619dd1469a
    .quad 0xc4df756fdb3d139d
    .quad 0x8addef2a016bb11a
    .quad 0xc791f52fef15d082
    .quad 0xd97af1417c6c3351
    .quad 0x3fc0e003c404c396
    .quad 0x264ecb1c053d1738
    .quad 0xc86df0fc94844d52
    .quad 0x93f8437119419fe3
    .quad 0x5d440f328254b485
    .quad 0xe1520c601cab5031
    .quad 0x177a02eec8c10943
    .quad 0xe0e3b2549449e56d
    .quad 0xe1e260b50c833e6f
    .quad 0x6cf7ac53ec38ecfd
    .quad 0xcc88ab84a81f3c74
    .quad 0x1d585d768a054633
    .quad 0x9b23cbea914cf754
    .quad 0x30c2c501f3607038
    .quad 0x2cb7f475b2550090
    .quad 0x64c5e995cafc7e7a
    .quad 0xf37df1cbad9b3b78
    .quad 0x78167b085f845ea4
    .quad 0xcc622f45ef19fcd7
    .quad 0x9122ed6d66d0538c
    .quad 0xa3d7d96d79fef811
    .quad 0x98e04854e9f511d9
    .quad 0xc37951831f613cae
    .quad 0x77f2c627270876c0
    .quad 0xd8c74d8845511311
    .quad 0x6996bfd399fdfd33
    .quad 0xa69de06f87b3ed41
    .quad 0x5324278a4a905224
    .quad 0x0c8e7dc5803c0ba0
    .quad 0xe8e674786f2b11fa
    .quad 0x8649365cfefb63f7
    .quad 0x0e77b18fbc4d78e6
    .quad 0x634efc23ea204017
    .quad 0x8c5633112b34ebf8
    .quad 0xa345175d043696ee
    .quad 0x1665fa49c0e6a4f0
    .quad 0xd56c51693880bf9e
    .quad 0x46b368e0e8ce830f
    .quad 0x9bec748f317bea89
    .quad 0x5163e66cd861dfd1
    .quad 0xccae2574c4e5edd4
    .quad 0x10d01aab9026e0eb
    .quad 0xb47271415124ac58
    .quad 0x1f34c7721dcff73c
    .quad 0x192c4911f801f951
    .quad 0x3c3ee7acace6288e
    .quad 0x163dff799da5c9ed
    .quad 0xec0dcb2ec31a5374
    .quad 0xa33fb9d4762ce4e9
    .quad 0xc48bfbdbd4978e48
    .quad 0x749e7d8905e2556b
    .quad 0x1729e19e2f517c99
    .quad 0x6f32f56ea09145f9
    .quad 0xb9a7755146937fe9
    .quad 0x3bf1b376d6dae8cd
    .quad 0x0032674fde78506a
    .quad 0x495b4ae4260d5dba
    .quad 0xbac0cf0bd30ae3e3
    .quad 0xbef8739bcd7181ec
    .quad 0x7a90228108de235c
    .quad 0xa1e4daca17732e9a
    .quad 0xb06a2c27eff84879
    .quad 0x63ebbd76a5978d3f
    .quad 0xa0993c83601baec6
    .quad 0x8237f29be4f2727e
    .quad 0xf596877b6c6d07d5
    .quad 0x96ec24a9dc59f289
    .quad 0xe01b9943b8895b54
    .quad 0x83e0a37494e49b2b
    .quad 0xf493cbb86a8562ea
    .quad 0xd2e8ba7ad8a81627
    .quad 0xf93867500bc0d143
    .quad 0x1b889bb370a59393
    .quad 0x5d766fe281183c52
    .quad 0x48ee948a66492000
    .quad 0x639642cefc1494f9
    .quad 0xc271b4fe537dc795
    .quad 0x1ab6b51f1611cbfb
    .quad 0x9385742f4311444b
    .quad 0x6ff34d2bb11d30b7
    .quad 0xdd5ee266af955a28
    .quad 0x5b49ad24f224b928
    .quad 0x694ee15b7224d892
    .quad 0x559dea338dd3ad34
    .quad 0x5694d091aec523e7
    .quad 0x1b6d06f67939e67b
    .quad 0x734680cb1041681f
    .quad 0xe1be7c2d5fcd9c2c
    .quad 0xfe21aa672a804e41
    .quad 0xeba377287db42d62
    .quad 0xa1a126a00c926536
    .quad 0xbb9d8dcc500c5979
    .quad 0x6a13aef21ee76257
    .quad 0x89811f2d266af070
    .quad 0x74ab275c005f9270
    .quad 0x337ef41d56737ce5
    .quad 0x8a5fe23956d3a687
    .quad 0x6cd1fa758209aa79
    .quad 0x242ee9370a6b034e
    .quad 0x05288dcdd5b15468
    .quad 0xbfb23c51567f2800
    .quad 0x570e0b3e9e297934
    .quad 0x59dae687ddb8f6e9
    .quad 0x574f67c74a693eb4
    .quad 0x9541d9e2139cbe0a
    .quad 0xd2e13929218d513e
    .quad 0xf16e0130d841e1b0
    .quad 0x8c86ae489af2d424
    .quad 0xdfcc02075c00363a
    .quad 0x0b32597ac1cfcf9f
    .quad 0xb78f5f58b59944a2
    .quad 0x481712fac536f002
    .quad 0xa0cf4bccb6c492fb
    .quad 0x434c50100eef3706
    .quad 0xa5d3f8ffee0e5f8b
    .quad 0x993d8b090aa323c0
    .quad 0x890c2890e007a897
    .quad 0xeb878300355a4c31
    .quad 0x45dd6bf9333c4956
    .quad 0x60be6da1a2c82ba3
    .quad 0x3f67ae275f931ab1
    .quad 0xd04c3c2722923db9
    .quad 0xf88746c31513b9f8
    .quad 0x8568da20f65d99c0
    .quad 0x8dc5e11992a4263b
    .quad 0x65b519fa18d2b023
    .quad 0xa39103a08721c257
    .quad 0x498a2731885e6ef2
    .quad 0x6c67957f4faf09ea
    .quad 0x482089f997b002de
    .quad 0x01e38c72a5878304
    .quad 0xfcb4fd479b211e2e
    .quad 0x1d25d2c39cb6808e
    .quad 0x53b96dbbf42ec727
    .quad 0xc333c0786010d232
    .quad 0xf2a9c05f2078925e
    .quad 0xba05c2213459ccf9
    .quad 0x41cfb5870f8c6e0a
    .quad 0x71a06ae2814bcf0b
    .quad 0x77e3ff73f914f041
    .quad 0xdd0407d05318a34d
    .quad 0xf7c0f4b03b8f302b
    .quad 0x669b93f2d236d1fa
    .quad 0xce169748e11c78dd
    .quad 0xecf7aa16124d0ff1
    .quad 0xda2c45caf33cf1d6
    .quad 0xd5d2ea5428ce8f9a
    .quad 0xcca67c791e7bfd3f
    .quad 0x7b2c2cd6de519711
    .quad 0xf59d2247e407befc
    .quad 0x23b5c248cb70ed69
    .quad 0x604bae429e7901e0
    .quad 0xb9108474240c6ec6
    .quad 0xf6b906dd84d920fd
    .quad 0x83911c8adf0689f6
    .quad 0xb17800b31faf3713
    .quad 0x0ca139cc38b9b7bb
    .quad 0xb2bef980b91d846b
    .quad 0x60c89e62da76fc59
    .quad 0x802274d37a8119f8
    .quad 0x4de6a65ddf139994
    .quad 0xfa6dc7e43d5e4b5e
    .quad 0xaf34e4d177051949
    .quad 0x76bfb778493c6b9d
    .quad 0x5b5dca2181bbd9a3
    .quad 0x43bae06b424839b9
    .quad 0x80edc78e06e2638a
    .quad 0x4a8a106c50b96f4e
    .quad 0x32425d0703a3dd0d
    .quad 0xd45b85e58bad38c9
    .quad 0x571002f46fa5864c
    .quad 0x44eedd4eb368bb20
    .quad 0x690b8a741fab516f
    .quad 0x71b207291c2330b4
    .quad 0xc00e24f902facb19
    .quad 0xd1c55b1d064b6ab9
    .quad 0x145cd01d5f7adcd0
    .quad 0xf214a67e35b7ac06
    .quad 0x6ea7dc02a6e18d94
    .quad 0x5ef3f98da5773921
    .quad 0x6a112237b2c33145
    .quad 0x93a6b5f829b1b015
    .quad 0xec446e5795773463
    .quad 0x4b62fd7d4085686d
    .quad 0xd5f61456e269447e
    .quad 0x9ad8da8b8ea5690e
    .quad 0x37cf4f21ee5c4e2f
    .quad 0xd394a2cfbcd1c6db
    .quad 0x503bb8f6abad005e
    .quad 0xf46e1eef9740e5b5
    .quad 0x7562dd42d39a8fdf
    .quad 0x75898649286d1b72
    .quad 0xe172fccdd9a2839c
    .quad 0x285396820bd8a049
    .quad 0x8f93f82ca6913cc3
    .quad 0x5811a01ad59d56a3
    .quad 0x91187158328f42b8
    .quad 0x368e6958d297e937
    .quad 0x65caf0ba34b684c5
    .quad 0x5f62b55a9cd02f93
    .quad 0x54187c8acf0f9f2f
    .quad 0x9cb9a5cecebb268f
    .quad 0xf2b84e013662d962
    .quad 0xdae65ecc57efb8a6
    .quad 0x34310ed055feb33e
    .quad 0xcb9fe2eaaf1f244b
    .quad 0x30fc7f8471f4bbbb
    .quad 0x927894c3894536e1
    .quad 0xe2848a13723bc3ac
    .quad 0xe7ef80e29a8f9453
    .quad 0x90058bf6ccd9b4c6
    .quad 0xa0ae61402d861700
    .quad 0x9bb1f47fef40377e
    .quad 0x77ddece1a6734af4
    .quad 0xaca65bb328435c5a
    .quad 0xc1ba4191e8058aaf
    .quad 0xcc0b9556bac3304c
    .quad 0x25d7d372c243e6d7
    .quad 0x0dec587a0b4212f7
    .quad 0x1dfba988cc19202d
    .quad 0x653a5a487a6796c2
    .quad 0x9977759e4a4f387d
    .quad 0x9ff4e924b6b7f80d
    .quad 0xab805c5de6269a6f
    .quad 0xa71ac0850de3f280
    .quad 0x5671d110c90f1248
    .quad 0x069d245e99b48bfc
    .quad 0x876d1cb0d3cff4ba
    .quad 0x7a787846a6062e65
    .quad 0x42dde9c32025d33d
    .quad 0x7f25e46b316ce468
    .quad 0xbe0982cfafb98993
    .quad 0x92b85bd4a9f95a0f
    .quad 0x8d474edf76c01f42
    .quad 0x49ff22310069c699
    .quad 0x591a060e1b233686
    .quad 0x4915d39b1dbe939e
    .quad 0x5886131e73774c6c
    .quad 0x4972afb9ef35f3d1
    .quad 0xfcb49f1982982b83
    .quad 0x36f587f92724ebc4
    .quad 0x95a9ed67920495f5
    .quad 0x5c09aee993db2e83
    .quad 0xef858030b741b2b1
    .quad 0xa983955fe3a42c86
    .quad 0xc6e94676fc31f309
    .quad 0xad72acb90f4d4d73
    .quad 0xc4db9a0bc3bbb481
    .quad 0xd43c24e3cb9ee2be
    .quad 0xd743382ef65680bb
    .quad 0xc62f604dee347132
    .quad 0x59048663a786604c
    .quad 0x3396fe9a34b067d7
    .quad 0x72b1116baa42ea73
    .quad 0xf8b6b3ddeea6578c
    .quad 0xcff5970db440e8de
    .quad 0xcd8a8750941f8524
    .quad 0xad888d29b8dfc315
    .quad 0xd5b3cf83ca983822
    .quad 0x599fdc3d17ebf8d6
    .quad 0xe3375633bb0dd3ef
    .quad 0xbae2ec776e0393c9
    .quad 0x49a57b1c6cdf669c
    .quad 0xf387f91d121bc100
    .quad 0x5dcbec432d51275a
    .quad 0x0a4849d16c0b98a5
    .quad 0x8ec270b4a4b45c8b
    .quad 0xcbbdd252abd1760f
    .quad 0x40639c3d7308ee37
    .quad 0x0ed776717f4b7bb1
    .quad 0xce88cdfd159e4451
    .quad 0xfbd2e5916b5bf084
    .quad 0xa4d025fcaa1e95be
    .quad 0xf2e95c0d79a30f19
    .quad 0x34e1df77e51326c3
    .quad 0x8b74bacd7d97eab0
    .quad 0xbb78b4adc7ccd499
    .quad 0xf77a591dcd8a219c
    .quad 0x740ebe61b3c59931
    .quad 0x4009fc573f734962
    .quad 0x9db8902f6d4c3b2f
    .quad 0xc1e90452def1a213
    .quad 0x94aa8f98cafbc3f0
    .quad 0x2158ef949cf7e46e
    .quad 0x485a1b52bf15bdcf
    .quad 0xbe6db8f638a2e47b
    .quad 0x30162d7567fa9f2f
    .quad 0xeb3dd8c018d97088
    .quad 0xa1b9791e0b5813a5
    .quad 0xd23987d9b8fbbdda
    .quad 0xfeb8acbbeaf007c5
    .quad 0x36516b8636cbc391

.section .data.core_0_el1_ns__data_shared_segment_1_1320
.global core_0_el1_ns__data_shared_segment_1_1320
core_0_el1_ns__data_shared_segment_1_1320:
    .quad 0x4c2dd7abff22e7f0
    .quad 0x3f9a405a14c86ce3
    .quad 0x79e6802459ce5511
    .quad 0x2832fe4b798c87c9
    .quad 0x8157a7f5b38de2ec
    .quad 0xbacb376f2d02c135
    .quad 0x53fc249b99428d3c
    .quad 0x814fd42ea4350738
    .quad 0x5e356aeda3e42995
    .quad 0x7392c42245aa150a
    .quad 0xbbb3a9da97a97ac1
    .quad 0xcd8c941b3644b799
    .quad 0xdaea3b95c914e782
    .quad 0x7f39feefe51eb4db
    .quad 0xdd6e6cf526b89819
    .quad 0xb94d72971635bf50
    .quad 0xfa9ae04c5db4be9a
    .quad 0x74c6c7e3501c82a0
    .quad 0x5fc4f919cc125785
    .quad 0x10dea72e6dc0888b
    .quad 0x54fb100fc1c18b49
    .quad 0xd68f25a105908114
    .quad 0xa7fddd7c27d3dc12
    .quad 0x63fdebe2106912b2
    .quad 0x6c40203300bd4f2a
    .quad 0xc8b9bf9b9cd1104b
    .quad 0x2b34207c872e6a77
    .quad 0x1eeffc9137b4d2ee
    .quad 0x9caafd61f253ff12
    .quad 0xb042bc3c8d75aa61
    .quad 0x4b4919e5d093ed36
    .quad 0x8d40505532026018
    .quad 0xd4c9bfa25fa8c521
    .quad 0xf61c71bab06d95b4
    .quad 0xcdc550b1d769f860
    .quad 0x8f28d693b722071a
    .quad 0x1511cb7b6a9b6d88
    .quad 0xa724c2171e15ad2e
    .quad 0xc9068983fad96e93
    .quad 0x6c934c6bc99a44f6
    .quad 0xe992e2e8b5d4b374
    .quad 0x492f42fef137c4e3
    .quad 0x6c85d6cb18c1b1bc
    .quad 0x110e4d1e18d13ae8
    .quad 0x9fac21ba56c2bcbe
    .quad 0x35a818784855e233
    .quad 0xa4ec6e38a2f18d04
    .quad 0xbf5f4455f4611270
    .quad 0x2ca878643e1da297
    .quad 0xac586a5ebd213642
    .quad 0x364b9a07801675c2
    .quad 0xbe21fcb121f2fc5b
    .quad 0x21dc3f65068c2173
    .quad 0xb3fab81e459f9aba
    .quad 0xb566637353470aa8
    .quad 0x40e8a59a5ef0cb47
    .quad 0xbd68fc74876f10a3
    .quad 0xc5b91625eeba76a7
    .quad 0x972ace62fb4ec4cd
    .quad 0x4e9a4dbffa03d813
    .quad 0x33b54e6d2a110c30
    .quad 0xda4822a966715eb9
    .quad 0xa7bdc778c3c1b2fb
    .quad 0x0acc2e38751fb4f8
    .quad 0xa8a8b0df5eaeba1c
    .quad 0xbc031e8b748d61b7
    .quad 0x3039fbe7f29bf228
    .quad 0xcbd526b99dfac0ae
    .quad 0xb0db8da174b3c51e
    .quad 0x1fc1b7c8fc4df573
    .quad 0xdd1e476642f08f20
    .quad 0xab83fe38536cfc20
    .quad 0x83f3898b63284640
    .quad 0xf3d7181029974d37
    .quad 0xd5ad1bad3305b77a
    .quad 0xe8d8b5e8a91361b9
    .quad 0x88bb08d60f8c322c
    .quad 0x522a1dd343234503
    .quad 0x24eeceeb3974c202
    .quad 0xfa738cacf4b183a5
    .quad 0x47520e5773ff3cb8
    .quad 0x6cc19d3dcd0d8e04
    .quad 0x64204958ef56e9e5
    .quad 0xb25f8b0a12e02210
    .quad 0xad14035f9dfabe31
    .quad 0xf4ea1e5f8754a688
    .quad 0x139d5e231876ff4d
    .quad 0x3b5b0b8011791447
    .quad 0x7dedd228f7c75951
    .quad 0x9e1e51acdb9b14aa
    .quad 0xd6ccc7f865bd503a
    .quad 0x141dff1e989aac8c
    .quad 0x3966e2dd19ca1b10
    .quad 0x7691d50e97375200
    .quad 0x81584da26cf83dc6
    .quad 0xb5cf4254a80082c6
    .quad 0x08a9ad60f08468c3
    .quad 0x2e0fc1765672d549
    .quad 0x16e319b27eaeaaaa
    .quad 0xec69600e8669f199
    .quad 0x856fd4373aa6fe5e
    .quad 0x89ee1178c36ea7cb
    .quad 0xc8cc276f3fefe01a
    .quad 0x09b42e0ec6f885b4
    .quad 0xe734512f5a567b00
    .quad 0x6461d2dd502f0812
    .quad 0xd2c255076f095f6f
    .quad 0x230824b5b3b011fe
    .quad 0x3705b219e246c411
    .quad 0xef03b644f1d6b8ec
    .quad 0x3a742b78ec26dec1
    .quad 0x4fc4df6d200d58f7
    .quad 0x0e80270c640d94d8
    .quad 0x0e0f17b09542a36e
    .quad 0xf2008d0239c0bd8a
    .quad 0x51069537b1d14c52
    .quad 0x6788cf72f404daf8
    .quad 0xb97f0d47c17a8c91
    .quad 0xb83053b2b090ea09
    .quad 0x7dcd082e0c275b8d
    .quad 0xca1a07e336377e6b
    .quad 0x42a20cacdd8f0f2c
    .quad 0x43a4885b1abb31d9
    .quad 0x2310bdf929e70dca
    .quad 0xdf175f570f958d72
    .quad 0x3329c572340021d9
    .quad 0x128beddf06784951
    .quad 0xcc6f1c6618b3b363
    .quad 0x3e48518338ee5c91
    .quad 0xf8cdf054303ad69d
    .quad 0x49fc6c07a39a850a
    .quad 0x045ec9c9a7c83086
    .quad 0xe9488d2801516d2b
    .quad 0x861488f8318b545a
    .quad 0x4ee59452c6b65860
    .quad 0xf4e40954e926bbb6
    .quad 0x651fd8e24c1a31fe
    .quad 0x3290ffe084b3e6c3
    .quad 0x229aae8675dc4b4c
    .quad 0xdf0e26a6c93bd560
    .quad 0x3730b2c55c2c462e
    .quad 0x62ca59bd2caba095
    .quad 0xf5611961bac5d1e3
    .quad 0x290aade90d8317ac
    .quad 0x948fd2690560d642
    .quad 0xc0c79cac0f9533c5
    .quad 0x80f0696ee927cd9b
    .quad 0xd934a7562630e8f0
    .quad 0x6799b61b56289680
    .quad 0xfdc562383d868ebb
    .quad 0x20c24b742baa8b5c
    .quad 0xa2b72f67df86c14b
    .quad 0x8e7a6abcacca71ad
    .quad 0x891c0675ca9f8c69
    .quad 0x669c85a94bc22475
    .quad 0xd5d173da0849624b
    .quad 0xe6036295b4a33ce1
    .quad 0x30c9b9350e32b899
    .quad 0x335c4a6b819d67a0
    .quad 0xac978efb5bca381f
    .quad 0xe0dee147ad78fa57
    .quad 0x923d36b516911756
    .quad 0x7fb371476ca3b47e
    .quad 0x97d7e7763e719534
    .quad 0xd69d199e517b4e1c
    .quad 0xe5fcb9792f71f113
    .quad 0xbbce5c3d1e352911
    .quad 0xb4ab9b0ba740cbe1
    .quad 0x74e4993baa0251f4
    .quad 0x651a5f0380bdc895
    .quad 0x98a4119f797415d7
    .quad 0x6fa313070c7f9850
    .quad 0x0a9e9453d0ae4e58
    .quad 0x05588ff99a8414a8
    .quad 0x3138f2cfa08a8b57
    .quad 0x1f529bf3809d2a60
    .quad 0xc8647a8117240609
    .quad 0x0687c644ff786d09
    .quad 0x944b1496bca79c2f
    .quad 0xe83f1297341ac2cc
    .quad 0x8894b40151eaa056
    .quad 0xc84b7b206c532629
    .quad 0xfa93e8ac8e5867c0
    .quad 0x1c67aaea125c212c
    .quad 0xb5a35a1811a70521
    .quad 0xeb3aaefa7cd0eece
    .quad 0xfef8d42368666c08
    .quad 0x207cd3738144fc20
    .quad 0x85ae4b43148bcd80
    .quad 0x17ad8f695d77c947
    .quad 0x5d4df45cf0af0f0c
    .quad 0x0ca0b9fa347752e3
    .quad 0xead6d2eb8aee2cfa
    .quad 0xb4b3180e9edaff11
    .quad 0x2af635d1cf37a874
    .quad 0x4387e4278b9ff7a7
    .quad 0x6b35d37512ca5842
    .quad 0x856f0ad6fd63a134
    .quad 0x1924c26d9d9d7353
    .quad 0x02fd850c8d5bbedf
    .quad 0xbb9baf5a4740c952
    .quad 0xf340b70fcd0782f1
    .quad 0xdf088b6dc166b7c8
    .quad 0x28e4ac75ed97abbf
    .quad 0xfddaad1643b23cda
    .quad 0x316fa036305a4dca
    .quad 0xd9517d0571ae957f
    .quad 0xaace0fee53e3bd89
    .quad 0x1ebc9432cc082f29
    .quad 0x352462a42a3e7ab0
    .quad 0x698507dfb03982c1
    .quad 0x0aab19f68357aad6
    .quad 0xb5054bd68dec6fbe
    .quad 0x75fb064db6942b70
    .quad 0x4bcef4b1dca92bb1
    .quad 0x322b681e987ffdfb
    .quad 0xb889f7a3074ffde9
    .quad 0x772d01de2d8c64d4
    .quad 0xf7cbadc3e31a70c8
    .quad 0xb72097d140c6fca4
    .quad 0xa47cd46f540e3660
    .quad 0xa6c1c1dcc633bdf3
    .quad 0x1921f533e995086a
    .quad 0x8e79a8bbcdef379b
    .quad 0x7bddde188b2e5378
    .quad 0x6bba240e873f275a
    .quad 0xf00c17fcd507daa9
    .quad 0xf12829eeef2b7aa7
    .quad 0x690f48b79c37852a
    .quad 0x4adc992b3a4ae074
    .quad 0xe0cf8d21eb8b5fc2
    .quad 0xda0119dc2161cf23
    .quad 0xc9dc614c1b871dcd
    .quad 0xd30c36d1454c99c9
    .quad 0x667b5be7d71523cd
    .quad 0x2616ce0c10f9e23f
    .quad 0x19d7a87be57c2b66
    .quad 0x9bfca95c25d277b6
    .quad 0xc452f11e536e86b4
    .quad 0x1edcdba3fdabcf9d
    .quad 0xdafafd6b52a0bc4b
    .quad 0x5e4a00d065a36c71
    .quad 0x46d444614cc5996a
    .quad 0x2132737e17bb71d6
    .quad 0xf5fb0b287cf96ce6
    .quad 0xd55552c7112eaa45
    .quad 0xe3bf07bafd43b7e9
    .quad 0xe1984a4cb6f26729
    .quad 0xc6e3c1bfa7be25ee
    .quad 0x863f238e951b8de1
    .quad 0x9db2cdb5372b7387
    .quad 0xba7bd22a603d2f29
    .quad 0xc75d393c32e2600c
    .quad 0xe6fcc755347d84ac
    .quad 0xe50d8863cfbafe5c
    .quad 0xeac76b13860333ff
    .quad 0x6edda3eab7d32369
    .quad 0xfe80873725507944
    .quad 0x1a1b3c029ce5c721
    .quad 0xb1b25844931406a1
    .quad 0x23a82ccf8ba7cc9e
    .quad 0xa6d52d160e1dd6d0
    .quad 0x56c777cad2e37356
    .quad 0x8d010afbc3fbb695
    .quad 0x3919e0093bee22da
    .quad 0xb844d8357db2cfa0
    .quad 0x54689b51891da626
    .quad 0x03c28928f5b19b4e
    .quad 0x3651df8efd53cf5b
    .quad 0x8bc41b3106575cf0
    .quad 0xaa68b7fcfaa24c69
    .quad 0x559174130641bf97
    .quad 0x6ef11ef84b59590a
    .quad 0xe94f8c5e79640055
    .quad 0xd4fdea35794ad7c2
    .quad 0x315a9c44a4b69f7f
    .quad 0xc50ca53d3fae2781
    .quad 0xf87988245a0702ae
    .quad 0x4cdd3da43590d86c
    .quad 0xa4631473b9dec500
    .quad 0x4b835824a0abd3e9
    .quad 0x6fb7b9b6ff4b63f0
    .quad 0x5c0bdae0e4948030
    .quad 0x124a9d1acd1575b3
    .quad 0x086036944467e89c
    .quad 0xfd1cf145d64b01be
    .quad 0x82dee7443e1fd07a
    .quad 0x5ac407bc8ea9c52b
    .quad 0x421df423be792a68
    .quad 0x3424f66a5a252f4f
    .quad 0x220cbd0faf021953
    .quad 0x2f44dc4cd53c70c5
    .quad 0xbad93e7f099c5b3f
    .quad 0xbfac2fd89044f2a3
    .quad 0xfb8738ec8d1d3cd2
    .quad 0x4ca3066870c6a823
    .quad 0x9c7b74a233704b58
    .quad 0xf71800811a21bc50
    .quad 0x5d5910aa33a31825
    .quad 0xcc5933e3e6faf828
    .quad 0x2d806c1510259dfe
    .quad 0x55c8cff9c0948b3b
    .quad 0xd7be88c450a41e20
    .quad 0xfe227162ecc217b3
    .quad 0x0f0c7c942f8bdda7
    .quad 0xe1c8b53ca41dc4cc
    .quad 0x56198862a8a04ffe
    .quad 0x3dc0d32e901c9e84
    .quad 0x0bc1cfba93401885
    .quad 0x711f580443950a14
    .quad 0xf069baf3edf50caf
    .quad 0xe62ffcb576ada15f
    .quad 0x01c9bb11c48654a3
    .quad 0xc05224755d228f50
    .quad 0xc67a352bb66e2c8b
    .quad 0x05a0ac355af93bad
    .quad 0x897edae77ce3620c
    .quad 0x9bb5b34f1a9a1c92
    .quad 0xa54e91b8735b79c7
    .quad 0x8fe38d1ad431f088
    .quad 0xa3e8f28690f8701a
    .quad 0x9be0dcd179703dd1
    .quad 0x95f635ef9be3ca0e
    .quad 0xd49a7ab43fd78f03
    .quad 0x6a52998632ec7dd3
    .quad 0x1a298881d2c6f128
    .quad 0x34cab12986d0e754
    .quad 0x9227d925e49eb7f9
    .quad 0x295855b0f566a6cf
    .quad 0xd9392f7f11b17842
    .quad 0x73ce44d88c1669ae
    .quad 0x41e001e96d0aedf1
    .quad 0xec647cc086a23788
    .quad 0x7868d07a39cf372e
    .quad 0x726daf89f2804d49
    .quad 0x21815395900048f6
    .quad 0x8071d863c6060d6e
    .quad 0xaf0ae12c02297e42
    .quad 0xf97a274e0e05a8b9
    .quad 0x816cf3a5b96a7985
    .quad 0xe0710f278f8782fb
    .quad 0x96b1121acce474c4
    .quad 0x988ef08b43855d29
    .quad 0x131a9025ca548e4e
    .quad 0x6e567c9e46dfddcc
    .quad 0x0d415ef0fb897ac5
    .quad 0x29a1171ac5623678
    .quad 0x6c80d00bc7edebb6
    .quad 0x7a2af23dfefbf9b3
    .quad 0x9f8817f5e10569be
    .quad 0xc06ba8daefb4ed12
    .quad 0x042978d4d593e25c
    .quad 0x8c4b5803e91dd78d
    .quad 0xc37a4ee5364f56a5
    .quad 0x34d717af843e3db2
    .quad 0x1ed5e5ddf1cb944a
    .quad 0xff7f3112c9b3bf13
    .quad 0x4ec2132c4f033a20
    .quad 0x73e5da7913060db3
    .quad 0x1f69c30d8b59937f
    .quad 0x6e5bb8bfa1e0717d
    .quad 0xfc5385038d5c9e64
    .quad 0x68cdce7639c95b5d
    .quad 0xcffb4f29bf1592cc
    .quad 0x7dbd40392ed63906
    .quad 0xac01828c58724a97
    .quad 0x43c5bd74c3523f46
    .quad 0xd5c06bb0b5a50439
    .quad 0x7248724ce34a672e
    .quad 0xed94ba28f305d59a
    .quad 0x570b409e0cd9ffa2
    .quad 0x1ecea7c1db2bb0c2
    .quad 0x335043c56e89fa20
    .quad 0x9728accf943a62f5
    .quad 0xf62e86385287b393
    .quad 0xce5a8b815987f01a
    .quad 0x0221b4fe1d275e54
    .quad 0x1caa4cfb8cc9881e
    .quad 0xa9ebb88e4334a621
    .quad 0x2d95cc4a106f5905
    .quad 0x539ebacbbda610f6
    .quad 0x29d7bebe62b88ba8
    .quad 0x7732e75f600e7de8
    .quad 0x793e74ccc77fd209
    .quad 0x542f8991506d1d51
    .quad 0x3efae4e45837b8c5
    .quad 0x2927e13c3dc3a9fb
    .quad 0x72a5e18bb11f97d1
    .quad 0xd0874ae049b50970
    .quad 0x4d15a067ec2309fb
    .quad 0x748d71f127634940
    .quad 0xbf5b8694fc7c153d
    .quad 0x6c8cba7a35f19932
    .quad 0x32057127caf820b5
    .quad 0xb0e4beccdf488ee9
    .quad 0x023ea82fa60a4674
    .quad 0xb8d379b68bb02fc4
    .quad 0x2b29509fa00c4f08
    .quad 0x52cccfb8f7f60727
    .quad 0x51fb3e5020652016
    .quad 0x0161a97e1ebaf2f8
    .quad 0x7720839c293b71a6
    .quad 0xa247b058061e98af
    .quad 0xda6984cf10a1098b
    .quad 0x31e5ac96979948b4
    .quad 0xf6b05f132cfb39e5
    .quad 0xd077caddd2f406a5
    .quad 0xf30c9a4a94598528
    .quad 0xce08ff1824d62f98
    .quad 0xca4d3a35b114f387
    .quad 0xb0dc02a78f59ed39
    .quad 0x9cda14bd7df67436
    .quad 0x36e781314dee31ef
    .quad 0x0af4f89a3de9a4c2
    .quad 0x6f48fb7608532408
    .quad 0x2942fca6cbf9a20e
    .quad 0x02ae77a762e1dbd6
    .quad 0xf0db1a84578b9d1a
    .quad 0xb7bf94b1108549aa
    .quad 0xd4a6e54c5b077f5c
    .quad 0x7074babec8b5ce0e
    .quad 0x1dbd7ea04a8bd60f
    .quad 0x2b58fd401ecdc58e
    .quad 0xb13022f3750fa995
    .quad 0x2ae326f77a0736e7
    .quad 0xedf6cd2011cd37f6
    .quad 0x404d5c0964f3b2f9
    .quad 0xe260994d4dc0dbeb
    .quad 0x5620f773e41f4b6e
    .quad 0x3a759a8c1b284712
    .quad 0x4a196d419a0df5fa
    .quad 0xc8ed91f112309f6d
    .quad 0x7f2613b8a0d4b1fa
    .quad 0x3309cbb68d18eb71
    .quad 0xfb6240c6c931b625
    .quad 0x81fed691b7703917
    .quad 0xeca43448bfe58229
    .quad 0xbde3cce3eaf6e4ae
    .quad 0xcbe1b04bef44a06d
    .quad 0x2b9475644800e775
    .quad 0x12e5b950e86a6751
    .quad 0xbc71a55808eb4bc4
    .quad 0xb248955d1458206d
    .quad 0x44a97dd205aa0dab
    .quad 0x6d40a29633c9a55b
    .quad 0x8cace65552d59bf3
    .quad 0xda76804a70ea9a99
    .quad 0x70aedea25a6fe3fe
    .quad 0x9ca647826581524f
    .quad 0x4885e0246768ae5c
    .quad 0x4d38ac84ecb366d0
    .quad 0xecfab5cef26cbfe1
    .quad 0x690282686bcce0c5
    .quad 0xa269ea10482728e6
    .quad 0x29df48fb1d55f232
    .quad 0xbbeca866bf612a78
    .quad 0x19139a9547e73eba
    .quad 0x8ac2a75cbc98ccfa
    .quad 0x01f2dba87d61aa62
    .quad 0xd6371e55aec3dfc1
    .quad 0x7d392a9befd24c04
    .quad 0x2880fbb192066ab6
    .quad 0x594282637dd73fbb
    .quad 0xffc062c1ead5dd1e
    .quad 0xfdff4cec93ff96ee
    .quad 0x9d0e1f39d5a5a8c1
    .quad 0xd1fb2a6d78e21d82
    .quad 0x3595ddb243f9aeb6
    .quad 0x0ee6f2bfb03782b2
    .quad 0x65f74ea54bc28042
    .quad 0xff21b24487a21be4
    .quad 0x3c03b5881926489a
    .quad 0x45adb14555a49b21
    .quad 0x4bdc2d6d4b24b513
    .quad 0x7222c2f01925f4ae
    .quad 0xdb976b365579de86
    .quad 0x3a737377027a563a
    .quad 0x68abaa8b6424c4e7
    .quad 0x61b27fce328955e4
    .quad 0x71e7cfaa56f96208
    .quad 0xf93b0d7f1454252a
    .quad 0xf301820a32235d61
    .quad 0x0ff547fd95e3a4da
    .quad 0xf62eef52f2b3d714
    .quad 0x8c2e485be3327ae1
    .quad 0xf82628bcb2d1bfa1
    .quad 0x5af3d7bf36e363b3
    .quad 0x8b411618d8ff6921
    .quad 0x34bee602bb91cdd3
    .quad 0x48d6675236cedc5d
    .quad 0xcc57e73dacf3dac7
    .quad 0xc3498a8e2225e7d6
    .quad 0xb5635d51111c6a8b
    .quad 0x12f73f27b5b18a76
    .quad 0x113b0675393fbc17
    .quad 0x40ce416d81f57283
    .quad 0xc3dfa9e063caa271
    .quad 0xe01bea9dbae92514
    .quad 0xcb86e97f4f04c3ef
    .quad 0x549d58e2117eb5ab
    .quad 0x2c6d8d05a9f04626
    .quad 0x355b0573f8c8fa25
    .quad 0xec3a1dae6fe13a61
    .quad 0x1e238de310f7e68f
    .quad 0xfecc45cb7a83521f
    .quad 0xf2ede0b5be6150b4
    .quad 0x07fd538c369a1212
    .quad 0x9deebe65176c8a0f
    .quad 0x8400c9e36a0a7e0a
    .quad 0xdc6e4189bafb37b3
    .quad 0x697f2ccaee78469e
    .quad 0xd0ed325cc9d8f258

.section .data.cross_core_data_segment_1298
.global cross_core_data_segment_1298
cross_core_data_segment_1298:
.org 0x4e8
.align 3
label_4901_end_boot_barrier_barrier_vector_mem1985__core_0_el1_ns:
    .word 0x00000003  // 4 bytes

.org 0x780
.align 3
label_4922_end_test_barrier_barrier_vector_mem2017__core_0_el1_ns:
    .word 0x00000003  // 4 bytes



.section .data.core_0_el1_ns__data_preserve_segment_0_1321
.global core_0_el1_ns__data_preserve_segment_0_1321
core_0_el1_ns__data_preserve_segment_0_1321:
.org 0x340
.align 4
test_end_str_block_mem2196:
    .word 0x54202a2a  // 4 bytes
    .word 0x20545345  // 4 bytes
    .word 0x4c494146  // 4 bytes
    .word 0x2a204445  // 4 bytes
    .byte 0xa2a  // 1 byte

.org 0x584
.align 1
core_0_el1_ns__exception_callback_LOWER_A64_SYNC_mem1979:
    .word 0x00000000  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0xa28
.align 2
core_0_el1_ns__exception_callback_LOWER_A64_SYNC_mem1980:
    .word 0x00000000  // 4 bytes
    .word 0x00000000  // 4 bytes


// No uninitialized data on core_0_el1_ns__data_preserve_segment_1_1322 data segment. skipping .data section

// No uninitialized data on core_0_el1_ns__stack_segment_1323 data segment. skipping .data section


.section .data.core_1_el3_root__data_shared_segment_0_1331
.global core_1_el3_root__data_shared_segment_0_1331
core_1_el3_root__data_shared_segment_0_1331:
    .quad 0xe5e5fd06792f73bf
    .quad 0x80bab60284a3fd28
    .quad 0x7828429cbbbb6fc3
    .quad 0x18afc3bce9e283df
    .quad 0x1853f7722cd03254
    .quad 0xbe83a0066941bd80
    .quad 0xdffef20155fdec7e
    .quad 0xdac594bf04a57024
    .quad 0x21510d0d8203804a
    .quad 0x78a3ea2224581444
    .quad 0x2237da7c985ee99c
    .quad 0x80569caa4a4a3f39
    .quad 0x864ef16c81e84c49
    .quad 0x1fe3833f20acb58f
    .quad 0x693136a1d3e832b0
    .quad 0x67254cb4e258c50c
    .quad 0x8aa4f9b2a73742e1
    .quad 0x1a978ac23e3f0471
    .quad 0x007686103b0bc291
    .quad 0xec2c6fb89979cf3e
    .quad 0x82ab823731134b9d
    .quad 0x61300ebca0a95dde
    .quad 0x7e32d5090bddd181
    .quad 0xb542b23c8df40912
    .quad 0x2ea7f538c4204f98
    .quad 0x2927211a59dfb980
    .quad 0x38dc5a813f88f008
    .quad 0x04d44846e1e4f93b
    .quad 0x62dee85af9a4f5b7
    .quad 0xb3c0d6acfe85571d
    .quad 0xb5d976cfc7880434
    .quad 0x30913fcdc7597519
    .quad 0x0a1553df9f689bbc
    .quad 0x93b715bb791314ac
mem2012:
    .quad 0x131665f4bb7bac8a
    .quad 0x232f62dbe1ef5ad3
    .quad 0x1d779d5abd6fca9f
    .quad 0xedcf43257245dfe9
    .quad 0x49cd2aaf890d9eaa
    .quad 0x81a6f84b99cedd33
    .quad 0xa02c975552db1978
    .quad 0xbd6c6af2cd68b359
    .quad 0x7084651abee94200
    .quad 0xcd905ff1b2be272f
    .quad 0x5921da5f7df73eea
    .quad 0x0a778f248eeefa36
    .quad 0x0456bd58e9a1f814
    .quad 0xd661cc419488ec51
    .quad 0x78e9000ae72dfd57
    .quad 0xa59c694e31fd97ce
    .quad 0x42e1c982fa08c1c7
    .quad 0xf28e461045e8965b
    .quad 0x1745156c2624a799
    .quad 0xf572b98c32be3de3
    .quad 0x4a9a2edf388f19a3
    .quad 0x95206a05f49e6979
    .quad 0xd21b6d4607fa1002
    .quad 0x57bbcdec3c2ab58f
    .quad 0xce91f6450461c7d0
    .quad 0xd22b732f9a29c256
    .quad 0x859cf51cb8feea7b
    .quad 0xe8b842148b46c8c3
    .quad 0xc411438508d96e30
    .quad 0x3c757177af13abd5
    .quad 0x6c4c62ec6c893423
    .quad 0xc45d0a976309e1a9
    .quad 0x80b722153b49630b
    .quad 0x26953172ca87a582
    .quad 0xb8b218141c02ff27
    .quad 0xf4b0a4ed347d66f6
    .quad 0xbcbbb0a12cb5969b
    .quad 0x0654c363037e0a70
    .quad 0x1c4ec3e64bbc4913
    .quad 0xdfc1d5e7a10202e1
    .quad 0x682dde01a35a33c4
    .quad 0x18a2fda173e1a66e
    .quad 0x7092a7722217dfbc
    .quad 0x510f6b7011d28bee
    .quad 0x24cfd2a489b84ead
    .quad 0xb5ccb793b2d1b180
    .quad 0x48819505f2835cd8
    .quad 0x39b0d41a7b9e85ce
    .quad 0xde3ffe528ba4d127
    .quad 0xd6e9baa12a460b8d
    .quad 0x41d49d94c66bc51a
    .quad 0x7459479dc4accd6f
    .quad 0xf489487af5ea2650
    .quad 0xd479eef81e0e03a1
    .quad 0x8e2d9c6df3191ded
    .quad 0xd1e61b2e7be07743
    .quad 0xb58f598c5a0a965d
    .quad 0xf8323950a2a8fc54
    .quad 0x22f6b4138c4d3776
    .quad 0x6018823535f03376
    .quad 0xd652f531d8630627
    .quad 0xa07e741a3950c9e9
    .quad 0xcad5830059111665
    .quad 0x97251613991dff15
    .quad 0x1630b4fbf2111c41
    .quad 0xbb801cc52a2bf5f6
    .quad 0x2110216669d78706
    .quad 0x726a80163be8fca2
    .quad 0xccf6da344cbd59cf
    .quad 0x45dd6816f572bc2f
    .quad 0x164c84dc34abd324
    .quad 0x8cddcfc373a5c855
    .quad 0xd8110a418b3bea94
    .quad 0x20c495fa2fabe20b
    .quad 0xc32c41eec3c8a4b6
    .quad 0x6206cb31251bc5a3
    .quad 0x76098fe71b340a62
    .quad 0x47e436e144533c4b
    .quad 0x975602f6545df2ce
    .quad 0x8d118796c7990300
    .quad 0xb2996493f76da0b3
    .quad 0x49dca1cfeb2bb2c2
    .quad 0xf5725c619ab2e1d0
    .quad 0xcd5b84e2250e50ad
    .quad 0x231f4bf57bacb7d9
    .quad 0x2879b90545077556
    .quad 0xd6a2974cf7ebf7e1
    .quad 0x5ecc82025fc4106b
    .quad 0xd7e6903bb4611e6e
    .quad 0xc6e217d5f05c60d5
    .quad 0x1cf985d81b65626a
    .quad 0x269dd5c5ba7a97ce
    .quad 0x890de682c8e3d6ff
    .quad 0xfad597d22f17dbf2
    .quad 0x70e7b2a818dcd316
    .quad 0x9dd4f3da631b1fc9
    .quad 0x619502413c685195
    .quad 0xc6e74e62a5e5460b
    .quad 0x1bd7e6fd38ca3776
    .quad 0x1e85cae6a5bc9ea9
    .quad 0xe0f6153eec69e47c
    .quad 0x680e64f348164461
    .quad 0x7a4156544748e531
    .quad 0x4594fd5f2533d9b0
    .quad 0x77eefddb1b23d8c6
    .quad 0x25fe4e1795b8b040
    .quad 0xa7519acf294b4ed3
    .quad 0x570cf98ce26365b4
    .quad 0x7aaee42ad19b5fa2
    .quad 0x1cc6aec87b0be90d
    .quad 0x560ed951e5694d7c
    .quad 0xc56c934ce3519550
    .quad 0x8aba175b983ec5ed
    .quad 0xe0a20c2f594a4bc4
    .quad 0xa2e790fdd5069abf
    .quad 0x635d48042bffb842
    .quad 0xe0ade99141890800
    .quad 0x17ebc9042e3cd233
    .quad 0x793e73b9c1572700
    .quad 0x19786f30c83af757
    .quad 0xb32823d746cea94c
    .quad 0x4821b2451b4657e3
    .quad 0x40db008d93d77085
    .quad 0xf473ca7e379b214a
    .quad 0x572639fbb550db8d
    .quad 0x84620142d7494cf0
    .quad 0x151c48f655a12d3e
    .quad 0xf7609afb02a85f7c
    .quad 0xb37b54bb803a7099
    .quad 0x78176345cdee1e09
    .quad 0x77cf1a06fe4b141d
    .quad 0xdebbb0767bdd00a9
    .quad 0xb2cb8b4f5bb7e46e
    .quad 0x14f2f2bf34271b1d
    .quad 0xe2754d93f6a5120a
    .quad 0x41fad60299c35495
    .quad 0xdf66724a5d4466b0
    .quad 0x96e59e8a7f6e5c6e
    .quad 0x0e4fba95bb270def
    .quad 0x5b6a742e88d60faf
    .quad 0xce577c81630ed110
    .quad 0xfd27451d4273f2e7
    .quad 0x61cb2cff8b86997e
    .quad 0xed4c89fab7104d86
    .quad 0xba7bee1d21fea143
    .quad 0x9f146159d0cd6e8b
    .quad 0x50742c228bb6e192
    .quad 0xdde08e9721fe0474
    .quad 0x69b6e317f4dc41c0
    .quad 0x4a797b22b2dfcf7d
    .quad 0xd2da4e8fcb9d41ad
    .quad 0xc783e3762e45c49b
    .quad 0x1d8bbac1d2751b63
    .quad 0x9e9a673c1360c4ab
    .quad 0xe3305aebdcc87915
    .quad 0xea78d0c7d74773c4
    .quad 0x699f9225f119b2ea
    .quad 0xf25df8894e918b8a
    .quad 0x35ca5e06d94b4b7a
    .quad 0xa0723bfb8c061614
    .quad 0xa5619428f20a7cc3
    .quad 0x8317977e3612742b
    .quad 0x85ecac9f33a4d66b
    .quad 0xe315e4582e0e3a6f
    .quad 0xf3f0836bd3c3797c
    .quad 0xec9f5b6e65c1186f
    .quad 0x5f2f262fd8cd4301
    .quad 0xd1b73d8630bc0bde
    .quad 0xd65e525cb59273a7
    .quad 0x17298608ee627677
    .quad 0x0ed0e3fa98febe7d
    .quad 0x7d977eeee65f5000
    .quad 0xa90f727fbd1ea4ae
    .quad 0xe29532fbdbd8e2d4
    .quad 0x8cbbc1bfaf1482a4
    .quad 0xa6f20f5bbeca5900
    .quad 0x345b56410b8805cf
    .quad 0x21e79ce53b8dbec2
    .quad 0xfc8b517e902104d7
    .quad 0xd85a5ae7b72bda54
    .quad 0x94081ea0b2876c38
    .quad 0xe30b83d37227c9af
    .quad 0xbbacfc4fb2a0280a
    .quad 0xc20f015101c7e358
    .quad 0xd2b243f86ee15ff9
    .quad 0x0942a9a2f33d0180
    .quad 0xdabf8d7e2ced0864
    .quad 0xb80ec66224122180
    .quad 0xf1f35e11e07a6ba5
    .quad 0xf9db4a2dcc48b545
    .quad 0x7a385ef860a324ac
    .quad 0x92f8bc03471cc53e
    .quad 0x12a481a5eb72f772
    .quad 0x5b3b7dee737c01e4
    .quad 0xf186f13eb6f52781
    .quad 0xd479996a38f50f49
    .quad 0x2b74b68db867f0ae
    .quad 0xd7861877ecc6d4c0
    .quad 0xa6929313247d4047
    .quad 0xeeae13493095dbe6
    .quad 0xd118386bada99f80
    .quad 0x08683f280cb9a8ac
    .quad 0x56ca79119f8372cd
    .quad 0x6c7f682cb856247e
    .quad 0xf087d904acbf9f7c
    .quad 0xf6cf8f96862fb9d6
    .quad 0xd0d79c260269b352
    .quad 0x80408cd507c9bd43
    .quad 0xa37deb44fe3537c9
    .quad 0x18405542035cb5c5
    .quad 0xce8ddad56eb33b80
    .quad 0xfad86dc8c2879740
    .quad 0x2e385ff8c58a7965
    .quad 0x45bd4cc389081863
    .quad 0x39d21b4e42e24038
    .quad 0xba8677d3455c49e0
    .quad 0x5df6069937709b86
    .quad 0xb0c26a2596d15d25
    .quad 0xc93479d5b018e09f
    .quad 0x3b073dc2e7d06f4b
    .quad 0x5aecd97cacce2c8f
    .quad 0x1ef8900096eff912
    .quad 0x8b545285c80fefbf
    .quad 0xc4f0e8dae3e78d0c
    .quad 0x75b091662d8b520e
    .quad 0x9558744538d2563e
    .quad 0x660fccc2244aab2f
    .quad 0x1af393b0d9115642
    .quad 0x3ef81821b70ecda1
    .quad 0x4eb182af2220729e
    .quad 0x342c62af806a15c7
    .quad 0xb2de3ae7c8903624
    .quad 0xba22cb5fbdfadac2
    .quad 0x644d5af6af9e20be
    .quad 0x2450966b75dd6820
    .quad 0x9ecb1853249aaaa1
    .quad 0x12fb761f320b6d76
    .quad 0x7e690b27782d8d45
    .quad 0x4ee67c9c3afae917
    .quad 0xb3e97cad950da02b
    .quad 0x58efe59393817f9a
    .quad 0x868c68763bc330bc
    .quad 0x56a13baf912168ff
    .quad 0x7f2b63197a6f7305
    .quad 0x5c24441bf74d2c13
    .quad 0x0a0e67811e383314
    .quad 0xf7da1194f3c8839f
    .quad 0x378f232c2b5212a9
    .quad 0xc6225fab63ec0fd8
    .quad 0x55e1cc710b437af6
    .quad 0x27a4a6f94dd7ad2a
    .quad 0xed664b7a3d74030c
    .quad 0x9a1d0d7c5283fe4b
    .quad 0x3e61f3b0c4a5f7d7
    .quad 0x2e3a060892bb1267
    .quad 0x41c13f07c2078401
    .quad 0x3779c7bb92e267af
    .quad 0xfad35de39afde2af
    .quad 0xcf090ecd820020e6
    .quad 0x24387a954f40f67f
    .quad 0xa0c6c32cd6fe12c0
    .quad 0x155ab2047baf0e1d
    .quad 0x9d39d98e5ac2de8c
    .quad 0x7401ff1ccb7a6c18
    .quad 0x21ccb7cac2fe61d7
    .quad 0x0536f3af0e12a7fa
    .quad 0x9cbd2042e987de95
    .quad 0xb9c972e90ced66e6
    .quad 0x47a7733aaadf7934
    .quad 0x89f310beb04d9a15
    .quad 0x8faf91dd4ea0199a
    .quad 0xcf731edc79bb9cf4
    .quad 0x94b2312c67565389
    .quad 0xc10e05982bc9f254
    .quad 0x4e92da551d113502
    .quad 0x3625ad400cf17816
    .quad 0xeb49182c59925e0c
    .quad 0x2d6550b9b7a9d86e
    .quad 0x26e0a40e3182560e
    .quad 0x9c72e76ca2d8b87c
    .quad 0x95bad90578dc54d0
    .quad 0x2ed24f1f414e310f
    .quad 0x1a8e36c187da08fa
    .quad 0x9d85fa6905d39fc6
    .quad 0x5ddb891fee0728e7
    .quad 0x3bed8278b315db25
    .quad 0x6d115b33388d6d9b
    .quad 0x68e7c04865c3789e
    .quad 0x366ee5d09fa9020c
    .quad 0xb762fc994b22c703
    .quad 0x813ff58b39035349
    .quad 0x98104e558c5c69ac
    .quad 0xfb55d0622e310210
    .quad 0x37a52de53885501a
    .quad 0x6716faad60d080a0
    .quad 0x5c56c9439f565968
    .quad 0xe1ba496e2e2234ac
    .quad 0x5aa54415a61059a9
    .quad 0x6feb6b9a5fd25f81
    .quad 0x374c8ceb888459d7
    .quad 0xc8a9fe9bcb54a5b5
    .quad 0x19617f8298e26fec
    .quad 0xca6aa8ae498f890f
    .quad 0xe37df3158f9a9b06
    .quad 0x7a19641429edafbd
    .quad 0x832266ad139119a2
    .quad 0x98c9dab293df14bc
    .quad 0xc02db6b6f3c904fa
    .quad 0xc9260680e20d4221
    .quad 0x2e455297dc54809f
    .quad 0xeea348624f22e9c6
    .quad 0xac20addf6925d8d9
    .quad 0xdedb77e323252575
    .quad 0x6da71c46c904221a
    .quad 0x60d6f6e8ee857b94
    .quad 0x9a590654b786de61
    .quad 0xcf7fb520cd7cf67f
    .quad 0xdffd916a81fb233f
    .quad 0xdd681b24ea0bb644
    .quad 0x733423b5a1935b74
    .quad 0x29ad5a629fdcfd8f
    .quad 0xf3f4f15aa7df6170
    .quad 0x82a845f1add3afb1
    .quad 0x591be4dbe78b3e85
    .quad 0xb1e6d9d6221aee9d
    .quad 0xad672e7f14338816
    .quad 0x3cf225a8c71240c3
    .quad 0x517b5f8c207f7450
    .quad 0xfdbf3b8d833046e4
    .quad 0x6921f0264d43091b
    .quad 0xdbde9449f8dec0a1
    .quad 0x33aec507db82abe8
    .quad 0x153cad18f6c918c4
    .quad 0xfd26a3bfbabca845
    .quad 0xdc78b5235cd2d377
    .quad 0xdbe0bbaa758b50c3
    .quad 0x9e76a57efcc3cd1c
    .quad 0xf168ebc08c929b97
    .quad 0xcdc2d82e58df3953
    .quad 0xe7cabb361c0a4d59
    .quad 0xedfdc3cdad93e932
    .quad 0x9040e7b4620c87dc
    .quad 0xb9a34c14cf96dbeb
    .quad 0x948077323960baa5
    .quad 0x5406c5f0a1819c4a
    .quad 0xbe70c862789acf70
    .quad 0xad5c9a773696d8f6
    .quad 0xd4a2f1ff87c2b44b
    .quad 0x7065b89d58e63c7e
    .quad 0x3931e86c2f434bc6
    .quad 0x078a4435bd2e0059
    .quad 0x272d7b3b6f79311b
    .quad 0xe22f021d7f1026c8
    .quad 0x2f66c585e6a6f992
    .quad 0x87440974deae0b1d
    .quad 0xf9860bfc108a6c4f
    .quad 0x29f583f7eb91db58
    .quad 0xd5cef9243ea72287
    .quad 0xe6cf6f44a0ff83fc
    .quad 0x259e14a8712fc584
    .quad 0xb51c71922fcfff48
    .quad 0x452ae34375b4cc20
    .quad 0xf53eef2ed5f2da8f
    .quad 0x3e34cf4be280d6f4
    .quad 0x31eec1bb1464fa24
    .quad 0xef4664711a891d0d
    .quad 0x7e2e847848619446
    .quad 0x2e5f3390e84b80af
    .quad 0xca64b2eb1e2a33e4
    .quad 0x56b1a3313a953c80
    .quad 0xd496fb367cf5ea81
    .quad 0x6b2c35c7070beb9f
    .quad 0x6f5f6e6904a8aca8
    .quad 0xa6dccebd7fb0652a
    .quad 0x53da4ab6deaed0d2
    .quad 0xb28b641f62d0190a
    .quad 0x9aad20ebb53ad279
    .quad 0x8a59a996edf998cc
    .quad 0xa655bf3f7cbafcd0
    .quad 0x3a5da2fe168e4756
    .quad 0x0448cbbc4e7306b8
    .quad 0x48c0c52444210871
    .quad 0x97e7079cf1429905
    .quad 0xadd42e8122d774bb
    .quad 0x0e11885748560764
    .quad 0x9f4dad43499cf716
    .quad 0xb3e0421f7ee2bb8d
    .quad 0x5e159e321e507ddc
    .quad 0x6eb2d12ed119bcae
    .quad 0x9e80ed38a0442440
    .quad 0x415512f8fecb8a0e
    .quad 0xb76ca8decb78e6e2
    .quad 0x1cab393caa7d9cff
    .quad 0x472b4c0c682e3ab9
    .quad 0x0a5677ca0566ab7e
    .quad 0xb105f34ecbd6576d
    .quad 0x8860377beba4fe1b
    .quad 0x968af6e964fd1717
    .quad 0xf89c7cb28247a26d
    .quad 0xde8cb4bdfdc169ef
    .quad 0x5a93078dc063d74c
    .quad 0x7b7d79669e6a86f6
    .quad 0xf0b0369f117989fc
    .quad 0xb64450b4a1ecbc4e
    .quad 0xbb39efe9f5dd79ad
    .quad 0xed1806a7cfac8f08
    .quad 0xbfe4d9ee8537a0e1
    .quad 0xad543e3fd008ee43
    .quad 0xf28af42a154e7962
    .quad 0x98cd081456ea1180
    .quad 0x2d04bd0d9b91183d
    .quad 0x7ccd6ea226d2ff05
    .quad 0x56b617580f3cdea2
    .quad 0x4fe0068f75111c6c
    .quad 0x27b4719cad2b1639
    .quad 0x289575498d25cf4a
    .quad 0x4bfcd08f8090a687
    .quad 0x837c83aca7857cf4
    .quad 0x91a21be3630b486f
    .quad 0x1d3bd745c648727d
    .quad 0x4b9bd71a88e24991
    .quad 0xa1d6aee754c9496e
    .quad 0x3ff076bda104bca4
    .quad 0xbe4d2097c1451b63
    .quad 0x5b846f81d1658a08
    .quad 0x16a4ba73c729b819
    .quad 0x5a673c8e69037d6c
    .quad 0x5e65a94011e0b00a
    .quad 0x74d91549d92fa6b1
    .quad 0xefadefdd9c439355
    .quad 0xb7da9f15e222367f
    .quad 0x3edda2d04b0fb67b
    .quad 0x36cd73ecfe16b1c5
    .quad 0x844a18224b9bae8a
    .quad 0x675b5d5c613e6bd2
    .quad 0x13dce6da2a910c29
    .quad 0x802893c3c99146d8
    .quad 0x1cbac46171eefe55
    .quad 0x1c59f88a4d813e8c
    .quad 0x2e4ced186668e70f
    .quad 0x86efe0e07fbe5562
    .quad 0x631ba2869f883af1
    .quad 0xd1735d6e3d0d52d4
    .quad 0x0b01111c62e02a14
    .quad 0x3a86a44cbff2f9c4
    .quad 0x5e88673410286102
    .quad 0xd1e5ecea5fa115ba
    .quad 0x9bee72cf766546c5
    .quad 0x0bac041bfbfcaffa
    .quad 0xe059a595d181b679
    .quad 0x2b6783634b7804af
    .quad 0xd48812aa995a23ff
    .quad 0x82355dac22126528
    .quad 0xe5c03f5f7a0ae81e
    .quad 0x20045b5a100b90dc
    .quad 0x63a5c6bf95b699af
    .quad 0xd99975a10b490c47
    .quad 0xe13c72c780c2e637
    .quad 0x26ddf128a05a7ead
    .quad 0x7a8eede0739c3906
    .quad 0x1289571a9e97f9ab
    .quad 0x8080b295f5464989
    .quad 0xff971afcdd4a9518
    .quad 0x6b0398d798e3b604
    .quad 0x5940f70de8b3beed
    .quad 0xfc2f1236d253a180
    .quad 0x85f7e5ce486e1610
    .quad 0x40e5e475ebfe500a
    .quad 0xc1c8de0e25a3e25a
    .quad 0x4256945c63eb7e98
    .quad 0x7c73916066376413
    .quad 0x676941d1cda6e00c
    .quad 0x337bdb2bba49d45f
    .quad 0xc3ed2cefb7a66b24
    .quad 0x74deb9a64311294b
    .quad 0xf0b0f1eee1691114
    .quad 0xf47387d6a5ff618c
    .quad 0x871dd479b566d06a

.section .data.core_1_el3_root__data_shared_segment_1_1332
.global core_1_el3_root__data_shared_segment_1_1332
core_1_el3_root__data_shared_segment_1_1332:
    .quad 0xb28d75bd17e1f054
    .quad 0x67e2a9bf2ffe334f
    .quad 0xc4a9a75fe29dd0b5
    .quad 0x5444f41e90ef1615
    .quad 0x2a4c29a2a7f90026
    .quad 0x691a12ea8735f6a6
    .quad 0xb2522012b002d274
    .quad 0xb2e66c14388dd719
    .quad 0x0210bfd854d2bff5
    .quad 0xd28687d7e2253888
    .quad 0x5540d2f6567c2051
    .quad 0x983d8b88a41c1d65
    .quad 0x257c0186ad9e1d50
    .quad 0x2af1b75842144172
    .quad 0x8c038e093aaf6e8e
    .quad 0xaf2b5258508b9853
    .quad 0xe74244389e663bc0
    .quad 0xa1ced8e50ac9a738
    .quad 0xe191a28a9b288072
    .quad 0xc381e2ab452f2302
    .quad 0xbae719fe02f89982
    .quad 0xa4116d0e90c1fe32
    .quad 0x1493d7f4f5262d05
    .quad 0x0d4d61506dfd5e49
    .quad 0xfaf6f437fcd91e91
    .quad 0xfb4dc68e5a487dfd
    .quad 0x6b7d317fe246a875
    .quad 0xce1330b3d32b5f6d
    .quad 0xbd593dc349fe93a8
    .quad 0x2ba35385cb9b90e7
    .quad 0x50c37ba3846456a1
    .quad 0x8abca89249eee703
    .quad 0xe244268877c918f7
    .quad 0xc7f3ebe86c6036ac
    .quad 0x7b78eafc6adf7744
    .quad 0x28e7d210f16ea605
    .quad 0xc7d2afe190cad2f2
    .quad 0x30474f99ecf027bc
    .quad 0x45ac52ea2e48c1f0
    .quad 0x282768af9f842a2a
    .quad 0xb46addbde7daf2da
    .quad 0xbd10dacb194741b2
    .quad 0x0a228882b438c1de
    .quad 0x32644dd63f07939d
    .quad 0x8e82f054d7c82582
    .quad 0x73bc943f1a511e3a
    .quad 0xb35b2627995d1506
    .quad 0x449d65b8d446e864
    .quad 0xcfff2aef3d10ef89
    .quad 0xc59fe837d52c585e
    .quad 0x406ea468a66e0918
    .quad 0x7454d3769a662de5
    .quad 0x2b22ceff483299b1
    .quad 0x6b16c6b987b73efa
    .quad 0x87eeb46cd260406c
    .quad 0x9855eb0303f020ed
    .quad 0xe7ab15ca865d0f1a
    .quad 0x95daa39dc31b75f9
    .quad 0x9ae0b4ed8416330a
    .quad 0x11a3e9d4a4a1772b
    .quad 0xe705736a2eafeeae
    .quad 0xf6c861a5bd08a03b
    .quad 0x8cc51493c8662af1
    .quad 0xe903857770dc8609
    .quad 0xb77717a9cd481b58
    .quad 0xbf5a4c5d8da76a23
    .quad 0x6306d442ad70d2ee
    .quad 0x7918032bf6ff9edf
    .quad 0xbe863b1faa9e7b37
    .quad 0x987080bf46580e36
    .quad 0x62e6d5bcd199b213
    .quad 0x93519576c50eea25
    .quad 0x329b5f6507c9ba7a
    .quad 0x3fcc6b18f9e17ad9
    .quad 0x059b91ca0f1dea18
    .quad 0xcba2931160ce7a11
    .quad 0x3e9ffba52e61acc2
    .quad 0x4b609f5b27fefcb7
    .quad 0xc1ce61872e7ba3a5
    .quad 0x4e0900ccd8c8ca77
    .quad 0xc606c1741224c283
    .quad 0xbf521dd2b9ff00dc
    .quad 0x4cbf66c8deb92437
    .quad 0xbe0f56329957ec67
    .quad 0x55f76d04fa338c51
    .quad 0x1db15d3f852a1873
    .quad 0xdde6a2c2243c2336
    .quad 0x0f78a4494f82df63
    .quad 0x7050c2c2c83a2295
    .quad 0xd955b9b4eb9e24d3
    .quad 0xd1219fdb549d0e47
    .quad 0xe93b3d640cb7b1fc
    .quad 0x111871ad4cd3e264
    .quad 0xb78fe7dc0a16b3e3
    .quad 0x88902af303916773
    .quad 0xa91982fac3335731
    .quad 0x772bdb475d7320ec
    .quad 0xdd11b4e5761b8f12
    .quad 0x004f35c10b8dffed
    .quad 0xcee380f20d5275b6
    .quad 0xd9586eac85b093be
    .quad 0x22d93a59516458fe
    .quad 0x09c03ea0927bd820
    .quad 0x582565c96b824be2
    .quad 0xf4dffbf3b8ac6ed6
    .quad 0x33a7c4a3517d348c
    .quad 0xfeaca4a9e791473c
    .quad 0x797aaf3f5f68a3a9
    .quad 0x7e3287ba832e5594
    .quad 0xe5be9fbd3ccb03ec
    .quad 0x3b6cb4352cede951
    .quad 0x4747d91c3fca4aa7
    .quad 0x0b4ab8786d97a4c8
    .quad 0xf3ba5ff092781389
    .quad 0x0511aac5157659a0
    .quad 0x7e29a1171c62da2b
    .quad 0x1c6879b8cb88864e
    .quad 0xc8c6fea4f226438d
    .quad 0xe48da908d4621261
    .quad 0x5cd4f66a814c75e1
    .quad 0xa3a3dc41a3b0924a
    .quad 0xd721262fb698ced7
    .quad 0x083f4430b0d48401
    .quad 0x1313ed1a005ff38b
    .quad 0x268d86ef6cb45a46
    .quad 0x33b65865a2225ae9
    .quad 0xa03de07127c7242e
    .quad 0xdf367102b5f121b1
    .quad 0x852d030327dfcc7a
    .quad 0xe2eb1844b23219ff
    .quad 0x4637147277675e40
    .quad 0x25b04452c4e17744
    .quad 0x6f88e98dac448c26
    .quad 0xc513ada53788fc15
    .quad 0xee6a3d52967d6833
    .quad 0xef748a2583e246dd
    .quad 0x69ae27c0276a5e23
    .quad 0x515f9e83d304651c
    .quad 0x3975518be5f9feca
    .quad 0x01c87e177b06e5e9
    .quad 0x049ca881a0ce9cc0
    .quad 0x279a7cd3319602b0
    .quad 0x99752d28e1dc733b
    .quad 0x815bb17bc511d4c9
    .quad 0x517cf399b2c97fd5
    .quad 0x9c3591a7621faf58
    .quad 0x82c4699a0de718fe
    .quad 0x951788d48fc851b0
    .quad 0x100c736f5b7eb863
    .quad 0x93978ec787cdced7
    .quad 0x7103b1f43fa05018
    .quad 0x14c1762b389d6256
    .quad 0x9b883d172fbeb334
    .quad 0x47db330bd8aca4a2
    .quad 0x0a69dc1148f312f3
    .quad 0x83d939a85049ba25
    .quad 0x1626e4cdcbf59579
    .quad 0xdb1a997b9d9c0509
    .quad 0xe57b02bff97c8eb3
    .quad 0xa625a5dcaea14c8a
    .quad 0xfccb29ac25e3e82a
    .quad 0x1779b5c9ef7fdb9e
    .quad 0xa9498f4bf12f97fd
    .quad 0xa148a5e4b2ce90fe
    .quad 0x07eb17b0f2a0e966
    .quad 0x571c0ae50eb1fc8d
    .quad 0x04fd6fffc8d47a60
    .quad 0x3e462aeb36e0dc07
    .quad 0xc2479935ff72d6ae
    .quad 0xac01d119d78cdef4
    .quad 0xad552d43406676c8
    .quad 0x12447b2926e45dfa
    .quad 0x9e9ad4f347af0e53
    .quad 0x5c6ff6f9f6c721b3
    .quad 0x145487828cd5848b
    .quad 0x0a35b87ba8c8d866
    .quad 0x755796288776729f
    .quad 0x8e3ecf881c017b77
    .quad 0x55290c86500aedc4
    .quad 0xdbf18160e1ec7fb3
    .quad 0x900e07ac093286ed
    .quad 0xd2a97465335c4e0e
    .quad 0xbff104fa05cdbc72
    .quad 0xcebaa7a77b7fea21
    .quad 0x3465f9dbae5eb0dc
    .quad 0x8496dc8412108b50
    .quad 0x87dd7e72082690ab
    .quad 0xc2395265d9da4473
    .quad 0x1e2587ef08a7e0ab
    .quad 0x6a8e994b4fc93340
    .quad 0x38fff072a4c8ef8a
    .quad 0xda392e9c6376f6c3
    .quad 0xbefe51c71bba2652
    .quad 0x9a0a81f12e9056ba
    .quad 0x3457285cb5044eba
    .quad 0x9fa5ba3584abc74c
    .quad 0x47f7e3b1ff7e9790
    .quad 0x96db0eb29c2b890a
    .quad 0xb4416a532150c147
    .quad 0x1db899205d38cc80
    .quad 0xd9efe3dc7b10cdc2
    .quad 0x10b15c8fb91a6d08
    .quad 0xe729fb358caf402b
    .quad 0xe6602ed3c0e73f35
    .quad 0x1df43747ef24e638
    .quad 0x9571bb7142d43830
    .quad 0xbd6aecdea75289e3
    .quad 0xa43f44fb06d534ea
    .quad 0x061f302617eb2200
    .quad 0xb87fd2eb68f95141
    .quad 0x864791700b621674
    .quad 0x291a69485197d595
    .quad 0xe635ad65f8828738
    .quad 0x2a7915954fb441e8
    .quad 0x741d31a1bfdd359d
    .quad 0x7c2ab40990e73bd8
    .quad 0xab86e76a5baf8cbd
    .quad 0x37e61cffd5f6f4dd
    .quad 0x5cb60a2135baa0fb
    .quad 0xc049c33a3e588e35
    .quad 0xe300552a4ddc4322
    .quad 0xdcf2df7f31c07556
    .quad 0xedc235db26d22b09
    .quad 0xbc3bbbce4d71c595
    .quad 0x0fac9acdaa5d67e7
    .quad 0x5e55b7d8b2fedb8b
    .quad 0x22bba454fe60c0c4
    .quad 0x1d4586ff2dd9f5e0
    .quad 0xeaeab13868b0dad2
    .quad 0x38599238118f04c9
    .quad 0xb8fa019188377e6d
    .quad 0x6a15c0e978707be4
    .quad 0x5d3409596320b670
    .quad 0x4418ebc32779a186
    .quad 0x2e3a7e22f61e537a
    .quad 0x6322ef7aa7a58af4
    .quad 0x7ac9e32024c493f5
    .quad 0x2104e3140c305438
    .quad 0xfacd4fd259dd7515
    .quad 0x2f6bdb9eed1bd40a
    .quad 0x3cf5cee6a295e942
    .quad 0x18b15d078ce26850
    .quad 0x0d8baa6391ce7075
    .quad 0xc545135f8815ff5a
    .quad 0x633b09771e22a5b3
    .quad 0x0ac70ccb1bcbc6a1
    .quad 0x4c8749e91f839bd0
    .quad 0x9d811a75bda21658
    .quad 0x0b6eb829230018ca
    .quad 0x77fd97fb1a1ac9e2
    .quad 0x39c00757d213c16f
    .quad 0x45c4e9a3f9bcbb47
    .quad 0x3ec3ba8b0459d6d4
    .quad 0x1e3c9abf7dff12e2
    .quad 0xf317afb803f82ccd
    .quad 0x9b1e3aa0e41e74f6
    .quad 0x7dcd7c0710cd59dd
    .quad 0x3c006d15acc6aab1
    .quad 0x7fe7b8492f023ad2
    .quad 0x0b433fbae63c1665
    .quad 0x2413b970c048afb3
    .quad 0xa78b39dd0a9d0bde
    .quad 0x27259c4061fa7e65
    .quad 0x739cef9df6d91069
    .quad 0x4368352b837c3281
    .quad 0x7ef32594c429e8a1
    .quad 0xc500d633344bbc96
    .quad 0x6ccd0b51f49766bf
    .quad 0xdf76d0a84d7ee7ea
    .quad 0x99f5f9840afa4048
    .quad 0xb9e91a608cc8a988
    .quad 0x6ead506a076f22bd
    .quad 0x8d6d9bc66432dd92
    .quad 0x336273ce5dc493f1
    .quad 0x53042efb56fc6f28
    .quad 0xd84d1d189aeef5a4
    .quad 0x23477fe2ea5a06ab
    .quad 0x5898a1329d8d8621
    .quad 0xfe899f286a003f00
    .quad 0x1030b6616ba6024f
    .quad 0x32097d551c2bfdab
    .quad 0xca470e1d118c3302
    .quad 0x5e9570d6071b5e05
    .quad 0x20af146db37ddebf
    .quad 0xd98f3fe7fd12dfbc
    .quad 0x1979cebbdcfa52fe
    .quad 0x46d51230314809cc
    .quad 0x36ccca7f72ec49bf
    .quad 0x4f4db6ec4b44977a
    .quad 0x7194de14c4692ab0
    .quad 0x10fd8d9680bd4696
    .quad 0xabdf0c195cd94976
    .quad 0xb41a70abf07f9c20
    .quad 0xe3c65b149f25fc27
    .quad 0x76c34387fe6b5b55
    .quad 0x12cee580b018e472
    .quad 0x39af615f3bc84057
    .quad 0xc816199d5e41e4ea
    .quad 0xa871b6d2109e0422
    .quad 0x434bd7753f3ebd72
    .quad 0x9da38a83de245792
    .quad 0x958a3385e5434a19
    .quad 0x4a8c107415ebc624
    .quad 0x2072bdc5b0d5781c
    .quad 0xbf9c9f538968be4c
    .quad 0x34da7091a23e88bc
    .quad 0x7c3b5eb252885022
    .quad 0x69c257e396917b1c
    .quad 0x480f368e89febee2
    .quad 0x532873449408bebb
    .quad 0x0e43f7daec937e3e
    .quad 0x3b013ed753f19f8d
    .quad 0x904faac6b6a86fd8
    .quad 0x24b791b96c062412
    .quad 0x0f2fd63b0cbba338
    .quad 0x776983f492b46d20
    .quad 0x5c661e18cfe49331
    .quad 0xed3c379a831d1e61
    .quad 0x2f3cd09dd77bf29c
    .quad 0x271bc61a5117ae93
    .quad 0x6ea2cc972fa07d69
    .quad 0xdc2d81bc4c350490
    .quad 0x646345e1281800ae
    .quad 0xb9a2d4ae00e71152
    .quad 0x60c30f23604d910b
    .quad 0x2f385a2a9a38d1ee
    .quad 0x2e152e94b70dc54b
    .quad 0x52839228cb96674a
    .quad 0x9f5ed6d6919fbb5b
    .quad 0x4536261bba9aaa29
    .quad 0xa1be1d0742504119
    .quad 0x83f37f858c0026d2
    .quad 0xff98d9f5f3f330e7
    .quad 0x57461b47f489de75
    .quad 0x3eca39f12940f254
    .quad 0x697452ab1ecb797e
    .quad 0x19653a845b803d94
    .quad 0xd0d1698435fa9e41
    .quad 0xe4448fbf3418cba4
    .quad 0x46c343d0a0d8aa56
    .quad 0x52b65ed5be145aac
    .quad 0x2d8e22c35da785c0
    .quad 0x8ffef00af2a13ace
    .quad 0x0fa2cf933cc3eeb0
    .quad 0x22c7f7a380a145d6
    .quad 0xe21df14648526c65
    .quad 0x5307c2d63f775b00
    .quad 0x0840a82263a9fc48
    .quad 0x11ff79ac0c73625f
    .quad 0xe711d3dacb8dced0
    .quad 0xb47f10934cd95b0c
    .quad 0x88d1ad1b28f1804d
    .quad 0xa88eaf8c0a797b33
    .quad 0xf8b0317422fa194c
    .quad 0xb669bac866453fa5
    .quad 0x469f8e84b88f83c7
    .quad 0x22644a744f8d59be
    .quad 0x846201dd0303b648
    .quad 0xf30282befb41b194
    .quad 0xc9b3c346608cfa77
    .quad 0xcbcd61e91a14a86b
    .quad 0x4837347e4da5e2bf
    .quad 0xf13c2619502be38c
    .quad 0x94d236c310c4a4fa
    .quad 0xef3aba6f05fe2837
    .quad 0xde79da5065b37e2c
    .quad 0x080dd5c208446594
    .quad 0x7122134a0b8fad76
    .quad 0x794b4d67c931ecb2
    .quad 0x575511a1af843698
    .quad 0xdac5bb316d4df635
    .quad 0xd15ae3cc32077c11
    .quad 0x44edb16129086f2b
    .quad 0xa008a1303ea99ce5
    .quad 0x08ca96b66a615fca
    .quad 0x3bbace923bb3fb57
    .quad 0x67032f9345d5ac3f
    .quad 0xd1e4256f0e8f6bbc
    .quad 0xa14cd35e0d8fba11
    .quad 0x923513301e989112
    .quad 0x5e3820212bd92a0d
    .quad 0xd4295e03ef3a2f5d
    .quad 0x0005269ed5a34996
    .quad 0x4a02b9bc6c762021
    .quad 0x75722175984fe62e
    .quad 0x508c9722f9653185
    .quad 0x8b626c463f28fd51
    .quad 0xc0a1160d3648a405
    .quad 0x50b9bac27ab3825a
    .quad 0xe68560d6c77f93d6
    .quad 0x5e2b2bf8b152faca
    .quad 0xbf6f25b2e77f047a
    .quad 0x834ff2b56c57869e
    .quad 0xc8bfb8c4d03e3c6a
    .quad 0xc5635093c610a5f5
    .quad 0xdd5b1e22afddba5a
    .word 0x511edeaa
mem1993:
    .quad 0xf27df4cf4a383175
    .quad 0x85d19faa83c67bbc
    .quad 0x3e9e7031b71e95ee
    .quad 0x30263550a1857ca1
    .quad 0x820d0be34c250272
    .quad 0x7026df6391db2295
    .quad 0x001200798b774f4e
    .quad 0x9c7ff88e73ee83d6
    .quad 0x4a6439f30af92e46
    .quad 0xe49f8309c172ac32
    .quad 0xd1a5b24a21d512f9
    .quad 0x39bf37ef8468df7f
    .quad 0xd5a1c9453f8a20a0
    .quad 0x24808da298cf4601
    .quad 0x240b1b1ac0bc29ab
    .quad 0xa5384f4b648ea3a7
    .quad 0x7f949296562ec9fb
    .quad 0xe49d29179d218a6a
    .quad 0x911abdf84fd287fa
    .quad 0xd8e4f7b97804e552
    .quad 0x89c0d14c08f91b2e
    .quad 0x6205c8c8e7959fb0
    .quad 0xb0a95b781c2b715d
    .quad 0x717fc1ebb7e3bee4
    .quad 0xbc31b7096d1f2752
    .quad 0xe82eae12327e885c
    .quad 0x5c29c3cfdfc86123
    .quad 0x03bf85428ba4dafc
    .quad 0xeb27c0f2526b5e06
    .quad 0x675603b71ec3fea1
    .quad 0xc93d33cc93c53d3c
    .quad 0x6a6295bb406183c1
    .quad 0xf88253236ad3c8c7
    .quad 0x3a15c06f777581a0
    .quad 0xe96bd1e002ee67a6
    .quad 0xc72d660dc72ac6ac
    .quad 0xff540e61bc22e972
    .quad 0x12263f76e4d73c02
    .quad 0xee738957e1889db6
    .quad 0x1df1e37a9f0bcaf5
    .quad 0x18ce84781b26e1fc
    .quad 0x061321814afe2c36
    .quad 0xc0db3245af6637e9
    .quad 0x0f971c0069dde85b
    .quad 0x41f34f303ec2dfd5
    .quad 0xb4fae4cda61d0a31
    .quad 0x3e06507b3cf6984a
    .quad 0x2968d3d1c271747f
    .quad 0x7a67703af72cfedb
    .quad 0x245fa7678b525ec6
    .quad 0x8a14f282154342ef
    .quad 0x6dc89bf8c8d0d63d
    .quad 0x30d091b542420dc1
    .quad 0x0b015afc5fc12b1e
    .quad 0x052f48023147303b
    .quad 0x4cf30a5e5951e2e1
    .quad 0x33659b40e0e5c508
    .quad 0xfc6ed74f0f3ef33d
    .quad 0x4703cbbeced122c5
    .quad 0x90905c827cba1189
    .quad 0x153cd7c5a6d1ebd1
    .quad 0x023425695b8fb2b7
    .quad 0x7f5de27295b4250a
    .quad 0x28b390236a155852
    .quad 0x7b7492a66e036818
    .quad 0x8bba32900ccd46bc
    .quad 0xd5ab270ca6c36084
    .quad 0x048b7c3f4f8ed18a
    .quad 0x0367ac35bbf10bc6
    .quad 0x196071eef9dd6637
    .quad 0xde7f5750a97bad27
    .quad 0x461986b7e79c97c1
    .quad 0x0100ea1976d3286c
    .quad 0x0fbe105770fb3f3a
    .quad 0xeb89f572888dcfa8
    .quad 0x75d16729e045a83b
    .quad 0x14f1d309d4b18751
    .quad 0xc6ceffbecfb8ff45
    .quad 0xcde16b14103ae348
    .quad 0x681a043f876f45cf
    .quad 0xced3dda81c041a3b
    .word 0x3fac744b
mem2008:
    .quad 0x6a18b05f52d7f84c
    .quad 0x706b58da37104768
    .quad 0xcf27bd333ebda2bb
    .quad 0x5d6293475e4883d1
    .quad 0xbccbd079085e84fb
    .quad 0x6efe929e7aac9738
    .quad 0x407425fa5d128023
    .quad 0xeb62b078fb135f99
    .quad 0xe8d91c0a97079080
    .quad 0x938a48a67abff8c8
    .quad 0x6dbfd4495be03a81
    .quad 0x27f486c5599b4434
    .quad 0x7e4f8b63e91cd76b
    .quad 0xad8bc8c52c6f79b7
    .quad 0x64c5ef6bf1f1653c
    .quad 0x58fafc9429c4f3af
    .quad 0x547cd4722ec6ccd3
    .quad 0xeefd97c97d8ceca0
    .quad 0xc9d1a8aa34a4755a
    .quad 0xc4f0f25ef103ee40
    .quad 0xab421cece4478047
    .quad 0xda74e1297fce1897
    .quad 0x40f9e364efd94b00
    .quad 0x1c1b4f554950aa51
    .quad 0xb07ef0bf59447740
    .quad 0xaca81abde9862ec0
    .quad 0x51b86bab5e74d7fc
    .quad 0x43c9b2a93dcbc3d4
    .quad 0xf165178233f331f3
    .byte 0x79
mem2009:
    .quad 0x9b981e6f4f2a126b
    .quad 0xcd9cd9761c1a8707
    .quad 0x777e57d075996007
    .quad 0xd8a153bf72619358
    .word 0x132c29b5
    .byte 0x8e
    .byte 0xd0
    .byte 0x8e

.section .data.cross_core_data_segment_1299
.global cross_core_data_segment_1299
cross_core_data_segment_1299:
.org 0x4e8
.align 3
label_4901_end_boot_barrier_barrier_vector_mem1985__core_1_el3_root:
    .word 0x00000003  // 4 bytes

.org 0x780
.align 3
label_4922_end_test_barrier_barrier_vector_mem2017__core_1_el3_root:
    .word 0x00000003  // 4 bytes



.section .data.core_1_el3_root__data_preserve_segment_0_1333
.global core_1_el3_root__data_preserve_segment_0_1333
core_1_el3_root__data_preserve_segment_0_1333:
.org 0x84c
.align 2
mem1995:
    .word 0x00001234  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0x9b4
.align 1
mem2013:
    .word 0x00000456  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0xb5c
.align 2
mem1994:
    .word 0x00000456  // 4 bytes
    .word 0x00000000  // 4 bytes



.section .data.core_1_el3_root__data_preserve_segment_1_1334
.global core_1_el3_root__data_preserve_segment_1_1334
core_1_el3_root__data_preserve_segment_1_1334:
.org 0x530
.align 1
mem1996:
    .word 0x00005678  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0x573
.align 0
mem2016:
    .word 0x00100000  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0x721
.align 0
core_1_el3_root__exception_callback_LOWER_A64_SYNC_mem1982:
    .word 0x00000000  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0x7a4
.align 2
mem2015:
    .word 0x00005678  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0x8c0
.align 2
mem2014:
    .word 0x00001234  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0x934
.align 2
core_1_el3_root__exception_callback_LOWER_A64_SYNC_mem1981:
    .word 0x00000000  // 4 bytes
    .word 0x00000000  // 4 bytes

.org 0xe88
.align 2
mem1997:
    .word 0x00020100  // 4 bytes
    .word 0x00000100  // 4 bytes


// No uninitialized data on core_1_el3_root__stack_segment_1335 data segment. skipping .data section


.section .data.core_1_el1_ns__data_shared_segment_0_1342
.global core_1_el1_ns__data_shared_segment_0_1342
core_1_el1_ns__data_shared_segment_0_1342:
    .quad 0x247986bc0d87b80c
    .quad 0x5e13979792614a42
    .quad 0x67c6c168eb8edee8
    .quad 0xaa0f9becc1fe84f3
    .quad 0x58ab6a5fc7cb835b
    .quad 0x8e5a1813032661f9
    .quad 0x95f0a3cf07482122
    .quad 0x1efe0ec17f589981
    .quad 0x4614a4bb85823c65
    .quad 0x7a5c2604ba901e52
    .quad 0xeeee43b2852ede9b
    .quad 0x8218f944982ed192
    .quad 0xd10a1b74dbd10fd6
    .quad 0xd5598e670d3ba367
    .quad 0x56d91e5c515c4773
    .quad 0xaee02dfed3da5912
    .quad 0xe106bfeb7db5936e
    .quad 0xb09a6dd7459f37ce
    .quad 0xaaaaeda3bcb23497
    .quad 0x81c47b0dc312c5c6
    .quad 0x180555c501712816
    .quad 0xd0dd21b34d71c805
    .quad 0xaa723c19b67817b0
    .quad 0x87ca20923ff014f7
    .quad 0xc1697901463198fe
    .quad 0x08c98d89f92276d4
    .quad 0xa69740846e1b1360
    .quad 0xaa682dc29a71bb75
    .quad 0x3e4e4a4051969394
    .quad 0x021bf9d123360375
    .quad 0x4327c3dc9010255c
    .quad 0xf975510c24927bfd
    .quad 0x4c4396f97c3e3a8f
    .quad 0xb9ab5f77ada9c153
    .quad 0xb6b8dd866be390eb
    .quad 0xaa185a1b7fcd2857
    .quad 0xcbbc27a3771c289a
    .quad 0x6c179f0ac0412862
    .quad 0x5d28c2042877f265
    .quad 0x5aa60af65b7680be
    .quad 0x1d3568d18c47626b
    .quad 0x8cb435d196d46b7f
    .quad 0xbfcd908674737665
    .quad 0x353a0cb0ac273608
    .quad 0x706fbbaa7eb3ce00
    .quad 0xa47344e6bd861ece
    .quad 0xa015ad9c14e44737
    .quad 0x1a2f6fd2da001b28
    .quad 0xf8694c42b0ba7683
    .quad 0x2864ee6113d9e549
    .quad 0x3099a5ce7ed55537
    .quad 0xe13916eafb02b887
    .quad 0xf018f9ead8498767
    .quad 0x72e9c1f11943b3f5
    .quad 0x53a07c32d8c76e09
    .quad 0x8717f2e7e8d1f225
    .quad 0x054663bf4251c1d7
    .quad 0xc00e075f618fea41
    .quad 0xe2d4888af22af29b
    .quad 0x8b76143743be914c
    .quad 0xc8593242a6e72309
    .quad 0x84a36c9ae286352f
    .quad 0xba55fea5272acd7b
    .quad 0xa15889dbf52ef3fb
    .quad 0x3bde093dfbe4116c
    .quad 0x201cfe5427953d0f
    .quad 0x9cf0926de1d94bbc
    .quad 0xba1ec2e1ec421600
    .quad 0xa9289c9dcc69e62f
    .quad 0xcd974b969274c12a
    .quad 0xe21c2a080999d023
    .quad 0xec85f4767b1a36a2
    .quad 0x967788effa3f2485
    .quad 0xf24ae6a4b88d855e
    .quad 0x66f43c07f3d1e800
    .quad 0x77953e7802a84db2
    .quad 0xf35c4cf3b8fdd3bd
    .quad 0xdb9761c6e3ff6bb1
    .quad 0x318616c3f319ea60
    .quad 0xcd0cc9a78b518cf2
    .quad 0x3106c4d8f137c196
    .quad 0xe1b5224188a35b49
    .quad 0x87fbb51c54d99028
    .quad 0xaf6bc022488aec48
    .quad 0xab8cd944bf9d7dcf
    .quad 0xedcd8694674bb906
    .quad 0x3654e1c7c1d52748
    .quad 0xa81775dc2b80c9c3
    .quad 0x1eb305862e702e52
    .quad 0x8296af619e82ccef
    .quad 0x2da9b6a67815248d
    .quad 0x8a634144ab06fcd4
    .quad 0x41e1d7d5d689d9cb
    .quad 0x5e5f8384a095c927
    .quad 0xba032a59feb34a3f
    .quad 0xa9d4018c5696068c
    .quad 0x84e3cd619dfc311f
    .quad 0x565aff9a5eb69865
    .quad 0x7982dd97ed239fbe
    .quad 0x4f520987e1d634de
    .quad 0x62d6d2ae272a1390
    .quad 0xa2506b5e6c0a5317
    .quad 0x72b9a03b4e9ede6f
    .quad 0x16d52e3b1708e9d1
    .quad 0xb839c15da1749d12
    .quad 0xac40bb03f00af97c
    .quad 0x36193cbeff2391c0
    .quad 0x35c78b90f37ac7a2
    .quad 0x311c36133cf0f008
    .quad 0x5cd6a14dfcf252b2
    .quad 0x04aaec5af16c3dcf
    .quad 0xddc7a7ee41577460
    .quad 0x927da12ded71d567
    .quad 0xf10db377e8c06252
    .quad 0x32d0b8aaf86359b8
    .quad 0x5146541a96b64107
    .quad 0xeb946923d60dee18
    .quad 0x2ae3769d51395206
    .quad 0x8c5cd674cdb75e04
    .quad 0x09a7aac9ce9021ea
    .quad 0x395071d2d1b94c1b
    .quad 0xe4db498285a37162
    .quad 0xe46937b8b32e764f
    .quad 0x5743c43e13de5783
    .quad 0x2ef4d37f12c36d65
    .quad 0x534a5b9c9fd8fe57
    .quad 0xffdbee5a505f8bc6
    .quad 0x8cfab2105d79a36c
    .quad 0xdf59052da4ecf787
    .quad 0xfb3004f26aeb9b57
    .quad 0xd442066c81a6fcea
    .quad 0x410aba9e52656a9c
    .quad 0xb7e32976a762c6e4
    .quad 0xe9445a4038e5ba0c
    .quad 0x5b44a01621364d3b
    .quad 0xda3eb78b3caff508
    .quad 0x8ab83c32d05e6a85
    .quad 0x3143417ab190a4fd
    .quad 0x4100b967d4df95a8
    .quad 0xc69043872f40b149
    .quad 0xb96714337ce7e82c
    .quad 0x4e64f9802b87128d
    .quad 0x93c3944266fd8480
    .quad 0x222661408702b258
    .quad 0x439954e9013010e5
    .quad 0xa40d04f6d8b5e291
    .quad 0x6265d831b0cd8c1d
    .quad 0x053d478d486e5679
    .quad 0x57c0f19954e60fe9
    .quad 0x92fb9af4d737501b
    .quad 0x73bcb6d017f237cd
    .quad 0x174cb288e39d9ae5
    .quad 0xf4981955d8e011b7
    .quad 0x5f3a2a92b2a1b8a4
    .quad 0x5eed922cab427054
    .quad 0x3d9fe45302be01a8
    .quad 0x12983d7bb5accb9a
    .quad 0x0b526e8d1ae2ab23
    .quad 0x601fe5c8bfda1416
    .quad 0xb0c6a6585e9f562c
    .quad 0xa600084fc7316021
    .quad 0x61b825d553910330
    .quad 0x0066b469d46a4088
    .quad 0x634251e88b2dc4c5
    .quad 0x5039e6e5b8137277
    .quad 0x92c1607aea4941d8
    .quad 0x670df3a934de1c0c
    .quad 0x36ef3bf91efb13a3
    .quad 0xc7a62778bee13adb
    .quad 0xd0755ddc3fededb0
    .quad 0x4a7e640e8771a136
    .quad 0xb4fd374e6e0e0617
    .quad 0xb5ab4f84b2613cbe
    .quad 0xc538b99289ef5dcc
    .quad 0x5326cea8ab95045f
    .quad 0xebe825ed4baf1123
    .quad 0x39797d466b7296fb
    .quad 0xa79cf48eb7d2d71b
    .quad 0x843a240aa9bc1e3d
    .quad 0x9b7a0b6396913fbc
    .quad 0xd83f14095d3ad3ac
    .quad 0xbc71ba6be0bb2641
    .quad 0xabf393722cd877e6
    .quad 0x40af7d5d7746e911
    .quad 0x912c5047986f5951
    .quad 0x713c1e6ed7f29c5e
    .quad 0x374dce23cc648bc5
    .quad 0x5a7f2a9ac7d6329c
    .quad 0x8af6f3a32ae3c177
    .quad 0xbe57c79ee23f37b2
    .quad 0x8ee67253887a9c5c
    .quad 0xf5ba2cf7bb3f63de
    .quad 0x96726350572648fb
    .quad 0xcbbeb1e622424b7b
    .quad 0x1db3fb7c713f1352
    .quad 0x4d1e2c06daa21f5f
    .quad 0xd5ed3648a6714d90
    .quad 0x91522681841a58a4
    .quad 0x7dd40d4f46b93ddf
    .quad 0xfafa13850dcc9346
    .quad 0x22b5347ad5deb8a1
    .quad 0xede487a427f51cbe
    .quad 0xe258206540d5cde4
    .quad 0xa20c312d6b0df84d
    .quad 0x5fc3b6c0356d2874
    .quad 0xfdb5ca67efe0396f
    .quad 0x272c81f06bc523b5
    .quad 0x957b05926d7385aa
    .quad 0x6dcaed9463fa936d
    .quad 0x99f1c7df91310631
    .quad 0x2c83766b4d755b56
    .quad 0x34ca7224d8aa325e
    .quad 0x86d80a15c97ad3c5
    .quad 0x6057e8a53c5250db
    .quad 0x751578a9575d5acc
    .quad 0x910061aacfbc76fb
    .quad 0xfc1addfbd4415693
    .quad 0xf5cdf7134c8c357c
    .quad 0x27751fc5972ef6de
    .quad 0xb82212143702396e
    .quad 0xfd47872a3cfdcfb8
    .quad 0x7390d7c272661b6b
    .quad 0xdfc30532e4367d49
    .quad 0xf991b09c327c7e27
    .quad 0x0138a04505038f97
    .quad 0x20fc83aea1d5e711
    .quad 0x99ecb43b5977f688
    .quad 0x4f83ef2fef2af6c2
    .quad 0xd9c6a215c10d6262
    .quad 0x916910995c47bcfa
    .quad 0x630c97e909c67025
    .quad 0x00a3a064e0fab6c2
    .quad 0x6dae4521572ae8eb
    .quad 0xcf14125bc6140552
    .quad 0xf4def56e9e720d69
    .quad 0xabcf8a196cb20300
    .quad 0xa5c3d9c4bb05a282
    .quad 0x09d4d6f8ec7e849e
    .quad 0xc185a13a806eee57
    .quad 0x033e2d1ade641807
    .quad 0x7e6926a5724ed4ca
    .quad 0x96ed9b051e24565c
    .quad 0x8372e16f1616b7c8
    .quad 0xdc3ee509ae095325
    .quad 0x8fcff06e3f525d92
    .quad 0x6f8575be609933e3
    .quad 0x93d6a86d432ee231
    .quad 0xe49e2b96d3e2ab64
    .quad 0xb2dfc7cccb9a60ef
    .quad 0x5cdc6dad8d13fe43
    .quad 0xf233c87a66a33b71
    .quad 0xff1d3fe5a513ca85
    .quad 0x555094d5327ef652
    .quad 0x1219047f23bd319c
    .quad 0xb9d75e99ce0f88cb
    .quad 0xa087f93ae1d5e8c8
    .quad 0xed5f3f99c2b581ac
    .quad 0x343f5ff45660aacc
    .quad 0xfffd75c66873e690
    .quad 0xad73e00ececa48fa
    .quad 0x0c4b26bca356dd49
    .quad 0x45e3c24c2ae1c6a5
    .quad 0x3ad702ae9c8738ff
    .quad 0xd4f1ae0ae6f4d632
    .quad 0x5478e66f4b9f0469
    .quad 0xf71d5a2086709435
    .quad 0x5da6f1ed86aff33f
    .quad 0x03f61e8962cdb6ed
    .quad 0x3f4de34e5c971c1f
    .quad 0x8d9fbbdff793a110
    .quad 0x8e337e133022ac69
    .quad 0xa000e6dda69fe362
    .quad 0xc57b306120e98976
    .quad 0xa97c5d9de7211c81
    .quad 0x43d5fa78cba3f291
    .quad 0xc3cff25046d15820
    .quad 0xfa1b512eccb6ce4b
    .quad 0x23e2eeffd0fc2e3f
    .quad 0x5ae8cd9b7b5588e1
    .quad 0xa8c255d3e894a863
    .quad 0xaabed7e1783ee9cf
    .quad 0x44ea8718499c1357
    .quad 0x6639723d565010f9
    .quad 0xe7474c1c9270048a
    .quad 0xce34e340c313dcb4
    .quad 0x10b271d602ca2485
    .quad 0x713a98a9fb7e5187
    .quad 0x699cf67aa33aa440
    .quad 0xa0bcf65a4a5981ce
    .quad 0x41683fbf8da887e9
    .quad 0xae89cbae726c5035
    .quad 0x5de2792647c88215
    .quad 0x019bb5ebee3478e1
    .quad 0x2f921c2e95161502
    .quad 0x435c1b8ebd40ef23
    .quad 0x91bcae51039453c1
    .quad 0x7ca71da9a717b13a
    .quad 0x9627e8bc6a2bb55f
    .quad 0xfa1854bd650ab4c8
    .quad 0x372a526003b75a6d
    .quad 0xae6ef6ee8b068cc4
    .quad 0x2fc80ebf94d26c40
    .quad 0xbc155698ade4f87c
    .quad 0xc72084b1eab8a954
    .quad 0x8f4e3b44d588f8b8
    .quad 0x89bb0c13d7670fff
    .quad 0x0de78776920cf71a
    .quad 0x2d4d128103c5282b
    .quad 0xb8391cf74b487baf
    .quad 0x6a5b48fe52ec8881
    .quad 0x371da8e61382dab6
    .quad 0xbabcb28d479745f8
    .quad 0xfb156203acb0d653
    .quad 0x6762eb98323e679d
    .quad 0x409fa978e2a66417
    .quad 0x241931959b101732
    .quad 0x5094dec8289a3c79
    .quad 0x58c46f73851e5cfa
    .quad 0x484fbc869f483407
    .quad 0xefa8827a161e52e5
    .quad 0x77d5ff6df17ce372
    .quad 0x06b90eacfe46e82c
    .quad 0x1c250ffdc0dbab95
    .quad 0x779d4eaa2af90da2
    .quad 0xca096bf0628c8640
    .quad 0x68f63c4747c2efea
    .quad 0xaab73d95268f3ab3
    .quad 0x5f94a6ff68b702ee
    .quad 0x1baa96dca1098779
    .quad 0xd89c827fd572162b
    .quad 0x0584c481dffb82e8
    .quad 0x11d33744ff510a54
    .quad 0xabd15dbe6cc1c0e6
    .quad 0xd86343e8367eef8b
    .quad 0x466f63bfe9dc836e
    .quad 0xcae8d13f79eb4622
    .quad 0x8f8617d13d4efeef
    .quad 0xda66471f67a52e7f
    .quad 0x8ade7052933941d7
    .quad 0x198f47bfc0d8ac50
    .quad 0x44c9b7810d2534f2
    .quad 0x2ad22f8b8df1fb47
    .quad 0x248c9da29d48435e
    .quad 0x85b9b27fc2b4046f
    .quad 0x95cef8c005013630
    .quad 0x0d1da6fc5974a66f
    .quad 0x8678f631f2568b06
    .quad 0x461457d0cd848923
    .quad 0xda6b2589e2812594
    .quad 0x9fd3d43f71b87b43
    .quad 0x7ebb7cf66bd1d9b2
    .quad 0xd42f3506d9d402ee
    .quad 0xe82f470cf6399921
    .quad 0x04bde0c8e895c744
    .quad 0xe825154a967702b2
    .quad 0x77d6d308f07ce5f5
    .quad 0xb3682bc396ad0ffb
    .quad 0x180a9052ca9a6117
    .quad 0xf5282ce803bf2426
    .quad 0xca270080406b4b84
    .quad 0x97a93ac8ed6cded4
    .quad 0x5743c101f519555c
    .quad 0x45e1634ae4466bc2
    .quad 0xce9ee813f0752ea4
    .quad 0x220ac0068cfb5354
    .quad 0x0fd01164737b0aa0
    .quad 0x6d7c9eed999731ec
    .quad 0xb445751afbdbb694
    .quad 0xcc1f3255779bdfb2
    .quad 0x5421247d395a15c0
    .quad 0x6de8c8c978867612
    .quad 0xe46aec53e7e52068
    .quad 0x02b13ff447288243
    .quad 0x9f847adbc2891634
    .quad 0x6b7e12feb787bb6a
    .quad 0x4b9e53cd84e054f9
    .quad 0x3d6ecc4118c9fba2
    .quad 0xf1443cc5bbfd3848
    .quad 0xdc102ca854e5bdb2
    .quad 0xd38289ab5f13fa00
    .quad 0xc6db15a507d95def
    .quad 0xfa3a8a42bf69e550
    .quad 0xb924be5e6ad30249
    .quad 0xb365a450580171a5
    .quad 0xa7fcf563a858ea49
    .quad 0xc990c82550cd9a0f
    .quad 0x0bd33332056cf69a
    .quad 0x03915b5187efb8e6
    .quad 0x1728c2538a0931d0
    .quad 0x9a1f39a4ae324f76
    .quad 0xc73b757f2bdd04e5
    .quad 0xd5f7e5178ccd9e0c
    .quad 0x53cf8273274efaa3
    .quad 0x0e3fbf3303f00bcb
    .quad 0xed3cd4b0de89e331
    .quad 0x806f8f85d65d4ce5
    .quad 0x261bb3cb26a2b35c
    .quad 0x281e389f044daddf
    .quad 0xe2bcaec59d0d77a0
    .quad 0xdce336eb37c7e95e
    .quad 0xf8434772a0adf6e4
    .quad 0x179f89a0467f34df
    .quad 0xe7f78d57717a0734
    .quad 0xb6f036d0bb2d4640
    .quad 0xf6b8e0a507ccbf25
    .quad 0x691b5db968f05b3f
    .quad 0x11b405ead4c1aa94
    .quad 0x6bef8230c309688f
    .quad 0x56b93bc60b07c126
    .quad 0xd8e9e38a1a1de412
    .quad 0x74ddec3a0f986384
    .quad 0xc2acfc5aefafc578
    .quad 0x24843639a40fe988
    .quad 0xed315836165abfc8
    .quad 0x4950c72c82937b81
    .quad 0x6f08b44c4d16a9b2
    .quad 0xda4370aeff28162d
    .quad 0x5975afd14295301e
    .quad 0xc1277a8805a2e8b4
    .quad 0x69452825c9b1a564
    .quad 0x0b7f997f0fc7abb0
    .quad 0x1188f06ea4e21050
    .quad 0xbdb54abef67813b8
    .quad 0xdf6b635790af61f9
    .quad 0x2d5ad8cb7851c1f0
    .quad 0x052d9d99f2c62e64
    .quad 0x389266a859b24095
    .quad 0x6dac2c9a07d268e4
    .quad 0x30c3fb8d6cf282f0
    .quad 0x01916ea8f5b75307
    .quad 0x01cd838161ecc2b4
    .quad 0x45b1d5fc0aad6f86
    .quad 0xf3e94bccef11857b
    .quad 0x3de1a5cb76329ff5
    .quad 0x84e52ca35b4bb954
    .quad 0x333ab66f164b0b8d
    .quad 0xfcf1cbef07b8a884
    .quad 0x6eb0e2b8f295a74c
    .quad 0x6987e7e7ae46bd2a
    .quad 0xff282990ff29b3df
    .quad 0xc29cf0464b9ecc08
    .quad 0x0cfe6214365c6857
    .quad 0x3e82e3fbe16ca338
    .quad 0x3d92bdb5a23f6742
    .quad 0x99c4c19c79f78f4b
    .quad 0x05cb15700cdd6932
    .quad 0x16a7e02da21d0b47
    .quad 0xd1d66f75f15ed8ea
    .quad 0x916336cbfc27a4ea
    .quad 0x3c4e659b8366781d
    .quad 0xea714555fb89efdc
    .quad 0x1f5a2cddcc4c1ddc
    .quad 0x3dc501cc098ce778
    .quad 0x098fca050a6a0c5c
    .quad 0x75358078b57ffa50
    .quad 0xbd633700f9fa782e
    .quad 0x1d7970e7684569a8
    .quad 0x9cbe7b7f531eb9f0
    .quad 0xb069d1e5dace913b
    .quad 0xe9d58fe3abe364e0
    .quad 0xc170377fe885095c
    .quad 0xc6c8514398c74c01
    .quad 0x4104f720150b07f9
    .quad 0x46d2b33367234ef0
    .quad 0xd27a429e9f375b0c
    .quad 0xd72b5dec73fc92cd
    .quad 0xb4ad40a122a9532b
    .quad 0x655e03ca4784d21b
    .quad 0x4d68378b38545c7f
    .quad 0xec56fbadbf14c479
    .quad 0x29ffbdf86cc51c7e
    .quad 0x5be2b1cde0f39b0c
    .quad 0xeb90bd8481943162
    .quad 0xf2551fec908d26e2
    .quad 0x97fb779d71cd5fb8
    .quad 0x2bd4685aefdaf195
    .quad 0xf2a3c8ae27bdde06
    .quad 0xdf45c6ba2a7fbb0e
    .quad 0x3c3aa20fad64ff05
    .quad 0xc64a38ee49e328ff
    .quad 0x5e43a6d6d41c29f8
    .quad 0x9e41f4cbe4f2a609
    .quad 0xf4538523e08289f8
    .quad 0x35302937889dc9b5
    .quad 0x55faeb7ab1491420
    .quad 0xe44b23d660a42e14
    .quad 0x4b06bda4d667135c
    .quad 0x5f78811084c11225
    .quad 0x28fad37087e197a7
    .quad 0x6808f012c7d97e34
    .quad 0xdd780550494bc2e3
    .quad 0x1c5f867a4ac4afbc
    .quad 0xa8b1d42a445d669f
    .quad 0xa3b69804ebde8a65
    .quad 0xb42679494fa343e2
    .quad 0x6d70d365202b8b6e
    .quad 0xa1db25eb34c0892b
    .quad 0x5931fbbf73f14cc9
    .quad 0xf1affd7213a688c0
    .quad 0xb991c4243d9ffd2f
    .quad 0x05278a1fecfde33c
    .quad 0x8961341d45aa4fbc
    .quad 0x70d5528a2e26f3dc
    .quad 0x865d8dfdc40f2b25
    .quad 0xdd7e58df5ad1087d
    .quad 0xb88ddc9ed054bfd1
    .quad 0x73d7ac6dd4891a30
    .quad 0xbcc911367ed18868
    .quad 0x64062075ed69316f
    .quad 0xa7e24b211e684eb2
    .quad 0x5bf582261e84f46d
    .quad 0xe73ad4d8697e4e76

.section .data.core_1_el1_ns__data_shared_segment_1_1343
.global core_1_el1_ns__data_shared_segment_1_1343
core_1_el1_ns__data_shared_segment_1_1343:
    .quad 0xd69f0267d59ab366
    .quad 0x2056e35a2fa6cca1
    .quad 0x3c28eb39fa0c5c37
    .quad 0x35a0b6662cd0ab82
    .quad 0x7fcf70447f8b012a
    .quad 0x7665e9ceb99dd424
    .quad 0xc3ed2cf4267e647c
    .quad 0xb119b71a6e0effad
    .quad 0xc8f97711219aea2c
    .quad 0xf959efa7db1c02fb
    .quad 0x37cc9a5ea8f4759e
    .quad 0x395fe3de844b8679
    .quad 0x24a16bf732286d98
    .quad 0x1b10e3d6001c1941
    .quad 0x24f81683aa5e69b4
    .quad 0xf99b4163b491f2b0
    .quad 0x9160a24024838735
    .quad 0xfb1d789049d1d517
    .quad 0xed7741bdaee04bec
    .quad 0xb6af8727a31a3d37
    .quad 0x13352be02aadc169
    .quad 0x379dbc18ea4cd6ee
    .quad 0xc1128a0b7251d47c
    .quad 0x5f19487086422ec4
    .quad 0x68d71b29778c283d
    .quad 0x975b1d5d6c7b30ef
    .quad 0xd637096179b5cd07
    .quad 0x1d15796fc3354c4c
    .quad 0xac1e69b7b3d65716
    .quad 0x231c5b21cbbcf55c
    .quad 0xe19d9cdd286ce2a9
    .quad 0xd61ed8fbe8723ff8
    .quad 0xa0c41f77b23b8909
    .quad 0x6e42950acf0dd818
    .quad 0x7f260ba63f043d5a
    .quad 0xf8c46bed2a95a55e
    .quad 0x7ae61f09e43a2dbe
    .quad 0x9fd34bb22fe4db60
    .quad 0xa7795b18ef23bcbb
    .quad 0x9020075df8dfe632
    .quad 0x746c229d07904d1e
    .quad 0xa22e9244d29d4eca
    .quad 0x83f69c8c52e42039
    .quad 0x1af1507df213487c
    .quad 0x16e092614319f5e5
    .quad 0x1643e0cc192d38a5
    .quad 0xc2ef324ae8621b19
    .quad 0xb4e05212b8bb4f67
    .quad 0xaa4e90566ca5dd32
    .quad 0x4205a355e2a498af
    .quad 0xfad3ac9905d5d89c
    .quad 0xab53811add274a77
    .quad 0xdf3ea6ced82987e4
    .quad 0xb37bf78b7a08ef16
    .quad 0xce26fe213dc9ecc6
    .quad 0x9a9a1d4a80b82f2c
    .quad 0xcba7c3a97e9b4926
    .quad 0xd0b9bac420af7fa3
    .quad 0x1a3097cedd543e84
    .quad 0x2b90c60e5ff3189b
    .quad 0x5e07bea6681b1518
    .quad 0xab5362f2166f9193
    .quad 0x30d6f68d24108db4
    .quad 0xa7a0349127364801
    .quad 0xcfbe04bb65f31a74
    .quad 0x8f4867079739d787
    .quad 0xf8763b76c63d6eb6
    .quad 0xb349a39819dc6b7e
    .quad 0xc391e8f1d56334de
    .quad 0x1315431d3ac649bd
    .quad 0xcf06c10bed5637db
    .quad 0x512d506c35880a61
    .quad 0xed21c8bd4198ff60
    .quad 0xf87fcda63f8d8fed
    .quad 0xc260c4c3f7ac61a1
    .quad 0xcde454e5b87e3faf
    .quad 0xe40e5600e0496426
    .quad 0x7d7462aa405ff6cf
    .quad 0xcf57d65635312e23
    .quad 0x97f7231cb51f557b
    .quad 0xa800ddd2cd63788a
    .quad 0xb671f2981b8a5cf5
    .quad 0x9271d27933af9dec
    .quad 0xaed68d376ef5d152
    .quad 0x7ec732f6b6475dcb
    .quad 0x2829ff9dfb976de1
    .quad 0x3d8ca9a658ac1353
    .quad 0x0347906fc06ab114
    .quad 0xbb95967be4bbdd72
    .quad 0x7062c3432a54023a
    .quad 0xbdcbb6b60451efd8
    .quad 0x15e36937eb3dc380
    .quad 0x18bc5a800b0941f9
    .quad 0xfa62dc0b59f94fa2
    .quad 0xc23b2b294e902d68
    .quad 0x214d786719f662a4
    .quad 0x5d68864a4df98da5
    .quad 0xba631ce0547a349e
    .quad 0xf011aa4f24361b07
    .quad 0x81ee168c92abc2dc
    .quad 0x90b69bcccbe109e5
    .quad 0x9705ae224159ca5f
    .quad 0x238c4e98e40ad28e
    .quad 0x0206e165a98cfe54
    .quad 0x28482b9fddcc90a3
    .quad 0x651855a7b0151888
    .quad 0x9b9599bf0229ca0a
    .quad 0x1139ed58efb67147
    .quad 0xa3fb7d2006e2eeb9
    .quad 0x6bb33283f250bd6d
    .quad 0x313a11dc853ca90b
    .quad 0xeb34e1d059191f86
    .quad 0x736449a7429f9c40
    .quad 0x177f2bed96bacb5a
    .quad 0xe3f45cffd745938a
    .quad 0xfaac279f18c1c503
    .quad 0xc755358bc51cb14e
    .quad 0xa3be66700a80495e
    .quad 0x07e5b946bd04885c
    .quad 0xde06fa02c233e963
    .quad 0xce43308a3efec6b7
    .quad 0xd763d182db00eb7a
    .quad 0x7cabbed373105570
    .quad 0x16c8142f5c51e1d5
    .quad 0x297d431edaf224d0
    .quad 0x7c1a0845e16bca9e
    .quad 0x242406354a5b8be6
    .quad 0x44e5828a1930c89b
    .quad 0x539ca984f6bd1a3c
    .quad 0x9e9924ea6ef82c95
    .quad 0xde9d835f9a73b23a
    .quad 0xf11abb71d908d582
    .quad 0x81d73737af45f8b3
    .quad 0x3c74a3ac9725a586
    .quad 0x353d22955c1e3223
    .quad 0xf44a6861eee2a29c
    .quad 0x14eb28a7df414f36
    .quad 0x10f15e009693a3e8
    .quad 0xa76c3bb063d7b5e7
    .quad 0xa0553f8745cefffa
    .quad 0x9cea0a27098d3c3a
    .quad 0x6c39cd26ae237b76
    .quad 0x4f90a9eaff62fc71
    .quad 0x50fd320de39415df
    .quad 0xe56cb8790a5367bf
    .quad 0x3a2e98b2d7a673be
    .quad 0x55b8ec9766cdddb1
    .quad 0x4814add78988af94
    .quad 0x35fc8903ddca11a5
    .quad 0x39789efeb9eb6c66
    .quad 0x5604d3cfddb0fb5c
    .quad 0xc03255095ce0bd9b
    .quad 0x07375ca806e3b4cc
    .quad 0xad4c760b6457c818
    .quad 0xcaebcf5aaedc19e8
    .quad 0xbf60674152597b89
    .quad 0x6480b688a129b74f
    .quad 0x12de69eda0096c42
    .quad 0x60dedaac49bf9b83
    .quad 0xb800a5b9899acec6
    .quad 0xf7d82d157ba00251
    .quad 0x9a42f679928b0915
    .quad 0xaf428e11db6239ba
    .quad 0x2a29160d8aa05090
    .quad 0xa52f94ce422cbbe7
    .quad 0xc0826d93bcd4448c
    .quad 0x1386fdb3acbfc8e5
    .quad 0xb64a5f11b9b16550
    .quad 0x5bdfb9e8a53cc1f7
    .quad 0x1ee172493ccb6264
    .quad 0xd47d17051813fb78
    .quad 0x3a8ba4a3b38a0392
    .quad 0xa30d65b0373fc0d6
    .quad 0x8d6e0301938bffc3
    .quad 0x6d2f6d103f237976
    .quad 0x0d9dbbeaf9cbd37f
    .quad 0x1fe6327d0c3ef417
    .quad 0xcb81b347e5fd67de
    .quad 0x82fe171b3b993b39
    .quad 0xa0839bddc070b294
    .quad 0xfbc6021470e4a404
    .quad 0x4681c33a76927285
    .quad 0x35c9bee91e7adf4a
    .quad 0xbec81d038465ef66
    .quad 0x46b180dd1518e672
    .quad 0xf11f751ce806e59a
    .quad 0xca67bb7b04d364ba
    .quad 0x0a2468ec09e4853c
    .quad 0x9ad57bcc6ee34adf
    .quad 0xef2ed574eba896dc
    .quad 0x4365906902fc62fa
    .quad 0xa8c86ca60dd03e55
    .quad 0x3878f95d73ff3266
    .quad 0x0a3ebcfc3bc4c13b
    .quad 0x7a1541a8483d7af4
    .quad 0xb568e34b6d47f6db
    .quad 0x040de57a3c264c93
    .quad 0x42146b400212b29d
    .quad 0xd77a41449209710f
    .quad 0xd5a90895914e234b
    .quad 0x34fe039e8eaac3fd
    .quad 0x2fdec523bdce6d27
    .quad 0x772b787290cfe3b8
    .quad 0x5b6c76c25b9de51e
    .quad 0x360a99720fa412ef
    .quad 0xdba93eef8866e78b
    .quad 0x459360fe39d21f96
    .quad 0x2a095a7991c00fdb
    .quad 0xcd5698040c019b36
    .quad 0x0fd52f97c8a8b264
    .quad 0xe1ccad1a42d39a9f
    .quad 0x4371079666ca5854
    .quad 0x3fb25e9178d0d64d
    .quad 0x0b038dc58612659c
    .quad 0xf7270114ba973bdf
    .quad 0xa68d6ff1708543ec
    .quad 0x2e66063fa09bbdcd
    .quad 0x9c96755551f83f9e
    .quad 0xcee5c245c6d7e0b8
    .quad 0x2d7e5335fa2a8203
    .quad 0x4c17ca787125c1dd
    .quad 0x78dd8cc741174f68
    .quad 0xfe03eec39b817eed
    .quad 0x909ebf7ce7c5434e
    .quad 0x55f2e0f903be05b1
    .quad 0xc0aade6bdba42707
    .quad 0x93c4108d750d47ae
    .quad 0x9f3ca1b73df07904
    .quad 0x60b4eb96c34eb1ca
    .quad 0xf1e2b967daaf15ef
    .quad 0xb0e121fce27428c6
    .quad 0xf9b92ed27ef11daf
    .quad 0xbd12fe5cb397ec1f
    .quad 0xb94cb4e77c8369fb
    .quad 0x2ecfe57b28d32efe
    .quad 0x9188e049e348a07d
    .quad 0xb19c1ed3d07ac19b
    .quad 0x1fed0bc8e2281274
    .quad 0x63bd83e0186f1711
    .quad 0xc30ed77cb0c78502
    .quad 0xc6422548bdeabbb6
    .quad 0x88831a8fb484ae55
    .quad 0xee21607b7f9bff0b
    .quad 0x630dc5d4379234bd
    .quad 0x8180cfc1cb258126
    .quad 0x343da0e97f016f45
    .quad 0xe9582d44a382b230
    .quad 0x043d771799ddfd17
    .quad 0x490797960deeb077
    .quad 0x3990cb15127882d7
    .quad 0x58e80419ebe640ed
    .quad 0xf8538a81d2a588fc
    .quad 0xf768238c64af9db9
    .quad 0x47ff6db315a7ea3c
    .quad 0x2c95f11dd0923888
    .quad 0x6bbd34c2f955d3f2
    .quad 0x589fc9864d81ba74
    .quad 0x4c9b9c7827b8abd0
    .quad 0x5c87a5fd1fbfd889
    .quad 0x78461b6bdc4721ca
    .quad 0xee73bcbcda36f42a
    .quad 0xfd6ab0513259e201
    .quad 0xf2a511c73a314f98
    .quad 0x6110a32505cd6fbd
    .quad 0xf774daf18e927562
    .quad 0x92e80c2505848630
    .quad 0x853d3b98c588828b
    .quad 0xf9998819c3597aa0
    .quad 0x094c388fa3bf4d12
    .quad 0x24a747daeefe4320
    .quad 0x5f6320a30df649d0
    .quad 0xf75e5da528326663
    .quad 0xdc52d829a46681e7
    .quad 0x6d0e232d41a4ceae
    .quad 0x30bc08ce7829eef3
    .quad 0x6c6bdeebc1e1b1f2
    .quad 0x95a8e92d4be11e0b
    .quad 0xa2cde6a3b458142d
    .quad 0x8329764c458dea30
    .quad 0x8c9c04ae40213e8f
    .quad 0x10efe315d2015232
    .quad 0x94eeddf12ca7a9cc
    .quad 0xee18f99c10598816
    .quad 0xe3ea97efe205a2ff
    .quad 0xdb384401398e5ea7
    .quad 0x67839ac2f8add8d7
    .quad 0x904035ae70c24ad2
    .quad 0xaf066c1977d6e02a
    .quad 0x7b75b74fa9d40020
    .quad 0x69eb4e7d21c7b92e
    .quad 0x0f3ca85a2a6a3154
    .quad 0xf1894b269468adf1
    .quad 0x87765c533c070c31
    .quad 0xff72183623ad425b
    .quad 0x19ba0e6ad86f2f11
    .quad 0x5cc4ca539a6b4c59
    .quad 0x37f9e7806842c9a5
    .quad 0xf90b518a963628f4
    .quad 0x87f34bae4fb6a319
    .quad 0xf4a0cee483ad558e
    .quad 0x9ae2200377924f7c
    .quad 0xf310da64965df6bb
    .quad 0x94ca2ae1e0398ee2
    .quad 0x783b44d8c457288a
    .quad 0xf7cab7ec028402d7
    .quad 0x2824901e52f81238
    .quad 0x13769e3e9083ebb4
    .quad 0x00e298186f2ecf04
    .quad 0x54acae9b35cc8e66
    .quad 0xc7e7f045e341320c
    .quad 0x705e73b418980d41
    .quad 0xecb9251ae30ee9c6
    .quad 0xdf32bd116a7f9ec9
    .quad 0xa4710241bbaeac6a
    .quad 0x152e42232602042f
    .quad 0x2ecae37406f8e9ec
    .quad 0xd9e0ba2e591cd95e
    .quad 0x40fc4c28b337afe1
    .quad 0x41ab101990f53ced
    .quad 0x0337107998ccb6cc
    .quad 0x92638f6da9416431
    .quad 0x9507090284735d46
    .quad 0x3d8de30558db33fd
    .quad 0x4dbe1e16d9ad95fd
    .quad 0xae9d2b6329b14bf7
    .quad 0xeb227842ac772081
    .quad 0x639803dc7bff5c01
    .quad 0xfd55c483a8c9267b
    .quad 0x9141b027c85477f6
    .quad 0xa8890079a9a6e9e6
    .quad 0xa84b3b4b49db99a2
    .quad 0xb3c69bc522980b0f
    .quad 0x89429177a40cae7d
    .quad 0x209c3614bdf44764
    .quad 0x3e21dfaf56af64b3
    .quad 0x28d2214653239050
    .quad 0xa04d0b44530285fb
    .quad 0xcbead34eb9d2b5de
    .quad 0xe429def1edaa55a5
    .quad 0xc0a0c23665e93581
    .quad 0x69d3718b7b27a263
    .quad 0xcb2229f837cc7c4b
    .quad 0x2830b1486bb226d8
    .quad 0xf9d3fbe44cc53620
    .quad 0xdfa6cdb27939376b
    .quad 0x87e76f8e0fc5b7df
    .quad 0x120b005b19852d69
    .quad 0x6084d436b270e17f
    .quad 0xe8234e36c1658271
    .quad 0x1553a17f31fd69fd
    .quad 0x69bbbe488cf0a619
    .quad 0xae7195e5166a1c7d
    .quad 0x219959cd76648e18
    .quad 0x45023d8e6e73a384
    .quad 0x02578073189cd360
    .quad 0x64ef8ce812a70d81
    .quad 0x56ec20bab8ca1cc9
    .quad 0xf0aceead6bd1e927
    .quad 0x6c6be79c5699161f
    .quad 0x1864b3b7a0200d5b
    .quad 0xd301e6ed4eaf7d9f
    .quad 0xf55dc8176c9f3a42
    .quad 0x570554b94d971a5e
    .quad 0x4cf0c1723bb90cc8
    .quad 0x2e98cac39e664753
    .quad 0x0fd715bab99b30de
    .quad 0x470cba4187d498e4
    .quad 0x852b0dec42c7e538
    .quad 0x821cb1dfe1ea1c79
    .quad 0x149e052325e5261a
    .quad 0x3f027878d39ab288
    .quad 0x9616ddc5255f47bf
    .quad 0x1a5dd5c24fac3906
    .quad 0xfecf5e61e3293b39
    .quad 0x29fcefc9284b228a
    .quad 0x84834f37a3da2a67
    .quad 0x176a22df6bd723d6
    .quad 0x25db5a0f516acbec
    .quad 0x2111b6865f7fda91
    .quad 0x459077a795da0fc9
    .quad 0x6b77445a924e1721
    .quad 0x2af62c69083c86c1
    .quad 0xf0d9c617d54f5dcf
    .quad 0xe48d229006f0f6a3
    .quad 0xcaec2f29ba7a4687
    .quad 0x0b6e15b41bdae3fb
    .quad 0x91b8815ff0972a74
    .quad 0x01466445a3894f78
    .quad 0x849be9fb71eb3b98
    .quad 0xc1e31051b5d812db
    .quad 0x3a4ef4c9e78954d2
    .quad 0x8e62c3e3f48abc26
    .quad 0xf3b0ef812c03dbec
    .quad 0xec037c83127c1056
    .quad 0xcccbad4c9923b016
    .quad 0x025b7aa6ab34d92d
    .quad 0xba22d3eefb62e063
    .quad 0x12bba7836b927d1a
    .quad 0x77edc83929aa0eb9
    .quad 0x9b1c751743d9c465
    .quad 0xb7343b47f9fe6c42
    .quad 0x021add8a2ef9a946
    .quad 0x3076208513e2221a
    .quad 0xad2e96ef20db931a
    .quad 0x344539f61749e6a6
    .quad 0x225e108a74728b6f
    .quad 0xb7c018bb7f281789
    .quad 0x31052a73a94681fd
    .quad 0x3f94ad47bbad3984
    .quad 0x721e3fb70eeac3cc
    .quad 0x3afccf0df903e743
    .quad 0x07640840cf5b2822
    .quad 0xc6c2f5b7a83bccb8
    .quad 0x88d81a65d5b71cb6
    .quad 0x40d134e9e3175a85
    .quad 0xded7d4d98dfed3ab
    .quad 0x01a7fd7d8580e283
    .quad 0xc0f591fec8d2683b
    .quad 0x4dc362652e53fbd4
    .quad 0x1b1f6689b0e1b9c7
    .quad 0x28376e610efc441a
    .quad 0xad9c7de9d91fc2cb
    .quad 0xe313f6b23ec3a520
    .quad 0x7bc7a54b5959e047
    .quad 0xd2d77784163310f9
    .quad 0x1d6f21db6bcdb3b1
    .quad 0x39dae4e32813fda0
    .quad 0x45a5fe94777b4787
    .quad 0x29b0141c9713f0c9
    .quad 0xec8677ea2394cfe4
    .quad 0xcd0ee0b4dc2d884a
    .quad 0xa21a1000fc879520
    .quad 0xa8a74a5a58a726ba
    .quad 0x3e9d34f0e47cb76b
    .quad 0x4791fc82398725e9
    .quad 0x33989ee1387a33f9
    .quad 0x525d9ee6407b4bc8
    .quad 0xa16bd342e699f638
    .quad 0xc49b2761a1f778df
    .quad 0x53a3afe1c931cfed
    .quad 0xa9e4a92cbfa4ba6a
    .quad 0x272fb576bae98efb
    .quad 0xe04071296cb5f516
    .quad 0x0bdc07a59bbad04d
    .quad 0xc2e62b48c46c35cc
    .quad 0x88fefeddb331996d
    .quad 0xdef7b6099efdd294
    .quad 0x908ed4cfef4aada7
    .quad 0x064545e200e4942a
    .quad 0x3c6549993c3e125d
    .quad 0x44f34123126eecd3
    .quad 0x8a4d3d5d8e96ac96
    .quad 0x2fd7a582789f611c
    .quad 0x0a31f40a250ecdbc
    .quad 0x815779861f619f11
    .quad 0xd6652b2bc1e8f15c
    .quad 0x0017460b7c93aa13
    .quad 0x51d6f01db5c1cdf2
    .quad 0x593392c598402061
    .quad 0xda8fd954fe294b1b
    .quad 0x0ca4ff72f464dccd
    .quad 0x2a6a685c47240d63
    .quad 0x46879c2e39fd51e2
    .quad 0xcd29c173ec6c299f
    .quad 0xc5cfa35c9a984e85
    .quad 0x321ce2c7cacf8e01
    .quad 0xaba985ed421cc050
    .quad 0x02cbe7c4579d377c
    .quad 0xac32ea9832881a46
    .quad 0x70ff559e3b8dd1d8
    .quad 0x9e578b3371ad4a7d
    .quad 0xde2dbbf9ead9d033
    .quad 0x3df843bb5f5eba17
    .quad 0x56313fb36f624e85
    .quad 0x4c29a0ff72394e89
    .quad 0x515fac619a445bbd
    .quad 0xd1b45c2d7f9883d9
    .quad 0x816daad48b333086
    .quad 0xdfcca64f2035d161
    .quad 0x2e56a94d78241c1e
    .quad 0x389cb5271755c4df
    .quad 0xcb3cffbd75cf10c1
    .quad 0x09c0b6ab308a6307
    .quad 0xdc8d1c61c31016a3
    .quad 0xd3c9e3a7f202a350
    .quad 0x312f1e243ffea8fb
    .quad 0xe90d379189578adc
    .quad 0xb40e2b757c1ba58d
    .quad 0x1364857c61baa3a6
    .quad 0xa4195d17d13d9180
    .quad 0x44e1307def44bd0e
    .quad 0xce47da224ba59b1e
    .quad 0x1b00ddc18e4956f1
    .quad 0x79146aad4e1275be
    .quad 0x7589326ce1ef39e3
    .quad 0x2101a34da80966fb
    .quad 0x2c1e3f3e7b9cc414
    .quad 0x920a43062d1ae767
    .quad 0xccbc4ea7fda5dfb1
    .quad 0x6eabd64b9fbc282b
    .quad 0x1e7833413d88bbde
    .quad 0x92b5b0d0808a3e32
    .quad 0xb54bdccfd48651da
    .quad 0xe4b7057eb1ee1b4e
    .quad 0x62db8d672b7b1b83
    .quad 0x4e41fde80b62f068
    .quad 0xc87a53693d6d2d09
    .quad 0xbfbdb98229586ce3
    .quad 0xcfc87acd6cc06c1f
    .quad 0x7532fb550616c25e
    .quad 0x0509a4ec2633231b
    .quad 0xd0f79467bcdb825a

.section .data.cross_core_data_segment_1300
.global cross_core_data_segment_1300
cross_core_data_segment_1300:
.org 0x4e8
.align 3
label_4901_end_boot_barrier_barrier_vector_mem1985__core_1_el1_ns:
    .word 0x00000003  // 4 bytes

.org 0x780
.align 3
label_4922_end_test_barrier_barrier_vector_mem2017__core_1_el1_ns:
    .word 0x00000003  // 4 bytes



.section .data.core_1_el1_ns__data_preserve_segment_0_1344
.global core_1_el1_ns__data_preserve_segment_0_1344
core_1_el1_ns__data_preserve_segment_0_1344:
.org 0xe90
.align 2
core_1_el1_ns__exception_callback_LOWER_A64_SYNC_mem1984:
    .word 0x00000000  // 4 bytes
    .word 0x00000000  // 4 bytes



.section .data.core_1_el1_ns__data_preserve_segment_1_1345
.global core_1_el1_ns__data_preserve_segment_1_1345
core_1_el1_ns__data_preserve_segment_1_1345:
.org 0xa4c
.align 1
core_1_el1_ns__exception_callback_LOWER_A64_SYNC_mem1983:
    .word 0x00000000  // 4 bytes
    .word 0x00000000  // 4 bytes


// No uninitialized data on core_1_el1_ns__stack_segment_1346 data segment. skipping .data section

