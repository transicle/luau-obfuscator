from luau_ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        return self.tokens[self.pos + offset] if self.pos + offset < len(self.tokens) else None

    def at_end(self):
        return self.pos >= len(self.tokens)

    def check(self, *values):
        token = self.peek()
        return token is not None and token.value in values

    def check_type(self, *types):
        token = self.peek()
        return token is not None and token.type in types

    def advance(self):
        if not self.at_end():
            self.pos += 1
        return self.peek(-1)

    def consume(self, *values):
        if self.check(*values):
            return self.advance()
        return None

    def expect(self, value):
        token = self.consume(value)
        if token is None:
            raise SyntaxError(f"Expected '{value}'")
        return token

    def expect_type(self, *types):
        token = self.consume_type(*types)
        if token is None:
            raise SyntaxError(f"Expected one of types: {types}")
        return token

    def parse_block(self):
        pass

    def parse_stmt(self):
        pass

    def parse_local(self):
        pass

    def parse_function_decl(self, is_local):
        pass

    def parse_func_body(self, is_method=False):
        pass

    def parse_if(self):
        pass

    def parse_while(self):
        pass

    def parse_repeat(self):
        pass

    def parse_for(self):
        pass

    def parse_return(self):
        pass

    def parse_expr_stat(self):
        pass

    def parse_expr_list(self):
        pass

    def parse_expr(self, min_prec=0):
        pass

    def parse_unary(self):
        pass

    def parse_suffixed_expr(self):
        pass

    def parse_primary(self):
        pass

    def parse_call_args(self):
        pass

    def parse_table_constructor(self):
        pass

def parse(tokens):
    pass