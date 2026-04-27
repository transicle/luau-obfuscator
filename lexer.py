from tokens import *

def skip_whitespace(code, index):
    while index < len(code) and code[index].isspace():
        index += 1
    return index

def tokenize(code):
    tokens = []
    skip_whitespace(code, 0)
    for word in code.split():
        if word in VAR_DECLS:
            tokens.append(make_token("VAR_DECL", word))
        elif word in SYMBOLS:
            tokens.append(make_token("SYMBOL", word))
        else:
            tokens.append(make_token("IDENTIFIER", word))
    return tokens