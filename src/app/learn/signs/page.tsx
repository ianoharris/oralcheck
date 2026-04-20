import Link from "next/link";

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
