#!/usr/bin/env node
/**
 * Keeps every translated messages/<locale>.json in sync with messages/en.json.
 *
 * Run this any time English copy is added or changed anywhere on the site
 * (a new page, a new component, an edited sentence). For each target locale it
 * walks both message trees, finds every English string that is missing from
 * that locale (or has changed since it was machine-translated last time), and
 * asks Claude to translate just those, then writes the result back in place.
 *
 * Target locales come from src/i18n/routing.ts, so adding a language there is
 * the only step needed to start translating it.
 *
 * Each locale gets its OWN snapshot (messages/.en.snapshot.<locale>.json).
 * A single shared snapshot silently breaks the moment a second language
 * exists: syncing Spanish would stamp the snapshot as fully translated, and
 * Portuguese would then see nothing stale and skip every changed string.
 *
 * Usage:
 *   node scripts/i18n-sync.mjs                # every locale, what changed
 *   node scripts/i18n-sync.mjs --locale=pt    # one locale
 *   node scripts/i18n-sync.mjs --force        # retranslate everything
 *
 * Requires ANTHROPIC_API_KEY in the environment.
 */
import fs from "fs";
import path from "path";
import Anthropic from "@anthropic-ai/sdk";

const ROOT = path.join(import.meta.dirname, "..");
const EN_PATH = path.join(ROOT, "messages", "en.json");
const ROUTING_PATH = path.join(ROOT, "src", "i18n", "routing.ts");

const FORCE = process.argv.includes("--force");
const ONLY = (process.argv.find((a) => a.startsWith("--locale=")) || "").split("=")[1];

const localePath = (l) => path.join(ROOT, "messages", `${l}.json`);
const snapshotPath = (l) => path.join(ROOT, "messages", `.en.snapshot.${l}.json`);

// How each locale should be described to the translator. A locale missing from
// here is a hard error rather than a guess: "translate to pt" without saying
// Brazilian Portuguese, for a health audience, is exactly the sort of silent
// wrong answer that is expensive to notice later.
const LOCALE_BRIEF = {
  es: {
    name: "Spanish",
    detail:
      "Latin American / neutral Spanish, suitable for the US Hispanic community. " +
      "Medical terms should read the way a Spanish-speaking patient (general public, " +
      "not a clinician) would expect to see them on a health site.",
  },
  pt: {
    name: "Brazilian Portuguese",
    detail:
      "Brazilian Portuguese (pt-BR), not European Portuguese. The audience is the " +
      "Brazilian general public, so use Brazilian vocabulary and spelling throughout " +
      "(for example 'usuário', 'câncer bucal', 'odontologista' or 'dentista'). " +
      "Medical terms should read the way a Brazilian patient, not a clinician, would " +
      "expect to see them on a health site.",
  },
};

/** Locales to translate into, read from routing.ts so there is one source of truth. */
function targetLocales() {
  const src = fs.readFileSync(ROUTING_PATH, "utf8");
  const locales = (src.match(/locales:\s*\[([^\]]*)\]/) || [])[1];
  const def = (src.match(/defaultLocale:\s*["']([^"']+)["']/) || [])[1];
  if (!locales || !def) {
    throw new Error("Could not read locales/defaultLocale from src/i18n/routing.ts");
  }
  const all = [...locales.matchAll(/["']([a-zA-Z-]+)["']/g)].map((m) => m[1]);
  return all.filter((l) => l !== def);
}

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

async function translateBatch(client, entries, locale) {
  // entries: [[dottedKey, englishText], ...]
  const payload = Object.fromEntries(entries);

  const brief = LOCALE_BRIEF[locale];
  if (!brief) {
    throw new Error(
      `No translator brief for locale "${locale}". Add one to LOCALE_BRIEF in this file ` +
      `before translating into it, so the register and regional variant are stated explicitly.`
    );
  }

  const prompt = `You are translating UI and content copy for OralCheck, a free, private oral cancer risk screener. The brand voice is calm, grounded, and evidence-based: no exclamation points, no hype, no em dashes (use commas, colons, or periods instead), and first person is never used ("we"). ${brief.detail} Keep any ICU placeholders like {year} or {name} exactly as-is, unchanged. Keep any HTML-like tags exactly as-is (e.g. <b>, </b>). Preserve punctuation style (e.g. arrows like "→" stay as-is). Do not add quotation marks around values that don't already have them.

Translate every value in this JSON object from English to ${brief.name}. Return ONLY a JSON object with the exact same keys, translated values, no commentary, no markdown fences.

${JSON.stringify(payload, null, 2)}`;

  // Streamed: at this max_tokens the SDK rejects a non-streaming call outright,
  // since a slow generation could outrun the request timeout.
  const msg = await client.messages
    .stream({
      // Translation is not a frontier-model task, and this runs on every copy
      // change. Opus 4.8 costs 5x Sonnet's input and output for a job Sonnet
      // does indistinguishably well on UI strings. Override with I18N_MODEL if
      // a particular batch ever reads badly.
      model: process.env.I18N_MODEL || "claude-sonnet-4-6",
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
        ...(await translateBatch(client, a, locale)),
        ...(await translateBatch(client, b, locale)),
      };
    }
    throw err;
  }
}

async function syncLocale(client, en, enFlat, locale) {
  const target = readJson(localePath(locale));
  const snapshot = FORCE ? {} : readJson(snapshotPath(locale));
  const targetFlat = flatten(target);
  const snapFlat = flatten(snapshot);

  // Needs translation if: missing from this locale entirely, OR the English
  // text changed since the last time we translated it for this locale.
  //
  // The staleness check compares by VALUE, not by reference. `flatten` keeps
  // arrays as leaves, and two arrays parsed from two different files are never
  // `!==`-equal even when their contents are identical. The previous strict
  // comparison therefore marked every array-valued key stale on every run, for
  // ever: 45 of them here, and they hold the largest blocks of copy on the site
  // (the Terms and Privacy sections, the learn-page lists, the checklists).
  // Every sync retranslated all of it and paid for it again, whether or not a
  // single word had changed.
  const changed = (a, b) =>
    typeof a === "object" || typeof b === "object"
      ? JSON.stringify(a) !== JSON.stringify(b)
      : a !== b;

  const toTranslate = Object.entries(enFlat).filter(([key, val]) => {
    const missing = !(key in targetFlat) || targetFlat[key] === "" || targetFlat[key] == null;
    const stale = snapFlat[key] !== undefined && changed(snapFlat[key], val);
    return missing || stale;
  });

  if (toTranslate.length === 0) {
    console.log(`  ${locale}: already up to date.`);
    return 0;
  }

  console.log(`  ${locale}: translating ${toTranslate.length} key(s)...`);

  const BATCH_SIZE = 40;
  const merged = { ...targetFlat };

  for (let i = 0; i < toTranslate.length; i += BATCH_SIZE) {
    const batch = toTranslate.slice(i, i + BATCH_SIZE);
    console.log(
      `    batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(toTranslate.length / BATCH_SIZE)} (${batch.length} keys)`
    );
    const translated = await translateBatch(client, batch, locale);
    for (const [key] of batch) {
      if (translated[key] !== undefined) merged[key] = translated[key];
      else console.warn(`    ! no translation returned for "${key}", leaving as-is`);
    }
  }

  // Rebuild the nested file in the same shape/order as en.json.
  const nested = {};
  for (const [key, val] of Object.entries(merged)) setPath(nested, key, val);
  const ordered = sortLikeEn(en, nested);

  fs.writeFileSync(localePath(locale), JSON.stringify(ordered, null, 2) + "\n");
  // Snapshot only after a successful write, and only for this locale.
  fs.writeFileSync(snapshotPath(locale), JSON.stringify(en, null, 2) + "\n");

  console.log(`  ${locale}: updated ${toTranslate.length} key(s).`);
  return toTranslate.length;
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error("ANTHROPIC_API_KEY is not set.");
    process.exit(1);
  }

  const locales = ONLY ? [ONLY] : targetLocales();
  if (locales.length === 0) {
    console.log("No target locales configured in src/i18n/routing.ts.");
    return;
  }

  const en = readJson(EN_PATH);
  const enFlat = flatten(en);
  const client = new Anthropic();

  console.log(`Syncing ${locales.join(", ")} against en.json...`);
  let total = 0;
  for (const locale of locales) {
    total += await syncLocale(client, en, enFlat, locale);
  }

  console.log(total === 0 ? "Everything already up to date." : `Done. ${total} key(s) translated.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
