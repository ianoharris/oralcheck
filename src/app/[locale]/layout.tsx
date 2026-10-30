import type { Metadata, Viewport } from "next";
import { DM_Serif_Display, Source_Sans_3, JetBrains_Mono } from "next/font/google";
import { notFound } from "next/navigation";
import { NextIntlClientProvider, hasLocale } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import "../globals.css";
import { routing } from "@/i18n/routing";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import ServiceWorkerRegistration from "@/components/ServiceWorkerRegistration";
import { GoogleAnalytics } from "@next/third-parties/google";
import { Analytics } from "@vercel/analytics/next";

const GA_ID = "G-9DPR4C91FM";

const dmSerif = DM_Serif_Display({
  variable: "--font-dm-serif",
  subsets: ["latin"],
  weight: "400",
});

const sourceSans = Source_Sans_3({
  variable: "--font-source-sans",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
});

const SITE_URL = "https://oralcheck.org";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": `${SITE_URL}/#website`,
      url: SITE_URL,
      name: "OralCheck",
      description:
        "Free, private oral cancer risk screener. Understand your risk, learn the signs, and find care near you.",
    },
    {
      "@type": "MedicalWebPage",
      "@id": `${SITE_URL}/#webpage`,
      url: SITE_URL,
      name: "OralCheck — Free Oral Cancer Risk Screener",
      description:
        "A short set of questions to understand your oral cancer risk factors. Free, private, and takes 2 minutes.",
      about: {
        "@type": "MedicalCondition",
        name: "Oral Cancer",
        alternateName: ["Oral Cavity Cancer", "Oropharyngeal Cancer"],
        description:
          "Oral cancer refers to cancer that develops in any part of the mouth or throat. Risk factors include tobacco use, alcohol consumption, HPV infection, and sun exposure.",
        associatedAnatomy: {
          "@type": "AnatomicalStructure",
          name: "Oral Cavity",
        },
        recognizingAuthority: {
          "@type": "Organization",
          name: "American Cancer Society",
          url: "https://www.cancer.org",
        },
        relevantSpecialty: {
          "@type": "MedicalSpecialty",
          name: "Dentistry",
        },
        possibleTreatment: {
          "@type": "MedicalTherapy",
          name: "Early detection through routine oral cancer screening",
        },
      },
      audience: {
        "@type": "MedicalAudience",
        audienceType: "Patient",
      },
      medicalAudience: {
        "@type": "MedicalAudience",
        audienceType: "Patient",
      },
      datePublished: "2024-12-01",
      lastReviewed: "2026-06-12",
      reviewedBy: {
        "@type": "Person",
        name: "Ian Harris",
        affiliation: {
          "@type": "Organization",
          name: "University of Wisconsin-Madison",
        },
        url: `${SITE_URL}/about`,
      },
    },
    {
      "@type": "Organization",
      "@id": `${SITE_URL}/#organization`,
      url: SITE_URL,
      name: "OralCheck",
      description:
        "A free educational tool to help people understand oral cancer risk and find affordable care.",
      sameAs: [
        "https://github.com/ianoharris/oralcheck",
        "https://www.instagram.com/oralcheckdotorg",
      ],
    },
  ],
};

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

type Props = {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Meta" });
  const path = locale === routing.defaultLocale ? "" : `/${locale}`;

  return {
    title: {
      default: t("siteTitle"),
      template: "%s | OralCheck",
    },
    description: t("siteDescription"),
    metadataBase: new URL(SITE_URL),
    openGraph: {
      title: t("siteTitle"),
      description: t("ogDescription"),
      url: `${SITE_URL}${path}`,
      siteName: "OralCheck",
      type: "website",
      locale: locale === "es" ? "es_ES" : "en_US",
    },
    alternates: {
      canonical: `${SITE_URL}${path}`,
      languages: {
        en: SITE_URL,
        es: `${SITE_URL}/es`,
        "x-default": SITE_URL,
      },
    },
  };
}

export const viewport: Viewport = {
  themeColor: "#0d7377",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default async function RootLayout({ children, params }: Props) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) notFound();

  // Enables static rendering for this request's locale.
  setRequestLocale(locale);

  return (
    <html
      lang={locale}
      className={`${dmSerif.variable} ${sourceSans.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <head>
        {/* Keeps development and Ian's own visits out of GA. Dev servers
            shared the live property: 376 of 1,321 pageviews in the 90 days to
            30 Oct came from localhost, 242 of them one /pt tab on 21 Oct, which
            outnumbered every real visitor that month. So only oralcheck.org
            reports, and a browser opened once with ?notrack=1 stops counting
            itself on the live site too (?notrack=0 undoes it). It has to run
            before gtag loads, which is why it is inline here. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `try{var q=new URLSearchParams(location.search).get("notrack");if(q==="1")localStorage.setItem("oralcheck:notrack","1");if(q==="0")localStorage.removeItem("oralcheck:notrack");if(localStorage.getItem("oralcheck:notrack")==="1"||!/(^|\\.)oralcheck\\.org$/.test(location.hostname))window["ga-disable-${GA_ID}"]=true}catch(e){}`,
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="min-h-full flex flex-col">
        <NextIntlClientProvider>
          <ServiceWorkerRegistration />
          <Nav />
          <main className="flex-1">{children}</main>
          <Footer />
        </NextIntlClientProvider>
      </body>
      <GoogleAnalytics gaId={GA_ID} />
      <Analytics />
    </html>
  );
}
