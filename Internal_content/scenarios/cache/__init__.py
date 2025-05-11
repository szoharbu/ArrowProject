import random
from Utils.configuration_management import Configuration
from Arrow_API import AR
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.CACHE])
def simple_cache_scenario():
    '''
    Repeatedly load/store memory across cache lines to stress data cache behavior.
    Triggers cache fills, evictions, and potential line conflicts using stride access.
    '''
    print("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz simple_cache_scenario")
    block_size = 100
    stride = 8
    counter = block_size // stride

    base_reg = RegisterManager.get_and_reserve(reg_type="gpr")
    offset_reg = RegisterManager.get_and_reserve(reg_type="gpr")
    address_reg = RegisterManager.get_and_reserve(reg_type="gpr")
    data_reg = RegisterManager.get(reg_type="gpr")  # no need to reserve, can be overwritten
    mem_block = MemoryManager.MemoryBlock(name="cache_stress_block", byte_size=block_size, init_value=0xaaaaaaaabbbbbbbbccccccccdddddddd, alignment=8)

    print(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz mem block: {mem_block}")
    print(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz mem block unique label: {mem_block.unique_label}")
  
    AR.asm(f"adrp {base_reg}, {mem_block.unique_label}")
    AR.asm(f"add  {base_reg}, {base_reg}, :lo12:{mem_block.unique_label}")
    AR.asm(f"mov {offset_reg}, #0")

    # setting counter to be mem_block.byte_size / 8
    with AR.Loop(counter=counter):
        AR.asm(f"add {address_reg}, {base_reg}, {offset_reg}", comment="base + offset")
        AR.asm(f"ldr {data_reg}, [{address_reg}]", comment="load from memory")
        AR.generate(instruction_count=2, dest=data_reg, comment="randonly touch the data")
        AR.asm(f"str {data_reg}, [{address_reg}]", comment="store back to memory")
        AR.asm(f"add {offset_reg}, {offset_reg}, #64", comment="increment offset")

    RegisterManager.free(address_reg)
    RegisterManager.free(offset_reg)
    RegisterManager.free(base_reg)


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.CACHE])
def factorial():
    '''
    ------------------------------------------------------------------------------
    Function: factorial
    Input:   x0 - Non-negative integer
    Output:  x0 - Factorial of x0 (x0!)
    Clobbers: x1
    ------------------------------------------------------------------------------
    '''
    factorial_value = random.randint(4, 6)
    AR.asm(f"mov x0, #1")
    AR.asm(f"mov x1, #1", comment="")

    with AR.Loop(counter=factorial_value - 1):
        AR.asm("add x0, x0, #1      // Increment n")
        AR.asm("mul x1, x1, x0      // result = result * (n-1)")

    AR.asm("mov x0, x1          // Move the result back to x0")
    


# factorial:
#     cmp x0, #1          // Base case: if n <= 1, return 1
#     ble .Lfact_base

#     mov x1, x0          // Store original n
# .Lfact_loop:
#     sub x0, x0, #1      // Decrement n
#     mul x1, x1, x0      // result = result * (n-1)
#     cmp x0, #1          // Loop until n becomes 1
#     bgt .Lfact_loop

#     mov x0, x1          // Move the result back to x0
# .Lfact_base:
#     ret
'''
// ------------------------------------------------------------------------------
// Function: reverse_string
// Input:   x0 - Pointer to the null-terminated string
// Output:  None (string is reversed in place)
// Clobbers: x1, x2, x3, w4
// ------------------------------------------------------------------------------
reverse_string:
    mov x1, x0          // ptr_start = str
.Lrev_find_end:
    ldrb w2, [x1]       // Load byte at ptr_end
    cbz w2, .Lrev_swap  // If byte is null, we've reached the end
    add x1, x1, #1      // Increment ptr_end
    b .Lrev_find_end

.Lrev_swap:
    sub x1, x1, #1      // ptr_end now points to the last character

.Lrev_loop:
    cmp x0, x1          // While ptr_start < ptr_end
    bge .Lrev_done

    ldrb w2, [x0]       // Load byte at ptr_start
    ldrb w3, [x1]       // Load byte at ptr_end
    strb w3, [x0]       // Store byte at ptr_end to ptr_start
    strb w2, [x1]       // Store byte at ptr_start to ptr_end

    add x0, x0, #1      // Increment ptr_start
    sub x1, x1, #1      // Decrement ptr_end
    b .Lrev_loop

.Lrev_done:
    ret

// ------------------------------------------------------------------------------
// _start: Entry point of the program
// ------------------------------------------------------------------------------
_start:
    // --- Demonstrate Factorial ---
    mov x0, #5          // Calculate factorial of 5
    bl factorial        // Call the factorial function

    // Result of factorial (5! = 120) is now in x0

    // --- Demonstrate String Reversal ---
    adr x0, .Lstring    // Load the address of the string
    bl reverse_string   // Call the reverse_string function

    // The string at .Lstring is now reversed

    // --- Exit the program ---
    mov x8, #93         // syscall number for exit
    mov x0, #0          // exit code 0
    svc #0              // Invoke the system call

.data
.Lstring:
    .asciz "Hello, ARM Assembly!"
'''