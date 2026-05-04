import Link from "next/link";

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "What is oral cancer?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Oral cancer refers to cancer that develops in any part of the mouth or throat, including the lips, tongue, gums, floor of the mouth, palate, and oropharynx. It is one of the most underdiagnosed cancers in the US, with over 54,000 new cases diagnosed each year. When caught early, the five-year survival rate is over 84%.",
      },
    },
    {
      "@type": "Question",
      name: "How common is oral cancer?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Oral and oropharyngeal cancers affect over 54,000 Americans each year and cause approximately 11,580 deaths annually — about one death every 50 minutes. Rates have been rising due to an increase in HPV-related throat cancers, which now outnumber tobacco-related cases in the oropharynx.",
      },
    },
    {
      "@type": "Question",
      name: "What are the early warning signs of oral cancer?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Early warning signs include a sore or ulcer in the mouth that doesn't heal after 2 weeks, a red or white patch on the gums, tongue, or lining of the mouth, a lump or thickening in the cheek, unexplained numbness or pain, and difficulty chewing or swallowing. Many early oral cancers are painless, which is why regular dental screenings matter.",
      },
    },
    {
      "@type": "Question",
      name: "How do I check for oral cancer at home?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "You can do a 2-minute self-exam at home using a mirror and good lighting. Check your lips, gums, tongue (top, sides, and underside), floor of the mouth, roof of the mouth, and throat. Look for any red or white patches, sores, lumps, or asymmetries. Anything that hasn't resolved after 2 weeks should be evaluated by a dentist.",
      },
    },
    {
      "@type": "Question",
      name: "Is OralCheck free to use?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes. OralCheck is completely free. No account is required, nothing is saved to a server, and there is no tracking of your answers. The screener takes about 2 minutes and provides a personalized risk summary based on published risk factors from the American Cancer Society, NCI, and Oral Cancer Foundation.",
      },
    },
  ],
};

const stats = [
  {
    value: "54,000+",
    label: "new US oral & oropharyngeal cancer cases each year",
  },
  {
    value: "84%",
    label: "five-year survival when caught early",
  },
  {
    value: "2 min",
    label: "is all a dental screening takes",
  },
];

const features = [
  {
    title: "Private risk screener",
    description:
      "10 quick questions based on published clinical risk factors. Nothing is saved or sent anywhere.",
    href: "/screener",
    cta: "Start screener",
  },
  {
    title: "Know the warning signs",
    description:
      "Red and white patches, non-healing sores, lumps. Learn what to look for and how to do a self-exam.",
    href: "/learn",
    cta: "Learn the signs",
  },
  {
    title: "Find affordable care",
    description:
      "Community health centers, dental schools, and free clinics near you — including HRSA-funded providers.",
    href: "/find-care",
    cta: "Find care",
  },
];

export default function Home() {
  return (
    <div>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <section className="max-w-6xl mx-auto px-5 pt-16 sm:pt-24 pb-12">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-10 items-center">
          <div className="md:col-span-3 space-y-6">
            <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full">
              Free · Private · Evidence-based
            </span>
            <h1 className="font-serif text-5xl sm:text-6xl leading-[1.05] text-ink">
              2 minutes could <span className="text-brand">save your life.</span>
            </h1>
            <p className="text-lg text-ink-soft max-w-xl leading-relaxed">
              Oral cancer is one of the most underdiagnosed cancers — largely
              because early symptoms look ordinary. OralCheck helps you
              understand your risk in minutes and points you toward care.
            </p>
            <div className="flex flex-wrap gap-3 pt-2">
              <Link
                href="/screener"
                className="bg-accent hover:bg-accent-dark text-white px-7 py-3.5 rounded-full font-semibold transition-colors inline-flex items-center gap-2"
              >
                Start Screening
                <span aria-hidden>→</span>
              </Link>
              <Link
                href="/learn"
                className="bg-white hover:bg-warm-dim text-ink px-7 py-3.5 rounded-full font-semibold transition-colors border border-warm-dim"
              >
                Learn the signs
              </Link>
            </div>
            <p className="text-xs text-ink-soft pt-2">
              Not a medical diagnosis. An educational awareness tool.
            </p>
            <div className="flex items-center gap-2 pt-1">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-brand flex-shrink-0" />
              <span className="text-xs text-ink-soft">
                Shared by the{" "}
                <span className="font-semibold text-ink">Wisconsin Dental Association</span>
              </span>
            </div>
          </div>

          <div className="md:col-span-2">
            <div
              aria-hidden
              className="aspect-square rounded-3xl bg-gradient-to-br from-brand-soft via-warm-dim to-warm-dim flex items-center justify-center relative overflow-hidden"
            >
              <div className="absolute inset-6 rounded-2xl border border-brand/20" />
              <div className="relative text-center px-6">
                <div className="text-6xl mb-3">🦷</div>
                <div className="font-serif text-2xl text-brand">Know early.</div>
                <div className="font-serif text-2xl text-accent">Act early.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-warm-dim bg-white/60">
        <div className="max-w-6xl mx-auto px-5 py-10 grid grid-cols-1 sm:grid-cols-3 gap-6">
          {stats.map((s) => (
            <div key={s.label}>
              <div className="font-mono text-3xl text-brand font-semibold">
                {s.value}
              </div>
              <div className="text-sm text-ink-soft mt-1 leading-snug">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-5 py-20">
        <div className="mb-10">
          <h2 className="font-serif text-3xl sm:text-4xl text-ink">
            Three things this tool does
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map(({ title, description, href, cta }) => (
            <Link
              key={href}
              href={href}
              className="group p-7 rounded-2xl bg-white border border-warm-dim hover:border-brand/40 transition-all"
            >
              <h3 className="font-serif text-2xl text-ink mb-3 group-hover:text-brand transition-colors">
                {title}
              </h3>
              <p className="text-ink-soft text-sm leading-relaxed mb-5">
                {description}
              </p>
              <span className="text-sm font-semibold text-brand">
                {cta} →
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section className="max-w-3xl mx-auto px-5 pb-16 text-center">
        <blockquote className="font-serif text-2xl sm:text-3xl text-ink leading-snug">
          &ldquo;Oral cancer is one of the few cancers where a routine visit
          that takes 2 minutes can change the outcome by decades.&rdquo;
        </blockquote>
      </section>
    </div>
  );
}
