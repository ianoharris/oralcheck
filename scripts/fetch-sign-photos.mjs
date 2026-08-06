#!/usr/bin/env node
/**
 * One-off: pull the clinical reference photos for the /learn/signs visual guide
 * from Wikimedia Commons into public/signs/, and write the attribution data the
 * component renders.
 *
 * Only images that are public domain or under a CC licence permitting
 * commercial use are eligible. Every non-PD image keeps its author, licence and
 * source URL so the page can credit it, which CC BY / CC BY-SA require.
 */
import fs from "node:fs/promises";
import path from "node:path";

const OUT_DIR = path.join(process.cwd(), "public", "signs");
const MANIFEST = path.join(process.cwd(), "src", "lib", "signPhotos.json");
const UA = "OralCheck/1.0 (+https://oralcheck.org)";

// signId -> Commons file. signId matches SIGN_META in SignsVisualGuide.
const WANTED = [
  { signId: "white", file: "Leukoplakia.jpg" },
  { signId: "mixed", file: "NIH DOC 19 Erythroleukoplakia.jpg" },
  { signId: "sore",  file: "Oral Carcinoma Cuniculatum.jpg" },
  { signId: "lip",   file: "Actinic Cheilitis Photo.jpg" },
];

const strip = (html) => (html || "").replace(/<[^>]*>/g, "").replace(/\s+/g, " ").trim();

async function meta(file) {
  const url = "https://commons.wikimedia.org/w/api.php?" + new URLSearchParams({
    action: "query", titles: `File:${file}`, prop: "imageinfo",
    iiprop: "url|size|extmetadata", format: "json",
  });
  const r = await fetch(url, { headers: { "User-Agent": UA } });
  const j = await r.json();
  const page = Object.values(j.query.pages)[0];
  const ii = (page.imageinfo || [])[0];
  if (!ii) throw new Error(`no imageinfo for ${file}`);
  const m = ii.extmetadata || {};
  return {
    url: ii.url,
    width: ii.width,
    height: ii.height,
    description: strip((m.ImageDescription || {}).value).slice(0, 200),
    author: strip((m.Artist || {}).value) || "Unknown",
    license: (m.LicenseShortName || {}).value || "unknown",
    licenseUrl: (m.LicenseUrl || {}).value || "",
    source: `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(file)}`,
  };
}

const ALLOWED = /^(public domain|cc0|cc by|cc by-sa)/i;

await fs.mkdir(OUT_DIR, { recursive: true });
const manifest = {};

for (const { signId, file } of WANTED) {
  const m = await meta(file);
  if (!ALLOWED.test(m.license)) {
    console.log(`SKIP ${signId}: licence "${m.license}" not permitted`);
    continue;
  }
  const ext = path.extname(new URL(m.url).pathname) || ".jpg";
  const local = `${signId}${ext}`;
  const bytes = Buffer.from(await (await fetch(m.url, { headers: { "User-Agent": UA } })).arrayBuffer());
  await fs.writeFile(path.join(OUT_DIR, local), bytes);

  manifest[signId] = {
    src: `/signs/${local}`,
    width: m.width,
    height: m.height,
    author: m.author,
    license: m.license,
    licenseUrl: m.licenseUrl,
    source: m.source,
  };
  console.log(`${signId.padEnd(6)} ${m.width}x${m.height}  [${m.license}]  ${(bytes.length/1024).toFixed(0)}KB`);
  console.log(`       author: ${m.author.slice(0, 60)}`);
  console.log(`       desc:   ${m.description.slice(0, 80)}`);
  await new Promise((r) => setTimeout(r, 800));
}

await fs.writeFile(MANIFEST, JSON.stringify(manifest, null, 2) + "\n");
console.log(`\nwrote ${Object.keys(manifest).length} entries -> src/lib/signPhotos.json`);
