import random

from luau_ast import *
from util import random_name


def _is_flattenable_stmt(stmt):
    return isinstance(
        stmt,
        (
            Assign,
            CallStmt,
            IfStmt,
            WhileLoop,
            RepeatLoop,
            NumericFor,
            GenericFor,
            Do,
            RawStmt,
        ),
    )


def _can_flatten_block(block, min_statements):
    if len(block.stmts) < min_statements:
        return False
    for stmt in block.stmts:
        if not _is_flattenable_stmt(stmt):
            return False
    return True


def _flatten_block(stmts, rand):
    state_name = random_name(rand)
    init = LocalDecl([state_name], [NumberLit("1")])

    clauses = []
    for idx, stmt in enumerate(stmts, start=1):
        body = Block(
            [
                stmt,
                Assign([Name(state_name)], [NumberLit(str(idx + 1))]),
            ]
        )
        cond = BinOp("==", Name(state_name), NumberLit(str(idx)))
        clauses.append((cond, body))

    dispatcher = IfStmt(clauses, Block([BreakStmt()]))
    loop = WhileLoop(BoolLit(True), Block([dispatcher]))
    return [init, loop]


def _walk_stmt(stmt, rand, min_statements):
    if isinstance(stmt, Do):
        _walk_block(stmt.body, rand, min_statements)
        return

    if isinstance(stmt, WhileLoop):
        _walk_block(stmt.body, rand, min_statements)
        return

    if isinstance(stmt, RepeatLoop):
        _walk_block(stmt.body, rand, min_statements)
        return

    if isinstance(stmt, IfStmt):
        for _, body in stmt.clauses:
            _walk_block(body, rand, min_statements)
        if stmt.else_body:
            _walk_block(stmt.else_body, rand, min_statements)
        return

    if isinstance(stmt, NumericFor):
        _walk_block(stmt.body, rand, min_statements)
        return

    if isinstance(stmt, GenericFor):
        _walk_block(stmt.body, rand, min_statements)
        return

    if isinstance(stmt, FuncDecl):
        _walk_block(stmt.body, rand, min_statements)
        return


def _walk_block(block, rand, min_statements):
    for stmt in list(block.stmts):
        _walk_stmt(stmt, rand, min_statements)

    if _can_flatten_block(block, min_statements):
        block.stmts = _flatten_block(block.stmts, rand)


def flatten_control_flow(ast, min_statements=4):
    rand = random.SystemRandom()
    _walk_block(ast, rand, min_statements)
    return ast
