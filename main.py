import pprint

from lexer import tokenize
from parser import parse

if __name__ == "__main__":
    code = ""
    with open("@template/input.lua", "r") as f:
        code = f.read()
    
    tokens = tokenize(code)
    ast = parse(tokens)

    pprint.pprint(ast)

    # Write to output file
    with open("@template/output.lua", "w") as f:
        f.write(repr(ast))