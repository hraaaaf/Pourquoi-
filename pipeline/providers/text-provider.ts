export type TextStage = "research" | "script" | "fact-check" | "storyboard";

export interface TextGenerationRequest {
  stage: TextStage;
  promptId: string;
  input: unknown;
}

export interface TextProvider {
  readonly id: string;
  readonly model: string;
  generateJson(request: TextGenerationRequest): Promise<unknown>;
}
