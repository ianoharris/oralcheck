import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy | OralCheck",
  description:
    "OralCheck does not collect your name, email, or any identifying information. Your screener answers are not stored.",
};

const sections = [
  {
    heading: "No personal information collected",
    body: "OralCheck does not collect your name, email address, or any information that identifies you. No account is required to use the screener.",
  },
  {
    heading: "Screener answers stay on your device",
    body: "Your answers are used to calculate your result and are not stored on our servers. Nothing you enter is saved after your session ends.",
  },
  {
    heading: "Google Analytics",
    body: "This site uses Google Analytics to understand how people find and use OralCheck — which pages are visited, how long sessions last, and what country visitors are from. Google Analytics collects anonymous usage data including your approximate location, browser type, and device. It does not receive your screener answers.",
    link: {
      label: "Opt out of Google Analytics →",
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
      <p className="text-ink-soft text-lg leading-relaxed mb-10 max-w-2xl">
        OralCheck is private by design. Here is exactly what is and is not collected when you use this site.
      </p>

      {/* Summary callout */}
      <div className="bg-brand-soft border border-brand/20 rounded-2xl px-6 py-5 mb-14 max-w-2xl">
        <p className="text-sm font-semibold text-brand mb-3">The short version</p>
        <ul className="space-y-1.5 text-sm text-ink">
          {[
            "No name, email, or identifying information collected",
            "Screener answers are never stored — they disappear when you close the page",
            "Google Analytics tracks anonymous usage only (pages visited, country, device)",
            "No data is sold or shared with third parties",
          ].map((item) => (
            <li key={item} className="flex items-start gap-2">
              <span className="text-brand mt-0.5 flex-shrink-0">✓</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Sections */}
      <div className="max-w-2xl divide-y divide-warm-dim mb-14">
        {sections.map((s) => (
          <section key={s.heading} className="py-8 first:pt-0">
            <h2 className="font-serif text-xl text-ink mb-3">{s.heading}</h2>
            <p className="text-ink-soft text-sm leading-relaxed">{s.body}</p>
            {s.link && (
              <a
                href={s.link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block text-brand hover:underline text-sm mt-3"
              >
                {s.link.label}
              </a>
            )}
          </section>
        ))}

        <section className="py-8">
          <h2 className="font-serif text-xl text-ink mb-3">Contact</h2>
          <p className="text-ink-soft text-sm leading-relaxed">
            Questions about this policy? Email{" "}
            <a href="mailto:hello@oralcheck.org" className="text-brand hover:underline">
              hello@oralcheck.org
            </a>
          </p>
        </section>
      </div>

      {/* Disclaimer */}
      <div className="border-t border-warm-dim pt-8 max-w-2xl space-y-2">
        <p className="text-xs text-ink-soft leading-relaxed">
          <strong className="text-ink">Disclaimer.</strong> OralCheck is not a medical diagnosis.
          It is an educational tool. Consult a qualified clinician about any symptom or concern.
        </p>
        <p className="text-xs text-ink-soft leading-relaxed">
          Screening logic informed by ACS, NCI, and Oral Cancer Foundation clinical guidelines.
        </p>
        <p className="text-xs text-ink-soft pt-2">Last updated June 2026.</p>
      </div>
    </div>
  );
}
