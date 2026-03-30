/**
 * Report Generator - 파이프라인 결과 리포트 생성 + notepad 열기
 * Usage: node src/report.js <timestamp> [--error "error message"]
 */

import { readFileSync, writeFileSync, existsSync, readdirSync } from "fs";
import { resolve, dirname, join } from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");
const STOCK_GENERATOR_ROOT = resolve(PROJECT_ROOT, "..");
const REPORTS_DIR = resolve(PROJECT_ROOT, "reports");

const timestamp = process.argv[2];
if (!timestamp) {
  console.error("Usage: node src/report.js <timestamp> [--error 'msg']");
  process.exit(1);
}

// Check for pipeline-level error
const errorIdx = process.argv.indexOf("--error");
const pipelineError = errorIdx !== -1 ? process.argv[errorIdx + 1] : null;

const outputDir = join(STOCK_GENERATOR_ROOT, "generations", timestamp);
const upscaledDir = join(outputDir, "upscaled");
const resultsPath = join(outputDir, "_results.json");

// ─── Build report ───
const lines = [];
const now = new Date();
const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")} ${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}:${String(now.getSeconds()).padStart(2, "0")}`;

lines.push("=".repeat(60));
lines.push("  ImageFX Auto Pipeline Report");
lines.push(`  ${dateStr}`);
lines.push("=".repeat(60));
lines.push("");

if (pipelineError) {
  lines.push(`  STATUS: FAILED`);
  lines.push(`  FAILED STEP: ${pipelineError}`);
  lines.push("");
  lines.push("  Error Details:");
  lines.push(`  ${pipelineError}`);
  lines.push("");
  lines.push("  Troubleshooting:");
  if (pipelineError.includes("Cookie") || pipelineError.includes("Authentication") || pipelineError.includes("401")) {
    lines.push("  → Cookie expired. Re-extract from labs.google");
    lines.push("  → Update .env file in imagefx-generator/");
  } else if (pipelineError.includes("429") || pipelineError.includes("rate")) {
    lines.push("  → Rate limited. Increase --delay or reduce batch size");
  } else if (pipelineError.includes("claude") || pipelineError.includes("prompt")) {
    lines.push("  → Claude CLI prompt generation failed");
    lines.push("  → Check: claude --version");
  } else if (pipelineError.includes("upscale") || pipelineError.includes("pipeline")) {
    lines.push("  → Image processing failed (crop/upscale)");
    lines.push("  → Check GPU memory / torch installation");
  } else {
    lines.push(`  → Copy this error and ask Claude to diagnose`);
  }
} else {
  // Read generation results
  let genResults = null;
  if (existsSync(resultsPath)) {
    genResults = JSON.parse(readFileSync(resultsPath, "utf-8"));
  }

  // Count upscaled images
  let upscaledCount = 0;
  if (existsSync(upscaledDir)) {
    upscaledCount = readdirSync(upscaledDir).filter((f) => f.endsWith(".png")).length;
  }

  // Check CSV
  const csvPath = join(upscaledDir, "submission.csv");
  const csvExists = existsSync(csvPath);

  const allGood = genResults && genResults.failed === 0 && upscaledCount > 0 && csvExists;
  const partial = genResults && genResults.failed > 0;

  lines.push(`  STATUS: ${allGood ? "SUCCESS" : partial ? "PARTIAL" : "CHECK NEEDED"}`);
  lines.push("");
  lines.push(`  Timestamp : ${timestamp}`);
  lines.push(`  Generated : ${genResults ? `${genResults.success}/${genResults.total}` : "N/A"}`);
  lines.push(`  Upscaled  : ${upscaledCount}`);
  lines.push(`  CSV       : ${csvExists ? csvPath : "NOT FOUND"}`);
  lines.push(`  Output    : ${upscaledDir}`);
  lines.push("");

  if (genResults && genResults.results) {
    lines.push("-".repeat(60));
    lines.push("  Image Details:");
    lines.push("-".repeat(60));

    for (const r of genResults.results) {
      if (r.status === "OK") {
        lines.push(`  [${String(r.id).padStart(2)}] ${r.filename} — OK (seed: ${r.seed})`);
      } else if (r.status === "FAIL") {
        lines.push(`  [${String(r.id).padStart(2)}] ${r.filename} — FAIL`);
        lines.push(`       Error: ${r.message}`);
      } else {
        lines.push(`  [${String(r.id).padStart(2)}] ${r.filename} — ${r.status}`);
      }
    }
  }

  if (partial) {
    lines.push("");
    lines.push("-".repeat(60));
    lines.push("  Failed Items - Copy & ask Claude to diagnose:");
    lines.push("-".repeat(60));
    for (const r of genResults.results.filter((r) => r.status === "FAIL")) {
      lines.push(`  [${r.id}] ${r.filename}: ${r.message}`);
    }
  }
}

lines.push("");
lines.push("=".repeat(60));
lines.push("");

const reportContent = lines.join("\r\n");

// Save report
if (!existsSync(REPORTS_DIR)) {
  const { mkdirSync } = await import("fs");
  mkdirSync(REPORTS_DIR, { recursive: true });
}

const reportFilename = `report_${timestamp}.txt`;
const reportPath = join(REPORTS_DIR, reportFilename);
writeFileSync(reportPath, reportContent, "utf-8");

console.log(`[*] Report saved: ${reportPath}`);

// Open in notepad
try {
  execSync(`start notepad "${reportPath}"`, { shell: true });
} catch (e) {
  console.log("[*] Could not open notepad, report saved at:", reportPath);
}
