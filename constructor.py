from luau_ast import *


class Constructor:
    def __init__(self, indent_str="    "):
        self.indent_str = indent_str
        self._depth = 0

    def _indent(self):
        return self.indent_str * self._depth

    def _block(self, node):
        self._depth += 1
        lines = [self._stmt(s) for s in node.stmts]
        self._depth -= 1
        return "\n".join(lines)

    def _expr_list(self, exprs):
        return ", ".join(self._expr(e) for e in exprs)

    def _name_list(self, names):
        return ", ".join(names)

    def generate(self, ast):
        lines = [self._stmt(s) for s in ast.stmts]
        return "\n".join(lines)

    def _stmt(self, node):
        ind = self._indent()
        if isinstance(node, LocalDecl):
            names = self._name_list(node.names)
            if node.exprs:
                return f"{ind}local {names} = {self._expr_list(node.exprs)}"
            return f"{ind}local {names}"

        if isinstance(node, Assign):
            targets = ", ".join(self._expr(t) for t in node.targets)
            return f"{ind}{targets} = {self._expr_list(node.exprs)}"

        if isinstance(node, Do):
            body = self._block(node.body)
            return f"{ind}do\n{body}\n{ind}end"

        if isinstance(node, WhileLoop):
            body = self._block(node.body)
            return f"{ind}while {self._expr(node.cond)} do\n{body}\n{ind}end"

        if isinstance(node, RepeatLoop):
            body = self._block(node.body)
            return f"{ind}repeat\n{body}\n{ind}until {self._expr(node.cond)}"

        if isinstance(node, IfStmt):
            return self._if_stmt(node)

        if isinstance(node, NumericFor):
            parts = [self._expr(node.start), self._expr(node.stop)]
            if node.step:
                parts.append(self._expr(node.step))
            body = self._block(node.body)
            return f"{ind}for {node.var} = {', '.join(parts)} do\n{body}\n{ind}end"

        if isinstance(node, GenericFor):
            names = self._name_list(node.names)
            iters = self._expr_list(node.iters)
            body = self._block(node.body)
            return f"{ind}for {names} in {iters} do\n{body}\n{ind}end"

        if isinstance(node, FuncDecl):
            return self._func_decl(node)

        if isinstance(node, ReturnStmt):
            if node.exprs:
                return f"{ind}return {self._expr_list(node.exprs)}"
            return f"{ind}return"

        if isinstance(node, BreakStmt):
            return f"{ind}break"

        if isinstance(node, ContinueStmt):
            return f"{ind}continue"

        if isinstance(node, CallStmt):
            return f"{ind}{self._expr(node.call_expr)}"

        raise NotImplementedError(f"_stmt: unhandled {type(node).__name__}")

    def _if_stmt(self, node):
        ind = self._indent()
        parts = []
        for i, (cond, body) in enumerate(node.clauses):
            keyword = "if" if i == 0 else "elseif"
            body_src = self._block(body)
            parts.append(f"{ind}{keyword} {self._expr(cond)} then\n{body_src}")
        if node.else_body:
            body_src = self._block(node.else_body)
            parts.append(f"{ind}else\n{body_src}")
        return "\n".join(parts) + f"\n{ind}end"

    def _func_decl(self, node):
        ind = self._indent()
        prefix = "local " if node.is_local else ""
        params = self._name_list(node.params)
        body = self._block(node.body)
        return f"{ind}{prefix}function {node.name}({params})\n{body}\n{ind}end"

    def _expr(self, node):
        if isinstance(node, Name):
            return node.name

        if isinstance(node, NumberLit):
            return node.value

        if isinstance(node, StringLit):
            return node.value

        if isinstance(node, BoolLit):
            return "true" if node.value else "false"

        if isinstance(node, NilLit):
            return "nil"

        if isinstance(node, VarArgExpr):
            return "..."

        if isinstance(node, BinOp):
            return f"{self._expr(node.left)} {node.op} {self._expr(node.right)}"

        if isinstance(node, UnOp):
            sep = "" if node.op == "#" else " "
            return f"{node.op}{sep}{self._expr(node.operand)}"

        if isinstance(node, FieldExpr):
            return f"{self._expr(node.obj)}.{node.field}"

        if isinstance(node, IndexExpr):
            return f"{self._expr(node.obj)}[{self._expr(node.key)}]"

        if isinstance(node, MethodCallExpr):
            args = self._expr_list(node.args)
            return f"{self._expr(node.obj)}:{node.method}({args})"

        if isinstance(node, CallExpr):
            args = self._expr_list(node.args)
            return f"{self._expr(node.func)}({args})"

        if isinstance(node, FuncExpr):
            params = self._name_list(node.params)
            body = self._block(node.body)
            ind = self._indent()
            return f"function({params})\n{body}\n{ind}end"

        if isinstance(node, TableConstructor):
            return self._table(node)

        raise NotImplementedError(f"_expr: unhandled {type(node).__name__}")

    def _table(self, node):
        if not node.fields:
            return "{}"
        self._depth += 1
        ind = self._indent()
        items = []
        for key, value in node.fields:
            if key is None:
                items.append(f"{ind}{self._expr(value)}")
            elif isinstance(key, Name):
                items.append(f"{ind}{key.name} = {self._expr(value)}")
            else:
                items.append(f"{ind}[{self._expr(key)}] = {self._expr(value)}")
        self._depth -= 1
        outer = self._indent()
        body = ",\n".join(items)
        return f"{{\n{body},\n{outer}}}"
