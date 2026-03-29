/**
 * Claude CLI로 동적 프롬프트 생성
 * Usage: node src/generate-prompts.js [--count 50]
 */

import { execSync } from "child_process";
import { readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");

const args = process.argv.slice(2);
const getArg = (name) => {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : null;
};

const COUNT = getArg("count") ? parseInt(getArg("count")) : 50;
const OUTPUT = resolve(PROJECT_ROOT, "prompts.json");

// Read system prompt template
const template = readFileSync(resolve(__dirname, "prompt-system.md"), "utf-8");
const today = new Date().toISOString().split("T")[0];
const systemPrompt = template
  .replace(/\{\{COUNT\}\}/g, String(COUNT))
  .replace(/\{\{TODAY\}\}/g, today);

console.log(`[*] Generating ${COUNT} prompts via Claude CLI...`);

// Build the user message
const userMessage = `Generate ${COUNT} Adobe Stock image prompts. Today is ${today}. Return ONLY the JSON array, nothing else.`;

try {
  // Combine system prompt + user message into a single prompt for -p mode
  const fullPrompt = `${systemPrompt}\n\n---\n\nNow generate ${COUNT} prompts. Today is ${today}. Return ONLY the JSON array.`;

  // Write to temp file to avoid shell escaping issues
  const tempPromptPath = resolve(PROJECT_ROOT, ".tmp-prompt.txt");
  writeFileSync(tempPromptPath, fullPrompt, "utf-8");

  // Use stdin pipe via temp file
  const result = execSync(
    `cat "${tempPromptPath.replace(/\\/g, "/")}" | claude -p --output-format text --model claude-opus-4-6`,
    {
      cwd: PROJECT_ROOT,
      encoding: "utf-8",
      timeout: 180000,
      maxBuffer: 10 * 1024 * 1024,
      shell: "bash",
    }
  );

  // Extract JSON from response (handle possible markdown wrapping)
  let jsonStr = result.trim();
  const jsonMatch = jsonStr.match(/\[[\s\S]*\]/);
  if (!jsonMatch) {
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
  console.log(`  Seasonal: ${prompts.filter((p) => p.slot === "seasonal").length}`);
  console.log(`  Evergreen: ${prompts.filter((p) => p.slot === "evergreen").length}`);
  console.log(`  OutOfBox: ${prompts.filter((p) => p.slot === "outofbox").length}`);
  console.log(`  Trending: ${prompts.filter((p) => p.slot === "trending").length}`);
} catch (error) {
  console.error(`[FAIL] Prompt generation failed: ${error.message}`);
  process.exit(1);
}
