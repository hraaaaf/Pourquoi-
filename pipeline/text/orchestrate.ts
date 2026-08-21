import type {
  FactCheckContract,
  ResearchContract,
  ScriptContract,
  StoryboardContract,
  TextBundleContract,
  TopicContract,
} from "../contracts/text.js";
import { TEXT_PROMPTS } from "../prompts/manifest.js";
import type { TextProvider } from "../providers/text-provider.js";
import { validateTextBundle } from "./validate.js";

export interface GenerationTrace {
  providerId: string;
  model: string;
  prompts: typeof TEXT_PROMPTS;
}

export async function generateTextBundle(
  provider: TextProvider,
  metadata: TextBundleContract["metadata"],
  topic: TopicContract,
): Promise<{ bundle: TextBundleContract; trace: GenerationTrace }> {
  const research = (await provider.generateJson({
    stage: "research",
    promptId: TEXT_PROMPTS.research,
    input: { metadata, topic },
  })) as ResearchContract;

  const script = (await provider.generateJson({
    stage: "script",
    promptId: TEXT_PROMPTS.script,
    input: { metadata, topic, research },
  })) as ScriptContract;

  const factCheck = (await provider.generateJson({
    stage: "fact-check",
    promptId: TEXT_PROMPTS.factCheck,
    input: { metadata, topic, research, script },
  })) as FactCheckContract;

  if (factCheck?.status !== "pass") {
    throw new Error("TEXT_PIPELINE_BLOCKED: fact-check did not pass");
  }

  const storyboard = (await provider.generateJson({
    stage: "storyboard",
    promptId: TEXT_PROMPTS.storyboard,
    input: { metadata, topic, research, script, factCheck },
  })) as StoryboardContract;

  const bundle: TextBundleContract = {
    metadata,
    topic,
    research,
    script,
    factCheck,
    storyboard,
  };

  const validation = validateTextBundle(bundle);
  if (!validation.ok) {
    throw new Error(`TEXT_GATE_FAIL:\n${validation.issues.join("\n")}`);
  }

  return {
    bundle,
    trace: {
      providerId: provider.id,
      model: provider.model,
      prompts: TEXT_PROMPTS,
    },
  };
}
