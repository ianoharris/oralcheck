import { Link } from "@/i18n/navigation";
import { notFound } from "next/navigation";
import type { Metadata, ResolvingMetadata } from "next";
import { getTranslations } from "next-intl/server";
import {
  getAllPublishedArticles,
  getPublishedArticle,
  getRelatedArticles,
  hasTranslation,
  type ArticleHeading,
} from "@/lib/articles";

// Layout borrows from clinical journals (NEJM, JAMA, BMJ, BDJ): an article-type
// label over the title, a standfirst, one quiet meta line, a contents rail,
// hairline rules instead of boxes, and numbered sources. It deliberately skips
// what only makes sense for researchers: author affiliations, DOIs, metrics,
// abstracts. See docs/OWNERS_GUIDE.md, "The article page".

const SITE_URL = "https://oralcheck.org";

type Props = { params: Promise<{ slug: string; locale: string }> };

export async function generateStaticParams() {
  return getAllPublishedArticles().map((a) => ({ slug: a.slug }));
}

function articleUrl(slug: string, contentLocale: string) {
  return contentLocale === "en"
    ? `${SITE_URL}/learn/${slug}`
    : `${SITE_URL}/${contentLocale}/learn/${slug}`;
}

export async function generateMetadata({ params }: Props, parent: ResolvingMetadata): Promise<Metadata> {
  const { slug, locale } = await params;
  const article = getPublishedArticle(slug, locale);
  if (!article) return {};
  // A translated article is its own canonical. An untranslated one (Portuguese
  // today) serves the English text, so it still points at the English page.
  const languages: Record<string, string> = { en: articleUrl(slug, "en") };
  if (hasTranslation(slug, "es")) languages.es = articleUrl(slug, "es");
  const url = articleUrl(slug, article.contentLocale);
  const description = article.standfirst || article.excerpt;
  // Setting openGraph here replaces the parent's object wholesale, so carry
  // over its share image (the Learn card) and site name explicitly. Before
  // this, a shared article previewed as the generic home page.
  const prev = await parent;
  const images = prev.openGraph?.images ?? [];
  return {
    title: article.title,
    description,
    alternates: {
      canonical: url,
      languages: { ...languages, "x-default": languages.en },
    },
    openGraph: {
      type: "article",
      url,
      siteName: "OralCheck",
      title: article.title,
      description,
      images,
      publishedTime: article.date || undefined,
      modifiedTime: article.updated || undefined,
    },
    twitter: {
      card: "summary_large_image",
      title: article.title,
      description,
      images: images.map((i) => (typeof i === "string" || i instanceof URL ? i : i.url)),
    },
  };
}

function formatDate(iso: string, locale: string) {
  const d = new Date(`${iso}T00:00:00Z`);
  if (Number.isNaN(d.getTime())) return "";
  return new Intl.DateTimeFormat(locale, { dateStyle: "long", timeZone: "UTC" }).format(d);
}

function Contents({ headings }: { headings: ArticleHeading[] }) {
  return (
    <ol className="article-contents">
      {headings.map((h, i) => (
        <li key={h.id}>
          <a href={`#${h.id}`}>
            <span aria-hidden className="article-contents-n">{i + 1}</span>
            <span>{h.text}</span>
          </a>
        </li>
      ))}
    </ol>
  );
}

export default async function ArticlePage({ params }: Props) {
  const { slug, locale } = await params;
  const article = getPublishedArticle(slug, locale);
  if (!article) notFound();
  const t = await getTranslations({ locale, namespace: "ArticlePage" });
  const related = getRelatedArticles(slug, locale);
  const url = articleUrl(slug, article.contentLocale);
  const description = article.standfirst || article.excerpt;
  const published = article.date ? formatDate(article.date, locale) : "";
  const updated = article.updated && article.updated !== article.date ? formatDate(article.updated, locale) : "";
  const showContents = article.headings.length >= 2;

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "MedicalWebPage",
        "@id": `${url}#webpage`,
        url,
        name: article.title,
        headline: article.title,
        description,
        inLanguage: article.contentLocale,
        isPartOf: { "@id": `${SITE_URL}/#website` },
        audience: { "@type": "MedicalAudience", audienceType: "Patient" },
        datePublished: article.date,
        dateModified: article.updated || article.date,
        lastReviewed: article.date,
        publisher: { "@type": "Organization", name: "OralCheck", url: SITE_URL },
        ...(article.author ? { author: { "@type": "Person", name: article.author } } : {}),
        ...(article.sources.length
          ? { citation: article.sources.map((s) => ({ "@type": "CreativeWork", name: s.label, url: s.href })) }
          : {}),
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home",  item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
          { "@type": "ListItem", position: 3, name: article.title, item: url },
        ],
      },
    ],
  };

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 pt-6 pb-16 sm:pt-10 sm:pb-24">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }}
      />

      <Link
        href="/learn"
        className="inline-flex min-h-11 items-center text-sm font-medium text-ink-soft hover:text-ink"
      >
        {t("backToLearn")}
      </Link>

      <div className="mt-4 sm:mt-6 lg:grid lg:grid-cols-[minmax(0,40rem)_14rem] lg:justify-between lg:gap-x-12">
        <article lang={article.contentLocale} className="min-w-0 max-w-[40rem]">
          {/* ── Header: type label, title, standfirst, one meta line ── */}
          <header className="article-header">
            <p lang={locale} className="article-type text-xs font-semibold uppercase tracking-[0.14em]">
              {t("typeLabel")}
            </p>
            <h1 className="mt-3 font-serif text-[2.125rem] leading-[1.12] sm:text-5xl sm:leading-[1.08] text-ink text-balance">
              {article.title}
            </h1>
            {article.standfirst && (
              <p className="mt-5 max-w-[35rem] text-lg sm:text-xl leading-relaxed text-ink-soft text-pretty">
                {article.standfirst}
              </p>
            )}
            <p lang={locale} className="article-meta mt-6 max-w-[35rem] pt-4 text-sm text-ink-soft">
              {article.author && <span>{t("byAuthor", { author: article.author })}</span>}
              {published && (
                <span>
                  <time dateTime={article.date}>{t("published", { date: published })}</time>
                </span>
              )}
              {updated && (
                <span>
                  <time dateTime={article.updated}>{t("updated", { date: updated })}</time>
                </span>
              )}
              <span>{t("readingTime", { minutes: article.readingMinutes })}</span>
            </p>
            {article.contentLocale !== locale && (
              <p lang={locale} className="mt-3 text-sm text-ink-soft">{t("onlyInEnglish")}</p>
            )}
          </header>

          {/* ── Key points: front matter only, never generated ── */}
          {article.keyPoints.length > 0 && (
            <section aria-labelledby="article-key-points" className="article-keypoints mt-8">
              <h2 id="article-key-points" lang={locale}>{t("keyPoints")}</h2>
              <ul>
                {article.keyPoints.map((p) => (
                  <li key={p}>{p}</li>
                ))}
              </ul>
            </section>
          )}

          {/* ── Contents, phone and tablet: collapsed, out of the way ── */}
          {showContents && (
            <details className="article-contents-mobile mt-8 max-w-[35rem] lg:hidden" lang={locale}>
              <summary>{t("contents")}</summary>
              <Contents headings={article.headings} />
            </details>
          )}

          <div
            className="prose-article mt-8 sm:mt-10"
            dangerouslySetInnerHTML={{ __html: article.bodyHtml }}
          />

          {/* ── Sources: only links the article itself cites ── */}
          {article.sources.length > 0 && (
            <section aria-labelledby="article-sources" className="article-sources mt-12" lang={locale}>
              <h2 id="article-sources">{t("sources")}</h2>
              <ol>
                {article.sources.map((s) => (
                  <li key={s.n} id={`source-${s.n}`}>
                    <a href={s.href} target="_blank" rel="noopener noreferrer">
                      {s.label}
                    </a>
                    <span className="text-ink-soft">. {s.host}.</span>{" "}
                    <a href={`#cite-${s.n}`} className="article-backref" aria-label={t("backToText")}>
                      ↩
                    </a>
                  </li>
                ))}
              </ol>
            </section>
          )}

          {/* ── Disclaimer: the article's own wording when it has one ── */}
          <p className="article-note mt-12 pt-5 text-[0.8125rem] leading-relaxed text-ink-soft">
            <strong className="font-semibold text-ink" lang={locale}>{t("disclaimerLabel")}</strong>{" "}
            {article.disclaimer || <span lang={locale}>{t("disclaimerBody")}</span>}
          </p>

          {/* ── Closing: screener CTA, same pattern as the home page panel ── */}
          <aside lang={locale} className="mt-10 rounded-3xl bg-brand-soft border border-brand/20 px-6 py-8 sm:px-10 sm:py-10">
            <p className="article-type text-xs font-semibold tracking-widest uppercase mb-2">
              {t("ctaEyebrow")}
            </p>
            <h2 className="font-serif text-2xl sm:text-3xl text-ink mb-3 text-balance">
              {t("ctaHeading")}
            </h2>
            <p className="text-ink-soft leading-relaxed mb-6 max-w-xl">{t("ctaBody")}</p>
            <Link
              href="/screener"
              className="inline-flex min-h-12 items-center bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
            >
              {t("takeScreener")}
            </Link>
          </aside>

          {/* ── Related: other published guides, as a plain list ── */}
          {related.length > 0 && (
            <nav aria-labelledby="article-related" className="article-related mt-14" lang={locale}>
              <h2 id="article-related">{t("relatedHeading")}</h2>
              <ul>
                {related.map((r) => (
                  <li key={r.slug}>
                    <Link href={`/learn/${r.slug}`} className="group block py-4">
                      <span className="block font-serif text-lg leading-snug text-ink group-hover:text-brand transition-colors">
                        {r.title}
                      </span>
                      {r.date && (
                        <time dateTime={r.date} className="mt-1 block text-sm text-ink-soft">
                          {formatDate(r.date, locale)}
                        </time>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
          )}

          <p className="mt-10 text-xs text-ink-soft" lang={locale}>
            {t("publishedBy")}{" "}
            <Link href="/about" className="underline underline-offset-2 hover:text-ink">
              {t("aboutLink")}
            </Link>
          </p>
        </article>

        {/* ── Desktop rail: sticky contents ── */}
        {showContents && (
          <aside className="hidden lg:block" lang={locale}>
            <nav aria-labelledby="article-contents-rail" className="article-rail sticky top-24">
              <h2 id="article-contents-rail">{t("contents")}</h2>
              <Contents headings={article.headings} />
              <Link href="/screener" className="article-rail-cta">
                {t("takeScreener")}
              </Link>
            </nav>
          </aside>
        )}
      </div>
    </div>
  );
}
