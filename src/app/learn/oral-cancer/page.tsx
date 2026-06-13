import type { Metadata } from "next";
import Link from "next/link";
import LearnReadNext from "@/components/LearnReadNext";

export const metadata: Metadata = {
  title: "What Is Oral Cancer? Definition, Types & Key Facts",
  description:
    "Oral cancer is cancer that forms in the mouth or throat. Learn the definition, types, key statistics, causes, and warning signs — and when to see a doctor.",
  alternates: { canonical: "https://oralcheck.org/learn/oral-cancer" },
};

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      "@id": `${SITE_URL}/learn/oral-cancer#webpage`,
      url: `${SITE_URL}/learn/oral-cancer`,
      name: "What Is Oral Cancer? Definition, Types & Key Facts",
      description:
        "Oral cancer is cancer that forms in the mouth or throat. Learn the definition, types, key statistics, causes, and warning signs.",
      about: {
        "@type": "MedicalCondition",
        name: "Oral Cancer",
        associatedAnatomy: {
          "@type": "AnatomicalStructure",
          name: "Oral Cavity and Oropharynx",
        },
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
        { "@type": "ListItem", position: 3, name: "What Is Oral Cancer?", item: `${SITE_URL}/learn/oral-cancer` },
      ],
    },
    {
      "@type": "FAQPage",
      "@id": `${SITE_URL}/learn/oral-cancer#faq`,
      mainEntity: [
        {
          "@type": "Question",
          name: "What is oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Oral cancer is cancer that develops in any part of the mouth (oral cavity) or the back of the throat (oropharynx). This includes the lips, tongue, gums, floor of the mouth, hard and soft palate, cheeks, and throat. Most oral cancers are squamous cell carcinomas, meaning they begin in the flat cells that line these surfaces.",
          },
        },
        {
          "@type": "Question",
          name: "What are the types of oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The main types of oral cancer are: squamous cell carcinoma (the most common, accounting for about 90% of cases), oropharyngeal cancer (affecting the tonsils, base of tongue, and back of the throat — often HPV-related), salivary gland cancer (a rarer type affecting the glands that produce saliva), and oral lymphoma (cancer of lymph tissue in the mouth or throat).",
          },
        },
        {
          "@type": "Question",
          name: "Is oral cancer the same as throat cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "They overlap but are not identical. 'Oral cancer' typically refers to cancers of the lips, tongue, gums, cheeks, and floor and roof of the mouth. 'Throat cancer' or oropharyngeal cancer affects the tonsils, base of the tongue, and back of the throat. Because the oropharynx connects to the oral cavity, these terms are often used together as 'oral and oropharyngeal cancer.'",
          },
        },
        {
          "@type": "Question",
          name: "How common is oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "In the United States, more than 54,000 people are diagnosed with oral and oropharyngeal cancer each year. It is about twice as common in men as in women, and the median age at diagnosis is 62. Globally, oral cancer is among the ten most common cancers.",
          },
        },
        {
          "@type": "Question",
          name: "Can oral cancer be cured if caught early?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes. When detected at an early stage, oral cancer has a 5-year survival rate of around 84%. That rate drops to roughly 40% when caught at a late stage. This is why routine dental screenings and monthly self-exams matter — the earlier a change is found, the better the outcome.",
          },
        },
      ],
    },
  ],
};

const types = [
  {
    name: "Squamous cell carcinoma (SCC)",
    pct: "~90% of cases",
    description:
      "The most common type by far. SCC begins in the squamous cells — the thin, flat cells that line the mouth, lips, tongue, and throat. Most oral cancers diagnosed are SCCs. Tobacco and alcohol are major drivers; HPV is increasingly implicated in oropharyngeal SCCs.",
  },
  {
    name: "Oropharyngeal cancer",
    pct: "Tonsils, base of tongue, throat",
    description:
      "Technically a subtype of SCC, oropharyngeal cancers develop at the back of the mouth and throat. They are now most commonly linked to HPV-16 infection rather than tobacco, and they tend to be caught at a later stage because the area is harder to see and symptoms are easy to miss.",
  },
  {
    name: "Salivary gland cancer",
    pct: "Rare — <10% of cases",
    description:
      "Cancer arising in the parotid, sublingual, or submandibular glands. There are several subtypes (mucoepidermoid carcinoma, adenoid cystic carcinoma, others), each with different behaviors and prognoses. Treatment and outlook vary widely by subtype.",
  },
  {
    name: "Oral lymphoma",
    pct: "Uncommon",
    description:
      "Cancer of the lymphatic tissue in the mouth or throat. It is more likely to be seen in people who are immunocompromised (e.g., HIV-positive individuals). It typically presents as a soft swelling, often painless, in the tonsils or back of the mouth.",
  },
];

const stats = [
  { value: "54,000+", label: "new diagnoses per year", sub: "US, oral & oropharyngeal combined" },
  { value: "84%", label: "survival rate if caught early", sub: "drops to ~40% at late stage" },
  { value: "2×", label: "more common in men", sub: "though rates in women are rising" },
  { value: "62", label: "median age at diagnosis", sub: "but it can occur at any age" },
];

const causes = [
  {
    factor: "Tobacco use",
    detail:
      "Cigarettes, cigars, pipes, chewing tobacco, and snuff are the single biggest modifiable risk factor for traditional oral cancers (lips, tongue, floor of mouth). Risk is dose-dependent — heavier use means higher risk — and it falls significantly after quitting.",
  },
  {
    factor: "Alcohol",
    detail:
      "Heavy drinking is an independent risk factor, and the combination with tobacco multiplies risk rather than just adding it. People who both smoke heavily and drink heavily face a risk up to 15 times higher than non-users of either.",
  },
  {
    factor: "HPV infection",
    detail:
      "Human Papillomavirus, specifically HPV-16, has overtaken tobacco as the leading cause of oropharyngeal cancers. HPV-related cancers often appear in non-smokers in their 40s and 50s. The HPV vaccine dramatically reduces risk.",
  },
  {
    factor: "Sun exposure",
    detail:
      "Chronic UV exposure is a leading risk factor specifically for cancer of the lower lip — not for cancers inside the mouth. People who work outdoors are at elevated risk. SPF lip balm and a wide-brimmed hat offer meaningful protection.",
  },
  {
    factor: "Age",
    detail:
      "Risk increases with age. Most diagnoses occur after age 55, though HPV-related oropharyngeal cancers are increasingly common in middle-aged adults. Regular dental screenings become more important as you get older.",
  },
];

const faqs = [
  {
    q: "What is oral cancer?",
    a: "Oral cancer is cancer that develops in any part of the mouth (oral cavity) or the back of the throat (oropharynx). This includes the lips, tongue, gums, floor of the mouth, hard and soft palate, cheeks, and throat. Most oral cancers are squamous cell carcinomas — cancers that begin in the flat cells lining these surfaces.",
  },
  {
    q: "What are the types of oral cancer?",
    a: "The main types are: squamous cell carcinoma (about 90% of cases), oropharyngeal cancer (tonsils, base of tongue, throat — often HPV-related), salivary gland cancer (rare, with several subtypes), and oral lymphoma (uncommon, more likely in immunocompromised individuals).",
  },
  {
    q: "Is oral cancer the same as throat cancer?",
    a: "They overlap. Oral cancer typically refers to cancers of the lips, tongue, gums, cheeks, and floor and roof of the mouth. Oropharyngeal (throat) cancer affects the tonsils, base of the tongue, and back of the throat. Because these regions connect, they are often grouped together as 'oral and oropharyngeal cancer.'",
  },
  {
    q: "How common is oral cancer?",
    a: "More than 54,000 Americans are diagnosed with oral and oropharyngeal cancer each year. It is about twice as common in men as in women, and the median age at diagnosis is 62. It ranks among the ten most common cancers worldwide.",
  },
  {
    q: "Can oral cancer be cured if caught early?",
    a: "Yes. The 5-year survival rate for early-stage oral cancer is around 84%. At a late stage, that drops to roughly 40%. Early detection through routine dental checkups and monthly self-exams is the single biggest factor in improving outcomes.",
  },
];

export default function OralCancerPage() {
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
          ← Back to Learn
        </Link>
        <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
          Basics
        </span>
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4 leading-tight">
          What Is Oral Cancer?
        </h1>
        <p className="text-lg text-ink-soft leading-relaxed mb-10">
          Oral cancer is cancer that develops in the mouth or throat. It is
          more common than most people realize, but when caught early it is
          highly treatable. Here is what you need to know.
        </p>

        {/* Definition */}
        <div className="bg-warm-dim border border-warm-dim rounded-2xl p-6 sm:p-8 mb-6">
          <h2 className="font-serif text-2xl text-ink mb-3">Definition</h2>
          <p className="text-ink-soft leading-relaxed mb-3">
            <strong className="text-ink">Oral cancer</strong> is an umbrella
            term for cancers that form in the{" "}
            <strong className="text-ink">oral cavity</strong> (lips, tongue,
            gums, cheeks, floor and roof of the mouth) or the{" "}
            <strong className="text-ink">oropharynx</strong> (tonsils, base
            of the tongue, and back of the throat).
          </p>
          <p className="text-ink-soft leading-relaxed">
            Roughly 90% of oral cancers are{" "}
            <strong className="text-ink">squamous cell carcinomas</strong> —
            cancers that begin in the thin, flat cells lining these surfaces.
            Most start as a small, painless change that goes unnoticed until it
            has grown.
          </p>
        </div>

        {/* Types */}
        <section className="mb-6">
          <h2 className="font-serif text-3xl text-ink mb-4">
            Types of oral cancer
          </h2>
          <div className="space-y-4">
            {types.map((t) => (
              <div
                key={t.name}
                className="bg-warm-dim border border-warm-dim rounded-2xl p-6 sm:p-8"
              >
                <div className="flex flex-wrap items-center gap-3 mb-2">
                  <h3 className="font-semibold text-ink text-lg">{t.name}</h3>
                  <span className="text-xs font-semibold text-brand bg-brand-soft px-2.5 py-0.5 rounded-full">
                    {t.pct}
                  </span>
                </div>
                <p className="text-ink-soft leading-relaxed text-sm">
                  {t.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* By the numbers */}
        <section className="mb-6">
          <h2 className="font-serif text-3xl text-ink mb-4">By the numbers</h2>
          <div className="grid grid-cols-2 gap-4">
            {stats.map((s) => (
              <div
                key={s.label}
                className="bg-warm-dim border border-warm-dim rounded-2xl p-5"
              >
                <div className="font-mono text-3xl sm:text-4xl text-brand font-semibold">
                  {s.value}
                </div>
                <div className="font-semibold text-ink text-sm mt-2">
                  {s.label}
                </div>
                <div className="text-xs text-ink-soft mt-1 leading-relaxed">
                  {s.sub}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* What causes it */}
        <section className="mb-6">
          <h2 className="font-serif text-3xl text-ink mb-4">
            What causes it?
          </h2>
          <p className="text-ink-soft leading-relaxed mb-5">
            Oral cancer develops when cells in the mouth or throat accumulate
            DNA mutations that cause uncontrolled growth. Several well-established
            risk factors increase the likelihood of those mutations occurring.
          </p>
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
                    {c.factor === "HPV infection" ? (
                      <>
                        <Link
                          href="/learn/hpv"
                          className="text-brand underline underline-offset-2 hover:text-brand-dark"
                        >
                          HPV infection
                        </Link>
                      </>
                    ) : (
                      c.factor
                    )}
                  </div>
                  <p className="text-sm text-ink-soft leading-relaxed">
                    {c.detail}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* What does it look like */}
        <section className="mb-6">
          <div className="bg-warm-dim border border-warm-dim rounded-2xl p-6 sm:p-8">
            <h2 className="font-serif text-2xl text-ink mb-3">
              What does it look like?
            </h2>
            <p className="text-ink-soft leading-relaxed mb-4">
              Early oral cancer is often painless and easy to overlook. The
              most common signs include:
            </p>
            <ul className="space-y-2 mb-4">
              {[
                "A red or white patch inside the mouth that doesn't go away",
                "A sore or ulcer that hasn't healed in 2 weeks",
                "A lump or thickening on the cheek, tongue, or gum",
                "Unexplained numbness or pain in the mouth or face",
                "Difficulty chewing, swallowing, or moving the jaw",
                "Hoarseness or a sore throat lasting more than 2 weeks",
                "A painless lump in the neck",
              ].map((sign) => (
                <li key={sign} className="flex gap-3 items-start text-sm text-ink-soft">
                  <span className="text-accent font-bold flex-shrink-0 mt-0.5">→</span>
                  {sign}
                </li>
              ))}
            </ul>
            <p className="text-sm text-ink-soft">
              See the full{" "}
              <Link
                href="/learn/signs"
                className="text-brand underline underline-offset-2 hover:text-brand-dark"
              >
                warning signs guide
              </Link>{" "}
              for detailed descriptions and photos.
            </p>
          </div>
        </section>

        {/* 2-week rule callout */}
        <div className="bg-accent/10 border border-accent/20 rounded-2xl p-6 mb-6">
          <h2 className="font-serif text-2xl text-ink mb-2">The 2-week rule</h2>
          <p className="text-ink leading-relaxed">
            Any sore, patch, lump, or change in your mouth that has not healed
            or resolved after <strong>2 weeks</strong> should be evaluated by a
            dentist or doctor. Most of the time it turns out to be nothing
            serious — but catching oral cancer early changes everything.
          </p>
        </div>

        {/* FAQ */}
        <section className="mb-6">
          <h2 className="font-serif text-3xl text-ink mb-6">
            Common questions
          </h2>
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
          <strong className="text-ink">Sources:</strong> American Cancer
          Society, National Cancer Institute SEER database, Oral Cancer
          Foundation, CDC, World Health Organization. This page is educational
          and does not constitute medical advice.
        </div>

        {/* CTA row */}
        <div className="flex flex-wrap gap-3">
          <Link
            href="/screener"
            className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
          >
            Take the free screener →
          </Link>
          <Link
            href="/learn/signs"
            className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            Learn warning signs
          </Link>
          <Link
            href="/learn/self-exam"
            className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            How to do a self-exam
          </Link>
        </div>
        <LearnReadNext currentHref="/learn/oral-cancer" />
      </article>
    </>
  );
}
