import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { validateTextBundle } from "../pipeline/text/validate.js";

const PILOT_PATH = "episodes/pilot-ciel-bleu/text-bundle.json";

async function loadPilot(): Promise<unknown> {
  return JSON.parse(await readFile(PILOT_PATH, "utf8")) as unknown;
}

test("operator-produced pilot passes the canonical text gate", async () => {
  const pilot = await loadPilot();
  const result = validateTextBundle(pilot);
  assert.deepEqual(result, { ok: true, issues: [] });
});

test("pilot research uses real institutional sources", async () => {
  const pilot = (await loadPilot()) as {
    research: { sources: Array<{ url: string; publisher: string }> };
  };

  assert.ok(pilot.research.sources.length >= 2);
  for (const source of pilot.research.sources) {
    const hostname = new URL(source.url).hostname;
    assert.notEqual(hostname, "example.com");
    assert.ok(
      hostname.endsWith("nasa.gov") || hostname.endsWith("noaa.gov"),
      `unexpected pilot source host: ${hostname}`,
    );
    assert.match(source.publisher, /NASA|NOAA/);
  }
});

test("pilot contains no unsourced research facts", async () => {
  const pilot = (await loadPilot()) as {
    research: {
      facts: Array<{ id: string; sourceIds: string[] }>;
      sources: Array<{ id: string }>;
    };
  };

  const sourceIds = new Set(pilot.research.sources.map((source) => source.id));
  for (const fact of pilot.research.facts) {
    assert.ok(fact.sourceIds.length > 0, `${fact.id} has no source`);
    for (const sourceId of fact.sourceIds) {
      assert.ok(sourceIds.has(sourceId), `${fact.id} references unknown ${sourceId}`);
    }
  }
});
