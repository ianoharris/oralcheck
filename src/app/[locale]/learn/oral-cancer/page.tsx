import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import LearnReadNext from "@/components/LearnReadNext";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "OralCancerMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/learn/oral-cancer"),
  };
}

const SITE_URL = "https://oralcheck.org";

type TypeItem = { name: string; pct: string; description: string };
type Stat = { value: string; label: string; sub: string };
type Cause = { factor: string; detail: string; link?: string };
type Faq = { q: string; a: string };

export default async function OralCancerPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "OralCancerPage" });
  const tSub = await getTranslations({ locale, namespace: "LearnSubpage" });
  const types = t.raw("types") as TypeItem[];
  const stats = t.raw("stats") as Stat[];
  const causes = t.raw("causes") as Cause[];
  const signs = t.raw("signs") as string[];
  const faqs = t.raw("faqs") as Faq[];

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "MedicalWebPage",
        "@id": `${SITE_URL}/learn/oral-cancer#webpage`,
        url: `${SITE_URL}/learn/oral-cancer`,
        name: t("heading"),
        description: t("intro"),
        about: {
          "@type": "MedicalCondition",
          name: "Oral Cancer",
          associatedAnatomy: { "@type": "AnatomicalStructure", name: "Oral Cavity and Oropharynx" },
        },
        audience: { "@type": "MedicalAudience", audienceType: "Patient" },
        datePublished: "2026-04-23",
        lastReviewed: "2026-04-23",
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
          { "@type": "ListItem", position: 3, name: t("heading"), item: `${SITE_URL}/learn/oral-cancer` },
        ],
      },
      {
        "@type": "FAQPage",
        "@id": `${SITE_URL}/learn/oral-cancer#faq`,
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

        {/* Definition */}
        <div className="bg-warm-dim border border-warm-dim rounded-2xl p-6 sm:p-8 mb-6">
          <h2 className="font-serif text-2xl text-ink mb-3">{t("definitionHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-3">
            <strong className="text-ink">{t("definitionBold1")}</strong> {t("definitionP1Start")}{" "}
            <strong className="text-ink">{t("definitionBold2")}</strong> {t("definitionMid")}{" "}
            <strong className="text-ink">{t("definitionBold3")}</strong> {t("definitionEnd")}
          </p>
          <p className="text-ink-soft leading-relaxed">
            {t("definitionP2Start")} <strong className="text-ink">{t("definitionBold4")}</strong>,{" "}
            {t("definitionP2End")}
          </p>
        </div>

        {/* Types */}
        <section className="mb-6">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("typesHeading")}</h2>
          <div className="space-y-4">
            {types.map((ty) => (
              <div
                key={ty.name}
                className="bg-warm-dim border border-warm-dim rounded-2xl p-6 sm:p-8"
              >
                <div className="flex flex-wrap items-center gap-3 mb-2">
                  <h3 className="font-semibold text-ink text-lg">{ty.name}</h3>
                  <span className="text-xs font-semibold text-brand bg-brand-soft px-2.5 py-0.5 rounded-full">
                    {ty.pct}
                  </span>
                </div>
                <p className="text-ink-soft leading-relaxed text-sm">{ty.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* By the numbers */}
        <section className="mb-6">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("byNumbersHeading")}</h2>
          <div className="grid grid-cols-2 gap-4">
            {stats.map((s) => (
              <div
                key={s.label}
                className="bg-warm-dim border border-warm-dim rounded-2xl p-5"
              >
                <div className="font-mono text-3xl sm:text-4xl text-brand font-semibold">
                  {s.value}
                </div>
                <div className="font-semibold text-ink text-sm mt-2">{s.label}</div>
                <div className="text-xs text-ink-soft mt-1 leading-relaxed">{s.sub}</div>
              </div>
            ))}
          </div>
        </section>

        {/* What causes it */}
        <section className="mb-6">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("causesHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-5">{t("causesIntro")}</p>
          <div className="space-y-3">
            {causes.map((c, i) => (
              <div
                key={c.factor}
                className="bg-warm-dim border border-warm-dim rounded-xl p-5 flex gap-4"
              >
                <div className="flex-shrink-0 font-mono text-xs text-brand font-semibold w-6 mt-0.5">
                  {String(i + 1).padStart(2, "0")}
                </div>
                <div>
                  <div className="font-semibold text-ink mb-1">
                    {c.link ? (
                      <Link
                        href={c.link}
                        className="text-brand underline underline-offset-2 hover:text-brand-dark"
                      >
                        {c.factor}
                      </Link>
                    ) : (
                      c.factor
                    )}
                  </div>
                  <p className="text-sm text-ink-soft leading-relaxed">{c.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* What does it look like */}
        <section className="mb-6">
          <div className="bg-warm-dim border border-warm-dim rounded-2xl p-6 sm:p-8">
            <h2 className="font-serif text-2xl text-ink mb-3">{t("lookLikeHeading")}</h2>
            <p className="text-ink-soft leading-relaxed mb-4">{t("lookLikeIntro")}</p>
            <ul className="space-y-2 mb-4">
              {signs.map((sign) => (
                <li key={sign} className="flex gap-3 items-start text-sm text-ink-soft">
                  <span className="text-accent font-bold flex-shrink-0 mt-0.5">→</span>
                  {sign}
                </li>
              ))}
            </ul>
            <p className="text-sm text-ink-soft">
              {t("seeFullStart")}{" "}
              <Link
                href="/learn/signs"
                className="text-brand underline underline-offset-2 hover:text-brand-dark"
              >
                {t("seeFullLink")}
              </Link>{" "}
              {t("seeFullEnd")}
            </p>
          </div>
        </section>

        {/* 2-week rule callout */}
        <div className="bg-accent/10 border border-accent/20 rounded-2xl p-6 mb-6">
          <h2 className="font-serif text-2xl text-ink mb-2">{t("twoWeekHeading")}</h2>
          <p className="text-ink leading-relaxed">
            {t("twoWeekP1Start")} <strong>{t("twoWeekBold")}</strong> {t("twoWeekP1End")}
          </p>
        </div>

        {/* FAQ */}
        <section className="mb-6">
          <h2 className="font-serif text-3xl text-ink mb-6">{t("faqHeading")}</h2>
          <div className="space-y-4">
            {faqs.map((faq) => (
              <details
                key={faq.q}
                className="bg-warm-dim border border-warm-dim rounded-2xl group"
              >
                <summary className="flex items-center justify-between px-6 py-4 cursor-pointer list-none font-semibold text-ink">
                  {faq.q}
                  <span className="ml-4 flex-shrink-0 text-brand text-lg font-light group-open:rotate-45 transition-transform">
                    +
                  </span>
                </summary>
                <p className="px-6 pb-5 text-ink-soft leading-relaxed text-sm">{faq.a}</p>
              </details>
            ))}
          </div>
        </section>

        <div className="mt-4 p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed mb-4">
          <strong className="text-ink">{t("sourcesLabel")}</strong> {t("sourcesBody")}
        </div>

        <p className="text-xs text-ink-soft mb-8">
          {t("byline")}{" "}
          <Link href="/about" className="underline underline-offset-2 hover:text-ink">
            {t("aboutLink")}
          </Link>
        </p>

        {/* CTA row */}
        <div className="flex flex-wrap gap-3">
          <Link
            href="/screener"
            className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
          >
            {t("takeScreener")}
          </Link>
          <Link
            href="/learn/signs"
            className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            {t("learnSigns")}
          </Link>
          <Link
            href="/learn/self-exam"
            className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            {t("howToSelfExam")}
          </Link>
        </div>
        <LearnReadNext currentHref="/learn/oral-cancer" />
      </article>
    </>
  );
}
