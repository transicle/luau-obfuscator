from lexer        import tokenize
from obfuscate    import rename_vars
from parser       import parse
from scope        import analyse, format_symbol_table
from constructor  import Constructor

if __name__ == "__main__":
    code = ""
    with open("@template/input.lua", "r") as f:
        code = f.read()

    tokens         = tokenize(code)
    ast            = parse(tokens)
    obfuscated_ast = rename_vars(ast)
    table          = analyse(obfuscated_ast)

    print(obfuscated_ast)
    print()
    print(format_symbol_table(table))

    luau_output = Constructor().generate(obfuscated_ast)

    with open("@template/output.lua", "w") as f:
        f.write(luau_output)
