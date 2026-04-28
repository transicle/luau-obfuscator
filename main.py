from lexer     import tokenize
from rename    import rename_vars
from encrypt   import encrypt_strings
from dead_code import inject_dead_code
from parser    import parse
from constructor import Constructor

def minify(code):
    tokens = tokenize(code)
    ast = parse(tokens)
    ast = encrypt_strings(ast)
    ast = rename_vars(ast)
    obfuscated_ast = inject_dead_code(ast)
    return Constructor(minify=True).generate(obfuscated_ast)

if __name__ == "__main__":
    code = ""
    with open("@template/input.lua", "r") as f:
        code = f.read()

    luau_output = minify(code)

    with open("@template/output.lua", "w") as f:
        f.write(luau_output)
