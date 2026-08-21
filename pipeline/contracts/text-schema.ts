import { z } from "zod/v4";

export const ResearchOutputSchema = z
  .object({
    sources: z
      .array(
        z.object({
          id: z.string().min(1),
          title: z.string().min(1),
          url: z.string().url(),
          publisher: z.string().min(1),
        }),
      )
      .min(2),
    facts: z
      .array(
        z.object({
          id: z.string().min(1),
          statement: z.string().min(1),
          sourceIds: z.array(z.string().min(1)).min(1),
        }),
      )
      .min(1),
  })
  .strict();

export const ScriptOutputSchema = z
  .object({
    targetSeconds: z.number().int().min(60).max(90),
    sections: z
      .array(
        z
          .object({
            kind: z.enum(["hook", "context", "explanation", "surprise", "challenge"]),
            narration: z.string().min(1),
            factIds: z.array(z.string().min(1)),
          })
          .strict(),
      )
      .min(4),
  })
  .strict();

export const FactCheckOutputSchema = z
  .object({
    status: z.enum(["pass", "fail"]),
    reviewedFactIds: z.array(z.string().min(1)),
  })
  .strict();

const StoryboardShotOutputSchema = z
  .object({
    id: z.string().min(1),
    sectionKind: z.enum(["hook", "context", "explanation", "surprise", "challenge"]),
    purpose: z.enum(["question", "cause", "consequence", "compare", "surprise", "recap"]),
    visual: z.string().min(1),
    onScreenText: z.string().nullable(),
    factIds: z.array(z.string().min(1)),
  })
  .strict();

export const StoryboardOutputSchema = z
  .object({
    shots: z.array(StoryboardShotOutputSchema).min(4),
  })
  .strict();
