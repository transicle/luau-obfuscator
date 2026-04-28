import random
import re

from luau_ast import *
from scope import analyse
from tokens import BUILTINS
from util import random_name


_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _builtin_names():
    seen = set()
    names = []
    for item in BUILTINS:
        base = item.split(".", 1)[0]
        if _IDENT.match(base) and base not in seen:
            seen.add(base)
            names.append(base)
    return names


def obfuscate_builtins(ast):
    rand = random.SystemRandom()
    table_name = random_name(rand)
    builtin_names = _builtin_names()
    field_by_builtin = {name: random_name(rand) for name in builtin_names}

    pairs = ",".join(f"{field_by_builtin[name]}={name}" for name in builtin_names)
    ast.stmts.insert(0, RawStmt(f"local {table_name}={{{pairs}}}"))

    table = analyse(ast)

    def rewrite_value(value, in_lhs=False):
        if isinstance(value, Node):
            return rewrite_node(value, in_lhs)
        if isinstance(value, list):
            return [rewrite_value(item, in_lhs) for item in value]
        if isinstance(value, tuple):
            return tuple(rewrite_value(item, in_lhs) for item in value)
        return value

    def rewrite_node(node, in_lhs=False):
        if node is None or not isinstance(node, Node):
            return node

        if isinstance(node, Name):
            if in_lhs:
                return node
            scope = table.scope_of.get(id(node))
            symbol = scope.lookup(node.name) if scope is not None else None
            if symbol is None and node.name in field_by_builtin:
                return FieldExpr(Name(table_name), field_by_builtin[node.name])
            return node

        if isinstance(node, Assign):
            node.exprs = [rewrite_value(expr, False) for expr in node.exprs]
            node.targets = [rewrite_value(target, True) for target in node.targets]
            return node

        for attr, value in list(node.__dict__.items()):
            setattr(node, attr, rewrite_value(value, False))
        return node

    rewrite_node(ast)
    return ast
