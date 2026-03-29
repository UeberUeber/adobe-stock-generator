/**
 * Metadata Enrichment — 캡션 + Claude로 키워드 30~35개 자동 생성
 *
 * 1. ImageFX captionImage API로 각 이미지 캡션 추출
 * 2. 캡션 + 원본 프롬프트를 Claude에게 넘겨 메타데이터 생성
 * 3. JSON 파일 덮어쓰기
 *
 * Usage: node src/enrich-metadata.js <timestamp>
 */

import { ImageFX } from "@rohitaryal/imagefx-api";
import { config } from "dotenv";
import { execSync } from "child_process";
import { resolve, dirname, join, extname } from "path";
import { fileURLToPath } from "url";
import { readFileSync, writeFileSync, readdirSync, existsSync } from "fs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");
const STOCK_ROOT = resolve(PROJECT_ROOT, "../adobe-stock-generator");

config({ path: resolve(PROJECT_ROOT, ".env") });

const timestamp = process.argv[2];
if (!timestamp) {
  console.error("Usage: node src/enrich-metadata.js <timestamp>");
  process.exit(1);
}

const cookie = process.env.GOOGLE_COOKIE;
if (!cookie) {
  console.error("[ERROR] GOOGLE_COOKIE not set in .env");
  process.exit(1);
}

const outputDir = join(STOCK_ROOT, "generations", timestamp);
if (!existsSync(outputDir)) {
  console.error(`[ERROR] Directory not found: ${outputDir}`);
  process.exit(1);
}

// ─── Step 1: Collect images and their existing metadata ───
const pngFiles = readdirSync(outputDir).filter(
  (f) => f.endsWith(".png") && !f.startsWith("_")
);
console.log(`[*] Found ${pngFiles.length} images in ${timestamp}`);

if (pngFiles.length === 0) {
  console.log("[*] No images to enrich.");
  process.exit(0);
}

// ─── Step 2: Generate captions via ImageFX API ───
console.log("[*] Generating captions via ImageFX API...");
const fx = new ImageFX(cookie);
const imageData = [];

for (const png of pngFiles) {
  const baseName = png.replace(".png", "");
  const jsonPath = join(outputDir, `${baseName}.json`);
  const imgPath = join(outputDir, png);

  let existingMeta = {};
  if (existsSync(jsonPath)) {
    existingMeta = JSON.parse(readFileSync(jsonPath, "utf-8"));
  }

  let caption = "";
  try {
    const captions = await fx.generateCaptionsFromImage(imgPath, "png", 1);
    caption = captions[0] || "";
    console.log(`  [OK] ${baseName}: "${caption.slice(0, 80)}..."`);
  } catch (error) {
    console.log(`  [WARN] Caption failed for ${baseName}: ${error.message}`);
    caption = existingMeta.prompt || "";
  }

  imageData.push({
    filename: png,
    baseName,
    caption,
    originalPrompt: existingMeta.prompt || "",
    category: existingMeta.category || 15,
    category_name: existingMeta.category_name || "",
    asset_type: existingMeta.asset_type || "photo",
  });
}

// ─── Step 3: Claude CLI — batch metadata generation ───
console.log(`\n[*] Generating metadata for ${imageData.length} images via Claude...`);

const claudePrompt = `You are an Adobe Stock metadata specialist. For each image below, generate optimized metadata for maximum search visibility and sales.

INPUT DATA (${imageData.length} images):
${JSON.stringify(imageData.map((d) => ({
  filename: d.filename,
  caption: d.caption,
  originalPrompt: d.originalPrompt,
  category_id: d.category,
  asset_type: d.asset_type,
})), null, 2)}

For EACH image, generate:
1. **title**: Natural English sentence/phrase describing the image.
   - MUST NOT start with "Professional", "Commercial", "High Quality", "Beautiful", "Stunning"
   - MUST read like a natural description, NOT keyword spam
   - GOOD: "Cozy living room with Christmas tree and glowing fireplace"
   - BAD: "christmas, tree, cozy, living room, holiday"
   - The core words in the title MUST also appear in the top 10 keywords

2. **keywords**: Exactly 30-35 keywords, ordered by importance:
   - Tier 1 (1-10): Core objects, main subject, primary action — HIGHEST search weight
   - Tier 2 (11-20): Setting, location, colors, lighting, mood, style
   - Tier 3 (21-30): Use cases (banner, background, wallpaper, poster, header), emotions, related concepts
   - Tier 4 (31-35): Long-tail niche terms, seasonal associations

3. **category_id**: Adobe Stock category (1-21). The PRIMARY SUBJECT determines the category.
   - Rose bouquet (Valentine's) = 14 (Plants), NOT 15 (Culture)
   - Heart pattern background = 8 (Graphic Resources), NOT 15
   - Christmas tree in living room = 15 (Culture)
   - Yoga/meditation scene = 12 (Lifestyle), NOT 18 (Sports)

KEYWORD RULES — STRICT:
- SINGULAR form only: "dog" not "dogs", "child" not "children", "leaf" not "leaves"
- All lowercase
- No duplicates
- No near-synonyms in the same tier: "dog, canine, puppy" → just "dog"
- Separate compound concepts: "red dress" → "red", "dress" as separate keywords
- For images with people, include: person count ("one person", "group"), age range, context

BANNED WORDS — NEVER include any of these:
- AI terms: AI, artificial intelligence, midjourney, stable diffusion, dall-e, generated, neural, machine learning, deep learning, render, rendering
- File/quality terms: PNG, JPEG, 4K, HD, UHD, 8K, high resolution, high quality, professional, stock photo, commercial
- Camera terms: Canon, Nikon, Sony, 50mm, f/1.8, ISO, DSLR, mirrorless, lens
- Brand names: Apple, Nike, Adidas, Starbucks, Google, Samsung, Microsoft, Coca-Cola, Dell, HP, Lenovo
- Celebrity/character names: any real person, any fictional character
- Style attribution: "in the style of", any artist name (Picasso, Van Gogh, etc.)

Return ONLY a JSON array:
[{"filename": "...", "title": "...", "keywords": [...], "category_id": N}]`;

const tempPromptPath = resolve(PROJECT_ROOT, ".tmp-enrich-prompt.txt");
writeFileSync(tempPromptPath, claudePrompt, "utf-8");

try {
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

  let jsonStr = result.trim();
  const jsonMatch = jsonStr.match(/\[[\s\S]*\]/);
  if (!jsonMatch) throw new Error("No JSON array in Claude response");

  const enriched = JSON.parse(jsonMatch[0]);

  // ─── Step 4: Update JSON files ───
  let updated = 0;
  for (const item of enriched) {
    const match = imageData.find((d) => d.filename === item.filename);
    if (!match) continue;

    const jsonPath = join(outputDir, `${match.baseName}.json`);
    let existing = {};
    if (existsSync(jsonPath)) {
      existing = JSON.parse(readFileSync(jsonPath, "utf-8"));
    }

    existing.title = item.title || existing.title;
    existing.keywords = item.keywords || existing.keywords;
    existing.category = item.category_id || existing.category;

    writeFileSync(jsonPath, JSON.stringify(existing, null, 2), "utf-8");
    updated++;
    console.log(`  [OK] ${match.baseName}: ${(item.keywords || []).length} keywords`);
  }

  console.log(`\n[OK] Enriched ${updated}/${pngFiles.length} metadata files.`);
} catch (error) {
  console.error(`[FAIL] Metadata enrichment failed: ${error.message}`);
  process.exit(1);
}
