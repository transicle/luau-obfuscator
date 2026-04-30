from lexer     import tokenize
from rename    import rename_vars
from encrypt   import encrypt_strings
from builtin_table import obfuscate_builtins
from dead_code import inject_dead_code
from control_flow import flatten_control_flow
from opaque import inject_opaque_predicates
from substitute import encode_numeric_literals
from expand_expr import expand_expressions
from bytecode import wrap_bytecode
from parser    import parse
from constructor import Constructor

def minify(code):
    tokens = tokenize(code)
    ast = parse(tokens)

    ast = encrypt_strings(ast)
    ast = encode_numeric_literals(ast)
    ast = expand_expressions(ast)
    ast = inject_opaque_predicates(ast)
    ast = flatten_control_flow(ast)
    ast = rename_vars(ast)
    ast = obfuscate_builtins(ast)
    obfuscated_ast = inject_dead_code(ast)

    generated = Constructor(minify=True).generate(obfuscated_ast)
    return wrap_bytecode(generated)

if __name__ == "__main__":
    code = ""
    with open("@template/input.lua", "r") as f:
        code = f.read()

    luau_output = minify(code)

    with open("@template/output.lua", "w") as f:
        f.write(luau_output)
