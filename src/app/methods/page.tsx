import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Scoring Methodology | OralCheck",
  description:
    "How OralCheck calculates oral cancer risk scores — sources, weight derivation, interaction terms, and limitations.",
};

const factors = [
  {
    factor: "Tobacco (daily)",
    or: "2.5 – 6.0×",
    weight: 8,
    source: "Gandini et al., Oral Oncology, 2008",
    note: "Anchor for the scaling constant k = 4.47",
  },
  {
    factor: "Betel quid / paan / gutka (current)",
    or: "7 – 10×",
    weight: 9,
    source: "IARC Monograph 85, 2004",
    note: "IARC Group 1 carcinogen independent of tobacco",
  },
  {
    factor: "Tobacco (occasional)",
    or: "~3.0×",
    weight: 5,
    source: "Gandini et al., Oral Oncology, 2008",
    note: "",
  },
  {
    factor: "Alcohol (daily)",
    or: "~3.0×",
    weight: 5,
    source: "Bagnardi et al., Annals of Oncology, 2015",
    note: "IARC Group 1 carcinogen",
  },
  {
    factor: "HPV-related history",
    or: "3 – 5× (blended)",
    weight: 5,
    source: "Gillison et al., JAMA, 2008",
    note: "Conservative estimate; OR ~15× for oropharyngeal specifically",
  },
  {
    factor: "Age 65+",
    or: "~4.0× (adjusted)",
    weight: 6,
    source: "SEER, NCI; multivariable-adjusted",
    note: "Median age at diagnosis is 62",
  },
  {
    factor: "Age 55 – 64",
    or: "~2.5×",
    weight: 4,
    source: "SEER, NCI",
    note: "",
  },
  {
    factor: "Betel quid (past use)",
    or: "~2.5×",
    weight: 4,
    source: "IARC Monograph 85, 2004",
    note: "",
  },
  {
    factor: "Alcohol (weekly)",
    or: "~2.0×",
    weight: 3,
    source: "Bagnardi et al., Annals of Oncology, 2015",
    note: "",
  },
  {
    factor: "Family history (first-degree)",
    or: "~2.0×",
    weight: 3,
    source: "General epidemiological consensus",
    note: "",
  },
  {
    factor: "Diet low in fruit/vegetables",
    or: "~2.0×",
    weight: 3,
    source: "Pavia et al., Oral Oncology, 2006",
    note: "Antioxidant-protective effect",
  },
  {
    factor: "Age 35 – 54",
    or: "~1.5×",
    weight: 2,
    source: "SEER, NCI",
    note: "",
  },
  {
    factor: "Tobacco (former)",
    or: "~1.5×",
    weight: 2,
    source: "Gandini et al., Oral Oncology, 2008",
    note: "Risk declines ~50% within 5 years of cessation",
  },
  {
    factor: "HPV (not vaccinated)",
    or: "~1.5×",
    weight: 2,
    source: "Gillison et al., JAMA, 2008",
    note: "",
  },
];

const refs = [
  {
    id: 1,
    citation:
      "Gandini S, et al. Tobacco smoking and cancer: a meta-analysis. Oral Oncology. 2008;44(7):617–638.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18055252/",
  },
  {
    id: 2,
    citation:
      "Bagnardi V, et al. Alcohol consumption and site-specific cancer risk: a comprehensive dose–response meta-analysis. Annals of Oncology. 2015;26(1):39–55.",
    url: "https://pubmed.ncbi.nlm.nih.gov/25022040/",
  },
  {
    id: 3,
    citation:
      "Gillison ML, et al. Distinct risk factor profiles for human papillomavirus type 16–positive and human papillomavirus type 16–negative head and neck cancers. JAMA. 2008;168(3):294–305.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18195198/",
  },
  {
    id: 4,
    citation:
      "International Agency for Research on Cancer. Betel-quid and Areca-nut Chewing and Some Areca-nut Derived Nitrosamines. IARC Monograph 85. Lyon, France: IARC; 2004.",
    url: "https://publications.iarc.fr/Book-And-Report-Series/Iarc-Monographs-On-The-Identification-Of-Carcinogenic-Hazards-To-Humans/Betel-Quid-And-Areca-Nut-Chewing-And-Some-Areca-Nut-Derived-Nitrosamines-2004",
  },
  {
    id: 5,
    citation:
      "Napier SS, Speight PM. Natural history of potentially malignant oral lesions and conditions: an overview of the literature. Journal of Oral Pathology & Medicine. 2008;37(1):1–10.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18154566/",
    note: "Leukoplakia 5–17% and erythroplakia 14–50% malignant transformation rates",
  },
  {
    id: 6,
    citation:
      "Pavia M, et al. Evidence-based medicine on the relationship between diet and cancers of the oral cavity and pharynx. Oral Oncology. 2006;42(1):15–25.",
    url: "https://pubmed.ncbi.nlm.nih.gov/16054866/",
  },
  {
    id: 7,
    citation:
      "National Cancer Institute. SEER Cancer Statistics Review 1975–2021. Surveillance, Epidemiology, and End Results Program.",
    url: "https://seer.cancer.gov/csr/1975_2021/",
  },
];

export default function MethodsPage() {
  return (
    <div className="max-w-4xl mx-auto px-5 py-12 sm:py-20">
      <div className="mb-10">
        <Link href="/" className="text-sm text-brand hover:underline">← OralCheck</Link>
      </div>

      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">Scoring Methodology</h1>
      <p className="text-ink-soft text-lg leading-relaxed mb-12 max-w-2xl">
        OralCheck assigns a risk weight to each answer based on published odds ratios. This page
        documents how that scoring works, which sources it&apos;s built on, and where the model has
        known limitations.
      </p>

      {/* Weight derivation */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-3">Weight Derivation</h2>
        <div className="prose prose-sm text-ink-soft max-w-2xl leading-relaxed space-y-3">
          <p>
            Each risk factor is assigned a weight proportional to the natural log of its published
            odds ratio (OR), scaled by a constant <em>k</em>:
          </p>
          <div className="bg-warm-dim rounded-xl px-6 py-4 font-mono text-sm text-ink">
            weight = round( ln(OR) × k )
          </div>
          <p>
            The scaling constant <em>k = 4.47</em> was chosen so that daily tobacco use (the
            highest-weighted modifiable factor, OR 6.0× per Gandini et al. 2008) maps to a weight
            of 8. That anchors all other weights to a consistent ordinal scale from the same
            evidence base.
          </p>
          <p>
            Where studies report a range of ORs, we use the midpoint or a conservative estimate.
            Symptoms like erythroplakia, leukoplakia, and non-healing ulcers work as clinical
            overrides rather than additive scores. They&apos;re better understood as possible
            in-situ pathology than as population-level risk exposures, so they&apos;re treated
            differently in the model.
          </p>
        </div>
      </section>

      {/* Factor table */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-4">Risk Factor Weights</h2>
        <div className="overflow-x-auto rounded-2xl border border-warm-dim">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-warm-dim/60 text-left">
                <th className="px-4 py-3 font-semibold text-ink">Factor</th>
                <th className="px-4 py-3 font-semibold text-ink">Published OR</th>
                <th className="px-4 py-3 font-semibold text-ink text-center">Weight</th>
                <th className="px-4 py-3 font-semibold text-ink">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-warm-dim">
              {factors.map((f) => (
                <tr key={f.factor} className="bg-warm-dim hover:bg-warm/50 transition-colors">
                  <td className="px-4 py-3 text-ink font-medium">
                    {f.factor}
                    {f.note && (
                      <div className="text-xs text-ink-soft font-normal mt-0.5">{f.note}</div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-ink-soft">{f.or}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="inline-block bg-brand-soft text-brand font-bold rounded-full px-2.5 py-0.5 text-xs">
                      {f.weight}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-ink-soft text-xs">{f.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Interaction term */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-3">Tobacco + Alcohol Interaction Term</h2>
        <div className="prose prose-sm text-ink-soft max-w-2xl leading-relaxed space-y-3">
          <p>
            When both tobacco and alcohol use are present at meaningful levels (daily or weekly),
            the model adds an interaction bonus of <strong className="text-ink">+3 points</strong>.
          </p>
          <p>
            The reason is that tobacco and alcohol together produce a multiplicative rather than
            additive increase in oral cancer risk. Combined regular use raises risk roughly 15×
            above baseline, while simply summing the individual weights only gets you to about 9×.
            The +3 captures that gap.
          </p>
          <p className="text-xs">
            Source: Bagnardi V, et al. Annals of Oncology, 2015.
          </p>
        </div>
      </section>

      {/* Tier thresholds */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-4">Risk Tier Thresholds</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          {[
            { label: "Low", range: "≤ 4", color: "bg-green-50 border-green-200 text-green-800" },
            { label: "Moderate", range: "5 – 13", color: "bg-yellow-50 border-yellow-200 text-yellow-800" },
            { label: "Elevated", range: "14 – 22", color: "bg-orange-50 border-orange-200 text-orange-800" },
            { label: "High", range: "≥ 23", color: "bg-red-50 border-red-200 text-red-800" },
          ].map((t) => (
            <div key={t.label} className={`rounded-xl border p-4 text-center ${t.color}`}>
              <div className="font-bold text-sm">{t.label}</div>
              <div className="font-mono text-lg font-bold mt-1">{t.range}</div>
            </div>
          ))}
        </div>
        <p className="text-sm text-ink-soft max-w-2xl leading-relaxed">
          The maximum possible score is approximately 53 (all highest-risk answers plus the
          interaction bonus). A few reference points: a daily smoker alone scores 8 (moderate);
          tobacco + alcohol + interaction lands at 16 (elevated); betel + tobacco + alcohol +
          interaction reaches 25 (high).
        </p>
        <p className="text-sm text-ink-soft max-w-2xl leading-relaxed mt-2">
          Regardless of score, any symptom lasting 2+ weeks (a persistent sore, red or white patch,
          unexplained lump, or difficulty swallowing) overrides the tier to <strong>High</strong> and
          triggers a prompt for immediate evaluation.
        </p>
      </section>

      {/* Limitations */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-3">Known Limitations</h2>
        <ul className="space-y-2 text-sm text-ink-soft max-w-2xl">
          {[
            "OralCheck hasn't been validated against a clinical outcome dataset. The weights are grounded in published literature, but they haven't been calibrated against a prospective cohort.",
            "The screener combines oral cavity and oropharyngeal cancer risk into a single score. These are epidemiologically distinct entities: HPV-16 is primarily a driver of oropharyngeal cancer, while tobacco and alcohol dominate in oral cavity cancer.",
            "Biological sex isn't captured. Men have roughly 2× the oral cavity cancer incidence of women, and that's a gap in the current model.",
            "Immunosuppression (HIV, organ transplant recipients, long-term corticosteroid use) is linked to significantly elevated oral cancer risk and isn't currently asked about.",
            "The screener relies on self-reported data. Tobacco and alcohol use are commonly under-reported.",
            "Dental visit frequency is included as a detection-delay proxy, not as a causal risk factor with a well-characterized OR. Its weight is based on clinical rationale rather than direct epidemiological derivation.",
          ].map((lim, i) => (
            <li key={i} className="flex gap-3">
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-warm-dim text-ink-soft text-xs flex items-center justify-center font-semibold mt-0.5">
                {i + 1}
              </span>
              <span>{lim}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* References */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-4">References</h2>
        <ol className="space-y-3">
          {refs.map((r) => (
            <li key={r.id} className="flex gap-3 text-sm text-ink-soft">
              <span className="flex-shrink-0 font-semibold text-ink w-5">{r.id}.</span>
              <span>
                {r.citation}
                {r.note && (
                  <span className="block text-xs text-ink-soft/70 mt-0.5">{r.note}</span>
                )}
                {r.url && (
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-brand hover:underline text-xs mt-0.5"
                  >
                    View on PubMed / publisher →
                  </a>
                )}
              </span>
            </li>
          ))}
        </ol>
      </section>

      {/* Footer CTA */}
      <div className="border-t border-warm-dim pt-10 flex flex-wrap gap-4">
        <Link
          href="/screener"
          className="bg-accent hover:bg-accent-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          Take the screener →
        </Link>
        <Link
          href="/for-clinicians"
          className="border border-brand text-brand hover:bg-brand hover:text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          For clinicians →
        </Link>
      </div>
    </div>
  );
}
