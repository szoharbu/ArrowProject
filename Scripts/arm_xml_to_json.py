import re
import json
import argparse
import xml.etree.ElementTree as ET
from typing import Optional
from bs4 import BeautifulSoup
from enum import Enum, auto


# Operand types in ARM A64
class OperandType(Enum):
    GPR = auto()  # General-purpose (Xn/Wn), SIMD (Vn), Special registers
    SIMD_FPR = auto()  # SIMD and floating-point registers (Vn, Dn, Sn, Hn)
    SVE = auto()  # Scalable vector SVE
    PREDICATE = auto()  # Scalable predicate register P0-P7
    IMMEDIATE = auto()  # Constant values like #imm
    SHIFT = auto()  # left shift to apply to the immediate
    MEMORY = auto()  # Load/store operands like [Xn, #offset]
    LABEL = auto()  # Branch target like B label
    UNKNOWN = auto()  # Unknown operand type, need to ensure no such types left


# Operand roles in an instruction
class OperandRole(Enum):
    SRC = auto()  # Source operand (Rn, Rm, immediate values)
    DEST = auto()  # Destination operand (Rd)
    SRC_DEST = auto()  # Acts as both source and destination (e.g., ADD Rd, Rd, Rn)
    NA = auto()  # Not applicable (e.g., Labels don't have a role)
    UNKNOWN = auto()  # Unknown operand role, need to ensure no such rules left


class Operand:
    """ Represents an operand with its value and optionality. """

    def __init__(self, text: str,
                 size: Optional[int] = None,
                 role: Optional[OperandRole] = None,
                 type: Optional[OperandType] = None,
                 element_size: Optional[str] = None,
                 anchor: Optional[str] = None,
                 is_optional=False):
        self.text = text
        self.type = type
        self.size = size
        self.role = role
        self.element_size = element_size
        self.is_optional = is_optional
        self._is_finalized = False
        self.anchors = []
        if anchor is not None:
            self.anchors.append(anchor)

    def extend_operand(self, text: Optional[str] = None, anchor: Optional[str] = None):
        ''' Extends the operand with additional text and link metadata. '''
        if self._is_finalized:
            raise ValueError("Cannot extend a finalized operand")
        if text:
            self.text += text
        if anchor:
            self.anchors.append(anchor)

    def finalize_operand(self):
        self._is_finalized = True
        print(f"finalize operand: {self.text}")
        for a in self.anchors:
            hover = a.get("hover", "").lower()
            if self.type is None:
                if "register" in hover:
                    if "general-purpose" in hover:
                        self.type = OperandType.GPR
                    elif "simd" in hover or "fp" in hover:
                        self.type = OperandType.SIMD_FPR
                        self.size = 128  # TODO:: need to adjust it
                    elif "scalable vector" in hover:
                        self.type = OperandType.SVE
                        self.size = 128  # TODO:: need to adjust it
                    elif "scalable predicate" in hover:
                        self.type = OperandType.PREDICATE
                        self.size = 16  # TODO:: need to adjust it
                elif "optional shift" in hover or "optional left shift" in hover:
                    self.type = OperandType.SHIFT
                    self.role = OperandRole.NA
                    self.size = "n/a"

                elif "immediate" in hover:
                    self.type = OperandType.IMMEDIATE
                    self.role = OperandRole.DEST
                    pattern = r"imm(\d+)"
                    match = re.search(pattern, hover)
                    if match:
                        self.size = int(match.group(1))

                elif "label" in hover:
                    self.type = OperandType.LABEL
                    self.role = OperandRole.NA

            if self.role is None:
                if "source and destination" in hover:
                    self.role = OperandRole.SRC_DEST
                elif "source" in hover:
                    self.role = OperandRole.SRC
                elif "destination" in hover:
                    self.role = OperandRole.DEST
                elif "governing scalable predicate" in hover:
                    self.role = OperandRole.NA
            if self.size is None:
                if "64-bit" in hover:
                    self.size = 64
                elif "32-bit" in hover:
                    self.size = 32
                elif "16-bit" in hover:
                    self.size = 16
                elif "8-bit" in hover:
                    self.size = 8
                elif "imm19" in hover:
                    self.size = 19
                elif "imm26" in hover:
                    self.size = 26

        if self.type is None: self.type = OperandType.UNKNOWN
        if self.role is None: self.role = OperandRole.UNKNOWN
        if self.size is None: self.size = "unknown"

    def __repr__(self):
        return f"{self.text}  [ size = {self.size}, role = {self.role}, element_size = {self.element_size}, optional = {self.is_optional} ]"
        # if self.is_optional:
        #     return f"{self.value}  (optional)"
        # else:
        #     return f"{self.value}"

    def to_dict(self):
        """ Converts the object to a dictionary for JSON serialization. """
        return {"text": self.text,
                "type": self.type.name,
                "role": self.role.name,
                "size": self.size,
                "element_size": self.element_size,
                "is_optional": self.is_optional,
                "anchors": [anchor.get("hover", "") for anchor in self.anchors]  # Nested JSON list
                }


def parse_asm_template(xml_string):
    # Convert XML ElementTree object to string if needed
    if isinstance(xml_string, ET.Element):
        xml_string = ET.tostring(xml_string, encoding="unicode")
    # Parse the XML with BeautifulSoup
    soup = BeautifulSoup(xml_string, "html.parser")

    # Collect all <text> and <a> elements
    elements = soup.find_all(["text", "a"])

    if not elements:
        return
        # raise ValueError("Invalid format: No <text> or <a> elements found")

    print(f"xml_string: {xml_string}")

    # step 1: extracted full syntax
    extracted_text = []
    for elem in elements:
        extracted_text.append(elem.get_text())
    syntax = "".join(extracted_text)
    syntax = re.sub(r'\s+', ' ', syntax)  # Clean up extra spaces
    print(f"syntax: {syntax}")

    operands = []
    current_operand: Operand = None
    mnemonic = None
    optional_depth = 0

    for elem in elements:
        # print(f"elem: {elem}")
        element_text = elem.text.strip()

        if mnemonic is None:
            # The assumption is that the first element start with the mnemonic.
            first_text_parts = element_text.split(" ", 1)
            mnemonic = first_text_parts[0]
            # print(f"mnemonic: {mnemonic}")
            if len(first_text_parts) > 1:
                element_text = first_text_parts[1]
            else:
                continue

        if elem.name == "text":

            parts = element_text.split(", ")  # check for operand separator

            for i, part in enumerate(parts):
                # print(f"text parts: '{part}'")

                if part == ",":
                    if current_operand is not None:
                        current_operand.finalize_operand()
                        operands.append(current_operand)
                        current_operand = None  # reset for the next operand
                elif part.startswith("{"):
                    optional_depth += 1
                elif part.startswith("}"):
                    optional_depth -= 1
                    if optional_depth == 0:
                        current_operand.is_optional = True

                elif part.endswith(","):
                    if current_operand is None:
                        current_operand = Operand(text=part[:-1])
                    else:
                        current_operand.extend_operand(text=part[:-1])
                    current_operand.finalize_operand()
                    operands.append(current_operand)
                    current_operand = None
                else:
                    if current_operand is None:
                        current_operand = Operand(text=part)
                    else:
                        current_operand.extend_operand(text=part)

                if i != len(parts) - 1:
                    # all parts beside the last one should finalize operands
                    if current_operand is not None:
                        current_operand.finalize_operand()
                        operands.append(current_operand)
                        current_operand = None
        elif elem.name == "a":
            # Extend operand with link information
            # Assumption: <a> tags always exist inside an operand, not split across several operands
            if current_operand is None:
                current_operand = Operand(text=elem.text, anchor=elem)
            else:
                current_operand.extend_operand(text=elem.text, anchor=elem)

    if current_operand is not None:
        current_operand.finalize_operand()
        operands.append(current_operand)

    # print(" finish asm_template")
    print(f" - {mnemonic}")
    for op in operands:
        print(f" --- {op.text}")
        print(f" ----- {op.type}")
        print(f" ----- {op.role}")
        print(f" ----- {op.size}")
        for a in op.anchors:
            print(f" ------- {a}")

    asm_template = {"mnemonic": mnemonic, "syntax": syntax}
    asm_template["operands"] = [op.to_dict() for op in operands]

    return asm_template  # {"mnemonic": mnemonic, "syntax": syntax, "operands": operands}


def parse_instruction(inst):
    """Parses a single instruction element and extracts relevant data."""
    instruction_section = inst.find(".//instructionsection")
    instruction_info = {
        "file_name": inst.get("file"),
        "id": instruction_section.get("id") if instruction_section is not None else None,
        "title": instruction_section.get("title") if instruction_section is not None else None,
        # "type": instruction_section.get("type") if instruction_section is not None else None,
        "docvars": {},
        "description": {
            "brief": None,
            "full": None
        },
        "asm_templates": []
    }
    print(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz {instruction_info["id"]}")

    # Extract docvars
    docvars = inst.find(".//docvars")  # Only direct children, not nested ones
    if docvars is not None:
        for docvar in docvars.findall("docvar"):
            key = docvar.get("key")
            value = docvar.get("value")
            if key and value:
                instruction_info["docvars"][key] = value

    # Extract brief and full description
    brief = inst.find(".//desc/brief/para")
    full_desc = inst.find(".//desc/authored")
    if brief is not None:
        instruction_info["description"]["brief"] = brief.text.strip()
    if full_desc is not None:
        instruction_info["description"]["full"] = " ".join(
            para.text.strip() for para in full_desc.findall("para") if para.text)

    # Extract all asmtemplate elements
    for asm in inst.findall(".//asmtemplate"):
        parsed_asm = parse_asm_template(asm)
        instruction_info["asm_templates"].append(parsed_asm)

    return instruction_info


def extract_instructions(xml_path):
    """Extracts instruction sections as Element objects from a large XML file."""
    instructions = []

    context = ET.iterparse(xml_path, events=("start", "end"))
    _, root = next(context)  # Get root element

    current_instruction = None

    for event, elem in context:
        # Start of a new instruction
        if event == "start" and elem.tag == "file" and elem.get("type") == "instructionsection":
            current_instruction = elem  # Capture this instruction block

        # End of an instruction block
        elif event == "end" and elem.tag == "file" and elem.get("type") == "instructionsection":
            if current_instruction is not None:
                instructions.append(current_instruction)  # Store full element
                current_instruction = None  # Reset for the next instruction
            root.clear()  # Free memory

    return instructions  # Returns a list of ElementTree elements


def process_xml_file(xml_path, output_json):
    """Extracts and structures instruction data, then saves to JSON."""
    instructions = extract_instructions(xml_path)
    # TODO:: remove after
    # TODO:: remove after
    # instructions = instructions[7:8] # Limit to X instructions for testing
    # TODO:: remove after
    # TODO:: remove after
    instructions_data = [parse_instruction(inst) for inst in instructions]

    with open(output_json, "w", encoding="utf-8") as json_f:
        json.dump(
            {"instructions": instructions_data},
            json_f,
            # default=lambda o: o.to_dict() if isinstance(o, Operand) else o,
            indent=2
        )

    print(f"Processed {len(instructions_data)} instruction entries and saved to {output_json}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XML to JSON instruction extractor")
    parser.add_argument("source", help="Path to the ASL.XML file")
    parser.add_argument("dest", help="Path to the output JSON file")

    # source = "Scripts/mini.xml"
    # dest = "instr.json"
    # process_xml_file(source, dest)
    args = parser.parse_args()

    if args.source is None:
        args.source = "/home/nvcpu-sw-co100/asl/1.0/current/debug_arm/x86_64/src/projectA_asl.xml"

    process_xml_file(args.source, args.dest)
