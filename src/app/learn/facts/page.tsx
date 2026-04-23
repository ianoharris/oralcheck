import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Oral Cancer Facts & Statistics | OralCheck",
  description:
    "Key oral cancer statistics: 54,000+ US cases per year, 84% survival when caught early, and why HPV has overtaken tobacco as the top cause. Evidence-based, cited.",
  alternates: { canonical: "https://oralcheck.org/learn/facts" },
};

const stats = [
  {
    value: "54,000+",
    label: "new US cases per year",
    detail: "Oral and oropharyngeal cancers combined.",
  },
  {
    value: "11,580",
    label: "US deaths per year",
    detail: "About one death every 50 minutes.",
  },
  {
    value: "84%",
    label: "5-year survival if caught early",
    detail: "Drops to ~40% if found at a late stage.",
  },
  {
    value: "2×",
    label: "more common in men",
    detail: "Though rates in women are rising.",
  },
];

const facts = [
  {
    title: "HPV is now the leading cause of oropharyngeal cancer.",
    detail:
      "HPV-related cases have risen sharply over the past two decades, surpassing tobacco as the top driver. HPV vaccination dramatically reduces risk and is approved through age 45.",
  },
  {
    title: "Tobacco and alcohol together multiply risk — not just add.",
    detail:
      "People who use both are at substantially higher risk than the sum of each alone. Quitting either reduces risk over time.",
  },
  {
    title: "Early-stage oral cancer is highly treatable.",
    detail:
      "When found at Stage I, the 5-year survival rate is over 80%. At Stage IV, it drops below 40%. Stage at diagnosis is the single biggest factor in outcome.",
  },
  {
    title: "Dentists find most early cases.",
    detail:
      "A routine dental visit includes a 2-minute oral cancer screening. For people who skip dental care, cancers are more often caught at later stages.",
  },
  {
    title: "It doesn't only affect older smokers anymore.",
    detail:
      "HPV-related oropharyngeal cancer frequently appears in middle-aged adults with no history of tobacco use. If you have persistent symptoms, your age or lifestyle shouldn't rule out screening.",
  },
];

export default function FactsPage() {
  return (
    <article className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      <Link
        href="/learn"
        className="text-sm font-medium text-ink-soft hover:text-ink mb-6 inline-block"
      >
        ← Back to Learn
      </Link>
      <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
        Facts
      </span>
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        Oral Cancer Facts &amp; Stats
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10">
        The numbers that shape why early detection matters so much.
      </p>

      <div className="grid grid-cols-2 gap-4 mb-12">
        {stats.map((s) => (
          <div
            key={s.label}
            className="bg-white rounded-2xl border border-warm-dim p-5"
          >
            <div className="font-mono text-3xl sm:text-4xl text-brand font-semibold">
              {s.value}
            </div>
            <div className="font-semibold text-ink text-sm mt-2">
              {s.label}
            </div>
            <div className="text-xs text-ink-soft mt-1 leading-relaxed">
              {s.detail}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-5">
        {facts.map((f, i) => (
          <div key={f.title} className="bg-white rounded-2xl border border-warm-dim p-6">
            <div className="font-mono text-xs text-brand mb-2">
              FACT {String(i + 1).padStart(2, "0")}
            </div>
            <h2 className="font-serif text-2xl text-ink mb-2 leading-tight">
              {f.title}
            </h2>
            <p className="text-ink-soft leading-relaxed">{f.detail}</p>
          </div>
        ))}
      </div>

      <div className="mt-12 p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed">
        <strong className="text-ink">Sources:</strong> American Cancer Society
        (2024), Oral Cancer Foundation, National Cancer Institute SEER data,
        CDC. Figures are approximate and rounded for readability.
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <Link
          href="/screener"
          className="bg-accent hover:bg-accent-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          Check your risk →
        </Link>
        <Link
          href="/learn/self-exam"
          className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          Learn the self-exam
        </Link>
      </div>
    </article>
  );
}
