import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { Marked, Renderer, type Tokens } from "marked";

const PUBLISHED_DIR = path.join(process.cwd(), "content/published");
const DRAFTS_DIR    = path.join(process.cwd(), "content/drafts");

export interface ArticleMeta {
  slug:    string;
  title:   string;
  date:    string;
  keyword: string;
  excerpt: string;
  filename: string;
}

/** An H2 in the article body, for the on-page contents list. */
export interface ArticleHeading {
  id:   string;
  text: string;
}

/** An outside source linked from the body, numbered in order of first citation. */
export interface ArticleSource {
  n:     number;
  href:  string;
  label: string;
  host:  string;
}

export interface Article extends ArticleMeta {
  /** Whole body as HTML (leading H1 removed). The draft review page renders this. */
  html: string;

  // ── Journal layout (published article page) ────────────────────────────
  // Every field below is derived from the markdown or from OPTIONAL front
  // matter, so an article written before the redesign renders without edits.

  /** Front matter `description`, if the article has one. */
  description: string;
  /** One or two plain-text sentences shown under the title, and used as the
   *  meta description. From `description`, else lifted from the opening
   *  paragraph (the sentences move, they are not duplicated). */
  standfirst: string;
  /** Body HTML for the journal layout: standfirst and trailing disclaimer
   *  lifted out (both are set separately by the page). */
  bodyHtml: string;
  headings: ArticleHeading[];
  sources:  ArticleSource[];
  /** Front matter `keyPoints` (list of strings). Never generated. */
  keyPoints: string[];
  /** Front matter `updated`, if the article has been revised since `date`. */
  updated: string;
  /** Front matter `author`. Empty when unnamed: the page then shows no byline. */
  author: string;
  /** The article's own closing disclaimer, as plain text; "" if it has none. */
  disclaimer: string;
  readingMinutes: number;
  /** Language the body is actually in ("en" when a translation is missing). */
  contentLocale: string;
}

function slugFromFilename(filename: string): string {
  return filename.replace(/^\d{4}-\d{2}-\d{2}-/, "").replace(/\.md$/, "");
}

function firstParagraph(content: string): string {
  return (
    content
      .split("\n")
      .find((l) => l.trim() && !l.startsWith("#"))
      ?.slice(0, 200) ?? ""
  );
}

function stripLeadingH1(content: string): string {
  return content.trimStart().replace(/^#[^#][^\n]*\n?/, "").trimStart();
}

// ── Markdown rendering ─────────────────────────────────────────────────────

const OWN_HOSTS = new Set(["oralcheck.org", "www.oralcheck.org"]);

function plainInline(md: string): string {
  return md
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/[*_`~]/g, "")
    .trim();
}

function slugify(text: string): string {
  return (
    text
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .toLowerCase()
      .replace(/&[a-z]+;/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "section"
  );
}

function externalHost(href: string): string | null {
  try {
    const u = new URL(href);
    if (u.protocol !== "http:" && u.protocol !== "https:") return null;
    return OWN_HOSTS.has(u.hostname) ? null : u.hostname.replace(/^www\./, "");
  } catch {
    return null;
  }
}

interface Rendered {
  html: string;
  headings: ArticleHeading[];
  sources: ArticleSource[];
}

/**
 * Renders article markdown with journal conventions: H2/H3 get stable ids for
 * the contents list, tables get a scroll wrapper so they never widen the page
 * on a phone, and every link to an outside site gets a superscript number
 * pointing at the Sources list. Nothing is added that the markdown does not
 * already contain: no link, no source, no citation.
 */
function renderMarkdown(md: string): Rendered {
  const headings: ArticleHeading[] = [];
  const sources: ArticleSource[] = [];
  const usedIds = new Map<string, number>();
  const cited = new Set<number>();

  const marked = new Marked({
    renderer: {
      heading(this: Renderer, token: Tokens.Heading) {
        const inner = this.parser.parseInline(token.tokens);
        if (token.depth < 2 || token.depth > 3) return false;
        const base = slugify(plainInline(token.text));
        const seen = usedIds.get(base) ?? 0;
        usedIds.set(base, seen + 1);
        const id = seen ? `${base}-${seen + 1}` : base;
        if (token.depth === 2) headings.push({ id, text: plainInline(token.text) });
        return `<h${token.depth} id="${id}">${inner}</h${token.depth}>\n`;
      },
      link(this: Renderer, token: Tokens.Link) {
        const out = Renderer.prototype.link.call(this, token);
        const host = externalHost(token.href);
        if (!host) return out;
        let src = sources.find((s) => s.href === token.href);
        if (!src) {
          src = { n: sources.length + 1, href: token.href, label: plainInline(token.text), host };
          sources.push(src);
        }
        // Only the first citation carries the id the Sources list links back to.
        const id = cited.has(src.n) ? "" : ` id="cite-${src.n}"`;
        cited.add(src.n);
        return `${out}<sup class="cite"><a href="#source-${src.n}"${id}>${src.n}</a></sup>`;
      },
      table(this: Renderer, token: Tokens.Table) {
        return `<div class="table-wrap">${Renderer.prototype.table.call(this, token)}</div>`;
      },
    },
  });

  const html = marked.parse(md, { async: false }) as string;
  return { html, headings, sources };
}

// ── Journal layout helpers ─────────────────────────────────────────────────

// Abbreviations whose full stop does not end a sentence.
const ABBREV = /\b(?:U\.S|U\.K|e\.g|i\.e|Dr|Drs|vs|etc|approx|No|St|Mr|Mrs|Ms|Sr|Sra|EE\.UU)\.$/i;

/**
 * The first one or two sentences of a paragraph, if they make a standfirst of
 * sensible length. Returns "" when the paragraph carries inline markup (a link
 * or emphasis would otherwise be split or lost).
 */
function leadingSentences(text: string): string {
  if (/[[\]*_`<>]/.test(text)) return "";
  const ends: number[] = [];
  const re = /[.!?](?=\s+["“¿¡(]?[A-ZÁÉÍÓÚÑ0-9])/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) && ends.length < 2) {
    if (ABBREV.test(text.slice(0, m.index + 1))) continue;
    ends.push(m.index + 1);
  }
  if (ends.length < 2) ends.push(text.length);
  const two = text.slice(0, ends[1]).trim();
  if (two.length <= 280) return two;
  const one = text.slice(0, ends[0]).trim();
  return one.length <= 280 ? one : "";
}

/** Splits the opening paragraph into standfirst + remainder. */
function liftStandfirst(body: string): { standfirst: string; rest: string } {
  // Only a plain opening paragraph: not a heading, quote, table, list or image.
  if (/^(?:[#>|!*+-]|\d+[.)]\s)/.test(body)) return { standfirst: "", rest: body };
  const para = body.match(/^([^\n]+(?:\n(?!\s*\n)[^\n]+)*)/);
  if (!para) return { standfirst: "", rest: body };
  const text = para[1].replace(/\s*\n\s*/g, " ").trim();
  const standfirst = leadingSentences(text);
  if (!standfirst) return { standfirst: "", rest: body };
  const remainder = text.slice(standfirst.length).trim();
  const after = body.slice(para[1].length).replace(/^\s+/, "");
  return {
    standfirst,
    rest: (remainder ? `${remainder}\n\n` : "") + after,
  };
}

// The generator ends every article with an italic one-paragraph disclaimer,
// usually after a rule. Each one is worded for its article (the survival
// article's notes that population figures do not predict individual outcomes),
// so it is kept, but lifted out of the body and set as the page's own
// disclaimer note instead of a stray italic paragraph after the last section.
const TRAILING_DISCLAIMER =
  /(?:\n\s*-{3,}\s*)?\n\s*[*_](?:Medical disclaimer|Disclaimer|Aviso m[eé]dico|Descargo de responsabilidad(?: m[eé]dica)?|Aviso legal)\s*:\s*([^\n]*?)[*_]\s*$/i;

function splitTrailingDisclaimer(body: string): { body: string; disclaimer: string } {
  const m = body.match(TRAILING_DISCLAIMER);
  const rest = m ? body.slice(0, m.index) : body;
  return {
    body: rest.replace(/\n\s*-{3,}\s*$/, "").trimEnd(),
    disclaimer: m ? plainInline(m[1]) : "",
  };
}

function wordCount(md: string): number {
  return plainInline(md).replace(/[#>|-]/g, " ").split(/\s+/).filter(Boolean).length;
}

function asString(v: unknown): string {
  if (v instanceof Date) return v.toISOString().slice(0, 10);
  return typeof v === "string" ? v.trim() : "";
}

function asStringList(v: unknown): string[] {
  return Array.isArray(v) ? v.filter((x): x is string => typeof x === "string" && !!x.trim()) : [];
}

function parseFile(dir: string, filename: string, contentLocale = "en"): Article {
  const raw = fs.readFileSync(path.join(dir, filename), "utf8");
  const { data, content } = matter(raw);
  const body = stripLeadingH1(content);
  const description = asString(data.description);

  const { body: trimmed, disclaimer } = splitTrailingDisclaimer(body);
  const lifted = description ? { standfirst: "", rest: trimmed } : liftStandfirst(trimmed);
  const layout = renderMarkdown(lifted.rest);

  return {
    slug:     slugFromFilename(filename),
    title:    data.title  ?? slugFromFilename(filename),
    date:     asString(data.date),
    keyword:  data.keyword ?? "",
    excerpt:  firstParagraph(content),
    filename,
    html: renderMarkdown(body).html,

    description,
    standfirst: description || lifted.standfirst,
    bodyHtml:  layout.html,
    headings:  layout.headings,
    sources:   layout.sources,
    keyPoints: asStringList(data.keyPoints ?? data.key_points),
    updated:   asString(data.updated),
    author:    asString(data.author),
    disclaimer,
    readingMinutes: Math.max(1, Math.round(wordCount(trimmed) / 220)),
    contentLocale,
  };
}

function listDir(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md") && f !== ".gitkeep")
    .sort()
    .reverse();
}

// English is the canonical article list (slugs/dates); Spanish is an
// optional same-filename translation living in a `es/` subdirectory,
// produced by oralcheck-agent/seo_pipeline.py and promoted alongside the
// English article on publish (see src/app/api/publish/route.ts). Any
// article not yet translated falls back to English rather than 404ing.

export function getAllPublishedArticles(locale: string = "en"): ArticleMeta[] {
  return listDir(PUBLISHED_DIR).map((f) => {
    const enRaw = fs.readFileSync(path.join(PUBLISHED_DIR, f), "utf8");
    const en = matter(enRaw);
    const esPath = path.join(PUBLISHED_DIR, "es", f);
    const useEs = locale === "es" && fs.existsSync(esPath);
    const { data, content } = useEs ? matter(fs.readFileSync(esPath, "utf8")) : en;
    return {
      slug:     slugFromFilename(f),
      title:    data.title  ?? en.data.title ?? slugFromFilename(f),
      date:     asString(data.date) || asString(en.data.date),
      keyword:  data.keyword ?? en.data.keyword ?? "",
      excerpt:  firstParagraph(content),
      filename: f,
    };
  });
}

/** Whether a same-filename translation exists for this slug (e.g. "es"). */
export function hasTranslation(slug: string, locale: string): boolean {
  if (locale === "en") return true;
  const match = listDir(PUBLISHED_DIR).find((f) => slugFromFilename(f) === slug);
  return !!match && fs.existsSync(path.join(PUBLISHED_DIR, locale, match));
}

export function getPublishedArticle(slug: string, locale: string = "en"): Article | null {
  const match = listDir(PUBLISHED_DIR).find(
    (f) => slugFromFilename(f) === slug
  );
  if (!match) return null;
  if (locale === "es") {
    const esPath = path.join(PUBLISHED_DIR, "es");
    if (fs.existsSync(path.join(esPath, match))) return parseFile(esPath, match, "es");
  }
  return parseFile(PUBLISHED_DIR, match);
}

/**
 * Up to `limit` other published articles, closest first: shared words in the
 * target keyword, then most recent. Purely mechanical, no editorial claims.
 */
export function getRelatedArticles(slug: string, locale: string, limit = 3): ArticleMeta[] {
  const all = getAllPublishedArticles(locale);
  const current = all.find((a) => a.slug === slug);
  const words = (s: string) =>
    new Set(s.toLowerCase().split(/\W+/).filter((w) => w.length > 3 && w !== "oral" && w !== "cancer"));
  const mine = words(`${current?.keyword ?? ""} ${slug.replace(/-/g, " ")}`);
  return all
    .filter((a) => a.slug !== slug)
    .map((a) => {
      const theirs = words(`${a.keyword} ${a.slug.replace(/-/g, " ")}`);
      let score = 0;
      for (const w of theirs) if (mine.has(w)) score++;
      return { a, score };
    })
    .sort((x, y) => y.score - x.score || y.a.date.localeCompare(x.a.date))
    .slice(0, limit)
    .map(({ a }) => a);
}

export function getAllDraftArticles(): ArticleMeta[] {
  return listDir(DRAFTS_DIR).map((f) => {
    const raw = fs.readFileSync(path.join(DRAFTS_DIR, f), "utf8");
    const { data, content } = matter(raw);
    return {
      slug:     slugFromFilename(f),
      title:    data.title  ?? slugFromFilename(f),
      date:     asString(data.date),
      keyword:  data.keyword ?? "",
      excerpt:  firstParagraph(content),
      filename: f,
    };
  });
}

export function getDraftArticle(slug: string): Article | null {
  const match = listDir(DRAFTS_DIR).find(
    (f) => slugFromFilename(f) === slug
  );
  return match ? parseFile(DRAFTS_DIR, match) : null;
}
