import random

from luau_ast import RawStmt
from util import random_name


def _fresh_name(rand, used):
    while True:
        name = random_name(rand)
        if name not in used:
            used.add(name)
            return name


def _collect_existing_names(ast):
    names = set()

    def walk(node):
        if node is None:
            return
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if isinstance(node, tuple):
            for item in node:
                walk(item)
            return
        if not hasattr(node, "__dict__"):
            return

        kind = type(node).__name__
        if kind == "Name":
            names.add(node.name)
        elif kind == "LocalDecl":
            for n in node.names:
                names.add(n)
        elif kind == "FuncDecl":
            if "." not in node.name and ":" not in node.name:
                names.add(node.name)
            for p in node.params:
                if p != "...":
                    names.add(p)
        elif kind == "FuncExpr":
            for p in node.params:
                if p != "...":
                    names.add(p)
        elif kind == "NumericFor":
            names.add(node.var)
        elif kind == "GenericFor":
            for n in node.names:
                names.add(n)

        for value in node.__dict__.values():
            walk(value)

    walk(ast)
    return names


def _lua_quote(text):
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _chunk_concat(text, rand):
    parts = []
    i = 0
    while i < len(text):
        step = rand.randint(2, 5)
        parts.append(_lua_quote(text[i : i + step]))
        i += step
    return "..".join(parts) if parts else '""'


def _rand_blob(rand):
    alphabet = "abcdef0123456789"
    size = rand.randint(20, 42)
    return "".join(rand.choice(alphabet) for _ in range(size))


def _rand_expr(rand, depth=0):
    if depth > 2 or rand.random() < 0.35:
        return str(rand.randint(0, 2048))
    left = _rand_expr(rand, depth + 1)
    right = _rand_expr(rand, depth + 1)
    op = rand.choice(["+", "-", "*", "~", "%"])
    if op == "%":
        right = str(rand.randint(3, 251))
    return f"(({left}){op}({right}))"


def _common_names(rand, used):
    nonce_name = _fresh_name(rand, used)
    table_name = _fresh_name(rand, used)
    nonce_key_name = _fresh_name(rand, used)
    sig_key_name = _fresh_name(rand, used)
    ttl_key_name = _fresh_name(rand, used)
    func_name = _fresh_name(rand, used)
    arg_a = _fresh_name(rand, used)
    arg_b = _fresh_name(rand, used)
    tmp_name = _fresh_name(rand, used)
    idx_name = _fresh_name(rand, used)
    marker_name = _fresh_name(rand, used)
    return {
        "nonce_name": nonce_name,
        "table_name": table_name,
        "nonce_key_name": nonce_key_name,
        "sig_key_name": sig_key_name,
        "ttl_key_name": ttl_key_name,
        "func_name": func_name,
        "arg_a": arg_a,
        "arg_b": arg_b,
        "tmp_name": tmp_name,
        "idx_name": idx_name,
        "marker_name": marker_name,
    }


def _entropy_prelude(rand, used):
    seed_name = _fresh_name(rand, used)
    ok_time = _fresh_name(rand, used)
    val_time = _fresh_name(rand, used)
    ok_clock = _fresh_name(rand, used)
    val_clock = _fresh_name(rand, used)
    ok_dt = _fresh_name(rand, used)
    val_dt = _fresh_name(rand, used)
    round_idx = _fresh_name(rand, used)

    prelude = (
        f"local {seed_name}=0;"
        f"local {ok_time},{val_time}=pcall(function() return (os and os.time and os.time()) or 0 end);"
        f"if {ok_time} and tonumber({val_time})~=nil then {seed_name}=({seed_name}+{val_time})%2147483647 end;"
        f"local {ok_clock},{val_clock}=pcall(function() return (os and os.clock and os.clock()) or 0 end);"
        f"if {ok_clock} and tonumber({val_clock})~=nil then {seed_name}=({seed_name}+math.floor({val_clock}*1000000))%2147483647 end;"
        f"local {ok_dt},{val_dt}=pcall(function() return DateTime.now().UnixTimestampMillis end);"
        f"if {ok_dt} and tonumber({val_dt})~=nil then {seed_name}=({seed_name}+{val_dt})%2147483647 end;"
        f"for {round_idx}=1,{rand.randint(2,5)} do {seed_name}=(({seed_name}*1103515245)+12345)%2147483647 end;"
    )
    return seed_name, prelude


def _dead_block_alpha(rand, used):
    n = _common_names(rand, used)
    seed_name, seed_code = _entropy_prelude(rand, used)

    base = rand.randint(10_000, 999_999)
    salt = rand.randint(100, 9_999)
    marker = _rand_blob(rand)
    chunked_marker = _chunk_concat(marker, rand)
    ttl_expr = _rand_expr(rand)
    slot_name = _fresh_name(rand, used)
    fake_cmp = rand.randint(650, 1400)

    return (
        seed_code
        +
        f"local {n['nonce_name']}=((({base}*7)-({base}*7))+{salt}+({seed_name}%997));"
        f"local {n['marker_name']}={chunked_marker};"
        f"local {n['table_name']}={{{n['nonce_key_name']}={n['nonce_name']},{n['sig_key_name']}={n['marker_name']},{n['ttl_key_name']}={ttl_expr}}};"
        f"local function {n['func_name']}({n['arg_a']},{n['arg_b']})"
        f" local {n['tmp_name']}=(({n['arg_a']}*3)+({n['arg_b']}*11))%257;"
        f" if {n['tmp_name']}==-1 then return ({_lua_quote('X')}..{_lua_quote('Y')}) end;"
        f" return ({n['tmp_name']}~{n['tmp_name']})+({n['nonce_name']}%1)+(({seed_name}%3)-({seed_name}%3))"
        f" end;"
        f"if (({n['nonce_name']}%2)==1 and ({n['nonce_name']}%2)==0) or (#tostring({n['table_name']}.{n['sig_key_name']})<0) then "
        f"{n['func_name']}({rand.randint(1,9)},{rand.randint(1,9)}) end;"
        f"do local {n['tmp_name']}={{}};"
        f"for {n['idx_name']}=1,3 do {n['tmp_name']}[{n['idx_name']}]=(({n['idx_name']}*11)~{n['idx_name']})%256 end;"
        f"if {n['tmp_name']}[1]=={fake_cmp} then {n['table_name']}.{n['ttl_key_name']}={n['tmp_name']}[1] end;"
        f"local {slot_name}=({n['table_name']}.{n['ttl_key_name']}~{n['table_name']}.{n['ttl_key_name']})+(({seed_name}%17)-({seed_name}%17));"
        f"if ({seed_name}%19)==23 then {n['table_name']}.{n['ttl_key_name']}={slot_name} end"
        f" end"
    )


def _dead_block_beta(rand, used):
    n = _common_names(rand, used)
    seed_name, seed_code = _entropy_prelude(rand, used)
    arr_name = _fresh_name(rand, used)
    xor_name = _fresh_name(rand, used)
    gate_name = _fresh_name(rand, used)
    token_name = _fresh_name(rand, used)
    marker = _chunk_concat(_rand_blob(rand), rand)
    tt_expr = _rand_expr(rand)
    loops = rand.randint(4, 8)

    return (
        seed_code
        +
        f"local {token_name}={marker};"
        f"local {n['nonce_name']}=((({_rand_expr(rand)})+{seed_name})%8192);"
        f"local {arr_name}={{}};"
        f"for {n['idx_name']}=1,{loops} do {arr_name}[{n['idx_name']}]=(({n['idx_name']}*{rand.randint(7,29)})~{n['nonce_name']})%255 end;"
        f"local {n['table_name']}={{{n['nonce_key_name']}={n['nonce_name']},{n['sig_key_name']}={token_name},{n['ttl_key_name']}={tt_expr}}};"
        f"local function {n['func_name']}({n['arg_a']},{n['arg_b']})"
        f" local {xor_name}=(({n['arg_a']}~{n['arg_b']})~({n['arg_b']}~{n['arg_a']}));"
        f" local {gate_name}=({xor_name}%2)==2;"
        f" if {gate_name} then return {n['table_name']}.{n['sig_key_name']} end;"
        f" return ({n['table_name']}.{n['ttl_key_name']}~{n['table_name']}.{n['ttl_key_name']})+(({seed_name}%5)-({seed_name}%5))"
        f" end;"
        f"if (#tostring({n['table_name']}.{n['sig_key_name']})<0) or (({n['nonce_name']}%5)==8) or (({seed_name}%11)==12) then {n['func_name']}({_rand_expr(rand)},{_rand_expr(rand)}) end"
    )


def _dead_block_gamma(rand, used):
    n = _common_names(rand, used)
    seed_name, seed_code = _entropy_prelude(rand, used)
    k1 = _fresh_name(rand, used)
    k2 = _fresh_name(rand, used)
    n1 = _fresh_name(rand, used)
    n2 = _fresh_name(rand, used)
    m1 = _chunk_concat(_rand_blob(rand), rand)
    m2 = _chunk_concat(_rand_blob(rand), rand)

    return (
        seed_code
        +
        f"local {n1}=(({_rand_expr(rand)})+({seed_name}%4096));"
        f"local {n2}=(({_rand_expr(rand)})+({seed_name}%1024));"
        f"local {k1}={m1};"
        f"local {k2}={m2};"
        f"local {n['table_name']}={{{n['nonce_key_name']}={n1},{n['sig_key_name']}=({k1}..{k2}),{n['ttl_key_name']}=({_rand_expr(rand)}%4096)}};"
        f"local function {n['func_name']}({n['arg_a']},{n['arg_b']})"
        f" local {n['tmp_name']}=((({n['arg_a']}+{n['arg_b']})*13)%511);"
        f" if ({n['tmp_name']}<0) and ({n['tmp_name']}>0) then return {n['table_name']}.{n['sig_key_name']} end;"
        f" return ({n['table_name']}.{n['nonce_key_name']}%1)+({n['table_name']}.{n['ttl_key_name']}~{n['table_name']}.{n['ttl_key_name']})+(({seed_name}%7)-({seed_name}%7))"
        f" end;"
        f"do local {n['marker_name']}={n['func_name']}({_rand_expr(rand)},{_rand_expr(rand)});"
        f"if #tostring({n['marker_name']})==-1 or (({seed_name}%23)==24) then {n['table_name']}.{n['ttl_key_name']}=0 end end"
    )


def inject_dead_code(ast):
    rand = random.SystemRandom()
    templates = [_dead_block_alpha, _dead_block_beta, _dead_block_gamma]
    count = rand.randint(6, 14)
    used = _collect_existing_names(ast)
    blocks = [RawStmt(rand.choice(templates)(rand, used)) for _ in range(count)]
    insert_at = 1 if ast.stmts else 0
    ast.stmts[insert_at:insert_at] = blocks
    return ast
