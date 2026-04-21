import type { Metadata, Viewport } from "next";
import { DM_Serif_Display, Source_Sans_3, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import ServiceWorkerRegistration from "@/components/ServiceWorkerRegistration";
import { GoogleAnalytics } from "@next/third-parties/google";
import { Analytics } from "@vercel/analytics/next";

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

const SITE_URL = "https://oralcheck.vercel.app";

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
        "Answer 10 questions to understand your oral cancer risk factors. Free, private, and takes 2 minutes.",
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
      lastReviewed: "2025-01-01",
      reviewedBy: {
        "@type": "Organization",
        name: "OralCheck",
      },
    },
    {
      "@type": "Organization",
      "@id": `${SITE_URL}/#organization`,
      url: SITE_URL,
      name: "OralCheck",
      description:
        "A free educational tool to help people understand oral cancer risk and find affordable care.",
      sameAs: ["https://github.com/ianoharris/oralcheck"],
    },
  ],
};

export const metadata: Metadata = {
  title: "OralCheck — 2 Minutes Could Save Your Life",
  description:
    "Free, private oral cancer risk screener. Understand your risk, learn the signs, and find care near you.",
  metadataBase: new URL(SITE_URL),
  openGraph: {
    title: "OralCheck — Free Oral Cancer Risk Screener",
    description:
      "Answer 10 questions to understand your oral cancer risk. Free, private, takes 2 minutes.",
    url: SITE_URL,
    siteName: "OralCheck",
    type: "website",
  },
  alternates: {
    canonical: SITE_URL,
  },
};

export const viewport: Viewport = {
  themeColor: "#0d7377",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${dmSerif.variable} ${sourceSans.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="min-h-full flex flex-col">
        <ServiceWorkerRegistration />
        <Nav />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
      <GoogleAnalytics gaId="G-9DPR4C91FM" />
      <Analytics />
    </html>
  );
}
