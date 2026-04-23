import Link from "next/link";

export default function NotFound() {
  return (
    <div className="max-w-2xl mx-auto px-5 py-20 sm:py-28 text-center">
      <div className="text-5xl mb-6">🦷</div>
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        Page not found
      </h1>
      <p className="text-ink-soft text-lg leading-relaxed mb-10 max-w-md mx-auto">
        The page you&apos;re looking for doesn&apos;t exist. But your oral health still does — pick up where you left off.
      </p>
      <div className="flex flex-wrap justify-center gap-3">
        <Link
          href="/screener"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          Take the screener →
        </Link>
        <Link
          href="/learn"
          className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          Browse learn
        </Link>
        <Link
          href="/"
          className="text-sm font-medium text-ink-soft hover:text-ink px-4 py-3"
        >
          Go home
        </Link>
      </div>
    </div>
  );
}
