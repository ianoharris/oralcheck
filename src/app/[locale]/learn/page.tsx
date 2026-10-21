import { Link } from "@/i18n/navigation";
import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import FadeUp from "@/components/FadeUp";
import AnimatedLearnCards from "@/components/AnimatedLearnCards";
import { getAllPublishedArticles } from "@/lib/articles";
import { localizedAlternates } from "@/lib/pageMetadata";
import LoadMoreList from "@/components/LoadMoreList";

// Articles shown before "Load more", and how many each click adds.
const ARTICLES_PER_PAGE = 5;

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "LearnMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/learn"),
  };
}

export default async function LearnPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "LearnPage" });
  // Newest first by the article's publish date (filename date as tiebreak).
  const articles = getAllPublishedArticles(locale).sort(
    (a, b) => b.date.localeCompare(a.date) || b.filename.localeCompare(a.filename),
  );

  return (
    <div className="max-w-5xl mx-auto px-5 py-10 sm:py-16">
      <FadeUp>
        <div className="max-w-2xl mb-12">
          <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-3">{t("heading")}</h1>
          <p className="text-ink-soft text-lg leading-relaxed">{t("subheading")}</p>
        </div>
      </FadeUp>

      <AnimatedLearnCards />

      {articles.length > 0 && (
        <FadeUp>
          <div className="mt-16">
            <h2 className="font-serif text-2xl text-ink mb-6">{t("moreArticles")}</h2>
            <LoadMoreList
              className="flex flex-col gap-3"
              step={ARTICLES_PER_PAGE}
              buttonLabel={t("loadMore")}
              items={articles.map((a) => (
                <Link
                  key={a.slug}
                  href={`/learn/${a.slug}`}
                  className="flex items-start gap-4 rounded-2xl border border-warm-dim bg-warm-dim p-5 hover:border-brand/40 hover:shadow-sm transition-[color,background-color,border-color,box-shadow] group"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-ink group-hover:text-brand transition-colors leading-snug">
                      {a.title}
                    </p>
                    {a.excerpt && (
                      <p className="text-sm text-ink-soft mt-1 line-clamp-2">{a.excerpt}</p>
                    )}
                  </div>
                  <span className="text-brand shrink-0 mt-0.5 text-sm font-semibold" aria-hidden>→</span>
                </Link>
              ))}
            />
          </div>
        </FadeUp>
      )}
    </div>
  );
}
