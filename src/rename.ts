function makeName(len: number): string {
    const chars = 'abcdefghijklmnopqrstuvwxyz';
    let name = '';
    for (let i = 0; i < 6; i++) {
        name += chars[(len + i * 7) % chars.length];
    }
    return name;
}

export function renameVars(
    source: string
): string {
    let i = 0;
    const map = new Map<string, string>();
    
    source = source.replace(/function\s+([a-zA-Z_]\w*)/g, (_, name) => {
        if (!map.has(name)) {
            map.set(name, makeName(i++));
        }
        return `function ${map.get(name)}`;
    });

    source = source.replace(/local\s+([a-zA-Z_]\w*)/g, (_, name) => {
        if (!map.has(name)) {
            map.set(name, name !== 'function' ? makeName(i++) : 'function');
        }
        return `local ${map.get(name)}`;
    });

    // replace variable usage
    for (const [orig, obf] of map.entries()) {
        const re = new RegExp(`\\b${orig}\\b`, "g");
        source = source.replace(re, obf);
    }

    return source;
}