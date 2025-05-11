"""
Standalone ARM asm-template parser using Lark.

Provides parse_asm_template(template: str) -> dict with keys:
  - mnemonic: str
  - operands: list of operand dicts

Operand dicts have key `kind` among:
  "simple"   : <Xd> or <Xn|SP>
  "typed"    : <Vd>.<T>
  "immediate": #4 or #<pimm>
  "union"    : (A|B)
  "range"    : A-B
  "optional" : {A, B, C}
  "memory"   : [ ... ]

Usage:
    from asm_template_parser import parse_asm_template
    ast = parse_asm_template("ADD <Vd>.<T>, [<Xn|SP>, #4], {<Vm>.<T>}")

Install dependency:
    pip install lark-parser
"""
import logging
from lark import Lark, Transformer

logger = logging.getLogger(__name__)

_arm_asm_grammar = r"""
    start: instr

    instr: MNEMONIC operand_list?
    operand_list: operand ("," operand)*

    ?operand: union_operand
            | range_operand
            | optional_group
            | memory_group
            | typed_operand
            | simple_operand
            | immediate_operand

    MNEMONIC: /[A-Z][A-Z0-9\.]*/

    simple_operand: "<" NAME ("|" NAME)* ">"
    typed_operand: simple_operand "." "<" NAME ">"
    immediate_operand: "#" (INT | "<" NAME ">")
    union_operand: "(" operand ("|" operand)+ ")"
    range_operand: (typed_operand | simple_operand) "-" (typed_operand | simple_operand)
    optional_group: "{" operand ("," operand)* "}"
    memory_group: "[" mem_item ("," mem_item)* "]" SUFFIX?
    mem_item: operand ("{" NAME ("," NAME)* "}")?

    NAME: /[A-Za-z0-9_+\.\-]+/
    INT: /-?\d+/
    SUFFIX: /[!?]/
    WS: /[ \t\f\r\n]+/

    %ignore WS
"""

_parser = Lark(_arm_asm_grammar, start="start", parser="lalr")

class AsmTemplateTransformer(Transformer):
    def start(self, items):
        return items[0]

    def instr(self, items):
        mnemonic = items[0]
        operands = items[1] if len(items) > 1 else []
        return {
            "mnemonic": mnemonic,
            "operands": [{
                **op,
                "index": i+1
            } for i, op in enumerate(operands)]
        }

    def MNEMONIC(self, token):
        return token.value

    def simple_operand(self, items):
        # items: list of NAME strings
        names = items
        return {"kind": "simple", "text": "<" + "|".join(names) + ">"}

    def typed_operand(self, items):
        base = items[0]
        typ = items[1]
        text = base["text"] + ".<" + typ + ">"
        return {"kind": "typed", "text": text, "base": base, "type": typ}

    def immediate_operand(self, items):
        val = items[0]
        return {"kind": "immediate", "text": "#" + val}

    def union_operand(self, items):
        return {"kind": "union", "options": items}

    def range_operand(self, items):
        return {"kind": "range", "from": items[0], "to": items[1]}

    def optional_group(self, items):
        return {"kind": "optional", "elements": items}

    def mem_item(self, items):
        # items: [operand] or [operand, name1, ...]
        op = items[0]
        if len(items) > 1:
            # curly-brace tail after mem operand
            tail_names = items[1:]
            op = op.copy()
            op["tail"] = tail_names
        return op

    def memory_group(self, items):
        result = {"kind": "memory", "items": items[:-1] if items[-1].type == "SUFFIX" else items}
        if items[-1].type == "SUFFIX":
            result["suffix"] = items[-1].value
        return result

    def NAME(self, token):
        return token.value

    def INT(self, token):
        return token.value

    def SUFFIX(self, token):
        return token


def parse_asm_template(template: str) -> dict:
    """
    Parse an ARM asm template into a structured AST.

    Returns:
      { "mnemonic": str,
        "operands": [operand dicts] }
    """
    try:
        tree = _parser.parse(template)
        return AsmTemplateTransformer().transform(tree)
    except Exception as e:
        logger.error(f"Failed to parse template '{template}': {str(e)}")
        return {"mnemonic": "", "operands": []}


if __name__ == "__main__":
    import pprint
    examples = [
        "ADD <Vd>.<T>, [<Xn|SP>, #4], {<Vm>.<T>}",
        "ST3  { <Vt>.H, <Vt2>.H, <Vt3>.H }[<index>], [<Xn|SP>], #6",
        "UVDOT   ZA.S[<Wv>, <offs>{, VGx2}], { <Zn1>.H-<Zn4>.H }, <Zm>.H[<index>]",
        "STR  <Ht>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]",
        "STP  <Xt1>, <Xt2>, [<Xn|SP>, #<imm>]!",
        "LDR <Xt>, [<Xn|SP>], #<imm>"
    ]
    pp = pprint.PrettyPrinter(indent=2, width=60)
    
    for tmpl in examples:
        print("\n" + "="*80)
        print(f"Template: {tmpl}")
        print("-"*80)
        ast = parse_asm_template(tmpl)
        pp.pprint(ast)
