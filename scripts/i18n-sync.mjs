#!/usr/bin/env node
/**
 * Keeps messages/es.json in sync with messages/en.json.
 *
 * Run this any time English copy is added or changed anywhere on the site
 * (a new page, a new component, an edited sentence). It walks both message
 * trees, finds every English string that's missing from the Spanish file
 * (or unchanged since it was machine-translated last time — tracked via
 * messages/.en.snapshot.json), and asks Claude to translate just those,
 * then writes the result back into es.json in place.
 *
 * Usage:
 *   node scripts/i18n-sync.mjs           # translate what changed
 *   node scripts/i18n-sync.mjs --force   # retranslate everything
 *
 * Requires ANTHROPIC_API_KEY in the environment.
 */
import fs from "fs";
import path from "path";
import Anthropic from "@anthropic-ai/sdk";

const ROOT = path.join(import.meta.dirname, "..");
const EN_PATH = path.join(ROOT, "messages", "en.json");
const ES_PATH = path.join(ROOT, "messages", "es.json");
const SNAPSHOT_PATH = path.join(ROOT, "messages", ".en.snapshot.json");

const FORCE = process.argv.includes("--force");

function readJson(p) {
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : {};
}

function isPlainObject(v) {
  return v !== null && typeof v === "object" && !Array.isArray(v);
}

// Flattens {"a": {"b": "c"}} -> {"a.b": "c"}
function flatten(obj, prefix = "", out = {}) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (isPlainObject(v)) flatten(v, key, out);
    else out[key] = v;
  }
  return out;
}

function setPath(obj, dottedKey, value) {
  const parts = dottedKey.split(".");
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (!isPlainObject(cur[parts[i]])) cur[parts[i]] = {};
    cur = cur[parts[i]];
  }
  cur[parts[parts.length - 1]] = value;
}

function sortLikeEn(enObj, esObj) {
  // Rebuilds esObj with the same key order/shape as enObj, dropping stale keys.
  if (Array.isArray(enObj)) return esObj;
  if (!isPlainObject(enObj)) return esObj;
  const out = {};
  for (const k of Object.keys(enObj)) {
    out[k] = sortLikeEn(enObj[k], isPlainObject(esObj) ? esObj[k] : undefined);
  }
  return out;
}

async function translateBatch(client, entries) {
  // entries: [[dottedKey, englishText], ...]
  const payload = Object.fromEntries(entries);

  const prompt = `You are translating UI and content copy for OralCheck, a free, private oral cancer risk screener. The brand voice is calm, grounded, and evidence-based: no exclamation points, no hype, no em dashes (use commas, colons, or periods instead), first person is never used ("we"), and medical terms should read the way a Spanish-speaking patient (general public, not a clinician) would expect to see them on a health site aimed at the US Hispanic community. Keep any ICU placeholders like {year} or {name} exactly as-is, unchanged. Keep any HTML-like tags exactly as-is (e.g. <b>, </b>). Preserve punctuation style (e.g. arrows like "→" stay as-is). Do not add quotation marks around values that don't already have them.

Translate every value in this JSON object from English to Spanish (Latin American / neutral, suitable for the US Hispanic community). Return ONLY a JSON object with the exact same keys, translated values, no commentary, no markdown fences.

${JSON.stringify(payload, null, 2)}`;

  // Streamed: at this max_tokens the SDK rejects a non-streaming call outright,
  // since a slow generation could outrun the request timeout.
  const msg = await client.messages
    .stream({
      model: "claude-opus-4-8",
      max_tokens: 32000,
      messages: [{ role: "user", content: prompt }],
    })
    .finalMessage();

  const text = msg.content.find((b) => b.type === "text")?.text ?? "{}";
  const cleaned = text.trim().replace(/^```(json)?/, "").replace(/```$/, "").trim();

  try {
    return JSON.parse(cleaned);
  } catch (err) {
    // A batch of long values can still outrun the output limit and come back
    // truncated mid-string. Halve it and retry rather than losing the whole run
    // (which previously died on the first oversized batch and translated none).
    if (entries.length > 1) {
      const mid = Math.ceil(entries.length / 2);
      console.warn(`    response unparseable for ${entries.length} keys, splitting`);
      const [a, b] = [entries.slice(0, mid), entries.slice(mid)];
      return {
        ...(await translateBatch(client, a)),
        ...(await translateBatch(client, b)),
      };
    }
    throw err;
  }
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error("ANTHROPIC_API_KEY is not set.");
    process.exit(1);
  }

  const en = readJson(EN_PATH);
  const es = readJson(ES_PATH);
  const snapshot = FORCE ? {} : readJson(SNAPSHOT_PATH);

  const enFlat = flatten(en);
  const esFlat = flatten(es);
  const snapFlat = flatten(snapshot);

  // Needs translation if: missing from es entirely, OR the English text
  // changed since the last time we translated it (snapshot mismatch).
  const toTranslate = Object.entries(enFlat).filter(([key, val]) => {
    const missing = !(key in esFlat) || esFlat[key] === "" || esFlat[key] == null;
    const stale = snapFlat[key] !== undefined && snapFlat[key] !== val;
    return missing || stale;
  });

  if (toTranslate.length === 0) {
    console.log("es.json is already up to date with en.json. Nothing to do.");
    return;
  }

  console.log(`Translating ${toTranslate.length} key(s)...`);

  const client = new Anthropic();
  const BATCH_SIZE = 40;
  const merged = { ...esFlat };

  for (let i = 0; i < toTranslate.length; i += BATCH_SIZE) {
    const batch = toTranslate.slice(i, i + BATCH_SIZE);
    console.log(
      `  batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(toTranslate.length / BATCH_SIZE)} (${batch.length} keys)`
    );
    const translated = await translateBatch(client, batch);
    for (const [key] of batch) {
      if (translated[key] !== undefined) merged[key] = translated[key];
      else console.warn(`  ! no translation returned for "${key}", leaving as-is`);
    }
  }

  // Rebuild nested es.json in the same shape/order as en.json.
  const nestedEs = {};
  for (const [key, val] of Object.entries(merged)) setPath(nestedEs, key, val);
  const orderedEs = sortLikeEn(en, nestedEs);

  fs.writeFileSync(ES_PATH, JSON.stringify(orderedEs, null, 2) + "\n");
  fs.writeFileSync(SNAPSHOT_PATH, JSON.stringify(en, null, 2) + "\n");

  console.log(`Done. Updated ${toTranslate.length} key(s) in messages/es.json.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
