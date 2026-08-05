import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import LearnReadNext from "@/components/LearnReadNext";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "FactsMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/learn/facts"),
  };
}

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      url: `${SITE_URL}/learn/facts`,
      name: "Oral Cancer Facts & Statistics",
      description:
        "Key oral cancer statistics: 54,000+ US cases per year, 84% survival when caught early, and why HPV has overtaken tobacco as the top cause.",
      about: { "@type": "MedicalCondition", name: "Oral Cancer" },
      datePublished: "2025-01-01",
      lastReviewed: "2026-04-23",
    },
    {
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
        { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
        { "@type": "ListItem", position: 3, name: "Oral Cancer Facts & Stats", item: `${SITE_URL}/learn/facts` },
      ],
    },
  ],
};

type Stat = { value: string; label: string; detail: string };
type Fact = { title: string; detail: string };

export default async function FactsPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "FactsPage" });
  const tSub = await getTranslations({ locale, namespace: "LearnSubpage" });
  const stats = t.raw("stats") as Stat[];
  const facts = t.raw("facts") as Fact[];

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
        {tSub("backToLearn")}
      </Link>
      <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
        {t("tag")}
      </span>
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        {t("heading")}
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10">
        {t("introRest")}{" "}
        <Link
          href="/learn/oral-cancer"
          className="text-brand underline underline-offset-2 hover:text-brand-dark"
        >
          {t("introLink")}
        </Link>
      </p>

      <div className="grid grid-cols-2 gap-4 mb-12">
        {stats.map((s) => (
          <div
            key={s.label}
            className="bg-warm-dim rounded-2xl border border-warm-dim p-5"
          >
            <div className="font-mono text-3xl sm:text-4xl text-brand font-semibold">
              {s.value}
            </div>
            <div className="font-semibold text-ink text-sm mt-2">
              {s.label}
            </div>
            <div className="text-xs text-ink-soft mt-1 leading-relaxed">
              {s.detail}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-5">
        {facts.map((f, i) => (
          <div key={f.title} className="bg-warm-dim rounded-2xl border border-warm-dim p-6">
            <div className="font-mono text-xs text-brand mb-2">
              {t("factLabel")} {String(i + 1).padStart(2, "0")}
            </div>
            <h2 className="font-serif text-2xl text-ink mb-2 leading-tight">
              {f.title}
            </h2>
            <p className="text-ink-soft leading-relaxed">{f.detail}</p>
          </div>
        ))}
      </div>

      <div className="mt-12 p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed">
        <strong className="text-ink">{t("sourcesLabel")}</strong> {t("sourcesBody")}
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <Link
          href="/screener"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          {t("takeScreener")}
        </Link>
        <Link
          href="/learn/oral-cancer"
          className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          {t("whatIsOralCancer")}
        </Link>
        <Link
          href="/learn/self-exam"
          className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          {t("learnSelfExam")}
        </Link>
      </div>
      <LearnReadNext currentHref="/learn/facts" />
    </article>
  );
}
