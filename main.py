from lexer  import tokenize
from parser import parse, pretty_parse
from scope  import analyse, format_symbol_table

if __name__ == "__main__":
    code = ""
    with open("@template/input.lua", "r") as f:
        code = f.read()

    tokens  = tokenize(code)
    ast     = parse(tokens)
    table   = analyse(ast)

    print(ast)
    print()
    print(format_symbol_table(table))

    # Write pretty AST to output file
    with open("@template/output.lua", "w") as f:
        f.write(pretty_parse(tokens))
