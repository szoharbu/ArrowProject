from typing import Optional

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

        self.asm_unit = ""

        if self.prefix:
            self.asm_unit += self.prefix
        if self.asm_string:
            self.asm_unit += f" {self.asm_string}"
        if self.mnemonic:
            self.asm_unit += f" {self.mnemonic} {', '.join(map(str, self.operands))}"
        if self.comment:
            self.asm_unit += f" ; {self.comment}"

    def __str__(self):
        return self.asm_unit
