from luau_ast import *

def _visit_list(visit_fn, lst):
    result = []
    for item in lst:
        if isinstance(item, Node):
            result.append(visit_fn(item))
        else:
            result.append(item)
    return result


def _visit_clauses(visit_fn, clauses):
    result = []
    for cond, body in clauses:
        new_cond = visit_fn(cond)
        new_body = visit_fn(body)
        result.append((new_cond, new_body))
    return result


def _visit_fields(visit_fn, fields):
    result = []
    for key, value in fields:
        new_key = visit_fn(key) if isinstance(key, Node) else key
        new_value = visit_fn(value)
        result.append((new_key, new_value))
    return result


class Visitor:
    def __init__(self, order="pre"):
        assert order in ("pre", "post"), "order must be 'pre' or 'post'"
        self.order = order

    def visit(self, node):
        if node is None:
            return
        method = getattr(self, f"visit_{type(node).__name__}", self.generic_visit)
        if self.order == "pre":
            method(node)
            self._traverse_children(node)
        else:
            self._traverse_children(node)
            method(node)

    def generic_visit(self, node):
        pass

    def _traverse_children(self, node):
        if isinstance(node, Block):
            for stmt in node.stmts:
                self.visit(stmt)

        elif isinstance(node, LocalDecl):
            for expr in node.exprs:
                self.visit(expr)

        elif isinstance(node, Assign):
            for t in node.targets:
                self.visit(t)
            for e in node.exprs:
                self.visit(e)

        elif isinstance(node, Do):
            self.visit(node.body)

        elif isinstance(node, WhileLoop):
            self.visit(node.cond)
            self.visit(node.body)

        elif isinstance(node, RepeatLoop):
            self.visit(node.body)
            self.visit(node.cond)

        elif isinstance(node, IfStmt):
            for cond, body in node.clauses:
                self.visit(cond)
                self.visit(body)
            if node.else_body:
                self.visit(node.else_body)

        elif isinstance(node, NumericFor):
            self.visit(node.start)
            self.visit(node.stop)
            if node.step:
                self.visit(node.step)
            self.visit(node.body)

        elif isinstance(node, GenericFor):
            for it in node.iters:
                self.visit(it)
            self.visit(node.body)

        elif isinstance(node, FuncDecl):
            self.visit(node.body)

        elif isinstance(node, FuncExpr):
            self.visit(node.body)

        elif isinstance(node, ReturnStmt):
            for e in node.exprs:
                self.visit(e)

        elif isinstance(node, CallStmt):
            self.visit(node.call_expr)

        elif isinstance(node, CallExpr):
            self.visit(node.func)
            for a in node.args:
                self.visit(a)

        elif isinstance(node, MethodCallExpr):
            self.visit(node.obj)
            for a in node.args:
                self.visit(a)

        elif isinstance(node, FieldExpr):
            self.visit(node.obj)

        elif isinstance(node, IndexExpr):
            self.visit(node.obj)
            self.visit(node.key)

        elif isinstance(node, BinOp):
            self.visit(node.left)
            self.visit(node.right)

        elif isinstance(node, UnOp):
            self.visit(node.operand)

        elif isinstance(node, TableConstructor):
            for key, value in node.fields:
                if isinstance(key, Node):
                    self.visit(key)
                self.visit(value)

        # Leaf nodes: Name, NumberLit, StringLit, BoolLit,
        #             NilLit, VarArgExpr, BreakStmt, ContinueStmt — no children


class Transformer:
    def __init__(self, order="pre"):
        assert order in ("pre", "post"), "order must be 'pre' or 'post'"
        self.order = order

    def visit(self, node):
        if node is None:
            return None
        method = getattr(self, f"visit_{type(node).__name__}", self.generic_visit)
        if self.order == "pre":
            node = method(node)
            return self._rebuild(node)
        else:
            node = self._rebuild(node)
            return method(node)

    def generic_visit(self, node):
        return node

    def _rebuild(self, node):
        if isinstance(node, Block):
            node.stmts = _visit_list(self.visit, node.stmts)

        elif isinstance(node, LocalDecl):
            node.exprs = _visit_list(self.visit, node.exprs)

        elif isinstance(node, Assign):
            node.targets = _visit_list(self.visit, node.targets)
            node.exprs = _visit_list(self.visit, node.exprs)

        elif isinstance(node, Do):
            node.body = self.visit(node.body)

        elif isinstance(node, WhileLoop):
            node.cond = self.visit(node.cond)
            node.body = self.visit(node.body)

        elif isinstance(node, RepeatLoop):
            node.body = self.visit(node.body)
            node.cond = self.visit(node.cond)

        elif isinstance(node, IfStmt):
            node.clauses = _visit_clauses(self.visit, node.clauses)
            if node.else_body:
                node.else_body = self.visit(node.else_body)

        elif isinstance(node, NumericFor):
            node.start = self.visit(node.start)
            node.stop  = self.visit(node.stop)
            node.step  = self.visit(node.step) if node.step else None
            node.body  = self.visit(node.body)

        elif isinstance(node, GenericFor):
            node.iters = _visit_list(self.visit, node.iters)
            node.body  = self.visit(node.body)

        elif isinstance(node, FuncDecl):
            node.body = self.visit(node.body)

        elif isinstance(node, FuncExpr):
            node.body = self.visit(node.body)

        elif isinstance(node, ReturnStmt):
            node.exprs = _visit_list(self.visit, node.exprs)

        elif isinstance(node, CallStmt):
            node.call_expr = self.visit(node.call_expr)

        elif isinstance(node, CallExpr):
            node.func = self.visit(node.func)
            node.args = _visit_list(self.visit, node.args)

        elif isinstance(node, MethodCallExpr):
            node.obj  = self.visit(node.obj)
            node.args = _visit_list(self.visit, node.args)

        elif isinstance(node, FieldExpr):
            node.obj = self.visit(node.obj)

        elif isinstance(node, IndexExpr):
            node.obj = self.visit(node.obj)
            node.key = self.visit(node.key)

        elif isinstance(node, BinOp):
            node.left  = self.visit(node.left)
            node.right = self.visit(node.right)

        elif isinstance(node, UnOp):
            node.operand = self.visit(node.operand)

        elif isinstance(node, TableConstructor):
            node.fields = _visit_fields(self.visit, node.fields)

        return node
