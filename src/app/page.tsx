import Link from "next/link";
import HeroSection from "@/components/HeroSectionWide";
import AnimatedStats from "@/components/AnimatedStats";
import FadeUp from "@/components/FadeUp";

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "What is oral cancer?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Oral cancer refers to cancer that develops in any part of the mouth or throat, including the lips, tongue, gums, floor of the mouth, palate, and oropharynx. It is one of the most underdiagnosed cancers in the US, with over 54,000 new cases diagnosed each year. When caught early, the five-year survival rate is over 84%.",
      },
    },
    {
      "@type": "Question",
      name: "How common is oral cancer?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Oral and oropharyngeal cancers affect over 54,000 Americans each year and cause approximately 11,580 deaths annually — about one death every 50 minutes. Rates have been rising due to an increase in HPV-related throat cancers, which now outnumber tobacco-related cases in the oropharynx.",
      },
    },
    {
      "@type": "Question",
      name: "What are the early warning signs of oral cancer?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Early warning signs include a sore or ulcer in the mouth that doesn't heal after 2 weeks, a red or white patch on the gums, tongue, or lining of the mouth, a lump or thickening in the cheek, unexplained numbness or pain, and difficulty chewing or swallowing. Many early oral cancers are painless, which is why regular dental screenings matter.",
      },
    },
    {
      "@type": "Question",
      name: "How do I check for oral cancer at home?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "You can do a 2-minute self-exam at home using a mirror and good lighting. Check your lips, gums, tongue (top, sides, and underside), floor of the mouth, roof of the mouth, and throat. Look for any red or white patches, sores, lumps, or asymmetries. Anything that hasn't resolved after 2 weeks should be evaluated by a dentist.",
      },
    },
    {
      "@type": "Question",
      name: "Is OralCheck free to use?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes. OralCheck is completely free. No account is required, nothing is saved to a server, and there is no tracking of your answers. The screener takes about 2 minutes and provides a personalized risk summary based on published risk factors from the American Cancer Society, NCI, and Oral Cancer Foundation.",
      },
    },
  ],
};

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
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Hero — animated client component */}
      <HeroSection />

      {/* Stats — count-up on scroll */}
      <AnimatedStats />

      {/* Features */}
      <section className="max-w-6xl mx-auto px-5 py-20">
        <FadeUp>
          <div className="mb-10">
            <h2 className="font-serif text-3xl sm:text-4xl text-ink">
              Three things this tool does
            </h2>
          </div>
        </FadeUp>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map(({ title, description, href, cta }, i) => (
            <FadeUp key={href} delay={i * 0.1}>
              <Link
                href={href}
                className="group flex flex-col h-full p-7 rounded-2xl bg-white border border-warm-dim hover:border-brand/40 hover:shadow-md transition-all duration-200"
              >
                <h3 className="font-serif text-2xl text-ink mb-3 group-hover:text-brand transition-colors">
                  {title}
                </h3>
                <p className="text-ink-soft text-sm leading-relaxed mb-5 flex-1">
                  {description}
                </p>
                <span className="text-sm font-semibold text-brand">
                  {cta} →
                </span>
              </Link>
            </FadeUp>
          ))}
        </div>
      </section>

      {/* Blockquote */}
      <FadeUp>
        <section className="max-w-3xl mx-auto px-5 pb-16 text-center">
          <blockquote className="font-serif text-2xl sm:text-3xl text-ink leading-snug">
            &ldquo;Oral cancer is one of the few cancers where a routine visit
            that takes 2 minutes can change the outcome by decades.&rdquo;
          </blockquote>
        </section>
      </FadeUp>
    </div>
  );
}
