import { readFileSync } from "node:fs";
import path from "node:path";

function make_name(len: number): string {
    const chars = 'abcdefghijklmnopqrstuvwxyz';
    let name = '';
    for (let i = 0; i < 6; i++) {
        name += chars[(len + i * 7) % chars.length];
    }
    return name;
}

function obfuscate(source: string): string {
    let i = 0;
    const map = new Map<string, string>();

    source = source.replace(/local\s+([a-zA-Z_]\w*)/g, (_, name) => {
        if (!map.has(name)) {
            map.set(name, make_name(i++));
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

console.log(obfuscate(readFileSync(path.join("@template", "input.lua"), "utf-8")));