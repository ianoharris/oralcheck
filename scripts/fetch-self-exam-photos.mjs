#!/usr/bin/env node
/**
 * One-off: pull the NIH "Detecting Oral Cancer" demonstration series (DOC 1-15)
 * from Wikimedia Commons into public/self-exam/, and write the manifest the
 * self-exam page renders.
 *
 * Unlike the /learn/signs photos, these are not lesion images. They show a
 * clinician demonstrating each step of the exam, so they render inline rather
 * than behind a reveal.
 *
 * The series is a US federal government work and therefore public domain, but
 * the licence is still checked per file rather than assumed.
 */
import fs from "node:fs/promises";
import path from "node:path";

const OUT_DIR = path.join(process.cwd(), "public", "self-exam");
const MANIFEST = path.join(process.cwd(), "src", "lib", "selfExamPhotos.json");
const UA = "OralCheck/1.0 (+https://oralcheck.org)";

// stepSlug -> Commons files, in the order they should appear under that step.
// stepSlug matches STEP_SLUGS in the self-exam page, which is parallel to the
// translated `steps` array in messages/*.json.
const WANTED = [
  { slug: "face-neck", files: ["NIH DOC 1 face.jpg"] },
  { slug: "lips",      files: ["NIH DOC 2 lip.jpg", "NIH DOC 3 labialmucosa.jpg", "NIH DOC 4 labialmucosa.jpg"] },
  { slug: "cheeks",    files: ["NIH DOC 5 buccalmucosa1.jpg", "NIH DOC 6 buccalmucosa2.jpg"] },
  { slug: "gums",      files: ["NIH DOC 7 gingiva.jpg"] },
  { slug: "tongue",    files: ["NIH DOC 8 TongueDorsum.jpg", "NIH DOC 9 TongueLeftMargin.jpg", "NIH DOC 10 TongueRightMargin.jpg", "NIH DOC 11 TongueVentral.jpg"] },
  // DOC 15 is bimanual palpation under the chin with the mouth open, which is
  // the floor-of-mouth step in the NIH sequence, not neck palpation.
  { slug: "floor",     files: ["NIH DOC 12 MouthFloor.jpg", "NIH DOC 15 palpation.jpg"] },
  { slug: "palate",    files: ["NIH DOC 13 HardPalate.jpg"] },
  { slug: "throat",    files: ["NIH DOC 14 Oropharynx.jpg"] },
];

const strip = (html) => (html || "").replace(/<[^>]*>/g, "").replace(/\s+/g, " ").trim();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Commons rate-limits bursts of 15+ requests with a 429. Back off and retry
// rather than failing the run half way through and leaving a partial manifest.
async function get(url) {
  for (let attempt = 0; attempt < 5; attempt++) {
    const res = await fetch(url, { headers: { "User-Agent": UA } });
    if (res.ok) return res;
    if (res.status !== 429 && res.status < 500) {
      throw new Error(`${url} -> ${res.status}`);
    }
    const wait = 1000 * 2 ** attempt;
    console.log(`  ${res.status}, retrying in ${wait}ms`);
    await sleep(wait);
  }
  throw new Error(`${url} -> gave up after 5 attempts`);
}

async function meta(file) {
  const url = "https://commons.wikimedia.org/w/api.php?" + new URLSearchParams({
    action: "query", titles: `File:${file}`, prop: "imageinfo",
    iiprop: "url|size|extmetadata", format: "json",
  });
  const r = await get(url);
  const j = await r.json();
  const page = Object.values(j.query.pages)[0];
  const ii = (page.imageinfo || [])[0];
  if (!ii) throw new Error(`no imageinfo for ${file}`);
  const m = ii.extmetadata || {};
  return {
    url: ii.url,
    width: ii.width,
    height: ii.height,
    description: strip((m.ImageDescription || {}).value).slice(0, 300),
    author: strip((m.Artist || {}).value) || "National Institutes of Health",
    license: (m.LicenseShortName || {}).value || "unknown",
    licenseUrl: (m.LicenseUrl || {}).value || "",
    source: `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(file)}`,
  };
}

const ALLOWED = /^(public domain|cc0|cc by|cc by-sa)/i;

await fs.mkdir(OUT_DIR, { recursive: true });
const manifest = {};

for (const { slug, files } of WANTED) {
  const entries = [];
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const m = await meta(file);
    if (!ALLOWED.test(m.license)) {
      console.log(`SKIP ${file}: licence "${m.license}" not permitted`);
      continue;
    }
    const name = files.length > 1 ? `${slug}-${i + 1}.jpg` : `${slug}.jpg`;
    const res = await get(m.url);
    await fs.writeFile(path.join(OUT_DIR, name), Buffer.from(await res.arrayBuffer()));
    entries.push({
      src: `/self-exam/${name}`,
      width: m.width,
      height: m.height,
      description: m.description,
      author: m.author,
      license: m.license,
      licenseUrl: m.licenseUrl,
      source: m.source,
    });
    console.log(`OK   ${name}  ${m.width}x${m.height}  ${m.license}`);
    await sleep(400);
  }
  if (entries.length) manifest[slug] = entries;
}

await fs.writeFile(MANIFEST, JSON.stringify(manifest, null, 2) + "\n");
console.log(`\nwrote ${MANIFEST} (${Object.keys(manifest).length} steps)`);
