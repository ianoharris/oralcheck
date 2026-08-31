import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { localizedAlternates } from "@/lib/pageMetadata";
import { QUESTION_SKELETON } from "@/lib/questions";
import Icon, { type IconName } from "@/components/Icon";

// Reuse the screener's own icons so a reader recognizes each rationale as the
// question they just answered. Derived from the skeleton rather than restated,
// so a new question can't end up with a different icon in the two places.
const QUESTION_ICONS: Record<string, IconName> = Object.fromEntries(
  QUESTION_SKELETON.map((q) => [q.id, q.icon]),
);

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "MethodsMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/methods"),
  };
}

// Factor names/notes are translated (messages.MethodsPage.factorNames/factorNotes,
// keyed by `id`); the OR and source (bibliographic citation) columns are not,
// citations stay in their original published form regardless of page language.
const factors = [
  { id: "tobaccoDaily", or: "2.5 – 6.0×", weight: 8, source: "Gandini et al., Oral Oncology, 2008" },
  { id: "betelCurrent", or: "7 – 10×", weight: 9, source: "IARC Monograph 85, 2004" },
  { id: "tobaccoOccasional", or: "~3.0×", weight: 5, source: "Gandini et al., Oral Oncology, 2008" },
  { id: "alcoholDaily", or: "~3.0×", weight: 5, source: "Bagnardi et al., Annals of Oncology, 2015" },
  { id: "hpvHistory", or: "3 – 5× (blended)", weight: 5, source: "Gillison et al., JAMA, 2008" },
  { id: "systemicYes", or: "2 – 4× (blended)", weight: 5, source: "Engels et al., JAMA, 2011; Grulich et al., Lancet, 2007" },
  { id: "age65", or: "~4.0× (adjusted)", weight: 6, source: "SEER, NCI; multivariable-adjusted" },
  { id: "age55", or: "~2.5×", weight: 4, source: "SEER, NCI" },
  { id: "betelPast", or: "~2.5×", weight: 4, source: "IARC Monograph 85, 2004" },
  { id: "alcoholWeekly", or: "~2.0×", weight: 3, source: "Bagnardi et al., Annals of Oncology, 2015" },
  { id: "familyHistory", or: "~2.0×", weight: 3, source: "Negri et al., Eur J Cancer Prev, 2009" },
  { id: "dietLow", or: "~2.0×", weight: 3, source: "Pavia et al., Oral Oncology, 2006" },
  { id: "sexMale", or: "~2.0× (conservative)", weight: 3, source: "SEER, NCI (17.5 vs 6.6 per 100,000)" },
  { id: "age35", or: "~1.5×", weight: 2, source: "SEER, NCI" },
  { id: "sexUnstated", or: "population average", weight: 2, source: "SEER, NCI" },
  { id: "tobaccoFormer", or: "~1.5×", weight: 2, source: "Gandini et al., Oral Oncology, 2008" },
  { id: "hpvUnvaccinated", or: "~1.5× (proxy)", weight: 2, source: "D'Souza et al., NEJM, 2007; population exposure estimate" },
  { id: "sunExposure", or: "2 – 3×", weight: 2, source: "Perea-Milla López et al., Br J Cancer, 2003" },
  { id: "symptomPresent", or: "override", weight: 6, source: "Napier & Speight, J Oral Pathol Med, 2008" },
  { id: "symptomUnsure", or: "override", weight: 3, source: "Napier & Speight, J Oral Pathol Med, 2008" },
  { id: "dentalNever", or: "detection proxy", weight: 3, source: "SEER stage-at-diagnosis distribution" },
  { id: "dentalLongAgo", or: "detection proxy", weight: 2, source: "SEER stage-at-diagnosis distribution" },
  { id: "dentalFewYears", or: "detection proxy", weight: 1, source: "SEER stage-at-diagnosis distribution" },
  { id: "alcoholRarely", or: "~1.2×", weight: 1, source: "Bagnardi et al., Annals of Oncology, 2015" },
  { id: "sunRegular", or: "~1.5×", weight: 1, source: "Perea-Milla López et al., Br J Cancer, 2003" },
  { id: "familyDistant", or: "~1.3×", weight: 1, source: "Negri et al., Eur J Cancer Prev, 2009" },
  { id: "dietWeekly", or: "~1.3×", weight: 1, source: "Pavia et al., Oral Oncology, 2006" },
  { id: "hpvUnknown", or: "~1.2× (proxy)", weight: 1, source: "D'Souza et al., NEJM, 2007; population exposure estimate" },
  { id: "systemicUnsure", or: "~1.2× (proxy)", weight: 1, source: "Engels et al., JAMA, 2011; population exposure estimate" },
] as const;

// Bibliographic references: never translated (citations stay in their
// published language/format regardless of page locale).
const refs = [
  {
    id: 1,
    citation: "Gandini S, et al. Tobacco smoking and cancer: a meta-analysis. Oral Oncology. 2008;44(7):617–638.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18055252/",
  },
  {
    id: 2,
    citation: "Bagnardi V, et al. Alcohol consumption and site-specific cancer risk: a comprehensive dose–response meta-analysis. Annals of Oncology. 2015;26(1):39–55.",
    url: "https://pubmed.ncbi.nlm.nih.gov/25022040/",
  },
  {
    id: 3,
    citation: "Gillison ML, et al. Distinct risk factor profiles for human papillomavirus type 16–positive and human papillomavirus type 16–negative head and neck cancers. JAMA. 2008;168(3):294–305.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18195198/",
  },
  {
    id: 4,
    citation: "International Agency for Research on Cancer. Betel-quid and Areca-nut Chewing and Some Areca-nut Derived Nitrosamines. IARC Monograph 85. Lyon, France: IARC; 2004.",
    url: "https://publications.iarc.fr/Book-And-Report-Series/Iarc-Monographs-On-The-Identification-Of-Carcinogenic-Hazards-To-Humans/Betel-Quid-And-Areca-Nut-Chewing-And-Some-Areca-Nut-Derived-Nitrosamines-2004",
  },
  {
    id: 5,
    citation: "Napier SS, Speight PM. Natural history of potentially malignant oral lesions and conditions: an overview of the literature. Journal of Oral Pathology & Medicine. 2008;37(1):1–10.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18154566/",
    note: "Leukoplakia 5–17% and erythroplakia 14–50% malignant transformation rates",
  },
  {
    id: 6,
    citation: "Pavia M, et al. Evidence-based medicine on the relationship between diet and cancers of the oral cavity and pharynx. Oral Oncology. 2006;42(1):15–25.",
    url: "https://pubmed.ncbi.nlm.nih.gov/16054866/",
  },
  {
    id: 7,
    citation: "National Cancer Institute. SEER Cancer Statistics Review 1975–2021. Surveillance, Epidemiology, and End Results Program.",
    url: "https://seer.cancer.gov/csr/1975_2021/",
  },
  {
    id: 8,
    citation: "Hashibe M, Brennan P, Chuang SC, et al. Interaction between tobacco and alcohol use and the risk of head and neck cancer: pooled analysis in the International Head and Neck Cancer Epidemiology Consortium. Cancer Epidemiology, Biomarkers & Prevention. 2009;18(2):541–550.",
    url: "https://pubmed.ncbi.nlm.nih.gov/19190158/",
    note: "Heavy combined users: OR 35.8× vs non-users of both, supporting supra-multiplicative interaction term",
  },
  {
    id: 9,
    citation: "Negri E, Boffetta P, Berthiller J, et al. Family history of cancer: pooled analysis in the International Head and Neck Cancer Epidemiology Consortium. International Journal of Cancer. 2009;124(2):394–401.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18814267/",
    note: "OR ~2.0 for first-degree relative with head and neck cancer",
  },
  {
    id: 10,
    citation: "D'Souza G, Kreimer AR, Viscidi R, et al. Case-control study of human papillomavirus and oropharyngeal cancer. New England Journal of Medicine. 2007;356(19):1944–1956.",
    url: "https://pubmed.ncbi.nlm.nih.gov/17494927/",
    note: "HPV-16 seropositivity OR 32.2× for oropharyngeal cancer; behavioral exposure proxies used in screener",
  },
  {
    id: 11,
    citation: "Perea-Milla López E, Minarro-Del Moral RM, Martinez-Garcia C, et al. Lifestyles, environmental and phenotypic factors associated with lip cancer: a case-control study in southern Spain. British Journal of Cancer. 2003;88(11):1702–1707.",
    url: "https://pubmed.ncbi.nlm.nih.gov/12771986/",
    note: "Sun exposure OR 2–3× for lower lip squamous cell carcinoma in outdoor vs indoor workers",
  },
  {
    id: 12,
    citation: "Engels EA, Pfeiffer RM, Fraumeni JF Jr, et al. Spectrum of cancer risk among US solid organ transplant recipients. JAMA. 2011;306(17):1891–1901.",
    url: "https://pubmed.ncbi.nlm.nih.gov/22045767/",
    note: "Transplant Cancer Match Study, 175,732 recipients; elevated incidence across many sites including the oral cavity and pharynx, and markedly elevated for lip",
  },
  {
    id: 13,
    citation: "Grulich AE, van Leeuwen MT, Falster MO, Vajdic CM. Incidence of cancers in people with HIV/AIDS compared with immunosuppressed transplant recipients: a meta-analysis. Lancet. 2007;370(9581):59–67.",
    url: "https://pubmed.ncbi.nlm.nih.gov/17617273/",
    note: "Establishes that the two immunosuppressed populations share a similar pattern of raised incidence, which is the basis for grouping them into one question",
  },
] as const;

export default async function MethodsPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "MethodsPage" });
  const factorNames = t.raw("factorNames") as Record<string, string>;
  const factorNotes = t.raw("factorNotes") as Record<string, string>;
  const limitations = t.raw("limitations") as string[];
  const rationale = t.raw("rationale") as { id: string; title: string; body: string }[];
  const cannot = t.raw("cannot") as string[];
  const seerRows = t.raw("seerRows") as {
    stage: string; survival: string; share: string; note: string;
  }[];

  const tiers = [
    { label: t("tierLow"), range: "≤ 4", color: "bg-green-50 border-green-200 text-green-800" },
    { label: t("tierModerate"), range: "5 – 13", color: "bg-yellow-50 border-yellow-200 text-yellow-800" },
    { label: t("tierElevated"), range: "14 – 22", color: "bg-orange-50 border-orange-200 text-orange-800" },
    { label: t("tierHigh"), range: "≥ 23", color: "bg-red-50 border-red-200 text-red-800" },
  ];

  return (
    <div className="max-w-4xl mx-auto px-5 py-12 sm:py-20">
      <div className="mb-10">
        <Link href="/" className="text-sm text-brand hover:underline">{t("back")}</Link>
      </div>

      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">{t("heading")}</h1>
      <p className="text-ink-soft text-lg leading-relaxed mb-5 max-w-2xl">{t("intro")}</p>

      {/* Dateline. A methodology page with no review date asks the reader to
          assume it's current; this states it before they scroll. */}
      <p className="text-xs uppercase tracking-wider text-ink-soft mb-12">
        {t("lastReviewedLabel")}
        {": "}
        <span className="text-ink font-semibold">{t("lastReviewedDate")}</span>
      </p>

      {/* Weight derivation */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("weightDerivationHeading")}</h2>
        <div className="prose prose-sm text-ink-soft max-w-2xl leading-relaxed space-y-3">
          <p>{t.rich("weightP1", { i: (c) => <em>{c}</em> })}</p>
          <div className="bg-warm-dim rounded-xl px-6 py-4 font-mono text-sm text-ink">
            {t("weightFormula")}
          </div>
          <p>{t.rich("weightP2", { i: (c) => <em>{c}</em> })}</p>
          <p>{t("weightP3")}</p>
        </div>
      </section>

      {/* Factor table */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-4">{t("factorTableHeading")}</h2>
        <div className="overflow-x-auto rounded-2xl border border-warm-dim">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-warm-dim/60 text-left">
                <th className="px-4 py-3 font-semibold text-ink">{t("colFactor")}</th>
                <th className="px-4 py-3 font-semibold text-ink">{t("colOR")}</th>
                <th className="px-4 py-3 font-semibold text-ink text-center">{t("colWeight")}</th>
                <th className="px-4 py-3 font-semibold text-ink">{t("colSource")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-warm-dim">
              {/* Sorted here rather than by hand, so a row added in the wrong
                  place can't leave a column headed "Weight" out of order. */}
              {[...factors].sort((a, b) => b.weight - a.weight).map((f) => (
                <tr key={f.id} className="bg-warm-dim hover:bg-warm/50 transition-colors">
                  <td className="px-4 py-3 text-ink font-medium">
                    {factorNames[f.id]}
                    {factorNotes[f.id] && (
                      <div className="text-xs text-ink-soft font-normal mt-0.5">{factorNotes[f.id]}</div>
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

      {/* Per-question rationale */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("rationaleHeading")}</h2>
        <p className="text-sm text-ink-soft max-w-2xl leading-relaxed mb-6">{t("rationaleIntro")}</p>
        <div className="space-y-5">
          {rationale.map((r) => (
            <div key={r.id} className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-full bg-brand-soft text-brand flex items-center justify-center">
                <Icon name={QUESTION_ICONS[r.id] ?? "check"} size={18} />
              </span>
              <div className="max-w-2xl">
                <h3 className="text-ink font-semibold text-sm mb-1">{r.title}</h3>
                <p className="text-sm text-ink-soft leading-relaxed">{r.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Interaction term */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("interactionHeading")}</h2>
        <div className="prose prose-sm text-ink-soft max-w-2xl leading-relaxed space-y-3">
          <p>{t.rich("interactionP1Rest", { b: (c) => <strong className="text-ink">{c}</strong> })}</p>
          <p>{t("interactionP2")}</p>
          <p className="text-xs">
            {t("interactionSourcesLabel")} Hashibe M, et al. Cancer Epidemiology, Biomarkers &amp; Prevention, 2009 (heavy combined users: OR 35.8×); Bagnardi V, et al. Annals of Oncology, 2015.
          </p>
        </div>
      </section>

      {/* Tier thresholds */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-4">{t("tierThresholdsHeading")}</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          {tiers.map((tier) => (
            <div key={tier.label} className={`rounded-xl border p-4 text-center ${tier.color}`}>
              <div className="font-bold text-sm">{tier.label}</div>
              <div className="font-mono text-lg font-bold mt-1">{tier.range}</div>
            </div>
          ))}
        </div>
        <p className="text-sm text-ink-soft max-w-2xl leading-relaxed">{t("tierP1")}</p>
        <p className="text-sm text-ink-soft max-w-2xl leading-relaxed mt-2">
          {t("tierP2Rest", { bold: t("tierP2Bold") })}
        </p>
        <p className="text-sm text-ink-soft max-w-2xl leading-relaxed mt-2">
          {t("thresholdAnchorNote")}
        </p>
        {/* Guarded because English is written first and the translations follow
            on a separate run. Without this, a locale that hasn't been synced yet
            renders the literal key path on the page, which looks far worse than
            a paragraph that is briefly missing. */}
        {t.has("thresholdProvenance") && (
          <p className="text-sm text-ink-soft max-w-2xl leading-relaxed mt-2">
            {t("thresholdProvenance")}
          </p>
        )}
      </section>

      {/* Survival figures quoted elsewhere on the site */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("seerHeading")}</h2>
        <p className="text-sm text-ink-soft max-w-2xl leading-relaxed mb-5">{t("seerIntro")}</p>
        <div className="overflow-x-auto rounded-2xl border border-warm-dim mb-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-warm-dim/60 text-left">
                <th className="px-4 py-3 font-semibold text-ink">{t("colStage")}</th>
                <th className="px-4 py-3 font-semibold text-ink">{t("colSurvival")}</th>
                <th className="px-4 py-3 font-semibold text-ink">{t("colShare")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-warm-dim">
              {seerRows.map((r) => (
                <tr key={r.stage} className="bg-warm-dim">
                  <td className="px-4 py-3 text-ink font-medium">
                    {r.stage}
                    <div className="text-xs text-ink-soft font-normal mt-0.5">{r.note}</div>
                  </td>
                  <td className="px-4 py-3 text-ink font-semibold tabular-nums">{r.survival}</td>
                  <td className="px-4 py-3 text-ink-soft tabular-nums">{r.share}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-sm text-ink-soft max-w-2xl leading-relaxed">{t("seerNote")}</p>
        <p className="text-xs text-ink-soft max-w-2xl leading-relaxed mt-2">{t("seerSourceLine")}</p>
      </section>

      {/* What the tool cannot tell you */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("cannotHeading")}</h2>
        <p className="text-sm text-ink-soft max-w-2xl leading-relaxed mb-5">{t("cannotIntro")}</p>
        <ul className="space-y-3 max-w-2xl">
          {cannot.map((item, i) => (
            <li key={i} className="flex gap-3 text-sm text-ink-soft leading-relaxed">
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-accent/10 text-accent flex items-center justify-center mt-0.5">
                <Icon name="close" size={11} weight="bold" />
              </span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Limitations */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("limitationsHeading")}</h2>
        <ul className="space-y-2 text-sm text-ink-soft max-w-2xl">
          {limitations.map((lim, i) => (
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
        <h2 className="font-serif text-2xl text-ink mb-4">{t("referencesHeading")}</h2>
        <ol className="space-y-3">
          {refs.map((r) => (
            <li key={r.id} className="flex gap-3 text-sm text-ink-soft">
              <span className="flex-shrink-0 font-semibold text-ink w-5">{r.id}.</span>
              <span>
                {r.citation}
                {"note" in r && r.note && (
                  <span className="block text-xs text-ink-soft/70 mt-0.5">{r.note}</span>
                )}
                {r.url && (
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-brand hover:underline text-xs mt-0.5"
                  >
                    {t("viewOn")}
                  </a>
                )}
              </span>
            </li>
          ))}
        </ol>
      </section>

      {/* Review provenance */}
      <section className="mb-14">
        <h2 className="font-serif text-2xl text-ink mb-4">{t("reviewHeading")}</h2>
        <div className="rounded-2xl border border-warm-dim bg-warm-dim/40 p-6 max-w-2xl">
          <div className="text-xs uppercase tracking-wider text-ink-soft mb-1">
            {t("lastReviewedLabel")}
          </div>
          <div className="font-serif text-xl text-ink mb-4">{t("lastReviewedDate")}</div>
          <p className="text-sm text-ink-soft leading-relaxed mb-3">{t("reviewBody")}</p>
          <p className="text-sm text-ink-soft leading-relaxed">{t("reviewCadence")}</p>
        </div>
      </section>

      {/* Footer CTA */}
      <div className="border-t border-warm-dim pt-10 flex flex-wrap gap-4">
        <Link
          href="/screener"
          className="bg-accent hover:bg-accent-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          {t("takeScreener")}
        </Link>
        <Link
          href="/for-clinicians"
          className="border border-brand text-brand hover:bg-brand hover:text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          {t("forClinicians")}
        </Link>
      </div>
    </div>
  );
}
