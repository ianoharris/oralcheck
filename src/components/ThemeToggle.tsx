"use client";

import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(false);

  // On mount: use stored preference, or fall back to system preference
  useEffect(() => {
    const stored = localStorage.getItem("theme");
    const prefersDark =
      stored === "dark" ||
      (stored === null && window.matchMedia("(prefers-color-scheme: dark)").matches);

    setDark(prefersDark);
    document.documentElement.setAttribute("data-theme", prefersDark ? "dark" : "light");

    // Watch system preference changes — only apply if user hasn't manually set a preference
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handleSystemChange = (e: MediaQueryListEvent) => {
      if (localStorage.getItem("theme") === null) {
        setDark(e.matches);
        document.documentElement.setAttribute("data-theme", e.matches ? "dark" : "light");
      }
    };
    mq.addEventListener("change", handleSystemChange);
    return () => mq.removeEventListener("change", handleSystemChange);
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.setAttribute("data-theme", next ? "dark" : "light");
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  return (
    <button
      onClick={toggle}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      className="w-8 h-8 flex items-center justify-center rounded-full text-ink-soft hover:text-ink hover:bg-warm-dim transition-colors"
      style={{ fontSize: "1rem" }}
    >
      {dark ? "☀︎" : "☾"}
    </button>
  );
}
