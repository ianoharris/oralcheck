"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import ThemeToggle from "@/components/ThemeToggle";

const links = [
  { href: "/screener", label: "Screener" },
  { href: "/find-care", label: "Find Care" },
  { href: "/learn", label: "Learn" },
  { href: "/for-clinicians", label: "For Clinicians" },
  { href: "/about", label: "About" },
];

export default function Nav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  // Close menu on route change
  useEffect(() => { setOpen(false); }, [pathname]);

  // Lock body scroll when menu is open
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <header className="border-b border-warm-dim bg-warm/90 backdrop-blur sticky top-0 z-30">
      <div className="max-w-6xl mx-auto px-5 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 font-serif text-2xl text-brand flex-shrink-0"
          onClick={() => setOpen(false)}
        >
          <span aria-hidden className="inline-block w-2.5 h-2.5 rounded-full bg-accent" />
          OralCheck
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          <nav className="flex gap-1">
            {links.map(({ href, label }) => {
              const active = pathname === href || pathname.startsWith(href + "/");
              return (
                <Link
                  key={href}
                  href={href}
                  className={`text-sm font-medium px-3 py-1.5 rounded-full transition-colors ${
                    active ? "bg-brand text-warm" : "text-ink-soft hover:text-ink hover:bg-warm-dim"
                  }`}
                >
                  {label}
                </Link>
              );
            })}
          </nav>
          <ThemeToggle />
        </div>

        {/* Mobile: theme toggle + hamburger */}
        <div className="flex items-center gap-1 md:hidden">
          <ThemeToggle />
          <button
            aria-label={open ? "Close menu" : "Open menu"}
            onClick={() => setOpen(o => !o)}
            className="w-9 h-9 flex flex-col items-center justify-center gap-[5px] rounded-full hover:bg-warm-dim transition-colors"
          >
            <span
              className="block w-5 h-[1.5px] bg-ink-soft transition-all duration-200 origin-center"
              style={{ transform: open ? "translateY(6.5px) rotate(45deg)" : "none" }}
            />
            <span
              className="block w-5 h-[1.5px] bg-ink-soft transition-all duration-200"
              style={{ opacity: open ? 0 : 1 }}
            />
            <span
              className="block w-5 h-[1.5px] bg-ink-soft transition-all duration-200 origin-center"
              style={{ transform: open ? "translateY(-6.5px) rotate(-45deg)" : "none" }}
            />
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      {open && (
        <nav className="md:hidden border-t border-warm-dim bg-warm px-5 py-3 flex flex-col gap-1">
          {links.map(({ href, label }) => {
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setOpen(false)}
                className={`text-sm font-medium px-3 py-2.5 rounded-xl transition-colors ${
                  active ? "bg-brand text-warm" : "text-ink-soft hover:text-ink hover:bg-warm-dim"
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      )}
    </header>
  );
}
