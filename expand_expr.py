import random

from luau_ast import *


def _parse_int_literal(text):
    try:
        if text.startswith(("0x", "0X")):
            return int(text, 16)
        return int(text, 10)
    except Exception:
        return None


def _num(n):
    return NumberLit(str(n))


def expand_expressions(ast, probability=0.55):
    rand = random.SystemRandom()

    def expand_number(node):
        value = _parse_int_literal(node.value)
        if value is None:
            return node
        if rand.random() > probability:
            return node

        delta = rand.randint(11, 251)
        return BinOp("-", BinOp("+", _num(value + delta), _num(delta)), _num(delta * 2))

    def wrap_numeric_expr(node):
        if not isinstance(node, BinOp):
            return node
        if node.op not in {"+", "-", "*", "/", "%", "//"}:
            return node
        if rand.random() > 0.35:
            return node

        z = rand.randint(31, 401)
        zero = BinOp("-", _num(z), _num(z))
        return BinOp("+", node, zero)

    def walk(node):
        if node is None or not isinstance(node, Node):
            return node

        if isinstance(node, NumberLit):
            return expand_number(node)

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

        return wrap_numeric_expr(node)

    walk(ast)
    return ast
