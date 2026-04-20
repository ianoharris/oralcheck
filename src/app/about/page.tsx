import Link from "next/link";

export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        About OralCheck
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10">
        A free, private tool to help anyone understand their oral cancer risk
        — and take the next step toward care.
      </p>

      <section className="bg-white rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-3">Why this exists</h2>
        <p className="text-ink-soft leading-relaxed mb-3">
          Oral cancer is one of the most underdiagnosed cancers in the United
          States. Its earliest symptoms look ordinary: a patch on the tongue,
          a sore that doesn&apos;t heal, a lump that doesn&apos;t hurt. Many
          people wait months or years before seeing a clinician.
        </p>
        <p className="text-ink-soft leading-relaxed">
          OralCheck is built on a simple premise: if people had a fast, private
          way to understand their risk and learn the signs, more cases would
          be caught at Stage I — where the 5-year survival rate is over 80%.
        </p>
      </section>

      <section className="bg-white rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-3">Who built this</h2>
        <p className="text-ink-soft leading-relaxed">
          OralCheck is a personal project built by a predental student. It&apos;s
          part awareness tool, part portfolio piece, entirely mission-driven.
          The screening logic is informed by published risk factors from the
          American Cancer Society, NCI, and clinical research on oral cancer
          epidemiology.
        </p>
      </section>

      <section className="bg-white rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-3">How it works</h2>
        <ul className="space-y-3 text-ink-soft leading-relaxed">
          <li>
            <strong className="text-ink">Your answers stay on your device.</strong>{" "}
            Nothing is saved to a server. No accounts. No tracking of responses.
          </li>
          <li>
            <strong className="text-ink">Scoring is educational, not clinical.</strong>{" "}
            Each answer contributes a weight derived from published risk data.
            The total maps to a risk tier — Low, Moderate, Elevated, or
            See-a-Dentist-Soon.
          </li>
          <li>
            <strong className="text-ink">It is not a diagnosis.</strong>{" "}
            OralCheck can suggest you should talk to a clinician. It cannot
            tell you whether you have cancer.
          </li>
        </ul>
      </section>

      <section className="bg-white rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-3">Sources &amp; references</h2>
        <ul className="space-y-2 text-sm text-ink-soft leading-relaxed list-disc pl-5">
          <li>American Cancer Society — Key Statistics for Oral Cavity and Oropharyngeal Cancers</li>
          <li>National Cancer Institute — SEER Cancer Statistics Review</li>
          <li>Oral Cancer Foundation — Risk Factors &amp; Early Detection</li>
          <li>CDC — Human Papillomavirus (HPV) and Cancer</li>
          <li>HRSA — Find a Health Center directory</li>
          <li>CAMBRA risk assessment framework — adapted for educational use</li>
        </ul>
      </section>

      <section className="bg-accent/10 border border-accent/20 rounded-2xl p-6 sm:p-8 mb-10">
        <h2 className="font-serif text-2xl text-ink mb-3">Medical disclaimer</h2>
        <p className="text-ink leading-relaxed">
          OralCheck provides general health information only. It does not
          constitute medical advice, diagnosis, or treatment. Always seek the
          advice of a qualified health provider with any questions about a
          medical condition. Do not delay seeking care because of information
          on this site.
        </p>
      </section>

      <div className="flex flex-wrap gap-3">
        <Link
          href="/screener"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          Start the screener →
        </Link>
        <Link
          href="/find-care"
          className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          Find care
        </Link>
      </div>
    </div>
  );
}
