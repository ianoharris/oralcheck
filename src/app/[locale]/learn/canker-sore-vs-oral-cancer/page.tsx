import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import LearnReadNext from "@/components/LearnReadNext";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "CankerMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/learn/canker-sore-vs-oral-cancer"),
  };
}

const SITE_URL = "https://oralcheck.org";

type Row = { feature: string; canker: string; cancer: string };
type WhenItem = { title: string; desc: string };
type Faq = { q: string; a: string };

export default async function CankerSorePage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "CankerPage" });
  const tSub = await getTranslations({ locale, namespace: "LearnSubpage" });
  const cankerTraits = t.raw("cankerTraits") as string[];
  const cancerTraits = t.raw("cancerTraits") as string[];
  const comparison = t.raw("comparison") as Row[];
  const whenToSee = t.raw("whenToSee") as WhenItem[];
  const faqs = t.raw("faqs") as Faq[];

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "MedicalWebPage",
        "@id": `${SITE_URL}/learn/canker-sore-vs-oral-cancer#webpage`,
        url: `${SITE_URL}/learn/canker-sore-vs-oral-cancer`,
        name: t("heading"),
        description: t("intro"),
        about: { "@type": "MedicalCondition", name: "Oral Cancer" },
        datePublished: "2026-04-23",
        lastReviewed: "2026-04-23",
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
          { "@type": "ListItem", position: 3, name: t("heading"), item: `${SITE_URL}/learn/canker-sore-vs-oral-cancer` },
        ],
      },
      {
        "@type": "FAQPage",
        "@id": `${SITE_URL}/learn/canker-sore-vs-oral-cancer#faq`,
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

      <article className="max-w-5xl mx-auto px-5 py-10 sm:py-16">
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
        <p className="text-lg text-ink-soft leading-relaxed mb-10 max-w-3xl">{t("intro")}</p>

        {/* Quick answer callout */}
        <div className="bg-brand/5 border border-brand/20 rounded-2xl p-6 mb-10">
          <h2 className="font-serif text-xl text-ink mb-2">{t("quickAnswerHeading")}</h2>
          <p className="text-ink-soft leading-relaxed text-sm">
            {t("quickAnswerP1Start")} <strong className="text-ink">{t("quickAnswerP1Bold1")}</strong>{" "}
            {t("quickAnswerP1Mid")} <strong className="text-ink">{t("quickAnswerP1Bold2")}</strong>,{" "}
            {t("quickAnswerP1End")}
          </p>
        </div>

        {/* What is a canker sore */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("cankerHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-4 max-w-prose">{t("cankerP1")}</p>
          <ul className="space-y-2 mb-4">
            {cankerTraits.map((item) => (
              <li key={item} className="flex gap-3 text-sm text-ink-soft">
                <span className="text-low font-bold mt-0.5 flex-shrink-0">✓</span>
                {item}
              </li>
            ))}
          </ul>
          <p className="text-ink-soft leading-relaxed text-sm">{t("cankerP2")}</p>
        </section>

        {/* What does oral cancer look like */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("cancerLookHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-4 max-w-prose">{t("cancerLookP1")}</p>
          <ul className="space-y-2 mb-4">
            {cancerTraits.map((item) => (
              <li key={item} className="flex gap-3 text-sm text-ink-soft">
                <span className="text-accent font-bold mt-0.5 flex-shrink-0">→</span>
                {item}
              </li>
            ))}
          </ul>
          <p className="text-ink-soft leading-relaxed text-sm">{t("cancerLookP2")}</p>
        </section>

        {/* Comparison table */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-5">{t("sideBySideHeading")}</h2>
          <div className="rounded-2xl overflow-hidden border border-warm-dim">
            <div className="grid grid-cols-3 bg-warm-dim/60 text-xs font-semibold uppercase tracking-wider text-ink-soft">
              <div className="px-5 py-3">{t("colFeature")}</div>
              <div className="px-5 py-3 border-l border-warm-dim text-low">{t("colCanker")}</div>
              <div className="px-5 py-3 border-l border-warm-dim text-accent">{t("colCancer")}</div>
            </div>
            {comparison.map((row, i) => (
              <div
                key={row.feature}
                className={`grid grid-cols-3 text-sm ${i % 2 === 0 ? "bg-warm-dim" : "bg-warm/40"}`}
              >
                <div className="px-5 py-4 font-semibold text-ink">{row.feature}</div>
                <div className="px-5 py-4 text-ink-soft border-l border-warm-dim">{row.canker}</div>
                <div className="px-5 py-4 text-ink-soft border-l border-warm-dim">{row.cancer}</div>
              </div>
            ))}
          </div>
        </section>

        {/* 2-week rule */}
        <div className="bg-accent/10 border border-accent/20 rounded-2xl p-6 mb-10">
          <h2 className="font-serif text-2xl text-ink mb-2">{t("twoWeekHeading")}</h2>
          <p className="text-ink leading-relaxed">
            {t("twoWeekP1Start")} <strong>{t("twoWeekBold")}</strong> {t("twoWeekP1End")}
          </p>
        </div>

        {/* When to see a doctor */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("whenToSeeHeading")}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {whenToSee.map(({ title, desc }) => (
              <div key={title} className="bg-warm-dim border border-warm-dim rounded-2xl p-5 flex gap-4 items-start">
                <span className="text-accent font-bold mt-0.5 flex-shrink-0">→</span>
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
          <div className="space-y-4 max-w-3xl">
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
            className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            {t("seeAllSigns")}
          </Link>
          <Link
            href="/find-care"
            className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            {t("findDentist")}
          </Link>
        </div>
        <LearnReadNext currentHref="/learn/canker-sore-vs-oral-cancer" />
      </article>
    </>
  );
}
