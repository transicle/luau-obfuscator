import pprint

from luau_ast import *


class Parser:
    PRECEDENCE = {
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

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        idx = self.pos + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def at_end(self):
        return self.pos >= len(self.tokens)

    def check(self, *values):
        token = self.peek()
        return token is not None and token.value in values

    def check_type(self, *types):
        token = self.peek()
        return token is not None and token.type in types

    def advance(self):
        token = self.peek()
        if token is not None:
            self.pos += 1
        return token

    def consume(self, *values):
        if self.check(*values):
            return self.advance()
        return None

    def expect(self, value):
        token = self.consume(value)
        if token is None:
            got = self.peek().value if self.peek() is not None else "EOF"
            raise SyntaxError(f"Expected '{value}', got '{got}'")
        return token

    def consume_type(self, *types):
        if self.check_type(*types):
            return self.advance()
        return None

    def expect_type(self, *types):
        token = self.consume_type(*types)
        if token is None:
            got = self.peek().type if self.peek() is not None else "EOF"
            raise SyntaxError(f"Expected one of types {types}, got '{got}'")
        return token

    def parse_block(self):
        stmts = []
        while not self.at_end() and not self.check("end", "else", "elseif", "until"):
            stmt = self.parse_stmt()
            if stmt is not None:
                stmts.append(stmt)
            self.consume(";")
        return Block(stmts)

    def parse_stmt(self):
        if self.check("local"):
            return self.parse_local()
        if self.check("function"):
            return self.parse_function_decl(is_local=False)
        if self.check("if"):
            return self.parse_if()
        if self.check("while"):
            return self.parse_while()
        if self.check("repeat"):
            return self.parse_repeat()
        if self.check("for"):
            return self.parse_for()
        if self.check("return"):
            return self.parse_return()
        if self.check("break"):
            self.advance()
            return BreakStmt()
        if self.check("continue"):
            self.advance()
            return ContinueStmt()
        return self.parse_expr_stat()

    def parse_local(self):
        self.expect("local")

        if self.consume("function"):
            name = self.expect_type("IDENTIFIER", "BUILTIN").value
            params, body = self.parse_func_body()
            return FuncDecl(name, params, body, is_local=True)

        names = []
        while True:
            token = self.expect_type("IDENTIFIER", "BUILTIN")
            names.append(token.value)
            if not self.consume(","):
                break

        exprs = []
        if self.consume("="):
            exprs = self.parse_expr_list()

        return LocalDecl(names, exprs)

    def parse_function_decl(self, is_local):
        self.expect("function")
        name, is_method = self.parse_func_name()
        params, body = self.parse_func_body(is_method=is_method)
        return FuncDecl(name, params, body, is_local=is_local, is_method=is_method)

    def parse_func_name(self):
        name = self.expect_type("IDENTIFIER", "BUILTIN").value
        is_method = False

        while self.consume("."):
            field = self.expect_type("IDENTIFIER", "BUILTIN").value
            name = f"{name}.{field}"

        if self.consume(":"):
            method = self.expect_type("IDENTIFIER", "BUILTIN").value
            name = f"{name}:{method}"
            is_method = True

        return name, is_method

    def parse_func_body(self, is_method=False):
        self.expect("(")
        params = ["self"] if is_method else []

        if not self.check(")"):
            while True:
                if self.check("..."):
                    self.advance()
                    params.append("...")
                    break
                token = self.expect_type("IDENTIFIER", "BUILTIN")
                params.append(token.value)
                if not self.consume(","):
                    break

        self.expect(")")
        body = self.parse_block()
        self.expect("end")
        return params, body

    def parse_if(self):
        clauses = []
        else_body = None

        self.expect("if")
        cond = self.parse_expr()
        self.expect("then")
        then_body = self.parse_block()
        clauses.append((cond, then_body))

        while self.consume("elseif"):
            cond = self.parse_expr()
            self.expect("then")
            then_body = self.parse_block()
            clauses.append((cond, then_body))

        if self.consume("else"):
            else_body = self.parse_block()

        self.expect("end")
        return IfStmt(clauses, else_body)

    def parse_while(self):
        self.expect("while")
        cond = self.parse_expr()
        self.expect("do")
        body = self.parse_block()
        self.expect("end")
        return WhileLoop(cond, body)

    def parse_repeat(self):
        self.expect("repeat")
        body = self.parse_block()
        self.expect("until")
        cond = self.parse_expr()
        return RepeatLoop(body, cond)

    def parse_for(self):
        self.expect("for")
        token = self.expect_type("IDENTIFIER", "BUILTIN")
        var = token.value

        if self.consume("="):
            start = self.parse_expr()
            self.expect(",")
            stop = self.parse_expr()
            step = None
            if self.consume(","):
                step = self.parse_expr()
            self.expect("do")
            body = self.parse_block()
            self.expect("end")
            return NumericFor(var, start, stop, step, body)

        names = [var]
        while self.consume(","):
            token = self.expect_type("IDENTIFIER", "BUILTIN")
            names.append(token.value)
        self.expect("in")
        iters = self.parse_expr_list()
        self.expect("do")
        body = self.parse_block()
        self.expect("end")
        return GenericFor(names, iters, body)

    def parse_return(self):
        self.expect("return")
        exprs = []
        if not self.check("end", "else", "elseif", "until", ";") and not self.at_end():
            exprs = self.parse_expr_list()
        return ReturnStmt(exprs)

    def parse_expr_stat(self):
        first = self.parse_suffixed_expr()

        if self.check(",", "="):
            targets = [first]
            while self.consume(","):
                targets.append(self.parse_suffixed_expr())
            self.expect("=")
            exprs = self.parse_expr_list()
            return Assign(targets, exprs)

        if isinstance(first, (CallExpr, MethodCallExpr)):
            return CallStmt(first)

        raise SyntaxError("Invalid statement: expected assignment or function call")

    def parse_expr_list(self):
        exprs = [self.parse_expr()]
        while self.consume(","):
            exprs.append(self.parse_expr())
        return exprs

    def get_precedence(self, op):
        return self.PRECEDENCE.get(op, -1)

    def parse_expr(self, min_prec=0):
        expr = self.parse_unary()

        while True:
            op = self.peek()
            if op is None:
                break

            prec = self.get_precedence(op.value)
            if prec < min_prec:
                break

            self.advance()
            next_min_prec = prec if op.value in self.RIGHT_ASSOCIATIVE else prec + 1
            right = self.parse_expr(next_min_prec)
            expr = BinOp(op.value, expr, right)

        return expr

    def parse_unary(self):
        if self.check("-", "not", "#"):
            op = self.advance().value
            operand = self.parse_unary()
            return UnOp(op, operand)
        return self.parse_suffixed_expr()

    def parse_primary(self):
        token = self.peek()
        if token is None:
            raise SyntaxError("Unexpected end of input")

        if token.type == "NUMBER":
            self.advance()
            return NumberLit(token.value)
        if token.type in ("STRING", "INTERP_STRING"):
            self.advance()
            return StringLit(token.value)
        if token.type == "KEYWORD" and token.value in ("true", "false"):
            self.advance()
            return BoolLit(token.value == "true")
        if token.type == "KEYWORD" and token.value == "nil":
            self.advance()
            return NilLit()
        if token.type == "SYMBOL" and token.value == "...":
            self.advance()
            return VarArgExpr()
        if token.type in ("IDENTIFIER", "BUILTIN"):
            self.advance()
            return Name(token.value)
        if token.type == "SYMBOL" and token.value == "(":
            self.advance()
            expr = self.parse_expr()
            self.expect(")")
            return expr
        if token.type == "SYMBOL" and token.value == "{":
            return self.parse_table_constructor()
        if token.type == "KEYWORD" and token.value == "function":
            self.advance()
            params, body = self.parse_func_body()
            return FuncExpr(params, body)

        raise SyntaxError(f"Unexpected token: {token}")

    def parse_suffixed_expr(self):
        expr = self.parse_primary()

        while True:
            if self.consume("."):
                field = self.expect_type("IDENTIFIER", "BUILTIN").value
                expr = FieldExpr(expr, field)
            elif self.consume(":"):
                method = self.expect_type("IDENTIFIER", "BUILTIN").value
                args = self.parse_call_args()
                expr = MethodCallExpr(expr, method, args)
            elif self.consume("["):
                key = self.parse_expr()
                self.expect("]")
                expr = IndexExpr(expr, key)
            elif self.check("("):
                args = self.parse_call_args()
                expr = CallExpr(expr, args)
            else:
                break

        return expr

    def parse_call_args(self):
        if self.consume("("):
            args = []
            if not self.check(")"):
                while True:
                    args.append(self.parse_expr())
                    if not self.consume(","):
                        break
            self.expect(")")
            return args
        if self.check("{"):
            return [self.parse_table_constructor()]
        if self.check_type("STRING", "INTERP_STRING"):
            return [StringLit(self.advance().value)]
        raise SyntaxError("Expected function call arguments")

    def parse_table_constructor(self):
        self.expect("{")
        fields = []

        while not self.check("}"):
            if self.check("["):
                self.advance()
                key = self.parse_expr()
                self.expect("]")
                self.expect("=")
                value = self.parse_expr()
                fields.append((key, value))
            elif (
                self.check_type("IDENTIFIER", "BUILTIN")
                and self.peek(1) is not None
                and self.peek(1).value == "="
            ):
                key = self.advance().value
                self.expect("=")
                value = self.parse_expr()
                fields.append((key, value))
            else:
                value = self.parse_expr()
                fields.append((None, value))

            if not self.consume(",") and not self.consume(";"):
                break

        self.expect("}")
        return TableConstructor(fields)


def parse(tokens):
    parser = Parser(tokens)
    block = parser.parse_block()
    if not parser.at_end():
        token = parser.peek()
        raise SyntaxError(f"Unexpected token at top level: {token}")
    return block


def pretty_parse(tokens):
    ast = parse(tokens)

    def to_data(value):
        if isinstance(value, Node):
            data = {"type": value.__class__.__name__}
            for key, node_value in value.__dict__.items():
                data[key] = to_data(node_value)
            return data
        if isinstance(value, list):
            return [to_data(item) for item in value]
        if isinstance(value, tuple):
            return tuple(to_data(item) for item in value)
        return value

    return pprint.pformat(to_data(ast), sort_dicts=False, width=100, compact=False)