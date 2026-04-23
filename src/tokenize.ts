export type Token = {
    type: string;
    value: string;
};

export function tokenize(source: string): Token[] {
    const tokens: Token[] = [];
    const regex = /[a-zA-Z_]\w*|\d+|==|~=|<=|>=|[{}()[\].,=+\-*/^#]|"[^"]*"|'[^']*'|\s+/g;

    let match;
    while ((match = regex.exec(source)) !== null) {
        const value = match[0];

        if (/^\s+$/.test(value)) continue;

        if (/^[a-zA-Z_]\w*$/.test(value)) {
            tokens.push({ type: "ident", value });
        } else if (/^\d+$/.test(value)) {
            tokens.push({ type: "number", value });
        } else {
            tokens.push({ type: "symbol", value });
        }
    }

    return tokens;
}

export function detokenize(tokens: Token[]): string {
    return tokens.map(t => t.value).join("");
}