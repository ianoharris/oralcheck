"use client";

import { useState, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import QRCode from "react-qr-code";

const features = [
  {
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
      </svg>
    ),
    title: "10 quick questions",
    desc: "Based on real clinical risk factors — takes about 2 minutes on your phone.",
  },
  {
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
      </svg>
    ),
    title: "Completely private",
    desc: "Nothing is saved or sent anywhere. Your answers stay on your device.",
  },
  {
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <polyline points="9 12 11 14 15 10" />
      </svg>
    ),
    title: "Know your risk level",
    desc: "Get a personalized summary and guidance on what to do next.",
  },
  {
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
        <circle cx="12" cy="10" r="3" />
      </svg>
    ),
    title: "Find affordable care nearby",
    desc: "Connects you to free and low-cost clinics, dental schools, and community health centers.",
  },
];

const warningSigns = [
  "Sores that won't heal",
  "Red or white patches",
  "Lumps or thickening",
  "Difficulty swallowing",
  "Unexplained ear pain",
];

const stats = [
  { value: "54k+", label: "new US oral cancer diagnoses each year" },
  { value: "84%", label: "survival rate when caught early" },
  { value: "2 min", label: "is all a dental screening takes" },
];

const countryCodes = [
  { code: "+1",   label: "🇺🇸 +1" },
  { code: "+44",  label: "🇬🇧 +44" },
  { code: "+61",  label: "🇦🇺 +61" },
  { code: "+64",  label: "🇳🇿 +64" },
  { code: "+353", label: "🇮🇪 +353" },
  { code: "+52",  label: "🇲🇽 +52" },
  { code: "+55",  label: "🇧🇷 +55" },
];

function formatUSPhone(raw: string): string {
  const d = raw.replace(/\D/g, "").slice(0, 10);
  if (!d) return "";
  if (d.length <= 3) return `(${d}`;
  if (d.length <= 6) return `(${d.slice(0, 3)}) ${d.slice(3)}`;
  return `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}`;
}

function openPrintWindow(flyerEl: HTMLElement) {
  // Collect Next.js stylesheet links from the current page
  const cssLinks = Array.from(
    document.querySelectorAll<HTMLLinkElement>('link[rel="stylesheet"]')
  )
    .map((l) => `<link rel="stylesheet" href="${l.href}">`)
    .join("\n");

  const win = window.open("", "_blank");
  if (!win) { window.print(); return; }

  win.document.write(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>OralCheck Flyer</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
  ${cssLinks}
  <style>
    *, *::before, *::after {
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
      box-sizing: border-box;
    }
    @page { margin: 0; size: letter portrait; }
    html, body {
      margin: 0;
      padding: 0.12in 0.18in;
      background: white;
    }
    /* Flatten the card */
    #flyer-inner {
      max-width: 100% !important;
      border-radius: 0 !important;
      box-shadow: none !important;
      border: 0 !important;
    }
    /* Tighten internal spacing so everything fits on one page */
    #flyer-inner .space-y-4 > * + * { margin-top: 0.6rem !important; }
    #flyer-inner .mt-5 { margin-top: 0.75rem !important; }
    #flyer-inner .pb-6 { padding-bottom: 0.75rem !important; }
    #flyer-inner .pt-4 { padding-top: 0.6rem !important; }
    #flyer-inner .mb-4 { margin-bottom: 0.6rem !important; }
    #flyer-inner .mb-5 { margin-bottom: 0.75rem !important; }
  </style>
</head>
<body>
  ${flyerEl.outerHTML}
</body>
</html>`);

  win.document.close();

  // Give fonts and styles time to load before triggering print
  setTimeout(() => {
    win.focus();
    win.print();
  }, 700);
}

export default function PrintableFlyer() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [practice, setPractice] = useState(searchParams.get("practice") ?? "");
  const [countryCode, setCountryCode] = useState(searchParams.get("cc") ?? "+1");
  const [phone, setPhone] = useState(searchParams.get("phone") ?? "");
  const [copied, setCopied] = useState(false);

  const updateParams = useCallback(
    (p: string, cc: string, ph: string) => {
      const params = new URLSearchParams();
      if (p) params.set("practice", p);
      if (cc && cc !== "+1") params.set("cc", cc);
      if (ph) params.set("phone", ph);
      router.replace(params.toString() ? `?${params.toString()}` : "?", { scroll: false });
    },
    [router]
  );

  const handlePracticeChange = (val: string) => { setPractice(val); updateParams(val, countryCode, phone); };
  const handleCountryChange  = (val: string) => { setCountryCode(val); setPhone(""); updateParams(practice, val, ""); };
  const handlePhoneChange    = (val: string) => {
    const fmt = countryCode === "+1" ? formatUSPhone(val) : val;
    setPhone(fmt);
    updateParams(practice, countryCode, fmt);
  };

  const handlePrint = () => {
    const el = document.getElementById("flyer-inner");
    if (el) openPrintWindow(el);
    else window.print();
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const displayPhone = phone
    ? (countryCode === "+1" ? phone : `${countryCode} ${phone}`)
    : "";

  return (
    <>
      {/* Controls — hidden on print */}
      <div className="print:hidden mb-8 bg-white rounded-2xl border border-warm-dim p-6 sm:p-8">
        <h2 className="font-serif text-2xl text-ink mb-1">Customize your flyer</h2>
        <p className="text-sm text-ink-soft mb-5">
          Your practice name appears as a banner on the flyer. Add a phone number and it shows up too.
        </p>
        <div className="space-y-3 mb-5">
          <div>
            <label htmlFor="practice-name" className="block text-sm font-semibold text-ink mb-1.5">
              Practice name
            </label>
            <input
              id="practice-name"
              type="text"
              value={practice}
              onChange={(e) => handlePracticeChange(e.target.value)}
              placeholder="e.g. Lakeside Family Dentistry"
              className="w-full max-w-md rounded-xl border border-warm-dim bg-warm px-4 py-2.5 text-sm text-ink placeholder:text-ink-soft/60 focus:outline-none focus:ring-2 focus:ring-brand/30"
            />
          </div>
          <div>
            <label htmlFor="practice-phone" className="block text-sm font-semibold text-ink mb-1.5">
              Phone number <span className="font-normal text-ink-soft">(optional)</span>
            </label>
            <div className="flex gap-2 max-w-md">
              <select
                value={countryCode}
                onChange={(e) => handleCountryChange(e.target.value)}
                className="rounded-xl border border-warm-dim bg-warm px-3 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-brand/30 flex-shrink-0"
              >
                {countryCodes.map((c) => (
                  <option key={c.code} value={c.code}>{c.label}</option>
                ))}
              </select>
              <input
                id="practice-phone"
                type="tel"
                value={phone}
                onChange={(e) => handlePhoneChange(e.target.value)}
                placeholder={countryCode === "+1" ? "(555) 000-0000" : "Phone number"}
                className="flex-1 rounded-xl border border-warm-dim bg-warm px-4 py-2.5 text-sm text-ink placeholder:text-ink-soft/60 focus:outline-none focus:ring-2 focus:ring-brand/30"
              />
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={handlePrint}
            className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-2.5 rounded-full text-sm transition-colors"
          >
            Print flyer
          </button>
          {(practice || phone) && (
            <button
              onClick={handleCopyLink}
              className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-2.5 rounded-full text-sm border border-warm-dim transition-colors"
            >
              {copied ? "✓ Link copied!" : "Copy shareable link"}
            </button>
          )}
        </div>
        {(practice || phone) && (
          <p className="text-xs text-ink-soft mt-3">
            Share the link above — anyone who opens it sees the same customized flyer.
          </p>
        )}
      </div>

      {/* Flyer preview */}
      <div>
        <div
          id="flyer-inner"
          className="bg-white w-full max-w-[800px] mx-auto shadow-sm border border-warm-dim overflow-hidden rounded-2xl"
        >
          {/* Top teal bar */}
          <div className="h-2 bg-brand" />

          {/* Header row */}
          <div className="flex justify-between items-center px-8 pt-5 pb-3">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-accent flex-shrink-0" />
              <span className="text-sm font-bold tracking-[0.15em] text-ink">ORALCHECK</span>
            </div>
            <div className="bg-brand text-white text-[11px] font-semibold px-4 py-1.5 rounded-full tracking-wider">
              FREE · PRIVATE · EVIDENCE-BASED
            </div>
          </div>

          {/* Practice banner — compact, left-aligned, no decorative stretch */}
          {practice && (
            <div className="mx-6 mb-2 rounded-xl bg-brand px-5 py-2.5 inline-block w-[calc(100%-48px)]">
              <div className="text-white/70 text-[10px] font-semibold tracking-widest uppercase leading-none mb-1">
                Presented by
              </div>
              <div className="text-white font-bold text-base leading-snug">{practice}</div>
              {displayPhone && (
                <div className="text-white/80 text-xs mt-0.5">{displayPhone}</div>
              )}
            </div>
          )}

          {/* Main content */}
          <div className="px-8 pt-4 pb-6">
            <div className="text-[10px] font-bold tracking-[0.2em] text-brand mb-3">
              ORAL CANCER AWARENESS
            </div>

            <h2 className="font-serif text-[3rem] leading-[1.05] text-ink mb-4">
              2 minutes<br />
              could <span className="italic text-brand">save</span><br />
              your life.
            </h2>

            <p className="text-ink-soft text-[15px] leading-relaxed mb-5 max-w-lg">
              Oral cancer is one of the most underdiagnosed cancers — largely because
              early symptoms look ordinary. Take a free, private risk check while you wait.
            </p>

            <div className="border-t border-warm-dim mb-5" />

            {/* Features + QR */}
            <div className="flex gap-8 items-start">
              <div className="flex-1 space-y-4">
                {features.map((f) => (
                  <div key={f.title} className="flex gap-3 items-start">
                    <div className="w-9 h-9 rounded-lg bg-brand flex items-center justify-center flex-shrink-0">
                      {f.icon}
                    </div>
                    <div>
                      <div className="font-semibold text-ink text-sm leading-snug">{f.title}</div>
                      <div className="text-ink-soft text-xs leading-relaxed mt-0.5">{f.desc}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* QR */}
              <div className="flex flex-col items-center gap-1.5 flex-shrink-0">
                <div className="bg-white border-2 border-warm-dim rounded-xl p-3">
                  <QRCode value="https://oralcheck.org" size={148} fgColor="#0d7377" bgColor="#ffffff" level="M" />
                </div>
                <span className="text-[10px] font-bold tracking-wider text-brand">↑ SCAN TO START</span>
                <span className="text-[10px] text-ink-soft font-mono">oralcheck.org</span>
              </div>
            </div>

            {/* Stats */}
            <div className="flex gap-6 mt-5 pt-5 border-t border-warm-dim">
              {stats.map((s) => (
                <div key={s.value} className="flex-1 pb-2 border-b-2 border-brand">
                  <div className="text-[1.6rem] font-bold text-brand leading-none">{s.value}</div>
                  <div className="text-[11px] text-ink-soft leading-snug mt-1">{s.label}</div>
                </div>
              ))}
            </div>

            {/* Warning signs */}
            <div className="bg-brand rounded-xl p-4 mt-5">
              <div className="flex flex-wrap gap-2 items-center">
                <span className="text-white text-[10px] font-bold tracking-widest mr-1">WARNING SIGNS</span>
                {warningSigns.map((sign) => (
                  <span key={sign} className="border border-white/40 text-white text-[11px] px-2.5 py-0.5 rounded-full">
                    {sign}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-between items-end px-8 py-3 border-t border-warm-dim">
            <p className="text-[10px] text-ink-soft max-w-md leading-relaxed">
              <strong className="text-ink">Not a medical diagnosis.</strong> OralCheck is a free
              educational awareness tool. Consult a qualified clinician about any symptom or concern.
              Free · Private · No account required.
            </p>
            <span className="text-[10px] font-bold tracking-[0.15em] text-ink-soft ml-4 flex-shrink-0">ORALCHECK</span>
          </div>

          {/* Bottom orange bar */}
          <div className="h-2 bg-accent" />
        </div>
      </div>
    </>
  );
}
