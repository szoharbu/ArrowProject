#!/usr/bin/env python3
"""
Script to merge Arrow test.asm with objdump output
Combines the assembly file with comments/labels and the objdump with addresses/opcodes
"""

import re
import sys
import os
from Arrow.Utils.logger_management import get_logger

def parse_objdump_by_sections(objdump_file):
    """Parse objdump file and organize instructions by section"""
    sections = {}
    current_section = None
    current_instructions = []
    
    with open(objdump_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Check for disassembly section start
            match = re.match(r'Disassembly of section (.+):', line)
            if match:
                # Save previous section if it exists
                if current_section and current_instructions:
                    sections[current_section] = current_instructions
                
                # Start new section
                current_section = match.group(1)
                current_instructions = []
                continue
            
            # Skip if not in a section
            if current_section is None:
                continue
                
            # Skip empty lines and function labels
            if not line or (line.endswith('>:') and not line[0].isdigit()):
                continue
                
            # Parse actual instruction lines (starts with address)
            # Format: "   1b0961700:	d503201f 	nop"
            match = re.match(r'\s*([0-9a-f]{8,16}):\s+([0-9a-f]{8})\s+(.+)', line)
            if match:
                address = match.group(1)
                opcode = match.group(2)
                instruction = match.group(3)
                current_instructions.append((address, opcode, instruction))
    
    # Save the last section
    if current_section and current_instructions:
        sections[current_section] = current_instructions
    
    return sections

def get_instruction_mnemonic(line):
    """Extract instruction mnemonic from a line"""
    stripped = line.strip()
    
    # Remove trailing comments
    if '//' in stripped:
        stripped = stripped.split('//')[0].strip()
    
    # Get first word (the instruction)
    parts = stripped.split()
    return parts[0].lower() if parts else ""

def is_instruction_line(line):
    """Check if a line contains an assembly instruction (not comment or label)"""
    stripped = line.strip()
    
    # Empty line
    if not stripped:
        return False
    
    # Comment line
    if stripped.startswith('//'):
        return False
    
    # Label line - check if it ends with colon (before any comment)
    # Split by '//' to remove inline comments first
    code_part = stripped.split('//')[0].strip()
    if code_part.endswith(':'):
        return False
    
    # Check for data directives that generate actual machine code
    # These should be treated as "instructions" for merging purposes
    data_directives = ['.word', '.byte', '.hword', '.dword', '.quad', '.long', '.short']
    if any(stripped.startswith(directive) for directive in data_directives):
        return True
    
    # Other directive lines (like .section, .global, .org, etc.)
    if stripped.startswith('.'):
        return False
    
    # If it's not a comment, label, or non-data directive, assume it's an instruction
    return True

def normalize_mnemonic(mnemonic):
    """Normalize mnemonics to handle objdump variations"""
    # Handle conditional branches: b.ne -> bne, b.eq -> beq, etc.
    if mnemonic.startswith('b.'):
        return 'b' + mnemonic[2:]
    return mnemonic

def check_before_after_alignment(asm_instructions, obj_instructions, current_idx):
    """
    Check if instructions before and after the current position are aligned.
    If they are, we can assume the current mismatch is an equivalent operation.
    """
    # Check if we have enough context (at least one instruction before and after)
    if current_idx == 0 or current_idx >= len(asm_instructions) - 1:
        return False
    if current_idx == 0 or current_idx >= len(obj_instructions) - 1:
        return False
    
    # Check instruction before
    prev_asm_mnemonic = normalize_mnemonic(get_instruction_mnemonic(asm_instructions[current_idx - 1]))
    prev_obj_mnemonic = normalize_mnemonic(obj_instructions[current_idx - 1][2].split()[0].lower())
    
    # Check instruction after
    next_asm_mnemonic = normalize_mnemonic(get_instruction_mnemonic(asm_instructions[current_idx + 1]))
    next_obj_mnemonic = normalize_mnemonic(obj_instructions[current_idx + 1][2].split()[0].lower())
    
    # Both before and after must match for us to consider this an equivalent operation
    before_matches = prev_asm_mnemonic == prev_obj_mnemonic
    after_matches = next_asm_mnemonic == next_obj_mnemonic
    
    return before_matches and after_matches

def merge_files(asm_file, objdump_file, output_file):
    """Merge the ASM file with objdump information"""
    logger = get_logger()
    logger.debug(f"Parsing objdump sections: {objdump_file}")
    objdump_sections = parse_objdump_by_sections(objdump_file)
    logger.debug(f"Found {len(objdump_sections)} sections in objdump:")
    for section_name, instructions in objdump_sections.items():
        logger.debug(f"  {section_name}: {len(instructions)} instructions")
    
    logger.debug(f"\nProcessing ASM file: {asm_file}")
    
    # Calculate prefix length for consistent formatting
    # Find the longest address to ensure consistent spacing
    max_addr_len = 0
    for section_instructions in objdump_sections.values():
        for addr, opcode, _ in section_instructions:
            max_addr_len = max(max_addr_len, len(addr))
    
    # Create prefix with maximum lengths to ensure all lines align properly
    # Format: "[max_addr] "
    prefix_length = 1 + max_addr_len + 2  # "[addr] "
    spacing_prefix = " " * prefix_length
    
    logger.debug(f"Max address length: {max_addr_len}")
    logger.debug(f"Calculated prefix length: {prefix_length}")
    logger.debug(f"Spacing prefix: '{spacing_prefix}' (length: {len(spacing_prefix)})")
    
    # Track errors for summary
    errors = []
    
    # First pass: collect all instructions per section from ASM
    asm_sections = {}
    current_section = None
    
    with open(asm_file, 'r') as f:
        for line in f:
            # Check for section directive
            match = re.match(r'\.section\s+(.+)', line.strip())
            if match:
                current_section = match.group(1)
                if current_section not in asm_sections:
                    asm_sections[current_section] = []
                continue
            
            # Collect instructions for this section
            if (current_section and 
                is_instruction_line(line) and  # Check if it's an instruction first
                line.startswith('     ')):     # Then check if it's indented
                asm_sections[current_section].append(line.rstrip('\n'))
    
    # Second pass: merge with before/after alignment checking
    with open(asm_file, 'r') as f_in, open(output_file, 'w') as f_out:
        current_section = None
        section_instruction_index = 0
        
        for line_num, line in enumerate(f_in, 1):
            original_line = line.rstrip('\n')
            
            # Check for section directive
            match = re.match(r'\.section\s+(.+)', line.strip())
            if match:
                current_section = match.group(1)
                section_instruction_index = 0
                # Add spacing to section directives
                f_out.write(spacing_prefix + original_line + '\n')
                continue
            
            # If this is an instruction line and we're in a known section
            if (current_section and 
                current_section in objdump_sections and 
                current_section in asm_sections and
                is_instruction_line(line) and  # Check if it's an instruction first
                line.startswith('     ')):     # Then check if it's indented
                
                objdump_instructions = objdump_sections[current_section]
                asm_instructions = asm_sections[current_section]
                
                if section_instruction_index < len(objdump_instructions):
                    addr, opcode, objdump_instr = objdump_instructions[section_instruction_index]
                    
                    # Get mnemonics for verification
                    asm_mnemonic = get_instruction_mnemonic(line)
                    objdump_mnemonic = objdump_instr.split()[0].lower() if objdump_instr.split() else ""
                    
                    # Normalize mnemonics for comparison
                    normalized_asm = normalize_mnemonic(asm_mnemonic)
                    normalized_obj = normalize_mnemonic(objdump_mnemonic)
                    
                    # Check if they match
                    if normalized_asm == normalized_obj:
                        # Perfect match
                        prefix = f"[{addr}] "
                        merged_line = prefix + original_line
                        f_out.write(merged_line + '\n')
                        section_instruction_index += 1
                    else:
                        # Mismatch - check if before and after instructions are aligned
                        if check_before_after_alignment(asm_instructions, objdump_instructions, section_instruction_index):
                            # Before and after are aligned - treat as equivalent instruction
                            prefix = f"[{addr}] "
                            merged_line = prefix + original_line
                            f_out.write(merged_line + '\n')
                            logger.debug(f"Info: Equivalent instruction at line {line_num}: ASM='{asm_mnemonic}' ≈ OBJ='{objdump_mnemonic}' (before/after aligned)")
                            section_instruction_index += 1
                        else:
                            # Cannot confirm equivalence - this is an error
                            error_msg = f"ERROR: Misaligned instruction at line {line_num}: ASM='{asm_mnemonic}' vs OBJ='{objdump_mnemonic}' (before/after not aligned)"
                            logger.error(error_msg)
                            errors.append(error_msg)
                            
                            # Continue processing with error marker
                            prefix = f"[ERROR: {addr}] "
                            merged_line = prefix + original_line
                            f_out.write(merged_line + '\n')
                            section_instruction_index += 1
                else:
                    # No more objdump instructions for this section
                    prefix = "[NO_MORE_OBJ] "
                    merged_line = prefix + original_line
                    f_out.write(merged_line + '\n')
            else:
                # Not an instruction, add spacing to maintain alignment
                f_out.write(spacing_prefix + original_line + '\n')
    
    logger.debug(f"\nMerge complete. Output written to: {output_file}")
    
    # Print error summary
    if errors:
        logger.error(f"\n⚠️  MERGE COMPLETED WITH {len(errors)} ERRORS:")
        for i, error in enumerate(errors, 1):
            logger.error(f"  {i}. {error}")
        logger.error(f"\n❌ Partial merge file generated with error markers: {output_file}")
        raise ValueError(f"Merge completed with {len(errors)} alignment errors. Check the output file for details.")
    else:
        logger.info(f"---- Success: Merging asm and objdump files completed, see {output_file}")

def main():
    # File paths
    asm_file = "Arrow_output/test.asm"
    objdump_file = "Arrow_output/test.elf.objdump"
    output_file = "Arrow_output/test_merged.asm"
    
    # Check if files exist
    if not os.path.exists(asm_file):
        print(f"Error: ASM file not found: {asm_file}")
        sys.exit(1)
        
    if not os.path.exists(objdump_file):
        print(f"Error: Objdump file not found: {objdump_file}")
        sys.exit(1)
    
    print("Starting merge process...")
    merge_files(asm_file, objdump_file, output_file)
    print("Done!")

if __name__ == "__main__":
    main() 