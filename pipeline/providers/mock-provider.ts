import type {
  TextGenerationRequest,
  TextProvider,
  TextStage,
} from "./text-provider.js";

export class MockTextProvider implements TextProvider {
  readonly id = "mock";
  readonly model = "deterministic-fixture";
  readonly calls: TextGenerationRequest[] = [];

  constructor(private readonly responses: Record<TextStage, unknown>) {}

  async generateJson(request: TextGenerationRequest): Promise<unknown> {
    this.calls.push(request);
    return structuredClone(this.responses[request.stage]);
  }
}
