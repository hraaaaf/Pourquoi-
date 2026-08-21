import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import type { TextBundleContract } from "../contracts/text.js";
import { createTextProviderFromEnv } from "../providers/registry.js";
import { generateTextBundle } from "./orchestrate.js";

async function main(): Promise<void> {
  const inputPath = process.argv[2] ?? "episodes/fixtures/p1-valid.json";
  const outputPath = process.argv[3] ?? "artifacts/p1c/live-bundle.json";

  const source = JSON.parse(await readFile(resolve(inputPath), "utf8")) as TextBundleContract;
  const provider = createTextProviderFromEnv();
  const result = await generateTextBundle(provider, source.metadata, source.topic);

  await mkdir(dirname(resolve(outputPath)), { recursive: true });
  await writeFile(
    resolve(outputPath),
    JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        bundle: result.bundle,
        trace: result.trace,
      },
      null,
      2,
    ) + "\n",
    "utf8",
  );

  console.log(
    JSON.stringify({
      ok: true,
      episodeId: result.bundle.metadata.episodeId,
      provider: result.trace.providerId,
      model: result.trace.model,
      outputPath,
    }),
  );
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(message);
  process.exitCode = 1;
});
