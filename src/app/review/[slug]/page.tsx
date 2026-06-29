"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

// Draft preview page — noindex, not linked publicly.
// Ian reviews the article here before publishing.

interface Article {
  slug: string;
  title: string;
  keyword: string;
  excerpt: string;
  html: string;
  date: string;
}

export default function ReviewPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const [slug, setSlug]           = useState<string>("");
  const [article, setArticle]     = useState<Article | null>(null);
  const [status, setStatus]       = useState<"idle" | "publishing" | "done" | "error">("idle");
  const [errorMsg, setErrorMsg]   = useState<string>("");

  useEffect(() => {
    params.then(({ slug: s }) => {
      setSlug(s);
      fetch(`/api/draft?slug=${encodeURIComponent(s)}`)
        .then((r) => r.json())
        .then((data) => setArticle(data.article ?? null));
    });
  }, [params]);

  async function publish() {
    if (!slug) return;
    setStatus("publishing");
    const res  = await fetch("/api/publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slug }),
    });
    const data = await res.json();
    if (!res.ok) {
      setStatus("error");
      setErrorMsg(data.error ?? "Unknown error");
    } else {
      setStatus("done");
    }
  }

  if (!article) {
    return (
      <div className="max-w-3xl mx-auto px-5 py-20 text-center">
        <p className="text-ink-soft">Loading draft...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      {/* Draft banner */}
      <div className="mb-8 flex items-center justify-between gap-4 rounded-2xl border-2 border-dashed border-accent/40 bg-accent/5 px-5 py-4">
        <div>
          <p className="text-sm font-semibold text-ink">Draft preview</p>
          <p className="text-xs text-ink-soft mt-0.5">
            Not published yet. Approve to make it live at{" "}
            <span className="font-mono text-ink">oralcheck.org/learn/{slug}</span>.
          </p>
        </div>

        {status === "idle" && (
          <button
            onClick={publish}
            className="shrink-0 rounded-full bg-brand px-5 py-2 text-sm font-semibold text-white hover:bg-brand-dark transition-colors"
          >
            Publish →
          </button>
        )}
        {status === "publishing" && (
          <span className="shrink-0 text-sm text-ink-soft">Publishing...</span>
        )}
        {status === "done" && (
          <span className="shrink-0 text-sm font-semibold text-brand">
            Published. Deploying in ~60s.
          </span>
        )}
        {status === "error" && (
          <span className="shrink-0 text-sm text-accent">{errorMsg}</span>
        )}
      </div>

      <Link
        href="/learn"
        className="text-sm font-medium text-ink-soft hover:text-ink mb-6 inline-block"
      >
        ← Back to Learn
      </Link>

      <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
        {article.keyword || "Oral Health"}
      </span>

      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-6 leading-tight">
        {article.title}
      </h1>

      <div
        className="prose-article"
        dangerouslySetInnerHTML={{ __html: article.html }}
      />
    </div>
  );
}
