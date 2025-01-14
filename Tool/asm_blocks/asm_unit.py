from typing import Optional
from Utils.configuration_management import Configuration
from Tool.asm_blocks.data_unit import get_last_user_context



class AsmUnit:
    def __init__(
            self,
            *,
            prefix:str=None,
            mnemonic: Optional[str]=None,
            operands: Optional[list]=None,
            asm_string: Optional[str]=None,
            comment: Optional[str]=None,
    ):
        """
        Initializes an AsmUnit from an asm, generate or comment syntax. and can later be published into the asm file
        """

        if asm_string is not None and (mnemonic is not None or operands is not None):
            raise ValueError("asm_string and mnemonic or operands are mutually excluded.")

        # order is important here to determine the type
        if asm_string:
            self.type = "asm_string"
        elif mnemonic:
            self.type = "generation"
        elif comment:
            self.type = "comment"
        else:
            raise ValueError("invalid AsmUnit type. one of 'asm_string', 'mnemonic', 'comment' must be provided")

        self.prefix = prefix
        self.mnemonic = mnemonic
        self.operands = operands
        self.asm_string = asm_string
        self.comment = comment

        #extract context to generated data
        self.file_name, self.file_name_shortened_path, self.line_number = get_last_user_context()

        self.extended_comment = ""
        self.asm_unit = ""

        if self.prefix:
            self.asm_unit += self.prefix
        if self.asm_string:
            self.asm_unit += f" {self.asm_string}"
        if self.mnemonic:
            self.asm_unit += f" {self.mnemonic} {', '.join(map(str, self.operands))}"
        if self.comment:
            self.asm_unit += f" {get_comment_mark()} {self.comment}"

        # add file and line Inspect
        self.asm_unit = format_with_alignment(self.asm_unit, f"{get_comment_mark()} ( From {self.file_name_shortened_path}, line {self.line_number})")

        #print(f"   {self.asm_unit}")


    def __str__(self):
        return self.asm_unit

def get_comment_mark():
    if Configuration.Architecture.x86:
        return ";"
    elif Configuration.Architecture.riscv:
        return "#"
    elif Configuration.Architecture.arm:
        return "//"
    else:
        raise ValueError(f"Unknown Architecture requested")



def format_with_alignment(main_text, comment, width=120):
    """
    Pads main_text to a fixed width and appends comment aligned to that width.

    Parameters:
    - main_text (str): The main part of the text.
    - comment (str): The additional text to align after the main text.
    - width (int): Fixed width for the main text. Default is 30 characters.

    Returns:
    - str: A formatted string with aligned main text and comment.
    """
    # Pad main_text to the specified width
    aligned_text = main_text.ljust(width)

    # Append the comment, which will start after the padded main text
    return f"{aligned_text}{comment}"
