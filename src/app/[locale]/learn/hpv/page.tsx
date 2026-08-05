import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import LearnReadNext from "@/components/LearnReadNext";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "HpvMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/learn/hpv"),
  };
}

const SITE_URL = "https://oralcheck.org";

type Symptom = { symptom: string; note: string };
type Faq = { q: string; a: string };

export default async function HpvPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "HpvPage" });
  const tSub = await getTranslations({ locale, namespace: "LearnSubpage" });
  const symptoms = t.raw("symptoms") as Symptom[];
  const faqs = t.raw("faqs") as Faq[];

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "MedicalWebPage",
        "@id": `${SITE_URL}/learn/hpv#webpage`,
        url: `${SITE_URL}/learn/hpv`,
        name: t("heading"),
        description: t("statBody"),
        about: {
          "@type": "MedicalCondition",
          name: "HPV-Related Oropharyngeal Cancer",
          associatedAnatomy: { "@type": "AnatomicalStructure", name: "Oropharynx" },
          cause: { "@type": "MedicalCause", name: "Human Papillomavirus (HPV-16)" },
        },
        datePublished: "2026-04-23",
        lastReviewed: "2026-04-23",
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
          { "@type": "ListItem", position: 3, name: t("heading"), item: `${SITE_URL}/learn/hpv` },
        ],
      },
      {
        "@type": "FAQPage",
        "@id": `${SITE_URL}/learn/hpv#faq`,
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
        <p className="text-lg text-ink-soft leading-relaxed mb-10">
          {t("introStart")}{" "}
          <Link
            href="/learn/oral-cancer"
            className="text-brand underline underline-offset-2 hover:text-brand-dark"
          >
            {t("introLink")}
          </Link>{" "}
          {t("introEnd")}
        </p>

        {/* Key stat callout */}
        <div className="bg-brand/5 border border-brand/20 rounded-2xl p-6 mb-10 flex gap-5 items-start">
          <div className="text-4xl" aria-hidden>🦠</div>
          <div>
            <div className="font-serif text-2xl text-ink mb-1">{t("statHeading")}</div>
            <p className="text-ink-soft leading-relaxed text-sm">{t("statBody")}</p>
          </div>
        </div>

        {/* What is HPV-related oral cancer */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("whatIsHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-4">
            {t("whatIsP1Start")} <strong className="text-ink">{t("whatIsP1Bold")}</strong>{" "}
            {t("whatIsP1End")}
          </p>
          <p className="text-ink-soft leading-relaxed mb-4">
            {t("whatIsP2Start")} <strong className="text-ink">{t("whatIsP2Bold")}</strong>
            {t("whatIsP2End")}
          </p>
          <p className="text-ink-soft leading-relaxed">{t("whatIsP3")}</p>
        </section>

        {/* Symptoms */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("symptomsHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-5">
            {t("symptomsIntroStart")} <strong className="text-ink">{t("symptomsIntroBold")}</strong>,{" "}
            {t("symptomsIntroEnd")}
          </p>
          <ul className="space-y-3">
            {symptoms.map(({ symptom, note }) => (
              <li
                key={symptom}
                className="bg-warm-dim border border-warm-dim rounded-xl p-4 flex gap-3 items-start"
              >
                <span className="text-accent font-bold mt-0.5 flex-shrink-0">→</span>
                <div>
                  <div className="font-semibold text-ink text-sm">{symptom}</div>
                  <div className="text-xs text-ink-soft mt-0.5">{note}</div>
                </div>
              </li>
            ))}
          </ul>
        </section>

        {/* Who is at risk */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("whoHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-4">
            {t("whoP1Start")} <strong className="text-ink">{t("whoP1Bold")}</strong>{" "}
            {t("whoP1End")}
          </p>
          <p className="text-ink-soft leading-relaxed mb-4">{t("whoP2")}</p>
          <p className="text-ink-soft leading-relaxed">{t("whoP3")}</p>
        </section>

        {/* Vaccine */}
        <section className="bg-brand/5 border border-brand/20 rounded-2xl p-7 mb-10">
          <h2 className="font-serif text-3xl text-ink mb-3">{t("vaccineHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-4">
            <strong className="text-ink">{t("vaccineP1Bold")}</strong> {t("vaccineP1Rest")}{" "}
            <strong className="text-ink">{t("vaccineP1Ages")}</strong>.
          </p>
          <p className="text-ink-soft leading-relaxed mb-4">{t("vaccineP2")}</p>
          <p className="text-ink-soft leading-relaxed">{t("vaccineP3")}</p>
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
                  <span className="ml-4 flex-shrink-0 text-brand text-lg font-light group-open:rotate-45 transition-transform">
                    +
                  </span>
                </summary>
                <p className="px-6 pb-5 text-ink-soft leading-relaxed text-sm">
                  {faq.a}
                </p>
              </details>
            ))}
          </div>
        </section>

        <div className="mt-4 p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed mb-8">
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
            href="/learn/prevention"
            className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            {t("preventionGuide")}
          </Link>
        </div>
        <LearnReadNext currentHref="/learn/hpv" />
      </article>
    </>
  );
}
