import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { renameTokens } from "./rename.ts";
import { detokenize, tokenize } from "./tokenize.ts";
import type { Token } from "./tokenize.ts";

function obfuscate(source: string): string {
    console.log("SOURCE SIZE:", source.length);

    let tokens: Token[] = tokenize(source);
    console.log("TOKENS:", tokens.length);

    tokens = renameTokens(tokens);
    console.log("TOKENS AFTER RENAME:", tokens.length);

    const out = detokenize(tokens);
    console.log("OUTPUT SIZE:", out.length);

    return out;
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