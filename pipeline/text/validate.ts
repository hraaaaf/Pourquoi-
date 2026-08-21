import {
  SECTION_KINDS,
  type TextBundleContract,
} from "../contracts/text.js";

export interface ValidationResult {
  ok: boolean;
  issues: string[];
}

const isObject = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const isString = (value: unknown): value is string =>
  typeof value === "string" && value.trim().length > 0;

const isStringArray = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every(isString);

export function validateTextBundle(input: unknown): ValidationResult {
  const issues: string[] = [];

  if (!isObject(input)) {
    return { ok: false, issues: ["bundle must be an object"] };
  }

  const bundle = input as unknown as TextBundleContract;

  if (!isObject(bundle.metadata)) {
    issues.push("metadata is required");
  } else {
    if (!isString(bundle.metadata.episodeId) || !/^[a-z0-9-]+$/.test(bundle.metadata.episodeId)) {
      issues.push("metadata.episodeId must be a lowercase slug");
    }
    if (!Number.isInteger(bundle.metadata.version) || bundle.metadata.version < 1) {
      issues.push("metadata.version must be a positive integer");
    }
  }

  if (!isObject(bundle.topic)) {
    issues.push("topic is required");
  } else {
    if (!isString(bundle.topic.question) || !bundle.topic.question.trim().endsWith("?")) {
      issues.push("topic.question must be a non-empty question ending with ?");
    }
    if (!Number.isInteger(bundle.topic.minAge) || !Number.isInteger(bundle.topic.maxAge)) {
      issues.push("topic ages must be integers");
    } else if (bundle.topic.minAge < 6 || bundle.topic.maxAge > 9 || bundle.topic.minAge > bundle.topic.maxAge) {
      issues.push("topic age range must stay within 6–9 years");
    }
    if (!isString(bundle.topic.keyAnswer)) {
      issues.push("topic.keyAnswer is required");
    }
  }

  const sources = bundle.research?.sources;
  const facts = bundle.research?.facts;
  if (!Array.isArray(sources) || sources.length < 2) {
    issues.push("research requires at least two sources");
  }
  if (!Array.isArray(facts) || facts.length === 0) {
    issues.push("research requires at least one fact");
  }

  const sourceIds = new Set<string>();
  if (Array.isArray(sources)) {
    for (const source of sources) {
      if (!isObject(source) || !isString(source.id)) {
        issues.push("every source requires an id");
        continue;
      }
      if (sourceIds.has(source.id)) issues.push(`duplicate source id: ${source.id}`);
      sourceIds.add(source.id);
      if (!isString(source.title) || !isString(source.publisher)) {
        issues.push(`source ${source.id} requires title and publisher`);
      }
      if (!isString(source.url) || !source.url.startsWith("https://")) {
        issues.push(`source ${source.id} requires an https URL`);
      }
    }
  }

  const factIds = new Set<string>();
  if (Array.isArray(facts)) {
    for (const fact of facts) {
      if (!isObject(fact) || !isString(fact.id)) {
        issues.push("every fact requires an id");
        continue;
      }
      if (factIds.has(fact.id)) issues.push(`duplicate fact id: ${fact.id}`);
      factIds.add(fact.id);
      if (!isString(fact.statement)) issues.push(`fact ${fact.id} requires a statement`);
      if (!isStringArray(fact.sourceIds) || fact.sourceIds.length === 0) {
        issues.push(`fact ${fact.id} must cite at least one source`);
      } else {
        for (const sourceId of fact.sourceIds) {
          if (!sourceIds.has(sourceId)) issues.push(`fact ${fact.id} references unknown source ${sourceId}`);
        }
      }
    }
  }

  const sections = bundle.script?.sections;
  if (!Number.isInteger(bundle.script?.targetSeconds) || bundle.script.targetSeconds < 60 || bundle.script.targetSeconds > 90) {
    issues.push("script.targetSeconds must be between 60 and 90");
  }
  if (!Array.isArray(sections) || sections.length !== SECTION_KINDS.length) {
    issues.push(`script must contain exactly ${SECTION_KINDS.length} canonical sections`);
  } else {
    sections.forEach((section, index) => {
      const expected = SECTION_KINDS[index];
      if (!isObject(section) || section.kind !== expected) {
        issues.push(`script section ${index + 1} must be ${expected}`);
        return;
      }
      if (!isString(section.narration)) issues.push(`section ${expected} requires narration`);
      if (!isStringArray(section.factIds)) issues.push(`section ${expected} factIds must be an array`);
      else for (const factId of section.factIds) if (!factIds.has(factId)) issues.push(`section ${expected} references unknown fact ${factId}`);
    });
  }

  if (bundle.factCheck?.status !== "pass") {
    issues.push("factCheck.status must be pass before storyboard validation");
  }
  if (!isStringArray(bundle.factCheck?.reviewedFactIds)) {
    issues.push("factCheck.reviewedFactIds is required");
  } else {
    for (const factId of factIds) {
      if (!bundle.factCheck.reviewedFactIds.includes(factId)) issues.push(`fact ${factId} is not fact-checked`);
    }
  }

  const shots = bundle.storyboard?.shots;
  if (!Array.isArray(shots) || shots.length < SECTION_KINDS.length) {
    issues.push("storyboard requires at least one shot per canonical section");
  } else {
    const coveredSections = new Set<string>();
    for (const shot of shots) {
      if (!isObject(shot) || !isString(shot.id)) {
        issues.push("every storyboard shot requires an id");
        continue;
      }
      if (!SECTION_KINDS.includes(shot.sectionKind as never)) {
        issues.push(`shot ${shot.id} has invalid sectionKind`);
      } else {
        coveredSections.add(shot.sectionKind as string);
      }
      if (!isString(shot.visual)) issues.push(`shot ${shot.id} requires a visual description`);
      if (!isStringArray(shot.factIds)) issues.push(`shot ${shot.id} factIds must be an array`);
      else for (const factId of shot.factIds) if (!factIds.has(factId)) issues.push(`shot ${shot.id} references unknown fact ${factId}`);
    }
    for (const section of SECTION_KINDS) {
      if (!coveredSections.has(section)) issues.push(`storyboard does not cover section ${section}`);
    }
  }

  return { ok: issues.length === 0, issues };
}
