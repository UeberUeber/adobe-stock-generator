/**
 * Claude CLI로 동적 프롬프트 생성
 * - 과거 생성 히스토리를 읽어서 반복 방지
 * Usage: node src/generate-prompts.js [--count 50]
 */

import { execSync } from "child_process";
import { readFileSync, writeFileSync, readdirSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");
const GENERATIONS_DIR = resolve(PROJECT_ROOT, "..", "generations");

const args = process.argv.slice(2);
const getArg = (name) => {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : null;
};

const COUNT = getArg("count") ? parseInt(getArg("count")) : 50;
const OUTPUT = resolve(PROJECT_ROOT, "prompts.json");

// ─── 과거 생성 히스토리 수집 ───
function getRecentFilenames(daysBack = 14) {
  if (!existsSync(GENERATIONS_DIR)) return [];

  const cutoff = Date.now() - daysBack * 24 * 60 * 60 * 1000;
  const filenames = new Set();

  try {
    const folders = readdirSync(GENERATIONS_DIR, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name)
      .sort()
      .reverse();

    for (const folder of folders) {
      // Parse folder timestamp (e.g., 2026-03-30_22-40-00)
      const match = folder.match(/^(\d{4})-(\d{2})-(\d{2})/);
      if (!match) continue;

      const folderDate = new Date(`${match[1]}-${match[2]}-${match[3]}`);
      if (folderDate.getTime() < cutoff) break;

      const folderPath = resolve(GENERATIONS_DIR, folder);
      try {
        const files = readdirSync(folderPath);
        for (const f of files) {
          if (!f.endsWith(".png")) continue;
          // Strip timestamp suffix: "abstract_blue_2026-03-30_22-40-00.png" → "abstract_blue"
          const name = f.replace(/_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.png$/, "");
          if (name && name !== f) filenames.add(name);
        }
      } catch (e) {
        // skip unreadable folders
      }
    }
  } catch (e) {
    console.error(`[WARN] Could not read generation history: ${e.message}`);
  }

  return [...filenames];
}

// ─── 시스템 프롬프트 조립 ───
const template = readFileSync(resolve(__dirname, "prompt-system.md"), "utf-8");
const today = new Date().toISOString().split("T")[0];

const recentNames = getRecentFilenames(14);
let historySection = "";
if (recentNames.length > 0) {
  historySection = `The following ${recentNames.length} images were already generated in the past 14 days. Do NOT generate similar concepts. Use this list to push yourself into NEW territory:\n${recentNames.join(", ")}`;
} else {
  historySection =
    "No recent generation history found. Generate diverse concepts freely.";
}

const systemPrompt = template
  .replace(/\{\{COUNT\}\}/g, String(COUNT))
  .replace(/\{\{TODAY\}\}/g, today)
  .replace(/\{\{HISTORY_SECTION\}\}/g, historySection);

console.log(`[*] Generating ${COUNT} prompts via Claude CLI...`);
console.log(`[*] Recent history: ${recentNames.length} unique images from last 14 days`);

// ─── Claude CLI 호출 ───
const userMessage = `Generate ${COUNT} Adobe Stock image prompts. Today is ${today}. Return ONLY the JSON array, nothing else.`;

try {
  const fullPrompt = `${systemPrompt}\n\n---\n\nNow generate ${COUNT} prompts. Today is ${today}. Return ONLY the JSON array.`;

  const tempPromptPath = resolve(PROJECT_ROOT, ".tmp-prompt.txt");
  writeFileSync(tempPromptPath, fullPrompt, "utf-8");

  const result = execSync(
    `cat "${tempPromptPath.replace(/\\/g, "/")}" | claude -p --output-format text --model claude-sonnet-4-20250514`,
    {
      cwd: PROJECT_ROOT,
      encoding: "utf-8",
      timeout: 180000,
      maxBuffer: 10 * 1024 * 1024,
      shell: "bash",
    }
  );

  // Extract JSON from response (handle markdown code fences)
  let jsonStr = result.trim();
  // Strip markdown code fences if present
  jsonStr = jsonStr.replace(/^```(?:json)?\s*\n?/gm, "").replace(/\n?```\s*$/gm, "");
  const jsonMatch = jsonStr.match(/\[[\s\S]*\]/);
  if (!jsonMatch) {
    console.error(`[DEBUG] Response preview: ${jsonStr.substring(0, 300)}`);
    throw new Error("No JSON array found in Claude response");
  }
  jsonStr = jsonMatch[0];

  const prompts = JSON.parse(jsonStr);

  if (!Array.isArray(prompts) || prompts.length === 0) {
    throw new Error("Parsed result is not a valid array");
  }

  // Add sequential IDs
  prompts.forEach((p, i) => (p.id = i + 1));

  writeFileSync(OUTPUT, JSON.stringify(prompts, null, 2), "utf-8");
  console.log(`[OK] ${prompts.length} prompts saved to prompts.json`);

  // Slot breakdown
  const slots = {};
  prompts.forEach((p) => {
    slots[p.slot] = (slots[p.slot] || 0) + 1;
  });
  for (const [slot, count] of Object.entries(slots).sort(
    (a, b) => b[1] - a[1]
  )) {
    console.log(`  ${slot}: ${count}`);
  }
} catch (error) {
  console.error(`[FAIL] Prompt generation failed: ${error.message}`);
  process.exit(1);
}
