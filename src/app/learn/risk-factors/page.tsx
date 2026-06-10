import type { Metadata } from "next";
import Link from "next/link";
import LearnReadNext from "@/components/LearnReadNext";

export const metadata: Metadata = {
  title: "Oral Cancer Risk Factors: What Raises Your Risk | OralCheck",
  description:
    "The major risk factors for oral cancer include tobacco use, alcohol, HPV-16, age, and sun exposure. Learn how each factor works and how they combine.",
  alternates: { canonical: "https://oralcheck.org/learn/risk-factors" },
};

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      "@id": `${SITE_URL}/learn/risk-factors#webpage`,
      url: `${SITE_URL}/learn/risk-factors`,
      name: "Oral Cancer Risk Factors: What Raises Your Risk",
      description:
        "The major risk factors for oral cancer include tobacco use, alcohol, HPV-16, age, and sun exposure. Learn how each factor works and how they interact.",
      about: { "@type": "MedicalCondition", name: "Oral Cancer" },
      audience: { "@type": "MedicalAudience", audienceType: "Patient" },
      datePublished: "2026-06-09",
      lastReviewed: "2026-06-09",
    },
    {
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
        { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
        { "@type": "ListItem", position: 3, name: "Risk Factors", item: `${SITE_URL}/learn/risk-factors` },
      ],
    },
    {
      "@type": "FAQPage",
      "@id": `${SITE_URL}/learn/risk-factors#faq`,
      mainEntity: [
        {
          "@type": "Question",
          name: "What is the biggest risk factor for oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "For oral cavity cancers (lips, tongue, gums, floor of the mouth), tobacco use — cigarettes, cigars, pipes, chewing tobacco, and snuff — is the single biggest modifiable risk factor, responsible for about 75% of cases. For oropharyngeal cancers (base of tongue, tonsils, throat), HPV-16 infection has now surpassed tobacco as the leading cause in the United States.",
          },
        },
        {
          "@type": "Question",
          name: "Does alcohol increase the risk of oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes. Heavy alcohol use is an independent risk factor for oral cancer. People who drink heavily are 5 to 6 times more likely to develop oral cancer than non-drinkers. The combination of tobacco and alcohol is especially dangerous — their effects are synergistic, meaning the combined risk is greater than either alone. Someone who both smokes heavily and drinks heavily can face a 30-fold increase in oral cancer risk.",
          },
        },
        {
          "@type": "Question",
          name: "Can you get oral cancer without smoking or drinking?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes. HPV-related oropharyngeal cancers have been increasing rapidly in people who have never smoked or used tobacco. HPV-16 is now responsible for the majority of throat and tonsillar cancers in the US. Other risk factors — including age, family history, sun exposure, and diet — can also contribute without any tobacco or alcohol use.",
          },
        },
        {
          "@type": "Question",
          name: "Is oral cancer hereditary?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Family history is a recognized but modest independent risk factor. Having a first-degree relative with oral or head-and-neck cancer does increase your risk somewhat, likely due to a combination of shared genetic susceptibility and shared environmental exposures (such as tobacco use in the household). However, the majority of oral cancers are not primarily hereditary — they are driven by modifiable risk factors like tobacco, alcohol, and HPV.",
          },
        },
        {
          "@type": "Question",
          name: "At what age does oral cancer risk increase?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Oral cancer risk increases significantly with age. Historically, most cases were diagnosed in people over 55, with peak incidence in the 60s and 70s. However, HPV-related oropharyngeal cancers are being diagnosed in younger adults — people in their 40s and 50s — at increasing rates. Age 55 and older remains the highest-risk group overall, but the disease is not exclusive to older adults.",
          },
        },
      ],
    },
  ],
};

const riskFactors = [
  {
    rank: 1,
    name: "Tobacco use",
    weight: "Very high",
    weightColor: "text-accent",
    summary: "Responsible for roughly 75% of traditional oral cavity cancers.",
    detail:
      "All forms of tobacco significantly raise oral cancer risk — cigarettes, cigars, pipes, chewing tobacco, snuff, and vaping products. The risk scales with how much you use and for how long. Heavy smokers are 6 to 27 times more likely to develop oral cancer than non-smokers. Quitting reduces risk over time, but risk does not return to baseline for years after cessation.",
    link: null,
  },
  {
    rank: 2,
    name: "Alcohol use",
    weight: "High",
    weightColor: "text-accent",
    summary: "Heavy drinkers are 5–6x more likely to develop oral cancer.",
    detail:
      "Alcohol is a direct carcinogen in the oral cavity. The risk increases with the amount consumed, and heavy drinking (more than 3–4 drinks per day) carries the highest risk. When combined with tobacco, the effects are synergistic — the combined risk far exceeds the sum of the two individual risks. Someone who both smokes heavily and drinks heavily can have a 30-fold increased risk compared to someone who does neither.",
    link: null,
  },
  {
    rank: 3,
    name: "HPV-16 infection",
    weight: "High — rising",
    weightColor: "text-accent",
    summary: "Now the leading cause of oropharyngeal cancer, overtaking tobacco.",
    detail:
      "Human papillomavirus type 16 (HPV-16) is a sexually transmitted infection that has become the dominant driver of oropharyngeal cancers — cancers of the base of the tongue, tonsils, and throat. Unlike tobacco-related oral cancers, HPV-related cancers tend to occur in younger adults with no history of smoking, and are more responsive to treatment. The HPV vaccine (Gardasil 9) is highly effective at preventing HPV-16 infection when given before exposure.",
    link: "/learn/hpv",
  },
  {
    rank: 4,
    name: "Age",
    weight: "Moderate",
    weightColor: "text-caution",
    summary: "Risk rises sharply after 55. Peak incidence in the 60s and 70s.",
    detail:
      "Oral cancer is more common as people age, partly because of longer cumulative exposure to risk factors, and partly because of age-related changes in immune function. The average age at diagnosis is 62. However, HPV-related oropharyngeal cancers are increasingly diagnosed in adults in their 40s and 50s, so younger adults are not without risk.",
    link: null,
  },
  {
    rank: 5,
    name: "Sun exposure",
    weight: "Moderate — lip cancer",
    weightColor: "text-caution",
    summary: "UV radiation is the main risk factor for lip cancer specifically.",
    detail:
      "Chronic, unprotected sun exposure increases the risk of lip cancer, particularly on the lower lip. People who work outdoors for long periods — farmers, construction workers, fishermen — have historically higher rates of lip cancer. Using lip balm with SPF and wearing a hat are effective protective measures.",
    link: null,
  },
  {
    rank: 6,
    name: "Diet",
    weight: "Moderate",
    weightColor: "text-caution",
    summary: "Diets low in fruits and vegetables are consistently linked to higher risk.",
    detail:
      "A diet low in fruits and vegetables — and therefore low in antioxidants, vitamins A, C, and E, and other micronutrients — is associated with elevated oral cancer risk in epidemiological studies. The protective effect of produce is well-documented, though diet is considered a secondary factor compared to tobacco, alcohol, and HPV.",
    link: null,
  },
  {
    rank: 7,
    name: "Betel nut use",
    weight: "Very high — specific populations",
    weightColor: "text-accent",
    summary: "A major cause of oral cancer in South and Southeast Asia.",
    detail:
      "Betel nut (areca nut), often chewed with betel leaf and slaked lime — or as paan, gutka, or pan masala — is one of the most potent oral carcinogens known. It is the fourth most commonly used psychoactive substance in the world and is responsible for high rates of oral submucous fibrosis and squamous cell carcinoma in South Asia, Southeast Asia, and diaspora populations globally.",
    link: null,
  },
  {
    rank: 8,
    name: "Family history",
    weight: "Modest",
    weightColor: "text-low",
    summary: "A first-degree relative with oral or head-and-neck cancer modestly raises risk.",
    detail:
      "Having a parent or sibling who developed oral or head-and-neck cancer increases your risk somewhat, likely through a combination of shared genetic susceptibility and shared environmental exposures. Family history alone is not considered a high-risk factor, but it strengthens the case for regular dental screenings.",
    link: null,
  },
  {
    rank: 9,
    name: "Infrequent dental visits",
    weight: "Indirect",
    weightColor: "text-low",
    summary: "Dentists are the primary first-line screeners for oral cancer.",
    detail:
      "Dentists routinely perform visual and physical checks for oral cancer signs during checkups. People who rarely see a dentist miss these routine screenings, which means early lesions can go undetected longer. This is not a direct biological cause, but it significantly increases the chance that a cancer is caught at a later, harder-to-treat stage.",
    link: "/find-care",
  },
];

export default function RiskFactorsPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <article className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
        <Link
          href="/learn"
          className="text-sm font-medium text-ink-soft hover:text-ink mb-6 inline-block"
        >
          ← Back to Learn
        </Link>
        <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
          Risk factors
        </span>
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4 leading-tight">
          Oral Cancer Risk Factors
        </h1>
        <p className="text-lg text-ink-soft leading-relaxed mb-10">
          Oral cancer has clear, well-understood causes. Most are modifiable.
          Understanding your specific risk factors is the first step toward doing
          something about them.
        </p>

        {/* Key callout */}
        <div className="bg-brand/5 border border-brand/20 rounded-2xl p-6 mb-12">
          <h2 className="font-serif text-xl text-ink mb-2">The two-factor rule</h2>
          <p className="text-ink-soft leading-relaxed text-sm">
            Tobacco and alcohol each independently raise oral cancer risk. Used
            together, their effects are{" "}
            <strong className="text-ink">synergistic, not additive</strong> — a
            heavy smoker who also drinks heavily can face a{" "}
            <strong className="text-ink">30-fold increase</strong> in risk
            compared to someone who does neither. If you use both, reducing or
            eliminating either one significantly lowers your risk.
          </p>
        </div>

        {/* Risk factor list */}
        <section className="mb-12 space-y-6">
          {riskFactors.map((rf) => (
            <div
              key={rf.name}
              className="bg-warm-dim border border-warm-dim rounded-2xl p-6"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-brand font-semibold shrink-0 w-6">
                    {String(rf.rank).padStart(2, "0")}
                  </span>
                  <h2 className="font-semibold text-ink text-lg">{rf.name}</h2>
                </div>
                <span className={`text-xs font-semibold shrink-0 ${rf.weightColor}`}>
                  {rf.weight}
                </span>
              </div>
              <p className="text-sm text-ink font-medium mb-2 ml-9">{rf.summary}</p>
              <p className="text-sm text-ink-soft leading-relaxed ml-9">{rf.detail}</p>
              {rf.link && (
                <div className="ml-9 mt-3">
                  <Link
                    href={rf.link}
                    className="text-sm text-brand hover:underline"
                  >
                    Learn more →
                  </Link>
                </div>
              )}
            </div>
          ))}
        </section>

        {/* Synergy section */}
        <section className="mb-12">
          <h2 className="font-serif text-3xl text-ink mb-4">
            How risk factors interact
          </h2>
          <p className="text-ink-soft leading-relaxed mb-4">
            Risk factors do not always operate independently. Tobacco and alcohol
            together are significantly more dangerous than either alone — both
            substances damage the same tissues, and alcohol may enhance the
            ability of tobacco carcinogens to penetrate the cells lining the
            mouth and throat.
          </p>
          <p className="text-ink-soft leading-relaxed mb-4">
            HPV-related oropharyngeal cancers follow a different pathway entirely
            — they are driven by viral integration into cell DNA rather than by
            chemical carcinogens. This is why HPV-related cancers tend to occur in
            younger, non-smoking adults. The HPV vaccine is currently the only
            preventive tool specifically targeting this pathway.
          </p>
          <p className="text-ink-soft leading-relaxed">
            Having multiple risk factors does not guarantee cancer, but it does
            strengthen the case for regular dental screenings and self-exams.
          </p>
        </section>

        {/* What you can do */}
        <section className="mb-12">
          <h2 className="font-serif text-3xl text-ink mb-5">
            What you can do about it
          </h2>
          <div className="space-y-3">
            {[
              [
                "Quit tobacco",
                "The single highest-impact change. Risk drops measurably within years of quitting.",
              ],
              [
                "Limit alcohol",
                "Risk scales with consumption. Reducing heavy use reduces risk.",
              ],
              [
                "Get the HPV vaccine",
                "Gardasil 9 is approved through age 45 and is highly effective against HPV-16 when given before exposure.",
              ],
              [
                "Protect your lips",
                "Use lip balm with SPF 30+ outdoors. Wear a wide-brimmed hat.",
              ],
              [
                "See a dentist regularly",
                "Dental exams include a visual oral cancer screening. Every visit is an opportunity for early detection.",
              ],
              [
                "Know the warning signs",
                "Any sore, patch, or lump that hasn't resolved in 2 weeks should be evaluated.",
              ],
            ].map(([title, desc]) => (
              <div
                key={title}
                className="flex gap-4 bg-warm-dim border border-warm-dim rounded-2xl p-5"
              >
                <span className="text-brand font-bold mt-0.5 shrink-0">✓</span>
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
                q: "What is the biggest risk factor for oral cancer?",
                a: "For oral cavity cancers, tobacco is the single biggest modifiable risk factor, responsible for about 75% of cases. For oropharyngeal cancers (base of tongue, tonsils, throat), HPV-16 has now surpassed tobacco as the leading cause in the US.",
              },
              {
                q: "Does alcohol increase the risk of oral cancer?",
                a: "Yes. Heavy alcohol use is an independent risk factor. The combination of tobacco and alcohol is especially dangerous — their effects are synergistic, and the combined risk can be 30 times higher than for someone who uses neither.",
              },
              {
                q: "Can you get oral cancer without smoking or drinking?",
                a: "Yes. HPV-related oropharyngeal cancers have been increasing in people who have never smoked or used tobacco. HPV-16 is now responsible for the majority of throat and tonsillar cancers in the US.",
              },
              {
                q: "Is oral cancer hereditary?",
                a: "Family history is a recognized but modest independent risk factor. Most oral cancers are driven by modifiable risk factors like tobacco, alcohol, and HPV rather than hereditary causes.",
              },
              {
                q: "At what age does oral cancer risk increase?",
                a: "Risk rises sharply after 55, with peak incidence in the 60s and 70s. However, HPV-related oropharyngeal cancers are increasingly diagnosed in adults in their 40s and 50s.",
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
          <strong className="text-ink">Sources:</strong> American Cancer Society,
          National Cancer Institute (NCI SEER), Oral Cancer Foundation, CDC HPV
          and Cancer, International Agency for Research on Cancer (IARC). This
          page is educational and does not constitute medical advice.
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            href="/screener"
            className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
          >
            Check your risk →
          </Link>
          <Link
            href="/learn/signs"
            className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            Warning signs
          </Link>
          <Link
            href="/learn/prevention"
            className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            How to prevent oral cancer
          </Link>
          <Link
            href="/learn/hpv"
            className="bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
          >
            HPV and oral cancer
          </Link>
        </div>
        <LearnReadNext currentHref="/learn/risk-factors" />
      </article>
    </>
  );
}
