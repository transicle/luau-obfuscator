import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { renameVars } from "./rename.ts";

function obfuscate(source: string): string {
    source = renameVars(source);
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