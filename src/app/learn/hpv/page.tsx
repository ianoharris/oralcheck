import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "HPV and Oral Cancer: What You Need to Know | OralCheck",
  description:
    "HPV-16 is now the leading cause of oropharyngeal cancer in the US, overtaking tobacco. Learn who is at risk, what the symptoms are, and how the HPV vaccine helps.",
  alternates: { canonical: "https://oralcheck.org/learn/hpv" },
};

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      "@id": `${SITE_URL}/learn/hpv#webpage`,
      url: `${SITE_URL}/learn/hpv`,
      name: "HPV and Oral Cancer: What You Need to Know",
      description:
        "HPV-16 is now the leading cause of oropharyngeal cancer in the US. Learn who is at risk, what the symptoms are, and how the HPV vaccine helps.",
      about: {
        "@type": "MedicalCondition",
        name: "HPV-Related Oropharyngeal Cancer",
        associatedAnatomy: {
          "@type": "AnatomicalStructure",
          name: "Oropharynx",
        },
        cause: {
          "@type": "MedicalCause",
          name: "Human Papillomavirus (HPV-16)",
        },
      },
      lastReviewed: "2025-01-01",
    },
    {
      "@type": "FAQPage",
      "@id": `${SITE_URL}/learn/hpv#faq`,
      mainEntity: [
        {
          "@type": "Question",
          name: "Can HPV cause oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes. HPV (Human Papillomavirus), specifically the HPV-16 strain, is now the leading cause of oropharyngeal cancers — cancers of the tonsils, base of tongue, and back of the throat. HPV-related oral cancer cases have risen sharply over the past two decades and now outnumber those caused by tobacco for this part of the mouth.",
          },
        },
        {
          "@type": "Question",
          name: "What are the symptoms of HPV-related oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Common symptoms include a persistent sore throat, difficulty swallowing, a painless lump in the neck, ear pain, and hoarseness that doesn't resolve within two weeks. Because HPV-related cancers often start at the base of the tongue or tonsils — areas not easily visible — they are frequently caught at a later stage.",
          },
        },
        {
          "@type": "Question",
          name: "Does the HPV vaccine prevent oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The HPV vaccine (Gardasil 9) protects against HPV-16 and HPV-18, the strains responsible for most HPV-related cancers. It is FDA-approved for people ages 9 through 45 and is most effective when given before exposure to HPV. While it cannot treat an existing HPV infection, vaccination significantly reduces the risk of developing HPV-related oropharyngeal cancer.",
          },
        },
        {
          "@type": "Question",
          name: "Who is most at risk for HPV-related oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "HPV-related oropharyngeal cancer disproportionately affects middle-aged adults — particularly men between 40 and 60 — who have no history of tobacco use. A higher number of lifetime oral sexual partners is associated with greater risk. Unlike tobacco-related oral cancer, it often appears in people with no obvious risk factors, which is why awareness matters.",
          },
        },
        {
          "@type": "Question",
          name: "Is HPV-related oral cancer curable?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "HPV-positive oropharyngeal cancers generally have better outcomes than HPV-negative ones. When caught early, survival rates are high. However, many HPV-related oral cancers are found at a later stage because symptoms are easy to miss or dismiss. Any symptom in the mouth or throat lasting more than two weeks deserves evaluation by a dentist or doctor.",
          },
        },
      ],
    },
  ],
};

const faqs = [
  {
    q: "Can HPV cause oral cancer?",
    a: "Yes. HPV — specifically the HPV-16 strain — is now the leading cause of oropharyngeal cancers, which are cancers of the tonsils, base of tongue, and back of the throat. HPV-related cases have risen sharply over the past two decades and now outnumber tobacco-related cases in this part of the mouth.",
  },
  {
    q: "What are the symptoms of HPV-related oral cancer?",
    a: "Common symptoms include a persistent sore throat, difficulty swallowing, a painless lump in the neck, ear pain, and hoarseness that lasts longer than two weeks. Because these cancers often start at the base of the tongue or tonsils — areas not easily visible — they are frequently caught at a later stage.",
  },
  {
    q: "Does the HPV vaccine prevent oral cancer?",
    a: "The HPV vaccine (Gardasil 9) protects against HPV-16 and HPV-18, the strains responsible for most HPV-related cancers. It is FDA-approved for people ages 9 through 45 and is most effective before exposure to HPV. It cannot treat an existing infection, but vaccination significantly lowers the risk of HPV-related oropharyngeal cancer.",
  },
  {
    q: "Who is most at risk?",
    a: "HPV-related oropharyngeal cancer disproportionately affects middle-aged adults — particularly men between 40 and 60 — with no history of tobacco use. A higher number of lifetime oral sexual partners is associated with increased risk. Unlike traditional oral cancer, it often appears in people with no obvious risk factors.",
  },
  {
    q: "Is HPV-related oral cancer curable?",
    a: "HPV-positive oropharyngeal cancers tend to have better outcomes than HPV-negative ones. When caught early, survival rates are high. But many cases are found late because symptoms are easy to miss. Any symptom in the mouth or throat lasting more than two weeks deserves evaluation by a dentist or doctor.",
  },
];

export default function HpvPage() {
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
          Risk Factor
        </span>
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4 leading-tight">
          HPV and Oral Cancer
        </h1>
        <p className="text-lg text-ink-soft leading-relaxed mb-10">
          HPV-16 is now the leading cause of throat cancer in the US — overtaking
          tobacco. Here's what that means, who's at risk, and what you can do.
        </p>

        {/* Key stat callout */}
        <div className="bg-brand/5 border border-brand/20 rounded-2xl p-6 mb-10 flex gap-5 items-start">
          <div className="text-4xl" aria-hidden>🦠</div>
          <div>
            <div className="font-serif text-2xl text-ink mb-1">
              HPV is now #1
            </div>
            <p className="text-ink-soft leading-relaxed text-sm">
              Human Papillomavirus (HPV) has overtaken tobacco as the leading
              cause of oropharyngeal cancers — cancers of the tonsils, base of
              tongue, and back of the throat. Cases have risen by more than 300%
              since the 1980s.
            </p>
          </div>
        </div>

        {/* What is HPV-related oral cancer */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">
            What is HPV-related oral cancer?
          </h2>
          <p className="text-ink-soft leading-relaxed mb-4">
            HPV is a common sexually transmitted virus. Most infections clear on
            their own without symptoms. In some people, however, certain strains
            — especially <strong className="text-ink">HPV-16</strong> — cause
            changes in cell DNA that can eventually lead to cancer.
          </p>
          <p className="text-ink-soft leading-relaxed mb-4">
            HPV-related oral cancers typically develop in the{" "}
            <strong className="text-ink">oropharynx</strong>: the tonsils, the
            base of the tongue, and the back wall of the throat. This is
            different from traditional oral cancers, which tend to form on the
            lips, gums, tongue tip, and floor of the mouth.
          </p>
          <p className="text-ink-soft leading-relaxed">
            Because the oropharynx is hard to see and these cancers often don't
            cause pain early on, they're frequently caught later than other oral
            cancers — which is why knowing the symptoms matters.
          </p>
        </section>

        {/* Symptoms */}
        <section className="mb-10">
          <h2 className="font-serif text-3xl text-ink mb-4">
            Symptoms to watch for
          </h2>
          <p className="text-ink-soft leading-relaxed mb-5">
            HPV-related throat cancers can look a lot like a persistent cold or
            sore throat. The key signal is{" "}
            <strong className="text-ink">duration</strong> — symptoms that don't
            go away after two weeks deserve attention.
          </p>
          <ul className="space-y-3">
            {[
              ["Persistent sore throat", "Not caused by infection, doesn't resolve in 2 weeks"],
              ["Painless lump in the neck", "Often the first sign — caused by lymph node involvement"],
              ["Difficulty swallowing", "A feeling that food is catching or not going down right"],
              ["Ear pain on one side", "Can radiate from the throat even without ear infection"],
              ["Hoarseness or voice changes", "Lasting more than two weeks with no obvious cause"],
              ["Unexplained weight loss", "Especially when combined with any of the above"],
            ].map(([symptom, note]) => (
              <li
                key={symptom}
                className="bg-white border border-warm-dim rounded-xl p-4 flex gap-3 items-start"
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
          <h2 className="font-serif text-3xl text-ink mb-4">
            Who is at risk?
          </h2>
          <p className="text-ink-soft leading-relaxed mb-4">
            HPV-related oropharyngeal cancer most commonly affects{" "}
            <strong className="text-ink">men between the ages of 40 and 60</strong>{" "}
            with no history of tobacco use. This is one of the things that makes
            it easy to dismiss — people assume oral cancer is a smoker's disease.
          </p>
          <p className="text-ink-soft leading-relaxed mb-4">
            A higher number of lifetime oral sexual partners is associated with
            increased risk, as HPV is primarily transmitted through sexual contact.
            However, HPV is extremely common — most sexually active adults have
            been exposed at some point — and the vast majority of infections
            never lead to cancer.
          </p>
          <p className="text-ink-soft leading-relaxed">
            Tobacco and alcohol use alongside HPV infection further raises risk.
            Immune-compromising conditions (like HIV) also reduce the body's
            ability to clear HPV naturally.
          </p>
        </section>

        {/* Vaccine */}
        <section className="bg-brand/5 border border-brand/20 rounded-2xl p-7 mb-10">
          <h2 className="font-serif text-3xl text-ink mb-3">
            The HPV vaccine
          </h2>
          <p className="text-ink-soft leading-relaxed mb-4">
            <strong className="text-ink">Gardasil 9</strong> protects against
            HPV-16 and HPV-18 — the two strains responsible for most HPV-related
            cancers. It is FDA-approved for people ages{" "}
            <strong className="text-ink">9 through 45</strong>.
          </p>
          <p className="text-ink-soft leading-relaxed mb-4">
            The vaccine is most effective when given before exposure to HPV, which
            is why it is routinely recommended for preteens. But adults who
            weren't vaccinated earlier may still benefit — talk to your doctor.
          </p>
          <p className="text-ink-soft leading-relaxed">
            The vaccine cannot treat an existing HPV infection, but research
            shows it has already begun to reduce HPV-related cancer rates in
            vaccinated populations.
          </p>
        </section>

        {/* FAQ */}
        <section className="mb-12">
          <h2 className="font-serif text-3xl text-ink mb-6">
            Common questions
          </h2>
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
                <p className="px-6 pb-5 text-ink-soft leading-relaxed text-sm">
                  {faq.a}
                </p>
              </details>
            ))}
          </div>
        </section>

        <div className="mt-4 p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed mb-8">
          <strong className="text-ink">Sources:</strong> American Cancer Society,
          National Cancer Institute, CDC (HPV and Cancer), Oral Cancer Foundation,
          Journal of Clinical Oncology (HPV-OPC incidence data). This page is
          educational and does not constitute medical advice.
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
        </div>
      </article>
    </>
  );
}
