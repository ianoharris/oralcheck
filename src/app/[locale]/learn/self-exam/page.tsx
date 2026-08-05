import { Link } from "@/i18n/navigation";
import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import LearnReadNext from "@/components/LearnReadNext";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "SelfExamMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/learn/self-exam"),
  };
}

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      "@id": `${SITE_URL}/learn/self-exam#webpage`,
      url: `${SITE_URL}/learn/self-exam`,
      name: "How to Do a 2-Minute Oral Cancer Self-Exam",
      description:
        "A step-by-step guide to checking your own mouth for signs of oral cancer. Takes 2 minutes. Do it once a month.",
      about: { "@type": "MedicalCondition", name: "Oral Cancer" },
      audience: { "@type": "MedicalAudience", audienceType: "Patient" },
      reviewedBy: {
        "@type": "Person",
        name: "Ian Harris",
        affiliation: { "@type": "Organization", name: "University of Wisconsin-Madison" },
        url: `${SITE_URL}/about`,
      },
    },
    {
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
        { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
        { "@type": "ListItem", position: 3, name: "How to Do a Self-Exam", item: `${SITE_URL}/learn/self-exam` },
      ],
    },
  ],
};

type Step = { area: string; instruction: string };

export default async function SelfExamPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "SelfExamPage" });
  const tSub = await getTranslations({ locale, namespace: "LearnSubpage" });
  const steps = t.raw("steps") as Step[];

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
          href="/learn/signs"
          className="text-brand underline underline-offset-2 hover:text-brand-dark"
        >
          {t("introLink")}
        </Link>
      </p>

      <ol className="space-y-3">
        {steps.map((s, i) => (
          <li
            key={s.area}
            className="bg-warm-dim rounded-2xl border border-warm-dim p-5 flex gap-4"
          >
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-brand text-white flex items-center justify-center font-semibold font-mono">
              {i + 1}
            </div>
            <div>
              <h2 className="font-semibold text-ink mb-1">{s.area}</h2>
              <p className="text-ink-soft leading-relaxed">{s.instruction}</p>
            </div>
          </li>
        ))}
      </ol>

      <div className="mt-10 p-6 rounded-2xl bg-low/10 border border-low/20">
        <h2 className="font-serif text-2xl text-ink mb-2">
          {t("normalHeading")}
        </h2>
        <p className="text-ink leading-relaxed mb-2">
          {t("normalP1Rest")}{" "}
          <Link href="/learn/canker-sore-vs-oral-cancer" className="text-brand hover:underline font-medium">
            {t("normalP1Link")}
          </Link>{" "}
          {t("normalP1End")}
        </p>
        <p className="text-ink leading-relaxed">{t("normalP2")}</p>
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
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
          {t("warningSignsGuide")}
        </Link>
        <Link
          href="/learn/oral-cancer"
          className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          {t("whatIsOralCancer")}
        </Link>
        <Link
          href="/find-care"
          className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          {t("findDentist")}
        </Link>
      </div>
      <p className="text-xs text-ink-soft mt-8">
        {t("byline")}{" "}
        <Link href="/about" className="underline underline-offset-2 hover:text-ink">
          {t("aboutLink")}
        </Link>
      </p>
      <LearnReadNext currentHref="/learn/self-exam" />
    </article>
  );
}
