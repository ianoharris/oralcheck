"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/screener", label: "Screener" },
  { href: "/find-care", label: "Find Care" },
  { href: "/learn", label: "Learn" },
  { href: "/about", label: "About" },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <header className="border-b border-warm-dim bg-warm/90 backdrop-blur sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-5 h-16 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-2 font-serif text-2xl text-brand"
        >
          <span
            aria-hidden
            className="inline-block w-2.5 h-2.5 rounded-full bg-accent"
          />
          OralCheck
        </Link>
        <nav className="flex gap-1 sm:gap-2">
          {links.map(({ href, label }) => {
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={`text-sm font-medium px-3 py-1.5 rounded-full transition-colors ${
                  active
                    ? "bg-brand text-warm"
                    : "text-ink-soft hover:text-ink hover:bg-warm-dim"
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
