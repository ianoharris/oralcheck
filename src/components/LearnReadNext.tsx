import Link from "next/link";
import { learnArticles } from "@/lib/learnArticles";

interface Props {
  currentHref: string;
}

export default function LearnReadNext({ currentHref }: Props) {
  const related = learnArticles
    .filter((a) => a.href !== currentHref)
    .slice(0, 3);

  return (
    <div className="border-t border-warm-dim mt-16 pt-12">
      <p className="text-xs font-bold uppercase tracking-widest text-ink-soft mb-6">Read next</p>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {related.map(({ href, tag, title, description, icon }) => (
          <Link
            key={href}
            href={href}
            className="group flex flex-col bg-warm-dim rounded-2xl border border-warm-dim p-5 hover:border-brand/40 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xl" aria-hidden>{icon}</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-brand bg-brand-soft px-2 py-0.5 rounded-full">
                {tag}
              </span>
            </div>
            <h3 className="font-serif text-base text-ink mb-1.5 group-hover:text-brand transition-colors leading-snug">
              {title}
            </h3>
            <p className="text-xs text-ink-soft leading-relaxed flex-1">{description}</p>
            <span className="mt-3 text-xs font-semibold text-brand group-hover:underline">Read →</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
