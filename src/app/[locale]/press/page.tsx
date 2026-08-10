import type { Metadata } from "next";
import Image from "next/image";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import Icon from "@/components/Icon";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "PressMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/press"),
  };
}

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": `${SITE_URL}#organization`,
  name: "OralCheck",
  url: SITE_URL,
  logo: `${SITE_URL}/logo.png`,
  description:
    "A free, private oral cancer risk screener. Ten questions, about two minutes, no account required.",
  founder: {
    "@type": "Person",
    name: "Ian Harris",
    affiliation: {
      "@type": "Organization",
      name: "University of Wisconsin-Madison",
    },
  },
  sameAs: ["https://www.instagram.com/oralcheckdotorg/"],
};

// Downloadable brand assets. Kept to what actually exists in /public so the
// page can't offer a broken link.
const ASSETS = [
  { file: "/logo.svg", labelKey: "assetLogoSvg", type: "SVG" },
  { file: "/logo.png", labelKey: "assetLogoPng", type: "PNG" },
  { file: "/icon-512.png", labelKey: "assetIcon", type: "PNG" },
] as const;

const PALETTE = [
  { name: "Deep teal", hex: "#0d7377" },
  { name: "Coral", hex: "#e8634a" },
  { name: "Ink", hex: "#0d1a1b" },
  { name: "Warm", hex: "#e8e4de" },
];

export default async function PressPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "PressPage" });

  const facts = t.raw("facts") as { label: string; value: string }[];

  return (
    <div className="max-w-4xl mx-auto px-5 py-10 sm:py-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <span className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
        <Icon name="press" size={13} weight="bold" />
        {t("tag")}
      </span>
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">{t("heading")}</h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10 max-w-2xl">
        {t("subheading")}
      </p>

      {/* Boilerplate — the paragraph a journalist can paste verbatim */}
      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("boilerplateHeading")}</h2>
        <p className="text-ink-soft leading-relaxed mb-4">{t("boilerplateShort")}</p>
        <p className="text-ink-soft leading-relaxed">{t("boilerplateLong")}</p>
      </section>

      {/* Fast facts */}
      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-5">{t("factsHeading")}</h2>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
          {facts.map((f) => (
            <div key={f.label} className="border-b border-warm-dim pb-3">
              <dt className="text-xs font-semibold uppercase tracking-wider text-ink-soft mb-1">
                {f.label}
              </dt>
              <dd className="text-ink leading-relaxed">{f.value}</dd>
            </div>
          ))}
        </dl>
      </section>

      {/* Founder */}
      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-5">{t("founderHeading")}</h2>
        <div className="flex items-center gap-4 mb-5">
          <Image
            src="/ian-harris.jpg"
            alt="Ian Harris, founder of OralCheck"
            width={200}
            height={200}
            className="w-20 h-20 rounded-2xl object-cover object-[center_25%] border border-warm-dim shrink-0"
          />
          <div>
            <div className="font-serif text-xl text-ink">{t("founderName")}</div>
            <div className="text-sm text-ink-soft">{t("founderTitle")}</div>
          </div>
        </div>
        <p className="text-ink-soft leading-relaxed">{t("founderBio")}</p>
      </section>

      {/* Brand assets */}
      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-2">{t("assetsHeading")}</h2>
        <p className="text-sm text-ink-soft leading-relaxed mb-5">{t("assetsBody")}</p>
        <div className="flex flex-wrap gap-3 mb-7">
          {ASSETS.map((a) => (
            <a
              key={a.file}
              href={a.file}
              download
              className="inline-flex items-center gap-2 bg-warm border border-warm-dim rounded-xl px-4 py-2.5 text-sm font-medium text-ink hover:border-brand hover:text-brand transition-colors"
            >
              <Icon name="download" size={16} />
              {t(a.labelKey)}
              <span className="text-ink-soft text-xs font-mono">{a.type}</span>
            </a>
          ))}
        </div>

        <h3 className="font-semibold text-ink mb-3 text-sm">{t("paletteHeading")}</h3>
        <div className="flex flex-wrap gap-3">
          {PALETTE.map((c) => (
            <div key={c.hex} className="flex items-center gap-2.5">
              <span
                className="w-9 h-9 rounded-lg border border-warm-dim shrink-0"
                style={{ backgroundColor: c.hex }}
                aria-hidden
              />
              <div className="leading-tight">
                <div className="text-sm text-ink">{c.name}</div>
                <div className="text-xs text-ink-soft font-mono">{c.hex}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Contact */}
      <section className="bg-brand-soft border border-brand/15 rounded-2xl p-6 sm:p-8">
        <h2 className="font-serif text-2xl text-ink mb-2">{t("contactHeading")}</h2>
        <p className="text-ink-soft leading-relaxed mb-5">{t("contactBody")}</p>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/about#feedback"
            className="inline-flex items-center gap-2 bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
          >
            <Icon name="email" size={17} />
            {t("contactCta")}
          </Link>
          <a
            href="https://www.instagram.com/oralcheckdotorg/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-warm text-ink font-semibold px-6 py-3 rounded-full border border-warm-dim hover:border-brand transition-colors"
          >
            {t("contactInstagram")}
          </a>
        </div>
      </section>
    </div>
  );
}
