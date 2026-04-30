from tokens import *

_SYMBOLS_SORTED = sorted(SYMBOLS, key=len, reverse=True)


def tokenize(code):
    tokens = []
    i = 0
    n = len(code)

    while i < n:
        if code[i].isspace():
            i += 1
            continue

        if code[i : i + 2] == "--" and code[i : i + 4] != "--[[":
            while i < n and code[i] != "\n":
                i += 1
            continue

        if code[i : i + 4] == "--[[":
            i += 4
            while i < n and code[i : i + 2] != "]]":
                i += 1
            i += 2
            continue

        if code[i] == '"':
            j = i + 1
            while j < n and code[j] != '"':
                if code[j] == "\\":
                    j += 1
                j += 1
            j += 1
            tokens.append(make_token("STRING", code[i:j]))
            i = j
            continue

        if code[i] == "'":
            j = i + 1
            while j < n and code[j] != "'":
                if code[j] == "\\":
                    j += 1
                j += 1
            j += 1
            tokens.append(make_token("STRING", code[i:j]))
            i = j
            continue

        if code[i] == "`":
            j = i + 1
            while j < n and code[j] != "`":
                if code[j] == "\\":
                    j += 1
                j += 1
            j += 1
            tokens.append(make_token("INTERP_STRING", code[i:j]))
            i = j
            continue

        if code[i] == "[" and i + 1 < n and code[i + 1] in ("[", "="):
            level = 0
            k = i + 1
            while k < n and code[k] == "=":
                level += 1
                k += 1
            if k < n and code[k] == "[":
                close = "]" + "=" * level + "]"
                end = code.find(close, k + 1)
                if end != -1:
                    j = end + len(close)
                    tokens.append(make_token("STRING", code[i:j]))
                    i = j
                    continue

        if code[i].isdigit() or (
            code[i] == "." and i + 1 < n and code[i + 1].isdigit()
        ):
            j = i
            if code[j : j + 2] in ("0x", "0X"):
                j += 2
                while j < n and (code[j] in "0123456789abcdefABCDEF_"):
                    j += 1
            elif code[j : j + 2] in ("0b", "0B"):
                j += 2
                while j < n and code[j] in "01_":
                    j += 1
            else:
                while j < n and (code[j].isdigit() or code[j] == "_"):
                    j += 1
                if j < n and code[j] == ".":
                    j += 1
                    while j < n and (code[j].isdigit() or code[j] == "_"):
                        j += 1
                if j < n and code[j] in "eE":
                    j += 1
                    if j < n and code[j] in "+-":
                        j += 1
                    while j < n and code[j].isdigit():
                        j += 1
            tokens.append(make_token("NUMBER", code[i:j]))
            i = j
            continue

        if code[i] == "@":
            j = i + 1
            while j < n and (code[j].isalnum() or code[j] == "_"):
                j += 1
            word = code[i:j]
            if word in ATTRIBUTES:
                tokens.append(make_token("ATTRIBUTE", word))
            else:
                tokens.append(make_token("UNKNOWN", word))
            i = j
            continue

        matched_sym = False
        for sym in _SYMBOLS_SORTED:
            if code[i : i + len(sym)] == sym:
                tokens.append(make_token("SYMBOL", sym))
                i += len(sym)
                matched_sym = True
                break
        if matched_sym:
            continue

        if code[i].isalpha() or code[i] == "_":
            j = i
            while j < n and (code[j].isalnum() or code[j] == "_"):
                j += 1
            word = code[i:j]
            if word in KEYWORDS:
                tokens.append(make_token("KEYWORD", word))
            elif word in VAR_DECLS:
                tokens.append(make_token("VAR_DECL", word))
            elif word in TYPES:
                tokens.append(make_token("TYPE", word))
            elif word in BUILTINS:
                tokens.append(make_token("BUILTIN", word))
            else:
                tokens.append(make_token("IDENTIFIER", word))
            i = j
            continue

        tokens.append(make_token("UNKNOWN", code[i]))
        i += 1

    return tokens
