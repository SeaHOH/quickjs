# Used to patch third party before building, and revert it after building.
# This way to keeps third party's contents do not change.

import os

metadata = {
    "quickjs.c": (
        b"\nstatic int JS_SetGlobalVar",
        b"\nint JS_SetGlobalVar"
    ),
    "quickjs.h": (
        b";\n\n#define JS_GPN_STRING_MASK",
        b""";
int JS_SetGlobalVar(JSContext *ctx, JSAtom prop, JSValue val, int flag);
static inline int JS_SetGlobalVarStr(JSContext *ctx, const char *prop,
                                     JSValue val, int force)
{
    JSAtom atom = JS_NewAtom(ctx, prop);
    int ret = JS_SetGlobalVar(ctx, atom, val, force ? 1 : 0);
    JS_FreeAtom(ctx, atom);
    return ret;
}

#define JS_GPN_STRING_MASK"""
    )
}

origin_code = dict.fromkeys(metadata)

def patch():
    for name, repl_pair in metadata.items():
        if origin_code[name]:
            continue
        file = os.path.join("third-party", name)
        with open(file, "rb") as f:
            code = f.read()
        patched_code = code.replace(*repl_pair, 1)
        if code != patched_code:
            origin_code[name] = code
            with open(file, "wb") as f:
                f.write(patched_code)

def revert():
    for name, repl_pair in metadata.items():
        file = os.path.join("third-party", name)
        if origin_code[name]:
            with open(file, "wb") as f:
                f.write(origin_code[name])
            continue
        with open(file, "rb") as f:
            code = f.read()
        reverted_code = code.replace(*repl_pair[::-1], 1)
        if code != reverted_code:
            with open(file, "wb") as f:
                f.write(reverted_code)
