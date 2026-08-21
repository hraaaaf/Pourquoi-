import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import type { TextBundleContract } from "../pipeline/contracts/text.js";
import { generateTextBundle } from "../pipeline/text/orchestrate.js";
import { MockTextProvider } from "../pipeline/providers/mock-provider.js";

async function loadFixture(): Promise<TextBundleContract> {
  const raw = await readFile("episodes/fixtures/p1-valid.json", "utf8");
  return JSON.parse(raw) as TextBundleContract;
}

test("provider-neutral orchestration returns a gated bundle", async () => {
  const fixture = await loadFixture();
  const provider = new MockTextProvider({
    research: fixture.research,
    script: fixture.script,
    "fact-check": fixture.factCheck,
    storyboard: fixture.storyboard,
  });

  const result = await generateTextBundle(provider, fixture.metadata, fixture.topic);
  assert.equal(result.trace.providerId, "mock");
  assert.equal(result.bundle.metadata.episodeId, fixture.metadata.episodeId);
  assert.deepEqual(provider.calls.map((call) => call.stage), [
    "research",
    "script",
    "fact-check",
    "storyboard",
  ]);
});

test("invalid provider output cannot bypass local gates", async () => {
  const fixture = await loadFixture();
  const brokenResearch = structuredClone(fixture.research);
  brokenResearch.facts[0].sourceIds = [];

  const provider = new MockTextProvider({
    research: brokenResearch,
    script: fixture.script,
    "fact-check": fixture.factCheck,
    storyboard: fixture.storyboard,
  });

  await assert.rejects(
    generateTextBundle(provider, fixture.metadata, fixture.topic),
    /TEXT_GATE_FAIL/,
  );
});

test("failed fact-check blocks storyboard generation", async () => {
  const fixture = await loadFixture();
  const provider = new MockTextProvider({
    research: fixture.research,
    script: fixture.script,
    "fact-check": { status: "fail", reviewedFactIds: [] },
    storyboard: fixture.storyboard,
  });

  await assert.rejects(
    generateTextBundle(provider, fixture.metadata, fixture.topic),
    /TEXT_PIPELINE_BLOCKED/,
  );
  assert.deepEqual(provider.calls.map((call) => call.stage), [
    "research",
    "script",
    "fact-check",
  ]);
});
