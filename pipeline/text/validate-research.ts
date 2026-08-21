import type { ResearchContract, TextBundleContract, TopicContract } from "../contracts/text.js";
import { ResearchOutputSchema } from "../contracts/text-schema.js";

export function validateOperatorResearch(input: {
  metadata: TextBundleContract["metadata"];
  topic: TopicContract;
  research: ResearchContract;
}): void {
  if (!/^[a-z0-9-]+$/.test(input.metadata.episodeId) || input.metadata.version < 1) {
    throw new Error("OPERATOR_RESEARCH_GATE_FAIL: invalid metadata");
  }
  if (!input.topic.question.trim().endsWith("?")) {
    throw new Error("OPERATOR_RESEARCH_GATE_FAIL: invalid topic question");
  }

  const parsed = ResearchOutputSchema.safeParse(input.research);
  if (!parsed.success) {
    throw new Error(`OPERATOR_RESEARCH_GATE_FAIL: ${parsed.error.message}`);
  }

  const sourceIds = new Set(parsed.data.sources.map((source) => source.id));
  const factIds = new Set<string>();
  for (const fact of parsed.data.facts) {
    if (factIds.has(fact.id)) {
      throw new Error(`OPERATOR_RESEARCH_GATE_FAIL: duplicate fact id ${fact.id}`);
    }
    factIds.add(fact.id);
    for (const sourceId of fact.sourceIds) {
      if (!sourceIds.has(sourceId)) {
        throw new Error(
          `OPERATOR_RESEARCH_GATE_FAIL: fact ${fact.id} references unknown source ${sourceId}`,
        );
      }
    }
  }
}
