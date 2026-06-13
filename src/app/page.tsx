import type { Metadata } from "next";
import Link from "next/link";
import HeroSectionPhoto from "@/components/HeroSectionPhoto";
import AnimatedStats from "@/components/AnimatedStats";
import FadeUp from "@/components/FadeUp";
import LogoMarquee from "@/components/LogoMarquee";
import InstagramFeed from "@/components/InstagramFeed";

export const metadata: Metadata = {
  title: { absolute: "OralCheck | Free Oral Cancer Risk Screener" },
  description:
    "Answer 10 questions to understand your oral cancer risk. Free, private, takes 2 minutes. Based on ACS, NCI, and Oral Cancer Foundation risk data.",
  alternates: { canonical: "https://oralcheck.org" },
  openGraph: {
    title: "OralCheck | Free Oral Cancer Risk Screener",
    description:
      "Answer 10 questions to understand your oral cancer risk. Free, private, takes 2 minutes.",
    url: "https://oralcheck.org",
    siteName: "OralCheck",
    type: "website",
  },
};

const SITE_URL = "https://oralcheck.org";

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
      <h1 className="sr-only">Free Oral Cancer Risk Screener</h1>

      {/* Hero */}
      <HeroSectionPhoto />

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
                className="group flex flex-col h-full p-7 rounded-2xl bg-warm-dim border border-warm-dim hover:border-brand/40 hover:shadow-md transition-all duration-200"
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

      {/* Logo marquee */}
      <LogoMarquee />

      {/* Instagram feed */}
      {process.env.NEXT_PUBLIC_BEHOLD_WIDGET_ID && (
        <section className="max-w-6xl mx-auto px-5 py-20">
          <FadeUp>
            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8">
              <div>
                <p className="text-xs font-semibold tracking-widest text-brand uppercase mb-2">
                  Follow along
                </p>
                <h2 className="font-serif text-3xl sm:text-4xl text-ink">
                  @oralcheckdotorg
                </h2>
              </div>
              <a
                href="https://www.instagram.com/oralcheckdotorg"
                target="_blank"
                rel="noopener noreferrer"
                className="self-start sm:self-auto border border-brand text-brand hover:bg-brand hover:text-white font-semibold px-5 py-2.5 rounded-full text-sm transition-colors"
              >
                Follow on Instagram →
              </a>
            </div>
          </FadeUp>
          <InstagramFeed widgetId={process.env.NEXT_PUBLIC_BEHOLD_WIDGET_ID} />
        </section>
      )}
    </div>
  );
}
