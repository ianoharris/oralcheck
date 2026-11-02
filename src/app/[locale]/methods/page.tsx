import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { localizedAlternates } from "@/lib/pageMetadata";
import { QUESTION_SKELETON } from "@/lib/questions";
import { SEER } from "@/lib/seerStats";
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

// One row per scored answer. The weight is read from QUESTION_SKELETON, the
// same table the screener scores with, so this page cannot drift from the
// tool. (It used to restate every weight by hand.) Factor names and notes are
// translated (messages.MethodsPage.factorNames/factorNotes, keyed by `id`);
// the OR and source columns are not: citations stay in their published form.
// `formula` is set only where the weight departs from round(ln(OR) × k) at the
// midpoint of the range; the page says so beside the weight.
type FactorRow = {
  id: string;
  q: string;
  opt: string;
  or: string;
  source: string;
  formula?: number;
};

const factors: FactorRow[] = [
  { id: "age65", q: "age", opt: "65plus", or: "~4.0× (adjusted)", source: "SEER, NCI; multivariable-adjusted" },
  { id: "age55", q: "age", opt: "55to64", or: "~2.5×", source: "SEER, NCI" },
  { id: "age35", q: "age", opt: "35to54", or: "~1.5×", source: "SEER, NCI" },
  { id: "sexMale", q: "sex", opt: "male", or: "~2.0× (conservative)", source: `SEER, NCI (${SEER.incidencePer100k.male} vs ${SEER.incidencePer100k.female} per 100,000)` },
  { id: "sexUnstated", q: "sex", opt: "preferNotToSay", or: "population average", source: "SEER, NCI" },
  { id: "tobaccoDaily", q: "tobacco", opt: "daily", or: "2.5 – 6.0×", source: "Gandini et al., Int J Cancer, 2008" },
  { id: "tobaccoOccasional", q: "tobacco", opt: "occasional", or: "~3.0×", source: "Gandini et al., Int J Cancer, 2008" },
  { id: "tobaccoFormer", q: "tobacco", opt: "former", or: "~1.5×", source: "Gandini et al., Int J Cancer, 2008" },
  { id: "alcoholDaily", q: "alcohol", opt: "daily", or: "~3.0×", source: "Bagnardi et al., Br J Cancer, 2015" },
  { id: "alcoholWeekly", q: "alcohol", opt: "weekly", or: "~2.0×", source: "Bagnardi et al., Br J Cancer, 2015" },
  { id: "alcoholRarely", q: "alcohol", opt: "rarely", or: "~1.2×", source: "Bagnardi et al., Br J Cancer, 2015" },
  { id: "betelCurrent", q: "betel", opt: "current", or: "7 – 10×", source: "IARC Monograph 85, 2004", formula: 10 },
  { id: "betelPast", q: "betel", opt: "past", or: "~2.5×", source: "IARC Monograph 85, 2004" },
  { id: "hpvHistory", q: "hpv", opt: "history", or: "3 – 5× (blended)", source: "Gillison et al., J Natl Cancer Inst, 2008", formula: 6 },
  { id: "hpvUnvaccinated", q: "hpv", opt: "neither", or: "~1.5× (proxy)", source: "D'Souza et al., NEJM, 2007; population exposure estimate" },
  { id: "hpvUnknown", q: "hpv", opt: "unknown", or: "~1.2× (proxy)", source: "D'Souza et al., NEJM, 2007; population exposure estimate" },
  { id: "sunExposure", q: "sun", opt: "daily", or: "2 – 3×", source: "Perea-Milla López et al., Br J Cancer, 2003", formula: 4 },
  { id: "sunRegular", q: "sun", opt: "regular", or: "~1.5×", source: "Perea-Milla López et al., Br J Cancer, 2003", formula: 2 },
  { id: "symptomPresent", q: "symptom", opt: "yes", or: "override", source: "Napier & Speight, J Oral Pathol Med, 2008" },
  { id: "symptomUnsure", q: "symptom", opt: "unsure", or: "override", source: "Napier & Speight, J Oral Pathol Med, 2008" },
  { id: "familyHistory", q: "family", opt: "yes", or: "~2.0×", source: "Negri et al., Eur J Cancer Prev, 2009" },
  { id: "familyDistant", q: "family", opt: "distant", or: "~1.3×", source: "Negri et al., Eur J Cancer Prev, 2009" },
  { id: "systemicYes", q: "systemic", opt: "yes", or: "2 – 4× (blended)", source: "Engels et al., JAMA, 2011; Grulich et al., Lancet, 2007" },
  { id: "systemicUnsure", q: "systemic", opt: "unsure", or: "~1.2× (proxy)", source: "Engels et al., JAMA, 2011; population exposure estimate" },
  { id: "dietLow", q: "diet", opt: "rarely", or: "~2.0×", source: "Pavia et al., Am J Clin Nutr, 2006" },
  { id: "dietWeekly", q: "diet", opt: "weekly", or: "~1.3×", source: "Pavia et al., Am J Clin Nutr, 2006" },
  { id: "dentalNever", q: "dental", opt: "never", or: "detection proxy", source: "SEER stage-at-diagnosis distribution" },
  { id: "dentalLongAgo", q: "dental", opt: "longago", or: "detection proxy", source: "SEER stage-at-diagnosis distribution" },
  { id: "dentalFewYears", q: "dental", opt: "fewyears", or: "detection proxy", source: "SEER stage-at-diagnosis distribution" },
];

function weightOf(f: FactorRow): number {
  const w = QUESTION_SKELETON.find((q) => q.id === f.q)?.options.find((o) => o.id === f.opt)?.weight;
  if (w === undefined) throw new Error(`methods: no screener option ${f.q}/${f.opt}`);
  return w;
}

// Grouped by question, in screener order, heaviest answer first. A single list
// sorted by weight scattered each question's answers across thirty rows.
const factorGroups = QUESTION_SKELETON.map((q) => ({
  id: q.id,
  rows: factors
    .filter((f) => f.q === q.id)
    .map((f) => ({ ...f, weight: weightOf(f) }))
    .sort((a, b) => b.weight - a.weight),
})).filter((g) => g.rows.length > 0);

// Bibliographic references: never translated (citations stay in their
// published language/format regardless of page locale).
const refs = [
  {
    id: 1,
    citation: "Gandini S, Botteri E, Iodice S, et al. Tobacco smoking and cancer: a meta-analysis. International Journal of Cancer. 2008;122(1):155–164.",
    url: "https://pubmed.ncbi.nlm.nih.gov/17893872/",
  },
  {
    id: 2,
    citation: "Bagnardi V, Rota M, Botteri E, et al. Alcohol consumption and site-specific cancer risk: a comprehensive dose–response meta-analysis. British Journal of Cancer. 2015;112(3):580–593.",
    url: "https://pubmed.ncbi.nlm.nih.gov/25422909/",
    note: "Oral cavity and pharynx: RR 1.83 for moderate drinking (12.5 to 50 g/day), 5.13 for heavy drinking (more than 50 g/day)",
  },
  {
    id: 3,
    citation: "Gillison ML, D'Souza G, Westra W, et al. Distinct risk factor profiles for human papillomavirus type 16–positive and human papillomavirus type 16–negative head and neck cancers. Journal of the National Cancer Institute. 2008;100(6):407–420.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18334711/",
  },
  {
    id: 4,
    citation: "International Agency for Research on Cancer. Betel-quid and Areca-nut Chewing and Some Areca-nut Derived Nitrosamines. IARC Monograph 85. Lyon, France: IARC; 2004.",
    url: "https://publications.iarc.fr/Book-And-Report-Series/Iarc-Monographs-On-The-Identification-Of-Carcinogenic-Hazards-To-Humans/Betel-Quid-And-Areca-Nut-Chewing-And-Some-Areca-Nut-Derived-Nitrosamines-2004",
  },
  {
    id: 5,
    citation: "Napier SS, Speight PM. Natural history of potentially malignant oral lesions and conditions: an overview of the literature. Journal of Oral Pathology & Medicine. 2008;37(1):1–10.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18154571/",
    note: "Leukoplakia 5–17% and erythroplakia 14–50% malignant transformation rates",
  },
  {
    id: 6,
    citation: "Pavia M, Pileggi C, Nobile CG, Angelillo IF. Association between fruit and vegetable consumption and oral cancer: a meta-analysis of observational studies. American Journal of Clinical Nutrition. 2006;83(5):1126–1134.",
    url: "https://pubmed.ncbi.nlm.nih.gov/16685056/",
    note: "OR 0.51 per daily portion of fruit, 0.50 for vegetables, across 16 studies",
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
    note: "Joint effect greater than multiplicative: interaction parameter 2.15 overall, 3.09 for oral cavity. Oral cavity, more than 20 cigarettes and 3 or more drinks a day: OR 15.5× vs neither",
  },
  {
    id: 9,
    citation: "Negri E, Boffetta P, Berthiller J, et al. Family history of cancer: pooled analysis in the International Head and Neck Cancer Epidemiology Consortium. International Journal of Cancer. 2009;124(2):394–401.",
    url: "https://pubmed.ncbi.nlm.nih.gov/18814262/",
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
    url: "https://pubmed.ncbi.nlm.nih.gov/12771984/",
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
  {
    id: 14,
    citation: "Blot WJ, McLaughlin JK, Winn DM, et al. Smoking and drinking in relation to oral and pharyngeal cancer. Cancer Research. 1988;48(11):3282–3287.",
    url: "https://pubmed.ncbi.nlm.nih.gov/3365707/",
    note: "The often-quoted \"more than 35-fold\" figure: oral and pharyngeal cancer combined, two or more packs and more than four drinks a day. Not used here: Hashibe 2009 is larger, pooled, and reports the oral cavity separately",
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

  const rationaleTitle = Object.fromEntries(rationale.map((r) => [r.id, r.title]));

  // Same colours as the results gauge: a light tint behind the strong shade,
  // which carries the text at 5.3 to 5.6:1.
  const tiers = [
    { label: t("tierLow"), range: "≤ 4", tint: "--color-low", strong: "--color-low-strong" },
    { label: t("tierModerate"), range: "5 – 13", tint: "--color-mid", strong: "--color-mid-strong" },
    { label: t("tierElevated"), range: "14 – 22", tint: "--color-elevated", strong: "--color-elevated-strong" },
    { label: t("tierHigh"), range: "≥ 23", tint: "--color-high", strong: "--color-high-strong" },
  ];

  const h2 = "font-serif text-2xl sm:text-3xl text-ink mb-4";
  const body = "text-ink-soft leading-relaxed";

  // One column width for everything. Prose, the rationale list and the tables
  // used to sit at three different widths, so the left edge held but the text
  // block kept changing shape down the page.
  return (
    <div className="max-w-3xl mx-auto px-5 py-12 sm:py-20">
      <div className="mb-10">
        <Link href="/" className="inline-flex min-h-11 items-center text-sm text-brand hover:underline">{t("back")}</Link>
      </div>

      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">{t("heading")}</h1>
      <p className="text-ink-soft text-lg leading-relaxed mb-5">{t("intro")}</p>

      {/* Dateline. A methodology page with no review date asks the reader to
          assume it's current; this states it before they scroll. */}
      <p className="text-xs uppercase tracking-wider text-ink-soft mb-14">
        {t("lastReviewedLabel")}
        {": "}
        <span className="text-ink font-semibold">{t("lastReviewedDate")}</span>
      </p>

      {/* Weight derivation */}
      <section className="mb-16">
        <h2 className={h2}>{t("weightDerivationHeading")}</h2>
        <div className={`${body} space-y-4`}>
          <p>{t.rich("weightP1", { i: (c) => <em>{c}</em> })}</p>
          <div className="bg-warm-dim rounded-xl px-6 py-4 font-mono text-sm text-ink">
            {t("weightFormula")}
          </div>
          <p>{t.rich("weightP2", { i: (c) => <em>{c}</em> })}</p>
          <p>{t("weightP3")}</p>
          {t.has("weightDepartures") && <p>{t("weightDepartures")}</p>}
        </div>
      </section>

      {/* Factor table, grouped by question */}
      <section className="mb-16">
        <h2 className={h2}>{t("factorTableHeading")}</h2>
        <div className="rounded-2xl border border-warm-dim overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-warm-dim text-left">
                <th className="pl-4 pr-2 sm:px-4 py-3 font-semibold text-ink">{t("colFactor")}</th>
                <th className="px-2 sm:px-4 py-3 font-semibold text-ink">{t("colOR")}</th>
                <th className="px-2 sm:px-4 py-3 font-semibold text-ink text-center">{t("colWeight")}</th>
                <th className="hidden sm:table-cell px-4 py-3 font-semibold text-ink">{t("colSource")}</th>
              </tr>
            </thead>
            {factorGroups.map((g) => (
              <tbody key={g.id} className="border-t border-warm-dim">
                <tr>
                  <th
                    colSpan={4}
                    scope="rowgroup"
                    className="px-4 pt-4 pb-1 text-left text-xs font-semibold uppercase tracking-wider text-brand"
                  >
                    {rationaleTitle[g.id] ?? g.id}
                  </th>
                </tr>
                {g.rows.map((f) => (
                  <tr key={f.id} className="align-top">
                    <td className="pl-4 pr-2 sm:px-4 py-2.5 text-ink">
                      {factorNames[f.id]}
                      {factorNotes[f.id] && (
                        <div className="text-xs text-ink-soft mt-0.5">{factorNotes[f.id]}</div>
                      )}
                      {/* The source column is hidden on phones, where the
                          table used to scroll sideways with no hint that the
                          citations were off-screen. */}
                      <div className="sm:hidden text-xs text-ink-soft/80 mt-1">{f.source}</div>
                    </td>
                    <td className="px-2 sm:px-4 py-2.5 text-ink-soft sm:whitespace-nowrap">{f.or}</td>
                    <td className="px-2 sm:px-4 py-2.5 text-center">
                      <span className="inline-block bg-brand-soft text-brand font-bold rounded-full px-2.5 py-0.5 text-xs tabular-nums">
                        {f.weight}
                      </span>
                      {f.formula !== undefined && (
                        <div className="text-[11px] leading-tight text-ink-soft mt-1 whitespace-nowrap">
                          {t("formulaGives", { n: f.formula })}
                        </div>
                      )}
                    </td>
                    <td className="hidden sm:table-cell px-4 py-2.5 text-ink-soft text-xs">{f.source}</td>
                  </tr>
                ))}
              </tbody>
            ))}
          </table>
        </div>
      </section>

      {/* Per-question rationale */}
      <section className="mb-16">
        <h2 className={h2}>{t("rationaleHeading")}</h2>
        <p className={`${body} mb-6`}>{t("rationaleIntro")}</p>
        <div className="space-y-6">
          {rationale.map((r) => (
            <div key={r.id} className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-full bg-brand-soft text-brand flex items-center justify-center">
                <Icon name={QUESTION_ICONS[r.id] ?? "check"} size={18} />
              </span>
              <div>
                <h3 className="text-ink font-semibold mb-1">{r.title}</h3>
                <p className={body}>{r.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Interaction term */}
      <section className="mb-16">
        <h2 className={h2}>{t("interactionHeading")}</h2>
        <div className={`${body} space-y-4`}>
          <p>{t.rich("interactionP1Rest", { b: (c) => <strong className="text-ink">{c}</strong> })}</p>
          <p>{t("interactionP2")}</p>
          <p className="text-xs">
            {t("interactionSourcesLabel")}{" "}Hashibe M, et al. Cancer Epidemiology, Biomarkers &amp; Prevention, 2009 (interaction parameter 2.15; oral cavity, heaviest combined users: OR 15.5×).
          </p>
        </div>
      </section>

      {/* Tier thresholds */}
      <section className="mb-16">
        <h2 className={h2}>{t("tierThresholdsHeading")}</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          {tiers.map((tier) => (
            <div
              key={tier.label}
              className="rounded-xl border p-4 text-center"
              style={{
                backgroundColor: `color-mix(in srgb, var(${tier.tint}) 14%, transparent)`,
                borderColor: `color-mix(in srgb, var(${tier.tint}) 45%, transparent)`,
                color: `var(${tier.strong})`,
              }}
            >
              <div className="font-semibold text-sm">{tier.label}</div>
              <div className="font-mono text-lg font-bold mt-1 tabular-nums">{tier.range}</div>
            </div>
          ))}
        </div>
        <div className={`${body} space-y-4`}>
          <p>{t("tierP1")}</p>
          <p>{t("tierP2Rest", { bold: t("tierP2Bold") })}</p>
          <p>{t("thresholdAnchorNote")}</p>
          {/* Guarded because English is written first and the translations
              follow on a separate run. Without this, a locale that hasn't been
              synced yet renders the literal key path on the page. */}
          {t.has("thresholdProvenance") && <p>{t("thresholdProvenance")}</p>}
        </div>
      </section>

      {/* One score, two diseases */}
      <section className="mb-16">
        <h2 className={h2}>{t("siteHeading")}</h2>
        <div className={`${body} space-y-4`}>
          <p>{t("siteBody")}</p>
          <p>{t("siteBody2")}</p>
          <p>{t("siteBody3")}</p>
        </div>
      </section>

      {/* Survival figures quoted elsewhere on the site */}
      <section className="mb-16">
        <h2 className={h2}>{t("seerHeading")}</h2>
        <p className={`${body} mb-5`}>{t("seerIntro")}</p>
        <div className="rounded-2xl border border-warm-dim overflow-hidden mb-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-warm-dim text-left">
                <th className="px-4 py-3 font-semibold text-ink">{t("colStage")}</th>
                <th className="px-4 py-3 font-semibold text-ink">{t("colSurvival")}</th>
                <th className="px-4 py-3 font-semibold text-ink">{t("colShare")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-warm-dim">
              {seerRows.map((r) => (
                <tr key={r.stage} className="align-top">
                  <td className="px-4 py-3 text-ink">
                    {r.stage}
                    <div className="text-xs text-ink-soft mt-0.5">{r.note}</div>
                  </td>
                  <td className="px-4 py-3 text-ink font-semibold tabular-nums">{r.survival}</td>
                  <td className="px-4 py-3 text-ink-soft tabular-nums">{r.share}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className={`${body} space-y-2`}>
          <p>{t("seerNote")}</p>
          <p className="text-xs">{t("seerSourceLine")}</p>
        </div>
      </section>

      {/* What a result does not mean, for the reader */}
      <section className="mb-16">
        <h2 className={h2}>{t("cannotHeading")}</h2>
        <p className={`${body} mb-5`}>{t("cannotIntro")}</p>
        <ul className="space-y-3">
          {cannot.map((item, i) => (
            <li key={i} className={`flex gap-3 ${body}`}>
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-accent/10 text-accent flex items-center justify-center mt-1">
                <Icon name="close" size={11} weight="bold" />
              </span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Limitations of the method, for the sceptical clinician */}
      <section className="mb-16">
        <h2 className={h2}>{t("limitationsHeading")}</h2>
        <ol className="space-y-3">
          {limitations.map((lim, i) => (
            <li key={i} className={`flex gap-3 ${body}`}>
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-warm-dim text-ink-soft text-xs flex items-center justify-center font-semibold mt-0.5 tabular-nums">
                {i + 1}
              </span>
              <span>{lim}</span>
            </li>
          ))}
        </ol>
      </section>

      {/* References. The number, citation, note and link now share one grid
          column each: the number used to float above the text, and the link
          ran straight on from the citation ("164.View on PubMed") on some
          entries and sat on its own line on others. */}
      <section className="mb-16">
        <h2 className={h2}>{t("referencesHeading")}</h2>
        <ol className="space-y-5">
          {refs.map((r) => (
            <li key={r.id} className="grid grid-cols-[2rem_1fr] text-sm">
              <span className="font-semibold text-ink tabular-nums">{r.id}.</span>
              <div className="text-ink-soft leading-relaxed">
                <p>{r.citation}</p>
                {"note" in r && r.note && (
                  <p className="text-xs text-ink-soft/80 mt-1">{r.note}</p>
                )}
                {r.url && (
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex min-h-11 items-center text-brand hover:underline text-xs"
                  >
                    {t("viewOn")}
                  </a>
                )}
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* Review provenance */}
      <section className="mb-16">
        <h2 className={h2}>{t("reviewHeading")}</h2>
        <div className={`${body} space-y-4`}>
          <p>{t("reviewBody")}</p>
          <p>{t("reviewCadence")}</p>
        </div>
      </section>

      {/* Footer CTA */}
      <div className="border-t border-warm-dim pt-10 flex flex-wrap gap-4">
        <Link
          href="/screener"
          className="bg-accent-dark hover:bg-accent text-white font-semibold px-6 py-3 rounded-full transition-colors"
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
