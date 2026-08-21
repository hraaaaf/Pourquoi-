import assert from "node:assert/strict";
import test from "node:test";
import { OpenAITextProvider } from "../pipeline/providers/openai-provider.js";
import { createTextProviderFromEnv } from "../pipeline/providers/registry.js";

function fakeClient(output: unknown, calls: Record<string, unknown>[]) {
  return {
    responses: {
      async parse(params: Record<string, unknown>) {
        calls.push(params);
        return { output_parsed: output, id: "resp_test" };
      },
    },
  };
}

test("OpenAI research stage enables hosted web search", async () => {
  const calls: Record<string, unknown>[] = [];
  const provider = new OpenAITextProvider({
    apiKey: "test-key",
    client: fakeClient(
      {
        sources: [
          { id: "s1", title: "A", url: "https://example.com/a", publisher: "Example" },
          { id: "s2", title: "B", url: "https://example.com/b", publisher: "Example" },
        ],
        facts: [{ id: "f1", statement: "Fact", sourceIds: ["s1"] }],
      },
      calls,
    ),
    promptLoader: async () => "PROMPT",
  });

  await provider.generateJson({ stage: "research", promptId: "research.v1", input: {} });

  assert.deepEqual(calls[0]?.tools, [{ type: "web_search" }]);
  assert.equal(calls[0]?.store, false);
});

test("OpenAI non-research stages do not receive web search", async () => {
  const calls: Record<string, unknown>[] = [];
  const provider = new OpenAITextProvider({
    apiKey: "test-key",
    client: fakeClient({ status: "pass", reviewedFactIds: ["f1"] }, calls),
    promptLoader: async () => "PROMPT",
  });

  await provider.generateJson({ stage: "fact-check", promptId: "fact-check.v1", input: {} });

  assert.equal("tools" in calls[0]!, false);
});

test("OpenAI provider refuses missing structured output", async () => {
  const provider = new OpenAITextProvider({
    apiKey: "test-key",
    client: fakeClient(null, []),
    promptLoader: async () => "PROMPT",
  });

  await assert.rejects(
    provider.generateJson({ stage: "script", promptId: "script.v1", input: {} }),
    /OPENAI_STRUCTURED_OUTPUT_MISSING/,
  );
});

test("provider registry requires an API key and defaults to Luna", () => {
  assert.throws(() => createTextProviderFromEnv({ TEXT_PROVIDER: "openai" }), /OPENAI_API_KEY_REQUIRED/);

  const provider = createTextProviderFromEnv({
    TEXT_PROVIDER: "openai",
    OPENAI_API_KEY: "test-key",
  });
  assert.equal(provider.id, "openai");
  assert.equal(provider.model, "gpt-5.6-luna");
});
