
from Utils.configuration_management import Configuration
from Tool.state_management import get_current_state
from Tool.memory_management.memory_operand import Memory
from Tool.asm_libraries.asm_logger import AsmLogger


class MemoryArray:
    def __init__(self, array_name, elements, element_size=4):
        """
        Initialize the memory array.

        :param array_name: Name of the array (used for labels).
        :param elements: List of elements to populate the array.
        :param element_size: Size of each element in bytes (default 4 for word).
        """
        current_state = get_current_state()

        self.array_name = array_name
        self.elements = elements
        self.element_size = element_size
        self.array_size = len(elements) * element_size
        self.current_offset_register = "x1"  # Default offset register

        # Convert each integer to its byte representation
        byte_representation = []
        for value in self.elements:
            # Convert the integer to bytes, and ensure the byte size
            byte_rep = value.to_bytes(element_size, byteorder='little')  # or 'big' depending on endianness
            byte_representation.append(byte_rep)

        self.array_block = MemoryBlock(name=f"{self.array_name}_array_memory_block", byte_size=self.array_size, init_value_byte_representation=byte_representation, shared=False)
        self.offset_mem = Memory(name=f"{self.array_name}_index_memory", byte_size=2, init_value=0x0)

        AsmLogger.comment(f"Set address of the array block ({self.array_block.name}) in the Index memory ({self.offset_mem.name})")
        tmp_reg = current_state.register_manager.get_and_reserve()
        comment1 = f"Load address of {self.array_block.name} into {tmp_reg}"
        comment2 = f"Store address of {self.array_block.name} into {self.offset_mem.name}"
        if Configuration.Architecture.x86:
            AsmLogger.asm(f"lea {tmp_reg}, [{self.array_block.unique_label}]", comment=comment1)
            AsmLogger.asm(f"mov [{self.offset_mem.unique_label}], {tmp_reg}", comment=comment2)
        elif Configuration.Architecture.arm:
            AsmLogger.asm(f"ldr {tmp_reg}, ={self.array_block.unique_label}", comment=comment1)
            AsmLogger.asm(f"str {tmp_reg}, [{self.offset_mem.unique_label}]", comment=comment2)
        elif Configuration.Architecture.riscv:
            AsmLogger.asm(f"la {tmp_reg}, {self.array_block.unique_label}", comment=comment1)
            AsmLogger.asm(f"sw {tmp_reg}, {self.offset_mem.unique_label}", comment=comment2)
        else:
            raise ValueError(f"Unsupported architecture")
        current_state.register_manager.free(tmp_reg)

    def load_element(self, output_register)->None:
        """
        Generate assembly code to load the memory based on the current offset and store value into output_register
        :param output_register: The register to store the loaded value.
        """
        current_state = get_current_state()

        AsmLogger.comment(f"Load the address from {self.offset_mem.name} to access an element value in {self.array_block.name} into {output_register}")
        tmp_reg = current_state.register_manager.get_and_reserve()
        comment1 = f"Load address from {self.offset_mem.name}"
        comment2 = f"Dereference address in {tmp_reg} and load the value into {output_register}"
        if Configuration.Architecture.x86:
            AsmLogger.asm(f"mov {tmp_reg}, [{self.offset_mem.unique_label}]", comment=comment1)
            AsmLogger.asm(f"mov {output_register}, [{tmp_reg}]", comment=comment2)
        elif Configuration.Architecture.arm:
            AsmLogger.asm(f"ldr {tmp_reg}, [{self.offset_mem.unique_label}]", comment=comment1)
            AsmLogger.asm(f"ldr {output_register}, [{tmp_reg}]", comment=comment2)
        elif Configuration.Architecture.riscv:
            AsmLogger.asm(f"lw {tmp_reg}, {self.offset_mem.unique_label}", comment=comment1)
            AsmLogger.asm(f"lw {output_register}, 0({tmp_reg})", comment=comment2)
        else:
            raise ValueError(f"Unsupported architecture")

        current_state.register_manager.free(tmp_reg)

    def store_element(self, output_register)->None:
        """
        Generate assembly code to store the memory based on the current offset and store value into output_register
        :param output_register: The register that get stored.
        """
        current_state = get_current_state()

        AsmLogger.comment(f"Store the value in {output_register} to the address in {self.offset_mem.name} to store an element value in {self.array_block.name}")
        tmp_reg = current_state.register_manager.get_and_reserve()
        comment1 = f"Load address from {self.offset_mem.name} into {tmp_reg}"
        comment2 = f"Store value from {tmp_reg} into the address in {output_register}"
        if Configuration.Architecture.x86:
            AsmLogger.asm(f"mov {tmp_reg}, [{self.offset_mem.unique_label}]", comment=comment1)
            AsmLogger.asm(f"mov [{tmp_reg}], {output_register}", comment=comment2)
        elif Configuration.Architecture.arm:
            AsmLogger.asm(f"ldr {tmp_reg}, [{self.offset_mem.unique_label}]", comment=comment1)
            AsmLogger.asm(f"str {output_register}, [{tmp_reg}]", comment=comment2)
        elif Configuration.Architecture.riscv:
            AsmLogger.asm(f"lw {tmp_reg}, {self.offset_mem.unique_label}", comment=comment1)
            AsmLogger.asm(f"sw {output_register}, 0({tmp_reg})", comment=comment2)
        else:
            raise ValueError(f"Unsupported architecture")

        current_state.register_manager.free(tmp_reg)


    def next_element(self, num_elements)->None:
        """
        Generate assembly code to increment the offset and reset it if cyclic.

        :param num_elements: Total number of elements in the array.
        """
        current_state = get_current_state()

        print("TODO:::: need to make sure we are resting the value once reached array end, at the moment the below only increment index")

        AsmLogger.comment(f"Increment the address in {self.offset_mem.name} by {self.element_size} (element size)")
        if Configuration.Architecture.x86:
            AsmLogger.asm(f"add [{self.offset_mem.name}], {self.element_size}")
            # instructions = [
            #     f"    add {self.current_offset_register}, {self.current_offset_register}, #1  // Increment offset",
            #     f"    cmp {self.current_offset_register}, #{num_elements}  // Check if offset reached end",
            #     f"    csel {self.current_offset_register}, xzr, {self.current_offset_register}, eq  // Reset if cyclic",
            # ]
        elif Configuration.Architecture.arm:
            AsmLogger.asm(f"add [{self.offset_mem.name}], {self.element_size}")
        elif Configuration.Architecture.riscv:
            tmp_reg = current_state.register_manager.get_and_reserve()
            AsmLogger.asm(f"lw {tmp_reg}, {self.offset_mem.unique_label}")
            AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {self.element_size}")
            AsmLogger.asm(f"sw {tmp_reg}, {self.offset_mem.name}")
            current_state.register_manager.free(tmp_reg)
        else:
            raise ValueError(f"Unsupported architecture")

    # def cool_feature(self):
    #     """
    #     Add a cool feature: Reverse traversal of the array cyclically.
    #     """
    #     instructions = [
    #         f"    sub {self.current_offset_register}, {self.current_offset_register}, #1  // Decrement offset",
    #         f"    cmp {self.current_offset_register}, #0  // Check if offset is negative",
    #         f"    csel {self.current_offset_register}, #{len(self.elements) - 1}, {self.current_offset_register}, lt  // Wrap around if negative",
    #     ]
    #     return "\n".join(instructions)
    #
    # def generate_loop(self, base_register, output_register, iterations):
    #     """
    #     Generate a loop that cyclically accesses all elements of the array.
    #
    #     :param base_register: The register containing the base address of the array.
    #     :param output_register: The register to store the loaded value.
    #     :param iterations: Number of iterations for the loop.
    #     """
    #     loop_label = "loop_start"
    #     end_label = "loop_end"
    #
    #     instructions = [
    #         f"    mov x2, #{iterations}  // Set loop counter",
    #         f"{loop_label}:",
    #         self.access_memory(base_register, output_register),  # Access current element
    #         self.next_element(len(self.elements)),  # Move to next element cyclically
    #         f"    subs x2, x2, #1  // Decrement loop counter",
    #         f"    b.ne {loop_label}  // Repeat if counter not zero",
    #         f"{end_label}:",
    #     ]
    #     return "\n".join(instructions)


# # Example Usage
# if __name__ == "__main__":
#     # Create an array of 5 elements
#     mem_array = MemoryArray("my_array", [10, 20, 30, 40, 50])
#
#     # Generate memory declaration
#     print(mem_array.generate_memory())
#     print("\n// Access memory at current offset")
#     print(mem_array.access_memory("x0", "x3"))
#
#     # Generate "next element" cyclic code
#     print("\n// Increment offset cyclically")
#     print(mem_array.next_element(5))
#
#     # Generate a loop accessing all elements cyclically
#     print("\n// Generate loop code")
#     print(mem_array.generate_loop("x0", "x3", 10))
#
#     # Add a cool feature: Reverse traversal
#     print("\n// Reverse traversal")
#     print(mem_array.cool_feature())
