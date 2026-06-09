import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy | OralCheck",
  description:
    "OralCheck does not collect your name, email, or any identifying information. Your screener answers are not stored.",
};

const sections = [
  {
    heading: "What we collect",
    body: "OralCheck does not collect your name, email address, or any information that identifies you. No account is required to use the screener.",
  },
  {
    heading: "Your screener answers",
    body: "Your answers are used to calculate your result and are not stored on our servers. Nothing you enter is saved after your session ends.",
  },
  {
    heading: "Analytics",
    body: "This site uses Google Analytics to understand how people find and use OralCheck — which pages are visited, how long sessions last, and what country visitors are from. Google Analytics collects anonymous usage data including your approximate location, browser type, and device. It does not receive your screener answers. You can opt out at tools.google.com/dlpage/gaoptout.",
    link: {
      label: "Google Analytics opt-out →",
      href: "https://tools.google.com/dlpage/gaoptout",
    },
  },
  {
    heading: "Cookies",
    body: "Google Analytics sets cookies to distinguish visits. No other cookies are used.",
  },
  {
    heading: "Third parties",
    body: "OralCheck does not sell, share, or transfer your data to any third party for marketing or advertising purposes.",
  },
];

export default function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto px-5 py-12 sm:py-20">
      <div className="mb-10">
        <Link href="/" className="text-sm text-brand hover:underline">
          ← OralCheck
        </Link>
      </div>

      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">Privacy</h1>
      <p className="text-ink-soft text-lg leading-relaxed mb-12 max-w-2xl">
        OralCheck is designed to be private by default. Here is exactly what is and is not
        collected when you use this site.
      </p>

      <div className="space-y-10 max-w-2xl mb-16">
        {sections.map((s) => (
          <section key={s.heading}>
            <h2 className="font-serif text-xl text-ink mb-2">{s.heading}</h2>
            <p className="text-ink-soft text-sm leading-relaxed">{s.body}</p>
            {s.link && (
              <a
                href={s.link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block text-brand hover:underline text-sm mt-2"
              >
                {s.link.label}
              </a>
            )}
          </section>
        ))}
      </div>

      <div className="border-t border-warm-dim pt-10 space-y-4 max-w-2xl">
        <p className="text-xs text-ink-soft leading-relaxed">
          <strong className="text-ink">Disclaimer.</strong> OralCheck is not a medical diagnosis.
          It is an educational tool. Consult a qualified clinician about any symptom or concern.
        </p>
        <p className="text-xs text-ink-soft leading-relaxed">
          Screening logic informed by ACS, NCI, and Oral Cancer Foundation clinical guidelines.
        </p>
        <p className="text-xs text-ink-soft mt-4">Last updated June 2026.</p>
      </div>
    </div>
  );
}
