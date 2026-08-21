import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function readJson(path: string): Promise<any> {
  return JSON.parse(await readFile(path, "utf8"));
}

test("P2 pilot voice manifest stays review-gated", async () => {
  const voice = await readJson("episodes/pilot-ciel-bleu/audio/voice-manifest.json");
  assert.equal(voice.episodeId, "pilot-ciel-bleu");
  assert.equal(voice.voiceId, "crisp");
  assert.equal(voice.direction, "engaged-curious");
  assert.equal(voice.status, "human-review");
  assert.ok(voice.transcript.length > 500);
});

test("P2 music and mix fit the canonical episode window", async () => {
  const music = await readJson("episodes/pilot-ciel-bleu/audio/music-manifest.json");
  const mix = await readJson("episodes/pilot-ciel-bleu/audio/mix-profile.json");
  assert.ok(music.durationSeconds >= 60 && music.durationSeconds <= 90);
  assert.equal(music.status, "human-review");
  assert.ok(mix.musicUnderVoiceDb <= -18);
  assert.ok(mix.musicTransitionDb > mix.musicUnderVoiceDb);
  assert.equal(mix.loudnessTargetLufs, -16);
});
