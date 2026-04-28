import random

from luau_ast import *
from util import random_name


def encrypt_strings(ast):
    def _string_to_bytes(raw: str) -> bytes:
        if raw.startswith("["):
            level, i = 0, 1
            while i < len(raw) and raw[i] == "=":
                level += 1
                i += 1
            content = raw[i + 1 : -(level + 2)]
            if content.startswith("\n"):
                content = content[1:]
            return content.encode("utf-8")

        quote = raw[0]
        inner = raw[1:-1]
        out = bytearray()
        i = 0
        while i < len(inner):
            if inner[i] == "\\" and i + 1 < len(inner):
                nxt = inner[i + 1]
                if nxt == "n":
                    out.append(10)
                    i += 2
                elif nxt == "t":
                    out.append(9)
                    i += 2
                elif nxt == "r":
                    out.append(13)
                    i += 2
                elif nxt == "\\":
                    out.append(92)
                    i += 2
                elif nxt == quote:
                    out.append(ord(quote))
                    i += 2
                elif nxt == "0":
                    out.append(0)
                    i += 2
                elif nxt == "x" and i + 3 < len(inner):
                    out.append(int(inner[i + 2 : i + 4], 16))
                    i += 4
                elif nxt.isdigit():
                    j = i + 1
                    while j < len(inner) and j < i + 4 and inner[j].isdigit():
                        j += 1
                    out.append(int(inner[i + 1 : j]) & 0xFF)
                    i = j
                else:
                    out.append(ord(nxt))
                    i += 2
            else:
                out.append(ord(inner[i]))
                i += 1
        return bytes(out)

    def _bytes_to_escaped(data: bytes) -> str:
        return '"' + "".join(f"\\{b}" for b in data) + '"'

    def _xor_encrypt(plain: bytes, key: list[int]) -> bytes:
        n = len(key)
        return bytes(
            plain[i] ^ key[i % n] ^ (i & 0xFF) ^ ((i >> 8) & 0xFF)
            for i in range(len(plain))
        )

    rand = random.SystemRandom()
    key_len = rand.randint(4, 8)
    key = [rand.randint(1, 255) for _ in range(key_len)]

    dec_fn = random_name(rand)
    p_str = random_name(rand)
    p_tbl = random_name(rand)
    p_idx = random_name(rand)
    p_key = random_name(rand)

    key_lua = "{" + ",".join(str(b) for b in key) + "}"
    lua_func = (
        f"local function {dec_fn}({p_str})"
        f" local {p_key}={key_lua}"
        f" local {p_tbl}={{}}"
        f" for {p_idx}=1,#{p_str} do"
        f" {p_tbl}[{p_idx}]=string.char("
        f"string.byte({p_str},{p_idx})"
        f"~{p_key}[({p_idx}-1)%#{p_key}+1]"
        f"~(({p_idx}-1)%256)"
        f"~((math.floor(({p_idx}-1)/256))%256)"
        f")"
        f" end"
        f" return table.concat({p_tbl})"
        f" end"
    )

    def _encrypt_node_string(raw: str) -> CallExpr:
        plain = _string_to_bytes(raw)
        cipher = _xor_encrypt(plain, key)
        return CallExpr(Name(dec_fn), [StringLit(_bytes_to_escaped(cipher))])

    def walk(node):
        if node is None or not isinstance(node, Node):
            return
        for attr, value in list(node.__dict__.items()):
            if isinstance(value, StringLit):
                try:
                    setattr(node, attr, _encrypt_node_string(value.value))
                except Exception:
                    pass
            elif isinstance(value, Node):
                walk(value)
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, StringLit):
                        try:
                            value[idx] = _encrypt_node_string(item.value)
                        except Exception:
                            pass
                    elif isinstance(item, Node):
                        walk(item)
                    elif isinstance(item, tuple):
                        for part in item:
                            walk(part)
            elif isinstance(value, tuple):
                for part in value:
                    walk(part)

    walk(ast)
    ast.stmts.insert(0, RawStmt(lua_func))
    return ast
