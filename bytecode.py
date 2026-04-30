import os
import random
import subprocess
import tempfile

_LUAU_COMPILE = os.environ.get("LUAU_COMPILE", "/tmp/luau-compile")


def _find_compiler():
    if os.path.isfile(_LUAU_COMPILE) and os.access(_LUAU_COMPILE, os.X_OK):
        return _LUAU_COMPILE
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, "luau-compile")
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    raise FileNotFoundError(
        "luau-compile not found. Download from "
        "https://github.com/luau-lang/luau/releases and place at /tmp/luau-compile"
    )


def compile_to_bytecode(lua_source: str) -> bytes:
    compiler = _find_compiler()
    with tempfile.NamedTemporaryFile(suffix=".lua", mode="w", delete=False) as f:
        f.write(lua_source)
        tmp = f.name
    try:
        result = subprocess.run(
            [compiler, "--binary", "-O2", "-g0", tmp],
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"luau-compile failed (exit {result.returncode}):\n"
                + result.stderr.decode(errors="replace")
            )
        bc = result.stdout
        if len(bc) < 4:
            raise RuntimeError("luau-compile produced unexpectedly small output")
        return bc
    finally:
        os.unlink(tmp)


def _rand_ident(rand, min_len=9, max_len=18):
    head = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    tail = head + "0123456789_"
    size = rand.randint(min_len, max_len)
    return rand.choice(head) + "".join(rand.choice(tail) for _ in range(size - 1))


def _stream_xor(data: bytes, key: list) -> bytes:
    n = len(key)
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key[i % n] ^ (i & 0xFF) ^ ((i >> 8) & 0xFF))
    return bytes(out)


def _bytes_to_lua_escaped(data: bytes) -> str:
    return '"' + "".join(f"\\{b}" for b in data) + '"'


def wrap_bytecode(lua_source: str) -> str:
    rand = random.SystemRandom()

    bytecode = compile_to_bytecode(lua_source)
    key = [rand.randint(1, 255) for _ in range(rand.randint(8, 16))]
    cipher = _stream_xor(bytecode, key)

    n_k    = _rand_ident(rand)
    n_b    = _rand_ident(rand)
    n_dec  = _rand_ident(rand)
    n_i    = _rand_ident(rand)
    n_o    = _rand_ident(rand)
    n_bc   = _rand_ident(rand)
    n_fn   = _rand_ident(rand)
    n_err  = _rand_ident(rand)
    n_ok   = _rand_ident(rand)
    n_run  = _rand_ident(rand)
    n_ld   = _rand_ident(rand)

    key_lua   = "{" + ",".join(str(k) for k in key) + "}"
    blob_lua  = _bytes_to_lua_escaped(cipher)

    dec_fn = (
        f"local function {n_dec}(s,k)"
        f" local {n_o}={{}}"
        f";for {n_i}=1,#s do"
        f" {n_o}[{n_i}]=string.char("
        f"bit32.bxor("
        f"string.byte(s,{n_i}),"
        f"k[({n_i}-1)%#k+1],"
        f"({n_i}-1)%256,"
        f"math.floor(({n_i}-1)/256)%256"
        f")) end"
        f";return table.concat({n_o}) end"
    )

    exec_block = (
        f"do"
        f" local {n_bc}={n_dec}({n_b},{n_k})"
        f";local {n_ld}=loadstring or load"
        f";if type({n_ld})~=\"function\" then error(\"no loader\",0) end"
        f";local {n_fn},{n_err}={n_ld}({n_bc})"
        f";if not {n_fn} then error({n_err} or \"bad bytecode\",0) end"
        f";local {n_ok},{n_run}=pcall({n_fn})"
        f";if not {n_ok} then error({n_run},0) end"
        f" end"
    )

    parts = [
        f"local {n_k}={key_lua}",
        f"local {n_b}={blob_lua}",
        dec_fn,
        exec_block,
    ]
    return ";".join(parts)
