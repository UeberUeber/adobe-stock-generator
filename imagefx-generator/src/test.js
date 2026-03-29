import { ImageFX, Prompt } from "@rohitaryal/imagefx-api";
import { config } from "dotenv";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
config({ path: resolve(__dirname, "../.env") });

const cookie = process.env.GOOGLE_COOKIE;
if (!cookie) {
  console.error("[ERROR] GOOGLE_COOKIE not set in .env");
  process.exit(1);
}

const fx = new ImageFX(cookie);

const prompt = new Prompt({
  prompt: "Professional stock photo, a cup of coffee on a wooden table with morning sunlight, warm tones, shallow depth of field, commercial quality, 8k resolution",
  numberOfImages: 1,
  aspectRatio: "IMAGE_ASPECT_RATIO_LANDSCAPE",
  generationModel: "IMAGEN_3_5",
  seed: 42,
});

console.log("[*] Testing ImageFX API...");
console.log("[*] Prompt:", prompt.prompt);

try {
  const images = await fx.generateImage(prompt, 1);
  const outputDir = resolve(__dirname, "../output");

  images.forEach((image, i) => {
    const savedPath = image.save(outputDir);
    console.log(`[+] Image ${i + 1} saved: ${savedPath}`);
    console.log(`    Seed: ${image.seed}`);
    console.log(`    Model: ${image.model}`);
    console.log(`    MediaId: ${image.mediaId}`);
  });

  console.log("\n[OK] Test passed! ImageFX API is working.");
} catch (error) {
  console.error("[FAIL]", error.message);
  if (error.message.includes("Authentication")) {
    console.error("[TIP] Cookie may be expired. Re-extract from labs.google");
  }
  process.exit(1);
}
