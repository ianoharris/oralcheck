import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-warm-dim bg-warm mt-24">
      <div className="max-w-6xl mx-auto px-5 py-10 grid grid-cols-1 md:grid-cols-3 gap-8 text-sm">
        <div>
          <div className="font-serif text-xl text-brand mb-2">OralCheck</div>
          <p className="text-ink-soft leading-relaxed">
            A free educational tool to help you understand oral cancer risk and
            find the care you need.
          </p>
        </div>
        <div>
          <div className="font-semibold text-ink mb-2">Explore</div>
          <ul className="space-y-1.5 text-ink-soft">
            <li><Link href="/screener" className="hover:text-brand">Risk Screener</Link></li>
            <li><Link href="/find-care" className="hover:text-brand">Find Care</Link></li>
            <li><Link href="/learn" className="hover:text-brand">Learn</Link></li>
            <li><Link href="/about" className="hover:text-brand">About</Link></li>
          </ul>
        </div>
        <div>
          <div className="font-semibold text-ink mb-2">Disclaimer</div>
          <p className="text-ink-soft leading-relaxed">
            OralCheck is not a medical diagnosis. It is an educational tool.
            Consult a qualified clinician about any symptom or concern.
          </p>
        </div>
      </div>
      <div className="border-t border-warm-dim">
        <div className="max-w-6xl mx-auto px-5 py-4 text-xs text-ink-soft flex flex-col sm:flex-row justify-between gap-2">
          <span>© {new Date().getFullYear()} OralCheck</span>
          <span>Not affiliated with any medical institution.</span>
        </div>
      </div>
    </footer>
  );
}
