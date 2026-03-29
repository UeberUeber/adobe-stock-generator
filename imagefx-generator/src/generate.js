/**
 * ImageFX Generator - 이미지 생성 + 메타데이터 저장
 *
 * Usage: node src/generate.js [--prompts FILE] [--count N] [--delay MS] [--dry-run] [--timestamp TS]
 *   --prompts FILE : 프롬프트 JSON 경로 (기본: ./prompts.json, 없으면 seasonal_prompts.json)
 *   --count N      : 처음 N개만 처리
 *   --delay MS     : 요청 간 딜레이 ms (기본: 5000)
 *   --dry-run      : 이미지 생성 없이 메타데이터만 생성
 *   --timestamp TS : 타임스탬프 직접 지정 (파이프라인 연동용)
 */

import { ImageFX, Prompt } from "@rohitaryal/imagefx-api";
import { config } from "dotenv";
import { resolve, dirname, join } from "path";
import { fileURLToPath } from "url";
import { readFileSync, writeFileSync, mkdirSync, existsSync, appendFileSync } from "fs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");
const STOCK_GENERATOR_ROOT = resolve(PROJECT_ROOT, "../adobe-stock-generator");

// ─── Args ───
const args = process.argv.slice(2);
const getArg = (name) => {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : null;
};
const hasFlag = (name) => args.includes(`--${name}`);

const MAX_COUNT = getArg("count") ? parseInt(getArg("count")) : Infinity;
const DELAY_MS = getArg("delay") ? parseInt(getArg("delay")) : 5000;
const DRY_RUN = hasFlag("dry-run");

// ─── .env ───
config({ path: resolve(PROJECT_ROOT, ".env") });
const cookie = process.env.GOOGLE_COOKIE;
if (!cookie && !DRY_RUN) {
  console.error("[ERROR] GOOGLE_COOKIE not set in .env");
  process.exit(1);
}

// ─── Timestamp ───
const timestamp = getArg("timestamp") || (() => {
  const now = new Date();
  return [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, "0"),
    String(now.getDate()).padStart(2, "0"),
  ].join("-") + "_" + [
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0"),
  ].join("-");
})();

// ─── Output dir ───
const outputDir = join(STOCK_GENERATOR_ROOT, "generations", timestamp);
mkdirSync(outputDir, { recursive: true });

// ─── Read prompts (dynamic or seasonal) ───
const dynamicPromptsPath = getArg("prompts")
  ? resolve(getArg("prompts"))
  : resolve(PROJECT_ROOT, "prompts.json");
const seasonalPromptsPath = join(STOCK_GENERATOR_ROOT, "seasonal_prompts.json");

let promptsPath;
if (existsSync(dynamicPromptsPath)) {
  promptsPath = dynamicPromptsPath;
} else if (existsSync(seasonalPromptsPath)) {
  promptsPath = seasonalPromptsPath;
} else {
  console.error("[ERROR] No prompts file found");
  process.exit(1);
}

const prompts = JSON.parse(readFileSync(promptsPath, "utf-8"));
const targetPrompts = prompts.slice(0, MAX_COUNT);

console.log("=".repeat(60));
console.log("  ImageFX Generator");
console.log("=".repeat(60));
console.log(`  Timestamp : ${timestamp}`);
console.log(`  Source    : ${promptsPath}`);
console.log(`  Output    : ${outputDir}`);
console.log(`  Prompts   : ${targetPrompts.length}`);
console.log(`  Delay     : ${DELAY_MS}ms`);
console.log(`  Dry Run   : ${DRY_RUN}`);
console.log("=".repeat(60));

// ─── Metadata builder ───
function cleanFilename(text) {
  return text.replace(/[^a-zA-Z0-9\s]/g, "").trim().replace(/\s+/g, "_").toLowerCase();
}

function buildMetadata(item, filenameBase) {
  const promptText = item.prompt;
  const subject = item.subject || "";
  const theme = item.theme || "";

  // Extract keywords from subject
  const subjectWords = cleanFilename(subject).split("_").filter((w) => w.length > 3);
  const themeWords = cleanFilename(theme).split("_").filter((w) => w.length > 3);
  const keywords = [...new Set([...themeWords, ...subjectWords])].slice(0, 10);

  // Add generic stock keywords
  const hasPeople = promptText.toLowerCase().includes("no people") || promptText.toLowerCase().includes("no face");
  keywords.push(hasPeople ? "no people" : "people");
  keywords.push("horizontal", "copy space");
  keywords.push(promptText.includes("3D") || promptText.includes("Digital Art") ? "illustration" : "photography");
  if (item.slot) keywords.push(item.slot);

  return {
    filename: `${filenameBase}.png`,
    title: subject || `${theme} stock image`,
    keywords: [...new Set(keywords)],
    category: item.category_id || 15,
    category_name: item.category || "Culture/Religion",
    asset_type: item.asset_type || (promptText.includes("3D") || promptText.includes("Digital Art") ? "illustration" : "photo"),
    prompt: promptText,
    is_ai_generated: true,
    is_fictional: true,
  };
}

// ─── Safety filter rephrase patterns ───
const SAFETY_REPHRASES = [
  // Remove gender-specific solo descriptions
  { from: /\b(young |elderly |female |male )?(woman|girl|lady)\b/gi, to: "person" },
  // Remove clothing that implies exposed skin
  { from: /\b(swimsuit|bikini|swimwear|underwear|lingerie)\b/gi, to: "casual clothing" },
  // Add group context
  { from: /\bsitting alone\b/gi, to: "sitting peacefully" },
  { from: /\bstanding alone\b/gi, to: "standing confidently" },
  // Remove vulnerability cues
  { from: /\bexhausted\b/gi, to: "contemplative" },
  { from: /\btired\b/gi, to: "thoughtful" },
];

function rephraseSafetyPrompt(originalPrompt) {
  let safe = originalPrompt;
  for (const rule of SAFETY_REPHRASES) {
    safe = safe.replace(rule.from, rule.to);
  }
  // Add safety suffix if people are mentioned
  if (/\b(person|people|team|group|couple|friends)\b/i.test(safe)) {
    safe = safe.replace(
      /sharp focus,/,
      "diverse group setting, professional context, sharp focus,"
    );
  }
  return safe;
}

// ─── Results log (for report) ───
const results = [];

// ─── Main ───
const fx = DRY_RUN ? null : new ImageFX(cookie);
let successCount = 0;
let failCount = 0;
let authFailed = false;

for (let i = 0; i < targetPrompts.length; i++) {
  // Early exit on auth failure — don't waste time on remaining prompts
  if (authFailed) {
    results.push({ id: i + 1, filename: targetPrompts[i].filename || "skipped", status: "SKIP", message: "Skipped due to auth failure" });
    failCount++;
    continue;
  }

  const item = targetPrompts[i];
  const filename = item.filename || cleanFilename((item.subject || "image").split(" ").slice(0, 5).join(" "));
  const filenameBase = `${filename}_${timestamp}`;

  console.log(`\n[${i + 1}/${targetPrompts.length}] ${filename}`);

  // 1. Save metadata JSON
  const metadata = buildMetadata(item, filenameBase);
  const jsonPath = join(outputDir, `${filenameBase}.json`);
  writeFileSync(jsonPath, JSON.stringify(metadata, null, 2), "utf-8");

  // 2. Generate image
  if (DRY_RUN) {
    results.push({ id: i + 1, filename, status: "SKIP", message: "Dry run" });
    continue;
  }

  let generated = false;
  let promptText = item.prompt;

  // Try original prompt first, then rephrased if safety-filtered
  for (let attempt = 0; attempt < 2 && !generated; attempt++) {
    try {
      if (attempt === 1) {
        promptText = rephraseSafetyPrompt(item.prompt);
        console.log(`  [RETRY] Rephrased for safety filter...`);
      }

      const prompt = new Prompt({
        prompt: promptText,
        numberOfImages: 1,
        aspectRatio: "IMAGE_ASPECT_RATIO_LANDSCAPE",
        generationModel: "IMAGEN_3_5",
        seed: (item.id || i + 1) * 1000 + i + attempt,
      });

      const images = await fx.generateImage(prompt, 1);

      if (images.length > 0) {
        const imgPath = join(outputDir, `${filenameBase}.png`);
        writeFileSync(imgPath, images[0].encodedImage, "base64");
        console.log(`  [OK] seed=${images[0].seed}${attempt > 0 ? " (rephrased)" : ""}`);
        results.push({ id: i + 1, filename, status: "OK", seed: images[0].seed, rephrased: attempt > 0 });
        successCount++;
        generated = true;
      }
    } catch (error) {
      const isSafety = error.message.includes("UNSAFE_GENERATION");
      const isAuth = error.message.includes("401") || error.message.includes("UNAUTHENTICATED");

      if (isAuth) {
        console.error(`  [AUTH FAIL] Cookie expired or invalid. Stopping all remaining images.`);
        results.push({ id: i + 1, filename, status: "FAIL", message: "AUTH: Cookie expired" });
        failCount++;
        authFailed = true;
        break;
      }

      if (isSafety && attempt === 0) {
        // Will retry with rephrased prompt
        continue;
      }
      console.error(`  [FAIL] ${error.message}`);
      results.push({ id: i + 1, filename, status: "FAIL", message: error.message });
      failCount++;
    }
  }

  // 3. Rate limiting
  if (i < targetPrompts.length - 1) {
    await new Promise((r) => setTimeout(r, DELAY_MS));
  }
}

// ─── Save results JSON (for report generator) ───
const resultData = {
  timestamp,
  outputDir,
  promptsSource: promptsPath,
  total: targetPrompts.length,
  success: successCount,
  failed: failCount,
  dryRun: DRY_RUN,
  results,
};

writeFileSync(join(outputDir, "_results.json"), JSON.stringify(resultData, null, 2), "utf-8");

console.log("\n" + "=".repeat(60));
console.log(`  Done! Success: ${successCount} | Failed: ${failCount}`);
console.log(`  Output: ${outputDir}`);
console.log("=".repeat(60));

// Output timestamp for bat script to capture
console.log(`TIMESTAMP=${timestamp}`);
