export const SECTION_KINDS = [
  "hook",
  "context",
  "explanation",
  "surprise",
  "challenge",
] as const;

export type SectionKind = (typeof SECTION_KINDS)[number];

export type EpisodeCategory =
  | "science"
  | "history"
  | "world"
  | "nature"
  | "body"
  | "technology";

export interface TopicContract {
  question: string;
  minAge: number;
  maxAge: number;
  category: EpisodeCategory;
  keyAnswer: string;
}

export interface SourceContract {
  id: string;
  title: string;
  url: string;
  publisher: string;
}

export interface FactContract {
  id: string;
  statement: string;
  sourceIds: string[];
}

export interface ResearchContract {
  sources: SourceContract[];
  facts: FactContract[];
}

export interface ScriptSectionContract {
  kind: SectionKind;
  narration: string;
  factIds: string[];
}

export interface ScriptContract {
  targetSeconds: number;
  sections: ScriptSectionContract[];
}

export interface FactCheckContract {
  status: "pass" | "fail";
  reviewedFactIds: string[];
}

export interface StoryboardShotContract {
  id: string;
  sectionKind: SectionKind;
  purpose:
    | "question"
    | "cause"
    | "consequence"
    | "compare"
    | "surprise"
    | "recap";
  visual: string;
  onScreenText?: string;
  factIds: string[];
}

export interface StoryboardContract {
  shots: StoryboardShotContract[];
}

export interface TextBundleContract {
  metadata: {
    episodeId: string;
    version: number;
  };
  topic: TopicContract;
  research: ResearchContract;
  script: ScriptContract;
  factCheck: FactCheckContract;
  storyboard: StoryboardContract;
}
