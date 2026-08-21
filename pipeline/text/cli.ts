import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { validateTextBundle } from "./validate.js";

const file = process.argv[2];
if (!file) {
  console.error("Usage: node cli.js <episode-bundle.json>");
  process.exit(2);
}

try {
  const raw = await readFile(resolve(file), "utf8");
  const parsed: unknown = JSON.parse(raw);
  const result = validateTextBundle(parsed);

  if (!result.ok) {
    console.error("P1 TEXT GATE: FAIL");
    for (const issue of result.issues) console.error(`- ${issue}`);
    process.exit(1);
  }

  console.log("P1 TEXT GATE: PASS");
} catch (error) {
  console.error("P1 TEXT GATE: ERROR");
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(2);
}
