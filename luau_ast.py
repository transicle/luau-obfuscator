class Node:
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"


class Block(Node):
    def __init__(self, stmts):
        self.stmts = stmts


class LocalDecl(Node):
    def __init__(self, names, exprs):
        self.names = names
        self.exprs = exprs


class Assign(Node):
    def __init__(self, targets, exprs):
        self.targets = targets
        self.exprs = exprs


class Do(Node):
    def __init__(self, body):
        self.body = body


class WhileLoop(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body


class RepeatLoop(Node):
    def __init__(self, body, cond):
        self.body = body
        self.cond = cond


class IfStmt(Node):
    def __init__(self, clauses, else_body):
        self.clauses = clauses
        self.else_body = else_body



class NumericFor(Node):
    def __init__(self, var, start, stop, step, body):
        self.var = var
        self.start = start
        self.stop = stop
        self.step = step
        self.body = body


class GenericFor(Node):
    def __init__(self, names, iters, body):
        self.names = names
        self.iters = iters
        self.body = body


class FuncDecl(Node):
    def __init__(self, name, params, body, is_local=False, is_method=False):
        self.name = name
        self.params = params
        self.body = body
        self.is_local = is_local
        self.is_method = is_method


class ReturnStmt(Node):
    def __init__(self, exprs):
        self.exprs = exprs


class BreakStmt(Node):
    pass


class ContinueStmt(Node):
    pass


class CallStmt(Node):
    def __init__(self, call_expr):
        self.call_expr = call_expr


class NumberLit(Node):
    def __init__(self, value):
        self.value = value


class StringLit(Node):
    def __init__(self, value):
        self.value = value


class RawStmt(Node):
    def __init__(self, code):
        self.code = code


class BoolLit(Node):
    def __init__(self, value):
        self.value = value


class NilLit(Node):
    pass


class VarArgExpr(Node):
    pass


class Name(Node):
    def __init__(self, name):
        self.name = name


class IndexExpr(Node):
    def __init__(self, obj, key):
        self.obj = obj
        self.key = key


class FieldExpr(Node):
    def __init__(self, obj, field):
        self.obj = obj
        self.field = field


class MethodCallExpr(Node):
    def __init__(self, obj, method, args):
        self.obj = obj
        self.method = method
        self.args = args


class CallExpr(Node):
    def __init__(self, func, args):
        self.func = func
        self.args = args


class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class UnOp(Node):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


class TableConstructor(Node):
    def __init__(self, fields):
        self.fields = fields



class FuncExpr(Node):
    def __init__(self, params, body):
        self.params = params
        self.body = body
