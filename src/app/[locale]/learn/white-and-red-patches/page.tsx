import type { Metadata } from "next";
import Icon from "@/components/Icon";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import LearnReadNext from "@/components/LearnReadNext";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "PatchesMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/learn/white-and-red-patches"),
  };
}

const SITE_URL = "https://oralcheck.org";
const PATH = "/learn/white-and-red-patches";

type Item = { title: string; desc: string };
type Faq = { q: string; a: string };

export default async function WhiteAndRedPatchesPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "PatchesPage" });
  const tSub = await getTranslations({ locale, namespace: "LearnSubpage" });
  const leukoTraits = t.raw("leukoTraits") as string[];
  const notItems = t.raw("notItems") as Item[];
  const whenItems = t.raw("whenItems") as Item[];
  const faqs = t.raw("faqs") as Faq[];

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "MedicalWebPage",
        "@id": `${SITE_URL}${PATH}#webpage`,
        url: `${SITE_URL}${PATH}`,
        name: t("heading"),
        description: t("intro"),
        about: { "@type": "MedicalCondition", name: "Leukoplakia" },
        datePublished: "2026-09-14",
        lastReviewed: "2026-09-14",
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
          { "@type": "ListItem", position: 3, name: t("heading"), item: `${SITE_URL}${PATH}` },
        ],
      },
      {
        "@type": "FAQPage",
        "@id": `${SITE_URL}${PATH}#faq`,
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
          className="inline-flex min-h-11 items-center text-sm font-medium text-ink-soft hover:text-ink mb-4"
        >
          {tSub("backToLearn")}
        </Link>
        <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
          {t("tag")}
        </span>
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4 leading-tight text-balance">
          {t("heading")}
        </h1>
        <p className="text-lg text-ink-soft leading-relaxed mb-10 max-w-3xl">{t("intro")}</p>

        {/* The threshold, stated before anything else on the page. */}
        <div className="bg-brand/5 border border-brand/20 rounded-2xl p-6 mb-10">
          <h2 className="font-serif text-xl text-ink mb-2">{t("ruleHeading")}</h2>
          <p className="text-ink-soft leading-relaxed text-sm">
            {t("ruleP1Start")}
            <strong className="text-ink">{t("ruleBold1")}</strong>
            {t("ruleP1Mid")}
            <strong className="text-ink">{t("ruleBold2")}</strong>
            {t("ruleP1End")}
          </p>
        </div>

        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("leukoHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-4 max-w-prose">{t("leukoP1")}</p>
          <ul className="space-y-2 mb-4">
            {leukoTraits.map((item) => (
              <li key={item} className="flex gap-3 text-sm text-ink-soft">
                <span className="text-brand mt-0.5 flex-shrink-0" aria-hidden="true">
                  <Icon name="check" size={16} weight="bold" />
                </span>
                <span className="min-w-0">{item}</span>
              </li>
            ))}
          </ul>
          <p className="text-ink-soft leading-relaxed text-sm max-w-prose">{t("leukoP2")}</p>
        </section>

        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("erythroHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-4 max-w-prose">{t("erythroP1")}</p>
          <div className="rounded-2xl border border-accent/30 bg-accent/5 px-5 py-4 max-w-prose">
            <p className="text-sm text-ink leading-relaxed">{t("erythroP2")}</p>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("notHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-5 max-w-prose">{t("notP1")}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {notItems.map((item) => (
              <div
                key={item.title}
                className="rounded-2xl border border-warm-dim bg-warm-dim p-5 min-w-0"
              >
                <div className="font-semibold text-ink mb-1 break-words">{item.title}</div>
                <p className="text-sm text-ink-soft leading-relaxed break-words">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("biopsyHeading")}</h2>
          <p className="text-ink-soft leading-relaxed mb-4 max-w-prose">{t("biopsyP1")}</p>
          <p className="text-ink-soft leading-relaxed max-w-prose">{t("biopsyP2")}</p>
        </section>

        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("whenHeading")}</h2>
          <div className="space-y-3">
            {whenItems.map((item, i) => (
              <div
                key={item.title}
                className="flex gap-4 items-start rounded-2xl border border-warm-dim bg-warm-dim p-5"
              >
                <div
                  className="flex-none w-7 h-7 rounded-full bg-brand/10 text-brand text-xs font-bold flex items-center justify-center mt-0.5 tabular-nums"
                  aria-hidden="true"
                >
                  {i + 1}
                </div>
                <div className="min-w-0">
                  <div className="font-semibold text-ink mb-1 break-words">{item.title}</div>
                  <p className="text-sm text-ink-soft leading-relaxed break-words">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">{t("faqHeading")}</h2>
          <div className="space-y-4">
            {faqs.map((f) => (
              <div key={f.q} className="border-b border-warm-dim pb-4 last:border-0">
                <h3 className="font-semibold text-ink mb-1.5 text-balance">{f.q}</h3>
                <p className="text-sm text-ink-soft leading-relaxed max-w-prose">{f.a}</p>
              </div>
            ))}
          </div>
        </section>

        <div className="flex flex-col sm:flex-row gap-3 mb-10">
          <Link
            href="/screener"
            className="inline-flex min-h-12 items-center justify-center rounded-2xl bg-brand px-6 py-3 font-semibold text-white touch-manipulation transition-colors hover:bg-brand-dark"
          >
            {t("checkRisk")}
          </Link>
          <Link
            href="/learn/signs"
            className="inline-flex min-h-12 items-center justify-center rounded-2xl border border-warm-dim bg-warm-dim px-6 py-3 font-semibold text-ink touch-manipulation transition-colors hover:border-brand/40"
          >
            {t("seeAllSigns")}
          </Link>
          <Link
            href="/find-care"
            className="inline-flex min-h-12 items-center justify-center rounded-2xl border border-warm-dim bg-warm-dim px-6 py-3 font-semibold text-ink touch-manipulation transition-colors hover:border-brand/40"
          >
            {t("findDentist")}
          </Link>
        </div>

        <p className="text-xs text-ink-soft leading-relaxed max-w-prose">
          <strong className="text-ink">{t("sourcesLabel")}:</strong> {t("sourcesBody")}
        </p>

        <LearnReadNext currentHref={PATH} />
      </article>
    </>
  );
}
