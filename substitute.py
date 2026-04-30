import random

from luau_ast import *
from util import random_name


def _parse_int_literal(text):
    try:
        if text.startswith(("0x", "0X")):
            return int(text, 16)
        return int(text, 10)
    except Exception:
        return None


def encode_numeric_literals(ast, probability=0.65):
    rand = random.SystemRandom()
    decode_fn = random_name(rand)
    arg_value = random_name(rand)
    arg_key = random_name(rand)

    decode_raw = RawStmt(
        f"local function {decode_fn}({arg_value},{arg_key}) return {arg_value}-{arg_key} end"
    )

    def maybe_replace_num(node):
        if not isinstance(node, NumberLit):
            return node

        if rand.random() > probability:
            return node

        value = _parse_int_literal(node.value)
        if value is None or abs(value) > 10_000_000:
            return node

        key = rand.randint(5, 250)
        encoded = value + key
        return CallExpr(Name(decode_fn), [NumberLit(str(encoded)), NumberLit(str(key))])

    def walk(node):
        if node is None or not isinstance(node, Node):
            return node

        replaced = maybe_replace_num(node)
        if replaced is not node:
            return replaced

        for attr, value in list(node.__dict__.items()):
            if isinstance(value, Node):
                setattr(node, attr, walk(value))
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, Node):
                        value[idx] = walk(item)
                    elif isinstance(item, tuple):
                        rebuilt = []
                        for part in item:
                            rebuilt.append(walk(part) if isinstance(part, Node) else part)
                        value[idx] = tuple(rebuilt)
            elif isinstance(value, tuple):
                rebuilt = []
                for part in value:
                    rebuilt.append(walk(part) if isinstance(part, Node) else part)
                setattr(node, attr, tuple(rebuilt))

        return node

    walk(ast)
    ast.stmts.insert(0, decode_raw)
    return ast
