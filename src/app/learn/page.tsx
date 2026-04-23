import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Learn About Oral Cancer | OralCheck",
  description:
    "Evidence-based guides on oral cancer signs, self-exams, HPV, and statistics. Written for regular people, not clinicians.",
  alternates: { canonical: "https://oralcheck.org/learn" },
};

const articles = [
  {
    href: "/learn/signs",
    tag: "Symptoms",
    title: "Signs & Warning Symptoms",
    description:
      "Red and white patches, sores that don't heal, lumps, and numbness — what to look for and when to act.",
    icon: "⚠️",
  },
  {
    href: "/learn/self-exam",
    tag: "How-to",
    title: "How to Do a 2-Minute Self-Exam",
    description:
      "Step-by-step: lips, gums, tongue, floor of mouth, palate, throat. All you need is a mirror.",
    icon: "🔎",
  },
  {
    href: "/learn/facts",
    tag: "Facts",
    title: "Oral Cancer Facts & Stats",
    description:
      "Incidence, survival rates by stage, who's most affected, and the growing role of HPV.",
    icon: "📊",
  },
  {
    href: "/learn/hpv",
    tag: "Risk Factor",
    title: "HPV and Oral Cancer",
    description:
      "HPV-16 is now the leading cause of throat cancer in the US. What that means, who's at risk, and how the vaccine helps.",
    icon: "🦠",
  },
  {
    href: "/learn/prevention",
    tag: "Prevention",
    title: "How to Prevent Oral Cancer",
    description:
      "Six evidence-based steps: quit tobacco, limit alcohol, get vaccinated, protect your lips, and get screened regularly.",
    icon: "🛡️",
  },
  {
    href: "/learn/canker-sore-vs-oral-cancer",
    tag: "Guide",
    title: "Canker Sore vs Oral Cancer",
    description:
      "Canker sores heal in 7–10 days. Oral cancer doesn't. Here's how to tell them apart and when to see a doctor.",
    icon: "🔬",
  },
];

export default function LearnPage() {
  return (
    <div className="max-w-5xl mx-auto px-5 py-10 sm:py-16">
      <div className="max-w-2xl mb-12">
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-3">Learn</h1>
        <p className="text-ink-soft text-lg leading-relaxed">
          Short, evidence-based guides on oral cancer detection and prevention.
          Written for regular people, not clinicians.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {articles.map((a) => (
          <Link
            key={a.href}
            href={a.href}
            className="group bg-white rounded-2xl border border-warm-dim p-7 hover:border-brand/40 transition-all"
          >
            <div className="text-3xl mb-4" aria-hidden>
              {a.icon}
            </div>
            <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-2.5 py-0.5 rounded-full mb-3">
              {a.tag}
            </span>
            <h2 className="font-serif text-2xl text-ink mb-2 group-hover:text-brand transition-colors">
              {a.title}
            </h2>
            <p className="text-sm text-ink-soft leading-relaxed">
              {a.description}
            </p>
            <div className="mt-5 text-sm font-semibold text-brand">
              Read →
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
