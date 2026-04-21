import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Signs & Symptoms of Oral Cancer | OralCheck",
  description:
    "Learn the early warning signs of oral cancer: red or white patches, sores that don't heal, lumps, and numbness. Early detection saves lives.",
};

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      url: `${SITE_URL}/learn/signs`,
      name: "Signs & Warning Symptoms of Oral Cancer",
      description:
        "Early oral cancer rarely hurts. Learn the signs worth checking — especially if anything lasts longer than 2 weeks.",
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
        ],
      },
      audience: { "@type": "MedicalAudience", audienceType: "Patient" },
    },
    {
      "@type": "FAQPage",
      mainEntity: [
        {
          "@type": "Question",
          name: "What are the warning signs of oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The main warning signs of oral cancer include: red or white patches inside the mouth, sores or ulcers that don't heal within 2 weeks, a lump or thickening in the cheek or gums, unexplained numbness or pain in the mouth or face, difficulty chewing or swallowing, and persistent hoarseness. Most early oral cancers are painless, which is why regular screening matters.",
          },
        },
        {
          "@type": "Question",
          name: "What is the 2-week rule for oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The 2-week rule means that any sore, patch, lump, or other change in your mouth that hasn't healed or gone away after 2 weeks should be evaluated by a dentist or doctor. Canker sores typically heal in 7–10 days. Anything lasting longer deserves a professional look — not because it's definitely cancer, but because early detection dramatically improves outcomes.",
          },
        },
        {
          "@type": "Question",
          name: "Can oral cancer be painless?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes — early oral cancer is often completely painless, which is one reason it goes undetected. A red or white patch, a small lump, or a sore that doesn't heal may not cause any discomfort at all. This is why routine oral cancer screenings during dental visits are so important.",
          },
        },
        {
          "@type": "Question",
          name: "What does oral cancer look like?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Oral cancer can appear as a red patch (erythroplakia), a white patch (leukoplakia), a speckled red-and-white patch, a sore that bleeds easily or doesn't heal, a lump or thickening of the skin or lining of the mouth, or loose teeth with no dental explanation. It can develop on the tongue, gums, lips, cheeks, floor of the mouth, or throat.",
          },
        },
        {
          "@type": "Question",
          name: "How is oral cancer detected early?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Oral cancer is most often detected early through routine dental exams, which include a quick visual and physical check of the mouth and throat. You can also perform a monthly self-exam at home by looking inside your mouth with a flashlight and checking for any patches, sores, or lumps. A free online risk screener like OralCheck can also help you understand your personal risk factors.",
          },
        },
      ],
    },
  ],
};

const signs = [
  {
    title: "Red or white patches",
    description:
      "A persistent red (erythroplakia) or white (leukoplakia) patch inside the mouth that doesn't scrape off. Red patches are especially concerning.",
  },
  {
    title: "Sores that don't heal",
    description:
      "A mouth or lip sore lasting longer than 2 weeks. Canker sores typically heal in 7–10 days; anything longer deserves evaluation.",
  },
  {
    title: "Lumps or thickening",
    description:
      "A new lump, bump, or area of thickening in the cheek, tongue, gum, or neck — especially if it's painless.",
  },
  {
    title: "Numbness or pain",
    description:
      "Unexplained numbness, tenderness, or pain in the mouth, face, tongue, or neck.",
  },
  {
    title: "Difficulty swallowing or chewing",
    description:
      "Trouble swallowing, chewing, or moving the jaw or tongue — or the feeling that something is stuck in your throat.",
  },
  {
    title: "Ear pain with no ear problem",
    description:
      "Ongoing ear pain without any ear infection can sometimes signal an issue at the back of the tongue or throat.",
  },
  {
    title: "Voice changes",
    description:
      "Persistent hoarseness or a change in your voice that lasts more than 2 weeks.",
  },
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
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        Signs &amp; Warning Symptoms
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10">
        Early oral cancer rarely hurts. That&apos;s part of why it goes
        unnoticed. These are the signs worth checking — especially if anything
        lasts longer than 2 weeks.
      </p>

      <div className="space-y-4">
        {signs.map((s, i) => (
          <div
            key={s.title}
            className="bg-white rounded-2xl border border-warm-dim p-5"
          >
            <div className="flex gap-4">
              <div className="font-mono text-sm text-brand font-semibold shrink-0 w-8">
                {String(i + 1).padStart(2, "0")}
              </div>
              <div>
                <h2 className="font-semibold text-ink text-lg mb-1">
                  {s.title}
                </h2>
                <p className="text-ink-soft leading-relaxed">{s.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-10 p-6 rounded-2xl bg-accent/10 border border-accent/20">
        <h2 className="font-serif text-2xl text-ink mb-2">The 2-week rule</h2>
        <p className="text-ink leading-relaxed">
          If any of the above lasts longer than 2 weeks, see a dentist or
          doctor. Most of the time it turns out to be nothing serious — but
          catching oral cancer early changes everything.
        </p>
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <Link
          href="/learn/self-exam"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          How to do a self-exam →
        </Link>
        <Link
          href="/screener"
          className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          Check your risk
        </Link>
      </div>
    </article>
  );
}
