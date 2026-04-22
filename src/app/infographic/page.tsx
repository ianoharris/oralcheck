"use client";

import Link from "next/link";

export default function InfographicPage() {
  return (
    <>
      <style>{`
        @media print {
          nav, footer, #controls { display: none !important; }
          body { background: white !important; }
          #infographic { box-shadow: none !important; margin: 0 !important; max-width: 100% !important; }
        }
      `}</style>

      <div className="max-w-3xl mx-auto px-5 py-10 sm:py-14">

        {/* Page controls — hidden on print */}
        <div id="controls" className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="font-serif text-3xl text-ink">Infographic</h1>
            <p className="text-ink-soft text-sm mt-1">Print, screenshot, or share on social media.</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => window.print()}
              className="bg-brand hover:bg-brand-dark text-white font-semibold px-5 py-2.5 rounded-full text-sm transition-colors"
            >
              Print
            </button>
            <Link
              href="/qr"
              className="bg-white hover:bg-warm-dim text-ink font-semibold px-5 py-2.5 rounded-full text-sm transition-colors border border-warm-dim"
            >
              Get QR code
            </Link>
          </div>
        </div>

        {/* Infographic card */}
        <div
          id="infographic"
          style={{ fontFamily: "Georgia, 'Times New Roman', serif" }}
          className="bg-white rounded-3xl overflow-hidden shadow-sm border border-warm-dim"
        >
          {/* Header */}
          <div style={{ background: "#0d7377" }} className="px-10 py-8 text-white">
            <div className="flex items-center gap-3 mb-5">
              <svg viewBox="0 0 512 512" width="40" height="40">
                <rect width="512" height="512" rx="112" fill="white" fillOpacity="0.15"/>
                <circle cx="256" cy="256" r="128" fill="none" stroke="white" strokeWidth="32"/>
                <circle cx="380" cy="168" r="36" fill="#e8634a"/>
              </svg>
              <span style={{ fontFamily: "Georgia, serif", fontSize: 22, fontWeight: 700, letterSpacing: "-0.3px" }}>
                OralCheck
              </span>
            </div>
            <h2 style={{ fontSize: 32, fontWeight: 700, lineHeight: 1.2, margin: 0 }}>
              Know Your Oral Cancer Risk
            </h2>
            <p style={{ fontSize: 16, opacity: 0.85, marginTop: 8, fontFamily: "system-ui, sans-serif", fontWeight: 400 }}>
              Oral cancer is one of the most preventable — and most overlooked — cancers in the US.
            </p>
          </div>

          {/* Stat row */}
          <div className="grid grid-cols-3 divide-x divide-warm-dim border-b border-warm-dim">
            {[
              { stat: "54,000+", label: "Americans diagnosed yearly" },
              { stat: "84%", label: "Survival rate when caught early" },
              { stat: "2 min", label: "To check your risk at oralcheck.org" },
            ].map((s) => (
              <div key={s.stat} className="px-6 py-6 text-center">
                <div style={{ fontSize: 30, fontWeight: 700, color: "#0d7377", lineHeight: 1 }}>
                  {s.stat}
                </div>
                <div style={{ fontSize: 12, fontFamily: "system-ui, sans-serif", color: "#6b6b6b", marginTop: 6, lineHeight: 1.4 }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>

          {/* Two columns */}
          <div className="grid grid-cols-1 sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x divide-warm-dim">

            {/* Risk factors */}
            <div className="px-8 py-7">
              <h3 style={{ fontSize: 14, fontFamily: "system-ui, sans-serif", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "#e8634a", marginBottom: 14 }}>
                Main risk factors
              </h3>
              <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
                {[
                  ["🚬", "Tobacco use (any form)"],
                  ["🍷", "Heavy alcohol use"],
                  ["☀️", "Prolonged sun exposure (lips)"],
                  ["🦠", "HPV infection"],
                  ["👨‍👩‍👦", "Family history of oral cancer"],
                  ["🦷", "Infrequent dental visits"],
                ].map(([icon, label]) => (
                  <li key={label} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10, fontFamily: "system-ui, sans-serif", fontSize: 14, color: "#2d2d2d" }}>
                    <span style={{ fontSize: 18, flexShrink: 0 }}>{icon}</span>
                    {label}
                  </li>
                ))}
              </ul>
            </div>

            {/* Warning signs */}
            <div className="px-8 py-7">
              <h3 style={{ fontSize: 14, fontFamily: "system-ui, sans-serif", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "#0d7377", marginBottom: 14 }}>
                Warning signs
              </h3>
              <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
                {[
                  "Red or white patches in the mouth",
                  "A sore that doesn't heal in 2 weeks",
                  "A lump or thickening in the cheek",
                  "Unexplained numbness or pain",
                  "Difficulty chewing or swallowing",
                  "Persistent hoarseness",
                ].map((sign) => (
                  <li key={sign} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 10, fontFamily: "system-ui, sans-serif", fontSize: 14, color: "#2d2d2d" }}>
                    <span style={{ color: "#0d7377", fontWeight: 700, flexShrink: 0, marginTop: 1 }}>→</span>
                    {sign}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* The 2-week rule */}
          <div style={{ background: "#faf9f6", borderTop: "1px solid #e8e4de", borderBottom: "1px solid #e8e4de" }} className="px-8 py-6">
            <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
              <div style={{ fontSize: 28, flexShrink: 0 }}>⏱️</div>
              <div>
                <div style={{ fontWeight: 700, fontSize: 16, color: "#2d2d2d", marginBottom: 4 }}>
                  The 2-week rule
                </div>
                <div style={{ fontFamily: "system-ui, sans-serif", fontSize: 14, color: "#6b6b6b", lineHeight: 1.6 }}>
                  Any sore, patch, lump, or change in your mouth that hasn't gone away after 2 weeks deserves a look from a dentist or doctor. Most of the time it's nothing — but catching oral cancer early changes everything.
                </div>
              </div>
            </div>
          </div>

          {/* CTA footer */}
          <div style={{ background: "#0d7377" }} className="px-10 py-7">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <div style={{ color: "white", fontWeight: 700, fontSize: 18, marginBottom: 4 }}>
                  Check your risk in 2 minutes — free.
                </div>
                <div style={{ color: "rgba(255,255,255,0.8)", fontFamily: "system-ui, sans-serif", fontSize: 14 }}>
                  No account. Nothing saved. Just answers.
                </div>
              </div>
              <div style={{ background: "white", color: "#0d7377", fontFamily: "system-ui, sans-serif", fontWeight: 700, fontSize: 16, padding: "12px 28px", borderRadius: 999, whiteSpace: "nowrap", flexShrink: 0 }}>
                oralcheck.org
              </div>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="px-8 py-4">
            <p style={{ fontFamily: "system-ui, sans-serif", fontSize: 10, color: "#aaa", lineHeight: 1.5, margin: 0 }}>
              OralCheck is a free educational tool — not a medical diagnosis. Risk factors informed by the American Cancer Society, NCI, and clinical oral cancer epidemiology research. Always consult a qualified clinician.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
