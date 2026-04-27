from lexer        import tokenize
from obfuscate    import rename_vars
from parser       import parse
from constructor  import Constructor

def minify(code):
    tokens = tokenize(code)
    ast = parse(tokens)
    obfuscated_ast = rename_vars(ast)
    return Constructor(minify=True).generate(obfuscated_ast)

if __name__ == "__main__":
    code = ""
    with open("@template/input.lua", "r") as f:
        code = f.read()

    luau_output = minify(code)

    with open("@template/output.lua", "w") as f:
        f.write(luau_output)
