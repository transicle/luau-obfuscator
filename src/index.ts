import { readFileSync, writeFileSync } from "node:fs";
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

    source = source.replace(/function\s+([a-zA-Z_]\w*)/g, (_, name) => {
        if (!map.has(name)) {
            map.set(name, make_name(i++));
        }
        return `function ${map.get(name)}`;
    });

    source = source.replace(/local\s+([a-zA-Z_]\w*)/g, (_, name) => {
        if (!map.has(name)) {
            map.set(name, name !== 'function' ? make_name(i++) : 'function');
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

const output = obfuscate(readFileSync(path.join("@template", "input.lua"), "utf-8"));
const readMe = `# luau-obfuscator
Basic Luau obfuscator and learning project for beginners exploring code obfuscation and script rewriting.

## Example

\`\`\`lua
${output}
\`\`\``;

writeFileSync(path.join("@template", "output.lua"), output);
writeFileSync(path.join("README.md"), readMe);

console.log(output);