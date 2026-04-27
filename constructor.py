from luau_ast import *


class Constructor:
    BIN_PRECEDENCE = {
        "or": 1,
        "and": 2,
        "<": 3,
        ">": 3,
        "<=": 3,
        ">=": 3,
        "==": 3,
        "~=": 3,
        "|": 4,
        "&": 5,
        "..": 6,
        "+": 7,
        "-": 7,
        "*": 8,
        "/": 8,
        "//": 8,
        "%": 8,
        "^": 10,
    }
    RIGHT_ASSOCIATIVE = {"..", "^"}
    UNARY_PRECEDENCE = 9

    def __init__(self, indent_str="    ", minify=False):
        self.indent_str = indent_str
        self.minify = minify
        self._depth = 0

    def _indent(self):
        if self.minify:
            return ""
        return self.indent_str * self._depth

    def _block(self, node):
        self._depth += 1
        lines = [self._stmt(s) for s in node.stmts]
        self._depth -= 1
        if self.minify:
            return ";".join(lines)
        return "\n".join(lines)

    def _expr_list(self, exprs):
        if self.minify:
            return ",".join(self._expr(e) for e in exprs)
        return ", ".join(self._expr(e) for e in exprs)

    def _name_list(self, names):
        if self.minify:
            return ",".join(names)
        return ", ".join(names)

    def generate(self, ast):
        lines = [self._stmt(s) for s in ast.stmts]
        if self.minify:
            return ";".join(lines)
        return "\n".join(lines)

    def _wrap_block(self, body):
        if not body:
            return ""
        if self.minify:
            return f" {body}"
        return f"\n{body}"

    def _expr_prec(self, node):
        if isinstance(node, BinOp):
            return self.BIN_PRECEDENCE[node.op]
        if isinstance(node, UnOp):
            return self.UNARY_PRECEDENCE
        return 99

    def _maybe_paren(self, node, text, parent_prec, side):
        if parent_prec is None:
            return text
        prec = self._expr_prec(node)
        if prec < parent_prec:
            return f"({text})"
        if isinstance(node, BinOp) and prec == parent_prec:
            if side == "left" and node.op in self.RIGHT_ASSOCIATIVE:
                return f"({text})"
            if side == "right" and node.op not in self.RIGHT_ASSOCIATIVE:
                return f"({text})"
        return text

    def _op_sep(self, op):
        if self.minify and op not in {"and", "or"}:
            return ""
        return " "

    def _stmt(self, node):
        ind = self._indent()
        if isinstance(node, LocalDecl):
            names = self._name_list(node.names)
            if node.exprs:
                eq = "=" if self.minify else " = "
                return f"{ind}local {names}{eq}{self._expr_list(node.exprs)}"
            return f"{ind}local {names}"

        if isinstance(node, Assign):
            target_sep = "," if self.minify else ", "
            targets = target_sep.join(self._expr(t) for t in node.targets)
            eq = "=" if self.minify else " = "
            return f"{ind}{targets}{eq}{self._expr_list(node.exprs)}"

        if isinstance(node, Do):
            body = self._block(node.body)
            if self.minify:
                return f"{ind}do{self._wrap_block(body)} end"
            return f"{ind}do\n{body}\n{ind}end"

        if isinstance(node, WhileLoop):
            body = self._block(node.body)
            cond = self._expr(node.cond)
            if self.minify:
                return f"{ind}while {cond} do{self._wrap_block(body)} end"
            return f"{ind}while {self._expr(node.cond)} do\n{body}\n{ind}end"

        if isinstance(node, RepeatLoop):
            body = self._block(node.body)
            cond = self._expr(node.cond)
            if self.minify:
                return f"{ind}repeat{self._wrap_block(body)} until {cond}"
            return f"{ind}repeat\n{body}\n{ind}until {self._expr(node.cond)}"

        if isinstance(node, IfStmt):
            return self._if_stmt(node)

        if isinstance(node, NumericFor):
            parts = [self._expr(node.start), self._expr(node.stop)]
            if node.step:
                parts.append(self._expr(node.step))
            body = self._block(node.body)
            sep = "," if self.minify else ", "
            if self.minify:
                return f"{ind}for {node.var}={sep.join(parts)} do{self._wrap_block(body)} end"
            return f"{ind}for {node.var} = {', '.join(parts)} do\n{body}\n{ind}end"

        if isinstance(node, GenericFor):
            names = self._name_list(node.names)
            iters = self._expr_list(node.iters)
            body = self._block(node.body)
            if self.minify:
                return f"{ind}for {names} in {iters} do{self._wrap_block(body)} end"
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
            if self.minify:
                parts.append(f"{ind}{keyword} {self._expr(cond)} then{self._wrap_block(body_src)}")
                continue
            parts.append(f"{ind}{keyword} {self._expr(cond)} then\n{body_src}")
        if node.else_body:
            body_src = self._block(node.else_body)
            if self.minify:
                parts.append(f"{ind}else{self._wrap_block(body_src)}")
            else:
                parts.append(f"{ind}else\n{body_src}")
        if self.minify:
            return " ".join(parts) + f" end"
        return "\n".join(parts) + f"\n{ind}end"

    def _func_decl(self, node):
        ind = self._indent()
        prefix = "local " if node.is_local else ""
        params = self._name_list(node.params)
        body = self._block(node.body)
        if self.minify:
            return f"{ind}{prefix}function {node.name}({params}){self._wrap_block(body)} end"
        return f"{ind}{prefix}function {node.name}({params})\n{body}\n{ind}end"

    def _expr(self, node, parent_prec=None, side=None):
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
            prec = self.BIN_PRECEDENCE[node.op]
            left = self._expr(node.left, prec, "left")
            right = self._expr(node.right, prec, "right")
            op_sep = self._op_sep(node.op)
            text = f"{left}{op_sep}{node.op}{op_sep}{right}"
            return self._maybe_paren(node, text, parent_prec, side)

        if isinstance(node, UnOp):
            sep = "" if node.op == "#" else " "
            if self.minify and node.op != "not":
                sep = ""
            text = f"{node.op}{sep}{self._expr(node.operand, self.UNARY_PRECEDENCE, 'right')}"
            return self._maybe_paren(node, text, parent_prec, side)

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
            if self.minify:
                return f"function({params}){self._wrap_block(body)} end"
            return f"function({params})\n{body}\n{ind}end"

        if isinstance(node, TableConstructor):
            return self._table(node)

        raise NotImplementedError(f"_expr: unhandled {type(node).__name__}")

    def _table(self, node):
        if not node.fields:
            return "{}"
        if self.minify:
            items = []
            for key, value in node.fields:
                if key is None:
                    items.append(self._expr(value))
                elif isinstance(key, str):
                    items.append(f"{key}={self._expr(value)}")
                elif isinstance(key, Name):
                    items.append(f"{key.name}={self._expr(value)}")
                else:
                    items.append(f"[{self._expr(key)}]={self._expr(value)}")
            return "{" + ",".join(items) + "}"

        self._depth += 1
        ind = self._indent()
        items = []
        for key, value in node.fields:
            if key is None:
                items.append(f"{ind}{self._expr(value)}")
            elif isinstance(key, str):
                items.append(f"{ind}{key} = {self._expr(value)}")
            elif isinstance(key, Name):
                items.append(f"{ind}{key.name} = {self._expr(value)}")
            else:
                items.append(f"{ind}[{self._expr(key)}] = {self._expr(value)}")
        self._depth -= 1
        outer = self._indent()
        body = ",\n".join(items)
        return f"{{\n{body},\n{outer}}}"
