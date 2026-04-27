from lexer import tokenize

if __name__ == "__main__":
    code = ""
    with open("@template/input.lua", "r") as f:
        code = f.read()
    
    tokens = tokenize(code)
    for token in tokens:
        print(token)

    # Write to output file

    with open("@template/output.lua", "w") as f:
        for token in tokens:
            f.write(f"{token}\n")