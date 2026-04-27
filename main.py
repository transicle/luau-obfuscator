from lexer import tokenize
from parser import parse, pretty_parse

if __name__ == "__main__":
    code = ""
    with open("@template/input.lua", "r") as f:
        code = f.read()

    tokens = tokenize(code)
    ast = parse(tokens)
    pretty_ast = pretty_parse(tokens)

    print(ast)

    # Write to output file
    with open("@template/output.lua", "w") as f:
        f.write(pretty_ast)
