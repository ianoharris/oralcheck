import Link from "next/link";
import type { Metadata } from "next";
import LearnReadNext from "@/components/LearnReadNext";

export const metadata: Metadata = {
  title: "Signs & Symptoms of Oral Cancer: What to Look For",
  description:
    "Learn the early warning signs of oral cancer: red or white patches, sores that won't heal, unexplained lumps, and numbness. Know when to act.",
  alternates: { canonical: "https://oralcheck.org/learn/signs" },
};

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      "@id": `${SITE_URL}/learn/signs#webpage`,
      url: `${SITE_URL}/learn/signs`,
      name: "Signs & Symptoms of Oral Cancer: What to Look For",
      description:
        "Early oral cancer rarely hurts. Learn the warning signs worth checking — especially if anything lasts longer than 2 weeks.",
      about: {
        "@type": "MedicalCondition",
        name: "Oral Cancer",
        signOrSymptom: [
          { "@type": "MedicalSymptom", name: "Red or white patches in the mouth" },
          { "@type": "MedicalSymptom", name: "Mouth sores that do not heal within 2 weeks" },
          { "@type": "MedicalSymptom", name: "Lump or thickening in cheek, gums, or throat" },
          { "@type": "MedicalSymptom", name: "Numbness or pain in the mouth or lips" },
          { "@type": "MedicalSymptom", name: "Difficulty chewing, swallowing, or moving the jaw" },
          { "@type": "MedicalSymptom", name: "Hoarseness or sore throat lasting more than 2 weeks" },
          { "@type": "MedicalSymptom", name: "Ear pain without an ear problem" },
          { "@type": "MedicalSymptom", name: "Loose teeth with no dental explanation" },
        ],
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
        {
          "@type": "ListItem",
          position: 3,
          name: "Signs & Warning Symptoms",
          item: `${SITE_URL}/learn/signs`,
        },
      ],
    },
    {
      "@type": "FAQPage",
      "@id": `${SITE_URL}/learn/signs#faq`,
      mainEntity: [
        {
          "@type": "Question",
          name: "What are the early warning signs of oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The main early warning signs of oral cancer include: red or white patches inside the mouth, sores or ulcers that don't heal within 2 weeks, a lump or thickening in the cheek, gums, or throat, unexplained numbness or pain in the mouth or face, difficulty chewing or swallowing, loose teeth with no dental cause, persistent hoarseness, and ear pain with no ear problem. Most early oral cancers are completely painless, which is why regular dental screenings matter.",
          },
        },
        {
          "@type": "Question",
          name: "What does oral cancer look like?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Oral cancer most commonly appears as a red patch (erythroplakia), a white patch (leukoplakia), or a mixed red-and-white patch that doesn't scrape off. It can also appear as a sore that bleeds easily or refuses to heal, a raised lump or thickening, or an ulcer with irregular raised edges. These lesions can develop on the tongue, floor of the mouth, lips, gums, inner cheeks, palate, or the back of the throat.",
          },
        },
        {
          "@type": "Question",
          name: "Can oral cancer be painless?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes — early oral cancer is often completely painless. This is one of the main reasons it goes undetected until it reaches a later stage. A red or white patch, a small lump, or a sore that doesn't heal may cause no discomfort at all. Pain, when it does appear, tends to signal more advanced disease. This is why routine dental screenings and self-exams matter.",
          },
        },
        {
          "@type": "Question",
          name: "What is the 2-week rule for oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The 2-week rule means that any sore, patch, lump, or change in your mouth that hasn't resolved after 2 weeks should be evaluated by a dentist or doctor. Canker sores typically heal in 7 to 10 days. Anything lasting longer deserves a professional assessment — not because it's necessarily cancer, but because early detection dramatically improves outcomes.",
          },
        },
        {
          "@type": "Question",
          name: "Where does oral cancer most commonly develop?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The most common sites for oral cancer are the tongue (especially the sides and underside), the floor of the mouth, the lips, and the gums. Oropharyngeal cancers — those driven primarily by HPV — tend to develop at the base of the tongue, the tonsils, and the back wall of the throat. Tobacco-related oral cancers are more common on the floor of the mouth and the underside of the tongue.",
          },
        },
        {
          "@type": "Question",
          name: "How is oral cancer detected early?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Oral cancer is most commonly detected early through routine dental exams. Dentists perform a visual and physical check of the mouth and throat during regular visits. Monthly self-exams at home — using a mirror and good lighting to inspect your lips, gums, tongue, and floor of the mouth — can also catch changes between dental visits. A free online risk screener like OralCheck can help you assess your personal risk factors.",
          },
        },
      ],
    },
  ],
};

const signs = [
  {
    title: "Red or white patches",
    detail:
      "One of the most important early signs. A persistent red patch (erythroplakia) is the highest-risk lesion — studies estimate that 50% or more of red patches are either already cancerous or precancerous at biopsy. White patches (leukoplakia) are more common and usually benign, but roughly 5 to 17% will become malignant if left untreated. A mixed red-and-white speckled patch (erythroleukoplakia) carries the highest risk of all. The defining feature: these patches don't scrape or rub off.",
    urgent: true,
  },
  {
    title: "Sores or ulcers that don't heal",
    detail:
      "A sore or ulcer in the mouth that hasn't resolved after 2 weeks is the classic red flag. Canker sores (aphthous ulcers) heal in 7 to 10 days without treatment. Oral cancer lesions do not. They may have irregular, raised, or hardened edges — different from the clean round border of a canker sore. They may bleed easily when touched. The absence of pain does not mean the absence of danger.",
    urgent: true,
  },
  {
    title: "A lump, thickening, or rough patch",
    detail:
      "A new lump or area of thickening in the cheek, tongue, gum, or floor of the mouth — especially if it has a firm, hard consistency — warrants evaluation. Early tumors often feel rubbery or firm, like a pea under the skin. A swollen lymph node in the neck that persists for more than 2 weeks, even without an obvious infection, can also signal oral or oropharyngeal cancer.",
    urgent: false,
  },
  {
    title: "Numbness or unexplained pain",
    detail:
      "Unexplained numbness, tingling, or loss of sensation in the mouth, tongue, lips, or face — particularly if it's one-sided — can be a sign of nerve involvement. Intermittent or persistent pain in the mouth or jaw that has no obvious dental cause (no cavity, no tooth problem) is also worth investigating. Pain typically appears in more advanced cases, but some early cancers do cause discomfort.",
    urgent: false,
  },
  {
    title: "Difficulty chewing, swallowing, or moving the jaw",
    detail:
      "Feeling like food is sticking in your throat, difficulty opening your mouth fully (trismus), or pain and restriction when moving the jaw or tongue can indicate a mass affecting the surrounding structures. This symptom is more common with tumors at the base of the tongue or oropharynx — where HPV-related cancers tend to originate — and often appears before a visible lesion.",
    urgent: false,
  },
  {
    title: "Loose teeth with no dental explanation",
    detail:
      "If teeth become loose without an obvious cause — no gum disease diagnosis, no injury, no dental problem — it can signal that a tumor is affecting the bone or soft tissue supporting the teeth. This is particularly relevant for lesions on the gum (gingival carcinoma), which can mimic periodontal disease and go undetected for months.",
    urgent: false,
  },
  {
    title: "Persistent hoarseness or voice changes",
    detail:
      "A change in voice quality or persistent hoarseness that lasts more than 2 weeks — especially without a preceding cold or respiratory illness — can signal laryngeal involvement or a tumor near the back of the throat. This symptom is more associated with oropharyngeal and laryngeal cancers than with oral cavity cancers.",
    urgent: false,
  },
  {
    title: "Ear pain without an ear problem",
    detail:
      "Called referred otalgia, ear pain that occurs without any ear infection or problem can result from pain signals that originate in the throat or back of the tongue being misrouted through the ear's nerve pathway. If your ears hurt and your doctor finds no ear pathology, the base of tongue and tonsils should be examined.",
    urgent: false,
  },
];

const locations = [
  { site: "Tongue", note: "Sides and underside — most common site overall. Easy to overlook without a self-exam.", risk: "Highest" },
  { site: "Floor of the mouth", note: "The U-shaped tissue under the tongue. Often hard to see without lifting the tongue.", risk: "Very high" },
  { site: "Lips", note: "Lower lip most common — linked to sun exposure. Usually visible.", risk: "High" },
  { site: "Gums (gingiva)", note: "Can mimic gum disease. Loose teeth without a dental cause is a key clue.", risk: "High" },
  { site: "Inner cheeks", note: "The soft tissue lining the inside of the cheeks.", risk: "Moderate" },
  { site: "Base of tongue / tonsils", note: "Where HPV-related oropharyngeal cancers tend to start. Often no visible lesion.", risk: "High — HPV-related" },
  { site: "Palate", note: "Hard palate (roof of mouth) and soft palate. Check both sides.", risk: "Moderate" },
];

export default function SignsPage() {
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
        ← Back to Learn
      </Link>
      <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
        Symptoms
      </span>
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4 leading-tight">
        Signs &amp; Symptoms of Oral Cancer
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10">
        Most early{" "}
        <Link
          href="/learn/oral-cancer"
          className="text-brand underline underline-offset-2 hover:text-brand-dark"
        >
          oral cancers
        </Link>{" "}
        are completely painless. That is why so many cases are caught late. These
        are the changes worth knowing about — especially if anything lasts longer
        than 2 weeks.
      </p>

      {/* The 2-week rule — prominent */}
      <div className="bg-accent/10 border border-accent/20 rounded-2xl p-6 mb-12">
        <h2 className="font-serif text-xl text-ink mb-2">The 2-week rule</h2>
        <p className="text-ink-soft leading-relaxed text-sm">
          Any sore, patch, lump, or unusual change in your mouth that has{" "}
          <strong className="text-ink">not resolved after 2 weeks</strong> should
          be evaluated by a dentist or doctor. Canker sores heal in 7 to 10 days.
          Oral cancer does not. You do not need to wait to see if it gets worse
          — 2 weeks is the threshold.
        </p>
      </div>

      {/* Signs list */}
      <section className="mb-14">
        <h2 className="font-serif text-3xl text-ink mb-6">Warning signs</h2>
        <div className="space-y-5">
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
                        High priority
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
        <h2 className="font-serif text-3xl text-ink mb-3">
          Where oral cancer most commonly develops
        </h2>
        <p className="text-ink-soft leading-relaxed mb-6 text-sm">
          Oral cancer can appear anywhere in the mouth or throat, but certain
          sites carry higher risk. Knowing where to look makes self-exams and
          dental screenings more effective.
        </p>
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
        <h2 className="font-serif text-3xl text-ink mb-4">
          Why early oral cancer often has no pain
        </h2>
        <p className="text-ink-soft leading-relaxed mb-4">
          Pain is the body&apos;s alarm system, but early-stage oral cancer
          frequently bypasses it. A small tumor on the floor of the mouth or the
          side of the tongue may grow for months before causing any discomfort.
          Red and white patches are often completely asymptomatic.
        </p>
        <p className="text-ink-soft leading-relaxed mb-4">
          By the time pain appears — typically from nerve involvement or
          ulceration — the cancer is often at a more advanced stage. This dynamic
          is the core reason oral cancer has a low early-detection rate and a
          5-year survival rate of only about 40% for late-stage disease, compared
          to over 84% when caught early.
        </p>
        <p className="text-ink-soft leading-relaxed">
          The absence of pain is not reassurance. It is precisely why the
          2-week rule matters, and why routine dental exams that include an oral
          cancer check are worth keeping.
        </p>
      </section>

      {/* Oral cancer vs canker sore quick comparison */}
      <section className="mb-14">
        <h2 className="font-serif text-3xl text-ink mb-4">
          Oral cancer vs. canker sore: quick comparison
        </h2>
        <p className="text-ink-soft leading-relaxed mb-6 text-sm">
          Canker sores and early oral cancer can look similar.{" "}
          <Link href="/learn/canker-sore-vs-oral-cancer" className="text-brand hover:underline">
            See the full comparison page
          </Link>{" "}
          for more detail. The short version:
        </p>
        <div className="overflow-hidden rounded-2xl border border-warm-dim">
          <div className="grid grid-cols-3 bg-warm-dim px-5 py-3">
            <span className="text-xs font-bold uppercase tracking-wider text-ink-soft"></span>
            <span className="text-xs font-bold uppercase tracking-wider text-ink-soft">Canker sore</span>
            <span className="text-xs font-bold uppercase tracking-wider text-accent">Oral cancer</span>
          </div>
          {[
            ["Heals within", "7–10 days", "Does not heal"],
            ["Pain level", "Usually painful", "Often painless"],
            ["Border", "Round, clean", "Irregular, raised"],
            ["Color", "White/yellow center, red rim", "Red, white, or mixed"],
            ["Location", "Soft tissue, inside lips", "Any site, often tongue/floor"],
            ["What to do", "Monitor, should resolve", "See a dentist if 2+ weeks"],
          ].map(([label, a, b], i, arr) => (
            <div
              key={label}
              className={`grid grid-cols-3 px-5 py-3.5 ${
                i < arr.length - 1 ? "border-b border-warm-dim" : ""
              }`}
            >
              <span className="text-xs font-semibold text-ink-soft">{label}</span>
              <span className="text-xs text-ink-soft">{a}</span>
              <span className={`text-xs font-medium ${b === "Does not heal" || b === "See a dentist if 2+ weeks" ? "text-accent" : "text-ink-soft"}`}>{b}</span>
            </div>
          ))}
        </div>
      </section>

      {/* What to do */}
      <section className="mb-12">
        <h2 className="font-serif text-3xl text-ink mb-4">What to do if you notice a sign</h2>
        <div className="space-y-3">
          {[
            ["Don't wait for it to hurt", "Pain is not a reliable indicator of severity. Act on what you see, not what you feel."],
            ["Give it 2 weeks", "Minor trauma (a bite, rough food) causes mouth sores. Give any new lesion 2 weeks to resolve on its own."],
            ["See a dentist", "If it's still there after 2 weeks, book a dental appointment. Dentists are the primary screeners for oral cancer. Many offer free oral cancer screenings."],
            ["Do not self-diagnose", "Most abnormalities turn out to be benign. A professional exam — not a Google search — is what provides an answer."],
            ["Know your risk factors", "Tobacco use, heavy alcohol use, HPV, and age all raise your baseline risk. The more risk factors you carry, the more important regular screenings are."],
          ].map(([title, desc]) => (
            <div key={title as string} className="flex gap-4 bg-warm-dim border border-warm-dim rounded-2xl p-5">
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
        <h2 className="font-serif text-3xl text-ink mb-6">Common questions</h2>
        <div className="space-y-4">
          {[
            {
              q: "What does oral cancer look like?",
              a: "Oral cancer most commonly appears as a red patch, a white patch, or a mixed red-and-white patch that doesn't scrape off. It can also look like a sore with irregular edges that bleeds easily but won't heal, a raised lump, or a hard area of thickening. It can develop on the tongue, gums, lips, floor of the mouth, cheeks, or throat.",
            },
            {
              q: "Can oral cancer be painless?",
              a: "Yes — early oral cancer is often completely painless. This is why routine dental screenings and monthly self-exams matter. Pain tends to appear with more advanced disease, not early-stage lesions.",
            },
            {
              q: "What is the 2-week rule?",
              a: "Any sore, patch, lump, or change in your mouth that has not resolved after 2 weeks should be professionally evaluated. Canker sores heal in 7 to 10 days. Anything lasting longer deserves a dentist's assessment.",
            },
            {
              q: "Where does oral cancer most commonly develop?",
              a: "The sides and underside of the tongue and the floor of the mouth are the most common sites for oral cavity cancers. HPV-related oropharyngeal cancers tend to start at the base of the tongue and the tonsils, where there may be no visible lesion at all.",
            },
            {
              q: "How is oral cancer detected early?",
              a: "Regular dental exams, which include a visual and physical oral cancer check, are the most reliable way to catch it early. Monthly at-home self-exams can also catch changes between dental visits. If you have risk factors for oral cancer, talk to your dentist about getting a formal screening.",
            },
          ].map((faq) => (
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
        <strong className="text-ink">Sources:</strong> American Cancer Society, National Cancer
        Institute, Oral Cancer Foundation, National Institute of Dental and Craniofacial Research
        (NIDCR). This page is educational and does not constitute medical advice.
      </div>

      <div className="flex flex-wrap gap-3">
        <Link
          href="/screener"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          Take the free screener →
        </Link>
        <Link
          href="/learn/self-exam"
          className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          How to do a self-exam
        </Link>
        <Link
          href="/learn/canker-sore-vs-oral-cancer"
          className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          Canker sore vs oral cancer
        </Link>
        <Link
          href="/learn/risk-factors"
          className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          Risk factors
        </Link>
      </div>
      <p className="text-xs text-ink-soft mt-6">
        Written by Ian Harris, predental student at the University of Wisconsin-Madison.{" "}
        <Link href="/about" className="underline underline-offset-2 hover:text-ink">
          About OralCheck
        </Link>
      </p>
      <LearnReadNext currentHref="/learn/signs" />
    </article>
  );
}
