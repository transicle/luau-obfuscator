import type { Token } from "./tokenize.ts";

function makeName(len: number): string {
    const chars = 'abcdefghijklmnopqrstuvwxyz';
    let name = '';
    for (let i = 0; i < 6; i++) {
        name += chars[(len + i * 7) % chars.length];
    }
    return name.toUpperCase();
}

export function renameTokens(tokens: Token[]): Token[] {
    const map = new Map<string, string>();
    let i = 0;

    const isDecl = (t: Token, prev?: Token) =>
        prev?.value === "local" || prev?.value === "function";

    let prev: Token | undefined;

    return tokens.map((t) => {
        if (t.type === "ident") {
            if (!map.has(t.value) && isDecl(t, prev)) {
                map.set(t.value, makeName(i++));
            }

            if (map.has(t.value)) {
                const renamed = map.get(t.value)!;
                prev = t;
                return { ...t, value: renamed };
            }
        }

        prev = t;
        return t;
    });
}