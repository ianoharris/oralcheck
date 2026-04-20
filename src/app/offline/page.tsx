import Link from "next/link";

export default function OfflinePage() {
  return (
    <div className="max-w-md mx-auto px-5 py-24 text-center">
      <div className="text-5xl mb-6">📡</div>
      <h1 className="font-serif text-3xl text-ink mb-3">You're offline</h1>
      <p className="text-ink-soft leading-relaxed mb-8">
        The screener and clinic finder need an internet connection. These pages
        are available offline once you've visited them:
      </p>
      <div className="flex flex-col gap-3">
        <Link
          href="/learn"
          className="bg-white border border-warm-dim rounded-2xl px-6 py-4 font-semibold text-brand hover:bg-warm-dim transition-colors"
        >
          Learn about oral cancer →
        </Link>
        <Link
          href="/learn/signs"
          className="bg-white border border-warm-dim rounded-2xl px-6 py-4 font-semibold text-brand hover:bg-warm-dim transition-colors"
        >
          Signs & symptoms →
        </Link>
        <Link
          href="/learn/self-exam"
          className="bg-white border border-warm-dim rounded-2xl px-6 py-4 font-semibold text-brand hover:bg-warm-dim transition-colors"
        >
          Self-exam guide →
        </Link>
      </div>
    </div>
  );
}
