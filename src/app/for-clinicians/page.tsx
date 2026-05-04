import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import PrintableFlyer from "./PrintableFlyer";
import EmbedBlock from "./EmbedBlock";

export const metadata: Metadata = {
  title: "For Dental Professionals | OralCheck",
  description:
    "Help your patients take 2 minutes that could save their life. Free printable waiting room flyer, QR code, and patient education materials — no login required.",
  alternates: { canonical: "https://oralcheck.org/for-clinicians" },
};

const howToUse = [
  {
    step: "1",
    title: "Print the flyer",
    desc: "Customize it with your practice name below, then print it. Post it in your waiting room, exam rooms, or front desk.",
  },
  {
    step: "2",
    title: "Share the link",
    desc: "Text or email oralcheck.org to patients before appointments. It takes 2 minutes and works on any phone.",
  },
  {
    step: "3",
    title: "Use it as a conversation starter",
    desc: "When a patient flags elevated risk, it opens the door for a clinical oral exam and documentation.",
  },
];

const whyPoints = [
  {
    icon: "🔒",
    title: "Zero PHI collected",
    desc: "Answers never leave the patient's device. No HIPAA concerns, no data liability.",
  },
  {
    icon: "✓",
    title: "Evidence-based risk factors",
    desc: "Scoring logic draws from ACS, NCI, and Oral Cancer Foundation clinical guidelines.",
  },
  {
    icon: "⚡",
    title: "No setup, no login",
    desc: "Send a link or hang a QR code. Nothing to install, nothing to manage.",
  },
  {
    icon: "🆓",
    title: "Free — permanently",
    desc: "There is no paid tier. No vendor relationship to manage.",
  },
];

export default function ForCliniciansPage() {
  return (
    <div className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      {/* Hero */}
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        For Dental Professionals
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10">
        A free tool you can put in your waiting room today. Patients take a
        2-minute private risk check on their phone — no login, no data collected,
        no cost.
      </p>

      {/* Why use it */}
      <section className="bg-white rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-5">Why OralCheck</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {whyPoints.map((p) => (
            <div key={p.title} className="flex gap-3 items-start">
              <span className="text-xl leading-none mt-0.5">{p.icon}</span>
              <div>
                <div className="font-semibold text-ink text-sm">{p.title}</div>
                <div className="text-ink-soft text-sm leading-relaxed mt-0.5">{p.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How to use */}
      <section className="bg-white rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-5">How to use it</h2>
        <div className="space-y-5">
          {howToUse.map((item) => (
            <div key={item.step} className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full bg-brand text-white font-bold text-sm flex items-center justify-center flex-shrink-0">
                {item.step}
              </div>
              <div>
                <div className="font-semibold text-ink">{item.title}</div>
                <div className="text-ink-soft text-sm leading-relaxed mt-0.5">{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Disclaimer note */}
      <section className="bg-accent/10 border border-accent/20 rounded-2xl p-5 mb-10">
        <p className="text-sm text-ink leading-relaxed">
          <strong>Important:</strong> OralCheck is an educational awareness tool —
          not a diagnostic instrument. It does not replace a clinical oral cancer
          exam. Encourage any patient with concerning symptoms or an elevated
          screen result to schedule a full clinical evaluation.
        </p>
      </section>

      {/* Embed code */}
      <EmbedBlock />

      {/* Flyer section */}
      <div className="mb-2">
        <h2 className="font-serif text-3xl text-ink mb-2">Waiting room flyer</h2>
        <p className="text-ink-soft mb-8">
          Recreated from the official OralCheck poster. Customize with your
          practice name and print — letter size, portrait.
        </p>
        <Suspense fallback={<div className="h-32 bg-warm-dim rounded-2xl animate-pulse" />}>
          <PrintableFlyer />
        </Suspense>
      </div>

      {/* Bottom links */}
      <div className="mt-12 pt-8 border-t border-warm-dim flex flex-wrap gap-3">
        <Link
          href="/screener"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors text-sm"
        >
          Preview the screener →
        </Link>
        <Link
          href="/about#feedback"
          className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full border border-warm-dim transition-colors text-sm"
        >
          Contact us
        </Link>
      </div>
    </div>
  );
}
