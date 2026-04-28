import random

from luau_ast import *
from scope import analyse
from tokens import *


def rename_vars(ast):
    forbidden = (
        set(BUILTINS) | set(KEYWORDS) | set(TYPES) | set(TYPE_KEYWORDS) | set(VAR_DECLS)
    )
    chars = "IlJjfFtT"
    rest  = "Il1JjfFtT7"
    used  = set(forbidden)
    rand  = random.SystemRandom()
    scope_table = analyse(ast)
    renamed = {}

    def fresh():
        while True:
            name = rand.choice(chars) + "".join(
                rand.choice(rest) for _ in range(rand.randint(13, 21))
            )
            if name not in used:
                used.add(name)
                return name

    for symbols in scope_table.symbol_of.values():
        for symbol in symbols:
            if symbol.decl_node is not None:
                renamed[id(symbol)] = fresh()

    def rename(scope, name, local_only=False):
        if scope is None:
            return name
        symbol = scope.lookup_local(name) if local_only else scope.lookup(name)
        return name if symbol is None else renamed.get(id(symbol), name)

    def walk(node):
        if node is None or not isinstance(node, Node):
            return
        scope = scope_table.scope_of.get(id(node))
        if isinstance(node, Name):
            node.name = rename(scope, node.name)
        elif isinstance(node, LocalDecl):
            node.names = [rename(scope, n, True) for n in node.names]
        elif isinstance(node, Assign):
            for target in node.targets:
                if isinstance(target, Name):
                    target.name = rename(scope, target.name)
        elif isinstance(node, FuncDecl):
            body_scope = scope_table.scope_of.get(id(node.body))
            if "." not in node.name and ":" not in node.name:
                node.name = rename(scope, node.name, True)
            node.params = [
                rename(body_scope, p, True) if p != "..." else p
                for p in node.params
            ]
        elif isinstance(node, FuncExpr):
            body_scope = scope_table.scope_of.get(id(node.body))
            node.params = [
                rename(body_scope, p, True) if p != "..." else p
                for p in node.params
            ]
        elif isinstance(node, NumericFor):
            node.var = rename(scope_table.scope_of.get(id(node.body)), node.var, True)
        elif isinstance(node, GenericFor):
            body_scope = scope_table.scope_of.get(id(node.body))
            node.names = [rename(body_scope, n, True) for n in node.names]

        for value in node.__dict__.values():
            if isinstance(value, Node):
                walk(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, Node):
                        walk(item)
                    elif isinstance(item, tuple):
                        for part in item:
                            walk(part)
            elif isinstance(value, tuple):
                for part in value:
                    walk(part)

    walk(ast)
    return ast
