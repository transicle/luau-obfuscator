import random

from luau_ast import *
from util import random_name


def _num(n):
    return NumberLit(str(n))


def _opaque_true(rand):
    a = rand.randint(100, 4000)
    b = rand.randint(100, 4000)
    m = rand.choice([7, 9, 11, 13, 17, 19])
    left = BinOp("%", BinOp("+", _num(a), _num(b)), _num(m))
    right = _num((a + b) % m)
    return BinOp("==", left, right)


def _opaque_false(rand):
    a = rand.randint(100, 4000)
    return BinOp("==", BinOp("-", _num(a), _num(a)), _num(1))


def _walk_expr(expr, rand, branch_probability):
    if expr is None or not isinstance(expr, Node):
        return expr

    for attr, value in list(expr.__dict__.items()):
        if isinstance(value, Node):
            setattr(expr, attr, _walk_expr(value, rand, branch_probability))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, Node):
                    value[i] = _walk_expr(item, rand, branch_probability)
    return expr


def _walk_block(block, rand, branch_probability):
    for stmt in block.stmts:
        _walk_stmt(stmt, rand, branch_probability)


def _walk_stmt(stmt, rand, branch_probability):
    if isinstance(stmt, IfStmt):
        new_clauses = []
        for cond, body in stmt.clauses:
            cond = _walk_expr(cond, rand, branch_probability)
            if rand.random() < branch_probability:
                cond = BinOp("and", _opaque_true(rand), cond)
            _walk_block(body, rand, branch_probability)
            new_clauses.append((cond, body))

        if rand.random() < 0.45:
            tmp = random_name(rand)
            dead_body = Block([
                LocalDecl([tmp], [NumberLit(str(rand.randint(100, 9999)))]),
                Assign([Name(tmp)], [BinOp("+", Name(tmp), NumberLit("1"))]),
            ])
            new_clauses.insert(0, (_opaque_false(rand), dead_body))

        stmt.clauses = new_clauses
        if stmt.else_body:
            _walk_block(stmt.else_body, rand, branch_probability)
        return

    if isinstance(stmt, WhileLoop):
        stmt.cond = _walk_expr(stmt.cond, rand, branch_probability)
        if rand.random() < branch_probability:
            stmt.cond = BinOp("and", _opaque_true(rand), stmt.cond)
        _walk_block(stmt.body, rand, branch_probability)
        return

    if isinstance(stmt, RepeatLoop):
        _walk_block(stmt.body, rand, branch_probability)
        stmt.cond = _walk_expr(stmt.cond, rand, branch_probability)
        if rand.random() < branch_probability:
            stmt.cond = BinOp("and", _opaque_true(rand), stmt.cond)
        return

    if isinstance(stmt, Do):
        _walk_block(stmt.body, rand, branch_probability)
        return

    if isinstance(stmt, NumericFor):
        stmt.start = _walk_expr(stmt.start, rand, branch_probability)
        stmt.stop = _walk_expr(stmt.stop, rand, branch_probability)
        if stmt.step:
            stmt.step = _walk_expr(stmt.step, rand, branch_probability)
        _walk_block(stmt.body, rand, branch_probability)
        return

    if isinstance(stmt, GenericFor):
        stmt.iters = [_walk_expr(it, rand, branch_probability) for it in stmt.iters]
        _walk_block(stmt.body, rand, branch_probability)
        return

    if isinstance(stmt, FuncDecl):
        _walk_block(stmt.body, rand, branch_probability)
        return

    for attr, value in list(stmt.__dict__.items()):
        if isinstance(value, Node):
            setattr(stmt, attr, _walk_expr(value, rand, branch_probability))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, Node):
                    value[i] = _walk_expr(item, rand, branch_probability)


def inject_opaque_predicates(ast, branch_probability=0.8):
    rand = random.SystemRandom()
    _walk_block(ast, rand, branch_probability)
    return ast
