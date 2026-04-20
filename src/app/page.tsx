import Link from "next/link";

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
