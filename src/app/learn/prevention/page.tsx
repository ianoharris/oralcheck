import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "How to Prevent Oral Cancer | OralCheck",
  description:
    "Six evidence-based ways to lower your oral cancer risk: quit tobacco, limit alcohol, get the HPV vaccine, protect your lips, and get regular dental screenings.",
  alternates: { canonical: "https://oralcheck.org/learn/prevention" },
};

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      "@id": `${SITE_URL}/learn/prevention#webpage`,
      url: `${SITE_URL}/learn/prevention`,
      name: "How to Prevent Oral Cancer",
      description:
        "Six evidence-based ways to lower your oral cancer risk: quit tobacco, limit alcohol, get the HPV vaccine, protect your lips, and get regular dental screenings.",
      about: {
        "@type": "MedicalCondition",
        name: "Oral Cancer",
      },
      lastReviewed: "2026-04-23",
    },
    {
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
        { "@type": "ListItem", position: 2, name: "Learn", item: `${SITE_URL}/learn` },
        { "@type": "ListItem", position: 3, name: "How to Prevent Oral Cancer", item: `${SITE_URL}/learn/prevention` },
      ],
    },
    {
      "@type": "FAQPage",
      "@id": `${SITE_URL}/learn/prevention#faq`,
      mainEntity: [
        {
          "@type": "Question",
          name: "Can oral cancer be prevented?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Many cases of oral cancer are preventable. The biggest modifiable risk factors are tobacco use, heavy alcohol consumption, and HPV infection — all of which can be addressed. Avoiding tobacco is the single most impactful step. Regular dental checkups also catch early changes before they become cancer.",
          },
        },
        {
          "@type": "Question",
          name: "Does quitting tobacco lower oral cancer risk?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes, significantly. Tobacco use — including cigarettes, cigars, pipes, chewing tobacco, and snuff — is the leading cause of traditional oral cancers. Risk begins to drop within a few years of quitting, and long-term ex-smokers approach the risk level of people who never smoked.",
          },
        },
        {
          "@type": "Question",
          name: "How does the HPV vaccine help prevent oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The HPV vaccine (Gardasil 9) protects against HPV-16 and HPV-18, the strains responsible for the majority of HPV-related oropharyngeal cancers. It is FDA-approved for people ages 9 through 45 and is most effective before exposure to HPV. Vaccination does not treat an existing HPV infection, but population data already shows a reduction in HPV-related cancers in vaccinated groups.",
          },
        },
        {
          "@type": "Question",
          name: "How often should I get an oral cancer screening?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "A routine dental checkup includes a brief oral cancer screening at no extra cost. For most people, this means once or twice a year. People with elevated risk factors — tobacco use, heavy drinking, or a history of HPV — may benefit from more frequent screenings. Talk to your dentist about the right schedule for you.",
          },
        },
        {
          "@type": "Question",
          name: "Does sun exposure cause oral cancer?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes, but specifically for lip cancer rather than cancers inside the mouth. Chronic sun exposure is a leading risk factor for cancer of the lower lip. Wearing SPF lip balm and a wide-brimmed hat when outdoors significantly reduces this risk. People who work outdoors are at higher risk.",
          },
        },
      ],
    },
  ],
};

const steps = [
  {
    number: "01",
    heading: "Quit tobacco — any form",
    body: "Tobacco use is the single biggest modifiable risk factor for oral cancer. That includes cigarettes, cigars, pipes, chewing tobacco, and snuff. The good news: risk drops measurably within a few years of quitting, and long-term ex-users approach the risk level of those who never used tobacco.",
    cta: null,
    color: "#e8634a",
  },
  {
    number: "02",
    heading: "Limit alcohol — especially with tobacco",
    body: "Heavy alcohol use is an independent risk factor, but the combination of tobacco and alcohol doesn't just add the risks — it multiplies them. If you drink, keeping to moderate levels (up to 1 drink/day for women, 2 for men) meaningfully lowers your risk compared to heavy use.",
    cta: null,
    color: "#0d7377",
  },
  {
    number: "03",
    heading: "Get vaccinated against HPV",
    body: "Gardasil 9 protects against HPV-16 and HPV-18 — the strains behind most HPV-related throat cancers. It's FDA-approved for ages 9–45 and most effective before HPV exposure. Adults who weren't vaccinated as teens can still benefit. Ask your doctor if you're a candidate.",
    cta: { label: "Learn more about HPV and oral cancer →", href: "/learn/hpv" },
    color: "#0d7377",
  },
  {
    number: "04",
    heading: "Get regular dental checkups",
    body: "A routine dental visit includes a 2-minute oral cancer screening — your dentist checks your lips, gums, tongue, cheeks, palate, and throat. Most early-stage oral cancers are found this way. For people who skip dental care, cancers are more often caught at later stages when outcomes are worse.",
    cta: { label: "Find dental care near you →", href: "/find-care" },
    color: "#0d7377",
  },
  {
    number: "05",
    heading: "Protect your lips from the sun",
    body: "Chronic sun exposure is a leading cause of cancer of the lower lip — a risk that's easy to overlook. Wearing SPF lip balm (SPF 30+) and a wide-brimmed hat when outdoors makes a real difference, especially for people who work outside. Lip cancer is highly treatable when caught early.",
    cta: null,
    color: "#0d7377",
  },
  {
    number: "06",
    heading: "Do a monthly self-exam",
    body: "Prevention isn't just about avoiding risk — it's also about catching changes early. A monthly 2-minute self-exam of your mouth and throat means you notice anything unusual before it becomes serious. Most people have never done one.",
    cta: { label: "Learn how to do a self-exam →", href: "/learn/self-exam" },
    color: "#0d7377",
  },
];

const faqs = [
  {
    q: "Can oral cancer be prevented?",
    a: "Many cases are preventable. The biggest modifiable risk factors are tobacco use, heavy alcohol consumption, and HPV infection — all of which can be addressed. Avoiding tobacco is the single most impactful step. Regular dental checkups also catch early changes before they become cancer.",
  },
  {
    q: "Does quitting tobacco lower oral cancer risk?",
    a: "Yes, significantly. Tobacco use is the leading cause of traditional oral cancers. Risk begins to drop within a few years of quitting, and long-term ex-smokers approach the risk level of people who never smoked.",
  },
  {
    q: "How does the HPV vaccine help prevent oral cancer?",
    a: "The HPV vaccine (Gardasil 9) protects against HPV-16 and HPV-18 — the strains behind most HPV-related throat cancers. It's FDA-approved for ages 9–45. Population data already shows reduced HPV-related cancer rates in vaccinated groups.",
  },
  {
    q: "How often should I get an oral cancer screening?",
    a: "For most people, once or twice a year at a routine dental visit is enough — the screening is included at no extra cost. People with elevated risk factors (tobacco, heavy drinking, HPV history) may benefit from more frequent checkups.",
  },
  {
    q: "Does sun exposure cause oral cancer?",
    a: "Yes, specifically for lip cancer. Chronic sun exposure is a leading cause of lower lip cancer. SPF lip balm and a wide-brimmed hat when outdoors significantly reduce this risk, especially for people who work outdoors.",
  },
];

export default function PreventionPage() {
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
          Prevention
        </span>
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4 leading-tight">
          How to Prevent Oral Cancer
        </h1>
        <p className="text-lg text-ink-soft leading-relaxed mb-10">
          Oral cancer isn't entirely preventable — some risk factors, like age
          and genetics, aren't in your control. But the biggest ones are. Here's
          what the evidence actually supports.
        </p>

        {/* Steps */}
        <div className="space-y-5 mb-14">
          {steps.map((step) => (
            <div
              key={step.number}
              className="bg-white border border-warm-dim rounded-2xl p-6 sm:p-7"
            >
              <div
                className="font-mono text-xs font-semibold mb-2"
                style={{ color: step.color }}
              >
                {step.number}
              </div>
              <h2 className="font-serif text-2xl text-ink mb-3 leading-snug">
                {step.heading}
              </h2>
              <p className="text-ink-soft leading-relaxed text-sm mb-3">
                {step.body}
              </p>
              {step.cta && (
                <Link
                  href={step.cta.href}
                  className="text-sm font-semibold text-brand hover:underline"
                >
                  {step.cta.label}
                </Link>
              )}
            </div>
          ))}
        </div>

        {/* Callout: what you can't control */}
        <div className="bg-warm-dim/50 border border-warm-dim rounded-2xl p-6 mb-12">
          <h2 className="font-serif text-xl text-ink mb-2">
            What you can't fully control
          </h2>
          <p className="text-ink-soft text-sm leading-relaxed">
            Age, sex assigned at birth, family history, and immune status all
            affect oral cancer risk and aren't modifiable. If you have multiple
            non-modifiable risk factors, that's a reason to be more diligent
            about the ones you can control — and to talk to your dentist about
            your screening schedule.
          </p>
        </div>

        {/* FAQ */}
        <section className="mb-12">
          <h2 className="font-serif text-3xl text-ink mb-6">
            Common questions
          </h2>
          <div className="space-y-4">
            {faqs.map((faq) => (
              <details
                key={faq.q}
                className="bg-white border border-warm-dim rounded-2xl group"
              >
                <summary className="flex items-center justify-between px-6 py-4 cursor-pointer list-none font-semibold text-ink">
                  {faq.q}
                  <span className="ml-4 flex-shrink-0 text-brand text-lg font-light group-open:rotate-45 transition-transform">
                    +
                  </span>
                </summary>
                <p className="px-6 pb-5 text-ink-soft leading-relaxed text-sm">
                  {faq.a}
                </p>
              </details>
            ))}
          </div>
        </section>

        <div className="mt-4 p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed mb-8">
          <strong className="text-ink">Sources:</strong> American Cancer Society,
          National Cancer Institute, CDC, Oral Cancer Foundation, World Health
          Organization. This page is educational and does not constitute medical
          advice.
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            href="/screener"
            className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
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
    </>
  );
}
