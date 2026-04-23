import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Canker Sore vs Oral Cancer: How to Tell the Difference | OralCheck",
  description:
    "Canker sores heal in 7–10 days. Oral cancer doesn't. Learn the key differences, what each looks like, and exactly when to see a doctor.",
  alternates: { canonical: "https://oralcheck.org/learn/canker-sore-vs-oral-cancer" },
};

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      "@id": `${SITE_URL}/learn/canker-sore-vs-oral-cancer#webpage`,
      url: `${SITE_URL}/learn/canker-sore-vs-oral-cancer`,
      name: "Canker Sore vs Oral Cancer: How to Tell the Difference",
      description:
        "Canker sores heal in 7–10 days. Oral cancer doesn't. Learn the key differences, what each looks like, and exactly when to see a doctor.",
      about: { "@type": "MedicalCondition", name: "Oral Cancer" },
      lastReviewed: "2026-04-23",
    },
    {
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
        { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
        { "@type": "ListItem", position: 3, name: "Canker Sore vs Oral Cancer", item: `${SITE_URL}/learn/canker-sore-vs-oral-cancer` },
      ],
    },
    {
      "@type": "FAQPage",
      "@id": `${SITE_URL}/learn/canker-sore-vs-oral-cancer#faq`,
      mainEntity: [
        {
          "@type": "Question",
          name: "How do I know if a mouth sore is cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The most reliable indicator is time. Canker sores heal on their own within 7–14 days. If a sore, patch, or lump in your mouth hasn't resolved after 2 weeks, it should be evaluated by a dentist or doctor. Other warning signs include a sore that bleeds easily, is painless, has irregular edges, is growing, or is accompanied by a lump in your neck.",
          },
        },
        {
          "@type": "Question",
          name: "Can a canker sore turn into oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "No. Canker sores (aphthous ulcers) are benign and do not become cancerous. They are not caused by HPV or any other cancer-related virus. However, oral cancer can sometimes look similar to a canker sore, especially early on — which is why the 2-week rule matters. If something looks like a canker sore but hasn't healed in 2 weeks, get it checked.",
          },
        },
        {
          "@type": "Question",
          name: "What does an oral cancer lesion actually look like?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Oral cancer can appear as a red patch (erythroplakia), a white patch (leukoplakia), or a speckled red-and-white patch. It may look like a sore or ulcer that doesn't heal, a lump or thickening, or a rough, crusted area. Early lesions are often painless, which makes them easy to ignore. They can develop on the tongue, floor of the mouth, gums, cheeks, lips, or throat.",
          },
        },
        {
          "@type": "Question",
          name: "Is a painless sore more worrying than a painful one?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Counterintuitively, yes. Canker sores are typically quite painful. Early oral cancer is often painless or only mildly uncomfortable — which is one reason people delay getting them checked. A painless sore or patch that persists beyond 2 weeks is a more concerning sign than a painful one that's healing.",
          },
        },
        {
          "@type": "Question",
          name: "I have a white patch in my mouth. Is it cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "A white patch in the mouth (called leukoplakia) is not always cancer, but it should always be evaluated by a dentist — especially if it's been there longer than 2 weeks, can't be scraped off, or is accompanied by a red area. Most white patches turn out to be benign, but some are precancerous. A dentist can determine whether a biopsy is needed.",
          },
        },
      ],
    },
  ],
};

const comparison = [
  {
    feature: "Appearance",
    canker: "Round or oval; white or yellow center with a red border",
    cancer: "Red, white, or mixed patch; irregular edges; may bleed",
  },
  {
    feature: "Pain",
    canker: "Usually painful or tender",
    cancer: "Often painless early — especially concerning",
  },
  {
    feature: "Location",
    canker: "Inside cheeks, tongue, or gums only — never on lips",
    cancer: "Anywhere: tongue, gums, floor of mouth, lip, throat",
  },
  {
    feature: "Duration",
    canker: "Heals on its own in 7–14 days",
    cancer: "Doesn't heal — persists and may grow",
  },
  {
    feature: "Edges",
    canker: "Smooth, defined",
    cancer: "Irregular, raised, or indurated (hard)",
  },
  {
    feature: "Cause",
    canker: "Stress, injury, certain foods — not contagious",
    cancer: "Tobacco, alcohol, HPV, sun — or unknown",
  },
];

const faqs = [
  {
    q: "How do I know if a mouth sore is cancer?",
    a: "The most reliable indicator is time. Canker sores heal within 7–14 days. If a sore, patch, or lump hasn't resolved after 2 weeks, see a dentist or doctor. Other red flags: bleeds easily, is painless, has irregular edges, is growing, or is accompanied by a neck lump.",
  },
  {
    q: "Can a canker sore turn into oral cancer?",
    a: "No. Canker sores are benign and do not become cancerous. But oral cancer can sometimes look like a canker sore early on — which is exactly why the 2-week rule exists. If it looks like a canker sore but hasn't healed in 2 weeks, get it checked.",
  },
  {
    q: "What does an oral cancer lesion actually look like?",
    a: "It can appear as a red patch, a white patch, or a speckled mix of both. It may look like a sore that won't heal, a lump, or a rough crusted area. Early lesions are often painless. They can develop on the tongue, floor of the mouth, gums, cheeks, lips, or throat.",
  },
  {
    q: "Is a painless sore more worrying than a painful one?",
    a: "Counterintuitively, yes. Canker sores are typically quite painful. Early oral cancer is often painless — which is why people ignore it. A painless sore or patch that lasts beyond 2 weeks is more concerning than a painful one that's healing.",
  },
  {
    q: "I have a white patch in my mouth. Is it cancer?",
    a: "Not necessarily — but a white patch (leukoplakia) that's been there more than 2 weeks, can't be scraped off, or is paired with a red area should be evaluated by a dentist. Most turn out to be benign. A dentist can determine whether a biopsy is needed.",
  },
];

export default function CankerSorePage() {
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
          Guide
        </span>
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4 leading-tight">
          Canker Sore vs Oral Cancer
        </h1>
        <p className="text-lg text-ink-soft leading-relaxed mb-10">
          The main difference is time. Canker sores heal in 7–14 days — oral
          cancer doesn&apos;t. Here&apos;s how to tell them apart, and exactly
          when to stop waiting and see a doctor.
        </p>

        {/* Quick answer callout */}
        <div className="bg-brand/5 border border-brand/20 rounded-2xl p-6 mb-10">
          <h2 className="font-serif text-xl text-ink mb-2">The quick answer</h2>
          <p className="text-ink-soft leading-relaxed text-sm">
            If it&apos;s been there <strong className="text-ink">less than 2 weeks</strong> and is painful — it&apos;s almost certainly a canker sore. Give it time.{" "}
            If it&apos;s been there <strong className="text-ink">more than 2 weeks</strong>, is painless, bleeding, growing, or has irregular edges — see a dentist. Don&apos;t wait it out.
          </p>
        </div>

        {/* What is a canker sore */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">What is a canker sore?</h2>
          <p className="text-ink-soft leading-relaxed mb-4">
            A canker sore (aphthous ulcer) is a small, shallow sore that forms
            inside the mouth — on the inner cheeks, tongue, or gums. They&apos;re
            extremely common, affecting about 1 in 5 people.
          </p>
          <ul className="space-y-2 mb-4">
            {[
              "Round or oval with a white or yellow center and a red rim",
              "Usually quite painful, especially when eating or talking",
              "Appears inside the mouth only — never on the outer lip",
              "Heals on its own in 7 to 14 days without treatment",
              "Not contagious, not caused by a virus, not cancerous",
            ].map((item) => (
              <li key={item} className="flex gap-3 text-sm text-ink-soft">
                <span className="text-low font-bold mt-0.5 flex-shrink-0">✓</span>
                {item}
              </li>
            ))}
          </ul>
          <p className="text-ink-soft leading-relaxed text-sm">
            Common triggers include minor mouth injuries (biting your cheek),
            stress, certain foods (citrus, tomatoes), and hormonal changes.
          </p>
        </section>

        {/* What does oral cancer look like */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">What does an oral cancer lesion look like?</h2>
          <p className="text-ink-soft leading-relaxed mb-4">
            Oral cancer can look deceptively similar to a canker sore, especially
            in the early stages — which is exactly why people miss it. Key differences:
          </p>
          <ul className="space-y-2 mb-4">
            {[
              "A red patch (erythroplakia), white patch (leukoplakia), or speckled mix",
              "A sore or ulcer that doesn't heal after 2 weeks",
              "Often painless or only mildly uncomfortable early on",
              "Can appear anywhere: tongue sides, floor of mouth, gums, throat, lips",
              "May bleed easily when touched",
              "May feel hard or indurated (firm) underneath",
              "Can be accompanied by a painless lump in the neck",
            ].map((item) => (
              <li key={item} className="flex gap-3 text-sm text-ink-soft">
                <span className="text-accent font-bold mt-0.5 flex-shrink-0">→</span>
                {item}
              </li>
            ))}
          </ul>
          <p className="text-ink-soft leading-relaxed text-sm">
            The most common locations for oral cancer are the sides and bottom of
            the tongue, the floor of the mouth, and the back of the throat —
            places many people never look.
          </p>
        </section>

        {/* Comparison table */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-5">Side by side</h2>
          <div className="rounded-2xl overflow-hidden border border-warm-dim">
            {/* Header */}
            <div className="grid grid-cols-3 bg-warm-dim/60 text-xs font-semibold uppercase tracking-wider text-ink-soft">
              <div className="px-5 py-3">Feature</div>
              <div className="px-5 py-3 border-l border-warm-dim text-low">Canker Sore</div>
              <div className="px-5 py-3 border-l border-warm-dim text-accent">Oral Cancer</div>
            </div>
            {comparison.map((row, i) => (
              <div
                key={row.feature}
                className={`grid grid-cols-3 text-sm ${i % 2 === 0 ? "bg-white" : "bg-warm/40"}`}
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
          <h2 className="font-serif text-2xl text-ink mb-2">The 2-week rule</h2>
          <p className="text-ink leading-relaxed">
            Any sore, patch, lump, or change in your mouth that hasn&apos;t
            resolved after <strong>2 weeks</strong> should be seen by a dentist
            or doctor. Most of the time it turns out to be nothing — but that
            reassurance is worth a 10-minute appointment. Oral cancer caught at
            Stage I has an 84% five-year survival rate.
          </p>
        </div>

        {/* When to see a doctor */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">When to see a doctor — don&apos;t wait if:</h2>
          <div className="space-y-3">
            {[
              ["It's been there more than 2 weeks", "The single most important signal."],
              ["It's painless", "Early oral cancer is often painless. That's not reassuring — it's a reason to get checked."],
              ["It bleeds easily when touched", "Unusual bleeding from a sore or patch is a warning sign."],
              ["It's growing or changing", "A sore that's getting larger or changing color needs evaluation."],
              ["It feels hard underneath", "Firmness or induration under a lesion is concerning."],
              ["You also have a lump in your neck", "Swollen lymph nodes alongside a mouth sore warrant prompt evaluation."],
            ].map(([title, desc]) => (
              <div key={title} className="bg-white border border-warm-dim rounded-2xl p-5 flex gap-4 items-start">
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
          <h2 className="font-serif text-3xl text-ink mb-6">Common questions</h2>
          <div className="space-y-4">
            {faqs.map((faq) => (
              <details
                key={faq.q}
                className="bg-white border border-warm-dim rounded-2xl group"
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
          <strong className="text-ink">Sources:</strong> American Cancer Society,
          Oral Cancer Foundation, National Institute of Dental and Craniofacial
          Research (NIDCR), Mayo Clinic. This page is educational and does not
          constitute medical advice.
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            href="/screener"
            className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
          >
            Check your risk →
          </Link>
          <Link
            href="/learn/signs"
            className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            See all warning signs
          </Link>
          <Link
            href="/find-care"
            className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            Find a dentist →
          </Link>
        </div>
      </article>
    </>
  );
}
