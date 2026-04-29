"use client";

import { useEffect, useRef, useState } from "react";
import QRCode from "react-qr-code";

export default function QRPage() {
  const [url, setUrl] = useState("https://oralcheck.org");
  const qrRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setUrl(window.location.origin);
  }, []);

  const handlePrint = () => window.print();

  const handleDownload = () => {
    const svg = qrRef.current?.querySelector("svg");
    if (!svg) return;
    const serialized = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement("canvas");
    const size = 800;
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, size, size);
    const img = new Image();
    const blob = new Blob([serialized], { type: "image/svg+xml" });
    const blobUrl = URL.createObjectURL(blob);
    img.onload = () => {
      ctx.drawImage(img, 0, 0, size, size);
      URL.revokeObjectURL(blobUrl);
      const a = document.createElement("a");
      a.href = canvas.toDataURL("image/png");
      a.download = "oralcheck-qr.png";
      a.click();
    };
    img.src = blobUrl;
  };

  return (
    <>
      {/* Print styles — hide everything except the card */}
      <style>{`
        @media print {
          body > * { display: none !important; }
          #print-card { display: flex !important; }
          #print-card * { display: revert !important; }
        }
      `}</style>

      <div className="max-w-2xl mx-auto px-5 py-12 sm:py-20 text-center">
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-3">
          Share OralCheck
        </h1>
        <p className="text-ink-soft text-lg mb-10">
          Print this and post it anywhere — dental offices, community centers,
          waiting rooms. Anyone who scans it gets a free, private oral cancer
          risk check in 2 minutes.
        </p>

        {/* Card — this is what gets printed */}
        <div
          id="print-card"
          className="flex flex-col items-center bg-white rounded-3xl border border-warm-dim p-10 sm:p-14 shadow-sm"
        >
          <div className="text-brand font-serif text-3xl font-bold mb-1">
            OralCheck
          </div>
          <p className="text-ink-soft text-sm mb-8">
            Free oral cancer risk screener
          </p>

          <div ref={qrRef} className="p-4 bg-white rounded-2xl border-2 border-warm-dim">
            <QRCode
              value={url}
              size={220}
              fgColor="#0d7377"
              bgColor="#ffffff"
              level="M"
            />
          </div>

          <p className="mt-8 font-serif text-2xl sm:text-3xl text-ink leading-snug max-w-xs">
            2 minutes could save your life.
          </p>
          <p className="mt-3 text-sm text-ink-soft font-mono">{url}</p>

          <div className="mt-8 flex gap-6 text-xs text-ink-soft">
            <span>✓ Free</span>
            <span>✓ Private</span>
            <span>✓ No account needed</span>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <button
            onClick={handlePrint}
            className="bg-brand hover:bg-brand-dark text-white font-semibold px-7 py-3 rounded-full transition-colors"
          >
            Print this page
          </button>
          <button
            onClick={handleDownload}
            className="bg-white hover:bg-warm-dim text-ink font-semibold px-7 py-3 rounded-full border border-warm-dim transition-colors"
          >
            Download PNG
          </button>
          <button
            onClick={() => {
              if (navigator.share) {
                navigator.share({ title: "OralCheck", url });
              } else if (navigator.clipboard) {
                navigator.clipboard.writeText(url);
                alert("Link copied!");
              }
            }}
            className="bg-white hover:bg-warm-dim text-ink font-semibold px-7 py-3 rounded-full border border-warm-dim transition-colors"
          >
            Share link
          </button>
        </div>

        <p className="mt-10 text-xs text-ink-soft leading-relaxed max-w-sm mx-auto">
          This tool provides general health education only — not medical
          advice or diagnosis. Encourage anyone with concerns to see a
          clinician.
        </p>
      </div>
    </>
  );
}
