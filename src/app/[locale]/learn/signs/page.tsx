import { Link } from "@/i18n/navigation";
import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import LearnReadNext from "@/components/LearnReadNext";
import SignsVisualGuide from "@/components/SignsVisualGuide";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "SignsMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/learn/signs"),
  };
}

const SITE_URL = "https://oralcheck.org";

type Sign = { title: string; detail: string; urgent: boolean };
type Location = { site: string; note: string; risk: string };
type ComparisonRow = { label: string; a: string; b: string };
type TodoItem = { title: string; desc: string };
type Faq = { q: string; a: string };

export default async function SignsPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "SignsPage" });
  const tSub = await getTranslations({ locale, namespace: "LearnSubpage" });
  const signs = t.raw("signs") as Sign[];
  const locations = t.raw("locations") as Location[];
  const comparison = t.raw("comparison") as ComparisonRow[];
  const whatToDo = t.raw("whatToDo") as TodoItem[];
  const faqs = t.raw("faqs") as Faq[];

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "MedicalWebPage",
        "@id": `${SITE_URL}/learn/signs#webpage`,
        url: `${SITE_URL}/learn/signs`,
        name: t("heading"),
        description: t("painlessP1"),
        about: {
          "@type": "MedicalCondition",
          name: "Oral Cancer",
          signOrSymptom: signs.map((s) => ({ "@type": "MedicalSymptom", name: s.title })),
        },
        audience: { "@type": "MedicalAudience", audienceType: "Patient" },
        datePublished: "2025-01-01",
        lastReviewed: "2026-06-09",
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
          { "@type": "ListItem", position: 3, name: t("heading"), item: `${SITE_URL}/learn/signs` },
        ],
      },
      {
        "@type": "FAQPage",
        "@id": `${SITE_URL}/learn/signs#faq`,
        mainEntity: faqs.map((f) => ({
          "@type": "Question",
          name: f.q,
          acceptedAnswer: { "@type": "Answer", text: f.a },
        })),
      },
    ],
  };

  return (
    <article className="max-w-5xl mx-auto px-5 py-10 sm:py-16">
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
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4 leading-tight">
        {t("heading")}
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10 max-w-3xl">
        {t("introStart")}{" "}
        <Link
          href="/learn/oral-cancer"
          className="text-brand underline underline-offset-2 hover:text-brand-dark"
        >
          {t("introLink")}
        </Link>{" "}
        {t("introEnd")}
      </p>

      {/* The 2-week rule — prominent */}
      <div className="bg-accent/10 border border-accent/20 rounded-2xl p-6 mb-12">
        <h2 className="font-serif text-xl text-ink mb-2">{t("twoWeekHeading")}</h2>
        <p className="text-ink-soft leading-relaxed text-sm">
          {t("twoWeekP1Start")} <strong className="text-ink">{t("twoWeekBold")}</strong>{" "}
          {t("twoWeekP1End")}
        </p>
      </div>

      <SignsVisualGuide />

      {/* Signs list */}
      <section className="mb-14">
        <h2 className="font-serif text-3xl text-ink mb-6">{t("signsHeading")}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
          {signs.map((s, i) => (
            <div
              key={s.title}
              className={`rounded-2xl border p-6 ${
                s.urgent
                  ? "bg-accent/5 border-accent/25"
                  : "bg-warm-dim border-warm-dim"
              }`}
            >
              <div className="flex gap-4">
                <span className="font-mono text-sm text-brand font-semibold shrink-0 w-6 mt-0.5">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <h3 className="font-semibold text-ink text-lg leading-snug">
                      {s.title}
                    </h3>
                    {s.urgent && (
                      <span className="text-[10px] font-bold uppercase tracking-wider text-accent bg-accent/10 px-2 py-0.5 rounded-full">
                        {t("highPriority")}
                      </span>
                    )}
                  </div>
                  <p className="text-ink-soft leading-relaxed text-sm">{s.detail}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Where it develops */}
      <section className="mb-14">
        <h2 className="font-serif text-3xl text-ink mb-3">{t("whereHeading")}</h2>
        <p className="text-ink-soft leading-relaxed mb-6 text-sm max-w-prose">{t("whereIntro")}</p>
        <div className="overflow-hidden rounded-2xl border border-warm-dim">
          {locations.map((loc, i) => (
            <div
              key={loc.site}
              className={`flex items-start gap-4 px-5 py-4 ${
                i < locations.length - 1 ? "border-b border-warm-dim" : ""
              }`}
            >
              <div className="flex-1 min-w-0">
                <span className="font-semibold text-ink text-sm">{loc.site}</span>
                <p className="text-xs text-ink-soft mt-0.5">{loc.note}</p>
              </div>
              <span className="text-xs font-semibold text-ink-soft shrink-0 text-right">
                {loc.risk}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* Painlessness callout */}
      <section className="mb-14">
        <h2 className="font-serif text-3xl text-ink mb-4">{t("painlessHeading")}</h2>
        <p className="text-ink-soft leading-relaxed mb-4 max-w-prose">{t("painlessP1")}</p>
        <p className="text-ink-soft leading-relaxed mb-4 max-w-prose">{t("painlessP2")}</p>
        <p className="text-ink-soft leading-relaxed max-w-prose">{t("painlessP3")}</p>
      </section>

      {/* Oral cancer vs canker sore quick comparison */}
      <section className="mb-14">
        <h2 className="font-serif text-3xl text-ink mb-4">{t("comparisonHeading")}</h2>
        <p className="text-ink-soft leading-relaxed mb-6 text-sm max-w-prose">
          {t("comparisonIntroStart")}{" "}
          <Link href="/learn/canker-sore-vs-oral-cancer" className="text-brand hover:underline">
            {t("comparisonIntroLink")}
          </Link>{" "}
          {t("comparisonIntroEnd")}
        </p>
        <div className="overflow-hidden rounded-2xl border border-warm-dim">
          <div className="grid grid-cols-3 bg-warm-dim px-5 py-3">
            <span className="text-xs font-bold uppercase tracking-wider text-ink-soft"></span>
            <span className="text-xs font-bold uppercase tracking-wider text-ink-soft">{t("colCankerSore")}</span>
            <span className="text-xs font-bold uppercase tracking-wider text-accent">{t("colOralCancer")}</span>
          </div>
          {comparison.map((row, i, arr) => (
            <div
              key={row.label}
              className={`grid grid-cols-3 px-5 py-3.5 ${
                i < arr.length - 1 ? "border-b border-warm-dim" : ""
              }`}
            >
              <span className="text-xs font-semibold text-ink-soft">{row.label}</span>
              <span className="text-xs text-ink-soft">{row.a}</span>
              <span className={`text-xs font-medium ${row.b === "Does not heal" || row.b === "No sana" || row.label === "What to do" || row.label === "Qué hacer" ? "text-accent" : "text-ink-soft"}`}>{row.b}</span>
            </div>
          ))}
        </div>
      </section>

      {/* What to do */}
      <section className="mb-12">
        <h2 className="font-serif text-3xl text-ink mb-4">{t("whatToDoHeading")}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {whatToDo.map(({ title, desc }) => (
            <div key={title} className="flex gap-4 bg-warm-dim border border-warm-dim rounded-2xl p-5">
              <span className="text-brand font-bold mt-0.5 shrink-0">→</span>
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
          {t("takeScreener")}
        </Link>
        <Link
          href="/learn/self-exam"
          className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          {t("howToSelfExam")}
        </Link>
        <Link
          href="/learn/canker-sore-vs-oral-cancer"
          className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          {t("cankerVsCancer")}
        </Link>
        <Link
          href="/learn/risk-factors"
          className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          {t("riskFactors")}
        </Link>
      </div>
      <p className="text-xs text-ink-soft mt-6">
        {t("byline")}{" "}
        <Link href="/about" className="underline underline-offset-2 hover:text-ink">
          {t("aboutLink")}
        </Link>
      </p>
      <LearnReadNext currentHref="/learn/signs" />
    </article>
  );
}
