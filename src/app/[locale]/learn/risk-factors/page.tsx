import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import LearnReadNext from "@/components/LearnReadNext";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "RiskFactorsMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/learn/risk-factors"),
  };
}

const SITE_URL = "https://oralcheck.org";

type RiskFactor = {
  rank: number; name: string; weight: string; weightColor: string;
  summary: string; detail: string; link: string | null;
};
type Todo = { title: string; desc: string };
type Faq = { q: string; a: string };

export default async function RiskFactorsPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "RiskFactorsPage" });
  const tSub = await getTranslations({ locale, namespace: "LearnSubpage" });
  const riskFactors = t.raw("riskFactors") as RiskFactor[];
  const whatToDo = t.raw("whatToDo") as Todo[];
  const faqs = t.raw("faqs") as Faq[];

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "MedicalWebPage",
        "@id": `${SITE_URL}/learn/risk-factors#webpage`,
        url: `${SITE_URL}/learn/risk-factors`,
        name: t("heading"),
        description: t("intro"),
        about: { "@type": "MedicalCondition", name: "Oral Cancer" },
        audience: { "@type": "MedicalAudience", audienceType: "Patient" },
        datePublished: "2026-06-09",
        lastReviewed: "2026-06-09",
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
          { "@type": "ListItem", position: 3, name: t("heading"), item: `${SITE_URL}/learn/risk-factors` },
        ],
      },
      {
        "@type": "FAQPage",
        "@id": `${SITE_URL}/learn/risk-factors#faq`,
        mainEntity: faqs.map((f) => ({
          "@type": "Question",
          name: f.q,
          acceptedAnswer: { "@type": "Answer", text: f.a },
        })),
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <article className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
        <Link
          href="/learn"
          className="text-sm font-medium text-ink-soft hover:text-ink mb-6 inline-block"
        >
          {tSub("backToLearn")}
        </Link>
        <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
          {t("tag")}
        </span>
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4 leading-tight">
          {t("heading")}
        </h1>
        <p className="text-lg text-ink-soft leading-relaxed mb-10">{t("intro")}</p>

        {/* Key callout */}
        <div className="bg-brand/5 border border-brand/20 rounded-2xl p-6 mb-12">
          <h2 className="font-serif text-xl text-ink mb-2">{t("twoFactorHeading")}</h2>
          <p className="text-ink-soft leading-relaxed text-sm">
            {t("twoFactorP1")} <strong className="text-ink">{t("twoFactorBold1")}</strong>,{" "}
            {t("twoFactorP2")} <strong className="text-ink">{t("twoFactorBold2")}</strong>{" "}
            {t("twoFactorP3")}
          </p>
        </div>

        {/* Risk factor list */}
        <section className="mb-12 space-y-6">
          {riskFactors.map((rf) => (
            <div
              key={rf.name}
              className="bg-warm-dim border border-warm-dim rounded-2xl p-6"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-brand font-semibold shrink-0 w-6">
                    {String(rf.rank).padStart(2, "0")}
                  </span>
                  <h2 className="font-semibold text-ink text-lg">{rf.name}</h2>
                </div>
                <span className={`text-xs font-semibold shrink-0 ${rf.weightColor}`}>
                  {rf.weight}
                </span>
              </div>
              <p className="text-sm text-ink font-medium mb-2 ml-9">{rf.summary}</p>
              <p className="text-sm text-ink-soft leading-relaxed ml-9">{rf.detail}</p>
              {rf.link && (
                <div className="ml-9 mt-3">
                  <Link href={rf.link} className="text-sm text-brand hover:underline">
                    {t("learnMore")}
                  </Link>
                </div>
              )}
            </div>
          ))}
        </section>

        {/* Synergy section */}
        <section className="mb-12">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("interactHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-4">{t("interactP1")}</p>
          <p className="text-ink-soft leading-relaxed mb-4">{t("interactP2")}</p>
          <p className="text-ink-soft leading-relaxed">{t("interactP3")}</p>
        </section>

        {/* What you can do */}
        <section className="mb-12">
          <h2 className="font-serif text-3xl text-ink mb-5">{t("whatToDoHeading")}</h2>
          <div className="space-y-3">
            {whatToDo.map(({ title, desc }) => (
              <div
                key={title}
                className="flex gap-4 bg-warm-dim border border-warm-dim rounded-2xl p-5"
              >
                <span className="text-brand font-bold mt-0.5 shrink-0">✓</span>
                <div>
                  <div className="font-semibold text-ink text-sm">{title}</div>
                  <div className="text-xs text-ink-soft mt-0.5">{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section className="mb-12">
          <h2 className="font-serif text-3xl text-ink mb-6">{t("faqHeading")}</h2>
          <div className="space-y-4">
            {faqs.map((faq) => (
              <details
                key={faq.q}
                className="bg-warm-dim border border-warm-dim rounded-2xl group"
              >
                <summary className="flex items-center justify-between px-6 py-4 cursor-pointer list-none font-semibold text-ink">
                  {faq.q}
                  <span className="ml-4 shrink-0 text-brand text-lg font-light group-open:rotate-45 transition-transform">
                    +
                  </span>
                </summary>
                <p className="px-6 pb-5 text-ink-soft leading-relaxed text-sm">{faq.a}</p>
              </details>
            ))}
          </div>
        </section>

        <div className="p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed mb-8">
          <strong className="text-ink">{t("sourcesLabel")}</strong> {t("sourcesBody")}
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            href="/screener"
            className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
          >
            {t("checkRisk")}
          </Link>
          <Link
            href="/learn/signs"
            className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            {t("warningSigns")}
          </Link>
          <Link
            href="/learn/prevention"
            className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            {t("preventionGuide")}
          </Link>
          <Link
            href="/learn/hpv"
            className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            {t("hpvGuide")}
          </Link>
        </div>
        <LearnReadNext currentHref="/learn/risk-factors" />
      </article>
    </>
  );
}
