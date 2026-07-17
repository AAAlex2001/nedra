import { access, stat, unlink } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import sharp from "sharp";

const publicDir = path.resolve(process.cwd(), "public");
const removeOriginals = process.argv.includes("--remove-originals");

const images = [
  { source: "block_2.jpg", quality: 80, preserveOriginal: true },
  { source: "contacts.jpg", quality: 78, maxWidth: 2560 },
  { source: "block_5.png", quality: 82 },
  { source: "block_6.png", quality: 80 },
  { source: "block_7.png", quality: 80 },
  { source: "block_8_left.png", quality: 82 },
  { source: "block_8_right.png", quality: 82 },
  { source: "block_9.png", quality: 82, maxWidth: 1200 },
  { source: "block_9_diplom.png", quality: 90 },
  { source: "block_11.png", quality: 80 },
  { source: "globe/globe.png", quality: 82, maxWidth: 1200 },
  { source: "nedra_doc_attest_metodica.jpg", quality: 90 },
  { source: "partners/bashmed.jpg", quality: 88, maxWidth: 250 },
  { source: "partners/stroyservice.png", quality: 90, maxWidth: 600 },
  { source: "partners/volkovskiygok.jpg", quality: 88, maxWidth: 200 },
  ...Array.from({ length: 6 }, (_, index) => ({
    source: `what_is_this/what_is_this_${index + 1}.png`,
    quality: 82,
  })),
  ...Array.from({ length: 9 }, (_, index) => ({
    source: `uslugi/${index + 1}.png`,
    quality: 82,
  })),
  ...Array.from({ length: 12 }, (_, index) => ({
    source: `docs/docs_${index + 1}.${index < 2 ? "png" : "jpg"}`,
    quality: 90,
  })),
];

const exists = async (filePath) => {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
};

let originalBytes = 0;
let optimizedBytes = 0;

for (const image of images) {
  const sourcePath = path.join(publicDir, image.source);
  const outputPath = sourcePath.replace(/\.(png|jpe?g)$/i, ".webp");

  if (!(await exists(sourcePath))) {
    if (await exists(outputPath)) {
      console.log(`skip: ${path.relative(publicDir, outputPath)} already exists`);
      continue;
    }

    throw new Error(`Image not found: ${sourcePath}`);
  }

  const sourceStat = await stat(sourcePath);
  let pipeline = sharp(sourcePath).rotate();

  if (image.maxWidth) {
    pipeline = pipeline.resize({
      width: image.maxWidth,
      withoutEnlargement: true,
      fit: "inside",
    });
  }

  await pipeline
    .webp({
      quality: image.quality,
      alphaQuality: Math.max(image.quality, 90),
      effort: 6,
      smartSubsample: true,
    })
    .toFile(outputPath);

  const outputStat = await stat(outputPath);
  originalBytes += sourceStat.size;
  optimizedBytes += outputStat.size;

  console.log(
    `${image.source} -> ${path.relative(publicDir, outputPath)}: ` +
      `${(sourceStat.size / 1024).toFixed(0)} KB -> ${(outputStat.size / 1024).toFixed(0)} KB`,
  );

  if (removeOriginals && !image.preserveOriginal) {
    await unlink(sourcePath);
  }
}

if (originalBytes > 0) {
  const savedPercent = Math.round((1 - optimizedBytes / originalBytes) * 100);
  console.log(
    `Total: ${(originalBytes / 1024 / 1024).toFixed(1)} MB -> ` +
      `${(optimizedBytes / 1024 / 1024).toFixed(1)} MB (${savedPercent}% smaller)`,
  );
}
