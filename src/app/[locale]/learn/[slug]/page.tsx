import { Link } from "@/i18n/navigation";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { getAllPublishedArticles, getPublishedArticle } from "@/lib/articles";

export async function generateStaticParams() {
  return getAllPublishedArticles().map((a) => ({ slug: a.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string; locale: string }>;
}): Promise<Metadata> {
  const { slug, locale } = await params;
  const article = getPublishedArticle(slug, locale);
  if (!article) return {};
  return {
    title: article.title,
    description: article.excerpt,
    alternates: { canonical: `https://oralcheck.org/learn/${slug}` },
  };
}

const SITE_URL = "https://oralcheck.org";

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ slug: string; locale: string }>;
}) {
  const { slug, locale } = await params;
  const article = getPublishedArticle(slug, locale);
  if (!article) notFound();
  const t = await getTranslations({ locale, namespace: "ArticlePage" });

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "MedicalWebPage",
        "@id": `${SITE_URL}/learn/${slug}#webpage`,
        url: `${SITE_URL}/learn/${slug}`,
        name: article.title,
        description: article.excerpt,
        audience: { "@type": "MedicalAudience", audienceType: "Patient" },
        datePublished: article.date,
        lastReviewed: article.date,
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home",  item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
          { "@type": "ListItem", position: 3, name: article.title, item: `${SITE_URL}/learn/${slug}` },
        ],
      },
    ],
  };

  return (
    <article className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <Link
        href="/learn"
        className="text-sm font-medium text-ink-soft hover:text-ink mb-6 inline-block"
      >
        {t("backToLearn")}
      </Link>

      <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
        {locale === "en" && article.keyword ? article.keyword : t("defaultTag")}
      </span>

      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-6 leading-tight">
        {article.title}
      </h1>

      <div
        className="prose-article"
        dangerouslySetInnerHTML={{ __html: article.html }}
      />

      <div className="mt-12 pt-8 border-t border-warm-dim">
        <Link
          href="/screener"
          className="inline-block bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          {t("takeScreener")}
        </Link>
      </div>

      <p className="text-xs text-ink-soft mt-6">
        {t("byline")}{" "}
        <Link href="/about" className="underline underline-offset-2 hover:text-ink">
          {t("aboutLink")}
        </Link>
      </p>

      <div className="mt-6 p-5 rounded-2xl bg-warm-dim text-xs text-ink-soft leading-relaxed">
        <strong className="text-ink">{t("disclaimerLabel")}</strong> {t("disclaimerBody")}
      </div>
    </article>
  );
}
