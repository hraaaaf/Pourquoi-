import type { TextProvider } from "./text-provider.js";
import { OpenAITextProvider } from "./openai-provider.js";

export function createTextProviderFromEnv(
  env: NodeJS.ProcessEnv = process.env,
): TextProvider {
  const providerId = env.TEXT_PROVIDER ?? "openai";

  if (providerId !== "openai") {
    throw new Error(`UNSUPPORTED_TEXT_PROVIDER: ${providerId}`);
  }

  const apiKey = env.OPENAI_API_KEY ?? "";
  if (!apiKey.trim()) {
    throw new Error("OPENAI_API_KEY_REQUIRED");
  }

  return new OpenAITextProvider({
    apiKey,
    model: env.OPENAI_TEXT_MODEL ?? "gpt-5.6-luna",
  });
}
