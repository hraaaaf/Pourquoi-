import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { validateTextBundle } from "../pipeline/text/validate.js";

async function loadFixture(): Promise<Record<string, unknown>> {
  const raw = await readFile("episodes/fixtures/p1-valid.json", "utf8");
  return JSON.parse(raw) as Record<string, unknown>;
}

test("valid P1 bundle passes", async () => {
  const fixture = await loadFixture();
  const result = validateTextBundle(fixture);
  assert.equal(result.ok, true, result.issues.join("\n"));
});

test("unsourced fact fails", async () => {
  const fixture = await loadFixture();
  const research = fixture.research as { facts: Array<{ sourceIds: string[] }> };
  research.facts[0].sourceIds = [];
  const result = validateTextBundle(fixture);
  assert.equal(result.ok, false);
  assert.ok(result.issues.some((issue) => issue.includes("must cite at least one source")));
});

test("missing canonical section fails", async () => {
  const fixture = await loadFixture();
  const script = fixture.script as { sections: unknown[] };
  script.sections.pop();
  const result = validateTextBundle(fixture);
  assert.equal(result.ok, false);
  assert.ok(result.issues.some((issue) => issue.includes("exactly 5 canonical sections")));
});
