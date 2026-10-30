import type { MetadataRoute } from "next";
import { routing } from "@/i18n/routing";
import {
  getAllPublishedArticles,
  getPublishedArticle,
  hasTranslation,
} from "@/lib/articles";

const BASE = "https://oralcheck.org";

/**
 * Every page, once, with its translations declared as alternates.
 *
 * Previously this listed English URLs only, so the Spanish site had never
 * appeared in the sitemap at all and search engines had no signal that
 * /es/<page> was the same page in another language. Listing translated URLs as
 * separate entries would be worse than useless (they read as duplicates);
 * `alternates.languages` is what tells a crawler they are one page in several
 * languages, and it is generated from routing.locales so a new language needs
 * no change here.
 */
type Entry = {
  path: string;
  changeFrequency: MetadataRoute.Sitemap[number]["changeFrequency"];
  priority: number;
};

const PAGES: Entry[] = [
  { path: "", changeFrequency: "monthly", priority: 1 },
  { path: "/screener", changeFrequency: "monthly", priority: 0.9 },
  { path: "/learn", changeFrequency: "monthly", priority: 0.9 },
  { path: "/learn/oral-cancer", changeFrequency: "monthly", priority: 0.9 },
  { path: "/learn/signs", changeFrequency: "monthly", priority: 0.9 },
  { path: "/learn/risk-factors", changeFrequency: "monthly", priority: 0.9 },
  { path: "/learn/hpv", changeFrequency: "monthly", priority: 0.8 },
  { path: "/learn/self-exam", changeFrequency: "monthly", priority: 0.8 },
  { path: "/learn/prevention", changeFrequency: "monthly", priority: 0.8 },
  { path: "/learn/canker-sore-vs-oral-cancer", changeFrequency: "monthly", priority: 0.8 },
  { path: "/learn/white-and-red-patches", changeFrequency: "monthly", priority: 0.8 },
  { path: "/learn/facts", changeFrequency: "monthly", priority: 0.7 },
  { path: "/find-care", changeFrequency: "monthly", priority: 0.8 },
  { path: "/for-clinicians", changeFrequency: "monthly", priority: 0.7 },
  { path: "/methods", changeFrequency: "yearly", priority: 0.6 },
  { path: "/about", changeFrequency: "monthly", priority: 0.6 },
  { path: "/press", changeFrequency: "monthly", priority: 0.4 },
  { path: "/privacy", changeFrequency: "yearly", priority: 0.3 },
  { path: "/qr", changeFrequency: "yearly", priority: 0.3 },
  { path: "/terms", changeFrequency: "yearly", priority: 0.3 },
];

/** "/es/screener" for a prefixed locale, "/screener" for the default one. */
function localeUrl(locale: string, path: string) {
  return locale === routing.defaultLocale
    ? `${BASE}${path}`
    : `${BASE}/${locale}${path}`;
}

/**
 * The published SEO articles, which this file used to leave out: Google had to
 * find them through /learn, yet they are what organic search actually lands on
 * (a symptom comparison is the top search landing page after the home page).
 * Only English and real Spanish translations are listed. Portuguese serves the
 * English text and canonicals to the English page, so listing it would point
 * crawlers at a page that disowns itself.
 */
function articleEntries(): MetadataRoute.Sitemap {
  return getAllPublishedArticles().map(({ slug, date }) => {
    const path = `/learn/${slug}`;
    const updated = getPublishedArticle(slug)?.updated || date;
    const languages: Record<string, string> = { en: localeUrl("en", path) };
    if (hasTranslation(slug, "es")) languages.es = localeUrl("es", path);
    return {
      url: localeUrl(routing.defaultLocale, path),
      lastModified: updated ? new Date(`${updated}T00:00:00Z`) : undefined,
      changeFrequency: "monthly" as const,
      priority: 0.7,
      alternates: { languages },
    };
  });
}

export default function sitemap(): MetadataRoute.Sitemap {
  const today = new Date("2026-08-27");

  const pages = PAGES.map(({ path, changeFrequency, priority }) => ({
    url: localeUrl(routing.defaultLocale, path),
    lastModified: today,
    changeFrequency,
    priority,
    alternates: {
      languages: Object.fromEntries(
        routing.locales.map((l) => [l, localeUrl(l, path)]),
      ),
    },
  }));

  return [...pages, ...articleEntries()];
}
