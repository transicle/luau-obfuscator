import random


def _rand_ident(rand, min_len=9, max_len=18):
    head = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    tail = head + "0123456789_"
    size = rand.randint(min_len, max_len)
    return rand.choice(head) + "".join(rand.choice(tail) for _ in range(size - 1))


def _fnv1a_32_bytes(data):
    h = 2166136261
    for b in data:
        h ^= b
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def _djb2_32_bytes(data):
    h = 5381
    for b in data:
        h = ((h * 33) + b) & 0xFFFFFFFF
    return h


def _stream_xor(data, key):
    n = len(key)
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key[i % n] ^ (i & 0xFF) ^ ((i >> 8) & 0xFF))
    return bytes(out)


def _bytes_to_lua_escaped(data):
    return '"' + "".join(f"\\{b}" for b in data) + '"'


def _compile_vm_bytecode(payload_bytes, rand):
    pool = list(range(256))
    rand.shuffle(pool)
    op_push = pool[0:3]
    op_skip = pool[3:5]
    op_chk  = pool[5]
    op_rot  = pool[6]
    op_end  = pool[7]

    vm_mask = rand.randint(1, 255)
    vm_seed = rand.randint(0, 255)
    cookie  = [rand.randint(0, 255) for _ in range(4)]
    limit   = max(4096, len(payload_bytes) * 8 + 256)

    out = bytearray()
    out.extend([0x7F, 0x4C, 0x56, 0x4D] + cookie)

    state        = vm_seed
    running_hash = 0
    chk_every    = max(8, len(payload_bytes) // 10)

    for i, b in enumerate(payload_bytes):
        if rand.random() < 0.12:
            out.extend([rand.choice(op_skip), rand.randint(0, 255)])
        if rand.random() < 0.07:
            rv    = rand.randint(0, 255)
            state = ((state * 0x6B) + rv) & 0xFF
            out.extend([op_rot, rv])
        enc          = (b ^ vm_mask ^ state ^ (i & 0xFF)) & 0xFF
        state        = ((state * 0x6B) + enc) & 0xFF
        running_hash = (running_hash + b) & 0xFF
        out.extend([rand.choice(op_push), enc])
        if (i + 1) % chk_every == 0:
            out.extend([op_chk, running_hash])

    out.extend([op_chk, running_hash])
    out.extend([op_end, len(payload_bytes) & 0xFF])

    return {
        "bytecode": bytes(out),
        "op_push":  op_push,
        "op_skip":  op_skip,
        "op_chk":   op_chk,
        "op_rot":   op_rot,
        "op_end":   op_end,
        "vm_mask":  vm_mask,
        "vm_seed":  vm_seed,
        "cookie":   cookie,
        "limit":    limit,
    }


def _build_wrapper_components(payload_code):
    rand = random.SystemRandom()
    key  = [rand.randint(1, 255) for _ in range(rand.randint(8, 16))]
    mask = rand.randint(1, 0xFFFFFFFF)

    payload_bytes    = payload_code.encode("utf-8")
    vm               = _compile_vm_bytecode(payload_bytes, rand)
    cipher           = _stream_xor(vm["bytecode"], key)

    expected_blob_fnv = _fnv1a_32_bytes(cipher)
    expected_blob_djb = _djb2_32_bytes(cipher)
    key_bytes         = bytes(key)
    expected_key_fnv  = _fnv1a_32_bytes(key_bytes)

    masked_h1 = expected_blob_fnv ^ mask
    masked_h2 = (expected_blob_djb - ((mask * 33) & 0xFFFFFFFF)) & 0xFFFFFFFF
    masked_kh = expected_key_fnv  ^ ((mask * 17) & 0xFFFFFFFF)

    names = {
        "k":      _rand_ident(rand),
        "blob":   _rand_ident(rand),
        "m":      _rand_ident(rand),
        "m1":     _rand_ident(rand),
        "m2":     _rand_ident(rand),
        "m3":     _rand_ident(rand),
        "fail":   _rand_ident(rand),
        "fnv":    _rand_ident(rand),
        "djb":    _rand_ident(rand),
        "dec":    _rand_ident(rand),
        "vm":     _rand_ident(rand),
        "loader": _rand_ident(rand),
        "fn":     _rand_ident(rand),
        "err":    _rand_ident(rand),
    }

    return {
        "key":               key,
        "cipher":            cipher,
        "expected_blob_fnv": expected_blob_fnv,
        "expected_blob_djb": expected_blob_djb,
        "expected_key_fnv":  expected_key_fnv,
        "mask":              mask,
        "masked_h1":         masked_h1,
        "masked_h2":         masked_h2,
        "masked_kh":         masked_kh,
        "op_push":           vm["op_push"],
        "op_skip":           vm["op_skip"],
        "op_chk":            vm["op_chk"],
        "op_rot":            vm["op_rot"],
        "op_end":            vm["op_end"],
        "vm_mask":           vm["vm_mask"],
        "vm_seed":           vm["vm_seed"],
        "cookie":            vm["cookie"],
        "vm_limit":          vm["limit"],
        "names":             names,
    }


def _render_wrapper(parts):
    key_lua  = "{" + ",".join(str(k) for k in parts["key"]) + "}"
    blob_lua = _bytes_to_lua_escaped(parts["cipher"])
    n        = parts["names"]
    p        = parts
    pa, pb, ph = p["op_push"]
    sa, sb     = p["op_skip"]
    ck         = p["op_chk"]
    rt         = p["op_rot"]
    en         = p["op_end"]
    mk         = p["vm_mask"]
    sd         = p["vm_seed"]
    c0, c1, c2, c3 = p["cookie"]

    lines = []
    lines.append(f"local {n['k']}={key_lua}")
    lines.append(f"local {n['blob']}={blob_lua}")
    lines.append(f"local {n['m']}={p['mask']}")
    lines.append(f"local {n['m1']}={p['masked_h1']}")
    lines.append(f"local {n['m2']}={p['masked_h2']}")
    lines.append(f"local {n['m3']}={p['masked_kh']}")
    lines.append(
        f"local function {n['fail']}() error(\"tamper detected\",0) end"
    )
    lines.append(
        f"local function {n['fnv']}(s)"
        " local h=2166136261;"
        "for i=1,#s do h=bit32.band(bit32.bxor(h,string.byte(s,i))*16777619,4294967295) end;"
        "return string.format(\"%08x\",h) end"
    )
    lines.append(
        f"local function {n['djb']}(s)"
        " local h=5381;"
        "for i=1,#s do h=((h*33)+string.byte(s,i))%4294967296 end;"
        "return h end"
    )
    lines.append(
        f"local function {n['dec']}(s,k)"
        " local o={};"
        "for i=1,#s do"
        " local b=string.byte(s,i);"
        "local kk=k[(i-1)%#k+1];"
        f"o[i]=string.char(bit32.bxor(b,kk,(i-1)%256,math.floor((i-1)/256)%256)) end;"
        "return table.concat(o) end"
    )
    lines.append(
        f"local function {n['vm']}(bc)"
        f" if #bc<8 then return nil end;"
        f"if string.byte(bc,1)~=127 or string.byte(bc,2)~=76"
        f" or string.byte(bc,3)~=86 or string.byte(bc,4)~=77"
        f" or string.byte(bc,5)~={c0} or string.byte(bc,6)~={c1}"
        f" or string.byte(bc,7)~={c2} or string.byte(bc,8)~={c3}"
        f" then return nil end;"
        f"local pc=9;local out={{}};local oi=1;"
        f"local state={sd};local rh=0;local steps=0;"
        f"while pc<=#bc do"
        f" steps=steps+1;"
        f"if steps>{p['vm_limit']} then return nil end;"
        f"local op=string.byte(bc,pc);"
        f"local arg=string.byte(bc,pc+1) or 0;"
        f"pc=pc+2;"
        f"if op=={pa} or op=={pb} or op=={ph} then"
        f" local ch=bit32.bxor(arg,{mk},state,(oi-1)%256);"
        f"state=((state*107)+arg)%256;"
        f"rh=(rh+ch)%256;"
        f"out[oi]=string.char(ch);"
        f"oi=oi+1;"
        f"elseif op=={sa} or op=={sb} then"
        f" local _j=((bit32.bxor(arg,pc%256))*7)%13;"
        f"elseif op=={ck} then"
        f" if rh~=arg then return nil end;"
        f"elseif op=={rt} then"
        f" state=((state*107)+arg)%256;"
        f"elseif op=={en} then"
        f" if(oi-1)%256~=arg then return nil end;break;"
        f"else return nil end end;"
        f"if oi==1 then return nil end;"
        f"return table.concat(out) end"
    )
    lines.append(
        "do"
        f" local e1n=bit32.bxor({n['m']},{n['m1']});"
        f"local e1=string.format(\"%08x\",e1n);"
        f"local e2=({n['m2']}+(({n['m']}*33)%4294967296))%4294967296;"
        f"local ekn=bit32.bxor({n['m3']},({n['m']}*17)%4294967296);"
        f"local ek=string.format(\"%08x\",ekn);"
        f"local kb={{}};"
        f"for i=1,#{n['k']} do kb[i]=string.char({n['k']}[i]) end;"
        f"if {n['fnv']}(table.concat(kb))~=ek then {n['fail']}() end;"
        f"if {n['fnv']}({n['blob']})~=e1 then {n['fail']}() end;"
        f"if {n['djb']}({n['blob']})~=e2 then {n['fail']}() end;"
        f"local bc={n['dec']}({n['blob']},{n['k']});"
        f"if type(bc)~=\"string\" or #bc==0 then {n['fail']}() end;"
        f"local src={n['vm']}(bc);"
        f"if type(src)~=\"string\" or #src==0 then {n['fail']}() end;"
        f"local {n['loader']}=loadstring or load;"
        f"if type({n['loader']})~=\"function\" then {n['fail']}() end;"
        f"local {n['fn']},{n['err']}={n['loader']}(src);"
        f"if not {n['fn']} then {n['fail']}() end;"
        f"local ok,run=pcall({n['fn']});"
        f"if not ok then error(run,0) end end"
    )
    return ";".join(lines)


def wrap_with_tamper_guard(payload_code):
    parts = _build_wrapper_components(payload_code)
    return _render_wrapper(parts)


def _verify_components(parts):
    blob = parts["cipher"]
    key = bytes(parts["key"])
    if _fnv1a_32_bytes(blob) != parts["expected_blob_fnv"]:
        return False
    if _djb2_32_bytes(blob) != parts["expected_blob_djb"]:
        return False
    if _fnv1a_32_bytes(key) != parts["expected_key_fnv"]:
        return False
    return True


def pen_test_tamper_components(payload_code, rounds=250):
    base = _build_wrapper_components(payload_code)
    detected = {
        "flip_blob_byte": 0,
        "delete_blob_byte": 0,
        "append_blob_byte": 0,
        "flip_key_byte": 0,
        "patch_only_hash_1": 0,
        "patch_only_hash_2": 0,
    }

    rand = random.SystemRandom()
    for _ in range(rounds):
        c = {
            "key": list(base["key"]),
            "cipher": bytes(base["cipher"]),
            "expected_blob_fnv": base["expected_blob_fnv"],
            "expected_blob_djb": base["expected_blob_djb"],
            "expected_key_fnv": base["expected_key_fnv"],
        }

        buf = bytearray(c["cipher"])
        idx = rand.randrange(len(buf))
        buf[idx] ^= rand.randint(1, 255)
        c["cipher"] = bytes(buf)
        if not _verify_components(c):
            detected["flip_blob_byte"] += 1

        c = {
            "key": list(base["key"]),
            "cipher": bytes(base["cipher"]),
            "expected_blob_fnv": base["expected_blob_fnv"],
            "expected_blob_djb": base["expected_blob_djb"],
            "expected_key_fnv": base["expected_key_fnv"],
        }
        buf = bytearray(c["cipher"])
        del buf[rand.randrange(len(buf))]
        c["cipher"] = bytes(buf)
        if not _verify_components(c):
            detected["delete_blob_byte"] += 1

        c = {
            "key": list(base["key"]),
            "cipher": bytes(base["cipher"]),
            "expected_blob_fnv": base["expected_blob_fnv"],
            "expected_blob_djb": base["expected_blob_djb"],
            "expected_key_fnv": base["expected_key_fnv"],
        }
        buf = bytearray(c["cipher"])
        buf.append(rand.randint(1, 255))
        c["cipher"] = bytes(buf)
        if not _verify_components(c):
            detected["append_blob_byte"] += 1

        c = {
            "key": list(base["key"]),
            "cipher": bytes(base["cipher"]),
            "expected_blob_fnv": base["expected_blob_fnv"],
            "expected_blob_djb": base["expected_blob_djb"],
            "expected_key_fnv": base["expected_key_fnv"],
        }
        c["key"][rand.randrange(len(c["key"]))] ^= rand.randint(1, 255)
        if not _verify_components(c):
            detected["flip_key_byte"] += 1

        c = {
            "key": list(base["key"]),
            "cipher": bytes(base["cipher"]),
            "expected_blob_fnv": base["expected_blob_fnv"],
            "expected_blob_djb": base["expected_blob_djb"],
            "expected_key_fnv": base["expected_key_fnv"],
        }
        buf = bytearray(c["cipher"])
        buf[rand.randrange(len(buf))] ^= rand.randint(1, 255)
        c["cipher"] = bytes(buf)
        c["expected_blob_fnv"] = _fnv1a_32_bytes(c["cipher"])
        if not _verify_components(c):
            detected["patch_only_hash_1"] += 1

        c = {
            "key": list(base["key"]),
            "cipher": bytes(base["cipher"]),
            "expected_blob_fnv": base["expected_blob_fnv"],
            "expected_blob_djb": base["expected_blob_djb"],
            "expected_key_fnv": base["expected_key_fnv"],
        }
        buf = bytearray(c["cipher"])
        buf[rand.randrange(len(buf))] ^= rand.randint(1, 255)
        c["cipher"] = bytes(buf)
        c["expected_blob_djb"] = _djb2_32_bytes(c["cipher"])
        if not _verify_components(c):
            detected["patch_only_hash_2"] += 1

    summary = {}
    for key, value in detected.items():
        summary[key] = {
            "detected": value,
            "total": rounds,
            "rate": round((value / rounds) * 100.0, 2),
        }
    return summary
