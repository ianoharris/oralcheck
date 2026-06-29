import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { marked } from "marked";

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

export interface Article extends ArticleMeta {
  html: string;
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

function parseFile(dir: string, filename: string): Article {
  const raw = fs.readFileSync(path.join(dir, filename), "utf8");
  const { data, content } = matter(raw);
  const body = stripLeadingH1(content);
  return {
    slug:     slugFromFilename(filename),
    title:    data.title  ?? slugFromFilename(filename),
    date:     data.date   ?? "",
    keyword:  data.keyword ?? "",
    excerpt:  firstParagraph(content),
    filename,
    html: marked(body) as string,
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

export function getAllPublishedArticles(): ArticleMeta[] {
  return listDir(PUBLISHED_DIR).map((f) => {
    const raw = fs.readFileSync(path.join(PUBLISHED_DIR, f), "utf8");
    const { data, content } = matter(raw);
    return {
      slug:     slugFromFilename(f),
      title:    data.title  ?? slugFromFilename(f),
      date:     data.date   ?? "",
      keyword:  data.keyword ?? "",
      excerpt:  firstParagraph(content),
      filename: f,
    };
  });
}

export function getPublishedArticle(slug: string): Article | null {
  const match = listDir(PUBLISHED_DIR).find(
    (f) => slugFromFilename(f) === slug
  );
  return match ? parseFile(PUBLISHED_DIR, match) : null;
}

export function getAllDraftArticles(): ArticleMeta[] {
  return listDir(DRAFTS_DIR).map((f) => {
    const raw = fs.readFileSync(path.join(DRAFTS_DIR, f), "utf8");
    const { data, content } = matter(raw);
    return {
      slug:     slugFromFilename(f),
      title:    data.title  ?? slugFromFilename(f),
      date:     data.date   ?? "",
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
